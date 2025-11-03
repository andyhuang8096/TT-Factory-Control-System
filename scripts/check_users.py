"""检查系统用户信息。

显示系统中的所有用户信息。
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
from src.features.crud import CRUDOperations
from src.utils.logger import setup_logging
import logging

logger = logging.getLogger(__name__)


def check_users() -> None:
    """检查系统中的用户信息。"""
    setup_logging(log_level=logging.WARNING)  # 减少日志输出
    
    print("=" * 60)
    print("系统用户信息检查")
    print("=" * 60)
    print()
    
    try:
        # 加载配置
        config = ConfigManager()
        if not config.load_config():
            print("  ✗ 配置文件加载失败")
            return
        
        # 连接数据库
        db_connection = DatabaseConnectionFactory.create_from_config(config)
        if not db_connection.connect():
            print("  ✗ 数据库连接失败")
            return
        
        crud = CRUDOperations(db_connection)
        
        # 查询所有用户
        print("正在查询用户信息...")
        users = crud.read.get_all('UserTable', order_by='CreateTime DESC')
        
        if users:
            print(f"\n✓ 找到 {len(users)} 个用户:\n")
            for i, user in enumerate(users, 1):
                print(f"用户 {i}:")
                print(f"  - ID: {user.get('Id', 'N/A')}")
                print(f"  - 用户名: {user.get('UserName', 'N/A')}")
                print(f"  - 全名: {user.get('FullName', 'N/A')}")
                print(f"  - 邮箱: {user.get('Email', 'N/A')}")
                print(f"  - 角色: {user.get('Role', 'N/A')}")
                print(f"  - 状态: {'激活' if user.get('IsActive') else '禁用'}")
                print(f"  - 创建时间: {user.get('CreateTime', 'N/A')}")
                print()
        else:
            print("\n⚠ 系统中没有用户")
            print("\n需要创建默认管理员用户，请运行：")
            print("  python scripts/create_admin.py")
            print("\n默认管理员账户信息：")
            print("  - 用户名: admin")
            print("  - 密码: admin123")
        
        db_connection.disconnect()
        
    except Exception as e:
        print(f"\n✗ 查询失败: {e}")
        logger.error(f"查询用户失败: {e}", exc_info=True)


if __name__ == "__main__":
    check_users()
