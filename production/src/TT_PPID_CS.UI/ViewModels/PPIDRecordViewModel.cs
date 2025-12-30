using CommunityToolkit.Mvvm.ComponentModel;
using TT_PPID_CS.Application.DTOs;
using System.Collections.Generic;

namespace TT_PPID_CS.UI.ViewModels
{
    public partial class PPIDRecordViewModel : ObservableObject
    {
        [ObservableProperty]
        private string _title = "添加记录";

        [ObservableProperty]
        private PPIDRecordDto _record;
        
        public bool IsEditMode { get; private set; }

        public List<string> StatusOptions { get; } = new List<string> { "available", "in_use", "corrupted", "retired" };

        public PPIDRecordViewModel(PPIDRecordDto? record = null)
        {
            if (record != null)
            {
                Title = "编辑记录";
                IsEditMode = true;
                // Clone the record to avoid modifying the original list item directly before saving
                Record = new PPIDRecordDto
                {
                    Id = record.Id,
                    PPID = record.PPID,
                    SerialNumber = record.SerialNumber,
                    Model = record.Model,
                    PN = record.PN,
                    Status = record.Status,
                    Notes = record.Notes,
                    InUseDays = record.InUseDays,
                    CorruptedAttempts = record.CorruptedAttempts,
                    LastUsedTime = record.LastUsedTime,
                    CreateTime = record.CreateTime,
                    CreateUser = record.CreateUser
                };
            }
            else
            {
                Record = new PPIDRecordDto { Status = "available" };
            }
        }
    }
}
