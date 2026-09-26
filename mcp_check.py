# mcp_check.py - talk to server.py the same way Claude does, to prove the tools work end to end.
import asyncio
import sys
from pathlib import Path

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

HERE = Path(__file__).parent

CALLS = [
    ("list_leagues", {}),
    ("get_league", {"league_id": "work"}),
    ("get_current_week", {}),
    ("get_player_usage", {"name": "Jameson Williams"}),
    ("get_trending", {"kind": "add", "limit": 3}),
    ("get_week_games", {}),
]

async def main():
    params = StdioServerParameters(command=sys.executable, args=[str(HERE / "server.py")], cwd=str(HERE))
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print("TOOLS:", [t.name for t in tools.tools])
            for name, args in CALLS:
                r = await session.call_tool(name, args)
                text = " ".join(getattr(c, "text", "") for c in r.content)
                print(f"\n{name}({args}) error={r.is_error}\n  {text[:300]}")

asyncio.run(main())
