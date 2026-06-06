# Question #364 - Topic 1

A hospital is designing a new application that gathers symptoms from patients. The hospital has decided to use Amazon Simple Queue Service (Amazon SQS) and Amazon Simple Notification Service (Amazon SNS) in the architecture. A solutions architect is reviewing the infrastructure design. Data must be encrypted at rest and in transit. Only authorized personnel of the hospital should be able to access the data. Which combination of steps should the solutions architect take to meet these requirements? (Choose two.)

## Options

**A.** Turn on server-side encryption on the SQS components. Update the default key policy to restrict key usage to a set of authorized principals.

**B.** Turn on server-side encryption on the SNS components by using an AWS Key Management Service (AWS KMS) customer managed key. Apply a key policy to restrict key usage to a set of authorized principals.

**C.** Turn on encryption on the SNS components. Update the default key policy to restrict key usage to a set of authorized principals. Set a condition in the topic policy to allow only encrypted connections over TLS.

**D.** Turn on server-side encryption on the SQS components by using an AWS Key Management Service (AWS KMS) customer managed key. Apply a key policy to restrict key usage to a set of authorized principals. Set a condition in the queue policy to allow only encrypted connections over TLS.

**E.** Turn on server-side encryption on the SQS components by using an AWS Key Management Service (AWS KMS) customer managed key. Apply an IAM policy to restrict key usage to a set of authorized principals. Set a condition in the queue policy to allow only encrypted connections over TLS.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Hospital app dùng SQS + SNS. Cần encryption at rest + in transit. Only authorized personnel access.
- **Existing Resources:** SQS, SNS (in design).
- **Current Issue/Goal:** Encrypt data + access control cho cả SQS và SNS.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `encrypted at rest` | SSE with KMS cho SQS và SNS. |
| `encrypted in transit` | TLS condition trong queue/topic policy. |
| `authorized personnel` | KMS key policy restrict key usage to authorized principals. |
| `customer managed key` | Cho phép custom key policy (restrict to specific IAM roles/users). |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Choose two
- **Constraints:** SQS + SNS encryption at rest + in transit + access control

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B (SNS) và D (SQS)**

**Giải thích:**
- **B (SNS):** SSE with KMS CMK + key policy restrict to authorized principals.
- **D (SQS):** SSE with KMS CMK + key policy restrict + TLS condition in queue policy (in transit).
- Cả 2 cover encryption at rest (KMS), in transit (TLS), và access control (key policy).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Default key policy không restrict authorized principals → không đáp ứng access control.

**❌ Đáp án C:**
- Thiếu TLS condition cho SNS topics. SNS default encryption không rõ ràng (không chỉ định KMS CMK).

**❌ Đáp án E:**
- IAM policy không thể restrict KMS key usage (cần key policy, không phải IAM policy).

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"SNS encryption → SSE-KMS + key policy. SQS encryption → SSE-KMS + key policy + TLS. Key policy ≠ IAM policy."*
