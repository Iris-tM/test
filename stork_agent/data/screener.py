"""
选股筛选模块

实现各种股票筛选策略
"""

import akshare as ak
import pandas as pd
from typing import Dict, List, Optional
from stork_agent.agent.schemas import ScreeningFilter, StockBrief


def screen_stocks(filters: ScreeningFilter) -> Dict:
    """
    按条件筛选股票

    Args:
        filters: 筛选条件对象

    Returns:
        筛选结果字典
    """
    try:
        # 获取全市场数据
        df = ak.stock_zh_a_spot_em()

        # 应用筛选条件
        filtered_df = df.copy()

        # PE 筛选
        if filters.pe_min is not None:
            filtered_df = filtered_df[
                pd.to_numeric(filtered_df.get("市盈率-动态", 0), errors="coerce") >= filters.pe_min
            ]
        if filters.pe_max is not None:
            filtered_df = filtered_df[
                pd.to_numeric(filtered_df.get("市盈率-动态", 999), errors="coerce") <= filters.pe_max
            ]

        # PB 筛选
        if filters.pb_min is not None:
            filtered_df = filtered_df[
                pd.to_numeric(filtered_df.get("市净率", 0), errors="coerce") >= filters.pb_min
            ]
        if filters.pb_max is not None:
            filtered_df = filtered_df[
                pd.to_numeric(filtered_df.get("市净率", 999), errors="coerce") <= filters.pb_max
            ]

        # 市值筛选（转换为亿元）
        if filters.market_cap_min is not None:
            filtered_df = filtered_df[
                pd.to_numeric(filtered_df.get("总市值", 0), errors="coerce") / 100000000 >= filters.market_cap_min
            ]
        if filters.market_cap_max is not None:
            filtered_df = filtered_df[
                pd.to_numeric(filtered_df.get("总市值", 999999999), errors="coerce") / 100000000 <= filters.market_cap_max
            ]

        # 涨跌幅筛选
        if filters.change_min is not None:
            filtered_df = filtered_df[
                pd.to_numeric(filtered_df.get("涨跌幅", -999), errors="coerce") >= filters.change_min
            ]
        if filters.change_max is not None:
            filtered_df = filtered_df[
                pd.to_numeric(filtered_df.get("涨跌幅", 999), errors="coerce") <= filters.change_max
            ]

        # 换手率筛选
        if filters.turnover_min is not None:
            filtered_df = filtered_df[
                pd.to_numeric(filtered_df.get("换手率", 0), errors="coerce") >= filters.turnover_min
            ]
        if filters.turnover_max is not None:
            filtered_df = filtered_df[
                pd.to_numeric(filtered_df.get("换手率", 999), errors="coerce") <= filters.turnover_max
            ]

        # 行业筛选
        if filters.industry:
            filtered_df = filtered_df[
                filtered_df.get("行业", "").str.contains(filters.industry, na=False)
            ]

        # 限制结果数量
        result_df = filtered_df.head(filters.limit)

        # 转换为结果格式
        stocks = []
        for _, row in result_df.iterrows():
            stocks.append({
                "code": row.get("代码", ""),
                "name": row.get("名称", ""),
                "price": float(row.get("最新价", 0)),
                "change": float(row.get("涨跌额", 0)),
                "change_pct": float(row.get("涨跌幅", 0)),
                "pe_ratio": float(row.get("市盈率-动态", 0)) if pd.notna(row.get("市盈率-动态")) else None,
                "pb_ratio": float(row.get("市净率", 0)) if pd.notna(row.get("市净率")) else None,
                "market_cap": float(row.get("总市值", 0)) / 100000000 if pd.notna(row.get("总市值")) else None,
                "turnover": float(row.get("换手率", 0)) if pd.notna(row.get("换手率")) else None,
            })

        return {
            "stocks": stocks,
            "total": len(stocks),
            "criteria": filters.model_dump()
        }
    except Exception as e:
        raise Exception(f"筛选股票失败: {str(e)}")


def screen_by_pe(pe_min: float = 0, pe_max: float = 50, limit: int = 50) -> List[StockBrief]:
    """
    按 PE 筛选股票

    Args:
        pe_min: 最小市盈率
        pe_max: 最大市盈率
        limit: 返回数量限制

    Returns:
        符合条件的股票列表
    """
    filters = ScreeningFilter(pe_min=pe_min, pe_max=pe_max, limit=limit)
    result = screen_stocks(filters)
    return [StockBrief(**stock) for stock in result["stocks"]]


def screen_by_market_cap(
    min_cap: float = 0,
    max_cap: float = 10000,
    limit: int = 50
) -> List[StockBrief]:
    """
    按市值筛选股票

    Args:
        min_cap: 最小市值（亿元）
        max_cap: 最大市值（亿元）
        limit: 返回数量限制

    Returns:
        符合条件的股票列表
    """
    filters = ScreeningFilter(
        market_cap_min=min_cap,
        market_cap_max=max_cap,
        limit=limit
    )
    result = screen_stocks(filters)
    return [StockBrief(**stock) for stock in result["stocks"]]


def screen_by_industry(industry: str, limit: int = 50) -> List[StockBrief]:
    """
    按行业筛选股票

    Args:
        industry: 行业名称
        limit: 返回数量限制

    Returns:
        符合条件的股票列表
    """
    filters = ScreeningFilter(industry=industry, limit=limit)
    result = screen_stocks(filters)
    return [StockBrief(**stock) for stock in result["stocks"]]


def screen_gainers(limit: int = 20) -> List[StockBrief]:
    """
    筛选涨幅榜股票

    Args:
        limit: 返回数量限制

    Returns:
        涨幅榜股票列表
    """
    try:
        df = ak.stock_zh_a_spot_em()
        df = df.sort_values("涨跌幅", ascending=False).head(limit)

        stocks = []
        for _, row in df.iterrows():
            stocks.append(StockBrief(
                code=row.get("代码", ""),
                name=row.get("名称", ""),
                price=float(row.get("最新价", 0)),
                change=float(row.get("涨跌额", 0)),
                change_pct=float(row.get("涨跌幅", 0)),
                pe_ratio=float(row.get("市盈率-动态", 0)) if pd.notna(row.get("市盈率-动态")) else None,
                pb_ratio=float(row.get("市净率", 0)) if pd.notna(row.get("市净率")) else None,
                market_cap=float(row.get("总市值", 0)) / 100000000 if pd.notna(row.get("总市值")) else None,
                turnover=float(row.get("换手率", 0)) if pd.notna(row.get("换手率")) else None,
            ))
        return stocks
    except Exception as e:
        raise Exception(f"筛选涨幅榜失败: {str(e)}")


def screen_losers(limit: int = 20) -> List[StockBrief]:
    """
    筛选跌幅榜股票

    Args:
        limit: 返回数量限制

    Returns:
        跌幅榜股票列表
    """
    try:
        df = ak.stock_zh_a_spot_em()
        df = df.sort_values("涨跌幅", ascending=True).head(limit)

        stocks = []
        for _, row in df.iterrows():
            stocks.append(StockBrief(
                code=row.get("代码", ""),
                name=row.get("名称", ""),
                price=float(row.get("最新价", 0)),
                change=float(row.get("涨跌额", 0)),
                change_pct=float(row.get("涨跌幅", 0)),
                pe_ratio=float(row.get("市盈率-动态", 0)) if pd.notna(row.get("市盈率-动态")) else None,
                pb_ratio=float(row.get("市净率", 0)) if pd.notna(row.get("市净率")) else None,
                market_cap=float(row.get("总市值", 0)) / 100000000 if pd.notna(row.get("总市值")) else None,
                turnover=float(row.get("换手率", 0)) if pd.notna(row.get("换手率")) else None,
            ))
        return stocks
    except Exception as e:
        raise Exception(f"筛选跌幅榜失败: {str(e)}")


def screen_active_stocks(limit: int = 20) -> List[StockBrief]:
    """
    筛选成交活跃股票（按换手率）

    Args:
        limit: 返回数量限制

    Returns:
        活跃股票列表
    """
    try:
        df = ak.stock_zh_a_spot_em()
        df = df.sort_values("换手率", ascending=False).head(limit)

        stocks = []
        for _, row in df.iterrows():
            stocks.append(StockBrief(
                code=row.get("代码", ""),
                name=row.get("名称", ""),
                price=float(row.get("最新价", 0)),
                change=float(row.get("涨跌额", 0)),
                change_pct=float(row.get("涨跌幅", 0)),
                pe_ratio=float(row.get("市盈率-动态", 0)) if pd.notna(row.get("市盈率-动态")) else None,
                pb_ratio=float(row.get("市净率", 0)) if pd.notna(row.get("市净率")) else None,
                market_cap=float(row.get("总市值", 0)) / 100000000 if pd.notna(row.get("总市值")) else None,
                turnover=float(row.get("换手率", 0)) if pd.notna(row.get("换手率")) else None,
            ))
        return stocks
    except Exception as e:
        raise Exception(f"筛选活跃股票失败: {str(e)}")
