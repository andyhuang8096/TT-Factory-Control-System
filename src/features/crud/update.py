"""更新操作模块。

提供数据更新功能，使用参数化查询防止 SQL 注入。
"""

from typing import Optional, Dict, Any
from datetime import datetime
from src.core.database.connection import DatabaseConnection, DatabaseError
import logging

logger = logging.getLogger(__name__)


class UpdateOperation:
    """更新操作类。
    
    负责执行数据更新操作。
    """
    
    def __init__(self, db_connection: DatabaseConnection) -> None:
        """初始化更新操作。
        
        Args:
            db_connection: 数据库连接对象
        """
        self.db = db_connection
    
    def update(self, table_name: str, record_id: int, data: Dict[str, Any],
               user: Optional[str] = None) -> int:
        """更新记录。
        
        Args:
            table_name: 表名
            record_id: 记录 ID
            data: 要更新的数据字典
            user: 操作用户名
        
        Returns:
            受影响的行数
        
        Raises:
            DatabaseError: 数据库操作失败时抛出
        """
        try:
            if not data:
                raise ValueError("更新数据不能为空")
            
            # 移除不能更新的字段
            data.pop('Id', None)
            data.pop('CreateTime', None)
            data.pop('CreateUser', None)
            
            # 添加更新字段
            data['UpdateTime'] = datetime.now()
            if user:
                data['UpdateUser'] = user
            
            # 构建 SET 子句
            set_clauses = []
            values = []
            for key, value in data.items():
                set_clauses.append(f"{key} = ?")
                values.append(value)
            
            # 添加 WHERE 参数
            values.append(record_id)
            
            # 构建 SQL
            sql = f"""
                UPDATE {table_name}
                SET {', '.join(set_clauses)}
                WHERE Id = ? AND IsDeleted = 0
            """
            
            # 执行更新
            affected_rows = self.db.execute_non_query(sql, tuple(values))
            
            if affected_rows > 0:
                logger.info(f"成功更新记录: {table_name} ID={record_id}")
            else:
                logger.warning(f"未找到要更新的记录: {table_name} ID={record_id}")
            
            return affected_rows
        
        except Exception as e:
            logger.error(f"更新记录失败: {table_name} ID={record_id}", exc_info=True)
            raise DatabaseError(f"更新记录失败: {e}") from e
    
    def update_batch(self, table_name: str, updates: Dict[int, Dict[str, Any]],
                     user: Optional[str] = None) -> int:
        """批量更新记录。
        
        Args:
            table_name: 表名
            updates: 更新字典，键为记录 ID，值为要更新的数据字典
            user: 操作用户名
        
        Returns:
            受影响的总行数
        
        Raises:
            DatabaseError: 数据库操作失败时抛出
        """
        total_affected = 0
        for record_id, data in updates.items():
            try:
                affected = self.update(table_name, record_id, data, user)
                total_affected += affected
            except Exception as e:
                logger.error(f"批量更新记录失败: ID={record_id}", exc_info=True)
                raise DatabaseError(f"批量更新记录失败: {e}") from e
        
        logger.info(f"批量更新完成: {table_name}，共 {total_affected} 条记录")
        return total_affected

