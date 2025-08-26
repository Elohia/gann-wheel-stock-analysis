# 江恩轮中轮股票分析系统

基于江恩理论和量价分析的智能股票分析工具，提供完整的API接口和交互式分析功能。

## 🌟 项目特色

### 📈 实时数据获取
- **多数据源支持**：AKShare、新浪财经、东方财富等
- **实时价格监控**：5秒级数据更新，支持价格变动告警
- **分时数据分析**：获取详细的分时成交数据
- **盘口数据展示**：实时买卖五档数据
- **智能缓存机制**：提升数据获取效率，减少API调用

### 核心分析功能
- **江恩轮中轮分析**：基于江恩理论的时间和价格分析
- **量价关系分析**：深度分析成交量与价格的关系
- **智能买卖点识别**：自动识别潜在的买入和卖出信号
- **多维度技术指标**：整合多种技术分析指标

### 技术架构
- **RESTful API**：完整的HTTP接口，支持第三方集成
- **交互式界面**：用户友好的命令行交互界面
- **数据持久化**：SQLite数据库存储分析结果
- **实时数据**：集成AKShare获取实时股票数据

## 🚀 快速开始

### 环境要求
- Python 3.8+
- 依赖包见 `requirements.txt`

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/Elohia/gann-wheel-stock-analysis.git
cd gann-wheel-stock-analysis
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置设置**
```bash
cp config/config.example.yaml config/config.yaml
# 根据需要修改配置文件
```

### 使用方式

#### 1. API服务模式
```bash
# 启动API服务器
python run_api.py --port 8001

# 访问API文档
# http://localhost:8001/docs
```

#### 2. 交互式模式
```bash
# 启动交互式分析
python run_interactive.py
```

#### 3. 测试实时数据功能
```bash
# 运行实时数据演示
python examples/realtime_data_example.py

# 或直接测试API接口
curl http://localhost:8001/stocks/realtime/000001
```

#### 3. 命令行模式
```bash
# 分析单只股票
python analyze_stock.py 000001

# 生成价格预测报告
python generate_price_report.py 000001
```

## 📊 API接口

### 核心接口

#### 获取股票数据
```http
GET /api/v1/stock/{symbol}/data?days=30
```

#### 江恩轮中轮分析
```http
POST /api/v1/analysis/gann-wheel
Content-Type: application/json

{
  "symbol": "000001",
  "analysis_type": "time_price",
  "days": 30
}
```

#### 量价分析
```http
POST /api/v1/analysis/volume-price
Content-Type: application/json

{
  "symbol": "000001",
  "days": 30
}
```

#### 获取分析结果
```http
GET /api/v1/analysis/{symbol}/latest
```

#### 实时数据接口
```http
GET /api/v1/stocks/realtime/{symbol}
```

```http
GET /api/v1/stocks/realtime/{symbol}/tick
```

```http
GET /api/v1/stocks/realtime/{symbol}/depth
```

### 响应示例
```json
{
  "success": true,
  "data": {
    "symbol": "000001",
    "analysis_date": "2024-01-15T10:30:00Z",
    "gann_analysis": {
      "time_cycles": [7, 14, 21],
      "price_levels": [10.5, 11.2, 12.0],
      "trend_direction": "上升"
    },
    "volume_price_analysis": {
      "volume_trend": "放量",
      "price_volume_correlation": 0.85,
      "buy_sell_signals": [
        {
          "date": "2024-01-15",
          "signal": "买入",
          "confidence": 0.78
        }
      ]
    }
  }
}
```

## 🧪 测试

```bash
# 运行所有测试
python -m pytest tests/ -v

# 运行API测试
python -m pytest api/test_api.py -v

# 运行系统集成测试
python test_system.py
```

## 📁 项目结构

```
江恩轮中轮+量价分析/
├── api/                    # API相关文件
│   ├── server.py          # FastAPI服务器
│   ├── models.py          # API数据模型
│   ├── examples.py        # API使用示例
│   └── test_api.py        # API测试
├── src/                   # 核心源代码
│   ├── analysis/          # 分析模块
│   │   ├── gann/         # 江恩分析
│   │   └── volume_price/ # 量价分析
│   ├── data/             # 数据获取
│   ├── storage/          # 数据存储
│   └── utils/            # 工具函数
├── config/               # 配置文件
├── docs/                 # 文档
├── tests/                # 测试文件
├── logs/                 # 日志文件
└── data/                 # 数据文件
```

## 🔧 配置说明

主要配置项（`config/config.yaml`）：

```yaml
# 数据库配置
database:
  path: "data/stock_analysis.db"
  
# 日志配置
logging:
  level: "INFO"
  file: "logs/app.log"
  
# API配置
api:
  host: "0.0.0.0"
  port: 8000
  debug: false
  
# 分析参数
analysis:
  default_days: 30
  gann_cycles: [7, 14, 21, 30]
  volume_threshold: 1.5
```

## 📈 功能特性

### 江恩轮中轮分析
- 时间周期分析
- 价格水平计算
- 趋势方向判断
- 关键转折点预测

### 量价关系分析
- 成交量趋势分析
- 价量背离检测
- 买卖信号生成
- 资金流向分析

### 数据管理
- 自动数据更新
- 历史数据存储
- 分析结果缓存
- 数据质量检查

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 联系方式

- 项目链接: [https://github.com/Elohia/gann-wheel-stock-analysis](https://github.com/Elohia/gann-wheel-stock-analysis)
- 问题反馈: [Issues](https://github.com/Elohia/gann-wheel-stock-analysis/issues)

## 🙏 致谢

- [AKShare](https://github.com/akfamily/akshare) - 提供股票数据接口
- [FastAPI](https://fastapi.tiangolo.com/) - 现代化的API框架
- [江恩理论](https://en.wikipedia.org/wiki/William_Delbert_Gann) - 技术分析理论基础

---

⭐ 如果这个项目对你有帮助，请给它一个星标！