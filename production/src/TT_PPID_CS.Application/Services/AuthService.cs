using System;
using System.Linq;
using System.Threading.Tasks;
using TT_PPID_CS.Application.DTOs;
using TT_PPID_CS.Application.Interfaces;
using TT_PPID_CS.Application.Utils;
using TT_PPID_CS.Domain.Interfaces;

namespace TT_PPID_CS.Application.Services
{
    public class AuthService : IAuthService
    {
        private readonly IUnitOfWork _unitOfWork;
        public UserDto? CurrentUser { get; private set; }
        public bool IsAuthenticated => CurrentUser != null;

        public AuthService(IUnitOfWork unitOfWork)
        {
            _unitOfWork = unitOfWork;
        }

        public async Task<UserDto?> LoginAsync(string username, string password)
        {
            var users = await _unitOfWork.Users.FindAsync(u => u.UserName == username && u.IsActive);
            var user = users.FirstOrDefault();

            if (user == null || !PasswordHasher.VerifyPassword(password, user.Password))
            {
                return null;
            }

            user.LastLoginTime = DateTime.Now;
            await _unitOfWork.Users.UpdateAsync(user);
            await _unitOfWork.CompleteAsync();

            CurrentUser = new UserDto
            {
                Id = user.Id,
                UserName = user.UserName,
                Email = user.Email,
                FullName = user.FullName,
                Role = user.Role,
                IsActive = user.IsActive,
                LastLoginTime = user.LastLoginTime
            };

            return CurrentUser;
        }

        public Task LogoutAsync()
        {
            CurrentUser = null;
            return Task.CompletedTask;
        }
    }
}
