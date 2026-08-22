# Question #366 - Topic 1

A company's web application consists of an Amazon API Gateway API in front of an AWS Lambda function and an Amazon DynamoDB database. The Lambda function handles the business logic, and the DynamoDB table hosts the data. The application uses Amazon Cognito user pools to identify the individual users of the application. A solutions architect needs to update the application so that only users who have a subscription can access premium content. Which solution will meet this requirement with the LEAST operational overhead?

## Options

**A.** Enable API caching and throttling on the API Gateway API.

**B.** Set up AWS WAF on the API Gateway API. Create a rule to filter users who have a subscription.

**C.** Apply fine-grained IAM permissions to the premium content in the DynamoDB table.

**D.** Implement API usage plans and API keys to limit the access of users who do not have a subscription.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** API Gateway + Lambda + DynamoDB + Cognito. Cần restrict premium content to subscribed users.
- **Existing Resources:** API Gateway, Lambda, DynamoDB, Cognito user pools.
- **Current Issue/Goal:** Access control based on subscription status, least operational overhead.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `users who have a subscription` | Cần tiered access → API usage plans + API keys. |
| `API usage plans` | Define throttling/quotas per API key → có thể dùng cho subscription tiers. |
| `least operational overhead` | API keys + usage plans tích hợp sẵn API Gateway. |
| `Cognito user pools` | Identify users, có thể map users → API keys. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Least operational overhead
- **Constraints:** Premium content access for subscribed users

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- API Gateway usage plans: tạo API keys cho subscribed users, usage plan kiểm soát access.
- Subscribed users có API key → access premium endpoints.
- Non-subscribed users không có key → bị chặn.
- Tích hợp sẵn API Gateway, operational overhead thấp.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- API caching/throttling kiểm soát rate, không kiểm soát user-level authorization.

**❌ Đáp án B:**
- WAF block traffic dựa trên IP/headers, không phải user subscription status.

**❌ Đáp án C:**
- Fine-grained IAM permissions trên DynamoDB: operational overhead cao hơn, cần Cognito identity pool + IAM roles.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"API subscription tiers → API Gateway usage plans + API keys. WAF = IP/header. IAM DDB = operational overhead cao."*
