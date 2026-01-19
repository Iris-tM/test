"""
技术指标计算模块

实现常用技术指标的计算
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Optional


def calculate_ma(prices: List[float], period: int) -> List[Optional[float]]:
    """
    计算移动平均线 (MA)

    Args:
        prices: 价格列表
        period: 周期

    Returns:
        MA 值列表，前面不足周期部分为 None
    """
    ma_values = []
    for i in range(len(prices)):
        if i < period - 1:
            ma_values.append(None)
        else:
            ma = sum(prices[i - period + 1:i + 1]) / period
            ma_values.append(ma)
    return ma_values


def calculate_ema(prices: List[float], period: int) -> List[float]:
    """
    计算指数移动平均线 (EMA)

    Args:
        prices: 价格列表
        period: 周期

    Returns:
        EMA 值列表
    """
    ema_values = []
    multiplier = 2 / (period + 1)

    # 第一个 EMA 使用 SMA
    if len(prices) >= period:
        first_ema = sum(prices[:period]) / period
        for i in range(period - 1):
            ema_values.append(prices[i])
    else:
        return prices.copy()

    ema_values.append(first_ema)

    # 后续 EMA
    for i in range(period, len(prices)):
        ema = (prices[i] - ema_values[-1]) * multiplier + ema_values[-1]
        ema_values.append(ema)

    return ema_values


def calculate_macd(
    prices: List[float],
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9
) -> Dict[str, List[float]]:
    """
    计算 MACD 指标

    Args:
        prices: 价格列表
        fast_period: 快线周期
        slow_period: 慢线周期
        signal_period: 信号线周期

    Returns:
        包含 dif, dea, bar 的字典
    """
    # 计算 EMA
    ema_fast = calculate_ema(prices, fast_period)
    ema_slow = calculate_ema(prices, slow_period)

    # 计算 DIF
    dif = [ema_fast[i] - ema_slow[i] for i in range(len(prices))]

    # 计算 DEA (DIF 的 EMA)
    dea = calculate_ema(dif, signal_period)

    # 计算 MACD 柱
    bar = [(dif[i] - dea[i]) * 2 for i in range(len(prices))]

    return {
        "dif": dif,
        "dea": dea,
        "bar": bar
    }


def calculate_rsi(prices: List[float], period: int = 14) -> List[Optional[float]]:
    """
    计算 RSI 相对强弱指标

    Args:
        prices: 价格列表
        period: 周期

    Returns:
        RSI 值列表，前面不足周期部分为 None
    """
    rsi_values = []

    # 计算价格变化
    deltas = [prices[i] - prices[i - 1] for i in range(1, len(prices))]

    for i in range(len(deltas)):
        if i < period:
            rsi_values.append(None)
        else:
            # 计算涨幅和跌幅
            gains = [max(d, 0) for d in deltas[i - period + 1:i + 1]]
            losses = [abs(min(d, 0)) for d in deltas[i - period + 1:i + 1]]

            avg_gain = sum(gains) / period
            avg_loss = sum(losses) / period

            if avg_loss == 0:
                rsi = 100
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))

            rsi_values.append(rsi)

    # 在前面补一个 None 以保持长度一致
    rsi_values.insert(0, None)

    return rsi_values


def calculate_bollinger_bands(
    prices: List[float],
    period: int = 20,
    std_dev: float = 2.0
) -> Dict[str, List[Optional[float]]]:
    """
    计算布林带 (BOLL)

    Args:
        prices: 价格列表
        period: 周期
        std_dev: 标准差倍数

    Returns:
        包含 upper, middle, lower 的字典
    """
    middle = calculate_ma(prices, period)
    upper = []
    lower = []

    for i in range(len(prices)):
        if i < period - 1:
            upper.append(None)
            lower.append(None)
        else:
            # 计算标准差
            window = prices[i - period + 1:i + 1]
            std = np.std(window)

            upper.append(middle[i] + std_dev * std)
            lower.append(middle[i] - std_dev * std)

    return {
        "upper": upper,
        "middle": middle,
        "lower": lower
    }


def calculate_kdj(
    highs: List[float],
    lows: List[float],
    closes: List[float],
    n: int = 9,
    m1: int = 3,
    m2: int = 3
) -> Dict[str, List[Optional[float]]]:
    """
    计算 KDJ 指标

    Args:
        highs: 最高价列表
        lows: 最低价列表
        closes: 收盘价列表
        n: RSV 周期
        m1: K 值平滑周期
        m2: D 值平滑周期

    Returns:
        包含 k, d, j 的字典
    """
    k_values = [50]  # 初始值
    d_values = [50]  # 初始值
    j_values = [50]  # 初始值

    for i in range(n, len(closes)):
        # 计算 RSV
        high_n = max(highs[i - n + 1:i + 1])
        low_n = min(lows[i - n + 1:i + 1])

        if high_n == low_n:
            rsv = 50
        else:
            rsv = (closes[i] - low_n) / (high_n - low_n) * 100

        # 计算 K
        k = (2 / 3) * k_values[-1] + (1 / 3) * rsv
        k_values.append(k)

        # 计算 D
        d = (2 / 3) * d_values[-1] + (1 / 3) * k
        d_values.append(d)

        # 计算 J
        j = 3 * k - 2 * d
        j_values.append(j)

    # 在前面补 None 以保持长度一致
    for _ in range(n):
        k_values.insert(0, None)
        d_values.insert(0, None)
        j_values.insert(0, None)

    return {
        "k": k_values,
        "d": d_values,
        "j": j_values
    }


def atr(prices: List[float], highs: List[float], lows: List[float], period: int = 14) -> List[float]:
    """
    计算平均真实波幅 (ATR)

    Args:
        prices: 收盘价列表
        highs: 最高价列表
        lows: 最低价列表
        period: 周期

    Returns:
        ATR 值列表
    """
    tr_values = []

    for i in range(len(prices)):
        if i == 0:
            tr = highs[i] - lows[i]
        else:
            hl = highs[i] - lows[i]
            hc = abs(highs[i] - prices[i - 1])
            lc = abs(lows[i] - prices[i - 1])
            tr = max(hl, hc, lc)

        tr_values.append(tr)

    # 计算 ATR (使用 EMA)
    atr_values = calculate_ema(tr_values, period)

    return atr_values


def calculate_volume_ma(volumes: List[float], period: int = 5) -> List[Optional[float]]:
    """
    计算成交量移动平均

    Args:
        volumes: 成交量列表
        period: 周期

    Returns:
        成交量MA值列表
    """
    return calculate_ma(volumes, period)


def obv(prices: List[float], volumes: List[float]) -> List[float]:
    """
    计算能量潮 (OBV)

    Args:
        prices: 价格列表
        volumes: 成交量列表

    Returns:
        OBV 值列表
    """
    obv_values = [volumes[0]]

    for i in range(1, len(prices)):
        if prices[i] > prices[i - 1]:
            obv_values.append(obv_values[-1] + volumes[i])
        elif prices[i] < prices[i - 1]:
            obv_values.append(obv_values[-1] - volumes[i])
        else:
            obv_values.append(obv_values[-1])

    return obv_values
