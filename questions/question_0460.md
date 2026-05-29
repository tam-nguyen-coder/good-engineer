# Question #460 - Topic 1

A company wants to securely exchange data between its software as a service (SaaS) application Salesforce account and Amazon S3. The company must encrypt the data at rest by using AWS Key Management Service (AWS KMS) customer managed keys (CMKs). The company must also encrypt the data in transit. The company has enabled API access for the Salesforce account.

## Options

**A.** Create AWS Lambda functions to transfer the data securely from Salesforce to Amazon S3.

**B.** Create an AWS Step Functions workflow. Define the task to transfer the data securely from Salesforce to Amazon S3.

**C.** Create Amazon AppFlow flows to transfer the data securely from Salesforce to Amazon S3.

**D.** Create a custom connector for Salesforce to transfer the data securely from Salesforce to Amazon S3.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Salesforce → S3 data transfer. KMS CMK encryption at rest + encryption in transit. API access enabled.
- **Existing Resources:** Salesforce account, S3 bucket.
- **Current Issue/Goal:** Secure data transfer with KMS encryption.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `Salesforce` | SaaS application. |
| `Amazon AppFlow` | Managed integration between SaaS apps and AWS services. |
| `KMS CMK` | AppFlow supports KMS encryption. |
| `encrypt in transit` | AppFlow: HTTPS/TLS automatically. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Integration / Data transfer
- **Constraints:** Salesforce to S3, KMS encryption, in-transit encryption

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- Amazon AppFlow: managed service để transfer data between SaaS apps (Salesforce) and AWS (S3).
- Hỗ trợ KMS CMK cho encryption at rest.
- HTTPS/TLS cho encryption in transit.
- No code, no server management.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Lambda: custom code, cần quản lý authentication, error handling → operational overhead.

**❌ Đáp án B:**
- Step Functions: orchestration, vẫn cần Lambda tasks để transfer → more overhead.

**❌ Đáp án D:**
- Custom connector: tự xây dựng → nhiều effort nhất.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Salesforce → S3 = Amazon AppFlow (managed, KMS, no code)."*