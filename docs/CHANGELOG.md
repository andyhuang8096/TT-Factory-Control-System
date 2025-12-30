# 更新日志

## [1.0.0-mvp] - 2024-12-30

### 新增

- **数据管理**
    - 实现了通用的数据添加和编辑对话框 (`RecordDialog`)，支持根据数据库表结构动态生成表单。
    - 实现了数据导入对话框 (`ImportDialog`)，支持 CSV, Excel, JSON 格式，包含后台线程处理和进度条。
    - 实现了数据搜索功能，支持并在字段中搜索关键词。

- **系统维护**
    - 实现了数据库备份功能 (`_backup_database`)，支持将数据库备份到本地文件。
    - 实现了数据库恢复功能 (`_restore_database`)，支持从备份文件恢复数据库（需谨慎使用）。

- **UI 改进**
    - 在主窗口工具栏下方添加了表选择、搜索框和重置按钮。
    - 优化了菜单栏和工具栏的布局。

### 修复

- 完善了 `MainWindow` 中的占位符方法。

### 技术细节

- `RecordDialog`: 使用 `INFORMATION_SCHEMA.COLUMNS` 动态获取列信息。
- `DataImporter`: 集成到 GUI，增加了异常处理和用户反馈。
- `DatabaseBackup/Restore`: 实现了 SQL Server 的备份和恢复逻辑，包括处理连接切换。
