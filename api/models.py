#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API数据模型定义

定义所有API接口的请求和响应数据模型，确保接口的标准化和类型安全。

Author: AI Assistant
Date: 2024
"""

from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class AnalysisType(str, Enum):
    """分析类型枚举"""
    GANN = "gann"
    VOLUME_PRICE = "volume_price"
    ALL = "all"


class DataPeriod(str, Enum):
    """数据周期枚举"""
    ONE_DAY = "1d"
    FIVE_DAYS = "5d"
    ONE_MONTH = "1mo"
    THREE_MONTHS = "3mo"
    SIX_MONTHS = "6mo"
    ONE_YEAR = "1y"
    TWO_YEARS = "2y"
    FIVE_YEARS = "5y"


class ResponseStatus(str, Enum):
    """响应状态枚举"""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"


# ============ 基础响应模型 ============

class BaseResponse(BaseModel):
    """基础响应模型"""
    status: ResponseStatus = Field(..., description="响应状态")
    message: str = Field(..., description="响应消息")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间戳")


class ErrorResponse(BaseResponse):
    """错误响应模型"""
    status: ResponseStatus = ResponseStatus.ERROR
    error_code: Optional[str] = Field(None, description="错误代码")
    error_details: Optional[Dict[str, Any]] = Field(None, description="错误详情")


# ============ 股票数据相关模型 ============

class StockDataRequest(BaseModel):
    """股票数据获取请求"""
    symbol: str = Field(..., description="股票代码")
    period: DataPeriod = Field(DataPeriod.ONE_YEAR, description="数据周期")


class StockDataInfo(BaseModel):
    """股票数据信息"""
    symbol: str = Field(..., description="股票代码")
    start_date: datetime = Field(..., description="数据开始日期")
    end_date: datetime = Field(..., description="数据结束日期")
    total_records: int = Field(..., description="数据记录总数")
    last_update: datetime = Field(..., description="最后更新时间")


class StockDataResponse(BaseResponse):
    """股票数据响应"""
    status: ResponseStatus = ResponseStatus.SUCCESS
    data: Optional[StockDataInfo] = Field(None, description="股票数据信息")


# ============ 分析请求模型 ============

class AnalysisRequest(BaseModel):
    """股票分析请求"""
    symbol: str = Field(..., description="股票代码", example="000001.SZ")
    analysis_type: AnalysisType = Field(AnalysisType.ALL, description="分析类型")
    auto_fetch: bool = Field(True, description="如果数据不存在是否自动获取")
    period: Optional[DataPeriod] = Field(None, description="数据周期（仅在auto_fetch=True时有效）")


class BatchAnalysisRequest(BaseModel):
    """批量分析请求"""
    symbols: List[str] = Field(..., description="股票代码列表", example=["000001.SZ", "600036.SH"])
    analysis_type: AnalysisType = Field(AnalysisType.ALL, description="分析类型")
    auto_fetch: bool = Field(True, description="如果数据不存在是否自动获取")
    period: Optional[DataPeriod] = Field(None, description="数据周期（仅在auto_fetch=True时有效）")


# ============ 江恩分析结果模型 ============

class TimeCycle(BaseModel):
    """时间周期"""
    cycle_days: int = Field(..., description="周期天数")
    strength: float = Field(..., description="周期强度")
    next_date: Optional[datetime] = Field(None, description="下一个周期日期")


class PriceLevel(BaseModel):
    """价格位"""
    price: float = Field(..., description="价格")
    level_type: str = Field(..., description="位置类型", example="support")
    strength: float = Field(..., description="强度")
    distance_percent: float = Field(..., description="与当前价格的距离百分比")


class GannPrediction(BaseModel):
    """江恩预测"""
    direction: str = Field(..., description="预测方向", example="up")
    target_price: float = Field(..., description="目标价格")
    confidence: float = Field(..., description="置信度")
    time_frame: str = Field(..., description="时间框架")
    prediction_type: str = Field(..., description="预测类型")


class GannAnalysisResult(BaseModel):
    """江恩分析结果"""
    symbol: str = Field(..., description="股票代码")
    analysis_date: datetime = Field(..., description="分析日期")
    current_price: float = Field(..., description="当前价格")
    
    # 时间分析
    dominant_cycle: Optional[TimeCycle] = Field(None, description="主导时间周期")
    time_cycles: List[TimeCycle] = Field(default_factory=list, description="时间周期列表")
    
    # 价格分析
    support_levels: List[PriceLevel] = Field(default_factory=list, description="支撑位列表")
    resistance_levels: List[PriceLevel] = Field(default_factory=list, description="阻力位列表")
    
    # 预测
    predictions: List[GannPrediction] = Field(default_factory=list, description="预测列表")
    overall_trend: str = Field(..., description="整体趋势")
    trend_strength: float = Field(..., description="趋势强度")


# ============ 量价分析结果模型 ============

class VolumeSignal(BaseModel):
    """成交量信号"""
    signal_type: str = Field(..., description="信号类型")
    strength: float = Field(..., description="信号强度")
    description: str = Field(..., description="信号描述")
    date: datetime = Field(..., description="信号日期")


class VolumePriceAnalysisResult(BaseModel):
    """量价分析结果"""
    symbol: str = Field(..., description="股票代码")
    analysis_date: datetime = Field(..., description="分析日期")
    current_price: float = Field(..., description="当前价格")
    current_volume: float = Field(..., description="当前成交量")
    
    # 量价关系
    price_strength: float = Field(..., description="价格强度")
    volume_strength: float = Field(..., description="成交量强度")
    combined_strength: float = Field(..., description="综合强度")
    strength_level: str = Field(..., description="强度等级")
    
    # 趋势分析
    price_trend: str = Field(..., description="价格趋势")
    volume_trend: str = Field(..., description="成交量趋势")
    overall_trend: str = Field(..., description="整体趋势")
    
    # 信号
    volume_signals: List[VolumeSignal] = Field(default_factory=list, description="成交量信号列表")
    
    # 预测目标
    target_prices: List[float] = Field(default_factory=list, description="目标价格列表")


# ============ 综合分析结果模型 ============

class ComprehensiveAnalysisResult(BaseModel):
    """综合分析结果"""
    symbol: str = Field(..., description="股票代码")
    analysis_date: datetime = Field(..., description="分析日期")
    data_range: Dict[str, Any] = Field(..., description="数据范围信息")
    
    gann_analysis: Optional[GannAnalysisResult] = Field(None, description="江恩分析结果")
    volume_price_analysis: Optional[VolumePriceAnalysisResult] = Field(None, description="量价分析结果")


class AnalysisResponse(BaseResponse):
    """分析响应"""
    status: ResponseStatus = ResponseStatus.SUCCESS
    result: Optional[ComprehensiveAnalysisResult] = Field(None, description="分析结果")


class BatchAnalysisResponse(BaseResponse):
    """批量分析响应"""
    status: ResponseStatus = ResponseStatus.SUCCESS
    results: List[ComprehensiveAnalysisResult] = Field(default_factory=list, description="分析结果列表")
    success_count: int = Field(..., description="成功分析数量")
    failed_symbols: List[str] = Field(default_factory=list, description="分析失败的股票代码")


# ============ 系统状态模型 ============

class SystemStatus(BaseModel):
    """系统状态"""
    service_name: str = Field(..., description="服务名称")
    version: str = Field(..., description="版本号")
    status: str = Field(..., description="运行状态")
    uptime: str = Field(..., description="运行时间")
    database_status: str = Field(..., description="数据库状态")
    data_sources_status: Dict[str, str] = Field(..., description="数据源状态")


class SystemStatusResponse(BaseResponse):
    """系统状态响应"""
    status: ResponseStatus = ResponseStatus.SUCCESS
    system_info: SystemStatus = Field(..., description="系统信息")


# ============ 股票列表模型 ============

class StockInfo(BaseModel):
    """股票信息"""
    symbol: str = Field(..., description="股票代码")
    name: Optional[str] = Field(None, description="股票名称")
    last_update: Optional[datetime] = Field(None, description="最后更新时间")
    data_count: Optional[int] = Field(None, description="数据记录数")


class StockListResponse(BaseResponse):
    """股票列表响应"""
    status: ResponseStatus = ResponseStatus.SUCCESS
    stocks: List[StockInfo] = Field(default_factory=list, description="股票列表")
    total_count: int = Field(..., description="总数量")