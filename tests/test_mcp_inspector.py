"""
MCP Inspector 测试脚本

用于使用 MCP Inspector 验证 Stork Agent MCP 服务器的功能

使用方法:
1. 确保 MCP Inspector 已安装: pip install mcp-inspector
2. 运行此脚本启动服务器供 Inspector 连接
3. 在另一个终端运行: mcp-inspector python -m stork_agent.mcp_server.server
"""

import asyncio
import sys
import os

# 添加项目路径（tests/ 是项目根目录的子目录，所以需要2次 dirname）
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

from stork_agent.mcp_server.server import main as server_main


async def run_inspector_test():
    """
    启动 MCP 服务器供 Inspector 测试

    运行此脚本后，在另一个终端运行:
    npx @modelcontextprotocol/inspector python -m stork_agent.mcp_server.server

    或者直接运行:
    python -m stork_agent.mcp_server.server
    """
    print("=" * 60)
    print("Stork Agent MCP Server - Inspector 测试模式")
    print("=" * 60)
    print()
    print("服务器正在启动...")
    print()
    print("在另一个终端运行以下命令来连接 Inspector:")
    print("  npx @modelcontextprotocol/inspector python -m stork_agent.mcp_server.server")
    print()
    print("或者使用 Python MCP Inspector:")
    print("  mcp-inspector python -m stork_agent.mcp_server.server")
    print()
    print("按 Ctrl+C 停止服务器")
    print("=" * 60)
    print()

    try:
        await server_main()
    except KeyboardInterrupt:
        print("\n服务器已停止")


def test_tool_list():
    """
    测试工具列表功能（不启动服务器）

    验证所有工具都能正确列出
    """
    from stork_agent.mcp_server.server import list_tools
    from mcp.types import Tool

    print("\n" + "=" * 60)
    print("测试工具列表")
    print("=" * 60)

    # 这是一个同步函数，但被定义为 async
    # 我们需要用 asyncio 来运行它
    async def _test():
        tools_result = await list_tools()
        print(f"\n找到 {len(tools_result)} 个工具:\n")

        for tool in tools_result:
            print(f"工具名称: {tool.name}")
            print(f"描述: {tool.description[:80]}...")
            print(f"必需参数: {tool.inputSchema.get('required', [])}")
            print("-" * 60)

        return tools_result

    tools_result = asyncio.run(_test())

    # 验证所有预期的工具都存在
    expected_tools = [
        "stork_query_stock",
        "stork_screen_stocks",
        "stork_next_page",
        "stork_prev_page",
        "stork_export_current_result",
        "stork_compare_stocks",
        "stork_get_stock_history",
        "stork_search_stocks",
        "stork_get_financials",
        "stork_calculate_indicator",
        "stork_get_market_summary",
    ]

    actual_tools = [tool.name for tool in tools_result]

    print("\n工具验证:")
    print("-" * 60)
    for expected in expected_tools:
        if expected in actual_tools:
            print(f"[OK] {expected}")
        else:
            print(f"[X] {expected} - 缺失!")

    missing = set(expected_tools) - set(actual_tools)
    extra = set(actual_tools) - set(expected_tools)

    if missing:
        print(f"\n[WARNING] 缺失的工具: {missing}")
    if extra:
        print(f"\n[WARNING] 额外的工具: {extra}")

    if not missing and not extra:
        print("\n[SUCCESS] 所有工具都正确注册!")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Stork Agent MCP Inspector 测试")
    parser.add_argument(
        "--test-list",
        action="store_true",
        help="测试工具列表（不启动服务器）"
    )
    parser.add_argument(
        "--server",
        action="store_true",
        help="启动服务器供 Inspector 连接"
    )

    args = parser.parse_args()

    if args.test_list:
        test_tool_list()
    elif args.server:
        asyncio.run(run_inspector_test())
    else:
        print("请使用 --test-list 或 --server 参数")
        print("  --test-list: 测试工具列表")
        print("  --server:    启动服务器")
