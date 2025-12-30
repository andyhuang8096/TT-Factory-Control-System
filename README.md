# TT_PPID_CS 数据库管理系统

## 项目简介

这是一个基于 SQL Server 2019 的数据库管理系统（DBS/DBMS），结合了数据库管理功能和业务应用功能。项目采用 Python 开发原型，后期将迁移到 C#/.NET 生产环境。

**当前版本**: MVP 1.0.0 - 可测试版本

## 功能特性

- ✅ 基础的 CRUD 操作（增删改查）
- ✅ 数据导入/导出（CSV, Excel, JSON）
- ✅ 数据库备份/恢复
- ✅ 用户权限管理（基于角色的访问控制）
- ✅ 数据统计分析
- ✅ Windows 桌面应用界面（PyQt6）

## 技术栈

### 原型阶段（当前）
- Python 3.10+
- PyQt6（GUI框架）
- pyodbc（SQL Server 连接）
- pandas（数据处理）
- cryptography（密码加密）

### 生产环境（后续）
- C# (.NET 6/7/8)
- WPF/WinForms
- Entity Framework Core

## 快速开始

### 环境要求

- Python 3.10 或更高版本
- SQL Server 2019 或更高版本
- Windows 操作系统

### 安装步骤

1. **创建虚拟环境**：
```bash
python -m venv venv
```

2. **激活虚拟环境**（Windows）：
```bash
venv\Scripts\activate
```

3. **安装依赖**：
```bash
pip install -r requirements.txt
```

4. **配置数据库连接**：
   - 复制 `config/app.ini.example` 为 `config/app.ini`
   - 修改数据库连接信息：
```ini
[Database]
server=localhost,1433
database=PPID_DB
login=sa
password=your_password
```

5. **初始化数据库**：
```bash
# 创建数据库表结构
python scripts/init_database.py

# 创建默认管理员用户
python scripts/create_admin.py
```

默认管理员账户：
- 用户名: `admin`
- 密码: `admin123`

**⚠️ 重要**: 生产环境请立即修改密码！

6. **测试系统**：
```bash
# 测试数据库连接
python scripts/test_connection.py

# 运行 MVP 快速测试
python scripts/test_mvp.py
```

7. **运行应用**：
```bash
python src/main.py
```

## 项目结构

```
TT_PPID_CS/
├── src/                    # 源代码
│   ├── core/              # 核心模块
│   │   ├── database/     # 数据库连接和模型
│   │   ├── config/        # 配置管理
│   │   └── security/      # 安全模块
│   ├── features/          # 功能模块
│   │   ├── crud/         # CRUD 操作
│   │   ├── import_export/# 导入导出
│   │   ├── backup/       # 备份恢复
│   │   └── analytics/    # 统计分析
│   ├── ui/               # 用户界面
│   └── utils/            # 工具函数
├── config/               # 配置文件
├── scripts/              # 脚本文件
│   ├── init_database.py  # 初始化数据库
│   ├── create_admin.py   # 创建管理员
│   ├── test_connection.py# 测试连接
│   └── test_mvp.py      # MVP 测试
├── tests/                # 测试代码
├── docs/                 # 文档
└── requirements.txt      # 依赖列表
```

## MVP 版本功能

### ✅ 已实现

- 用户登录认证
- 数据表格显示和刷新
- 数据导出（CSV/Excel/JSON）
- 数据删除（软删除）
- 统计信息查看
- 权限控制
- 数据添加/编辑对话框
- 数据导入对话框
- 数据库备份/恢复对话框
- 数据搜索和过滤 (基于字段)

### ⏳ 待实现

- (无 - MVP 功能已全部完成)

详细测试指南请参考 [MVP 测试指南](docs/MVP_TEST_GUIDE.md)

## 开发指南

详细的开发指南请参考 `AGEND.md` 文件。

## 常见问题

### 数据库连接失败

1. 检查 SQL Server 是否运行
2. 检查 `config/app.ini` 中的连接信息
3. 检查 SQL Server 是否启用 TCP/IP 协议
4. 检查防火墙是否允许端口 1433

### 表不存在错误

运行数据库初始化脚本：
```bash
python scripts/init_database.py
```

### 登录失败

创建默认管理员：
```bash
python scripts/create_admin.py
```

## 许可证

[待定]

## 更新日志

### MVP 1.0.0 (2024)

- 初始 MVP 版本发布
- 实现核心功能模块
- 基础 UI 界面
- 可测试版本

