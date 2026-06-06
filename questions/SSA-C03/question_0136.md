# Question #136 - Topic 1

A company is migrating its on-premises PostgreSQL database to Amazon Aurora PostgreSQL. The on-premises database must remain online and accessible during the migration. The Aurora database must remain synchronized with the on-premises database. Which combination of actions must a solutions architect take to meet these requirements? (Choose two.)

## Options

**A.** Create an ongoing replication task.

**B.** Create a database backup of the on-premises database.

**C.** Create an AWS Database Migration Service (AWS DMS) replication server.

**D.** Convert the database schema by using the AWS Schema Conversion Tool (AWS SCT).

**E.** Create an Amazon EventBridge (Amazon CloudWatch Events) rule to monitor the database synchronization.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Migrate PostgreSQL → Aurora PostgreSQL, on-prem must stay online, sync during migration.
- **Existing Resources:** PostgreSQL on-prem.
- **Current Issue/Goal:** Online migration with continuous sync.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `must remain online and accessible` | **AWS DMS** with ongoing replication |
| `remain synchronized` | DMS continuous replication (CDC) |
| `same database engine` | PostgreSQL → Aurora PostgreSQL = homogeneous → no SCT needed |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Database migration
- **Constraints:** Chọn 2, online, sync

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A và C**

**Giải thích:**
- **C: DMS replication server** — tạo server để thực hiện migration.
- **A: Ongoing replication task** — CDC (Change Data Capture) để đồng bộ thay đổi real-time.
- PostgreSQL → Aurora PostgreSQL là **homogeneous migration**, không cần SCT.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Backup không cần thiết cho DMS migration (DMS tự động full load + CDC).

**❌ Đáp án D:**
- **SCT** dùng cho heterogeneous migration (VD: Oracle → Aurora), không cần khi cùng engine.

**❌ Đáp án E:**
- EventBridge không phải tool để monitor DMS replication.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"DMS replication server + ongoing replication task = online migration with CDC. SCT only for heterogeneous"*
