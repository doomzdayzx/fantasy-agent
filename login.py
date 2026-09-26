# login.py - one-time Yahoo login that explicitly requests Fantasy Sports access.
# Why: yahoo_oauth's built-in login asks for no scope, so Yahoo issues a token
# without Fantasy access (every Fantasy call returns 403). Asking for fspt-r fixes it.
# Token refreshes afterwards are handled automatically by yahoo_client.py.
import json, time, webbrowser
from pathlib import Path
from urllib.parse import urlencode, urlparse, parse_qs
import requests
import yahoo_client  # noqa: F401 - registers Chrome as the browser

FILE = Path(__file__).parent / "oauth2.json"
REDIRECT = "https://localhost:8080"   # must exactly match the Redirect URI on the Yahoo app

cfg = json.loads(FILE.read_text())

# Step 1: send the user to Yahoo, asking for Fantasy Sports read (fspt-r)
auth_url = "https://api.login.yahoo.com/oauth2/request_auth?" + urlencode({
    "client_id": cfg["consumer_key"],
    "redirect_uri": REDIRECT,
    "response_type": "code",
    "scope": "fspt-r",
})
webbrowser.open(auth_url)

# Step 2: Chrome lands on a broken localhost page; the code is in its URL
pasted = input("\nAfter clicking Agree, copy the FULL address bar URL and paste it here:\n> ").strip()
code = parse_qs(urlparse(pasted).query)["code"][0]

# Step 3: trade the code (plus our secret) for a token
r = requests.post("https://api.login.yahoo.com/oauth2/get_token",
                  auth=(cfg["consumer_key"], cfg["consumer_secret"]),
                  data={"grant_type": "authorization_code", "redirect_uri": REDIRECT, "code": code})
if r.status_code != 200:
    raise SystemExit(f"Token request failed: {r.status_code} {r.text}")
tok = r.json()

cfg.update(access_token=tok["access_token"], refresh_token=tok["refresh_token"],
           token_type=tok["token_type"], token_time=time.time(),
           guid=tok.get("xoauth_yahoo_guid"))
FILE.write_text(json.dumps(cfg, indent=2))
print("Saved token to oauth2.json")

# Quick test: can this token read Fantasy data?
t = requests.get("https://fantasysports.yahooapis.com/fantasy/v2/game/nfl",
                 params={"format": "json"},
                 headers={"Authorization": f"Bearer {tok['access_token']}"})
print(f"Fantasy test -> HTTP {t.status_code}\n{t.text[:300]}")
