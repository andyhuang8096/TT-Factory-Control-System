using System.Linq;
using System.Threading.Tasks;
using TT_PPID_CS.Application.DTOs;
using TT_PPID_CS.Application.Interfaces;
using TT_PPID_CS.Domain.Interfaces;

namespace TT_PPID_CS.Application.Services
{
    public class ReportService : IReportService
    {
        private readonly IUnitOfWork _unitOfWork;

        public ReportService(IUnitOfWork unitOfWork)
        {
            _unitOfWork = unitOfWork;
        }

        public async Task<DashboardDto> GetDashboardStatisticsAsync()
        {
            var dto = new DashboardDto();

            // PPID Stats
            // Note: Since IUnitOfWork exposes Generic Repositories, we might need to access DbContext directly for GroupBy 
            // or fetch all (inefficient) or extend Repository.
            // For now, assume GetAllAsync is NOT efficient for count.
            // Repositories usually expose CountAsync or similar. 
            // Our generic Repository has DBSet.
            
            // However, Generic Repository in this project doesn't have CountAsync exposed on Interface yet.
            // I will iterate on fetching all for MVP or cast to concrete logic.
            // Ideally, I should add CountAsync to IRepository.
            
            // Let's rely on GetAllAsync for now as dataset is small, or just implement query logic here if we can access DB.
            // But _unitOfWork hides DB.
            // Let's fetch all users and logs (might be heavy eventually).
            
            // BETTER: Add GetCountAsync to IRepository.
            // But I cannot modify Interface easily without breaking others.
            // I will use GetAllAsync (assuming < 10k records for MVP) or efficient queries later.
            
            var ppids = await _unitOfWork.PPIDRecords.GetAllAsync();
            dto.TotalPPIDCount = ppids.Count();
            dto.AvailableCount = ppids.Count(p => p.Status == "available");
            dto.InUseCount = ppids.Count(p => p.Status == "in_use");
            dto.CorruptedCount = ppids.Count(p => p.Status == "corrupted");
            dto.RetiredCount = ppids.Count(p => p.Status == "retired");
            
            dto.ModelDistribution = ppids
                .Where(p => !string.IsNullOrEmpty(p.Model))
                .GroupBy(p => p.Model)
                .ToDictionary(g => g.Key, g => g.Count());

            // Other Stats
            dto.TotalUserCount = (await _unitOfWork.Users.GetAllAsync()).Count();
            dto.ImportCount = (await _unitOfWork.ImportLogs.GetAllAsync()).Count();
            dto.BackupCount = (await _unitOfWork.BackupLogs.GetAllAsync()).Count();

            return dto;
        }
    }
}
