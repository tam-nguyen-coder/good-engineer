# Question #411 - Topic 1

A company has a web application with sporadic usage patterns. There is heavy usage at the beginning of each month, moderate usage at the start of each week, and unpredictable usage during the week. The application consists of a web server and a MySQL database server running inside the data center. The company would like to move the application to the AWS Cloud, and needs to select a cost-effective database platform that will not require database modifications. Which solution will meet these requirements?

## Options

**A.** Amazon DynamoDB

**B.** Amazon RDS for MySQL

**C.** MySQL-compatible Amazon Aurora Serverless

**D.** MySQL deployed on Amazon EC2 in an Auto Scaling group

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Sporadic usage pattern (heavy monthly, moderate weekly, unpredictable). MySQL DB. Must not require DB modifications.
- **Existing Resources:** On-prem web app + MySQL DB.
- **Current Issue/Goal:** Cost-effective DB on AWS, no code changes.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `sporadic usage patterns` | Aurora Serverless: auto scale, pay per second. |
| `no database modifications` | Must be MySQL-compatible (no schema change). |
| `cost-effective` | Serverless = không trả tiền khi không dùng. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Cost-effective / Database
- **Constraints:** MySQL-compatible, no code modifications

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- Aurora Serverless: MySQL-compatible, tự động scale từ 0 theo workload.
- Pay per second (ACU), tiết kiệm khi sporadic usage.
- Không cần modify application (MySQL protocol).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- DynamoDB: NoSQL, không MySQL-compatible → cần modify application.

**❌ Đáp án B:**
- RDS for MySQL: MySQL-compatible nhưng luôn chạy (không serverless) → tốn kém cho sporadic usage.

**❌ Đáp án D:**
- MySQL on EC2 + ASG: tự quản DB, operational overhead cao. DB không scale theo ASG dễ dàng.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Sporadic MySQL = Aurora Serverless (auto scale, pay per use). RDS luôn chạy = tốn."*

