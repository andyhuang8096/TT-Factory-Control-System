"""创建默认管理员用户脚本。

用于首次运行时创建默认管理员账户。
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
from src.core.security import Authentication
from src.utils.logger import setup_logging
import logging

logger = logging.getLogger(__name__)


def create_default_admin() -> bool:
    """创建默认管理员用户。
    
    Returns:
        创建成功返回 True，失败返回 False
    """
    try:
        # 设置日志
        setup_logging()
        
        # 加载配置
        config = ConfigManager()
        if not config.load_config():
            logger.error("配置文件加载失败")
            return False
        
        # 创建数据库连接
        db_connection = DatabaseConnectionFactory.create_from_config(config)
        
        if not db_connection.connect():
            logger.error("数据库连接失败")
            return False
        
        # 创建认证对象
        auth = Authentication(db_connection)
        
        # 检查管理员是否已存在
        from src.features.crud.read import ReadOperation
        read_op = ReadOperation(db_connection)
        existing = read_op.get_all(
            'UserTable',
            where_clause='UserName = ? AND Role = ?',
            parameters=('admin', 'admin')
        )
        
        if existing:
            logger.info("管理员用户已存在")
            db_connection.disconnect()
            return True
        
        # 创建默认管理员
        # 默认密码：admin123（生产环境应该修改）
        admin_id = auth.create_user(
            username='admin',
            password='admin123',
            email='admin@example.com',
            full_name='系统管理员',
            role='admin'
        )
        
        logger.info(f"默认管理员创建成功，ID: {admin_id}")
        logger.warning("默认密码: admin123，请尽快修改！")
        
        db_connection.disconnect()
        return True
    
    except Exception as e:
        logger.error(f"创建默认管理员失败: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    print("正在创建默认管理员用户...")
    print("默认用户名: admin")
    print("默认密码: admin123")
    print("（请在生产环境中修改密码）")
    print()
    
    success = create_default_admin()
    
    if success:
        print("✓ 默认管理员创建成功")
        print("请使用用户名 'admin' 和密码 'admin123' 登录")
    else:
        print("✗ 默认管理员创建失败")
        print("请检查日志以获取详细信息")
    
    sys.exit(0 if success else 1)

