# Question #554 - Topic 1

A company's SAP application has a backend SQL Server database in an on-premises environment. The company wants to migrate its on-premises application and database server to AWS. The company needs an instance type that meets the high demands of its SAP database. On-premises performance data shows that both the SAP application and the database have high memory utilization. Which solution will meet these requirements?

## Options

**A.** Use the compute optimized instance family for the application. Use the memory optimized instance family for the database.

**B.** Use the storage optimized instance family for both the application and the database.

**C.** Use the memory optimized instance family for both the application and the database.

**D.** Use the high performance computing (HPC) optimized instance family for the application. Use the memory optimized instance family for the database.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Migrate SAP application và SQL Server database từ on-prem lên AWS. Cả application và database đều có high memory utilization.
- **Existing Resources:** SAP application và SQL Server database on-prem.
- **Current Issue/Goal:** Chọn instance family phù hợp cho cả application và database.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `high memory utilization` | Cả SAP app và database đều dùng nhiều RAM |
| `SAP application` | Ứng dụng SAP thường yêu cầu nhiều memory |
| `SQL Server database` | Database cũng cần nhiều memory |
| `memory optimized` | Instance family tối ưu cho memory-intensive workloads (R series: R5, R6g, X2, etc.) |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most appropriate solution
- **Constraints:** High memory utilization cho cả app và database, SAP + SQL Server

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- Cả SAP application và SQL Server database đều có high memory utilization → cần memory optimized instance family cho cả hai.
- Memory optimized families (R5, R6i, R6g, X2idn, X2iedn, etc.) cung cấp tỷ lệ RAM/vCPU cao, phù hợp cho SAP workloads và SQL Server.
- SAP trên AWS best practices khuyến nghị memory optimized instances.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A (Compute optimized for app, memory optimized for DB):** Compute optimized (C series) phù hợp cho compute-intensive workloads, không tối ưu cho SAP application vì SAP cũng cần nhiều memory.

**❌ Đáp án B (Storage optimized for both):** Storage optimized (I3, I4i, D2, D3, etc.) tối ưu cho I/O-intensive workloads (cơ sở dữ liệu lớn với high I/O), không phải memory-intensive.

**❌ Đáp án D (HPC optimized for app):** HPC optimized (Hpc6a, Hpc7a) dành cho high performance computing workloads (scientific simulations, weather modeling), không phù hợp cho SAP application.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"High memory utilization = memory optimized (R/X series). SAP + SQL Server = memory hungry. Don't confuse with compute (C) or storage (I/D)."*
