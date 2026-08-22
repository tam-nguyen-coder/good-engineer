# Question #196 - Topic 1

A company runs an application on a large fleet of Amazon EC2 instances. The application reads and writes entries into an Amazon DynamoDB table. The size of the DynamoDB table continuously grows, but the application needs only data from the last 30 days. The company needs a solution that minimizes cost and development effort. Which solution meets these requirements?

## Options

**A.** Use an AWS CloudFormation template to deploy the complete solution. Redeploy the CloudFormation stack every 30 days, and delete the original stack.

**B.** Use an EC2 instance that runs a monitoring application from AWS Marketplace. Configure the monitoring application to use Amazon DynamoDB Streams to store the timestamp when a new item is created in the table. Use a script that runs on the EC2 instance to delete items that have a timestamp that is older than 30 days.

**C.** Configure Amazon DynamoDB Streams to invoke an AWS Lambda function when a new item is created in the table. Configure the Lambda function to delete items in the table that are older than 30 days.

**D.** Extend the application to add an attribute that has a value of the current timestamp plus 30 days to each new item that is created in the table. Configure DynamoDB to use the attribute as the TTL attribute.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** DynamoDB table growing continuously, only need last 30 days data.
- **Existing Resources:** EC2 fleet, DynamoDB table.
- **Current Issue/Goal:** Auto-delete old data, min cost + dev effort.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `only data from the last 30 days` | **DynamoDB TTL** (Time to Live) |
| `minimizes cost and development effort` | TTL = zero maintenance, tự động delete |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Database / Cost optimization
- **Constraints:** Auto cleanup, min effort

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- **DynamoDB TTL** — define attribute as expiry time → DynamoDB tự động delete items sau TTL.
- Chỉ cần thêm attribute (timestamp + 30 days) vào mỗi item → minimal dev effort.
- Không cần EC2, Lambda hay monitoring tools → chi phí thấp nhất.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- CloudFormation redeploy — data loss, không practical.

**❌ Đáp án B:**
- EC2 + Marketplace + Streams + delete script — operational overhead, cost.

**❌ Đáp án C:**
- DynamoDB Streams + Lambda — more dev effort, tốn Lambda cost.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"DynamoDB TTL = auto-expire data. Lambda/EC2 cleanup = more effort and cost"*
