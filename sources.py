# sources.py - free, non-Yahoo data: NFL stats (nflverse), trends (Sleeper), weather (Open-Meteo)
import json
import re
import time
from pathlib import Path

import nflreadpy as nfl
import polars as pl
import requests

HERE = Path(__file__).parent
CACHE = HERE / "cache"
CACHE.mkdir(exist_ok=True)
SEASON = 2026

# ---------- helpers ----------
_mem = {}

def _cached(key, ttl, loader):
    """Keep expensive downloads in memory for `ttl` seconds instead of refetching every call."""
    hit = _mem.get(key)
    if hit and time.time() - hit[0] < ttl:
        return hit[1]
    value = loader()
    _mem[key] = (time.time(), value)
    return value

def _norm(name):
    """'A.J. Brown Jr.' -> 'aj brown' so names match across data sources."""
    n = re.sub(r"[.'`,]", "", (name or "").lower())
    n = re.sub(r"\b(jr|sr|ii|iii|iv|v)\b", "", n)
    return " ".join(n.split())

def _stats():
    return _cached("stats", 3600, lambda: nfl.load_player_stats([SEASON]))

def _snaps():
    return _cached("snaps", 3600, lambda: nfl.load_snap_counts([SEASON]))

def _pfr_ids():
    """Stats use gsis_id, snap counts use pfr_id; this maps one to the other (names differ, e.g. Greg/Gregory)."""
    def load():
        p = nfl.load_players().select(["gsis_id", "pfr_id"]).drop_nulls()
        return dict(zip(p["gsis_id"].to_list(), p["pfr_id"].to_list()))
    return _cached("pfr_ids", 86400, load)

def _schedule():
    return _cached("sched", 3600, lambda: nfl.load_schedules([SEASON]))

# ---------- schedule / Vegas ----------
def current_week():
    """First regular-season week that still has an unplayed game."""
    s = _schedule().filter((pl.col("game_type") == "REG") & pl.col("home_score").is_null())
    return int(s["week"].min()) if s.height else 18

def week_games(week=None, with_weather=True):
    """Every game in a week: kickoff (ET), Vegas lines, implied team totals, roof, and weather."""
    week = week or current_week()
    stadiums = json.loads((HERE / "stadiums.json").read_text(encoding="utf-8"))
    games = []
    for g in _schedule().filter(pl.col("week") == week).sort(["gameday", "gametime"]).iter_rows(named=True):
        info = {"game": f'{g["away_team"]} @ {g["home_team"]}',
                "kickoff_et": f'{g["gameday"]} {g["gametime"]}',
                "stadium": g["stadium"]}
        if g["home_score"] is not None:
            info["final"] = f'{g["away_team"]} {g["away_score"]} - {g["home_team"]} {g["home_score"]}'
        total, spread = g["total_line"], g["spread_line"]  # spread_line > 0 means home team favored
        if total is not None and spread is not None:
            info["vegas"] = {"total": total, "home_favored_by": spread,
                             "implied": {g["home_team"]: round(total / 2 + spread / 2, 1),
                                         g["away_team"]: round(total / 2 - spread / 2, 1)}}
        if with_weather:
            info["weather"] = _game_weather(g, stadiums.get(g["stadium_id"]))
        games.append(info)
    return {"week": week, "games": games}

# ---------- weather ----------
def _game_weather(g, stadium):
    roof = g["roof"]
    if roof in ("dome", "closed"):
        return "indoors"
    if stadium is None:
        return f'unknown stadium {g["stadium_id"]}'
    try:
        # timezone=America/New_York so hourly times line up with nflverse's ET kickoff times
        w = requests.get("https://api.open-meteo.com/v1/forecast", params={
            "latitude": stadium["lat"], "longitude": stadium["lon"],
            "hourly": "temperature_2m,precipitation_probability,precipitation,wind_speed_10m,wind_gusts_10m",
            "temperature_unit": "fahrenheit", "wind_speed_unit": "mph", "precipitation_unit": "inch",
            "timezone": "America/New_York", "start_date": g["gameday"], "end_date": g["gameday"]},
            timeout=20).json()
        h = w["hourly"]
        stamp = f'{g["gameday"]}T{g["gametime"][:2]}:00'
        i = h["time"].index(stamp)
        out = {"temp_f": h["temperature_2m"][i], "wind_mph": h["wind_speed_10m"][i],
               "gusts_mph": h["wind_gusts_10m"][i], "rain_chance_pct": h["precipitation_probability"][i],
               "precip_in": h["precipitation"][i]}
    except (KeyError, ValueError, requests.RequestException):
        return "forecast not available yet (Open-Meteo covers ~16 days ahead)"
    if roof is None:
        out["note"] = "retractable roof - open/closed decided on game day"
    return out

# ---------- league scoring ----------
# Scoring stats that are sums of several nflverse columns
DERIVED = {
    "two_pt": ["passing_2pt_conversions", "rushing_2pt_conversions", "receiving_2pt_conversions"],
    "return_yards": ["punt_return_yards", "kickoff_return_yards"],
    "def_blocks": ["def_fg_blocks", "def_punt_blocks", "def_pat_blocks"],
    # offensive fumbles only (runs, catches, sacks) - matches nflverse; excludes kick/punt return fumbles
    "fumbles_lost": ["rushing_fumbles_lost", "receiving_fumbles_lost", "sack_fumbles_lost"],
}

def league_points(row, rules):
    """Fantasy points for one player-week under a league's scoring_rules ({stat: points per unit})."""
    total = 0.0
    for stat, pts in rules.items():
        if stat.startswith("_"):
            continue
        total += pts * sum((row.get(c) or 0) for c in DERIVED.get(stat, [stat]))
    return round(total, 2)

# ---------- player usage (nflverse) ----------
USAGE_COLS = ["week", "team", "opponent_team", "fantasy_points_ppr", "targets", "target_share",
              "air_yards_share", "receptions", "receiving_yards", "receiving_tds", "carries",
              "rushing_yards", "rushing_tds", "attempts", "completions", "passing_yards", "passing_tds",
              "passing_interceptions", "fg_made", "fg_att", "def_tackles_solo", "def_tackle_assists",
              "def_sacks", "def_interceptions", "def_pass_defended", "def_fumbles_forced"]

def player_usage(name, team=None, last_n=4, scoring=None):
    """Recent weekly usage for a player: stats, target share, snap %. `team` breaks name ties.
    Pass a league's scoring_rules as `scoring` to add league_pts (points under that league's rules)."""
    key = _norm(name)
    stats = _stats().with_columns(pl.col("player_display_name").map_elements(_norm, return_dtype=pl.Utf8).alias("_n"))
    rows = stats.filter(pl.col("_n") == key)
    if rows.is_empty():
        rows = stats.filter(pl.col("_n").str.contains(key, literal=True))
    if team:
        rows = rows.filter(pl.col("team") == team.upper())
    if rows.is_empty():
        # No games played yet (injured, suspended, inactive...) - still report status so the caller knows why
        return {"error": f"no {SEASON} stats found for '{name}'", "status": _sleeper_status(name, team)}
    if rows["player_id"].n_unique() > 3:  # too vague - ask for a more specific name instead of dumping stats
        who = rows.unique("player_id").select(["player_display_name", "position", "team"]).to_dicts()
        return {"error": f"'{name}' matches {len(who)} players - use a full name and/or team", "matches": who[:15]}

    snaps = _snaps().with_columns(pl.col("player").map_elements(_norm, return_dtype=pl.Utf8).alias("_n"))
    players = []
    for pid, grp in rows.group_by("player_id"):
        grp = grp.sort("week").tail(last_n)
        first = grp.row(0, named=True)
        cols = [c for c in USAGE_COLS if c in grp.columns]
        weekly = []
        for r in grp.to_dicts():
            w = {k: (round(r[k], 3) if isinstance(r[k], float) else r[k])
                 for k in cols if r[k] not in (None, 0, 0.0) or k == "week"}
            if scoring:
                w["league_pts"] = league_points(r, scoring)
            weekly.append(w)
        pfr = _pfr_ids().get(pid[0] if isinstance(pid, tuple) else pid)
        match = (pl.col("pfr_player_id") == pfr) if pfr else \
                ((pl.col("_n") == _norm(first["player_display_name"])) & (pl.col("team") == first["team"]))
        snap_rows = (snaps.filter(match)
                          .sort("week").tail(last_n)
                          .select(["week", pl.max_horizontal("offense_pct", "defense_pct").alias("pct")]).to_dicts())
        players.append({"name": first["player_display_name"], "position": first["position"],
                        "team": grp["team"][-1], "weekly": weekly,
                        "snap_pct": {r["week"]: round(r["pct"] * 100) for r in snap_rows},  # offense or defense, whichever they play
                        "status": _sleeper_status(first["player_display_name"], grp["team"][-1])})
    return players[0] if len(players) == 1 else {"multiple_matches": players}

# ---------- Sleeper ----------
def _sleeper_players():
    f = CACHE / "sleeper_players.json"
    if not f.exists() or time.time() - f.stat().st_mtime > 86400:  # ~5 MB, refresh daily
        r = requests.get("https://api.sleeper.app/v1/players/nfl", timeout=60)
        r.raise_for_status()
        f.write_text(r.text, encoding="utf-8")
    return _cached("sleeper", 3600, lambda: json.loads(f.read_text(encoding="utf-8")))

SLEEPER_TEAM = {"LA": "LAR"}  # nflverse team code -> Sleeper team code, where they differ

def _sleeper_status(name, team=None):
    key = _norm(name)
    team = SLEEPER_TEAM.get(team, team)
    for p in _sleeper_players().values():
        if _norm(p.get("full_name")) == key and (team is None or p.get("team") == team):
            return {"injury": p.get("injury_status") or "healthy", "body_part": p.get("injury_body_part"),
                    "depth_chart": p.get("depth_chart_order")}
    return None

def trending(kind="add", hours=48, limit=40):
    """Players most added ('add') or dropped ('drop') across Sleeper leagues in the last `hours`."""
    r = requests.get(f"https://api.sleeper.app/v1/players/nfl/trending/{kind}",
                     params={"lookback_hours": hours, "limit": limit}, timeout=20)
    r.raise_for_status()
    players = _sleeper_players()
    out = []
    for t in r.json():
        p = players.get(t["player_id"], {})
        out.append({"name": p.get("full_name") or f'{p.get("team", t["player_id"])} DEF',
                    "pos": p.get("position"), "team": p.get("team"),
                    "injury": p.get("injury_status"), "count": t["count"]})
    return out
