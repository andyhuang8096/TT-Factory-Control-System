"""读取操作模块。

提供数据查询功能，使用参数化查询防止 SQL 注入。
"""

from typing import Optional, Dict, Any, List
from src.core.database.connection import DatabaseConnection, DatabaseError
import logging

logger = logging.getLogger(__name__)


class ReadOperation:
    """读取操作类。
    
    负责执行数据查询操作。
    """
    
    def __init__(self, db_connection: DatabaseConnection) -> None:
        """初始化读取操作。
        
        Args:
            db_connection: 数据库连接对象
        """
        self.db = db_connection
    
    def get_by_id(self, table_name: str, record_id: int) -> Optional[Dict[str, Any]]:
        """根据 ID 获取记录。
        
        Args:
            table_name: 表名
            record_id: 记录 ID
        
        Returns:
            记录字典，如果不存在则返回 None
        
        Raises:
            DatabaseError: 数据库操作失败时抛出
        """
        try:
            sql = f"""
                SELECT * FROM {table_name}
                WHERE Id = ? AND IsDeleted = 0
            """
            
            results = self.db.execute_query(sql, (record_id,))
            
            if results:
                logger.debug(f"成功获取记录: {table_name} ID={record_id}")
                return results[0]
            else:
                logger.debug(f"记录不存在: {table_name} ID={record_id}")
                return None
        
        except Exception as e:
            logger.error(f"获取记录失败: {table_name} ID={record_id}", exc_info=True)
            raise DatabaseError(f"获取记录失败: {e}") from e
    
    def get_all(self, table_name: str, 
                where_clause: Optional[str] = None,
                parameters: Optional[tuple] = None,
                order_by: Optional[str] = None,
                limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """获取所有记录。
        
        Args:
            table_name: 表名
            where_clause: WHERE 子句（不包含 WHERE 关键字），使用 ? 作为参数占位符
            parameters: WHERE 子句的参数
            order_by: ORDER BY 子句
            limit: 限制返回的记录数
        
        Returns:
            记录字典列表
        
        Raises:
            DatabaseError: 数据库操作失败时抛出
        """
        try:
            sql = f"SELECT * FROM {table_name}"
            
            # 添加 WHERE 子句
            if where_clause:
                sql += f" WHERE {where_clause} AND IsDeleted = 0"
            else:
                sql += " WHERE IsDeleted = 0"
            
            # 添加 TOP 子句（必须在 SELECT 之后）
            if limit:
                sql = sql.replace("SELECT *", f"SELECT TOP {limit} *")
            
            # 添加 ORDER BY 子句
            if order_by:
                sql += f" ORDER BY {order_by}"
            
            results = self.db.execute_query(sql, parameters)
            
            logger.debug(f"成功获取 {len(results)} 条记录: {table_name}")
            return results
        
        except Exception as e:
            logger.error(f"获取记录失败: {table_name}", exc_info=True)
            raise DatabaseError(f"获取记录失败: {e}") from e
    
    def count(self, table_name: str,
              where_clause: Optional[str] = None,
              parameters: Optional[tuple] = None) -> int:
        """统计记录数。
        
        Args:
            table_name: 表名
            where_clause: WHERE 子句（不包含 WHERE 关键字）
            parameters: WHERE 子句的参数
        
        Returns:
            记录数
        
        Raises:
            DatabaseError: 数据库操作失败时抛出
        """
        try:
            sql = f"SELECT COUNT(*) AS Count FROM {table_name}"
            
            if where_clause:
                sql += f" WHERE {where_clause} AND IsDeleted = 0"
            else:
                sql += " WHERE IsDeleted = 0"
            
            result = self.db.execute_scalar(sql, parameters)
            
            return result if result else 0
        
        except Exception as e:
            logger.error(f"统计记录数失败: {table_name}", exc_info=True)
            raise DatabaseError(f"统计记录数失败: {e}") from e
    
    def search(self, table_name: str, search_field: str, search_value: str,
               limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """搜索记录。
        
        Args:
            table_name: 表名
            search_field: 搜索字段名
            search_value: 搜索值（支持模糊匹配）
            limit: 限制返回的记录数
        
        Returns:
            记录字典列表
        
        Raises:
            DatabaseError: 数据库操作失败时抛出
        """
        try:
            where_clause = f"{search_field} LIKE ?"
            parameters = (f"%{search_value}%",)
            
            return self.get_all(table_name, where_clause, parameters, 
                              order_by=None, limit=limit)
        
        except Exception as e:
            logger.error(f"搜索记录失败: {table_name}", exc_info=True)
            raise DatabaseError(f"搜索记录失败: {e}") from e

