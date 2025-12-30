using System.Threading.Tasks;

namespace TT_PPID_CS.Application.Interfaces
{
    public interface IImportService
    {
        Task<(int total, int success, int failed, string message)> ImportPPIDRecordsAsync(string filePath, string? user = null);
    }
}
