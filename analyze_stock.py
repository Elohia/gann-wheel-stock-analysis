#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票分析命令行工具

使用akshare数据源进行股票分析的命令行工具
用法: python analyze_stock.py [股票代码]

Author: AI Assistant
Date: 2024
"""

import sys
import os
from pathlib import Path
import argparse

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from main import StockAnalysisSystem
from src.utils.logger_setup import setup_logger
from loguru import logger


def validate_stock_code(code: str) -> tuple[bool, str]:
    """
    验证并标准化股票代码
    
    Args:
        code: 股票代码
        
    Returns:
        tuple: (是否有效, 标准化后的代码)
    """
    import re
    
    if not code:
        return False, ""
    
    # 移除空格并转换为大写
    code = code.strip().upper()
    
    # 检查是否已包含交易所后缀
    if re.match(r'^\d{6}\.(SZ|SH)$', code):
        return True, code
    
    # 6位数字，自动判断交易所
    if re.match(r'^\d{6}$', code):
        # 根据代码前缀判断交易所
        if code.startswith(('000', '002', '300')):
            return True, f"{code}.SZ"  # 深交所
        elif code.startswith(('600', '601', '603', '605')):
            return True, f"{code}.SH"  # 上交所
        else:
            # 默认深交所
            return True, f"{code}.SZ"
    
    return False, code


def display_analysis_results(symbol: str, results: dict) -> None:
    """
    显示分析结果
    
    Args:
        symbol: 股票代码
        results: 分析结果
    """
    print(f"\n📊 {symbol} 分析结果")
    print("=" * 50)
    
    # 江恩轮中轮分析结果
    if 'gann' in results:
        gann_data = results['gann']
        print("\n🔮 江恩轮中轮分析:")
        
        # 时间分析结果
        if 'time_analysis' in gann_data:
            time_analysis = gann_data['time_analysis']
            if isinstance(time_analysis, dict):
                cycles_found = time_analysis.get('cycles_found', [])
                if cycles_found and isinstance(cycles_found, list):
                    print(f"  📅 时间周期: {len(cycles_found)} 个周期")
                    dominant = time_analysis.get('dominant_cycle')
                    if dominant and isinstance(dominant, dict):
                        print(f"     主导周期: {dominant.get('cycle_days', 'N/A')} 天 (强度: {dominant.get('strength', 0):.2f})")
                else:
                    print("  📅 时间周期: 暂无数据")
            else:
                print("  📅 时间周期: 暂无数据")
        
        # 价格分析结果
        if 'price_analysis' in gann_data:
            price_analysis = gann_data['price_analysis']
            if isinstance(price_analysis, dict):
                key_levels = price_analysis.get('key_levels', [])
                if key_levels and isinstance(key_levels, list):
                    print(f"  💰 价格轮回: {len(key_levels)} 个关键位")
                    price_range = price_analysis.get('price_range', 0)
                    if price_range > 0:
                        print(f"     价格区间: {price_range:.2f}")
                else:
                    print("  💰 价格轮回: 暂无数据")
            else:
                print("  💰 价格轮回: 暂无数据")
        
        # 关键位分析
        if 'key_levels' in gann_data:
            key_levels = gann_data['key_levels']
            if isinstance(key_levels, dict):
                supports = key_levels.get('key_supports', [])
                resistances = key_levels.get('key_resistances', [])
                if supports and isinstance(supports, list):
                    # 提取价格值
                    support_prices = [level.get('price', 0) if isinstance(level, dict) else level for level in supports[:3]]
                    support_str = [f"{price:.2f}" for price in support_prices if isinstance(price, (int, float))]
                    if support_str:
                        print(f"  📈 支撑位: {support_str}")
                if resistances and isinstance(resistances, list):
                    # 提取价格值
                    resistance_prices = [level.get('price', 0) if isinstance(level, dict) else level for level in resistances[:3]]
                    resistance_str = [f"{price:.2f}" for price in resistance_prices if isinstance(price, (int, float))]
                    if resistance_str:
                        print(f"  📉 阻力位: {resistance_str}")
                if not supports and not resistances:
                    print("  📊 支撑阻力位: 暂无数据")
            else:
                print("  📊 支撑阻力位: 暂无数据")
    
    # 量价分析结果
    if 'volume_price' in results:
        vp_data = results['volume_price']
        print("\n📈 量价分析:")
        
        if 'volume_price_relation' in vp_data:
            relation = vp_data['volume_price_relation']
            if isinstance(relation, dict):
                trend = relation.get('trend', 'N/A')
                score = relation.get('coordination_score', 'N/A')
                print(f"  🔄 量价关系: {trend}")
                if isinstance(score, (int, float)):
                    print(f"  ⭐ 配合度评分: {score:.2f}")
                else:
                    print(f"  ⭐ 配合度评分: {score}")
        
        if 'divergence_analysis' in vp_data:
            divergence = vp_data['divergence_analysis']
            if isinstance(divergence, dict):
                has_divergence = divergence.get('has_divergence', False)
                divergence_type = divergence.get('divergence_type', 'N/A')
                print(f"  ⚠️  量价背离: {'是' if has_divergence else '否'}")
                if has_divergence:
                    print(f"     背离类型: {divergence_type}")
        
        # 处理交易信号
        if 'trading_signals' in vp_data:
            signals_data = vp_data['trading_signals']
            
            # 如果是复杂的信号数据结构
            if isinstance(signals_data, dict):
                # 获取推荐信息
                if 'recommendation' in signals_data:
                    rec = signals_data['recommendation']
                    action = rec.get('action', 'N/A')
                    confidence = rec.get('confidence', 0)
                    reason = rec.get('reason', 'N/A')
                    risk_level = rec.get('risk_level', 'N/A')
                    score_advice = rec.get('score_based_advice', 'N/A')
                    
                    print(f"  🎯 交易建议: {action.upper()}")
                    print(f"     信心度: {confidence:.1%}")
                    print(f"     理由: {reason}")
                    print(f"     风险等级: {risk_level}")
                    print(f"     综合评分: {score_advice}")
                
                # 获取信号统计
                if 'signal_statistics' in signals_data:
                    stats = signals_data['signal_statistics']
                    if isinstance(stats, dict) and stats:
                        total = stats.get('total_signals', 0)
                        buy_signals = stats.get('buy_signals', 0)
                        sell_signals = stats.get('sell_signals', 0)
                        print(f"  📊 信号统计: 总计{total}个 (买入{buy_signals}个, 卖出{sell_signals}个)")
                
                # 获取当前信号
                if 'current_signal' in signals_data:
                    current = signals_data['current_signal']
                    if current and isinstance(current, dict):
                        signal_type = current.get('signal_type', 'N/A')
                        strength = current.get('strength', 0)
                        description = current.get('description', 'N/A')
                        print(f"  🔔 当前信号: {signal_type.upper()}")
                        print(f"     强度: {strength:.2f}")
                        print(f"     描述: {description}")
            
            # 如果是简单的信号列表
            elif isinstance(signals_data, list) and signals_data:
                print(f"  🎯 交易信号: {len(signals_data)} 个")
                for i, signal in enumerate(signals_data[:3], 1):
                    if isinstance(signal, dict):
                        signal_type = signal.get('signal_type', signal.get('type', 'N/A'))
                        strength = signal.get('strength', 'N/A')
                        description = signal.get('description', 'N/A')
                        if isinstance(strength, (int, float)):
                            print(f"     {i}. {signal_type}: {description} (强度: {strength:.2f})")
                        else:
                            print(f"     {i}. {signal_type}: {description}")
            else:
                print("  🎯 交易信号: 暂无明确信号")


def analyze_single_stock(stock_code: str, period: str = "1y") -> bool:
    """
    分析单只股票
    
    Args:
        stock_code: 股票代码
        period: 数据周期
        
    Returns:
        是否成功
    """
    try:
        # 验证股票代码
        is_valid, normalized_code = validate_stock_code(stock_code)
        
        if not is_valid:
            print(f"❌ 无效的股票代码格式: {stock_code}")
            print("💡 支持格式: 000001, 000001.SZ, 600036.SH")
            return False
        
        print(f"🔄 正在分析股票: {normalized_code}")
        
        # 设置日志
        logging_config = {
            'level': 'INFO',
            'format': '{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}',
            'file': 'logs/analyze_stock.log'
        }
        setup_logger(logging_config)
        
        # 初始化系统
        print("🚀 正在初始化分析系统...")
        system = StockAnalysisSystem()
        print("✅ 系统初始化完成")
        
        # 获取并存储数据
        print(f"📥 正在获取股票数据 (周期: {period})...")
        success = system.fetch_and_store_data(normalized_code, period)
        
        if not success:
            print(f"❌ 无法获取股票 {normalized_code} 的数据")
            print("💡 请检查股票代码是否正确或网络连接")
            return False
        
        print("✅ 数据获取成功")
        
        # 执行分析
        print("🔍 正在执行综合分析...")
        results = system.analyze_stock(normalized_code, "all")
        
        if results:
            print("✅ 分析完成")
            display_analysis_results(normalized_code, results)
            return True
        else:
            print(f"❌ 股票 {normalized_code} 分析失败")
            print("💡 请检查数据质量或稍后重试")
            return False
            
    except Exception as e:
        logger.error(f"分析股票 {stock_code} 时发生错误: {str(e)}")
        print(f"❌ 分析过程中发生错误: {str(e)}")
        print("💡 请检查日志文件获取详细信息")
        return False


def main():
    """
    主函数
    """
    parser = argparse.ArgumentParser(
        description="江恩轮中轮+量价分析系统 - 命令行工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python analyze_stock.py 000001        # 分析平安银行
  python analyze_stock.py 600036.SH     # 分析招商银行
  python analyze_stock.py 000001 --period 6mo  # 分析6个月数据

支持的股票代码格式:
  - 6位数字: 000001, 600036
  - 完整格式: 000001.SZ, 600036.SH

支持的数据周期:
  - 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y
        """
    )
    
    parser.add_argument(
        "stock_code", 
        nargs='?',
        help="股票代码 (如: 000001, 600036.SH)"
    )
    
    parser.add_argument(
        "--period", 
        default="1y",
        choices=['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y'],
        help="数据周期 (默认: 1y)"
    )
    
    args = parser.parse_args()
    
    print("🎯 江恩轮中轮+量价分析系统 - 命令行工具")
    print("📊 数据源: akshare")
    print("=" * 50)
    
    if not args.stock_code:
        # 交互式输入
        print("\n📝 请输入股票代码:")
        print("💡 支持格式: 000001, 000001.SZ, 600036.SH")
        
        try:
            stock_code = input("🔍 股票代码: ").strip()
            if not stock_code:
                print("❌ 未输入股票代码")
                return
        except (KeyboardInterrupt, EOFError):
            print("\n👋 程序已退出")
            return
    else:
        stock_code = args.stock_code
    
    # 分析股票
    success = analyze_single_stock(stock_code, args.period)
    
    if success:
        print("\n🎉 分析完成！")
    else:
        print("\n❌ 分析失败")
        sys.exit(1)


if __name__ == "__main__":
    main()