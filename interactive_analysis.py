#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
江恩轮中轮+量价分析系统 - 交互式分析工具

支持用户交互式输入股票代码进行分析，使用akshare作为主要数据源

Author: AI Assistant
Date: 2024
"""

import sys
import os
from pathlib import Path
import re

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from main import StockAnalysisSystem
from src.utils.logger_setup import setup_logger
from loguru import logger


class InteractiveAnalyzer:
    """
    交互式股票分析器
    
    提供用户友好的交互界面，支持实时输入股票代码进行分析
    """
    
    def __init__(self):
        """
        初始化交互式分析器
        """
        self.system = None
        self._init_system()
    
    def _init_system(self) -> None:
        """
        初始化分析系统
        """
        try:
            print("🚀 正在初始化江恩轮中轮+量价分析系统...")
            self.system = StockAnalysisSystem()
            print("✅ 系统初始化完成！")
        except Exception as e:
            print(f"❌ 系统初始化失败: {str(e)}")
            print("请检查配置文件和依赖包是否正确安装")
            sys.exit(1)
    
    def _validate_stock_code(self, code: str) -> tuple[bool, str]:
        """
        验证股票代码格式
        
        Args:
            code: 股票代码
            
        Returns:
            tuple: (是否有效, 标准化后的代码)
        """
        if not code:
            return False, ""
        
        # 移除空格并转换为大写
        code = code.strip().upper()
        
        # 支持的格式：
        # 1. 6位数字 (如: 000001) -> 自动添加.SZ或.SH
        # 2. 6位数字.SZ/SH (如: 000001.SZ)
        # 3. 3位数字 (如: 300) -> 自动添加.SZ
        
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
        
        # 3位数字，默认深交所创业板
        if re.match(r'^\d{3}$', code):
            return True, f"300{code}.SZ"
        
        return False, code
    
    def _display_analysis_results(self, symbol: str, results: dict) -> None:
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
            
            if 'time_cycles' in gann_data:
                cycles = gann_data['time_cycles']
                print(f"  📅 时间周期: {len(cycles)} 个周期")
                if cycles:
                    latest_cycle = cycles[-1] if isinstance(cycles, list) else cycles
                    if isinstance(latest_cycle, dict):
                        print(f"     最新周期: {latest_cycle.get('cycle_type', 'N/A')}")
            
            if 'price_cycles' in gann_data:
                price_cycles = gann_data['price_cycles']
                print(f"  💰 价格轮回: {len(price_cycles)} 个轮回")
            
            if 'support_resistance' in gann_data:
                levels = gann_data['support_resistance']
                support = levels.get('support', [])
                resistance = levels.get('resistance', [])
                print(f"  📈 支撑位: {support[:3] if len(support) > 3 else support}")
                print(f"  📉 阻力位: {resistance[:3] if len(resistance) > 3 else resistance}")
        
        # 量价分析结果
        if 'volume_price' in results:
            vp_data = results['volume_price']
            print("\n📈 量价分析:")
            
            if 'volume_price_relation' in vp_data:
                relation = vp_data['volume_price_relation']
                trend = relation.get('trend', 'N/A')
                score = relation.get('coordination_score', 'N/A')
                print(f"  🔄 量价关系: {trend}")
                print(f"  ⭐ 配合度评分: {score}")
            
            if 'divergence_analysis' in vp_data:
                divergence = vp_data['divergence_analysis']
                has_divergence = divergence.get('has_divergence', False)
                divergence_type = divergence.get('divergence_type', 'N/A')
                print(f"  ⚠️  量价背离: {'是' if has_divergence else '否'}")
                if has_divergence:
                    print(f"     背离类型: {divergence_type}")
            
            if 'trading_signals' in vp_data:
                signals = vp_data['trading_signals']
                if isinstance(signals, list) and signals:
                    print(f"  🎯 交易信号: {len(signals)} 个")
                    for i, signal in enumerate(signals[:3], 1):
                        if isinstance(signal, dict):
                            signal_type = signal.get('type', 'N/A')
                            signal_action = signal.get('signal', 'N/A')
                            strength = signal.get('strength', 'N/A')
                            print(f"     {i}. {signal_type}: {signal_action} (强度: {strength})")
                else:
                    print(f"  🎯 交易信号: {signals}")
    
    def _get_user_input(self) -> str:
        """
        获取用户输入的股票代码
        
        Returns:
            用户输入的股票代码
        """
        print("\n" + "=" * 60)
        print("📝 请输入股票代码 (支持格式: 000001, 000001.SZ, 600036.SH)")
        print("💡 提示: 输入 'quit' 或 'exit' 退出程序")
        print("=" * 60)
        
        while True:
            try:
                user_input = input("\n🔍 股票代码: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    return 'quit'
                
                if not user_input:
                    print("❌ 请输入有效的股票代码")
                    continue
                
                return user_input
                
            except KeyboardInterrupt:
                print("\n\n👋 程序已退出")
                return 'quit'
            except EOFError:
                print("\n\n👋 程序已退出")
                return 'quit'
    
    def run(self) -> None:
        """
        运行交互式分析器
        """
        print("\n" + "=" * 60)
        print("🎯 江恩轮中轮+量价分析系统 - 交互式分析")
        print("📊 数据源: akshare")
        print("=" * 60)
        
        while True:
            # 获取用户输入
            user_input = self._get_user_input()
            
            if user_input == 'quit':
                print("\n👋 感谢使用江恩轮中轮+量价分析系统！")
                break
            
            # 验证股票代码
            is_valid, stock_code = self._validate_stock_code(user_input)
            
            if not is_valid:
                print(f"❌ 无效的股票代码格式: {user_input}")
                print("💡 支持格式: 000001, 000001.SZ, 600036.SH")
                continue
            
            print(f"\n🔄 正在分析股票: {stock_code}")
            
            try:
                # 获取并存储数据
                print("📥 正在获取股票数据...")
                success = self.system.fetch_and_store_data(stock_code, "1y")
                
                if not success:
                    print(f"❌ 无法获取股票 {stock_code} 的数据")
                    print("💡 请检查股票代码是否正确或网络连接")
                    continue
                
                print("✅ 数据获取成功")
                
                # 执行分析
                print("🔍 正在执行综合分析...")
                results = self.system.analyze_stock(stock_code, "all")
                
                if results:
                    print("✅ 分析完成")
                    self._display_analysis_results(stock_code, results)
                else:
                    print(f"❌ 股票 {stock_code} 分析失败")
                    print("💡 请检查数据质量或稍后重试")
                
            except Exception as e:
                logger.error(f"分析股票 {stock_code} 时发生错误: {str(e)}")
                print(f"❌ 分析过程中发生错误: {str(e)}")
                print("💡 请检查日志文件获取详细信息")


def main():
    """
    主函数
    """
    # 设置日志（使用默认配置）
    logging_config = {
        'level': 'INFO',
        'format': '{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}',
        'file': 'logs/interactive_analysis.log'
    }
    setup_logger(logging_config)
    
    # 创建并运行交互式分析器
    analyzer = InteractiveAnalyzer()
    analyzer.run()


if __name__ == "__main__":
    main()