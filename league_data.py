# league_data.py - where league info (rosters, scoring) comes from.
# Today: leagues.json, filled in by hand. Later: swap in yahoo_client.py once API access is approved.
# Everything else (server, commands) only calls these functions, so only this file changes.
import json
from datetime import date
from pathlib import Path

FILE = Path(__file__).parent / "leagues.json"

def _load():
    if not FILE.exists():
        return {"leagues": []}
    return json.loads(FILE.read_text(encoding="utf-8"))

def list_leagues():
    out = []
    for lg in _load()["leagues"]:
        updated = lg.get("updated")
        age = (date.today() - date.fromisoformat(updated)).days if updated else None
        out.append({"id": lg["id"], "name": lg["name"], "scoring": lg.get("scoring"),
                    "updated": updated, "days_since_update": age})
    return out

def get_league(league_id):
    for lg in _load()["leagues"]:
        if lg["id"] == league_id:
            return lg
    return {"error": f"no league '{league_id}'. Known: {[l['id'] for l in _load()['leagues']]}"}
