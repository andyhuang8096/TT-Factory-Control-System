"""MVP 版本快速测试指南。

用于快速验证 MVP 版本是否正常工作。
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.config.config_manager import ConfigManager
from src.core.database import DatabaseConnectionFactory, CREATE_TABLES
from src.core.database.connection import DatabaseConnection
from src.core.security import Authentication
from src.features.crud import CRUDOperations
from src.utils.logger import setup_logging
import logging

logger = logging.getLogger(__name__)


def run_mvp_tests() -> bool:
    """运行 MVP 版本的基本测试。
    
    Returns:
        所有测试通过返回 True，否则返回 False
    """
    setup_logging()
    
    print("=" * 60)
    print("MVP 版本快速测试")
    print("=" * 60)
    print()
    
    tests_passed = 0
    tests_failed = 0
    
    # 测试 1: 配置文件加载
    print("测试 1: 配置文件加载")
    try:
        config = ConfigManager()
        if config.load_config():
            print("  ✓ 配置文件加载成功")
            tests_passed += 1
        else:
            print("  ✗ 配置文件加载失败")
            tests_failed += 1
    except Exception as e:
        print(f"  ✗ 配置文件加载出错: {e}")
        tests_failed += 1
    
    print()
    
    # 测试 2: 数据库连接
    print("测试 2: 数据库连接")
    try:
        config = ConfigManager()
        config.load_config()
        db_connection = DatabaseConnectionFactory.create_from_config(config)
        
        if db_connection.connect():
            print("  ✓ 数据库连接成功")
            tests_passed += 1
            
            # 测试 3: 数据库查询
            print("测试 3: 数据库查询")
            try:
                result = db_connection.execute_scalar("SELECT 1")
                if result == 1:
                    print("  ✓ 数据库查询成功")
                    tests_passed += 1
                else:
                    print("  ✗ 数据库查询失败")
                    tests_failed += 1
            except Exception as e:
                print(f"  ✗ 数据库查询出错: {e}")
                tests_failed += 1
            
            # 测试 4: CRUD 操作
            print("测试 4: CRUD 操作")
            try:
                crud = CRUDOperations(db_connection)
                count = crud.read.count('UserTable')
                print(f"  ✓ CRUD 操作成功 (UserTable 记录数: {count})")
                tests_passed += 1
            except Exception as e:
                print(f"  ✗ CRUD 操作出错: {e}")
                tests_failed += 1
            
            # 测试 5: 认证功能
            print("测试 5: 认证功能")
            try:
                auth = Authentication(db_connection)
                # 检查是否有用户
                users = crud.read.get_all('UserTable', limit=1)
                if users:
                    print("  ✓ 认证模块初始化成功")
                    tests_passed += 1
                else:
                    print("  ⚠ 认证模块初始化成功，但无用户数据")
                    print("    请运行: python scripts/create_admin.py")
                    tests_passed += 1
            except Exception as e:
                print(f"  ✗ 认证功能出错: {e}")
                tests_failed += 1
            
            db_connection.disconnect()
        else:
            print("  ✗ 数据库连接失败")
            tests_failed += 1
    except Exception as e:
        print(f"  ✗ 数据库连接出错: {e}")
        tests_failed += 1
    
    print()
    print("=" * 60)
    print(f"测试结果: {tests_passed} 通过, {tests_failed} 失败")
    print("=" * 60)
    
    if tests_failed == 0:
        print("\n✓ 所有测试通过！可以运行应用程序")
        print("  运行命令: python src/main.py")
        return True
    else:
        print("\n✗ 部分测试失败，请检查配置和数据库")
        return False


if __name__ == "__main__":
    success = run_mvp_tests()
    sys.exit(0 if success else 1)

