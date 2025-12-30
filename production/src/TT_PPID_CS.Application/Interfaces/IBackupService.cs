using System.Threading.Tasks;

namespace TT_PPID_CS.Application.Interfaces
{
    public interface IBackupService
    {
        Task<(bool success, string message)> BackupDatabaseAsync(string backupPath, string? user = null);
        Task<(bool success, string message)> RestoreDatabaseAsync(string backupPath);
    }
}
