# Question #314 - Topic 1

A company has an on-premises MySQL database used by the global sales team with infrequent access patterns. The sales team requires the database to have minimal downtime. A database administrator wants to migrate this database to AWS without selecting a particular instance type in anticipation of more users in the future. Which service should a solutions architect recommend?

## Options

**A.** Amazon Aurora MySQL

**B.** Amazon Aurora Serverless for MySQL

**C.** Amazon Redshift Spectrum

**D.** Amazon RDS for MySQL

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** On-prem MySQL, infrequent access, minimal downtime, không muốn chọn instance type trước.
- **Existing Resources:** On-premises MySQL database.
- **Current Issue/Goal:** Migrate to AWS, không chọn instance type, minimal downtime, infrequent access.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `infrequent access patterns` | Không cần instance chạy 24/7 → serverless lý tưởng (pay per request). |
| `without selecting a particular instance type` | Aurora Serverless tự động scale, không cần chọn instance type. |
| `minimal downtime` | Aurora Serverless có tính năng auto-scaling và failover. |
| `Amazon Aurora Serverless` | Auto-scaling database, pay per ACU (Aurora Capacity Units), không cần chọn instance. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Which service to recommend
- **Constraints:** Infrequent access, no instance type selection, minimal downtime

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- Aurora Serverless: tự động scale compute capacity dựa trên nhu cầu, không cần chọn instance type.
- Phù hợp cho infrequent access: scale xuống 0 ACU khi không dùng, pay per second.
- Minimal downtime: Aurora Serverless tự động failover và patch.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Aurora MySQL (provisioned) yêu cầu chọn instance type, không tự động scale xuống 0.

**❌ Đáp án C:**
- Redshift Spectrum dùng cho query S3 data (data warehouse), không phải OLTP database.

**❌ Đáp án D:**
- RDS for MySQL yêu cầu chọn instance type, không tự động scale.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Infrequent access + no instance selection → Aurora Serverless (auto-scale, pay per request). RDS/Aurora provisioned = chọn instance."*
