using System;
using System.Threading.Tasks;
using TT_PPID_CS.Domain.Entities;
using TT_PPID_CS.Domain.Interfaces;
using TT_PPID_CS.Infrastructure.Repositories;

namespace TT_PPID_CS.Infrastructure.Persistence
{
    public class UnitOfWork : IUnitOfWork
    {
        private readonly AppDbContext _context;

        public UnitOfWork(AppDbContext context)
        {
            _context = context;
            Users = new Repository<UserTable>(_context);
            PPIDRecords = new Repository<PPIDRecord>(_context);
            ImportLogs = new Repository<ImportLog>(_context);
            BackupLogs = new Repository<BackupLog>(_context);
            AuditLogs = new Repository<AuditLog>(_context);
        }

        public IRepository<UserTable> Users { get; private set; }
        public IRepository<PPIDRecord> PPIDRecords { get; private set; }
        public IRepository<ImportLog> ImportLogs { get; private set; }
        public IRepository<BackupLog> BackupLogs { get; private set; }
        public IRepository<AuditLog> AuditLogs { get; private set; }

        public async Task<int> CompleteAsync()
        {
            return await _context.SaveChangesAsync();
        }

        public void Dispose()
        {
            _context.Dispose();
        }
    }
}
