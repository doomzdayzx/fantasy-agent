# check_rosters.py - confirm every rostered player in leagues.json matches the stats data.
# Run after editing leagues.json: python check_rosters.py
import contextlib
import sys

import league_data
import sources

with contextlib.redirect_stdout(sys.stderr):
    leagues = [league_data.get_league(l["id"]) for l in league_data.list_leagues()]

problems = 0
for lg in leagues:
    print(f"\n{lg['name']}")
    for p in lg["my_team"]:
        if p["pos"] == "DEF":
            continue
        with contextlib.redirect_stdout(sys.stderr):
            r = sources.player_usage(p["name"], p["team"], last_n=3)
        if "error" in r:
            problems += 1
            print(f"  ?? {p['name']} ({p['team']}): {r['error']}")
        else:
            st = (r.get("status") or {}).get("injury", "no Sleeper match")
            print(f"  ok {r['name']:26} {r['team']:4} weeks={[w['week'] for w in r['weekly']]} status={st}")
print(f"\n{problems} player(s) need attention")
