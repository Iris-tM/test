"""
辅助函数模块

提供通用的辅助功能
"""

import re
from typing import Optional, List, Dict
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
    return f"{value:.{decimals}f}%"


def format_volume(volume: Optional[float]) -> str:
    """
    格式化成交量

    Args:
        volume: 成交量

    Returns:
        格式化后的成交量字符串
    """
    if volume is None:
        return "N/A"

    if volume >= 100000000:
        return f"{volume / 100000000:.2f}亿"
    elif volume >= 10000:
        return f"{volume / 10000:.2f}万"
    else:
        return f"{volume:.0f}"


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
    else:
        return f"{cap:.2f}亿"


def parse_stock_code(code: str) -> tuple:
    """
    解析股票代码，返回代码和市场

    Args:
        code: 股票代码

    Returns:
        (代码, 市场) 元组
    """
    code = code.strip().upper()

    # 如果包含市场前缀
    if code.startswith("SH"):
        return code[2:], "SH"
    elif code.startswith("SZ"):
        return code[2:], "SZ"

    # 根据代码判断市场
    if code.startswith("6"):
        return code.zfill(6), "SH"
    elif code.startswith(("0", "3")):
        return code.zfill(6), "SZ"
    else:
        return code.zfill(6), "UNKNOWN"


def validate_stock_code(code: str) -> bool:
    """
    验证股票代码格式

    Args:
        code: 股票代码

    Returns:
        是否有效
    """
    # 移除市场前缀
    code = code.strip().upper()
    if code.startswith(("SH", "SZ")):
        code = code[2:]

    # 检查是否为6位数字
    return bool(re.match(r"^\d{6}$", code))


def calculate_return(start_price: float, end_price: float) -> Dict[str, float]:
    """
    计算收益率

    Args:
        start_price: 起始价格
        end_price: 结束价格

    Returns:
        包含收益率和涨跌额的字典
    """
    change = end_price - start_price
    change_pct = (change / start_price) * 100 if start_price != 0 else 0

    return {
        "change": change,
        "change_pct": change_pct
    }


def get_period_desc(days: int) -> str:
    """
    获取周期描述

    Args:
        days: 天数

    Returns:
        周期描述字符串
    """
    if days < 7:
        return f"{days}天"
    elif days < 30:
        return f"{days // 7}周"
    elif days < 365:
        return f"{days // 30}个月"
    else:
        return f"{days // 365}年"


def merge_dicts(*dicts: Dict) -> Dict:
    """
    合并多个字典

    Args:
        *dicts: 字典列表

    Returns:
        合并后的字典
    """
    result = {}
    for d in dicts:
        result.update(d)
    return result


def chunks(lst: List, n: int) -> List[List]:
    """
    将列表分割成块

    Args:
        lst: 列表
        n: 块大小

    Returns:
        分割后的列表
    """
    return [lst[i:i + n] for i in range(0, len(lst), n)]


def safe_divide(a: Optional[float], b: Optional[float], default: float = 0) -> float:
    """
    安全除法

    Args:
        a: 被除数
        b: 除数
        default: 默认值

    Returns:
        除法结果
    """
    if a is None or b is None or b == 0:
        return default
    return a / b


def color_change(value: float) -> str:
    """
    根据涨跌返回颜色标识

    Args:
        value: 涨跌幅值

    Returns:
        颜色标识 (up/down/flat)
    """
    if value > 0:
        return "up"
    elif value < 0:
        return "down"
    else:
        return "flat"


def truncate_string(s: str, max_length: int = 20, suffix: str = "...") -> str:
    """
    截断字符串

    Args:
        s: 原字符串
        max_length: 最大长度
        suffix: 后缀

    Returns:
        截断后的字符串
    """
    if len(s) <= max_length:
        return s
    return s[:max_length - len(suffix)] + suffix
