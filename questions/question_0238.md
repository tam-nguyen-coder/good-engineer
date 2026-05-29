# Question #238 - Topic 1

A company wants to experiment with individual AWS accounts for its engineer team. The company wants to be notified as soon as the Amazon EC2 instance usage for a given month exceeds a specific threshold for each account. What should a solutions architect do to meet this requirement MOST cost-effectively?

## Options

**A.** Use Cost Explorer to create a daily report of costs by service. Filter the report by EC2 instances. Configure Cost Explorer to send an Amazon Simple Email Service (Amazon SES) notification when a threshold is exceeded.

**B.** Use Cost Explorer to create a monthly report of costs by service. Filter the report by EC2 instances. Configure Cost Explorer to send an Amazon Simple Email Service (Amazon SES) notification when a threshold is exceeded.

**C.** Use AWS Budgets to create a cost budget for each account. Set the period to monthly. Set the scope to EC2 instances. Set an alert threshold for the budget. Configure an Amazon Simple Notification Service (Amazon SNS) topic to receive a notification when a threshold is exceeded.

**D.** Use AWS Cost and Usage Reports to create a report with hourly granularity. Integrate the report data with Amazon Athena. Use Amazon EventBridge to schedule an Athena query. Configure an Amazon Simple Notification Service (Amazon SNS) topic to receive a notification when a threshold is exceeded.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Multiple AWS accounts for engineers. Notify when EC2 usage exceeds monthly threshold.
- **Existing Resources:** AWS accounts.
- **Current Issue/Goal:** Cost threshold alert, most cost-effective.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `notified as soon as... exceeds a specific threshold` | **AWS Budgets** with alerts |
| `for each account` | Per-account budgets |
| `most cost-effectively` | AWS Budgets (free tier available) |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Cost management
- **Constraints:** Per-account threshold alert, cost-effective

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- **AWS Budgets** — tạo cost budget cho mỗi account, scope EC2.
- Set **alert threshold** → gửi notification qua **SNS** khi vượt ngưỡng.
- AWS Budgets có free tier → cost-effective.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Cost Explorer — chỉ xem report, không gửi notification trực tiếp.

**❌ Đáp án B:**
- Cost Explorer — không có tính năng gửi alert.

**❌ Đáp án D:**
- CUR + Athena + EventBridge — quá phức tạp, tốn kém.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"AWS Budgets + SNS = cost threshold alerts. Cost Explorer = reports only (no alerts)"*
