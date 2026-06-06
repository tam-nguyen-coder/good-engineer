# Question #569 - Topic 1

An Amazon EventBridge rule targets a third-party API. The third-party API has not received any incoming traffic. A solutions architect needs to determine whether the rule conditions are being met and if the rule's target is being invoked. Which solution will meet these requirements?

## Options

**A.** Check for metrics in Amazon CloudWatch in the namespace for AWS/Events.

**B.** Review events in the Amazon Simple Queue Service (Amazon SQS) dead-letter queue.

**C.** Check for the events in Amazon CloudWatch Logs.

**D.** Check the trails in AWS CloudTrail for the EventBridge events.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** EventBridge rule target một third-party API nhưng API không nhận được traffic. Cần xác định rule conditions có được đáp ứng không và target có được invoke không.
- **Existing Resources:** EventBridge rule, third-party API target.
- **Current Issue/Goal:** Debug EventBridge rule – kiểm tra rule matching và invocation.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `EventBridge rule` | Xác định event pattern và target |
| `rule conditions are being met` | Kiểm tra có events match pattern không |
| `target is being invoked` | Kiểm tra target có được gọi không |
| `CloudWatch metrics` | AWS/Events namespace chứa metrics về EventBridge |
| `Invocations` và `TriggeredRules` | CloudWatch metrics EventBridge |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most appropriate solution
- **Constraints:** Debug rule matching và target invocation

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- CloudWatch metrics trong namespace AWS/Events cung cấp metrics cho EventBridge:
  - `Invocations`: số lần target được invoke (xác định target có được gọi không)
  - `TriggeredRules`: số lần rule triggered (xác định có events match pattern không)
  - `FailedInvocations`, `ThrottledRules`, v.v.
- Nếu `Invocations` = 0, target không được gọi. Nếu `TriggeredRules` = 0, không có events match pattern.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B (SQS dead-letter queue):** SQS dead-letter queue chỉ hoạt động khi target là SQS. Ở đây target là third-party API, không phải SQS. DLQ không có events nếu rule chưa bao giờ trigger.

**❌ Đáp án C (CloudWatch Logs):** EventBridge không tự động ghi logs vào CloudWatch Logs. Phải cấu hình target là CloudWatch Logs. Nếu chưa cấu hình, không có logs.

**❌ Đáp án D (CloudTrail):** CloudTrail ghi lại API calls tạo/sửa/xóa EventBridge rules, không ghi lại việc rule được trigger hay target được invoke.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"EventBridge debugging → CloudWatch metrics (AWS/Events). Invocations & TriggeredRules. CloudTrail = API management, not rule execution."*
