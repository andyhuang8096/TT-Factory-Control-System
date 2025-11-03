-- 数据库迁移脚本：将 DPKRecord 表重命名为 PPIDRecord
-- 执行此脚本前请先备份数据库！

-- 检查 DPKRecord 表是否存在
IF EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[DPKRecord]') AND type in (N'U'))
BEGIN
    -- 检查 PPIDRecord 表是否已存在
    IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[PPIDRecord]') AND type in (N'U'))
    BEGIN
        -- 重命名表
        EXEC sp_rename 'DPKRecord', 'PPIDRecord';
        
        -- 重命名索引
        IF EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_DPKRecord_PPID' AND object_id = OBJECT_ID('PPIDRecord'))
            EXEC sp_rename 'PPIDRecord.IX_DPKRecord_PPID', 'IX_PPIDRecord_PPID', 'INDEX';
            
        IF EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_DPKRecord_Status' AND object_id = OBJECT_ID('PPIDRecord'))
            EXEC sp_rename 'PPIDRecord.IX_DPKRecord_Status', 'IX_PPIDRecord_Status', 'INDEX';
            
        IF EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_DPKRecord_Model' AND object_id = OBJECT_ID('PPIDRecord'))
            EXEC sp_rename 'PPIDRecord.IX_DPKRecord_Model', 'IX_PPIDRecord_Model', 'INDEX';
        
        PRINT '表 DPKRecord 已成功重命名为 PPIDRecord';
    END
    ELSE
    BEGIN
        PRINT '警告: PPIDRecord 表已存在，无法重命名。如果需要迁移数据，请手动处理。';
    END
END
ELSE
BEGIN
    PRINT 'DPKRecord 表不存在，无需迁移。';
END

