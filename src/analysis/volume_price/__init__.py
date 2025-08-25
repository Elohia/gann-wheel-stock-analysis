# -*- coding: utf-8 -*-
"""
量价分析模块

该模块提供股票量价关系分析功能，包括：
- 成交量与价格关系分析
- 量价背离检测
- 成交量模式识别
- 量价配合度分析
- 异常成交量识别
- 量价趋势分析
- 交易信号生成
"""

from .volume_price_analyzer import VolumePriceAnalyzer

__all__ = ['VolumePriceAnalyzer']