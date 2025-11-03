"""查询 PPID 记录详细信息。

显示指定 PPID 记录的完整信息。
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


def query_ppid_records() -> None:
    """查询所有 PPID 记录。"""
    setup_logging(log_level=logging.WARNING)
    
    print("=" * 70)
    print("查询 PPID 记录")
    print("=" * 70)
    print()
    
    try:
        # 加载配置和连接数据库
        config = ConfigManager()
        if not config.load_config():
            print("  ✗ 配置文件加载失败")
            return
        
        db_connection = DatabaseConnectionFactory.create_from_config(config)
        if not db_connection.connect():
            print("  ✗ 数据库连接失败")
            return
        
        crud = CRUDOperations(db_connection)
        
        # 查询所有有效的 PPID 记录
        print("正在查询 PPID 记录...")
        records = crud.read.get_all(
            'PPIDRecord',
            where_clause='IsDeleted = 0',
            order_by='Id DESC'
        )
        
        if records:
            print(f"\n✓ 找到 {len(records)} 条有效记录:\n")
            print("-" * 70)
            
            for i, record in enumerate(records, 1):
                print(f"\n记录 #{i}:")
                print(f"  ID: {record.get('Id', 'N/A')}")
                print(f"  PPID: {record.get('PPID', 'N/A')}")
                print(f"  序列号: {record.get('SerialNumber', 'N/A')}")
                print(f"  型号: {record.get('Model', 'N/A')}")
                print(f"  零件号: {record.get('PN', 'N/A')}")
                print(f"  状态: {record.get('Status', 'N/A')}")
                print(f"  使用天数: {record.get('InUseDays', 0)}")
                print(f"  损坏尝试次数: {record.get('CorruptedAttempts', 0)}")
                print(f"  最后使用时间: {record.get('LastUsedTime', 'N/A')}")
                print(f"  备注: {record.get('Notes', 'N/A')}")
                print(f"  创建时间: {record.get('CreateTime', 'N/A')}")
                print(f"  创建用户: {record.get('CreateUser', 'N/A')}")
                print(f"  更新时间: {record.get('UpdateTime', 'N/A')}")
                print("-" * 70)
        else:
            print("\n⚠ 没有找到有效的 PPID 记录")
        
        # 统计信息
        total_count = crud.read.count('PPIDRecord')
        active_count = crud.read.count('PPIDRecord', where_clause='IsDeleted = 0')
        deleted_count = total_count - active_count
        
        print(f"\n统计信息:")
        print(f"  - 总记录数: {total_count}")
        print(f"  - 有效记录数: {active_count}")
        print(f"  - 已删除记录数: {deleted_count}")
        
        db_connection.disconnect()
        
    except Exception as e:
        print(f"\n✗ 查询失败: {e}")
        logger.error(f"查询 PPID 记录失败: {e}", exc_info=True)


if __name__ == "__main__":
    query_ppid_records()

