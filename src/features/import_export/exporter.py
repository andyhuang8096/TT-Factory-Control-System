"""数据导出模块。

支持将数据库数据导出为 CSV、Excel、JSON 格式。
"""

import csv
import json
import pandas as pd
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime
import logging

from src.core.database.connection import DatabaseConnection, DatabaseError
from src.features.crud.read import ReadOperation

logger = logging.getLogger(__name__)


class ExportError(Exception):
    """导出异常类。"""
    pass


class DataExporter:
    """数据导出类。
    
    负责将数据库数据导出为各种格式的文件。
    """
    
    def __init__(self, db_connection: DatabaseConnection) -> None:
        """初始化数据导出器。
        
        Args:
            db_connection: 数据库连接对象
        """
        self.db = db_connection
        self.read_op = ReadOperation(db_connection)
    
    def export_csv(self, table_name: str, file_path: str,
                   where_clause: Optional[str] = None,
                   parameters: Optional[tuple] = None,
                   columns: Optional[List[str]] = None) -> bool:
        """导出数据为 CSV 格式。
        
        Args:
            table_name: 表名
            file_path: 输出文件路径
            where_clause: WHERE 子句
            parameters: WHERE 子句参数
            columns: 要导出的列名列表，如果为 None 则导出所有列
        
        Returns:
            导出成功返回 True，失败返回 False
        
        Raises:
            ExportError: 导出失败时抛出
        """
        try:
            # 查询数据
            rows = self.read_op.get_all(table_name, where_clause, parameters)
            
            if not rows:
                logger.warning(f"没有数据可导出: {table_name}")
                return False
            
            # 过滤列
            if columns:
                rows = [{k: v for k, v in row.items() if k in columns} 
                       for row in rows]
            
            # 获取列名
            if columns:
                fieldnames = columns
            else:
                fieldnames = list(rows[0].keys()) if rows else []
            
            # 写入 CSV 文件
            file_path_obj = Path(file_path)
            file_path_obj.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for row in rows:
                    # 处理 datetime 对象
                    clean_row = {}
                    for key, value in row.items():
                        if isinstance(value, datetime):
                            clean_row[key] = value.isoformat()
                        else:
                            clean_row[key] = value
                    writer.writerow(clean_row)
            
            logger.info(f"CSV 导出成功: {table_name} -> {file_path} ({len(rows)} 条记录)")
            return True
        
        except Exception as e:
            logger.error(f"CSV 导出失败: {file_path}", exc_info=True)
            raise ExportError(f"CSV 导出失败: {e}") from e
    
    def export_excel(self, table_name: str, file_path: str,
                     where_clause: Optional[str] = None,
                     parameters: Optional[tuple] = None,
                     columns: Optional[List[str]] = None,
                     sheet_name: str = "Sheet1") -> bool:
        """导出数据为 Excel 格式。
        
        Args:
            table_name: 表名
            file_path: 输出文件路径
            where_clause: WHERE 子句
            parameters: WHERE 子句参数
            columns: 要导出的列名列表
            sheet_name: 工作表名称
        
        Returns:
            导出成功返回 True，失败返回 False
        
        Raises:
            ExportError: 导出失败时抛出
        """
        try:
            # 查询数据
            rows = self.read_op.get_all(table_name, where_clause, parameters)
            
            if not rows:
                logger.warning(f"没有数据可导出: {table_name}")
                return False
            
            # 过滤列
            if columns:
                rows = [{k: v for k, v in row.items() if k in columns} 
                       for row in rows]
            
            # 转换为 DataFrame
            df = pd.DataFrame(rows)
            
            # 写入 Excel 文件
            file_path_obj = Path(file_path)
            file_path_obj.parent.mkdir(parents=True, exist_ok=True)
            
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            logger.info(
                f"Excel 导出成功: {table_name} -> {file_path} "
                f"({len(rows)} 条记录)"
            )
            return True
        
        except Exception as e:
            logger.error(f"Excel 导出失败: {file_path}", exc_info=True)
            raise ExportError(f"Excel 导出失败: {e}") from e
    
    def export_json(self, table_name: str, file_path: str,
                    where_clause: Optional[str] = None,
                    parameters: Optional[tuple] = None,
                    columns: Optional[List[str]] = None,
                    indent: int = 2) -> bool:
        """导出数据为 JSON 格式。
        
        Args:
            table_name: 表名
            file_path: 输出文件路径
            where_clause: WHERE 子句
            parameters: WHERE 子句参数
            columns: 要导出的列名列表
            indent: JSON 缩进空格数
        
        Returns:
            导出成功返回 True，失败返回 False
        
        Raises:
            ExportError: 导出失败时抛出
        """
        try:
            # 查询数据
            rows = self.read_op.get_all(table_name, where_clause, parameters)
            
            if not rows:
                logger.warning(f"没有数据可导出: {table_name}")
                return False
            
            # 过滤列
            if columns:
                rows = [{k: v for k, v in row.items() if k in columns} 
                       for row in rows]
            
            # 处理 datetime 对象
            json_rows = []
            for row in rows:
                json_row = {}
                for key, value in row.items():
                    if isinstance(value, datetime):
                        json_row[key] = value.isoformat()
                    else:
                        json_row[key] = value
                json_rows.append(json_row)
            
            # 写入 JSON 文件
            file_path_obj = Path(file_path)
            file_path_obj.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(json_rows, f, ensure_ascii=False, indent=indent)
            
            logger.info(
                f"JSON 导出成功: {table_name} -> {file_path} "
                f"({len(rows)} 条记录)"
            )
            return True
        
        except Exception as e:
            logger.error(f"JSON 导出失败: {file_path}", exc_info=True)
            raise ExportError(f"JSON 导出失败: {e}") from e

