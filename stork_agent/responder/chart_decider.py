"""
图表决策器

根据查询意图和数据特征，决定是否生成图表以及生成何种类型的图表
"""

from typing import Dict, Optional


def should_generate_chart(intent: str, data: Optional[Dict] = None) -> bool:
    """
    决定是否需要生成图表

    Args:
        intent: 查询意图
        data: 数据字典（可选，用于进一步判断）

    Returns:
        是否需要生成图表
    """
    intent = intent.lower()

    # 明确需要图表的意图
    chart_intents = {
        "kline", "candlestick", "ohlc",
        "chart", "plot", "graph",
        "trend", "走势",
        "对比", "compare", "comparison",
        "份额", "占比", "proportion", "share",
        "macd", "rsi", "boll",
    }

    # 检查意图关键词
    for keyword in chart_intents:
        if keyword in intent:
            return True

    # 检查数据特征
    if data:
        # 时间序列数据
        if "data" in data and isinstance(data["data"], list):
            # 如果有超过5个数据点，考虑生成图表
            if len(data["data"]) > 5:
                data_sample = data["data"][0]
                # 检查是否为时间序列格式（包含 date, open, high, low, close 等）
                if isinstance(data_sample, dict):
                    if any(k in data_sample for k in ["date", "time", "open", "high", "low", "close", "value"]):
                        return True

        # 对比数据
        if "stocks" in data and isinstance(data["stocks"], list) and len(data["stocks"]) > 1:
            return True

    return False


def get_chart_type(intent: str, data: Optional[Dict] = None) -> str:
    """
    根据意图和数据返回图表类型

    Args:
        intent: 查询意图
        data: 数据字典（可选）

    Returns:
        图表类型: 'kline', 'line', 'bar', 'pie', 'indicator'
    """
    intent = intent.lower()

    # K线图
    kline_keywords = {"kline", "candlestick", "ohlc", "蜡烛", "k线"}
    if any(kw in intent for kw in kline_keywords):
        return "kline"

    # 饼图（份额、占比）
    pie_keywords = {"份额", "占比", "比例", "proportion", "share", "pie", "饼图"}
    if any(kw in intent for kw in pie_keywords):
        return "pie"

    # 柱状图（对比）
    bar_keywords = {"对比", "compare", "comparison", "bar"}
    if any(kw in intent for kw in bar_keywords):
        # 如果有多个股票对比数据
        if data and "stocks" in data and len(data.get("stocks", [])) > 1:
            return "bar"

    # 技术指标
    indicator_keywords = {"macd", "rsi", "boll", "kdj", "指标"}
    if any(kw in intent for kw in indicator_keywords):
        return "indicator"

    # 默认折线图（时间序列）
    return "line"


def get_chart_title(intent: str, data: Optional[Dict] = None) -> str:
    """
    生成图表标题

    Args:
        intent: 查询意图
        data: 数据字典（可选）

    Returns:
        图表标题
    """
    if data:
        name = data.get("name", "")
        code = data.get("code", "")

        if name and code:
            base_title = f"{name} ({code})"
        elif code:
            base_title = f"股票 {code}"
        elif name:
            base_title = name
        else:
            base_title = "股票数据"

        # 根据意图添加后缀
        intent = intent.lower()
        if "kline" in intent or "candlestick" in intent:
            return f"{base_title} - K线图"
        elif "trend" in intent or "走势" in intent:
            return f"{base_title} - 价格走势"
        elif "macd" in intent:
            return f"{base_title} - MACD指标"
        elif "rsi" in intent:
            return f"{base_title} - RSI指标"
        elif "boll" in intent:
            return f"{base_title} - 布林带"
        elif "对比" in intent or "compare" in intent:
            return "股票指标对比"
        else:
            return base_title

    return "股票图表"


def get_max_data_points(chart_type: str) -> int:
    """
    获取不同图表类型的最大数据点数

    Args:
        chart_type: 图表类型

    Returns:
        最大数据点数
    """
    limits = {
        "kline": 5000,
        "line": 5000,
        "bar": 100,
        "pie": 20,
        "indicator": 5000,
    }
    return limits.get(chart_type, 5000)


def should_limit_data_points(intent: str, data: Optional[Dict] = None) -> bool:
    """
    判断是否需要限制数据点数量

    Args:
        intent: 查询意图
        data: 数据字典（可选）

    Returns:
        是否需要限制
    """
    chart_type = get_chart_type(intent, data)
    max_points = get_max_data_points(chart_type)

    if data and "data" in data and isinstance(data["data"], list):
        return len(data["data"]) > max_points

    return False
