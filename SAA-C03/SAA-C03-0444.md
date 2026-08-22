# Question #444 - Topic 1

A company has hired a solutions architect to design a reliable architecture for its application. The application consists of one Amazon RDS DB instance and two manually provisioned Amazon EC2 instances that run web servers. The EC2 instances are located in a single Availability Zone. An employee recently deleted the DB instance, and the application was unavailable for 24 hours as a result. The company is concerned with the overall reliability of its environment. What should the solutions architect do to maximize reliability of the application's infrastructure?

## Options

**A.** Delete one EC2 instance and enable termination protection on the other EC2 instance. Update the DB instance to be Multi-AZ, and enable deletion protection.

**B.** Update the DB instance to be Multi-AZ, and enable deletion protection. Place the EC2 instances behind an Application Load Balancer, and run them in an EC2 Auto Scaling group across multiple Availability Zones.

**C.** Create an additional DB instance along with an Amazon API Gateway and an AWS Lambda function. Configure the application to invoke the Lambda function through API Gateway. Have the Lambda function write the data to the two DB instances.

**D.** Place the EC2 instances in an EC2 Auto Scaling group that has multiple subnets located in multiple Availability Zones. Use Spot Instances instead of On-Demand Instances. Set up Amazon CloudWatch alarms to monitor the health of the instances Update the DB instance to be Multi-AZ, and enable deletion protection.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Single AZ: 2 EC2 (manual) + 1 RDS. Employee deleted RDS → 24h downtime. Need max reliability.
- **Existing Resources:** 2 EC2 web servers, 1 RDS DB instance.
- **Current Issue/Goal:** Maximize reliability: HA + data protection.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `maximize reliability` | Multi-AZ for both compute + database. Deletion protection. |
| `deletion protection` | RDS deletion protection: ngăn accidental delete. |
| `Multi-AZ` | RDS Multi-AZ (HA) + EC2 ASG across AZs. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** High Availability / Reliability
- **Constraints:** Prevent accidental deletion, survive AZ failure

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- RDS Multi-AZ: automatic failover nếu primary fails. Deletion protection: ngăn delete DB instance.
- EC2: ALB + ASG across AZs → compute HA, tự động replace failed instances.
- Multi-AZ architecture: không SPOF.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Delete 1 EC2: chỉ còn 1 instance → SPOF. Termination protection không ngăn được AZ failure.

**❌ Đáp án C:**
- API Gateway + Lambda + 2 DB: overly complex, không cần thiết cho web app.

**❌ Đáp án D:**
- Spot Instances: có thể bị interrupt → không reliable cho production.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Reliability = Multi-AZ (compute + DB) + deletion protection. Spot != reliable."*