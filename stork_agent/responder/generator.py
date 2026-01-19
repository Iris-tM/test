"""
主生成器

根据意图和数据生成自然语言回复
"""

from typing import Dict, Optional
from stork_agent.responder.formatter import (
    format_stock_quote,
    format_stock_list,
    format_comparison,
    format_history_data,
    format_financial_data,
    format_indicator_data,
    format_chart_response,
)
from stork_agent.responder.chart_decider import (
    should_generate_chart,
    get_chart_type,
    get_chart_title,
)
from stork_agent.cache.manager import get_cache_manager


def generate_response(
    intent: str,
    data: Dict,
    include_chart: bool = False,
    chart_path: Optional[str] = None,
) -> str:
    """
    根据意图和数据生成自然语言回复

    Args:
        intent: 查询意图
        data: 数据字典
        include_chart: 是否包含图表
        chart_path: 图表文件路径

    Returns:
        格式化后的文本回复
    """
    intent = intent.lower()

    # 根据意图类型选择格式化器
    if intent in {"realtime", "quote", "price", "stock"}:
        text = format_stock_quote(data)
    elif intent in {"list", "screen", "screener", "filter"}:
        page = data.get("page", 1)
        page_size = data.get("page_size", 50)
        total = data.get("total", len(data.get("stocks", [])))
        stocks = data.get("stocks", [])
        text = format_stock_list(stocks, page, page_size, total)
    elif intent in {"history", "kline", "candlestick"}:
        text = format_history_data(data)
    elif intent in {"financial", "finance"}:
        text = format_financial_data(data)
    elif intent in {"compare", "comparison"}:
        text = format_comparison(data)
    elif intent in {"indicator", "ma", "macd", "rsi", "boll"}:
        text = format_indicator_data(data)
    elif intent in {"market", "summary"}:
        text = _format_market_summary(data)
    elif intent in {"search"}:
        stocks = data.get("stocks", [])
        text = format_stock_list(stocks)
    else:
        # 默认格式化
        text = _format_default(data)

    # 添加图表信息
    if include_chart and chart_path:
        title = get_chart_title(intent, data)
        chart_text = format_chart_response(chart_path, title)
        text = f"{text}\n\n---\n\n{chart_text}"

    return text


def _format_market_summary(data: Dict) -> str:
    """
    格式化市场概览

    Args:
        data: 市场概览数据

    Returns:
        格式化后的文本
    """
    lines = ["## 市场概览", ""]

    # 主要指数
    indices = data.get("indices", [])
    if indices:
        lines.append("### 主要指数")
        for idx in indices:
            name = idx.get("name", "")
            price = idx.get("price", 0)
            change_pct = idx.get("change_pct", 0)
            sign = "+" if change_pct > 0 else ""
            lines.append(f"- **{name}**: {price:.2f} ({sign}{change_pct:.2f}%)")

    # 统计信息
    total = data.get("total_stocks", 0)
    if total:
        lines.append("")
        lines.append(f"### 市场统计")
        lines.append(f"- A股总数: {total} 只")

    return "\n".join(lines)


def _format_default(data: Dict) -> str:
    """
    默认格式化

    Args:
        data: 数据字典

    Returns:
        格式化后的文本
    """
    lines = ["## 查询结果", ""]

    for key, value in data.items():
        if key == "stocks" and isinstance(value, list):
            # 股票列表
            lines.append(format_stock_list(value))
        elif key == "data" and isinstance(value, list):
            # 数据列表
            lines.append(f"- 共 {len(value)} 条数据")
        elif isinstance(value, (int, float)):
            lines.append(f"- {key}: {value}")
        elif isinstance(value, str):
            lines.append(f"- {key}: {value}")
        elif value is None:
            lines.append(f"- {key}: N/A")

    return "\n".join(lines)


def generate_error_response(error: str, context: Optional[str] = None) -> str:
    """
    生成错误响应

    Args:
        error: 错误信息
        context: 错误上下文

    Returns:
        格式化后的错误文本
    """
    lines = ["## 查询失败", ""]
    lines.append(f"**错误**: {error}")

    if context:
        lines.append("")
        lines.append(f"**上下文**: {context}")

    lines.append("")
    lines.append("请检查：")
    lines.append("1. 股票代码是否正确（6位数字）")
    lines.append("2. 网络连接是否正常")
    lines.append("3. 数据源服务是否可用")

    return "\n".join(lines)


def generate_success_response(message: str, data: Optional[Dict] = None) -> str:
    """
    生成成功响应

    Args:
        message: 成功消息
        data: 附加数据

    Returns:
        格式化后的成功文本
    """
    lines = [f"**{message}**", ""]

    if data:
        for key, value in data.items():
            if isinstance(value, (int, float)):
                lines.append(f"- {key}: {value}")
            elif isinstance(value, str):
                lines.append(f"- {key}: {value}")

    return "\n".join(lines)
