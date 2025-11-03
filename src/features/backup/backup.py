"""数据库备份模块。

提供 SQL Server 数据库备份功能。
"""

import os
from typing import Optional, Dict, Any, List
from datetime import datetime
from pathlib import Path
import logging

from src.core.database.connection import DatabaseConnection, DatabaseError
from src.features.crud.create import CreateOperation
from src.features.crud.read import ReadOperation

logger = logging.getLogger(__name__)


class BackupError(Exception):
    """备份异常类。"""
    pass


class DatabaseBackup:
    """数据库备份类。
    
    负责执行 SQL Server 数据库备份操作。
    """
    
    def __init__(self, db_connection: DatabaseConnection) -> None:
        """初始化备份类。
        
        Args:
            db_connection: 数据库连接对象
        """
        self.db = db_connection
        self.create_op = CreateOperation(db_connection)
        self.read_op = ReadOperation(db_connection)
    
    def backup(self, backup_path: Optional[str] = None,
               backup_type: str = "full",
               user: Optional[str] = None) -> Dict[str, Any]:
        """执行数据库备份。
        
        Args:
            backup_path: 备份文件路径，如果为 None 则自动生成
            backup_type: 备份类型（full, differential）
            user: 操作用户名
        
        Returns:
            备份结果字典，包含备份文件路径、大小等信息
        
        Raises:
            BackupError: 备份失败时抛出
        """
        try:
            # 获取数据库名称
            db_name = self.db.database
            
            # 生成备份文件路径
            if not backup_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_dir = Path("backups")
                backup_dir.mkdir(exist_ok=True)
                backup_path = str(backup_dir / f"{db_name}_{backup_type}_{timestamp}.bak")
            
            backup_path_obj = Path(backup_path)
            backup_path_obj.parent.mkdir(parents=True, exist_ok=True)
            
            # 确保备份文件路径是绝对路径
            backup_path = str(backup_path_obj.absolute())
            
            start_time = datetime.now()
            
            # 记录备份日志
            backup_log = {
                'BackupFileName': backup_path_obj.name,
                'BackupPath': backup_path,
                'BackupType': backup_type,
                'DatabaseName': db_name,
                'FileSize': 0,
                'Status': 'pending',
                'StartTime': start_time
            }
            
            log_id = self.create_op.create('BackupLog', backup_log, user)
            
            try:
                # 构建备份 SQL
                # SQL Server 备份命令需要完整的文件路径
                backup_sql = f"""
                    BACKUP DATABASE [{db_name}]
                    TO DISK = '{backup_path}'
                    WITH FORMAT, INIT,
                    NAME = '{db_name}_{backup_type}_backup',
                    DESCRIPTION = '{backup_type.capitalize()} backup of {db_name}'
                """
                
                if backup_type.lower() == "differential":
                    backup_sql += ", DIFFERENTIAL"
                
                # 执行备份
                self.db.execute_non_query(backup_sql)
                
                # 检查备份文件是否存在
                if not backup_path_obj.exists():
                    raise BackupError("备份文件未生成")
                
                # 获取文件大小
                file_size = backup_path_obj.stat().st_size
                end_time = datetime.now()
                
                # 更新备份日志
                from src.features.crud.update import UpdateOperation
                update_op = UpdateOperation(self.db)
                update_op.update('BackupLog', log_id, {
                    'FileSize': file_size,
                    'Status': 'success',
                    'EndTime': end_time
                }, user)
                
                result = {
                    'backup_path': backup_path,
                    'file_size': file_size,
                    'backup_type': backup_type,
                    'database_name': db_name,
                    'start_time': start_time,
                    'end_time': end_time,
                    'duration': (end_time - start_time).total_seconds(),
                    'log_id': log_id
                }
                
                logger.info(
                    f"数据库备份成功: {db_name} -> {backup_path} "
                    f"({file_size / 1024 / 1024:.2f} MB)"
                )
                
                return result
            
            except Exception as e:
                # 更新备份日志为失败状态
                end_time = datetime.now()
                from src.features.crud.update import UpdateOperation
                update_op = UpdateOperation(self.db)
                update_op.update('BackupLog', log_id, {
                    'Status': 'failed',
                    'ErrorMessage': str(e),
                    'EndTime': end_time
                }, user)
                
                raise BackupError(f"备份执行失败: {e}") from e
        
        except BackupError:
            raise
        except Exception as e:
            logger.error(f"数据库备份失败: {e}", exc_info=True)
            raise BackupError(f"数据库备份失败: {e}") from e
    
    def get_backup_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取备份历史记录。
        
        Args:
            limit: 返回记录数限制
        
        Returns:
            备份日志列表
        """
        try:
            backups = self.read_op.get_all(
                'BackupLog',
                order_by='CreateTime DESC',
                limit=limit
            )
            return backups
        except Exception as e:
            logger.error(f"获取备份历史失败: {e}", exc_info=True)
            return []
    
    def get_backup_info(self, backup_path: str) -> Optional[Dict[str, Any]]:
        """获取备份文件信息。
        
        Args:
            backup_path: 备份文件路径
        
        Returns:
            备份信息字典，如果文件不存在则返回 None
        """
        try:
            backup_path_obj = Path(backup_path)
            if not backup_path_obj.exists():
                return None
            
            # 查询数据库中的备份信息
            backups = self.read_op.get_all(
                'BackupLog',
                where_clause='BackupPath = ?',
                parameters=(str(backup_path_obj.absolute()),)
            )
            
            if backups:
                backup_info = backups[0]
                backup_info['file_exists'] = True
                backup_info['actual_file_size'] = backup_path_obj.stat().st_size
                return backup_info
            
            # 如果数据库中无记录，返回文件基本信息
            return {
                'file_exists': True,
                'file_size': backup_path_obj.stat().st_size,
                'file_path': str(backup_path_obj.absolute()),
                'modified_time': datetime.fromtimestamp(
                    backup_path_obj.stat().st_mtime
                )
            }
        
        except Exception as e:
            logger.error(f"获取备份信息失败: {e}", exc_info=True)
            return None

