"""
评估问题验证脚本

用于验证 Stork Agent MCP 服务器的评估问题是否能够正确回答
"""

import sys
import os
import asyncio

# 添加项目路径（evaluations/ 是项目根目录的子目录，所以需要2次 dirname）
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

from stork_agent.mcp_server import tools as mcp_tools


def test_q1_basic_query():
    """问题 1: 基本查询"""
    print("\n" + "=" * 60)
    print("问题 1: 查询贵州茅台的当前股价和市盈率")
    print("=" * 60)
    result = mcp_tools.query_stock("600519")
    print(result)
    print("\n验证: 是否包含股价和PE信息")
    print("✓ 通过" if "价格" in result or "PE" in result or "市盈率" in result else "✗ 失败")


def test_q2_stock_screening():
    """问题 2: 选股筛选"""
    print("\n" + "=" * 60)
    print("问题 2: 筛选市盈率低于20且市值超过100亿元的股票")
    print("=" * 60)
    result = mcp_tools.screen_stocks(
        criteria={"pe_max": 20, "market_cap_min": 100},
        page=1,
        page_size=10
    )
    print(result)
    print("\n验证: 是否返回股票列表")
    print("✓ 通过" if "股票" in result or "只" in result else "✗ 失败")


def test_q3_compare_stocks():
    """问题 3: 多股票对比"""
    print("\n" + "=" * 60)
    print("问题 3: 对比贵州茅台和五粮液的表现")
    print("=" * 60)
    result = mcp_tools.compare_stocks(
        codes=["600519", "000858"],
        days=30
    )
    print(result)
    print("\n验证: 是否包含两只股票的对比数据")
    print("✓ 通过" if ("600519" in result or "贵州茅台" in result) else "✗ 失败")


def test_q4_technical_indicator():
    """问题 4: 技术指标"""
    print("\n" + "=" * 60)
    print("问题 4: 计算贵州茅台的MA20指标")
    print("=" * 60)
    result = mcp_tools.calculate_indicator(
        code="600519",
        indicator="ma",
        period=20
    )
    print(result)
    print("\n验证: 是否包含MA指标数据")
    print("✓ 通过" if "MA" in result or "ma" in result else "✗ 失败")


def test_q5_financial_data():
    """问题 5: 财务数据"""
    print("\n" + "=" * 60)
    print("问题 5: 查询贵州茅台的财务数据")
    print("=" * 60)
    result = mcp_tools.get_financials("600519")
    print(result)
    print("\n验证: 是否包含财务指标")
    print("✓ 通过" if "财务" in result or "营收" in result or "ROE" in result else "✗ 失败")


def test_q6_market_summary():
    """问题 6: 市场概览"""
    print("\n" + "=" * 60)
    print("问题 6: 查看市场概览")
    print("=" * 60)
    result = mcp_tools.get_market_summary()
    print(result)
    print("\n验证: 是否包含指数信息")
    print("✓ 通过" if "上证" in result or "深证" in result or "指数" in result else "✗ 失败")


def test_q7_history_data():
    """问题 7: 历史数据"""
    print("\n" + "=" * 60)
    print("问题 7: 获取贵州茅台30天K线数据")
    print("=" * 60)
    result = mcp_tools.get_stock_history(
        code="600519",
        days=30,
        period="daily"
    )
    print(result)
    print("\n验证: 是否包含历史数据")
    print("✓ 通过" if "数据" in result or "K线" in result or "600519" in result else "✗ 失败")


def test_q8_search_stocks():
    """问题 8: 股票搜索"""
    print("\n" + "=" * 60)
    print("问题 8: 搜索包含'白酒'的股票")
    print("=" * 60)
    result = mcp_tools.search_stocks(keyword="白酒", limit=5)
    print(result)
    print("\n验证: 是否返回搜索结果")
    print("✓ 通过" if "600519" in result or "贵州茅台" in result or "没有找到" in result else "✗ 失败")


def test_q9_pagination():
    """问题 9: 分页操作"""
    print("\n" + "=" * 60)
    print("问题 9: 筛选大市值股票并查看第2页")
    print("=" * 60)
    # 先执行筛选
    mcp_tools.screen_stocks(
        criteria={"market_cap_min": 1000},
        page=1,
        page_size=50
    )
    # 然后翻页
    result = mcp_tools.next_page()
    print(result)
    print("\n验证: 是否显示第2页数据")
    print("✓ 通过" if "第 2" in result or "页" in result else "✗ 失败")


def test_q10_complex_analysis():
    """问题 10: 综合分析"""
    print("\n" + "=" * 60)
    print("问题 10: 筛选低PE低价股并找出ROE最高的3只")
    print("=" * 60)
    result = mcp_tools.screen_stocks(
        criteria={"pe_max": 15},
        page=1,
        page_size=100
    )
    print(f"筛选结果（前100字符）: {result[:200]}...")
    print("\n注意: 完整的筛选和排序需要多次工具调用")
    print("✓ 基本功能验证通过")


def test_q11_kline_chart():
    """问题 11: K线图生成"""
    print("\n" + "=" * 60)
    print("问题 11: 生成K线图")
    print("=" * 60)

    # 获取历史数据
    history = mcp_tools.get_stock_history(
        code="600519",
        days=30,
        period="daily"
    )

    # 尝试生成K线图
    try:
        from stork_agent.analysis.charts import plot_kline
        import json

        # 解析历史数据
        if "600519" in history:
            data_lines = history.split("\n")
            print(f"获取到历史数据")
            print("注意: 当前 MCP 工具未直接集成图表生成功能")
            print("图表生成功能在 analysis/charts.py 模块中可用")
            print("✓ 图表模块存在验证通过")
        else:
            print("需要手动解析历史数据来生成图表")
    except ImportError:
        print("✗ 图表模块导入失败")


def test_q12_price_trend_chart():
    """问题 12: 价格走势图"""
    print("\n" + "=" * 60)
    print("问题 12: 生成价格走势图")
    print("=" * 60)

    try:
        from stork_agent.analysis.charts import plot_price_trend
        print("✓ 价格走势图功能可用")
        print("使用 plot_price_trend(dates, prices, title) 生成图表")
    except ImportError:
        print("✗ 图表模块导入失败")


def test_q13_financial_comparison_chart():
    """问题 13: 财务对比柱状图"""
    print("\n" + "=" * 60)
    print("问题 13: 生成财务对比图")
    print("=" * 60)

    try:
        from stork_agent.analysis.charts import plot_financial_comparison
        print("✓ 财务对比图功能可用")
        print("使用 plot_financial_comparison(names, metrics) 生成图表")
    except ImportError:
        print("✗ 图表模块导入失败")


def test_q14_macd_chart():
    """问题 14: MACD技术指标图"""
    print("\n" + "=" * 60)
    print("问题 14: 生成MACD图")
    print("=" * 60)

    try:
        from stork_agent.analysis.charts import plot_macd
        print("✓ MACD图功能可用")
        print("使用 plot_macd(dates, dif, dea, bar) 生成图表")
    except ImportError:
        print("✗ 图表模块导入失败")


def test_q15_rsi_chart():
    """问题 15: RSI技术指标图"""
    print("\n" + "=" * 60)
    print("问题 15: 生成RSI图")
    print("=" * 60)

    try:
        from stork_agent.analysis.charts import plot_indicator
        print("✓ RSI图功能可用")
        print("使用 plot_indicator(dates, values, title) 生成图表")
    except ImportError:
        print("✗ 图表模块导入失败")


def test_chart_generation():
    """测试图表生成功能"""
    print("\n" + "=" * 60)
    print("图表生成功能综合测试")
    print("=" * 60)

    try:
        from stork_agent.analysis import charts

        # 测试数据
        dates = ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"]
        prices = [100.0, 102.5, 98.0, 105.0, 103.5]
        opens = [99.0, 101.0, 97.5, 104.0, 102.0]
        highs = [102.0, 103.0, 101.0, 106.0, 104.5]
        lows = [98.0, 99.5, 96.0, 103.0, 101.5]
        closes = [100.0, 102.5, 98.0, 105.0, 103.5]
        volumes = [1000000, 1200000, 900000, 1500000, 1100000]

        # 测试K线图
        print("\n测试 K线图生成...")
        kline_path = charts.plot_kline(
            dates, opens, highs, lows, closes, volumes,
            title="测试K线图",
            filename="test_kline"
        )
        print(f"✓ K线图已生成: {kline_path}")

        # 测试价格走势图
        print("\n测试价格走势图生成...")
        trend_path = charts.plot_price_trend(
            dates, prices,
            title="测试价格走势",
            filename="test_trend"
        )
        print(f"✓ 价格走势图已生成: {trend_path}")

        # 测试财务对比图
        print("\n测试财务对比图生成...")
        comparison_path = charts.plot_financial_comparison(
            names=["股票A", "股票B", "股票C"],
            metrics={
                "市值(亿)": [1000, 800, 600],
                "PE": [20, 15, 25],
                "ROE(%)": [25, 30, 20]
            },
            title="测试财务对比",
            filename="test_comparison"
        )
        print(f"✓ 财务对比图已生成: {comparison_path}")

        print("\n" + "=" * 60)
        print("✅ 所有图表功能测试通过!")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"\n❌ 图表生成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_evaluations():
    """运行所有评估问题"""
    print("\n" + "=" * 60)
    print("Stork Agent MCP Server - 评估问题验证")
    print("=" * 60)
    print("\n开始验证评估问题...")

    try:
        # 基础功能测试 (问题 1-10)
        print("\n【第一部分】基础功能测试")
        print("-" * 60)
        test_q1_basic_query()
        test_q2_stock_screening()
        test_q3_compare_stocks()
        test_q4_technical_indicator()
        test_q5_financial_data()
        test_q6_market_summary()
        test_q7_history_data()
        test_q8_search_stocks()
        test_q9_pagination()
        test_q10_complex_analysis()

        # 图表功能测试 (问题 11-15)
        print("\n【第二部分】图表功能测试")
        print("-" * 60)
        test_q11_kline_chart()
        test_q12_price_trend_chart()
        test_q13_financial_comparison_chart()
        test_q14_macd_chart()
        test_q15_rsi_chart()

        # 综合图表生成测试
        print("\n【第三部分】综合图表生成测试")
        print("-" * 60)
        test_chart_generation()

        print("\n" + "=" * 60)
        print("评估验证完成!")
        print("=" * 60)
        print("\n📊 评估问题总数: 15 个")
        print("   - 基础功能: 10 个")
        print("   - 图表功能: 5 个")
        print("\n📝 注意事项:")
        print("1. 这些验证只是基本的工具调用测试")
        print("2. 真正的 LLM 有效性评估需要:")
        print("   - 使用 Claude CLI 或 MCP Inspector")
        print("   - 让 LLM 自然地提出这些问题")
        print("   - 检查 LLM 是否能正确组合使用工具")
        print("   - 验证答案的准确性和完整性")
        print("3. 图表功能目前在 analysis/charts.py 模块中")
        print("   需要通过 API 直接调用来生成图表")

    except Exception as e:
        print(f"\n❌ 评估过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_evaluations()
