using Microsoft.EntityFrameworkCore;
using TT_PPID_CS.Domain.Entities;

namespace TT_PPID_CS.Infrastructure.Persistence
{
    public class AppDbContext : DbContext
    {
        public AppDbContext(DbContextOptions<AppDbContext> options) : base(options)
        {
        }

        public DbSet<UserTable> Users { get; set; }
        public DbSet<PPIDRecord> PPIDRecords { get; set; }
        public DbSet<ImportLog> ImportLogs { get; set; }
        public DbSet<BackupLog> BackupLogs { get; set; }
        public DbSet<AuditLog> AuditLogs { get; set; }

        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
            base.OnModelCreating(modelBuilder);

            // Configure UserTable
            modelBuilder.Entity<UserTable>(entity =>
            {
                entity.ToTable("UserTable");
                entity.HasIndex(e => e.UserName).IsUnique();
                entity.Property(e => e.Role).HasDefaultValue("user");
                entity.Property(e => e.IsActive).HasDefaultValue(true);
                entity.Property(e => e.CreateTime).HasDefaultValueSql("GETDATE()");
                entity.Property(e => e.UpdateTime).HasDefaultValueSql("GETDATE()");
                entity.Property(e => e.IsDeleted).HasDefaultValue(false);
            });

            // Configure PPIDRecord
            modelBuilder.Entity<PPIDRecord>(entity =>
            {
                entity.ToTable("PPIDRecord");
                entity.HasIndex(e => e.PPID);
                entity.HasIndex(e => e.Status);
                entity.HasIndex(e => e.Model);
                entity.Property(e => e.Status).HasDefaultValue("available");
                entity.Property(e => e.CreateTime).HasDefaultValueSql("GETDATE()");
                entity.Property(e => e.UpdateTime).HasDefaultValueSql("GETDATE()");
                entity.Property(e => e.IsDeleted).HasDefaultValue(false);
            });

            // Configure ImportLog
            modelBuilder.Entity<ImportLog>(entity =>
            {
                entity.ToTable("ImportLog");
                entity.HasIndex(e => e.Status);
                entity.HasIndex(e => e.CreateTime);
                entity.Property(e => e.ImportType).HasDefaultValue("csv");
                entity.Property(e => e.Status).HasDefaultValue("pending");
                entity.Property(e => e.CreateTime).HasDefaultValueSql("GETDATE()");
                entity.Property(e => e.UpdateTime).HasDefaultValueSql("GETDATE()");
            });

            // Configure BackupLog
            modelBuilder.Entity<BackupLog>(entity =>
            {
                entity.ToTable("BackupLog");
                entity.HasIndex(e => e.Status);
                entity.HasIndex(e => e.CreateTime);
                entity.Property(e => e.BackupType).HasDefaultValue("full");
                entity.Property(e => e.Status).HasDefaultValue("pending");
                entity.Property(e => e.CreateTime).HasDefaultValueSql("GETDATE()");
                entity.Property(e => e.UpdateTime).HasDefaultValueSql("GETDATE()");
            });

            // Configure AuditLog
            modelBuilder.Entity<AuditLog>(entity =>
            {
                entity.ToTable("AuditLog");
                entity.HasIndex(e => e.UserName);
                entity.HasIndex(e => e.Action);
                entity.HasIndex(e => e.ActionTime);
                entity.Property(e => e.ActionTime).HasDefaultValueSql("GETDATE()");
                entity.Property(e => e.CreateTime).HasDefaultValueSql("GETDATE()");
                entity.Property(e => e.UpdateTime).HasDefaultValueSql("GETDATE()");
            });
        }
    }
}
