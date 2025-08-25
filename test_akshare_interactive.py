#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试akshare数据源和交互式功能

验证系统能否正确使用akshare获取数据并进行分析

Author: AI Assistant
Date: 2024
"""

import sys
import os
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from main import StockAnalysisSystem
from src.utils.logger_setup import setup_logger
from loguru import logger


def test_akshare_data_source():
    """
    测试akshare数据源功能
    """
    print("🧪 测试akshare数据源功能")
    print("=" * 50)
    
    # 设置日志
    logging_config = {
        'level': 'INFO',
        'format': '{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}',
        'file': 'logs/test_akshare.log'
    }
    setup_logger(logging_config)
    
    try:
        # 初始化系统
        print("🚀 正在初始化分析系统...")
        system = StockAnalysisSystem()
        print("✅ 系统初始化成功")
        
        # 测试股票代码列表
        test_stocks = [
            "000001",      # 平安银行（深交所）
            "000001.SZ",   # 平安银行（完整格式）
            "600036",      # 招商银行（上交所）
            "600036.SH",   # 招商银行（完整格式）
        ]
        
        for stock_code in test_stocks:
            print(f"\n📊 测试股票: {stock_code}")
            print("-" * 30)
            
            try:
                # 获取数据
                print(f"📥 正在获取 {stock_code} 的数据...")
                success = system.fetch_and_store_data(stock_code, "3mo")
                
                if success:
                    print(f"✅ {stock_code} 数据获取成功")
                    
                    # 执行分析
                    print(f"🔍 正在分析 {stock_code}...")
                    results = system.analyze_stock(stock_code, "all")
                    
                    if results:
                        print(f"✅ {stock_code} 分析完成")
                        
                        # 显示分析结果摘要
                        if 'gann' in results:
                            gann_data = results['gann']
                            print(f"   🔮 江恩分析: 包含 {len(gann_data.get('time_cycles', []))} 个时间周期")
                        
                        if 'volume_price' in results:
                            vp_data = results['volume_price']
                            if 'volume_price_relation' in vp_data:
                                relation = vp_data['volume_price_relation']
                                trend = relation.get('trend', 'N/A')
                                print(f"   📈 量价关系: {trend}")
                    else:
                        print(f"❌ {stock_code} 分析失败")
                else:
                    print(f"❌ {stock_code} 数据获取失败")
                    
            except Exception as e:
                print(f"❌ 处理 {stock_code} 时发生错误: {str(e)}")
                logger.error(f"处理股票 {stock_code} 时发生错误: {str(e)}")
        
        print("\n🎉 akshare数据源测试完成")
        
    except Exception as e:
        print(f"❌ 系统初始化失败: {str(e)}")
        logger.error(f"系统初始化失败: {str(e)}")


def test_stock_code_validation():
    """
    测试股票代码验证功能
    """
    print("\n🧪 测试股票代码验证功能")
    print("=" * 50)
    
    # 导入交互式分析器的验证函数
    from interactive_analysis import InteractiveAnalyzer
    
    analyzer = InteractiveAnalyzer()
    
    test_codes = [
        ("000001", True, "000001.SZ"),      # 6位数字，深交所
        ("600036", True, "600036.SH"),      # 6位数字，上交所
        ("000001.SZ", True, "000001.SZ"),   # 完整格式，深交所
        ("600036.SH", True, "600036.SH"),   # 完整格式，上交所
        ("300", True, "300300.SZ"),         # 3位数字，创业板
        ("abc", False, "abc"),              # 无效格式
        ("", False, ""),                    # 空字符串
        ("12345", False, "12345"),          # 5位数字
    ]
    
    for code, expected_valid, expected_result in test_codes:
        is_valid, result = analyzer._validate_stock_code(code)
        status = "✅" if is_valid == expected_valid and result == expected_result else "❌"
        print(f"{status} 输入: '{code}' -> 有效: {is_valid}, 结果: '{result}'")
        
        if is_valid != expected_valid or result != expected_result:
            print(f"   期望: 有效: {expected_valid}, 结果: '{expected_result}'")


def test_data_source_priority():
    """
    测试数据源优先级配置
    """
    print("\n🧪 测试数据源优先级配置")
    print("=" * 50)
    
    try:
        # 读取配置文件
        import yaml
        config_path = Path("config/config.yaml")
        
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            data_sources = config.get('data_sources', {})
            
            # 显示数据源配置
            print("📋 数据源配置:")
            for source_name, source_config in data_sources.items():
                enabled = source_config.get('enabled', False)
                priority = source_config.get('priority', 'N/A')
                status = "✅ 启用" if enabled else "❌ 禁用"
                print(f"   {source_name}: {status}, 优先级: {priority}")
            
            # 验证akshare是否为最高优先级
            akshare_config = data_sources.get('akshare', {})
            if akshare_config.get('enabled', False) and akshare_config.get('priority', 999) == 1:
                print("✅ akshare已正确设置为最高优先级数据源")
            else:
                print("❌ akshare未设置为最高优先级数据源")
        else:
            print("❌ 配置文件不存在")
            
    except Exception as e:
        print(f"❌ 读取配置文件失败: {str(e)}")


def main():
    """
    主测试函数
    """
    print("🎯 江恩轮中轮+量价分析系统 - akshare数据源测试")
    print("=" * 60)
    
    # 测试数据源优先级配置
    test_data_source_priority()
    
    # 测试股票代码验证
    test_stock_code_validation()
    
    # 测试akshare数据源
    test_akshare_data_source()
    
    print("\n🎉 所有测试完成！")
    print("💡 如需交互式使用，请运行: python interactive_analysis.py")


if __name__ == "__main__":
    main()