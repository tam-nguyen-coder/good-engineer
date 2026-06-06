# Question #82 - Topic 1

A company hosts its web applications in the AWS Cloud. The company configures Elastic Load Balancers to use certificates that are imported into AWS Certificate Manager (ACM). The company's security team must be notified 30 days before the expiration of each certificate. What should a solutions architect recommend to meet this requirement?

## Options

**A.** Add a rule in ACM to publish a custom message to an Amazon Simple Notification Service (Amazon SNS) topic every day, beginning 30 days before any certificate will expire.

**B.** Create an AWS Config rule that checks for certificates that will expire within 30 days. Configure Amazon EventBridge (Amazon CloudWatch Events) to invoke a custom alert by way of Amazon Simple Notification Service (Amazon SNS) when AWS Config reports a noncompliant resource.

**C.** Use AWS Trusted Advisor to check for certificates that will expire within 30 days. Create an Amazon CloudWatch alarm that is based on Trusted Advisor metrics for check status changes. Configure the alarm to send a custom alert by way of Amazon Simple Notification Service (Amazon SNS).

**D.** Create an Amazon EventBridge (Amazon CloudWatch Events) rule to detect any certificates that will expire within 30 days. Configure the rule to invoke an AWS Lambda function. Configure the Lambda function to send a custom alert by way of Amazon Simple Notification Service (Amazon SNS).

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Web apps với ELB dùng ACM certificates (imported). Cần notify security team 30 days trước expiry.
- **Existing Resources:** ACM with imported certs, ELB.
- **Current Issue/Goal:** Auto-detect certs expiring within 30 days → SNS notification.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `notified 30 days before expiration` | Cần monitoring + alerting |
| `certificates that are imported into ACM` | Imported certs → không auto-renew, cần manual |
| `AWS Config rule` | Managed rule `acm-certificate-expiration-check` |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Monitoring + Alerting
- **Constraints:** Notify 30 days before cert expiry

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- **AWS Config** có managed rule **acm-certificate-expiration-check** — kiểm tra cert sắp hết hạn.
- **EventBridge** lắng nghe sự kiện AWS Config compliance change → gửi đến SNS topic.
- Giải pháp managed, không cần custom Lambda.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- ACM không có built-in rule để publish SNS message trực tiếp.

**❌ Đáp án C:**
- Trusted Advisor không có check cụ thể cho certificate expiration với metrics để tạo CloudWatch alarm.

**❌ Đáp án D:**
- EventBridge + Lambda — được nhưng có operational overhead hơn (phải maintain Lambda code).
- AWS Config approach là managed, không cần code.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"AWS Config rule `acm-certificate-expiration-check` + EventBridge + SNS = managed cert expiry alert"*
