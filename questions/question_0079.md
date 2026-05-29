# Question #79 - Topic 1

A company is planning to use an Amazon DynamoDB table for data storage. The company is concerned about cost optimization. The table will not be used on most mornings. In the evenings, the read and write traffic will often be unpredictable. When traffic spikes occur, they will happen very quickly. What should a solutions architect recommend?

## Options

**A.** Create a DynamoDB table in on-demand capacity mode.

**B.** Create a DynamoDB table with a global secondary index.

**C.** Create a DynamoDB table with provisioned capacity and auto scaling.

**D.** Create a DynamoDB table in provisioned capacity mode, and configure it as a global table.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** DynamoDB table với traffic pattern: sáng không dùng, tối unpredictable + spike nhanh.
- **Existing Resources:** Chưa có.
- **Current Issue/Goal:** Cost optimization cho unpredictable traffic.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `not used on most mornings` | Có thời gian zero traffic |
| `unpredictable` | Không thể dự đoán capacity |
| `traffic spikes... very quickly` | Auto scaling không kịp scale |
| `cost optimization` | Chỉ trả cho những gì dùng |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Cost optimization
- **Constraints:** Unpredictable traffic, quick spikes

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- **On-demand capacity mode** — pay-per-request, không cần provision capacity.
- Phù hợp cho unpredictable workloads — không lo under-provisioning (throttling) hay over-provisioning (lãng phí).
- **Spikes xảy ra rất nhanh** — on-demand scale ngay lập tức, không cần chờ auto scaling.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- GSI không liên quan đến capacity mode hay scaling.

**❌ Đáp án C:**
- **Provisioned + auto scaling** — có thể không scale kịp với "spikes occur very quickly" (auto scaling có độ trễ).

**❌ Đáp án D:**
- Global tables = multi-Region replication, không giải quyết vấn đề capacity.
- Provisioned mode không phù hợp cho unpredictable traffic.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"On-demand = unpredictable + quick spikes. Provisioned = predictable traffic. Auto scaling = slow for sudden spikes"*
