import sys
import os
import asyncio
import aiohttp
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# ── Critical fix ─────────────────────────────────────────────────────────────
# When this file runs as __main__ (via `python server.py`), tool modules that
# do `from server import mcp` would normally trigger a *second* import of
# server.py under the name "server", creating an orphan FastMCP instance whose
# tools are never served.  Aliasing 'server' → __main__ prevents that.
sys.modules.setdefault("server", sys.modules[__name__])

# Load environment variables
load_dotenv()

# Initialize FastMCP Server
mcp = FastMCP("kinetifi-mcp")

@mcp.tool()
async def get_status() -> str:
    """
    Simple healthcheck tool to verify that the KinetiFi MCP Server is alive and operational.
    
    Returns:
        str: Status message indicating the server is operational.
    """
    return "KinetiFi MCP Server is operational."

# ── Tool Registration ─────────────────────────────────────────────────────────
# Import tool modules AFTER mcp is defined so @mcp.tool() decorators bind to
# the live instance above. The sys.modules alias above ensures 'from server
# import mcp' inside each tool resolves here, not to a duplicate.
import tools.scan_yields        # noqa: F401  – registers scan_yields
import tools.get_portfolio_state  # noqa: F401  – registers get_portfolio_state
import tools.generate_strategy  # noqa: F401  – registers generate_strategy

if __name__ == "__main__":
    # Start the FastMCP server using the stdio transport by default
    mcp.run(transport="stdio")

