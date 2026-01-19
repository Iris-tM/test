# Stork Agent - A股智能助手

基于 Python 的 A股数据查询和选股分析工具，使用 AkShare 作为免费数据源。

**核心特性**：Claude CLI 可调用的对话式股票助手 MCP Agent。用户可以用日常语言询问股票信息，Agent 理解意图、获取数据、生成自然语言回复（含交互式HTML图表）。

## 功能特性

- **MCP 服务器** - 通过 Model Context Protocol 集成 Claude CLI
- **自然语言交互** - 将结构化数据转换为自然语言回复
- **实时行情查询** - 获取个股实时价格、涨跌幅、成交量等
- **历史K线数据** - 支持日线、周线、月线，前复权/后复权
- **选股筛选** - 按PE/PB/市值/涨跌幅等条件筛选股票（支持分页）
- **公司对比** - 多公司财务指标和价格表现对比
- **财务数据** - 获取营收、净利润、ROE等财务指标
- **技术指标** - MA、MACD、RSI、BOLL等
- **交互式图表** - 使用 Plotly 生成交互式 HTML 图表
- **数据导出** - 支持 CSV、Excel、JSON 格式导出
- **智能缓存** - 自动缓存历史数据，减少API调用
- **CLI工具** - 命令行工具，方便快速查询

## 安装

### 环境要求

- Python 3.9+
- 依赖库见 `requirements.txt`

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置

复制 `.env.example` 为 `.env` 并根据需要修改配置：

```bash
cp .env.example .env
```

## 使用方法

### 作为 MCP 服务器（推荐）

启动 MCP 服务器：

```bash
python -m stork_agent.mcp.server
```

在 Claude CLI 配置中添加此 MCP 服务器，然后即可通过对话方式查询股票信息：

```
用户：帮我看看茅台现在怎么样？
Agent：[调用 query_stock 工具] 返回实时行情...

用户：筛选一下PE小于30的科技股
Agent：[调用 screen_stocks 工具] 返回符合条件的股票列表...

用户：下一页
Agent：[调用 next_page 工具] 返回下一页数据...

用户：导出Excel
Agent：[调用 export_current_result 工具] 返回文件路径...
```

### 作为 Python 库

```python
from stork_agent import (
    get_stock_realtime,
    get_stock_history,
    screen_stocks,
    compare_stocks,
    get_financials,
    calculate_indicator
)

# 查询实时行情
result = get_stock_realtime("600519")
if result.success:
    print(result.data)  # {'code': '600519', 'name': '贵州茅台', 'price': 1680.50, ...}

# 选股筛选
filters = {"pe_max": 20, "market_cap_min": 100}
result = screen_stocks(filters)
if result.success:
    print(f"找到 {result.data['total']} 只股票")

# 公司对比
result = compare_stocks(["600519", "000858"], days=30)
if result.success:
    for stock in result.data['stocks']:
        print(f"{stock['name']}: {stock['period_change_pct']:.2f}%")
```

### CLI 命令行

```bash
# 查询实时行情
python -m stork_agent query 600519

# 获取历史数据
python -m stork_agent history 600519 --days 30

# 选股筛选
python -m stork_agent screen --pe-max 20 --limit 10

# 公司对比
python -m stork_agent compare 600519,000858 --days 30

# 获取财务数据
python -m stork_agent financial 600519

# 计算技术指标
python -m stork_agent indicator 600519 ma --period 20
python -m stork_agent indicator 600519 macd

# 搜索股票
python -m stork_agent search 茅台

# 市场概览
python -m stork_agent summary
```

## 项目结构

```
stork_agent/
├── stork_agent/
│   ├── __init__.py         # 包入口
│   ├── cli.py              # CLI 命令行工具
│   ├── config.py           # 配置管理
│   ├── mcp/                # MCP 服务器（核心）
│   │   ├── server.py       # MCP 协议实现
│   │   ├── tools.py        # MCP 工具映射
│   │   └── session.py      # 会话状态管理
│   ├── responder/          # 回答生成层
│   │   ├── generator.py    # 主生成器
│   │   ├── formatter.py    # 数据格式化
│   │   ├── chart_decider.py # 图表决策器
│   │   └── exporter.py     # 数据导出
│   ├── cache/              # 缓存层
│   │   └── manager.py      # 缓存管理器
│   ├── agent/              # 底层工具层
│   │   ├── tools.py        # 数据获取工具
│   │   └── schemas.py      # 数据结构定义
│   ├── data/               # 数据层
│   │   ├── query.py        # 数据查询
│   │   ├── screener.py     # 选股筛选
│   │   └── comparator.py   # 公司对比
│   ├── analysis/           # 分析层
│   │   ├── indicators.py   # 技术指标计算
│   │   └── charts.py       # 图表绘制（Plotly）
│   └── utils/              # 工具模块
│       └── helpers.py      # 辅助函数
├── tests/                  # 测试
├── output/                 # 输出目录
│   ├── charts/             # HTML 图表
│   ├── exports/            # 数据导出
│   └── cache/              # 缓存文件
├── requirements.txt        # 依赖管理
├── .env.example            # 环境变量示例
├── README.md               # 项目说明
└── CLAUDE.md               # Claude Code 指南
```

## MCP 工具列表

| 工具名 | 描述 | 参数 |
|--------|------|------|
| query_stock | 查询股票实时行情 | code |
| screen_stocks | 筛选股票（支持分页） | criteria, page, page_size |
| next_page | 查看下一页 | - |
| prev_page | 查看上一页 | - |
| export_current_result | 导出当前查询结果 | format (csv/excel/json) |
| compare_stocks | 对比多只股票 | codes, days |
| get_stock_history | 获取K线数据 | code, days, period |
| search_stocks | 搜索股票 | keyword, limit |
| get_financials | 获取财务数据 | code |
| calculate_indicator | 计算技术指标 | code, indicator, period |
| get_market_summary | 获取市场概览 | - |

## 数据源

当前使用 **AkShare** 作为数据源：
- 免费无需注册
- 数据全面
- 更新及时

后续可扩展支持 **TuShare** 等其他数据源。

## 致谢

本项目的部署主要依赖以下开源 Python 库，非常感谢这些优秀的开源项目！请给这些仓库多点 ⭐

| 库名 | 说明 | 链接 |
|------|------|------|
| **AkShare** | 免费、好用的财经数据接口 | [akshare](https://github.com/akfamily/akshare) |
| **FastAPI** | 现代、快速的 Web 框架 | [fastapi](https://github.com/fastapi/fastapi) |
| **Plotly** | 交互式图表可视化库 | [plotly](https://github.com/plotly/plotly.py) |
| **Pandas** | 强大的数据分析和处理库 | [pandas](https://github.com/pandas-dev/pandas) |
| **Pydantic** | 数据验证和设置管理 | [pydantic](https://github.com/pydantic/pydantic) |
| **Uvicorn** | ASGI 服务器 | [uvicorn](https://github.com/encode/uvicorn) |
| **ModelContextProtocol** | MCP 协议实现 | [modelcontextprotocol](https://github.com/modelcontextprotocol) |
| **Typer** | 命令行界面构建库 | [typer](https://github.com/fastapi/typer) |

感谢所有为开源社区做出贡献的开发者！🙏

## 配置说明

主要配置项（环境变量或 .env 文件）：

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| OUTPUT_DIR | 输出目录 | ./output |
| CACHE_ENABLED | 是否启用缓存 | true |
| CHART_FORMAT | 图表格式 | html |
| SESSION_TIMEOUT | 会话超时时间（秒） | 1800 |
| DEFAULT_PAGE_SIZE | 默认每页数量 | 50 |

## 缓存策略

- **历史数据**（K线、财务）：TTL = 1天
- **实时数据**（当前价格）：TTL = 5分钟
- **筛选结果**：TTL = 1小时
- **静态数据**（股票列表）：TTL = 7天

## 注意事项

1. 数据更新时间：A股交易日 9:30-15:00
2. 部分指标可能因数据源限制无法获取
3. 图表存储在 `output/charts/` 目录，可点击打开交互式网页
4. 建议使用虚拟环境隔离依赖
5. MCP 服务器需要 Claude CLI 配置

## 开发

### 运行测试

```bash
pytest tests/
```

### 代码格式化

```bash
black stork_agent/
isort stork_agent/
```

### 类型检查

```bash
mypy stork_agent/
```

## License

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
