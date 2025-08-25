#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速启动交互式股票分析系统
"""

import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from interactive_menu import InteractiveMenu

if __name__ == "__main__":
    try:
        print("🔮 江恩轮中轮+量价分析系统")
        print("正在初始化...")
        
        menu = InteractiveMenu()
        menu.run()
        
    except KeyboardInterrupt:
        print("\n\n👋 用户取消，退出系统")
    except Exception as e:
        print(f"❌ 启动失败: {str(e)}")
        print("请检查系统环境和依赖包是否正确安装")