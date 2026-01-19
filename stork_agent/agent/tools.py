"""
Agent 可调用工具模块

所有工具函数返回结构化数据（dict/JSON），供 AI 系统调用
这是与 AI 系统的主要接口层
"""

from typing import Dict, List, Optional, Union
from stork_agent.data.query import (
    get_realtime_quote,
    get_history_kline,
    get_financial_data,
    batch_get_realtime,
    normalize_stock_code,
)
from stork_agent.data.screener import screen_stocks as screen_stocks_data
from stork_agent.data.comparator import compare_stocks as compare_stocks_data
from stork_agent.analysis.indicators import (
    calculate_ma,
    calculate_macd,
    calculate_rsi,
    calculate_bollinger_bands,
)
from stork_agent.agent.schemas import (
    ApiResponse,
    StockQuote,
    StockHistory,
    ScreeningFilter,
    ScreeningResult,
    StockComparison,
    FinancialData,
    IndicatorData,
)


def get_stock_realtime(code: str) -> ApiResponse:
    """
    获取股票实时行情

    Args:
        code: 股票代码，如 600519

    Returns:
        ApiResponse 格式的实时行情数据

    Example:
        >>> result = get_stock_realtime("600519")
        >>> print(result.data["name"])
        '贵州茅台'
    """
    try:
        data = get_realtime_quote(code)
        return ApiResponse(
            success=True,
            message=f"成功获取 {code} 实时行情",
            data=data
        )
    except Exception as e:
        return ApiResponse(
            success=False,
            message=f"获取实时行情失败",
            error=str(e)
        )


def get_stock_history(
    code: str,
    period: str = "daily",
    days: int = 100,
    adjust: str = "qfq"
) -> ApiResponse:
    """
    获取股票历史K线数据

    Args:
        code: 股票代码
        period: 周期 - daily(日线), weekly(周线), monthly(月线)
        days: 获取天数
        adjust: 复权方式 - qfq(前复权), hfq(后复权), ''(不复权)

    Returns:
        ApiResponse 格式的历史K线数据

    Example:
        >>> result = get_stock_history("600519", period="daily", days=30)
        >>> print(len(result.data["data"]))
        30
    """
    try:
        data = get_history_kline(code, period, days, adjust)
        return ApiResponse(
            success=True,
            message=f"成功获取 {code} 历史数据，共 {data['count']} 条",
            data=data
        )
    except Exception as e:
        return ApiResponse(
            success=False,
            message=f"获取历史数据失败",
            error=str(e)
        )


def get_stock_realtime_batch(codes: List[str]) -> ApiResponse:
    """
    批量获取多只股票的实时行情

    Args:
        codes: 股票代码列表

    Returns:
        ApiResponse 格式的批量行情数据

    Example:
        >>> result = get_stock_realtime_batch(["600519", "000858"])
        >>> print(len(result.data))
        2
    """
    try:
        from stork_agent.data.query import batch_get_realtime
        data = batch_get_realtime(codes)
        return ApiResponse(
            success=True,
            message=f"成功获取 {len(data)} 只股票的实时行情",
            data={"stocks": data}
        )
    except Exception as e:
        return ApiResponse(
            success=False,
            message="批量获取行情失败",
            error=str(e)
        )


def screen_stocks(filters: Union[Dict, ScreeningFilter]) -> ApiResponse:
    """
    按条件筛选股票

    Args:
        filters: 筛选条件字典或 ScreeningFilter 对象
            - pe_min: 最小市盈率
            - pe_max: 最大市盈率
            - pb_min: 最小市净率
            - pb_max: 最大市净率
            - market_cap_min: 最小市值（亿元）
            - market_cap_max: 最大市值（亿元）
            - change_min: 最小涨跌幅(%)
            - change_max: 最大涨跌幅(%)
            - industry: 行业筛选
            - turnover_min: 最小换手率(%)
            - turnover_max: 最大换手率(%)
            - limit: 返回结果数量限制

    Returns:
        ApiResponse 格式的筛选结果

    Example:
        >>> filters = {"pe_max": 20, "market_cap_min": 100}
        >>> result = screen_stocks(filters)
        >>> print(result.data["total"])
        15
    """
    try:
        # 如果是字典，转换为 ScreeningFilter
        if isinstance(filters, dict):
            filter_obj = ScreeningFilter(**filters)
        else:
            filter_obj = filters

        data = screen_stocks_data(filter_obj)
        return ApiResponse(
            success=True,
            message=f"筛选成功，共找到 {data['total']} 只股票",
            data=data
        )
    except Exception as e:
        return ApiResponse(
            success=False,
            message="筛选股票失败",
            error=str(e)
        )


def compare_stocks(codes: List[str], days: int = 30) -> ApiResponse:
    """
    对比多只股票

    Args:
        codes: 股票代码列表
        days: 对比天数（用于计算涨跌幅）

    Returns:
        ApiResponse 格式的对比结果

    Example:
        >>> result = compare_stocks(["600519", "000858"])
        >>> print(result.data["stocks"])
        [{'code': '600519', 'name': '贵州茅台', ...}, ...]
    """
    try:
        data = compare_stocks_data(codes, days)
        return ApiResponse(
            success=True,
            message=f"成功对比 {len(codes)} 只股票",
            data=data
        )
    except Exception as e:
        return ApiResponse(
            success=False,
            message="对比股票失败",
            error=str(e)
        )


def get_financials(code: str) -> ApiResponse:
    """
    获取财务数据

    Args:
        code: 股票代码

    Returns:
        ApiResponse 格式的财务数据

    Example:
        >>> result = get_financials("600519")
        >>> print(result.data["roe"])
        28.5
    """
    try:
        data = get_financial_data(code)
        return ApiResponse(
            success=True,
            message=f"成功获取 {code} 财务数据",
            data=data
        )
    except Exception as e:
        return ApiResponse(
            success=False,
            message="获取财务数据失败",
            error=str(e)
        )


def calculate_indicator(
    code: str,
    indicator: str,
    period: int = 20,
    **kwargs
) -> ApiResponse:
    """
    计算技术指标

    Args:
        code: 股票代码
        indicator: 指标类型 - ma/macd/rsi/boll
        period: 计算周期
        **kwargs: 其他参数

    Returns:
        ApiResponse 格式的指标数据

    Example:
        >>> result = calculate_indicator("600519", "ma", period=20)
        >>> print(result.data["indicator"])
        'MA20'
    """
    try:
        # 获取历史数据
        hist_data = get_history_kline(code, "daily", days=period + 50)

        # 提取收盘价
        closes = [bar["close"] for bar in hist_data["data"]]
        dates = [bar["date"] for bar in hist_data["data"]]

        result = {
            "code": code,
            "name": hist_data.get("name", ""),
            "indicator": indicator.upper()
        }

        if indicator.lower() == "ma":
            # 计算移动平均线
            ma_values = calculate_ma(closes, period)
            result["data"] = [
                {"date": dates[i], "value": ma_values[i]}
                for i in range(len(ma_values)) if ma_values[i] is not None
            ]
            result["description"] = f"MA{period} 移动平均线"

        elif indicator.lower() == "macd":
            # 计算 MACD
            macd_data = calculate_macd(closes, **kwargs)
            result["data"] = [
                {
                    "date": dates[i],
                    "dif": macd_data["dif"][i],
                    "dea": macd_data["dea"][i],
                    "bar": macd_data["bar"][i]
                }
                for i in range(len(macd_data["dif"]))
            ]
            result["description"] = "MACD 指标"

        elif indicator.lower() == "rsi":
            # 计算 RSI
            rsi_values = calculate_rsi(closes, period)
            result["data"] = [
                {"date": dates[i], "value": rsi_values[i]}
                for i in range(len(rsi_values)) if rsi_values[i] is not None
            ]
            result["description"] = f"RSI({period}) 相对强弱指标"

        elif indicator.lower() == "boll":
            # 计算布林带
            boll_data = calculate_bollinger_bands(closes, period)
            result["data"] = [
                {
                    "date": dates[i],
                    "upper": boll_data["upper"][i],
                    "middle": boll_data["middle"][i],
                    "lower": boll_data["lower"][i]
                }
                for i in range(len(boll_data["upper"]))
            ]
            result["description"] = f"BOLL({period}) 布林带"

        else:
            return ApiResponse(
                success=False,
                message=f"不支持的指标类型: {indicator}",
                error=f"支持的指标: ma, macd, rsi, boll"
            )

        return ApiResponse(
            success=True,
            message=f"成功计算 {indicator.upper()} 指标",
            data=result
        )
    except Exception as e:
        return ApiResponse(
            success=False,
            message=f"计算指标失败",
            error=str(e)
        )


def search_stocks(keyword: str, limit: int = 10) -> ApiResponse:
    """
    搜索股票

    Args:
        keyword: 搜索关键词（代码或名称）
        limit: 返回结果数量限制

    Returns:
        ApiResponse 格式的搜索结果
    """
    try:
        from stork_agent.data.query import get_stock_list
        df = get_stock_list()

        # 搜索匹配
        mask = df["code"].str.contains(keyword, na=False) | df["name"].str.contains(keyword, na=False)
        results = df[mask].head(limit)

        stocks = []
        for _, row in results.iterrows():
            stocks.append({
                "code": row["code"],
                "name": row["name"]
            })

        return ApiResponse(
            success=True,
            message=f"找到 {len(stocks)} 只匹配的股票",
            data={"stocks": stocks, "keyword": keyword}
        )
    except Exception as e:
        return ApiResponse(
            success=False,
            message="搜索股票失败",
            error=str(e)
        )


def get_market_summary() -> ApiResponse:
    """
    获取市场概览

    Returns:
        ApiResponse 格式的市场概览数据
    """
    try:
        from stork_agent.data.query import get_index_realtime

        # 获取主要指数
        indices = ["sh000001", "sz399001", "sz399006"]  # 上证指数、深证成指、创业板指
        indices_data = []

        for idx in indices:
            try:
                data = get_index_realtime(idx)
                indices_data.append({
                    "code": data["code"],
                    "name": data["name"],
                    "price": data["price"],
                    "change": data["change"],
                    "change_pct": data["change_pct"]
                })
            except:
                pass

        # 市场统计
        from stork_agent.data.query import get_stock_list
        df = get_stock_list()

        return ApiResponse(
            success=True,
            message="获取市场概览成功",
            data={
                "indices": indices_data,
                "total_stocks": len(df)
            }
        )
    except Exception as e:
        return ApiResponse(
            success=False,
            message="获取市场概览失败",
            error=str(e)
        )


# 导出所有工具函数
__all__ = [
    "get_stock_realtime",
    "get_stock_history",
    "get_stock_realtime_batch",
    "screen_stocks",
    "compare_stocks",
    "get_financials",
    "calculate_indicator",
    "search_stocks",
    "get_market_summary",
]
