"""统计分析模块。

提供数据统计分析和报表生成功能。
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging

from src.core.database.connection import DatabaseConnection, DatabaseError
from src.features.crud.read import ReadOperation

logger = logging.getLogger(__name__)


class AnalyticsError(Exception):
    """统计分析异常类。"""
    pass


class Analytics:
    """统计分析类。
    
    提供各种数据统计和报表功能。
    """
    
    def __init__(self, db_connection: DatabaseConnection) -> None:
        """初始化统计分析类。
        
        Args:
            db_connection: 数据库连接对象
        """
        self.db = db_connection
        self.read_op = ReadOperation(db_connection)
    
    def get_table_statistics(self, table_name: str) -> Dict[str, Any]:
        """获取表统计信息。
        
        Args:
            table_name: 表名
        
        Returns:
            统计信息字典，包含总记录数、有效记录数等
        """
        try:
            total_count = self.read_op.count(table_name)
            active_count = self.read_op.count(
                table_name,
                where_clause="IsDeleted = 0"
            )
            
            return {
                'table_name': table_name,
                'total_count': total_count,
                'active_count': active_count,
                'deleted_count': total_count - active_count
            }
        
        except Exception as e:
            logger.error(f"获取表统计信息失败: {table_name}", exc_info=True)
            raise AnalyticsError(f"获取表统计信息失败: {e}") from e
    
    def get_ppid_statistics(self) -> Dict[str, Any]:
        """获取 PPID 记录统计信息。
        
        Returns:
            PPID 统计信息字典
        """
        try:
            # 按状态统计
            status_query = """
                SELECT Status, COUNT(*) AS Count
                FROM PPIDRecord
                WHERE IsDeleted = 0
                GROUP BY Status
            """
            status_stats = {
                row['Status']: row['Count']
                for row in self.db.execute_query(status_query)
            }
            
            # 按型号统计
            model_query = """
                SELECT Model, COUNT(*) AS Count
                FROM PPIDRecord
                WHERE IsDeleted = 0 AND Model IS NOT NULL
                GROUP BY Model
            """
            model_stats = {
                row['Model']: row['Count']
                for row in self.db.execute_query(model_query)
            }
            
            # 使用天数统计
            usage_query = """
                SELECT 
                    AVG(InUseDays) AS AvgDays,
                    MAX(InUseDays) AS MaxDays,
                    MIN(InUseDays) AS MinDays
                FROM PPIDRecord
                WHERE IsDeleted = 0 AND InUseDays > 0
            """
            usage_stats = self.db.execute_query(usage_query)
            usage_info = usage_stats[0] if usage_stats else {}
            
            # 总记录数
            total_count = self.read_op.count('PPIDRecord')
            
            return {
                'total_count': total_count,
                'status_distribution': status_stats,
                'model_distribution': model_stats,
                'usage_statistics': {
                    'average_days': usage_info.get('AvgDays', 0),
                    'max_days': usage_info.get('MaxDays', 0),
                    'min_days': usage_info.get('MinDays', 0)
                }
            }
        
        except Exception as e:
            logger.error(f"获取 PPID 统计信息失败: {e}", exc_info=True)
            raise AnalyticsError(f"获取 PPID 统计信息失败: {e}") from e
    
    def get_import_statistics(self, days: int = 30) -> Dict[str, Any]:
        """获取导入操作统计信息。
        
        Args:
            days: 统计天数，默认 30 天
        
        Returns:
            导入统计信息字典
        """
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            # 总体统计
            total_query = """
                SELECT 
                    COUNT(*) AS TotalImports,
                    SUM(SuccessRows) AS TotalSuccess,
                    SUM(FailedRows) AS TotalFailed,
                    SUM(TotalRows) AS TotalRows
                FROM ImportLog
                WHERE CreateTime >= ? AND IsDeleted = 0
            """
            
            total_stats = self.db.execute_query(
                total_query,
                (start_date,)
            )
            
            # 按类型统计
            type_query = """
                SELECT 
                    ImportType,
                    COUNT(*) AS Count,
                    SUM(SuccessRows) AS SuccessRows,
                    SUM(FailedRows) AS FailedRows
                FROM ImportLog
                WHERE CreateTime >= ? AND IsDeleted = 0
                GROUP BY ImportType
            """
            
            type_stats = self.db.execute_query(type_query, (start_date,))
            
            # 按日期统计
            daily_query = """
                SELECT 
                    CAST(CreateTime AS DATE) AS ImportDate,
                    COUNT(*) AS Count,
                    SUM(SuccessRows) AS SuccessRows,
                    SUM(FailedRows) AS FailedRows
                FROM ImportLog
                WHERE CreateTime >= ? AND IsDeleted = 0
                GROUP BY CAST(CreateTime AS DATE)
                ORDER BY ImportDate DESC
            """
            
            daily_stats = self.db.execute_query(daily_query, (start_date,))
            
            return {
                'period_days': days,
                'start_date': start_date.isoformat(),
                'total_imports': total_stats[0]['TotalImports'] if total_stats else 0,
                'total_success_rows': total_stats[0]['TotalSuccess'] if total_stats else 0,
                'total_failed_rows': total_stats[0]['TotalFailed'] if total_stats else 0,
                'total_rows': total_stats[0]['TotalRows'] if total_stats else 0,
                'by_type': [
                    {
                        'type': row['ImportType'],
                        'count': row['Count'],
                        'success_rows': row['SuccessRows'],
                        'failed_rows': row['FailedRows']
                    }
                    for row in type_stats
                ],
                'by_date': [
                    {
                        'date': row['ImportDate'].isoformat() if isinstance(row['ImportDate'], datetime) else str(row['ImportDate']),
                        'count': row['Count'],
                        'success_rows': row['SuccessRows'],
                        'failed_rows': row['FailedRows']
                    }
                    for row in daily_stats
                ]
            }
        
        except Exception as e:
            logger.error(f"获取导入统计信息失败: {e}", exc_info=True)
            raise AnalyticsError(f"获取导入统计信息失败: {e}") from e
    
    def get_backup_statistics(self, days: int = 30) -> Dict[str, Any]:
        """获取备份操作统计信息。
        
        Args:
            days: 统计天数，默认 30 天
        
        Returns:
            备份统计信息字典
        """
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            # 总体统计
            total_query = """
                SELECT 
                    COUNT(*) AS TotalBackups,
                    SUM(FileSize) AS TotalSize,
                    AVG(FileSize) AS AvgSize,
                    MAX(FileSize) AS MaxSize,
                    MIN(FileSize) AS MinSize
                FROM BackupLog
                WHERE CreateTime >= ? AND IsDeleted = 0 AND Status = 'success'
            """
            
            total_stats = self.db.execute_query(total_query, (start_date,))
            
            # 按类型统计
            type_query = """
                SELECT 
                    BackupType,
                    COUNT(*) AS Count,
                    SUM(FileSize) AS TotalSize,
                    AVG(FileSize) AS AvgSize
                FROM BackupLog
                WHERE CreateTime >= ? AND IsDeleted = 0 AND Status = 'success'
                GROUP BY BackupType
            """
            
            type_stats = self.db.execute_query(type_query, (start_date,))
            
            # 最近备份
            recent_query = """
                SELECT TOP 10
                    BackupFileName,
                    BackupPath,
                    BackupType,
                    FileSize,
                    CreateTime,
                    Status
                FROM BackupLog
                WHERE IsDeleted = 0
                ORDER BY CreateTime DESC
            """
            
            recent_backups = self.db.execute_query(recent_query)
            
            return {
                'period_days': days,
                'start_date': start_date.isoformat(),
                'total_backups': total_stats[0]['TotalBackups'] if total_stats else 0,
                'total_size': total_stats[0]['TotalSize'] if total_stats else 0,
                'average_size': total_stats[0]['AvgSize'] if total_stats else 0,
                'max_size': total_stats[0]['MaxSize'] if total_stats else 0,
                'min_size': total_stats[0]['MinSize'] if total_stats else 0,
                'by_type': [
                    {
                        'type': row['BackupType'],
                        'count': row['Count'],
                        'total_size': row['TotalSize'],
                        'average_size': row['AvgSize']
                    }
                    for row in type_stats
                ],
                'recent_backups': [
                    {
                        'file_name': row['BackupFileName'],
                        'backup_path': row['BackupPath'],
                        'backup_type': row['BackupType'],
                        'file_size': row['FileSize'],
                        'create_time': row['CreateTime'].isoformat() if isinstance(row['CreateTime'], datetime) else str(row['CreateTime']),
                        'status': row['Status']
                    }
                    for row in recent_backups
                ]
            }
        
        except Exception as e:
            logger.error(f"获取备份统计信息失败: {e}", exc_info=True)
            raise AnalyticsError(f"获取备份统计信息失败: {e}") from e
    
    def get_user_activity_statistics(self, days: int = 30) -> Dict[str, Any]:
        """获取用户活动统计信息。
        
        Args:
            days: 统计天数，默认 30 天
        
        Returns:
            用户活动统计信息字典
        """
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            # 按用户统计操作次数
            user_query = """
                SELECT 
                    UserName,
                    COUNT(*) AS ActionCount,
                    COUNT(DISTINCT Action) AS ActionTypes
                FROM AuditLog
                WHERE ActionTime >= ? AND IsDeleted = 0
                GROUP BY UserName
                ORDER BY ActionCount DESC
            """
            
            user_stats = self.db.execute_query(user_query, (start_date,))
            
            # 按操作类型统计
            action_query = """
                SELECT 
                    Action,
                    COUNT(*) AS Count
                FROM AuditLog
                WHERE ActionTime >= ? AND IsDeleted = 0
                GROUP BY Action
                ORDER BY Count DESC
            """
            
            action_stats = self.db.execute_query(action_query, (start_date,))
            
            return {
                'period_days': days,
                'start_date': start_date.isoformat(),
                'by_user': [
                    {
                        'username': row['UserName'],
                        'action_count': row['ActionCount'],
                        'action_types': row['ActionTypes']
                    }
                    for row in user_stats
                ],
                'by_action': [
                    {
                        'action': row['Action'],
                        'count': row['Count']
                    }
                    for row in action_stats
                ]
            }
        
        except Exception as e:
            logger.error(f"获取用户活动统计信息失败: {e}", exc_info=True)
            raise AnalyticsError(f"获取用户活动统计信息失败: {e}") from e
    
    def generate_summary_report(self) -> Dict[str, Any]:
        """生成综合报表。
        
        Returns:
            综合报表字典
        """
        try:
            report = {
                'generated_at': datetime.now().isoformat(),
                'database_statistics': {},
                'ppid_statistics': self.get_ppid_statistics(),
                'import_statistics': self.get_import_statistics(30),
                'backup_statistics': self.get_backup_statistics(30),
                'user_activity': self.get_user_activity_statistics(30)
            }
            
            # 获取所有表的统计信息
            tables = ['UserTable', 'PPIDRecord', 'ImportLog', 'BackupLog', 'AuditLog']
            for table in tables:
                try:
                    report['database_statistics'][table] = self.get_table_statistics(table)
                except Exception as e:
                    logger.warning(f"获取表统计信息失败: {table} - {e}")
            
            return report
        
        except Exception as e:
            logger.error(f"生成综合报表失败: {e}", exc_info=True)
            raise AnalyticsError(f"生成综合报表失败: {e}") from e

