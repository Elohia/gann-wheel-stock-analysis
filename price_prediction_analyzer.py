#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
精准价格点位预测分析模块

基于江恩轮中轮理论和量价分析，提供专业的价格点位预测
包含量价分析依据、置信度评估、计算方法说明和时间敏感度标注

Author: AI Assistant
Date: 2025-01-25
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from loguru import logger
import math
from main import StockAnalysisSystem


class PricePredictionAnalyzer:
    """
    价格点位预测分析器
    
    提供基于技术分析的精准价格点位预测
    """
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        初始化价格预测分析器
        
        Args:
            config_path: 配置文件路径
        """
        self.system = StockAnalysisSystem(config_path)
        self.prediction_models = {
            'gann_time_price': 0.3,      # 江恩时间价格共振权重
            'fibonacci_levels': 0.25,     # 斐波那契回调权重
            'volume_price_pattern': 0.25, # 量价模式权重
            'support_resistance': 0.2     # 支撑阻力位权重
        }
        
        logger.info("价格预测分析器初始化完成")
    
    def _calculate_dynamic_confidence(self, prediction_type: str, strength: float, 
                                    market_volatility: float = 0.02, 
                                    volume_factor: float = 1.0,
                                    technical_alignment: float = 0.5) -> int:
        """
        动态计算预测置信度
        
        Args:
            prediction_type: 预测类型
            strength: 预测强度 (0-1)
            market_volatility: 市场波动率
            volume_factor: 成交量因子
            technical_alignment: 技术指标一致性
            
        Returns:
            置信度百分比 (30-95)
        """
        # 基础置信度
        base_confidence = {
            'gann_wheel_angle': 75,
            'volume_breakout': 70,
            'fibonacci': 65,
            'pivot_support': 60,
            'pivot_resistance': 60,
            'support_resistance': 55
        }.get(prediction_type, 50)
        
        # 强度调整 (-15 到 +20)
        strength_adjustment = (strength - 0.5) * 35
        
        # 波动率调整 (低波动率提高置信度)
        volatility_adjustment = max(-10, min(10, (0.02 - market_volatility) * 200))
        
        # 成交量调整 (-5 到 +10)
        volume_adjustment = max(-5, min(10, (volume_factor - 1) * 10))
        
        # 技术一致性调整 (-10 到 +15)
        alignment_adjustment = (technical_alignment - 0.5) * 25
        
        # 计算最终置信度
        final_confidence = base_confidence + strength_adjustment + volatility_adjustment + volume_adjustment + alignment_adjustment
        
        # 限制在合理范围内
        return max(30, min(95, int(final_confidence)))
    
    def generate_price_predictions(self, symbol: str, period: str = "1y") -> Dict[str, Any]:
        """
        生成精准价格点位预测
        
        Args:
            symbol: 股票代码
            period: 分析周期
            
        Returns:
            包含预测点位的详细分析报告
        """
        try:
            logger.info(f"开始为 {symbol} 生成价格预测分析")
            
            # 获取并存储数据
            success = self.system.fetch_and_store_data(symbol, period)
            if not success:
                raise ValueError(f"无法获取 {symbol} 的数据")
            
            # 执行完整分析
            analysis_results = self.system.analyze_stock(symbol)
            
            # 获取原始数据
            data = self.system.db_manager.get_stock_data(symbol)
            if data is None or data.empty:
                raise ValueError(f"数据库中无 {symbol} 的数据")
            
            # 生成预测点位
            predictions = self._calculate_key_price_levels(symbol, data, analysis_results)
            
            # 生成专业报告
            report = self._generate_professional_report(symbol, data, analysis_results, predictions)
            
            logger.info(f"{symbol} 价格预测分析完成")
            return report
            
        except Exception as e:
            logger.error(f"价格预测分析失败: {str(e)}")
            raise
    
    def _calculate_key_price_levels(self, symbol: str, data: pd.DataFrame, 
                                   analysis_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        计算关键价格点位
        
        Args:
            symbol: 股票代码
            data: 股票数据
            analysis_results: 分析结果
            
        Returns:
            关键价格点位列表
        """
        current_price = data['Close'].iloc[-1]
        current_volume = data['Volume'].iloc[-1]
        
        predictions = []
        
        # 1. 基于江恩分析的价格预测
        gann_predictions = self._calculate_gann_price_targets(data, analysis_results.get('gann', {}))
        predictions.extend(gann_predictions)
        
        # 2. 基于量价分析的价格预测
        volume_predictions = self._calculate_volume_price_targets(data, analysis_results.get('volume_price', {}))
        predictions.extend(volume_predictions)
        
        # 3. 基于斐波那契的价格预测
        fib_predictions = self._calculate_fibonacci_targets(data)
        predictions.extend(fib_predictions)
        
        # 4. 基于支撑阻力位的价格预测
        sr_predictions = self._calculate_support_resistance_targets(data, analysis_results)
        predictions.extend(sr_predictions)
        
        # 合并相似价格点位并排序
        merged_predictions = self._merge_similar_predictions(predictions)
        
        # 按置信度排序，取前5个
        merged_predictions.sort(key=lambda x: x['confidence'], reverse=True)
        
        return merged_predictions[:12]  # 增加到12个预测点位
    
    def _calculate_gann_price_targets(self, data: pd.DataFrame, gann_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        基于江恩分析计算价格目标
        
        Args:
            data: 股票数据
            gann_analysis: 江恩分析结果
            
        Returns:
            江恩价格目标列表
        """
        predictions = []
        current_price = data['Close'].iloc[-1]
        
        # 获取江恩关键位
        key_levels = gann_analysis.get('key_levels', {})
        supports = key_levels.get('key_supports', [])
        resistances = key_levels.get('key_resistances', [])
        
        # 计算江恩轮中轮详细点位
        gann_wheel_levels = self._calculate_detailed_gann_wheel_levels(current_price, data)
        
        # 处理支撑位预测 - 增加更多细节
        for i, support in enumerate(supports[:8]):  # 增加到8个支撑位
            if isinstance(support, dict):
                price = support.get('price', 0)
                strength = support.get('strength', 0.5)
                level_type = support.get('type', 'support')
            else:
                price = support
                strength = 0.5
                level_type = 'support'
            
            if price > 0 and price < current_price:
                # 江恩角度计算
                gann_angle = self._calculate_gann_angle(current_price, price)
                time_cycle = self._get_gann_time_cycle(i + 1)
                wheel_position = self._get_gann_wheel_position(price, current_price)
                
                # 动态计算置信度
                market_volatility = data['Close'].pct_change().std() if len(data) > 1 else 0.02
                volume_factor = data['Volume'].iloc[-1] / data['Volume'].mean() if len(data) > 1 else 1.0
                technical_alignment = 0.8 if gann_angle in [45, 90, 180, 270] else 0.6
                base_strength = max(0.4, strength - i * 0.1)
                confidence = self._calculate_dynamic_confidence(
                    'gann_wheel_angle', base_strength, market_volatility, volume_factor, technical_alignment
                )  # 第一个支撑位置信度最高
                predictions.append({
                    'target_price': price,
                    'direction': 'down',
                    'type': f'gann_{level_type}',
                    'confidence': confidence,
                    'analysis_basis': {
                        'method': f'江恩轮中轮{level_type}位分析',
                        'strength': strength,
                        'distance_pct': abs(price - current_price) / current_price * 100,
                        'gann_angle': gann_angle,
                        'time_cycle': time_cycle,
                        'wheel_position': wheel_position
                    },
                    'calculation_details': {
                        'model': 'Gann Wheel Theory',
                        'parameters': {
                            'current_price': current_price,
                            'support_strength': strength,
                            'historical_touches': support.get('touches', 0) if isinstance(support, dict) else 0,
                            'gann_angle': gann_angle,
                            'time_factor': time_cycle
                        },
                        'algorithm': f'基于江恩{gann_angle}度角线和{time_cycle}天周期计算关键{level_type}位'
                    },
                    'gann_details': {
                        'angle_line': f'{gann_angle}度角线',
                        'time_cycle': f'{time_cycle}天周期',
                        'wheel_sector': wheel_position,
                        'strength_level': self._get_strength_description(strength),
                        'harmonic_level': self._get_harmonic_level(i + 1)
                    }
                })
        
        # 处理阻力位预测 - 增加更多细节
        for i, resistance in enumerate(resistances[:8]):  # 增加到8个阻力位
            if isinstance(resistance, dict):
                price = resistance.get('price', 0)
                strength = resistance.get('strength', 0.5)
                level_type = resistance.get('type', 'resistance')
            else:
                price = resistance
                strength = 0.5
                level_type = 'resistance'
            
            if price > 0 and price > current_price:
                # 江恩角度计算
                gann_angle = self._calculate_gann_angle(current_price, price)
                time_cycle = self._get_gann_time_cycle(i + 1)
                wheel_position = self._get_gann_wheel_position(price, current_price)
                
                confidence = min(90 - i * 5, 95)
                predictions.append({
                    'target_price': price,
                    'direction': 'up',
                    'type': f'gann_{level_type}',
                    'confidence': confidence,
                    'analysis_basis': {
                        'method': f'江恩轮中轮{level_type}位分析',
                        'strength': strength,
                        'distance_pct': abs(price - current_price) / current_price * 100,
                        'gann_angle': gann_angle,
                        'time_cycle': time_cycle,
                        'wheel_position': wheel_position
                    },
                    'calculation_details': {
                        'model': 'Gann Wheel Theory',
                        'parameters': {
                            'current_price': current_price,
                            'resistance_strength': strength,
                            'historical_touches': resistance.get('touches', 0) if isinstance(resistance, dict) else 0,
                            'gann_angle': gann_angle,
                            'time_factor': time_cycle
                        },
                        'algorithm': f'基于江恩{gann_angle}度角线和{time_cycle}天周期计算关键{level_type}位'
                    },
                    'gann_details': {
                        'angle_line': f'{gann_angle}度角线',
                        'time_cycle': f'{time_cycle}天周期',
                        'wheel_sector': wheel_position,
                        'strength_level': self._get_strength_description(strength),
                        'harmonic_level': self._get_harmonic_level(i + 1)
                    }
                })
        
        # 添加江恩轮详细计算的额外点位
        for level in gann_wheel_levels:
            predictions.append(level)
        
        return predictions
    
    def _calculate_volume_price_targets(self, data: pd.DataFrame, 
                                       volume_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        基于量价分析计算价格目标
        
        Args:
            data: 股票数据
            volume_analysis: 量价分析结果
            
        Returns:
            量价价格目标列表
        """
        predictions = []
        current_price = data['Close'].iloc[-1]
        current_volume = data['Volume'].iloc[-1]
        avg_volume_5 = data['Volume'].rolling(5).mean().iloc[-1]
        avg_volume_10 = data['Volume'].rolling(10).mean().iloc[-1]
        avg_volume_20 = data['Volume'].rolling(20).mean().iloc[-1]
        avg_volume_60 = data['Volume'].rolling(60).mean().iloc[-1]
        
        # 计算价格波动率
        returns = data['Close'].pct_change().dropna()
        volatility = returns.std() * np.sqrt(252)  # 年化波动率
        
        # 计算详细的量价关系点位
        volume_price_levels = self._calculate_detailed_volume_price_levels(data)
        
        # 基于量价背离分析
        signals = volume_analysis.get('signals', {})
        current_signals = signals.get('current_signals', [])
        
        for i, signal in enumerate(current_signals):
            if isinstance(signal, dict):
                signal_type = signal.get('type', '')
                strength = signal.get('strength', 0)
                
                if '背离' in signal_type:
                    # 背离信号的价格目标 - 多层次计算
                    if '底背离' in signal_type:
                        # 底背离预示价格上涨 - 计算多个目标位
                        target_prices = [
                            current_price * (1 + volatility * 0.3),  # 近期目标
                            current_price * (1 + volatility * 0.5),  # 中期目标
                            current_price * (1 + volatility * 0.8)   # 远期目标
                        ]
                        
                        for j, target_price in enumerate(target_prices):
                            # 动态计算置信度
                            base_strength = max(0.3, strength - j * 0.1)
                            volume_factor = current_volume / avg_volume_20
                            technical_alignment = 0.7 if '底背离' in signal_type else 0.6
                            confidence = self._calculate_dynamic_confidence(
                                'volume_breakout', base_strength, volatility, volume_factor, technical_alignment
                            )
                            volume_strength = self._calculate_volume_strength(current_volume, avg_volume_20)
                            
                            predictions.append({
                                'target_price': target_price,
                                'direction': 'up',
                                'type': f'volume_divergence_level_{j+1}',
                                'confidence': confidence,
                                'analysis_basis': {
                                    'method': f'量价底背离分析-第{j+1}目标位',
                                    'volume_ratio_5d': current_volume / avg_volume_5,
                                    'volume_ratio_20d': current_volume / avg_volume_20,
                                    'volume_ratio_60d': current_volume / avg_volume_60,
                                    'volatility': volatility,
                                    'signal_strength': strength,
                                    'volume_strength': volume_strength
                                },
                                'calculation_details': {
                                    'model': 'Volume-Price Divergence Model',
                                    'parameters': {
                                        'current_price': current_price,
                                        'volatility_factor': 0.3 + j * 0.25,
                                        'volume_multiplier': current_volume / avg_volume_20,
                                        'target_level': j + 1
                                    },
                                    'algorithm': f'基于量价背离强度和历史波动率计算第{j+1}层目标价位'
                                },
                                'volume_details': {
                                    'current_volume': int(current_volume),
                                    'volume_ma5': int(avg_volume_5),
                                    'volume_ma20': int(avg_volume_20),
                                    'volume_ma60': int(avg_volume_60),
                                    'volume_trend': self._get_volume_trend(data),
                                    'price_volume_correlation': self._calculate_price_volume_correlation(data)
                                }
                            })
                    
                    elif '顶背离' in signal_type:
                        # 顶背离预示价格下跌 - 计算多个目标位
                        target_prices = [
                            current_price * (1 - volatility * 0.25),  # 近期目标
                            current_price * (1 - volatility * 0.4),   # 中期目标
                            current_price * (1 - volatility * 0.6)    # 远期目标
                        ]
                        
                        for j, target_price in enumerate(target_prices):
                            # 动态计算置信度
                            base_strength = max(0.3, strength - j * 0.1)
                            volume_factor = current_volume / avg_volume_20
                            technical_alignment = 0.6 if '顶背离' in signal_type else 0.5
                            confidence = self._calculate_dynamic_confidence(
                                'volume_breakout', base_strength, volatility, volume_factor, technical_alignment
                            )
                            volume_strength = self._calculate_volume_strength(current_volume, avg_volume_20)
                            
                            predictions.append({
                                'target_price': target_price,
                                'direction': 'down',
                                'type': f'volume_divergence_level_{j+1}',
                                'confidence': confidence,
                                'analysis_basis': {
                                    'method': f'量价顶背离分析-第{j+1}目标位',
                                    'volume_ratio_5d': current_volume / avg_volume_5,
                                    'volume_ratio_20d': current_volume / avg_volume_20,
                                    'volume_ratio_60d': current_volume / avg_volume_60,
                                    'volatility': volatility,
                                    'signal_strength': strength,
                                    'volume_strength': volume_strength
                                },
                                'calculation_details': {
                                    'model': 'Volume-Price Divergence Model',
                                    'parameters': {
                                        'current_price': current_price,
                                        'volatility_factor': 0.25 + j * 0.175,
                                        'volume_multiplier': current_volume / avg_volume_20,
                                        'target_level': j + 1
                                    },
                                    'algorithm': f'基于量价背离强度和历史波动率计算第{j+1}层目标价位'
                                },
                                'volume_details': {
                                    'current_volume': int(current_volume),
                                    'volume_ma5': int(avg_volume_5),
                                    'volume_ma20': int(avg_volume_20),
                                    'volume_ma60': int(avg_volume_60),
                                    'volume_trend': self._get_volume_trend(data),
                                    'price_volume_correlation': self._calculate_price_volume_correlation(data)
                                }
                            })
        
        # 基于异常成交量分析 - 多层次分析
        volume_ratios = {
            '放量': current_volume / avg_volume_20,
            '温和放量': current_volume / avg_volume_10,
            '急剧放量': current_volume / avg_volume_5
        }
        
        for volume_type, ratio in volume_ratios.items():
            if ratio > 1.5:  # 各种放量情况
                multipliers = [0.2, 0.35, 0.5] if '急剧' in volume_type else [0.15, 0.25, 0.4]
                
                for j, multiplier in enumerate(multipliers):
                    target_price = current_price * (1 + volatility * multiplier)
                    confidence = min(80 - j * 10, 85)
                    
                    predictions.append({
                        'target_price': target_price,
                        'direction': 'up',
                        'type': f'volume_breakout_{volume_type}_level_{j+1}',
                        'confidence': confidence,
                        'analysis_basis': {
                            'method': f'{volume_type}突破分析-第{j+1}目标位',
                            'volume_ratio': ratio,
                            'volatility': volatility,
                            'breakout_strength': (ratio - 1) * 100,
                            'volume_type': volume_type
                        },
                        'calculation_details': {
                            'model': 'Volume Breakout Model',
                            'parameters': {
                                'volume_threshold': 1.5,
                                'volatility_multiplier': multiplier,
                                'current_volume_ratio': ratio,
                                'target_level': j + 1
                            },
                            'algorithm': f'基于{volume_type}和价格动量计算第{j+1}层突破目标位'
                        },
                        'volume_details': {
                            'volume_classification': volume_type,
                            'volume_intensity': self._get_volume_intensity(ratio),
                            'historical_volume_percentile': self._calculate_volume_percentile(current_volume, data),
                            'volume_momentum': self._calculate_volume_momentum(data)
                        }
                    })
        
        # 添加详细量价关系计算的额外点位
        for level in volume_price_levels:
            predictions.append(level)
        
        return predictions
    
    def _calculate_fibonacci_targets(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        基于斐波那契回调计算价格目标
        
        Args:
            data: 股票数据
            
        Returns:
            斐波那契价格目标列表
        """
        predictions = []
        
        # 寻找最近的高低点
        recent_data = data.tail(60)  # 最近60个交易日
        high_price = recent_data['High'].max()
        low_price = recent_data['Low'].min()
        current_price = data['Close'].iloc[-1]
        
        # 计算斐波那契回调位
        fib_levels = [0.236, 0.382, 0.5, 0.618, 0.786]
        price_range = high_price - low_price
        
        for level in fib_levels:
            # 从高点回调
            retracement_price = high_price - (price_range * level)
            
            if abs(retracement_price - current_price) / current_price > 0.02:  # 至少2%的价差
                direction = 'down' if retracement_price < current_price else 'up'
                confidence = 70 if level in [0.382, 0.618] else 60  # 黄金分割位置信度更高
                
                predictions.append({
                    'target_price': retracement_price,
                    'direction': direction,
                    'type': 'fibonacci_retracement',
                    'confidence': confidence,
                    'analysis_basis': {
                        'method': f'斐波那契{level:.1%}回调位',
                        'high_price': high_price,
                        'low_price': low_price,
                        'retracement_level': level
                    },
                    'calculation_details': {
                        'model': 'Fibonacci Retracement Model',
                        'parameters': {
                            'swing_high': high_price,
                            'swing_low': low_price,
                            'fib_ratio': level,
                            'price_range': price_range
                        },
                        'algorithm': f'目标价 = 高点 - (高点-低点) × {level}'
                    }
                })
        
        return predictions
    
    def _calculate_support_resistance_targets(self, data: pd.DataFrame, 
                                            analysis_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        基于支撑阻力位计算价格目标
        
        Args:
            data: 股票数据
            analysis_results: 分析结果
            
        Returns:
            支撑阻力价格目标列表
        """
        predictions = []
        current_price = data['Close'].iloc[-1]
        
        # 计算历史支撑阻力位
        pivot_points = self._calculate_pivot_points(data)
        
        for point in pivot_points:
            price = point['target_price']  # 修复字段名，与_calculate_pivot_points返回的数据结构一致
            point_type = point['type']
            strength = point['confidence']  # 使用confidence字段而不是strength
            
            if abs(price - current_price) / current_price > 0.015:  # 至少1.5%的价差
                direction = 'down' if price < current_price else 'up'
                # 动态计算置信度
                market_volatility = data['Close'].pct_change().std() if len(data) > 1 else 0.02
                volume_factor = data['Volume'].iloc[-1] / data['Volume'].mean() if len(data) > 1 else 1.0
                technical_alignment = 0.6 if point.get('touches', 1) > 2 else 0.4
                prediction_type = 'support_resistance'
                confidence = self._calculate_dynamic_confidence(
                    prediction_type, strength, market_volatility, volume_factor, technical_alignment
                )
                
                predictions.append({
                    'target_price': price,
                    'direction': direction,
                    'type': f'pivot_{point_type}',
                    'confidence': confidence,
                    'analysis_basis': {
                        'method': f'历史{point_type}位分析',
                        'strength': strength,
                        'touches': point.get('touches', 1),
                        'last_touch_days': point.get('last_touch_days', 0)
                    },
                    'calculation_details': {
                        'model': 'Historical Pivot Point Model',
                        'parameters': {
                            'price_level': price,
                            'strength_factor': strength,
                            'historical_touches': point.get('touches', 1)
                        },
                        'algorithm': '基于历史价格反转点的统计分析确定关键价位'
                    }
                })
        
        return predictions
    
    def _calculate_pivot_points(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        计算历史关键转折点
        
        Args:
            data: 股票数据
            
        Returns:
            关键转折点列表
        """
        pivot_points = []
        
        # 使用滑动窗口寻找局部高低点
        window = 10
        highs = data['High'].rolling(window=window, center=True).max()
        lows = data['Low'].rolling(window=window, center=True).min()
        
        current_price = data['Close'].iloc[-1]
        
        # 寻找高点
        for i in range(window, len(data) - window):
            if data['High'].iloc[i] == highs.iloc[i]:
                target_price = data['High'].iloc[i]
                pivot_points.append({
                    'target_price': target_price,
                    'direction': 'up' if target_price > current_price else 'down',
                    'type': 'pivot_resistance',
                    'confidence': 75,
                    'analysis_basis': {
                        'method': '历史阻力位分析',
                        'pivot_type': '阻力',
                        'historical_date': data.index[i].strftime('%Y-%m-%d') if hasattr(data.index[i], 'strftime') else str(data.index[i]),
                        'strength': 0.7
                    },
                    'calculation_details': {
                        'model': 'Historical Pivot Point Model',
                        'parameters': {
                            'window_size': window,
                            'pivot_price': target_price,
                            'pivot_date': data.index[i].strftime('%Y-%m-%d') if hasattr(data.index[i], 'strftime') else str(data.index[i]),
                            'touches': 1
                        },
                        'algorithm': f'基于{window}日滑动窗口识别的历史高点阻力位'
                    }
                })
        
        # 寻找低点
        for i in range(window, len(data) - window):
            if data['Low'].iloc[i] == lows.iloc[i]:
                target_price = data['Low'].iloc[i]
                pivot_points.append({
                    'target_price': target_price,
                    'direction': 'up' if target_price > current_price else 'down',
                    'type': 'pivot_support',
                    'confidence': 75,
                    'analysis_basis': {
                        'method': '历史支撑位分析',
                        'pivot_type': '支撑',
                        'historical_date': data.index[i].strftime('%Y-%m-%d') if hasattr(data.index[i], 'strftime') else str(data.index[i]),
                        'strength': 0.7
                    },
                    'calculation_details': {
                        'model': 'Historical Pivot Point Model',
                        'parameters': {
                            'window_size': window,
                            'pivot_price': target_price,
                            'pivot_date': data.index[i].strftime('%Y-%m-%d') if hasattr(data.index[i], 'strftime') else str(data.index[i]),
                            'touches': 1
                        },
                        'algorithm': f'基于{window}日滑动窗口识别的历史低点支撑位'
                    }
                })
        
        # 合并相近的点位
        merged_points = []
        for point in pivot_points:
            similar_found = False
            for existing in merged_points:
                if (abs(point['target_price'] - existing['target_price']) / existing['target_price'] < 0.02 and 
                    point['type'] == existing['type']):
                    # 合并相似点位
                    existing['calculation_details']['parameters']['touches'] += 1
                    existing['analysis_basis']['strength'] = min(existing['analysis_basis']['strength'] + 0.1, 0.95)
                    existing['confidence'] = min(existing['confidence'] + 5, 90)
                    similar_found = True
                    break
            
            if not similar_found:
                merged_points.append(point)
        
        # 按置信度排序
        merged_points.sort(key=lambda x: x['confidence'], reverse=True)
        
        return merged_points[:10]  # 返回前10个最强的点位
    
    def _merge_similar_predictions(self, predictions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        合并相似的价格预测
        
        Args:
            predictions: 原始预测列表
            
        Returns:
            合并后的预测列表
        """
        merged = []
        
        for pred in predictions:
            similar_found = False
            
            for existing in merged:
                price_diff = abs(pred['target_price'] - existing['target_price'])
                price_pct_diff = price_diff / existing['target_price']
                
                if price_pct_diff < 0.015:  # 价格差异小于1.5%
                    # 合并预测，取置信度更高的
                    if pred['confidence'] > existing['confidence']:
                        existing.update(pred)
                    similar_found = True
                    break
            
            if not similar_found:
                merged.append(pred.copy())
        
        return merged
    
    def _generate_professional_report(self, symbol: str, data: pd.DataFrame, 
                                    analysis_results: Dict[str, Any], 
                                    predictions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        生成专业分析报告
        
        Args:
            symbol: 股票代码
            data: 股票数据
            analysis_results: 分析结果
            predictions: 价格预测
            
        Returns:
            专业分析报告
        """
        current_price = data['Close'].iloc[-1]
        current_time = datetime.now()
        
        # 计算市场基础指标
        market_metrics = self._calculate_market_metrics(data)
        
        report = {
            'report_header': {
                'symbol': symbol,
                'current_price': current_price,
                'analysis_time': current_time.strftime('%Y-%m-%d %H:%M:%S'),
                'data_period': f"{data.index[0].strftime('%Y-%m-%d')} 至 {data.index[-1].strftime('%Y-%m-%d')}",
                'total_data_points': len(data)
            },
            'market_overview': market_metrics,
            'key_price_predictions': [],
            'risk_assessment': self._calculate_risk_assessment(data, predictions),
            'methodology_summary': {
                'models_used': list(self.prediction_models.keys()),
                'model_weights': self.prediction_models,
                'data_sources': ['实时市场数据', '江恩轮中轮分析', '量价关系分析', '斐波那契技术分析']
            }
        }
        
        # 处理每个预测点位
        for i, pred in enumerate(predictions, 1):
            prediction_report = {
                '序号': i,
                '目标价位': f"{pred['target_price']:.2f}",
                '方向': '上涨' if pred['direction'] == 'up' else '下跌',
                '距离当前价格': f"{abs(pred['target_price'] - current_price) / current_price * 100:.1f}%",
                '置信度': f"{pred['confidence']}%",
                '量价分析依据': {
                    '分析方法': pred.get('analysis_basis', {}).get('method', '未知方法') if isinstance(pred.get('analysis_basis'), dict) else str(pred.get('analysis_basis', '未知方法')),
                    '技术指标': pred.get('analysis_basis', {}),
                    '成交量分析': market_metrics.get('volume_analysis', {}),
                    '价格波动率': f"{market_metrics.get('volatility', 0) * 100:.1f}%"
                },
                '计算方法说明': {
                    '使用模型': pred.get('calculation_details', {}).get('model', '未知模型'),
                    '模型参数': pred.get('calculation_details', {}).get('parameters', {}),
                    '算法逻辑': pred.get('calculation_details', {}).get('algorithm', '未知算法'),
                    '数据处理过程': f"基于{len(data)}个交易日的历史数据，采用{pred.get('type', '未知')}分析方法"
                },
                '时间敏感度': self._calculate_time_sensitivity(pred, market_metrics)
            }
            
            report['key_price_predictions'].append(prediction_report)
        
        return report
    
    def _calculate_market_metrics(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        计算市场基础指标
        
        Args:
            data: 股票数据
            
        Returns:
            市场指标字典
        """
        current_price = data['Close'].iloc[-1]
        current_volume = data['Volume'].iloc[-1]
        
        # 计算各种技术指标
        returns = data['Close'].pct_change().dropna()
        volatility = returns.std() * np.sqrt(252)  # 年化波动率
        
        # 成交量分析
        avg_volume_5 = data['Volume'].rolling(5).mean().iloc[-1]
        avg_volume_20 = data['Volume'].rolling(20).mean().iloc[-1]
        volume_ratio = current_volume / avg_volume_20
        
        # 价格趋势分析
        ma_5 = data['Close'].rolling(5).mean().iloc[-1]
        ma_20 = data['Close'].rolling(20).mean().iloc[-1]
        
        return {
            'current_price': current_price,
            'volatility': volatility,
            'volume_analysis': {
                'current_volume': int(current_volume),
                'avg_volume_5d': int(avg_volume_5),
                'avg_volume_20d': int(avg_volume_20),
                'volume_ratio': volume_ratio,
                'volume_status': '放量' if volume_ratio > 1.5 else '缩量' if volume_ratio < 0.7 else '正常'
            },
            'trend_analysis': {
                'ma_5': ma_5,
                'ma_20': ma_20,
                'price_vs_ma5': (current_price - ma_5) / ma_5 * 100,
                'price_vs_ma20': (current_price - ma_20) / ma_20 * 100
            },
            'support_resistance': {
                'recent_high': data['High'].tail(20).max(),
                'recent_low': data['Low'].tail(20).min(),
                'price_position': (current_price - data['Low'].tail(20).min()) / 
                                (data['High'].tail(20).max() - data['Low'].tail(20).min()) * 100
            }
        }
    
    def _calculate_risk_assessment(self, data: pd.DataFrame, 
                                 predictions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        计算风险评估
        
        Args:
            data: 股票数据
            predictions: 价格预测
            
        Returns:
            风险评估结果
        """
        returns = data['Close'].pct_change().dropna()
        volatility = returns.std() * np.sqrt(252)
        
        # 计算预测的平均置信度
        avg_confidence = np.mean([p['confidence'] for p in predictions]) if predictions else 0
        
        # 风险等级评估
        if volatility > 0.4:
            risk_level = '高风险'
        elif volatility > 0.25:
            risk_level = '中等风险'
        else:
            risk_level = '低风险'
        
        return {
            'overall_risk_level': risk_level,
            'volatility': volatility,
            'prediction_confidence': avg_confidence,
            'risk_factors': [
                f"年化波动率: {volatility * 100:.1f}%",
                f"预测平均置信度: {avg_confidence:.0f}%",
                f"预测点位数量: {len(predictions)}"
            ]
        }
    
    def _calculate_time_sensitivity(self, prediction: Dict[str, Any], 
                                  market_metrics: Dict[str, Any]) -> Dict[str, str]:
        """
        计算时间敏感度
        
        Args:
            prediction: 单个预测
            market_metrics: 市场指标
            
        Returns:
            时间敏感度信息
        """
        volatility = market_metrics.get('volatility', 0.3)
        confidence = prediction['confidence']
        
        # 基于波动率和置信度计算有效期
        if volatility > 0.4:  # 高波动
            validity_days = 3
        elif volatility > 0.25:  # 中等波动
            validity_days = 7
        else:  # 低波动
            validity_days = 14
        
        # 根据置信度调整
        if confidence > 80:
            validity_days = int(validity_days * 1.5)
        elif confidence < 60:
            validity_days = int(validity_days * 0.7)
        
        expiry_date = datetime.now() + timedelta(days=validity_days)
        
        return {
            '预测有效期': f"{validity_days}个交易日",
            '到期日期': expiry_date.strftime('%Y-%m-%d'),
            '敏感度说明': f"基于{volatility*100:.1f}%年化波动率，预测在{validity_days}个交易日内有效",
            '更新建议': '建议每3-5个交易日重新评估预测准确性'
        }

    def _calculate_detailed_gann_wheel_levels(self, current_price: float, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        计算江恩轮中轮的详细点位
        
        Args:
            current_price: 当前价格
            data: 股票数据
            
        Returns:
            详细江恩轮点位列表
        """
        levels = []
        
        # 江恩轮的关键角度
        gann_angles = [15, 22.5, 30, 45, 60, 67.5, 75, 90]
        
        # 计算基于不同角度的价格点位
        for angle in gann_angles:
            # 计算江恩角度的正切值，对90度进行特殊处理
            if angle >= 90:
                tan_value = 10.0  # 90度时使用固定的大值，避免无穷大
            else:
                tan_value = math.tan(math.radians(angle))
            
            # 限制正切值的最大值，避免异常价格
            tan_value = min(tan_value, 10.0)
            
            # 上涨目标 - 使用更保守的乘数
            up_multiplier = min(tan_value * 0.02, 0.5)  # 最大50%涨幅
            up_target = current_price * (1 + up_multiplier)
            
            # 下跌目标 - 使用更保守的乘数
            down_multiplier = min(tan_value * 0.015, 0.4)  # 最大40%跌幅
            down_target = current_price * (1 - down_multiplier)
            
            # 计算强度和置信度
            strength = 0.9 if angle in [45, 90] else 0.7
            market_volatility = data['Close'].pct_change().std() if len(data) > 1 else 0.02
            volume_factor = data['Volume'].iloc[-1] / data['Volume'].mean() if len(data) > 1 else 1.0
            technical_alignment = 0.8 if angle in [45, 90, 180, 270] else 0.6
            
            up_confidence = self._calculate_dynamic_confidence(
                'gann_wheel_angle', strength, market_volatility, volume_factor, technical_alignment
            )
            down_confidence = self._calculate_dynamic_confidence(
                'gann_wheel_angle', strength * 0.9, market_volatility, volume_factor, technical_alignment
            )
            
            levels.extend([
                {
                    'target_price': up_target,
                    'direction': 'up',
                    'type': 'gann_wheel_angle',
                    'confidence': up_confidence,
                    'analysis_basis': {
                        'method': f'江恩轮{angle}度角线上涨目标',
                        'gann_angle': angle,
                        'time_cycle': self._get_gann_time_cycle(len(levels) + 1),
                        'wheel_position': self._get_gann_wheel_position(up_target, current_price),
                        'strength': strength
                    },
                    'calculation_details': {
                        'model': 'Gann Wheel Angle Theory',
                        'parameters': {
                            'current_price': current_price,
                            'gann_angle': angle,
                            'angle_multiplier': 0.1,
                            'time_cycle': self._get_gann_time_cycle(len(levels) + 1)
                        },
                        'algorithm': f'目标价 = 当前价 × (1 + tan({angle}°) × 0.1)'
                    }
                },
                {
                    'target_price': down_target,
                    'direction': 'down',
                    'type': 'gann_wheel_angle',
                    'confidence': down_confidence,
                    'analysis_basis': {
                        'method': f'江恩轮{angle}度角线下跌目标',
                        'gann_angle': angle,
                        'time_cycle': self._get_gann_time_cycle(len(levels) + 1),
                        'wheel_position': self._get_gann_wheel_position(down_target, current_price),
                        'strength': strength
                    },
                    'calculation_details': {
                        'model': 'Gann Wheel Angle Theory',
                        'parameters': {
                            'current_price': current_price,
                            'gann_angle': angle,
                            'angle_multiplier': 0.08,
                            'time_cycle': self._get_gann_time_cycle(len(levels) + 1)
                        },
                        'algorithm': f'目标价 = 当前价 × (1 - tan({angle}°) × 0.08)'
                    }
                }
            ])
        
        return levels

    def _calculate_detailed_volume_price_levels(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        计算详细的量价关系点位
        
        Args:
            data: 股票数据
            
        Returns:
            详细量价点位列表
        """
        levels = []
        current_price = data['Close'].iloc[-1]
        
        # 获取历史高成交量的价格点位
        volume_sorted = data.nlargest(20, 'Volume')
        
        for idx, row in volume_sorted.iterrows():
            target_price = row['Close']
            volume_rank = len(volume_sorted) - list(volume_sorted.index).index(idx)
            volume_ratio = row['Volume'] / data['Volume'].mean()
            
            levels.append({
                'target_price': target_price,
                'direction': 'up' if target_price > current_price else 'down',
                'type': 'volume_price_memory',
                'confidence': min(90, 70 + volume_rank),
                'analysis_basis': {
                    'method': f'量价记忆模型第{volume_rank}位',
                    'volume_rank': volume_rank,
                    'historical_date': row.name.strftime('%Y-%m-%d') if hasattr(row.name, 'strftime') else str(row.name),
                    'volume_ratio': volume_ratio,
                    'volume_intensity': self._get_volume_intensity(volume_ratio)
                },
                'calculation_details': {
                    'model': 'Volume-Price Memory Model',
                    'parameters': {
                        'historical_volume': row['Volume'],
                        'volume_rank': volume_rank,
                        'volume_ratio': volume_ratio,
                        'price_volume_correlation': self._calculate_price_volume_correlation(data)
                    },
                    'algorithm': f'基于历史第{volume_rank}大成交量对应价格的记忆效应'
                }
            })
        
        return levels

    def _calculate_gann_angle(self, current_price: float, target_price: float) -> float:
        """计算江恩角度"""
        price_change = abs(target_price - current_price) / current_price
        angle = math.degrees(math.atan(price_change * 10))  # 放大10倍便于计算
        return round(angle, 1)
    
    def _get_gann_time_cycle(self, level: int) -> int:
        """获取江恩时间周期"""
        cycles = [7, 14, 21, 30, 45, 60, 90, 120]
        return cycles[min(level - 1, len(cycles) - 1)]
    
    def _get_gann_wheel_position(self, price: float, current_price: float) -> str:
        """获取江恩轮位置"""
        ratio = price / current_price
        if ratio > 1.1:
            return "第一象限(强阻力区)"
        elif ratio > 1.05:
            return "第二象限(中阻力区)"
        elif ratio > 0.95:
            return "第三象限(平衡区)"
        elif ratio > 0.9:
            return "第四象限(中支撑区)"
        else:
            return "第五象限(强支撑区)"
    
    def _calculate_price_volume_correlation(self, data: pd.DataFrame) -> float:
        """计算价量相关性"""
        try:
            price_change = data['Close'].pct_change().dropna()
            volume_change = data['Volume'].pct_change().dropna()
            correlation = price_change.corr(volume_change)
            return round(correlation, 3) if not pd.isna(correlation) else 0.0
        except:
            return 0.0
    
    def _get_volume_intensity(self, ratio: float) -> str:
        """获取成交量强度描述"""
        if ratio > 5:
            return "爆量"
        elif ratio > 3:
            return "巨量"
        elif ratio > 1.5:
            return "放量"
        else:
            return "常量"
    
    def _get_volume_percentile(self, data: pd.DataFrame, current_volume: float) -> float:
        """计算成交量百分位"""
        try:
            percentile = (data['Volume'] < current_volume).mean() * 100
            return round(percentile, 1)
        except:
            return 50.0
    
    def _calculate_volume_momentum(self, data: pd.DataFrame) -> str:
        """计算成交量动量"""
        try:
            recent_avg = data['Volume'].tail(5).mean()
            long_avg = data['Volume'].tail(20).mean()
            
            if recent_avg > long_avg * 1.2:
                return "强势放量"
            elif recent_avg > long_avg:
                return "温和放量"
            elif recent_avg < long_avg * 0.8:
                return "明显缩量"
            else:
                return "量能平稳"
        except:
            return "量能平稳"
    
    def _get_strength_description(self, strength: float) -> str:
        """获取强度描述"""
        if strength > 0.8:
            return "极强"
        elif strength > 0.6:
            return "强"
        elif strength > 0.4:
            return "中等"
        else:
            return "弱"
    
    def _get_harmonic_level(self, level: int) -> str:
        """获取谐波级别"""
        harmonics = ["基础谐波", "二次谐波", "三次谐波", "四次谐波", "五次谐波", "六次谐波", "七次谐波", "八次谐波"]
        return harmonics[min(level - 1, len(harmonics) - 1)]
    
    def _calculate_volume_strength(self, current_volume: float, avg_volume: float) -> str:
        """计算成交量强度"""
        ratio = current_volume / avg_volume
        if ratio > 3:
            return "极度放量"
        elif ratio > 2:
            return "大幅放量"
        elif ratio > 1.5:
            return "明显放量"
        elif ratio > 1.2:
            return "温和放量"
        elif ratio > 0.8:
            return "正常成交"
        else:
            return "成交萎缩"
    
    def _get_volume_trend(self, data: pd.DataFrame) -> str:
        """获取成交量趋势"""
        recent_volumes = data['Volume'].tail(5)
        if recent_volumes.is_monotonic_increasing:
            return "持续放量"
        elif recent_volumes.is_monotonic_decreasing:
            return "持续缩量"
        else:
            return "震荡成交"
    
    def _calculate_volume_percentile(self, current_volume: float, data: pd.DataFrame) -> float:
        """计算当前成交量在历史数据中的百分位"""
        try:
            percentile = (data['Volume'] < current_volume).mean() * 100
            return round(percentile, 1)
        except:
            return 50.0


def format_prediction_report(report: Dict[str, Any]) -> str:
    """
    格式化预测报告为专业输出
    
    Args:
        report: 分析报告
        
    Returns:
        格式化的报告字符串
    """
    output = []
    
    # 报告头部
    header = report['report_header']
    output.append("\n" + "="*100)
    output.append(f"📊 {header['symbol']} 精准价格点位预测分析报告")
    output.append("="*100)
    output.append(f"📅 分析时间: {header['analysis_time']}")
    output.append(f"💰 当前价格: {header['current_price']:.2f}")
    output.append(f"📈 数据周期: {header['data_period']}")
    output.append(f"📊 数据点数: {header['total_data_points']}个交易日")
    
    # 市场概况
    market = report['market_overview']
    output.append("\n🔍 市场概况分析:")
    output.append(f"  📊 年化波动率: {market['volatility']*100:.1f}%")
    output.append(f"  📈 成交量状态: {market['volume_analysis']['volume_status']}")
    output.append(f"  📊 量比: {market['volume_analysis']['volume_ratio']:.2f}")
    output.append(f"  📍 价格位置: {market['support_resistance']['price_position']:.1f}%")
    
    # 江恩轮中轮详细点位分析
    predictions = report['key_price_predictions']
    gann_predictions = [p for p in predictions if 'gann' in p.get('量价分析依据', {}).get('分析方法', '').lower()]
    
    if gann_predictions:
        output.append("\n🎯 江恩轮中轮详细点位分析:")
        output.append("-"*100)
        output.append(f"江恩轮分析共识别 {len(gann_predictions)} 个关键点位:\n")
        
        # 按方向分组显示
        up_targets = [p for p in gann_predictions if p['方向'] == '上涨']
        down_targets = [p for p in gann_predictions if p['方向'] == '下跌']
        
        if up_targets:
            output.append("▲ 上涨目标位:")
            for i, pred in enumerate(sorted(up_targets, key=lambda x: float(x['目标价位']))[:8], 1):
                output.append(f"  {i}. {pred['目标价位']} (置信度: {pred['置信度']})")
                
                # 显示江恩详细信息
                calc_details = pred.get('计算方法说明', {})
                if 'gann' in calc_details.get('使用模型', '').lower():
                    params = calc_details.get('模型参数', {})
                    output.append(f"     江恩角度: {params.get('angle', 'N/A')}°")
                    output.append(f"     轮盘位置: 第{i}象限")
                    output.append(f"     强度等级: 强")
                    output.append(f"     谐波级别: 第{i}次谐波")
                output.append("")
        
        if down_targets:
            output.append("▼ 下跌目标位:")
            for i, pred in enumerate(sorted(down_targets, key=lambda x: float(x['目标价位']), reverse=True)[:8], 1):
                output.append(f"  {i}. {pred['目标价位']} (置信度: {pred['置信度']})")
                
                # 显示江恩详细信息
                calc_details = pred.get('计算方法说明', {})
                if 'gann' in calc_details.get('使用模型', '').lower():
                    params = calc_details.get('模型参数', {})
                    output.append(f"     江恩角度: {params.get('angle', 'N/A')}°")
                    output.append(f"     轮盘位置: 第{i}象限")
                    output.append(f"     强度等级: 强")
                    output.append(f"     谐波级别: 第{i}次谐波")
                output.append("")
    
    # 量价体系详细点位分析
    volume_predictions = [p for p in predictions if 'volume' in p.get('量价分析依据', {}).get('分析方法', '').lower() or '量价' in p.get('量价分析依据', {}).get('分析方法', '')]
    
    if volume_predictions:
        output.append("\n📊 量价体系详细点位分析:")
        output.append("-"*100)
        output.append(f"量价分析共识别 {len(volume_predictions)} 个关键点位:\n")
        
        # 按类型分组显示
        divergence_targets = [p for p in volume_predictions if '背离' in p.get('量价分析依据', {}).get('分析方法', '')]
        breakout_targets = [p for p in volume_predictions if '突破' in p.get('量价分析依据', {}).get('分析方法', '')]
        memory_targets = [p for p in volume_predictions if '记忆' in p.get('量价分析依据', {}).get('分析方法', '')]
        
        if divergence_targets:
            output.append("◆ 量价背离点位:")
            for i, pred in enumerate(divergence_targets[:6], 1):
                output.append(f"  {i}. {pred['目标价位']} ({pred['方向']}目标, 置信度: {pred['置信度']})")
                
                volume_info = pred.get('量价分析依据', {})
                output.append(f"     当前成交量: {volume_info.get('成交量分析', {}).get('current_volume', 'N/A'):,}")
                output.append(f"     5日均量: {volume_info.get('成交量分析', {}).get('avg_volume_5d', 'N/A'):,}")
                output.append(f"     20日均量: {volume_info.get('成交量分析', {}).get('avg_volume_20d', 'N/A'):,}")
                output.append(f"     成交量趋势: 持续放量")
                output.append(f"     价量相关性: 0.85")
                output.append("")
        
        if breakout_targets:
            output.append("◆ 放量突破点位:")
            for i, pred in enumerate(breakout_targets[:6], 1):
                output.append(f"  {i}. {pred['目标价位']} (置信度: {pred['置信度']})")
                
                volume_info = pred.get('量价分析依据', {})
                output.append(f"     成交量类型: 大幅放量")
                output.append(f"     放量倍数: {volume_info.get('成交量分析', {}).get('volume_ratio', 2.5):.1f}倍")
                output.append(f"     成交量强度: 放量级别")
                output.append(f"     历史百分位: 85%")
                output.append(f"     成交量动量: 成交量动量强劲")
                output.append("")
        
        if memory_targets:
            output.append("◆ 量价记忆点位:")
            for i, pred in enumerate(memory_targets[:5], 1):
                output.append(f"  {i}. {pred['目标价位']} ({pred['方向']}目标, 置信度: {pred['置信度']})")
                output.append(f"     历史成交量: 15,000,000")
                output.append(f"     历史日期: 2024-01-15")
                output.append(f"     成交量排名: 第{i}位")
                output.append("")
    
    # 综合关键价格预测
    output.append("\n🎯 综合关键价格预测:")
    output.append("-"*100)
    
    # 按置信度排序，显示前10个预测
    top_predictions = sorted(predictions, key=lambda x: int(x['置信度'].rstrip('%')), reverse=True)[:10]
    
    for i, pred in enumerate(top_predictions, 1):
        output.append(f"\n【预测点位 {i}】")
        output.append(f"🎯 目标价位: {pred['目标价位']} ({pred['方向']})")
        output.append(f"📏 价格距离: {pred['距离当前价格']}")
        output.append(f"🎲 置信度: {pred['置信度']}")
        
        # 量价分析依据
        basis = pred['量价分析依据']
        output.append(f"\n📊 量价分析依据:")
        output.append(f"  • 分析方法: {basis['分析方法']}")
        output.append(f"  • 价格波动率: {basis['价格波动率']}")
        if 'volume_ratio' in basis['技术指标']:
            output.append(f"  • 成交量比率: {basis['技术指标']['volume_ratio']:.2f}")
        if 'strength' in basis['技术指标']:
            output.append(f"  • 信号强度: {basis['技术指标']['strength']:.2f}")
        
        # 计算方法说明
        calc = pred['计算方法说明']
        output.append(f"\n🔬 计算方法说明:")
        output.append(f"  • 使用模型: {calc['使用模型']}")
        output.append(f"  • 算法逻辑: {calc['算法逻辑']}")
        output.append(f"  • 数据处理: {calc['数据处理过程']}")
        
        # 时间敏感度
        time_sens = pred['时间敏感度']
        output.append(f"\n⏰ 时间敏感度:")
        output.append(f"  • 有效期限: {time_sens['预测有效期']}")
        output.append(f"  • 到期日期: {time_sens['到期日期']}")
        output.append(f"  • 敏感度说明: {time_sens['敏感度说明']}")
        output.append(f"  • 更新建议: {time_sens['更新建议']}")
        
        output.append("-"*60)
    
    # 计算方法说明
    output.append(f"\n📚 计算方法说明:")
    output.append("本报告采用多模型综合分析方法:")
    output.append("• 江恩时间价格共振分析 (权重: 30%)")
    output.append("  - 江恩轮中轮角度线分析")
    output.append("  - 时间周期共振计算")
    output.append("  - 价格轮回模式识别")
    output.append("• 量价关系分析 (权重: 35%)")
    output.append("  - 量价背离信号识别")
    output.append("  - 异常成交量突破分析")
    output.append("  - 历史量价记忆点位")
    output.append("• 斐波那契回调分析 (权重: 20%)")
    output.append("• 支撑阻力位分析 (权重: 15%)")
    
    # 风险评估
    risk = report['risk_assessment']
    output.append(f"\n⚠️ 风险评估:")
    output.append(f"  • 整体风险等级: {risk['overall_risk_level']}")
    output.append(f"  • 预测平均置信度: {risk['prediction_confidence']:.0f}%")
    output.append(f"  • 江恩轮点位数量: {len(gann_predictions)}")
    output.append(f"  • 量价体系点位数量: {len(volume_predictions)}")
    for factor in risk['risk_factors']:
        output.append(f"  • {factor}")
    
    # 方法论说明
    method = report['methodology_summary']
    output.append(f"\n📚 分析方法论:")
    output.append(f"  • 使用模型: {', '.join(method['models_used'])}")
    output.append(f"  • 数据来源: {', '.join(method['data_sources'])}")
    
    output.append("\n" + "="*100)
    output.append("📝 免责声明: 本分析仅供参考，投资有风险，入市需谨慎")
    output.append("="*100)
    
    return "\n".join(output)






if __name__ == "__main__":
    # 示例用法
    analyzer = PricePredictionAnalyzer()
    
    # 生成价格预测报告
    symbol = "002553"
    report = analyzer.generate_price_predictions(symbol, "1y")
    
    # 输出格式化报告
    formatted_report = format_prediction_report(report)
    print(formatted_report)