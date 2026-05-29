# Question #356 - Topic 1

A company stores its data objects in Amazon S3 Standard storage. A solutions architect has found that 75% of the data is rarely accessed after 30 days. The company needs all the data to remain immediately accessible with the same high availability and resiliency, but the company wants to minimize storage costs. Which storage solution will meet these requirements?

## Options

**A.** Move the data objects to S3 Glacier Deep Archive after 30 days.

**B.** Move the data objects to S3 Standard-Infrequent Access (S3 Standard-IA) after 30 days.

**C.** Move the data objects to S3 One Zone-Infrequent Access (S3 One Zone-IA) after 30 days.

**D.** Move the data objects to S3 One Zone-Infrequent Access (S3 One Zone-IA) immediately.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** 75% data rarely accessed after 30 days. Need immediate access, same HA/resiliency, minimize cost.
- **Existing Resources:** S3 Standard.
- **Current Issue/Goal:** Cost saving, maintain HA and immediate access.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `immediately accessible` | IA và Standard đều immediate access (milliseconds). Glacier có retrieval time (phút-giờ). |
| `same high availability and resiliency` | Multi-AZ → Standard-IA (not One Zone-IA). |
| `S3 Standard-IA` | Multi-AZ, immediate access, lower storage cost, retrieval fee. |
| `S3 One Zone-IA` | Single AZ → không same HA. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Minimize storage costs
- **Constraints:** Immediate access, same HA/resiliency

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- S3 Standard-IA: Multi-AZ (same HA/resiliency), immediate access, storage cost thấp hơn Standard (~50%).
- 75% data rarely accessed → cost saving đáng kể với retrieval fee không đáng kể.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Glacier Deep Archive: retrieval time 12-48 hours → không immediate access.

**❌ Đáp án C:**
- One Zone-IA: chỉ 1 AZ → không same HA/resiliency.

**❌ Đáp án D:**
- One Zone-IA: không same HA, không phù hợp.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Rarely accessed + same HA → S3 Standard-IA. One Zone = không HA. Glacier = không immediate."*
