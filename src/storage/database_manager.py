#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库管理模块

提供统一的数据库操作接口，支持SQLite和MySQL数据库。
负责股票数据的存储、查询和管理。

Author: AI Assistant
Date: 2024
"""

import sqlite3
import pandas as pd
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from loguru import logger

try:
    from sqlalchemy import create_engine, text, MetaData, Table, Column, String, Float, DateTime, Integer, Index
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.ext.declarative import declarative_base
except ImportError:
    logger.error("SQLAlchemy未安装，数据库功能将不可用")
    raise


Base = declarative_base()


class StockData(Base):
    """
    股票数据表模型
    """
    __tablename__ = 'stock_data'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, index=True)
    date = Column(DateTime, nullable=False, index=True)
    open_price = Column(Float, nullable=False)
    high_price = Column(Float, nullable=False)
    low_price = Column(Float, nullable=False)
    close_price = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    change_pct = Column(Float)
    change_amount = Column(Float)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 创建复合索引
    __table_args__ = (
        Index('idx_symbol_date', 'symbol', 'date'),
    )


class AnalysisResult(Base):
    """
    分析结果表模型
    """
    __tablename__ = 'analysis_results'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, index=True)
    analysis_type = Column(String(50), nullable=False)  # 'gann', 'volume_price'
    analysis_date = Column(DateTime, nullable=False, index=True)
    result_data = Column(String(10000))  # JSON格式存储分析结果
    created_at = Column(DateTime, default=datetime.now)
    
    # 创建复合索引
    __table_args__ = (
        Index('idx_symbol_type_date', 'symbol', 'analysis_type', 'analysis_date'),
    )


class DatabaseManager:
    """
    数据库管理器
    
    提供统一的数据库操作接口
    """
    
    def __init__(self, database_config: Dict[str, Any]):
        """
        初始化数据库管理器
        
        Args:
            database_config: 数据库配置
        """
        self.config = database_config
        self.engine = None
        self.Session = None
        
        # 初始化数据库连接
        self._init_database()
        
        logger.info("数据库管理器初始化完成")
    
    def _init_database(self) -> None:
        """
        初始化数据库连接
        """
        # 查找启用的数据库配置
        db_type = None
        db_config = None
        
        for db_name, config in self.config.items():
            if config.get('enabled', False):
                db_type = db_name
                db_config = config
                break
        
        if db_type is None:
            # 默认使用SQLite
            db_type = 'sqlite'
            db_config = {
                'path': 'data/stock_data.db',
                'enabled': True
            }
            logger.info("未找到启用的数据库配置，使用默认SQLite配置")
        
        # 创建数据库引擎
        if db_type == 'sqlite':
            self._init_sqlite(db_config)
        elif db_type == 'mysql':
            self._init_mysql(db_config)
        else:
            raise ValueError(f"不支持的数据库类型: {db_type}")
        
        # 创建会话工厂
        self.Session = sessionmaker(bind=self.engine)
        
        # 创建表
        self._create_tables()
    
    def _init_sqlite(self, config: Dict[str, Any]) -> None:
        """
        初始化SQLite数据库
        
        Args:
            config: SQLite配置
        """
        db_path = Path(config['path'])
        
        # 确保数据库目录存在
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 创建SQLite引擎
        self.engine = create_engine(
            f'sqlite:///{db_path}',
            echo=False,
            pool_pre_ping=True
        )
        
        logger.info(f"SQLite数据库初始化成功: {db_path}")
    
    def _init_mysql(self, config: Dict[str, Any]) -> None:
        """
        初始化MySQL数据库
        
        Args:
            config: MySQL配置
        """
        host = config.get('host', 'localhost')
        port = config.get('port', 3306)
        username = config.get('username', 'root')
        password = config.get('password', '')
        database = config.get('database', 'stock_analysis')
        
        # 创建MySQL连接字符串
        connection_string = f'mysql+pymysql://{username}:{password}@{host}:{port}/{database}?charset=utf8mb4'
        
        # 创建MySQL引擎
        self.engine = create_engine(
            connection_string,
            echo=False,
            pool_pre_ping=True,
            pool_recycle=3600
        )
        
        logger.info(f"MySQL数据库初始化成功: {host}:{port}/{database}")
    
    def _create_tables(self) -> None:
        """
        创建数据库表
        """
        try:
            Base.metadata.create_all(self.engine)
            logger.info("数据库表创建成功")
        except Exception as e:
            logger.error(f"创建数据库表失败: {str(e)}")
            raise
    
    def save_stock_data(self, symbol: str, data: pd.DataFrame) -> bool:
        """
        保存股票数据
        
        Args:
            symbol: 股票代码
            data: 股票数据DataFrame
            
        Returns:
            是否保存成功
        """
        try:
            session = self.Session()
            
            # 删除已存在的数据（避免重复）
            date_range = (data.index.min(), data.index.max())
            session.query(StockData).filter(
                StockData.symbol == symbol,
                StockData.date >= date_range[0],
                StockData.date <= date_range[1]
            ).delete()
            
            # 准备新数据
            records = []
            for date, row in data.iterrows():
                record = StockData(
                    symbol=symbol,
                    date=date,
                    open_price=float(row['Open']),
                    high_price=float(row['High']),
                    low_price=float(row['Low']),
                    close_price=float(row['Close']),
                    volume=float(row['Volume']),
                    change_pct=float(row.get('Change', 0)) if pd.notna(row.get('Change', 0)) else None,
                    change_amount=float(row.get('Change_Amount', 0)) if pd.notna(row.get('Change_Amount', 0)) else None
                )
                records.append(record)
            
            # 批量插入
            session.add_all(records)
            session.commit()
            
            logger.info(f"成功保存 {symbol} 的 {len(records)} 条数据")
            return True
            
        except Exception as e:
            logger.error(f"保存股票数据失败: {str(e)}")
            session.rollback()
            return False
        finally:
            session.close()
    
    def get_stock_data(self, symbol: str, start_date: Optional[datetime] = None, 
                      end_date: Optional[datetime] = None) -> Optional[pd.DataFrame]:
        """
        获取股票数据
        
        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            股票数据DataFrame
        """
        try:
            session = self.Session()
            
            # 构建查询
            query = session.query(StockData).filter(StockData.symbol == symbol)
            
            if start_date:
                query = query.filter(StockData.date >= start_date)
            
            if end_date:
                query = query.filter(StockData.date <= end_date)
            
            # 按日期排序
            query = query.order_by(StockData.date)
            
            # 执行查询
            results = query.all()
            
            if not results:
                logger.warning(f"未找到股票 {symbol} 的数据")
                return None
            
            # 转换为DataFrame
            data = []
            for record in results:
                data.append({
                    'Date': record.date,
                    'Open': record.open_price,
                    'High': record.high_price,
                    'Low': record.low_price,
                    'Close': record.close_price,
                    'Volume': record.volume,
                    'Change': record.change_pct,
                    'Change_Amount': record.change_amount,
                    'Symbol': record.symbol
                })
            
            df = pd.DataFrame(data)
            df.set_index('Date', inplace=True)
            
            logger.info(f"成功获取 {symbol} 的 {len(df)} 条数据")
            return df
            
        except Exception as e:
            logger.error(f"获取股票数据失败: {str(e)}")
            return None
        finally:
            session.close()
    
    def save_analysis_result(self, symbol: str, analysis_type: str, 
                           result_data: str, analysis_date: Optional[datetime] = None) -> bool:
        """
        保存分析结果
        
        Args:
            symbol: 股票代码
            analysis_type: 分析类型
            result_data: 分析结果（JSON字符串）
            analysis_date: 分析日期
            
        Returns:
            是否保存成功
        """
        try:
            session = self.Session()
            
            if analysis_date is None:
                analysis_date = datetime.now()
            
            # 删除已存在的同类型分析结果
            session.query(AnalysisResult).filter(
                AnalysisResult.symbol == symbol,
                AnalysisResult.analysis_type == analysis_type,
                AnalysisResult.analysis_date.cast(String).like(f"{analysis_date.strftime('%Y-%m-%d')}%")
            ).delete()
            
            # 创建新记录
            record = AnalysisResult(
                symbol=symbol,
                analysis_type=analysis_type,
                analysis_date=analysis_date,
                result_data=result_data
            )
            
            session.add(record)
            session.commit()
            
            logger.info(f"成功保存 {symbol} 的 {analysis_type} 分析结果")
            return True
            
        except Exception as e:
            logger.error(f"保存分析结果失败: {str(e)}")
            session.rollback()
            return False
        finally:
            session.close()
    
    def get_analysis_result(self, symbol: str, analysis_type: str, 
                          analysis_date: Optional[datetime] = None) -> Optional[str]:
        """
        获取分析结果
        
        Args:
            symbol: 股票代码
            analysis_type: 分析类型
            analysis_date: 分析日期（可选，默认获取最新的）
            
        Returns:
            分析结果JSON字符串
        """
        try:
            session = self.Session()
            
            query = session.query(AnalysisResult).filter(
                AnalysisResult.symbol == symbol,
                AnalysisResult.analysis_type == analysis_type
            )
            
            if analysis_date:
                query = query.filter(
                    AnalysisResult.analysis_date.cast(String).like(f"{analysis_date.strftime('%Y-%m-%d')}%")
                )
            
            # 获取最新的结果
            result = query.order_by(AnalysisResult.analysis_date.desc()).first()
            
            if result:
                return result.result_data
            else:
                return None
                
        except Exception as e:
            logger.error(f"获取分析结果失败: {str(e)}")
            return None
        finally:
            session.close()
    
    def get_available_symbols(self) -> List[str]:
        """
        获取数据库中所有可用的股票代码
        
        Returns:
            股票代码列表
        """
        try:
            session = self.Session()
            
            results = session.query(StockData.symbol).distinct().all()
            symbols = [result[0] for result in results]
            
            return symbols
            
        except Exception as e:
            logger.error(f"获取股票代码列表失败: {str(e)}")
            return []
        finally:
            session.close()
    
    def get_data_date_range(self, symbol: str) -> Optional[tuple]:
        """
        获取指定股票的数据日期范围
        
        Args:
            symbol: 股票代码
            
        Returns:
            (最早日期, 最晚日期) 或 None
        """
        try:
            session = self.Session()
            
            result = session.query(
                session.query(StockData.date).filter(StockData.symbol == symbol).order_by(StockData.date.asc()).limit(1).subquery().c.date.label('min_date'),
                session.query(StockData.date).filter(StockData.symbol == symbol).order_by(StockData.date.desc()).limit(1).subquery().c.date.label('max_date')
            ).first()
            
            if result and result[0] and result[1]:
                return (result[0], result[1])
            else:
                return None
                
        except Exception as e:
            logger.error(f"获取数据日期范围失败: {str(e)}")
            return None
        finally:
            session.close()
    
    def cleanup_old_data(self, days: int = 365) -> bool:
        """
        清理旧数据
        
        Args:
            days: 保留天数
            
        Returns:
            是否清理成功
        """
        try:
            session = self.Session()
            
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # 删除旧的股票数据
            deleted_stock = session.query(StockData).filter(
                StockData.date < cutoff_date
            ).delete()
            
            # 删除旧的分析结果
            deleted_analysis = session.query(AnalysisResult).filter(
                AnalysisResult.analysis_date < cutoff_date
            ).delete()
            
            session.commit()
            
            logger.info(f"清理完成：删除了 {deleted_stock} 条股票数据，{deleted_analysis} 条分析结果")
            return True
            
        except Exception as e:
            logger.error(f"清理旧数据失败: {str(e)}")
            session.rollback()
            return False
        finally:
            session.close()
    
    def get_database_stats(self) -> Dict[str, Any]:
        """
        获取数据库统计信息
        
        Returns:
            统计信息字典
        """
        try:
            session = self.Session()
            
            # 股票数据统计
            stock_count = session.query(StockData).count()
            symbol_count = session.query(StockData.symbol).distinct().count()
            
            # 分析结果统计
            analysis_count = session.query(AnalysisResult).count()
            
            # 最新数据日期
            latest_date = session.query(StockData.date).order_by(StockData.date.desc()).first()
            latest_date = latest_date[0] if latest_date else None
            
            stats = {
                'stock_records': stock_count,
                'unique_symbols': symbol_count,
                'analysis_records': analysis_count,
                'latest_data_date': latest_date
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"获取数据库统计信息失败: {str(e)}")
            return {}
        finally:
            session.close()
    
    def close(self) -> None:
        """
        关闭数据库连接
        """
        if self.engine:
            self.engine.dispose()
            logger.info("数据库连接已关闭")