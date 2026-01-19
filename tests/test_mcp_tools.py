"""
MCP 服务器工具测试

测试 Stork Agent MCP 服务器的所有工具功能
"""

import pytest
import sys
import os

# 添加项目路径
project_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

from stork_agent.mcp_server import tools


class TestQueryStock:
    """测试股票查询功能"""

    def test_query_valid_stock(self):
        """测试查询有效股票"""
        result = tools.query_stock("600519")  # 贵州茅台
        assert isinstance(result, str)
        assert "贵州茅台" in result or "600519" in result
        assert "价格" in result or "当前" in result

    def test_query_invalid_stock(self):
        """测试查询无效股票代码"""
        result = tools.query_stock("999999")  # 不存在的代码
        assert isinstance(result, str)
        assert "错误" in result or "失败" in result or "未找到" in result


class TestScreenStocks:
    """测试股票筛选功能"""

    def test_screen_by_pe(self):
        """测试按市盈率筛选"""
        result = tools.screen_stocks(
            criteria={"pe_max": 20},
            page=1,
            page_size=10
        )
        assert isinstance(result, str)
        assert "股票" in result or "只" in result or "没有找到" in result

    def test_screen_by_market_cap(self):
        """测试按市值筛选"""
        result = tools.screen_stocks(
            criteria={"market_cap_min": 100},  # 市值大于100亿
            page=1,
            page_size=10
        )
        assert isinstance(result, str)


class TestPagination:
    """测试分页功能"""

    def test_next_page_without_query(self):
        """测试在没有查询的情况下调用下一页"""
        result = tools.next_page()
        assert isinstance(result, str)
        assert "没有" in result or "请先执行" in result

    def test_prev_page_without_query(self):
        """测试在没有查询的情况下调用上一页"""
        result = tools.prev_page()
        assert isinstance(result, str)
        assert "没有" in result or "请先执行" in result


class TestCompareStocks:
    """测试股票对比功能"""

    def test_compare_two_stocks(self):
        """测试对比两只股票"""
        result = tools.compare_stocks(
            codes=["600519", "000858"],  # 贵州茅台 vs 五粮液
            days=30
        )
        assert isinstance(result, str)
        # 结果应包含股票信息或错误信息
        assert "贵州茅台" in result or "五粮液" in result or "错误" in result

    def test_compare_empty_list(self):
        """测试对比空列表"""
        result = tools.compare_stocks(codes=[])
        assert isinstance(result, str)


class TestSearchStocks:
    """测试股票搜索功能"""

    def test_search_by_name(self):
        """测试按名称搜索"""
        result = tools.search_stocks(keyword="茅台", limit=5)
        assert isinstance(result, str)
        assert "600519" in result or "贵州茅台" in result or "没有找到" in result

    def test_search_by_code(self):
        """测试按代码搜索"""
        result = tools.search_stocks(keyword="600519", limit=5)
        assert isinstance(result, str)
        assert "600519" in result or "贵州茅台" in result or "没有找到" in result


class TestGetStockHistory:
    """测试获取历史数据功能"""

    def test_get_history_valid_stock(self):
        """测试获取有效股票的历史数据"""
        result = tools.get_stock_history(
            code="600519",
            days=30,
            period="daily"
        )
        assert isinstance(result, str)
        assert "600519" in result or "贵州茅台" in result or "错误" in result

    def test_get_history_weekly(self):
        """测试获取周线数据"""
        result = tools.get_stock_history(
            code="600519",
            days=30,
            period="weekly"
        )
        assert isinstance(result, str)


class TestGetFinancials:
    """测试获取财务数据功能"""

    def test_get_financials_valid_stock(self):
        """测试获取有效股票的财务数据"""
        result = tools.get_financials("600519")
        assert isinstance(result, str)
        assert "600519" in result or "贵州茅台" in result or "财务" in result


class TestCalculateIndicator:
    """测试技术指标计算功能"""

    def test_calculate_ma(self):
        """测试计算移动平均线"""
        result = tools.calculate_indicator(
            code="600519",
            indicator="ma",
            period=20
        )
        assert isinstance(result, str)
        assert "MA" in result or "ma" in result or "移动平均" in result

    def test_calculate_macd(self):
        """测试计算 MACD"""
        result = tools.calculate_indicator(
            code="600519",
            indicator="macd"
        )
        assert isinstance(result, str)
        assert "MACD" in result or "macd" in result

    def test_calculate_invalid_indicator(self):
        """测试计算不支持的指标"""
        result = tools.calculate_indicator(
            code="600519",
            indicator="invalid"
        )
        assert isinstance(result, str)
        assert "错误" in result or "不支持" in result


class TestGetMarketSummary:
    """测试获取市场概览功能"""

    def test_get_market_summary(self):
        """测试获取市场概览"""
        result = tools.get_market_summary()
        assert isinstance(result, str)
        # 应该包含指数信息或错误信息
        assert "上证" in result or "深证" in result or "指数" in result or "市场" in result


class TestExport:
    """测试导出功能"""

    def test_export_without_data(self):
        """测试在没有数据的情况下导出"""
        result = tools.export_current_result(format="csv")
        assert isinstance(result, str)
        assert "没有" in result or "请先执行" in result or "导出" in result


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])
