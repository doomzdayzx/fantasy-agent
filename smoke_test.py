# smoke_test.py - quick "does every data source still work?" check. Run: python smoke_test.py
import json
import time
import traceback

import sources as s

def show(label, fn):
    t = time.time()
    try:
        out = json.dumps(fn(), default=str)
        print(f"\n### {label}  ({time.time() - t:.1f}s, {len(out)} chars)\n{out[:1400]}")
    except Exception:
        print(f"\n### {label} FAILED")
        traceback.print_exc()

STANDARD_PPR = {"passing_yards": 0.04, "passing_tds": 4, "passing_interceptions": -2, "rushing_yards": 0.1,
                "rushing_tds": 6, "receptions": 1, "receiving_yards": 0.1, "receiving_tds": 6,
                "two_pt": 2, "fumbles_lost": -2, "special_teams_tds": 6}

def check_scoring_engine():
    """Our league_points() with standard PPR rules must reproduce nflverse's fantasy_points_ppr."""
    rows = s._stats().to_dicts()
    bad = [(r["player_display_name"], r["week"], r["fantasy_points_ppr"], s.league_points(r, STANDARD_PPR))
           for r in rows if abs((r["fantasy_points_ppr"] or 0) - s.league_points(r, STANDARD_PPR)) > 0.05]
    return {"rows_checked": len(rows), "mismatches": len(bad), "examples": bad[:5]}

if __name__ == "__main__":
    show("scoring engine vs nflverse PPR", check_scoring_engine)
    show("current_week", s.current_week)
    show("week_games", lambda: s.week_games())
    show("usage: Josh Allen (no team given)", lambda: s.player_usage("Josh Allen"))
    show("usage: Williams (too vague)", lambda: s.player_usage("Williams"))
    show("usage: Josh Allen BUF", lambda: s.player_usage("Josh Allen", team="BUF"))
    show("usage: AJ Brown (punctuation)", lambda: s.player_usage("AJ Brown"))
    show("usage: unknown player", lambda: s.player_usage("Nobody McFake"))
    show("trending adds", lambda: s.trending("add", 48, 10))
    show("usage again (should be fast - cached)", lambda: s.player_usage("Josh Allen", team="BUF"))
