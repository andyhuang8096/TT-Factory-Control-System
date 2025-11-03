"""数据导入模块。

支持从 CSV、Excel、JSON 文件导入数据到数据库。
"""

import csv
import json
import pandas as pd
from typing import List, Dict, Any, Optional, Callable
from pathlib import Path
from datetime import datetime
import logging

from src.core.database.connection import DatabaseConnection, DatabaseError
from src.features.crud.create import CreateOperation
from src.core.config.config_manager import ConfigManager

logger = logging.getLogger(__name__)


class ImportError(Exception):
    """导入异常类。"""
    pass


class DataImporter:
    """数据导入类。
    
    负责从各种格式的文件导入数据到数据库。
    """
    
    def __init__(self, db_connection: DatabaseConnection, 
                 config: ConfigManager) -> None:
        """初始化数据导入器。
        
        Args:
            db_connection: 数据库连接对象
            config: 配置管理器
        """
        self.db = db_connection
        self.config = config
        self.create_op = CreateOperation(db_connection)
        
        # 获取导入配置
        import_config = config.get_import_config()
        self.separator = import_config.get('separator', ',')
        self.skip_lines = int(import_config.get('skipline', '0'))
    
    def import_csv(self, file_path: str, table_name: str,
                  column_mapping: Optional[Dict[str, str]] = None,
                  user: Optional[str] = None) -> Dict[str, Any]:
        """从 CSV 文件导入数据。
        
        Args:
            file_path: CSV 文件路径
            table_name: 目标表名
            column_mapping: 列映射字典，键为文件列名，值为数据库列名
            user: 操作用户名
        
        Returns:
            导入结果字典，包含成功和失败的行数
        
        Raises:
            ImportError: 导入失败时抛出
        """
        try:
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                raise ImportError(f"文件不存在: {file_path}")
            
            # 记录导入开始
            start_time = datetime.now()
            
            # 读取 CSV 文件
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                # 跳过指定行数
                for _ in range(self.skip_lines):
                    next(f, None)
                
                reader = csv.DictReader(f, delimiter=self.separator)
                rows = list(reader)
            
            # 映射列名
            if column_mapping:
                mapped_rows = []
                for row in rows:
                    mapped_row = {}
                    for file_col, db_col in column_mapping.items():
                        if file_col in row:
                            mapped_row[db_col] = row[file_col]
                    mapped_rows.append(mapped_row)
                rows = mapped_rows
            
            # 批量导入
            success_count = 0
            failed_count = 0
            errors = []
            
            for idx, row in enumerate(rows, start=1):
                try:
                    # 清理空值
                    row = {k: v if v and v.strip() else None 
                          for k, v in row.items()}
                    
                    self.create_op.create(table_name, row, user)
                    success_count += 1
                except Exception as e:
                    failed_count += 1
                    error_msg = f"第 {idx} 行: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)
            
            end_time = datetime.now()
            
            result = {
                'total_rows': len(rows),
                'success_rows': success_count,
                'failed_rows': failed_count,
                'errors': errors[:10],  # 只保留前10个错误
                'start_time': start_time,
                'end_time': end_time,
                'duration': (end_time - start_time).total_seconds()
            }
            
            logger.info(
                f"CSV 导入完成: {file_path} -> {table_name}, "
                f"成功: {success_count}, 失败: {failed_count}"
            )
            
            return result
        
        except Exception as e:
            logger.error(f"CSV 导入失败: {file_path}", exc_info=True)
            raise ImportError(f"CSV 导入失败: {e}") from e
    
    def import_excel(self, file_path: str, table_name: str,
                     sheet_name: Optional[str] = None,
                     column_mapping: Optional[Dict[str, str]] = None,
                     user: Optional[str] = None) -> Dict[str, Any]:
        """从 Excel 文件导入数据。
        
        Args:
            file_path: Excel 文件路径
            table_name: 目标表名
            sheet_name: 工作表名称，如果为 None 则使用第一个工作表
            column_mapping: 列映射字典
            user: 操作用户名
        
        Returns:
            导入结果字典
        
        Raises:
            ImportError: 导入失败时抛出
        """
        try:
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                raise ImportError(f"文件不存在: {file_path}")
            
            start_time = datetime.now()
            
            # 读取 Excel 文件
            df = pd.read_excel(file_path, sheet_name=sheet_name, 
                              skiprows=self.skip_lines)
            
            # 转换为字典列表
            rows = df.to_dict('records')
            
            # 映射列名
            if column_mapping:
                mapped_rows = []
                for row in rows:
                    mapped_row = {}
                    for file_col, db_col in column_mapping.items():
                        if file_col in row:
                            mapped_row[db_col] = row[file_col]
                    mapped_rows.append(mapped_row)
                rows = mapped_rows
            
            # 批量导入
            success_count = 0
            failed_count = 0
            errors = []
            
            for idx, row in enumerate(rows, start=1):
                try:
                    # 处理 NaN 值
                    row = {k: (None if pd.isna(v) else v) 
                          for k, v in row.items()}
                    
                    self.create_op.create(table_name, row, user)
                    success_count += 1
                except Exception as e:
                    failed_count += 1
                    error_msg = f"第 {idx} 行: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)
            
            end_time = datetime.now()
            
            result = {
                'total_rows': len(rows),
                'success_rows': success_count,
                'failed_rows': failed_count,
                'errors': errors[:10],
                'start_time': start_time,
                'end_time': end_time,
                'duration': (end_time - start_time).total_seconds()
            }
            
            logger.info(
                f"Excel 导入完成: {file_path} -> {table_name}, "
                f"成功: {success_count}, 失败: {failed_count}"
            )
            
            return result
        
        except Exception as e:
            logger.error(f"Excel 导入失败: {file_path}", exc_info=True)
            raise ImportError(f"Excel 导入失败: {e}") from e
    
    def import_json(self, file_path: str, table_name: str,
                    column_mapping: Optional[Dict[str, str]] = None,
                    user: Optional[str] = None) -> Dict[str, Any]:
        """从 JSON 文件导入数据。
        
        Args:
            file_path: JSON 文件路径
            table_name: 目标表名
            column_mapping: 列映射字典
            user: 操作用户名
        
        Returns:
            导入结果字典
        
        Raises:
            ImportError: 导入失败时抛出
        """
        try:
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                raise ImportError(f"文件不存在: {file_path}")
            
            start_time = datetime.now()
            
            # 读取 JSON 文件
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 如果是单个对象，转换为列表
            if isinstance(data, dict):
                rows = [data]
            elif isinstance(data, list):
                rows = data
            else:
                raise ImportError("JSON 格式不正确，应为对象或数组")
            
            # 映射列名
            if column_mapping:
                mapped_rows = []
                for row in rows:
                    mapped_row = {}
                    for file_col, db_col in column_mapping.items():
                        if file_col in row:
                            mapped_row[db_col] = row[file_col]
                    mapped_rows.append(mapped_row)
                rows = mapped_rows
            
            # 批量导入
            success_count = 0
            failed_count = 0
            errors = []
            
            for idx, row in enumerate(rows, start=1):
                try:
                    self.create_op.create(table_name, row, user)
                    success_count += 1
                except Exception as e:
                    failed_count += 1
                    error_msg = f"第 {idx} 行: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)
            
            end_time = datetime.now()
            
            result = {
                'total_rows': len(rows),
                'success_rows': success_count,
                'failed_rows': failed_count,
                'errors': errors[:10],
                'start_time': start_time,
                'end_time': end_time,
                'duration': (end_time - start_time).total_seconds()
            }
            
            logger.info(
                f"JSON 导入完成: {file_path} -> {table_name}, "
                f"成功: {success_count}, 失败: {failed_count}"
            )
            
            return result
        
        except Exception as e:
            logger.error(f"JSON 导入失败: {file_path}", exc_info=True)
            raise ImportError(f"JSON 导入失败: {e}") from e

