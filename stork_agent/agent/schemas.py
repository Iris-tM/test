"""
Agent 数据结构定义

使用 Pydantic 进行数据验证和序列化，确保所有返回给 AI 的数据都是结构化的
"""

from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class StockQuote(BaseModel):
    """股票实时行情数据结构"""
    code: str = Field(..., description="股票代码")
    name: str = Field(..., description="股票名称")
    price: float = Field(..., description="当前价格")
    open: float = Field(..., description="开盘价")
    high: float = Field(..., description="最高价")
    low: float = Field(..., description="最低价")
    volume: float = Field(..., description="成交量（手）")
    amount: float = Field(..., description="成交额（元）")
    change: float = Field(..., description="涨跌额")
    change_pct: float = Field(..., description="涨跌幅(%)")
    turnover: float = Field(..., description="换手率(%)")
    pe_ratio: Optional[float] = Field(None, description="市盈率")
    pb_ratio: Optional[float] = Field(None, description="市净率")
    market_cap: Optional[float] = Field(None, description="总市值（亿元）")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="数据时间戳")

    class Config:
        json_schema_extra = {
            "example": {
                "code": "600519",
                "name": "贵州茅台",
                "price": 1680.50,
                "open": 1670.00,
                "high": 1690.00,
                "low": 1665.00,
                "volume": 25000,
                "amount": 4200000000,
                "change": 10.50,
                "change_pct": 0.63,
                "turnover": 0.12,
                "pe_ratio": 28.5,
                "pb_ratio": 12.3,
                "market_cap": 21000
            }
        }


class HistoryBar(BaseModel):
    """历史K线数据条目"""
    date: str = Field(..., description="日期")
    open: float = Field(..., description="开盘价")
    high: float = Field(..., description="最高价")
    low: float = Field(..., description="最低价")
    close: float = Field(..., description="收盘价")
    volume: float = Field(..., description="成交量")
    amount: float = Field(..., description="成交额")
    change_pct: float = Field(..., description="涨跌幅(%)")


class StockHistory(BaseModel):
    """股票历史K线数据结构"""
    code: str = Field(..., description="股票代码")
    name: str = Field(..., description="股票名称")
    period: str = Field(..., description="周期: daily/weekly/monthly")
    data: List[HistoryBar] = Field(..., description="K线数据列表")
    count: int = Field(..., description="数据条数")


class ScreeningFilter(BaseModel):
    """选股筛选条件"""
    pe_min: Optional[float] = Field(None, description="最小市盈率")
    pe_max: Optional[float] = Field(None, description="最大市盈率")
    pb_min: Optional[float] = Field(None, description="最小市净率")
    pb_max: Optional[float] = Field(None, description="最大市净率")
    market_cap_min: Optional[float] = Field(None, description="最小市值（亿元）")
    market_cap_max: Optional[float] = Field(None, description="最大市值（亿元）")
    change_min: Optional[float] = Field(None, description="最小涨跌幅(%)")
    change_max: Optional[float] = Field(None, description="最大涨跌幅(%)")
    industry: Optional[str] = Field(None, description="行业筛选")
    turnover_min: Optional[float] = Field(None, description="最小换手率(%)")
    turnover_max: Optional[float] = Field(None, description="最大换手率(%)")
    limit: int = Field(50, description="返回结果数量限制")


class StockBrief(BaseModel):
    """股票简要信息"""
    code: str = Field(..., description="股票代码")
    name: str = Field(..., description="股票名称")
    price: float = Field(..., description="当前价格")
    change: float = Field(..., description="涨跌额")
    change_pct: float = Field(..., description="涨跌幅(%)")
    pe_ratio: Optional[float] = Field(None, description="市盈率")
    pb_ratio: Optional[float] = Field(None, description="市净率")
    market_cap: Optional[float] = Field(None, description="总市值（亿元）")
    turnover: Optional[float] = Field(None, description="换手率(%)")


class ScreeningResult(BaseModel):
    """选股结果"""
    stocks: List[StockBrief] = Field(..., description="符合条件的股票列表")
    total: int = Field(..., description="总数量")
    criteria: ScreeningFilter = Field(..., description="筛选条件")


class StockMetrics(BaseModel):
    """股票指标"""
    code: str = Field(..., description="股票代码")
    name: str = Field(..., description="股票名称")
    pe_ratio: Optional[float] = Field(None, description="市盈率")
    pb_ratio: Optional[float] = Field(None, description="市净率")
    roe: Optional[float] = Field(None, description="净资产收益率(%)")
    revenue_growth: Optional[float] = Field(None, description="营收增长率(%)")
    profit_growth: Optional[float] = Field(None, description="利润增长率(%)")
    debt_ratio: Optional[float] = Field(None, description="资产负债率(%)")


class StockComparison(BaseModel):
    """股票对比结果"""
    stocks: List[StockMetrics] = Field(..., description="对比的股票列表")
    summary: dict = Field(..., description="对比摘要（最优值等）")


class FinancialData(BaseModel):
    """财务数据"""
    code: str = Field(..., description="股票代码")
    name: str = Field(..., description="股票名称")
    report_date: str = Field(..., description="报告期")
    revenue: Optional[float] = Field(None, description="营业收入（亿元）")
    net_profit: Optional[float] = Field(None, description="净利润（亿元）")
    total_assets: Optional[float] = Field(None, description="总资产（亿元）")
    total_liability: Optional[float] = Field(None, description="总负债（亿元）")
    eps: Optional[float] = Field(None, description="每股收益")
    bps: Optional[float] = Field(None, description="每股净资产")
    roe: Optional[float] = Field(None, description="净资产收益率(%)")
    roa: Optional[float] = Field(None, description="总资产收益率(%)")
    debt_ratio: Optional[float] = Field(None, description="资产负债率(%)")


class IndicatorData(BaseModel):
    """技术指标数据"""
    code: str = Field(..., description="股票代码")
    name: str = Field(..., description="股票名称")
    indicator: str = Field(..., description="指标名称")
    data: List[dict] = Field(..., description="指标数据列表")
    description: str = Field(..., description="指标说明")


class IndicatorValue(BaseModel):
    """单个技术指标值"""
    date: str = Field(..., description="日期")
    value: float = Field(..., description="指标值")
    signal: Optional[str] = Field(None, description="交易信号: buy/sell/neutral")


class MACDData(IndicatorData):
    """MACD 指标数据"""
    data: List[dict] = Field(..., description="包含 dif, dea, bar 的数据列表")


class RSIData(IndicatorData):
    """RSI 指标数据"""
    rsi6: Optional[float] = Field(None, description="RSI(6)")
    rsi12: Optional[float] = Field(None, description="RSI(12)")
    rsi24: Optional[float] = Field(None, description="RSI(24)")


class BollingerBands(BaseModel):
    """布林带数据"""
    upper: float = Field(..., description="上轨")
    middle: float = Field(..., description="中轨")
    lower: float = Field(..., description="下轨")


class ApiResponse(BaseModel):
    """通用 API 响应格式"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    data: Optional[dict] = Field(None, description="响应数据")
    error: Optional[str] = Field(None, description="错误信息")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "操作成功",
                "data": {},
                "error": None
            }
        }
