# TT_PPID_CS 数据库管理系统 - Agent 开发指南

## Repository Guidelines

## Project Structure & Module Organization

### 目录结构说明

- `src/core/`: 核心功能模块，包括数据库连接、配置管理、安全模块
- `src/features/`: 业务功能模块，包括 CRUD、导入导出、备份恢复、统计分析
- `src/ui/`: 用户界面模块，使用 PyQt6 开发
- `src/utils/`: 通用工具函数

### 模块依赖关系

```
main.py
  ├── ui/main_window.py
  │   ├── features/crud/
  │   ├── features/import_export/
  │   ├── features/backup/
  │   └── features/analytics/
  ├── core/database/connection.py
  ├── core/config/config_manager.py
  └── core/security/
```

## Build, Test, and Development Commands

### 开发环境设置

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境（Windows）
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 安装开发依赖（格式化工具）
pip install black isort
```

### 运行应用

```bash
# 直接运行
python src/main.py

# 或使用模块方式
python -m src.main
```

### 测试

```bash
# 运行所有测试
pytest tests/

# 运行单元测试
pytest tests/unit/

# 运行集成测试
pytest tests/integration/

# 生成覆盖率报告
pytest --cov=src tests/
```

### 代码格式化

```bash
# 格式化代码
black src/
isort src/

# 检查代码格式（不修改）
black --check src/
isort --check src/
```

## Coding Style & Naming Conventions

### Python 代码规范

- **遵循 PEP 8**: 使用 4 个空格缩进，行长度限制 88 字符（Black 默认）
- **类型提示**: 所有函数必须包含类型提示
- **文档字符串**: 所有模块、类、函数必须包含 docstring（Google 风格）
- **命名规范**:
  - 变量和函数: `snake_case`
  - 类名: `PascalCase`
  - 常量: `UPPER_SNAKE_CASE`
  - 私有成员: `_single_leading_underscore`

### 数据库规范

- **表名**: `PascalCase`（如：`UserTable`, `PPIDRecord`）
- **列名**: `PascalCase`（如：`UserId`, `CreateTime`）
- **主键**: 统一命名为 `Id`
- **外键**: `{ReferencedTable}Id`（如：`UserId`）
- **审计字段**: 每个表包含 `CreateTime`, `UpdateTime`, `CreateUser`, `UpdateUser`
- **软删除**: 使用 `IsDeleted` 标志位

### 代码示例

```python
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

class DatabaseConnection:
    """数据库连接管理类。
    
    负责管理 SQL Server 数据库连接，包括连接池管理和异常处理。
    """
    
    def __init__(self, connection_string: str) -> None:
        """初始化数据库连接。
        
        Args:
            connection_string: 数据库连接字符串
        """
        self.connection_string = connection_string
        self._connection: Optional[pyodbc.Connection] = None
    
    def execute_query(self, query: str, parameters: Optional[tuple] = None) -> List[dict]:
        """执行查询语句。
        
        Args:
            query: SQL 查询语句（使用参数化查询）
            parameters: 查询参数
        
        Returns:
            查询结果列表
        
        Raises:
            DatabaseError: 数据库操作失败时抛出
        """
        pass
```

## Testing Guidelines

### 测试原则

1. **单元测试**: 每个核心功能模块必须有对应的单元测试
2. **集成测试**: 覆盖主要业务流程
3. **覆盖率**: 核心模块测试覆盖率 ≥ 80%
4. **测试数据库**: 使用独立的测试数据库，不影响生产数据
5. **异常测试**: 测试各种异常情况（连接失败、数据错误等）

### 测试示例

```python
import pytest
from src.core.database.connection import DatabaseConnection

class TestDatabaseConnection:
    """数据库连接测试类。"""
    
    def test_connection_success(self):
        """测试成功连接数据库。"""
        conn = DatabaseConnection("test_connection_string")
        assert conn.connect() is True
    
    def test_connection_failure(self):
        """测试连接失败的情况。"""
        conn = DatabaseConnection("invalid_connection_string")
        with pytest.raises(DatabaseError):
            conn.connect()
```

## Commit & Pull Request Guidelines

### 提交信息规范

使用语义化提交信息：

- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档更新
- `style`: 代码格式（不影响代码运行）
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

示例：
```
feat: 实现数据库连接模块
fix: 修复 SQL 注入漏洞
docs: 更新 README.md
```

### Pull Request 检查清单

- [ ] 代码符合 PEP 8 规范
- [ ] 所有函数包含类型提示和文档字符串
- [ ] 使用参数化查询（防止 SQL 注入）
- [ ] 包含适当的错误处理和日志记录
- [ ] 通过了所有测试
- [ ] 更新了相关文档

## Security & Configuration Tips

### 安全要求

1. **密码加密**: 配置文件中的密码使用加密存储（使用 cryptography 库）
2. **SQL 注入防护**: 严格使用参数化查询，禁止字符串拼接 SQL
3. **权限控制**: 实现基于角色的访问控制（RBAC）
4. **连接安全**: 使用加密连接（`Encrypt=yes`）
5. **敏感信息**: 不在日志中记录密码等敏感信息

### 配置管理

- 配置文件使用 INI 格式
- 敏感信息（密码）必须加密存储
- 提供配置模板文件（`app.ini.example`）
- 配置文件不应提交到版本控制系统

### 数据库连接示例

```python
# 正确的参数化查询
cursor.execute(
    "SELECT * FROM UserTable WHERE UserId = ? AND IsDeleted = ?",
    (user_id, False)
)

# 错误的字符串拼接（禁止使用）
# cursor.execute(f"SELECT * FROM UserTable WHERE UserId = {user_id}")
```

## Agent-Specific Notes

### 开发优先级

1. **数据库连接层** → **配置管理** → **核心 CRUD** → **UI 界面**
2. 每个模块完成后立即编写测试
3. 保持代码简洁，避免过度设计

### 代码审查检查点

- [ ] 是否使用参数化查询（防止 SQL 注入）
- [ ] 是否正确处理数据库连接异常
- [ ] 是否包含错误日志记录
- [ ] 是否符合 PEP 8 规范
- [ ] 是否有适当的类型提示
- [ ] 是否有文档字符串

### 快速开发原则

- 使用配置驱动开发，减少硬编码
- 复用通用组件和工具函数
- 优先实现 MVP（最小可行产品），后续迭代优化
- 保持模块化设计，便于后续迁移到 C#

### 常见问题

1. **数据库连接失败**: 检查 SQL Server 是否启用 TCP/IP 协议，防火墙端口是否开放
2. **编码问题**: 确保数据库连接字符串包含 `Charset=utf8` 或使用正确的编码
3. **性能问题**: 使用连接池，避免频繁创建和关闭连接
