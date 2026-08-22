# Question #588 - Topic 1

An ecommerce company wants a disaster recovery solution for its Amazon RDS DB instances that run Microsoft SQL Server Enterprise Edition. The company's current recovery point objective (RPO) and recovery time objective (RTO) are 24 hours. Which solution will meet these requirements MOST cost-effectively?

## Options

**A.** Create a cross-Region read replica and promote the read replica to the primary instance.

**B.** Use AWS Database Migration Service (AWS DMS) to create RDS cross-Region replication.

**C.** Use cross-Region replication every 24 hours to copy native backups to an Amazon S3 bucket.

**D.** Copy automatic snapshots to another Region every 24 hours.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** RDS SQL Server, DR solution, RPO/RTO = 24 hours.
- **Existing Resources:** RDS SQL Server Enterprise Edition.
- **Current Issue/Goal:** DR cost-effective, RPO/RTO 24h.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `RPO 24 hours` | Có thể mất tối đa 24h data → snapshot mỗi 24h là đủ. |
| `RTO 24 hours` | Restore trong 24h là chấp nhận được. |
| `MOST cost-effectively` | Copy automatic snapshots là rẻ nhất. |
| `cross-Region` | DR yêu cầu khác Region. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most cost-effectively
- **Constraints:** RDS SQL Server, RPO/RTO 24h, DR

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- RDS tự động tạo snapshot hàng ngày, có thể cấu hình copy sang Region khác.
- RPO 24h: snapshot 1 lần/ngày là đủ.
- RTO 24h: restore từ snapshot trong 24h là feasible.
- Cost: chỉ tốn storage cho snapshot + cross-Region data transfer (thấp nhất).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- SQL Server cross-Region read replica: không hỗ trợ cho SQL Server (chỉ có cho MySQL/MariaDB/PostgreSQL/Aurora).

**❌ Đáp án B:**
- AWS DMS: thêm chi phí (replication instance), overkill nếu RPO 24h.

**❌ Đáp án C:**
- Native backup replication: cần thêm scripting và quản lý, tốn kém hơn snapshot copy.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"RPO/RTO 24h → copy automatic snapshots cross-Region (cheapest). SQL Server không có cross-Region read replica."*
