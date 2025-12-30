# 生产版本开发计划 (C#/.NET)

## 1. 技术栈选型

根据项目需求，生产版本将基于 Microsoft .NET 平台开发，确保高性能、可维护性和企业级安全性。

- **核心框架**: .NET 8.0 (LTS - 长期支持版本)
- **UI 框架**: WPF (Windows Presentation Foundation)
    - 采用 MVVM (Model-View-ViewModel) 架构模式
    - UI 库: MaterialDesignInXamlToolkit (现代化外观) 或同样原生控件配合自定义样式
    - MVVM 框架: CommunityToolkit.Mvvm (微软官方轻量级 MVVM 库)
- **数据库访问**: Entity Framework Core 8
    - Code First 或 Database First (建议 Code First 以保持模型清晰)
    - 数据库: SQL Server 2019+
- **依赖注入**: Microsoft.Extensions.DependencyInjection
- **日志**: Serilog
- **单元测试**: xUnit + Moq + FluentAssertions

## 2. 项目架构 (Clean Architecture)

我们将采用类似于 Clean Architecture 的分层结构，以解耦关注点：

```
production/
├── src/
│   ├── TT_PPID_CS.Domain/          # 核心领域层 (实体, 领域服务, 接口) - 无依赖
│   ├── TT_PPID_CS.Application/     # 应用层 (DTOs, 业务逻辑接口, 映射) - 依赖 Domain
│   ├── TT_PPID_CS.Infrastructure/  # 基础设施层 (EF Core,文件操作, 外部服务实现) - 依赖 Application
│   └── TT_PPID_CS.UI/              # 表示层 (WPF 应用程序) - 依赖 Application, Infrastructure
├── tests/
│   └── TT_PPID_CS.Tests/           # 单元测试和集成测试
└── TT_PPID_CS.sln                  # 解决方案文件
```

## 3. 初始功能迁移规划

基于 Python MVP 版本，我们将分阶段迁移功能：

### 第一阶段：基础设施搭建
- 搭建解决方案结构
- 配置 EF Core 数据库上下文
- 实现通用 Repository 模式
- 搭建 WPF MVVM 基础框架 (主窗口、导航)

### 第二阶段：核心功能迁移
- **用户认证**: 登录界面，基于角色的权限控制
- **基础数据管理**: PPID 记录的 CRUD
- **数据表格**: 使用 DataGrid 展示数据，支持分页和排序

### 第三阶段：高级功能
- **导入/导出**: 迁移 Excel/CSV 处理逻辑 (使用 EPPlus 或 CsvHelper)
- **报表统计**: 迁移统计分析逻辑
- **备份恢复**: 集成 SQL DMO 或 T-SQL 备份命令

## 4. 数据库迁移策略
由于 MVP 已经设计了数据库结构，我们将：
1. 使用 EF Core 对现有数据库进行逆向工程 (Scaffold-DbContext) 以生成初始实体。
2. 或者手动创建实体以匹配现有 schema。

## 5. 下一步行动
1. 创建 `production` 目录。
2. 使用 `dotnet` CLI 初始化解决方案和项目。
3. 添加项目引用和 NuGet 包。
