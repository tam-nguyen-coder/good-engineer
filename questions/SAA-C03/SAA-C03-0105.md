# Question #105 - Topic 1

A company is preparing to deploy a new serverless workload. A solutions architect must use the principle of least privilege to configure permissions that will be used to run an AWS Lambda function. An Amazon EventBridge (Amazon CloudWatch Events) rule will invoke the function. Which solution meets these requirements?

## Options

**A.** Add an execution role to the function with lambda:InvokeFunction as the action and * as the principal.

**B.** Add an execution role to the function with lambda:InvokeFunction as the action and Service: lambda.amazonaws.com as the principal.

**C.** Add a resource-based policy to the function with lambda:* as the action and Service: events.amazonaws.com as the principal.

**D.** Add a resource-based policy to the function with lambda:InvokeFunction as the action and Service: events.amazonaws.com as the principal.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Lambda function được invoke bởi EventBridge rule. Cần least privilege.
- **Existing Resources:** Lambda function, EventBridge rule.
- **Current Issue/Goal:** Cấu hình permissions để EventBridge được phép invoke Lambda.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `least privilege` | Chỉ grant quyền tối thiểu cần thiết |
| `EventBridge (CloudWatch Events) rule will invoke the function` | EventBridge service cần `lambda:InvokeFunction` |
| `resource-based policy` | Lambda dùng resource-based policy cho cross-service invoke |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** IAM / Security
- **Constraints:** Least privilege

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- **Resource-based policy** — Lambda cho phép AWS services khác invoke function.
- **Action: `lambda:InvokeFunction`** — chỉ quyền tối thiểu (không dùng `lambda:*`).
- **Principal: `events.amazonaws.com`** — chỉ EventBridge service, không phải tất cả services.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- **Execution role** dùng cho function để access AWS resources, không phải để cho service khác invoke function.
- `*` as principal — quá rộng.

**❌ Đáp án B:**
- `lambda.amazonaws.com` là sai — EventBridge không dùng service principal này.
- Execution role sai use case.

**❌ Đáp án C:**
- `lambda:*` — quá rộng, không phải least privilege.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Lambda resource-based policy = cho phép service khác invoke. Execution role = cho function access resources"*
