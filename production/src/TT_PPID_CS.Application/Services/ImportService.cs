using CsvHelper;
using CsvHelper.Configuration;
using MiniExcelLibs;
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using TT_PPID_CS.Application.Interfaces;
using TT_PPID_CS.Domain.Entities;
using TT_PPID_CS.Domain.Interfaces;

namespace TT_PPID_CS.Application.Services
{
    public class ImportService : IImportService
    {
        private readonly IUnitOfWork _unitOfWork;

        public ImportService(IUnitOfWork unitOfWork)
        {
            _unitOfWork = unitOfWork;
        }

        public async Task<(int total, int success, int failed, string message)> ImportPPIDRecordsAsync(string filePath, string? user = null)
        {
            if (!File.Exists(filePath))
            {
                return (0, 0, 0, "文件不存在");
            }

            var extension = Path.GetExtension(filePath).ToLower();
            List<PPIDRecord> recordsToImport = new List<PPIDRecord>();
            int total = 0;
            int success = 0;
            int failed = 0;

            try
            {
                if (extension == ".csv")
                {
                    using (var reader = new StreamReader(filePath))
                    using (var csv = new CsvReader(reader, new CsvConfiguration(CultureInfo.InvariantCulture)
                    {
                        HeaderValidated = null,
                        MissingFieldFound = null
                    }))
                    {
                        var records = csv.GetRecords<PPIDImportDto>().ToList();
                        total = records.Count;
                        recordsToImport = MapDtosToEntities(records, user);
                    }
                }
                else if (extension == ".xlsx" || extension == ".xls")
                {
                    var records = MiniExcel.Query<PPIDImportDto>(filePath).ToList();
                    total = records.Count;
                    recordsToImport = MapDtosToEntities(records, user);
                }
                else if (extension == ".json")
                {
                    var json = await File.ReadAllTextAsync(filePath);
                    var records = System.Text.Json.JsonSerializer.Deserialize<List<PPIDImportDto>>(json);
                    if (records != null)
                    {
                        total = records.Count;
                        recordsToImport = MapDtosToEntities(records, user);
                    }
                }
                else
                {
                    return (0, 0, 0, "不支持的文件格式");
                }

                // Batch insert
                foreach (var record in recordsToImport)
                {
                    try
                    {
                        // Check duplication if needed (e.g. PPID should be unique)
                        // For bulk performance, we might want to check in memory or batch check
                        // Here we do simple check
                        var exists = (await _unitOfWork.PPIDRecords.FindAsync(r => r.PPID == record.PPID)).Any();
                        if (!exists)
                        {
                            await _unitOfWork.PPIDRecords.AddAsync(record);
                            success++;
                        }
                        else
                        {
                            failed++; // Duplicate
                        }
                    }
                    catch
                    {
                        failed++;
                    }
                }

                await _unitOfWork.CompleteAsync();
                
                // Log import
                await _unitOfWork.ImportLogs.AddAsync(new ImportLog
                {
                    FileName = Path.GetFileName(filePath),
                    FilePath = filePath,
                    ImportType = extension.TrimStart('.'),
                    TotalRows = total,
                    SuccessRows = success,
                    FailedRows = failed,
                    Status = "completed",
                    CreateUser = user,
                    UpdateUser = user,
                    StartTime = DateTime.Now,
                    EndTime = DateTime.Now
                });
                await _unitOfWork.CompleteAsync();

                return (total, success, failed, "导入完成");

            }
            catch (Exception ex)
            {
                return (total, success, failed, $"导入出错: {ex.Message}");
            }
        }

        private List<PPIDRecord> MapDtosToEntities(List<PPIDImportDto> dtos, string? user)
        {
            return dtos.Select(d => new PPIDRecord
            {
                PPID = d.PPID,
                SerialNumber = d.SerialNumber,
                Model = d.Model,
                PN = d.PN,
                Status = string.IsNullOrWhiteSpace(d.Status) ? "available" : d.Status,
                Notes = d.Notes,
                CreateUser = user,
                UpdateUser = user
            }).ToList();
        }

        // Helper private DTO for import structure
        private class PPIDImportDto
        {
            public string PPID { get; set; } = string.Empty;
            public string? SerialNumber { get; set; }
            public string? Model { get; set; }
            public string? PN { get; set; }
            public string? Status { get; set; }
            public string? Notes { get; set; }
        }
    }
}
