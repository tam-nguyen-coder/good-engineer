# Question #529 - Topic 1

A company is migrating its workloads to AWS. The company has transactional and sensitive data in its databases. The company wants to use AWS Cloud solutions to increase security and reduce operational overhead for the databases. Which solution will meet these requirements?

## Options

**A.** Migrate the databases to Amazon EC2. Use an AWS Key Management Service (AWS KMS) AWS managed key for encryption.

**B.** Migrate the databases to Amazon RDS Configure encryption at rest.

**C.** Migrate the data to Amazon S3 Use Amazon Macie for data security and protection.

**D.** Migrate the database to Amazon RDS. Use Amazon CloudWatch Logs for data security and protection.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Migrate transactional & sensitive databases lên AWS. Cần tăng security và giảm operational overhead.
- **Existing Resources:** On-premises databases.
- **Current Issue/Goal:** Database migration với encryption, operational overhead thấp.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `transactional and sensitive data` | Cần relational database với encryption |
| `increase security` | Encryption at rest là yêu cầu cơ bản |
| `reduce operational overhead` | RDS managed service (tự động backup, patching, replication) |
| `encryption at rest` | RDS hỗ trợ encryption at rest với KMS |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Operational overhead reduction + security
- **Constraints:** Transactional data, sensitive data

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- Amazon RDS là managed database service, giảm operational overhead so với tự quản lý database trên EC2.
- RDS hỗ trợ encryption at rest sử dụng AWS KMS → bảo vệ dữ liệu nhạy cảm.
- RDS tự động: backup, patch, replication, failover.
- Phù hợp với transactional workload (relational database).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Database trên EC2: vẫn phải tự quản lý OS, database patches, backups → operational overhead cao.
- AWS managed key cho EC2 volume encryption không tự động encrypt database files bên trong.

**❌ Đáp án C:**
- S3 không phải database, không phù hợp cho transactional data.
- Macie dùng để detect PII trong S3, không phải database security solution.

**❌ Đáp án D:**
- CloudWatch Logs dùng để log monitoring, không phải data security/protection.
- Không có encryption at rest được đề cập.

## 6. MẸO GHI NHỚ (MEMORY HOOK)
🧠 *"Transactional + sensitive data → RDS with encryption at rest = managed + secure."*
