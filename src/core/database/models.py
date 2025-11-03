"""数据模型定义。

定义数据库表结构和数据模型类。
"""

from typing import Optional, Dict, Any
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class BaseModel:
    """基础数据模型类。
    
    所有数据模型的基础类，包含通用字段。
    """
    Id: Optional[int] = None
    CreateTime: Optional[datetime] = None
    UpdateTime: Optional[datetime] = None
    CreateUser: Optional[str] = None
    UpdateUser: Optional[str] = None
    IsDeleted: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典。
        
        Returns:
            数据字典
        """
        result = asdict(self)
        # 转换 datetime 为字符串
        for key, value in result.items():
            if isinstance(value, datetime):
                result[key] = value.isoformat()
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseModel':
        """从字典创建对象。
        
        Args:
            data: 数据字典
        
        Returns:
            模型对象
        """
        return cls(**data)


@dataclass
class UserTable(BaseModel):
    """用户表模型。
    
    存储系统用户信息。
    """
    UserName: str = ""
    Password: str = ""  # 加密后的密码
    Email: Optional[str] = None
    FullName: Optional[str] = None
    Role: str = "user"  # 角色：admin, user, viewer
    IsActive: bool = True
    LastLoginTime: Optional[datetime] = None


@dataclass
class PPIDRecord(BaseModel):
    """PPID 记录表模型。
    
    存储 PPID（产品标识符）相关信息。
    """
    PPID: str = ""  # 产品标识符
    SerialNumber: Optional[str] = None
    Model: Optional[str] = None  # 型号（如：DELL, WYSE）
    PN: Optional[str] = None  # 零件号
    Status: str = "available"  # 状态：available, in_use, corrupted
    InUseDays: int = 0  # 使用天数
    CorruptedAttempts: int = 0  # 损坏尝试次数
    LastUsedTime: Optional[datetime] = None
    Notes: Optional[str] = None


@dataclass
class ImportLog(BaseModel):
    """导入日志表模型。
    
    记录数据导入操作的历史。
    """
    FileName: str = ""
    FilePath: str = ""
    ImportType: str = "csv"  # csv, excel, json
    TotalRows: int = 0
    SuccessRows: int = 0
    FailedRows: int = 0
    Status: str = "pending"  # pending, success, failed
    ErrorMessage: Optional[str] = None
    StartTime: Optional[datetime] = None
    EndTime: Optional[datetime] = None


@dataclass
class BackupLog(BaseModel):
    """备份日志表模型。
    
    记录数据库备份操作的历史。
    """
    BackupFileName: str = ""
    BackupPath: str = ""
    BackupType: str = "full"  # full, differential
    DatabaseName: str = ""
    FileSize: int = 0  # 字节
    Status: str = "pending"  # pending, success, failed
    ErrorMessage: Optional[str] = None
    StartTime: Optional[datetime] = None
    EndTime: Optional[datetime] = None


@dataclass
class AuditLog(BaseModel):
    """审计日志表模型。
    
    记录系统操作审计信息。
    """
    UserName: str = ""
    Action: str = ""  # create, update, delete, query, export, import, backup, restore
    TableName: Optional[str] = None
    RecordId: Optional[int] = None
    Description: Optional[str] = None
    IPAddress: Optional[str] = None
    ActionTime: Optional[datetime] = None


# 表名映射
TABLE_NAMES = {
    'user': 'UserTable',
    'ppid': 'PPIDRecord',
    'import_log': 'ImportLog',
    'backup_log': 'BackupLog',
    'audit_log': 'AuditLog'
}
