# Question #350 - Topic 1

A company uses a 100 GB Amazon RDS for Microsoft SQL Server Single-AZ DB instance in the us-east-1 Region to store customer transactions. The company needs high availability and automatic recovery for the DB instance. The company must also run reports on the RDS database several times a year. The report process causes transactions to take longer than usual to post to the customers' accounts. The company needs a solution that will improve the performance of the report process. Which combination of steps will meet these requirements? (Choose two.)

## Options

**A.** Modify the DB instance from a Single-AZ DB instance to a Multi-AZ deployment.

**B.** Take a snapshot of the current DB instance. Restore the snapshot to a new RDS deployment in another Availability Zone.

**C.** Create a read replica of the DB instance in a different Availability Zone. Point all requests for reports to the read replica.

**D.** Migrate the database to RDS Custom.

**E.** Use RDS Proxy to limit reporting requests to the maintenance window.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** 100 GB RDS SQL Server Single-AZ. Cần HA + automatic recovery. Reports cause slow transactions. Need to improve report performance.
- **Existing Resources:** RDS SQL Server Single-AZ.
- **Current Issue/Goal:** HA + offload reporting workload.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `high availability and automatic recovery` | Multi-AZ deployment (synchronous standby, auto failover). |
| `reports ... cause transactions to take longer` | Read replica offload reporting queries → không impact primary. |
| `improve the performance of the report process` | Run reports on read replica. |
| `read replica` | Read-only copy, xử lý reporting workload. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Choose two
- **Constraints:** HA + automatic recovery + improve report performance

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A (Multi-AZ) và C (Read Replica)**

**Giải thích:**
- **A (Multi-AZ):** Cung cấp HA + automatic failover cho production database.
- **C (Read Replica):** Tạo read replica ở AZ khác, point report requests đến read replica → không ảnh hưởng production transactions.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Restore snapshot không phải HA solution. Snapshot không real-time, không tự động failover.

**❌ Đáp án D:**
- RDS Custom chỉ cần khi cần SQL Server features không có trong RDS managed. Không giải quyết HA hay report performance.

**❌ Đáp án E:**
- RDS Proxy: connection pooling, không limit reporting requests. Không giải quyết root cause (report làm chậm primary).

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"HA → Multi-AZ. Report performance → Read Replica (offload). Cả 2 cần thiết cho production."*
