#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FastAPI服务器

提供股票分析系统的RESTful API接口，支持江恩轮中轮分析和量价分析。

Author: AI Assistant
Date: 2024
"""

import os
import sys
import traceback
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import StockAnalysisSystem
from api.models import (
    # 请求模型
    StockDataRequest, AnalysisRequest, BatchAnalysisRequest,
    # 响应模型
    BaseResponse, ErrorResponse, StockDataResponse, AnalysisResponse, 
    BatchAnalysisResponse, SystemStatusResponse, StockListResponse,
    # 数据模型
    StockDataInfo, ComprehensiveAnalysisResult, GannAnalysisResult, 
    VolumePriceAnalysisResult, SystemStatus, StockInfo,
    # 枚举
    ResponseStatus, AnalysisType, DataPeriod
)


# 全局变量
analysis_system: Optional[StockAnalysisSystem] = None
app_start_time = datetime.now()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global analysis_system
    
    # 启动时初始化
    try:
        print("正在初始化股票分析系统...")
        analysis_system = StockAnalysisSystem()
        print("股票分析系统初始化完成")
    except Exception as e:
        print(f"初始化失败: {e}")
        raise
    
    yield
    
    # 关闭时清理
    print("正在关闭股票分析系统...")
    analysis_system = None
    print("股票分析系统已关闭")


# 创建FastAPI应用
app = FastAPI(
    title="股票分析API",
    description="基于江恩轮中轮理论和量价分析的股票分析系统API",
    version="1.0.0",
    lifespan=lifespan
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============ 异常处理 ============

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理器"""
    error_msg = str(exc)
    error_details = {
        "type": type(exc).__name__,
        "traceback": traceback.format_exc()
    }
    
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            message=f"服务器内部错误: {error_msg}",
            error_code="INTERNAL_ERROR",
            error_details=error_details
        ).dict()
    )


def get_analysis_system() -> StockAnalysisSystem:
    """获取分析系统实例"""
    if analysis_system is None:
        raise HTTPException(
            status_code=503,
            detail="分析系统未初始化或不可用"
        )
    return analysis_system


# ============ API路由 ============

@app.get("/", response_model=BaseResponse)
async def root():
    """根路径 - API信息"""
    return BaseResponse(
        status=ResponseStatus.SUCCESS,
        message="股票分析API服务正在运行"
    )


@app.get("/health", response_model=SystemStatusResponse)
async def health_check():
    """健康检查"""
    try:
        system = get_analysis_system()
        
        # 检查数据库连接
        db_status = "connected" if system.db_manager else "disconnected"
        
        # 检查数据源状态
        data_sources_status = {
            "yfinance": "available" if system.data_fetcher else "unavailable"
        }
        
        uptime = str(datetime.now() - app_start_time)
        
        system_info = SystemStatus(
            service_name="股票分析API",
            version="1.0.0",
            status="running",
            uptime=uptime,
            database_status=db_status,
            data_sources_status=data_sources_status
        )
        
        return SystemStatusResponse(
            message="系统运行正常",
            system_info=system_info
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"系统健康检查失败: {str(e)}"
        )


@app.get("/stocks", response_model=StockListResponse)
async def list_stocks(
    limit: int = Query(100, ge=1, le=1000, description="返回数量限制"),
    offset: int = Query(0, ge=0, description="偏移量")
):
    """获取股票列表"""
    try:
        system = get_analysis_system()
        
        # 从数据库获取股票列表
        # 这里需要根据实际的数据库结构来实现
        # 暂时返回示例数据
        stocks = [
            StockInfo(
                symbol="000001.SZ",
                name="平安银行",
                last_update=datetime.now(),
                data_count=1000
            ),
            StockInfo(
                symbol="600036.SH",
                name="招商银行",
                last_update=datetime.now(),
                data_count=1200
            )
        ]
        
        return StockListResponse(
            message="获取股票列表成功",
            stocks=stocks[offset:offset+limit],
            total_count=len(stocks)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取股票列表失败: {str(e)}"
        )


@app.post("/stocks/data", response_model=StockDataResponse)
async def fetch_stock_data(request: StockDataRequest):
    """获取股票数据"""
    try:
        system = get_analysis_system()
        
        # 获取股票数据
        success = system.fetch_and_store_data(
            symbol=request.symbol,
            period=request.period.value
        )
        
        if not success:
            raise HTTPException(
                status_code=400,
                detail=f"获取股票数据失败: {request.symbol}"
            )
        
        # 构造响应数据
        data_info = StockDataInfo(
            symbol=request.symbol,
            start_date=datetime.now(),  # 实际应该从数据库获取
            end_date=datetime.now(),
            total_records=0,  # 实际应该从数据库获取
            last_update=datetime.now()
        )
        
        return StockDataResponse(
            message=f"股票数据获取成功: {request.symbol}",
            data=data_info
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取股票数据时发生错误: {str(e)}"
        )


@app.post("/analysis/single", response_model=AnalysisResponse)
async def analyze_single_stock(request: AnalysisRequest):
    """单股票分析"""
    try:
        system = get_analysis_system()
        
        # 如果需要自动获取数据
        if request.auto_fetch:
            period = request.period.value if request.period else "1y"
            success = system.fetch_and_store_data(
                symbol=request.symbol,
                period=period
            )
            if not success:
                raise HTTPException(
                    status_code=400,
                    detail=f"无法获取股票数据: {request.symbol}"
                )
        
        # 执行分析
        analysis_result = system.analyze_stock(request.symbol)
        
        if not analysis_result:
            raise HTTPException(
                status_code=404,
                detail=f"未找到股票数据或分析失败: {request.symbol}"
            )
        
        # 转换分析结果
        result = convert_analysis_result(request.symbol, analysis_result, request.analysis_type)
        
        return AnalysisResponse(
            message=f"股票分析完成: {request.symbol}",
            result=result
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"分析股票时发生错误: {str(e)}"
        )


@app.post("/analysis/batch", response_model=BatchAnalysisResponse)
async def analyze_batch_stocks(request: BatchAnalysisRequest):
    """批量股票分析"""
    try:
        system = get_analysis_system()
        
        results = []
        failed_symbols = []
        
        for symbol in request.symbols:
            try:
                # 如果需要自动获取数据
                if request.auto_fetch:
                    period = request.period.value if request.period else "1y"
                    success = system.fetch_and_store_data(
                        symbol=symbol,
                        period=period,
                        force_update=False
                    )
                    if not success:
                        failed_symbols.append(symbol)
                        continue
                
                # 执行分析
                analysis_result = system.analyze_stock(symbol)
                
                if analysis_result:
                    result = convert_analysis_result(symbol, analysis_result, request.analysis_type)
                    results.append(result)
                else:
                    failed_symbols.append(symbol)
                    
            except Exception as e:
                print(f"分析股票 {symbol} 时出错: {e}")
                failed_symbols.append(symbol)
        
        return BatchAnalysisResponse(
            message=f"批量分析完成，成功: {len(results)}, 失败: {len(failed_symbols)}",
            results=results,
            success_count=len(results),
            failed_symbols=failed_symbols
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"批量分析时发生错误: {str(e)}"
        )


@app.get("/analysis/{symbol}", response_model=AnalysisResponse)
async def get_analysis_by_symbol(
    symbol: str = Path(..., description="股票代码"),
    analysis_type: AnalysisType = Query(AnalysisType.ALL, description="分析类型"),
    auto_fetch: bool = Query(True, description="是否自动获取数据"),
    period: Optional[DataPeriod] = Query(None, description="数据周期")
):
    """通过GET方法获取股票分析结果"""
    request = AnalysisRequest(
        symbol=symbol,
        analysis_type=analysis_type,
        auto_fetch=auto_fetch,
        period=period
    )
    return await analyze_single_stock(request)


# ============ 辅助函数 ============

def convert_analysis_result(
    symbol: str, 
    analysis_result: dict, 
    analysis_type: AnalysisType
) -> ComprehensiveAnalysisResult:
    """转换分析结果为API响应格式"""
    
    gann_result = None
    volume_price_result = None
    
    # 处理江恩分析结果
    if analysis_type in [AnalysisType.GANN, AnalysisType.ALL] and 'gann_analysis' in analysis_result:
        gann_data = analysis_result['gann_analysis']
        gann_result = GannAnalysisResult(
            symbol=symbol,
            analysis_date=datetime.now(),
            current_price=gann_data.get('current_price', 0.0),
            predictions=gann_data.get('predictions', []),
            overall_trend=gann_data.get('overall_trend', 'unknown'),
            trend_strength=gann_data.get('trend_strength', 0.0)
        )
    
    # 处理量价分析结果
    if analysis_type in [AnalysisType.VOLUME_PRICE, AnalysisType.ALL] and 'volume_price_analysis' in analysis_result:
        vp_data = analysis_result['volume_price_analysis']
        volume_price_result = VolumePriceAnalysisResult(
            symbol=symbol,
            analysis_date=datetime.now(),
            current_price=vp_data.get('current_price', 0.0),
            current_volume=vp_data.get('current_volume', 0.0),
            price_strength=vp_data.get('price_strength', 0.0),
            volume_strength=vp_data.get('volume_strength', 0.0),
            combined_strength=vp_data.get('combined_strength', 0.0),
            strength_level=vp_data.get('strength_level', 'unknown'),
            price_trend=vp_data.get('price_trend', 'unknown'),
            volume_trend=vp_data.get('volume_trend', 'unknown'),
            overall_trend=vp_data.get('overall_trend', 'unknown'),
            target_prices=vp_data.get('target_prices', [])
        )
    
    return ComprehensiveAnalysisResult(
        symbol=symbol,
        analysis_date=datetime.now(),
        data_range=analysis_result.get('data_range', {}),
        gann_analysis=gann_result,
        volume_price_analysis=volume_price_result
    )


if __name__ == "__main__":
    import uvicorn
    
    print("启动股票分析API服务器...")
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )