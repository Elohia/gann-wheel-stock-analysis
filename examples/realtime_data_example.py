#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实时数据获取示例

演示如何使用实时数据获取功能：
1. 获取实时股价数据
2. 获取分时数据
3. 获取盘口数据
4. 启动实时监控
"""

import asyncio
import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data.realtime_fetcher import RealtimeFetcher
from src.utils.config_manager import ConfigManager


async def demo_realtime_data():
    """
    实时数据获取演示
    """
    print("=" * 60)
    print("江恩轮中轮股票分析系统 - 实时数据获取演示")
    print("=" * 60)
    
    try:
        # 初始化配置管理器和实时数据获取器
        config_manager = ConfigManager()
        realtime_fetcher = RealtimeFetcher(config_manager)
        
        # 测试股票代码
        test_symbols = ['000001', '000002', '600036']
        
        print("\n1. 获取实时股价数据")
        print("-" * 40)
        
        for symbol in test_symbols[:2]:  # 只测试前两个
            try:
                print(f"\n正在获取 {symbol} 的实时数据...")
                realtime_data = await realtime_fetcher.get_realtime_price(symbol)
                
                if realtime_data:
                    print(f"股票代码: {realtime_data.get('symbol', 'N/A')}")
                    print(f"股票名称: {realtime_data.get('name', 'N/A')}")
                    print(f"当前价格: {realtime_data.get('price', 'N/A')}")
                    print(f"涨跌额: {realtime_data.get('change', 'N/A')}")
                    print(f"涨跌幅: {realtime_data.get('change_pct', 'N/A')}%")
                    print(f"成交量: {realtime_data.get('volume', 'N/A')}")
                    print(f"更新时间: {realtime_data.get('timestamp', 'N/A')}")
                else:
                    print(f"未能获取到 {symbol} 的实时数据")
                    
            except Exception as e:
                print(f"获取 {symbol} 实时数据时出错: {str(e)}")
        
        print("\n2. 获取分时数据")
        print("-" * 40)
        
        try:
            symbol = test_symbols[0]
            print(f"\n正在获取 {symbol} 的分时数据...")
            tick_data = await realtime_fetcher.get_tick_data(symbol)
            
            if tick_data and 'data' in tick_data:
                print(f"股票代码: {tick_data.get('symbol', 'N/A')}")
                print(f"分时数据点数: {len(tick_data['data'])}")
                print("最近5个分时点:")
                
                for i, tick in enumerate(tick_data['data'][:5]):
                    print(f"  {tick.get('time', 'N/A')} - 价格: {tick.get('price', 'N/A')}, 成交量: {tick.get('volume', 'N/A')}")
                    
                print(f"更新时间: {tick_data.get('timestamp', 'N/A')}")
            else:
                print(f"未能获取到 {symbol} 的分时数据")
                
        except Exception as e:
            print(f"获取分时数据时出错: {str(e)}")
        
        print("\n3. 获取盘口数据")
        print("-" * 40)
        
        try:
            symbol = test_symbols[0]
            print(f"\n正在获取 {symbol} 的盘口数据...")
            depth_data = await realtime_fetcher.get_market_depth(symbol)
            
            if depth_data:
                print(f"股票代码: {depth_data.get('symbol', 'N/A')}")
                
                if 'bid' in depth_data and depth_data['bid']:
                    print("买盘（前3档）:")
                    for i, bid in enumerate(depth_data['bid'][:3]):
                        print(f"  买{i+1}: {bid.get('price', 'N/A')} x {bid.get('volume', 'N/A')}")
                
                if 'ask' in depth_data and depth_data['ask']:
                    print("卖盘（前3档）:")
                    for i, ask in enumerate(depth_data['ask'][:3]):
                        print(f"  卖{i+1}: {ask.get('price', 'N/A')} x {ask.get('volume', 'N/A')}")
                        
                print(f"更新时间: {depth_data.get('timestamp', 'N/A')}")
            else:
                print(f"未能获取到 {symbol} 的盘口数据")
                
        except Exception as e:
            print(f"获取盘口数据时出错: {str(e)}")
        
        print("\n4. 实时监控演示")
        print("-" * 40)
        
        try:
            print(f"\n开始监控股票: {test_symbols}")
            await realtime_fetcher.start_monitoring(test_symbols)
            print("监控已启动，将运行10秒...")
            
            # 运行10秒后停止
            await asyncio.sleep(10)
            
            print("\n停止监控...")
            await realtime_fetcher.stop_monitoring()
            print("监控已停止")
            
        except Exception as e:
            print(f"监控过程中出错: {str(e)}")
        
        print("\n5. 缓存机制演示")
        print("-" * 40)
        
        try:
            symbol = test_symbols[0]
            print(f"\n第一次获取 {symbol} 数据（从数据源）...")
            start_time = datetime.now()
            data1 = await realtime_fetcher.get_realtime_price(symbol)
            time1 = (datetime.now() - start_time).total_seconds()
            
            print(f"第二次获取 {symbol} 数据（从缓存）...")
            start_time = datetime.now()
            data2 = await realtime_fetcher.get_realtime_price(symbol)
            time2 = (datetime.now() - start_time).total_seconds()
            
            print(f"第一次耗时: {time1:.3f}秒")
            print(f"第二次耗时: {time2:.3f}秒")
            print(f"缓存加速比: {time1/time2:.1f}x" if time2 > 0 else "缓存生效")
            
        except Exception as e:
            print(f"缓存测试时出错: {str(e)}")
        
    except Exception as e:
        print(f"演示过程中发生错误: {str(e)}")
    
    print("\n=" * 60)
    print("实时数据获取演示完成")
    print("=" * 60)


async def demo_api_usage():
    """
    API使用演示
    """
    print("\n" + "=" * 60)
    print("API接口使用演示")
    print("=" * 60)
    
    import aiohttp
    
    # API基础URL（假设服务器运行在本地8000端口）
    base_url = "http://localhost:8000"
    
    async with aiohttp.ClientSession() as session:
        try:
            # 测试实时数据接口
            symbol = "000001"
            
            print(f"\n1. 测试实时价格接口: GET /stocks/realtime/{symbol}")
            async with session.get(f"{base_url}/stocks/realtime/{symbol}") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"响应状态: {response.status}")
                    print(f"股票代码: {data.get('symbol', 'N/A')}")
                    print(f"当前价格: {data.get('price', 'N/A')}")
                else:
                    print(f"请求失败，状态码: {response.status}")
            
            print(f"\n2. 测试分时数据接口: GET /stocks/realtime/{symbol}/tick")
            async with session.get(f"{base_url}/stocks/realtime/{symbol}/tick") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"响应状态: {response.status}")
                    print(f"分时数据点数: {len(data.get('data', []))}")
                else:
                    print(f"请求失败，状态码: {response.status}")
            
            print(f"\n3. 测试盘口数据接口: GET /stocks/realtime/{symbol}/depth")
            async with session.get(f"{base_url}/stocks/realtime/{symbol}/depth") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"响应状态: {response.status}")
                    print(f"买盘档数: {len(data.get('bid', []))}")
                    print(f"卖盘档数: {len(data.get('ask', []))}")
                else:
                    print(f"请求失败，状态码: {response.status}")
            
            print("\n4. 测试监控接口: POST /stocks/realtime/monitor")
            monitor_data = ["000001", "000002"]
            async with session.post(f"{base_url}/stocks/realtime/monitor", json=monitor_data) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"响应状态: {response.status}")
                    print(f"监控消息: {data.get('message', 'N/A')}")
                else:
                    print(f"请求失败，状态码: {response.status}")
            
            # 等待一段时间后停止监控
            await asyncio.sleep(5)
            
            print("\n5. 测试停止监控接口: POST /stocks/realtime/stop_monitor")
            async with session.post(f"{base_url}/stocks/realtime/stop_monitor") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"响应状态: {response.status}")
                    print(f"停止消息: {data.get('message', 'N/A')}")
                else:
                    print(f"请求失败，状态码: {response.status}")
                    
        except aiohttp.ClientError as e:
            print(f"网络请求错误: {str(e)}")
            print("请确保API服务器正在运行（python -m uvicorn api.server:app --reload）")
        except Exception as e:
            print(f"API测试过程中发生错误: {str(e)}")


def main():
    """
    主函数
    """
    print("江恩轮中轮股票分析系统 - 实时数据功能演示")
    print("\n选择演示模式:")
    print("1. 直接调用实时数据获取功能")
    print("2. 通过API接口测试（需要先启动服务器）")
    print("3. 运行所有演示")
    
    try:
        choice = input("\n请输入选择 (1-3): ").strip()
        
        if choice == '1':
            asyncio.run(demo_realtime_data())
        elif choice == '2':
            asyncio.run(demo_api_usage())
        elif choice == '3':
            asyncio.run(demo_realtime_data())
            asyncio.run(demo_api_usage())
        else:
            print("无效选择，运行默认演示...")
            asyncio.run(demo_realtime_data())
            
    except KeyboardInterrupt:
        print("\n演示被用户中断")
    except Exception as e:
        print(f"演示过程中发生错误: {str(e)}")


if __name__ == "__main__":
    main()