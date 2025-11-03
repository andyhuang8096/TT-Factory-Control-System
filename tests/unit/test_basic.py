"""单元测试示例。

提供基本的单元测试示例。
"""

import unittest
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.config.config_manager import ConfigManager
from src.core.database.connection import DatabaseConnection, DatabaseError


class TestConfigManager(unittest.TestCase):
    """配置管理器测试。"""
    
    def setUp(self):
        """设置测试环境。"""
        self.config = ConfigManager()
    
    def test_config_creation(self):
        """测试配置管理器创建。"""
        self.assertIsNotNone(self.config)
    
    def test_get_nonexistent_config(self):
        """测试获取不存在的配置。"""
        value = self.config.get('NonExistent', 'Key', 'default')
        self.assertEqual(value, 'default')


class TestPasswordHasher(unittest.TestCase):
    """密码加密测试。"""
    
    def setUp(self):
        """设置测试环境。"""
        from src.core.security.auth import PasswordHasher
        self.hasher = PasswordHasher
    
    def test_hash_password(self):
        """测试密码加密。"""
        password = "test123"
        hashed, salt = self.hasher.hash_password(password)
        
        self.assertIsNotNone(hashed)
        self.assertIsNotNone(salt)
        self.assertNotEqual(password, hashed)
    
    def test_verify_password(self):
        """测试密码验证。"""
        password = "test123"
        hashed, _ = self.hasher.hash_password(password)
        
        # 正确密码
        self.assertTrue(self.hasher.verify_password(password, hashed))
        
        # 错误密码
        self.assertFalse(self.hasher.verify_password("wrong", hashed))


class TestCRUDOperations(unittest.TestCase):
    """CRUD 操作测试。"""
    
    def setUp(self):
        """设置测试环境。"""
        # 创建模拟数据库连接
        self.mock_db = Mock(spec=DatabaseConnection)
        self.mock_db.execute_query = Mock(return_value=[])
        self.mock_db.execute_non_query = Mock(return_value=1)
        self.mock_db.execute_scalar = Mock(return_value=1)
        
        from src.features.crud import CRUDOperations
        self.crud = CRUDOperations(self.mock_db)
    
    def test_create_operation(self):
        """测试创建操作。"""
        from src.features.crud.create import CreateOperation
        create_op = CreateOperation(self.mock_db)
        
        data = {'Name': 'Test', 'Value': 123}
        result = create_op.create('TestTable', data)
        
        self.assertEqual(result, 1)
        self.mock_db.execute_scalar.assert_called_once()
    
    def test_read_operation(self):
        """测试读取操作。"""
        self.mock_db.execute_query.return_value = [
            {'Id': 1, 'Name': 'Test'}
        ]
        
        result = self.crud.read.get_by_id('TestTable', 1)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['Id'], 1)


if __name__ == '__main__':
    unittest.main()

