# Question #534 - Topic 1

A company wants to build a logging solution for its multiple AWS accounts. The company currently stores the logs from all accounts in a centralized account. The company has created an Amazon S3 bucket in the centralized account to store the VPC flow logs and AWS CloudTrail logs. All logs must be highly available for 30 days for frequent analysis, retained for an additional 60 days for backup purposes, and deleted 90 days after creation. Which solution will meet these requirements MOST cost-effectively?

## Options

**A.** Transition objects to the S3 Standard storage class 30 days after creation. Write an expiration action that directs Amazon S3 to delete objects after 90 days.

**B.** Transition objects to the S3 Standard-Infrequent Access (S3 Standard-IA) storage class 30 days after creation. Move all objects to the S3 Glacier Flexible Retrieval storage class after 90 days. Write an expiration action that directs Amazon S3 to delete objects after 90 days.

**C.** Transition objects to the S3 Glacier Flexible Retrieval storage class 30 days after creation. Write an expiration action that directs Amazon S3 to delete objects after 90 days.

**D.** Transition objects to the S3 One Zone-Infrequent Access (S3 One Zone-IA) storage class 30 days after creation. Move all objects to the S3 Glacier Flexible Retrieval storage class after 90 days. Write an expiration action that directs Amazon S3 to delete objects after 90 days.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Centralized S3 bucket chứa VPC Flow Logs + CloudTrail logs từ nhiều accounts.
- **Existing Resources:** S3 bucket.
- **Current Issue/Goal:** Lifecycle: 30 days HA (frequent analysis) → next 60 days backup → delete after 90 days. Cost-effective.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `highly available for 30 days` | Cần S3 Standard hoặc Standard-IA (multi-AZ) |
| `frequent analysis` | 30 ngày đầu cần truy cập thường xuyên |
| `retained for additional 60 days for backup` | 60 ngày tiếp theo chỉ cần backup, ít truy cập |
| `deleted 90 days after creation` | Xóa sau 90 ngày |
| `most cost-effectively` | S3 Standard-IA rẻ hơn Standard cho data ít truy cập |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most cost-effective (lifecycle)
- **Constraints:** 30 days HA + 60 days backup → delete day 90

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- Day 0-30: cần truy cập thường xuyên → S3 Standard (hoặc Standard-IA).
- Transition to S3 Standard-IA after 30 days → tiết kiệm chi phí cho 60 ngày backup tiếp theo (ít truy cập).
- Transition to S3 Glacier Flexible Retrieval after 90 days → nhưng option B nói "Move all objects to Glacier after 90 days" và "delete after 90 days" → mâu thuẫn. Thực tế cần chú ý: Glacier không cần vì delete ở day 90. Nhưng trong các option, B là tốt nhất vì:
  - Day 0-30: S3 Standard (mặc định)
  - Day 30: transition to Standard-IA → tiết kiệm cost
  - Day 90: expiration → delete
  - S3 Standard-IA vẫn highly available (multi-AZ), rẻ hơn Standard.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Transition to S3 Standard after 30 days → không có ý nghĩa (Standard là default storage class khi upload).
- Không chuyển xuống class rẻ hơn → chi phí cao hơn.

**❌ Đáp án C:**
- Transition to Glacier after 30 days → không phù hợp vì 30 ngày đầu cần frequent analysis (Glacier retrieval latency cao).
- Glacier chỉ nên dùng cho archive, không phải cho backup 60 ngày.

**❌ Đáp án D:**
- S3 One Zone-IA: không highly available (chỉ 1 AZ). Yêu cầu "highly available for 30 days" → One Zone-IA không đáp ứng.
- Glacier after 90 days + delete same time → mâu thuẫn.

## 6. MẸO GHI NHỚ (MEMORY HOOK)
🧠 *"30 days Standard/Std-IA (HA) → 60 days Std-IA (backup) → delete day 90. Standard-IA = rẻ + multi-AZ."*
