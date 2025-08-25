#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
江恩轮中轮分析模块

实现江恩轮中轮理论的核心算法，包括：
1. 时间轮回计算
2. 价格轮回计算
3. 时间价格共振分析
4. 关键支撑阻力位计算

Author: AI Assistant
Date: 2024
"""

import math
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from loguru import logger


class GannWheel:
    """
    江恩轮中轮分析器
    
    基于江恩理论实现时间和价格的轮回分析
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化江恩轮中轮分析器
        
        Args:
            config: 江恩分析配置参数
        """
        self.config = config
        
        # 基础参数
        self.time_cycles = config.get('time_cycles', [7, 14, 21, 30, 45, 60, 90, 120, 180, 360])
        self.price_angles = config.get('price_angles', [15, 30, 45, 60, 75, 90, 105, 120, 135, 150, 165, 180])
        self.square_size = config.get('square_size', 144)  # 江恩正方形大小
        self.tolerance = config.get('tolerance', 0.02)  # 容差范围
        
        logger.info("江恩轮中轮分析器初始化完成")
    
    def analyze_stock(self, symbol: str, data: pd.DataFrame) -> Dict[str, Any]:
        """
        对股票进行江恩轮中轮分析
        
        Args:
            symbol: 股票代码
            data: 股票数据DataFrame
            
        Returns:
            分析结果字典
        """
        try:
            logger.info(f"开始对 {symbol} 进行江恩轮中轮分析")
            
            # 基础数据准备
            if data.empty:
                raise ValueError("股票数据为空")
            
            # 确保数据按日期排序
            data = data.sort_index()
            
            # 分析结果容器
            analysis_result = {
                'symbol': symbol,
                'analysis_date': datetime.now(),
                'data_range': {
                    'start_date': data.index[0],
                    'end_date': data.index[-1],
                    'total_days': len(data)
                }
            }
            
            # 1. 时间轮回分析
            time_analysis = self._analyze_time_cycles(data)
            analysis_result['time_analysis'] = time_analysis
            
            # 2. 价格轮回分析
            price_analysis = self._analyze_price_cycles(data)
            analysis_result['price_analysis'] = price_analysis
            
            # 3. 江恩角度线分析
            angle_analysis = self._analyze_gann_angles(data)
            analysis_result['angle_analysis'] = angle_analysis
            
            # 4. 江恩正方形分析
            square_analysis = self._analyze_gann_square(data)
            analysis_result['square_analysis'] = square_analysis
            
            # 5. 时间价格共振分析
            resonance_analysis = self._analyze_time_price_resonance(data)
            analysis_result['resonance_analysis'] = resonance_analysis
            
            # 6. 关键位计算
            key_levels = self._calculate_key_levels(data)
            analysis_result['key_levels'] = key_levels
            
            # 7. 预测分析
            predictions = self._generate_predictions(data, analysis_result)
            analysis_result['predictions'] = predictions
            
            logger.info(f"{symbol} 江恩轮中轮分析完成")
            return analysis_result
            
        except Exception as e:
            logger.error(f"江恩轮中轮分析失败: {str(e)}")
            raise
    
    def _analyze_time_cycles(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        分析时间轮回周期
        
        Args:
            data: 股票数据
            
        Returns:
            时间轮回分析结果
        """
        try:
            # 寻找重要的高低点
            highs, lows = self._find_pivot_points(data)
            
            # 分析时间周期
            time_cycles_found = []
            
            for cycle in self.time_cycles:
                cycle_analysis = self._analyze_single_time_cycle(data, highs, lows, cycle)
                if cycle_analysis['strength'] > 0.3:  # 只保留强度较高的周期
                    time_cycles_found.append(cycle_analysis)
            
            # 按强度排序
            time_cycles_found.sort(key=lambda x: x['strength'], reverse=True)
            
            return {
                'cycles_found': time_cycles_found,
                'dominant_cycle': time_cycles_found[0] if time_cycles_found else None,
                'next_time_windows': self._calculate_next_time_windows(data, time_cycles_found)
            }
            
        except Exception as e:
            logger.error(f"时间轮回分析失败: {str(e)}")
            return {'cycles_found': [], 'dominant_cycle': None, 'next_time_windows': []}
    
    def _analyze_price_cycles(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        分析价格轮回周期
        
        Args:
            data: 股票数据
            
        Returns:
            价格轮回分析结果
        """
        try:
            # 计算价格波动范围
            price_range = data['High'].max() - data['Low'].min()
            price_center = (data['High'].max() + data['Low'].min()) / 2
            
            # 分析价格轮回
            price_cycles = []
            
            # 基于百分比的价格轮回
            for pct in [0.236, 0.382, 0.5, 0.618, 0.786, 1.0, 1.272, 1.618]:
                level = price_center + (price_range * pct / 2)
                level_low = price_center - (price_range * pct / 2)
                
                # 计算价格在这些水平附近的反应强度
                strength_high = self._calculate_price_level_strength(data, level)
                strength_low = self._calculate_price_level_strength(data, level_low)
                
                if strength_high > 0.2:
                    price_cycles.append({
                        'level': level,
                        'type': 'resistance',
                        'ratio': pct,
                        'strength': strength_high,
                        'touches': self._count_price_touches(data, level)
                    })
                
                if strength_low > 0.2:
                    price_cycles.append({
                        'level': level_low,
                        'type': 'support',
                        'ratio': pct,
                        'strength': strength_low,
                        'touches': self._count_price_touches(data, level_low)
                    })
            
            # 按强度排序
            price_cycles.sort(key=lambda x: x['strength'], reverse=True)
            
            return {
                'price_range': price_range,
                'price_center': price_center,
                'key_levels': price_cycles[:10],  # 取前10个最重要的价格水平
                'current_position': self._analyze_current_price_position(data, price_cycles)
            }
            
        except Exception as e:
            logger.error(f"价格轮回分析失败: {str(e)}")
            return {'price_range': 0, 'price_center': 0, 'key_levels': [], 'current_position': {}}
    
    def _analyze_gann_angles(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        分析江恩角度线
        
        Args:
            data: 股票数据
            
        Returns:
            江恩角度线分析结果
        """
        try:
            # 寻找重要的起始点（重要高低点）
            highs, lows = self._find_pivot_points(data)
            
            angle_lines = []
            
            # 从重要高低点绘制江恩角度线
            for point_type, points in [('high', highs), ('low', lows)]:
                for point in points[-5:]:  # 只分析最近的5个重要点
                    point_date = point['date']
                    point_price = point['price']
                    
                    # 计算各个角度的江恩线
                    for angle in self.price_angles:
                        angle_line = self._calculate_gann_angle_line(
                            data, point_date, point_price, angle, point_type
                        )
                        
                        if angle_line['strength'] > 0.3:
                            angle_lines.append(angle_line)
            
            # 按强度排序
            angle_lines.sort(key=lambda x: x['strength'], reverse=True)
            
            return {
                'angle_lines': angle_lines[:20],  # 取前20条最重要的角度线
                'current_angle_support': self._find_current_angle_support(data, angle_lines),
                'current_angle_resistance': self._find_current_angle_resistance(data, angle_lines)
            }
            
        except Exception as e:
            logger.error(f"江恩角度线分析失败: {str(e)}")
            return {'angle_lines': [], 'current_angle_support': None, 'current_angle_resistance': None}
    
    def _analyze_gann_square(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        分析江恩正方形
        
        Args:
            data: 股票数据
            
        Returns:
            江恩正方形分析结果
        """
        try:
            # 计算江恩正方形的基准价格
            current_price = data['Close'].iloc[-1]
            
            # 寻找最接近的江恩正方形中心
            square_root = math.sqrt(current_price)
            square_center = int(square_root) ** 2
            
            # 如果当前价格更接近下一个完全平方数
            if abs(current_price - (int(square_root) + 1) ** 2) < abs(current_price - square_center):
                square_center = (int(square_root) + 1) ** 2
            
            # 计算江恩正方形的关键价格位
            square_levels = self._calculate_gann_square_levels(square_center)
            
            # 分析当前价格在正方形中的位置
            current_position = self._analyze_square_position(current_price, square_levels)
            
            # 计算下一个重要的江恩正方形价格位
            next_levels = self._calculate_next_square_levels(current_price, square_levels)
            
            return {
                'square_center': square_center,
                'square_levels': square_levels,
                'current_position': current_position,
                'next_levels': next_levels,
                'square_strength': self._calculate_square_strength(data, square_levels)
            }
            
        except Exception as e:
            logger.error(f"江恩正方形分析失败: {str(e)}")
            return {'square_center': 0, 'square_levels': [], 'current_position': {}, 'next_levels': []}
    
    def _analyze_time_price_resonance(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        分析时间价格共振
        
        Args:
            data: 股票数据
            
        Returns:
            时间价格共振分析结果
        """
        try:
            resonance_points = []
            
            # 寻找时间和价格同时到达重要位置的点
            highs, lows = self._find_pivot_points(data)
            
            for point in highs + lows:
                point_date = point['date']
                point_price = point['price']
                
                # 检查时间共振
                time_resonance = self._check_time_resonance(data, point_date)
                
                # 检查价格共振
                price_resonance = self._check_price_resonance(data, point_price)
                
                # 计算综合共振强度
                total_resonance = (time_resonance['strength'] + price_resonance['strength']) / 2
                
                if total_resonance > 0.4:
                    resonance_points.append({
                        'date': point_date,
                        'price': point_price,
                        'type': point['type'],
                        'time_resonance': time_resonance,
                        'price_resonance': price_resonance,
                        'total_strength': total_resonance
                    })
            
            # 按共振强度排序
            resonance_points.sort(key=lambda x: x['total_strength'], reverse=True)
            
            # 预测下一个共振点
            next_resonance = self._predict_next_resonance(data, resonance_points)
            
            return {
                'resonance_points': resonance_points,
                'strongest_resonance': resonance_points[0] if resonance_points else None,
                'next_resonance_prediction': next_resonance
            }
            
        except Exception as e:
            logger.error(f"时间价格共振分析失败: {str(e)}")
            return {'resonance_points': [], 'strongest_resonance': None, 'next_resonance_prediction': None}
    
    def _calculate_key_levels(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        计算关键支撑阻力位
        
        Args:
            data: 股票数据
            
        Returns:
            关键位分析结果
        """
        try:
            current_price = data['Close'].iloc[-1]
            
            # 历史重要价格位
            historical_levels = self._find_historical_key_levels(data)
            
            # 江恩价格位
            gann_levels = self._calculate_gann_price_levels(data)
            
            # 斐波那契价格位
            fib_levels = self._calculate_fibonacci_levels(data)
            
            # 合并所有价格位并按重要性排序
            all_levels = historical_levels + gann_levels + fib_levels
            
            # 去重并按距离当前价格排序
            unique_levels = self._merge_similar_levels(all_levels)
            
            # 分类为支撑和阻力
            supports = [level for level in unique_levels if level['price'] < current_price]
            resistances = [level for level in unique_levels if level['price'] > current_price]
            
            # 按距离当前价格排序
            supports.sort(key=lambda x: current_price - x['price'])
            resistances.sort(key=lambda x: x['price'] - current_price)
            
            return {
                'current_price': current_price,
                'key_supports': supports[:5],  # 最近的5个支撑位
                'key_resistances': resistances[:5],  # 最近的5个阻力位
                'strongest_support': supports[0] if supports else None,
                'strongest_resistance': resistances[0] if resistances else None
            }
            
        except Exception as e:
            logger.error(f"关键位计算失败: {str(e)}")
            return {'current_price': 0, 'key_supports': [], 'key_resistances': [], 
                   'strongest_support': None, 'strongest_resistance': None}
    
    def _generate_predictions(self, data: pd.DataFrame, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成预测分析
        
        Args:
            data: 股票数据
            analysis_result: 分析结果
            
        Returns:
            预测分析结果
        """
        try:
            current_price = data['Close'].iloc[-1]
            current_date = data.index[-1]
            
            # 基于时间周期的预测
            time_predictions = self._predict_by_time_cycles(data, analysis_result.get('time_analysis', {}))
            
            # 基于价格轮回的预测
            price_predictions = self._predict_by_price_cycles(data, analysis_result.get('price_analysis', {}))
            
            # 基于江恩角度线的预测
            angle_predictions = self._predict_by_gann_angles(data, analysis_result.get('angle_analysis', {}))
            
            # 综合预测
            combined_prediction = self._combine_predictions(time_predictions, price_predictions, angle_predictions)
            
            return {
                'current_price': current_price,
                'current_date': current_date,
                'time_predictions': time_predictions,
                'price_predictions': price_predictions,
                'angle_predictions': angle_predictions,
                'combined_prediction': combined_prediction,
                'confidence_level': self._calculate_prediction_confidence(combined_prediction)
            }
            
        except Exception as e:
            logger.error(f"预测分析失败: {str(e)}")
            return {'current_price': 0, 'current_date': None, 'combined_prediction': {}}
    
    # 辅助方法实现
    def _find_pivot_points(self, data: pd.DataFrame, window: int = 5) -> Tuple[List[Dict], List[Dict]]:
        """
        寻找重要的高低点
        
        Args:
            data: 股票数据
            window: 窗口大小
            
        Returns:
            (高点列表, 低点列表)
        """
        highs = []
        lows = []
        
        for i in range(window, len(data) - window):
            # 检查是否为局部高点
            if all(data['High'].iloc[i] >= data['High'].iloc[i-j] for j in range(1, window+1)) and \
               all(data['High'].iloc[i] >= data['High'].iloc[i+j] for j in range(1, window+1)):
                highs.append({
                    'date': data.index[i],
                    'price': data['High'].iloc[i],
                    'type': 'high',
                    'index': i
                })
            
            # 检查是否为局部低点
            if all(data['Low'].iloc[i] <= data['Low'].iloc[i-j] for j in range(1, window+1)) and \
               all(data['Low'].iloc[i] <= data['Low'].iloc[i+j] for j in range(1, window+1)):
                lows.append({
                    'date': data.index[i],
                    'price': data['Low'].iloc[i],
                    'type': 'low',
                    'index': i
                })
        
        return highs, lows
    
    def _analyze_single_time_cycle(self, data: pd.DataFrame, highs: List[Dict], 
                                 lows: List[Dict], cycle: int) -> Dict[str, Any]:
        """
        分析单个时间周期
        
        Args:
            data: 股票数据
            highs: 高点列表
            lows: 低点列表
            cycle: 时间周期
            
        Returns:
            周期分析结果
        """
        matches = 0
        total_points = len(highs) + len(lows)
        
        if total_points == 0:
            return {'cycle': cycle, 'strength': 0, 'matches': 0}
        
        # 检查高低点之间的时间间隔是否符合周期
        all_points = sorted(highs + lows, key=lambda x: x['date'])
        
        for i in range(1, len(all_points)):
            time_diff = (all_points[i]['date'] - all_points[i-1]['date']).days
            
            # 检查是否接近目标周期（允许一定容差）
            if abs(time_diff - cycle) <= cycle * self.tolerance:
                matches += 1
        
        strength = matches / max(total_points - 1, 1)
        
        return {
            'cycle': cycle,
            'strength': strength,
            'matches': matches,
            'total_intervals': total_points - 1
        }
    
    def _calculate_next_time_windows(self, data: pd.DataFrame, cycles: List[Dict]) -> List[Dict]:
        """
        计算下一个时间窗口
        
        Args:
            data: 股票数据
            cycles: 时间周期列表
            
        Returns:
            下一个时间窗口列表
        """
        if not cycles:
            return []
        
        current_date = data.index[-1]
        time_windows = []
        
        for cycle_info in cycles[:3]:  # 只考虑前3个最强的周期
            cycle = cycle_info['cycle']
            next_date = current_date + timedelta(days=cycle)
            
            time_windows.append({
                'cycle': cycle,
                'next_date': next_date,
                'strength': cycle_info['strength'],
                'days_ahead': cycle
            })
        
        return time_windows
    
    def _calculate_price_level_strength(self, data: pd.DataFrame, level: float) -> float:
        """
        计算价格水平的强度
        
        Args:
            data: 股票数据
            level: 价格水平
            
        Returns:
            强度值
        """
        tolerance_range = level * self.tolerance
        touches = 0
        
        for _, row in data.iterrows():
            # 检查高点是否触及该水平
            if abs(row['High'] - level) <= tolerance_range:
                touches += 1
            # 检查低点是否触及该水平
            elif abs(row['Low'] - level) <= tolerance_range:
                touches += 1
        
        # 强度 = 触及次数 / 总天数
        return min(touches / len(data), 1.0)
    
    def _count_price_touches(self, data: pd.DataFrame, level: float) -> int:
        """
        计算价格触及某水平的次数
        
        Args:
            data: 股票数据
            level: 价格水平
            
        Returns:
            触及次数
        """
        tolerance_range = level * self.tolerance
        touches = 0
        
        for _, row in data.iterrows():
            if (row['Low'] <= level + tolerance_range and 
                row['High'] >= level - tolerance_range):
                touches += 1
        
        return touches
    
    def _analyze_current_price_position(self, data: pd.DataFrame, price_cycles: List[Dict]) -> Dict[str, Any]:
        """
        分析当前价格位置
        
        Args:
            data: 股票数据
            price_cycles: 价格周期列表
            
        Returns:
            当前价格位置分析
        """
        current_price = data['Close'].iloc[-1]
        
        # 找到最近的支撑和阻力位
        nearest_support = None
        nearest_resistance = None
        
        for level_info in price_cycles:
            level = level_info['level']
            
            if level < current_price and (nearest_support is None or level > nearest_support['level']):
                nearest_support = level_info
            elif level > current_price and (nearest_resistance is None or level < nearest_resistance['level']):
                nearest_resistance = level_info
        
        return {
            'current_price': current_price,
            'nearest_support': nearest_support,
            'nearest_resistance': nearest_resistance,
            'support_distance': (current_price - nearest_support['level']) / current_price if nearest_support else None,
            'resistance_distance': (nearest_resistance['level'] - current_price) / current_price if nearest_resistance else None
        }
    
    def _calculate_gann_angle_line(self, data: pd.DataFrame, start_date: datetime, 
                                 start_price: float, angle: float, point_type: str) -> Dict[str, Any]:
        """
        计算江恩角度线
        
        Args:
            data: 股票数据
            start_date: 起始日期
            start_price: 起始价格
            angle: 角度
            point_type: 点类型（high/low）
            
        Returns:
            角度线信息
        """
        # 计算角度线的斜率
        angle_rad = math.radians(angle)
        
        # 江恩角度线的基本斜率计算
        if angle == 45:  # 1x1线
            slope = 1 if point_type == 'low' else -1
        elif angle == 26.25:  # 2x1线
            slope = 2 if point_type == 'low' else -2
        elif angle == 63.75:  # 1x2线
            slope = 0.5 if point_type == 'low' else -0.5
        else:
            # 其他角度的近似计算
            slope = math.tan(angle_rad) if point_type == 'low' else -math.tan(angle_rad)
        
        # 计算角度线上的价格点
        line_points = []
        strength = 0
        touches = 0
        
        start_index = data.index.get_loc(start_date) if start_date in data.index else 0
        
        for i in range(start_index + 1, len(data)):
            days_diff = i - start_index
            predicted_price = start_price + (slope * days_diff * start_price * 0.01)  # 按百分比调整
            
            actual_high = data['High'].iloc[i]
            actual_low = data['Low'].iloc[i]
            
            # 检查价格是否触及角度线
            tolerance_range = predicted_price * self.tolerance
            
            if (actual_low <= predicted_price + tolerance_range and 
                actual_high >= predicted_price - tolerance_range):
                touches += 1
                line_points.append({
                    'date': data.index[i],
                    'predicted_price': predicted_price,
                    'actual_price': (actual_high + actual_low) / 2
                })
        
        # 计算角度线强度
        if len(data) - start_index > 0:
            strength = touches / (len(data) - start_index)
        
        return {
            'start_date': start_date,
            'start_price': start_price,
            'angle': angle,
            'point_type': point_type,
            'slope': slope,
            'strength': strength,
            'touches': touches,
            'line_points': line_points
        }
    
    def _find_current_angle_support(self, data: pd.DataFrame, angle_lines: List[Dict]) -> Optional[Dict]:
        """
        寻找当前的角度线支撑
        
        Args:
            data: 股票数据
            angle_lines: 角度线列表
            
        Returns:
            当前角度线支撑
        """
        current_price = data['Close'].iloc[-1]
        current_date = data.index[-1]
        
        best_support = None
        min_distance = float('inf')
        
        for line in angle_lines:
            if line['point_type'] == 'low':  # 只考虑从低点出发的上升角度线
                # 计算当前日期在角度线上的价格
                start_date = line['start_date']
                start_price = line['start_price']
                slope = line['slope']
                
                if current_date > start_date:
                    days_diff = (current_date - start_date).days
                    line_price = start_price + (slope * days_diff * start_price * 0.01)
                    
                    # 如果角度线价格低于当前价格，可能是支撑
                    if line_price < current_price:
                        distance = current_price - line_price
                        if distance < min_distance:
                            min_distance = distance
                            best_support = {
                                'line_info': line,
                                'support_price': line_price,
                                'distance': distance,
                                'distance_pct': distance / current_price
                            }
        
        return best_support
    
    def _find_current_angle_resistance(self, data: pd.DataFrame, angle_lines: List[Dict]) -> Optional[Dict]:
        """
        寻找当前的角度线阻力
        
        Args:
            data: 股票数据
            angle_lines: 角度线列表
            
        Returns:
            当前角度线阻力
        """
        current_price = data['Close'].iloc[-1]
        current_date = data.index[-1]
        
        best_resistance = None
        min_distance = float('inf')
        
        for line in angle_lines:
            if line['point_type'] == 'high':  # 只考虑从高点出发的下降角度线
                # 计算当前日期在角度线上的价格
                start_date = line['start_date']
                start_price = line['start_price']
                slope = line['slope']
                
                if current_date > start_date:
                    days_diff = (current_date - start_date).days
                    line_price = start_price + (slope * days_diff * start_price * 0.01)
                    
                    # 如果角度线价格高于当前价格，可能是阻力
                    if line_price > current_price:
                        distance = line_price - current_price
                        if distance < min_distance:
                            min_distance = distance
                            best_resistance = {
                                'line_info': line,
                                'resistance_price': line_price,
                                'distance': distance,
                                'distance_pct': distance / current_price
                            }
        
        return best_resistance
    
    def _calculate_gann_square_levels(self, center: float) -> List[Dict]:
        """
        计算江恩正方形的关键价格位
        
        Args:
            center: 正方形中心价格
            
        Returns:
            关键价格位列表
        """
        levels = []
        
        # 江恩正方形的基本结构
        square_root = math.sqrt(center)
        
        # 计算正方形的各个重要价格位
        for i in range(-2, 3):  # 中心前后各2个正方形
            base = (square_root + i) ** 2
            
            # 正方形的关键分割点
            divisions = [0, 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875, 1.0]
            
            for div in divisions:
                if i == 0:  # 当前正方形
                    next_square = (square_root + 1) ** 2
                    level_price = base + (next_square - base) * div
                else:
                    next_square = (square_root + i + 1) ** 2
                    level_price = base + (next_square - base) * div
                
                levels.append({
                    'price': level_price,
                    'square_level': i,
                    'division': div,
                    'type': 'gann_square'
                })
        
        return sorted(levels, key=lambda x: x['price'])
    
    def _analyze_square_position(self, current_price: float, square_levels: List[Dict]) -> Dict[str, Any]:
        """
        分析当前价格在江恩正方形中的位置
        
        Args:
            current_price: 当前价格
            square_levels: 正方形价格位列表
            
        Returns:
            位置分析结果
        """
        # 找到当前价格所在的正方形区间
        for i, level in enumerate(square_levels):
            if level['price'] > current_price:
                if i > 0:
                    lower_level = square_levels[i-1]
                    upper_level = level
                    
                    # 计算在区间中的位置
                    position_pct = (current_price - lower_level['price']) / (upper_level['price'] - lower_level['price'])
                    
                    return {
                        'current_price': current_price,
                        'lower_level': lower_level,
                        'upper_level': upper_level,
                        'position_pct': position_pct,
                        'square_level': lower_level['square_level']
                    }
                break
        
        return {'current_price': current_price, 'position_pct': 0}
    
    def _calculate_next_square_levels(self, current_price: float, square_levels: List[Dict]) -> List[Dict]:
        """
        计算下一个重要的江恩正方形价格位
        
        Args:
            current_price: 当前价格
            square_levels: 正方形价格位列表
            
        Returns:
            下一个重要价格位列表
        """
        next_levels = []
        
        # 找到当前价格附近的重要价格位
        for level in square_levels:
            distance = abs(level['price'] - current_price)
            distance_pct = distance / current_price
            
            # 只考虑距离在合理范围内的价格位
            if 0.01 <= distance_pct <= 0.2:  # 1%到20%的距离
                next_levels.append({
                    'price': level['price'],
                    'distance': distance,
                    'distance_pct': distance_pct,
                    'direction': 'up' if level['price'] > current_price else 'down',
                    'square_info': level
                })
        
        # 按距离排序
        next_levels.sort(key=lambda x: x['distance'])
        
        return next_levels[:5]  # 返回最近的5个价格位
    
    def _calculate_square_strength(self, data: pd.DataFrame, square_levels: List[Dict]) -> float:
        """
        计算江恩正方形的整体强度
        
        Args:
            data: 股票数据
            square_levels: 正方形价格位列表
            
        Returns:
            强度值
        """
        total_touches = 0
        total_levels = len(square_levels)
        
        for level_info in square_levels:
            level = level_info['price']
            touches = self._count_price_touches(data, level)
            total_touches += touches
        
        # 平均每个价格位的触及次数
        avg_touches = total_touches / max(total_levels, 1)
        
        # 强度 = 平均触及次数 / 总天数
        return min(avg_touches / len(data), 1.0)
    
    def _check_time_resonance(self, data: pd.DataFrame, target_date: datetime) -> Dict[str, Any]:
        """
        检查时间共振
        
        Args:
            data: 股票数据
            target_date: 目标日期
            
        Returns:
            时间共振分析结果
        """
        resonance_strength = 0
        matching_cycles = []
        
        # 检查各个时间周期是否在目标日期附近有重要点
        for cycle in self.time_cycles:
            # 寻找距离目标日期约为cycle天数的重要点
            tolerance_days = max(cycle * self.tolerance, 1)
            
            for i, date in enumerate(data.index):
                time_diff = abs((date - target_date).days)
                
                if abs(time_diff - cycle) <= tolerance_days:
                    resonance_strength += 1 / len(self.time_cycles)
                    matching_cycles.append({
                        'cycle': cycle,
                        'date': date,
                        'time_diff': time_diff
                    })
                    break
        
        return {
            'strength': resonance_strength,
            'matching_cycles': matching_cycles
        }
    
    def _check_price_resonance(self, data: pd.DataFrame, target_price: float) -> Dict[str, Any]:
        """
        检查价格共振
        
        Args:
            data: 股票数据
            target_price: 目标价格
            
        Returns:
            价格共振分析结果
        """
        # 计算目标价格的强度
        strength = self._calculate_price_level_strength(data, target_price)
        touches = self._count_price_touches(data, target_price)
        
        # 检查是否为江恩正方形价格位
        square_levels = self._calculate_gann_square_levels(target_price)
        is_gann_level = any(abs(level['price'] - target_price) / target_price < self.tolerance 
                           for level in square_levels)
        
        return {
            'strength': strength,
            'touches': touches,
            'is_gann_level': is_gann_level
        }
    
    def _predict_next_resonance(self, data: pd.DataFrame, resonance_points: List[Dict]) -> Optional[Dict]:
        """
        预测下一个共振点
        
        Args:
            data: 股票数据
            resonance_points: 历史共振点
            
        Returns:
            下一个共振点预测
        """
        if len(resonance_points) < 2:
            return None
        
        current_date = data.index[-1]
        current_price = data['Close'].iloc[-1]
        
        # 基于历史共振点的时间间隔预测
        time_intervals = []
        for i in range(1, len(resonance_points)):
            interval = (resonance_points[i-1]['date'] - resonance_points[i]['date']).days
            time_intervals.append(interval)
        
        if time_intervals:
            avg_interval = sum(time_intervals) / len(time_intervals)
            next_date = current_date + timedelta(days=int(avg_interval))
            
            # 基于江恩理论预测价格
            price_change_pct = 0.1  # 假设10%的价格变化
            next_price_up = current_price * (1 + price_change_pct)
            next_price_down = current_price * (1 - price_change_pct)
            
            return {
                'predicted_date': next_date,
                'days_ahead': int(avg_interval),
                'predicted_price_up': next_price_up,
                'predicted_price_down': next_price_down,
                'confidence': min(len(resonance_points) / 10, 1.0)  # 基于历史数据量的置信度
            }
        
        return None
    
    def _find_historical_key_levels(self, data: pd.DataFrame) -> List[Dict]:
        """
        寻找历史关键价格位
        
        Args:
            data: 股票数据
            
        Returns:
            历史关键价格位列表
        """
        levels = []
        
        # 历史最高价和最低价
        max_price = data['High'].max()
        min_price = data['Low'].min()
        
        levels.extend([
            {'price': max_price, 'type': 'historical_high', 'strength': 1.0},
            {'price': min_price, 'type': 'historical_low', 'strength': 1.0}
        ])
        
        # 重要的高低点
        highs, lows = self._find_pivot_points(data)
        
        for high in highs[-10:]:  # 最近10个高点
            strength = self._calculate_price_level_strength(data, high['price'])
            if strength > 0.1:
                levels.append({
                    'price': high['price'],
                    'type': 'pivot_high',
                    'strength': strength,
                    'date': high['date']
                })
        
        for low in lows[-10:]:  # 最近10个低点
            strength = self._calculate_price_level_strength(data, low['price'])
            if strength > 0.1:
                levels.append({
                    'price': low['price'],
                    'type': 'pivot_low',
                    'strength': strength,
                    'date': low['date']
                })
        
        return levels
    
    def _calculate_gann_price_levels(self, data: pd.DataFrame) -> List[Dict]:
        """
        计算江恩价格位
        
        Args:
            data: 股票数据
            
        Returns:
            江恩价格位列表
        """
        current_price = data['Close'].iloc[-1]
        square_levels = self._calculate_gann_square_levels(current_price)
        
        gann_levels = []
        for level_info in square_levels:
            strength = self._calculate_price_level_strength(data, level_info['price'])
            if strength > 0.05:  # 只保留有一定强度的价格位
                gann_levels.append({
                    'price': level_info['price'],
                    'type': 'gann_square',
                    'strength': strength,
                    'square_info': level_info
                })
        
        return gann_levels
    
    def _calculate_fibonacci_levels(self, data: pd.DataFrame) -> List[Dict]:
        """
        计算斐波那契价格位
        
        Args:
            data: 股票数据
            
        Returns:
            斐波那契价格位列表
        """
        # 寻找最近的重要高低点
        highs, lows = self._find_pivot_points(data)
        
        if not highs or not lows:
            return []
        
        # 使用最近的高低点计算斐波那契回调位
        recent_high = max(highs[-3:], key=lambda x: x['price']) if len(highs) >= 3 else highs[-1]
        recent_low = min(lows[-3:], key=lambda x: x['price']) if len(lows) >= 3 else lows[-1]
        
        price_range = recent_high['price'] - recent_low['price']
        
        fib_ratios = [0.236, 0.382, 0.5, 0.618, 0.786]
        fib_levels = []
        
        for ratio in fib_ratios:
            # 从高点回调
            retracement_price = recent_high['price'] - (price_range * ratio)
            strength = self._calculate_price_level_strength(data, retracement_price)
            
            if strength > 0.05:
                fib_levels.append({
                    'price': retracement_price,
                    'type': 'fibonacci_retracement',
                    'strength': strength,
                    'ratio': ratio,
                    'base_high': recent_high['price'],
                    'base_low': recent_low['price']
                })
        
        return fib_levels
    
    def _merge_similar_levels(self, levels: List[Dict]) -> List[Dict]:
        """
        合并相似的价格位
        
        Args:
            levels: 价格位列表
            
        Returns:
            合并后的价格位列表
        """
        if not levels:
            return []
        
        # 按价格排序
        sorted_levels = sorted(levels, key=lambda x: x['price'])
        merged_levels = []
        
        current_group = [sorted_levels[0]]
        
        for i in range(1, len(sorted_levels)):
            current_level = sorted_levels[i]
            last_in_group = current_group[-1]
            
            # 如果价格相近，合并到同一组
            if abs(current_level['price'] - last_in_group['price']) / last_in_group['price'] < self.tolerance:
                current_group.append(current_level)
            else:
                # 处理当前组
                merged_level = self._merge_level_group(current_group)
                merged_levels.append(merged_level)
                current_group = [current_level]
        
        # 处理最后一组
        if current_group:
            merged_level = self._merge_level_group(current_group)
            merged_levels.append(merged_level)
        
        return merged_levels
    
    def _merge_level_group(self, group: List[Dict]) -> Dict:
        """
        合并一组相似的价格位
        
        Args:
            group: 价格位组
            
        Returns:
            合并后的价格位
        """
        # 计算平均价格
        avg_price = sum(level['price'] for level in group) / len(group)
        
        # 计算总强度
        total_strength = sum(level['strength'] for level in group) / len(group)
        
        # 合并类型
        types = list(set(level['type'] for level in group))
        
        return {
            'price': avg_price,
            'type': types[0] if len(types) == 1 else 'combined',
            'strength': total_strength,
            'count': len(group),
            'original_types': types
        }
    
    def _predict_by_time_cycles(self, data: pd.DataFrame, time_analysis: Dict) -> Dict[str, Any]:
        """
        基于时间周期进行预测
        
        Args:
            data: 股票数据
            time_analysis: 时间分析结果
            
        Returns:
            时间周期预测结果
        """
        predictions = []
        
        time_windows = time_analysis.get('next_time_windows', [])
        
        for window in time_windows:
            predictions.append({
                'type': 'time_cycle',
                'target_date': window['next_date'],
                'cycle_days': window['cycle'],
                'strength': window['strength'],
                'prediction': 'potential_turning_point'
            })
        
        return {
            'predictions': predictions,
            'dominant_cycle': time_analysis.get('dominant_cycle')
        }
    
    def _predict_by_price_cycles(self, data: pd.DataFrame, price_analysis: Dict) -> Dict[str, Any]:
        """
        基于价格轮回进行预测
        
        Args:
            data: 股票数据
            price_analysis: 价格分析结果
            
        Returns:
            价格轮回预测结果
        """
        current_price = data['Close'].iloc[-1]
        key_levels = price_analysis.get('key_levels', [])
        
        predictions = []
        
        # 预测价格目标
        for level in key_levels[:5]:  # 取前5个重要价格位
            if level['type'] == 'resistance' and level['level'] > current_price:
                predictions.append({
                    'type': 'price_target',
                    'target_price': level['level'],
                    'direction': 'up',
                    'strength': level['strength'],
                    'distance_pct': (level['level'] - current_price) / current_price
                })
            elif level['type'] == 'support' and level['level'] < current_price:
                predictions.append({
                    'type': 'price_target',
                    'target_price': level['level'],
                    'direction': 'down',
                    'strength': level['strength'],
                    'distance_pct': (current_price - level['level']) / current_price
                })
        
        return {
            'predictions': predictions,
            'current_position': price_analysis.get('current_position')
        }
    
    def _predict_by_gann_angles(self, data: pd.DataFrame, angle_analysis: Dict) -> Dict[str, Any]:
        """
        基于江恩角度线进行预测
        
        Args:
            data: 股票数据
            angle_analysis: 角度线分析结果
            
        Returns:
            角度线预测结果
        """
        predictions = []
        
        current_support = angle_analysis.get('current_angle_support')
        current_resistance = angle_analysis.get('current_angle_resistance')
        
        if current_support:
            predictions.append({
                'type': 'angle_support',
                'target_price': current_support['support_price'],
                'direction': 'support',
                'strength': current_support['line_info']['strength'],
                'distance_pct': current_support['distance_pct']
            })
        
        if current_resistance:
            predictions.append({
                'type': 'angle_resistance',
                'target_price': current_resistance['resistance_price'],
                'direction': 'resistance',
                'strength': current_resistance['line_info']['strength'],
                'distance_pct': current_resistance['distance_pct']
            })
        
        return {
            'predictions': predictions,
            'current_support': current_support,
            'current_resistance': current_resistance
        }
    
    def _combine_predictions(self, time_pred: Dict, price_pred: Dict, angle_pred: Dict) -> Dict[str, Any]:
        """
        综合各种预测结果
        
        Args:
            time_pred: 时间预测
            price_pred: 价格预测
            angle_pred: 角度线预测
            
        Returns:
            综合预测结果
        """
        all_predictions = []
        
        # 收集所有预测
        all_predictions.extend(time_pred.get('predictions', []))
        all_predictions.extend(price_pred.get('predictions', []))
        all_predictions.extend(angle_pred.get('predictions', []))
        
        # 按强度排序
        all_predictions.sort(key=lambda x: x.get('strength', 0), reverse=True)
        
        # 寻找最强的预测
        strongest_prediction = all_predictions[0] if all_predictions else None
        
        # 计算综合趋势 - 修复字段匹配问题
        up_strength = sum(p.get('strength', 0) for p in all_predictions 
                         if p.get('direction') in ['up', 'resistance'] or p.get('type') == 'resistance')
        down_strength = sum(p.get('strength', 0) for p in all_predictions 
                           if p.get('direction') in ['down', 'support'] or p.get('type') == 'support')
        
        # 如果没有明确的方向预测，基于价格目标计算趋势
        if up_strength == 0 and down_strength == 0 and all_predictions:
            current_price = getattr(self, '_current_price', 0)
            for pred in all_predictions:
                target_price = pred.get('target_price')
                if target_price and current_price > 0:
                    if target_price > current_price:
                        up_strength += pred.get('strength', 0.5)
                    else:
                        down_strength += pred.get('strength', 0.5)
        
        overall_trend = 'neutral'
        direction = 'neutral'
        target_price = None
        
        if up_strength > down_strength * 1.2:
            overall_trend = 'bullish'
            direction = '上涨'
        elif down_strength > up_strength * 1.2:
            overall_trend = 'bearish'
            direction = '下跌'
        
        # 获取目标价位
        if strongest_prediction:
            target_price = strongest_prediction.get('target_price')
        
        return {
            'all_predictions': all_predictions[:10],  # 取前10个预测
            'strongest_prediction': strongest_prediction,
            'overall_trend': overall_trend,
            'direction': direction,
            'target_price': target_price,
            'trend_strength': max(up_strength, down_strength),
            'up_strength': up_strength,
            'down_strength': down_strength
        }
    
    def _calculate_prediction_confidence(self, combined_prediction: Dict) -> float:
        """
        计算预测置信度
        
        Args:
            combined_prediction: 综合预测结果
            
        Returns:
            置信度值
        """
        predictions = combined_prediction.get('all_predictions', [])
        
        if not predictions:
            return 0.0
        
        # 基于预测数量和强度计算置信度
        total_strength = sum(p.get('strength', 0) for p in predictions)
        avg_strength = total_strength / len(predictions)
        
        # 考虑预测的一致性
        trend_strength = combined_prediction.get('trend_strength', 0)
        
        # 综合置信度
        confidence = min((avg_strength + trend_strength) / 2, 1.0)
        
        return confidence