"""
MCP 工具映射

将底层 agent/tools 映射为 MCP 工具，返回自然语言回复
"""

from typing import Dict, List, Optional
import traceback

from stork_agent.agent import tools as agent_tools
from stork_agent.responder import generator, chart_decider, exporter
from stork_agent.responder.formatter import format_chart_response
from stork_agent.mcp_server.session import get_session
from stork_agent.cache.manager import get_cache_manager


def query_stock(code: str, session_id: str = "default") -> str:
    """
    查询股票信息，返回自然语言回复

    Args:
        code: 股票代码
        session_id: 会话 ID

    Returns:
        格式化后的文本回复
    """
    try:
        # 检查缓存
        cache = get_cache_manager()
        cache_key = cache._generate_key("realtime", {"code": code})
        cached = cache.get(cache_key, cache.TTL_REALTIME)
        if cached:
            return generator.generate_response("realtime", cached)

        # 获取数据
        result = agent_tools.get_stock_realtime(code)

        if not result.success:
            return generator.generate_error_response(
                result.error or "获取股票信息失败",
                f"股票代码: {code}"
            )

        # 缓存结果
        cache.set(cache_key, result.data, ttl=cache.TTL_REALTIME)

        # 生成回复
        return generator.generate_response("realtime", result.data)

    except Exception as e:
        return generator.generate_error_response(str(e), traceback.format_exc())


def screen_stocks(
    criteria: Dict,
    page: int = 1,
    page_size: int = 50,
    session_id: str = "default"
) -> str:
    """
    筛选股票，支持分页

    Args:
        criteria: 筛选条件字典
        page: 页码
        page_size: 每页数量
        session_id: 会话 ID

    Returns:
        格式化后的文本回复
    """
    try:
        # 检查缓存
        cache = get_cache_manager()
        cache_key = cache._generate_key("screen", criteria)
        cached = cache.get(cache_key, cache.TTL_SCREENING)

        all_stocks = []
        if cached:
            all_stocks = cached.get("stocks", [])
        else:
            # 执行筛选
            criteria["limit"] = 5000  # 获取更多数据用于分页
            result = agent_tools.screen_stocks(criteria)

            if not result.success:
                return generator.generate_error_response(
                    result.error or "筛选失败",
                    str(criteria)
                )

            all_stocks = result.data.get("stocks", [])
            # 缓存完整结果
            cache.set(cache_key, {"stocks": all_stocks})

        # 更新会话状态
        session = get_session(session_id)
        session.set_query(
            query="screen",
            data=all_stocks,
            criteria=criteria,
            page_size=page_size
        )

        # 获取当前页数据
        page_stocks = session.goto_page(page)

        # 生成回复
        response_data = {
            "stocks": page_stocks,
            "page": page,
            "page_size": page_size,
            "total": len(all_stocks),
        }

        return generator.generate_response("screen", response_data)

    except Exception as e:
        return generator.generate_error_response(str(e), traceback.format_exc())


def next_page(session_id: str = "default") -> str:
    """
    查看当前查询的下一页数据

    Args:
        session_id: 会话 ID

    Returns:
        格式化后的文本回复
    """
    try:
        session = get_session(session_id)

        if session.complete_data is None:
            return "没有正在进行的查询。请先执行筛选或搜索操作。"

        if not session.get_page_info()["has_next"]:
            page_info = session.get_page_info()
            return f"已经是最后一页了（第 {page_info['current_page']}/{page_info['total_pages']} 页）"

        # 获取下一页
        page_stocks = session.next_page()
        page_info = session.get_page_info()

        response_data = {
            "stocks": page_stocks,
            "page": page_info["current_page"],
            "page_size": page_info["page_size"],
            "total": page_info["total_count"],
        }

        return generator.generate_response("screen", response_data)

    except Exception as e:
        return generator.generate_error_response(str(e), traceback.format_exc())


def prev_page(session_id: str = "default") -> str:
    """
    查看当前查询的上一页数据

    Args:
        session_id: 会话 ID

    Returns:
        格式化后的文本回复
    """
    try:
        session = get_session(session_id)

        if session.complete_data is None:
            return "没有正在进行的查询。请先执行筛选或搜索操作。"

        if not session.get_page_info()["has_prev"]:
            return "已经是第一页了。"

        # 获取上一页
        page_stocks = session.prev_page()
        page_info = session.get_page_info()

        response_data = {
            "stocks": page_stocks,
            "page": page_info["current_page"],
            "page_size": page_info["page_size"],
            "total": page_info["total_count"],
        }

        return generator.generate_response("screen", response_data)

    except Exception as e:
        return generator.generate_error_response(str(e), traceback.format_exc())


def export_current_result(
    format: str = "csv",
    session_id: str = "default"
) -> str:
    """
    导出当前查询的完整数据

    Args:
        format: 导出格式 (csv, excel, json)
        session_id: 会话 ID

    Returns:
        导出结果信息
    """
    try:
        session = get_session(session_id)

        if session.complete_data is None:
            return "没有可导出的数据。请先执行筛选或搜索操作。"

        # 根据查询类型选择导出方式
        if session.current_query == "screen":
            filepath = exporter.export_stock_list(
                session.complete_data,
                session.query_criteria,
                format
            )
        else:
            filepath = exporter.export_data(session.complete_data, format)

        return generator.generate_success_response(
            f"数据已导出到: {filepath}",
            {"filepath": filepath, "rows": len(session.complete_data)}
        )

    except Exception as e:
        return generator.generate_error_response(str(e), traceback.format_exc())


def compare_stocks(codes: List[str], days: int = 30) -> str:
    """
    对比多只股票

    Args:
        codes: 股票代码列表
        days: 对比天数

    Returns:
        格式化后的对比结果
    """
    try:
        result = agent_tools.compare_stocks(codes, days)

        if not result.success:
            return generator.generate_error_response(
                result.error or "对比失败",
                f"股票代码: {codes}"
            )

        return generator.generate_response("compare", result.data)

    except Exception as e:
        return generator.generate_error_response(str(e), traceback.format_exc())


def get_stock_history(code: str, days: int = 30, period: str = "daily") -> str:
    """
    获取K线数据

    Args:
        code: 股票代码
        days: 获取天数
        period: 周期 (daily, weekly, monthly)

    Returns:
        格式化后的历史数据
    """
    try:
        result = agent_tools.get_stock_history(code, period, days)

        if not result.success:
            return generator.generate_error_response(
                result.error or "获取历史数据失败",
                f"股票代码: {code}"
            )

        return generator.generate_response("history", result.data)

    except Exception as e:
        return generator.generate_error_response(str(e), traceback.format_exc())


def search_stocks(keyword: str, limit: int = 10, session_id: str = "default") -> str:
    """
    搜索股票

    Args:
        keyword: 搜索关键词
        limit: 返回结果数量
        session_id: 会话 ID

    Returns:
        格式化后的搜索结果
    """
    try:
        result = agent_tools.search_stocks(keyword, limit)

        if not result.success:
            return generator.generate_error_response(
                result.error or "搜索失败",
                f"关键词: {keyword}"
            )

        # 更新会话状态（支持分页）
        stocks = result.data.get("stocks", [])
        session = get_session(session_id)
        session.set_query("search", stocks, {"keyword": keyword}, page_size=limit)

        return generator.generate_response("search", result.data)

    except Exception as e:
        return generator.generate_error_response(str(e), traceback.format_exc())


def get_financials(code: str) -> str:
    """
    获取财务数据

    Args:
        code: 股票代码

    Returns:
        格式化后的财务数据
    """
    try:
        result = agent_tools.get_financials(code)

        if not result.success:
            return generator.generate_error_response(
                result.error or "获取财务数据失败",
                f"股票代码: {code}"
            )

        return generator.generate_response("financial", result.data)

    except Exception as e:
        return generator.generate_error_response(str(e), traceback.format_exc())


def calculate_indicator(code: str, indicator: str, period: int = 20) -> str:
    """
    计算技术指标

    Args:
        code: 股票代码
        indicator: 指标类型 (ma, macd, rsi, boll)
        period: 计算周期

    Returns:
        格式化后的指标数据
    """
    try:
        result = agent_tools.calculate_indicator(code, indicator, period)

        if not result.success:
            return generator.generate_error_response(
                result.error or "计算指标失败",
                f"股票代码: {code}, 指标: {indicator}"
            )

        return generator.generate_response("indicator", result.data)

    except Exception as e:
        return generator.generate_error_response(str(e), traceback.format_exc())


def get_market_summary() -> str:
    """
    获取市场概览

    Returns:
        格式化后的市场概览
    """
    try:
        result = agent_tools.get_market_summary()

        if not result.success:
            return generator.generate_error_response(
                result.error or "获取市场概览失败"
            )

        return generator.generate_response("market", result.data)

    except Exception as e:
        return generator.generate_error_response(str(e), traceback.format_exc())


# 导出所有工具函数
__all__ = [
    "query_stock",
    "screen_stocks",
    "next_page",
    "prev_page",
    "export_current_result",
    "compare_stocks",
    "get_stock_history",
    "search_stocks",
    "get_financials",
    "calculate_indicator",
    "get_market_summary",
]
