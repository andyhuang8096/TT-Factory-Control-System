using CommunityToolkit.Mvvm.ComponentModel;
using System.Collections.Generic;
using TT_PPID_CS.Application.DTOs;

namespace TT_PPID_CS.UI.ViewModels
{
    public partial class UserViewModel : ObservableObject
    {
        [ObservableProperty]
        private string _title = "添加用户";

        [ObservableProperty]
        private UserDto _user;

        [ObservableProperty]
        private string _password = string.Empty;

        [ObservableProperty]
        private string _confirmPassword = string.Empty;

        public bool IsEditMode { get; private set; }

        public List<string> Roles { get; } = new List<string> { "admin", "user", "viewer" };

        public UserViewModel(UserDto? user = null)
        {
            if (user != null)
            {
                Title = "编辑用户";
                IsEditMode = true;
                User = new UserDto
                {
                    Id = user.Id,
                    UserName = user.UserName,
                    Email = user.Email,
                    FullName = user.FullName,
                    Role = user.Role,
                    IsActive = user.IsActive
                };
            }
            else
            {
                User = new UserDto { IsActive = true, Role = "user" };
            }
        }
    }
}
