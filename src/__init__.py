# -*- coding: utf-8 -*-
"""
江恩轮中轮+量价分析系统

一个集成股票数据获取、存储和技术分析的综合系统。

主要功能：
- 多数据源股票数据获取（Tushare、yfinance、AKShare）
- 数据存储管理（SQLite/MySQL）
- 江恩轮中轮分析
- 量价关系分析
- 配置管理和日志记录
"""

__version__ = '1.0.0'
__author__ = 'Stock Analysis System'

# 导入主要模块
from .data import DataFetcher
from .storage import DatabaseManager, StockData, AnalysisResult
from .analysis import GannWheel, VolumePriceAnalyzer
from .utils import ConfigManager, setup_logger, get_logger

__all__ = [
    'DataFetcher',
    'DatabaseManager', 'StockData', 'AnalysisResult',
    'GannWheel', 'VolumePriceAnalyzer',
    'ConfigManager', 'setup_logger', 'get_logger'
]