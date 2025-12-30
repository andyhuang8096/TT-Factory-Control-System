using System.Collections.Generic;

namespace TT_PPID_CS.Application.DTOs
{
    public class DashboardDto
    {
        public int TotalPPIDCount { get; set; }
        public int AvailableCount { get; set; }
        public int InUseCount { get; set; }
        public int CorruptedCount { get; set; }
        public int RetiredCount { get; set; }
        
        public int TotalUserCount { get; set; }
        public int ImportCount { get; set; }
        public int BackupCount { get; set; }
        
        // simple distribution for charts if needed
        public Dictionary<string, int> ModelDistribution { get; set; } = new Dictionary<string, int>();
    }
}
