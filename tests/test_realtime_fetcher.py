#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实时数据获取器测试模块

测试实时股票数据获取功能，包括：
- 实时价格获取
- 分时数据获取
- 盘口数据获取
- 数据缓存机制
- 监控功能
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta

from src.data.realtime_fetcher import RealtimeFetcher
from src.utils.config_manager import ConfigManager


class TestRealtimeFetcher:
    """实时数据获取器测试类"""
    
    @pytest.fixture
    def config_manager(self):
        """创建配置管理器实例"""
        config = {
            'realtime_data': {
                'enabled': True,
                'update_interval': 5,
                'max_retries': 3,
                'cache_timeout': 30,
                'akshare': {'enabled': True, 'priority': 1},
                'sina': {'enabled': True, 'priority': 2},
                'eastmoney': {'enabled': True, 'priority': 3},
                'tushare': {'enabled': False, 'priority': 4},
                'monitoring': {
                    'enabled': False,
                    'symbols': [],
                    'alert_threshold': 5.0
                }
            }
        }
        mock_config = Mock(spec=ConfigManager)
        mock_config.get_config.return_value = config
        return mock_config
    
    @pytest.fixture
    def realtime_fetcher(self, config_manager):
        """创建实时数据获取器实例"""
        return RealtimeFetcher(config_manager)
    
    def test_init(self, realtime_fetcher):
        """测试初始化"""
        assert realtime_fetcher is not None
        assert realtime_fetcher.config is not None
        assert realtime_fetcher.cache == {}
        assert realtime_fetcher.monitoring_symbols == set()
        assert realtime_fetcher.monitoring_task is None
    
    @pytest.mark.asyncio
    async def test_get_realtime_price_akshare(self, realtime_fetcher):
        """测试通过AKShare获取实时价格"""
        # Mock AKShare数据
        mock_data = {
            'symbol': '000001',
            'name': '平安银行',
            'price': 12.50,
            'change': 0.15,
            'change_pct': 1.21,
            'volume': 1000000,
            'amount': 12500000.0,
            'high': 12.60,
            'low': 12.30,
            'open': 12.35,
            'pre_close': 12.35,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        with patch.object(realtime_fetcher, '_fetch_akshare_realtime', 
                         new_callable=AsyncMock, return_value=mock_data):
            result = await realtime_fetcher.get_realtime_price('000001')
            
            assert result is not None
            assert result['symbol'] == '000001'
            assert result['price'] == 12.50
            assert 'timestamp' in result
    
    @pytest.mark.asyncio
    async def test_get_realtime_price_cache(self, realtime_fetcher):
        """测试实时价格缓存机制"""
        symbol = '000001'
        mock_data = {
            'symbol': symbol,
            'price': 12.50,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # 第一次调用，应该从数据源获取
        with patch.object(realtime_fetcher, '_fetch_akshare_realtime',
                         new_callable=AsyncMock, return_value=mock_data) as mock_fetch:
            result1 = await realtime_fetcher.get_realtime_price(symbol)
            assert mock_fetch.call_count == 1
        
        # 第二次调用，应该从缓存获取
        with patch.object(realtime_fetcher, '_fetch_akshare_realtime',
                         new_callable=AsyncMock, return_value=mock_data) as mock_fetch:
            result2 = await realtime_fetcher.get_realtime_price(symbol)
            assert mock_fetch.call_count == 0  # 不应该调用数据源
            assert result2['symbol'] == symbol
    
    @pytest.mark.asyncio
    async def test_get_tick_data(self, realtime_fetcher):
        """测试获取分时数据"""
        mock_data = {
            'symbol': '000001',
            'data': [
                {'time': '09:30', 'price': 12.35, 'volume': 100000},
                {'time': '09:31', 'price': 12.40, 'volume': 150000},
                {'time': '09:32', 'price': 12.45, 'volume': 120000}
            ],
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        with patch.object(realtime_fetcher, '_fetch_akshare_tick',
                         new_callable=AsyncMock, return_value=mock_data):
            result = await realtime_fetcher.get_tick_data('000001')
            
            assert result is not None
            assert result['symbol'] == '000001'
            assert len(result['data']) == 3
            assert result['data'][0]['time'] == '09:30'
    
    @pytest.mark.asyncio
    async def test_get_market_depth(self, realtime_fetcher):
        """测试获取盘口数据"""
        mock_data = {
            'symbol': '000001',
            'bid': [
                {'price': 12.49, 'volume': 1000},
                {'price': 12.48, 'volume': 2000},
                {'price': 12.47, 'volume': 1500}
            ],
            'ask': [
                {'price': 12.50, 'volume': 800},
                {'price': 12.51, 'volume': 1200},
                {'price': 12.52, 'volume': 900}
            ],
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        with patch.object(realtime_fetcher, '_fetch_akshare_depth',
                         new_callable=AsyncMock, return_value=mock_data):
            result = await realtime_fetcher.get_market_depth('000001')
            
            assert result is not None
            assert result['symbol'] == '000001'
            assert len(result['bid']) == 3
            assert len(result['ask']) == 3
            assert result['bid'][0]['price'] == 12.49
    
    @pytest.mark.asyncio
    async def test_start_monitoring(self, realtime_fetcher):
        """测试开始监控"""
        symbols = ['000001', '000002']
        
        await realtime_fetcher.start_monitoring(symbols)
        
        assert realtime_fetcher.monitoring_symbols == set(symbols)
        assert realtime_fetcher.monitoring_task is not None
        assert not realtime_fetcher.monitoring_task.done()
        
        # 清理
        await realtime_fetcher.stop_monitoring()
    
    @pytest.mark.asyncio
    async def test_stop_monitoring(self, realtime_fetcher):
        """测试停止监控"""
        symbols = ['000001', '000002']
        
        # 先开始监控
        await realtime_fetcher.start_monitoring(symbols)
        assert realtime_fetcher.monitoring_task is not None
        
        # 停止监控
        await realtime_fetcher.stop_monitoring()
        assert realtime_fetcher.monitoring_task is None
        assert len(realtime_fetcher.monitoring_symbols) == 0
    
    def test_is_cache_valid(self, realtime_fetcher):
        """测试缓存有效性检查"""
        symbol = '000001'
        
        # 缓存为空时应该无效
        assert not realtime_fetcher._is_cache_valid(symbol)
        
        # 添加新缓存
        realtime_fetcher.cache[symbol] = {
            'data': {'price': 12.50},
            'timestamp': datetime.now()
        }
        assert realtime_fetcher._is_cache_valid(symbol)
        
        # 过期缓存应该无效
        realtime_fetcher.cache[symbol]['timestamp'] = datetime.now() - timedelta(minutes=1)
        assert not realtime_fetcher._is_cache_valid(symbol)
    
    @pytest.mark.asyncio
    async def test_fallback_mechanism(self, realtime_fetcher):
        """测试数据源回退机制"""
        symbol = '000001'
        
        # Mock AKShare失败，Sina成功
        with patch.object(realtime_fetcher, '_fetch_akshare_realtime',
                         new_callable=AsyncMock, side_effect=Exception("AKShare failed")):
            with patch.object(realtime_fetcher, '_fetch_sina_realtime',
                             new_callable=AsyncMock, return_value={'symbol': symbol, 'price': 12.50}):
                result = await realtime_fetcher.get_realtime_price(symbol)
                assert result is not None
                assert result['symbol'] == symbol
    
    @pytest.mark.asyncio
    async def test_error_handling(self, realtime_fetcher):
        """测试错误处理"""
        symbol = '000001'
        
        # 所有数据源都失败
        with patch.object(realtime_fetcher, '_fetch_akshare_realtime',
                         new_callable=AsyncMock, side_effect=Exception("Failed")):
            with patch.object(realtime_fetcher, '_fetch_sina_realtime',
                             new_callable=AsyncMock, side_effect=Exception("Failed")):
                with patch.object(realtime_fetcher, '_fetch_eastmoney_realtime',
                                 new_callable=AsyncMock, side_effect=Exception("Failed")):
                    with pytest.raises(Exception):
                        await realtime_fetcher.get_realtime_price(symbol)


if __name__ == '__main__':
    pytest.main([__file__])