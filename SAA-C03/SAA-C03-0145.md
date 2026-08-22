# Question #145 - Topic 1

A company hosts a website analytics application on a single Amazon EC2 On-Demand Instance. The analytics software is written in PHP and uses a MySQL database. The analytics software, the web server that provides PHP, and the database server are all hosted on the EC2 instance. The application is showing signs of performance degradation during busy times and is presenting 5xx errors. The company needs to make the application scale seamlessly. Which solution will meet these requirements MOST cost-effectively?

## Options

**A.** Migrate the database to an Amazon RDS for MySQL DB instance. Create an AMI of the web application. Use the AMI to launch a second EC2 On-Demand Instance. Use an Application Load Balancer to distribute the load to each EC2 instance.

**B.** Migrate the database to an Amazon RDS for MySQL DB instance. Create an AMI of the web application. Use the AMI to launch a second EC2 On-Demand Instance. Use Amazon Route 53 weighted routing to distribute the load across the two EC2 instances.

**C.** Migrate the database to an Amazon Aurora MySQL DB instance. Create an AWS Lambda function to stop the EC2 instance and change the instance type. Create an Amazon CloudWatch alarm to invoke the Lambda function when CPU utilization surpasses 75%.

**D.** Migrate the database to an Amazon Aurora MySQL DB instance. Create an AMI of the web application. Apply the AMI to a launch template. Create an Auto Scaling group with the launch template Configure the launch template to use a Spot Fleet. Attach an Application Load Balancer to the Auto Scaling group.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Single EC2 (PHP + MySQL). Performance degradation + 5xx during busy times. Need seamless scaling.
- **Existing Resources:** 1 EC2 On-Demand.
- **Current Issue/Goal:** Auto-scaling, cost-effective.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `scale seamlessly` | ASG + ALB |
| `most cost-effectively` | **Aurora** (better performance) + **Spot Fleet** (cost savings) |
| `5xx errors` | Server overload — cần scale out |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Scalability + Cost optimization
- **Constraints:** Seamless scaling, cost-effective

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- **Aurora MySQL** — better performance and scalability than RDS MySQL, cost-effective.
- **ASG + Launch Template + ALB** — tự động scale in/out, seamless.
- **Spot Fleet** — giảm cost (có thể pha trộn Spot + On-Demand).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- RDS MySQL + 2 EC2 — không auto-scaling, chỉ 2 instances cố định. Không scale seamlessly.

**❌ Đáp án B:**
- Route 53 weighted routing — không tự động health check/failover như ALB.

**❌ Đáp án C:**
- Lambda resize instance — phải stop instance, gây downtime. Không seamless.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"ASG + ALB = seamless scaling. Aurora = better than MySQL. Spot Fleet = cost-effective"*
