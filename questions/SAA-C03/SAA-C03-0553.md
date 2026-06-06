# Question #553 - Topic 1

A solutions architect needs to review a company's Amazon S3 buckets to discover personally identifiable information (PII). The company stores the PII data in the us-east-1 Region and us-west-2 Region. Which solution will meet these requirements with the LEAST operational overhead?

## Options

**A.** Configure Amazon Macie in each Region. Create a job to analyze the data that is in Amazon S3.

**B.** Configure AWS Security Hub for all Regions. Create an AWS Config rule to analyze the data that is in Amazon S3.

**C.** Configure Amazon Inspector to analyze the data that is in Amazon S3.

**D.** Configure Amazon GuardDuty to analyze the data that is in Amazon S3.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Cần review S3 buckets để phát hiện PII (personally identifiable information). Dữ liệu PII lưu ở us-east-1 và us-west-2.
- **Existing Resources:** S3 buckets ở 2 regions.
- **Current Issue/Goal:** Phát hiện PII trong S3, ít operational overhead nhất.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `discover personally identifiable information (PII)` | Phát hiện dữ liệu nhạy cảm |
| `Amazon Macie` | Dịch vụ phát hiện PII và sensitive data trong S3 |
| `us-east-1` và `us-west-2` | Cần cấu hình ở cả 2 regions |
| `LEAST operational overhead` | Giải pháp managed, ít cấu hình nhất |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Least operational overhead
- **Constraints:** Phát hiện PII trong S3 buckets

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- Amazon Macie là dịch vụ chuyên dụng để phát hiện PII, thông tin thẻ tín dụng, credentials, và các sensitive data trong S3.
- Sử dụng ML và pattern matching tự động để phân loại dữ liệu.
- Chỉ cần tạo Macie job cho mỗi region (us-east-1, us-west-2) để scan S3 buckets.
- Cung cấp dashboard và alerts chi tiết về findings.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B (Security Hub + Config rule):** AWS Security Hub tập trung security findings từ nhiều services, nhưng không tự phân tích nội dung S3 objects. AWS Config rules kiểm tra cấu hình (config compliance), không phân tích dữ liệu.

**❌ Đáp án C (Inspector):** Amazon Inspector là vulnerability management service cho EC2 instances và container images, không phát hiện PII trong S3.

**❌ Đáp án D (GuardDuty):** Amazon GuardDuty là threat detection service, phát hiện các hoạt động đáng ngờ (API calls, network traffic), không phân tích nội dung S3 objects.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"PII in S3 → Amazon Macie. GuardDuty = threats. Inspector = EC2 vulns. Security Hub = central security dashboard."*
