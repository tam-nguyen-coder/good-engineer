# Question #403 - Topic 1

A developer has an application that uses an AWS Lambda function to upload files to Amazon S3 and needs the required permissions to perform the task. The developer already has an IAM user with valid IAM credentials required for Amazon S3. What should a solutions architect do to grant the permissions?

## Options

**A.** Add required IAM permissions in the resource policy of the Lambda function.

**B.** Create a signed request using the existing IAM credentials in the Lambda function.

**C.** Create a new IAM user and use the existing IAM credentials in the Lambda function.

**D.** Create an IAM execution role with the required permissions and attach the IAM role to the Lambda function.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Lambda function needs S3 upload permissions. Developer has IAM user with S3 credentials.
- **Existing Resources:** Lambda function, IAM user.
- **Current Issue/Goal:** Grant Lambda permissions to upload to S3.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `Lambda function` | Runs under an IAM execution role (service role). |
| `permissions` | Lambda execution role, không dùng IAM user credentials. |
| `execution role` | IAM role mà Lambda assume khi chạy. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Security / Permissions
- **Constraints:** Grant Lambda permission to upload S3

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- Lambda execution role: IAM role gán policy với S3 upload permissions → Lambda assume role này khi chạy.
- Best practice: service dùng role, không hardcode credentials.
- Developer's IAM user credentials không liên quan.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Lambda resource policy: kiểm soát AI/event nào có thể invoke Lambda, không phải permissions để Lambda gọi services khác.

**❌ Đáp án B:**
- Signed request dùng IAM credentials → không best practice, cần quản lý credentials trong code.

**❌ Đáp án C:**
- Tạo new IAM user + nhúng credentials vào code → security risk, không scalable.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Lambda permissions → IAM execution role. Not resource policy, not user credentials."*

