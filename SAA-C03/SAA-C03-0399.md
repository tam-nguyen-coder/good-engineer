# Question #399 - Topic 1

A financial company hosts a web application on AWS. The application uses an Amazon API Gateway Regional API endpoint to give users the ability to retrieve current stock prices. The company's security team has noticed an increase in the number of API requests. The security team is concerned that HTTP flood attacks might take the application offline. A solutions architect must design a solution to protect the application from this type of attack. Which solution meets these requirements with the LEAST operational overhead?

## Options

**A.** Create an Amazon CloudFront distribution in front of the API Gateway Regional API endpoint with a maximum TTL of 24 hours.

**B.** Create a Regional AWS WAF web ACL with a rate-based rule. Associate the web ACL with the API Gateway stage.

**C.** Use Amazon CloudWatch metrics to monitor the Count metric and alert the security team when the predefined rate is reached.

**D.** Create an Amazon CloudFront distribution with Lambda@Edge in front of the API Gateway Regional API endpoint. Create an AWS Lambda function to block requests from IP addresses that exceed the predefined rate.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** API Gateway Regional API, HTTP flood attack risk. Need protection with least operational overhead.
- **Existing Resources:** API Gateway Regional API.
- **Current Issue/Goal:** Protect against HTTP flood attacks.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `HTTP flood attacks` | Layer 7 DDoS → rate-based rule in AWS WAF. |
| `Regional` | API Gateway Regional endpoint → có thể associate WAF regional web ACL directly. |
| `AWS WAF` | Rate-based rule: block IPs vượt quá số requests trong 5 phút. |
| `least operational overhead` | WAF regional web ACL associate trực tiếp API Gateway stage, không cần CloudFront. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Least operational overhead
- **Constraints:** HTTP flood, API Gateway Regional

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- AWS WAF Regional web ACL với rate-based rule: tự động block IPs khi request rate vượt ngưỡng.
- Associate trực tiếp với API Gateway stage → không cần thay đổi architecture.
- Operational overhead thấp nhất.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- CloudFront TTL 24h: không bảo vệ chống HTTP flood. TTL cache không liên quan attack protection.

**❌ Đáp án C:**
- CloudWatch + alert: chỉ notify, không tự động block attacks. Cần manual intervention.

**❌ Đáp án D:**
- CloudFront + Lambda@Edge: thêm complexity, operational overhead cao hơn WAF trực tiếp.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"HTTP flood → WAF rate-based rule + API Gateway. CloudFront + Lambda@Edge = overkill. CloudWatch = manual."*
