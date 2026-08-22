# Question #183 - Topic 1

A company is building a new dynamic ordering website. The company wants to minimize server maintenance and patching. The website must be highly available and must scale read and write capacity as quickly as possible to meet changes in user demand. Which solution will meet these requirements?

## Options

**A.** Host static content in Amazon S3. Host dynamic content by using Amazon API Gateway and AWS Lambda. Use Amazon DynamoDB with on-demand capacity for the database. Configure Amazon CloudFront to deliver the website content.

**B.** Host static content in Amazon S3. Host dynamic content by using Amazon API Gateway and AWS Lambda. Use Amazon Aurora with Aurora Auto Scaling for the database. Configure Amazon CloudFront to deliver the website content.

**C.** Host all the website content on Amazon EC2 instances. Create an Auto Scaling group to scale the EC2 instances. Use an Application Load Balancer to distribute traffic. Use Amazon DynamoDB with provisioned write capacity for the database.

**D.** Host all the website content on Amazon EC2 instances. Create an Auto Scaling group to scale the EC2 instances. Use an Application Load Balancer to distribute traffic. Use Amazon Aurora with Aurora Auto Scaling for the database.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Dynamic ordering website. Minimize server maintenance, HA, scale read/write quickly.
- **Existing Resources:** None.
- **Current Issue/Goal:** Fully serverless, minimal maintenance.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `minimize server maintenance and patching` | **Serverless** (S3 + API Gateway + Lambda + DynamoDB) |
| `scale read and write capacity as quickly as possible` | **DynamoDB on-demand** (auto-scale instantly) |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Serverless / Web application
- **Constraints:** No server maintenance, HA, fast scaling

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- **S3** — static content, serverless.
- **API Gateway + Lambda** — dynamic content, serverless, auto-scale.
- **DynamoDB on-demand** — scale read/write instantly, không cần quản lý capacity.
- **CloudFront** — CDN, giảm latency.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Aurora — vẫn có server maintenance (dù là managed), scale chậm hơn DynamoDB on-demand.

**❌ Đáp án C:**
- EC2 instances — cần server maintenance, patching. DynamoDB provisioned không scale nhanh.

**❌ Đáp án D:**
- EC2 instances — cần maintenance. Aurora không scale nhanh như DynamoDB on-demand.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"S3 + API Gateway + Lambda + DynamoDB on-demand = fully serverless. EC2 = maintenance overhead"*
