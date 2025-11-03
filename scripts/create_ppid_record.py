"""创建新的 PPID 记录脚本。

创建一条新的 PPID 记录并保留在数据库中。
"""

import sys
from pathlib import Path
from datetime import datetime

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


def create_ppid_record() -> None:
    """创建一条新的 PPID 记录。"""
    setup_logging(log_level=logging.WARNING)
    
    print("=" * 60)
    print("创建新的 PPID 记录")
    print("=" * 60)
    print()
    
    try:
        # 加载配置和连接数据库
        print("1. 连接数据库...")
        config = ConfigManager()
        if not config.load_config():
            print("  ✗ 配置文件加载失败")
            return
        
        db_connection = DatabaseConnectionFactory.create_from_config(config)
        if not db_connection.connect():
            print("  ✗ 数据库连接失败")
            return
        
        print("  ✓ 数据库连接成功")
        crud = CRUDOperations(db_connection)
        
        # 生成 PPID（使用时间戳确保唯一性）
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        ppid = f"PPID-{timestamp}"
        
        print(f"\n2. 创建 PPID 记录...")
        print(f"   PPID: {ppid}")
        
        # 创建 PPID 记录
        ppid_data = {
            'PPID': ppid,
            'SerialNumber': f'SN{timestamp[-8:]}',  # 使用时间戳后8位作为序列号
            'Model': 'DELL',
            'PN': 'JN38V',
            'Status': 'available',
            'InUseDays': 0,
            'CorruptedAttempts': 0,
            'Notes': f'创建时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
        }
        
        try:
            record_id = crud.create.create('PPIDRecord', ppid_data, 'admin')
            print(f"  ✓ PPID 记录创建成功！")
            print(f"    - 记录 ID: {record_id}")
            print(f"    - PPID: {ppid}")
            print(f"    - SerialNumber: {ppid_data['SerialNumber']}")
            print(f"    - Model: {ppid_data['Model']}")
            print(f"    - PN: {ppid_data['PN']}")
            print(f"    - Status: {ppid_data['Status']}")
            
            # 验证记录已创建
            print(f"\n3. 验证记录...")
            record = crud.read.get_by_id('PPIDRecord', record_id)
            if record:
                print(f"  ✓ 记录验证成功")
                print(f"    - ID: {record['Id']}")
                print(f"    - PPID: {record['PPID']}")
                print(f"    - CreateTime: {record.get('CreateTime', 'N/A')}")
                print(f"    - IsDeleted: {record.get('IsDeleted', False)}")
            
            print(f"\n" + "=" * 60)
            print(f"✓ PPID 记录已成功创建并保存到数据库！")
            print(f"=" * 60)
            print(f"\n记录信息:")
            print(f"  - 记录 ID: {record_id}")
            print(f"  - PPID: {ppid}")
            print(f"  - 状态: {ppid_data['Status']}")
            print(f"\n记录已永久保存在数据库中，可以随时查询和管理。")
            
        except Exception as e:
            print(f"  ✗ 创建失败: {e}")
            logger.error(f"创建 PPID 记录失败: {e}", exc_info=True)
        
        db_connection.disconnect()
        
    except Exception as e:
        print(f"\n✗ 操作失败: {e}")
        logger.error(f"创建 PPID 记录过程出错: {e}", exc_info=True)


if __name__ == "__main__":
    create_ppid_record()

