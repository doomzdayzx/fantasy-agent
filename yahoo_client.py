# yahoo_client.py
import webbrowser
from pathlib import Path
from yahoo_oauth import OAuth2
import yahoo_fantasy_api as yfa

HERE = Path(__file__).parent
SEASON = 2026
_session = None

# Open the Yahoo login page in Chrome instead of printing the URL
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
webbrowser.register("chrome", None, webbrowser.BackgroundBrowser(CHROME), preferred=True)

def session():
    """Log in once, then reuse the token and refresh it when it expires (~1 hr)."""
    global _session
    if _session is None:
        _session = OAuth2(None, None, from_file=str(HERE / "oauth2.json"), browser_callback=True)
    if not _session.token_is_valid():
        _session.refresh_access_token()
    return _session

def game():
    return yfa.Game(session(), "nfl")

def league(league_id):
    return game().to_league(league_id)

def my_leagues():
    out = []
    for lid in game().league_ids(year=SEASON):
        out.append({"league_id": lid, "name": league(lid).settings()["name"]})
    return out

def my_roster(league_id):
    lg = league(league_id)
    week = lg.current_week()
    team = lg.to_team(lg.team_key())
    return {"week": week, "players": team.roster(week)}

def league_settings(league_id):
    lg = league(league_id)
    return {"settings": lg.settings(), "stat_categories": lg.stat_categories()}

def free_agents(league_id, position):
    fas = league(league_id).free_agents(position)
    fas.sort(key=lambda p: p.get("percent_owned", 0), reverse=True)
    return fas[:40]  # top 40 only, so we don't flood Claude with junk

def all_rosters(league_id):
    """Every team's roster. Used to find trade partners."""
    lg = league(league_id)
    week = lg.current_week()
    return {t["name"]: lg.to_team(key).roster(week) for key, t in lg.teams().items()}