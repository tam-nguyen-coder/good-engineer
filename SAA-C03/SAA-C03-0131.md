# Question #131 - Topic 1

A company is developing a file-sharing application that will use an Amazon S3 bucket for storage. The company wants to serve all the files through an Amazon CloudFront distribution. The company does not want the files to be accessible through direct navigation to the S3 URL. What should a solutions architect do to meet these requirements?

## Options

**A.** Write individual policies for each S3 bucket to grant read permission for only CloudFront access.

**B.** Create an IAM user. Grant the user read permission to objects in the S3 bucket. Assign the user to CloudFront.

**C.** Write an S3 bucket policy that assigns the CloudFront distribution ID as the Principal and assigns the target S3 bucket as the Amazon Resource Name (ARN).

**D.** Create an origin access identity (OAI). Assign the OAI to the CloudFront distribution. Configure the S3 bucket permissions so that only the OAI has read permission.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** S3 + CloudFront, chặn direct S3 URL access.
- **Existing Resources:** S3 bucket, CloudFront distribution.
- **Current Issue/Goal:** Only allow access through CloudFront, not direct S3.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | ý nghĩa / Gợi ý |
|---------|-----------------|
| `not be accessible through direct navigation to the S3 URL` | Cần **OAI** (Origin Access Identity) |
| `CloudFront distribution` | CDN phía trước S3 |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Security / CDN
- **Constraints:** CloudFront-only access

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- **OAI (Origin Access Identity)** — virtual identity cho CloudFront distribution.
- **S3 bucket policy** chỉ cho phép OAI đọc objects.
- Users chỉ có thể access files qua CloudFront URL, không thể access trực tiếp S3 URL.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Bucket policy không thể dùng CloudFront distribution ID làm Principal trực tiếp (cần OAI).

**❌ Đáp án B:**
- IAM user assigned to CloudFront — không phải cách CloudFront hoạt động.

**❌ Đáp án C:**
- CloudFront distribution ID không thể dùng làm Principal trong bucket policy — cần OAI.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"OAI = CloudFront virtual identity. Bucket policy allow OAI only = no direct S3 access"*
