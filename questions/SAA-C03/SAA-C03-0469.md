# Question #469 - Topic 1

A company stores raw collected data in an Amazon S3 bucket. The data is used for several types of analytics on behalf of the company's customers. The type of analytics requested determines the access pattern on the S3 objects. The company cannot predict or control the access pattern. The company wants to reduce its S3 costs. Which solution will meet these requirements?

## Options

**A.** Use S3 replication to transition infrequently accessed objects to S3 Standard-Infrequent Access (S3 Standard-IA)

**B.** Use S3 Lifecycle rules to transition objects from S3 Standard to Standard-Infrequent Access (S3 Standard-IA)

**C.** Use S3 Lifecycle rules to transition objects from S3 Standard to S3 Intelligent-Tiering

**D.** Use S3 Inventory to identify and transition objects that have not been accessed from S3 Standard to S3 Intelligent-Tiering

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Raw data in S3, access pattern unpredictable (phụ thuộc vào loại analytics customer yêu cầu).
- **Existing Resources:** S3 bucket.
- **Current Issue/Goal:** Reduce S3 costs, không predict/control được access pattern.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `cannot predict or control the access pattern` | Cần S3 Intelligent-Tiering: tự động move objects giữa access tiers dựa trên usage. |
| `reduce S3 costs` | Intelligent-Tiering tự động tối ưu chi phí. |
| `Lifecycle rules` | Dùng để chuyển objects giữa storage classes. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Cost reduction
- **Constraints:** Unpredictable access patterns

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- S3 Intelligent-Tiering: tự động monitor access patterns và move objects giữa 3 tiers: Frequent Access, Infrequent Access, Archive Instant Access.
- Không có lifecycle rule cố định, không cần predict pattern.
- Trả phí monitoring nhỏ nhưng tiết kiệm đáng kể so với để all objects ở S3 Standard.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- S3 replication không dùng để transition storage class. Replication dùng để copy objects cross-region/cross-account.

**❌ Đáp án B:**
- Lifecycle rules chuyển Standard → Standard-IA: cần biết rule cố định (ví dụ: objects sau 30 ngày). Nhưng access pattern unpredictable → không biết đặt threshold nào.

**❌ Đáp án D:**
- S3 Inventory: reporting tool, không tự động transition.
- "Identify and transition" → cần custom solution, không tự động như Intelligent-Tiering.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Không predict được access pattern → S3 Intelligent-Tiering. Standard-IA = biết trước ít access."*
