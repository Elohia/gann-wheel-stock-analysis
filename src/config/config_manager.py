#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理模块

负责加载和管理系统配置文件，提供配置项的读取和验证功能。

Author: AI Assistant
Date: 2024
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from loguru import logger


class ConfigManager:
    """
    配置管理器
    
    负责加载、验证和管理系统配置
    """
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径
        """
        # 如果是相对路径，则相对于项目根目录
        if not os.path.isabs(config_path):
            project_root = Path(__file__).parent.parent.parent
            self.config_path = project_root / config_path
        else:
            self.config_path = Path(config_path)
        self.config = {}
        self._load_config()
    
    def _load_config(self) -> None:
        """
        加载配置文件
        
        如果配置文件不存在，则从示例配置文件复制
        """
        try:
            # 检查配置文件是否存在
            if not self.config_path.exists():
                example_config_path = self.config_path.parent / "config.example.yaml"
                if example_config_path.exists():
                    logger.warning(f"配置文件 {self.config_path} 不存在，从示例配置复制")
                    self._copy_example_config(example_config_path)
                else:
                    logger.error(f"配置文件和示例配置文件都不存在")
                    raise FileNotFoundError(f"配置文件 {self.config_path} 不存在")
            
            # 加载配置文件
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f) or {}
            
            logger.info(f"配置文件加载成功: {self.config_path}")
            
            # 验证配置
            self._validate_config()
            
        except Exception as e:
            logger.error(f"加载配置文件失败: {str(e)}")
            raise
    
    def _copy_example_config(self, example_path: Path) -> None:
        """
        从示例配置文件复制配置
        
        Args:
            example_path: 示例配置文件路径
        """
        try:
            # 确保目标目录存在
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 复制文件
            with open(example_path, 'r', encoding='utf-8') as src:
                content = src.read()
            
            with open(self.config_path, 'w', encoding='utf-8') as dst:
                dst.write(content)
            
            logger.info(f"已从 {example_path} 复制配置到 {self.config_path}")
            
        except Exception as e:
            logger.error(f"复制示例配置文件失败: {str(e)}")
            raise
    
    def _validate_config(self) -> None:
        """
        验证配置文件的完整性和正确性
        """
        required_sections = [
            'data_sources',
            'database',
            'gann_analysis',
            'volume_price_analysis',
            'logging'
        ]
        
        for section in required_sections:
            if section not in self.config:
                logger.warning(f"配置文件缺少必需的节: {section}")
        
        # 验证数据源配置
        data_sources = self.config.get('data_sources', {})
        if not any(source.get('enabled', False) for source in data_sources.values()):
            logger.warning("没有启用任何数据源")
        
        # 验证数据库配置
        database = self.config.get('database', {})
        if not any(db.get('enabled', False) for db in database.values()):
            logger.warning("没有启用任何数据库")
        
        logger.info("配置文件验证完成")
    
    def get_config(self) -> Dict[str, Any]:
        """
        获取完整配置
        
        Returns:
            配置字典
        """
        return self.config.copy()
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """
        获取指定配置节
        
        Args:
            section: 配置节名称
            
        Returns:
            配置节内容
        """
        return self.config.get(section, {})
    
    def get_value(self, key: str, default: Any = None) -> Any:
        """
        获取配置值，支持点号分隔的嵌套键
        
        Args:
            key: 配置键，支持 'section.subsection.key' 格式
            default: 默认值
            
        Returns:
            配置值
        """
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set_value(self, key: str, value: Any) -> None:
        """
        设置配置值
        
        Args:
            key: 配置键，支持 'section.subsection.key' 格式
            value: 配置值
        """
        keys = key.split('.')
        config = self.config
        
        # 创建嵌套字典结构
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save_config(self) -> None:
        """
        保存配置到文件
        """
        try:
            # 确保目录存在
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, 
                         allow_unicode=True, indent=2)
            
            logger.info(f"配置文件保存成功: {self.config_path}")
            
        except Exception as e:
            logger.error(f"保存配置文件失败: {str(e)}")
            raise
    
    def reload_config(self) -> None:
        """
        重新加载配置文件
        """
        logger.info("重新加载配置文件")
        self._load_config()
    
    def get_data_source_config(self, source_name: str) -> Optional[Dict[str, Any]]:
        """
        获取指定数据源的配置
        
        Args:
            source_name: 数据源名称 (tushare, yfinance, akshare)
            
        Returns:
            数据源配置，如果不存在或未启用则返回None
        """
        data_sources = self.get_section('data_sources')
        source_config = data_sources.get(source_name, {})
        
        if source_config.get('enabled', False):
            return source_config
        else:
            return None
    
    def get_database_config(self) -> Dict[str, Any]:
        """
        获取启用的数据库配置
        
        Returns:
            数据库配置
        """
        database_config = self.get_section('database')
        
        # 查找启用的数据库
        for db_type, config in database_config.items():
            if config.get('enabled', False):
                return {db_type: config}
        
        # 如果没有启用的数据库，返回SQLite默认配置
        return {
            'sqlite': {
                'path': 'data/stock_data.db',
                'enabled': True
            }
        }
    
    def is_data_source_enabled(self, source_name: str) -> bool:
        """
        检查数据源是否启用
        
        Args:
            source_name: 数据源名称
            
        Returns:
            是否启用
        """
        return self.get_data_source_config(source_name) is not None