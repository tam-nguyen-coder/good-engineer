# Question #66 - Topic 1

A company has an application that generates a large number of files, each approximately 5 MB in size. The files are stored in Amazon S3. Company policy requires the files to be stored for 4 years before they can be deleted. Immediate accessibility is always required as the files contain critical business data that is not easy to reproduce. The files are frequently accessed in the first 30 days of the object creation but are rarely accessed after the first 30 days. Which storage solution is MOST cost-effective?

## Options

**A.** Create an S3 bucket lifecycle policy to move files from S3 Standard to S3 Glacier 30 days from object creation. Delete the files 4 years after object creation.

**B.** Create an S3 bucket lifecycle policy to move files from S3 Standard to S3 One Zone-Infrequent Access (S3 One Zone-IA) 30 days from object creation. Delete the files 4 years after object creation.

**C.** Create an S3 bucket lifecycle policy to move files from S3 Standard to S3 Standard-Infrequent Access (S3 Standard-IA) 30 days from object creation. Delete the files 4 years after object creation.

**D.** Create an S3 bucket lifecycle policy to move files from S3 Standard to S3 Standard-Infrequent Access (S3 Standard-IA) 30 days from object creation. Move the files to S3 Glacier 4 years after object creation.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Files 5MB, lưu 4 năm, immediate access luôn cần (critical data).
- **Existing Resources:** S3.
- **Current Issue/Goal:** Cost-effective: frequently accessed first 30 days, rarely after.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `immediate accessibility is always required` | Không thể dùng Glacier (retrieval delay) |
| `critical business data` | Cần durability cao — không dùng One Zone |
| `rarely accessed after the first 30 days` | Phù hợp Standard-IA (rẻ hơn Standard) |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most cost-effective
- **Constraints:** Immediate access required, 4 years, critical data

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- **S3 Standard** cho 30 ngày đầu (frequently accessed).
- **S3 Standard-IA** cho 30 ngày → 4 năm (rarely accessed, rẻ hơn Standard, nhưng vẫn **immediately accessible**).
- Delete sau 4 năm.
- Đáp ứng "immediate accessibility is always required" — Standard-IA có retrieval time như Standard.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- **S3 Glacier** có retrieval delay (phút → giờ) — không đáp ứng "immediate accessibility".

**❌ Đáp án B:**
- **S3 One Zone-IA** chỉ lưu 1 AZ — không phù hợp cho "critical business data" (cần maximum durability).

**❌ Đáp án D:**
- Move to S3 Glacier after 4 years (khi delete) là vô nghĩa — data sẽ bị delete ngay.
- Ngay cả khi không delete, Glacier không immediate accessible.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Standard-IA = immediate access + cheaper storage. Glacier = retrieval delay. One Zone ≠ critical data"*
