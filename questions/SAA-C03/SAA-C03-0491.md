# Question #491 - Topic 1

A solutions architect is designing an asynchronous application to process credit card data validation requests for a bank. The application must be secure and be able to process each request at least once. Which solution will meet these requirements MOST cost-effectively?

## Options

**A.** Use AWS Lambda event source mapping. Set Amazon Simple Queue Service (Amazon SQS) standard queues as the event source. Use AWS Key Management Service (SSE-KMS) for encryption. Add the kms:Decrypt permission for the Lambda execution role.

**B.** Use AWS Lambda event source mapping. Use Amazon Simple Queue Service (Amazon SQS) FIFO queues as the event source. Use SQS managed encryption keys (SSE-SQS) for encryption. Add the encryption key invocation permission for the Lambda function.

**C.** Use the AWS Lambda event source mapping. Set Amazon Simple Queue Service (Amazon SQS) FIFO queues as the event source. Use AWS KMS keys (SSE-KMS). Add the kms:Decrypt permission for the Lambda execution role.

**D.** Use the AWS Lambda event source mapping. Set Amazon Simple Queue Service (Amazon SQS) standard queues as the event source. Use AWS KMS keys (SSE-KMS) for encryption. Add the encryption key invocation permission for the Lambda function.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Bank processing credit card validation requests asynchronously. Cần "at least once" processing và secure.
- **Existing Resources:** N/A (greenfield).
- **Current Issue/Goal:** Chọn SQS queue type + encryption method cost-effectively.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `at least once` | SQS Standard queue: at-least-once delivery. FIFO: exactly-once (đắt hơn). |
| `secure` | SSE-KMS (AWS KMS) cho encryption. |
| `credit card data` | Dữ liệu nhạy cảm → cần encryption mạnh (KMS). |
| `most cost-effectively` | Standard queue rẻ hơn FIFO. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most cost-effective + secure
- **Constraints:** At-least-once processing, secure encryption.

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- **SQS Standard queue:** Cung cấp at-least-once delivery (FIFO là exactly-once, không cần thiết và đắt hơn).
- **SSE-KMS:** Dùng AWS KMS keys để encrypt data at rest → đáp ứng yêu cầu security cho credit card data.
- **kms:Decrypt permission** cho Lambda execution role → Lambda có thể decrypt messages từ SQS.
- Standard queue rẻ hơn FIFO → cost-effective.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- **FIFO queue:** exactly-once, không cần thiết cho use case này và đắt hơn Standard.
- **SSE-SQS:** SQS managed keys, ít secure hơn SSE-KMS. Không phù hợp cho credit card data.

**❌ Đáp án C:**
- **FIFO queue:** Chi phí cao hơn, không cần thiết (at-least-once đã đủ).

**❌ Đáp án D:**
- **Standard + SSE-KMS:** Đúng về queue type và encryption, nhưng "encryption key invocation permission" không phải permission chính xác. Lambda cần `kms:Decrypt` permission để decrypt messages.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"At-least-once → Standard queue (rẻ hơn). Secure → SSE-KMS. kms:Decrypt cho Lambda."*
