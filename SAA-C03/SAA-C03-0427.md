# Question #427 - Topic 1

A solutions architect is implementing a complex Java application with a MySQL database. The Java application must be deployed on Apache Tomcat and must be highly available. What should the solutions architect do to meet these requirements?

## Options

**A.** Deploy the application in AWS Lambda. Configure an Amazon API Gateway API to connect with the Lambda functions.

**B.** Deploy the application by using AWS Elastic Beanstalk. Configure a load-balanced environment and a rolling deployment policy.

**C.** Migrate the database to Amazon ElastiCache. Configure the ElastiCache security group to allow access from the application.

**D.** Launch an Amazon EC2 instance. Install a MySQL server on the EC2 instance. Configure the application on the server. Create an AMI. Use the AMI to create a launch template with an Auto Scaling group.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Java app on Apache Tomcat with MySQL. Need high availability.
- **Existing Resources:** Java application, MySQL database.
- **Current Issue/Goal:** Highly available deployment on AWS.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `Java application` | Elastic Beanstalk supports Java/Tomcat platform. |
| `Apache Tomcat` | Elastic Beanstalk Tomcat platform. |
| `highly available` | Load-balanced environment (multi-AZ). |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** High Availability / Deployment
- **Constraints:** Java Tomcat, HA

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- Elastic Beanstalk: PaaS, hỗ trợ Java với Tomcat platform.
- Load-balanced environment: tự động tạo ALB + ASG across AZs → HA.
- Rolling deployment: zero-downtime deployments.
- Managed platform: tự động patching, health monitoring.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Lambda không chạy Apache Tomcat. Lambda dùng cho serverless functions, không phải Java web app với Tomcat.

**❌ Đáp án C:**
- ElastiCache: in-memory caching, không phải MySQL database.

**❌ Đáp án D:**
- EC2 + ASG: tự quản nhiều thứ (OS, Tomcat, MySQL). Cần nhiều config thủ công, không phải giải pháp HA tốt nhất.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Java + Tomcat + HA → Elastic Beanstalk (PaaS). Lambda không support Tomcat."*