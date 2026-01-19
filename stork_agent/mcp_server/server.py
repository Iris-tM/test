"""
MCP 服务器入口

实现 Model Context Protocol，将股票分析功能暴露为 Claude 可调用的工具
直接使用 asyncio 实现，避免 anyio 兼容性问题
"""

import asyncio
import sys
import os
from typing import Any

# 添加项目路径到 sys.path
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

# 使用绝对导入避免命名冲突
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions
from mcp.types import TextContent

# 导入 tools 时也使用绝对导入
import sys
sys.path.insert(0, project_dir)
from stork_agent.mcp_server import tools


# 创建 MCP 服务器实例
server = Server("stork-agent")


@server.list_resources()
async def list_resources() -> list[str]:
    """列出可用资源"""
    return []


@server.list_tools()
async def list_tools():
    """列出所有可用工具，带 MCP 注解"""
    from mcp.types import Tool

    return [
        Tool(
            name="stork_query_stock",
            description="查询股票实时行情信息。输入股票代码（如 600519）返回当前价格、涨跌幅、成交量等数据。",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "股票代码，6位数字，如 600519（贵州茅台）"
                    }
                },
                "required": ["code"]
            }
        ),
        Tool(
            name="stork_screen_stocks",
            description="根据条件筛选股票。支持市盈率、市值、涨跌幅等多维度筛选，返回符合条件的股票列表（支持分页）。",
            inputSchema={
                "type": "object",
                "properties": {
                    "criteria": {
                        "type": "object",
                        "description": "筛选条件",
                        "properties": {
                            "pe_min": {"type": "number", "description": "最小市盈率"},
                            "pe_max": {"type": "number", "description": "最大市盈率"},
                            "pb_min": {"type": "number", "description": "最小市净率"},
                            "pb_max": {"type": "number", "description": "最大市净率"},
                            "market_cap_min": {"type": "number", "description": "最小市值（亿元）"},
                            "market_cap_max": {"type": "number", "description": "最大市值（亿元）"},
                            "change_min": {"type": "number", "description": "最小涨跌幅(%)"},
                            "change_max": {"type": "number", "description": "最大涨跌幅(%)"},
                            "industry": {"type": "string", "description": "行业筛选"},
                            "turnover_min": {"type": "number", "description": "最小换手率(%)"},
                            "turnover_max": {"type": "number", "description": "最大换手率(%)"},
                        }
                    },
                    "page": {"type": "number", "description": "页码，默认为 1", "default": 1},
                    "page_size": {"type": "number", "description": "每页数量，默认为 50", "default": 50}
                },
                "required": ["criteria"]
            }
        ),
        Tool(
            name="stork_next_page",
            description="查看当前筛选或搜索结果的下一页数据。需要先执行 screen_stocks 或 search_stocks。",
            inputSchema={"type": "object", "properties": {}, "required": []}
        ),
        Tool(
            name="stork_prev_page",
            description="查看当前筛选或搜索结果的上一页数据。需要先执行 screen_stocks 或 search_stocks。",
            inputSchema={"type": "object", "properties": {}, "required": []}
        ),
        Tool(
            name="stork_export_current_result",
            description="导出当前查询的完整数据到文件。支持 CSV、Excel、JSON 格式。需要先执行筛选或搜索操作。",
            inputSchema={
                "type": "object",
                "properties": {
                    "format": {
                        "type": "string",
                        "description": "导出格式：csv、excel 或 json",
                        "enum": ["csv", "excel", "json"],
                        "default": "csv"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="stork_compare_stocks",
            description="对比多只股票的关键指标。输入股票代码列表，返回市值、PE、ROE 等指标对比表格。",
            inputSchema={
                "type": "object",
                "properties": {
                    "codes": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "股票代码列表，如 [\"600519\", \"000858\"]"
                    },
                    "days": {"type": "number", "description": "对比天数，用于计算涨跌幅", "default": 30}
                },
                "required": ["codes"]
            }
        ),
        Tool(
            name="stork_get_stock_history",
            description="获取股票历史K线数据。返回指定天数内的开盘、收盘、最高、最低价等信息。支持日线、周线、月线。",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "股票代码"},
                    "days": {"type": "number", "description": "获取天数", "default": 30},
                    "period": {
                        "type": "string",
                        "description": "周期：daily（日线）、weekly（周线）、monthly（月线）",
                        "enum": ["daily", "weekly", "monthly"],
                        "default": "daily"
                    }
                },
                "required": ["code"]
            }
        ),
        Tool(
            name="stork_search_stocks",
            description="搜索股票。支持按代码或名称模糊搜索。返回匹配的股票列表（支持分页）。",
            inputSchema={
                "type": "object",
                "properties": {
                    "keyword": {"type": "string", "description": "搜索关键词，可以是股票代码或名称"},
                    "limit": {"type": "number", "description": "返回结果数量", "default": 10}
                },
                "required": ["keyword"]
            }
        ),
        Tool(
            name="stork_get_financials",
            description="获取股票财务数据。包括营收、净利润、ROE、资产负债率等财务指标。",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "股票代码"}
                },
                "required": ["code"]
            }
        ),
        Tool(
            name="stork_calculate_indicator",
            description="计算技术指标。支持 MA（移动平均线）、MACD、RSI（相对强弱指标）、BOLL（布林带）等常用技术指标。",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "股票代码"},
                    "indicator": {
                        "type": "string",
                        "description": "指标类型：ma（移动平均线）、macd、rsi、boll（布林带）",
                        "enum": ["ma", "macd", "rsi", "boll"]
                    },
                    "period": {"type": "number", "description": "计算周期，默认为 20", "default": 20}
                },
                "required": ["code", "indicator"]
            }
        ),
        Tool(
            name="stork_get_market_summary",
            description="获取市场概览。包括上证指数、深证成指、创业板指等主要指数表现和市场统计数据。",
            inputSchema={"type": "object", "properties": {}, "required": []}
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """处理工具调用"""

    try:
        # 映射工具名称到函数（使用 stork_ 前缀避免命名冲突）
        tool_functions = {
            "stork_query_stock": lambda: tools.query_stock(
                code=arguments.get("code", "")
            ),
            "stork_screen_stocks": lambda: tools.screen_stocks(
                criteria=arguments.get("criteria", {}),
                page=arguments.get("page", 1),
                page_size=arguments.get("page_size", 50)
            ),
            "stork_next_page": lambda: tools.next_page(),
            "stork_prev_page": lambda: tools.prev_page(),
            "stork_export_current_result": lambda: tools.export_current_result(
                format=arguments.get("format", "csv")
            ),
            "stork_compare_stocks": lambda: tools.compare_stocks(
                codes=arguments.get("codes", []),
                days=arguments.get("days", 30)
            ),
            "stork_get_stock_history": lambda: tools.get_stock_history(
                code=arguments.get("code", ""),
                days=arguments.get("days", 30),
                period=arguments.get("period", "daily")
            ),
            "stork_search_stocks": lambda: tools.search_stocks(
                keyword=arguments.get("keyword", ""),
                limit=arguments.get("limit", 10)
            ),
            "stork_get_financials": lambda: tools.get_financials(
                code=arguments.get("code", "")
            ),
            "stork_calculate_indicator": lambda: tools.calculate_indicator(
                code=arguments.get("code", ""),
                indicator=arguments.get("indicator", ""),
                period=arguments.get("period", 20)
            ),
            "stork_get_market_summary": lambda: tools.get_market_summary(),
        }

        if name not in tool_functions:
            return [TextContent(
                type="text",
                text=f"未知工具: {name}"
            )]

        # 执行工具函数
        result = tool_functions[name]()

        return [TextContent(
            type="text",
            text=result
        )]

    except Exception as e:
        import traceback
        error_msg = f"工具执行出错 ({name}): {str(e)}\n\n{traceback.format_exc()}"
        return [TextContent(
            type="text",
            text=error_msg
        )]


async def main():
    """启动 MCP 服务器"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="stork-agent",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
