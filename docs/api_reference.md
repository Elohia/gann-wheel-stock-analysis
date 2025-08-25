# API 参考文档

本文档详细介绍了江恩轮中轮+量价分析系统的所有API接口。

## 目录

- [主系统类](#主系统类)
- [数据获取模块](#数据获取模块)
- [数据存储模块](#数据存储模块)
- [江恩分析模块](#江恩分析模块)
- [量价分析模块](#量价分析模块)
- [工具模块](#工具模块)

## 主系统类

### StockAnalysisSystem

主要的系统入口类，整合所有功能模块。

#### 初始化

```python
StockAnalysisSystem(config_path: str = "config/config.yaml")
```

**参数：**
- `config_path` (str): 配置文件路径

**示例：**
```python
system = StockAnalysisSystem("config/config.yaml")
```

#### 方法

##### fetch_and_store_data

```python
fetch_and_store_data(symbol: str, period: str = None) -> bool
```

获取并存储股票数据。

**参数：**
- `symbol` (str): 股票代码（如：000001.SZ）
- `period` (str, 可选): 数据周期（如：1y, 2y, 5y）

**返回：**
- `bool`: 操作是否成功

**示例：**
```python
success = system.fetch_and_store_data("000001.SZ", "2y")
```

##### analyze_stock

```python
analyze_stock(symbol: str, analysis_type: str = "all") -> dict
```

分析股票。

**参数：**
- `symbol` (str): 股票代码
- `analysis_type` (str): 分析类型（"gann", "volume_price", "all"）

**返回：**
- `dict`: 分析结果字典

**示例：**
```python
result = system.analyze_stock("000001.SZ", "all")
```

##### batch_analyze

```python
batch_analyze(symbols: list = None) -> dict
```

批量分析股票。

**参数：**
- `symbols` (list, 可选): 股票代码列表，默认使用配置文件中的列表

**返回：**
- `dict`: 批量分析结果

**示例：**
```python
results = system.batch_analyze(["000001.SZ", "000002.SZ"])
```

##### update_all_data

```python
update_all_data() -> None
```

更新所有股票数据。

**示例：**
```python
system.update_all_data()
```

## 数据获取模块

### DataFetcher

负责从多个数据源获取股票数据。

#### 初始化

```python
DataFetcher(config: dict)
```

**参数：**
- `config` (dict): 数据源配置字典

#### 方法

##### fetch_stock_data

```python
fetch_stock_data(symbol: str, period: str = "1y", source: str = None) -> pd.DataFrame
```

获取股票数据。

**参数：**
- `symbol` (str): 股票代码
- `period` (str): 数据周期
- `source` (str, 可选): 指定数据源

**返回：**
- `pd.DataFrame`: 股票数据

##### test_connections

```python
test_connections() -> dict
```

测试所有数据源连接。

**返回：**
- `dict`: 连接状态字典

##### get_stock_info

```python
get_stock_info(symbol: str) -> dict
```

获取股票基本信息。

**参数：**
- `symbol` (str): 股票代码

**返回：**
- `dict`: 股票信息字典

## 数据存储模块

### DatabaseManager

负责数据库操作和数据存储。

#### 初始化

```python
DatabaseManager(config: dict)
```

**参数：**
- `config` (dict): 数据库配置字典

#### 方法

##### save_stock_data

```python
save_stock_data(symbol: str, data: pd.DataFrame) -> bool
```

保存股票数据。

**参数：**
- `symbol` (str): 股票代码
- `data` (pd.DataFrame): 股票数据

**返回：**
- `bool`: 操作是否成功

##### get_stock_data

```python
get_stock_data(symbol: str, start_date: str = None, end_date: str = None) -> pd.DataFrame
```

获取股票数据。

**参数：**
- `symbol` (str): 股票代码
- `start_date` (str, 可选): 开始日期
- `end_date` (str, 可选): 结束日期

**返回：**
- `pd.DataFrame`: 股票数据

##### save_analysis_result

```python
save_analysis_result(symbol: str, analysis_type: str, result: dict) -> bool
```

保存分析结果。

**参数：**
- `symbol` (str): 股票代码
- `analysis_type` (str): 分析类型
- `result` (dict): 分析结果

**返回：**
- `bool`: 操作是否成功

##### get_analysis_result

```python
get_analysis_result(symbol: str, analysis_type: str = None) -> dict
```

获取分析结果。

**参数：**
- `symbol` (str): 股票代码
- `analysis_type` (str, 可选): 分析类型

**返回：**
- `dict`: 分析结果

##### get_database_stats

```python
get_database_stats() -> dict
```

获取数据库统计信息。

**返回：**
- `dict`: 统计信息字典

## 江恩分析模块

### GannWheel

实现江恩轮中轮分析算法。

#### 初始化

```python
GannWheel(config: dict = None)
```

**参数：**
- `config` (dict, 可选): 江恩分析配置

#### 方法

##### analyze

```python
analyze(data: pd.DataFrame) -> dict
```

执行江恩轮中轮分析。

**参数：**
- `data` (pd.DataFrame): 股票数据

**返回：**
- `dict`: 分析结果字典

**返回结果结构：**
```python
{
    "time_cycles": [...],           # 时间周期分析
    "price_cycles": [...],          # 价格轮回分析
    "gann_angles": [...],           # 江恩角度线
    "gann_square": {...},           # 江恩正方形
    "resonance_analysis": {...},    # 时间价格共振
    "support_resistance": {...},    # 支撑阻力位
    "prediction": {...}             # 预测分析
}
```

##### calculate_time_cycles

```python
calculate_time_cycles(data: pd.DataFrame) -> list
```

计算时间周期。

##### calculate_price_cycles

```python
calculate_price_cycles(data: pd.DataFrame) -> list
```

计算价格轮回。

##### calculate_gann_angles

```python
calculate_gann_angles(data: pd.DataFrame) -> dict
```

计算江恩角度线。

##### find_support_resistance

```python
find_support_resistance(data: pd.DataFrame) -> dict
```

寻找支撑阻力位。

## 量价分析模块

### VolumePriceAnalyzer

实现量价关系分析。

#### 初始化

```python
VolumePriceAnalyzer(config: dict = None)
```

**参数：**
- `config` (dict, 可选): 量价分析配置

#### 方法

##### analyze

```python
analyze(data: pd.DataFrame) -> dict
```

执行量价分析。

**参数：**
- `data` (pd.DataFrame): 股票数据

**返回：**
- `dict`: 分析结果字典

**返回结果结构：**
```python
{
    "volume_price_relation": {...},    # 量价关系分析
    "divergence_analysis": {...},      # 量价背离分析
    "volume_indicators": {...},        # 成交量指标
    "coordination_analysis": {...},     # 价量配合度分析
    "abnormal_volume": {...},          # 异常成交量识别
    "trend_analysis": {...},           # 量价趋势分析
    "comprehensive_rating": {...},     # 综合评级
    "trading_signals": [...]           # 交易信号
}
```

##### analyze_volume_price_relation

```python
analyze_volume_price_relation(data: pd.DataFrame) -> dict
```

分析量价关系。

##### detect_divergence

```python
detect_divergence(data: pd.DataFrame) -> dict
```

检测量价背离。

##### calculate_volume_indicators

```python
calculate_volume_indicators(data: pd.DataFrame) -> dict
```

计算成交量指标。

##### identify_abnormal_volume

```python
identify_abnormal_volume(data: pd.DataFrame) -> dict
```

识别异常成交量。

##### generate_trading_signals

```python
generate_trading_signals(data: pd.DataFrame) -> list
```

生成交易信号。

## 工具模块

### ConfigManager

配置管理器。

#### 初始化

```python
ConfigManager(config_path: str)
```

**参数：**
- `config_path` (str): 配置文件路径

#### 方法

##### get_config

```python
get_config(key: str = None) -> dict
```

获取配置。

**参数：**
- `key` (str, 可选): 配置键名

**返回：**
- `dict`: 配置字典

##### set_config

```python
set_config(key: str, value: any) -> None
```

设置配置。

**参数：**
- `key` (str): 配置键名
- `value` (any): 配置值

##### save_config

```python
save_config() -> None
```

保存配置到文件。

### 日志设置

#### setup_logger

```python
setup_logger(config: dict) -> None
```

设置日志系统。

**参数：**
- `config` (dict): 日志配置字典

#### get_logger

```python
get_logger(name: str = None) -> Logger
```

获取日志记录器。

**参数：**
- `name` (str, 可选): 日志记录器名称

**返回：**
- `Logger`: 日志记录器实例

## 数据结构

### 股票数据格式

股票数据使用pandas DataFrame格式，包含以下列：

```python
{
    'date': '日期',
    'open': '开盘价',
    'high': '最高价', 
    'low': '最低价',
    'close': '收盘价',
    'volume': '成交量',
    'amount': '成交额'  # 可选
}
```

### 分析结果格式

所有分析结果都以字典格式返回，包含以下通用字段：

```python
{
    'symbol': '股票代码',
    'analysis_date': '分析日期',
    'data_period': '数据周期',
    'analysis_type': '分析类型',
    'result': {...}  # 具体分析结果
}
```

## 错误处理

所有API方法都包含适当的错误处理：

- 数据获取失败时返回None或空DataFrame
- 分析失败时返回包含错误信息的字典
- 数据库操作失败时返回False
- 所有异常都会记录到日志文件

## 使用示例

### 完整分析流程

```python
from main import StockAnalysisSystem

# 初始化系统
system = StockAnalysisSystem()

# 获取数据
system.fetch_and_store_data("000001.SZ", "2y")

# 执行分析
result = system.analyze_stock("000001.SZ", "all")

# 处理结果
if result:
    gann_result = result.get('gann', {})
    vp_result = result.get('volume_price', {})
    
    # 获取关键信息
    support_levels = gann_result.get('support_resistance', {}).get('support', [])
    trading_signals = vp_result.get('trading_signals', [])
    
    print(f"支撑位: {support_levels}")
    print(f"交易信号: {len(trading_signals)} 个")
```

### 自定义分析

```python
from src.analysis.gann.gann_wheel import GannWheel
from src.analysis.volume_price.volume_price_analyzer import VolumePriceAnalyzer

# 自定义配置
gann_config = {
    'time_cycles': [7, 14, 21, 30],
    'price_squares': [144, 169, 225]
}

vp_config = {
    'ma_periods': [5, 10, 20],
    'volume_threshold': 2.0
}

# 创建分析器
gann_analyzer = GannWheel(gann_config)
vp_analyzer = VolumePriceAnalyzer(vp_config)

# 执行分析
gann_result = gann_analyzer.analyze(data)
vp_result = vp_analyzer.analyze(data)
```