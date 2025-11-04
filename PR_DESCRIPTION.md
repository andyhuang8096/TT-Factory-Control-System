## 变更内容

- ✅ 将项目中所有 DPK 替换为 PPID
  - 更新数据模型: DPKRecord -> PPIDRecord
  - 更新数据库表名和 SQL 语句
  - 更新界面显示文本
  - 更新所有脚本和配置文件
  - 更新文档

- ✅ 数据库迁移脚本
  - 创建 migrate_dpk_to_ppid.py 用于表迁移
  - 创建 migrate_dpk_to_ppid.sql SQL 迁移脚本

- ✅ 添加 GitHub 推送辅助工具
  - PowerShell 脚本
  - Bash 脚本
  - 推送指南文档

## 测试

- [x] 数据库迁移脚本测试通过
- [x] 数据库连接测试通过
- [x] 所有表已正确创建/迁移

## 相关变更

- 代码更新: 69 个文件，7417 行代码
- 数据库迁移: DPKRecord -> PPIDRecord
- 界面更新: 所有 DPK 相关显示文本已更新为 PPID

