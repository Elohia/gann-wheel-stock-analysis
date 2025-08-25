#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
价格预测报告生成工具

命令行工具，用于生成专业的股票价格点位预测分析报告

Author: AI Assistant
Date: 2025-01-25
"""

import argparse
import sys
from pathlib import Path
from loguru import logger
from price_prediction_analyzer import PricePredictionAnalyzer, format_prediction_report


def setup_logging():
    """
    设置日志配置
    """
    logger.remove()  # 移除默认处理器
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO"
    )


def validate_stock_symbol(symbol: str) -> str:
    """
    验证股票代码格式
    
    Args:
        symbol: 股票代码
        
    Returns:
        标准化的股票代码
    """
    symbol = symbol.upper().strip()
    
    # 检查A股代码格式
    if len(symbol) == 6 and symbol.isdigit():
        # 根据代码判断交易所
        if symbol.startswith(('00', '30')):
            return f"{symbol}.SZ"  # 深交所
        elif symbol.startswith(('60', '68')):
            return f"{symbol}.SH"  # 上交所
        else:
            logger.warning(f"无法确定 {symbol} 的交易所，默认使用深交所")
            return f"{symbol}.SZ"
    
    # 已包含交易所后缀
    if '.' in symbol and symbol.split('.')[1] in ['SZ', 'SH']:
        return symbol
    
    # 其他格式（如港股、美股等）
    return symbol


def main():
    """
    主函数
    """
    setup_logging()
    
    parser = argparse.ArgumentParser(
        description="生成专业的股票价格点位预测分析报告",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python generate_price_report.py 000001 --period 1y
  python generate_price_report.py 600036.SH --period 6mo --output report.txt
  python generate_price_report.py 002553.SZ --period 3mo --interactive

支持的周期格式:
  1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
        """
    )
    
    parser.add_argument(
        "symbol",
        nargs="?",
        help="股票代码 (如: 000001, 600036.SH, 002553.SZ)"
    )
    
    parser.add_argument(
        "--period", "-p",
        default="1y",
        help="分析周期 (默认: 1y)"
    )
    
    parser.add_argument(
        "--output", "-o",
        help="输出文件路径 (可选，默认输出到控制台)"
    )
    
    parser.add_argument(
        "--config", "-c",
        default="config/config.yaml",
        help="配置文件路径 (默认: config/config.yaml)"
    )
    
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="交互式模式，生成报告后等待用户输入"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="详细输出模式"
    )
    
    args = parser.parse_args()
    
    # 设置日志级别
    if args.verbose:
        logger.remove()
        logger.add(
            sys.stderr,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level="DEBUG"
        )
    
    try:
        if args.interactive:
            # 交互式模式下不需要验证symbol参数
            # 检查配置文件
            config_path = Path(args.config)
            if not config_path.exists():
                logger.error(f"配置文件不存在: {config_path}")
                sys.exit(1)
        else:
            # 非交互模式下需要验证symbol参数
            if not args.symbol:
                logger.error("非交互模式下必须提供股票代码")
                sys.exit(1)
            
            # 验证股票代码
            symbol = validate_stock_symbol(args.symbol)
            logger.info(f"开始分析股票: {symbol}")
            
            # 检查配置文件
            config_path = Path(args.config)
            if not config_path.exists():
                logger.error(f"配置文件不存在: {config_path}")
                sys.exit(1)
            
            # 创建分析器
            analyzer = PricePredictionAnalyzer(str(config_path))
            
            # 生成预测报告
            logger.info(f"正在生成 {symbol} 的价格预测报告...")
            report = analyzer.generate_price_predictions(symbol, args.period)
            
            # 格式化报告
            formatted_report = format_prediction_report(report)
            
            # 输出报告
            if args.output:
                output_path = Path(args.output)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(formatted_report)
                
                logger.info(f"报告已保存到: {output_path}")
                print(f"\n✅ 价格预测报告已生成并保存到: {output_path}")
            else:
                print(formatted_report)
        
        # 交互式模式
        if args.interactive:
            print("\n" + "="*50)
            print("🔄 交互式模式")
            print("="*50)
            
            while True:
                try:
                    user_input = input("\n请输入命令 (help查看帮助, quit退出): ").strip().lower()
                    
                    if user_input in ['quit', 'exit', 'q']:
                        print("👋 再见！")
                        break
                    elif user_input in ['help', 'h']:
                        print("""
📚 可用命令:
  refresh / r    - 重新生成当前股票的预测报告
  change <code>  - 切换到其他股票 (如: change 600036)
  period <time>  - 更改分析周期 (如: period 6mo)
  save <file>    - 保存当前报告到文件
  help / h       - 显示此帮助信息
  quit / q       - 退出程序
                        """)
                    elif user_input in ['refresh', 'r']:
                        print(f"\n🔄 重新生成 {symbol} 的预测报告...")
                        report = analyzer.generate_price_predictions(symbol, args.period)
                        formatted_report = format_prediction_report(report)
                        print(formatted_report)
                    elif user_input.startswith('change '):
                        new_symbol = user_input.split(' ', 1)[1]
                        try:
                            symbol = validate_stock_symbol(new_symbol)
                            print(f"\n📈 切换到股票: {symbol}")
                            report = analyzer.generate_price_predictions(symbol, args.period)
                            formatted_report = format_prediction_report(report)
                            print(formatted_report)
                        except Exception as e:
                            print(f"❌ 切换股票失败: {str(e)}")
                    elif user_input.startswith('period '):
                        new_period = user_input.split(' ', 1)[1]
                        try:
                            args.period = new_period
                            print(f"\n📅 更改分析周期为: {new_period}")
                            report = analyzer.generate_price_predictions(symbol, args.period)
                            formatted_report = format_prediction_report(report)
                            print(formatted_report)
                        except Exception as e:
                            print(f"❌ 更改周期失败: {str(e)}")
                    elif user_input.startswith('save '):
                        save_path = user_input.split(' ', 1)[1]
                        try:
                            with open(save_path, 'w', encoding='utf-8') as f:
                                f.write(formatted_report)
                            print(f"✅ 报告已保存到: {save_path}")
                        except Exception as e:
                            print(f"❌ 保存失败: {str(e)}")
                    else:
                        print("❓ 未知命令，输入 'help' 查看可用命令")
                        
                except KeyboardInterrupt:
                    print("\n👋 再见！")
                    break
                except Exception as e:
                    print(f"❌ 执行命令时出错: {str(e)}")
        
        logger.info("价格预测报告生成完成")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断操作")
        sys.exit(1)
    except Exception as e:
        logger.error(f"生成价格预测报告失败: {str(e)}")
        print(f"\n❌ 错误: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()