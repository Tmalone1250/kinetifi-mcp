import asyncio
import pytest
from server import mcp

def test_server_initialization():
    """Verify that the FastMCP server is correctly initialized with the expected name."""
    assert mcp.name == "kinetifi-mcp"

def test_get_status_tool_registered():
    """Verify that the get_status tool is registered in the server's tools list."""
    tools = asyncio.run(mcp.list_tools())
    tool_names = [tool.name for tool in tools]
    assert "get_status" in tool_names

def test_get_status_tool_execution():
    """Verify that calling the get_status tool returns the expected status message."""
    content_blocks, raw_output = asyncio.run(mcp.call_tool("get_status", {}))
    
    # Verify raw output dictionary
    assert "result" in raw_output
    assert raw_output["result"] == "KinetiFi MCP Server is operational."
    
    # Verify the formatted text output content block
    assert len(content_blocks) == 1
    assert content_blocks[0].type == "text"
    assert "operational" in content_blocks[0].text
