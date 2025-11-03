"""快速数据库连接测试脚本。

测试连接到指定 SQL Server 数据库。
"""

import sys
from pathlib import Path

# 设置 Windows 控制台输出为 UTF-8
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


def test_connection() -> bool:
    """测试数据库连接。
    
    Returns:
        连接成功返回 True，失败返回 False
    """
    setup_logging()
    
    print("=" * 60)
    print("SQL Server 连接测试")
    print("=" * 60)
    print()
    
    try:
        # 加载配置
        print("1. 加载配置文件...")
        config = ConfigManager()
        if not config.load_config():
            print("  ✗ 配置文件加载失败")
            print(f"  配置文件路径: {config.config_path}")
            return False
        
        print(f"  ✓ 配置文件加载成功: {config.config_path}")
        
        # 显示配置信息
        db_config = config.get_database_config()
        print("\n2. 数据库配置信息:")
        print(f"   服务器: {db_config.get('server', 'N/A')}")
        print(f"   数据库: {db_config.get('database', 'N/A')}")
        print(f"   用户名: {db_config.get('login', 'N/A')}")
        password = db_config.get('password', '')
        print(f"   密码: {'***' if password else '(空)'}")
        
        # 创建连接
        print("\n3. 创建数据库连接...")
        db_connection = DatabaseConnectionFactory.create_from_config(config)
        print("  ✓ 连接对象创建成功")
        
        # 测试连接
        print("\n4. 测试数据库连接...")
        print("   正在连接，请稍候...")
        
        if db_connection.connect():
            print("  ✓ 数据库连接成功！")
            
            # 测试查询
            print("\n5. 测试数据库查询...")
            try:
                result = db_connection.execute_scalar("SELECT @@VERSION")
                if result:
                    version_info = str(result).split('\n')[0] if result else "N/A"
                    print(f"  ✓ 查询成功")
                    print(f"   SQL Server 版本: {version_info[:80]}...")
                
                # 测试数据库是否存在
                db_name = db_config.get('database', '')
                check_db_sql = f"""
                    SELECT COUNT(*) 
                    FROM sys.databases 
                    WHERE name = '{db_name}'
                """
                db_exists = db_connection.execute_scalar(check_db_sql)
                
                if db_exists and db_exists > 0:
                    print(f"\n  ✓ 数据库 '{db_name}' 存在")
                else:
                    print(f"\n  ⚠ 数据库 '{db_name}' 不存在")
                    print(f"  请先创建数据库: CREATE DATABASE {db_name}")
                
                # 测试表是否存在
                print(f"\n6. 检查数据库表...")
                tables_sql = """
                    SELECT TABLE_NAME 
                    FROM INFORMATION_SCHEMA.TABLES 
                    WHERE TABLE_TYPE = 'BASE TABLE'
                    ORDER BY TABLE_NAME
                """
                tables = db_connection.execute_query(tables_sql)
                
                if tables:
                    print(f"  ✓ 找到 {len(tables)} 个表:")
                    for table in tables[:10]:  # 只显示前10个
                        print(f"    - {table['TABLE_NAME']}")
                    if len(tables) > 10:
                        print(f"    ... 还有 {len(tables) - 10} 个表")
                else:
                    print("  ⚠ 数据库中没有表")
                    print("  请运行: python scripts/init_database.py")
                
            except Exception as e:
                print(f"  ✗ 查询测试失败: {e}")
                logger.error(f"查询测试失败: {e}", exc_info=True)
            
            # 关闭连接
            db_connection.disconnect()
            print("\n" + "=" * 60)
            print("✓ 数据库连接测试通过！")
            print("=" * 60)
            return True
        else:
            print("  ✗ 数据库连接失败")
            return False
    
    except Exception as e:
        print(f"\n✗ 测试过程出错: {e}")
        logger.error(f"连接测试失败: {e}", exc_info=True)
        print("\n可能的原因:")
        print("  1. SQL Server 未运行或不可访问")
        print("  2. 服务器地址或端口不正确")
        print("  3. 用户名或密码错误")
        print("  4. 防火墙阻止连接")
        print("  5. SQL Server 未启用 TCP/IP 协议")
        return False


if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)

