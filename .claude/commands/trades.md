---
description: Buy-low / sell-high trade targets. Usage: /trades [league...] e.g. /trades work
---
Leagues: "$ARGUMENTS". Match loosely against `list_leagues` ids and names (e.g. "lego", "Lego League", "todds", "work league"); several may be given. If blank, do all leagues. If nothing matches, show the league list and ask. Then for each selected league:

1. Sell-high: players on my roster whose points outpace their usage (TD-dependent, falling
   snap %, tough upcoming schedule, returning teammate).
2. Buy-low: players with strong usage (snap %, target share, carries) but poor recent points.
   Use `get_player_usage` and web search to confirm the reason.
3. Identify my positional surplus vs. need, and suggest 1–2 specific, fair trade offers.
4. I don't have other teams' rosters in leagues.json — name targets and ask me who owns them
   (or use rosters I've pasted).
