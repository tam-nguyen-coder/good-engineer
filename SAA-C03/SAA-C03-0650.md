# Question #650 - Topic 1

A company wants to migrate its on-premises Microsoft SQL Server Enterprise edition database to AWS. The company's online application uses the database to process transactions. The data analysis team uses the same production database to run reports for analytical processing. The company wants to reduce operational overhead by moving to managed services wherever possible. Which solution will meet these requirements with the LEAST operational overhead?

## Options

**A.** Migrate to Amazon RDS for Microsoft SOL Server. Use read replicas for reporting purposes

**B.** Migrate to Microsoft SQL Server on Amazon EC2. Use Always On read replicas for reporting purposes

**C.** Migrate to Amazon DynamoDB. Use DynamoDB on-demand replicas for reporting purposes

**D.** Migrate to Amazon Aurora MySQL. Use Aurora read replicas for reporting purposes

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Migrate SQL Server Enterprise from on-prem to AWS. App uses DB for transactions, data analysis team runs reports on production DB (heavy read).
- **Existing Resources:** SQL Server Enterprise database.
- **Current Issue/Goal:** Reduce operational overhead, managed services, separate read traffic for reporting.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `Microsoft SQL Server Enterprise` | Cần compatible DB engine (không thể chuyển sang MySQL/Aurora dễ dàng). |
| `reduce operational overhead` | RDS managed > EC2 self-managed. |
| `read replicas for reporting` | Giảm tải read trên production DB. |
| `least operational overhead` | RDS managed service. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Least operational overhead
- **Constraints:** SQL Server, managed services, read replica for reporting

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- Amazon RDS for SQL Server là managed service → giảm operational overhead (no patching, backup management).
- Read replicas: RDS for SQL Server hỗ trợ read replicas (trong cùng region) → tách read traffic cho reporting team.
- Giữ nguyên SQL Server engine → không cần sửa application code.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- SQL Server trên EC2: tự quản lý OS, DB patches, backups → operational overhead cao hơn RDS.

**❌ Đáp án C:**
- DynamoDB là NoSQL, không compatible với SQL Server → cần rewrite application.

**❌ Đáp án D:**
- Aurora MySQL khác engine với SQL Server → không compatible, cần rewrite.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"SQL Server migration → RDS for SQL Server managed + read replicas. Don't change engine."*
