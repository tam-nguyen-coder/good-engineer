# Question #316 - Topic 1

A company uses an Amazon EC2 instance to run a script to poll for and process messages in an Amazon Simple Queue Service (Amazon SQS) queue. The company wants to reduce operational costs while maintaining its ability to process a growing number of messages that are added to the queue. What should a solutions architect recommend to meet these requirements?

## Options

**A.** Increase the size of the EC2 instance to process messages faster.

**B.** Use Amazon EventBridge to turn off the EC2 instance when the instance is underutilized.

**C.** Migrate the script on the EC2 instance to an AWS Lambda function with the appropriate runtime.

**D.** Use AWS Systems Manager Run Command to run the script on demand.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** EC2 instance polling SQS queue. Cần giảm cost và scale với số lượng messages tăng.
- **Existing Resources:** EC2 instance, SQS queue.
- **Current Issue/Goal:** Reduce cost, handle growing message volume.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `reduce operational costs` | EC2 chạy 24/7 tốn kém → Lambda chỉ trả khi chạy. |
| `process a growing number of messages` | Lambda auto-scale với số lượng messages (SQS là event source cho Lambda). |
| `Lambda with SQS` | Lambda tự động poll SQS, scale concurrency dựa trên số messages. |
| `operational costs` | Lambda: pay per invocation + duration, không cost khi idle. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Reduce costs + maintain processing ability
- **Constraints:** Growing message volume, SQS-based processing

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- Lambda tự động poll SQS messages và scale concurrency khi số lượng messages tăng.
- Không tốn chi phí khi queue rỗng (không như EC2 chạy 24/7).
- Lambda pay per request + duration → tiết kiệm hơn EC2.
- Không cần quản lý server.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Tăng instance size → tăng cost, không giải quyết scaling khi message volume tăng (vẫn single instance).

**❌ Đáp án B:**
- EventBridge không thể turn on/off EC2 dựa trên utilization một cách hiệu quả. EC2 vẫn tốn cost khi chạy.

**❌ Đáp án D:**
- Systems Manager Run Command chạy script trên EC2, không giảm cost (vẫn cần EC2 chạy 24/7).

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"EC2 poll SQS → migrate to Lambda (serverless, auto-scale, pay per use). EC2 = cost even when idle."*
