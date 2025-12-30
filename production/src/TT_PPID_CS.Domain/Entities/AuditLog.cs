using System;

namespace TT_PPID_CS.Domain.Entities
{
    public class AuditLog : BaseEntity
    {
        public string UserName { get; set; } = string.Empty;
        public string Action { get; set; } = string.Empty;
        public string? TableName { get; set; }
        public int? RecordId { get; set; }
        public string? Description { get; set; }
        public string? IPAddress { get; set; }
        public DateTime ActionTime { get; set; } = DateTime.Now;
    }
}
