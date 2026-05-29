# Question #550 - Topic 1

A company is using AWS Key Management Service (AWS KMS) keys to encrypt AWS Lambda environment variables. A solutions architect needs to ensure that the required permissions are in place to decrypt and use the environment variables. Which steps must the solutions architect take to implement the correct permissions? (Choose two.)

## Options

**A.** Add AWS KMS permissions in the Lambda resource policy.

**B.** Add AWS KMS permissions in the Lambda execution role.

**C.** Add AWS KMS permissions in the Lambda function policy.

**D.** Allow the Lambda execution role in the AWS KMS key policy.

**E.** Allow the Lambda resource policy in the AWS KMS key policy.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Công ty dùng KMS keys để encrypt Lambda environment variables. Cần đảm bảo permissions đúng để decrypt và sử dụng environment variables.
- **Existing Resources:** Lambda function, KMS key.
- **Current Issue/Goal:** Thiết lập permissions để Lambda có thể decrypt KMS-encrypted environment variables.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `AWS KMS` | Key Management Service – quản lý encryption keys |
| `Lambda environment variables` | Biến môi trường trong Lambda |
| `decrypt` | Cần quyền KMS Decrypt |
| `Lambda execution role` | IAM Role mà Lambda assume khi chạy |
| `AWS KMS key policy` | Policy gắn trực tiếp vào KMS key |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Multi-select (2 answers)
- **Constraints:** Permissions để Lambda decrypt và dùng environment variables

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B, D**

**Giải thích:**
- **B (KMS permissions trong Lambda execution role):** Lambda execution role cần có quyền `kms:Decrypt` (và có thể `kms:GenerateDataKey` nếu encrypt). Đây là IAM role mà Lambda assume, nên các KMS permissions phải được thêm vào role này.
- **D (Allow Lambda execution role trong KMS key policy):** KMS key policy là một loại resource policy gắn trực tiếp vào KMS key. Để một IAM role (Lambda execution role) có thể dùng KMS key, role đó phải được allowed trong KMS key policy, hoặc KMS key policy phải cho phép IAM policies của account kiểm soát access.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A (KMS permissions trong Lambda resource policy):** Lambda resource policy (function policy) dùng để kiểm soát ai có thể invoke Lambda function, không phải permissions mà Lambda có khi thực thi.

**❌ Đáp án C (KMS permissions trong Lambda function policy):** "Lambda function policy" cũng là resource policy (giống A). Không liên quan đến KMS decrypt permissions.

**❌ Đáp án E (Allow Lambda resource policy trong KMS key policy):** Lambda resource policy không phải IAM principal. KMS key policy cần IAM principals (users, roles), không phải Lambda resource policy.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Lambda + KMS: (1) Add KMS permissions to Lambda execution role. (2) Allow that role in KMS key policy. Two sides of the same coin."*
