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

        [ObservableProperty]
        private string _selectedMenu = "PPID";

        partial void OnSelectedMenuChanged(string value)
        {
            switch (value)
            {
                case "PPID":
                    SwitchToPPIDView();
                    break;
                case "User":
                    SwitchToUserView();
                    break;
                case "Audit":
                    SwitchToStatisticsView();
                    break;
            }
        }

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

        [RelayCommand]
        private void SwitchToUserView()
        {
            CurrentView = _serviceProvider.GetRequiredService<TT_PPID_CS.UI.Views.UserManagementView>();
        }

        [RelayCommand]
        private void SwitchToStatisticsView()
        {
            CurrentView = _serviceProvider.GetRequiredService<TT_PPID_CS.UI.Views.StatisticsView>();
        }

        [RelayCommand]
        private async Task ImportAsync()
        {
            var dialog = new Microsoft.Win32.OpenFileDialog
            {
                Filter = "Data Files|*.csv;*.xlsx;*.xls;*.json|CSV Files|*.csv|Excel Files|*.xlsx;*.xls|JSON Files|*.json",
                Title = "导入数据"
            };

            if (dialog.ShowDialog() == true)
            {
                try 
                {
                    var importService = _serviceProvider.GetRequiredService<IImportService>();
                    var result = await importService.ImportPPIDRecordsAsync(dialog.FileName, CurrentUser?.UserName);
                    
                    System.Windows.MessageBox.Show($"{result.message}\n总计: {result.total}\n成功: {result.success}\n失败: {result.failed}", 
                                                   "导入结果", System.Windows.MessageBoxButton.OK, System.Windows.MessageBoxImage.Information);
                    
                    // 刷新视图
                    SwitchToPPIDView();
                }
                catch (Exception ex)
                {
                    System.Windows.MessageBox.Show($"导入失败: {ex.Message}", "错误", System.Windows.MessageBoxButton.OK, System.Windows.MessageBoxImage.Error);
                }
            }
        }

        [RelayCommand]
        private async Task BackupAsync()
        {
            var dialog = new Microsoft.Win32.SaveFileDialog
            {
                Filter = "SQL Server Backup|*.bak",
                FileName = $"PPID_DB_Backup_{DateTime.Now:yyyyMMdd_HHmmss}.bak",
                Title = "备份数据库"
            };

            if (dialog.ShowDialog() == true)
            {
                try
                {
                    var backupService = _serviceProvider.GetRequiredService<IBackupService>();
                    // 请注意: SQL Server 备份路径是相对于 SQL Server 服务进程的。
                    // 如果 SQL Server 在远程机器，本地路径将无效。
                    // 假设这是本地开发或者共享路径有效。如果远程 SQL，需保存到远程路径。
                    // 此处通过 EF Core 执行 SQL，路径被传递给 Server。
                    
                    var result = await backupService.BackupDatabaseAsync(dialog.FileName, CurrentUser?.UserName);
                    
                    if (result.success)
                         System.Windows.MessageBox.Show(result.message, "成功", System.Windows.MessageBoxButton.OK, System.Windows.MessageBoxImage.Information);
                    else
                         System.Windows.MessageBox.Show(result.message, "错误", System.Windows.MessageBoxButton.OK, System.Windows.MessageBoxImage.Error);
                }
                catch (Exception ex)
                {
                     System.Windows.MessageBox.Show($"备份出错: {ex.Message}", "错误");
                }
            }
        }
    }
}
