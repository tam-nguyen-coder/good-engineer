# Question #373 - Topic 1

A company has an application that collects data from IoT sensors on automobiles. The data is streamed and stored in Amazon S3 through Amazon Kinesis Data Firehose. The data produces trillions of S3 objects each year. Each morning, the company uses the data from the previous 30 days to retrain a suite of machine learning (ML) models. Four times each year, the company uses the data from the previous 12 months to perform analysis and train other ML models. The data must be available with minimal delay for up to 1 year. After 1 year, the data must be retained for archival purposes. Which storage solution meets these requirements MOST cost-effectively?

## Options

**A.** Use the S3 Intelligent-Tiering storage class. Create an S3 Lifecycle policy to transition objects to S3 Glacier Deep Archive after 1 year.

**B.** Use the S3 Intelligent-Tiering storage class. Configure S3 Intelligent-Tiering to automatically move objects to S3 Glacier Deep Archive after 1 year.

**C.** Use the S3 Standard-Infrequent Access (S3 Standard-IA) storage class. Create an S3 Lifecycle policy to transition objects to S3 Glacier Deep Archive after 1 year.

**D.** Use the S3 Standard storage class. Create an S3 Lifecycle policy to transition objects to S3 Standard-Infrequent Access (S3 Standard-IA) after 30 days, and then to S3 Glacier Deep Archive after 1 year.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** IoT data (trillions objects/year), daily ML retraining (30-day window), quarterly analysis (12-month). Available minimal delay for 1 year, then archive.
- **Existing Resources:** Kinesis Firehose → S3.
- **Current Issue/Goal:** Cost-effective storage, access patterns inconsistent.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `previous 30 days` | Data gần đây được access daily. |
| `previous 12 months` | Older data access quarterly. |
| `available with minimal delay` | Cần immediate access (Glacier Deep Archive retrieval 12-48h → chỉ dùng cho archive). |
| `S3 Intelligent-Tiering` | Auto move between access tiers based on usage pattern (frequent ↔ infrequent). |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most cost-effective
- **Constraints:** Daily access 30-day data, quarterly 12-month data, archive after 1 year

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- S3 Intelligent-Tiering: tự động move objects giữa Frequent Access và Infrequent Access dựa trên actual access → phù hợp cho "30-day daily + 12-month quarterly" inconsistent pattern.
- Lifecycle policy → Glacier Deep Archive after 1 year (Intelligent-Tiering không tự động archive vào Glacier).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- S3 Intelligent-Tiering không thể tự động move objects to Glacier Deep Archive (chỉ move giữa access tiers của Intelligent-Tiering).

**❌ Đáp án C:**
- S3 Standard-IA: không phù hợp cho data 30-day được truy cập daily (retrieval fee cao).

**❌ Đáp án D:**
- S3 Standard → IA → Glacier Deep Archive: Standard-IA có retrieval fee cho daily access. Intelligent-Tiering tối ưu hơn.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Inconsistent access + archive → Intelligent-Tiering + Lifecycle to Glacier Deep Archive. IA = retrieval fee cho frequent access."*
