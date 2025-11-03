"""删除操作模块。

提供数据删除功能，使用软删除机制。
"""

from typing import Optional
from datetime import datetime
from src.core.database.connection import DatabaseConnection, DatabaseError
import logging

logger = logging.getLogger(__name__)


class DeleteOperation:
    """删除操作类。
    
    负责执行数据删除操作（软删除）。
    """
    
    def __init__(self, db_connection: DatabaseConnection) -> None:
        """初始化删除操作。
        
        Args:
            db_connection: 数据库连接对象
        """
        self.db = db_connection
    
    def delete(self, table_name: str, record_id: int,
               user: Optional[str] = None) -> int:
        """软删除记录。
        
        Args:
            table_name: 表名
            record_id: 记录 ID
            user: 操作用户名
        
        Returns:
            受影响的行数
        
        Raises:
            DatabaseError: 数据库操作失败时抛出
        """
        try:
            sql = f"""
                UPDATE {table_name}
                SET IsDeleted = 1, UpdateTime = ?, UpdateUser = ?
                WHERE Id = ? AND IsDeleted = 0
            """
            
            parameters = (datetime.now(), user, record_id)
            affected_rows = self.db.execute_non_query(sql, parameters)
            
            if affected_rows > 0:
                logger.info(f"成功删除记录: {table_name} ID={record_id}")
            else:
                logger.warning(f"未找到要删除的记录: {table_name} ID={record_id}")
            
            return affected_rows
        
        except Exception as e:
            logger.error(f"删除记录失败: {table_name} ID={record_id}", exc_info=True)
            raise DatabaseError(f"删除记录失败: {e}") from e
    
    def delete_batch(self, table_name: str, record_ids: list[int],
                     user: Optional[str] = None) -> int:
        """批量软删除记录。
        
        Args:
            table_name: 表名
            record_ids: 记录 ID 列表
            user: 操作用户名
        
        Returns:
            受影响的总行数
        
        Raises:
            DatabaseError: 数据库操作失败时抛出
        """
        try:
            if not record_ids:
                return 0
            
            # 构建参数占位符
            placeholders = ', '.join(['?' for _ in record_ids])
            
            sql = f"""
                UPDATE {table_name}
                SET IsDeleted = 1, UpdateTime = ?, UpdateUser = ?
                WHERE Id IN ({placeholders}) AND IsDeleted = 0
            """
            
            parameters = (datetime.now(), user) + tuple(record_ids)
            affected_rows = self.db.execute_non_query(sql, parameters)
            
            logger.info(f"批量删除完成: {table_name}，共 {affected_rows} 条记录")
            return affected_rows
        
        except Exception as e:
            logger.error(f"批量删除记录失败: {table_name}", exc_info=True)
            raise DatabaseError(f"批量删除记录失败: {e}") from e
    
    def permanent_delete(self, table_name: str, record_id: int) -> int:
        """永久删除记录（物理删除）。
        
        警告：此操作不可恢复，请谨慎使用。
        
        Args:
            table_name: 表名
            record_id: 记录 ID
        
        Returns:
            受影响的行数
        
        Raises:
            DatabaseError: 数据库操作失败时抛出
        """
        try:
            sql = f"DELETE FROM {table_name} WHERE Id = ?"
            
            affected_rows = self.db.execute_non_query(sql, (record_id,))
            
            if affected_rows > 0:
                logger.warning(f"永久删除记录: {table_name} ID={record_id}")
            
            return affected_rows
        
        except Exception as e:
            logger.error(f"永久删除记录失败: {table_name} ID={record_id}", exc_info=True)
            raise DatabaseError(f"永久删除记录失败: {e}") from e

