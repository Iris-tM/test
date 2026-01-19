# Stork Agent MCP 工具注解文档

本文档记录了 Stork Agent MCP 服务器的所有工具注解信息。

## 工具注解说明

| 注解 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `readOnlyHint` | boolean | false | 工具只读，不修改系统状态 |
| `destructiveHint` | boolean | true | 工具可能执行破坏性操作 |
| `idempotentHint` | boolean | false | 幂等性：重复调用相同参数无副作用 |
| `openWorldHint` | boolean | true | 工具与外部世界交互 |

---

## 工具列表

### 1. stork_query_stock

**描述**: 查询股票实时行情信息。输入股票代码（如 600519）返回当前价格、涨跌幅、成交量等数据。

**注解**:
```python
{
    "readOnlyHint": True,      # 只读操作，不修改任何数据
    "destructiveHint": False,  # 不执行任何破坏性操作
    "idempotentHint": True,    # 有缓存，多次查询结果一致
    "openWorldHint": True      # 调用外部 AkShare API
}
```

**使用场景**: 查询单只股票的实时行情数据

**示例**: `stork_query_stock(code="600519")`

---

### 2. stork_screen_stocks

**描述**: 根据条件筛选股票。支持市盈率、市值、涨跌幅等多维度筛选，返回符合条件的股票列表（支持分页）。

**注解**:
```python
{
    "readOnlyHint": True,      # 只读操作
    "destructiveHint": False,  # 不执行任何破坏性操作
    "idempotentHint": True,    # 相同条件筛选结果一致（有缓存）
    "openWorldHint": True      # 调用外部 API
}
```

**使用场景**: 按条件筛选股票，如低PE、高市值等

**示例**: `stork_screen_stocks(criteria={"pe_max": 20, "market_cap_min": 100}, page=1, page_size=50)`

---

### 3. stork_next_page

**描述**: 查看当前筛选或搜索结果的下一页数据。需要先执行 screen_stocks 或 search_stocks。

**注解**:
```python
{
    "readOnlyHint": True,      # 只读取会话状态
    "destructiveHint": False,  # 不破坏任何数据
    "idempotentHint": False,   # 每次调用会改变页码状态
    "openWorldHint": False     # 只操作内存中的会话状态
}
```

**使用场景**: 浏览筛选结果的下一页

**示例**: `stork_next_page()`

---

### 4. stork_prev_page

**描述**: 查看当前筛选或搜索结果的上一页数据。需要先执行 screen_stocks 或 search_stocks。

**注解**:
```python
{
    "readOnlyHint": True,      # 只读取会话状态
    "destructiveHint": False,  # 不破坏任何数据
    "idempotentHint": False,   # 每次调用会改变页码状态
    "openWorldHint": False     # 只操作内存中的会话状态
}
```

**使用场景**: 浏览筛选结果的上一页

**示例**: `stork_prev_page()`

---

### 5. stork_export_current_result

**描述**: 导出当前查询的完整数据到文件。支持 CSV、Excel、JSON 格式。需要先执行筛选或搜索操作。

**注解**:
```python
{
    "readOnlyHint": False,     # 会写入文件系统
    "destructiveHint": False,  # 只是创建文件，不破坏现有数据
    "idempotentHint": False,   # 每次导出可能覆盖文件
    "openWorldHint": False     # 只写入本地文件系统
}
```

**使用场景**: 导出筛选结果到文件

**示例**: `stork_export_current_result(format="csv")`

---

### 6. stork_compare_stocks

**描述**: 对比多只股票的关键指标。输入股票代码列表，返回市值、PE、ROE 等指标对比表格。

**注解**:
```python
{
    "readOnlyHint": True,      # 只读操作
    "destructiveHint": False,  # 不执行任何破坏性操作
    "idempotentHint": True,    # 相同条件对比结果一致
    "openWorldHint": True      # 调用外部 API
}
```

**使用场景**: 对比多只股票的关键指标

**示例**: `stork_compare_stocks(codes=["600519", "000858"], days=30)`

---

### 7. stork_get_stock_history

**描述**: 获取股票历史K线数据。返回指定天数内的开盘、收盘、最高、最低价等信息。支持日线、周线、月线。

**注解**:
```python
{
    "readOnlyHint": True,      # 只读操作
    "destructiveHint": False,  # 不执行任何破坏性操作
    "idempotentHint": True,    # 相同参数结果一致（有缓存）
    "openWorldHint": True      # 调用外部 API
}
```

**使用场景**: 获取股票历史K线数据

**示例**: `stork_get_stock_history(code="600519", days=30, period="daily")`

---

### 8. stork_search_stocks

**描述**: 搜索股票。支持按代码或名称模糊搜索。返回匹配的股票列表（支持分页）。

**注解**:
```python
{
    "readOnlyHint": True,      # 只读操作
    "destructiveHint": False,  # 不执行任何破坏性操作
    "idempotentHint": True,    # 相同关键词搜索结果一致
    "openWorldHint": True      # 调用外部 API
}
```

**使用场景**: 按关键词搜索股票

**示例**: `stork_search_stocks(keyword="茅台", limit=10)`

---

### 9. stork_get_financials

**描述**: 获取股票财务数据。包括营收、净利润、ROE、资产负债率等财务指标。

**注解**:
```python
{
    "readOnlyHint": True,      # 只读操作
    "destructiveHint": False,  # 不执行任何破坏性操作
    "idempotentHint": True,    # 相同股票财务数据一致（有缓存）
    "openWorldHint": True      # 调用外部 API
}
```

**使用场景**: 查看股票财务数据

**示例**: `stork_get_financials(code="600519")`

---

### 10. stork_calculate_indicator

**描述**: 计算技术指标。支持 MA（移动平均线）、MACD、RSI（相对强弱指标）、BOLL（布林带）等常用技术指标。

**注解**:
```python
{
    "readOnlyHint": True,      # 只读操作
    "destructiveHint": False,  # 不执行任何破坏性操作
    "idempotentHint": True,    # 相同参数计算结果一致
    "openWorldHint": True      # 调用外部 API 获取历史数据
}
```

**使用场景**: 计算技术指标进行分析

**示例**: `stork_calculate_indicator(code="600519", indicator="ma", period=20)`

---

### 11. stork_get_market_summary

**描述**: 获取市场概览。包括上证指数、深证成指、创业板指等主要指数表现和市场统计数据。

**注解**:
```python
{
    "readOnlyHint": True,      # 只读操作
    "destructiveHint": False,  # 不执行任何破坏性操作
    "idempotentHint": True,    # 市场概览数据一致（有缓存）
    "openWorldHint": True      # 调用外部 API
}
```

**使用场景**: 查看市场整体表现

**示例**: `stork_get_market_summary()`

---

## 注解汇总表

| 工具名称 | readOnlyHint | destructiveHint | idempotentHint | openWorldHint |
|---------|--------------|-----------------|----------------|---------------|
| stork_query_stock | ✅ True | ❌ False | ✅ True | ✅ True |
| stork_screen_stocks | ✅ True | ❌ False | ✅ True | ✅ True |
| stork_next_page | ✅ True | ❌ False | ❌ False | ❌ False |
| stork_prev_page | ✅ True | ❌ False | ❌ False | ❌ False |
| stork_export_current_result | ❌ False | ❌ False | ❌ False | ❌ False |
| stork_compare_stocks | ✅ True | ❌ False | ✅ True | ✅ True |
| stork_get_stock_history | ✅ True | ❌ False | ✅ True | ✅ True |
| stork_search_stocks | ✅ True | ❌ False | ✅ True | ✅ True |
| stork_get_financials | ✅ True | ❌ False | ✅ True | ✅ True |
| stork_calculate_indicator | ✅ True | ❌ False | ✅ True | ✅ True |
| stork_get_market_summary | ✅ True | ❌ False | ✅ True | ✅ True |

---

## 实现说明

当前实现使用的是底层 MCP Python SDK (`mcp.server.Server`)，该 SDK 不直接支持在工具定义中传递注解参数。

### 未来改进方向

如果需要完整的注解支持，建议迁移到 FastMCP 框架：

```python
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

mcp = FastMCP("stork_mcp")

class QueryStockInput(BaseModel):
    code: str = Field(..., description="股票代码")

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
    '''查询股票实时行情'''
    # 实现代码
    pass
```

### 当前解决方案

虽然底层 SDK 不直接支持注解，但：

1. **工具名称遵循约定**: 使用 `stork_` 前缀避免命名冲突
2. **描述清晰准确**: 详细描述工具功能和副作用
3. **本文档记录**: 作为工具行为的参考文档
4. **客户端可推断**: Claude 可以根据工具描述推断其行为
