# Question #416 - Topic 1

A rapidly growing global ecommerce company is hosting its web application on AWS. The web application includes static content and dynamic content. The website stores online transaction processing (OLTP) data in an Amazon RDS database The website's users are experiencing slow page loads. Which combination of actions should a solutions architect take to resolve this issue? (Choose two.)

## Options

**A.** Configure an Amazon Redshift cluster.

**B.** Set up an Amazon CloudFront distribution.

**C.** Host the dynamic web content in Amazon S3.

**D.** Create a read replica for the RDS DB instance.

**E.** Configure a Multi-AZ deployment for the RDS DB instance.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Global ecommerce, static + dynamic content, RDS (OLTP). Slow page loads.
- **Existing Resources:** Web app on AWS, RDS database.
- **Current Issue/Goal:** Improve page load speed globally.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `global` | CloudFront: CDN, edge caching giảm latency. |
| `static content` | CloudFront cache at edge. |
| `dynamic content` | CloudFront hỗ trợ dynamic + static. |
| `OLTP data in RDS` | Read replica: offload read queries, cải thiện performance. |
| `slow page loads` | Combine CDN + DB read offloading. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Performance / Global
- **Constraints:** Static + dynamic content, OLTP RDS

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B, D**

**Giải thích:**
- **B:** CloudFront: CDN cache static content at edge → giảm latency. Hỗ trợ dynamic content acceleration.
- **D:** Read replica: offload read queries từ primary DB → giảm load, cải thiện response time.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Redshift: data warehouse (OLAP), không phải giải pháp cho web performance.

**❌ Đáp án C:**
- S3 chỉ lưu static content, không host dynamic web content.

**❌ Đáp án E:**
- Multi-AZ: high availability, không cải thiện read performance (standby không dùng cho reads).

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Slow global site → CloudFront (CDN) + RDS Read Replica (offload reads). Multi-AZ = HA, không phải performance."*

