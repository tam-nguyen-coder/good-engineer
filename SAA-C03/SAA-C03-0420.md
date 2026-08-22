# Question #420 - Topic 1

A company wants to use an Amazon RDS for PostgreSQL DB cluster to simplify time-consuming database administrative tasks for production database workloads. The company wants to ensure that its database is highly available and will provide automatic failover support in most scenarios in less than 40 seconds. The company wants to offload reads off of the primary instance and keep costs as low as possible. Which solution will meet these requirements?

## Options

**A.** Use an Amazon RDS Multi-AZ DB instance deployment. Create one read replica and point the read workload to the read replica.

**B.** Use an Amazon RDS Multi-AZ DB cluster deployment Create two read replicas and point the read workload to the read replicas.

**C.** Use an Amazon RDS Multi-AZ DB instance deployment. Point the read workload to the secondary instances in the Multi-AZ pair.

**D.** Use an Amazon RDS Multi-AZ DB cluster deployment Point the read workload to the reader endpoint.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** RDS for PostgreSQL. Need HA, automatic failover < 40s. Offload reads from primary. Low cost.
- **Existing Resources:** PostgreSQL database.
- **Current Issue/Goal:** HA + read scaling with minimal cost.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `offload reads off of the primary` | Need readable standby instances. |
| `automatic failover in less than 40 seconds` | Multi-AZ DB cluster (fast failover). |
| `keep costs as low as possible` | Không tạo thêm resources không cần thiết. |
| `reader endpoint` | Multi-AZ DB cluster: 2 reader instances, tự động load balance. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** High Availability / Performance
- **Constraints:** < 40s failover, offload reads, low cost

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- Multi-AZ DB cluster (RDS for PostgreSQL/MySQL): 1 writer + 2 reader instances across 3 AZs.
- Reader endpoint: tự động phân phối read traffic giữa 2 reader instances.
- Failover < 40s (automatic).
- Không cần thêm read replica → cost thấp nhất.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Multi-AZ DB instance: standby không dùng cho reads. Phải tạo thêm read replica → tốn thêm cost.

**❌ Đáp án B:**
- Multi-AZ DB cluster đã có 2 reader instances. Thêm 2 read replicas là dư thừa, tăng cost.

**❌ Đáp án C:**
- Multi-AZ DB instance: chỉ có 1 standby, không dùng cho reads. Không có "secondary instances" để đọc.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Multi-AZ DB cluster = 1 writer + 2 readers, reader endpoint. Cheaper than instance + extra replicas."*