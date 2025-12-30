using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using System.Threading.Tasks;
using TT_PPID_CS.Application.DTOs;
using TT_PPID_CS.Application.Interfaces;

namespace TT_PPID_CS.UI.ViewModels
{
    public partial class StatisticsViewModel : ObservableObject
    {
        private readonly IReportService _reportService;

        [ObservableProperty]
        private DashboardDto _stats;

        [ObservableProperty]
        private bool _isBusy;

        public StatisticsViewModel(IReportService reportService)
        {
            _reportService = reportService;
            // Initialize with empty DTO to avoid null reference in binding before load
            Stats = new DashboardDto(); 
            _ = LoadDataAsync();
        }

        [RelayCommand]
        private async Task LoadDataAsync()
        {
            IsBusy = true;
            try
            {
                Stats = await _reportService.GetDashboardStatisticsAsync();
            }
            finally
            {
                IsBusy = false;
            }
        }
    }
}
