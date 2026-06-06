# Question #478 - Topic 1

A law firm needs to share information with the public. The information includes hundreds of files that must be publicly readable. Modifications or deletions of the files by anyone before a designated future date are prohibited. Which solution will meet these requirements in the MOST secure way?

## Options

**A.** Upload all files to an Amazon S3 bucket that is configured for static website hosting. Grant read-only IAM permissions to any AWS principals that access the S3 bucket until the designated date.

**B.** Create a new Amazon S3 bucket with S3 Versioning enabled. Use S3 Object Lock with a retention period in accordance with the designated date. Configure the S3 bucket for static website hosting. Set an S3 bucket policy to allow read-only access to the objects.

**C.** Create a new Amazon S3 bucket with S3 Versioning enabled. Configure an event trigger to run an AWS Lambda function in case of object modification or deletion. Configure the Lambda function to replace the objects with the original versions from a private S3 bucket.

**D.** Upload all files to an Amazon S3 bucket that is configured for static website hosting. Select the folder that contains the files. Use S3 Object Lock with a retention period in accordance with the designated date. Grant read-only IAM permissions to any AWS principals that access the S3 bucket.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Law firm public information sharing, files publicly readable, không cho modify/delete trước future date.
- **Existing Resources:** Files cần share.
- **Current Issue/Goal:** MOST secure way, prevent modification/deletion until future date.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `publicly readable` | Cần S3 bucket policy cho phép public read. |
| `Modifications or deletions prohibited before designated future date` | Cần S3 Object Lock (WORM model). |
| `S3 Object Lock` | Prevent objects from being deleted/modified trong retention period. Yêu cầu Versioning enabled. |
| `MOST secure` | Object Lock là native AWS solution, không dựa vào reactive Lambda. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most secure
- **Constraints:** Public read, prevent write/delete until future date

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- S3 Versioning: cần enable trước khi dùng Object Lock.
- S3 Object Lock với retention mode (COMPLIANCE): không ai có thể overwrite/delete objects kể cả root user.
- S3 bucket policy cho phép `s3:GetObject` cho public (read-only).
- Static website hosting để public access files.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Chỉ dùng IAM permissions: không ngăn được modification/deletion bởi AWS account owner. IAM grant cho "any AWS principals" không ngăn người có quyền cao hơn.

**❌ Đáp án C:**
- Lambda reactive: không bảo vệ được. Nếu object bị delete trước khi Lambda chạy, hoặc nếu Lambda bị lỗi, data sẽ mất.
- Không phải "most secure" vì dựa vào event-driven recovery.

**❌ Đáp án D:**
- "Select the folder that contains the files. Use S3 Object Lock" → Object Lock áp dụng ở bucket level hoặc object level, không phải folder level.
- IAM permissions cho "any AWS principals" không đủ mạnh để ngăn chặn deletion nếu không có Object Lock.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Không cho sửa/xóa file trước date → S3 Object Lock (WORM). Versioning bắt buộc. Lambda reactive = không an toàn."*
