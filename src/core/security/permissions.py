"""权限管理模块。

提供基于角色的访问控制（RBAC）功能。
"""

from typing import Optional, List, Set
import logging

from src.core.security.auth import Authentication

logger = logging.getLogger(__name__)


class PermissionError(Exception):
    """权限异常类。"""
    pass


class Permissions:
    """权限管理类。
    
    实现基于角色的访问控制（RBAC）。
    """
    
    # 定义角色和权限映射
    ROLE_PERMISSIONS = {
        'admin': {
            'create', 'read', 'update', 'delete',
            'import', 'export', 'backup', 'restore',
            'manage_users', 'view_audit_log'
        },
        'user': {
            'create', 'read', 'update', 'delete',
            'import', 'export'
        },
        'viewer': {
            'read', 'export'
        }
    }
    
    # 定义表权限映射
    TABLE_PERMISSIONS = {
        'UserTable': {'read', 'create', 'update', 'delete', 'manage_users'},
        'PPIDRecord': {'read', 'create', 'update', 'delete'},
        'ImportLog': {'read'},
        'BackupLog': {'read'},
        'AuditLog': {'read', 'view_audit_log'}
    }
    
    def __init__(self, auth: Authentication) -> None:
        """初始化权限管理类。
        
        Args:
            auth: 认证对象
        """
        self.auth = auth
    
    def has_permission(self, permission: str) -> bool:
        """检查用户是否有指定权限。
        
        Args:
            permission: 权限名称
        
        Returns:
            有权限返回 True，否则返回 False
        """
        if not self.auth.is_authenticated():
            return False
        
        user = self.auth.get_current_user()
        if not user:
            return False
        
        role = user.get('Role', 'viewer')
        permissions = self.ROLE_PERMISSIONS.get(role, set())
        
        return permission in permissions
    
    def check_permission(self, permission: str) -> None:
        """检查权限，如果没有权限则抛出异常。
        
        Args:
            permission: 权限名称
        
        Raises:
            PermissionError: 没有权限时抛出
        """
        if not self.has_permission(permission):
            user = self.auth.get_current_user()
            username = user.get('UserName', 'Unknown') if user else 'Unknown'
            role = user.get('Role', 'Unknown') if user else 'Unknown'
            
            logger.warning(f"权限拒绝: {username} ({role}) 尝试访问 {permission}")
            raise PermissionError(f"权限不足: 需要 {permission} 权限")
    
    def has_table_permission(self, table_name: str, action: str) -> bool:
        """检查用户是否有指定表的操作权限。
        
        Args:
            table_name: 表名
            action: 操作类型（read, create, update, delete）
        
        Returns:
            有权限返回 True，否则返回 False
        """
        if not self.auth.is_authenticated():
            return False
        
        # 检查通用权限
        if self.has_permission(action):
            return True
        
        # 检查表特定权限
        table_perms = self.TABLE_PERMISSIONS.get(table_name, set())
        required_perm = f"{action}_{table_name.lower()}"
        
        return required_perm in table_perms or action in table_perms
    
    def check_table_permission(self, table_name: str, action: str) -> None:
        """检查表权限，如果没有权限则抛出异常。
        
        Args:
            table_name: 表名
            action: 操作类型
        
        Raises:
            PermissionError: 没有权限时抛出
        """
        if not self.has_table_permission(table_name, action):
            user = self.auth.get_current_user()
            username = user.get('UserName', 'Unknown') if user else 'Unknown'
            
            logger.warning(
                f"权限拒绝: {username} 尝试在 {table_name} 上执行 {action}"
            )
            raise PermissionError(
                f"权限不足: 无法在 {table_name} 上执行 {action} 操作"
            )
    
    def is_admin(self) -> bool:
        """检查当前用户是否是管理员。
        
        Returns:
            是管理员返回 True，否则返回 False
        """
        if not self.auth.is_authenticated():
            return False
        
        user = self.auth.get_current_user()
        return user.get('Role', '') == 'admin' if user else False
    
    def get_user_role(self) -> Optional[str]:
        """获取当前用户角色。
        
        Returns:
            用户角色，如果未登录则返回 None
        """
        if not self.auth.is_authenticated():
            return None
        
        user = self.auth.get_current_user()
        return user.get('Role') if user else None
    
    def get_permissions(self) -> Set[str]:
        """获取当前用户的所有权限。
        
        Returns:
            权限集合
        """
        if not self.auth.is_authenticated():
            return set()
        
        user = self.auth.get_current_user()
        if not user:
            return set()
        
        role = user.get('Role', 'viewer')
        return self.ROLE_PERMISSIONS.get(role, set()).copy()

