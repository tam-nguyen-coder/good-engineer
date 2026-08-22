# Question #278 - Topic 1

A company wants to create an application to store employee data in a hierarchical structured relationship. The company needs a minimum-latency response to high-traffic queries for the employee data and must protect any sensitive data. The company also needs to receive monthly email messages if any financial information is present in the employee data. Which combination of steps should a solutions architect take to meet these requirements? (Choose two.)

## Options

**A.** Use Amazon Redshift to store the employee data in hierarchies. Unload the data to Amazon S3 every month.

**B.** Use Amazon DynamoDB to store the employee data in hierarchies. Export the data to Amazon S3 every month.

**C.** Configure Amazon Macie for the AWS account. Integrate Macie with Amazon EventBridge to send monthly events to AWS Lambda.

**D.** Use Amazon Athena to analyze the employee data in Amazon S3. Integrate Athena with Amazon QuickSight to publish analysis dashboards and share the dashboards with users.

**E.** Configure Amazon Macie for the AWS account. Integrate Macie with Amazon EventBridge to send monthly notifications through an Amazon Simple Notification Service (Amazon SNS) subscription.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Employee data, hierarchical, high-traffic low-latency queries. Protect sensitive data. Monthly email if financial info detected.
- **Existing Resources:** None.
- **Current Issue/Goal:** Low-latency DB + sensitive data detection.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `hierarchical structured relationship` | **DynamoDB** (single table, adjacency list) |
| `minimum-latency response to high-traffic queries` | DynamoDB single-digit ms |
| `financial information is present` | **Amazon Macie** (sensitive data discovery) |
| `monthly email messages` | SNS notification |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Database / Security
- **Constraints:** Chọn 2, low latency, sensitive data detection

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B và E**

**Giải thích:**
- **B: DynamoDB** — low latency, hierarchical data (adjacency list pattern).
- **E: Macie + EventBridge + SNS** — phát hiện financial data, gửi email monthly.
- DynamoDB export to S3 monthly cho Macie analysis.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Redshift — OLAP, không phù hợp high-traffic low-latency queries.

**❌ Đáp án C:**
- Macie + Lambda — không phù hợp cho monthly notifications (SNS tốt hơn).

**❌ Đáp án D:**
- Athena + QuickSight — analytics, không phải sensitive data detection.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"DynamoDB = low-latency hierarchical data. Macie = detect sensitive data. SNS = email notifications"*
