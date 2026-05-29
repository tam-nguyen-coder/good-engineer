# Question #434 - Topic 1

A company hosts its application in the AWS Cloud. The application runs on Amazon EC2 instances behind an Elastic Load Balancer in an Auto Scaling group and with an Amazon DynamoDB table. The company wants to ensure the application can be made available in another AWS Region with minimal downtime. What should a solutions architect do to meet these requirements with the LEAST amount of downtime?

## Options

**A.** Create an Auto Scaling group and a load balancer in the disaster recovery Region. Configure the DynamoDB table as a global table. Configure DNS failover to point to the new disaster recovery Region's load balancer.

**B.** Create an AWS CloudFormation template to create EC2 instances, load balancers, and DynamoDB tables to be launched when needed Configure DNS failover to point to the new disaster recovery Region's load balancer.

**C.** Create an AWS CloudFormation template to create EC2 instances and a load balancer to be launched when needed. Configure the DynamoDB table as a global table. Configure DNS failover to point to the new disaster recovery Region's load balancer.

**D.** Create an Auto Scaling group and load balancer in the disaster recovery Region. Configure the DynamoDB table as a global table. Create an Amazon CloudWatch alarm to trigger an AWS Lambda function that updates Amazon Route 53 pointing to the disaster recovery load balancer.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Multi-AZ app (EC2 + ELB + ASG + DynamoDB). Need cross-region DR with minimal downtime.
- **Existing Resources:** EC2, ELB, ASG, DynamoDB table.
- **Current Issue/Goal:** Active-passive DR, minimize downtime.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `minimal downtime` | Pre-provisioned DR resources + DynamoDB Global Tables. |
| `DynamoDB global table` | Multi-region replication, active-active. |
| `DNS failover` | Route 53 failover routing policy. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Disaster Recovery
- **Constraints:** Cross-region, minimal downtime

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- Pre-create ASG + ALB in DR region: resources sẵn sàng, chỉ cần switch DNS → downtime thấp nhất.
- DynamoDB Global Table: tự động replicate data across regions.
- Route 53 DNS failover: tự động chuyển traffic khi primary region fails.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- CloudFormation launch khi cần: resources phải tạo mới → downtime cao (phút → giờ).

**❌ Đáp án C:**
- CloudFormation launch khi cần, DynamoDB global table ok nhưng compute resources không pre-provisioned → downtime cao.

**❌ Đáp án D:**
- CloudWatch → Lambda → Route 53 update: thêm complexity, không nhanh hơn Route 53 failover routing.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Minimal downtime DR = pre-provisioned resources + DynamoDB Global Tables + Route 53 failover."*