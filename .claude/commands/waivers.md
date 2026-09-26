---
description: Waiver wire + free agent report. Usage: /waivers [league...] e.g. /waivers todd
---
Leagues: "$ARGUMENTS". Match loosely against `list_leagues` ids and names (e.g. "lego", "Lego League", "todds", "work league"); several may be given. If blank, do all leagues. If nothing matches, show the league list and ask. Then for each selected league:

1. `get_league`: find weak spots — injured/IR starters, low-usage starters, thin positions, bye weeks ahead.
2. `get_trending` (adds, 48h) and web-search this week's waiver-wire consensus.
3. Check the top candidates with `get_player_usage` — rising snap %/targets/carries beats one big game.
4. Availability: I can't see Yahoo free agents automatically. List your top candidates per
   league and ask me to confirm who's available (or use a pasted free-agent list if I gave one).
5. For each league: top 5 pickups with suggested drop and FAAB bid (% of remaining budget) or
   claim priority. End with 2–3 "stash" players to watch.
