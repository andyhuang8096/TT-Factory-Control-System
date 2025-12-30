using System.Threading.Tasks;
using TT_PPID_CS.Application.DTOs;

namespace TT_PPID_CS.Application.Interfaces
{
    public interface IAuthService
    {
        Task<UserDto?> LoginAsync(string username, string password);
        Task LogoutAsync();
        bool IsAuthenticated { get; }
        UserDto? CurrentUser { get; }
    }
}
