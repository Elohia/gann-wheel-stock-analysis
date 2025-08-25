#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
江恩轮中轮+量价分析系统使用示例

本脚本展示了如何使用系统进行股票分析的完整流程
"""

import sys
import os
from pathlib import Path
import json

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from main import StockAnalysisSystem
from src.utils.logger_setup import setup_logger

def example_single_stock_analysis():
    """
    单只股票分析示例
    """
    print("=== 单只股票分析示例 ===")
    
    # 初始化系统
    system = StockAnalysisSystem()
    
    # 要分析的股票代码
    stock_symbol = "000001.SZ"  # 平安银行
    
    print(f"\n1. 获取股票 {stock_symbol} 的数据...")
    success = system.fetch_and_store_data(stock_symbol, "2y")
    
    if success:
        print(f"✓ 数据获取成功")
        
        print(f"\n2. 执行江恩轮中轮分析...")
        gann_result = system.analyze_stock(stock_symbol, "gann")
        
        if gann_result and 'gann' in gann_result:
            print("✓ 江恩轮中轮分析完成")
            print("主要分析结果:")
            gann_data = gann_result['gann']
            
            # 显示关键信息
            if 'time_cycles' in gann_data:
                print(f"  - 时间周期分析: {len(gann_data['time_cycles'])} 个周期")
            if 'price_cycles' in gann_data:
                print(f"  - 价格轮回分析: {len(gann_data['price_cycles'])} 个轮回")
            if 'support_resistance' in gann_data:
                levels = gann_data['support_resistance']
                print(f"  - 支撑位: {levels.get('support', [])}")
                print(f"  - 阻力位: {levels.get('resistance', [])}")
        
        print(f"\n3. 执行量价分析...")
        vp_result = system.analyze_stock(stock_symbol, "volume_price")
        
        if vp_result and 'volume_price' in vp_result:
            print("✓ 量价分析完成")
            print("主要分析结果:")
            vp_data = vp_result['volume_price']
            
            # 显示关键信息
            if 'volume_price_relation' in vp_data:
                relation = vp_data['volume_price_relation']
                print(f"  - 量价关系: {relation.get('trend', 'N/A')}")
                print(f"  - 配合度评分: {relation.get('coordination_score', 'N/A')}")
            
            if 'divergence_analysis' in vp_data:
                divergence = vp_data['divergence_analysis']
                print(f"  - 量价背离: {divergence.get('has_divergence', False)}")
            
            if 'trading_signals' in vp_data:
                signals = vp_data['trading_signals']
                if isinstance(signals, list):
                    print(f"  - 交易信号: {len(signals)} 个信号")
                    for signal in signals[:3]:  # 显示前3个信号
                        print(f"    * {signal.get('type', 'N/A')}: {signal.get('signal', 'N/A')} (强度: {signal.get('strength', 'N/A')})")
                else:
                    print(f"  - 交易信号: {signals}")
        
        print(f"\n4. 执行综合分析...")
        full_result = system.analyze_stock(stock_symbol, "all")
        
        if full_result:
            print("✓ 综合分析完成")
            print(f"分析结果包含: {list(full_result.keys())}")
    
    else:
        print(f"✗ 数据获取失败，无法进行分析")

def example_batch_analysis():
    """
    批量股票分析示例
    """
    print("\n\n=== 批量股票分析示例 ===")
    
    # 初始化系统
    system = StockAnalysisSystem()
    
    # 要分析的股票列表
    stock_symbols = [
        "000001.SZ",  # 平安银行
        "000002.SZ",  # 万科A
        "600000.SH",  # 浦发银行
    ]
    
    print(f"\n批量分析 {len(stock_symbols)} 只股票...")
    
    for i, symbol in enumerate(stock_symbols, 1):
        print(f"\n{i}. 分析股票 {symbol}...")
        
        # 获取数据
        success = system.fetch_and_store_data(symbol, "1y")
        
        if success:
            # 执行分析
            result = system.analyze_stock(symbol, "all")
            
            if result:
                print(f"  ✓ {symbol} 分析完成")
                
                # 简要显示结果
                if 'gann' in result:
                    gann_data = result['gann']
                    if 'prediction' in gann_data:
                        pred = gann_data['prediction']
                        print(f"    江恩预测: {pred.get('trend', 'N/A')} (置信度: {pred.get('confidence', 'N/A')})")
                
                if 'volume_price' in result:
                    vp_data = result['volume_price']
                    if 'comprehensive_rating' in vp_data:
                        rating = vp_data['comprehensive_rating']
                        print(f"    量价评级: {rating.get('rating', 'N/A')} (评分: {rating.get('score', 'N/A')})")
            else:
                print(f"  ✗ {symbol} 分析失败")
        else:
            print(f"  ✗ {symbol} 数据获取失败")

def example_data_management():
    """
    数据管理示例
    """
    print("\n\n=== 数据管理示例 ===")
    
    # 初始化系统
    system = StockAnalysisSystem()
    
    print("\n1. 查看数据库统计信息...")
    try:
        stats = system.db_manager.get_database_stats()
        print(f"数据库统计: {stats}")
    except Exception as e:
        print(f"获取统计信息失败: {e}")
    
    print("\n2. 测试数据源连接...")
    try:
        connections = system.data_fetcher.test_connections()
        print("数据源连接状态:")
        for source, status in connections.items():
            status_text = "✓ 连接成功" if status else "✗ 连接失败"
            print(f"  {source}: {status_text}")
    except Exception as e:
        print(f"测试连接失败: {e}")
    
    print("\n3. 更新所有数据...")
    try:
        system.update_all_data()
        print("✓ 数据更新完成")
    except Exception as e:
        print(f"数据更新失败: {e}")

def example_configuration():
    """
    配置管理示例
    """
    print("\n\n=== 配置管理示例 ===")
    
    # 初始化系统
    system = StockAnalysisSystem()
    
    print("\n1. 查看当前配置...")
    config = system.config_manager.get_config()
    
    print("主要配置项:")
    print(f"  - 数据源: {list(config.get('data_sources', {}).keys())}")
    print(f"  - 数据库类型: {config.get('database', {}).get('type', 'N/A')}")
    print(f"  - 日志级别: {config.get('logging', {}).get('level', 'N/A')}")
    
    print("\n2. 获取特定配置...")
    db_config = system.config_manager.get_database_config()
    print(f"数据库配置: {db_config}")
    
    tushare_config = system.config_manager.get_data_source_config('tushare')
    print(f"Tushare配置: {tushare_config}")

def main():
    """
    主函数 - 运行所有示例
    """
    print("江恩轮中轮+量价分析系统 - 使用示例")
    print("=" * 60)
    
    # 设置日志
    setup_logger({'level': 'INFO'})
    
    try:
        # 运行各种示例
        example_configuration()
        example_data_management()
        example_single_stock_analysis()
        example_batch_analysis()
        
        print("\n" + "=" * 60)
        print("所有示例运行完成！")
        print("\n使用提示:")
        print("1. 确保已正确配置 config/config.yaml 文件")
        print("2. 安装所需的Python依赖包: pip install -r requirements.txt")
        print("3. 如需使用Tushare，请在配置文件中设置API token")
        print("4. 查看日志文件了解详细的运行信息")
        
    except Exception as e:
        print(f"\n运行示例时发生错误: {e}")
        print("请检查配置文件和依赖包是否正确安装")

if __name__ == "__main__":
    main()