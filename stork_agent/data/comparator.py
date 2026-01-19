"""
公司对比模块

实现多公司财务指标对比
"""

import akshare as ak
import pandas as pd
from typing import Dict, List
from stork_agent.data.query import (
    get_realtime_quote,
    get_financial_data,
    get_history_kline,
    normalize_stock_code,
)


def compare_stocks(codes: List[str], days: int = 30) -> Dict:
    """
    对比多只股票的基本面和价格表现

    Args:
        codes: 股票代码列表
        days: 对比天数（用于计算期间涨跌幅）

    Returns:
        对比结果字典
    """
    try:
        stocks_data = []

        for code in codes:
            try:
                # 获取实时行情
                quote = get_realtime_quote(code)

                # 获取财务数据
                financial = get_financial_data(code)

                # 获取历史数据计算涨跌幅
                hist = get_history_kline(code, "daily", days + 10)
                if len(hist["data"]) > days:
                    start_price = hist["data"][-days]["close"]
                    current_price = hist["data"][-1]["close"]
                    period_change_pct = ((current_price - start_price) / start_price) * 100
                else:
                    period_change_pct = None

                # 合并数据
                stock_metric = {
                    "code": code,
                    "name": quote.get("name", ""),
                    "price": quote.get("price"),
                    "change": quote.get("change"),
                    "change_pct": quote.get("change_pct"),
                    "period_change_pct": period_change_pct,
                    "pe_ratio": quote.get("pe_ratio"),
                    "pb_ratio": quote.get("pb_ratio"),
                    "market_cap": quote.get("market_cap"),
                    "turnover": quote.get("turnover"),
                    "roe": financial.get("roe"),
                    "revenue": financial.get("revenue"),
                    "net_profit": financial.get("net_profit"),
                    "debt_ratio": financial.get("debt_ratio"),
                }
                stocks_data.append(stock_metric)
            except Exception as e:
                # 跳过获取失败的股票
                continue

        # 计算摘要信息
        summary = {}
        if stocks_data:
            # 找出各项最优
            valid_market_caps = [s["market_cap"] for s in stocks_data if s["market_cap"]]
            if valid_market_caps:
                summary["max_market_cap"] = max(valid_market_caps)

            valid_roes = [s["roe"] for s in stocks_data if s["roe"]]
            if valid_roes:
                summary["max_roe"] = max(valid_roes)

            valid_pes = [s["pe_ratio"] for s in stocks_data if s["pe_ratio"]]
            if valid_pes:
                summary["min_pe"] = min(valid_pes)

            summary["total"] = len(stocks_data)

        return {
            "stocks": stocks_data,
            "summary": summary
        }
    except Exception as e:
        raise Exception(f"对比股票失败: {str(e)}")


def compare_financials(codes: List[str]) -> Dict:
    """
    对比多只股票的财务指标

    Args:
        codes: 股票代码列表

    Returns:
        财务对比结果
    """
    try:
        financials_data = []

        for code in codes:
            try:
                financial = get_financial_data(code)
                financials_data.append({
                    "code": code,
                    "name": financial.get("name", ""),
                    "revenue": financial.get("revenue"),
                    "net_profit": financial.get("net_profit"),
                    "roe": financial.get("roe"),
                    "roa": financial.get("roa"),
                    "debt_ratio": financial.get("debt_ratio"),
                    "eps": financial.get("eps"),
                    "bps": financial.get("bps"),
                })
            except:
                continue

        return {
            "stocks": financials_data,
            "total": len(financials_data)
        }
    except Exception as e:
        raise Exception(f"财务对比失败: {str(e)}")


def compare_price_performance(codes: List[str], days: int = 30) -> Dict:
    """
    对比多只股票的价格表现

    Args:
        codes: 股票代码列表
        days: 对比天数

    Returns:
        价格表现对比结果
    """
    try:
        performance_data = []

        for code in codes:
            try:
                hist = get_history_kline(code, "daily", days + 10)

                if len(hist["data"]) > days:
                    start_data = hist["data"][-days]
                    end_data = hist["data"][-1]

                    # 计算期间最高最低
                    period_data = hist["data"][-days:]
                    high = max(bar["high"] for bar in period_data)
                    low = min(bar["low"] for bar in period_data)
                    volume_avg = sum(bar["volume"] for bar in period_data) / len(period_data)

                    performance_data.append({
                        "code": code,
                        "name": hist.get("name", ""),
                        "start_price": start_data["close"],
                        "end_price": end_data["close"],
                        "high": high,
                        "low": low,
                        "change": end_data["close"] - start_data["close"],
                        "change_pct": ((end_data["close"] - start_data["close"]) / start_data["close"]) * 100,
                        "volume_avg": volume_avg,
                    })
            except:
                continue

        # 按涨跌幅排序
        performance_data.sort(key=lambda x: x.get("change_pct", 0), reverse=True)

        return {
            "stocks": performance_data,
            "total": len(performance_data),
            "period_days": days
        }
    except Exception as e:
        raise Exception(f"价格表现对比失败: {str(e)}")


def generate_comparison_report(codes: List[str]) -> str:
    """
    生成股票对比报告

    Args:
        codes: 股票代码列表

    Returns:
        对比报告文本
    """
    try:
        # 获取对比数据
        comparison = compare_stocks(codes)

        report_lines = []
        report_lines.append("=" * 60)
        report_lines.append("股票对比报告")
        report_lines.append("=" * 60)
        report_lines.append("")

        # 基本信息
        report_lines.append("【基本信息对比】")
        report_lines.append(f"{'代码':<10}{'名称':<12}{'价格':<10}{'涨跌幅':<10}{'市值(亿)':<12}{'换手率':<10}")
        report_lines.append("-" * 60)

        for stock in comparison["stocks"]:
            report_lines.append(
                f"{stock['code']:<10}"
                f"{stock['name']:<12}"
                f"{stock['price']:<10.2f}"
                f"{stock['change_pct']:<10.2f}"
                f"{stock['market_cap'] or 0:<12.2f}"
                f"{stock['turnover'] or 0:<10.2f}"
            )

        report_lines.append("")

        # 估值指标
        report_lines.append("【估值指标对比】")
        report_lines.append(f"{'代码':<10}{'名称':<12}{'PE':<10}{'PB':<10}")
        report_lines.append("-" * 60)

        for stock in comparison["stocks"]:
            report_lines.append(
                f"{stock['code']:<10}"
                f"{stock['name']:<12}"
                f"{stock['pe_ratio'] or 'N/A':<10}"
                f"{stock['pb_ratio'] or 'N/A':<10}"
            )

        report_lines.append("")

        # 财务指标
        report_lines.append("【财务指标对比】")
        report_lines.append(f"{'代码':<10}{'名称':<12}{'ROE(%)':<12}{'营收(亿)':<12}{'净利润(亿)':<12}")
        report_lines.append("-" * 60)

        for stock in comparison["stocks"]:
            report_lines.append(
                f"{stock['code']:<10}"
                f"{stock['name']:<12}"
                f"{stock['roe'] or 'N/A':<12}"
                f"{stock['revenue'] or 'N/A':<12}"
                f"{stock['net_profit'] or 'N/A':<12}"
            )

        report_lines.append("")
        report_lines.append("=" * 60)

        return "\n".join(report_lines)
    except Exception as e:
        return f"生成对比报告失败: {str(e)}"
