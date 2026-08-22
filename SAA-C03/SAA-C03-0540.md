# Question #540 - Topic 1

A company has an on-premises server that uses an Oracle database to process and store customer information. The company wants to use an AWS database service to achieve higher availability and to improve application performance. The company also wants to offload reporting from its primary database system. Which solution will meet these requirements in the MOST operationally efficient way?

## Options

**A.** Use AWS Database Migration Service (AWS DMS) to create an Amazon RDS DB instance in multiple AWS Regions. Point the reporting functions toward a separate DB instance from the primary DB instance.

**B.** Use Amazon RDS in a Single-AZ deployment to create an Oracle database. Create a read replica in the same zone as the primary DB instance. Direct the reporting functions to the read replica.

**C.** Use Amazon RDS deployed in a Multi-AZ cluster deployment to create an Oracle database. Direct the reporting functions to use the reader instance in the cluster deployment.

**D.** Use Amazon RDS deployed in a Multi-AZ instance deployment to create an Amazon Aurora database. Direct the reporting functions to the reader instances.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** On-premises Oracle database cần migrate lên AWS. Yêu cầu: higher availability, improve performance, offload reporting từ primary database.
- **Existing Resources:** On-premises Oracle database.
- **Current Issue/Goal:** HA, performance, reporting offload.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `higher availability` | Multi-AZ → HA |
| `offload reporting` | Reader instances → read-only workload |
| `Oracle database` | Cần Amazon RDS for Oracle hoặc Aurora (Aurora không hỗ trợ Oracle) |
| `most operationally efficient` | RDS managed service, Multi-AZ cluster |
| `reader instance` | Readable standby trong Multi-AZ cluster → vừa HA vừa serve reporting |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most operationally efficient
- **Constraints:** Oracle database, HA, offload reporting

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- Amazon RDS for Oracle Multi-AZ cluster deployment: 1 writer + 2 reader instances (readable standby) across 3 AZs.
- Reader instances vừa cung cấp HA (failover) vừa serve reporting queries → offload primary database.
- Multi-AZ cluster cung cấp high availability (tự động failover).
- Operational efficiency: managed service, không cần quản lý replication riêng.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- DMS tạo RDS instance multi-Region: phức tạp, operational overhead cao.
- Không cần multi-Region nếu chỉ cần HA + reporting offload.

**❌ Đáp án B:**
- Single-AZ: không HA (nếu AZ fail → database mất).
- Read replica trong cùng AZ: không cung cấp HA.

**❌ Đáp án D:**
- Amazon Aurora không hỗ trợ Oracle (Aurora chỉ hỗ trợ MySQL và PostgreSQL).
- Câu hỏi nói Oracle database → không thể migrate sang Aurora.

## 6. MẸO GHI NHỚ (MEMORY HOOK)
🧠 *"Oracle + HA + reporting offload → RDS for Oracle Multi-AZ cluster (reader instances). Aurora = MySQL/PostgreSQL only."*
