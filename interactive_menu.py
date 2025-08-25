#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交互式股票分析菜单系统
提供简洁的命令行界面进行股票技术分析
"""

import os
import sys
from typing import Optional
from loguru import logger

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import StockAnalysisSystem
from price_prediction_analyzer import PricePredictionAnalyzer, format_prediction_report


class InteractiveMenu:
    """交互式菜单系统"""
    
    def __init__(self):
        """初始化菜单系统"""
        self.system = StockAnalysisSystem()
        self.analyzer = PricePredictionAnalyzer()
        self.current_symbol = None
        
    def display_main_menu(self):
        """显示主菜单"""
        print("\n" + "="*60)
        print("🔮 江恩轮中轮 + 量价分析系统")
        print("="*60)
        print("1. 📈 股票技术分析")
        print("2. 🎯 价格预测分析")
        print("3. 📊 综合分析报告")
        print("4. ⚙️  系统设置")
        print("5. ❓ 帮助信息")
        print("0. 🚪 退出系统")
        print("="*60)
        
    def display_stock_menu(self):
        """显示股票分析菜单"""
        print("\n" + "-"*50)
        print("📈 股票技术分析")
        print("-"*50)
        print("1. 🔍 输入股票代码")
        print("2. 🌀 江恩轮中轮分析")
        print("3. 📊 量价关系分析")
        print("4. 📋 查看分析历史")
        print("0. ⬅️  返回主菜单")
        print("-"*50)
        
    def display_prediction_menu(self):
        """显示价格预测菜单"""
        print("\n" + "-"*50)
        print("🎯 价格预测分析")
        print("-"*50)
        print("1. 🔍 输入股票代码")
        print("2. 📈 生成价格预测")
        print("3. 📊 详细预测报告")
        print("4. 💾 保存预测结果")
        print("0. ⬅️  返回主菜单")
        print("-"*50)
        
    def get_user_choice(self, max_choice: int) -> int:
        """获取用户选择"""
        while True:
            try:
                choice = input(f"\n请选择 (0-{max_choice}): ").strip()
                if choice == '':
                    continue
                choice_num = int(choice)
                if 0 <= choice_num <= max_choice:
                    return choice_num
                else:
                    print(f"❌ 请输入 0-{max_choice} 之间的数字")
            except ValueError:
                print("❌ 请输入有效的数字")
            except KeyboardInterrupt:
                print("\n\n👋 感谢使用，再见！")
                sys.exit(0)
                
    def get_stock_symbol(self) -> Optional[str]:
        """获取股票代码"""
        print("\n📝 请输入股票代码:")
        print("💡 示例: 000001 (平安银行), 002553 (南方轴承), 600036 (招商银行)")
        print("💡 支持A股代码，系统会自动添加后缀(.SZ/.SH)")
        
        while True:
            try:
                symbol = input("股票代码: ").strip().upper()
                if not symbol:
                    continue
                    
                # 简单验证股票代码格式
                if len(symbol) == 6 and symbol.isdigit():
                    # 自动添加后缀
                    if symbol.startswith(('000', '002', '300')):
                        symbol += '.SZ'
                    elif symbol.startswith(('600', '601', '603', '688')):
                        symbol += '.SH'
                    else:
                        symbol += '.SZ'  # 默认深圳
                elif '.' in symbol:
                    # 已包含后缀
                    pass
                else:
                    print("❌ 请输入6位数字的股票代码")
                    continue
                    
                self.current_symbol = symbol
                print(f"✅ 已选择股票: {symbol}")
                return symbol
                
            except KeyboardInterrupt:
                return None
                
    def run_stock_analysis(self):
        """运行股票技术分析"""
        if not self.current_symbol:
            print("❌ 请先输入股票代码")
            return
            
        print(f"\n🔄 正在分析 {self.current_symbol}...")
        try:
            # 先尝试从数据库获取数据
            data = self.system.db_manager.get_stock_data(self.current_symbol)
            
            # 如果数据库中没有数据，则获取并存储
            if data is None or data.empty:
                print("📥 正在获取股票数据...")
                success = self.system.fetch_and_store_data(self.current_symbol)
                if not success:
                    print("❌ 无法获取股票数据，请检查代码是否正确")
                    return
                # 重新从数据库获取数据
                data = self.system.db_manager.get_stock_data(self.current_symbol)
                if data is None or data.empty:
                    print("❌ 数据获取失败")
                    return
                
            # 江恩分析
            print("🌀 执行江恩轮中轮分析...")
            gann_result = self.system.gann_wheel.analyze_stock(self.current_symbol, data)
            
            # 量价分析
            print("📊 执行量价关系分析...")
            volume_result = self.system.volume_price_analyzer.analyze_stock(self.current_symbol, data)
            
            # 显示结果摘要
            print("\n" + "="*50)
            print(f"📈 {self.current_symbol} 技术分析结果")
            print("="*50)
            
            # 江恩分析摘要
            if gann_result:
                print("\n🌀 江恩轮中轮分析:")
                
                # 显示时间分析
                time_analysis = gann_result.get('time_analysis', {})
                if time_analysis:
                    # 显示主导周期
                    dominant_cycle = time_analysis.get('dominant_cycle')
                    if dominant_cycle:
                        cycle_days = dominant_cycle.get('cycle_days', 'N/A')
                        strength = dominant_cycle.get('strength', 'N/A')
                        print(f"   主导周期: {cycle_days}天")
                        if isinstance(strength, (int, float)):
                            print(f"   周期强度: {strength:.2f}")
                        else:
                            print(f"   周期强度: {strength}")
                    
                    # 显示关键时间点
                    key_dates = time_analysis.get('key_time_points', [])
                    if key_dates:
                        dates_str = ", ".join([str(date) for date in key_dates[:3]])
                        print(f"   关键时间: {dates_str}")
                    
                    # 显示下一个重要时间窗口
                    next_window = time_analysis.get('next_time_window')
                    if next_window:
                        print(f"   下个时间窗口: {next_window}")
                    
                    if not dominant_cycle and not key_dates and not next_window:
                        print("   时间周期: 暂无数据")
                else:
                    print("   时间周期: 暂无数据")
                
                # 显示价格分析
                price_analysis = gann_result.get('price_analysis', {})
                if price_analysis:
                    # 显示价格统计
                    price_stats = price_analysis.get('price_statistics', {})
                    if price_stats:
                        if price_stats.get('price_range'):
                            print(f"   价格区间: {price_stats['price_range']:.2f}")
                        if price_stats.get('price_center'):
                            print(f"   价格中心: {price_stats['price_center']:.2f}")
                    
                    # 显示当前价格位置
                    current_pos = price_analysis.get('current_position', {})
                    if current_pos:
                        current_price = current_pos.get('current_price', '未知')
                        print(f"   当前价格: {current_price}")
                        
                        if current_pos.get('nearest_support'):
                            support = current_pos['nearest_support']
                            level = support.get('level', 0)
                            strength = support.get('strength', 'N/A')
                            if isinstance(level, (int, float)):
                                print(f"   最近支撑: {level:.2f} (强度: {strength})")
                            else:
                                print(f"   最近支撑: {level} (强度: {strength})")
                        
                        if current_pos.get('nearest_resistance'):
                            resistance = current_pos['nearest_resistance']
                            level = resistance.get('level', 0)
                            strength = resistance.get('strength', 'N/A')
                            if isinstance(level, (int, float)):
                                print(f"   最近阻力: {level:.2f} (强度: {strength})")
                            else:
                                print(f"   最近阻力: {level} (强度: {strength})")
                    
                    if not price_stats and not current_pos:
                        print("   价格位置: 暂无数据")
                else:
                    print("   价格位置: 暂无数据")
                
                # 显示江恩角度线
                angle_analysis = gann_result.get('angle_analysis', {})
                if angle_analysis:
                    # 显示关键角度线
                    key_angles = angle_analysis.get('key_angles', [])
                    if key_angles:
                        angle_values = []
                        for angle_info in key_angles[:3]:
                            if isinstance(angle_info, dict):
                                angle = angle_info.get('angle', 'N/A')
                                strength = angle_info.get('strength', 0)
                                if isinstance(strength, (int, float)):
                                    angle_values.append(f"{angle}°(强度:{strength:.2f})")
                                else:
                                    angle_values.append(f"{angle}°")
                            else:
                                angle_values.append(f"{angle_info}°")
                        angles_str = ', '.join(angle_values)
                        print(f"   关键角度: {angles_str}")
                    
                    # 显示当前角度支撑和阻力
                    current_angles = angle_analysis.get('current_angles', {})
                    if current_angles:
                        if current_angles.get('support_angle'):
                            support = current_angles['support_angle']
                            angle = support.get('angle', 'N/A')
                            price = support.get('price', 0)
                            if isinstance(price, (int, float)):
                                print(f"   角度支撑: {angle}° 在 {price:.2f}")
                        
                        if current_angles.get('resistance_angle'):
                            resistance = current_angles['resistance_angle']
                            angle = resistance.get('angle', 'N/A')
                            price = resistance.get('price', 0)
                            if isinstance(price, (int, float)):
                                print(f"   角度阻力: {angle}° 在 {price:.2f}")
                    
                    if not key_angles and not current_angles:
                        print("   关键角度: 暂无数据")
                else:
                    print("   关键角度: 暂无数据")
                
                # 显示关键位计算
                key_levels = gann_result.get('key_levels', {})
                if key_levels:
                    # 支撑位
                    supports = key_levels.get('key_supports', [])
                    if supports:
                        support_prices = [f"{s['price']:.2f}({s.get('type', 'support')})" for s in supports[:3]]
                        supports_str = ", ".join(support_prices)
                        print(f"   支撑位: {supports_str}")
                    else:
                        print("   支撑位: 暂无数据")
                    
                    # 阻力位
                    resistances = key_levels.get('key_resistances', [])
                    if resistances:
                        resistance_prices = [f"{r['price']:.2f}({r.get('type', 'resistance')})" for r in resistances[:3]]
                        resistances_str = ", ".join(resistance_prices)
                        print(f"   阻力位: {resistances_str}")
                    else:
                        print("   阻力位: 暂无数据")
                    
                    # 显示最强支撑和阻力
                    if key_levels.get('strongest_support'):
                        strongest_sup = key_levels['strongest_support']
                        print(f"   最强支撑: {strongest_sup['price']:.2f} (强度: {strongest_sup.get('strength', 'N/A')})")
                    
                    if key_levels.get('strongest_resistance'):
                        strongest_res = key_levels['strongest_resistance']
                        print(f"   最强阻力: {strongest_res['price']:.2f} (强度: {strongest_res.get('strength', 'N/A')})")
                    
                    if not supports and not resistances:
                        print("   关键位: 暂无数据")
                else:
                    print("   关键位: 暂无数据")
                
                # 显示预测信息
                predictions = gann_result.get('predictions', {})
                if predictions:
                    print("\n📈 预测信息:")
                    
                    # 综合预测
                    combined_pred = predictions.get('combined_prediction', {})
                    if combined_pred:
                        direction = combined_pred.get('direction', '暂无数据')
                        target_price = combined_pred.get('target_price', '暂无数据')
                        print(f"   预测方向: {direction}")
                        if isinstance(target_price, (int, float)):
                            print(f"   目标价位: {target_price:.2f}")
                        else:
                            print(f"   目标价位: {target_price}")
                    
                    # 置信度
                    confidence = predictions.get('confidence_level', '暂无数据')
                    if isinstance(confidence, (int, float)):
                        print(f"   置信度: {confidence:.2%}")
                    else:
                        print(f"   置信度: {confidence}")
                    
                    # 当前价格
                    current_price = predictions.get('current_price', '暂无数据')
                    if isinstance(current_price, (int, float)):
                        print(f"   当前价格: {current_price:.2f}")
                else:
                    print("\n📈 预测信息: 暂无数据")
                
            # 量价分析摘要
            if volume_result:
                print("\n📊 量价关系分析:")
                # 显示趋势分析
                trend_analysis = volume_result.get('trend_analysis', {})
                if trend_analysis:
                    overall_trend = trend_analysis.get('overall_trend', 'N/A')
                    trend_strength = trend_analysis.get('trend_strength', 'N/A')
                    print(f"   整体趋势: {overall_trend} (强度: {trend_strength})")
                
                # 显示量价关系
                vp_relation = volume_result.get('volume_price_relation', {})
                if vp_relation:
                    current_relation = vp_relation.get('current_relation', 'N/A')
                    relation_score = vp_relation.get('relation_score', 'N/A')
                    print(f"   量价关系: {current_relation} (评分: {relation_score})")
                
                # 显示综合评分
                comp_score = volume_result.get('comprehensive_score', {})
                if comp_score:
                    total_score = comp_score.get('total_score', 0)
                    rating = comp_score.get('rating', 'N/A')
                    print(f"   综合评分: {total_score:.1f} ({rating})")
                
                # 显示交易信号
                trading_signals = volume_result.get('trading_signals', {})
                if trading_signals:
                    current_signal = trading_signals.get('current_strongest_signal')
                    if current_signal:
                        signal_type = current_signal.get('signal_type', 'N/A')
                        strength = current_signal.get('strength', 'N/A')
                        confidence = current_signal.get('confidence', 'N/A')
                        print(f"   当前信号: {signal_type} (强度: {strength}, 置信度: {confidence})")
                
                # 显示关键指标
                key_indicators = volume_result.get('key_indicators', {})
                if key_indicators:
                    volume_trend = key_indicators.get('volume_trend', 'N/A')
                    price_momentum = key_indicators.get('price_momentum', 'N/A')
                    print(f"   成交量趋势: {volume_trend}")
                    print(f"   价格动量: {price_momentum}")
                
            print("\n✅ 分析完成！")
            
        except Exception as e:
            print(f"❌ 分析过程中出现错误: {str(e)}")
            logger.error(f"Stock analysis error: {e}")
            
    def run_price_prediction(self):
        """运行价格预测分析"""
        if not self.current_symbol:
            print("❌ 请先输入股票代码")
            return
            
        print(f"\n🔄 正在生成 {self.current_symbol} 价格预测...")
        try:
            # 生成预测报告
            report = self.analyzer.generate_price_predictions(self.current_symbol)
            
            if not report:
                print("❌ 无法生成预测报告")
                return
                
            # 显示预测摘要
            predictions = report.get('key_price_predictions', [])
            if predictions:
                print("\n" + "="*50)
                print(f"🎯 {self.current_symbol} 价格预测摘要")
                print("="*50)
                print(f"📊 预测点位数量: {len(predictions)}")
                
                # 显示前5个预测
                print("\n🔝 主要预测点位:")
                for i, pred in enumerate(predictions[:5], 1):
                    direction = "📈" if pred.get('方向') == '上涨' else "📉"
                    price_str = pred.get('目标价位', '0')
                    # 处理价格字符串，提取数值
                    try:
                        price = float(price_str) if isinstance(price_str, (int, float)) else float(price_str.replace('¥', '').replace(',', ''))
                    except (ValueError, AttributeError):
                        price = 0
                    confidence_str = pred.get('置信度', '0%')
                    # 处理置信度字符串，提取数值
                    try:
                        confidence = float(confidence_str.replace('%', '')) if isinstance(confidence_str, str) else confidence_str
                    except (ValueError, AttributeError):
                        confidence = 0
                    print(f"   {i}. {direction} {price:.2f} (置信度: {confidence}%)")
                    
                print("\n✅ 预测完成！")
            else:
                print("❌ 未生成有效预测")
                
        except Exception as e:
            print(f"❌ 预测过程中出现错误: {str(e)}")
            logger.error(f"Price prediction error: {e}")
            
    def show_detailed_report(self):
        """显示详细预测报告"""
        if not self.current_symbol:
            print("❌ 请先输入股票代码")
            return
            
        print(f"\n🔄 正在生成 {self.current_symbol} 详细报告...")
        try:
            report = self.analyzer.generate_price_predictions(self.current_symbol)
            if report:
                formatted_report = format_prediction_report(report)
                print("\n" + "="*80)
                print(formatted_report)
                print("="*80)
            else:
                print("❌ 无法生成详细报告")
                
        except Exception as e:
            print(f"❌ 生成报告时出现错误: {str(e)}")
            logger.error(f"Report generation error: {e}")
            
    def save_report(self):
        """保存预测报告"""
        if not self.current_symbol:
            print("❌ 请先输入股票代码")
            return
            
        try:
            report = self.analyzer.generate_price_predictions(self.current_symbol)
            if report:
                formatted_report = format_prediction_report(report)
                filename = f"prediction_report_{self.current_symbol}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.txt"
                
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(formatted_report)
                    
                print(f"✅ 报告已保存到: {filename}")
            else:
                print("❌ 无法生成报告")
                
        except Exception as e:
            print(f"❌ 保存报告时出现错误: {str(e)}")
            
    def show_help(self):
        """显示帮助信息"""
        print("\n" + "="*60)
        print("❓ 系统帮助")
        print("="*60)
        print("📖 功能说明:")
        print("   • 江恩轮中轮分析: 基于江恩理论的时间和价格分析")
        print("   • 量价关系分析: 成交量与价格变化的关联性分析")
        print("   • 价格预测: 综合多种技术指标的价格目标预测")
        print("\n💡 使用提示:")
        print("   • 支持A股主要股票代码")
        print("   • 建议使用活跃交易的股票获得更准确分析")
        print("   • 预测结果仅供参考，投资需谨慎")
        print("\n🔧 技术支持:")
        print("   • 数据源: AKShare, yfinance")
        print("   • 分析周期: 默认1年历史数据")
        print("   • 更新频率: 实时获取最新数据")
        print("="*60)
        
    def run(self):
        """运行交互式菜单"""
        print("🚀 启动江恩轮中轮+量价分析系统...")
        
        while True:
            try:
                self.display_main_menu()
                choice = self.get_user_choice(5)
                
                if choice == 0:
                    print("\n👋 感谢使用，再见！")
                    break
                elif choice == 1:
                    # 股票技术分析
                    while True:
                        self.display_stock_menu()
                        sub_choice = self.get_user_choice(4)
                        
                        if sub_choice == 0:
                            break
                        elif sub_choice == 1:
                            self.get_stock_symbol()
                        elif sub_choice == 2:
                            self.run_stock_analysis()
                        elif sub_choice == 3:
                            self.run_stock_analysis()  # 量价分析包含在技术分析中
                        elif sub_choice == 4:
                            print("📋 分析历史功能开发中...")
                            
                elif choice == 2:
                    # 价格预测分析
                    while True:
                        self.display_prediction_menu()
                        sub_choice = self.get_user_choice(4)
                        
                        if sub_choice == 0:
                            break
                        elif sub_choice == 1:
                            self.get_stock_symbol()
                        elif sub_choice == 2:
                            self.run_price_prediction()
                        elif sub_choice == 3:
                            self.show_detailed_report()
                        elif sub_choice == 4:
                            self.save_report()
                            
                elif choice == 3:
                    # 综合分析报告
                    if self.current_symbol:
                        print(f"\n🔄 正在生成 {self.current_symbol} 综合分析报告...")
                        self.run_stock_analysis()
                        input("\n按回车键继续...")
                        self.show_detailed_report()
                    else:
                        print("❌ 请先选择股票代码")
                        
                elif choice == 4:
                    # 系统设置
                    print("⚙️  系统设置功能开发中...")
                    
                elif choice == 5:
                    # 帮助信息
                    self.show_help()
                    
            except KeyboardInterrupt:
                print("\n\n👋 感谢使用，再见！")
                break
            except Exception as e:
                print(f"❌ 系统错误: {str(e)}")
                logger.error(f"Menu system error: {e}")
                

if __name__ == "__main__":
    # 导入pandas用于时间戳
    import pandas as pd
    
    menu = InteractiveMenu()
    menu.run()