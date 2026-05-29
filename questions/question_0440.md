# Question #440 - Topic 1

A company used an Amazon RDS for MySQL DB instance during application testing. Before terminating the DB instance at the end of the test cycle, a solutions architect created two backups. The solutions architect created the first backup by using the mysqldump utility to create a database dump. The solutions architect created the second backup by enabling the final DB snapshot option on RDS termination. The company is now planning for a new test cycle and wants to create a new DB instance from the most recent backup. The company has chosen a MySQL-compatible edition of Amazon Aurora to host the DB instance. Which solutions will create the new DB instance? (Choose two.)

## Options

**A.** Import the RDS snapshot directly into Aurora.

**B.** Upload the RDS snapshot to Amazon S3. Then import the RDS snapshot into Aurora.

**C.** Upload the database dump to Amazon S3. Then import the database dump into Aurora.

**D.** Use AWS Database Migration Service (AWS DMS) to import the RDS snapshot into Aurora.

**E.** Upload the database dump to Amazon S3. Then use AWS Database Migration Service (AWS DMS) to import the database dump into Aurora.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** RDS MySQL test instance terminated. Have 2 backups: mysqldump + RDS snapshot. Need Aurora MySQL DB from most recent backup.
- **Existing Resources:** MySQL database dump, RDS final snapshot.
- **Current Issue/Goal:** Migrate to Aurora MySQL from existing backup.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `RDS snapshot` | Can be restored/migrated directly to Aurora MySQL. |
| `mysqldump` | Can be imported via S3 into Aurora. |
| `Aurora MySQL` | MySQL-compatible. Supports both migration paths. |
| `Choose two` | 2 answers required. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Migration / Database
- **Constraints:** From RDS MySQL to Aurora MySQL. Use existing backups.

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A, C**

**Giải thích:**
- **A:** RDS MySQL snapshot → restore directly as Aurora MySQL DB cluster (built-in migration feature).
- **C:** mysqldump → upload to S3 → use Aurora's LOAD DATA FROM S3 or import via console/CLI.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- RDS snapshot không thể upload manually lên S3 (AWS quản lý snapshots internally).

**❌ Đáp án D:**
- DMS không import RDS snapshots. DMS dùng để migrate data liên tục (CDC).

**❌ Đáp án E:**
- DMS có thể migrate từ MySQL sang Aurora nhưng complex hơn import trực tiếp từ S3.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"RDS → Aurora: restore snapshot directly OR mysqldump → S3 → import."*