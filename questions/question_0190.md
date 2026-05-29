# Question #190 - Topic 1

A company has a web application that is based on Java and PHP. The company plans to move the application from on premises to AWS. The company needs the ability to test new site features frequently. The company also needs a highly available and managed solution that requires minimum operational overhead. Which solution will meet these requirements?

## Options

**A.** Create an Amazon S3 bucket. Enable static web hosting on the S3 bucket. Upload the static content to the S3 bucket. Use AWS Lambda to process all dynamic content.

**B.** Deploy the web application to an AWS Elastic Beanstalk environment. Use URL swapping to switch between multiple Elastic Beanstalk environments for feature testing.

**C.** Deploy the web application to Amazon EC2 instances that are configured with Java and PHP. Use Auto Scaling groups and an Application Load Balancer to manage the website's availability.

**D.** Containerize the web application. Deploy the web application to Amazon EC2 instances. Use the AWS Load Balancer Controller to dynamically route traffic between containers that contain the new site features for testing.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Java/PHP web app migration. Need frequent feature testing, HA, managed, min overhead.
- **Existing Resources:** On-prem web app (Java/PHP).
- **Current Issue/Goal:** Managed platform with environment swapping.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `test new site features frequently` | **Elastic Beanstalk URL swapping** (blue/green) |
| `managed solution` | **Elastic Beanstalk** (PaaS) |
| `Java and PHP` | Elastic Beanstalk supports both |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Application deployment
- **Constraints:** Managed, frequent testing, HA

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- **Elastic Beanstalk** — PaaS, tự động quản lý capacity, load balancing, health monitoring.
- **URL swapping** — swap CNAME giữa environments → test features trước khi production.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- S3 static + Lambda — không phù hợp cho Java/PHP dynamic content.

**❌ Đáp án C:**
- EC2 + ASG + ALB — tự quản lý, operational overhead cao hơn Elastic Beanstalk.

**❌ Đáp án D:**
- Containerize + EC2 — cần thêm container orchestration, operational overhead.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Elastic Beanstalk = PaaS, URL swap = feature testing. EC2 self-managed = more overhead"*
