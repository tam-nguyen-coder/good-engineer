# Question #200 - Topic 1

A company hosts its application on AWS. The company uses Amazon Cognito to manage users. When users log in to the application, the application fetches required data from Amazon DynamoDB by using a REST API that is hosted in Amazon API Gateway. The company wants an AWS managed solution that will control access to the REST API to reduce development efforts. Which solution will meet these requirements with the LEAST operational overhead?

## Options

**A.** Configure an AWS Lambda function to be an authorizer in API Gateway to validate which user made the request.

**B.** For each user, create and assign an API key that must be sent with each request. Validate the key by using an AWS Lambda function.

**C.** Send the user's email address in the header with every request. Invoke an AWS Lambda function to validate that the user with that email address has proper access.

**D.** Configure an Amazon Cognito user pool authorizer in API Gateway to allow Amazon Cognito to validate each request.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Cognito + API Gateway + DynamoDB. Need managed access control for REST API.
- **Existing Resources:** Cognito user pool, API Gateway.
- **Current Issue/Goal:** Managed auth, reduce dev effort.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `Amazon Cognito to manage users` | Đã có user pool |
| `AWS managed solution` | **Cognito authorizer** trong API Gateway |
| `least operational overhead` | Không cần custom Lambda authorizer |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Security / Auth
- **Constraints:** Managed, least overhead

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- **Cognito User Pool Authorizer** — tích hợp native với API Gateway.
- API Gateway tự động validate JWT token từ Cognito — không cần custom code.
- Managed → least operational overhead.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Lambda authorizer — cần viết và maintain custom code.

**❌ Đáp án B:**
- API keys per user + Lambda — không scalable, development effort.

**❌ Đáp án C:**
- Email header + Lambda — insecure (email dễ giả mạo), development effort.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Cognito User Pool Authorizer = managed auth for API Gateway. Lambda authorizer = custom code (more overhead)"*
