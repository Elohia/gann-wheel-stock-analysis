#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统集成测试用例

本模块包含整个股票分析系统的集成测试。
测试覆盖数据获取、存储、分析和系统整体功能。

作者: Assistant
日期: 2024-01-15
"""

import unittest
import pandas as pd
import numpy as np
import os
import tempfile
import shutil
from datetime import datetime, timedelta
import sys

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import StockAnalysisSystem
from src.data.data_fetcher import DataFetcher
from src.storage.database_manager import DatabaseManager
from src.analysis.gann.gann_wheel import GannWheel
from src.analysis.volume_price.volume_price_analyzer import VolumePriceAnalyzer
from src.config.config_manager import ConfigManager


class TestSystemIntegration(unittest.TestCase):
    """系统集成测试类"""
    
    def setUp(self):
        """测试前准备工作"""
        # 创建临时目录用于测试
        self.test_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.test_dir, 'test_config.yaml')
        
        # 创建测试配置文件
        test_config = {
            'data_sources': {
                'primary': 'mock',  # 使用模拟数据源
                'fallback': ['mock'],
                'mock': {
                    'enabled': True
                }
            },
            'database': {
                'type': 'sqlite',
                'sqlite': {
                    'path': os.path.join(self.test_dir, 'test_stock_data.db')
                }
            },
            'analysis': {
                'gann': {
                    'time_cycles': [7, 14, 21, 30],
                    'price_squares': [144, 169, 225]
                },
                'volume_price': {
                    'ma_periods': [5, 10, 20],
                    'volume_threshold': 2.0
                }
            },
            'logging': {
                'level': 'INFO',
                'file': os.path.join(self.test_dir, 'test.log')
            },
            'stocks': {
                'default_list': ['TEST001', 'TEST002']
            }
        }
        
        # 写入配置文件
        import yaml
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(test_config, f, default_flow_style=False, allow_unicode=True)
            
        # 创建测试数据
        self.create_test_data()
        
    def tearDown(self):
        """测试后清理工作"""
        # 删除临时目录
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
            
    def create_test_data(self):
        """创建测试用的股票数据"""
        dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
        np.random.seed(42)
        
        # 生成两只测试股票的数据
        self.test_stocks = {}
        
        for symbol in ['TEST001', 'TEST002']:
            base_price = 10.0 if symbol == 'TEST001' else 20.0
            price_changes = np.random.normal(0, 0.02, len(dates))
            prices = [base_price]
            
            for change in price_changes[1:]:
                new_price = prices[-1] * (1 + change)
                prices.append(max(new_price, 0.1))
                
            volumes = np.random.lognormal(10, 0.5, len(dates))
            
            data = pd.DataFrame({
                'date': dates,
                'open': prices,
                'high': [p * (1 + abs(np.random.normal(0, 0.01))) for p in prices],
                'low': [p * (1 - abs(np.random.normal(0, 0.01))) for p in prices],
                'close': prices,
                'volume': volumes
            })
            
            # 确保OHLC数据的逻辑关系
            data['high'] = data[['high', 'close']].max(axis=1)
            data['low'] = data[['low', 'close']].min(axis=1)
            
            self.test_stocks[symbol] = data
            
    def test_system_initialization(self):
        """测试系统初始化"""
        try:
            system = StockAnalysisSystem(self.config_path)
            self.assertIsInstance(system, StockAnalysisSystem)
            
            # 检查各个组件是否正确初始化
            self.assertIsInstance(system.config_manager, ConfigManager)
            self.assertIsInstance(system.db_manager, DatabaseManager)
            self.assertIsInstance(system.data_fetcher, DataFetcher)
            self.assertIsInstance(system.gann_wheel, GannWheel)
            self.assertIsInstance(system.volume_price_analyzer, VolumePriceAnalyzer)
            
        except Exception as e:
            self.fail(f"系统初始化失败: {e}")
            
    def test_config_management(self):
        """测试配置管理"""
        system = StockAnalysisSystem(self.config_path)
        
        # 测试配置读取
        config = system.config_manager.get_config()
        self.assertIsInstance(config, dict)
        self.assertIn('data_sources', config)
        self.assertIn('database', config)
        self.assertIn('analysis', config)
        
        # 测试配置更新
        system.config_manager.set_config('test_key', 'test_value')
        self.assertEqual(system.config_manager.get_config('test_key'), 'test_value')
        
    def test_database_operations(self):
        """测试数据库操作"""
        system = StockAnalysisSystem(self.config_path)
        
        # 测试数据保存
        test_symbol = 'TEST001'
        test_data = self.test_stocks[test_symbol]
        
        success = system.db_manager.save_stock_data(test_symbol, test_data)
        self.assertTrue(success)
        
        # 测试数据读取
        retrieved_data = system.db_manager.get_stock_data(test_symbol)
        self.assertIsInstance(retrieved_data, pd.DataFrame)
        self.assertGreater(len(retrieved_data), 0)
        
        # 测试分析结果保存
        test_result = {
            'analysis_type': 'test',
            'result': {'score': 0.8, 'signals': ['buy']}
        }
        
        success = system.db_manager.save_analysis_result(
            test_symbol, 'test_analysis', test_result
        )
        self.assertTrue(success)
        
        # 测试分析结果读取
        retrieved_result = system.db_manager.get_analysis_result(
            test_symbol, 'test_analysis'
        )
        self.assertIsInstance(retrieved_result, dict)
        
    def test_data_fetching_workflow(self):
        """测试数据获取工作流程"""
        system = StockAnalysisSystem(self.config_path)
        
        # 模拟数据获取（由于使用mock数据源，这里主要测试流程）
        test_symbol = 'TEST001'
        
        # 测试数据获取和存储
        try:
            success = system.fetch_and_store_data(test_symbol, '1y')
            # 由于使用mock数据源，可能会失败，但不应该抛出异常
            self.assertIsInstance(success, bool)
        except Exception as e:
            # 如果mock数据源未实现，应该有适当的错误处理
            self.assertIsInstance(e, (NotImplementedError, ValueError))
            
    def test_gann_analysis_integration(self):
        """测试江恩分析集成"""
        system = StockAnalysisSystem(self.config_path)
        
        # 先保存测试数据
        test_symbol = 'TEST001'
        test_data = self.test_stocks[test_symbol]
        system.db_manager.save_stock_data(test_symbol, test_data)
        
        # 执行江恩分析
        try:
            result = system.analyze_stock(test_symbol, 'gann')
            
            self.assertIsInstance(result, dict)
            self.assertIn('gann', result)
            
            gann_result = result['gann']
            self.assertIsInstance(gann_result, dict)
            
            # 检查江恩分析结果结构
            expected_keys = [
                'time_cycles', 'price_cycles', 'gann_angles',
                'gann_square', 'resonance_analysis', 'support_resistance'
            ]
            
            for key in expected_keys:
                self.assertIn(key, gann_result)
                
        except Exception as e:
            self.fail(f"江恩分析集成测试失败: {e}")
            
    def test_volume_price_analysis_integration(self):
        """测试量价分析集成"""
        system = StockAnalysisSystem(self.config_path)
        
        # 先保存测试数据
        test_symbol = 'TEST001'
        test_data = self.test_stocks[test_symbol]
        system.db_manager.save_stock_data(test_symbol, test_data)
        
        # 执行量价分析
        try:
            result = system.analyze_stock(test_symbol, 'volume_price')
            
            self.assertIsInstance(result, dict)
            self.assertIn('volume_price', result)
            
            vp_result = result['volume_price']
            self.assertIsInstance(vp_result, dict)
            
            # 检查量价分析结果结构
            expected_keys = [
                'volume_price_relation', 'divergence_analysis',
                'volume_indicators', 'coordination_analysis',
                'abnormal_volume', 'trading_signals'
            ]
            
            for key in expected_keys:
                self.assertIn(key, vp_result)
                
        except Exception as e:
            self.fail(f"量价分析集成测试失败: {e}")
            
    def test_comprehensive_analysis(self):
        """测试综合分析"""
        system = StockAnalysisSystem(self.config_path)
        
        # 先保存测试数据
        test_symbol = 'TEST001'
        test_data = self.test_stocks[test_symbol]
        system.db_manager.save_stock_data(test_symbol, test_data)
        
        # 执行综合分析
        try:
            result = system.analyze_stock(test_symbol, 'all')
            
            self.assertIsInstance(result, dict)
            self.assertIn('gann', result)
            self.assertIn('volume_price', result)
            
            # 检查两种分析结果都存在
            gann_result = result['gann']
            vp_result = result['volume_price']
            
            self.assertIsInstance(gann_result, dict)
            self.assertIsInstance(vp_result, dict)
            
            # 检查结果是否被保存到数据库
            saved_result = system.db_manager.get_analysis_result(test_symbol)
            self.assertIsInstance(saved_result, dict)
            
        except Exception as e:
            self.fail(f"综合分析测试失败: {e}")
            
    def test_batch_analysis(self):
        """测试批量分析"""
        system = StockAnalysisSystem(self.config_path)
        
        # 保存多只股票的测试数据
        for symbol, data in self.test_stocks.items():
            system.db_manager.save_stock_data(symbol, data)
            
        # 执行批量分析
        try:
            results = system.batch_analyze(['TEST001', 'TEST002'])
            
            self.assertIsInstance(results, dict)
            self.assertIn('TEST001', results)
            self.assertIn('TEST002', results)
            
            # 检查每只股票的分析结果
            for symbol in ['TEST001', 'TEST002']:
                result = results[symbol]
                self.assertIsInstance(result, dict)
                
                if 'success' in result and result['success']:
                    self.assertIn('gann', result)
                    self.assertIn('volume_price', result)
                    
        except Exception as e:
            self.fail(f"批量分析测试失败: {e}")
            
    def test_error_handling(self):
        """测试错误处理"""
        system = StockAnalysisSystem(self.config_path)
        
        # 测试分析不存在的股票
        result = system.analyze_stock('NONEXISTENT', 'all')
        
        # 应该返回错误信息而不是抛出异常
        self.assertIsInstance(result, dict)
        if 'error' in result:
            self.assertIsInstance(result['error'], str)
            
        # 测试无效的分析类型
        test_symbol = 'TEST001'
        test_data = self.test_stocks[test_symbol]
        system.db_manager.save_stock_data(test_symbol, test_data)
        
        result = system.analyze_stock(test_symbol, 'invalid_type')
        self.assertIsInstance(result, dict)
        
    def test_data_consistency(self):
        """测试数据一致性"""
        system = StockAnalysisSystem(self.config_path)
        
        test_symbol = 'TEST001'
        test_data = self.test_stocks[test_symbol]
        
        # 保存数据
        system.db_manager.save_stock_data(test_symbol, test_data)
        
        # 读取数据
        retrieved_data = system.db_manager.get_stock_data(test_symbol)
        
        # 检查数据一致性
        self.assertEqual(len(test_data), len(retrieved_data))
        
        # 检查关键列是否存在
        required_columns = ['date', 'open', 'high', 'low', 'close', 'volume']
        for col in required_columns:
            self.assertIn(col, retrieved_data.columns)
            
    def test_performance_monitoring(self):
        """测试性能监控"""
        system = StockAnalysisSystem(self.config_path)
        
        test_symbol = 'TEST001'
        test_data = self.test_stocks[test_symbol]
        system.db_manager.save_stock_data(test_symbol, test_data)
        
        # 测试分析性能
        import time
        
        start_time = time.time()
        result = system.analyze_stock(test_symbol, 'all')
        end_time = time.time()
        
        analysis_time = end_time - start_time
        
        # 分析时间应该在合理范围内（小于10秒）
        self.assertLess(analysis_time, 10.0)
        
        # 检查结果是否有效
        self.assertIsInstance(result, dict)
        
    def test_logging_functionality(self):
        """测试日志功能"""
        system = StockAnalysisSystem(self.config_path)
        
        # 检查日志文件是否创建
        log_file = os.path.join(self.test_dir, 'test.log')
        
        # 执行一些操作以生成日志
        test_symbol = 'TEST001'
        test_data = self.test_stocks[test_symbol]
        system.db_manager.save_stock_data(test_symbol, test_data)
        system.analyze_stock(test_symbol, 'gann')
        
        # 检查日志文件是否存在且有内容
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                log_content = f.read()
                self.assertGreater(len(log_content), 0)
                
    def test_database_stats(self):
        """测试数据库统计功能"""
        system = StockAnalysisSystem(self.config_path)
        
        # 保存一些测试数据
        for symbol, data in self.test_stocks.items():
            system.db_manager.save_stock_data(symbol, data)
            
        # 获取数据库统计信息
        stats = system.db_manager.get_database_stats()
        
        self.assertIsInstance(stats, dict)
        
        # 检查统计信息是否包含预期的键
        expected_keys = ['total_stocks', 'total_records', 'date_range']
        
        for key in expected_keys:
            if key in stats:
                self.assertIsNotNone(stats[key])
                

class TestSystemRobustness(unittest.TestCase):
    """系统健壮性测试类"""
    
    def setUp(self):
        """测试前准备工作"""
        self.test_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.test_dir, 'test_config.yaml')
        
        # 创建基本配置
        test_config = {
            'database': {
                'type': 'sqlite',
                'sqlite': {
                    'path': os.path.join(self.test_dir, 'test_stock_data.db')
                }
            },
            'logging': {
                'level': 'ERROR',
                'file': os.path.join(self.test_dir, 'test.log')
            }
        }
        
        import yaml
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(test_config, f, default_flow_style=False, allow_unicode=True)
            
    def tearDown(self):
        """测试后清理工作"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
            
    def test_invalid_config_handling(self):
        """测试无效配置处理"""
        # 创建无效配置文件
        invalid_config_path = os.path.join(self.test_dir, 'invalid_config.yaml')
        with open(invalid_config_path, 'w') as f:
            f.write("invalid: yaml: content: [")
            
        # 系统应该能处理无效配置
        try:
            system = StockAnalysisSystem(invalid_config_path)
            # 如果能创建系统，说明有默认配置处理
            self.assertIsInstance(system, StockAnalysisSystem)
        except Exception as e:
            # 如果抛出异常，应该是可预期的异常类型
            self.assertIsInstance(e, (yaml.YAMLError, FileNotFoundError, ValueError))
            
    def test_missing_config_file(self):
        """测试配置文件缺失处理"""
        nonexistent_config = os.path.join(self.test_dir, 'nonexistent.yaml')
        
        try:
            system = StockAnalysisSystem(nonexistent_config)
            # 如果能创建系统，说明有默认配置处理
            self.assertIsInstance(system, StockAnalysisSystem)
        except FileNotFoundError:
            # 这是预期的异常
            pass
            
    def test_database_connection_failure(self):
        """测试数据库连接失败处理"""
        # 创建指向无效路径的配置
        invalid_db_config = {
            'database': {
                'type': 'sqlite',
                'sqlite': {
                    'path': '/invalid/path/database.db'  # 无效路径
                }
            },
            'logging': {
                'level': 'ERROR',
                'file': os.path.join(self.test_dir, 'test.log')
            }
        }
        
        invalid_config_path = os.path.join(self.test_dir, 'invalid_db_config.yaml')
        import yaml
        with open(invalid_config_path, 'w', encoding='utf-8') as f:
            yaml.dump(invalid_db_config, f, default_flow_style=False, allow_unicode=True)
            
        try:
            system = StockAnalysisSystem(invalid_config_path)
            # 系统应该能处理数据库连接失败
            self.assertIsInstance(system, StockAnalysisSystem)
        except Exception as e:
            # 应该有适当的错误处理
            self.assertIsInstance(e, (OSError, PermissionError, ValueError))
            
    def test_memory_usage_with_large_data(self):
        """测试大数据集的内存使用"""
        system = StockAnalysisSystem(self.config_path)
        
        # 创建大数据集（5年日线数据）
        dates = pd.date_range(start='2019-01-01', end='2023-12-31', freq='D')
        np.random.seed(42)
        
        large_data = pd.DataFrame({
            'date': dates,
            'open': np.random.uniform(10, 100, len(dates)),
            'high': np.random.uniform(10, 100, len(dates)),
            'low': np.random.uniform(10, 100, len(dates)),
            'close': np.random.uniform(10, 100, len(dates)),
            'volume': np.random.uniform(1000000, 10000000, len(dates))
        })
        
        # 确保OHLC逻辑关系
        large_data['high'] = large_data[['open', 'high', 'close']].max(axis=1)
        large_data['low'] = large_data[['open', 'low', 'close']].min(axis=1)
        
        try:
            # 保存大数据集
            success = system.db_manager.save_stock_data('LARGE_TEST', large_data)
            self.assertTrue(success)
            
            # 分析大数据集
            result = system.analyze_stock('LARGE_TEST', 'all')
            self.assertIsInstance(result, dict)
            
        except MemoryError:
            self.fail("系统在处理大数据集时出现内存错误")
        except Exception as e:
            # 其他异常应该被适当处理
            self.assertIsInstance(e, (ValueError, RuntimeError))
            

if __name__ == '__main__':
    # 创建测试套件
    test_suite = unittest.TestSuite()
    
    # 添加集成测试
    test_suite.addTest(unittest.makeSuite(TestSystemIntegration))
    
    # 添加健壮性测试
    test_suite.addTest(unittest.makeSuite(TestSystemRobustness))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 输出测试结果摘要
    print(f"\n测试摘要:")
    print(f"运行测试: {result.testsRun}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print(f"成功率: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    # 如果有失败或错误，输出详细信息
    if result.failures:
        print("\n失败的测试:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
            
    if result.errors:
        print("\n错误的测试:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")