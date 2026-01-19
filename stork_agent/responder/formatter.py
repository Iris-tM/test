"""
数据格式化工具

将结构化数据格式化为自然语言或 Markdown 表格
"""

from typing import Dict, List, Optional
from datetime import datetime


def format_number(value: Optional[float], decimals: int = 2) -> str:
    """
    格式化数字

    Args:
        value: 数值
        decimals: 小数位数

    Returns:
        格式化后的字符串
    """
    if value is None:
        return "N/A"
    return f"{value:.{decimals}f}"


def format_percentage(value: Optional[float], decimals: int = 2) -> str:
    """
    格式化百分比

    Args:
        value: 数值
        decimals: 小数位数

    Returns:
        格式化后的百分比字符串
    """
    if value is None:
        return "N/A"
    sign = "+" if value > 0 else ""
    return f"{sign}{value:.{decimals}f}%"


def format_market_cap(cap: Optional[float]) -> str:
    """
    格式化市值

    Args:
        cap: 市值（亿元）

    Returns:
        格式化后的市值字符串
    """
    if cap is None:
        return "N/A"
    if cap >= 10000:
        return f"{cap / 10000:.2f}万亿"
    return f"{cap:.2f}亿"


def format_volume(vol: Optional[float]) -> str:
    """
    格式化成交量

    Args:
        vol: 成交量（手）

    Returns:
        格式化后的成交量字符串
    """
    if vol is None:
        return "N/A"
    if vol >= 100000000:
        return f"{vol / 100000000:.2f}亿手"
    elif vol >= 10000:
        return f"{vol / 10000:.2f}万手"
    return f"{vol:.0f}手"


def format_stock_quote(data: Dict) -> str:
    """
    格式化股票行情为自然语言

    Args:
        data: 股票行情数据字典

    Returns:
        格式化后的文本
    """
    name = data.get("name", "未知")
    code = data.get("code", "")
    price = data.get("price", 0)
    change = data.get("change", 0)
    change_pct = data.get("change_pct", 0)
    open_price = data.get("open", 0)
    high = data.get("high", 0)
    low = data.get("low", 0)
    volume = data.get("volume", 0)
    pe = data.get("pe_ratio")
    pb = data.get("pb_ratio")
    market_cap = data.get("market_cap")

    lines = [
        f"## {name} ({code})",
        "",
        f"**当前价格**: ¥{format_number(price)}",
        f"**涨跌**: {format_percentage(change_pct)} ({format_number(change)})",
        "",
        "### 今日行情",
        f"- 开盘: ¥{format_number(open_price)}",
        f"- 最高: ¥{format_number(high)}",
        f"- 最低: ¥{format_number(low)}",
        f"- 成交量: {format_volume(volume)}",
    ]

    # 估值指标
    if pe is not None or pb is not None or market_cap is not None:
        lines.append("")
        lines.append("### 估值指标")
        if pe is not None:
            lines.append(f"- 市盈率(PE): {format_number(pe)}")
        if pb is not None:
            lines.append(f"- 市净率(PB): {format_number(pb)}")
        if market_cap is not None:
            lines.append(f"- 总市值: {format_market_cap(market_cap)}")

    return "\n".join(lines)


def format_stock_list(
    stocks: List[Dict],
    page: int = 1,
    page_size: int = 50,
    total: Optional[int] = None
) -> str:
    """
    格式化股票列表为 Markdown 表格

    Args:
        stocks: 股票列表
        page: 当前页码
        page_size: 每页数量
        total: 总数量（用于计算分页）

    Returns:
        格式化后的 Markdown 表格
    """
    if not stocks:
        return "没有找到符合条件的股票。"

    # 表头
    headers = ["代码", "名称", "价格", "涨跌幅", "PE", "市值"]
    rows = []

    for stock in stocks:
        row = [
            stock.get("code", ""),
            stock.get("name", ""),
            f"¥{format_number(stock.get('price', 0))}",
            format_percentage(stock.get("change_pct", 0)),
            format_number(stock.get("pe_ratio")),
            format_market_cap(stock.get("market_cap")),
        ]
        rows.append(row)

    # 构建 Markdown 表格
    lines = []
    lines.append(" | ".join(headers))
    lines.append(" | ".join(["---"] * len(headers)))
    for row in rows:
        lines.append(" | ".join(row))

    # 分页信息
    if total is not None and total > len(stocks):
        total_pages = (total + page_size - 1) // page_size
        lines.append("")
        lines.append(f"**共 {total} 只股票，当前第 {page}/{total_pages} 页**")
        lines.append(f"输入 `下一页` 查看更多结果")

    return "\n".join(lines)


def format_comparison(data: Dict) -> str:
    """
    格式化对比结果为 Markdown 表格

    Args:
        data: 对比数据字典，包含 stocks 列表

    Returns:
        格式化后的 Markdown 表格
    """
    stocks = data.get("stocks", [])

    if not stocks:
        return "没有可对比的股票数据。"

    # 定义要对比的指标
    metrics = [
        ("code", "代码"),
        ("name", "名称"),
        ("price", "价格"),
        ("change_pct", "涨跌幅"),
        ("pe_ratio", "PE"),
        ("pb_ratio", "PB"),
        ("roe", "ROE(%)"),
        ("market_cap", "市值(亿)"),
    ]

    # 表头
    headers = [metric[1] for metric in metrics]
    lines = []
    lines.append(" | ".join(headers))
    lines.append(" | ".join(["---"] * len(headers)))

    # 数据行
    for stock in stocks:
        row = []
        for key, _ in metrics:
            value = stock.get(key)
            if key == "change_pct":
                row.append(format_percentage(value))
            elif key == "market_cap":
                row.append(format_number(value))
            elif key in ["pe_ratio", "pb_ratio", "roe"]:
                row.append(format_number(value))
            elif key == "price":
                row.append(f"¥{format_number(value)}")
            else:
                row.append(str(value) if value is not None else "N/A")
        lines.append(" | ".join(row))

    return "\n".join(lines)


def format_chart_response(chart_path: str, title: str) -> str:
    """
    格式化图表响应

    Args:
        chart_path: HTML 图表文件路径
        title: 图表标题

    Returns:
        格式化后的响应文本
    """
    # 转换为相对路径或绝对路径
    if not chart_path.startswith(("http://", "https://", "/")):
        # 转换为绝对路径
        import os
        chart_path = os.path.abspath(chart_path)

    lines = [
        f"## {title}",
        "",
        f"图表已生成：[{chart_path}]({chart_path})",
        "",
        "点击链接在浏览器中查看交互式图表。",
    ]

    return "\n".join(lines)


def format_history_data(data: Dict) -> str:
    """
    格式化历史数据为 Markdown

    Args:
        data: 历史数据字典

    Returns:
        格式化后的文本
    """
    name = data.get("name", "")
    code = data.get("code", "")
    count = data.get("count", 0)
    period = data.get("period", "daily")

    period_map = {
        "daily": "日",
        "weekly": "周",
        "monthly": "月",
    }

    lines = [
        f"## {name} ({code})",
        "",
        f"**数据周期**: {period_map.get(period, period)}线",
        f"**数据条数**: {count} 条",
        "",
    ]

    # 添加最新数据
    bars = data.get("data", [])
    if bars:
        latest = bars[-1]
        lines.append("### 最新行情")
        lines.append(f"- 日期: {latest.get('date', '')}")
        lines.append(f"- 收盘: ¥{format_number(latest.get('close', 0))}")
        lines.append(f"- 涨跌幅: {format_percentage(latest.get('change_pct', 0))}")

    return "\n".join(lines)


def format_financial_data(data: Dict) -> str:
    """
    格式化财务数据为 Markdown

    Args:
        data: 财务数据字典

    Returns:
        格式化后的文本
    """
    name = data.get("name", "")
    code = data.get("code", "")
    report_date = data.get("report_date", "")

    lines = [
        f"## {name} ({code}) 财务数据",
        "",
        f"**报告期**: {report_date}",
        "",
        "### 主要指标",
    ]

    metrics = [
        ("revenue", "营业收入", "亿元"),
        ("net_profit", "净利润", "亿元"),
        ("eps", "每股收益", "元"),
        ("bps", "每股净资产", "元"),
        ("roe", "净资产收益率", "%"),
        ("debt_ratio", "资产负债率", "%"),
    ]

    for key, label, unit in metrics:
        value = data.get(key)
        if value is not None:
            lines.append(f"- {label}: {format_number(value)} {unit}")

    return "\n".join(lines)


def format_indicator_data(data: Dict) -> str:
    """
    格式化技术指标数据为 Markdown

    Args:
        data: 指标数据字典

    Returns:
        格式化后的文本
    """
    name = data.get("name", "")
    code = data.get("code", "")
    indicator = data.get("indicator", "")
    description = data.get("description", "")

    lines = [
        f"## {name} ({code})",
        "",
        f"**指标**: {indicator} - {description}",
        "",
    ]

    # 添加最新值
    points = data.get("data", [])
    if points:
        latest = points[-1]
        lines.append("### 最新值")
        lines.append(f"- 日期: {latest.get('date', '')}")

        # 根据不同指标显示不同字段
        if "value" in latest:
            lines.append(f"- 指标值: {format_number(latest['value'])}")
        if "dif" in latest:
            lines.append(f"- DIF: {format_number(latest['dif'])}")
            lines.append(f"- DEA: {format_number(latest['dea'])}")
            lines.append(f"- BAR: {format_number(latest['bar'])}")
        if "upper" in latest:
            lines.append(f"- 上轨: {format_number(latest['upper'])}")
            lines.append(f"- 中轨: {format_number(latest['middle'])}")
            lines.append(f"- 下轨: {format_number(latest['lower'])}")

    return "\n".join(lines)
