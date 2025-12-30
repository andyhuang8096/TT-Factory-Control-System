# TT_PPID_CS (Production Version)

这是 Factory Control System 的生产版本源码，基于 C#/.NET 8 开发。

## 项目结构

- **src/TT_PPID_CS.Domain**: 核心业务实体和接口。
- **src/TT_PPID_CS.Application**: 应用层逻辑、DTOs。
- **src/TT_PPID_CS.Infrastructure**: 数据库访问 (EF Core)、外部服务实现。
- **src/TT_PPID_CS.UI**: WPF 用户界面。

## 快速开始

### 前置要求

- .NET 8 SDK
- Visual Studio 2022 (推荐) 或 VS Code
- SQL Server

### 运行项目

1. 打开 `TT_PPID_CS.sln`
2. 将 `TT_PPID_CS.UI` 设为启动项目
3. 配置连接字符串 (在 `src/TT_PPID_CS.UI/appsettings.json` 中配置)
4. 运行 (F5)

## 数据库迁移

本项目使用 EF Core Code First。

```bash
cd src/TT_PPID_CS.Infrastructure
dotnet ef migrations add InitialCreate --startup-project ../TT_PPID_CS.UI
dotnet ef database update --startup-project ../TT_PPID_CS.UI
```
