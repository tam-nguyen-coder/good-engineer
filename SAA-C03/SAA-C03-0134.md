# Question #134 - Topic 1

A company wants to move its application to a serverless solution. The serverless solution needs to analyze existing and new data by using SL. The company stores the data in an Amazon S3 bucket. The data requires encryption and must be replicated to a different AWS Region. Which solution will meet these requirements with the LEAST operational overhead?

## Options

**A.** Create a new S3 bucket. Load the data into the new S3 bucket. Use S3 Cross-Region Replication (CRR) to replicate encrypted objects to an S3 bucket in another Region. Use server-side encryption with AWS KMS multi-Region kays (SSE-KMS). Use Amazon Athena to query the data.

**B.** Create a new S3 bucket. Load the data into the new S3 bucket. Use S3 Cross-Region Replication (CRR) to replicate encrypted objects to an S3 bucket in another Region. Use server-side encryption with AWS KMS multi-Region keys (SSE-KMS). Use Amazon RDS to query the data.

**C.** Load the data into the existing S3 bucket. Use S3 Cross-Region Replication (CRR) to replicate encrypted objects to an S3 bucket in another Region. Use server-side encryption with Amazon S3 managed encryption keys (SSE-S3). Use Amazon Athena to query the data.

**D.** Load the data into the existing S3 bucket. Use S3 Cross-Region Replication (CRR) to replicate encrypted objects to an S3 bucket in another Region. Use server-side encryption with Amazon S3 managed encryption keys (SSE-S3). Use Amazon RDS to query the data.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Serverless solution, analyze data with SQL, S3 data, encryption, cross-Region replication.
- **Existing Resources:** S3 bucket.
- **Current Issue/Goal:** Least operational overhead for serverless analytics + encryption + CRR.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `serverless solution` | **Athena** (serverless SQL) |
| `analyze data by using SQL` | Athena query S3 directly |
| `encryption` + `replicated to a different Region` | SSE-KMS + CRR |
| `least operational overhead` | Managed serverless |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Serverless analytics + Security
- **Constraints:** SQL analytics, encryption, CRR

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- **Athena** — serverless SQL query trên S3, không cần quản lý infrastructure.
- **SSE-KMS multi-Region keys** — cho phép CRR giữa các Regions với cùng key material.
- **CRR** — tự động replicate objects.
- Tất cả managed → least overhead.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- RDS — không serverless (phải provision), operational overhead hơn Athena.

**❌ Đáp án C:**
- SSE-S3 — CRR với SSE-S3 hoạt động nhưng không hỗ trợ cross-Region key management tốt như KMS multi-Region.

**❌ Đáp án D:**
- SSE-S3 + RDS — cả hai đều không optimal cho serverless requirement.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Athena = serverless SQL on S3. KMS multi-Region keys = cross-Region encryption. CRR = replication"*
