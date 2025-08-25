# 股票分析系统 API 文档

基于江恩轮中轮理论和量价分析的股票分析系统RESTful API接口。

## 目录

- [快速开始](#快速开始)
- [API概览](#api概览)
- [接口详情](#接口详情)
- [数据模型](#数据模型)
- [使用示例](#使用示例)
- [错误处理](#错误处理)
- [性能优化](#性能优化)

## 快速开始

### 1. 安装依赖

```bash
pip install fastapi uvicorn pydantic requests
```

### 2. 启动API服务器

```bash
# 基础启动
python run_api.py

# 开发模式（自动重载）
python run_api.py --reload

# 自定义端口
python run_api.py --port 8080

# 查看所有选项
python run_api.py --help
```

### 3. 访问API文档

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **健康检查**: http://localhost:8000/health

## API概览

### 基础信息

- **基础URL**: `http://localhost:8000`
- **内容类型**: `application/json`
- **字符编码**: `UTF-8`
- **API版本**: `1.0.0`

### 主要端点

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/` | API根路径信息 |
| GET | `/health` | 系统健康检查 |
| GET | `/stocks` | 获取股票列表 |
| POST | `/stocks/data` | 获取股票数据 |
| POST | `/analysis/single` | 单股票分析 |
| POST | `/analysis/batch` | 批量股票分析 |
| GET | `/analysis/{symbol}` | 通过GET获取分析结果 |

## 接口详情

### 1. 系统状态

#### GET `/health`

获取系统健康状态和运行信息。

**响应示例**:
```json
{
  "status": "success",
  "message": "系统运行正常",
  "timestamp": "2024-01-15T10:30:00",
  "system_info": {
    "service_name": "股票分析API",
    "version": "1.0.0",
    "status": "running",
    "uptime": "2:30:45",
    "database_status": "connected",
    "data_sources_status": {
      "yfinance": "available"
    }
  }
}
```

### 2. 股票列表

#### GET `/stocks`

获取系统中的股票列表。

**查询参数**:
- `limit` (int): 返回数量限制，默认100，最大1000
- `offset` (int): 偏移量，默认0

**响应示例**:
```json
{
  "status": "success",
  "message": "获取股票列表成功",
  "timestamp": "2024-01-15T10:30:00",
  "stocks": [
    {
      "symbol": "000001.SZ",
      "name": "平安银行",
      "last_update": "2024-01-15T09:00:00",
      "data_count": 1000
    }
  ],
  "total_count": 2
}
```

### 3. 股票数据获取

#### POST `/stocks/data`

获取指定股票的历史数据。

**请求体**:
```json
{
  "symbol": "000001.SZ",
  "period": "1y",
  "force_update": false
}
```

**参数说明**:
- `symbol` (string): 股票代码，如"000001.SZ"
- `period` (string): 数据周期，可选值："1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y"
- `force_update` (boolean): 是否强制更新数据

**响应示例**:
```json
{
  "status": "success",
  "message": "股票数据获取成功: 000001.SZ",
  "timestamp": "2024-01-15T10:30:00",
  "data": {
    "symbol": "000001.SZ",
    "start_date": "2023-01-15T00:00:00",
    "end_date": "2024-01-15T00:00:00",
    "total_records": 250,
    "last_update": "2024-01-15T10:30:00"
  }
}
```

### 4. 单股票分析

#### POST `/analysis/single`

对单个股票进行分析。

**请求体**:
```json
{
  "symbol": "000001.SZ",
  "analysis_type": "all",
  "auto_fetch": true,
  "period": "1y"
}
```

**参数说明**:
- `symbol` (string): 股票代码
- `analysis_type` (string): 分析类型，可选值："gann", "volume_price", "all"
- `auto_fetch` (boolean): 如果数据不存在是否自动获取
- `period` (string, 可选): 数据周期（仅在auto_fetch=true时有效）

**响应示例**:
```json
{
  "status": "success",
  "message": "股票分析完成: 000001.SZ",
  "timestamp": "2024-01-15T10:30:00",
  "result": {
    "symbol": "000001.SZ",
    "analysis_date": "2024-01-15T10:30:00",
    "data_range": {
      "start_date": "2023-01-15",
      "end_date": "2024-01-15",
      "total_days": 365
    },
    "gann_analysis": {
      "symbol": "000001.SZ",
      "analysis_date": "2024-01-15T10:30:00",
      "current_price": 12.50,
      "predictions": [
        {
          "direction": "up",
          "target_price": 13.20,
          "confidence": 0.75,
          "time_frame": "short_term",
          "prediction_type": "price_target"
        }
      ],
      "overall_trend": "bullish",
      "trend_strength": 0.68
    },
    "volume_price_analysis": {
      "symbol": "000001.SZ",
      "analysis_date": "2024-01-15T10:30:00",
      "current_price": 12.50,
      "current_volume": 1500000,
      "price_strength": 0.72,
      "volume_strength": 0.65,
      "combined_strength": 0.69,
      "strength_level": "medium",
      "price_trend": "up",
      "volume_trend": "increasing",
      "overall_trend": "bullish",
      "target_prices": [13.00, 13.50]
    }
  }
}
```

### 5. 批量分析

#### POST `/analysis/batch`

对多个股票进行批量分析。

**请求体**:
```json
{
  "symbols": ["000001.SZ", "600036.SH"],
  "analysis_type": "all",
  "auto_fetch": true,
  "period": "1y"
}
```

**响应示例**:
```json
{
  "status": "success",
  "message": "批量分析完成，成功: 2, 失败: 0",
  "timestamp": "2024-01-15T10:30:00",
  "results": [
    {
      "symbol": "000001.SZ",
      "analysis_date": "2024-01-15T10:30:00",
      "gann_analysis": { /* ... */ },
      "volume_price_analysis": { /* ... */ }
    }
  ],
  "success_count": 2,
  "failed_symbols": []
}
```

### 6. GET方式分析

#### GET `/analysis/{symbol}`

通过GET方法获取股票分析结果。

**路径参数**:
- `symbol` (string): 股票代码

**查询参数**:
- `analysis_type` (string): 分析类型，默认"all"
- `auto_fetch` (boolean): 是否自动获取数据，默认true
- `period` (string): 数据周期

**示例**:
```
GET /analysis/000001.SZ?analysis_type=all&auto_fetch=true&period=1y
```

## 数据模型

### 分析类型 (AnalysisType)

- `gann`: 仅江恩轮中轮分析
- `volume_price`: 仅量价分析
- `all`: 全部分析

### 数据周期 (DataPeriod)

- `1d`: 1天
- `5d`: 5天
- `1mo`: 1个月
- `3mo`: 3个月
- `6mo`: 6个月
- `1y`: 1年
- `2y`: 2年
- `5y`: 5年

### 响应状态 (ResponseStatus)

- `success`: 成功
- `error`: 错误
- `warning`: 警告

## 使用示例

### Python客户端示例

```python
import requests

# 创建会话
session = requests.Session()
session.headers.update({
    'Content-Type': 'application/json',
    'Accept': 'application/json'
})

base_url = "http://localhost:8000"

# 1. 健康检查
response = session.get(f"{base_url}/health")
print(f"系统状态: {response.json()['system_info']['status']}")

# 2. 获取股票数据
data = {
    "symbol": "000001.SZ",
    "period": "1y",
    "force_update": False
}
response = session.post(f"{base_url}/stocks/data", json=data)
print(f"数据获取: {response.json()['message']}")

# 3. 分析股票
data = {
    "symbol": "000001.SZ",
    "analysis_type": "all",
    "auto_fetch": True
}
response = session.post(f"{base_url}/analysis/single", json=data)
result = response.json()

if result['result']:
    analysis = result['result']
    print(f"股票: {analysis['symbol']}")
    
    if analysis.get('gann_analysis'):
        gann = analysis['gann_analysis']
        print(f"江恩趋势: {gann['overall_trend']} (强度: {gann['trend_strength']:.2f})")
    
    if analysis.get('volume_price_analysis'):
        vp = analysis['volume_price_analysis']
        print(f"量价趋势: {vp['overall_trend']} (强度: {vp['combined_strength']:.2f})")
```

### JavaScript/Node.js示例

```javascript
const axios = require('axios');

const baseURL = 'http://localhost:8000';
const client = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
});

// 分析股票
async function analyzeStock(symbol) {
  try {
    const response = await client.post('/analysis/single', {
      symbol: symbol,
      analysis_type: 'all',
      auto_fetch: true
    });
    
    const result = response.data.result;
    if (result) {
      console.log(`股票: ${result.symbol}`);
      
      if (result.gann_analysis) {
        const gann = result.gann_analysis;
        console.log(`江恩趋势: ${gann.overall_trend} (强度: ${gann.trend_strength.toFixed(2)})`);
      }
      
      if (result.volume_price_analysis) {
        const vp = result.volume_price_analysis;
        console.log(`量价趋势: ${vp.overall_trend} (强度: ${vp.combined_strength.toFixed(2)})`);
      }
    }
  } catch (error) {
    console.error('分析失败:', error.response?.data?.message || error.message);
  }
}

analyzeStock('000001.SZ');
```

### cURL示例

```bash
# 健康检查
curl -X GET "http://localhost:8000/health"

# 获取股票数据
curl -X POST "http://localhost:8000/stocks/data" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "000001.SZ",
    "period": "1y",
    "force_update": false
  }'

# 分析股票
curl -X POST "http://localhost:8000/analysis/single" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "000001.SZ",
    "analysis_type": "all",
    "auto_fetch": true
  }'

# GET方式分析
curl -X GET "http://localhost:8000/analysis/000001.SZ?analysis_type=all&auto_fetch=true"
```

## 错误处理

### 错误响应格式

```json
{
  "status": "error",
  "message": "错误描述",
  "timestamp": "2024-01-15T10:30:00",
  "error_code": "ERROR_CODE",
  "error_details": {
    "type": "ValueError",
    "traceback": "..."
  }
}
```

### 常见错误码

| HTTP状态码 | 错误类型 | 描述 |
|------------|----------|------|
| 400 | Bad Request | 请求参数错误 |
| 404 | Not Found | 资源不存在 |
| 422 | Validation Error | 数据验证失败 |
| 500 | Internal Server Error | 服务器内部错误 |
| 503 | Service Unavailable | 服务不可用 |

### 错误处理最佳实践

```python
import requests
from requests.exceptions import RequestException, HTTPError, ConnectionError, Timeout

def safe_api_call(url, method='GET', **kwargs):
    try:
        response = requests.request(method, url, timeout=30, **kwargs)
        response.raise_for_status()
        return response.json()
    
    except ConnectionError:
        print("无法连接到API服务器，请检查服务器是否运行")
    except Timeout:
        print("请求超时，请稍后重试")
    except HTTPError as e:
        if e.response.status_code == 422:
            print(f"数据验证错误: {e.response.json()}")
        elif e.response.status_code == 500:
            print(f"服务器错误: {e.response.json().get('message', '未知错误')}")
        else:
            print(f"HTTP错误 {e.response.status_code}: {e.response.text}")
    except RequestException as e:
        print(f"请求异常: {e}")
    
    return None
```

## 性能优化

### 1. 缓存策略

- 股票数据会被缓存在本地数据库中
- 分析结果可以通过设置`force_update=false`来使用缓存
- 建议在生产环境中实现Redis缓存

### 2. 批量处理

- 使用`/analysis/batch`端点进行批量分析
- 批量请求比多个单独请求更高效
- 建议每批处理不超过50个股票

### 3. 并发限制

- API服务器默认使用单个工作进程
- 生产环境建议使用多个worker：`python run_api.py --workers 4`
- 客户端应实现适当的并发控制

### 4. 监控和日志

- 使用`/health`端点进行健康监控
- 服务器日志包含详细的请求和错误信息
- 建议实现应用性能监控(APM)

## 部署建议

### 开发环境

```bash
# 启动开发服务器
python run_api.py --reload --log-level debug
```

### 生产环境

```bash
# 使用Gunicorn部署
pip install gunicorn
gunicorn api.server:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# 或使用uvicorn
uvicorn api.server:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker部署

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "api.server:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 测试

### 运行测试

```bash
# 启动API服务器
python run_api.py &

# 运行测试
python api/test_api.py

# 运行示例
python api/examples.py
```

### 测试覆盖

- 功能测试：所有API端点
- 错误处理：各种错误情况
- 性能测试：响应时间和并发
- 数据验证：输入参数验证

## 支持和反馈

如有问题或建议，请通过以下方式联系：

- 查看API文档：http://localhost:8000/docs
- 运行测试用例：`python api/test_api.py`
- 查看使用示例：`python api/examples.py`

---

**版本**: 1.0.0  
**更新日期**: 2024-01-15  
**作者**: AI Assistant