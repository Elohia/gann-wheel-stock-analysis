#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统功能测试脚本

用于测试江恩轮中轮+量价分析系统的基本功能
"""

import sys
import os
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from main import StockAnalysisSystem
from src.utils.logger_setup import setup_logger

def test_system_initialization():
    """
    测试系统初始化
    """
    print("=== 测试系统初始化 ===")
    try:
        # 使用示例配置文件
        system = StockAnalysisSystem("config.example.yaml")
        print("✓ 系统初始化成功")
        return system
    except Exception as e:
        print(f"✗ 系统初始化失败: {e}")
        return None

def test_data_fetcher(system):
    """
    测试数据获取功能
    """
    print("\n=== 测试数据获取功能 ===")
    try:
        # 测试连接
        connections = system.data_fetcher.test_connections()
        print(f"数据源连接测试结果: {connections}")
        
        # 测试获取数据（使用一个常见的股票代码）
        test_symbol = "000001.SZ"  # 平安银行
        print(f"尝试获取股票 {test_symbol} 的数据...")
        
        success = system.fetch_and_store_data(test_symbol, "1y")
        if success:
            print(f"✓ 股票 {test_symbol} 数据获取成功")
        else:
            print(f"✗ 股票 {test_symbol} 数据获取失败")
            
    except Exception as e:
        print(f"✗ 数据获取测试失败: {e}")

def test_analysis_modules(system):
    """
    测试分析模块
    """
    print("\n=== 测试分析模块 ===")
    try:
        # 创建测试数据
        import pandas as pd
        import numpy as np
        from datetime import datetime, timedelta
        
        # 生成模拟股票数据
        dates = pd.date_range(start=datetime.now() - timedelta(days=100), 
                             end=datetime.now(), freq='D')
        
        np.random.seed(42)  # 确保结果可重现
        prices = 100 + np.cumsum(np.random.randn(len(dates)) * 0.5)
        volumes = np.random.randint(1000000, 10000000, len(dates))
        
        test_data = pd.DataFrame({
            'open': prices * (1 + np.random.randn(len(dates)) * 0.01),
            'high': prices * (1 + np.abs(np.random.randn(len(dates))) * 0.02),
            'low': prices * (1 - np.abs(np.random.randn(len(dates))) * 0.02),
            'close': prices,
            'volume': volumes
        }, index=dates)
        
        print(f"生成测试数据: {len(test_data)} 条记录")
        
        # 测试江恩轮中轮分析
        print("测试江恩轮中轮分析...")
        try:
            gann_result = system.gann_wheel.analyze(test_data)
            print("✓ 江恩轮中轮分析完成")
            if gann_result:
                print(f"  - 分析结果包含 {len(gann_result)} 个项目")
        except Exception as e:
            print(f"✗ 江恩轮中轮分析失败: {e}")
        
        # 测试量价分析
        print("测试量价分析...")
        try:
            vp_result = system.volume_price_analyzer.analyze(test_data)
            print("✓ 量价分析完成")
            if vp_result:
                print(f"  - 分析结果包含 {len(vp_result)} 个项目")
        except Exception as e:
            print(f"✗ 量价分析失败: {e}")
            
    except Exception as e:
        print(f"✗ 分析模块测试失败: {e}")

def test_database_operations(system):
    """
    测试数据库操作
    """
    print("\n=== 测试数据库操作 ===")
    try:
        # 测试数据库连接
        stats = system.db_manager.get_database_stats()
        print(f"✓ 数据库连接成功")
        print(f"  - 数据库统计: {stats}")
        
    except Exception as e:
        print(f"✗ 数据库操作测试失败: {e}")

def main():
    """
    主测试函数
    """
    print("江恩轮中轮+量价分析系统 - 功能测试")
    print("=" * 50)
    
    # 设置基本日志
    setup_logger({'level': 'INFO'})
    
    # 测试系统初始化
    system = test_system_initialization()
    if system is None:
        print("\n系统初始化失败，无法继续测试")
        return
    
    # 测试数据库操作
    test_database_operations(system)
    
    # 测试数据获取功能
    test_data_fetcher(system)
    
    # 测试分析模块
    test_analysis_modules(system)
    
    print("\n=== 测试完成 ===")
    print("如果看到错误，请检查配置文件和依赖包是否正确安装")

if __name__ == "__main__":
    main()