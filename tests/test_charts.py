"""
图表功能测试脚本

专门测试 Stork Agent 的 Plotly 图表生成功能
"""

import sys
import os

# 添加项目路径（tests/ 是项目根目录的子目录，所以需要2次 dirname）
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

from stork_agent.analysis import charts


def test_kline_chart():
    """测试 K线图生成"""
    print("\n" + "=" * 60)
    print("测试 K线图生成")
    print("=" * 60)

    # 准备测试数据
    dates = ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05",
              "2024-01-08", "2024-01-09", "2024-01-10", "2024-01-11", "2024-01-12"]
    opens = [1680.0, 1675.0, 1690.0, 1685.0, 1695.0, 1700.0, 1692.0, 1688.0, 1705.0, 1710.0]
    highs = [1690.0, 1685.0, 1700.0, 1695.0, 1705.0, 1710.0, 1702.0, 1698.0, 1715.0, 1720.0]
    lows = [1675.0, 1670.0, 1685.0, 1680.0, 1690.0, 1695.0, 1688.0, 1682.0, 1700.0, 1705.0]
    closes = [1685.0, 1682.0, 1695.0, 1690.0, 1700.0, 1705.0, 1698.0, 1695.0, 1710.0, 1715.0]
    volumes = [25000, 28000, 30000, 22000, 26000, 32000, 35000, 29000, 38000, 40000]

    try:
        filepath = charts.plot_kline(
            dates=dates,
            opens=opens,
            highs=highs,
            lows=lows,
            closes=closes,
            volumes=volumes,
            title="贵州茅台 - K线图测试",
            filename="test_kline_moutai"
        )

        print(f"✅ K线图已生成")
        print(f"   文件路径: {filepath}")

        # 验证文件存在
        if os.path.exists(filepath):
            file_size = os.path.getsize(filepath)
            print(f"   文件大小: {file_size} bytes")
            print(f"✅ 文件验证通过")
            return True
        else:
            print("❌ 文件不存在")
            return False

    except Exception as e:
        print(f"❌ K线图生成失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_price_trend_chart():
    """测试价格走势图生成"""
    print("\n" + "=" * 60)
    print("测试价格走势图生成")
    print("=" * 60)

    # 准备测试数据
    dates = ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05",
              "2024-01-08", "2024-01-09", "2024-01-10", "2024-01-11", "2024-01-12"]
    prices = [1680.0, 1685.0, 1690.0, 1685.0, 1695.0, 1700.0, 1705.0, 1710.0, 1715.0, 1720.0]

    try:
        filepath = charts.plot_price_trend(
            dates=dates,
            prices=prices,
            title="贵州茅台 - 价格走势测试",
            filename="test_trend_moutai"
        )

        print(f"✅ 价格走势图已生成")
        print(f"   文件路径: {filepath}")

        if os.path.exists(filepath):
            file_size = os.path.getsize(filepath)
            print(f"   文件大小: {file_size} bytes")
            print(f"✅ 文件验证通过")
            return True
        else:
            print("❌ 文件不存在")
            return False

    except Exception as e:
        print(f"❌ 价格走势图生成失败: {e}")
        return False


def test_financial_comparison_chart():
    """测试财务对比图生成"""
    print("\n" + "=" * 60)
    print("测试财务对比图生成")
    print("=" * 60)

    # 准备测试数据
    names = ["贵州茅台", "五粮液", "泸州老窖"]
    metrics = {
        "市值(亿)": [21000, 12000, 3500],
        "PE": [28.5, 25.0, 35.0],
        "ROE(%)": [28.5, 25.3, 22.1]
    }

    try:
        filepath = charts.plot_financial_comparison(
            names=names,
            metrics=metrics,
            title="白酒龙头 - 财务指标对比",
            filename="test_comparison_baijiu"
        )

        print(f"✅ 财务对比图已生成")
        print(f"   文件路径: {filepath}")

        if os.path.exists(filepath):
            file_size = os.path.getsize(filepath)
            print(f"   文件大小: {file_size} bytes")
            print(f"✅ 文件验证通过")
            return True
        else:
            print("❌ 文件不存在")
            return False

    except Exception as e:
        print(f"❌ 财务对比图生成失败: {e}")
        return False


def test_macd_chart():
    """测试 MACD 图生成"""
    print("\n" + "=" * 60)
    print("测试 MACD 图生成")
    print("=" * 60)

    # 准备测试数据
    dates = [f"2024-01-{i:02d}" for i in range(1, 21)]
    dif = [100 + i * 2 for i in range(20)]
    dea = [98 + i * 1.5 for i in range(20)]
    bar = [dif[i] - dea[i] for i in range(20)]

    try:
        filepath = charts.plot_macd(
            dates=dates,
            dif=dif,
            dea=dea,
            bar=bar,
            title="贵州茅台 - MACD指标测试",
            filename="test_macd_moutai"
        )

        print(f"✅ MACD图已生成")
        print(f"   文件路径: {filepath}")

        if os.path.exists(filepath):
            file_size = os.path.getsize(filepath)
            print(f"   文件大小: {file_size} bytes")
            print(f"✅ 文件验证通过")
            return True
        else:
            print("❌ 文件不存在")
            return False

    except Exception as e:
        print(f"❌ MACD图生成失败: {e}")
        return False


def test_indicator_chart():
    """测试技术指标图生成"""
    print("\n" + "=" * 60)
    print("测试技术指标图生成 (RSI)")
    print("=" * 60)

    # 准备测试数据
    dates = [f"2024-01-{i:02d}" for i in range(1, 31)]
    values = [50 + i * 1.5 for i in range(30)]

    try:
        filepath = charts.plot_indicator(
            dates=dates,
            values=values,
            title="贵州茅台 - RSI(14)测试",
            filename="test_rsi_moutai"
        )

        print(f"✅ 技术指标图已生成")
        print(f"   文件路径: {filepath}")

        if os.path.exists(filepath):
            file_size = os.path.getsize(filepath)
            print(f"   文件大小: {file_size} bytes")
            print(f"✅ 文件验证通过")
            return True
        else:
            print("❌ 文件不存在")
            return False

    except Exception as e:
        print(f"❌ 技术指标图生成失败: {e}")
        return False


def test_pie_chart():
    """测试饼图生成"""
    print("\n" + "=" * 60)
    print("测试饼图生成")
    print("=" * 60)

    # 准备测试数据
    labels = ["消费", "金融", "科技", "医药", "能源"]
    values = [25, 20, 18, 22, 15]

    try:
        filepath = charts.plot_pie_chart(
            labels=labels,
            values=values,
            title="市场板块占比测试",
            filename="test_pie_chart"
        )

        print(f"✅ 饼图已生成")
        print(f"   文件路径: {filepath}")

        if os.path.exists(filepath):
            file_size = os.path.getsize(filepath)
            print(f"   文件大小: {file_size} bytes")
            print(f"✅ 文件验证通过")
            return True
        else:
            print("❌ 文件不存在")
            return False

    except Exception as e:
        print(f"❌ 饼图生成失败: {e}")
        return False


def run_all_chart_tests():
    """运行所有图表测试"""
    print("\n" + "=" * 60)
    print("Stork Agent - 图表功能测试")
    print("=" * 60)
    print("\n开始测试所有图表生成功能...")

    results = {
        "K线图": test_kline_chart(),
        "价格走势图": test_price_trend_chart(),
        "财务对比图": test_financial_comparison_chart(),
        "MACD图": test_macd_chart(),
        "技术指标图": test_indicator_chart(),
        "饼图": test_pie_chart()
    }

    # 统计结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for chart_type, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{chart_type:12} {status}")

    print("-" * 60)
    print(f"总计: {passed}/{total} 通过")

    if passed == total:
        print("\n🎉 所有图表功能测试通过!")
        print("\n生成的图表文件位置:")
        print(f"   {os.path.join(project_dir, 'output', 'charts')}")
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败，请检查")

    return passed == total


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Stork Agent 图表功能测试")
    parser.add_argument(
        "--test",
        choices=["kline", "trend", "comparison", "macd", "indicator", "pie", "all"],
        default="all",
        help="指定要测试的图表类型"
    )

    args = parser.parse_args()

    if args.test == "all":
        run_all_chart_tests()
    elif args.test == "kline":
        test_kline_chart()
    elif args.test == "trend":
        test_price_trend_chart()
    elif args.test == "comparison":
        test_financial_comparison_chart()
    elif args.test == "macd":
        test_macd_chart()
    elif args.test == "indicator":
        test_indicator_chart()
    elif args.test == "pie":
        test_pie_chart()
