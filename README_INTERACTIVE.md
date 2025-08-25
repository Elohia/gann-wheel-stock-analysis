# 江恩轮中轮+量价分析系统 - 交互式使用指南

## 概述

本系统提供了基于akshare数据源的股票分析工具，集成了江恩轮中轮分析和量价分析功能，支持命令行交互式操作。

## 功能特性

### 🎯 核心功能
- **江恩轮中轮分析**: 时间周期分析、价格轮回计算、支撑阻力位识别
- **量价分析**: 量价关系评估、背离分析、交易信号生成
- **多数据源支持**: 优先使用akshare，备用yfinance和tushare
- **交互式界面**: 支持命令行参数和交互式输入

### 📊 数据源配置
- **主要数据源**: akshare (优先级1)
- **备用数据源**: tushare (优先级2), yfinance (优先级3)
- **数据存储**: SQLite数据库
- **数据周期**: 支持1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y

## 使用方法

### 方法1: 命令行参数

```bash
# 分析单只股票（默认1年数据）
python analyze_stock.py 000001

# 分析指定周期数据
python analyze_stock.py 600036.SH --period 6mo

# 查看帮助信息
python analyze_stock.py --help
```

### 方法2: 交互式输入

```bash
# 启动交互模式
python analyze_stock.py

# 然后按提示输入股票代码
🔍 股票代码: 000001
```

### 方法3: 完整系统测试

```bash
# 运行测试脚本
python test_akshare_interactive.py

# 运行交互式分析程序
python interactive_analysis.py
```

## 支持的股票代码格式

| 格式 | 示例 | 说明 |
|------|------|------|
| 6位数字 | `000001` | 自动判断交易所 |
| 深交所完整格式 | `000001.SZ` | 深圳证券交易所 |
| 上交所完整格式 | `600036.SH` | 上海证券交易所 |

### 自动交易所判断规则
- `000xxx`, `002xxx`, `300xxx` → 深交所 (.SZ)
- `600xxx`, `601xxx`, `603xxx`, `605xxx` → 上交所 (.SH)
- 其他代码默认为深交所 (.SZ)

## 分析结果说明

### 🔮 江恩轮中轮分析
- **时间周期**: 识别的时间循环模式
- **价格轮回**: 价格运动的循环特征
- **支撑位**: 预测的价格支撑水平
- **阻力位**: 预测的价格阻力水平

### 📈 量价分析
- **量价关系**: 成交量与价格变动的协调性
- **配合度评分**: 量价配合的数值评估
- **量价背离**: 是否存在量价背离现象
- **交易建议**: BUY/SELL/HOLD 建议
- **信心度**: 建议的可信度百分比
- **风险等级**: low/medium/high
- **综合评分**: A+到D-的等级评分

### 🎯 交易信号类型
- **底背离**: 价格创新低但指标不创新低
- **顶背离**: 价格创新高但指标不创新高
- **异常放量**: 成交量异常放大
- **量价配合**: 量价关系良好

## 配置文件说明

### config.yaml 主要配置

```yaml
data_sources:
  akshare:
    enabled: true
    priority: 1  # 最高优先级
  
  tushare:
    enabled: false
    priority: 2
    token: "your_token_here"
  
  yfinance:
    enabled: true
    priority: 3

database:
  type: "sqlite"
  sqlite:
    path: "data/stock_analysis.db"
```

## 常见问题

### Q: 如何更改数据源优先级？
A: 修改 `config.yaml` 中各数据源的 `priority` 值，数值越小优先级越高。

### Q: 支持哪些股票市场？
A: 目前主要支持A股市场（上交所、深交所），通过akshare获取数据。

### Q: 分析结果保存在哪里？
A: 数据存储在 `data/stock_analysis.db` SQLite数据库中，日志保存在 `logs/` 目录。

### Q: 如何获取更多历史数据？
A: 使用 `--period` 参数指定更长的时间周期，如 `--period 2y` 获取2年数据。

### Q: 程序运行出错怎么办？
A: 检查 `logs/` 目录下的日志文件，通常包含详细的错误信息和解决建议。

## 文件结构

```
江恩轮中轮+量价分析/
├── analyze_stock.py              # 命令行分析工具
├── interactive_analysis.py       # 交互式分析程序
├── test_akshare_interactive.py   # 测试脚本
├── config.yaml                   # 配置文件
├── src/                          # 源代码目录
│   ├── data/                     # 数据获取模块
│   ├── analysis/                 # 分析模块
│   ├── storage/                  # 数据存储模块
│   └── utils/                    # 工具模块
├── data/                         # 数据存储目录
├── logs/                         # 日志目录
└── README_INTERACTIVE.md         # 本文档
```

## 更新日志

### v1.0.0 (2024-08-25)
- ✅ 集成akshare作为主要数据源
- ✅ 实现命令行交互式股票代码输入
- ✅ 优化分析结果显示格式
- ✅ 支持多种股票代码格式
- ✅ 添加详细的使用说明文档

## 技术支持

如有问题或建议，请查看日志文件或联系开发团队。

---

**注意**: 本系统仅供学习和研究使用，不构成投资建议。投资有风险，决策需谨慎。