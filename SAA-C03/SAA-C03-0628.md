# Question #628 - Topic 1

A global company runs its applications in multiple AWS accounts in AWS Organizations. The company's applications use multipart uploads to upload data to multiple Amazon S3 buckets across AWS Regions. The company wants to report on incomplete multipart uploads for cost compliance purposes. Which solution will meet these requirements with the LEAST operational overhead?

## Options

**A.** Configure AWS Config with a rule to report the incomplete multipart upload object count.

**B.** Create a service control policy (SCP) to report the incomplete multipart upload object count.

**C.** Configure S3 Storage Lens to report the incomplete multipart upload object count.

**D.** Create an S3 Multi-Region Access Point to report the incomplete multipart upload object count.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Multiple AWS accounts (Organizations), multipart uploads to S3 buckets across regions. Cần report incomplete multipart uploads cho cost compliance.
- **Existing Resources:** AWS Organizations, multiple accounts, S3 buckets.
- **Current Issue/Goal:** Report incomplete multipart uploads across accounts/regions với least overhead.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `multiple AWS accounts` | Cần cross-account visibility. |
| `across AWS Regions` | Cần global view. |
| `incomplete multipart uploads` | S3 Storage Lens có metric cho incomplete multipart uploads. |
| `cost compliance` | Incomplete multipart uploads tốn storage cost. |
| `S3 Storage Lens` | Cung cấp organization-level metrics và dashboards, bao gồm incomplete multipart uploads. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Least operational overhead
- **Constraints:** Multiple accounts, multiple regions, incomplete multipart uploads

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- S3 Storage Lens: cung cấp centralized visibility cho S3 usage và activity across accounts và regions.
- Có sẵn metric "IncompleteMultipartUploads" → reporting sẵn có, không cần custom code.
- Hỗ trợ AWS Organizations → xem dữ liệu từ tất cả member accounts.
- Operational overhead thấp nhất: chỉ cần enable và view dashboard.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- AWS Config: theo dõi resource configuration changes, không có built-in reporting cho incomplete multipart uploads. Cần custom rule.

**❌ Đáp án B:**
- SCP: dùng để restrict permissions, không phải reporting tool. Không thể report object count.

**❌ Đáp án D:**
- Multi-Region Access Point: cung cấp single endpoint cho S3 buckets across regions, không phải reporting tool.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"S3 Storage Lens = centralized metrics cho S3 across accounts/regions, có incomplete multipart upload metric."*
