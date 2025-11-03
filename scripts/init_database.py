"""数据库初始化脚本。

用于创建数据库表结构。
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.config.config_manager import ConfigManager
from src.core.database import DatabaseConnectionFactory, CREATE_TABLES
from src.utils.logger import setup_logging
import logging

logger = logging.getLogger(__name__)


def initialize_database() -> bool:
    """初始化数据库表结构。
    
    Returns:
        初始化成功返回 True，失败返回 False
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
        
        logger.info("开始创建数据库表...")
        
        # 创建所有表
        for i, create_sql in enumerate(CREATE_TABLES, 1):
            try:
                db_connection.execute_non_query(create_sql)
                logger.info(f"表 {i}/{len(CREATE_TABLES)} 创建成功")
            except Exception as e:
                logger.error(f"创建表失败: {e}", exc_info=True)
                # 继续创建其他表
                continue
        
        logger.info("数据库表结构初始化完成")
        
        # 关闭连接
        db_connection.disconnect()
        
        return True
    
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    success = initialize_database()
    sys.exit(0 if success else 1)

