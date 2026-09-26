# fantasy-agent

A personal, non-commercial tool for managing my own teams in Yahoo Fantasy Football.
It pulls **read-only** data from my leagues through the official
[Yahoo Fantasy Sports API](https://sports.yahoo.com/developer/), combines it with public
NFL statistics and weather forecasts, and helps me review lineup, waiver-wire and trade
decisions. I make all roster moves myself in the Yahoo app.

> **Status:** in development. Yahoo Fantasy API access is pending approval.

## Scope and data handling

- **Official API only.** All Yahoo data is accessed through the Fantasy Sports API with OAuth 2.0.
  No scraping, no browser automation.
- **Read-only.** Uses the `fspt-r` scope. The tool never modifies rosters, lineups or leagues.
- **Single user.** Used only by me, for the leagues I play in. No public app, site or service.
- **Low volume.** A few runs per week (e.g. after Monday's games and before Sunday kickoffs),
  under ~100 API calls per week, with short-lived local caching to avoid repeat requests.
- **Stays local.** League data is stored only on my own computer and is never published,
  shared, sold or redistributed. Credentials, tokens and cached data are excluded from this
  repository (see `.gitignore`).

## Yahoo data used

| Data | Used for |
|---|---|
| League settings and scoring rules | Valuing players correctly (PPR, bonuses, roster slots) |
| My roster | Start/sit decisions |
| Other teams' rosters in my leagues | Identifying realistic trade partners |
| Available free agents, ownership % | Waiver-wire candidates |
| Player status, weekly matchups | Injury and matchup context |

## Other data sources (non-Yahoo)

| Source | Data |
|---|---|
| [nflverse](https://github.com/nflverse) via `nflreadpy` | Weekly player stats, snap counts, target share, schedules |
| [Sleeper public API](https://docs.sleeper.com/) | League-wide trending adds/drops |
| [Open-Meteo](https://open-meteo.com/) | Kickoff-time weather forecasts for outdoor stadiums |

## Project structure

| File | Purpose |
|---|---|
| `yahoo_client.py` | Read-only Yahoo Fantasy API client (leagues, rosters, settings, free agents) |
| `login.py` | One-time OAuth 2.0 authorization requesting the `fspt-r` scope |
| `diagnose.py` | Connectivity check against basic API endpoints |
| `sources.py` | Non-Yahoo data: player usage and snap %, schedules and Vegas lines, weather, Sleeper trends |
| `stadiums.json` | Stadium coordinates (incl. international venues) for kickoff weather |
| `smoke_test.py` | End-to-end check that every data source still works |
| `requirements.txt` | Python dependencies |

## Setup

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create `oauth2.json` (git-ignored) with your own Yahoo app credentials:

```json
{ "consumer_key": "YOUR_CLIENT_ID", "consumer_secret": "YOUR_CLIENT_SECRET" }
```

Then authorize once with `python login.py`. Tokens refresh automatically afterward.

## License

Personal project, not affiliated with or endorsed by Yahoo. Yahoo data is subject to the
[Yahoo Fantasy Sports API Terms of Use](https://legal.yahoo.com/us/en/yahoo/terms/product-atos/fantasysportsapi/index.html).
