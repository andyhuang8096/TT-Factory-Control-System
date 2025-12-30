using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using TT_PPID_CS.Application.DTOs;
using TT_PPID_CS.Application.Interfaces;
using TT_PPID_CS.Application.Utils;
using TT_PPID_CS.Domain.Entities;
using TT_PPID_CS.Domain.Interfaces;

namespace TT_PPID_CS.Application.Services
{
    public class UserService : IUserService
    {
        private readonly IUnitOfWork _unitOfWork;

        public UserService(IUnitOfWork unitOfWork)
        {
            _unitOfWork = unitOfWork;
        }

        public async Task<IEnumerable<UserDto>> GetAllAsync()
        {
            var users = await _unitOfWork.Users.GetAllAsync();
            return users.Select(MapToDto).ToList();
        }

        public async Task<UserDto?> GetByIdAsync(int id)
        {
            var user = await _unitOfWork.Users.GetByIdAsync(id);
            return user == null ? null : MapToDto(user);
        }

        public async Task<UserDto?> GetByUsernameAsync(string username)
        {
            var users = await _unitOfWork.Users.FindAsync(u => u.UserName == username);
            var user = users.FirstOrDefault();
            return user == null ? null : MapToDto(user);
        }

        public async Task CreateAsync(UserDto dto, string password, string? creator = null)
        {
            // Check existence
            if ((await _unitOfWork.Users.FindAsync(u => u.UserName == dto.UserName)).Any())
            {
                throw new InvalidOperationException($"用户 {dto.UserName} 已存在");
            }

            var user = new UserTable
            {
                UserName = dto.UserName,
                // Hash Password
                Password = PasswordHasher.HashPassword(password, out _),
                Email = dto.Email,
                FullName = dto.FullName,
                Role = dto.Role ?? "user",
                IsActive = dto.IsActive,
                CreateUser = creator,
                UpdateUser = creator
            };

            await _unitOfWork.Users.AddAsync(user);
            await _unitOfWork.CompleteAsync();

            await _unitOfWork.AuditLogs.AddAsync(new AuditLog
            {
                UserName = creator ?? "system",
                Action = "CREATE_USER",
                Description = $"Created user: {user.UserName}"
            });
            await _unitOfWork.CompleteAsync();
        }

        public async Task UpdateAsync(UserDto dto, string? password = null, string? modifier = null)
        {
            var user = await _unitOfWork.Users.GetByIdAsync(dto.Id);
            if (user == null) throw new InvalidOperationException("用户不存在");

            user.Email = dto.Email;
            user.FullName = dto.FullName;
            user.Role = dto.Role;
            user.IsActive = dto.IsActive;
            user.UpdateUser = modifier;

            if (!string.IsNullOrEmpty(password))
            {
                user.Password = PasswordHasher.HashPassword(password, out _);
            }

            await _unitOfWork.Users.UpdateAsync(user);
            await _unitOfWork.CompleteAsync();

            await _unitOfWork.AuditLogs.AddAsync(new AuditLog
            {
                UserName = modifier ?? "system",
                Action = "UPDATE_USER",
                RecordId = user.Id,
                Description = $"Updated user: {user.UserName}"
            });
            await _unitOfWork.CompleteAsync();
        }

        public async Task DeleteAsync(int id, string? modifier = null)
        {
            await _unitOfWork.Users.SoftDeleteAsync(id, modifier);
            await _unitOfWork.CompleteAsync();

            await _unitOfWork.AuditLogs.AddAsync(new AuditLog
            {
                UserName = modifier ?? "system",
                Action = "DELETE_USER",
                RecordId = id,
                Description = "Soft deleted user"
            });
            await _unitOfWork.CompleteAsync();
        }

        public async Task<bool> ChangePasswordAsync(int userId, string oldPassword, string newPassword)
        {
            var user = await _unitOfWork.Users.GetByIdAsync(userId);
            if (user == null) return false;

            if (!PasswordHasher.VerifyPassword(oldPassword, user.Password))
            {
                return false;
            }

            user.Password = PasswordHasher.HashPassword(newPassword, out _);
            await _unitOfWork.Users.UpdateAsync(user);
            await _unitOfWork.CompleteAsync();

            return true;
        }

        private static UserDto MapToDto(UserTable user)
        {
            return new UserDto
            {
                Id = user.Id,
                UserName = user.UserName,
                Email = user.Email,
                FullName = user.FullName,
                Role = user.Role,
                IsActive = user.IsActive,
                LastLoginTime = user.LastLoginTime
            };
        }
    }
}
