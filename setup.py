# -*- coding: utf-8 -*-
"""
江恩轮中轮+量价分析系统安装脚本
"""

from setuptools import setup, find_packages
import os

# 读取README文件
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# 读取requirements文件
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="gann-volume-price-analysis",
    version="1.0.0",
    author="Stock Analysis System",
    author_email="",
    description="江恩轮中轮+量价分析系统 - 集成股票数据获取、存储和技术分析的综合系统",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial :: Investment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.7.0",
            "flake8>=6.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "stock-analysis=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.yaml", "*.yml", "*.json", "*.txt"],
    },
    zip_safe=False,
)