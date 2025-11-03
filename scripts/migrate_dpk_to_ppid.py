"""数据库迁移和初始化脚本。

用于将 DPKRecord 表迁移到 PPIDRecord，或创建新的 PPIDRecord 表。
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
from src.core.database import DatabaseConnectionFactory, CREATE_TABLES
from src.utils.logger import setup_logging
import logging

logger = logging.getLogger(__name__)


def migrate_or_create_table() -> bool:
    """迁移 DPKRecord 表到 PPIDRecord 或创建新表。
    
    Returns:
        操作成功返回 True，失败返回 False
    """
    try:
        # 设置日志
        setup_logging()
        
        # 加载配置
        config = ConfigManager()
        if not config.load_config():
            logger.error("配置文件加载失败")
            print("✗ 配置文件加载失败")
            return False
        
        # 创建数据库连接
        db_connection = DatabaseConnectionFactory.create_from_config(config)
        
        if not db_connection.connect():
            logger.error("数据库连接失败")
            print("✗ 数据库连接失败")
            return False
        
        print("✓ 数据库连接成功")
        
        # 检查 DPKRecord 表是否存在
        check_dpk_sql = """
            SELECT COUNT(*) AS Count
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_NAME = 'DPKRecord'
        """
        dpk_exists = db_connection.execute_scalar(check_dpk_sql)
        
        # 检查 PPIDRecord 表是否存在
        check_ppid_sql = """
            SELECT COUNT(*) AS Count
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_NAME = 'PPIDRecord'
        """
        ppid_exists = db_connection.execute_scalar(check_ppid_sql)
        
        if dpk_exists and dpk_exists > 0:
            print("检测到 DPKRecord 表存在")
            if ppid_exists and ppid_exists > 0:
                print("⚠ 警告: PPIDRecord 表也已存在")
                print("  请手动处理数据迁移")
                db_connection.disconnect()
                return False
            else:
                print("正在将 DPKRecord 表重命名为 PPIDRecord...")
                try:
                    # 重命名表
                    rename_table_sql = "EXEC sp_rename 'DPKRecord', 'PPIDRecord';"
                    db_connection.execute_non_query(rename_table_sql)
                    print("  ✓ 表重命名成功")
                    
                    # 重命名索引
                    try:
                        rename_index1_sql = "EXEC sp_rename 'PPIDRecord.IX_DPKRecord_PPID', 'IX_PPIDRecord_PPID', 'INDEX';"
                        db_connection.execute_non_query(rename_index1_sql)
                        print("  ✓ 索引 IX_DPKRecord_PPID 重命名成功")
                    except Exception as e:
                        logger.warning(f"重命名索引 IX_DPKRecord_PPID 失败（可能不存在）: {e}")
                    
                    try:
                        rename_index2_sql = "EXEC sp_rename 'PPIDRecord.IX_DPKRecord_Status', 'IX_PPIDRecord_Status', 'INDEX';"
                        db_connection.execute_non_query(rename_index2_sql)
                        print("  ✓ 索引 IX_DPKRecord_Status 重命名成功")
                    except Exception as e:
                        logger.warning(f"重命名索引 IX_DPKRecord_Status 失败（可能不存在）: {e}")
                    
                    try:
                        rename_index3_sql = "EXEC sp_rename 'PPIDRecord.IX_DPKRecord_Model', 'IX_PPIDRecord_Model', 'INDEX';"
                        db_connection.execute_non_query(rename_index3_sql)
                        print("  ✓ 索引 IX_DPKRecord_Model 重命名成功")
                    except Exception as e:
                        logger.warning(f"重命名索引 IX_DPKRecord_Model 失败（可能不存在）: {e}")
                    
                    print("✓ 表迁移完成")
                    db_connection.disconnect()
                    return True
                    
                except Exception as e:
                    logger.error(f"表重命名失败: {e}", exc_info=True)
                    print(f"✗ 表重命名失败: {e}")
                    db_connection.disconnect()
                    return False
        else:
            # DPKRecord 不存在，检查是否需要创建 PPIDRecord
            if not (ppid_exists and ppid_exists > 0):
                print("PPIDRecord 表不存在，正在创建...")
                try:
                    # 找到 CREATE_PPID_RECORD_TABLE 的 SQL
                    create_ppid_sql = None
                    for sql in CREATE_TABLES:
                        if 'CREATE TABLE PPIDRecord' in sql or 'CREATE TABLE PPIDRecord' in sql:
                            create_ppid_sql = sql
                            break
                    
                    if create_ppid_sql:
                        db_connection.execute_non_query(create_ppid_sql)
                        print("  ✓ PPIDRecord 表创建成功")
                    else:
                        # 如果找不到，执行所有表的创建脚本
                        print("  正在创建所有数据库表...")
                        for i, create_sql in enumerate(CREATE_TABLES, 1):
                            try:
                                db_connection.execute_non_query(create_sql)
                                logger.info(f"表 {i}/{len(CREATE_TABLES)} 创建成功")
                            except Exception as e:
                                logger.warning(f"创建表 {i} 失败（可能已存在）: {e}")
                        print("  ✓ 数据库表创建完成")
                    
                    db_connection.disconnect()
                    return True
                    
                except Exception as e:
                    logger.error(f"创建表失败: {e}", exc_info=True)
                    print(f"✗ 创建表失败: {e}")
                    db_connection.disconnect()
                    return False
            else:
                print("✓ PPIDRecord 表已存在，无需操作")
                db_connection.disconnect()
                return True
        
    except Exception as e:
        logger.error(f"迁移/创建表失败: {e}", exc_info=True)
        print(f"✗ 操作失败: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("数据库表迁移/初始化工具")
    print("=" * 60)
    print()
    
    success = migrate_or_create_table()
    
    if success:
        print()
        print("=" * 60)
        print("✓ 操作完成！")
        print("=" * 60)
        sys.exit(0)
    else:
        print()
        print("=" * 60)
        print("✗ 操作失败")
        print("=" * 60)
        sys.exit(1)

