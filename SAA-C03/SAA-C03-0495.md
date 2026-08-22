# Question #495 - Topic 1

A company is conducting an internal audit. The company wants to ensure that the data in an Amazon S3 bucket that is associated with the company's AWS Lake Formation data lake does not contain sensitive customer or employee data. The company wants to discover personally identifiable information (PII) or financial information, including passport numbers and credit card numbers. Which solution will meet these requirements?

## Options

**A.** Configure AWS Audit Manager on the account. Select the Payment Card Industry Data Security Standards (PCI DSS) for auditing.

**B.** Configure Amazon S3 Inventory on the S3 bucket Configure Amazon Athena to query the inventory.

**C.** Configure Amazon Macie to run a data discovery job that uses managed identifiers for the required data types.

**D.** Use Amazon S3 Select to run a report across the S3 bucket.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Internal audit, cần phát hiện sensitive data (PII, financial) trong S3 bucket của data lake (Lake Formation). Cần discover passport numbers, credit card numbers.
- **Existing Resources:** S3 bucket, AWS Lake Formation data lake.
- **Current Issue/Goal:** Phát hiện PII/financial data trong S3.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `discover personally identifiable information (PII)` | Amazon Macie: ML-powered data discovery for sensitive data. |
| `passport numbers and credit card numbers` | Managed identifiers trong Macie (built-in patterns). |
| `AWS Lake Formation` | Macie tích hợp với Lake Formation. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Data discovery / security
- **Constraints:** Phát hiện PII và financial data trong S3.

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- **Amazon Macie** là dịch vụ data security được thiết kế để phát hiện sensitive data trong S3.
- **Managed identifiers:** Macie có built-in patterns cho PII (passport numbers, SSN, email, v.v.) và financial data (credit card numbers, bank accounts).
- Macie dùng ML để phân loại và phát hiện sensitive data.
- Chạy **data discovery job** để scan S3 bucket và báo cáo kết quả.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- **AWS Audit Manager:** Dùng để audit compliance controls (PCI DSS, HIPAA), không phải data discovery tool để tìm PII trong objects.

**❌ Đáp án B:**
- **S3 Inventory + Athena:** Cần tạo custom queries để tìm PII. Không có ML/phân tích nội dung file. Chỉ phân tích metadata, không scan nội dung.

**❌ Đáp án D:**
- **S3 Select:** Dùng để query nội dung của một object (filter). Không thể scan toàn bộ bucket để discover PII.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"PII discovery → Amazon Macie (ML + managed identifiers). Audit Manager = compliance framework."*
