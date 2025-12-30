using System;

namespace TT_PPID_CS.Application.DTOs
{
    public class UserDto
    {
        public int Id { get; set; }
        public string UserName { get; set; } = string.Empty;
        public string? Email { get; set; }
        public string? FullName { get; set; }
        public string Role { get; set; } = "user";
        public bool IsActive { get; set; }
        public DateTime? LastLoginTime { get; set; }
    }
}
