# Question #517 - Topic 1

A company wants to send all AWS Systems Manager Session Manager logs to an Amazon S3 bucket for archival purposes. Which solution will meet this requirement with the MOST operational efficiency?

## Options

**A.** Enable S3 logging in the Systems Manager console. Choose an S3 bucket to send the session data to.

**B.** Install the Amazon CloudWatch agent. Push all logs to a CloudWatch log group. Export the logs to an S3 bucket from the group for archival purposes.

**C.** Create a Systems Manager document to upload all server logs to a central S3 bucket. Use Amazon EventBridge to run the Systems Manager document against all servers that are in the account daily.

**D.** Install an Amazon CloudWatch agent. Push all logs to a CloudWatch log group. Create a CloudWatch logs subscription that pushes any incoming log events to an Amazon Kinesis Data Firehose delivery stream. Set Amazon S3 as the destination.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Cần gửi Session Manager logs (SSM) từ tất cả sessions vào S3 để archive.
- **Existing Resources:** AWS Systems Manager Session Manager, S3 bucket.
- **Current Issue/Goal:** Gửi logs từ Session Manager về S3, operational efficiency cao nhất.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `Systems Manager Session Manager logs` | Session Manager có built-in integration với S3 và CloudWatch Logs. |
| `MOST operational efficiency` | Dùng tính năng có sẵn, không cần agent hay custom code. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most operational efficiency
- **Constraints:** Session Manager logs → S3

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- Systems Manager Session Manager có tích hợp sẵn để gửi logs trực tiếp đến S3 bucket hoặc CloudWatch Logs.
- Chỉ cần enable trong Systems Manager console, chọn S3 bucket → logs tự động được ghi vào S3.
- Không cần cài đặt CloudWatch agent, không cần Lambda, không cần KDF → operational efficiency cao nhất.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Phải cài CloudWatch agent trên mỗi EC2 → operational overhead cao.
- Export từ CloudWatch Logs sang S3 không phải real-time và cần thao tác thủ công hoặc script.

**❌ Đáp án C:**
- Tự tạo SSM document + EventBridge để collect logs → phức tạp, cần custom development.
- Không tận dụng built-in integration của Session Manager.

**❌ Đáp án D:**
- CloudWatch agent + subscription + KDF → pipeline quá phức tạp. Session Manager đã support sẵn ghi trực tiếp vào S3.
- Operational overhead cao nhất.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Session Manager logs → enable S3 logging directly in SSM console. Không cần agent, KDF hay Lambda."*
