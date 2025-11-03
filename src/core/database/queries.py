"""数据库表结构定义 SQL。

包含创建表的 SQL 语句。
"""

# 用户表
CREATE_USER_TABLE = """
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[UserTable]') AND type in (N'U'))
BEGIN
    CREATE TABLE UserTable (
        Id INT PRIMARY KEY IDENTITY(1,1),
        UserName NVARCHAR(50) NOT NULL UNIQUE,
        Password NVARCHAR(255) NOT NULL,
        Email NVARCHAR(100),
        FullName NVARCHAR(100),
        Role NVARCHAR(20) NOT NULL DEFAULT 'user',
        IsActive BIT NOT NULL DEFAULT 1,
        LastLoginTime DATETIME,
        CreateTime DATETIME NOT NULL DEFAULT GETDATE(),
        UpdateTime DATETIME NOT NULL DEFAULT GETDATE(),
        CreateUser NVARCHAR(50),
        UpdateUser NVARCHAR(50),
        IsDeleted BIT NOT NULL DEFAULT 0
    );
    
    CREATE INDEX IX_UserTable_UserName ON UserTable(UserName);
    CREATE INDEX IX_UserTable_Role ON UserTable(Role);
END
"""

# PPID 记录表
CREATE_PPID_RECORD_TABLE = """
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[PPIDRecord]') AND type in (N'U'))
BEGIN
    CREATE TABLE PPIDRecord (
        Id INT PRIMARY KEY IDENTITY(1,1),
        PPID NVARCHAR(100) NOT NULL,
        SerialNumber NVARCHAR(100),
        Model NVARCHAR(50),
        PN NVARCHAR(50),
        Status NVARCHAR(20) NOT NULL DEFAULT 'available',
        InUseDays INT NOT NULL DEFAULT 0,
        CorruptedAttempts INT NOT NULL DEFAULT 0,
        LastUsedTime DATETIME,
        Notes NVARCHAR(MAX),
        CreateTime DATETIME NOT NULL DEFAULT GETDATE(),
        UpdateTime DATETIME NOT NULL DEFAULT GETDATE(),
        CreateUser NVARCHAR(50),
        UpdateUser NVARCHAR(50),
        IsDeleted BIT NOT NULL DEFAULT 0
    );
    
    CREATE INDEX IX_PPIDRecord_PPID ON PPIDRecord(PPID);
    CREATE INDEX IX_PPIDRecord_Status ON PPIDRecord(Status);
    CREATE INDEX IX_PPIDRecord_Model ON PPIDRecord(Model);
END
"""

# 导入日志表
CREATE_IMPORT_LOG_TABLE = """
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[ImportLog]') AND type in (N'U'))
BEGIN
    CREATE TABLE ImportLog (
        Id INT PRIMARY KEY IDENTITY(1,1),
        FileName NVARCHAR(255) NOT NULL,
        FilePath NVARCHAR(500) NOT NULL,
        ImportType NVARCHAR(20) NOT NULL DEFAULT 'csv',
        TotalRows INT NOT NULL DEFAULT 0,
        SuccessRows INT NOT NULL DEFAULT 0,
        FailedRows INT NOT NULL DEFAULT 0,
        Status NVARCHAR(20) NOT NULL DEFAULT 'pending',
        ErrorMessage NVARCHAR(MAX),
        StartTime DATETIME,
        EndTime DATETIME,
        CreateTime DATETIME NOT NULL DEFAULT GETDATE(),
        UpdateTime DATETIME NOT NULL DEFAULT GETDATE(),
        CreateUser NVARCHAR(50),
        UpdateUser NVARCHAR(50),
        IsDeleted BIT NOT NULL DEFAULT 0
    );
    
    CREATE INDEX IX_ImportLog_Status ON ImportLog(Status);
    CREATE INDEX IX_ImportLog_CreateTime ON ImportLog(CreateTime);
END
"""

# 备份日志表
CREATE_BACKUP_LOG_TABLE = """
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[BackupLog]') AND type in (N'U'))
BEGIN
    CREATE TABLE BackupLog (
        Id INT PRIMARY KEY IDENTITY(1,1),
        BackupFileName NVARCHAR(255) NOT NULL,
        BackupPath NVARCHAR(500) NOT NULL,
        BackupType NVARCHAR(20) NOT NULL DEFAULT 'full',
        DatabaseName NVARCHAR(100) NOT NULL,
        FileSize BIGINT NOT NULL DEFAULT 0,
        Status NVARCHAR(20) NOT NULL DEFAULT 'pending',
        ErrorMessage NVARCHAR(MAX),
        StartTime DATETIME,
        EndTime DATETIME,
        CreateTime DATETIME NOT NULL DEFAULT GETDATE(),
        UpdateTime DATETIME NOT NULL DEFAULT GETDATE(),
        CreateUser NVARCHAR(50),
        UpdateUser NVARCHAR(50),
        IsDeleted BIT NOT NULL DEFAULT 0
    );
    
    CREATE INDEX IX_BackupLog_Status ON BackupLog(Status);
    CREATE INDEX IX_BackupLog_CreateTime ON BackupLog(CreateTime);
END
"""

# 审计日志表
CREATE_AUDIT_LOG_TABLE = """
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[AuditLog]') AND type in (N'U'))
BEGIN
    CREATE TABLE AuditLog (
        Id INT PRIMARY KEY IDENTITY(1,1),
        UserName NVARCHAR(50) NOT NULL,
        Action NVARCHAR(50) NOT NULL,
        TableName NVARCHAR(100),
        RecordId INT,
        Description NVARCHAR(MAX),
        IPAddress NVARCHAR(50),
        ActionTime DATETIME NOT NULL DEFAULT GETDATE(),
        CreateTime DATETIME NOT NULL DEFAULT GETDATE(),
        UpdateTime DATETIME NOT NULL DEFAULT GETDATE(),
        CreateUser NVARCHAR(50),
        UpdateUser NVARCHAR(50),
        IsDeleted BIT NOT NULL DEFAULT 0
    );
    
    CREATE INDEX IX_AuditLog_UserName ON AuditLog(UserName);
    CREATE INDEX IX_AuditLog_Action ON AuditLog(Action);
    CREATE INDEX IX_AuditLog_ActionTime ON AuditLog(ActionTime);
END
"""

# 所有创建表的 SQL 语句
CREATE_TABLES = [
    CREATE_USER_TABLE,
    CREATE_PPID_RECORD_TABLE,
    CREATE_IMPORT_LOG_TABLE,
    CREATE_BACKUP_LOG_TABLE,
    CREATE_AUDIT_LOG_TABLE
]

