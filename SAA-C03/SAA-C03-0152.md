# Question #152 - Topic 1

A company uses a three-tier web application to provide training to new employees. The application is accessed for only 12 hours every day. The company is using an Amazon RDS for MySQL DB instance to store information and wants to minimize costs. What should a solutions architect do to meet these requirements?

## Options

**A.** Configure an IAM policy for AWS Systems Manager Session Manager. Create an IAM role for the policy. Update the trust relationship of the role. Set up automatic start and stop for the DB instance.

**B.** Create an Amazon ElastiCache for Redis cache cluster that gives users the ability to access the data from the cache when the DB instance is stopped. Invalidate the cache after the DB instance is started.

**C.** Launch an Amazon EC2 instance. Create an IAM role that grants access to Amazon RDS. Attach the role to the EC2 instance. Configure a cron job to start and stop the EC2 instance on the desired schedule.

**D.** Create AWS Lambda functions to start and stop the DB instance. Create Amazon EventBridge (Amazon CloudWatch Events) scheduled rules to invoke the Lambda functions. Configure the Lambda functions as event targets for the rules.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** RDS MySQL cho training app, chỉ dùng 12h/ngày. Muốn minimize costs.
- **Existing Resources:** RDS MySQL DB instance.
- **Current Issue/Goal:** Stop DB khi không dùng để tiết kiệm.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `minimize costs` | Start/stop DB instance khi không dùng |
| `12 hours every day` | Schedule: start before use, stop after |
| `EventBridge scheduled rules` | Cron job serverless |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Cost optimization
- **Constraints:** 12h/day usage

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- **Lambda function** start/stop RDS instance.
- **EventBridge scheduled rule** — trigger Lambda theo lịch (start buổi sáng, stop buổi tối).
- Serverless, không cần quản lý EC2.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Session Manager dùng để SSH, không start/stop RDS.

**❌ Đáp án B:**
- ElastiCache cache — không giải quyết cost của RDS (RDS vẫn chạy).

**❌ Đáp án C:**
- EC2 cron job — phải trả tiền cho EC2 24/7, không tiết kiệm.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"EventBridge + Lambda = serverless schedule to start/stop RDS. EC2 cron = still pay for EC2"*
