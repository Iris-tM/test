"""
回答生成模块

将结构化数据转换为自然语言回复，支持分页和图表决策
"""

from .formatter import format_stock_quote, format_stock_list, format_comparison, format_chart_response
from .chart_decider import should_generate_chart, get_chart_type
from .generator import generate_response
from .exporter import export_data

__all__ = [
    "format_stock_quote",
    "format_stock_list",
    "format_comparison",
    "format_chart_response",
    "should_generate_chart",
    "get_chart_type",
    "generate_response",
    "export_data",
]
