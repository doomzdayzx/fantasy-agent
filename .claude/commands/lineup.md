---
description: Start/sit recommendations for this week (one league or all)
---
League: $ARGUMENTS (if blank, do all leagues from list_leagues).

1. `get_league` for the roster, slots and scoring. Skip `locked` players (already played).
2. `get_week_games` once for kickoff times, implied team totals and weather.
3. For every starter and every realistic bench alternative: `get_player_usage` (pass team and league_id),
   plus a web search for the latest injury/practice news on anyone Questionable or trending down.
4. Build the best legal lineup for the league's slots (flex = W/R/T).
5. Output per league: start/sit table, then "Changes to make" (e.g. "Bench X, start Y").
   Note any late-game (Sun/Mon night) injury risks to re-check before kickoff.
