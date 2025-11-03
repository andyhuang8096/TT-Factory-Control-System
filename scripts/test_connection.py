"""数据库连接测试脚本。

用于测试数据库连接是否正常。
"""

import sys
import os
from pathlib import Path

# Set Windows console output to UTF-8
if sys.platform == 'win32':
    try:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    except:
        pass

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.config.config_manager import ConfigManager
from src.core.database import DatabaseConnectionFactory
from src.utils.logger import setup_logging
import logging

logger = logging.getLogger(__name__)


def test_database_connection() -> bool:
    """测试数据库连接。
    
    Returns:
        连接成功返回 True，失败返回 False
    """
    try:
        # 设置日志
        setup_logging()
        
        print("正在加载配置文件...")
        config = ConfigManager()
        if not config.load_config():
            print("✗ 配置文件加载失败")
            print(f"  请检查配置文件: {config.config_path}")
            return False
        
        print("✓ 配置文件加载成功")
        
        print("正在连接数据库...")
        db_connection = DatabaseConnectionFactory.create_from_config(config)
        
        if not db_connection.connect():
            print("✗ 数据库连接失败")
            return False
        
        print("✓ 数据库连接成功")
        
        # 测试连接
        print("正在测试数据库连接...")
        if not db_connection.test_connection():
            print("✗ 数据库连接测试失败")
            db_connection.disconnect()
            return False
        
        print("✓ 数据库连接测试通过")
        
        # 检查表是否存在
        print("正在检查数据库表...")
        tables = ['UserTable', 'PPIDRecord', 'ImportLog', 'BackupLog', 'AuditLog']
        missing_tables = []
        
        for table in tables:
            try:
                check_sql = f"""
                    SELECT COUNT(*) AS Count
                    FROM INFORMATION_SCHEMA.TABLES
                    WHERE TABLE_NAME = '{table}'
                """
                result = db_connection.execute_scalar(check_sql)
                if result == 0:
                    missing_tables.append(table)
            except Exception as e:
                logger.warning(f"检查表 {table} 失败: {e}")
                missing_tables.append(table)
        
        if missing_tables:
            print(f"⚠ 以下表不存在: {', '.join(missing_tables)}")
            print("  请运行: python scripts/init_database.py")
        else:
            print("✓ 所有数据库表已存在")
        
        db_connection.disconnect()
        print("\n✓ 数据库连接测试完成")
        return True
    
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        logger.error(f"数据库连接测试失败: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    print("=" * 50)
    print("数据库连接测试")
    print("=" * 50)
    print()
    
    success = test_database_connection()
    
    print()
    if success:
        print("✓ 所有测试通过，可以运行应用程序")
    else:
        print("✗ 测试失败，请检查配置和数据库连接")
    
    sys.exit(0 if success else 1)

