using System.Threading.Tasks;
using TT_PPID_CS.Application.DTOs;

namespace TT_PPID_CS.Application.Interfaces
{
    public interface IReportService
    {
        Task<DashboardDto> GetDashboardStatisticsAsync();
    }
}
