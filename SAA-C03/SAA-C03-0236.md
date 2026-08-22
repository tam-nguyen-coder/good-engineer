# Question #236 - Topic 1

A company has a three-tier application for image sharing. The application uses an Amazon EC2 instance for the front-end layer, another EC2 instance for the application layer, and a third EC2 instance for a MySQL database. A solutions architect must design a scalable and highly available solution that requires the least amount of change to the application. Which solution meets these requirements?

## Options

**A.** Use Amazon S3 to host the front-end layer. Use AWS Lambda functions for the application layer. Move the database to an Amazon DynamoDB table. Use Amazon S3 to store and serve users' images.

**B.** Use load-balanced Multi-AZ AWS Elastic Beanstalk environments for the front-end layer and the application layer. Move the database to an Amazon RDS DB instance with multiple read replicas to serve users' images.

**C.** Use Amazon S3 to host the front-end layer. Use a fleet of EC2 instances in an Auto Scaling group for the application layer. Move the database to a memory optimized instance type to store and serve users' images.

**D.** Use load-balanced Multi-AZ AWS Elastic Beanstalk environments for the front-end layer and the application layer. Move the database to an Amazon RDS Multi-AZ DB instance. Use Amazon S3 to store and serve users' images.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Image sharing app: front-end EC2 + app EC2 + MySQL EC2. Need scalable + HA + least app change.
- **Existing Resources:** 3 EC2 instances (3-tier).
- **Current Issue/Goal:** HA + scalable with minimal refactoring.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `least amount of change to the application` | Rehost — **Elastic Beanstalk** |
| `image sharing` | **S3** để store/serve images |
| `MySQL` | **RDS Multi-AZ** |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Application modernization
- **Constraints:** Least app change, HA, scalable

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- **Elastic Beanstalk Multi-AZ** — load-balanced + HA, ít thay đổi code nhất.
- **RDS Multi-AZ** — managed MySQL, HA.
- **S3** — scalable, durable cho image storage (thay vì lưu trong DB).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Lambda + DynamoDB — major refactoring, nhiều thay đổi.

**❌ Đáp án B:**
- Read replicas để serve images — không phù hợp (images nên lưu S3).

**❌ Đáp án C:**
- S3 front-end + ASG + memory-optimized DB — vẫn cần thay đổi front-end.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Elastic Beanstalk = least change. RDS Multi-AZ = DB HA. S3 = image storage"*
