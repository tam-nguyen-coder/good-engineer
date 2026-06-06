# Question #671 - Topic 1

A company runs its applications on Amazon EC2 instances. The company performs periodic financial assessments of its AWS costs. The company recently identified unusual spending. The company needs a solution to prevent unusual spending. The solution must monitor costs and notify responsible stakeholders in the event of unusual spending. Which solution will meet these requirements?

## Options

**A.** Use an AWS Budgets template to create a zero spend budget.

**B.** Create an AWS Cost Anomaly Detection monitor in the AWS Billing and Cost Management console.

**C.** Create AWS Pricing Calculator estimates for the current running workload pricing details.

**D.** Use Amazon CloudWatch to monitor costs and to identify unusual spending.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Unusual AWS spending identified. Need to monitor costs and notify stakeholders of unusual spending.
- **Existing Resources:** EC2 applications.
- **Current Issue/Goal:** Detect and alert on cost anomalies.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `unusual spending` | Anomaly detection, không chỉ budget threshold. |
| `notify responsible stakeholders` | Automatic alerts. |
| `AWS Cost Anomaly Detection` | AWS managed ML-based anomaly detection for costs. |
| `AWS Budgets` | Threshold-based alerts (fixed $ amount), không phát hiện bất thường. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Meet requirements
- **Constraints:** Detect unusual spending, notify stakeholders

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- AWS Cost Anomaly Detection sử dụng ML để phát hiện spending patterns bất thường.
- Tự động gửi alert cho stakeholders khi phát hiện anomaly.
- Không cần cấu hình threshold thủ công.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Zero spend budget: cảnh báo khi có bất kỳ spending nào → không phải detection bất thường.

**❌ Đáp án C:**
- Pricing Calculator dùng để ước tính cost trước khi deploy, không monitor hay detect anomalies.

**❌ Đáp án D:**
- CloudWatch không có built-in cost anomaly detection. Cần custom solution.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Unusual spending detection → AWS Cost Anomaly Detection (ML-based, auto alerts)."*
