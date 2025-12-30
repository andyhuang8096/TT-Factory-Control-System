using Microsoft.EntityFrameworkCore;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using TT_PPID_CS.Application.DTOs;
using TT_PPID_CS.Application.Interfaces;
using TT_PPID_CS.Domain.Entities;
using TT_PPID_CS.Domain.Interfaces;

namespace TT_PPID_CS.Application.Services
{
    public class PPIDService : IPPIDService
    {
        private readonly IUnitOfWork _unitOfWork;

        public PPIDService(IUnitOfWork unitOfWork)
        {
            _unitOfWork = unitOfWork;
        }

        public async Task<IEnumerable<PPIDRecordDto>> GetAllAsync()
        {
            var entities = await _unitOfWork.PPIDRecords.GetAllAsync();
            
            // 简单的映射，实际项目中可以使用 AutoMapper
            return entities.Select(MapToDto).OrderByDescending(r => r.Id);
        }

        public async Task<IEnumerable<PPIDRecordDto>> SearchAsync(string field, string keyword)
        {
            if (string.IsNullOrWhiteSpace(keyword))
            {
                return await GetAllAsync();
            }

            keyword = keyword.ToLower();
            var result = await _unitOfWork.PPIDRecords.FindAsync(e => 
                (field == "PPID" && e.PPID.Contains(keyword)) ||
                (field == "SerialNumber" && e.SerialNumber != null && e.SerialNumber.Contains(keyword)) ||
                (field == "Model" && e.Model != null && e.Model.Contains(keyword)) ||
                (field == "Status" && e.Status.Contains(keyword))
            );

            // 如果字段不匹配或者想做通用搜索，这里可以扩展逻辑
            // 简单起见，上面的 FindAsync 是基于具体的 Lambda
            // 实际上，为了动态字段搜索，通常需要构建表达式树或在内存中过滤(数据量小的话)
            
            // 内存中过滤示例 (获取所有然后过滤，仅适用于 MVP/小数据量)
            // 生产环境建议修改 Repository 支持动态查询条件
            var all = await _unitOfWork.PPIDRecords.GetAllAsync();
            var filtered = all.Where(e => 
            {
                var val = field switch 
                {
                    "PPID" => e.PPID,
                    "SerialNumber" => e.SerialNumber,
                    "Model" => e.Model,
                    "Status" => e.Status,
                    "PN" => e.PN,
                    _ => ""
                };
                return val != null && val.ToLower().Contains(keyword);
            });

            return filtered.Select(MapToDto).OrderByDescending(r => r.Id);
        }

        public async Task<PPIDRecordDto?> GetByIdAsync(int id)
        {
            var entity = await _unitOfWork.PPIDRecords.GetByIdAsync(id);
            return entity == null ? null : MapToDto(entity);
        }

        public async Task CreateAsync(PPIDRecordDto dto, string? user = null)
        {
            var entity = new PPIDRecord
            {
                PPID = dto.PPID,
                SerialNumber = dto.SerialNumber,
                Model = dto.Model,
                PN = dto.PN,
                Status = dto.Status ?? "available",
                InUseDays = dto.InUseDays,
                CorruptedAttempts = dto.CorruptedAttempts,
                LastUsedTime = dto.LastUsedTime,
                Notes = dto.Notes,
                CreateUser = user,
                UpdateUser = user
            };

            await _unitOfWork.PPIDRecords.AddAsync(entity);
            await _unitOfWork.CompleteAsync();
            
            // 记录审计日志
            await _unitOfWork.AuditLogs.AddAsync(new AuditLog
            {
                UserName = user ?? "system",
                Action = "CREATE",
                TableName = "PPIDRecord",
                Description = $"Created PPID record: {entity.PPID}"
            });
            await _unitOfWork.CompleteAsync();
        }

        public async Task UpdateAsync(PPIDRecordDto dto, string? user = null)
        {
            var entity = await _unitOfWork.PPIDRecords.GetByIdAsync(dto.Id);
            if (entity == null) return;

            entity.PPID = dto.PPID;
            entity.SerialNumber = dto.SerialNumber;
            entity.Model = dto.Model;
            entity.PN = dto.PN;
            entity.Status = dto.Status;
            entity.InUseDays = dto.InUseDays;
            entity.CorruptedAttempts = dto.CorruptedAttempts;
            entity.LastUsedTime = dto.LastUsedTime;
            entity.Notes = dto.Notes;
            entity.UpdateUser = user;

            await _unitOfWork.PPIDRecords.UpdateAsync(entity);
            await _unitOfWork.CompleteAsync();

            await _unitOfWork.AuditLogs.AddAsync(new AuditLog
            {
                UserName = user ?? "system",
                Action = "UPDATE",
                TableName = "PPIDRecord",
                RecordId = entity.Id,
                Description = $"Updated PPID record: {entity.PPID}"
            });
            await _unitOfWork.CompleteAsync();
        }

        public async Task DeleteAsync(int id, string? user = null)
        {
            await _unitOfWork.PPIDRecords.SoftDeleteAsync(id, user);
            await _unitOfWork.CompleteAsync();

            await _unitOfWork.AuditLogs.AddAsync(new AuditLog
            {
                UserName = user ?? "system",
                Action = "DELETE",
                TableName = "PPIDRecord",
                RecordId = id,
                Description = "Soft deleted PPID record"
            });
            await _unitOfWork.CompleteAsync();
        }

        private static PPIDRecordDto MapToDto(PPIDRecord entity)
        {
            return new PPIDRecordDto
            {
                Id = entity.Id,
                PPID = entity.PPID,
                SerialNumber = entity.SerialNumber,
                Model = entity.Model,
                PN = entity.PN,
                Status = entity.Status,
                InUseDays = entity.InUseDays,
                CorruptedAttempts = entity.CorruptedAttempts,
                LastUsedTime = entity.LastUsedTime,
                Notes = entity.Notes,
                CreateTime = entity.CreateTime,
                CreateUser = entity.CreateUser,
                UpdateTime = entity.UpdateTime,
                UpdateUser = entity.UpdateUser
            };
        }
    }
}
