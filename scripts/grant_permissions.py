"""数据库用户权限配置脚本。

提供 SQL 语句来授权用户访问 PPID_DB 数据库。
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


def print_grant_permissions_sql() -> None:
    """打印授权 SQL 语句。
    
    用户需要在 SQL Server Management Studio 中执行这些 SQL 语句。
    """
    config = ConfigManager()
    config.load_config()
    
    db_config = config.get_database_config()
    database = db_config.get('database', 'PPID_DB')
    login = db_config.get('login', 'TGUser')
    
    print("=" * 70)
    print("数据库用户权限配置 SQL 语句")
    print("=" * 70)
    print()
    print("请在 SQL Server Management Studio 中，以管理员身份执行以下 SQL 语句：")
    print()
    print("-" * 70)
    print()
    
    sql_statements = f"""-- 1. 确保用户存在于 SQL Server 级别（如果不存在则创建）
-- IF NOT EXISTS (SELECT * FROM sys.server_principals WHERE name = '{login}')
-- BEGIN
--     CREATE LOGIN [{login}] WITH PASSWORD = 'your_password_here';
-- END
-- GO

-- 2. 授予用户访问 PPID_DB 数据库的权限
USE [{database}];
GO

-- 3. 创建数据库用户（如果不存在）
IF NOT EXISTS (SELECT * FROM sys.database_principals WHERE name = '{login}')
BEGIN
    CREATE USER [{login}] FOR LOGIN [{login}];
    PRINT '数据库用户 {login} 已创建';
END
ELSE
BEGIN
    PRINT '数据库用户 {login} 已存在';
END
GO

-- 4. 授予用户 db_owner 角色（完整权限）
ALTER ROLE db_owner ADD MEMBER [{login}];
GO

-- 或者授予更细粒度的权限：
-- ALTER ROLE db_datareader ADD MEMBER [{login}];  -- 读取权限
-- ALTER ROLE db_datawriter ADD MEMBER [{login}];  -- 写入权限
-- ALTER ROLE db_ddladmin ADD MEMBER [{login}];     -- DDL 权限

PRINT '用户 {login} 已获得数据库 {database} 的访问权限';
GO
"""
    
    print(sql_statements)
    print("-" * 70)
    print()
    print("执行步骤：")
    print(f"1. 打开 SQL Server Management Studio")
    print(f"2. 连接到服务器: {db_config.get('server', '192.168.30.254,1433')}")
    print(f"3. 以管理员身份登录")
    print(f"4. 执行上述 SQL 语句")
    print()
    print("=" * 70)


if __name__ == "__main__":
    print_grant_permissions_sql()

