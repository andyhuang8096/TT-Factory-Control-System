"""PPID CRUD 操作测试脚本。

演示完整的 PPID（PPID 记录）的增删改查操作。
"""

import sys
import os
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


def test_ppid_crud() -> bool:
    """测试 PPID 的 CRUD 操作。
    
    Returns:
        测试成功返回 True，失败返回 False
    """
    setup_logging()
    
    print("=" * 60)
    print("PPID CRUD 操作测试")
    print("=" * 60)
    print()
    
    try:
        # 1. 加载配置和连接数据库
        print("步骤 1: 连接数据库...")
        config = ConfigManager()
        if not config.load_config():
            print("  ✗ 配置文件加载失败")
            print(f"  请检查配置文件: {config.config_path}")
            return False
        
        db_connection = DatabaseConnectionFactory.create_from_config(config)
        if not db_connection.connect():
            print("  ✗ 数据库连接失败")
            return False
        
        print("  ✓ 数据库连接成功")
        crud = CRUDOperations(db_connection)
        
        # 2. CREATE - 创建 PPID 记录
        print("\n步骤 2: CREATE - 创建 PPID 记录...")
        test_ppid = f"TEST-PPID-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        ppid_data = {
            'PPID': test_ppid,
            'SerialNumber': 'SN123456789',
            'Model': 'DELL',
            'PN': 'JN38V',
            'Status': 'available',
            'InUseDays': 0,
            'CorruptedAttempts': 0,
            'Notes': '测试用的 PPID 记录'
        }
        
        try:
            record_id = crud.create.create('PPIDRecord', ppid_data, 'admin')
            print(f"  ✓ PPID 记录创建成功")
            print(f"    - ID: {record_id}")
            print(f"    - PPID: {test_ppid}")
            print(f"    - Model: {ppid_data['Model']}")
            print(f"    - Status: {ppid_data['Status']}")
        except Exception as e:
            print(f"  ✗ 创建失败: {e}")
            db_connection.disconnect()
            return False
        
        # 3. READ - 读取 PPID 记录
        print("\n步骤 3: READ - 读取 PPID 记录...")
        try:
            # 根据 ID 读取
            record = crud.read.get_by_id('PPIDRecord', record_id)
            if record:
                print(f"  ✓ 根据 ID 读取成功")
                print(f"    - ID: {record['Id']}")
                print(f"    - PPID: {record['PPID']}")
                print(f"    - SerialNumber: {record.get('SerialNumber', 'N/A')}")
                print(f"    - Model: {record.get('Model', 'N/A')}")
                print(f"    - Status: {record.get('Status', 'N/A')}")
                print(f"    - CreateTime: {record.get('CreateTime', 'N/A')}")
            else:
                print("  ✗ 记录未找到")
                db_connection.disconnect()
                return False
            
            # 根据 PPID 搜索
            print("\n  搜索 PPID...")
            search_results = crud.read.search('PPIDRecord', 'PPID', test_ppid[:10])
            print(f"  ✓ 搜索到 {len(search_results)} 条记录")
            
        except Exception as e:
            print(f"  ✗ 读取失败: {e}")
            db_connection.disconnect()
            return False
        
        # 4. UPDATE - 更新 PPID 记录
        print("\n步骤 4: UPDATE - 更新 PPID 记录...")
        update_data = {
            'Status': 'in_use',
            'InUseDays': 5,
            'LastUsedTime': datetime.now(),
            'Notes': '已更新：状态改为 in_use，使用天数 5 天'
        }
        
        try:
            affected_rows = crud.update.update('PPIDRecord', record_id, update_data, 'admin')
            if affected_rows > 0:
                print(f"  ✓ PPID 记录更新成功")
                print(f"    - 受影响行数: {affected_rows}")
                
                # 验证更新
                updated_record = crud.read.get_by_id('PPIDRecord', record_id)
                if updated_record:
                    print(f"    - 更新后 Status: {updated_record.get('Status')}")
                    print(f"    - 更新后 InUseDays: {updated_record.get('InUseDays')}")
                    print(f"    - 更新后 UpdateTime: {updated_record.get('UpdateTime')}")
            else:
                print("  ✗ 更新失败：未找到记录")
                db_connection.disconnect()
                return False
        except Exception as e:
            print(f"  ✗ 更新失败: {e}")
            db_connection.disconnect()
            return False
        
        # 5. 再次更新 - 模拟状态变更
        print("\n步骤 4.5: UPDATE - 再次更新状态...")
        update_data2 = {
            'Status': 'available',
            'InUseDays': 0,
            'Notes': '已更新：状态恢复为 available'
        }
        
        try:
            affected_rows = crud.update.update('PPIDRecord', record_id, update_data2, 'admin')
            print(f"  ✓ 第二次更新成功")
            print(f"    - 受影响行数: {affected_rows}")
        except Exception as e:
            print(f"  ✗ 第二次更新失败: {e}")
        
        # 6. DELETE - 软删除 PPID 记录
        print("\n步骤 5: DELETE - 软删除 PPID 记录...")
        try:
            # 先确认记录存在
            before_delete = crud.read.get_by_id('PPIDRecord', record_id)
            if not before_delete:
                print("  ✗ 删除前记录不存在")
                db_connection.disconnect()
                return False
            
            print(f"    - 删除前 IsDeleted: {before_delete.get('IsDeleted', False)}")
            
            # 执行软删除
            affected_rows = crud.delete.delete('PPIDRecord', record_id, 'admin')
            
            if affected_rows > 0:
                print(f"  ✓ PPID 记录软删除成功")
                print(f"    - 受影响行数: {affected_rows}")
                
                # 验证软删除（应该查询不到，因为 get_by_id 会过滤 IsDeleted=1）
                after_delete = crud.read.get_by_id('PPIDRecord', record_id)
                if after_delete is None:
                    print("  ✓ 软删除验证成功：记录已不可见（IsDeleted=1）")
                else:
                    print("  ⚠ 软删除验证：记录仍然可见（可能有问题）")
                
                # 直接查询数据库验证 IsDeleted 状态
                verify_sql = "SELECT IsDeleted FROM PPIDRecord WHERE Id = ?"
                verify_result = db_connection.execute_scalar(verify_sql, (record_id,))
                if verify_result:
                    print(f"  ✓ 数据库验证：IsDeleted = {verify_result} (1 表示已删除)")
            else:
                print("  ✗ 删除失败：未找到记录")
                db_connection.disconnect()
                return False
        except Exception as e:
            print(f"  ✗ 删除失败: {e}")
            db_connection.disconnect()
            return False
        
        # 7. 统计信息
        print("\n步骤 6: 统计信息...")
        try:
            total_count = crud.read.count('PPIDRecord')
            active_count = crud.read.count('PPIDRecord', where_clause='IsDeleted = 0')
            deleted_count = total_count - active_count
            
            print(f"  ✓ PPIDRecord 表统计:")
            print(f"    - 总记录数: {total_count}")
            print(f"    - 有效记录数: {active_count}")
            print(f"    - 已删除记录数: {deleted_count}")
        except Exception as e:
            print(f"  ✗ 统计失败: {e}")
        
        db_connection.disconnect()
        
        print("\n" + "=" * 60)
        print("✓ 所有 CRUD 操作测试通过！")
        print("=" * 60)
        print(f"\n测试使用的 PPID: {test_ppid}")
        print(f"记录 ID: {record_id}")
        print("\n注意：测试记录已被软删除，如需恢复，可以手动更新数据库中的 IsDeleted 字段")
        
        return True
    
    except Exception as e:
        print(f"\n✗ 测试过程出错: {e}")
        logger.error(f"PPID CRUD 测试失败: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    success = test_ppid_crud()
    sys.exit(0 if success else 1)

