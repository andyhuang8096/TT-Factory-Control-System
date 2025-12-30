using System.Collections.Generic;
using System.Threading.Tasks;
using TT_PPID_CS.Application.DTOs;

namespace TT_PPID_CS.Application.Interfaces
{
    public interface IPPIDService
    {
        Task<IEnumerable<PPIDRecordDto>> GetAllAsync();
        Task<IEnumerable<PPIDRecordDto>> SearchAsync(string field, string keyword);
        Task<PPIDRecordDto?> GetByIdAsync(int id);
        Task CreateAsync(PPIDRecordDto dto, string? user = null);
        Task UpdateAsync(PPIDRecordDto dto, string? user = null);
        Task DeleteAsync(int id, string? user = null);
    }
}
