# Question #606 - Topic 1

A solutions architect is designing an application that will allow business users to upload objects to Amazon S3. The solution needs to maximize object durability. Objects also must be readily available at any time and for any length of time. Users will access objects frequently within the first 30 days after the objects are uploaded, but users are much less likely to access objects that are older than 30 days. Which solution meets these requirements MOST cost-effectively?

## Options

**A.** Store all the objects in S3 Standard with an S3 Lifecycle rule to transition the objects to S3 Glacier after 30 days.

**B.** Store all the objects in S3 Standard with an S3 Lifecycle rule to transition the objects to S3 Standard-Infrequent Access (S3 Standard-IA) after 30 days.

**C.** Store all the objects in S3 Standard with an S3 Lifecycle rule to transition the objects to S3 One Zone-Infrequent Access (S3 One Zone-IA) after 30 days.

**D.** Store all the objects in S3 Intelligent-Tiering with an S3 Lifecycle rule to transition the objects to S3 Standard-Infrequent Access (S3 Standard-IA) after 30 days.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Users upload objects to S3. Cần maximize durability, objects must be readily available anytime. Frequent access first 30 days, less likely after.
- **Existing Resources:** None specified.
- **Current Issue/Goal:** Chọn S3 storage class phù hợp, most cost-effective.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `maximize durability` | Cần 99.999999999% durability → S3 Standard, Standard-IA, Intelligent-Tiering đều đạt. One Zone-IA chỉ 99.99%. |
| `readily available at any time` | Cần millisecond access → loại Glacier (phút-giờ). |
| `frequent first 30 days, less likely after` | S3 Standard (first 30 days) → S3 Standard-IA (after 30 days) là cost-effective. |
| `most cost-effectively` | Không cần Intelligent-Tiering vì pattern có thể đoán trước. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most cost-effective
- **Constraints:** Maximum durability, always available, frequent→infrequent after 30 days

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- S3 Standard (first 30 days): truy cập thường xuyên, chi phí phù hợp.
- Lifecycle rule transition to S3 Standard-IA sau 30 ngày: giảm chi phí lưu trữ khi truy cập ít hơn.
- Cả Standard và Standard-IA đều có durability 99.999999999% và millisecond access.
- Cost-effective hơn Intelligent-Tiering vì pattern access có thể dự đoán trước.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- S3 Glacier có retrieval time từ phút đến giờ → không đáp ứng "readily available at any time".

**❌ Đáp án C:**
- S3 One Zone-IA chỉ có durability 99.99% (1 AZ) → không maximize durability.

**❌ Đáp án D:**
- S3 Intelligent-Tiering có monitoring fee, không cần thiết khi đã biết trước access pattern.
- Tốn thêm chi phí không cần thiết.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Frequent → Infrequent (predictable) → Standard → Standard-IA via Lifecycle. No need Intelligent-Tiering."*
