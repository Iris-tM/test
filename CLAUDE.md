# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Status

**Stork Agent** - A股智能助手，Claude CLI 可调用的对话式股票助手 MCP Agent。

用户可以用日常语言询问股票信息，Agent 理解意图、获取数据、生成自然语言回复（含交互式HTML图表）。

## Build Commands

```bash
# 安装依赖
pip install -r requirements.txt

# 运行 MCP 服务器
python -m stork_agent.mcp_server.server

# 运行 CLI（原有功能保留）
python -m stork_agent query 600519
python -m stork_agent summary
```

## Test Commands

```bash
# 运行所有测试
pytest tests/ -v

# 运行 MCP 工具测试
pytest tests/test_mcp_tools.py -v

# 测试工具列表（不启动服务器）
python tests/test_mcp_inspector.py --test-list

# 启动服务器供 MCP Inspector 连接
python tests/test_mcp_inspector.py --server

# 运行评估验证
python evaluations/run_evaluation.py
```

## Development Commands

```bash
# 查询实时行情
python -m stork_agent query 600519

# 获取历史数据
python -m stork_agent history 600519 --days 30

# 选股筛选
python -m stork_agent screen --pe-max 20 --limit 10

# 公司对比
python -m stork_agent compare 600519,000858 --days 30
```

## Architecture Overview

### 核心设计理念

1. **MCP-First 架构** - 所有功能通过 MCP 协议暴露为 Claude 可调用的工具
2. **自然语言回复** - Responder 层将结构化数据转换为自然语言
3. **交互式图表** - 使用 Plotly 生成交互式 HTML 图表
4. **模块分离** - 数据层、分析层、工具层、缓存层、回答层清晰分离
5. **会话管理** - 支持分页和导出功能

### 关键模块说明

#### `stork_agent/mcp_server/` - MCP 服务器（核心）
- **server.py**: MCP 协议实现，工具注册
- **tools.py**: MCP 工具映射，连接 agent 和 responder
- **session.py**: 会话状态管理（分页、导出）

#### `stork_agent/responder/` - 回答生成层（新增）
- **generator.py**: 主生成器，数据 → 自然语言
- **formatter.py**: 数据格式化工具
- **chart_decider.py**: 图表决策器，决定何时返回图表
- **exporter.py**: 数据导出器（CSV/Excel/JSON）

#### `stork_agent/cache/` - 缓存层（新增）
- **manager.py**: 缓存管理器，支持 JSON + pickle 双模式

#### `stork_agent/agent/` - 底层工具层
- **tools.py**: 数据获取工具，返回 `ApiResponse`
- **schemas.py**: Pydantic 数据模型定义

#### `stork_agent/data/` - 数据层
- **query.py**: 使用 AkShare 获取原始数据
- **screener.py**: 选股筛选逻辑
- **comparator.py**: 公司对比逻辑

#### `stork_agent/analysis/` - 分析层
- **indicators.py**: 技术指标计算 (MA, MACD, RSI, BOLL)
- **charts.py**: 图表生成（Plotly 交互式 HTML）

### 数据流向

```
Claude 理解意图 → 调用 MCP 工具
    ↓
MCP 工具 → 检查缓存 → 数据层 (AkShare)
    ↓
获取结构化数据
    ↓
Responder 层：
  - ChartDecider: 是否需要图表？
  - Formatter: 数据格式化
  - Generator: 生成自然语言回复
  - Charts: 生成 Plotly 交互式 HTML（如需）
    ↓
返回给 Claude：
  - 纯文字回复（Markdown）
  - 或 Markdown 文字 + HTML 图表文件路径
    ↓
Claude 展示给用户（图表可点击打开交互式网页）
```

### 扩展指南

#### 添加新的 MCP 工具

1. 在 `mcp_server/tools.py` 添加工具函数
2. 在 `mcp_server/server.py` 的 `list_tools()` 中注册工具
3. 在 `call_tool()` 中添加处理逻辑

#### 添加新的回答格式

1. 在 `responder/formatter.py` 添加格式化函数
2. 在 `responder/generator.py` 的 `generate_response()` 中添加对应分支

#### 添加新的图表类型

1. 在 `analysis/charts.py` 添加绘图函数（使用 Plotly）
2. 在 `responder/chart_decider.py` 的 `get_chart_type()` 中添加类型判断

### 依赖关系

```
mcp_server/server.py
    ├── mcp_server/tools.py
    │   ├── agent/tools.py
    │   │   ├── data/query.py
    │   │   ├── data/screener.py
    │   │   ├── data/comparator.py
    │   │   └── analysis/indicators.py
    │   └── responder/
    │       ├── generator.py
    │       ├── formatter.py
    │       ├── chart_decider.py
    │       └── exporter.py
    └── mcp_server/session.py
        └── cache/manager.py

analysis/charts.py (Plotly HTML)
    └── analysis/indicators.py (部分使用)
```

### 重要约定

1. 所有 MCP 工具返回自然语言文本（Markdown 格式）
2. 图表返回 HTML 文件路径，不使用 base64
3. 使用 `normalize_stock_code()` 统一股票代码格式
4. 缓存策略：历史数据1天，实时数据5分钟，筛选结果1小时
5. 错误处理要完善，返回清晰的错误信息
6. 使用 `from __future__ import annotations` 支持类型提示

### 常用工具函数

- `normalize_stock_code(code)` - 规范化股票代码为6位
- `format_number(value)` - 格式化数字显示
- `format_percentage(value)` - 格式化百分比
- `format_market_cap(cap)` - 格式化市值显示
- `format_volume(vol)` - 格式化成交量显示
- `generate_response(intent, data)` - 生成自然语言回复
- `should_generate_chart(intent, data)` - 决定是否生成图表

### 输出目录结构

```
output/
├── charts/          # Plotly HTML 图表
├── exports/         # 数据导出（CSV/Excel/JSON）
└── cache/           # 缓存文件
    ├── json/        # JSON 格式缓存
    └── pickle/      # Pickle 格式缓存
```

### MCP 工具列表

| 工具名 | 描述 | 参数 |
|--------|------|------|
| stork_query_stock | 查询股票实时行情 | code |
| stork_screen_stocks | 筛选股票（支持分页） | criteria, page, page_size |
| stork_next_page | 查看下一页 | - |
| stork_prev_page | 查看上一页 | - |
| stork_export_current_result | 导出当前查询结果 | format (csv/excel/json) |
| stork_compare_stocks | 对比多只股票 | codes, days |
| stork_get_stock_history | 获取K线数据 | code, days, period |
| stork_search_stocks | 搜索股票 | keyword, limit |
| stork_get_financials | 获取财务数据 | code |
| stork_calculate_indicator | 计算技术指标 | code, indicator, period |
| stork_get_market_summary | 获取市场概览 | - |

**工具命名规范**: 所有工具使用 `stork_` 前缀，遵循 MCP 最佳实践，避免与其他 MCP 服务器的工具命名冲突。

### 配置说明

主要配置项（环境变量或 .env 文件）：

- `OUTPUT_DIR`: 输出目录（默认 ./output）
- `CACHE_ENABLED`: 是否启用缓存（默认 true）
- `CHART_FORMAT`: 图表格式（html/png）
- `SESSION_TIMEOUT`: 会话超时时间（默认 1800 秒）
- `DEFAULT_PAGE_SIZE`: 默认每页数量（默认 50）

---

## 测试与验证

### 测试文件结构

```
tests/
├── test_mcp_tools.py          # MCP 工具功能测试（pytest）
├── test_mcp_inspector.py      # MCP Inspector 集成测试
└── test_agent.py              # 原有 agent 层测试（保留）

evaluations/
├── questions.xml              # LLM 有效性评估问题（10个）
└── run_evaluation.py          # 评估验证脚本
```

### MCP Inspector 测试

使用 MCP Inspector 进行交互式测试：

```bash
# 方法 1: 直接启动
python -m stork_agent.mcp_server.server

# 方法 2: 使用测试脚本
python tests/test_mcp_inspector.py --server

# 然后在另一个终端运行 Inspector
npx @modelcontextprotocol/inspector python -m stork_agent.mcp_server.server
```

### 工具注解文档

详细的工具注解信息请参考：`docs/MCP_TOOL_ANNOTATIONS.md`

包含内容：
- 所有工具的 readOnlyHint、destructiveHint、idempotentHint、openWorldHint 注解
- 工具使用场景和示例
- 注解汇总表
- FastMCP 迁移指南（如需完整注解支持）

---

## 文档结构

```
docs/
└── MCP_TOOL_ANNOTATIONS.md    # 工具注解文档

evaluations/
├── questions.xml              # 评估问题（XML格式）
└── run_evaluation.py          # 评估验证脚本

MCP_IMPROVEMENTS.md            # MCP 改进总结文档
```

---

## 最近改进记录

### 2026-01-19 - MCP 服务器优化

**改进内容**:
1. ✅ 工具命名规范化 - 添加 `stork_` 前缀避免命名冲突
2. ✅ 工具描述优化 - 更详细、准确的描述
3. ✅ 错误处理改进 - 使用特定异常类型替代裸 except
4. ✅ 测试套件创建 - 完整的 pytest + Inspector 测试
5. ✅ 工具注解文档 - 完整的注解说明
6. ✅ 评估问题集 - 10个 LLM 有效性评估问题

**详细内容**: 查看 `MCP_IMPROVEMENTS.md`

---

## 在 Claude Desktop 中使用

在 Claude Desktop 的配置文件中添加此 MCP 服务器：

**Windows 配置文件位置**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "stork-agent": {
      "command": "python",
      "args": ["-m", "stork_agent.mcp_server.server"],
      "cwd": "C:\\Users\\zdn01\\Documents\\AI_projects\\main_projects\\stork_agent"
    }
  }
}
```

**使用示例**:

```
用户: 查询一下贵州茅台现在的股价
Claude: [调用 stork_query_stock] 返回实时行情...

用户: 帮我筛选市盈率低于20的股票
Claude: [调用 stork_screen_stocks] 返回符合条件的股票...

用户: 下一页
Claude: [调用 stork_next_page] 返回下一页数据...
```
