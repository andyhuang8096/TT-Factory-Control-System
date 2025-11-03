"""创建操作模块。

提供数据创建功能，使用参数化查询防止 SQL 注入。
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from src.core.database.connection import DatabaseConnection, DatabaseError
from src.core.database.models import BaseModel
import logging

logger = logging.getLogger(__name__)


class CreateOperation:
    """创建操作类。
    
    负责执行数据插入操作。
    """
    
    def __init__(self, db_connection: DatabaseConnection) -> None:
        """初始化创建操作。
        
        Args:
            db_connection: 数据库连接对象
        """
        self.db = db_connection
    
    def create(self, table_name: str, data: Dict[str, Any], 
               user: Optional[str] = None) -> int:
        """创建记录。
        
        Args:
            table_name: 表名
            data: 数据字典
            user: 操作用户名
        
        Returns:
            新创建记录的 ID
        
        Raises:
            DatabaseError: 数据库操作失败时抛出
        """
        try:
            # 构建列名和值
            columns = list(data.keys())
            
            # 添加审计字段
            now = datetime.now()
            if 'CreateTime' not in columns:
                columns.append('CreateTime')
                data['CreateTime'] = now
            if 'UpdateTime' not in columns:
                columns.append('UpdateTime')
                data['UpdateTime'] = now
            if user and 'CreateUser' not in columns:
                columns.append('CreateUser')
                data['CreateUser'] = user
            
            # 在添加完所有列后，构建占位符
            placeholders = ', '.join(['?' for _ in columns])
            column_names = ', '.join(columns)
            
            # 构建参数值
            values = tuple(data[col] for col in columns)
            
            # 构建 SQL
            sql = f"""
                INSERT INTO {table_name} ({', '.join(columns)})
                OUTPUT INSERTED.Id
                VALUES ({placeholders})
            """
            
            # 执行插入
            result = self.db.execute_scalar(sql, values)
            
            if result:
                logger.info(f"成功创建记录到 {table_name}，ID: {result}")
                return result
            else:
                raise DatabaseError("创建记录失败，未返回 ID")
        
        except Exception as e:
            logger.error(f"创建记录失败: {table_name}", exc_info=True)
            raise DatabaseError(f"创建记录失败: {e}") from e
    
    def create_batch(self, table_name: str, data_list: List[Dict[str, Any]],
                     user: Optional[str] = None) -> List[int]:
        """批量创建记录。
        
        Args:
            table_name: 表名
            data_list: 数据字典列表
            user: 操作用户名
        
        Returns:
            新创建记录的 ID 列表
        
        Raises:
            DatabaseError: 数据库操作失败时抛出
        """
        ids = []
        for data in data_list:
            try:
                record_id = self.create(table_name, data, user)
                ids.append(record_id)
            except Exception as e:
                logger.error(f"批量创建记录失败: {e}")
                raise DatabaseError(f"批量创建记录失败: {e}") from e
        
        logger.info(f"批量创建 {len(ids)} 条记录到 {table_name}")
        return ids

