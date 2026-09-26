# server.py - exposes our data functions as tools Claude can call (MCP, stdio transport).
# stdout is the channel Claude and this server talk over - never print() here.
import contextlib
import sys

from mcp.server.mcpserver import MCPServer

import league_data
import sources

mcp = MCPServer("fantasy")

def _quiet(fn, *args, **kwargs):
    """Run a data function with any library print() output sent to stderr, so it can't corrupt stdout."""
    with contextlib.redirect_stdout(sys.stderr):
        return fn(*args, **kwargs)

@mcp.tool()
def list_leagues() -> list:
    """List my fantasy leagues (id, name, scoring, how many days since the data was updated). Call this first."""
    return _quiet(league_data.list_leagues)

@mcp.tool()
def get_league(league_id: str) -> dict:
    """One league's details: my roster with current slots, scoring rules, roster slots, waiver/FAAB status, notes."""
    return _quiet(league_data.get_league, league_id)

@mcp.tool()
def get_current_week() -> int:
    """The current NFL regular-season week (first week that still has unplayed games)."""
    return _quiet(sources.current_week)

@mcp.tool()
def get_week_games(week: int = 0) -> dict:
    """All games in an NFL week: kickoff (ET), Vegas total/spread, implied team totals, roof, and kickoff weather
    (temp, wind, gusts, rain). week=0 means the current week."""
    return _quiet(sources.week_games, week or None)

@mcp.tool()
def get_player_usage(name: str, team: str = "", last_n: int = 4, league_id: str = "") -> dict:
    """A player's recent weekly stats, PPR points, target share, snap %, and injury status/depth chart.
    Pass team (e.g. 'BUF') if the name is common. Pass league_id to add league_pts: the player's
    actual points under that league's custom scoring (use this, not fantasy_points_ppr, when available)."""
    scoring = league_data.get_league(league_id).get("scoring_rules") if league_id else None
    return _quiet(sources.player_usage, name, team or None, last_n, scoring)

@mcp.tool()
def get_trending(kind: str = "add", hours: int = 48, limit: int = 30) -> list:
    """Players most added ('add') or dropped ('drop') across Sleeper leagues in the last `hours`.
    A strong signal for waiver-wire pickups."""
    return _quiet(sources.trending, kind, hours, limit)

if __name__ == "__main__":
    mcp.run(transport="stdio")
