using System;
using System.Threading.Tasks;
using TT_PPID_CS.Domain.Entities;

namespace TT_PPID_CS.Domain.Interfaces
{
    public interface IUnitOfWork : IDisposable
    {
        IRepository<UserTable> Users { get; }
        IRepository<PPIDRecord> PPIDRecords { get; }
        IRepository<ImportLog> ImportLogs { get; }
        IRepository<BackupLog> BackupLogs { get; }
        IRepository<AuditLog> AuditLogs { get; }
        Task<int> CompleteAsync();
    }
}
