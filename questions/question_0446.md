# Question #446 - Topic 1

A company stores data in PDF format in an Amazon S3 bucket. The company must follow a legal requirement to retain all new and existing data in Amazon S3 for 7 years. Which solution will meet these requirements with the LEAST operational overhead?

## Options

**A.** Turn on the S3 Versioning feature for the S3 bucket. Configure S3 Lifecycle to delete the data after 7 years. Configure multi-factor authentication (MFA) delete for all S3 objects.

**B.** Turn on S3 Object Lock with governance retention mode for the S3 bucket. Set the retention period to expire after 7 years. Recopy all existing objects to bring the existing data into compliance.

**C.** Turn on S3 Object Lock with compliance retention mode for the S3 bucket. Set the retention period to expire after 7 years. Recopy all existing objects to bring the existing data into compliance.

**D.** Turn on S3 Object Lock with compliance retention mode for the S3 bucket. Set the retention period to expire after 7 years. Use S3 Batch Operations to bring the existing data into compliance.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** PDFs in S3. Legal requirement: retain ALL data (new + existing) for 7 years, cannot be deleted early.
- **Existing Resources:** S3 bucket with PDFs.
- **Current Issue/Goal:** Immutable retention, prevent deletion, least overhead.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `legal requirement` | Compliance retention mode: không ai có thể xóa (kể cả root). |
| `retain for 7 years` | Object Lock retention period. |
| `all new and existing data` | S3 Batch Operations để apply retention cho existing objects. |
| `least operational overhead` | Batch Operations: xử lý hàng loạt tự động. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Compliance / Data retention
- **Constraints:** 7-year immutable retention, new + existing data

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- S3 Object Lock compliance mode: không thể xóa/override bởi bất kỳ ai (kể cả root) trong retention period.
- S3 Batch Operations: apply Object Lock settings cho existing objects hàng loạt (thay vì recopy).
- New objects: Object Lock tự động áp dụng nếu bucket configured.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Versioning + Lifecycle + MFA delete: Lifecycle delete vẫn có thể xóa. MFA delete không ngăn được authorized users.

**❌ Đáp án B:**
- Governance mode: user có s3:BypassGovernanceRetention có thể xóa. Không đủ compliance.

**❌ Đáp án C:**
- Compliance mode đúng nhưng "Recopy all existing objects" là thủ công, không operational efficiency.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Legal hold 7 years → S3 Object Lock compliance mode + Batch Operations."*