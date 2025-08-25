#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
江恩轮中轮分析模块测试用例

本模块包含江恩轮中轮分析器的单元测试和集成测试。
测试覆盖时间周期计算、价格轮回分析、江恩角度线等核心功能。

作者: Assistant
日期: 2024-01-15
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.analysis.gann.gann_wheel import GannWheel


class TestGannWheel(unittest.TestCase):
    """江恩轮中轮分析器测试类"""
    
    def setUp(self):
        """测试前准备工作"""
        # 创建测试配置
        self.test_config = {
            'time_cycles': [7, 14, 21, 30, 45, 60, 90, 120, 180, 360],
            'price_angles': [15, 30, 45, 60, 75, 90, 105, 120, 135, 150, 165, 180],
            'square_size': 144,
            'tolerance': 0.02
        }
        
        self.gann = GannWheel(self.test_config)
        
        # 创建测试数据
        dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
        np.random.seed(42)  # 确保测试结果可重复
        
        # 生成模拟股价数据
        base_price = 10.0
        price_changes = np.random.normal(0, 0.02, len(dates))
        prices = [base_price]
        
        for change in price_changes[1:]:
            new_price = prices[-1] * (1 + change)
            prices.append(max(new_price, 0.1))  # 确保价格为正
        
        # 生成成交量数据
        volumes = np.random.lognormal(10, 0.5, len(dates))
        
        self.test_data = pd.DataFrame({
            'date': dates,
            'open': prices,
            'high': [p * (1 + abs(np.random.normal(0, 0.01))) for p in prices],
            'low': [p * (1 - abs(np.random.normal(0, 0.01))) for p in prices],
            'close': prices,
            'volume': volumes
        })
        
        # 确保high >= close >= low
        self.test_data['high'] = self.test_data[['high', 'close']].max(axis=1)
        self.test_data['low'] = self.test_data[['low', 'close']].min(axis=1)
        
    def test_initialization(self):
        """测试江恩分析器初始化"""
        # 测试默认初始化
        default_config = {
            'time_cycles': [7, 14, 21, 30, 45, 60, 90, 120, 180, 360],
            'price_angles': [15, 30, 45, 60, 75, 90, 105, 120, 135, 150, 165, 180],
            'square_size': 144,
            'tolerance': 0.02
        }
        gann = GannWheel(default_config)
        self.assertIsInstance(gann, GannWheel)
        
        # 测试自定义配置初始化
        config = {
            'time_cycles': [7, 14, 21],
            'price_squares': [144, 169, 225],
            'square_size': 144,
            'tolerance': 0.02
        }
        gann_custom = GannWheel(config)
        self.assertIsInstance(gann_custom, GannWheel)
        
    def test_analyze_basic(self):
        """测试基本分析功能"""
        result = self.gann.analyze(self.test_data)
        
        # 检查返回结果结构
        self.assertIsInstance(result, dict)
        expected_keys = [
            'time_cycles', 'price_cycles', 'gann_angles',
            'gann_square', 'resonance_analysis', 'support_resistance',
            'prediction'
        ]
        
        for key in expected_keys:
            self.assertIn(key, result)
            
    def test_calculate_time_cycles(self):
        """测试时间周期计算"""
        cycles = self.gann.calculate_time_cycles(self.test_data)
        
        self.assertIsInstance(cycles, list)
        self.assertGreater(len(cycles), 0)
        
        # 检查周期数据结构
        for cycle in cycles:
            self.assertIsInstance(cycle, dict)
            self.assertIn('period', cycle)
            self.assertIn('strength', cycle)
            self.assertIn('next_date', cycle)
            
    def test_calculate_price_cycles(self):
        """测试价格轮回计算"""
        cycles = self.gann.calculate_price_cycles(self.test_data)
        
        self.assertIsInstance(cycles, list)
        self.assertGreater(len(cycles), 0)
        
        # 检查价格轮回数据结构
        for cycle in cycles:
            self.assertIsInstance(cycle, dict)
            self.assertIn('square_root', cycle)
            self.assertIn('price_level', cycle)
            self.assertIn('cycle_type', cycle)
            
    def test_calculate_gann_angles(self):
        """测试江恩角度线计算"""
        angles = self.gann.calculate_gann_angles(self.test_data)
        
        self.assertIsInstance(angles, dict)
        self.assertIn('angles', angles)
        self.assertIn('current_position', angles)
        
        # 检查角度线数据
        angle_lines = angles['angles']
        self.assertIsInstance(angle_lines, list)
        
        for angle in angle_lines:
            self.assertIn('angle', angle)
            self.assertIn('price_line', angle)
            self.assertIn('support_resistance', angle)
            
    def test_find_support_resistance(self):
        """测试支撑阻力位识别"""
        sr_levels = self.gann.find_support_resistance(self.test_data)
        
        self.assertIsInstance(sr_levels, dict)
        self.assertIn('support', sr_levels)
        self.assertIn('resistance', sr_levels)
        
        # 检查支撑阻力位数据
        support_levels = sr_levels['support']
        resistance_levels = sr_levels['resistance']
        
        self.assertIsInstance(support_levels, list)
        self.assertIsInstance(resistance_levels, list)
        
        # 检查价格水平的合理性
        current_price = self.test_data['close'].iloc[-1]
        
        for level in support_levels:
            self.assertLessEqual(level['price'], current_price)
            
        for level in resistance_levels:
            self.assertGreaterEqual(level['price'], current_price)
            
    def test_gann_square_calculation(self):
        """测试江恩正方形计算"""
        result = self.gann.analyze(self.test_data)
        gann_square = result['gann_square']
        
        self.assertIsInstance(gann_square, dict)
        self.assertIn('current_square', gann_square)
        self.assertIn('key_levels', gann_square)
        self.assertIn('next_resistance', gann_square)
        self.assertIn('next_support', gann_square)
        
    def test_resonance_analysis(self):
        """测试时间价格共振分析"""
        result = self.gann.analyze(self.test_data)
        resonance = result['resonance_analysis']
        
        self.assertIsInstance(resonance, dict)
        self.assertIn('resonance_points', resonance)
        self.assertIn('strength_score', resonance)
        self.assertIn('next_resonance_date', resonance)
        
    def test_prediction_analysis(self):
        """测试预测分析"""
        result = self.gann.analyze(self.test_data)
        prediction = result['prediction']
        
        self.assertIsInstance(prediction, dict)
        self.assertIn('price_targets', prediction)
        self.assertIn('time_targets', prediction)
        self.assertIn('trend_direction', prediction)
        self.assertIn('confidence_level', prediction)
        
    def test_empty_data_handling(self):
        """测试空数据处理"""
        empty_data = pd.DataFrame()
        
        with self.assertRaises(ValueError):
            self.gann.analyze(empty_data)
            
    def test_insufficient_data_handling(self):
        """测试数据不足处理"""
        # 只有几天的数据
        short_data = self.test_data.head(5)
        
        result = self.gann.analyze(short_data)
        
        # 应该返回结果但可能包含警告
        self.assertIsInstance(result, dict)
        
    def test_invalid_data_handling(self):
        """测试无效数据处理"""
        # 创建包含NaN的数据
        invalid_data = self.test_data.copy()
        invalid_data.loc[10:20, 'close'] = np.nan
        
        result = self.gann.analyze(invalid_data)
        
        # 应该能处理并返回结果
        self.assertIsInstance(result, dict)
        
    def test_custom_config(self):
        """测试自定义配置"""
        custom_config = {
            'time_cycles': [5, 10, 15, 20],
            'price_squares': [100, 121, 144, 169],
            'gann_angles': [1, 2, 3, 4, 8],
            'min_data_points': 30
        }
        
        custom_gann = GannWheel(custom_config)
        result = custom_gann.analyze(self.test_data)
        
        self.assertIsInstance(result, dict)
        
        # 检查是否使用了自定义配置
        time_cycles = result['time_cycles']
        self.assertTrue(any(cycle['period'] in custom_config['time_cycles'] 
                          for cycle in time_cycles))
                          
    def test_data_validation(self):
        """测试数据验证"""
        # 测试缺少必要列的数据
        incomplete_data = self.test_data[['date', 'close']].copy()
        
        with self.assertRaises(KeyError):
            self.gann.analyze(incomplete_data)
            
    def test_performance_with_large_dataset(self):
        """测试大数据集性能"""
        # 创建更大的数据集（5年数据）
        large_dates = pd.date_range(start='2019-01-01', end='2023-12-31', freq='D')
        np.random.seed(42)
        
        large_prices = [10.0]
        for _ in range(len(large_dates) - 1):
            change = np.random.normal(0, 0.01)
            new_price = large_prices[-1] * (1 + change)
            large_prices.append(max(new_price, 0.1))
            
        large_data = pd.DataFrame({
            'date': large_dates,
            'open': large_prices,
            'high': [p * 1.02 for p in large_prices],
            'low': [p * 0.98 for p in large_prices],
            'close': large_prices,
            'volume': np.random.lognormal(10, 0.5, len(large_dates))
        })
        
        # 测试分析时间（应该在合理时间内完成）
        import time
        start_time = time.time()
        result = self.gann.analyze(large_data)
        end_time = time.time()
        
        self.assertIsInstance(result, dict)
        self.assertLess(end_time - start_time, 30)  # 应该在30秒内完成
        
    def test_result_consistency(self):
        """测试结果一致性"""
        # 多次运行相同数据应该得到相同结果
        result1 = self.gann.analyze(self.test_data)
        result2 = self.gann.analyze(self.test_data)
        
        # 比较关键数值结果
        self.assertEqual(len(result1['time_cycles']), len(result2['time_cycles']))
        self.assertEqual(len(result1['price_cycles']), len(result2['price_cycles']))
        

class TestGannWheelIntegration(unittest.TestCase):
    """江恩轮中轮集成测试类"""
    
    def setUp(self):
        """集成测试准备"""
        # 创建测试配置
        self.test_config = {
            'time_cycles': [7, 14, 21, 30, 45, 60, 90, 120, 180, 360],
            'price_angles': [15, 30, 45, 60, 75, 90, 105, 120, 135, 150, 165, 180],
            'square_size': 144,
            'tolerance': 0.02
        }
        
        self.gann = GannWheel(self.test_config)
        
        # 创建更真实的股价数据（模拟趋势）
        dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
        
        # 模拟上升趋势 + 随机波动
        base_price = 10.0
        trend = 0.0002  # 每日0.02%的上升趋势
        
        prices = []
        for i, date in enumerate(dates):
            trend_price = base_price * (1 + trend) ** i
            noise = np.random.normal(0, 0.015)  # 1.5%的随机波动
            daily_price = trend_price * (1 + noise)
            prices.append(max(daily_price, 0.1))
            
        self.realistic_data = pd.DataFrame({
            'date': dates,
            'open': prices,
            'high': [p * (1 + abs(np.random.normal(0, 0.008))) for p in prices],
            'low': [p * (1 - abs(np.random.normal(0, 0.008))) for p in prices],
            'close': prices,
            'volume': np.random.lognormal(12, 0.3, len(dates))
        })
        
        # 确保OHLC数据的逻辑关系
        for i in range(len(self.realistic_data)):
            high = max(self.realistic_data.loc[i, ['open', 'close']].max(), 
                      self.realistic_data.loc[i, 'high'])
            low = min(self.realistic_data.loc[i, ['open', 'close']].min(), 
                     self.realistic_data.loc[i, 'low'])
            self.realistic_data.loc[i, 'high'] = high
            self.realistic_data.loc[i, 'low'] = low
            
    def test_full_analysis_workflow(self):
        """测试完整分析工作流程"""
        result = self.gann.analyze(self.realistic_data)
        
        # 验证所有组件都正常工作
        self.assertIsInstance(result, dict)
        
        # 验证时间周期分析
        time_cycles = result['time_cycles']
        self.assertGreater(len(time_cycles), 0)
        
        # 验证价格轮回分析
        price_cycles = result['price_cycles']
        self.assertGreater(len(price_cycles), 0)
        
        # 验证支撑阻力位
        sr_levels = result['support_resistance']
        self.assertIn('support', sr_levels)
        self.assertIn('resistance', sr_levels)
        
        # 验证预测结果
        prediction = result['prediction']
        self.assertIn('trend_direction', prediction)
        self.assertIn('confidence_level', prediction)
        
    def test_trend_detection_accuracy(self):
        """测试趋势检测准确性"""
        result = self.gann.analyze(self.realistic_data)
        prediction = result['prediction']
        
        # 由于我们创建的是上升趋势数据，预测应该反映这一点
        trend_direction = prediction.get('trend_direction', 'neutral')
        
        # 在上升趋势中，应该检测到正向趋势
        self.assertIn(trend_direction.lower(), ['up', 'bullish', 'positive', 'rising'])
        
    def test_support_resistance_logic(self):
        """测试支撑阻力位逻辑"""
        result = self.gann.analyze(self.realistic_data)
        sr_levels = result['support_resistance']
        
        current_price = self.realistic_data['close'].iloc[-1]
        
        # 支撑位应该在当前价格下方
        support_levels = sr_levels.get('support', [])
        for support in support_levels:
            if isinstance(support, dict) and 'price' in support:
                self.assertLessEqual(support['price'], current_price * 1.01)  # 允许小误差
                
        # 阻力位应该在当前价格上方
        resistance_levels = sr_levels.get('resistance', [])
        for resistance in resistance_levels:
            if isinstance(resistance, dict) and 'price' in resistance:
                self.assertGreaterEqual(resistance['price'], current_price * 0.99)  # 允许小误差
                

if __name__ == '__main__':
    # 创建测试套件
    test_suite = unittest.TestSuite()
    
    # 添加单元测试
    test_suite.addTest(unittest.makeSuite(TestGannWheel))
    
    # 添加集成测试
    test_suite.addTest(unittest.makeSuite(TestGannWheelIntegration))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 输出测试结果摘要
    print(f"\n测试摘要:")
    print(f"运行测试: {result.testsRun}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print(f"成功率: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")