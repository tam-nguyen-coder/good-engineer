# Question #227 - Topic 1

A company needs to retain its AWS CloudTrail logs for 3 years. The company is enforcing CloudTrail across a set of AWS accounts by using AWS Organizations from the parent account. The CloudTrail target S3 bucket is configured with S3 Versioning enabled. An S3 Lifecycle policy is in place to delete current objects after 3 years. After the fourth year of use of the S3 bucket, the S3 bucket metrics show that the number of objects has continued to rise. However, the number of new CloudTrail logs that are delivered to the S3 bucket has remained consistent. Which solution will delete objects that are older than 3 years in the MOST cost-effective manner?

## Options

**A.** Configure the organization's centralized CloudTrail trail to expire objects after 3 years.

**B.** Configure the S3 Lifecycle policy to delete previous versions as well as current versions.

**C.** Create an AWS Lambda function to enumerate and delete objects from Amazon S3 that are older than 3 years.

**D.** Configure the parent account as the owner of all objects that are delivered to the S3 bucket.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** CloudTrail logs in S3 with versioning. Lifecycle deletes current objects after 3 years. But object count keeps rising. New log rate consistent.
- **Existing Resources:** S3 bucket with versioning, lifecycle policy for current versions.
- **Current Issue/Goal:** Previous versions (non-current) accumulate and aren't deleted.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `S3 Versioning enabled` | Previous versions accumulate |
| `Lifecycle policy... delete current objects after 3 years` | Chỉ xoá current, không xoá previous versions |
| `number of objects has continued to rise` | Previous versions không được cleanup |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Storage / Lifecycle
- **Constraints:** Delete old non-current versions, cost-effective

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- Cần thêm lifecycle rule cho **NoncurrentVersionExpiration** — xoá previous versions sau 3 năm.
- Current lifecycle chỉ xử lý current versions → previous versions tích tụ mãi.
- Không cần Lambda — lifecycle policy rẻ nhất.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- CloudTrail trail — không có option expire objects trong S3.

**❌ Đáp án C:**
- Lambda — operational overhead, tốn chi phí hơn lifecycle policy.

**❌ Đáp án D:**
- Change owner — không giải quyết vấn đề previous versions accumulation.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"NoncurrentVersionExpiration = delete old versions. Current lifecycle = current objects only"*
