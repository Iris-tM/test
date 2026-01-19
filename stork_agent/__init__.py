"""
Stork Agent - A股智能选股助手

基于 AkShare 的 A股数据查询和选股分析工具
"""

__version__ = "0.1.0"

# Export agent tools for easy access
from stork_agent.agent.tools import (
    get_stock_realtime,
    get_stock_history,
    screen_stocks,
    compare_stocks,
    get_financials,
    calculate_indicator,
)

__all__ = [
    "get_stock_realtime",
    "get_stock_history",
    "screen_stocks",
    "compare_stocks",
    "get_financials",
    "calculate_indicator",
]
