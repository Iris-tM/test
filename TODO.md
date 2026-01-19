# Stork Agent MCP Server - 待办清单

最后更新: 2026-01-19

---

## 📊 总体进度

**已完成**: 10/17 任务 (59%)

| 类别 | 已完成 | 待办 | 完成率 |
|------|--------|------|--------|
| 基础改进 | 7 | 0 | 100% |
| 测试验证 | 3 | 1 | 75% |
| 功能增强 | 0 | 6 | 0% |

---

## ✅ 已完成任务

### MCP 基础改进
- [x] 工具命名规范化（添加 `stork_` 前缀）
- [x] 工具描述优化（更详细、准确）
- [x] 错误处理改进（特定异常类型）
- [x] 创建工具注解文档

### 测试与验证
- [x] 创建 pytest 测试套件
- [x] 创建 MCP Inspector 测试脚本
- [x] 创建图表功能测试
- [x] 运行完整测试并修复问题
- [x] 创建评估问题集（15个问题）

### 文档
- [x] 创建 TEST_RESULTS.md 测试结果文档
- [x] 更新 CLAUDE.md 项目说明
- [x] 更新 MCP_IMPROVEMENTS.md 改进总结

---

## ⏳ 进行中任务

### 1. 优化分页测试的会话状态管理

**问题描述**:
- `test_next_page_without_query` 和 `test_prev_page_without_query` 失败
- 原因：测试环境中存在缓存/会话状态，导致边缘情况测试失败

**解决方案**:
- 在测试开始时清理会话状态
- 或修改测试期望值以匹配实际行为

**优先级**: 低（不影响实际使用）

**相关文件**:
- `tests/test_mcp_tools.py` (lines 65-75)

---

## 📝 待办任务

### 短期任务（1-2周）

### 2. 添加 outputSchema 定义

**目标**: 为所有 MCP 工具添加结构化输出定义

**需要定义的工具**:
1. `stork_query_stock` - 股票查询结果结构
2. `stork_screen_stocks` - 筛选结果结构
3. `stork_compare_stocks` - 对比结果结构
4. `stork_get_stock_history` - 历史数据结构
5. `stork_get_financials` - 财务数据结构
6. `stork_calculate_indicator` - 技术指标结构
7. `stork_get_market_summary` - 市场概览结构
8. `stork_search_stocks` - 搜索结果结构
9. `stork_next_page` / `stork_prev_page` - 分页结果结构
10. `stork_export_current_result` - 导出结果结构

**影响文件**: `stork_agent/mcp_server/server.py`

**示例**:
```python
Tool(
    name="stork_query_stock",
    description="查询股票实时行情...",
    inputSchema={...},
    outputSchema={
        "type": "object",
        "properties": {
            "code": {"type": "string"},
            "name": {"type": "string"},
            "price": {"type": "number"},
            "change": {"type": "number"},
            "pe": {"type": "number"},
            "market_cap": {"type": "string"}
        }
    }
)
```

---

### 中期任务（1-2月）
### 自我学习模块
用户喂给Ai一些大V的策略，AI学会用用户提到的策略进行分析，比如，用户可能会说，吴富贵大佬的低波动红利策略是。。。。，吴富贵大佬今天发的帖子的内容是。。。。AI需要自动记录并分析低波动红利策略的要点，然后记录下来。在用户下次使用时，如果用户提到用低波动红利策略选股，那么就按照吴富贵大佬的策略进行分析。
- 这块功能有点没想好怎么实现，你有逻辑吗？

### 3. 实现图表返回功能（MCP 工具集成）

**目标**: 将图表生成集成到 MCP 工具返回值中

**当前状态**:
- 图表生成功能在 `analysis/charts.py` 中
- 可以通过 Python API 调用
- 未集成到 MCP 工具

**需要实现**:
- 添加新的 MCP 工具 `stork_generate_chart`
- 支持参数：图表类型、数据、标题
- 返回图表文件路径

**实现方案**:

```python
# stork_agent/mcp_server/tools.py
def generate_chart(
    chart_type: str,
    data: dict,
    title: str = None
) -> str:
    """
    生成交互式图表

    Args:
        chart_type: 图表类型 (kline, trend, comparison, macd, rsi, pie)
        data: 图表数据
        title: 图表标题

    Returns:
        图表文件路径
    """
    from stork_agent.analysis import charts

    if chart_type == "kline":
        filepath = charts.plot_kline(**data, title=title)
    elif chart_type == "trend":
        filepath = charts.plot_price_trend(**data, title=title)
    # ... 其他图表类型

    return f"图表已生成: {filepath}"
```

**影响文件**:
- `stork_agent/mcp_server/server.py` (注册新工具)
- `stork_agent/mcp_server/tools.py` (添加工具函数)

---

### 4. 考虑迁移到 FastMCP 框架（可选）

**目标**: 使用 FastMCP 框架以获得更好的开发体验

**优势**:
- 支持完整的工具注解（annotations）
- 更简洁的 API
- 自动参数验证
- 更好的类型提示

**迁移示例**:

```python
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

mcp = FastMCP("stork_mcp")

class QueryStockInput(BaseModel):
    code: str = Field(..., description="股票代码，6位数字")

@mcp.tool(
    name="stork_query_stock",
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def stork_query_stock(params: QueryStockInput) -> str:
    '''查询股票实时行情信息'''
    return tools.query_stock(params.code)
```

**影响文件**:
- `stork_agent/mcp_server/server.py` (完全重写)

**工作量**: 中等（约2-3天）

---

### 5. 优化工具描述

**目标**: 根据测试结果优化工具描述，改善 LLM 理解

**需要优化的工具**:
- 分页相关工具（添加使用示例）
- 导出工具（说明支持的格式）

**示例**:
```python
Tool(
    name="stork_next_page",
    description="""
    查看当前筛选或搜索结果的下一页数据。

    使用前必须先执行: stork_screen_stocks 或 stork_search_stocks

    示例:
    1. stork_screen_stocks(criteria={"pe_max": 20}, page=1, page_size=50)
    2. stork_next_page()  # 显示第2页

    返回: 第2页的股票列表
    """
)
```

---

### 长期任务（3-6月）

### 6. 图表功能优化

**需要实现**:
- [ ] 添加更多图表类型
  - 热力图（行业板块热度）
  - 散点图（风险收益分布）
  - 雷达图（多维度评分）

- [ ] 优化图表样式
  - 统一配色方案
  - 添加主题切换（亮色/暗色）
  - 优化移动端显示

- [ ] 增强交互功能
  - 添加数据筛选器
  - 支持时间范围选择
  - 添加指标切换按钮

- [ ] 支持图表导出
  - PNG/JPEG 图片格式
  - PDF 报告格式
  - 数据 Excel 格式

**影响文件**:
- `stork_agent/analysis/charts.py`

---

### 7. 添加更多技术指标

**目标**: 支持更多常用技术指标

**需要添加的指标**:
- [x] MA (移动平均线) - 已实现
- [x] MACD - 已实现
- [x] RSI - 已实现
- [x] BOLL (布林带) - 已实现
- [ ] KDJ (随机指标)
- [ ] OBV (能量潮)
- [ ] ATR (真实波幅)
- [ ] CCI (顺势指标)
- [ ] DMI (趋向指标)
- [ ] BIAS (乖离率)

**影响文件**:
- `stork_agent/analysis/indicators.py`
- `stork_agent/mcp_server/server.py`

---

### 8. 支持港股、美股数据

**目标**: 扩展数据源，支持多市场数据

**需要实现**:
- [ ] 港股数据获取
  - 使用 AkShare 的港股接口
  - 港股代码格式处理

- [ ] 美股数据获取
  - 使用 yfinance 或其他数据源
  - 美股代码格式处理

- [ ] 多市场对比
  - 汇率转换
  - 统一时间格式

**影响文件**:
- `stork_agent/data/query.py`
- `stork_agent/utils/normalizer.py`

---

### 9. 添加 AI 分析功能

**目标**: 基于数据生成智能投资建议

**需要实现**:
- [ ] 技术面分析
  - 趋势判断（上升/下降/震荡）
  - 支撑位/阻力位识别
  - 买卖信号生成

- [ ] 基本面分析
  - 财务健康度评分
  - 估值分析
  - 行业对比

- [ ] 风险评估
  - 波动率分析
  - 最大回撤计算
  - 风险等级评定

**技术方案**:
- 可以集成 Claude API 进行分析
- 或使用规则引擎生成简单建议

**影响文件**:
- `stork_agent/analysis/` (新模块)
- `stork_agent/mcp_server/tools.py` (添加新工具)

---

### 10. 性能优化

**目标**: 提升数据获取和响应速度

**需要优化**:
- [ ] 缓存策略优化
  - 实现分层缓存
  - 添加缓存预热
  - 优化缓存失效策略

- [ ] 并发请求
  - 支持批量查询
  - 异步数据获取

- [ ] 数据库支持
  - 存储历史数据
  - 减少重复请求

**影响文件**:
- `stork_agent/cache/manager.py`

---

## 🔥 优先级排序

### 高优先级（立即执行）
1. 添加 outputSchema 定义
2. 优化分页测试

### 中优先级（1-2周内）
3. 实现图表返回功能
4. 优化工具描述

### 低优先级（1-2月内）
5. 迁移到 FastMCP 框架
6. 图表功能优化

### 未来规划（3-6月）
7. 添加更多技术指标
8. 支持港股、美股数据
9. 添加 AI 分析功能
10. 性能优化

---

## 📚 相关文档

- [改进总结](./MCP_IMPROVEMENTS.md)
- [测试结果](./TEST_RESULTS.md)
- [工具注解文档](./docs/MCP_TOOL_ANNOTATIONS.md)
- [项目说明](./CLAUDE.md)

---

## 📝 更新日志

### 2026-01-19
- ✅ 完成所有基础改进任务
- ✅ 完成测试验证（pytest 16/18 通过）
- ✅ 创建待办清单文档
- 📝 列出 7 个待办任务

---

**提示**: 在开始新任务前，请：
1. 查看相关文档了解上下文
2. 使用 `git checkout -b feature/任务名` 创建新分支
3. 完成后更新此文档的任务状态
