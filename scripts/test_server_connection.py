"""测试 SQL Server 连接并列出可用数据库。

先连接到 master 数据库，然后列出所有可用数据库。
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
from src.core.database.connection import DatabaseConnection
from src.utils.logger import setup_logging
import logging

logger = logging.getLogger(__name__)


def test_server_connection() -> bool:
    """测试连接到 SQL Server 并列出数据库。
    
    Returns:
        连接成功返回 True，失败返回 False
    """
    setup_logging()
    
    print("=" * 60)
    print("SQL Server 连接测试（先连接 master 数据库）")
    print("=" * 60)
    print()
    
    try:
        # 加载配置
        print("1. 加载配置文件...")
        config = ConfigManager()
        if not config.load_config():
            print("  ✗ 配置文件加载失败")
            return False
        
        db_config = config.get_database_config()
        server = db_config.get('server', '')
        login = db_config.get('login', '')
        password = db_config.get('password', '')
        
        print(f"  ✓ 配置文件加载成功")
        print(f"   服务器: {server}")
        print(f"   用户名: {login}")
        
        # 解析服务器地址和端口
        if ',' in server:
            server_parts = server.split(',')
            server_addr = server_parts[0].strip()
            port = int(server_parts[1].strip()) if len(server_parts) > 1 else 1433
        else:
            server_addr = server.strip()
            port = 1433
        
        # 连接到 master 数据库
        print(f"\n2. 尝试连接到 master 数据库...")
        print(f"   服务器: {server_addr}:{port}")
        
        master_conn = DatabaseConnection(
            server=server_addr,
            database='master',  # 先连接到 master 数据库
            login=login,
            password=password,
            port=port,
            encrypt=True
        )
        
        if master_conn.connect():
            print("  ✓ 成功连接到 master 数据库！")
            
            # 列出所有数据库
            print("\n3. 列出所有可用数据库...")
            databases_sql = """
                SELECT name, database_id, create_date 
                FROM sys.databases 
                WHERE database_id > 4  -- 排除系统数据库
                ORDER BY name
            """
            
            databases = master_conn.execute_query(databases_sql)
            
            if databases:
                print(f"  ✓ 找到 {len(databases)} 个用户数据库:\n")
                for db in databases:
                    print(f"    - {db['name']}")
                    print(f"      ID: {db['database_id']}")
                    print(f"      创建日期: {db.get('create_date', 'N/A')}")
                    print()
            else:
                print("  ⚠ 没有找到用户数据库")
            
            # 检查目标数据库是否存在
            target_db = db_config.get('database', '')
            if target_db:
                print(f"\n4. 检查目标数据库 '{target_db}'...")
                check_sql = f"""
                    SELECT name 
                    FROM sys.databases 
                    WHERE name = '{target_db}'
                """
                result = master_conn.execute_query(check_sql)
                
                if result:
                    print(f"  ✓ 数据库 '{target_db}' 存在")
                    
                    # 尝试连接到目标数据库
                    print(f"\n5. 尝试连接到数据库 '{target_db}'...")
                    target_conn = DatabaseConnection(
                        server=server_addr,
                        database=target_db,
                        login=login,
                        password=password,
                        port=port,
                        encrypt=True
                    )
                    
                    if target_conn.connect():
                        print(f"  ✓ 成功连接到数据库 '{target_db}'！")
                        
                        # 列出表
                        tables_sql = """
                            SELECT TABLE_NAME 
                            FROM INFORMATION_SCHEMA.TABLES 
                            WHERE TABLE_TYPE = 'BASE TABLE'
                            ORDER BY TABLE_NAME
                        """
                        tables = target_conn.execute_query(tables_sql)
                        
                        if tables:
                            print(f"\n6. 数据库 '{target_db}' 中的表:")
                            for table in tables:
                                print(f"    - {table['TABLE_NAME']}")
                        else:
                            print(f"\n6. 数据库 '{target_db}' 中没有表")
                        
                        target_conn.disconnect()
                    else:
                        print(f"  ✗ 无法连接到数据库 '{target_db}'")
                        print(f"  可能是权限问题")
                else:
                    print(f"  ✗ 数据库 '{target_db}' 不存在")
                    print(f"\n建议:")
                    print(f"  1. 创建数据库: CREATE DATABASE {target_db}")
                    print(f"  2. 或者使用已存在的数据库名称")
            
            master_conn.disconnect()
            print("\n" + "=" * 60)
            print("✓ 连接测试完成！")
            print("=" * 60)
            return True
        else:
            print("  ✗ 无法连接到 master 数据库")
            print("\n可能的原因:")
            print("  1. 用户名或密码错误")
            print("  2. SQL Server 未启用 SQL Server 身份验证")
            print("  3. 用户没有访问权限")
            return False
    
    except Exception as e:
        print(f"\n✗ 测试过程出错: {e}")
        logger.error(f"连接测试失败: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    success = test_server_connection()
    sys.exit(0 if success else 1)

