# Question #239 - Topic 1

A solutions architect needs to design a new microservice for a company's application. Clients must be able to call an HTTPS endpoint to reach the microservice. The microservice also must use AWS Identity and Access Management (IAM) to authenticate calls. The solutions architect will write the logic for this microservice by using a single AWS Lambda function that is written in Go 1.x. Which solution will deploy the function in the MOST operationally efficient way?

## Options

**A.** Create an Amazon API Gateway REST API. Configure the method to use the Lambda function. Enable IAM authentication on the API.

**B.** Create a Lambda function URL for the function. Specify AWS_IAM as the authentication type.

**C.** Create an Amazon CloudFront distribution. Deploy the function to Lambda@Edge. Integrate IAM authentication logic into the Lambda@Edge function.

**D.** Create an Amazon CloudFront distribution. Deploy the function to CloudFront Functions. Specify AWS_IAM as the authentication type.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Single Lambda function (Go) as microservice. HTTPS endpoint + IAM auth. Most operationally efficient.
- **Existing Resources:** None.
- **Current Issue/Goal:** Simple Lambda HTTPS endpoint.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `single AWS Lambda function` | Chỉ 1 function → **Lambda function URL** |
| `HTTPS endpoint` | Function URL cung cấp HTTPS |
| `IAM to authenticate` | `AWS_IAM` auth type |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Serverless / API
- **Constraints:** Single Lambda, IAM auth, min overhead

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- **Lambda function URL** — create HTTPS endpoint trực tiếp cho Lambda, không cần API Gateway.
- **AWS_IAM auth type** — tự động xác thực requests qua IAM.
- Most operationally efficient — không cần provision API Gateway.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- API Gateway — thêm component không cần thiết cho single function.

**❌ Đáp án C:**
- Lambda@Edge — dùng cho CloudFront, không phải microservice API.

**❌ Đáp án D:**
- CloudFront Functions — lightweight JS functions, không hỗ trợ Go, không IAM auth.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Lambda Function URL = simplest HTTPS endpoint for single Lambda. API Gateway = more overhead"*
