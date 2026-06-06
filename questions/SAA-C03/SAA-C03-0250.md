# Question #250 - Topic 1

A company's security team requests that network traffic be captured in VPC Flow Logs. The logs will be frequently accessed for 90 days and then accessed intermittently. What should a solutions architect do to meet these requirements when configuring the logs?

## Options

**A.** Use Amazon CloudWatch as the target. Set the CloudWatch log group with an expiration of 90 days.

**B.** Use Amazon Kinesis as the target. Configure the Kinesis stream to always retain the logs for 90 days.

**C.** Use AWS CloudTrail as the target. Configure CloudTrail to save to an Amazon S3 bucket, and enable S3 Intelligent-Tiering.

**D.** Use Amazon S3 as the target. Enable an S3 Lifecycle policy to transition the logs to S3 Standard-Infrequent Access (S3 Standard-IA) after 90 days.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** VPC Flow Logs. Frequently accessed for 90 days, then intermittently.
- **Existing Resources:** VPC.
- **Current Issue/Goal:** Cost-effective log storage with lifecycle.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `frequently accessed for 90 days` | **S3 Standard** cho 90 ngày đầu |
| `then accessed intermittently` | Transition to **S3 Standard-IA** (cheaper, still accessible) |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Storage / Lifecycle
- **Constraints:** 90 days frequent, then intermittent

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- VPC Flow Logs → **S3 target**.
- **Lifecycle policy** — transition từ S3 Standard → S3 Standard-IA sau 90 ngày.
- Standard-IA rẻ hơn cho intermittent access, nhưng vẫn milliseconds retrieval.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- CloudWatch Logs 90-day expiration — delete logs sau 90 ngày, không thể access intermittently.

**❌ Đáp án B:**
- Kinesis — không phải target hợp lệ cho VPC Flow Logs.

**❌ Đáp án C:**
- CloudTrail — không phải target cho VPC Flow Logs.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"S3 + Lifecycle = standard → IA after 90 days. CloudWatch expiration = delete (no access). Kinesis = wrong target"*
