# Question #567 - Topic 1

A solutions architect is designing a workload that will store hourly energy consumption by business tenants in a building. The sensors will feed a database through HTTP requests that will add up usage for each tenant. The solutions architect must use managed services when possible. The workload will receive more features in the future as the solutions architect adds independent components. Which solution will meet these requirements with the LEAST operational overhead?

## Options

**A.** Use Amazon API Gateway with AWS Lambda functions to receive the data from the sensors, process the data, and store the data in an Amazon DynamoDB table.

**B.** Use an Elastic Load Balancer that is supported by an Auto Scaling group of Amazon EC2 instances to receive and process the data from the sensors. Use an Amazon S3 bucket to store the processed data.

**C.** Use Amazon API Gateway with AWS Lambda functions to receive the data from the sensors, process the data, and store the data in a Microsoft SQL Server Express database on an Amazon EC2 instance.

**D.** Use an Elastic Load Balancer that is supported by an Auto Scaling group of Amazon EC2 instances to receive and process the data from the sensors. Use an Amazon Elastic File System (Amazon EFS) shared file system to store the processed data.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Workload lưu hourly energy consumption cho business tenants. Sensors gửi dữ liệu qua HTTP requests, cộng dồn usage cho từng tenant. Phải dùng managed services khi có thể. Sẽ thêm features trong tương lai dưới dạng independent components.
- **Existing Resources:** Sensors.
- **Current Issue/Goal:** Serverless/managed, ít operational overhead, dễ mở rộng tính năng.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `HTTP requests` | Cần HTTP API endpoint |
| `add up usage for each tenant` | Cần atomic counter → DynamoDB (atomic counters) |
| `managed services` | Dùng serverless khi có thể |
| `independent components` | Kiến trúc microservices/serverless dễ mở rộng |
| `LEAST operational overhead` | Serverless nhất có thể |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Least operational overhead
- **Constraints:** Managed services, HTTP, aggregate usage, future extensibility

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- API Gateway: managed HTTP endpoint, nhận requests từ sensors.
- Lambda: serverless compute, xử lý dữ liệu, không cần quản lý servers.
- DynamoDB: managed NoSQL. Hỗ trợ atomic counters (UpdateItem với ADD) – lý tưởng để "add up usage for each tenant".
- Kiến trúc serverless dễ thêm independent components (Lambda functions mới cho features mới).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B (ALB + ASG + EC2 + S3):** EC2 instances không phải managed servers (phải quản lý OS, patches, scaling). S3 không tối ưu cho atomic updates/counters (eventual consistency, no atomic increment). Cần nhiều operational overhead hơn.

**❌ Đáp án C (API Gateway + Lambda + SQL Server Express on EC2):** SQL Server Express trên EC2 không phải managed service. Phải quản lý database server, patches, backup. DynamoDB managed sẽ ít overhead hơn.

**❌ Đáp án D (ALB + ASG + EC2 + EFS):** EC2 không managed. EFS không hỗ trợ atomic counters tốt như DynamoDB. Cần tự implement cộng dồn usage, operational overhead cao.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Sensor data + HTTP + atomic counters = API Gateway + Lambda + DynamoDB. Serverless = least overhead. S3 = no atomic counters."*
