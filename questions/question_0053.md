# Question #53 - Topic 1

A company needs to store its accounting records in Amazon S3. The records must be immediately accessible for 1 year and then must be archived for an additional 9 years. No one at the company, including administrative users and root users, can be able to delete the records during the entire 10-year period. The records must be stored with maximum resiliency. Which solution will meet these requirements?

## Options

**A.** Store the records in S3 Glacier for the entire 10-year period. Use an access control policy to deny deletion of the records for a period of 10 years.

**B.** Store the records by using S3 Intelligent-Tiering. Use an IAM policy to deny deletion of the records. After 10 years, change the IAM policy to allow deletion.

**C.** Use an S3 Lifecycle policy to transition the records from S3 Standard to S3 Glacier Deep Archive after 1 year. Use S3 Object Lock in compliance mode for a period of 10 years.

**D.** Use an S3 Lifecycle policy to transition the records from S3 Standard to S3 One Zone-Infrequent Access (S3 One Zone-IA) after 1 year. Use S3 Object Lock in governance mode for a period of 10 years.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Lưu accounting records 10 năm: 1 năm đầu cần truy cập ngay, 9 năm sau archive.
- **Existing Resources:** Chưa có.
- **Current Issue/Goal:** Không ai (kể cả admin/root) có thể xóa records trong 10 năm. Maximum resiliency.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `no one, including administrative users and root users, can delete` | Cần chế độ bất biến — **S3 Object Lock Compliance mode** |
| `maximum resiliency` | Không dùng One-Zone, cần Multi-AZ |
| `immediately accessible for 1 year` | Cần S3 Standard (hoặc tương đương) |
| `archived for 9 years` | Cần storage rẻ nhất — S3 Glacier Deep Archive |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Compliance + Security + Durability
- **Constraints:** 10-year retention, không ai xóa được, maximum resiliency

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- **S3 Object Lock in compliance mode** — không ai (kể cả root user) có thể xóa hoặc ghi đè object trong thời gian lock. Đây là chế độ mạnh nhất.
- **S3 Lifecycle** chuyển từ S3 Standard → S3 Glacier Deep Archive sau 1 năm — tiết kiệm chi phí cho 9 năm archive.
- **Maximum resiliency:** S3 Standard (99.999999999% durability, Multi-AZ) + Glacier Deep Archive (cũng Multi-AZ).
- Đáp ứng đủ 3 yêu cầu: immediate access (Standard), archive (Deep Archive), immutable (Object Lock compliance).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- S3 Glacier có retrieval delay (phút đến giờ) — không đáp ứng "immediately accessible for 1 year".
- "Access control policy" (IAM bucket policy) có thể bị thay đổi bởi root user — không đảm bảo không ai xóa được.

**❌ Đáp án B:**
- IAM policy có thể bị thay đổi bởi root/admin users — không ngăn được deletion.
- S3 Intelligent-Tiering có thể tự động move data, nhưng không có cơ chế WORM (Write Once Read Many).

**❌ Đáp án D:**
- **S3 One Zone-IA** chỉ lưu trong 1 AZ → không đạt "maximum resiliency".
- **Object Lock governance mode** có thể bị override bởi user có quyền đặc biệt (s3:BypassGovernanceRetention) — không ngăn được root.
- Phải dùng **compliance mode** để chặn root.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Compliance mode = even root can't delete. Governance mode = admin can override. One Zone ≠ maximum resiliency"*
