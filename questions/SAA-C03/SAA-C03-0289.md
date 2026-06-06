# Question #289 - Topic 1

A company has an AWS Lambda function that needs read access to an Amazon S3 bucket that is located in the same AWS account. Which solution will meet these requirements in the MOST secure manner?

## Options

**A.** Apply an S3 bucket policy that grants read access to the S3 bucket.

**B.** Apply an IAM role to the Lambda function. Apply an IAM policy to the role to grant read access to the S3 bucket.

**C.** Embed an access key and a secret key in the Lambda function's code to hardcode the required IAM permissions for read access to the S3 bucket.

**D.** Apply an IAM role to the Lambda function. Apply an IAM policy to the role to grant read access to all S3 buckets in the account.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Lambda function cần read access tới S3 bucket cùng account.
- **Existing Resources:** Lambda function, S3 bucket.
- **Current Issue/Goal:** Grant read access most secure way.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `same AWS account` | Cả Lambda và S3 cùng account → không cần cross-account, có thể dùng IAM role. |
| `most secure manner` | Least privilege, không hardcode credentials. |
| `IAM role` | Best practice: gán IAM role cho Lambda để cấp permissions tạm thời (through temporary credentials). |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most secure manner
- **Constraints:** Same account, read-only access, Lambda

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- Gán IAM role cho Lambda function → AWS tự động cung cấp temporary credentials thông qua STS.
- IAM policy attached vào role chỉ grant read access tới specific S3 bucket (least privilege).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- S3 bucket policy cũng được nhưng phức tạp hơn khi kết hợp với Principal và có thể cấp quyền rộng hơn. Với cùng account, IAM role trên Lambda là best practice.

**❌ Đáp án C:**
- Hardcode access key / secret key trong code là anti-pattern (kém bảo mật, khó rotate, exposed trong code).

**❌ Đáp án D:**
- Grant read access to ALL S3 buckets → violation of least privilege principle (quá rộng).

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Lambda + S3 cùng account → IAM role (temporary creds). Không hardcode keys, không grant all buckets."*
