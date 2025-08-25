#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票数据获取模块

支持多数据源的股票数据获取，包括Tushare、yfinance和AKShare。
提供统一的数据接口和自动重试机制。

Author: AI Assistant
Date: 2024
"""

import time
import pandas as pd
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from loguru import logger

try:
    import tushare as ts
except ImportError:
    ts = None
    logger.warning("Tushare未安装，相关功能将不可用")

try:
    import yfinance as yf
except ImportError:
    yf = None
    logger.warning("yfinance未安装，相关功能将不可用")

try:
    import akshare as ak
except ImportError:
    ak = None
    logger.warning("AKShare未安装，相关功能将不可用")


class DataFetcher:
    """
    股票数据获取器
    
    支持多数据源，提供统一的数据获取接口
    """
    
    def __init__(self, data_sources_config: Dict[str, Any]):
        """
        初始化数据获取器
        
        Args:
            data_sources_config: 数据源配置
        """
        self.config = data_sources_config
        self.max_retries = 3
        self.retry_delay = 1  # 秒
        
        # 初始化各数据源
        self._init_tushare()
        self._init_yfinance()
        self._init_akshare()
        
        logger.info("数据获取器初始化完成")
    
    def _init_tushare(self) -> None:
        """
        初始化Tushare
        """
        tushare_config = self.config.get('tushare', {})
        if tushare_config.get('enabled', False) and ts is not None:
            token = tushare_config.get('token')
            if token and token != 'your_tushare_token_here':
                ts.set_token(token)
                self.tushare_pro = ts.pro_api()
                logger.info("Tushare初始化成功")
            else:
                logger.warning("Tushare token未配置或无效")
                self.tushare_pro = None
        else:
            self.tushare_pro = None
    
    def _init_yfinance(self) -> None:
        """
        初始化yfinance
        """
        yfinance_config = self.config.get('yfinance', {})
        if yfinance_config.get('enabled', False) and yf is not None:
            self.yfinance_timeout = yfinance_config.get('timeout', 30)
            logger.info("yfinance初始化成功")
        else:
            self.yfinance_timeout = None
    
    def _init_akshare(self) -> None:
        """
        初始化AKShare
        """
        akshare_config = self.config.get('akshare', {})
        if akshare_config.get('enabled', False) and ak is not None:
            logger.info("AKShare初始化成功")
        else:
            logger.info("AKShare未启用或未安装")
    
    def fetch_stock_data(self, symbol: str, period: str = '2y', 
                        source: str = 'auto') -> Optional[pd.DataFrame]:
        """
        获取股票数据
        
        Args:
            symbol: 股票代码
            period: 数据周期 ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max')
            source: 数据源 ('auto', 'tushare', 'yfinance', 'akshare')
            
        Returns:
            股票数据DataFrame，包含OHLCV等信息
        """
        logger.info(f"获取股票数据: {symbol}, 周期: {period}, 数据源: {source}")
        
        # 标准化股票代码
        normalized_symbol = self._normalize_symbol(symbol)
        
        # 确定数据源优先级
        sources = self._get_source_priority(source)
        
        for src in sources:
            try:
                data = self._fetch_from_source(normalized_symbol, period, src)
                if data is not None and not data.empty:
                    # 标准化数据格式
                    data = self._standardize_data(data, symbol)
                    logger.info(f"从 {src} 成功获取 {symbol} 数据，共 {len(data)} 条记录")
                    return data
                else:
                    logger.warning(f"从 {src} 获取 {symbol} 数据为空")
            except Exception as e:
                logger.warning(f"从 {src} 获取 {symbol} 数据失败: {str(e)}")
                continue
        
        logger.error(f"所有数据源都无法获取 {symbol} 的数据")
        return None
    
    def _normalize_symbol(self, symbol: str) -> str:
        """
        标准化股票代码格式
        
        Args:
            symbol: 原始股票代码
            
        Returns:
            标准化后的股票代码
        """
        # 移除空格并转换为大写
        symbol = symbol.strip().upper()
        
        # 如果是6位数字，自动添加交易所后缀
        if symbol.isdigit() and len(symbol) == 6:
            if symbol.startswith(('000', '001', '002', '003', '300')):
                symbol += '.SZ'  # 深交所
            elif symbol.startswith(('600', '601', '603', '605', '688')):
                symbol += '.SH'  # 上交所
        
        return symbol
    
    def _get_source_priority(self, source: str) -> List[str]:
        """
        获取数据源优先级列表
        
        Args:
            source: 指定的数据源
            
        Returns:
            数据源优先级列表
        """
        if source != 'auto':
            return [source]
        
        # 自动模式下根据配置优先级排序
        available_sources = []
        
        # 检查akshare可用性和配置
        akshare_config = self.config.get('akshare', {})
        if ak is not None and akshare_config.get('enabled', False):
            priority = akshare_config.get('priority', 1)
            available_sources.append(('akshare', priority))
        
        # 检查tushare可用性和配置
        tushare_config = self.config.get('tushare', {})
        if self.tushare_pro is not None and tushare_config.get('enabled', False):
            priority = tushare_config.get('priority', 2)
            available_sources.append(('tushare', priority))
        
        # 检查yfinance可用性和配置
        yfinance_config = self.config.get('yfinance', {})
        if self.yfinance_timeout is not None and yfinance_config.get('enabled', False):
            priority = yfinance_config.get('priority', 3)
            available_sources.append(('yfinance', priority))
        
        # 按优先级排序（数字越小优先级越高）
        available_sources.sort(key=lambda x: x[1])
        
        return [source[0] for source in available_sources]
    
    def _fetch_from_source(self, symbol: str, period: str, source: str) -> Optional[pd.DataFrame]:
        """
        从指定数据源获取数据
        
        Args:
            symbol: 股票代码
            period: 数据周期
            source: 数据源
            
        Returns:
            股票数据DataFrame
        """
        for attempt in range(self.max_retries):
            try:
                if source == 'tushare':
                    return self._fetch_from_tushare(symbol, period)
                elif source == 'yfinance':
                    return self._fetch_from_yfinance(symbol, period)
                elif source == 'akshare':
                    return self._fetch_from_akshare(symbol, period)
                else:
                    logger.error(f"不支持的数据源: {source}")
                    return None
            except Exception as e:
                logger.warning(f"第 {attempt + 1} 次尝试从 {source} 获取数据失败: {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                else:
                    raise
        
        return None
    
    def _fetch_from_tushare(self, symbol: str, period: str) -> Optional[pd.DataFrame]:
        """
        从Tushare获取数据
        
        Args:
            symbol: 股票代码
            period: 数据周期
            
        Returns:
            股票数据DataFrame
        """
        if self.tushare_pro is None:
            raise Exception("Tushare未初始化")
        
        # 转换周期为日期范围
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = self._period_to_start_date(period).strftime('%Y%m%d')
        
        # 转换股票代码格式（Tushare格式）
        ts_symbol = symbol.replace('.SH', '.SH').replace('.SZ', '.SZ')
        
        # 获取日线数据
        df = self.tushare_pro.daily(
            ts_code=ts_symbol,
            start_date=start_date,
            end_date=end_date
        )
        
        if df.empty:
            return None
        
        # 转换列名和格式
        df = df.rename(columns={
            'trade_date': 'Date',
            'open': 'Open',
            'high': 'High',
            'low': 'Low',
            'close': 'Close',
            'vol': 'Volume'
        })
        
        # 转换日期格式
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.set_index('Date').sort_index()
        
        # 选择需要的列
        columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        df = df[columns]
        
        return df
    
    def _fetch_from_yfinance(self, symbol: str, period: str) -> Optional[pd.DataFrame]:
        """
        从yfinance获取数据
        
        Args:
            symbol: 股票代码
            period: 数据周期
            
        Returns:
            股票数据DataFrame
        """
        if yf is None:
            raise Exception("yfinance未安装")
        
        # 转换股票代码格式（yfinance格式）
        if '.SH' in symbol:
            yf_symbol = symbol.replace('.SH', '.SS')
        elif '.SZ' in symbol:
            yf_symbol = symbol.replace('.SZ', '.SZ')
        else:
            yf_symbol = symbol
        
        # 创建股票对象
        ticker = yf.Ticker(yf_symbol)
        
        # 获取历史数据
        df = ticker.history(period=period, timeout=self.yfinance_timeout)
        
        if df.empty:
            return None
        
        # 重命名列
        df.columns = ['Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits']
        
        # 选择需要的列
        columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        df = df[columns]
        
        return df
    
    def _fetch_from_akshare(self, symbol: str, period: str) -> Optional[pd.DataFrame]:
        """
        从AKShare获取数据
        
        Args:
            symbol: 股票代码
            period: 数据周期
            
        Returns:
            股票数据DataFrame
        """
        if ak is None:
            raise Exception("AKShare未安装")
        
        # 转换股票代码格式（AKShare格式）
        ak_symbol = symbol.replace('.SH', '').replace('.SZ', '')
        
        # 计算日期范围
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = self._period_to_start_date(period).strftime('%Y%m%d')
        
        # 获取股票历史数据
        df = ak.stock_zh_a_hist(
            symbol=ak_symbol,
            period="daily",
            start_date=start_date,
            end_date=end_date,
            adjust="qfq"  # 前复权
        )
        
        if df.empty:
            return None
        
        # 重命名列
        df = df.rename(columns={
            '日期': 'Date',
            '开盘': 'Open',
            '最高': 'High',
            '最低': 'Low',
            '收盘': 'Close',
            '成交量': 'Volume'
        })
        
        # 转换日期格式
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.set_index('Date').sort_index()
        
        # 选择需要的列
        columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        df = df[columns]
        
        return df
    
    def _period_to_start_date(self, period: str) -> datetime:
        """
        将周期字符串转换为开始日期
        
        Args:
            period: 周期字符串
            
        Returns:
            开始日期
        """
        now = datetime.now()
        
        if period == '1d':
            return now - timedelta(days=1)
        elif period == '5d':
            return now - timedelta(days=5)
        elif period == '1mo':
            return now - timedelta(days=30)
        elif period == '3mo':
            return now - timedelta(days=90)
        elif period == '6mo':
            return now - timedelta(days=180)
        elif period == '1y':
            return now - timedelta(days=365)
        elif period == '2y':
            return now - timedelta(days=730)
        elif period == '5y':
            return now - timedelta(days=1825)
        elif period == '10y':
            return now - timedelta(days=3650)
        elif period == 'ytd':
            return datetime(now.year, 1, 1)
        elif period == 'max':
            return datetime(1990, 1, 1)  # 足够早的日期
        else:
            # 默认2年
            return now - timedelta(days=730)
    
    def _standardize_data(self, data: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """
        标准化数据格式
        
        Args:
            data: 原始数据
            symbol: 股票代码
            
        Returns:
            标准化后的数据
        """
        # 确保数据按日期排序
        data = data.sort_index()
        
        # 添加股票代码列
        data['Symbol'] = symbol
        
        # 确保数值类型正确
        numeric_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        for col in numeric_columns:
            if col in data.columns:
                data[col] = pd.to_numeric(data[col], errors='coerce')
        
        # 移除包含NaN的行
        data = data.dropna()
        
        # 添加一些基础技术指标
        data['Change'] = data['Close'].pct_change(fill_method=None)
        data['Change_Amount'] = data['Close'] - data['Close'].shift(1)
        
        return data
    
    def get_available_sources(self) -> List[str]:
        """
        获取可用的数据源列表
        
        Returns:
            可用数据源列表
        """
        sources = []
        
        if self.tushare_pro is not None:
            sources.append('tushare')
        
        if self.yfinance_timeout is not None:
            sources.append('yfinance')
        
        if ak is not None and self.config.get('akshare', {}).get('enabled', False):
            sources.append('akshare')
        
        return sources
    
    def test_connection(self, source: str = 'auto') -> Dict[str, bool]:
        """
        测试数据源连接
        
        Args:
            source: 要测试的数据源
            
        Returns:
            测试结果字典
        """
        results = {}
        
        sources = self._get_source_priority(source)
        
        for src in sources:
            try:
                # 使用一个常见的股票代码进行测试
                test_symbol = "000001.SZ"  # 平安银行
                data = self._fetch_from_source(test_symbol, '5d', src)
                results[src] = data is not None and not data.empty
            except Exception as e:
                logger.warning(f"测试 {src} 连接失败: {str(e)}")
                results[src] = False
        
        return results