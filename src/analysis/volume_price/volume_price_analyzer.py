#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
量价分析模块

实现量价关系分析的核心算法，包括：
1. 成交量与价格关系分析
2. 量价背离检测
3. 成交量指标计算
4. 价量配合度分析
5. 异常成交量识别

Author: AI Assistant
Date: 2024
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from loguru import logger
import warnings
warnings.filterwarnings('ignore')


class VolumePriceAnalyzer:
    """
    量价分析器
    
    基于量价关系理论进行股票分析
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化量价分析器
        
        Args:
            config: 量价分析配置参数
        """
        self.config = config
        
        # 基础参数
        self.volume_ma_periods = config.get('volume_ma_periods', [5, 10, 20, 60])
        self.price_ma_periods = config.get('price_ma_periods', [5, 10, 20, 60])
        self.divergence_threshold = config.get('divergence_threshold', 0.15)  # 背离阈值
        self.volume_spike_threshold = config.get('volume_spike_threshold', 2.0)  # 放量阈值
        self.correlation_window = config.get('correlation_window', 20)  # 相关性计算窗口
        
        logger.info("量价分析器初始化完成")
    
    def analyze_stock(self, symbol: str, data: pd.DataFrame) -> Dict[str, Any]:
        """
        对股票进行量价分析
        
        Args:
            symbol: 股票代码
            data: 股票数据DataFrame，需包含OHLCV数据
            
        Returns:
            量价分析结果字典
        """
        try:
            logger.info(f"开始对 {symbol} 进行量价分析")
            
            # 基础数据验证
            if data.empty:
                raise ValueError("股票数据为空")
            
            required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            missing_columns = [col for col in required_columns if col not in data.columns]
            if missing_columns:
                raise ValueError(f"缺少必要的数据列: {missing_columns}")
            
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
            
            # 1. 基础量价指标计算
            basic_indicators = self._calculate_basic_indicators(data)
            analysis_result['basic_indicators'] = basic_indicators
            
            # 2. 量价关系分析
            volume_price_relation = self._analyze_volume_price_relation(data)
            analysis_result['volume_price_relation'] = volume_price_relation
            
            # 3. 量价背离分析
            divergence_analysis = self._analyze_divergence(data)
            analysis_result['divergence_analysis'] = divergence_analysis
            
            # 4. 成交量模式识别
            volume_patterns = self._identify_volume_patterns(data)
            analysis_result['volume_patterns'] = volume_patterns
            
            # 5. 价量配合度分析
            price_volume_coordination = self._analyze_price_volume_coordination(data)
            analysis_result['price_volume_coordination'] = price_volume_coordination
            
            # 6. 异常成交量分析
            abnormal_volume = self._analyze_abnormal_volume(data)
            analysis_result['abnormal_volume'] = abnormal_volume
            
            # 7. 量价趋势分析
            trend_analysis = self._analyze_volume_price_trend(data)
            analysis_result['trend_analysis'] = trend_analysis
            
            # 8. 综合评分
            comprehensive_score = self._calculate_comprehensive_score(analysis_result)
            analysis_result['comprehensive_score'] = comprehensive_score
            
            # 9. 交易信号生成
            trading_signals = self._generate_trading_signals(data, analysis_result)
            analysis_result['trading_signals'] = trading_signals
            
            logger.info(f"{symbol} 量价分析完成")
            return analysis_result
            
        except Exception as e:
            logger.error(f"量价分析失败: {str(e)}")
            raise
    
    def _calculate_basic_indicators(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        计算基础量价指标
        
        Args:
            data: 股票数据
            
        Returns:
            基础指标字典
        """
        try:
            indicators = {}
            
            # 价格相关指标
            indicators['price_change'] = data['Close'].pct_change(fill_method=None)
            indicators['price_volatility'] = indicators['price_change'].rolling(20).std()
            
            # 成交量相关指标
            indicators['volume_change'] = data['Volume'].pct_change(fill_method=None)
            indicators['volume_ma'] = {}
            for period in self.volume_ma_periods:
                indicators['volume_ma'][f'ma_{period}'] = data['Volume'].rolling(period).mean()
            
            # 价格均线
            indicators['price_ma'] = {}
            for period in self.price_ma_periods:
                indicators['price_ma'][f'ma_{period}'] = data['Close'].rolling(period).mean()
            
            # 相对成交量（当日成交量/平均成交量）
            indicators['relative_volume'] = data['Volume'] / data['Volume'].rolling(20).mean()
            
            # 成交量比率（Volume Ratio）
            indicators['volume_ratio'] = data['Volume'] / data['Volume'].shift(1)
            
            # 价格振幅
            indicators['price_amplitude'] = (data['High'] - data['Low']) / data['Close'].shift(1)
            
            # 成交量加权平均价格（VWAP）
            typical_price = (data['High'] + data['Low'] + data['Close']) / 3
            indicators['vwap'] = (typical_price * data['Volume']).cumsum() / data['Volume'].cumsum()
            
            # 当前状态
            current_data = {
                'current_price': data['Close'].iloc[-1],
                'current_volume': data['Volume'].iloc[-1],
                'avg_volume_20': data['Volume'].rolling(20).mean().iloc[-1],
                'relative_volume_current': indicators['relative_volume'].iloc[-1],
                'price_change_current': indicators['price_change'].iloc[-1]
            }
            
            indicators['current_status'] = current_data
            
            return indicators
            
        except Exception as e:
            logger.error(f"基础指标计算失败: {str(e)}")
            return {}
    
    def _analyze_volume_price_relation(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        分析量价关系
        
        Args:
            data: 股票数据
            
        Returns:
            量价关系分析结果
        """
        try:
            # 计算价格变化和成交量变化的相关性
            price_change = data['Close'].pct_change(fill_method=None)
            volume_change = data['Volume'].pct_change(fill_method=None)
            
            # 滚动相关性
            rolling_correlation = price_change.rolling(self.correlation_window).corr(volume_change)
            
            # 整体相关性
            overall_correlation = price_change.corr(volume_change)
            
            # 量价配合情况分类
            volume_price_patterns = self._classify_volume_price_patterns(data)
            
            # 量价强度分析
            strength_analysis = self._analyze_volume_price_strength(data)
            
            # 量价一致性分析
            consistency_analysis = self._analyze_volume_price_consistency(data)
            
            return {
                'overall_correlation': overall_correlation,
                'rolling_correlation': rolling_correlation.dropna(),
                'current_correlation': rolling_correlation.iloc[-1] if not rolling_correlation.empty else None,
                'volume_price_patterns': volume_price_patterns,
                'strength_analysis': strength_analysis,
                'consistency_analysis': consistency_analysis
            }
            
        except Exception as e:
            logger.error(f"量价关系分析失败: {str(e)}")
            return {}
    
    def _analyze_divergence(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        分析量价背离
        
        Args:
            data: 股票数据
            
        Returns:
            背离分析结果
        """
        try:
            divergences = []
            
            # 寻找价格高低点
            price_highs = self._find_price_extremes(data, 'high')
            price_lows = self._find_price_extremes(data, 'low')
            
            # 检测顶背离（价格创新高，成交量未创新高）
            top_divergences = self._detect_top_divergence(data, price_highs)
            divergences.extend(top_divergences)
            
            # 检测底背离（价格创新低，成交量未创新低）
            bottom_divergences = self._detect_bottom_divergence(data, price_lows)
            divergences.extend(bottom_divergences)
            
            # 按时间排序
            divergences.sort(key=lambda x: x['date'])
            
            # 当前背离状态
            current_divergence = self._check_current_divergence_status(data, divergences)
            
            # 背离强度评估
            divergence_strength = self._evaluate_divergence_strength(divergences)
            
            return {
                'divergences': divergences,
                'top_divergences': top_divergences,
                'bottom_divergences': bottom_divergences,
                'current_divergence': current_divergence,
                'divergence_strength': divergence_strength,
                'total_divergences': len(divergences)
            }
            
        except Exception as e:
            logger.error(f"背离分析失败: {str(e)}")
            return {}
    
    def _identify_volume_patterns(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        识别成交量模式
        
        Args:
            data: 股票数据
            
        Returns:
            成交量模式识别结果
        """
        try:
            patterns = []
            
            # 1. 放量突破模式
            volume_breakout = self._identify_volume_breakout(data)
            patterns.extend(volume_breakout)
            
            # 2. 缩量整理模式
            volume_consolidation = self._identify_volume_consolidation(data)
            patterns.extend(volume_consolidation)
            
            # 3. 异常放量模式
            abnormal_volume = self._identify_abnormal_volume_spikes(data)
            patterns.extend(abnormal_volume)
            
            # 4. 成交量递减模式
            volume_decline = self._identify_volume_decline_pattern(data)
            patterns.extend(volume_decline)
            
            # 5. 成交量递增模式
            volume_increase = self._identify_volume_increase_pattern(data)
            patterns.extend(volume_increase)
            
            # 按时间排序
            patterns.sort(key=lambda x: x['start_date'])
            
            # 当前活跃模式
            current_patterns = [p for p in patterns if p['end_date'] >= data.index[-5]]  # 最近5天内的模式
            
            return {
                'all_patterns': patterns,
                'current_patterns': current_patterns,
                'pattern_summary': self._summarize_patterns(patterns)
            }
            
        except Exception as e:
            logger.error(f"成交量模式识别失败: {str(e)}")
            return {}
    
    def _analyze_price_volume_coordination(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        分析价量配合度
        
        Args:
            data: 股票数据
            
        Returns:
            价量配合度分析结果
        """
        try:
            # 计算价格和成交量的标准化值
            price_normalized = (data['Close'] - data['Close'].rolling(20).mean()) / data['Close'].rolling(20).std()
            volume_normalized = (data['Volume'] - data['Volume'].rolling(20).mean()) / data['Volume'].rolling(20).std()
            
            # 配合度评分
            coordination_score = self._calculate_coordination_score(price_normalized, volume_normalized)
            
            # 配合度趋势
            coordination_trend = coordination_score.rolling(10).mean()
            
            # 配合度分类
            coordination_levels = self._classify_coordination_levels(coordination_score)
            
            # 当前配合度状态
            current_coordination = {
                'score': coordination_score.iloc[-1] if not coordination_score.empty else 0,
                'trend': coordination_trend.iloc[-1] if not coordination_trend.empty else 0,
                'level': self._get_coordination_level(coordination_score.iloc[-1] if not coordination_score.empty else 0)
            }
            
            return {
                'coordination_score': coordination_score,
                'coordination_trend': coordination_trend,
                'coordination_levels': coordination_levels,
                'current_coordination': current_coordination,
                'avg_coordination': coordination_score.mean()
            }
            
        except Exception as e:
            logger.error(f"价量配合度分析失败: {str(e)}")
            return {}
    
    def _analyze_abnormal_volume(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        分析异常成交量
        
        Args:
            data: 股票数据
            
        Returns:
            异常成交量分析结果
        """
        try:
            # 计算成交量的统计特征
            volume_mean = data['Volume'].rolling(60).mean()
            volume_std = data['Volume'].rolling(60).std()
            
            # 识别异常放量
            volume_spikes = data['Volume'] > (volume_mean + self.volume_spike_threshold * volume_std)
            
            # 识别异常缩量
            volume_drops = data['Volume'] < (volume_mean - volume_std)
            
            # 异常成交量事件
            abnormal_events = []
            
            # 放量事件
            spike_dates = data.index[volume_spikes]
            for date in spike_dates:
                if date in data.index:
                    idx = data.index.get_loc(date)
                    abnormal_events.append({
                        'date': date,
                        'type': 'volume_spike',
                        'volume': data['Volume'].iloc[idx],
                        'avg_volume': volume_mean.iloc[idx],
                        'ratio': data['Volume'].iloc[idx] / volume_mean.iloc[idx],
                        'price_change': data['Close'].pct_change(fill_method=None).iloc[idx]
                    })
            
            # 缩量事件
            drop_dates = data.index[volume_drops]
            for date in drop_dates:
                if date in data.index:
                    idx = data.index.get_loc(date)
                    abnormal_events.append({
                        'date': date,
                        'type': 'volume_drop',
                        'volume': data['Volume'].iloc[idx],
                        'avg_volume': volume_mean.iloc[idx],
                        'ratio': data['Volume'].iloc[idx] / volume_mean.iloc[idx],
                        'price_change': data['Close'].pct_change(fill_method=None).iloc[idx]
                    })
            
            # 按日期排序
            abnormal_events.sort(key=lambda x: x['date'])
            
            # 最近的异常事件
            recent_events = [e for e in abnormal_events if e['date'] >= data.index[-30]]  # 最近30天
            
            return {
                'abnormal_events': abnormal_events,
                'recent_events': recent_events,
                'spike_count': len([e for e in abnormal_events if e['type'] == 'volume_spike']),
                'drop_count': len([e for e in abnormal_events if e['type'] == 'volume_drop']),
                'latest_abnormal': abnormal_events[-1] if abnormal_events else None
            }
            
        except Exception as e:
            logger.error(f"异常成交量分析失败: {str(e)}")
            return {}
    
    def _analyze_volume_price_trend(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        分析量价趋势
        
        Args:
            data: 股票数据
            
        Returns:
            量价趋势分析结果
        """
        try:
            # 价格趋势
            price_trend = self._calculate_price_trend(data)
            
            # 成交量趋势
            volume_trend = self._calculate_volume_trend(data)
            
            # 量价趋势一致性
            trend_consistency = self._analyze_trend_consistency(price_trend, volume_trend)
            
            # 趋势强度
            trend_strength = self._calculate_trend_strength(data, price_trend, volume_trend)
            
            # 趋势持续性预测
            trend_sustainability = self._predict_trend_sustainability(data, trend_consistency)
            
            return {
                'price_trend': price_trend,
                'volume_trend': volume_trend,
                'trend_consistency': trend_consistency,
                'trend_strength': trend_strength,
                'trend_sustainability': trend_sustainability,
                'overall_trend': self._determine_overall_trend(price_trend, volume_trend, trend_consistency)
            }
            
        except Exception as e:
            logger.error(f"量价趋势分析失败: {str(e)}")
            return {}
    
    def _calculate_comprehensive_score(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        计算综合评分
        
        Args:
            analysis_result: 分析结果
            
        Returns:
            综合评分结果
        """
        try:
            scores = {}
            
            # 量价关系评分 (0-100)
            relation_score = self._score_volume_price_relation(analysis_result.get('volume_price_relation', {}))
            scores['relation_score'] = relation_score
            
            # 背离风险评分 (0-100，越高风险越大)
            divergence_score = self._score_divergence_risk(analysis_result.get('divergence_analysis', {}))
            scores['divergence_risk_score'] = divergence_score
            
            # 成交量健康度评分 (0-100)
            volume_health_score = self._score_volume_health(analysis_result.get('abnormal_volume', {}))
            scores['volume_health_score'] = volume_health_score
            
            # 价量配合度评分 (0-100)
            coordination_score = self._score_coordination(analysis_result.get('price_volume_coordination', {}))
            scores['coordination_score'] = coordination_score
            
            # 趋势一致性评分 (0-100)
            trend_score = self._score_trend_consistency(analysis_result.get('trend_analysis', {}))
            scores['trend_consistency_score'] = trend_score
            
            # 综合评分计算（加权平均）
            weights = {
                'relation_score': 0.25,
                'divergence_risk_score': -0.15,  # 负权重，风险越高总分越低
                'volume_health_score': 0.20,
                'coordination_score': 0.20,
                'trend_consistency_score': 0.20
            }
            
            comprehensive_score = sum(scores[key] * weights[key] for key in weights.keys())
            comprehensive_score = max(0, min(100, comprehensive_score))  # 限制在0-100范围内
            
            # 评级
            rating = self._get_comprehensive_rating(comprehensive_score)
            
            return {
                'individual_scores': scores,
                'comprehensive_score': comprehensive_score,
                'rating': rating,
                'weights': weights
            }
            
        except Exception as e:
            logger.error(f"综合评分计算失败: {str(e)}")
            return {'comprehensive_score': 50, 'rating': 'C'}
    
    def _generate_trading_signals(self, data: pd.DataFrame, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成交易信号
        
        Args:
            data: 股票数据
            analysis_result: 分析结果
            
        Returns:
            交易信号结果
        """
        try:
            signals = []
            
            # 基于量价关系的信号
            relation_signals = self._generate_relation_signals(data, analysis_result.get('volume_price_relation', {}))
            signals.extend(relation_signals)
            
            # 基于背离的信号
            divergence_signals = self._generate_divergence_signals(data, analysis_result.get('divergence_analysis', {}))
            signals.extend(divergence_signals)
            
            # 基于成交量模式的信号
            pattern_signals = self._generate_pattern_signals(data, analysis_result.get('volume_patterns', {}))
            signals.extend(pattern_signals)
            
            # 基于异常成交量的信号
            abnormal_signals = self._generate_abnormal_volume_signals(data, analysis_result.get('abnormal_volume', {}))
            signals.extend(abnormal_signals)
            
            # 信号过滤和优化
            filtered_signals = self._filter_and_optimize_signals(signals)
            
            # 当前最强信号
            current_signal = self._get_current_strongest_signal(filtered_signals)
            
            # 信号统计
            signal_stats = self._calculate_signal_statistics(filtered_signals)
            
            return {
                'all_signals': signals,
                'filtered_signals': filtered_signals,
                'current_signal': current_signal,
                'signal_statistics': signal_stats,
                'recommendation': self._generate_recommendation(current_signal, analysis_result)
            }
            
        except Exception as e:
            logger.error(f"交易信号生成失败: {str(e)}")
            return {}
    
    # 辅助方法实现
    def _classify_volume_price_patterns(self, data: pd.DataFrame) -> List[Dict]:
        """
        分类量价模式
        
        Args:
            data: 股票数据
            
        Returns:
            量价模式列表
        """
        patterns = []
        
        price_change = data['Close'].pct_change(fill_method=None)
        volume_change = data['Volume'].pct_change(fill_method=None)
        
        for i in range(1, len(data)):
            price_chg = price_change.iloc[i]
            volume_chg = volume_change.iloc[i]
            
            if pd.isna(price_chg) or pd.isna(volume_chg):
                continue
            
            # 分类量价模式
            if price_chg > 0.02 and volume_chg > 0.2:  # 价涨量增
                pattern_type = 'price_up_volume_up'
            elif price_chg > 0.02 and volume_chg < -0.2:  # 价涨量缩
                pattern_type = 'price_up_volume_down'
            elif price_chg < -0.02 and volume_chg > 0.2:  # 价跌量增
                pattern_type = 'price_down_volume_up'
            elif price_chg < -0.02 and volume_chg < -0.2:  # 价跌量缩
                pattern_type = 'price_down_volume_down'
            else:
                pattern_type = 'neutral'
            
            patterns.append({
                'date': data.index[i],
                'pattern_type': pattern_type,
                'price_change': price_chg,
                'volume_change': volume_chg
            })
        
        return patterns
    
    def _analyze_volume_price_strength(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        分析量价强度
        
        Args:
            data: 股票数据
            
        Returns:
            量价强度分析结果
        """
        # 计算价格强度（基于价格变化和振幅）
        price_change = data['Close'].pct_change(fill_method=None).abs()
        price_amplitude = (data['High'] - data['Low']) / data['Close'].shift(1)
        price_strength = (price_change + price_amplitude) / 2
        
        # 计算成交量强度（基于相对成交量）
        volume_ma = data['Volume'].rolling(20).mean()
        volume_strength = data['Volume'] / volume_ma
        
        # 综合强度
        combined_strength = (price_strength * volume_strength).rolling(5).mean()
        
        return {
            'price_strength': price_strength,
            'volume_strength': volume_strength,
            'combined_strength': combined_strength,
            'current_strength': combined_strength.iloc[-1] if not combined_strength.empty else 0
        }
    
    def _analyze_volume_price_consistency(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        分析量价一致性
        
        Args:
            data: 股票数据
            
        Returns:
            量价一致性分析结果
        """
        price_change = data['Close'].pct_change(fill_method=None)
        volume_change = data['Volume'].pct_change(fill_method=None)
        
        # 计算方向一致性
        direction_consistency = ((price_change > 0) == (volume_change > 0)).astype(int)
        consistency_ratio = direction_consistency.rolling(20).mean()
        
        # 计算强度一致性
        price_strength = price_change.abs()
        volume_strength = volume_change.abs()
        strength_correlation = price_strength.rolling(20).corr(volume_strength)
        
        return {
            'direction_consistency': direction_consistency,
            'consistency_ratio': consistency_ratio,
            'strength_correlation': strength_correlation,
            'current_consistency': consistency_ratio.iloc[-1] if not consistency_ratio.empty else 0
        }
    
    def _find_price_extremes(self, data: pd.DataFrame, extreme_type: str, window: int = 5) -> List[Dict]:
        """
        寻找价格极值点
        
        Args:
            data: 股票数据
            extreme_type: 极值类型 ('high' 或 'low')
            window: 窗口大小
            
        Returns:
            极值点列表
        """
        extremes = []
        
        if extreme_type == 'high':
            price_series = data['High']
            for i in range(window, len(data) - window):
                if all(price_series.iloc[i] >= price_series.iloc[i-j] for j in range(1, window+1)) and \
                   all(price_series.iloc[i] >= price_series.iloc[i+j] for j in range(1, window+1)):
                    extremes.append({
                        'date': data.index[i],
                        'price': price_series.iloc[i],
                        'volume': data['Volume'].iloc[i],
                        'type': 'high',
                        'index': i
                    })
        else:  # low
            price_series = data['Low']
            for i in range(window, len(data) - window):
                if all(price_series.iloc[i] <= price_series.iloc[i-j] for j in range(1, window+1)) and \
                   all(price_series.iloc[i] <= price_series.iloc[i+j] for j in range(1, window+1)):
                    extremes.append({
                        'date': data.index[i],
                        'price': price_series.iloc[i],
                        'volume': data['Volume'].iloc[i],
                        'type': 'low',
                        'index': i
                    })
        
        return extremes
    
    def _detect_top_divergence(self, data: pd.DataFrame, price_highs: List[Dict]) -> List[Dict]:
        """
        检测顶背离
        
        Args:
            data: 股票数据
            price_highs: 价格高点列表
            
        Returns:
            顶背离列表
        """
        divergences = []
        
        for i in range(1, len(price_highs)):
            current_high = price_highs[i]
            previous_high = price_highs[i-1]
            
            # 价格创新高
            if current_high['price'] > previous_high['price']:
                # 检查成交量是否未创新高
                if current_high['volume'] < previous_high['volume'] * (1 - self.divergence_threshold):
                    divergences.append({
                        'date': current_high['date'],
                        'type': 'top_divergence',
                        'price': current_high['price'],
                        'volume': current_high['volume'],
                        'previous_price': previous_high['price'],
                        'previous_volume': previous_high['volume'],
                        'price_change_pct': (current_high['price'] - previous_high['price']) / previous_high['price'],
                        'volume_change_pct': (current_high['volume'] - previous_high['volume']) / previous_high['volume'],
                        'strength': abs((current_high['volume'] - previous_high['volume']) / previous_high['volume'])
                    })
        
        return divergences
    
    def _detect_bottom_divergence(self, data: pd.DataFrame, price_lows: List[Dict]) -> List[Dict]:
        """
        检测底背离
        
        Args:
            data: 股票数据
            price_lows: 价格低点列表
            
        Returns:
            底背离列表
        """
        divergences = []
        
        for i in range(1, len(price_lows)):
            current_low = price_lows[i]
            previous_low = price_lows[i-1]
            
            # 价格创新低
            if current_low['price'] < previous_low['price']:
                # 检查成交量是否未创新低（相对放量）
                if current_low['volume'] > previous_low['volume'] * (1 + self.divergence_threshold):
                    divergences.append({
                        'date': current_low['date'],
                        'type': 'bottom_divergence',
                        'price': current_low['price'],
                        'volume': current_low['volume'],
                        'previous_price': previous_low['price'],
                        'previous_volume': previous_low['volume'],
                        'price_change_pct': (current_low['price'] - previous_low['price']) / previous_low['price'],
                        'volume_change_pct': (current_low['volume'] - previous_low['volume']) / previous_low['volume'],
                        'strength': abs((current_low['volume'] - previous_low['volume']) / previous_low['volume'])
                    })
        
        return divergences
    
    def _check_current_divergence_status(self, data: pd.DataFrame, divergences: List[Dict]) -> Optional[Dict]:
        """
        检查当前背离状态
        
        Args:
            data: 股票数据
            divergences: 背离列表
            
        Returns:
            当前背离状态
        """
        if not divergences:
            return None
        
        # 寻找最近的背离
        recent_divergences = [d for d in divergences if d['date'] >= data.index[-30]]  # 最近30天
        
        if recent_divergences:
            latest_divergence = max(recent_divergences, key=lambda x: x['date'])
            return {
                'has_recent_divergence': True,
                'latest_divergence': latest_divergence,
                'days_since_divergence': (data.index[-1] - latest_divergence['date']).days
            }
        
        return {'has_recent_divergence': False}
    
    def _evaluate_divergence_strength(self, divergences: List[Dict]) -> Dict[str, Any]:
        """
        评估背离强度
        
        Args:
            divergences: 背离列表
            
        Returns:
            背离强度评估结果
        """
        if not divergences:
            return {'avg_strength': 0, 'max_strength': 0, 'divergence_frequency': 0}
        
        strengths = [d['strength'] for d in divergences]
        
        return {
            'avg_strength': np.mean(strengths),
            'max_strength': np.max(strengths),
            'min_strength': np.min(strengths),
            'divergence_frequency': len(divergences),
            'top_divergence_count': len([d for d in divergences if d['type'] == 'top_divergence']),
            'bottom_divergence_count': len([d for d in divergences if d['type'] == 'bottom_divergence'])
        }
    
    # 继续实现其他辅助方法...
    def _identify_volume_breakout(self, data: pd.DataFrame) -> List[Dict]:
        """
        识别放量突破模式
        
        Args:
            data: 股票数据
            
        Returns:
            放量突破模式列表
        """
        patterns = []
        volume_ma = data['Volume'].rolling(20).mean()
        price_ma = data['Close'].rolling(20).mean()
        
        for i in range(20, len(data)):
            # 成交量突破（超过平均成交量的2倍）
            if data['Volume'].iloc[i] > volume_ma.iloc[i] * 2:
                # 价格也突破均线
                if data['Close'].iloc[i] > price_ma.iloc[i] * 1.02:  # 突破2%
                    patterns.append({
                        'start_date': data.index[i],
                        'end_date': data.index[i],
                        'pattern_type': 'volume_breakout',
                        'volume_ratio': data['Volume'].iloc[i] / volume_ma.iloc[i],
                        'price_change': (data['Close'].iloc[i] - price_ma.iloc[i]) / price_ma.iloc[i],
                        'strength': min(data['Volume'].iloc[i] / volume_ma.iloc[i] / 2, 2.0)  # 限制最大强度为2
                    })
        
        return patterns
    
    def _identify_volume_consolidation(self, data: pd.DataFrame) -> List[Dict]:
        """
        识别缩量整理模式
        
        Args:
            data: 股票数据
            
        Returns:
            缩量整理模式列表
        """
        patterns = []
        volume_ma = data['Volume'].rolling(20).mean()
        
        # 寻找连续缩量的区间
        low_volume_periods = data['Volume'] < volume_ma * 0.7  # 成交量低于平均值70%
        
        # 找到连续的缩量区间
        in_consolidation = False
        start_date = None
        
        for i, is_low_volume in enumerate(low_volume_periods):
            if is_low_volume and not in_consolidation:
                # 开始缩量整理
                in_consolidation = True
                start_date = data.index[i]
            elif not is_low_volume and in_consolidation:
                # 结束缩量整理
                in_consolidation = False
                if start_date and (data.index[i-1] - start_date).days >= 3:  # 至少持续3天
                    patterns.append({
                        'start_date': start_date,
                        'end_date': data.index[i-1],
                        'pattern_type': 'volume_consolidation',
                        'duration_days': (data.index[i-1] - start_date).days,
                        'avg_volume_ratio': data.loc[start_date:data.index[i-1], 'Volume'].mean() / volume_ma.loc[start_date:data.index[i-1]].mean(),
                        'strength': 1.0
                    })
        
        return patterns
    
    def _identify_abnormal_volume_spikes(self, data: pd.DataFrame) -> List[Dict]:
        """
        识别异常放量模式
        
        Args:
            data: 股票数据
            
        Returns:
            异常放量模式列表
        """
        patterns = []
        volume_ma = data['Volume'].rolling(60).mean()
        volume_std = data['Volume'].rolling(60).std()
        
        # 异常放量阈值（平均值 + 3倍标准差）
        spike_threshold = volume_ma + 3 * volume_std
        
        for i in range(60, len(data)):
            if data['Volume'].iloc[i] > spike_threshold.iloc[i]:
                patterns.append({
                    'start_date': data.index[i],
                    'end_date': data.index[i],
                    'pattern_type': 'abnormal_volume_spike',
                    'volume': data['Volume'].iloc[i],
                    'avg_volume': volume_ma.iloc[i],
                    'volume_ratio': data['Volume'].iloc[i] / volume_ma.iloc[i],
                    'price_change': data['Close'].pct_change(fill_method=None).iloc[i],
                    'strength': min(data['Volume'].iloc[i] / volume_ma.iloc[i] / 3, 3.0)
                })
        
        return patterns
    
    def _identify_volume_decline_pattern(self, data: pd.DataFrame) -> List[Dict]:
        """
        识别成交量递减模式
        
        Args:
            data: 股票数据
            
        Returns:
            成交量递减模式列表
        """
        patterns = []
        
        # 寻找连续递减的成交量
        for i in range(5, len(data)):
            # 检查最近5天是否呈递减趋势
            recent_volumes = data['Volume'].iloc[i-4:i+1]
            if all(recent_volumes.iloc[j] >= recent_volumes.iloc[j+1] for j in range(4)):
                decline_ratio = (recent_volumes.iloc[0] - recent_volumes.iloc[-1]) / recent_volumes.iloc[0]
                if decline_ratio > 0.3:  # 递减幅度超过30%
                    patterns.append({
                        'start_date': data.index[i-4],
                        'end_date': data.index[i],
                        'pattern_type': 'volume_decline',
                        'decline_ratio': decline_ratio,
                        'start_volume': recent_volumes.iloc[0],
                        'end_volume': recent_volumes.iloc[-1],
                        'strength': min(decline_ratio, 1.0)
                    })
        
        return patterns
    
    def _identify_volume_increase_pattern(self, data: pd.DataFrame) -> List[Dict]:
        """
        识别成交量递增模式
        
        Args:
            data: 股票数据
            
        Returns:
            成交量递增模式列表
        """
        patterns = []
        
        # 寻找连续递增的成交量
        for i in range(5, len(data)):
            # 检查最近5天是否呈递增趋势
            recent_volumes = data['Volume'].iloc[i-4:i+1]
            if all(recent_volumes.iloc[j] <= recent_volumes.iloc[j+1] for j in range(4)):
                increase_ratio = (recent_volumes.iloc[-1] - recent_volumes.iloc[0]) / recent_volumes.iloc[0]
                if increase_ratio > 0.5:  # 递增幅度超过50%
                    patterns.append({
                        'start_date': data.index[i-4],
                        'end_date': data.index[i],
                        'pattern_type': 'volume_increase',
                        'increase_ratio': increase_ratio,
                        'start_volume': recent_volumes.iloc[0],
                        'end_volume': recent_volumes.iloc[-1],
                        'strength': min(increase_ratio, 2.0)
                    })
        
        return patterns
    
    def _summarize_patterns(self, patterns: List[Dict]) -> Dict[str, Any]:
        """
        总结模式统计
        
        Args:
            patterns: 模式列表
            
        Returns:
            模式统计摘要
        """
        if not patterns:
            return {}
        
        pattern_types = {}
        for pattern in patterns:
            pattern_type = pattern['pattern_type']
            if pattern_type not in pattern_types:
                pattern_types[pattern_type] = 0
            pattern_types[pattern_type] += 1
        
        return {
            'total_patterns': len(patterns),
            'pattern_types': pattern_types,
            'most_common_pattern': max(pattern_types.items(), key=lambda x: x[1])[0] if pattern_types else None,
            'avg_strength': np.mean([p.get('strength', 0) for p in patterns])
        }
    
    def _calculate_coordination_score(self, price_normalized: pd.Series, volume_normalized: pd.Series) -> pd.Series:
        """
        计算配合度评分
        
        Args:
            price_normalized: 标准化价格
            volume_normalized: 标准化成交量
            
        Returns:
            配合度评分序列
        """
        # 基于价格和成交量标准化值的乘积
        coordination = price_normalized * volume_normalized
        
        # 平滑处理
        coordination_smoothed = coordination.rolling(3).mean()
        
        return coordination_smoothed
    
    def _classify_coordination_levels(self, coordination_score: pd.Series) -> Dict[str, int]:
        """
        分类配合度水平
        
        Args:
            coordination_score: 配合度评分
            
        Returns:
            配合度水平统计
        """
        levels = {
            'excellent': 0,  # > 1.5
            'good': 0,       # 0.5 to 1.5
            'fair': 0,       # -0.5 to 0.5
            'poor': 0,       # -1.5 to -0.5
            'very_poor': 0   # < -1.5
        }
        
        for score in coordination_score.dropna():
            if score > 1.5:
                levels['excellent'] += 1
            elif score > 0.5:
                levels['good'] += 1
            elif score > -0.5:
                levels['fair'] += 1
            elif score > -1.5:
                levels['poor'] += 1
            else:
                levels['very_poor'] += 1
        
        return levels
    
    def _get_coordination_level(self, score: float) -> str:
        """
        获取配合度等级
        
        Args:
            score: 配合度评分
            
        Returns:
            配合度等级
        """
        if score > 1.5:
            return 'excellent'
        elif score > 0.5:
            return 'good'
        elif score > -0.5:
            return 'fair'
        elif score > -1.5:
            return 'poor'
        else:
            return 'very_poor'
    
    def _calculate_price_trend(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        计算价格趋势
        
        Args:
            data: 股票数据
            
        Returns:
            价格趋势信息
        """
        # 短期趋势（5日）
        short_trend = (data['Close'].iloc[-1] - data['Close'].iloc[-6]) / data['Close'].iloc[-6] if len(data) >= 6 else 0
        
        # 中期趋势（20日）
        medium_trend = (data['Close'].iloc[-1] - data['Close'].iloc[-21]) / data['Close'].iloc[-21] if len(data) >= 21 else 0
        
        # 长期趋势（60日）
        long_trend = (data['Close'].iloc[-1] - data['Close'].iloc[-61]) / data['Close'].iloc[-61] if len(data) >= 61 else 0
        
        # 趋势方向
        if short_trend > 0.02:
            short_direction = 'up'
        elif short_trend < -0.02:
            short_direction = 'down'
        else:
            short_direction = 'sideways'
        
        return {
            'short_trend': short_trend,
            'medium_trend': medium_trend,
            'long_trend': long_trend,
            'short_direction': short_direction,
            'trend_strength': abs(short_trend)
        }
    
    def _calculate_volume_trend(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        计算成交量趋势
        
        Args:
            data: 股票数据
            
        Returns:
            成交量趋势信息
        """
        # 短期成交量趋势
        recent_volume = data['Volume'].iloc[-5:].mean() if len(data) >= 5 else data['Volume'].iloc[-1]
        previous_volume = data['Volume'].iloc[-10:-5].mean() if len(data) >= 10 else data['Volume'].iloc[:-5].mean() if len(data) > 5 else recent_volume
        
        volume_trend = (recent_volume - previous_volume) / previous_volume if previous_volume > 0 else 0
        
        # 趋势方向
        if volume_trend > 0.2:
            direction = 'increasing'
        elif volume_trend < -0.2:
            direction = 'decreasing'
        else:
            direction = 'stable'
        
        return {
            'volume_trend': volume_trend,
            'direction': direction,
            'recent_avg_volume': recent_volume,
            'previous_avg_volume': previous_volume
        }
    
    def _analyze_trend_consistency(self, price_trend: Dict, volume_trend: Dict) -> Dict[str, Any]:
        """
        分析趋势一致性
        
        Args:
            price_trend: 价格趋势
            volume_trend: 成交量趋势
            
        Returns:
            趋势一致性分析
        """
        price_direction = price_trend['short_direction']
        volume_direction = volume_trend['direction']
        
        # 判断一致性
        if price_direction == 'up' and volume_direction == 'increasing':
            consistency = 'highly_consistent'
            score = 1.0
        elif price_direction == 'down' and volume_direction == 'decreasing':
            consistency = 'consistent'
            score = 0.8
        elif price_direction == 'up' and volume_direction == 'decreasing':
            consistency = 'divergent'
            score = 0.2
        elif price_direction == 'down' and volume_direction == 'increasing':
            consistency = 'potentially_reversal'
            score = 0.3
        else:
            consistency = 'neutral'
            score = 0.5
        
        return {
            'consistency': consistency,
            'score': score,
            'price_direction': price_direction,
            'volume_direction': volume_direction
        }
    
    def _calculate_trend_strength(self, data: pd.DataFrame, price_trend: Dict, volume_trend: Dict) -> Dict[str, Any]:
        """
        计算趋势强度
        
        Args:
            data: 股票数据
            price_trend: 价格趋势
            volume_trend: 成交量趋势
            
        Returns:
            趋势强度信息
        """
        # 价格趋势强度 - 放大100倍使其更直观
        price_strength = abs(price_trend['short_trend']) * 100
        
        # 成交量趋势强度 - 限制在合理范围内
        volume_strength = min(abs(volume_trend['volume_trend']), 1.0)
        
        # 综合强度 - 使用加权平均，价格权重更高
        combined_strength = (price_strength * 0.7 + volume_strength * 0.3)
        
        # 强度等级 - 调整阈值使其更合理
        if combined_strength > 3.0:
            strength_level = 'strong'
        elif combined_strength > 1.0:
            strength_level = 'moderate'
        else:
            strength_level = 'weak'
        
        return {
            'price_strength': price_strength,
            'volume_strength': volume_strength,
            'combined_strength': combined_strength,
            'strength_level': strength_level
        }
    
    def _predict_trend_sustainability(self, data: pd.DataFrame, trend_consistency: Dict) -> Dict[str, Any]:
        """
        预测趋势持续性
        
        Args:
            data: 股票数据
            trend_consistency: 趋势一致性
            
        Returns:
            趋势持续性预测
        """
        consistency_score = trend_consistency['score']
        
        # 基于一致性评分预测持续性
        if consistency_score > 0.8:
            sustainability = 'high'
            probability = 0.8
        elif consistency_score > 0.5:
            sustainability = 'moderate'
            probability = 0.6
        else:
            sustainability = 'low'
            probability = 0.3
        
        return {
            'sustainability': sustainability,
            'probability': probability,
            'based_on_consistency': consistency_score
        }
    
    def _determine_overall_trend(self, price_trend: Dict, volume_trend: Dict, trend_consistency: Dict) -> str:
        """
        确定整体趋势
        
        Args:
            price_trend: 价格趋势
            volume_trend: 成交量趋势
            trend_consistency: 趋势一致性
            
        Returns:
            整体趋势
        """
        price_direction = price_trend['short_direction']
        consistency = trend_consistency['consistency']
        
        if price_direction == 'up' and consistency in ['highly_consistent', 'consistent']:
            return 'strong_uptrend'
        elif price_direction == 'up':
            return 'weak_uptrend'
        elif price_direction == 'down' and consistency in ['highly_consistent', 'consistent']:
            return 'strong_downtrend'
        elif price_direction == 'down':
            return 'weak_downtrend'
        else:
            return 'sideways'
    
    # 评分相关方法
    def _score_volume_price_relation(self, relation_data: Dict) -> float:
        """
        量价关系评分
        
        Args:
            relation_data: 量价关系数据
            
        Returns:
            评分 (0-100)
        """
        if not relation_data:
            return 50
        
        correlation = relation_data.get('current_correlation', 0)
        consistency = relation_data.get('consistency_analysis', {}).get('current_consistency', 0.5)
        
        # 基于相关性和一致性计算评分
        score = (abs(correlation) * 50) + (consistency * 50)
        return min(100, max(0, score))
    
    def _score_divergence_risk(self, divergence_data: Dict) -> float:
        """
        背离风险评分
        
        Args:
            divergence_data: 背离数据
            
        Returns:
            风险评分 (0-100，越高风险越大)
        """
        if not divergence_data:
            return 0
        
        current_divergence = divergence_data.get('current_divergence', {})
        if current_divergence.get('has_recent_divergence', False):
            days_since = current_divergence.get('days_since_divergence', 30)
            # 越近期的背离风险越高
            risk_score = max(0, 100 - days_since * 3)
            return min(100, risk_score)
        
        return 20  # 基础风险
    
    def _score_volume_health(self, abnormal_data: Dict) -> float:
        """
        成交量健康度评分
        
        Args:
            abnormal_data: 异常成交量数据
            
        Returns:
            健康度评分 (0-100)
        """
        if not abnormal_data:
            return 70
        
        recent_events = abnormal_data.get('recent_events', [])
        total_events = len(recent_events)
        
        # 异常事件越少，健康度越高
        if total_events == 0:
            return 90
        elif total_events <= 2:
            return 70
        elif total_events <= 5:
            return 50
        else:
            return 30
    
    def _score_coordination(self, coordination_data: Dict) -> float:
        """
        价量配合度评分
        
        Args:
            coordination_data: 配合度数据
            
        Returns:
            配合度评分 (0-100)
        """
        if not coordination_data:
            return 50
        
        current_coordination = coordination_data.get('current_coordination', {})
        level = current_coordination.get('level', 'fair')
        
        level_scores = {
            'excellent': 95,
            'good': 80,
            'fair': 60,
            'poor': 40,
            'very_poor': 20
        }
        
        return level_scores.get(level, 50)
    
    def _score_trend_consistency(self, trend_data: Dict) -> float:
        """
        趋势一致性评分
        
        Args:
            trend_data: 趋势数据
            
        Returns:
            一致性评分 (0-100)
        """
        if not trend_data:
            return 50
        
        consistency = trend_data.get('trend_consistency', {})
        score = consistency.get('score', 0.5)
        
        return score * 100
    
    def _get_comprehensive_rating(self, score: float) -> str:
        """
        获取综合评级
        
        Args:
            score: 综合评分
            
        Returns:
            评级等级
        """
        if score >= 90:
            return 'A+'
        elif score >= 80:
            return 'A'
        elif score >= 70:
            return 'B+'
        elif score >= 60:
            return 'B'
        elif score >= 50:
            return 'C+'
        elif score >= 40:
            return 'C'
        elif score >= 30:
            return 'D+'
        else:
            return 'D'
    
    # 交易信号生成相关方法
    def _generate_relation_signals(self, data: pd.DataFrame, relation_data: Dict) -> List[Dict]:
        """
        基于量价关系生成信号
        
        Args:
            data: 股票数据
            relation_data: 量价关系数据
            
        Returns:
            信号列表
        """
        signals = []
        
        if not relation_data:
            return signals
        
        current_correlation = relation_data.get('current_correlation', 0)
        consistency = relation_data.get('consistency_analysis', {}).get('current_consistency', 0.5)
        
        # 强正相关且一致性高 - 买入信号
        if current_correlation > 0.6 and consistency > 0.7:
            signals.append({
                'date': data.index[-1],
                'signal_type': 'buy',
                'source': 'volume_price_relation',
                'strength': min(current_correlation * consistency, 1.0),
                'description': '量价关系良好，呈现强正相关且一致性高',
                'confidence': 0.8
            })
        
        # 负相关且一致性低 - 卖出信号
        elif current_correlation < -0.4 and consistency < 0.3:
            signals.append({
                'date': data.index[-1],
                'signal_type': 'sell',
                'source': 'volume_price_relation',
                'strength': min(abs(current_correlation) * (1 - consistency), 1.0),
                'description': '量价关系恶化，呈现负相关且一致性差',
                'confidence': 0.7
            })
        
        return signals
    
    def _generate_divergence_signals(self, data: pd.DataFrame, divergence_data: Dict) -> List[Dict]:
        """
        基于背离生成信号
        
        Args:
            data: 股票数据
            divergence_data: 背离数据
            
        Returns:
            信号列表
        """
        signals = []
        
        if not divergence_data:
            return signals
        
        current_divergence = divergence_data.get('current_divergence', {})
        
        if current_divergence.get('has_recent_divergence', False):
            latest_divergence = current_divergence.get('latest_divergence', {})
            divergence_type = latest_divergence.get('type', '')
            days_since = current_divergence.get('days_since_divergence', 30)
            
            # 近期顶背离 - 卖出信号
            if divergence_type == 'top_divergence' and days_since <= 10:
                signals.append({
                    'date': data.index[-1],
                    'signal_type': 'sell',
                    'source': 'top_divergence',
                    'strength': latest_divergence.get('strength', 0.5),
                    'description': f'检测到顶背离，{days_since}天前发生',
                    'confidence': max(0.5, 1.0 - days_since * 0.05)
                })
            
            # 近期底背离 - 买入信号
            elif divergence_type == 'bottom_divergence' and days_since <= 10:
                signals.append({
                    'date': data.index[-1],
                    'signal_type': 'buy',
                    'source': 'bottom_divergence',
                    'strength': latest_divergence.get('strength', 0.5),
                    'description': f'检测到底背离，{days_since}天前发生',
                    'confidence': max(0.5, 1.0 - days_since * 0.05)
                })
        
        return signals
    
    def _generate_pattern_signals(self, data: pd.DataFrame, pattern_data: Dict) -> List[Dict]:
        """
        基于成交量模式生成信号
        
        Args:
            data: 股票数据
            pattern_data: 模式数据
            
        Returns:
            信号列表
        """
        signals = []
        
        if not pattern_data:
            return signals
        
        current_patterns = pattern_data.get('current_patterns', [])
        
        for pattern in current_patterns:
            pattern_type = pattern.get('pattern_type', '')
            strength = pattern.get('strength', 0.5)
            
            # 放量突破 - 买入信号
            if pattern_type == 'volume_breakout':
                signals.append({
                    'date': pattern.get('start_date', data.index[-1]),
                    'signal_type': 'buy',
                    'source': 'volume_breakout',
                    'strength': strength,
                    'description': '检测到放量突破模式',
                    'confidence': 0.8
                })
            
            # 异常放量 - 关注信号
            elif pattern_type == 'abnormal_volume_spike':
                price_change = pattern.get('price_change', 0)
                if price_change > 0.03:  # 价格上涨超过3%
                    signals.append({
                        'date': pattern.get('start_date', data.index[-1]),
                        'signal_type': 'buy',
                        'source': 'abnormal_volume_with_price_up',
                        'strength': strength,
                        'description': '异常放量伴随价格上涨',
                        'confidence': 0.7
                    })
                elif price_change < -0.03:  # 价格下跌超过3%
                    signals.append({
                        'date': pattern.get('start_date', data.index[-1]),
                        'signal_type': 'sell',
                        'source': 'abnormal_volume_with_price_down',
                        'strength': strength,
                        'description': '异常放量伴随价格下跌',
                        'confidence': 0.7
                    })
        
        return signals
    
    def _generate_abnormal_volume_signals(self, data: pd.DataFrame, abnormal_data: Dict) -> List[Dict]:
        """
        基于异常成交量生成信号
        
        Args:
            data: 股票数据
            abnormal_data: 异常成交量数据
            
        Returns:
            信号列表
        """
        signals = []
        
        if not abnormal_data:
            return signals
        
        recent_events = abnormal_data.get('recent_events', [])
        
        # 分析最近的异常成交量事件
        for event in recent_events[-3:]:  # 只看最近3个事件
            event_type = event.get('type', '')
            price_change = event.get('price_change', 0)
            volume_ratio = event.get('ratio', 1)
            
            if event_type == 'volume_spike' and volume_ratio > 3:
                if price_change > 0.05:  # 大幅上涨
                    signals.append({
                        'date': event.get('date', data.index[-1]),
                        'signal_type': 'buy',
                        'source': 'massive_volume_spike_up',
                        'strength': min(volume_ratio / 3, 1.0),
                        'description': f'巨量上涨，成交量是平均值的{volume_ratio:.1f}倍',
                        'confidence': 0.75
                    })
                elif price_change < -0.05:  # 大幅下跌
                    signals.append({
                        'date': event.get('date', data.index[-1]),
                        'signal_type': 'sell',
                        'source': 'massive_volume_spike_down',
                        'strength': min(volume_ratio / 3, 1.0),
                        'description': f'巨量下跌，成交量是平均值的{volume_ratio:.1f}倍',
                        'confidence': 0.75
                    })
        
        return signals
    
    def _filter_and_optimize_signals(self, signals: List[Dict]) -> List[Dict]:
        """
        过滤和优化信号
        
        Args:
            signals: 原始信号列表
            
        Returns:
            过滤后的信号列表
        """
        if not signals:
            return []
        
        # 按日期排序
        signals.sort(key=lambda x: x['date'])
        
        # 去重：相同日期和类型的信号只保留强度最高的
        filtered_signals = []
        seen_combinations = set()
        
        for signal in signals:
            key = (signal['date'], signal['signal_type'])
            if key not in seen_combinations:
                seen_combinations.add(key)
                filtered_signals.append(signal)
            else:
                # 找到已存在的信号，比较强度
                for i, existing_signal in enumerate(filtered_signals):
                    if (existing_signal['date'] == signal['date'] and 
                        existing_signal['signal_type'] == signal['signal_type']):
                        if signal['strength'] > existing_signal['strength']:
                            filtered_signals[i] = signal
                        break
        
        # 过滤低置信度信号
        filtered_signals = [s for s in filtered_signals if s.get('confidence', 0) >= 0.5]
        
        # 过滤低强度信号
        filtered_signals = [s for s in filtered_signals if s.get('strength', 0) >= 0.3]
        
        return filtered_signals
    
    def _get_current_strongest_signal(self, signals: List[Dict]) -> Optional[Dict]:
        """
        获取当前最强信号
        
        Args:
            signals: 信号列表
            
        Returns:
            最强信号
        """
        if not signals:
            return None
        
        # 获取最近的信号
        recent_signals = [s for s in signals if s['date'] >= signals[-1]['date'] - timedelta(days=5)]
        
        if not recent_signals:
            return None
        
        # 按综合评分排序（强度 * 置信度）
        recent_signals.sort(key=lambda x: x.get('strength', 0) * x.get('confidence', 0), reverse=True)
        
        return recent_signals[0]
    
    def _calculate_signal_statistics(self, signals: List[Dict]) -> Dict[str, Any]:
        """
        计算信号统计
        
        Args:
            signals: 信号列表
            
        Returns:
            信号统计信息
        """
        if not signals:
            return {}
        
        buy_signals = [s for s in signals if s['signal_type'] == 'buy']
        sell_signals = [s for s in signals if s['signal_type'] == 'sell']
        
        return {
            'total_signals': len(signals),
            'buy_signals': len(buy_signals),
            'sell_signals': len(sell_signals),
            'avg_buy_strength': np.mean([s['strength'] for s in buy_signals]) if buy_signals else 0,
            'avg_sell_strength': np.mean([s['strength'] for s in sell_signals]) if sell_signals else 0,
            'avg_confidence': np.mean([s.get('confidence', 0) for s in signals]),
            'signal_sources': list(set([s['source'] for s in signals]))
        }
    
    def _generate_recommendation(self, current_signal: Optional[Dict], analysis_result: Dict) -> Dict[str, Any]:
        """
        生成投资建议
        
        Args:
            current_signal: 当前最强信号
            analysis_result: 分析结果
            
        Returns:
            投资建议
        """
        comprehensive_score = analysis_result.get('comprehensive_score', {}).get('comprehensive_score', 50)
        rating = analysis_result.get('comprehensive_score', {}).get('rating', 'C')
        
        if not current_signal:
            return {
                'action': 'hold',
                'confidence': 0.5,
                'reason': '当前无明确信号，建议观望',
                'risk_level': 'medium',
                'score_based_advice': f'综合评分{comprehensive_score:.1f}分（{rating}级）'
            }
        
        signal_type = current_signal['signal_type']
        signal_strength = current_signal['strength']
        signal_confidence = current_signal.get('confidence', 0.5)
        
        # 基于信号类型和强度生成建议
        if signal_type == 'buy':
            if signal_strength > 0.8 and signal_confidence > 0.8:
                action = 'strong_buy'
                risk_level = 'low'
            elif signal_strength > 0.6:
                action = 'buy'
                risk_level = 'medium'
            else:
                action = 'weak_buy'
                risk_level = 'medium_high'
        else:  # sell
            if signal_strength > 0.8 and signal_confidence > 0.8:
                action = 'strong_sell'
                risk_level = 'low'
            elif signal_strength > 0.6:
                action = 'sell'
                risk_level = 'medium'
            else:
                action = 'weak_sell'
                risk_level = 'medium_high'
        
        return {
            'action': action,
            'confidence': signal_confidence,
            'reason': current_signal.get('description', ''),
            'risk_level': risk_level,
            'signal_source': current_signal.get('source', ''),
            'score_based_advice': f'综合评分{comprehensive_score:.1f}分（{rating}级）',
            'signal_date': current_signal.get('date')
        }
    
    def get_analysis_summary(self, analysis_result: Dict[str, Any]) -> str:
        """
        获取分析摘要
        
        Args:
            analysis_result: 分析结果
            
        Returns:
            分析摘要文本
        """
        try:
            symbol = analysis_result.get('symbol', 'Unknown')
            comprehensive_score = analysis_result.get('comprehensive_score', {}).get('comprehensive_score', 50)
            rating = analysis_result.get('comprehensive_score', {}).get('rating', 'C')
            
            # 当前状态
            current_status = analysis_result.get('basic_indicators', {}).get('current_status', {})
            current_price = current_status.get('current_price', 0)
            relative_volume = current_status.get('relative_volume_current', 1)
            
            # 趋势分析
            trend_analysis = analysis_result.get('trend_analysis', {})
            overall_trend = trend_analysis.get('overall_trend', 'unknown')
            
            # 交易建议
            recommendation = analysis_result.get('trading_signals', {}).get('recommendation', {})
            action = recommendation.get('action', 'hold')
            confidence = recommendation.get('confidence', 0.5)
            
            summary = f"""
【{symbol} 量价分析报告】

综合评分：{comprehensive_score:.1f}分 ({rating}级)
当前价格：{current_price:.2f}
相对成交量：{relative_volume:.2f}倍
整体趋势：{overall_trend}

投资建议：{action} (置信度：{confidence:.1%})
建议理由：{recommendation.get('reason', '无特殊信号')}
风险等级：{recommendation.get('risk_level', 'medium')}

分析时间：{analysis_result.get('analysis_date', datetime.now()).strftime('%Y-%m-%d %H:%M:%S')}
            """.strip()
            
            return summary
            
        except Exception as e:
            logger.error(f"生成分析摘要失败: {str(e)}")
            return f"分析摘要生成失败: {str(e)}"
    
    def export_analysis_to_dict(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        导出分析结果为字典格式
        
        Args:
            analysis_result: 分析结果
            
        Returns:
            导出的字典
        """
        try:
            # 简化的分析结果，便于存储和传输
            export_data = {
                'symbol': analysis_result.get('symbol'),
                'analysis_date': analysis_result.get('analysis_date'),
                'data_range': analysis_result.get('data_range'),
                'comprehensive_score': analysis_result.get('comprehensive_score', {}).get('comprehensive_score'),
                'rating': analysis_result.get('comprehensive_score', {}).get('rating'),
                'current_status': analysis_result.get('basic_indicators', {}).get('current_status'),
                'overall_trend': analysis_result.get('trend_analysis', {}).get('overall_trend'),
                'recommendation': analysis_result.get('trading_signals', {}).get('recommendation'),
                'key_signals': analysis_result.get('trading_signals', {}).get('filtered_signals', [])[-5:],  # 最近5个信号
                'divergence_count': analysis_result.get('divergence_analysis', {}).get('total_divergences', 0),
                'abnormal_volume_events': len(analysis_result.get('abnormal_volume', {}).get('recent_events', [])),
                'volume_price_correlation': analysis_result.get('volume_price_relation', {}).get('current_correlation')
            }
            
            return export_data
            
        except Exception as e:
            logger.error(f"导出分析结果失败: {str(e)}")
            return {'error': str(e)}


if __name__ == "__main__":
    # 测试代码
    import yfinance as yf
    
    # 测试配置
    test_config = {
        'volume_ma_periods': [5, 10, 20, 60],
        'price_ma_periods': [5, 10, 20, 60],
        'divergence_threshold': 0.15,
        'volume_spike_threshold': 2.0,
        'correlation_window': 20
    }
    
    # 创建分析器
    analyzer = VolumePriceAnalyzer(test_config)
    
    # 获取测试数据
    try:
        ticker = yf.Ticker("AAPL")
        data = ticker.history(period="1y")
        
        if not data.empty:
            # 进行分析
            result = analyzer.analyze_stock("AAPL", data)
            
            # 打印摘要
            summary = analyzer.get_analysis_summary(result)
            print(summary)
            
            # 导出结果
            export_data = analyzer.export_analysis_to_dict(result)
            print("\n导出数据示例:")
            for key, value in export_data.items():
                if key not in ['key_signals']:  # 跳过复杂的信号数据
                    print(f"{key}: {value}")
        else:
            print("无法获取测试数据")
            
    except Exception as e:
        print(f"测试失败: {str(e)}")
        print("请确保已安装 yfinance: pip install yfinance")