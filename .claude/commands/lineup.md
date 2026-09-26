---
description: Start/sit recommendations for this week. Usage: /lineup [league...] e.g. /lineup lego
---
Leagues: "$ARGUMENTS". Match loosely against `list_leagues` ids and names (e.g. "lego", "Lego League", "todds", "work league"); several may be given. If blank, do all leagues. If nothing matches, show the league list and ask.

1. `get_league` for the roster, slots and scoring. Skip `locked` players (already played).
2. `get_week_games` once for kickoff times, implied team totals and weather.
3. For every starter and every realistic bench alternative: `get_player_usage` (pass team and league_id),
   plus a web search for the latest injury/practice news on anyone Questionable or trending down.
4. Build the best legal lineup for the league's slots (flex = W/R/T).
5. Output per league: start/sit table, then "Changes to make" (e.g. "Bench X, start Y").
   Note any late-game (Sun/Mon night) injury risks to re-check before kickoff.
