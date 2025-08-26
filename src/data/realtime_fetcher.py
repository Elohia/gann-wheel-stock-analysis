#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实时股票数据获取模块

提供实时股票价格获取功能，支持多种实时数据源和WebSocket连接。
包括实时价格、分时数据和盘口数据的获取。

Author: AI Assistant
Date: 2024
"""

import asyncio
import json
import time
import websocket
import threading
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime, timedelta
from loguru import logger
import pandas as pd

try:
    import akshare as ak
except ImportError:
    ak = None
    logger.warning("AKShare未安装，实时数据功能将受限")

try:
    import tushare as ts
except ImportError:
    ts = None
    logger.warning("Tushare未安装，实时数据功能将受限")

try:
    import requests
except ImportError:
    requests = None
    logger.error("requests库未安装，无法获取实时数据")


class RealtimeDataFetcher:
    """
    实时股票数据获取器
    
    支持多种实时数据源，提供统一的实时数据获取接口
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化实时数据获取器
        
        Args:
            config: 实时数据配置
        """
        self.config = config
        self.realtime_config = config.get('realtime_data', {})
        self.update_interval = self.realtime_config.get('update_interval', 5)  # 默认5秒更新
        self.max_retries = self.realtime_config.get('max_retries', 3)
        
        # 实时数据缓存
        self.realtime_cache = {}
        self.last_update_time = {}
        
        # WebSocket连接
        self.ws_connections = {}
        self.ws_callbacks = {}
        
        # 数据源初始化
        self._init_data_sources()
        
        logger.info("实时数据获取器初始化完成")
    
    def _init_data_sources(self):
        """
        初始化数据源
        """
        # 初始化AKShare
        if ak is not None:
            self.akshare_enabled = self.realtime_config.get('akshare', {}).get('enabled', True)
        else:
            self.akshare_enabled = False
        
        # 初始化Tushare
        if ts is not None:
            tushare_config = self.realtime_config.get('tushare', {})
            token = tushare_config.get('token')
            if token and token != 'your_tushare_token_here':
                ts.set_token(token)
                self.tushare_enabled = True
            else:
                self.tushare_enabled = False
        else:
            self.tushare_enabled = False
        
        # 初始化其他数据源
        self.sina_enabled = self.realtime_config.get('sina', {}).get('enabled', True)
        self.eastmoney_enabled = self.realtime_config.get('eastmoney', {}).get('enabled', True)
    
    def get_realtime_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        获取实时股票价格
        
        Args:
            symbol: 股票代码
            
        Returns:
            实时价格数据字典
        """
        logger.info(f"获取实时价格: {symbol}")
        
        # 检查缓存
        if self._is_cache_valid(symbol):
            logger.debug(f"使用缓存数据: {symbol}")
            return self.realtime_cache.get(symbol)
        
        # 尝试从各数据源获取
        data = None
        
        # 1. 尝试AKShare
        if self.akshare_enabled and data is None:
            data = self._get_realtime_from_akshare(symbol)
        
        # 2. 尝试新浪财经
        if self.sina_enabled and data is None:
            data = self._get_realtime_from_sina(symbol)
        
        # 3. 尝试东方财富
        if self.eastmoney_enabled and data is None:
            data = self._get_realtime_from_eastmoney(symbol)
        
        # 4. 尝试Tushare
        if self.tushare_enabled and data is None:
            data = self._get_realtime_from_tushare(symbol)
        
        if data:
            # 更新缓存
            self.realtime_cache[symbol] = data
            self.last_update_time[symbol] = datetime.now()
            logger.info(f"实时价格获取成功: {symbol}, 价格: {data.get('current_price', 'N/A')}")
        else:
            logger.warning(f"无法获取实时价格: {symbol}")
        
        return data
    
    def _is_cache_valid(self, symbol: str) -> bool:
        """
        检查缓存是否有效
        
        Args:
            symbol: 股票代码
            
        Returns:
            缓存是否有效
        """
        if symbol not in self.realtime_cache:
            return False
        
        last_update = self.last_update_time.get(symbol)
        if not last_update:
            return False
        
        # 检查是否超过更新间隔
        time_diff = (datetime.now() - last_update).total_seconds()
        return time_diff < self.update_interval
    
    def _get_realtime_from_akshare(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        从AKShare获取实时数据
        
        Args:
            symbol: 股票代码
            
        Returns:
            实时数据字典
        """
        try:
            # 转换股票代码格式
            ak_symbol = symbol.replace('.SH', '').replace('.SZ', '')
            
            # 获取实时数据
            df = ak.stock_zh_a_spot_em()
            
            if df.empty:
                return None
            
            # 查找对应股票
            stock_data = df[df['代码'] == ak_symbol]
            
            if stock_data.empty:
                return None
            
            row = stock_data.iloc[0]
            
            return {
                'symbol': symbol,
                'name': row.get('名称', ''),
                'current_price': float(row.get('最新价', 0)),
                'change': float(row.get('涨跌额', 0)),
                'change_percent': float(row.get('涨跌幅', 0)),
                'open_price': float(row.get('今开', 0)),
                'high_price': float(row.get('最高', 0)),
                'low_price': float(row.get('最低', 0)),
                'pre_close': float(row.get('昨收', 0)),
                'volume': int(row.get('成交量', 0)),
                'turnover': float(row.get('成交额', 0)),
                'timestamp': datetime.now(),
                'source': 'akshare'
            }
            
        except Exception as e:
            logger.warning(f"AKShare获取实时数据失败 {symbol}: {str(e)}")
            return None
    
    def _get_realtime_from_sina(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        从新浪财经获取实时数据
        
        Args:
            symbol: 股票代码
            
        Returns:
            实时数据字典
        """
        try:
            # 转换股票代码格式
            if symbol.endswith('.SH'):
                sina_symbol = 'sh' + symbol.replace('.SH', '')
            elif symbol.endswith('.SZ'):
                sina_symbol = 'sz' + symbol.replace('.SZ', '')
            else:
                return None
            
            # 构建请求URL
            url = f"http://hq.sinajs.cn/list={sina_symbol}"
            
            response = requests.get(url, timeout=5)
            response.encoding = 'gbk'
            
            if response.status_code != 200:
                return None
            
            # 解析数据
            content = response.text
            if 'var hq_str_' not in content:
                return None
            
            data_str = content.split('="')[1].split('";')[0]
            data_parts = data_str.split(',')
            
            if len(data_parts) < 32:
                return None
            
            return {
                'symbol': symbol,
                'name': data_parts[0],
                'open_price': float(data_parts[1]) if data_parts[1] else 0,
                'pre_close': float(data_parts[2]) if data_parts[2] else 0,
                'current_price': float(data_parts[3]) if data_parts[3] else 0,
                'high_price': float(data_parts[4]) if data_parts[4] else 0,
                'low_price': float(data_parts[5]) if data_parts[5] else 0,
                'volume': int(float(data_parts[8])) if data_parts[8] else 0,
                'turnover': float(data_parts[9]) if data_parts[9] else 0,
                'change': float(data_parts[3]) - float(data_parts[2]) if data_parts[3] and data_parts[2] else 0,
                'change_percent': ((float(data_parts[3]) - float(data_parts[2])) / float(data_parts[2]) * 100) if data_parts[3] and data_parts[2] and float(data_parts[2]) != 0 else 0,
                'timestamp': datetime.now(),
                'source': 'sina'
            }
            
        except Exception as e:
            logger.warning(f"新浪财经获取实时数据失败 {symbol}: {str(e)}")
            return None
    
    def _get_realtime_from_eastmoney(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        从东方财富获取实时数据
        
        Args:
            symbol: 股票代码
            
        Returns:
            实时数据字典
        """
        try:
            # 转换股票代码格式
            if symbol.endswith('.SH'):
                em_symbol = '1.' + symbol.replace('.SH', '')
            elif symbol.endswith('.SZ'):
                em_symbol = '0.' + symbol.replace('.SZ', '')
            else:
                return None
            
            # 构建请求URL
            url = f"http://push2.eastmoney.com/api/qt/stock/get?secid={em_symbol}&fields=f43,f44,f45,f46,f47,f48,f49,f50,f51,f52,f57,f58"
            
            response = requests.get(url, timeout=5)
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            
            if not data.get('data'):
                return None
            
            stock_data = data['data']
            
            current_price = stock_data.get('f43', 0) / 100 if stock_data.get('f43') else 0
            pre_close = stock_data.get('f60', 0) / 100 if stock_data.get('f60') else 0
            
            return {
                'symbol': symbol,
                'name': stock_data.get('f58', ''),
                'current_price': current_price,
                'change': stock_data.get('f169', 0) / 100 if stock_data.get('f169') else 0,
                'change_percent': stock_data.get('f170', 0) / 100 if stock_data.get('f170') else 0,
                'open_price': stock_data.get('f46', 0) / 100 if stock_data.get('f46') else 0,
                'high_price': stock_data.get('f44', 0) / 100 if stock_data.get('f44') else 0,
                'low_price': stock_data.get('f45', 0) / 100 if stock_data.get('f45') else 0,
                'pre_close': pre_close,
                'volume': stock_data.get('f47', 0),
                'turnover': stock_data.get('f48', 0),
                'timestamp': datetime.now(),
                'source': 'eastmoney'
            }
            
        except Exception as e:
            logger.warning(f"东方财富获取实时数据失败 {symbol}: {str(e)}")
            return None
    
    def _get_realtime_from_tushare(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        从Tushare获取实时数据
        
        Args:
            symbol: 股票代码
            
        Returns:
            实时数据字典
        """
        try:
            if not self.tushare_enabled:
                return None
            
            # Tushare的实时数据接口（需要积分）
            df = ts.realtime_quote(ts_code=symbol)
            
            if df.empty:
                return None
            
            row = df.iloc[0]
            
            return {
                'symbol': symbol,
                'name': row.get('name', ''),
                'current_price': float(row.get('price', 0)),
                'change': float(row.get('change', 0)),
                'change_percent': float(row.get('pct_chg', 0)),
                'open_price': float(row.get('open', 0)),
                'high_price': float(row.get('high', 0)),
                'low_price': float(row.get('low', 0)),
                'pre_close': float(row.get('pre_close', 0)),
                'volume': int(row.get('vol', 0)),
                'turnover': float(row.get('amount', 0)),
                'timestamp': datetime.now(),
                'source': 'tushare'
            }
            
        except Exception as e:
            logger.warning(f"Tushare获取实时数据失败 {symbol}: {str(e)}")
            return None
    
    def get_realtime_quotes(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        批量获取实时报价
        
        Args:
            symbols: 股票代码列表
            
        Returns:
            股票实时数据字典
        """
        logger.info(f"批量获取实时报价: {len(symbols)} 只股票")
        
        results = {}
        
        for symbol in symbols:
            try:
                data = self.get_realtime_price(symbol)
                if data:
                    results[symbol] = data
                else:
                    logger.warning(f"获取实时数据失败: {symbol}")
            except Exception as e:
                logger.error(f"获取 {symbol} 实时数据时发生错误: {str(e)}")
        
        logger.info(f"批量获取完成，成功获取 {len(results)}/{len(symbols)} 只股票数据")
        return results
    
    def start_realtime_monitoring(self, symbols: List[str], callback: Callable[[str, Dict[str, Any]], None]):
        """
        启动实时监控
        
        Args:
            symbols: 要监控的股票代码列表
            callback: 数据更新回调函数
        """
        logger.info(f"启动实时监控: {len(symbols)} 只股票")
        
        def monitor_loop():
            while True:
                try:
                    for symbol in symbols:
                        data = self.get_realtime_price(symbol)
                        if data:
                            callback(symbol, data)
                    
                    time.sleep(self.update_interval)
                    
                except Exception as e:
                    logger.error(f"实时监控发生错误: {str(e)}")
                    time.sleep(self.update_interval)
        
        # 在后台线程中运行监控
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
        
        logger.info("实时监控已启动")
    
    def get_intraday_data(self, symbol: str, period: str = '1m') -> Optional[pd.DataFrame]:
        """
        获取分时数据
        
        Args:
            symbol: 股票代码
            period: 时间周期 ('1m', '5m', '15m', '30m', '60m')
            
        Returns:
            分时数据DataFrame
        """
        logger.info(f"获取分时数据: {symbol}, 周期: {period}")
        
        try:
            if ak is not None:
                # 使用AKShare获取分时数据
                ak_symbol = symbol.replace('.SH', '').replace('.SZ', '')
                
                if period == '1m':
                    df = ak.stock_zh_a_minute(symbol=ak_symbol, period='1', adjust="")
                elif period == '5m':
                    df = ak.stock_zh_a_minute(symbol=ak_symbol, period='5', adjust="")
                elif period == '15m':
                    df = ak.stock_zh_a_minute(symbol=ak_symbol, period='15', adjust="")
                elif period == '30m':
                    df = ak.stock_zh_a_minute(symbol=ak_symbol, period='30', adjust="")
                elif period == '60m':
                    df = ak.stock_zh_a_minute(symbol=ak_symbol, period='60', adjust="")
                else:
                    logger.warning(f"不支持的周期: {period}")
                    return None
                
                if not df.empty:
                    # 标准化列名
                    df = df.rename(columns={
                        'day': 'Date',
                        '开盘': 'Open',
                        '最高': 'High', 
                        '最低': 'Low',
                        '收盘': 'Close',
                        '成交量': 'Volume'
                    })
                    
                    df['Date'] = pd.to_datetime(df['Date'])
                    df = df.set_index('Date').sort_index()
                    
                    logger.info(f"分时数据获取成功: {symbol}, 共 {len(df)} 条记录")
                    return df
            
            logger.warning(f"无法获取分时数据: {symbol}")
            return None
            
        except Exception as e:
            logger.error(f"获取分时数据失败 {symbol}: {str(e)}")
            return None
    
    def clear_cache(self):
        """
        清空缓存
        """
        self.realtime_cache.clear()
        self.last_update_time.clear()
        logger.info("实时数据缓存已清空")
    
    def get_cache_info(self) -> Dict[str, Any]:
        """
        获取缓存信息
        
        Returns:
            缓存信息字典
        """
        return {
            'cached_symbols': list(self.realtime_cache.keys()),
            'cache_size': len(self.realtime_cache),
            'last_update_times': {k: v.isoformat() for k, v in self.last_update_time.items()},
            'update_interval': self.update_interval
        }