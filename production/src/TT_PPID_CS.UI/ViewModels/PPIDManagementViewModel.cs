using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using System.Collections.ObjectModel;
using System.Threading.Tasks;
using System.Windows;
using TT_PPID_CS.Application.DTOs;
using TT_PPID_CS.Application.Interfaces;

namespace TT_PPID_CS.UI.ViewModels
{
    public partial class PPIDManagementViewModel : ObservableObject
    {
        private readonly IPPIDService _ppidService;
        private readonly IAuthService _authService;

        [ObservableProperty]
        private ObservableCollection<PPIDRecordDto> _pPIDRecords = new();

        [ObservableProperty]
        private PPIDRecordDto? _selectedRecord;

        [ObservableProperty]
        private string _searchText = string.Empty;

        [ObservableProperty]
        private string _selectedSearchField = "PPID";

        [ObservableProperty]
        private bool _isBusy;

        public string[] SearchFields { get; } = new[] { "PPID", "SerialNumber", "Model", "PN", "Status" };

        public PPIDManagementViewModel(IPPIDService ppidService, IAuthService authService)
        {
            _ppidService = ppidService;
            _authService = authService;
            // LoadDataAsync(); // 可以在构造函数调用，也可以在 View Loaded 事件调用，这里简单起见放在构造函数
             _ = LoadDataAsync();
        }

        [RelayCommand]
        private async Task LoadDataAsync()
        {
            IsBusy = true;
            try
            {
                var data = await _ppidService.GetAllAsync();
                PPIDRecords = new ObservableCollection<PPIDRecordDto>(data);
            }
            catch (System.Exception ex)
            {
                MessageBox.Show($"加载数据失败: {ex.Message}", "错误", MessageBoxButton.OK, MessageBoxImage.Error);
            }
            finally
            {
                IsBusy = false;
            }
        }

        [RelayCommand]
        private async Task SearchAsync()
        {
            IsBusy = true;
            try
            {
                var data = await _ppidService.SearchAsync(SelectedSearchField, SearchText);
                PPIDRecords = new ObservableCollection<PPIDRecordDto>(data);
            }
            catch (System.Exception ex)
            {
                MessageBox.Show($"搜索失败: {ex.Message}", "错误", MessageBoxButton.OK, MessageBoxImage.Error);
            }
            finally
            {
                IsBusy = false;
            }
        }

        [RelayCommand]
        private async Task DeleteAsync()
        {
            if (SelectedRecord == null)
            {
                MessageBox.Show("请先选择一条记录", "提示", MessageBoxButton.OK, MessageBoxImage.Information);
                return;
            }

            var result = MessageBox.Show($"确定要删除 PPID: {SelectedRecord.PPID} 吗?\n(此操作为软删除)", 
                                       "确认删除", MessageBoxButton.YesNo, MessageBoxImage.Warning);
                                       
            if (result == MessageBoxResult.Yes)
            {
                try
                {
                    await _ppidService.DeleteAsync(SelectedRecord.Id, _authService.CurrentUser?.UserName);
                    await LoadDataAsync(); // 刷新列表
                    MessageBox.Show("记录已删除", "成功", MessageBoxButton.OK, MessageBoxImage.Information);
                }
                catch (System.Exception ex)
                {
                    MessageBox.Show($"删除失败: {ex.Message}", "错误", MessageBoxButton.OK, MessageBoxImage.Error);
                }
            }
        }
        
        // Add command placeholder
        [RelayCommand]
        private void Add()
        {
            MessageBox.Show("添加功能将在下一步实现", "提示");
        }

        // Edit command placeholder
        [RelayCommand]
        private void Edit()
        {
             if (SelectedRecord == null)
            {
                MessageBox.Show("请先选择一条记录", "提示");
                return;
            }
            MessageBox.Show($"编辑功能将在下一步实现 (ID: {SelectedRecord.Id})", "提示");
        }
    }
}
