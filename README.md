# 江恩轮中轮+量价分析系统

一个专业的股票技术分析系统，集成了江恩轮中轮理论和量价分析方法，为投资者提供全面的股票分析工具。

## 🌟 主要特性

### 📊 数据获取与存储
- **多数据源支持**: 集成tushare、yfinance、akshare等主流数据源
- **智能数据管理**: 支持SQLite和MySQL数据库，自动数据更新和清理
- **数据质量保证**: 内置数据验证和清洗机制

### 🔮 江恩轮中轮分析
- **时间周期分析**: 基于江恩理论的时间轮回计算
- **价格轮回分析**: 江恩价格正方形和价格循环识别
- **江恩角度线**: 1x1、1x2、2x1等关键角度线计算
- **支撑阻力位**: 基于江恩理论的关键价位识别
- **时间价格共振**: 时间周期与价格周期的共振分析
- **趋势预测**: 基于江恩轮中轮的未来走势预测

### 📈 量价分析
- **量价关系分析**: 成交量与价格变化的相关性分析
- **背离检测**: 价格与成交量背离信号识别
- **异常成交量**: 放量、缩量等异常成交量模式识别
- **量价配合度**: 量价配合程度的量化评估
- **交易信号生成**: 基于量价关系的买卖信号
- **趋势确认**: 利用成交量确认价格趋势

### 🛠️ 系统特性
- **模块化设计**: 松耦合的模块化架构，易于扩展和维护
- **配置化管理**: 灵活的YAML配置文件，支持多环境配置
- **完善的日志**: 多级别日志记录，便于调试和监控
- **异常处理**: 健壮的错误处理机制，确保系统稳定性
- **批量处理**: 支持多只股票的批量分析
- **命令行工具**: 提供便捷的命令行接口

## 🚀 快速开始

### 环境要求
- Python 3.8+
- 操作系统: Windows/Linux/macOS

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd 江恩轮中轮+量价分析
```

2. **创建虚拟环境**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **配置系统**
```bash
cp config/config.yaml.example config/config.yaml
# 编辑config.yaml文件，配置数据源和数据库
```

### 基本使用

#### Python脚本方式

```python
from main import StockAnalysisSystem

# 初始化系统
system = StockAnalysisSystem('config/config.yaml')

# 获取并存储股票数据
system.fetch_and_store_data('000001.SZ', '1y')

# 执行江恩轮中轮分析
gann_result = system.analyze_stock('000001.SZ', 'gann')
print("江恩分析结果:", gann_result)

# 执行量价分析
vp_result = system.analyze_stock('000001.SZ', 'volume_price')
print("量价分析结果:", vp_result)

# 执行综合分析
all_result = system.analyze_stock('000001.SZ', 'all')
print("综合分析结果:", all_result)
```

#### 命令行方式

```bash
# 分析单只股票
python main.py --symbol 000001.SZ --analysis all

# 批量分析
python main.py --batch stocks.txt --analysis all

# 更新数据
python main.py --symbol 000001.SZ --update-data

# 查看帮助
python main.py --help
```

## 📁 项目结构

```
江恩轮中轮+量价分析/
├── src/                          # 源代码目录
│   ├── data/                     # 数据模块
│   │   ├── data_fetcher.py      # 数据获取
│   │   ├── database_manager.py   # 数据库管理
│   │   └── __init__.py
│   ├── analysis/                 # 分析模块
│   │   ├── gann/                # 江恩分析
│   │   │   ├── gann_wheel.py    # 江恩轮中轮
│   │   │   └── __init__.py
│   │   ├── volume_price/        # 量价分析
│   │   │   ├── volume_price_analyzer.py
│   │   │   └── __init__.py
│   │   └── __init__.py
│   ├── utils/                   # 工具模块
│   │   ├── config_manager.py    # 配置管理
│   │   ├── logger.py           # 日志工具
│   │   └── __init__.py
│   └── __init__.py
├── config/                      # 配置文件
│   ├── config.yaml             # 主配置文件
│   └── config.yaml.example     # 配置模板
├── tests/                      # 测试文件
│   ├── test_gann_wheel.py      # 江恩分析测试
│   ├── test_volume_price_analyzer.py  # 量价分析测试
│   └── test_system_integration.py     # 系统集成测试
├── docs/                       # 文档
│   ├── quick_start.md          # 快速开始
│   └── api_reference.md        # API参考
├── logs/                       # 日志文件
├── data/                       # 数据文件
├── main.py                     # 主程序入口
├── test_system.py              # 系统测试脚本
├── example_usage.py            # 使用示例
├── requirements.txt            # 依赖包列表
├── setup.py                    # 安装脚本
└── README.md                   # 项目说明
```

## 🔧 配置说明

### 数据源配置

```yaml
data_sources:
  primary: tushare              # 主数据源
  fallback: [yfinance, akshare] # 备用数据源
  
  tushare:
    token: "your_tushare_token"  # tushare API token
    enabled: true
    
  yfinance:
    enabled: true
    
  akshare:
    enabled: true
```

### 数据库配置

```yaml
database:
  type: sqlite                   # 数据库类型: sqlite/mysql
  
  sqlite:
    path: "data/stock_data.db"   # SQLite数据库路径
    
  mysql:                        # MySQL配置(可选)
    host: localhost
    port: 3306
    username: root
    password: password
    database: stock_analysis
```

### 分析参数配置

```yaml
analysis:
  gann:
    time_cycles: [7, 14, 21, 30, 45, 60, 90]  # 时间周期
    price_squares: [144, 169, 225, 256, 289]  # 价格正方形
    angle_lines: ["1x1", "1x2", "2x1", "1x4", "4x1"]  # 角度线
    
  volume_price:
    ma_periods: [5, 10, 20, 60]   # 移动平均周期
    volume_threshold: 2.0         # 异常成交量阈值
    correlation_period: 20        # 相关性计算周期
```

## 📊 分析结果说明

### 江恩轮中轮分析结果

```python
{
    "time_cycles": {              # 时间周期分析
        "current_cycle": 21,      # 当前所处周期
        "cycle_position": 0.75,   # 周期位置(0-1)
        "next_turning_point": "2024-02-15"  # 下个转折点
    },
    "price_cycles": {            # 价格轮回分析
        "current_square": 169,    # 当前价格正方形
        "support_levels": [12.5, 13.0, 13.5],  # 支撑位
        "resistance_levels": [14.0, 14.5, 15.0]  # 阻力位
    },
    "gann_angles": {             # 江恩角度线
        "1x1_line": 13.2,        # 1x1角度线价位
        "trend_direction": "up",  # 趋势方向
        "angle_support": 12.8     # 角度线支撑
    },
    "resonance_analysis": {      # 共振分析
        "time_price_resonance": 0.85,  # 时间价格共振度
        "resonance_points": ["2024-01-15", "2024-03-20"]  # 共振点
    }
}
```

### 量价分析结果

```python
{
    "volume_price_relation": {   # 量价关系
        "correlation": 0.72,     # 相关系数
        "trend_confirmation": "strong",  # 趋势确认强度
        "price_volume_sync": true  # 价量同步性
    },
    "divergence_analysis": {     # 背离分析
        "price_divergence": false,  # 价格背离
        "volume_divergence": true,  # 成交量背离
        "divergence_strength": "weak"  # 背离强度
    },
    "abnormal_volume": {         # 异常成交量
        "volume_spikes": ["2024-01-10", "2024-01-20"],  # 放量日期
        "volume_dries": ["2024-01-15"],  # 缩量日期
        "avg_volume_ratio": 1.5   # 平均成交量比率
    },
    "trading_signals": {         # 交易信号
        "buy_signals": ["2024-01-12"],   # 买入信号
        "sell_signals": ["2024-01-25"],  # 卖出信号
        "signal_strength": "medium"       # 信号强度
    }
}
```

## 🧪 测试

### 运行所有测试
```bash
python -m pytest tests/ -v
```

### 运行特定测试
```bash
# 江恩分析测试
python -m pytest tests/test_gann_wheel.py -v

# 量价分析测试
python -m pytest tests/test_volume_price_analyzer.py -v

# 系统集成测试
python -m pytest tests/test_system_integration.py -v
```

### 测试覆盖率
```bash
python -m pytest tests/ --cov=src --cov-report=html
```

## 📚 文档

- [快速开始指南](docs/quick_start.md)
- [API参考文档](docs/api_reference.md)
- [配置文件说明](config/config.yaml.example)

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

### 开发规范

- 遵循PEP 8代码风格
- 添加适当的函数和类注释
- 为新功能编写测试用例
- 更新相关文档

## 📝 更新日志

### v1.0.0 (2024-01-15)
- ✨ 初始版本发布
- 🔮 实现江恩轮中轮分析功能
- 📈 实现量价分析功能
- 📊 支持多数据源股票数据获取
- 🛠️ 完善的配置管理和日志系统
- 🧪 完整的测试用例覆盖

## ⚠️ 免责声明

本系统仅供学习和研究使用，不构成任何投资建议。股票投资有风险，投资者应该根据自己的判断做出投资决策，并承担相应的投资风险。

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- 感谢江恩理论的创始人威廉·江恩(William Delbert Gann)
- 感谢开源社区提供的优秀工具和库
- 感谢所有贡献者的支持和帮助

## 📞 联系方式

如有问题或建议，请通过以下方式联系:

- 提交 Issue: [GitHub Issues](https://github.com/your-repo/issues)
- 邮箱: your-email@example.com

---

**⭐ 如果这个项目对您有帮助，请给我们一个星标！**