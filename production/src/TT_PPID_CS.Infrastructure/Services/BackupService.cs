using Microsoft.Data.SqlClient;
using Microsoft.EntityFrameworkCore;
using System;
using System.IO;
using System.Threading.Tasks;
using TT_PPID_CS.Application.Interfaces;
using TT_PPID_CS.Domain.Entities;
using TT_PPID_CS.Domain.Interfaces;
using TT_PPID_CS.Infrastructure.Persistence;

namespace TT_PPID_CS.Infrastructure.Services
{
    public class BackupService : IBackupService
    {
        private readonly AppDbContext _context;
        private readonly IUnitOfWork _unitOfWork;
        // In a real app, retrieve from IConfiguration
        private readonly string _connectionString = "Server=192.168.30.254,1433;Database=PPID_DB;User Id=TGUser;Password=Ydse%32gr7e#;Encrypt=True;TrustServerCertificate=True;";

        public BackupService(AppDbContext context, IUnitOfWork unitOfWork)
        {
            _context = context;
            _unitOfWork = unitOfWork;
        }

        public async Task<(bool success, string message)> BackupDatabaseAsync(string backupPath, string? user = null)
        {
            try
            {
                // Ensure directory exists
                var directory = Path.GetDirectoryName(backupPath);
                if (!string.IsNullOrEmpty(directory) && !Directory.Exists(directory))
                {
                    Directory.CreateDirectory(directory);
                }

                // Get DB Name
                var builder = new SqlConnectionStringBuilder(_connectionString);
                string dbName = builder.InitialCatalog;

                string sql = $"BACKUP DATABASE [{dbName}] TO DISK = @path WITH FORMAT, INIT, NAME = @name";
                
                await _context.Database.ExecuteSqlRawAsync(sql, 
                    new SqlParameter("@path", backupPath),
                    new SqlParameter("@name", $"{dbName}-Full Database Backup"));

                // Log success
                await _unitOfWork.BackupLogs.AddAsync(new BackupLog
                {
                    BackupFileName = Path.GetFileName(backupPath),
                    BackupPath = backupPath,
                    DatabaseName = dbName,
                    Status = "completed",
                    CreateUser = user,
                    UpdateUser = user,
                    StartTime = DateTime.Now,
                    EndTime = DateTime.Now,
                    FileSize = new FileInfo(backupPath).Length
                });
                await _unitOfWork.CompleteAsync();

                return (true, "备份成功");
            }
            catch (Exception ex)
            {
                return (false, $"备份失败: {ex.Message}");
            }
        }

        public async Task<(bool success, string message)> RestoreDatabaseAsync(string backupPath)
        {
            if (!File.Exists(backupPath))
            {
                return (false, "备份文件不存在");
            }

            try
            {
                var builder = new SqlConnectionStringBuilder(_connectionString);
                string dbName = builder.InitialCatalog;

                // Create connection to MASTER
                builder.InitialCatalog = "master";
                
                using (var connection = new SqlConnection(builder.ConnectionString))
                {
                    await connection.OpenAsync();

                    // Step 1: Set Single User to kill connections
                    string setSingleUserSql = $"ALTER DATABASE [{dbName}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE";
                    using (var cmd = new SqlCommand(setSingleUserSql, connection))
                    {
                        try { await cmd.ExecuteNonQueryAsync(); } catch { /* Ignore if DB doesn't exist */ }
                    }

                    // Step 2: Restore
                    string restoreSql = $"RESTORE DATABASE [{dbName}] FROM DISK = @path WITH REPLACE";
                    using (var cmd = new SqlCommand(restoreSql, connection))
                    {
                        cmd.Parameters.AddWithValue("@path", backupPath);
                        await cmd.ExecuteNonQueryAsync();
                    }

                    // Step 3: Set Multi User
                    string setMultiUserSql = $"ALTER DATABASE [{dbName}] SET MULTI_USER";
                    using (var cmd = new SqlCommand(setMultiUserSql, connection))
                    {
                        await cmd.ExecuteNonQueryAsync();
                    }
                }

                return (true, "恢复成功");
            }
            catch (Exception ex)
            {
                return (false, $"恢复失败: {ex.Message}");
            }
        }
    }
}
