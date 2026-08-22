# Question #295 - Topic 1

An ecommerce company stores terabytes of customer data in the AWS Cloud. The data contains personally identifiable information (PII). The company wants to use the data in three applications. Only one of the applications needs to process the PII. The PII must be removed before the other two applications process the data. Which solution will meet these requirements with the LEAST operational overhead?

## Options

**A.** Store the data in an Amazon DynamoDB table. Create a proxy application layer to intercept and process the data that each application requests.

**B.** Store the data in an Amazon S3 bucket. Process and transform the data by using S3 Object Lambda before returning the data to the requesting application.

**C.** Process the data and store the transformed data in three separate Amazon S3 buckets so that each application has its own custom dataset. Point each application to its respective S3 bucket.

**D.** Process the data and store the transformed data in three separate Amazon DynamoDB tables so that each application has its own custom dataset. Point each application to its respective DynamoDB table.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Terabytes of customer data with PII, 3 apps, only 1 needs PII. PII must be removed for other 2.
- **Existing Resources:** Customer data with PII in AWS Cloud.
- **Current Issue/Goal:** PII redaction cho 2 apps, least operational overhead.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `S3 Object Lambda` | Cho phép transform dữ liệu khi được request từ S3, không cần maintain nhiều copies. |
| `least operational overhead` | Không muốn maintain nhiều datasets riêng biệt. |
| `terabytes` | Data lớn → S3 là storage phù hợp. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Least operational overhead
- **Constraints:** PII redaction, 3 applications, 1 needs PII

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- S3 Object Lambda: dùng Lambda function để tự động redact PII khi data được request từ S3 → chỉ cần 1 S3 bucket duy nhất.
- Các application request data qua S3 Object Lambda endpoint: app cần PII nhận dữ liệu gốc, 2 app còn lại nhận dữ liệu đã redact.
- Không cần maintain nhiều bản copy riêng biệt → operational overhead thấp nhất.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- DynamoDB không phù hợp cho terabytes data (giới hạn 400 KB/item, chi phí cao cho data lớn). Proxy layer tăng operational overhead.

**❌ Đáp án C:**
- Phải maintain 3 S3 buckets riêng biệt → data duplication, cần sync khi data gốc thay đổi → operational overhead cao.

**❌ Đáp án D:**
- DynamoDB không phù hợp cho terabytes data. 3 tables riêng → data duplication cao.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"S3 Object Lambda = transform on-the-fly khi get data. Không cần duplicate data. Operational overhead thấp nhất."*
