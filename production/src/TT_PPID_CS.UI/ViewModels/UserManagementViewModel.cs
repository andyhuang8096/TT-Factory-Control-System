using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using System.Collections.ObjectModel;
using System.Threading.Tasks;
using System.Windows;
using TT_PPID_CS.Application.DTOs;
using TT_PPID_CS.Application.Interfaces;
using TT_PPID_CS.UI.Views;
using System;

namespace TT_PPID_CS.UI.ViewModels
{
    public partial class UserManagementViewModel : ObservableObject
    {
        private readonly IUserService _userService;
        private readonly IAuthService _authService;

        [ObservableProperty]
        private ObservableCollection<UserDto> _users = new();

        [ObservableProperty]
        private UserDto? _selectedUser;

        [ObservableProperty]
        private bool _isBusy;

        public UserManagementViewModel(IUserService userService, IAuthService authService)
        {
            _userService = userService;
            _authService = authService;
            _ = LoadDataAsync();
        }

        [RelayCommand]
        private async Task LoadDataAsync()
        {
            IsBusy = true;
            try
            {
                var data = await _userService.GetAllAsync();
                Users = new ObservableCollection<UserDto>(data);
            }
            catch (Exception ex)
            {
                MessageBox.Show($"加载用户失败: {ex.Message}", "错误");
            }
            finally
            {
                IsBusy = false;
            }
        }

        [RelayCommand]
        private async Task AddAsync()
        {
            var vm = new UserViewModel();
            var dialog = new UserDialog(vm);
            dialog.Owner = Application.Current.MainWindow;

            if (dialog.ShowDialog() == true)
            {
                try
                {
                    await _userService.CreateAsync(vm.User, vm.Password, _authService.CurrentUser?.UserName);
                    await LoadDataAsync();
                    MessageBox.Show($"用户 {vm.User.UserName} 创建成功", "成功");
                }
                catch (Exception ex)
                {
                     MessageBox.Show($"创建失败: {ex.Message}", "错误");
                }
            }
        }

        [RelayCommand]
        private async Task EditAsync()
        {
            if (SelectedUser == null) 
            {
                MessageBox.Show("请先选择一个用户", "提示");
                return;
            }
            
            var vm = new UserViewModel(SelectedUser);
            var dialog = new UserDialog(vm);
            dialog.Owner = Application.Current.MainWindow;

            if (dialog.ShowDialog() == true)
            {
                try
                {
                    // 仅当提供了密码时才更新密码
                    string? password = string.IsNullOrEmpty(vm.Password) ? null : vm.Password;
                    await _userService.UpdateAsync(vm.User, password, _authService.CurrentUser?.UserName);
                    await LoadDataAsync();
                    MessageBox.Show("用户更新成功", "成功");
                }
                catch (Exception ex)
                {
                     MessageBox.Show($"更新失败: {ex.Message}", "错误");
                }
            }
        }

        [RelayCommand]
        private async Task DeleteAsync()
        {
            if (SelectedUser == null) 
            {
                MessageBox.Show("请先选择一个用户", "提示");
                return;
            }
            
            if (MessageBox.Show($"确定删除用户 {SelectedUser.UserName}?", "确认删除", MessageBoxButton.YesNo, MessageBoxImage.Warning) == MessageBoxResult.Yes)
            {
                try
                {
                    await _userService.DeleteAsync(SelectedUser.Id, _authService.CurrentUser?.UserName);
                    await LoadDataAsync();
                    MessageBox.Show("用户已删除", "成功");
                }
                catch (Exception ex)
                {
                    MessageBox.Show($"删除失败: {ex.Message}", "错误");
                }
            }
        }
    }
}
