# Question #201 - Topic 1

A company is developing a marketing communications service that targets mobile app users. The company needs to send confirmation messages with Short Message Service (SMS) to its users. The users must be able to reply to the SMS messages. The company must store the responses for a year for analysis. What should a solutions architect do to meet these requirements?

## Options

**A.** Create an Amazon Connect contact flow to send the SMS messages. Use AWS Lambda to process the responses.

**B.** Build an Amazon Pinpoint journey. Configure Amazon Pinpoint to send events to an Amazon Kinesis data stream for analysis and archiving.

**C.** Use Amazon Simple Queue Service (Amazon SQS) to distribute the SMS messages. Use AWS Lambda to process the responses.

**D.** Create an Amazon Simple Notification Service (Amazon SNS) FIFO topic. Subscribe an Amazon Kinesis data stream to the SNS topic for analysis and archiving.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Marketing communications via SMS, users reply, store responses for 1 year for analysis.
- **Existing Resources:** Mobile app users.
- **Current Issue/Goal:** SMS sending + response collection + analytics.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `marketing communications service` | **Amazon Pinpoint** (targeted campaigns) |
| `SMS` | Pinpoint supports SMS channels |
| `store the responses for a year for analysis` | **Kinesis** data stream → analytics |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Marketing / Messaging
- **Constraints:** SMS, 2-way, analytics

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- **Amazon Pinpoint** — dịch vụ marketing campaigns, hỗ trợ SMS, email, push notifications.
- Pinpoint journey — thiết lập luồng gửi SMS, nhận replies.
- Pinpoint ghi events vào **Kinesis** → lưu trữ và phân tích.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Amazon Connect — contact center, không phải marketing campaign.

**❌ Đáp án C:**
- SQS — message queue, không thể gửi SMS trực tiếp.

**❌ Đáp án D:**
- SNS FIFO — không hỗ trợ SMS (SMS chỉ hỗ trợ Standard topic).

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Pinpoint = marketing campaigns (SMS/email/push). Connect = contact center. SNS = notifications"*
