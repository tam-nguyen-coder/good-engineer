# Question #171 - Topic 1

A company provides an API to its users that automates inquiries for tax computations based on item prices. The company experiences a larger number of inquiries during the holiday season only that cause slower response times. A solutions architect needs to design a solution that is scalable and elastic. What should the solutions architect do to accomplish this?

## Options

**A.** Provide an API hosted on an Amazon EC2 instance. The EC2 instance performs the required computations when the API request is made.

**B.** Design a REST API using Amazon API Gateway that accepts the item names. API Gateway passes item names to AWS Lambda for tax computations.

**C.** Create an Application Load Balancer that has two Amazon EC2 instances behind it. The EC2 instances will compute the tax on the received item names.

**D.** Design a REST API using Amazon API Gateway that connects with an API hosted on an Amazon EC2 instance. API Gateway accepts and passes the item names to the EC2 instance for tax computations.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Tax computation API, seasonal spike (holiday), slow response times.
- **Existing Resources:** None specified.
- **Current Issue/Goal:** Scalable + elastic API.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `scalable and elastic` | **Lambda + API Gateway** = auto-scale |
| `larger number of inquiries during the holiday season only` | Serverless không cần provision cho peak |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Serverless / API
- **Constraints:** Scalable, elastic

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- **API Gateway** — managed REST API, tự động scale.
- **Lambda** — serverless compute, chỉ chạy khi có request.
- Kết hợp → fully serverless, không cần quản lý servers, scale tự động theo demand.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Single EC2 — single point of failure, không elastic.

**❌ Đáp án C:**
- ALB + 2 EC2 — cần cấu hình Auto Scaling, oversize cho peak, không elastic.

**❌ Đáp án D:**
- API Gateway + EC2 — EC2 vẫn là bottleneck, không serverless.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"API Gateway + Lambda = serverless API, auto-scale. EC2 = single point / more overhead"*
