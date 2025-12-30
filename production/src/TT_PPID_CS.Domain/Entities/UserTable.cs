using System;

namespace TT_PPID_CS.Domain.Entities
{
    public class UserTable : BaseEntity
    {
        public string UserName { get; set; } = string.Empty;
        public string Password { get; set; } = string.Empty;
        public string? Email { get; set; }
        public string? FullName { get; set; }
        public string Role { get; set; } = "user";
        public bool IsActive { get; set; } = true;
        public DateTime? LastLoginTime { get; set; }
    }
}
