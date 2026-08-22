# Question #622 - Topic 1

A company is creating a new web application for its subscribers. The application will consist of a static single page and a persistent database layer. The application will have millions of users for 4 hours in the morning, but the application will have only a few thousand users during the rest of the day. The company's data architects have requested the ability to rapidly evolve their schema. Which solutions will meet these requirements and provide the MOST scalability? (Choose two.)

## Options

**A.** Deploy Amazon DynamoDB as the database solution. Provision on-demand capacity.

**B.** Deploy Amazon Aurora as the database solution. Choose the serverless DB engine mode.

**C.** Deploy Amazon DynamoDB as the database solution. Ensure that DynamoDB auto scaling is enabled.

**D.** Deploy the static content into an Amazon S3 bucket. Provision an Amazon CloudFront distribution with the S3 bucket as the origin.

**E.** Deploy the web servers for static content across a fleet of Amazon EC2 instances in Auto Scaling groups. Configure the instances to periodically refresh the content from an Amazon Elastic File System (Amazon EFS) volume.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Web app: static single page + database. Millions users 4h sáng, few thousand rest of day. Rapidly evolve schema.
- **Existing Resources:** None.
- **Current Issue/Goal:** Database với schema linh hoạt + static content hosting scalable.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `rapidly evolve their schema` | Cần schemaless database → DynamoDB (NoSQL). |
| `millions of users for 4 hours` | Traffic spike lớn, unpredictable. |
| `static single page` | Có thể host trên S3 + CloudFront. |
| `DynamoDB on-demand` | Pay-per-request, scale tự động từ 0 đến cao, không cần provision. |
| `MOST scalability` | S3 + CloudFront cho static content, DynamoDB cho database. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most scalability (Choose 2)
- **Constraints:** Static + dynamic, rapid schema evolution, variable traffic

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A và D**

**Giải thích:**
- **A - DynamoDB on-demand:** Schemaless (NoSQL) → dễ dàng evolve schema. On-demand capacity tự động scale từ 0 đến hàng triệu requests, không cần provisioning, lý tưởng cho unpredictable traffic.
- **D - S3 + CloudFront:** Static content hosting scalable nhất. S3 lưu static files, CloudFront CDN phân phối global với low latency.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Aurora Serverless: có thể scale nhưng database relational (schema cố định), không hỗ trợ "rapidly evolve schema" như DynamoDB.

**❌ Đáp án C:**
- DynamoDB auto scaling: scale tốt nhưng on-demand (A) xử lý traffic spikes tốt hơn (không cần warm-up). Tuy nhiên, auto scaling cũng là option, nhưng A cho on-demand có tính scalable hơn cho extreme spikes.

**❌ Đáp án E:**
- EC2 + EFS cho static content: không scalable bằng S3 + CloudFront, operational overhead cao hơn, cần quản lý servers.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Static → S3 + CloudFront. Dynamic + schemaless + spike → DynamoDB on-demand."*
