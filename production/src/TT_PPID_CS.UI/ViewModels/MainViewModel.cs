using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using System;
using Microsoft.Extensions.DependencyInjection;
using TT_PPID_CS.Application.Interfaces;
using TT_PPID_CS.Application.DTOs;

namespace TT_PPID_CS.UI.ViewModels
{
    public partial class MainViewModel : ObservableObject
    {
        private readonly IAuthService _authService;
        private readonly IServiceProvider _serviceProvider;

        [ObservableProperty]
        private UserDto? _currentUser;

        [ObservableProperty]
        private object? _currentView;

        public MainViewModel(IAuthService authService, IServiceProvider serviceProvider)
        {
            _authService = authService;
            _serviceProvider = serviceProvider;
            CurrentUser = _authService.CurrentUser;
            
            // 默认显示 PPID 管理界面
            SwitchToPPIDView();
        }

        [RelayCommand]
        private void SwitchToPPIDView()
        {
            // 使用完全限定名以避免命名空间冲突
            CurrentView = _serviceProvider.GetRequiredService<TT_PPID_CS.UI.Views.PPIDManagementView>();
        }
    }
}
