"""身份认证模块。

提供用户登录、注销、密码加密等功能。
"""

from typing import Optional
from datetime import datetime
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64
import secrets
import logging

from src.core.database.connection import DatabaseConnection, DatabaseError
from src.features.crud.read import ReadOperation
from src.features.crud.update import UpdateOperation

logger = logging.getLogger(__name__)


class AuthenticationError(Exception):
    """认证异常类。"""
    pass


class PasswordHasher:
    """密码加密工具类。
    
    使用 PBKDF2 算法加密密码。
    """
    
    @staticmethod
    def hash_password(password: str, salt: Optional[bytes] = None) -> tuple[str, bytes]:
        """加密密码。
        
        Args:
            password: 明文密码
            salt: 盐值，如果为 None 则自动生成
        
        Returns:
            (加密后的密码, 盐值) 元组
        """
        if salt is None:
            salt = secrets.token_bytes(16)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        
        key = kdf.derive(password.encode('utf-8'))
        
        # 将 salt 和 key 组合存储
        hashed_password = base64.b64encode(salt + key).decode('utf-8')
        
        return hashed_password, salt
    
    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """验证密码。
        
        Args:
            password: 明文密码
            hashed_password: 加密后的密码
        
        Returns:
            验证成功返回 True，失败返回 False
        """
        try:
            # 解码存储的密码
            decoded = base64.b64decode(hashed_password.encode('utf-8'))
            salt = decoded[:16]
            stored_key = decoded[16:]
            
            # 使用相同的 salt 加密输入的密码
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
                backend=default_backend()
            )
            
            input_key = kdf.derive(password.encode('utf-8'))
            
            # 比较密钥
            return secrets.compare_digest(stored_key, input_key)
        
        except Exception as e:
            logger.error(f"密码验证失败: {e}", exc_info=True)
            return False


class Authentication:
    """身份认证类。
    
    负责用户登录、注销、密码管理等功能。
    """
    
    def __init__(self, db_connection: DatabaseConnection) -> None:
        """初始化认证类。
        
        Args:
            db_connection: 数据库连接对象
        """
        self.db = db_connection
        self.read = ReadOperation(db_connection)
        self.update = UpdateOperation(db_connection)
        self.current_user: Optional[dict] = None
    
    def login(self, username: str, password: str) -> bool:
        """用户登录。
        
        Args:
            username: 用户名
            password: 密码
        
        Returns:
            登录成功返回 True，失败返回 False
        
        Raises:
            AuthenticationError: 认证失败时抛出
        """
        try:
            # 查询用户
            users = self.read.get_all(
                'UserTable',
                where_clause='UserName = ? AND IsActive = 1',
                parameters=(username,)
            )
            
            if not users:
                logger.warning(f"登录失败: 用户不存在 - {username}")
                raise AuthenticationError("用户名或密码错误")
            
            user = users[0]
            
            # 验证密码
            if not PasswordHasher.verify_password(password, user['Password']):
                logger.warning(f"登录失败: 密码错误 - {username}")
                raise AuthenticationError("用户名或密码错误")
            
            # 更新最后登录时间
            self.update.update(
                'UserTable',
                user['Id'],
                {'LastLoginTime': datetime.now()},
                username
            )
            
            # 保存当前用户信息（不包含密码）
            self.current_user = {k: v for k, v in user.items() if k != 'Password'}
            
            logger.info(f"用户登录成功: {username}")
            return True
        
        except AuthenticationError:
            raise
        except Exception as e:
            logger.error(f"登录过程出错: {e}", exc_info=True)
            raise AuthenticationError(f"登录失败: {e}") from e
    
    def logout(self) -> None:
        """用户注销。"""
        if self.current_user:
            username = self.current_user.get('UserName', 'Unknown')
            logger.info(f"用户注销: {username}")
            self.current_user = None
    
    def is_authenticated(self) -> bool:
        """检查是否已认证。
        
        Returns:
            已认证返回 True，否则返回 False
        """
        return self.current_user is not None
    
    def get_current_user(self) -> Optional[dict]:
        """获取当前登录用户信息。
        
        Returns:
            当前用户信息字典，如果未登录则返回 None
        """
        return self.current_user
    
    def change_password(self, old_password: str, new_password: str) -> bool:
        """修改密码。
        
        Args:
            old_password: 旧密码
            new_password: 新密码
        
        Returns:
            修改成功返回 True，失败返回 False
        
        Raises:
            AuthenticationError: 认证失败时抛出
        """
        if not self.is_authenticated():
            raise AuthenticationError("用户未登录")
        
        try:
            username = self.current_user['UserName']
            
            # 验证旧密码
            users = self.read.get_all(
                'UserTable',
                where_clause='UserName = ?',
                parameters=(username,)
            )
            
            if not users:
                raise AuthenticationError("用户不存在")
            
            user = users[0]
            
            if not PasswordHasher.verify_password(old_password, user['Password']):
                raise AuthenticationError("旧密码错误")
            
            # 加密新密码
            hashed_password, _ = PasswordHasher.hash_password(new_password)
            
            # 更新密码
            self.update.update(
                'UserTable',
                user['Id'],
                {'Password': hashed_password},
                username
            )
            
            logger.info(f"密码修改成功: {username}")
            return True
        
        except AuthenticationError:
            raise
        except Exception as e:
            logger.error(f"修改密码失败: {e}", exc_info=True)
            raise AuthenticationError(f"修改密码失败: {e}") from e
    
    def create_user(self, username: str, password: str, email: Optional[str] = None,
                   full_name: Optional[str] = None, role: str = "user") -> int:
        """创建新用户。
        
        Args:
            username: 用户名
            password: 密码
            email: 邮箱
            full_name: 全名
            role: 角色（admin, user, viewer）
        
        Returns:
            新创建用户的 ID
        
        Raises:
            AuthenticationError: 创建失败时抛出
        """
        try:
            # 检查用户是否已存在
            existing = self.read.get_all(
                'UserTable',
                where_clause='UserName = ?',
                parameters=(username,)
            )
            
            if existing:
                raise AuthenticationError(f"用户名已存在: {username}")
            
            # 加密密码
            hashed_password, _ = PasswordHasher.hash_password(password)
            
            # 创建用户
            from src.features.crud.create import CreateOperation
            create_op = CreateOperation(self.db)
            
            user_data = {
                'UserName': username,
                'Password': hashed_password,
                'Email': email,
                'FullName': full_name,
                'Role': role,
                'IsActive': True
            }
            
            current_user = self.get_current_user()
            creator = current_user['UserName'] if current_user else 'system'
            
            user_id = create_op.create('UserTable', user_data, creator)
            
            logger.info(f"用户创建成功: {username} (ID: {user_id})")
            return user_id
        
        except AuthenticationError:
            raise
        except Exception as e:
            logger.error(f"创建用户失败: {e}", exc_info=True)
            raise AuthenticationError(f"创建用户失败: {e}") from e

