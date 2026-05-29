# Question #159 - Topic 1

A company is running a publicly accessible serverless application that uses Amazon API Gateway and AWS Lambda. The application's traffic recently spiked due to fraudulent requests from botnets. Which steps should a solutions architect take to block requests from unauthorized users? (Choose two.)

## Options

**A.** Create a usage plan with an API key that is shared with genuine users only.

**B.** Integrate logic within the Lambda function to ignore the requests from fraudulent IP addresses.

**C.** Implement an AWS WAF rule to target malicious requests and trigger actions to filter them out.

**D.** Convert the existing public API to a private API. Update the DNS records to redirect users to the new API endpoint.

**E.** Create an IAM role for each user attempting to access the API. A user will assume the role when making the API call.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** API Gateway + Lambda public, botnet fraudulent requests spike.
- **Existing Resources:** API Gateway, Lambda.
- **Current Issue/Goal:** Block unauthorized/bot requests.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `block requests from unauthorized users` | **API keys + Usage plans** hoặc **WAF** |
| `botnets` | Automated malicious traffic |
| `fraudulent requests` | Cần WAF rules |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Security / API protection
- **Constraints:** Chọn 2

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A và C**

**Giải thích:**
- **A: Usage plan + API key** — chỉ genuine users có API key mới gọi được.
- **C: AWS WAF** — rules phát hiện + block malicious requests (rate limiting, IP block, SQL injection, XSS).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Lambda logic — khó maintain, không scale, không real-time như WAF.

**❌ Đáp án D:**
- Private API — chỉ доступ trong VPC, không public được.

**❌ Đáp án E:**
- IAM role per user — không practical cho public API.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"API key + usage plan = restrict access. WAF = block malicious traffic. Lambda logic = not scalable"*
