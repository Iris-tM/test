"""
MCP Server Test Script

Verify FastMCP server can start and respond correctly
"""

import asyncio
import sys
import os

# Add project path
project_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_path)

from stork_agent.mcp.server import mcp


async def test_mcp_server():
    """Test MCP Server"""
    print("=== MCP Server Test ===\n")

    # 1. Test tool list
    print("1. Testing tool list...")
    tools = await mcp.list_tools()
    print(f"   [OK] Registered {len(tools)} tools")
    for tool in tools:
        print(f"     - {tool.name}")

    # 2. Test tool call
    print("\n2. Testing tool call...")
    try:
        result = await mcp.call_tool("get_market_summary", {})
        print(f"   [OK] get_market_summary call successful")
        print(f"   Result length: {len(str(result))} chars")
    except Exception as e:
        print(f"   [FAIL] Call failed: {e}")

    # 3. Test search tool
    print("\n3. Testing search tool...")
    try:
        result = await mcp.call_tool("search_stocks", {"keyword": "MOUTAI", "limit": 3})
        print(f"   [OK] search_stocks call successful")
    except Exception as e:
        print(f"   [FAIL] Call failed: {e}")

    print("\n=== Test Complete ===")
    print("\nMCP Server Ready!")
    print("\nAvailable tools:")
    for tool in tools:
        print(f"  - {tool.name}: {tool.description}")


if __name__ == "__main__":
    asyncio.run(test_mcp_server())
