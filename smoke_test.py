# smoke_test.py - quick "does every data source still work?" check. Run: python smoke_test.py
import json
import time
import traceback

import sources as s

def show(label, fn):
    t = time.time()
    try:
        out = json.dumps(fn(), default=str)
        print(f"\n### {label}  ({time.time() - t:.1f}s, {len(out)} chars)\n{out[:1400]}")
    except Exception:
        print(f"\n### {label} FAILED")
        traceback.print_exc()

if __name__ == "__main__":
    show("current_week", s.current_week)
    show("week_games", lambda: s.week_games())
    show("usage: Josh Allen (no team given)", lambda: s.player_usage("Josh Allen"))
    show("usage: Williams (too vague)", lambda: s.player_usage("Williams"))
    show("usage: Josh Allen BUF", lambda: s.player_usage("Josh Allen", team="BUF"))
    show("usage: AJ Brown (punctuation)", lambda: s.player_usage("AJ Brown"))
    show("usage: unknown player", lambda: s.player_usage("Nobody McFake"))
    show("trending adds", lambda: s.trending("add", 48, 10))
    show("usage again (should be fast - cached)", lambda: s.player_usage("Josh Allen", team="BUF"))
