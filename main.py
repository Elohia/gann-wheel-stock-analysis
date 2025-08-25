#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
江恩轮中轮+量价分析系统 - 主程序入口

本程序集成了股票数据获取、江恩轮中轮分析和量价分析功能，
为投资者提供专业的技术分析工具。

Author: AI Assistant
Date: 2024
"""

import sys
import os
import argparse
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from loguru import logger
from src.config.config_manager import ConfigManager
from src.data.data_fetcher import DataFetcher
from src.storage.database_manager import DatabaseManager
from src.analysis.gann.gann_wheel import GannWheel
from src.analysis.volume_price.volume_price_analyzer import VolumePriceAnalyzer
from src.utils.logger_setup import setup_logger


class StockAnalysisSystem:
    """
    股票分析系统主类
    
    整合所有功能模块，提供统一的分析接口
    """
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        初始化股票分析系统
        
        Args:
            config_path: 配置文件路径
        """
        self.config_manager = ConfigManager(config_path)
        self.config = self.config_manager.get_config()
        
        # 设置日志
        setup_logger(self.config.get('logging', {}))
        
        # 初始化各个模块
        self.db_manager = DatabaseManager(self.config.get('database', {}))
        self.data_fetcher = DataFetcher(self.config.get('data_sources', {}))
        self.gann_wheel = GannWheel(self.config.get('gann_analysis', {}))
        self.volume_price_analyzer = VolumePriceAnalyzer(self.config.get('volume_price_analysis', {}))
        
        logger.info("股票分析系统初始化完成")
    
    def fetch_and_store_data(self, symbol: str, period: str = None):
        """
        获取并存储股票数据
        
        Args:
            symbol: 股票代码
            period: 数据周期，默认使用配置文件中的设置
        """
        try:
            if period is None:
                period = self.config.get('data_update', {}).get('default_period', '2y')
            
            logger.info(f"开始获取股票 {symbol} 的数据，周期: {period}")
            
            # 获取数据
            data = self.data_fetcher.fetch_stock_data(symbol, period)
            
            if data is not None and not data.empty:
                # 存储数据
                self.db_manager.save_stock_data(symbol, data)
                logger.info(f"股票 {symbol} 数据获取并存储成功，共 {len(data)} 条记录")
                return True
            else:
                logger.warning(f"股票 {symbol} 数据获取失败或为空")
                return False
                
        except Exception as e:
            logger.error(f"获取股票 {symbol} 数据时发生错误: {str(e)}")
            return False
    
    def analyze_stock(self, symbol: str, analysis_type: str = "all"):
        """
        分析股票
        
        Args:
            symbol: 股票代码
            analysis_type: 分析类型 ('gann', 'volume_price', 'all')
        """
        try:
            logger.info(f"开始分析股票 {symbol}，分析类型: {analysis_type}")
            
            # 从数据库获取数据
            data = self.db_manager.get_stock_data(symbol)
            
            if data is None or data.empty:
                logger.warning(f"股票 {symbol} 没有可用数据，请先获取数据")
                return None
            
            results = {}
            
            # 江恩轮中轮分析
            if analysis_type in ['gann', 'all']:
                logger.info(f"执行江恩轮中轮分析: {symbol}")
                gann_result = self.gann_wheel.analyze_stock(symbol, data)
                results['gann'] = gann_result
            
            # 量价分析
            if analysis_type in ['volume_price', 'all']:
                logger.info(f"执行量价分析: {symbol}")
                volume_price_result = self.volume_price_analyzer.analyze_stock(symbol, data)
                results['volume_price'] = volume_price_result
            
            logger.info(f"股票 {symbol} 分析完成")
            return results
            
        except Exception as e:
            logger.error(f"分析股票 {symbol} 时发生错误: {str(e)}")
            return None
    
    def batch_analyze(self, symbols: list = None):
        """
        批量分析股票
        
        Args:
            symbols: 股票代码列表，默认使用配置文件中的关注列表
        """
        if symbols is None:
            symbols = self.config.get('stocks', {}).get('watchlist', [])
        
        if not symbols:
            logger.warning("没有指定要分析的股票")
            return
        
        logger.info(f"开始批量分析 {len(symbols)} 只股票")
        
        results = {}
        for symbol in symbols:
            # 先获取数据
            if self.fetch_and_store_data(symbol):
                # 再进行分析
                result = self.analyze_stock(symbol)
                if result:
                    results[symbol] = result
        
        logger.info(f"批量分析完成，成功分析 {len(results)} 只股票")
        return results
    
    def update_all_data(self):
        """
        更新所有关注股票的数据
        """
        symbols = self.config.get('stocks', {}).get('watchlist', [])
        indices = self.config.get('stocks', {}).get('indices', [])
        
        all_symbols = symbols + indices
        
        logger.info(f"开始更新 {len(all_symbols)} 只股票/指数的数据")
        
        success_count = 0
        for symbol in all_symbols:
            if self.fetch_and_store_data(symbol):
                success_count += 1
        
        logger.info(f"数据更新完成，成功更新 {success_count}/{len(all_symbols)} 只股票/指数")


def main():
    """
    主函数 - 命令行接口
    """
    parser = argparse.ArgumentParser(description='江恩轮中轮+量价分析系统')
    parser.add_argument('--config', '-c', default='config/config.yaml', help='配置文件路径')
    parser.add_argument('--symbol', '-s', help='股票代码')
    parser.add_argument('--period', '-p', help='数据周期')
    parser.add_argument('--analysis', '-a', choices=['gann', 'volume_price', 'all'], 
                       default='all', help='分析类型')
    parser.add_argument('--batch', '-b', action='store_true', help='批量分析关注列表中的股票')
    parser.add_argument('--update', '-u', action='store_true', help='更新所有股票数据')
    parser.add_argument('--fetch-only', '-f', action='store_true', help='仅获取数据，不进行分析')
    
    args = parser.parse_args()
    
    try:
        # 初始化系统
        system = StockAnalysisSystem(args.config)
        
        if args.update:
            # 更新所有数据
            system.update_all_data()
            
        elif args.batch:
            # 批量分析
            system.batch_analyze()
            
        elif args.symbol:
            # 单只股票处理
            if args.fetch_only:
                # 仅获取数据
                system.fetch_and_store_data(args.symbol, args.period)
            else:
                # 获取数据并分析
                if system.fetch_and_store_data(args.symbol, args.period):
                    system.analyze_stock(args.symbol, args.analysis)
        else:
            # 默认行为：批量分析
            print("江恩轮中轮+量价分析系统")
            print("使用 --help 查看帮助信息")
            print("执行默认批量分析...")
            system.batch_analyze()
            
    except KeyboardInterrupt:
        logger.info("用户中断程序执行")
    except Exception as e:
        logger.error(f"程序执行出错: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()