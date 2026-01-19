"""
图表绘制模块

使用 Plotly 生成交互式 HTML 图表
支持 K线图、价格走势图、财务对比图等
"""

import os
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

from stork_agent.config import Config


# 创建输出目录
CHART_OUTPUT_DIR = os.path.join(Config.OUTPUT_DIR, "charts")
os.makedirs(CHART_OUTPUT_DIR, exist_ok=True)


def save_chart(fig: go.Figure, filename: str) -> str:
    """
    保存图表为 HTML 文件

    Args:
        fig: Plotly Figure 对象
        filename: 文件名（不含扩展名）

    Returns:
        HTML 文件的绝对路径
    """
    filepath = os.path.join(CHART_OUTPUT_DIR, f"{filename}.html")
    fig.write_html(filepath, include_plotlyjs="cdn", full_html=True)
    return os.path.abspath(filepath)


def plot_kline(
    dates: List[str],
    opens: List[float],
    highs: List[float],
    lows: List[float],
    closes: List[float],
    volumes: Optional[List[float]] = None,
    title: str = "K线图",
    ma_periods: List[int] = [5, 10, 20, 60],
    filename: Optional[str] = None
) -> str:
    """
    绘制 K线图（使用 Plotly）

    Args:
        dates: 日期列表
        opens: 开盘价列表
        highs: 最高价列表
        lows: 最低价列表
        closes: 收盘价列表
        volumes: 成交量列表
        title: 图表标题
        ma_periods: MA周期列表
        filename: 文件名（可选）

    Returns:
        HTML 文件路径
    """
    # 创建子图
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.7, 0.3],
        subplot_titles=('价格', '成交量')
    )

    # K线图
    fig.add_trace(
        go.Candlestick(
            x=dates,
            open=opens,
            high=highs,
            low=lows,
            close=closes,
            name="K线",
            increasing_line_color="red",
            decreasing_line_color="green"
        ),
        row=1, col=1
    )

    # 计算并添加移动平均线
    colors = ["blue", "orange", "purple", "cyan"]
    for i, period in enumerate(ma_periods):
        ma_values = []
        for j in range(len(closes)):
            if j < period - 1:
                ma_values.append(None)
            else:
                ma = sum(closes[j - period + 1:j + 1]) / period
                ma_values.append(ma)

        fig.add_trace(
            go.Scatter(
                x=dates,
                y=ma_values,
                mode="lines",
                name=f"MA{period}",
                line=dict(color=colors[i % len(colors)], width=1)
            ),
            row=1, col=1
        )

    # 成交量
    if volumes:
        colors_vol = ["red" if closes[i] >= opens[i] else "green" for i in range(len(closes))]
        fig.add_trace(
            go.Bar(
                x=dates,
                y=volumes,
                name="成交量",
                marker=dict(color=colors_vol)
            ),
            row=2, col=1
        )

    # 更新布局
    fig.update_layout(
        title=title,
        xaxis_rangeslider_visible=False,
        hovermode="x unified",
        height=800,
        template="plotly_white"
    )

    fig.update_xaxes(title_text="日期", row=2, col=1)
    fig.update_yaxes(title_text="价格", row=1, col=1)
    fig.update_yaxes(title_text="成交量", row=2, col=1)

    # 保存图表
    if filename is None:
        filename = f"kline_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    return save_chart(fig, filename)


def plot_price_trend(
    dates: List[str],
    prices: List[float],
    title: str = "价格走势图",
    compare_data: Optional[Dict[str, List[float]]] = None,
    filename: Optional[str] = None
) -> str:
    """
    绘制价格走势图

    Args:
        dates: 日期列表
        prices: 价格列表
        title: 图表标题
        compare_data: 对比数据，格式为 {名称: 价格列表}
        filename: 文件名（可选）

    Returns:
        HTML 文件路径
    """
    fig = go.Figure()

    # 主线
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=prices,
            mode="lines",
            name="价格",
            line=dict(width=2)
        )
    )

    # 对比线
    if compare_data:
        for name, data in compare_data.items():
            fig.add_trace(
                go.Scatter(
                    x=dates,
                    y=data,
                    mode="lines",
                    name=name,
                    line=dict(width=1.5)
                )
            )

    fig.update_layout(
        title=title,
        xaxis_title="日期",
        yaxis_title="价格",
        hovermode="x unified",
        height=600,
        template="plotly_white"
    )

    if filename is None:
        filename = f"trend_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    return save_chart(fig, filename)


def plot_financial_comparison(
    names: List[str],
    metrics: Dict[str, List[float]],
    title: str = "财务指标对比",
    filename: Optional[str] = None
) -> str:
    """
    绘制财务指标对比柱状图

    Args:
        names: 股票名称列表
        metrics: 指标数据，格式为 {指标名: [值列表]}
        title: 图表标题
        filename: 文件名（可选）

    Returns:
        HTML 文件路径
    """
    n_metrics = len(metrics)

    if n_metrics == 1:
        fig = go.Figure()
        metric_name, values = list(metrics.items())[0]
        fig.add_trace(
            go.Bar(
                x=names,
                y=values,
                name=metric_name,
                text=[f"{v:.2f}" for v in values],
                textposition="auto"
            )
        )
        fig.update_yaxes(title_text=metric_name)
    else:
        fig = make_subplots(
            rows=1, cols=n_metrics,
            subplot_titles=tuple(metrics.keys())
        )

        for i, (metric_name, values) in enumerate(metrics.items(), 1):
            fig.add_trace(
                go.Bar(
                    x=names,
                    y=values,
                    name=metric_name,
                    showlegend=False
                ),
                row=1, col=i
            )

    fig.update_layout(
        title_text=title,
        height=600,
        template="plotly_white"
    )

    if filename is None:
        filename = f"comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    return save_chart(fig, filename)


def plot_indicator(
    dates: List[str],
    values: List[float],
    title: str = "技术指标图",
    signal_positions: Optional[List[Tuple[int, str]]] = None,
    filename: Optional[str] = None
) -> str:
    """
    绘制技术指标图

    Args:
        dates: 日期列表
        values: 指标值列表
        title: 图表标题
        signal_positions: 信号位置，格式为 [(索引, 信号类型), ...]
        filename: 文件名（可选）

    Returns:
        HTML 文件路径
    """
    fig = go.Figure()

    # 主线
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=values,
            mode="lines",
            name=title,
            line=dict(width=2)
        )
    )

    # 信号点
    if signal_positions:
        buy_x, buy_y = [], []
        sell_x, sell_y = [], []

        for idx, signal_type in signal_positions:
            if idx < len(values):
                if signal_type == "buy":
                    buy_x.append(dates[idx])
                    buy_y.append(values[idx])
                elif signal_type == "sell":
                    sell_x.append(dates[idx])
                    sell_y.append(values[idx])

        if buy_x:
            fig.add_trace(
                go.Scatter(
                    x=buy_x,
                    y=buy_y,
                    mode="markers",
                    name="买入信号",
                    marker=dict(symbol="triangle-up", size=12, color="red")
                )
            )

        if sell_x:
            fig.add_trace(
                go.Scatter(
                    x=sell_x,
                    y=sell_y,
                    mode="markers",
                    name="卖出信号",
                    marker=dict(symbol="triangle-down", size=12, color="green")
                )
            )

    fig.update_layout(
        title=title,
        xaxis_title="日期",
        yaxis_title="指标值",
        hovermode="x unified",
        height=600,
        template="plotly_white"
    )

    # 添加参考线
    fig.add_hline(y=70, line_dash="dash", line_color="gray", annotation_text="超买")
    fig.add_hline(y=30, line_dash="dash", line_color="gray", annotation_text="超卖")

    if filename is None:
        filename = f"indicator_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    return save_chart(fig, filename)


def plot_macd(
    dates: List[str],
    dif: List[float],
    dea: List[float],
    bar: List[float],
    title: str = "MACD指标",
    filename: Optional[str] = None
) -> str:
    """
    绘制 MACD 指标图

    Args:
        dates: 日期列表
        dif: DIF 值列表
        dea: DEA 值列表
        bar: BAR 值列表
        title: 图表标题
        filename: 文件名（可选）

    Returns:
        HTML 文件路径
    """
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.6, 0.4],
        subplot_titles=('DIF/DEA', 'MACD柱')
    )

    # DIF 和 DEA
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=dif,
            mode="lines",
            name="DIF",
            line=dict(color="blue", width=1.5)
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=dates,
            y=dea,
            mode="lines",
            name="DEA",
            line=dict(color="orange", width=1.5)
        ),
        row=1, col=1
    )

    # MACD 柱
    colors = ["red" if v >= 0 else "green" for v in bar]
    fig.add_trace(
        go.Bar(
            x=dates,
            y=bar,
            name="MACD",
            marker=dict(color=colors)
        ),
        row=2, col=1
    )

    fig.update_layout(
        title=title,
        xaxis_rangeslider_visible=False,
        hovermode="x unified",
        height=700,
        template="plotly_white"
    )

    fig.update_yaxes(title_text="值", row=1, col=1)
    fig.update_yaxes(title_text="MACD", row=2, col=1)
    fig.update_xaxes(title_text="日期", row=2, col=1)

    if filename is None:
        filename = f"macd_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    return save_chart(fig, filename)


def plot_pie_chart(
    labels: List[str],
    values: List[float],
    title: str = "饼图",
    filename: Optional[str] = None
) -> str:
    """
    绘制饼图

    Args:
        labels: 标签列表
        values: 值列表
        title: 图表标题
        filename: 文件名（可选）

    Returns:
        HTML 文件路径
    """
    fig = go.Figure(data=[
        go.Pie(
            labels=labels,
            values=values,
            textinfo="label+percent",
            hovertemplate="%{label}<br>值: %{value}<br>占比: %{percent}<extra></extra>"
        )
    ])

    fig.update_layout(
        title=title,
        height=600,
        template="plotly_white"
    )

    if filename is None:
        filename = f"pie_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    return save_chart(fig, filename)


def generate_chart(
    chart_type: str,
    save_to_file: bool = True,
    filename: Optional[str] = None,
    **kwargs
) -> Dict[str, str]:
    """
    通用图表生成函数

    Args:
        chart_type: 图表类型 - kline/trend/comparison/indicator/macd/pie
        save_to_file: 是否保存为文件
        filename: 文件名（可选）
        **kwargs: 图表参数

    Returns:
        包含文件路径和信息的字典
    """
    try:
        chart_functions = {
            "kline": plot_kline,
            "trend": plot_price_trend,
            "comparison": plot_financial_comparison,
            "indicator": plot_indicator,
            "macd": plot_macd,
            "pie": plot_pie_chart,
        }

        if chart_type not in chart_functions:
            return {
                "success": False,
                "error": f"不支持的图表类型: {chart_type}"
            }

        # 如果指定了 filename，传递给绘图函数
        if save_to_file:
            filepath = chart_functions[chart_type](filename=filename, **kwargs)
            return {
                "success": True,
                "filepath": filepath,
                "type": "html",
                "format": "file"
            }
        else:
            # 不保存文件，返回 figure 对象（用于进一步处理）
            fig = chart_functions[chart_type](**kwargs)
            return {
                "success": True,
                "figure": fig,
                "type": "plotly"
            }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# 保留原有 base64 函数用于向后兼容（但已弃用）
def chart_to_base64(fig) -> str:
    """
    将 Plotly 图表转换为 base64 编码的 PNG（已弃用）

    Args:
        fig: Plotly Figure 对象

    Returns:
        base64 编码的图片字符串
    """
    import base64
    from io import BytesIO

    # 转换为静态图片
    img_bytes = fig.to_image(format="png", width=1200, height=800)
    base64_str = base64.b64encode(img_bytes).decode("utf-8")

    return base64_str
