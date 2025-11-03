"""数据库连接模块。

负责管理 SQL Server 2019 数据库连接，包括连接池管理和异常处理。
"""

import pyodbc
from typing import Optional, List, Dict, Any, Tuple
import logging
from contextlib import contextmanager
from threading import Lock

logger = logging.getLogger(__name__)


class DatabaseError(Exception):
    """数据库操作异常类。"""
    pass


class DatabaseConnection:
    """数据库连接管理类。
    
    负责管理 SQL Server 数据库连接，包括连接池管理和异常处理。
    使用参数化查询防止 SQL 注入。
    """
    
    def __init__(self, server: str, database: str, login: str, password: str,
                 port: int = 1433, encrypt: bool = True, timeout: int = 30) -> None:
        """初始化数据库连接。
        
        Args:
            server: 数据库服务器地址
            database: 数据库名称
            login: 登录用户名
            password: 登录密码
            port: 端口号，默认 1433
            encrypt: 是否使用加密连接，默认 True
            timeout: 连接超时时间（秒），默认 30
        """
        self.server = server
        self.database = database
        self.login = login
        self.password = password
        self.port = port
        self.encrypt = encrypt
        self.timeout = timeout
        
        self._connection: Optional[pyodbc.Connection] = None
        self._lock = Lock()
    
    def _get_connection_string(self) -> str:
        """构建数据库连接字符串。
        
        Returns:
            数据库连接字符串
        """
        driver = "{ODBC Driver 17 for SQL Server}"  # SQL Server 2019 推荐驱动
        
        connection_string = (
            f"DRIVER={driver};"
            f"SERVER={self.server},{self.port};"
            f"DATABASE={self.database};"
            f"UID={self.login};"
            f"PWD={self.password};"
            f"Encrypt={'yes' if self.encrypt else 'no'};"
            f"TrustServerCertificate=yes;"
            f"Connection Timeout={self.timeout};"
        )
        
        return connection_string
    
    def connect(self) -> bool:
        """建立数据库连接。
        
        Returns:
            连接成功返回 True，失败返回 False
        """
        try:
            connection_string = self._get_connection_string()
            self._connection = pyodbc.connect(connection_string)
            logger.info(f"数据库连接成功: {self.server}/{self.database}")
            return True
        except pyodbc.Error as e:
            logger.error(f"数据库连接失败: {e}", exc_info=True)
            raise DatabaseError(f"数据库连接失败: {e}") from e
    
    def disconnect(self) -> None:
        """关闭数据库连接。"""
        if self._connection:
            try:
                self._connection.close()
                logger.info("数据库连接已关闭")
            except Exception as e:
                logger.error(f"关闭数据库连接时出错: {e}", exc_info=True)
            finally:
                self._connection = None
    
    def is_connected(self) -> bool:
        """检查数据库连接状态。
        
        Returns:
            如果已连接返回 True，否则返回 False
        """
        return self._connection is not None
    
    @contextmanager
    def get_cursor(self):
        """获取数据库游标的上下文管理器。
        
        Yields:
            数据库游标对象
        
        Raises:
            DatabaseError: 数据库操作失败时抛出
        """
        if not self.is_connected():
            self.connect()
        
        cursor = None
        try:
            cursor = self._connection.cursor()
            yield cursor
            self._connection.commit()
        except pyodbc.Error as e:
            if self._connection:
                self._connection.rollback()
            logger.error(f"数据库操作失败: {e}", exc_info=True)
            raise DatabaseError(f"数据库操作失败: {e}") from e
        finally:
            if cursor:
                cursor.close()
    
    def execute_query(self, query: str, parameters: Optional[Tuple] = None) -> List[Dict[str, Any]]:
        """执行查询语句。
        
        使用参数化查询防止 SQL 注入。
        
        Args:
            query: SQL 查询语句（使用 ? 作为参数占位符）
            parameters: 查询参数元组
        
        Returns:
            查询结果列表，每个元素是一个字典
        
        Raises:
            DatabaseError: 数据库操作失败时抛出
        """
        with self.get_cursor() as cursor:
            try:
                if parameters:
                    cursor.execute(query, parameters)
                else:
                    cursor.execute(query)
                
                # 获取列名
                columns = [column[0] for column in cursor.description]
                
                # 获取所有行
                rows = cursor.fetchall()
                
                # 转换为字典列表
                results = [dict(zip(columns, row)) for row in rows]
                
                logger.debug(f"查询执行成功，返回 {len(results)} 条记录")
                return results
            except pyodbc.Error as e:
                logger.error(f"查询执行失败: {query[:100]}...", exc_info=True)
                raise DatabaseError(f"查询执行失败: {e}") from e
    
    def execute_non_query(self, query: str, parameters: Optional[Tuple] = None) -> int:
        """执行非查询语句（INSERT, UPDATE, DELETE）。
        
        使用参数化查询防止 SQL 注入。
        
        Args:
            query: SQL 语句（使用 ? 作为参数占位符）
            parameters: 参数元组
        
        Returns:
            受影响的行数
        
        Raises:
            DatabaseError: 数据库操作失败时抛出
        """
        with self.get_cursor() as cursor:
            try:
                if parameters:
                    cursor.execute(query, parameters)
                else:
                    cursor.execute(query)
                
                affected_rows = cursor.rowcount
                logger.debug(f"执行成功，影响 {affected_rows} 行")
                return affected_rows
            except pyodbc.Error as e:
                logger.error(f"执行失败: {query[:100]}...", exc_info=True)
                raise DatabaseError(f"执行失败: {e}") from e
    
    def execute_scalar(self, query: str, parameters: Optional[Tuple] = None) -> Any:
        """执行标量查询（返回单个值）。
        
        Args:
            query: SQL 查询语句
            parameters: 查询参数元组
        
        Returns:
            查询结果的第一行第一列的值
        
        Raises:
            DatabaseError: 数据库操作失败时抛出
        """
        results = self.execute_query(query, parameters)
        if results and len(results) > 0:
            first_row = results[0]
            if first_row:
                return list(first_row.values())[0]
        return None
    
    def test_connection(self) -> bool:
        """测试数据库连接。
        
        Returns:
            连接成功返回 True，失败返回 False
        """
        try:
            result = self.execute_scalar("SELECT 1")
            return result == 1
        except Exception as e:
            logger.error(f"连接测试失败: {e}")
            return False
    
    def __enter__(self):
        """上下文管理器入口。"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口。"""
        self.disconnect()

