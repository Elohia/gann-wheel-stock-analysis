# 快速开始指南

本指南将帮助您快速上手江恩轮中轮+量价分析系统。

## 环境要求

- Python 3.8 或更高版本
- 操作系统：Windows、macOS 或 Linux
- 内存：建议 4GB 以上
- 硬盘空间：至少 1GB 可用空间

## 安装步骤

### 1. 克隆或下载项目

```bash
# 如果使用Git
git clone <repository-url>
cd 江恩轮中轮+量价分析

# 或直接下载并解压项目文件
```

### 2. 创建虚拟环境（推荐）

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. 安装依赖包

```bash
# 安装所有依赖
pip install -r requirements.txt

# 如果遇到ta-lib安装问题，请参考下面的解决方案
```

#### TA-Lib 安装问题解决

**Windows 用户：**
```bash
# 下载对应版本的whl文件
# 从 https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib 下载
pip install TA_Lib-0.4.25-cp39-cp39-win_amd64.whl
```

**macOS 用户：**
```bash
brew install ta-lib
pip install ta-lib
```

**Linux 用户：**
```bash
sudo apt-get install libta-lib-dev
pip install ta-lib
```

### 4. 配置系统

```bash
# 复制配置文件模板
cp config.example.yaml config/config.yaml

# 编辑配置文件
# 根据需要修改数据源API密钥、数据库设置等
```

## 配置说明

### 数据源配置

在 `config/config.yaml` 中配置数据源：

```yaml
data_sources:
  tushare:
    enabled: true
    token: "your_tushare_token"  # 在 https://tushare.pro 注册获取
  
  yfinance:
    enabled: true
  
  akshare:
    enabled: true
```

### 数据库配置

```yaml
database:
  type: "sqlite"  # 或 "mysql"
  sqlite:
    path: "data/stock_analysis.db"
  mysql:
    host: "localhost"
    port: 3306
    username: "your_username"
    password: "your_password"
    database: "stock_analysis"
```

## 第一次运行

### 1. 测试系统

```bash
# 运行系统测试
python test_system.py
```

### 2. 查看使用示例

```bash
# 运行使用示例
python example_usage.py
```

### 3. 使用命令行工具

```bash
# 获取股票数据
python main.py fetch --symbol 000001.SZ --period 2y

# 分析股票
python main.py analyze --symbol 000001.SZ --type all

# 批量分析
python main.py batch --symbols 000001.SZ,000002.SZ,600000.SH

# 更新所有数据
python main.py update
```

## 基本使用

### Python 脚本中使用

```python
from main import StockAnalysisSystem

# 初始化系统
system = StockAnalysisSystem("config/config.yaml")

# 获取股票数据
system.fetch_and_store_data("000001.SZ", "2y")

# 执行分析
result = system.analyze_stock("000001.SZ", "all")

# 查看结果
print(result)
```

### 分析结果说明

分析结果包含两个主要部分：

1. **江恩轮中轮分析** (`gann`)：
   - 时间周期分析
   - 价格轮回计算
   - 支撑阻力位
   - 趋势预测

2. **量价分析** (`volume_price`)：
   - 量价关系评估
   - 量价背离检测
   - 成交量模式识别
   - 交易信号生成

## 常见问题

### Q1: 无法获取股票数据

**解决方案：**
- 检查网络连接
- 确认API密钥配置正确
- 验证股票代码格式（如：000001.SZ, 600000.SH）

### Q2: 数据库连接失败

**解决方案：**
- 检查数据库配置
- 确保数据库服务正在运行
- 验证用户名和密码

### Q3: 分析结果为空

**解决方案：**
- 确保有足够的历史数据（建议至少100个交易日）
- 检查数据质量
- 查看日志文件了解详细错误信息

### Q4: 依赖包安装失败

**解决方案：**
- 升级pip：`pip install --upgrade pip`
- 使用国内镜像：`pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt`
- 单独安装问题包

## 进阶使用

### 自定义分析参数

在配置文件中调整分析参数：

```yaml
gann_analysis:
  time_cycles: [7, 14, 21, 30, 45, 60, 90, 120, 180, 360]
  price_squares: [144, 169, 225, 289, 361]
  angle_lines: ["1x1", "1x2", "2x1", "1x4", "4x1"]

volume_price_analysis:
  ma_periods: [5, 10, 20, 60]
  volume_threshold: 1.5
  divergence_periods: 20
```

### 批量处理

```python
# 批量分析多只股票
stocks = ["000001.SZ", "000002.SZ", "600000.SH"]
results = system.batch_analyze(stocks)
```

### 定时更新

```python
import schedule
import time

def update_data():
    system.update_all_data()

# 每天下午4点更新数据
schedule.every().day.at("16:00").do(update_data)

while True:
    schedule.run_pending()
    time.sleep(60)
```

## 获取帮助

- 查看详细文档：`docs/` 目录
- 运行示例代码：`example_usage.py`
- 查看日志文件：`logs/` 目录
- 检查配置文件：`config.example.yaml`

## 下一步

- 阅读 [API 文档](api_reference.md)
- 了解 [配置选项](configuration.md)
- 查看 [开发指南](development.md)
- 学习 [最佳实践](best_practices.md)