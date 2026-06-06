# Question #380 - Topic 1

A company is migrating its on-premises workload to the AWS Cloud. The company already uses several Amazon EC2 instances and Amazon RDS DB instances. The company wants a solution that automatically starts and stops the EC2 instances and DB instances outside of business hours. The solution must minimize cost and infrastructure maintenance. Which solution will meet these requirements?

## Options

**A.** Scale the EC2 instances by using elastic resize. Scale the DB instances to zero outside of business hours.

**B.** Explore AWS Marketplace for partner solutions that will automatically start and stop the EC2 instances and DB instances on a schedule.

**C.** Launch another EC2 instance. Configure a crontab schedule to run shell scripts that will start and stop the existing EC2 instances and DB instances on a schedule.

**D.** Create an AWS Lambda function that will start and stop the EC2 instances and DB instances. Configure Amazon EventBridge to invoke the Lambda function on a schedule.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Auto start/stop EC2 + RDS outside business hours. Minimize cost and infrastructure maintenance.
- **Existing Resources:** EC2 instances, RDS DB instances.
- **Current Issue/Goal:** Scheduled start/stop, minimal cost and maintenance.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `minimize cost and infrastructure maintenance` | Serverless (Lambda) > self-managed EC2. |
| `automatically starts and stops` | EventBridge schedule → Lambda → API calls (EC2 start/stop, RDS start/stop). |
| `outside of business hours` | Scheduled event. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Minimize cost and infrastructure maintenance
- **Constraints:** Auto start/stop EC2 + RDS on schedule

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- Lambda function: serverless, chỉ tốn cost khi chạy (vài giây mỗi lần).
- EventBridge schedule: trigger Lambda để start EC2/RDS đầu ngày và stop cuối ngày.
- Zero infrastructure maintenance (no EC2 to manage).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Elastic resize: không cho EC2. RDS không thể scale to zero.

**❌ Đáp án B:**
- AWS Marketplace partner solutions: có thể cost và phức tạp hơn Lambda + EventBridge.

**❌ Đáp án C:**
- EC2 instance chạy crontab: phải maintain thêm EC2 instance → cost + maintenance.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Schedule start/stop EC2 + RDS → Lambda + EventBridge (serverless). EC2 crontab = phải maintain thêm instance."*
