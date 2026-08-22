# Question #235 - Topic 1

A company is moving its on-premises Oracle database to Amazon Aurora PostgreSQL. The database has several applications that write to the same tables. The applications need to be migrated one by one with a month in between each migration. Management has expressed concerns that the database has a high number of reads and writes. The data must be kept in sync across both databases throughout the migration. What should a solutions architect recommend?

## Options

**A.** Use AWS DataSync for the initial migration. Use AWS Database Migration Service (AWS DMS) to create a change data capture (CDC) replication task and a table mapping to select all tables.

**B.** Use AWS DataSync for the initial migration. Use AWS Database Migration Service (AWS DMS) to create a full load plus change data capture (CDC) replication task and a table mapping to select all tables.

**C.** Use the AWS Schema Conversion Tool with AWS Database Migration Service (AWS DMS) using a memory optimized replication instance. Create a full load plus change data capture (CDC) replication task and a table mapping to select all tables.

**D.** Use the AWS Schema Conversion Tool with AWS Database Migration Service (AWS DMS) using a compute optimized replication instance. Create a full load plus change data capture (CDC) replication task and a table mapping to select the largest tables.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Oracle → Aurora PostgreSQL migration. Multiple apps, migrate 1/month. High R/W. Keep data in sync during migration.
- **Existing Resources:** Oracle on-prem.
- **Current Issue/Goal:** Heterogeneous migration with CDC.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `Oracle to Amazon Aurora PostgreSQL` | **Schema Conversion Tool (SCT)** — heterogeneous |
| `kept in sync across both databases` | **DMS full load + CDC** |
| `high number of reads and writes` | Memory-optimized replication instance |
| `select all tables` | Table mapping tất cả |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Database migration
- **Constraints:** Heterogeneous, CDC, high R/W

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- **SCT** — chuyển đổi schema từ Oracle → PostgreSQL (heterogeneous).
- **DMS full load + CDC** — full load ban đầu + replicate changes liên tục.
- **Memory-optimized instance** — cần nhiều RAM cho high R/W workload.
- **All tables** — phải chọn tất cả tables.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- DataSync — cho file/object, không phải database migration.

**❌ Đáp án B:**
- DataSync — không phù hợp.

**❌ Đáp án D:**
- Compute-optimized — không phù hợp cho high R/W (cần memory). Chỉ select largest tables — thiếu tables.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"SCT = heterogeneous schema conversion. DMS full load + CDC = sync. Memory-optimized = high R/W"*
