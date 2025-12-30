using System;

namespace TT_PPID_CS.Domain.Entities
{
    public class PPIDRecord : BaseEntity
    {
        public string PPID { get; set; } = string.Empty;
        public string? SerialNumber { get; set; }
        public string? Model { get; set; }
        public string? PN { get; set; }
        public string Status { get; set; } = "available";
        public int InUseDays { get; set; } = 0;
        public int CorruptedAttempts { get; set; } = 0;
        public DateTime? LastUsedTime { get; set; }
        public string? Notes { get; set; }
    }
}
