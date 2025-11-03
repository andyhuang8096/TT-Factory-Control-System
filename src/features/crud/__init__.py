"""CRUD 操作模块。

提供统一的 CRUD 操作接口。
"""

from src.features.crud.create import CreateOperation
from src.features.crud.read import ReadOperation
from src.features.crud.update import UpdateOperation
from src.features.crud.delete import DeleteOperation
from src.core.database.connection import DatabaseConnection


class CRUDOperations:
    """CRUD 操作封装类。
    
    提供统一的 CRUD 操作接口。
    """
    
    def __init__(self, db_connection: DatabaseConnection) -> None:
        """初始化 CRUD 操作。
        
        Args:
            db_connection: 数据库连接对象
        """
        self.db = db_connection
        self.create = CreateOperation(db_connection)
        self.read = ReadOperation(db_connection)
        self.update = UpdateOperation(db_connection)
        self.delete = DeleteOperation(db_connection)
