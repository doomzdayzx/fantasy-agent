# diagnose.py - ask Yahoo simple questions to find where access breaks
import yahoo_client as y

s = y.session().session  # the logged-in HTTP session the library uses
base = "https://fantasysports.yahooapis.com/fantasy/v2"

for path in ["game/nfl",
             "users;use_login=1",
             "users;use_login=1/games;game_codes=nfl/teams"]:
    r = s.get(f"{base}/{path}", params={"format": "json"})
    print(f"\n=== {path} -> HTTP {r.status_code}")
    print(r.text[:300])