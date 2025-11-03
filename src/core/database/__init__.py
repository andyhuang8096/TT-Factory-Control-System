"""数据库模块。

导出数据库连接、模型和查询相关功能。
"""

from src.core.database.connection import DatabaseConnection, DatabaseError
from src.core.database.models import (
    BaseModel,
    UserTable,
    PPIDRecord,
    ImportLog,
    BackupLog,
    AuditLog,
    TABLE_NAMES
)
from src.core.database.queries import CREATE_TABLES

from typing import Optional
from src.core.config.config_manager import ConfigManager
import logging

logger = logging.getLogger(__name__)


class DatabaseConnectionFactory:
    """数据库连接工厂类。
    
    负责从配置管理器创建数据库连接对象。
    """
    
    @staticmethod
    def create_from_config(config: ConfigManager) -> DatabaseConnection:
        """从配置管理器创建数据库连接。
        
        Args:
            config: 配置管理器实例
        
        Returns:
            数据库连接对象
        
        Raises:
            ValueError: 配置缺失时抛出
        """
        db_config = config.get_database_config()
        
        server = db_config.get('server')
        database = db_config.get('database')
        login = db_config.get('login')
        password = db_config.get('password', '')  # 允许空密码（Windows 身份验证）
        
        if not all([server, database, login]):
            missing = []
            if not server:
                missing.append('server')
            if not database:
                missing.append('database')
            if not login:
                missing.append('login')
            raise ValueError(f"数据库配置不完整，缺少: {', '.join(missing)}")
        
        # 解析服务器地址和端口
        if ',' in server:
            server_parts = server.split(',')
            server_addr = server_parts[0].strip()
            port = int(server_parts[1].strip()) if len(server_parts) > 1 else 1433
        else:
            server_addr = server.strip()
            port = 1433
        
        logger.info(f"创建数据库连接: {server_addr}:{port}/{database}")
        
        return DatabaseConnection(
            server=server_addr,
            database=database,
            login=login,
            password=password,
            port=port,
            encrypt=True
        )


__all__ = [
    'DatabaseConnection',
    'DatabaseError',
    'DatabaseConnectionFactory',
    'BaseModel',
    'UserTable',
    'PPIDRecord',
    'ImportLog',
    'BackupLog',
    'AuditLog',
    'TABLE_NAMES',
    'CREATE_TABLES',
]
