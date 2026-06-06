# Question #498 - Topic 1

A company uses Amazon S3 to store high-resolution pictures in an S3 bucket. To minimize application changes, the company stores the pictures as the latest version of an S3 object. The company needs to retain only the two most recent versions of the pictures. The company wants to reduce costs. The company has identified the S3 bucket as a large expense. Which solution will reduce the S3 costs with the LEAST operational overhead?

## Options

**A.** Use S3 Lifecycle to delete expired object versions and retain the two most recent versions.

**B.** Use an AWS Lambda function to check for older versions and delete all but the two most recent versions.

**C.** Use S3 Batch Operations to delete noncurrent object versions and retain only the two most recent versions.

**D.** Deactivate versioning on the S3 bucket and retain the two most recent versions.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** S3 bucket chứa high-resolution pictures. App dùng versioning, lưu latest version. Cần chỉ giữ 2 versions gần nhất. Muốn giảm cost.
- **Existing Resources:** S3 bucket with versioning enabled.
- **Current Issue/Goal:** Chỉ retain 2 recent versions, reduce cost, least ops overhead.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `retain only the two most recent versions` | S3 Lifecycle rule với `NewerNoncurrentVersions` = 2. |
| `least operational overhead` | S3 Lifecycle: native, không code. |
| `versioning` | Bucket đang có versioning enabled. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Least operational overhead (cost reduction)
- **Constraints:** Keep 2 most recent versions.

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- **S3 Lifecycle policy** có thể cấu hình `NoncurrentVersionExpiration` với `NewerNoncurrentVersions` = 2.
- Khi một object có hơn 2 noncurrent versions, S3 tự động xóa các versions cũ nhất.
- **Hoàn toàn native** - không cần code, không Lambda, không Batch Operations.
- Chỉ cần define lifecycle rules → S3 tự động thực thi.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- **Lambda:** Cần code, maintain function, schedule trigger → operational overhead cao hơn Lifecycle.

**❌ Đáp án C:**
- **S3 Batch Operations:** Tốt để xóa hàng loạt objects hiện tại, nhưng không phải giải pháp tự động liên tục cho future versions. Ops overhead cao hơn Lifecycle.

**❌ Đáp án D:**
- **Deactivate versioning:** Không thể "retain the two most recent versions" khi tắt versioning. Tắt versioning không xóa được versions cũ.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Keep N versions → S3 Lifecycle + NewerNoncurrentVersions. Zero code = least overhead."*
