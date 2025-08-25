#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API使用示例

演示如何使用股票分析系统的RESTful API接口。

Author: AI Assistant
Date: 2024
"""

import requests
import json
from typing import Dict, Any


class StockAnalysisAPIClient:
    """股票分析API客户端"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """初始化API客户端
        
        Args:
            base_url: API服务器基础URL
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        response = self.session.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def list_stocks(self, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """获取股票列表"""
        params = {'limit': limit, 'offset': offset}
        response = self.session.get(f"{self.base_url}/stocks", params=params)
        response.raise_for_status()
        return response.json()
    
    def fetch_stock_data(self, symbol: str, period: str = "1y") -> Dict[str, Any]:
        """获取股票数据"""
        data = {
            'symbol': symbol,
            'period': period
        }
        response = self.session.post(f"{self.base_url}/stocks/data", json=data)
        response.raise_for_status()
        return response.json()
    
    def analyze_single_stock(
        self, 
        symbol: str, 
        analysis_type: str = "all", 
        auto_fetch: bool = True, 
        period: str = None
    ) -> Dict[str, Any]:
        """单股票分析"""
        data = {
            'symbol': symbol,
            'analysis_type': analysis_type,
            'auto_fetch': auto_fetch
        }
        if period:
            data['period'] = period
        
        response = self.session.post(f"{self.base_url}/analysis/single", json=data)
        response.raise_for_status()
        return response.json()
    
    def analyze_batch_stocks(
        self, 
        symbols: list, 
        analysis_type: str = "all", 
        auto_fetch: bool = True, 
        period: str = None
    ) -> Dict[str, Any]:
        """批量股票分析"""
        data = {
            'symbols': symbols,
            'analysis_type': analysis_type,
            'auto_fetch': auto_fetch
        }
        if period:
            data['period'] = period
        
        response = self.session.post(f"{self.base_url}/analysis/batch", json=data)
        response.raise_for_status()
        return response.json()
    
    def get_analysis_by_symbol(
        self, 
        symbol: str, 
        analysis_type: str = "all", 
        auto_fetch: bool = True, 
        period: str = None
    ) -> Dict[str, Any]:
        """通过GET方法获取股票分析"""
        params = {
            'analysis_type': analysis_type,
            'auto_fetch': auto_fetch
        }
        if period:
            params['period'] = period
        
        response = self.session.get(f"{self.base_url}/analysis/{symbol}", params=params)
        response.raise_for_status()
        return response.json()


def example_basic_usage():
    """基础使用示例"""
    print("=== 基础使用示例 ===")
    
    # 创建API客户端
    client = StockAnalysisAPIClient()
    
    try:
        # 1. 健康检查
        print("\n1. 健康检查")
        health = client.health_check()
        print(f"系统状态: {health['system_info']['status']}")
        print(f"运行时间: {health['system_info']['uptime']}")
        
        # 2. 获取股票列表
        print("\n2. 获取股票列表")
        stocks = client.list_stocks(limit=5)
        print(f"股票总数: {stocks['total_count']}")
        for stock in stocks['stocks']:
            print(f"  - {stock['symbol']}: {stock.get('name', 'N/A')}")
        
        # 3. 分析单个股票
        print("\n3. 分析单个股票")
        symbol = "000001.SZ"
        result = client.analyze_single_stock(symbol, analysis_type="all")
        
        if result['result']:
            analysis = result['result']
            print(f"股票代码: {analysis['symbol']}")
            print(f"分析时间: {analysis['analysis_date']}")
            
            # 江恩分析结果
            if analysis.get('gann_analysis'):
                gann = analysis['gann_analysis']
                print(f"江恩分析 - 整体趋势: {gann['overall_trend']}")
                print(f"江恩分析 - 趋势强度: {gann['trend_strength']:.2f}")
            
            # 量价分析结果
            if analysis.get('volume_price_analysis'):
                vp = analysis['volume_price_analysis']
                print(f"量价分析 - 综合强度: {vp['combined_strength']:.2f}")
                print(f"量价分析 - 强度等级: {vp['strength_level']}")
                print(f"量价分析 - 整体趋势: {vp['overall_trend']}")
        
    except requests.exceptions.ConnectionError:
        print("错误: 无法连接到API服务器，请确保服务器正在运行")
        print("启动服务器: python run_api.py")
    except requests.exceptions.HTTPError as e:
        print(f"HTTP错误: {e}")
        if e.response:
            print(f"响应内容: {e.response.text}")
    except Exception as e:
        print(f"发生错误: {e}")


def example_batch_analysis():
    """批量分析示例"""
    print("\n=== 批量分析示例 ===")
    
    client = StockAnalysisAPIClient()
    
    try:
        # 批量分析多个股票
        symbols = ["000001.SZ", "600036.SH", "000002.SZ"]
        print(f"\n批量分析股票: {symbols}")
        
        result = client.analyze_batch_stocks(
            symbols=symbols,
            analysis_type="all",
            auto_fetch=True
        )
        
        print(f"成功分析: {result['success_count']} 个股票")
        print(f"失败股票: {result['failed_symbols']}")
        
        for analysis in result['results']:
            print(f"\n股票: {analysis['symbol']}")
            
            if analysis.get('gann_analysis'):
                gann = analysis['gann_analysis']
                print(f"  江恩趋势: {gann['overall_trend']} (强度: {gann['trend_strength']:.2f})")
            
            if analysis.get('volume_price_analysis'):
                vp = analysis['volume_price_analysis']
                print(f"  量价趋势: {vp['overall_trend']} (强度: {vp['combined_strength']:.2f})")
        
    except Exception as e:
        print(f"批量分析失败: {e}")


def example_data_fetching():
    """数据获取示例"""
    print("\n=== 数据获取示例 ===")
    
    client = StockAnalysisAPIClient()
    
    try:
        # 获取股票数据
        symbol = "000001.SZ"
        print(f"\n获取股票数据: {symbol}")
        
        result = client.fetch_stock_data(
            symbol=symbol,
            period="1y"
        )
        
        if result['data']:
            data = result['data']
            print(f"数据范围: {data['start_date']} 到 {data['end_date']}")
            print(f"记录总数: {data['total_records']}")
            print(f"最后更新: {data['last_update']}")
        
    except Exception as e:
        print(f"数据获取失败: {e}")


def example_different_analysis_types():
    """不同分析类型示例"""
    print("\n=== 不同分析类型示例 ===")
    
    client = StockAnalysisAPIClient()
    symbol = "000001.SZ"
    
    analysis_types = ["gann", "volume_price", "all"]
    
    for analysis_type in analysis_types:
        try:
            print(f"\n分析类型: {analysis_type}")
            result = client.analyze_single_stock(
                symbol=symbol,
                analysis_type=analysis_type
            )
            
            if result['result']:
                analysis = result['result']
                
                if analysis.get('gann_analysis'):
                    print("  包含江恩分析结果")
                
                if analysis.get('volume_price_analysis'):
                    print("  包含量价分析结果")
            
        except Exception as e:
            print(f"  分析失败: {e}")


def main():
    """主函数 - 运行所有示例"""
    print("股票分析API使用示例")
    print("=" * 50)
    
    # 运行各种示例
    example_basic_usage()
    example_batch_analysis()
    example_data_fetching()
    example_different_analysis_types()
    
    print("\n=== 示例完成 ===")
    print("\n更多信息:")
    print("- API文档: http://localhost:8000/docs")
    print("- 交互式文档: http://localhost:8000/redoc")
    print("- 健康检查: http://localhost:8000/health")


if __name__ == "__main__":
    main()