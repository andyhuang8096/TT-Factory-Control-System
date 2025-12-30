using System;

namespace TT_PPID_CS.Domain.Entities
{
    public abstract class BaseEntity
    {
        public int Id { get; set; }
        public DateTime CreateTime { get; set; } = DateTime.Now;
        public DateTime UpdateTime { get; set; } = DateTime.Now;
        public string? CreateUser { get; set; }
        public string? UpdateUser { get; set; }
        public bool IsDeleted { get; set; } = false;
    }
}
