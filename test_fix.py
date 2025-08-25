#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修复后的预测信息和趋势强度显示
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import StockAnalysisSystem
from loguru import logger

def test_analysis_fix():
    """
    测试修复后的分析功能
    """
    try:
        # 初始化系统
        system = StockAnalysisSystem()
        
        # 测试股票代码
        symbol = '000001'
        
        print(f"\n🔍 开始测试 {symbol} 的分析功能...")
        
        # 获取股票数据
        data = system.data_fetcher.fetch_stock_data(symbol, period='1y')
        if data is None or data.empty:
            print(f"无法获取股票 {symbol} 的数据")
            return
        
        print(f"✅ 成功获取 {symbol} 数据，共 {len(data)} 条记录")
        
        # 江恩轮中轮分析
        print("\n📊 执行江恩轮中轮分析...")
        gann_result = system.gann_wheel.analyze_stock(symbol, data)
        
        # 量价分析
        print("📈 执行量价分析...")
        volume_result = system.volume_price_analyzer.analyze_stock(symbol, data)
        
        # 检查江恩分析结果
        print("\n🔮 江恩轮中轮分析结果:")
        if 'predictions' in gann_result:
            predictions = gann_result['predictions']
            if predictions and 'combined_prediction' in predictions:
                combined = predictions['combined_prediction']
                print(f"  📍 预测方向: {combined.get('direction', '暂无数据')}")
                print(f"  🎯 目标价位: {combined.get('target_price', '暂无数据')}")
                print(f"  📊 整体趋势: {combined.get('overall_trend', '暂无数据')}")
                print(f"  💪 趋势强度: {combined.get('trend_strength', '暂无数据')}")
            else:
                print("  ❌ 预测信息: 暂无数据")
        else:
            print("  ❌ 江恩分析结果中没有预测信息")
        
        # 检查量价分析结果
        print("\n📈 量价分析结果:")
        if 'trend_analysis' in volume_result:
            trend = volume_result['trend_analysis']
            if 'trend_strength' in trend:
                strength = trend['trend_strength']
                print(f"  💪 价格强度: {strength.get('price_strength', '暂无数据')}")
                print(f"  📊 成交量强度: {strength.get('volume_strength', '暂无数据')}")
                print(f"  🔥 综合强度: {strength.get('combined_strength', '暂无数据')}")
                print(f"  📈 强度等级: {strength.get('strength_level', '暂无数据')}")
            else:
                print("  ❌ 趋势强度信息缺失")
            
            print(f"  📊 整体趋势: {trend.get('overall_trend', '暂无数据')}")
        else:
            print("  ❌ 量价分析结果中没有趋势分析")
        
        print("\n✅ 测试完成！")
        
    except Exception as e:
        logger.error(f"测试过程中发生错误: {str(e)}")
        print(f"❌ 测试失败: {str(e)}")

if __name__ == "__main__":
    test_analysis_fix()