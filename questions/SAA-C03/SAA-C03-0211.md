# Question #211 - Topic 1

A company hosts multiple production applications. One of the applications consists of resources from Amazon EC2, AWS Lambda, Amazon RDS, Amazon Simple Notification Service (Amazon SNS), and Amazon Simple Queue Service (Amazon SQS) across multiple AWS Regions. All company resources are tagged with a tag name of "application" and a value that corresponds to each application. A solutions architect must provide the quickest solution for identifying all of the tagged components. Which solution meets these requirements?

## Options

**A.** Use AWS CloudTrail to generate a list of resources with the application tag.

**B.** Use the AWS CLI to query each service across all Regions to report the tagged components.

**C.** Run a query in Amazon CloudWatch Logs Insights to report on the components with the application tag.

**D.** Run a query with the AWS Resource Groups Tag Editor to report on the resources globally with the application tag.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Multi-Region application with EC2, Lambda, RDS, SNS, SQS. All tagged. Need quick inventory by tag.
- **Existing Resources:** Tagged resources across Regions.
- **Current Issue/Goal:** Quickest way to find all resources with a specific tag.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `quickest solution` | **Resource Groups Tag Editor** |
| `all of the tagged components` | Global query across Regions |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Resource management
- **Constraints:** Quick, global, by tag

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- **AWS Resource Groups Tag Editor** — cho phép tìm kiếm resources by tag across all Regions and services.
- Kết quả hiển thị nhanh, export được.
- Không cần query từng service riêng lẻ.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- CloudTrail — ghi lại API calls, không phải resource inventory.

**❌ Đáp án B:**
- AWS CLI query từng service — chậm, manual.

**❌ Đáp án C:**
- CloudWatch Logs Insights — cho log analysis, không phải resource tags.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Tag Editor = quick resource search by tag across Regions. CloudTrail = API logs. CW Logs = log analysis"*
