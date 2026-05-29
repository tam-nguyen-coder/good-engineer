# Question #623 - Topic 1

A company uses Amazon API Gateway to manage its REST APIs that third-party service providers access. The company must protect the REST APIs from SQL injection and cross-site scripting attacks. What is the MOST operationally efficient solution that meets these requirements?

## Options

**A.** Configure AWS Shield.

**B.** Configure AWS WAF.

**C.** Set up API Gateway with an Amazon CloudFront distribution. Configure AWS Shield in CloudFront.

**D.** Set up API Gateway with an Amazon CloudFront distribution. Configure AWS WAF in CloudFront.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** API Gateway REST APIs cho third-party providers, cần bảo vệ khỏi SQL injection và XSS attacks.
- **Existing Resources:** Amazon API Gateway.
- **Current Issue/Goal:** WAF protection cho API Gateway với most operationally efficient.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `SQL injection and cross-site scripting` | Web application attacks → cần WAF (Web Application Firewall). |
| `API Gateway` | AWS WAF có thể associate trực tiếp với API Gateway REST API. |
| `most operationally efficient` | WAF tích hợp trực tiếp với API Gateway, không cần CloudFront. |
| `AWS Shield` | DDoS protection, không phải SQL injection/XSS. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most operationally efficient
- **Constraints:** SQL injection + XSS protection, API Gateway

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- AWS WAF có managed rules cho SQL injection và XSS protection.
- WAF có thể associate trực tiếp với API Gateway REST API (hiện tại đã hỗ trợ).
- Không cần CloudFront → đơn giản hơn, ít component hơn, operational efficiency cao nhất.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- AWS Shield bảo vệ DDoS, không có khả năng detect SQL injection hay XSS.

**❌ Đáp án C:**
- CloudFront + Shield: vẫn chỉ là DDoS protection, không có WAF rules cho SQL injection/XSS.
- Thêm CloudFront không cần thiết → tăng operational overhead.

**❌ Đáp án D:**
- CloudFront + WAF: có thể dùng, nhưng cần thêm CloudFront vào architecture → operational overhead cao hơn so với WAF trực tiếp trên API Gateway.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"SQL injection + XSS = WAF. API Gateway + WAF (no CloudFront needed). Shield = DDoS only."*
