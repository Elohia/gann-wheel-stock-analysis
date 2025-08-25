#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API服务器启动脚本

启动股票分析系统的RESTful API服务器。

Usage:
    python run_api.py [--host HOST] [--port PORT] [--reload]

Author: AI Assistant
Date: 2024
"""

import argparse
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="启动股票分析API服务器")
    parser.add_argument(
        "--host", 
        default="0.0.0.0", 
        help="服务器主机地址 (默认: 0.0.0.0)"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=8000, 
        help="服务器端口 (默认: 8000)"
    )
    parser.add_argument(
        "--reload", 
        action="store_true", 
        help="启用自动重载 (开发模式)"
    )
    parser.add_argument(
        "--log-level", 
        default="info", 
        choices=["critical", "error", "warning", "info", "debug", "trace"],
        help="日志级别 (默认: info)"
    )
    parser.add_argument(
        "--workers", 
        type=int, 
        default=1, 
        help="工作进程数 (默认: 1)"
    )
    
    args = parser.parse_args()
    
    try:
        import uvicorn
    except ImportError:
        print("错误: 未安装uvicorn，请运行: pip install uvicorn")
        sys.exit(1)
    
    print(f"启动股票分析API服务器...")
    print(f"服务器地址: http://{args.host}:{args.port}")
    print(f"API文档: http://{args.host}:{args.port}/docs")
    print(f"交互式文档: http://{args.host}:{args.port}/redoc")
    print(f"健康检查: http://{args.host}:{args.port}/health")
    
    if args.reload:
        print("注意: 启用了自动重载模式 (仅用于开发)")
    
    try:
        uvicorn.run(
            "api.server:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
            log_level=args.log_level,
            workers=args.workers if not args.reload else 1  # reload模式下只能使用1个worker
        )
    except KeyboardInterrupt:
        print("\n服务器已停止")
    except Exception as e:
        print(f"启动服务器时发生错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()