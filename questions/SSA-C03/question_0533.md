# Question #533 - Topic 1

A company stores data in Amazon S3. According to regulations, the data must not contain personally identifiable information (PII). The company recently discovered that S3 buckets have some objects that contain PII. The company needs to automatically detect PII in S3 buckets and to notify the company's security team. Which solution will meet these requirements?

## Options

**A.** Use Amazon Macie. Create an Amazon EventBridge rule to filter the SensitiveData event type from Macie findings and to send an Amazon Simple Notification Service (Amazon SNS) notification to the security team.

**B.** Use Amazon GuardDuty. Create an Amazon EventBridge rule to filter the CRITICAL event type from GuardDuty findings and to send an Amazon Simple Notification Service (Amazon SNS) notification to the security team.

**C.** Use Amazon Macie. Create an Amazon EventBridge rule to filter the SensitiveData:S3Object/Personal event type from Macie findings and to send an Amazon Simple Queue Service (Amazon SQS) notification to the security team.

**D.** Use Amazon GuardDuty. Create an Amazon EventBridge rule to filter the CRITICAL event type from GuardDuty findings and to send an Amazon Simple Queue Service (Amazon SQS) notification to the security team.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Cần tự động detect PII trong S3 buckets và notify security team.
- **Existing Resources:** S3 buckets.
- **Current Issue/Goal:** Auto detect PII + notification.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `personally identifiable information (PII)` | Amazon Macie: dịch vụ chuyên phát hiện PII trong S3 |
| `Amazon Macie` | Data security service dùng ML để detect sensitive data trong S3 |
| `automatically detect` | Macie quét S3 buckets tự động |
| `notify` | EventBridge + SNS → notification đến security team |
| `SensitiveData event type` | Macie findings bao gồm `SensitiveData:S3Object/Personal` |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Security / Compliance
- **Constraints:** Auto detect PII, S3 buckets, notify security team

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- Amazon Macie là dịch vụ chuyên biệt để discover và protect sensitive data (PII) trong S3.
- Macie dùng ML pattern matching để phát hiện PII.
- Macie findings được gửi đến Amazon EventBridge.
- EventBridge rule filter `SensitiveData` event type → trigger SNS notification đến security team.
- Option A đúng vì dùng đúng service (Macie) và đúng notification mechanism (EventBridge → SNS).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Amazon GuardDuty dùng để detect các mối đe dọa bảo mật (threat detection), không phải PII detection.
- GuardDuty không quét S3 objects content.

**❌ Đáp án C:**
- `SensitiveData:S3Object/Personal` là finding type chính xác của Macie cho PII in S3 objects, Tuy nhiên option dùng SQS để notify security team. SQS là queue, không push notification đến người dùng. Security team cần poll queue → không hiệu quả bằng SNS push notification.
- So với option A, option C dùng SQS kém hơn SNS cho use case notification.

**❌ Đáp án D:**
- GuardDuty không detect PII trong S3 objects.

## 6. MẸO GHI NHỚ (MEMORY HOOK)
🧠 *"PII in S3 = Amazon Macie + EventBridge + SNS. GuardDuty = threat detection, không phải PII."*
