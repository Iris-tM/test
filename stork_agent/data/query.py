"""
数据查询模块

使用 AkShare 获取 A股数据，包括实时行情、历史K线、财务数据等
"""

import akshare as ak
import pandas as pd
from typing import Optional, Dict, List, Union
from datetime import datetime, timedelta


def normalize_stock_code(code: str) -> str:
    """
    规范化股票代码格式

    Args:
        code: 股票代码，支持 600519 或 SH600519 或 sz000001 格式

    Returns:
        标准化的 6 位股票代码
    """
    code = code.strip().upper()
    # 移除市场前缀
    if code.startswith(("SH", "SZ")):
        code = code[2:]
    # 确保是6位数字
    return code.zfill(6)


def get_stock_list() -> pd.DataFrame:
    """
    获取 A股股票列表

    Returns:
        包含股票代码、名称等信息的 DataFrame
    """
    try:
        # 获取沪深A股列表
        df_sh = ak.stock_info_a_code_name()
        return df_sh
    except Exception as e:
        raise Exception(f"获取股票列表失败: {str(e)}")


def get_realtime_quote(code: str) -> Dict:
    """
    获取单只股票的实时行情

    Args:
        code: 股票代码

    Returns:
        实时行情数据字典
    """
    code = normalize_stock_code(code)

    try:
        # 判断市场
        if code.startswith("6"):
            symbol = f"sh{code}"
        else:
            symbol = f"sz{code}"

        # 获取实时行情
        df = ak.stock_zh_a_spot_em()

        # 查找对应股票
        stock_data = df[df["代码"] == code]

        if stock_data.empty:
            raise ValueError(f"未找到股票代码 {code}")

        row = stock_data.iloc[0]

        return {
            "code": code,
            "name": row.get("名称", ""),
            "price": float(row.get("最新价", 0)),
            "open": float(row.get("今开", 0)),
            "high": float(row.get("最高", 0)),
            "low": float(row.get("最低", 0)),
            "volume": float(row.get("成交量", 0)),
            "amount": float(row.get("成交额", 0)),
            "change": float(row.get("涨跌额", 0)),
            "change_pct": float(row.get("涨跌幅", 0)),
            "turnover": float(row.get("换手率", 0)),
            "pe_ratio": float(row.get("市盈率-动态", 0)) if pd.notna(row.get("市盈率-动态")) else None,
            "pb_ratio": float(row.get("市净率", 0)) if pd.notna(row.get("市净率")) else None,
            "market_cap": float(row.get("总市值", 0)) / 100000000 if pd.notna(row.get("总市值")) else None,
        }
    except Exception as e:
        raise Exception(f"获取实时行情失败 ({code}): {str(e)}")


def get_history_kline(
    code: str,
    period: str = "daily",
    days: int = 100,
    adjust: str = "qfq"
) -> Dict:
    """
    获取历史K线数据

    Args:
        code: 股票代码
        period: 周期 - daily(日线), weekly(周线), monthly(月线)
        days: 获取天数
        adjust: 复权方式 - qfq(前复权), hfq(后复权), ''(不复权)

    Returns:
        K线数据字典
    """
    code = normalize_stock_code(code)

    try:
        # 确定周期参数
        period_map = {
            "daily": "daily",
            "weekly": "weekly",
            "monthly": "monthly"
        }
        period_param = period_map.get(period, "daily")

        # 获取股票名称
        df_list = get_stock_list()
        stock_info = df_list[df_list["code"] == code]
        name = stock_info.iloc[0]["name"] if not stock_info.empty else ""

        # 根据复权方式选择 API
        if adjust == "qfq":
            df = ak.stock_zh_a_hist(
                symbol=code,
                period=period_param,
                adjust="qfq",
                start_date=(datetime.now() - timedelta(days=days*2)).strftime("%Y%m%d"),
                end_date=datetime.now().strftime("%Y%m%d")
            )
        elif adjust == "hfq":
            df = ak.stock_zh_a_hist(
                symbol=code,
                period=period_param,
                adjust="hfq",
                start_date=(datetime.now() - timedelta(days=days*2)).strftime("%Y%m%d"),
                end_date=datetime.now().strftime("%Y%m%d")
            )
        else:
            df = ak.stock_zh_a_hist(
                symbol=code,
                period=period_param,
                adjust="",
                start_date=(datetime.now() - timedelta(days=days*2)).strftime("%Y%m%d"),
                end_date=datetime.now().strftime("%Y%m%d")
            )

        # 重命名列
        df = df.rename(columns={
            "日期": "date",
            "开盘": "open",
            "收盘": "close",
            "最高": "high",
            "最低": "low",
            "成交量": "volume",
            "成交额": "amount",
            "涨跌幅": "change_pct"
        })

        # 取最近 days 条数据
        df = df.tail(days).reset_index(drop=True)

        # 转换为列表格式
        data = []
        for _, row in df.iterrows():
            data.append({
                "date": row["date"],
                "open": float(row["open"]),
                "high": float(row["high"]),
                "low": float(row["low"]),
                "close": float(row["close"]),
                "volume": float(row["volume"]),
                "amount": float(row.get("amount", 0)),
                "change_pct": float(row.get("change_pct", 0)) if pd.notna(row.get("change_pct")) else 0
            })

        return {
            "code": code,
            "name": name,
            "period": period,
            "data": data,
            "count": len(data)
        }
    except Exception as e:
        raise Exception(f"获取历史数据失败 ({code}): {str(e)}")


def get_financial_data(code: str) -> Dict:
    """
    获取财务数据

    Args:
        code: 股票代码

    Returns:
        财务数据字典
    """
    code = normalize_stock_code(code)

    try:
        # 获取股票名称
        df_list = get_stock_list()
        stock_info = df_list[df_list["code"] == code]
        name = stock_info.iloc[0]["name"] if not stock_info.empty else ""

        # 获取财务指标
        try:
            df = ak.stock_financial_analysis_indicator(symbol=code)
            if not df.empty:
                latest = df.iloc[0]
                return {
                    "code": code,
                    "name": name,
                    "report_date": latest.get("日期", str(datetime.now().date())),
                    "revenue": float(latest.get("营业收入", 0)) / 100000000 if pd.notna(latest.get("营业收入")) else None,
                    "net_profit": float(latest.get("净利润", 0)) / 100000000 if pd.notna(latest.get("净利润")) else None,
                    "eps": float(latest.get("基本每股收益", 0)) if pd.notna(latest.get("基本每股收益")) else None,
                    "bps": float(latest.get("每股净资产", 0)) if pd.notna(latest.get("每股净资产")) else None,
                    "roe": float(latest.get("净资产收益率", 0)) if pd.notna(latest.get("净资产收益率")) else None,
                    "debt_ratio": float(latest.get("资产负债率", 0)) if pd.notna(latest.get("资产负债率")) else None,
                }
        except (KeyError, ValueError, TypeError) as e:
            # 数据格式异常时返回默认值
            pass
        except Exception as e:
            # 记录但不中断流程，API 调用失败时使用默认值
            import warnings
            warnings.warn(f"Failed to fetch financial data for {code}: {str(e)}")

        # 备用方案：获取简化的财务数据
        return {
            "code": code,
            "name": name,
            "report_date": str(datetime.now().date()),
            "revenue": None,
            "net_profit": None,
            "eps": None,
            "bps": None,
            "roe": None,
            "debt_ratio": None,
        }
    except Exception as e:
        raise Exception(f"获取财务数据失败 ({code}): {str(e)}")


def get_index_realtime(index_code: str) -> Dict:
    """
    获取指数实时行情

    Args:
        index_code: 指数代码，如 sh000001(上证指数), sz399001(深证成指)

    Returns:
        指数行情数据字典
    """
    try:
        # 获取指数行情
        df = ak.stock_zh_index_spot_em()

        # 查找对应指数
        index_data = df[df["代码"] == index_code]

        if index_data.empty:
            raise ValueError(f"未找到指数代码 {index_code}")

        row = index_data.iloc[0]

        return {
            "code": index_code,
            "name": row.get("名称", ""),
            "price": float(row.get("最新价", 0)),
            "open": float(row.get("今开", 0)),
            "high": float(row.get("最高", 0)),
            "low": float(row.get("最低", 0)),
            "volume": float(row.get("成交量", 0)),
            "amount": float(row.get("成交额", 0)),
            "change": float(row.get("涨跌额", 0)),
            "change_pct": float(row.get("涨跌幅", 0)),
        }
    except Exception as e:
        raise Exception(f"获取指数行情失败 ({index_code}): {str(e)}")


def batch_get_realtime(codes: List[str]) -> List[Dict]:
    """
    批量获取多只股票的实时行情

    Args:
        codes: 股票代码列表

    Returns:
        实时行情数据列表
    """
    try:
        # 获取全市场数据
        df = ak.stock_zh_a_spot_em()

        results = []
        for code in codes:
            code_normalized = normalize_stock_code(code)
            stock_data = df[df["代码"] == code_normalized]

            if not stock_data.empty:
                row = stock_data.iloc[0]
                results.append({
                    "code": code_normalized,
                    "name": row.get("名称", ""),
                    "price": float(row.get("最新价", 0)),
                    "open": float(row.get("今开", 0)),
                    "high": float(row.get("最高", 0)),
                    "low": float(row.get("最低", 0)),
                    "volume": float(row.get("成交量", 0)),
                    "amount": float(row.get("成交额", 0)),
                    "change": float(row.get("涨跌额", 0)),
                    "change_pct": float(row.get("涨跌幅", 0)),
                    "turnover": float(row.get("换手率", 0)),
                    "pe_ratio": float(row.get("市盈率-动态", 0)) if pd.notna(row.get("市盈率-动态")) else None,
                    "pb_ratio": float(row.get("市净率", 0)) if pd.notna(row.get("市净率")) else None,
                    "market_cap": float(row.get("总市值", 0)) / 100000000 if pd.notna(row.get("总市值")) else None,
                })

        return results
    except Exception as e:
        raise Exception(f"批量获取行情失败: {str(e)}")


def get_stock_info(code: str) -> Dict:
    """
    获取股票基本信息

    Args:
        code: 股票代码

    Returns:
        股票基本信息字典
    """
    code = normalize_stock_code(code)

    try:
        # 获取个股信息
        info = ak.stock_individual_info_em(symbol=code)

        result = {"code": code}
        for _, row in info.iterrows():
            key = row["item"]
            value = row["value"]
            result[key] = value

        return result
    except Exception as e:
        raise Exception(f"获取股票信息失败 ({code}): {str(e)}")
