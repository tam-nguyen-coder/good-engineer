# Question #653 - Topic 1

A company maintains an Amazon RDS database that maps users to cost centers. The company has accounts in an organization in AWS Organizations. The company needs a solution that will tag all resources that are created in a specific AWS account in the organization. The solution must tag each resource with the cost center ID of the user who created the resource. Which solution will meet these requirements?

## Options

**A.** Move the specific AWS account to a new organizational unit (OU) in Organizations from the management account. Create a service control policy (SCP) that requires all existing resources to have the correct cost center tag before the resources are created. Apply the SCP to the new OU.

**B.** Create an AWS Lambda function to tag the resources after the Lambda function looks up the appropriate cost center from the RDS database. Configure an Amazon EventBridge rule that reacts to AWS CloudTrail events to invoke the Lambda function.

**C.** Create an AWS CloudFormation stack to deploy an AWS Lambda function. Configure the Lambda function to look up the appropriate cost center from the RDS database and to tag resources. Create an Amazon EventBridge scheduled rule to invoke the CloudFormation stack.

**D.** Create an AWS Lambda function to tag the resources with a default value. Configure an Amazon EventBridge rule that reacts to AWS CloudTrail events to invoke the Lambda function when a resource is missing the cost center tag.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** RDS DB maps users to cost centers. Tag resources in a specific AWS account with the creator's cost center ID at creation time.
- **Existing Resources:** RDS database (user→cost center mapping), AWS Organizations.
- **Current Issue/Goal:** Automated tagging based on user identity and cost center mapping.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `tag each resource with the cost center ID of the user who created the resource` | Cần lookup cost center từ RDS dựa trên user identity. |
| `AWS CloudTrail events` | Capture resource creation events (CreateResource API calls). |
| `Amazon EventBridge` | React to CloudTrail events → trigger Lambda. |
| `AWS Lambda` | Custom logic: lookup cost center → tag resource. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Meet requirements
- **Constraints:** Tag based on user→cost center mapping, real-time automation

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- CloudTrail ghi lại tất cả API calls (resource creation events).
- EventBridge rule phản ứng với CloudTrail events → invoke Lambda.
- Lambda đọc CloudTrail event để biết user identity, lookup cost center từ RDS, tag resource.
- Giải pháp real-time, tự động, không cần can thiệp thủ công.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- SCP không thể "require tags before resources are created". SCP là permission boundary.
- SCP không thể look up cost center từ RDS.

**❌ Đáp án C:**
- EventBridge scheduled rule chạy định kỳ (không real-time), có độ trễ.
- Invoke CloudFormation stack (không phải Lambda trực tiếp) → phức tạp không cần thiết.

**❌ Đáp án D:**
- Tag với default value → không lấy đúng cost center của user.
- Chỉ tag khi resource missing tag → không reactive với creation event.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Auto-tag resources → CloudTrail + EventBridge + Lambda. Lookup cost center from DB."*
