# Question #107 - Topic 1

A bicycle sharing company is developing a multi-tier architecture to track the location of its bicycles during peak operating hours. The company wants to use these data points in its existing analytics platform. A solutions architect must determine the most viable multi-tier option to support this architecture. The data points must be accessible from the REST API. Which action meets these requirements for storing and retrieving location data?

## Options

**A.** Use Amazon Athena with Amazon S3.

**B.** Use Amazon API Gateway with AWS Lambda.

**C.** Use Amazon QuickSight with Amazon Redshift.

**D.** Use Amazon API Gateway with Amazon Kinesis Data Analytics.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Bike sharing tracking, multi-tier, data accessible via REST API.
- **Existing Resources:** Analytics platform.
- **Current Issue/Goal:** Store + retrieve location data via REST API.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `REST API` | Cần **API Gateway** |
| `storing and retrieving` | Cần storage (Lambda/DynamoDB) + retrieval API |
| `multi-tier architecture` | Web tier + API tier + data tier |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Application architecture
- **Constraints:** REST API, store + retrieve

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- **API Gateway** — REST API endpoint.
- **Lambda** — business logic, store/retrieve data (e.g., DynamoDB).
- Pattern: API Gateway + Lambda + DynamoDB = serverless REST API.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Athena query S3 — analytics, không phải real-time REST API.

**❌ Đáp án C:**
- QuickSight + Redshift — BI visualization, không phải REST API.

**❌ Đáp án D:**
- Kinesis Data Analytics — real-time streaming analytics, không phải storage/retrieval API.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"REST API = API Gateway + Lambda (compute) + DynamoDB/RDS (storage)"*
