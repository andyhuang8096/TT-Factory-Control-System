using System;

namespace TT_PPID_CS.Domain.Entities
{
    public class BackupLog : BaseEntity
    {
        public string BackupFileName { get; set; } = string.Empty;
        public string BackupPath { get; set; } = string.Empty;
        public string BackupType { get; set; } = "full";
        public string DatabaseName { get; set; } = string.Empty;
        public long FileSize { get; set; } = 0;
        public string Status { get; set; } = "pending";
        public string? ErrorMessage { get; set; }
        public DateTime? StartTime { get; set; }
        public DateTime? EndTime { get; set; }
    }
}
