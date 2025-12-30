# TT_PPID_CS 生产版本实施总结

## 1. 项目概况
本项目 (`TT_PPID_CS`) 是 `TT-Factory-Control-System` 的 C#/.NET 8 WPF 生产版本，旨在替代 Python MVP 原型。项目采用 **Clean Architecture**（整洁架构）设计，确保代码的高内聚、低耦合和可维护性。

## 2. 核心架构与技术栈
*   **开发框架**: .NET 8 (LTS)
*   **UI 框架**: WPF (Windows Presentation Foundation)
*   **UI 组件库**: MaterialDesignInXamlToolkit (现代化 Material Design 风格)
*   **MVVM 框架**: CommunityToolkit.Mvvm
*   **ORM 框架**: Entity Framework Core 8 (SQL Server)
*   **依赖注入**: Microsoft.Extensions.DependencyInjection
*   **工具库**:
    *   `MiniExcel` & `CsvHelper`: 高性能 Excel/CSV 导入导出
    *   `Serilog`: 日志管理 (计划中)

## 3. 已实现功能模块

### 3.1 基础设施层 (Infrastructure)
*   **数据库上下文**: `AppDbContext` 配置了所有实体映射，支持自动审计字段 (`CreateTime`, `UpdateTime`)。
*   **仓储模式**: 实现了通用泛型仓储 `Repository<T>` 和工作单元 `UnitOfWork`，封装了基本 CRUD 和软删除逻辑。
*   **依赖注入**: 在 `App.xaml.cs` 中配置了完整的 DI 容器，服务生命周期管理优化为 `Transient` 以适应 WPF 线程模型。

### 3.2 业务逻辑层 (Application)
*   **认证服务 (`AuthService`)**: 实现了用户登录校验，密码哈希算法与 Python 版本完全兼容 (PBKDF2-HMAC-SHA256)，确保旧数据无缝迁移。
*   **PPID 管理 (`PPIDService`)**: 实现了 PPID 记录的增删改查、搜索、状态管理。
*   **数据导入 (`ImportService`)**: 支持 `.csv`, `.xlsx`, `.xls`, `.json` 格式数据导入，包含批量写入和事务处理。
*   **备份服务 (`BackupService`)**: 实现了 SQL Server 数据库的完整备份与恢复逻辑（通过原生 SQL 命令）。
*   **用户管理 (`UserService`)**: 实现了用户账户的创建、编辑、删除（软删除）、密码重置和角色管理。
*   **报表统计 (`ReportService`)**: 提供了系统概览数据统计（PPID 状态分布、用户数、操作记录数等）。

### 3.3 用户界面层 (UI)
*   **主窗口 (`MainWindow`)**: 采用侧边栏导航布局，集成了 Material Design 风格，支持动态视图切换。
*   **登录界面 (`LoginWindow`)**: 安全的登录入口，包含验证反馈。
*   **PPID 管理视图 (`PPIDManagementView`)**:
    *   数据表格展示，支持分页（基础）和状态高亮。
    *   顶部工具栏包含多条件搜索。
    *   集成添加/编辑对话框 (`PPIDRecordDialog`)。
*   **用户管理视图 (`UserManagementView`)**:
    *   用户列表展示。
    *   用户添加/编辑对话框 (`UserDialog`)，包含密码确认逻辑。
*   **统计概览视图 (`StatisticsView`)**:
    *   卡片式布局展示关键指标 (KPI)。
    *   模型分布条形图。

## 4. 数据库迁移状态
*   数据库结构与 Python MVP 版本保持一致。
*   连接字符串目前硬编码在 `App.xaml.cs` 中，下一步建议迁移至 `appsettings.json`。

## 5. 后续计划
1.  **配置外部化**: 将数据库连接字符串移至配置文件。
2.  **日志完善**: 集成 Serilog 并记录到文件/数据库。
3.  **异常处理**: 引入全局异常捕获机制。
4.  **单元测试**: 为 Application 层添加 xUnit 测试。

---
**状态**: 核心功能迁移完成，可进行集成测试。
