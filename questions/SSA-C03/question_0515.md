# Question #515 - Topic 1

A company is migrating an on-premises application to AWS. The company wants to use Amazon Redshift as a solution. Which use cases are suitable for Amazon Redshift in this scenario? (Choose three.)

## Options

**A.** Supporting data APIs to access data with traditional, containerized, and event-driven applications

**B.** Supporting client-side and server-side encryption

**C.** Building analytics workloads during specified hours and when the application is not active

**D.** Caching data to reduce the pressure on the backend database

**E.** Scaling globally to support petabytes of data and tens of millions of requests per minute

**F.** Creating a secondary replica of the cluster by using the AWS Management Console

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Migrate on-premises app lên AWS, dùng Amazon Redshift. Cần chọn use cases phù hợp với Redshift.
- **Existing Resources:** On-premises application, migrating to AWS.
- **Current Issue/Goal:** Xác định đúng use cases của Redshift.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `Amazon Redshift` | Data warehouse: petabyte-scale, analytics/BI, columnar storage, SQL query. |
| `analytics workloads` | Redshift dành cho analytics, không phải OLTP. |
| `encryption` | Redshift hỗ trợ encryption (KMS, HSM). |
| `petabytes of data` | Redshift scale đến petabyte. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Identify suitable use cases (choose 3)
- **Constraints:** N/A

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B, C, E**

**Giải thích:**
- **B - Encryption:** Redshift hỗ trợ cả server-side encryption (KMS, CloudHSM) và client-side encryption. → Use case phù hợp.
- **C - Analytics workloads:** Redshift là data warehouse, sinh ra để chạy analytics workloads trên dữ liệu lớn. → Use case chính.
- **E - Petabyte-scale:** Redshift có thể scale đến petabyte với kiến trúc massively parallel processing (MPP) và RA3 nodes với managed storage. Peta-scale analytics là use case cốt lõi.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Redshift không phải là data API backend cho ứng dụng real-time (OLTP). Dùng cho analytics/BI, không phải serving layer cho traditional/event-driven apps.
- Use case này phù hợp với DynamoDB, RDS, hoặc API Gateway + Lambda.

**❌ Đáp án D:**
- Caching là use case của ElastiCache (Redis/Memcached) hoặc DAX (DynamoDB Accelerator). Redshift không phải caching layer.

**❌ Đáp án F:**
- Redshift không hỗ trợ "secondary replica" như RDS Read Replica. Redshift có tính năng snapshot và cross-region snapshot restore, nhưng không phải live secondary replica. Câu này sai vì mô tả sai khả năng của Redshift.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Redshift = data warehouse: analytics (C) + petabyte-scale (E) + encryption (B). Không phải caching (ElastiCache), không phải API backend (DynamoDB)."*
