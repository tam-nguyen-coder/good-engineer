# Question #426 - Topic 1

A company needs to store data from its healthcare application. The application's data frequently changes. A new regulation requires audit access at all levels of the stored data. The company hosts the application on an on-premises infrastructure that is running out of storage capacity. A solutions architect must securely migrate the existing data to AWS while satisfying the new regulation. Which solution will meet these requirements?

## Options

**A.** Use AWS DataSync to move the existing data to Amazon S3. Use AWS CloudTrail to log data events.

**B.** Use AWS Snowcone to move the existing data to Amazon S3. Use AWS CloudTrail to log management events.

**C.** Use Amazon S3 Transfer Acceleration to move the existing data to Amazon S3. Use AWS CloudTrail to log data events.

**D.** Use AWS Storage Gateway to move the existing data to Amazon S3. Use AWS CloudTrail to log management events.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Healthcare app, data frequently changes. Need audit at all levels. Migrate from on-prem (out of storage).
- **Existing Resources:** On-prem healthcare app.
- **Current Issue/Goal:** Securely migrate + enable audit logging.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `audit access at all levels` | CloudTrail data events (object-level: GetObject, PutObject, etc.). |
| `data frequently changes` | S3 object versioning. |
| `migrate data` | DataSync: efficient, automated data transfer. |
| `CloudTrail data events` | Log s3:GetObject, s3:PutObject, s3:DeleteObject. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Migration / Compliance
- **Constraints:** Secure migration, audit at all levels

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- DataSync: automated, encrypted migration từ on-prem to S3.
- CloudTrail data events: log object-level S3 operations (Get, Put, Delete) → audit access at all levels.
- S3 có thể dùng versioning để track changes.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Snowcone: phù hợp cho offline migration nhưng không cần thiết nếu có network. Management events không log object-level access.

**❌ Đáp án C:**
- S3 Transfer Acceleration: tăng tốc upload, không phải migration tool cho existing data từ on-prem.

**❌ Đáp án D:**
- Storage Gateway: có thể dùng làm hybrid storage, nhưng management events không đủ cho audit object-level.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Audit object-level S3 → CloudTrail data events. Management events = control plane only."*