# Question #413 - Topic 1

A company has an ecommerce application experiencing an increase in user traffic. The application is deployed on Amazon EC2 instances as a two-tier web application consisting of a web tier and a separate database tier. As traffic increases, the company is noticing that the architecture is causing significant delays in sending timely marketing and order confirmation emails to users. The company wants to reduce the time it spends resolving complex email delivery issues and minimize operational overhead. What should a solutions architect do to meet these requirements?

## Options

**A.** Create a separate application tier using EC2 instances dedicated to email processing.

**B.** Configure the web instance to send email through Amazon Simple Email Service (Amazon SES).

**C.** Configure the web instance to send email through Amazon Simple Notification Service (Amazon SNS).

**D.** Create a separate application tier using EC2 instances dedicated to email processing. Place the instances in an Auto Scaling group.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Ecommerce app, high traffic → email delays (marketing + order confirmation). Want to reduce email delivery issues, minimize ops overhead.
- **Existing Resources:** EC2 web tier, database tier.
- **Current Issue/Goal:** Offload email sending to managed service.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `marketing and order confirmation emails` | Transactional + bulk email → SES. |
| `minimize operational overhead` | Managed service, không tự build email server. |
| `complex email delivery issues` | SES handles deliverability, bounces, complaints. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Operational overhead / Email
- **Constraints:** Reduce email complexity, minimize overhead

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- Amazon SES: managed email sending service (transactional + marketing).
- Giảm operational overhead: SES xử lý deliverability, reputation, bounces.
- Không cần quản lý email servers.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- EC2 dedicated tier: tự quản email server → operational overhead cao.

**❌ Đáp án C:**
- SNS: push notification service, không phải email sending solution. SNS có thể gửi email qua subscriptions nhưng không SES.

**❌ Đáp án D:**
- EC2 + ASG: tự quản email infrastructure → overhead, không tối ưu.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Send email = SES (Simple Email Service). SNS = notifications, not email."*

