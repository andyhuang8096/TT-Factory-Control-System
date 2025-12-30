using System;

namespace TT_PPID_CS.Domain.Entities
{
    public class ImportLog : BaseEntity
    {
        public string FileName { get; set; } = string.Empty;
        public string FilePath { get; set; } = string.Empty;
        public string ImportType { get; set; } = "csv";
        public int TotalRows { get; set; } = 0;
        public int SuccessRows { get; set; } = 0;
        public int FailedRows { get; set; } = 0;
        public string Status { get; set; } = "pending";
        public string? ErrorMessage { get; set; }
        public DateTime? StartTime { get; set; }
        public DateTime? EndTime { get; set; }
    }
}
