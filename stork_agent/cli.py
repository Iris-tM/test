"""
CLI 入口模块

提供命令行接口
"""

import click
import json
from stork_agent.agent.tools import (
    get_stock_realtime,
    get_stock_history,
    screen_stocks,
    compare_stocks,
    get_financials,
    calculate_indicator,
    search_stocks,
    get_market_summary,
)
from stork_agent.analysis.charts import generate_chart
from stork_agent.utils.helpers import (
    format_number,
    format_percentage,
    format_market_cap,
    format_volume,
)


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """A股智能选股助手 - 基于 AkShare 的股票数据分析工具"""
    pass


@cli.command()
@click.argument("code")
def query(code: str):
    """查询股票实时行情

    \b
    示例:
        python -m stork_agent.cli query 600519
    """
    result = get_stock_realtime(code)

    if result.success:
        data = result.data
        click.echo(f"\n{'='*50}")
        click.echo(f"股票代码: {data['code']}")
        click.echo(f"股票名称: {data['name']}")
        click.echo(f"{'='*50}")
        click.echo(f"当前价格: {format_number(data['price'])} 元")
        click.echo(f"开盘价: {format_number(data['open'])} 元")
        click.echo(f"最高价: {format_number(data['high'])} 元")
        click.echo(f"最低价: {format_number(data['low'])} 元")
        click.echo(f"涨跌额: {format_number(data['change'])} 元")
        click.echo(f"涨跌幅: {format_percentage(data['change_pct'])}")
        click.echo(f"成交量: {format_volume(data['volume'])} 手")
        click.echo(f"成交额: {format_volume(data['amount'])} 元")
        click.echo(f"换手率: {format_percentage(data['turnover'])}")

        if data.get("pe_ratio"):
            click.echo(f"市盈率: {format_number(data['pe_ratio'])}")
        if data.get("pb_ratio"):
            click.echo(f"市净率: {format_number(data['pb_ratio'])}")
        if data.get("market_cap"):
            click.echo(f"总市值: {format_market_cap(data['market_cap'])}")
        click.echo(f"{'='*50}\n")
    else:
        click.echo(f"查询失败: {result.error}", err=True)


@cli.command()
@click.argument("code")
@click.option("--period", default="daily", help="周期: daily/weekly/monthly")
@click.option("--days", default=100, help="获取天数")
@click.option("--output", help="输出文件路径")
def history(code: str, period: str, days: int, output: str):
    """获取历史K线数据

    \b
    示例:
        python -m stork_agent.cli history 600519 --days 30
    """
    result = get_stock_history(code, period, days)

    if result.success:
        data = result.data
        click.echo(f"\n{data['name']} ({data['code']}) - {period} K线数据")
        click.echo(f"共 {data['count']} 条数据\n")

        # 显示最近10条
        click.echo(f"{'日期':<12}{'开盘':<10}{'最高':<10}{'最低':<10}{'收盘':<10}{'成交量':<12}")
        click.echo("-" * 70)
        for bar in data["data"][-10:]:
            click.echo(
                f"{bar['date']:<12}"
                f"{bar['open']:<10.2f}"
                f"{bar['high']:<10.2f}"
                f"{bar['low']:<10.2f}"
                f"{bar['close']:<10.2f}"
                f"{format_volume(bar['volume']):<12}"
            )

        # 保存到文件
        if output:
            with open(output, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            click.echo(f"\n数据已保存到: {output}")
    else:
        click.echo(f"获取失败: {result.error}", err=True)


@cli.command()
@click.option("--pe-min", type=float, help="最小市盈率")
@click.option("--pe-max", type=float, help="最大市盈率")
@click.option("--pb-min", type=float, help="最小市净率")
@click.option("--pb-max", type=float, help="最大市净率")
@click.option("--market-cap-min", type=float, help="最小市值(亿元)")
@click.option("--market-cap-max", type=float, help="最大市值(亿元)")
@click.option("--change-min", type=float, help="最小涨跌幅(%)")
@click.option("--change-max", type=float, help="最大涨跌幅(%)")
@click.option("--limit", default=20, help="返回数量限制")
def screen(pe_min, pe_max, pb_min, pb_max, market_cap_min, market_cap_max,
           change_min, change_max, limit):
    """选股筛选

    \b
    示例:
        python -m stork_agent.cli screen --pe-max 20 --limit 10
    """
    filters = {
        "pe_min": pe_min,
        "pe_max": pe_max,
        "pb_min": pb_min,
        "pb_max": pb_max,
        "market_cap_min": market_cap_min,
        "market_cap_max": market_cap_max,
        "change_min": change_min,
        "change_max": change_max,
        "limit": limit
    }

    result = screen_stocks(filters)

    if result.success:
        data = result.data
        click.echo(f"\n筛选结果: 共找到 {data['total']} 只股票\n")

        click.echo(f"{'代码':<10}{'名称':<12}{'价格':<10}{'涨跌幅':<10}{'PE':<8}{'市值(亿)':<12}")
        click.echo("-" * 70)

        for stock in data["stocks"]:
            click.echo(
                f"{stock['code']:<10}"
                f"{stock['name']:<12}"
                f"{format_number(stock['price']):<10}"
                f"{format_percentage(stock['change_pct']):<10}"
                f"{format_number(stock['pe_ratio']) if stock['pe_ratio'] else 'N/A':<8}"
                f"{format_number(stock['market_cap']) if stock['market_cap'] else 'N/A':<12}"
            )
    else:
        click.echo(f"筛选失败: {result.error}", err=True)


@cli.command()
@click.argument("codes")
@click.option("--days", default=30, help="对比天数")
def compare(codes: str, days: int):
    """对比多只股票

    \b
    示例:
        python -m stork_agent.cli compare 600519,000858 --days 30
    """
    code_list = codes.split(",")
    result = compare_stocks(code_list, days)

    if result.success:
        data = result.data
        click.echo(f"\n股票对比报告 ({days}天)\n")

        click.echo(f"{'代码':<10}{'名称':<12}{'价格':<10}{'涨跌幅':<10}{'期间涨跌':<12}{'PE':<8}{'ROE':<8}")
        click.echo("-" * 80)

        for stock in data["stocks"]:
            period_change = stock.get("period_change_pct")
            click.echo(
                f"{stock['code']:<10}"
                f"{stock['name']:<12}"
                f"{format_number(stock['price']):<10}"
                f"{format_percentage(stock['change_pct']):<10}"
                f"{format_percentage(period_change) if period_change else 'N/A':<12}"
                f"{format_number(stock['pe_ratio']) if stock['pe_ratio'] else 'N/A':<8}"
                f"{format_number(stock['roe']) if stock['roe'] else 'N/A':<8}"
            )
    else:
        click.echo(f"对比失败: {result.error}", err=True)


@cli.command()
@click.argument("code")
def financial(code: str):
    """获取财务数据

    \b
    示例:
        python -m stork_agent.cli financial 600519
    """
    result = get_financials(code)

    if result.success:
        data = result.data
        click.echo(f"\n{data['name']} ({data['code']}) 财务数据")
        click.echo(f"报告期: {data['report_date']}\n")

        if data.get("revenue"):
            click.echo(f"营业收入: {format_number(data['revenue'])} 亿元")
        if data.get("net_profit"):
            click.echo(f"净利润: {format_number(data['net_profit'])} 亿元")
        if data.get("eps"):
            click.echo(f"每股收益: {format_number(data['eps'])} 元")
        if data.get("bps"):
            click.echo(f"每股净资产: {format_number(data['bps'])} 元")
        if data.get("roe"):
            click.echo(f"净资产收益率: {format_percentage(data['roe'])}")
        if data.get("debt_ratio"):
            click.echo(f"资产负债率: {format_percentage(data['debt_ratio'])}")
    else:
        click.echo(f"获取失败: {result.error}", err=True)


@cli.command()
@click.argument("code")
@click.argument("indicator")
@click.option("--period", default=20, help="计算周期")
def indicator(code: str, indicator: str, period: int):
    """计算技术指标

    \b
    示例:
        python -m stork_agent.cli indicator 600519 ma --period 20
        python -m stork_agent.cli indicator 600519 macd
    """
    result = calculate_indicator(code, indicator, period)

    if result.success:
        data = result.data
        click.echo(f"\n{data['name']} ({data['code']}) - {data['indicator']}")
        click.echo(f"{data['description']}\n")

        # 显示最近10条数据
        if isinstance(data["data"], list) and len(data["data"]) > 0:
            # 获取数据键
            keys = list(data["data"][0].keys())
            header = "  ".join(f"{k:<12}" for k in keys if k != "date")
            click.echo(f"{'日期':<12}{header}")
            click.echo("-" * 60)

            for item in data["data"][-10:]:
                values = "  ".join(
                    f"{format_number(item[k]) if isinstance(item[k], (int, float)) else str(item[k]):<12}"
                    for k in keys if k != "date"
                )
                click.echo(f"{item['date']:<12}{values}")
    else:
        click.echo(f"计算失败: {result.error}", err=True)


@cli.command()
@click.argument("keyword")
def search(keyword: str):
    """搜索股票

    \b
    示例:
        python -m stork_agent.cli search 茅台
    """
    result = search_stocks(keyword)

    if result.success:
        data = result.data
        click.echo(f"\n搜索结果 (关键词: {keyword})\n")

        click.echo(f"{'代码':<10}{'名称':<12}")
        click.echo("-" * 25)

        for stock in data["stocks"]:
            click.echo(f"{stock['code']:<10}{stock['name']:<12}")
    else:
        click.echo(f"搜索失败: {result.error}", err=True)


@cli.command()
def summary():
    """获取市场概览

    \b
    示例:
        python -m stork_agent.cli summary
    """
    result = get_market_summary()

    if result.success:
        data = result.data
        click.echo(f"\n{'='*50}")
        click.echo("市场概览")
        click.echo(f"{'='*50}\n")

        click.echo("主要指数:")
        click.echo(f"{'代码':<12}{'名称':<12}{'点位':<12}{'涨跌幅':<10}")
        click.echo("-" * 50)

        for idx in data.get("indices", []):
            click.echo(
                f"{idx['code']:<12}"
                f"{idx['name']:<12}"
                f"{format_number(idx['price']):<12}"
                f"{format_percentage(idx['change_pct']):<10}"
            )

        click.echo(f"\n市场总股票数: {data.get('total_stocks', 0)}")
    else:
        click.echo(f"获取失败: {result.error}", err=True)


if __name__ == "__main__":
    cli()
