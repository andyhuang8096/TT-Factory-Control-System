using System.Collections.Generic;
using System.Threading.Tasks;
using TT_PPID_CS.Application.DTOs;

namespace TT_PPID_CS.Application.Interfaces
{
    public interface IUserService
    {
        Task<IEnumerable<UserDto>> GetAllAsync();
        Task<UserDto?> GetByIdAsync(int id);
        Task<UserDto?> GetByUsernameAsync(string username);
        Task CreateAsync(UserDto dto, string password, string? creator = null);
        Task UpdateAsync(UserDto dto, string? password = null, string? modifier = null);
        Task DeleteAsync(int id, string? modifier = null);
        Task<bool> ChangePasswordAsync(int userId, string oldPassword, string newPassword);
    }
}
