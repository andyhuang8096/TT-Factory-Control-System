using System;

namespace TT_PPID_CS.Application.DTOs
{
    public class PPIDRecordDto
    {
        public int Id { get; set; }
        public string PPID { get; set; } = string.Empty;
        public string? SerialNumber { get; set; }
        public string? Model { get; set; }
        public string? PN { get; set; }
        public string Status { get; set; } = "available";
        public int InUseDays { get; set; }
        public int CorruptedAttempts { get; set; }
        public DateTime? LastUsedTime { get; set; }
        public string? Notes { get; set; }
        public DateTime CreateTime { get; set; }
        public string? CreateUser { get; set; }
        public DateTime UpdateTime { get; set; }
        public string? UpdateUser { get; set; }
    }
}
