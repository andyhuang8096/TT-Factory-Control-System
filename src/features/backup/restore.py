"""数据库恢复模块。

提供 SQL Server 数据库恢复功能。
"""

from typing import Optional, List
from datetime import datetime
from pathlib import Path
import logging

from src.core.database.connection import DatabaseConnection, DatabaseError
from src.features.crud.read import ReadOperation

logger = logging.getLogger(__name__)


class RestoreError(Exception):
    """恢复异常类。"""
    pass


class DatabaseRestore:
    """数据库恢复类。
    
    负责执行 SQL Server 数据库恢复操作。
    """
    
    def __init__(self, db_connection: DatabaseConnection) -> None:
        """初始化恢复类。
        
        Args:
            db_connection: 数据库连接对象
        """
        self.db = db_connection
        self.read_op = ReadOperation(db_connection)
    
    def restore(self, backup_path: str, 
               database_name: Optional[str] = None,
               replace: bool = False) -> bool:
        """恢复数据库。
        
        警告：恢复操作会覆盖现有数据库，请谨慎使用。
        
        Args:
            backup_path: 备份文件路径
            database_name: 目标数据库名称，如果为 None 则使用当前数据库
            replace: 是否替换现有数据库
        
        Returns:
            恢复成功返回 True，失败返回 False
        
        Raises:
            RestoreError: 恢复失败时抛出
        """
        try:
            backup_path_obj = Path(backup_path)
            
            if not backup_path_obj.exists():
                raise RestoreError(f"备份文件不存在: {backup_path}")
            
            # 确保使用绝对路径
            backup_path = str(backup_path_obj.absolute())
            
            # 确定目标数据库名称
            target_db = database_name or self.db.database
            
            logger.warning(
                f"准备恢复数据库: {target_db} <- {backup_path} "
                f"(替换: {replace})"
            )
            
            # 构建恢复 SQL
            restore_sql = f"""
                USE master;
                ALTER DATABASE [{target_db}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
                RESTORE DATABASE [{target_db}]
                FROM DISK = '{backup_path}'
                WITH REPLACE, RECOVERY;
                ALTER DATABASE [{target_db}] SET MULTI_USER;
            """
            
            if not replace:
                restore_sql = restore_sql.replace("WITH REPLACE, RECOVERY", "WITH RECOVERY")
            
            # 执行恢复
            # 注意：恢复操作需要连接到 master 数据库
            try:
                # 切换到 master 数据库执行恢复
                original_db = self.db.database
                self.db.disconnect()
                
                # 重新连接到 master 数据库
                master_conn = DatabaseConnection(
                    server=self.db.server,
                    database='master',
                    login=self.db.login,
                    password=self.db.password,
                    port=self.db.port
                )
                master_conn.connect()
                
                # 执行恢复命令
                master_conn.execute_non_query(restore_sql)
                
                master_conn.disconnect()
                
                # 重新连接到原数据库
                self.db.connect()
                
                logger.info(f"数据库恢复成功: {target_db} <- {backup_path}")
                return True
            
            except Exception as e:
                # 尝试重新连接原数据库
                try:
                    self.db.connect()
                except:
                    pass
                
                raise RestoreError(f"恢复执行失败: {e}") from e
        
        except RestoreError:
            raise
        except Exception as e:
            logger.error(f"数据库恢复失败: {e}", exc_info=True)
            raise RestoreError(f"数据库恢复失败: {e}") from e
    
    def verify_backup(self, backup_path: str) -> Dict[str, Any]:
        """验证备份文件。
        
        Args:
            backup_path: 备份文件路径
        
        Returns:
            验证结果字典
        """
        try:
            backup_path_obj = Path(backup_path)
            
            if not backup_path_obj.exists():
                return {
                    'valid': False,
                    'error': '备份文件不存在'
                }
            
            # 尝试读取备份文件头信息
            try:
                verify_sql = f"""
                    RESTORE VERIFYONLY
                    FROM DISK = '{backup_path_obj.absolute()}'
                    WITH FILE = 1
                """
                
                # 连接到 master 数据库执行验证
                master_conn = DatabaseConnection(
                    server=self.db.server,
                    database='master',
                    login=self.db.login,
                    password=self.db.password,
                    port=self.db.port
                )
                
                with master_conn:
                    master_conn.execute_non_query(verify_sql)
                
                return {
                    'valid': True,
                    'file_size': backup_path_obj.stat().st_size,
                    'file_path': str(backup_path_obj.absolute())
                }
            
            except Exception as e:
                return {
                    'valid': False,
                    'error': str(e),
                    'file_size': backup_path_obj.stat().st_size if backup_path_obj.exists() else 0
                }
        
        except Exception as e:
            logger.error(f"验证备份文件失败: {e}", exc_info=True)
            return {
                'valid': False,
                'error': str(e)
            }
    
    def get_backup_files(self, backup_dir: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取备份目录中的所有备份文件。
        
        Args:
            backup_dir: 备份目录路径，如果为 None 则使用默认目录
        
        Returns:
            备份文件信息列表
        """
        try:
            if backup_dir is None:
                backup_dir = "backups"
            
            backup_path_obj = Path(backup_dir)
            
            if not backup_path_obj.exists():
                return []
            
            backup_files = []
            for file_path in backup_path_obj.glob("*.bak"):
                try:
                    stat = file_path.stat()
                    backup_files.append({
                        'file_name': file_path.name,
                        'file_path': str(file_path.absolute()),
                        'file_size': stat.st_size,
                        'modified_time': datetime.fromtimestamp(stat.st_mtime)
                    })
                except Exception as e:
                    logger.warning(f"读取备份文件信息失败: {file_path} - {e}")
            
            # 按修改时间排序（最新的在前）
            backup_files.sort(key=lambda x: x['modified_time'], reverse=True)
            
            return backup_files
        
        except Exception as e:
            logger.error(f"获取备份文件列表失败: {e}", exc_info=True)
            return []

