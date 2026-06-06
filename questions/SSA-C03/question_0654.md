# Question #654 - Topic 1

A company recently migrated its web application to the AWS Cloud. The company uses an Amazon EC2 instance to run multiple processes to host the application. The processes include an Apache web server that serves static content. The Apache web server makes requests to a PHP application that uses a local Redis server for user sessions. The company wants to redesign the architecture to be highly available and to use AWS managed solutions. Which solution will meet these requirements?

## Options

**A.** Use AWS Elastic Beanstalk to host the static content and the PHP application. Configure Elastic Beanstalk to deploy its EC2 instance into a public subnet. Assign a public IP address.

**B.** Use AWS Lambda to host the static content and the PHP application. Use an Amazon API Gateway REST API to proxy requests to the Lambda function. Set the API Gateway CORS configuration to respond to the domain name. Configure Amazon ElastiCache for Redis to handle session information.

**C.** Keep the backend code on the EC2 instance. Create an Amazon ElastiCache for Redis cluster that has Multi-AZ enabled. Configure the ElastiCache for Redis cluster in cluster mode. Copy the frontend resources to Amazon S3. Configure the backend code to reference the EC2 instance.

**D.** Configure an Amazon CloudFront distribution with an Amazon S3 endpoint to an S3 bucket that is configured to host the static content. Configure an Application Load Balancer that targets an Amazon Elastic Container Service (Amazon ECS) service that runs AWS Fargate tasks for the PHP application. Configure the PHP application to use an Amazon ElastiCache for Redis cluster that runs in multiple Availability Zones.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Single EC2 runs Apache (static) + PHP + local Redis. Need HA + AWS managed solutions.
- **Existing Resources:** EC2 instance with Apache, PHP, Redis.
- **Current Issue/Goal:** Redesign to HA architecture, use managed services.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `highly available` | Multi-AZ, auto-scaling, no single point of failure. |
| `AWS managed solutions` | Use S3, CloudFront, ECS Fargate, ElastiCache instead of self-managed. |
| `static content` | S3 (object storage, static website hosting) + CloudFront (CDN). |
| `PHP application` | Containerized (ECS Fargate) → serverless compute. |
| `Redis for user sessions` | ElastiCache for Redis (managed, Multi-AZ). |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Meet requirements (HA + managed)
- **Constraints:** Highly available, AWS managed solutions

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- **Static content:** S3 bucket + CloudFront → managed, HA, global low latency.
- **PHP backend:** ECS Fargate (serverless containers) với ALB → auto scaling, HA across AZs.
- **Redis sessions:** ElastiCache for Redis Multi-AZ → managed, HA session store.
- Tất cả services đều là AWS managed.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Elastic Beanstalk vẫn dùng EC2 (cần quản lý OS).
- Public subnet + public IP → không HA (single instance).
- Redis vẫn local → mất session nếu instance fail.

**❌ Đáp án B:**
- Lambda không phù hợp cho PHP application (không hỗ trợ PHP native).
- CORS configuration không giải quyết vấn đề HA.

**❌ Đáp án C:**
- Vẫn dùng EC2 tự quản lý → operational overhead.
- S3 chỉ lưu static, backend vẫn single point of failure.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"HA web app: S3 + CloudFront for static, ECS Fargate + ALB for backend, ElastiCache for sessions."*
