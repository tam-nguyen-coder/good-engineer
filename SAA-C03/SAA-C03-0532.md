# Question #532 - Topic 1

A company has a workload in an AWS Region. Customers connect to and access the workload by using an Amazon API Gateway REST API. The company uses Amazon Route 53 as its DNS provider. The company wants to provide individual and secure URLs for all customers. Which combination of steps will meet these requirements with the MOST operational efficiency? (Choose three.)

## Options

**A.** Register the required domain in a registrar. Create a wildcard custom domain name in a Route 53 hosted zone and record in the zone that points to the API Gateway endpoint.

**B.** Request a wildcard certificate that matches the domains in AWS Certificate Manager (ACM) in a different Region.

**C.** Create hosted zones for each customer as required in Route 53. Create zone records that point to the API Gateway endpoint.

**D.** Request a wildcard certificate that matches the custom domain name in AWS Certificate Manager (ACM) in the same Region.

**E.** Create multiple API endpoints for each customer in API Gateway.
**F.** Create a custom domain name in API Gateway for the REST API. Import the certificate from AWS Certificate Manager (ACM).

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** API Gateway REST API, muốn cung cấp individual và secure URLs cho mỗi customer.
- **Existing Resources:** API Gateway REST API, Route 53.
- **Current Issue/Goal:** Individual secure URLs, operational efficiency.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `individual and secure URLs` | Custom domain names per customer với HTTPS |
| `wildcard certificate` | `*.example.com` → phủ nhiều subdomain cho mỗi customer |
| `API Gateway custom domain` | Map custom domain name đến API Gateway API |
| `same Region` | ACM certificate cho API Gateway phải cùng Region với API Gateway |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most operational efficiency
- **Constraints:** Individual URLs, secure (HTTPS), API Gateway + Route 53
- **Choose three** options

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A, D, F**

**Giải thích:**
- **A:** Register domain + Route 53 hosted zone + wildcard record trỏ đến API Gateway endpoint. Wildcard DNS record (`*.example.com`) phủ tất cả customer subdomains.
- **D:** Request wildcard certificate (`*.example.com`) trong ACM cùng Region với API Gateway (required).
- **F:** Tạo custom domain name trong API Gateway, import certificate từ ACM → API Gateway tự động serve HTTPS.
- Cách này operational efficient: chỉ cần 1 wildcard cert + 1 custom domain cho tất cả customers, không cần tạo riêng lẻ.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- ACM certificate phải cùng Region với API Gateway. Request ở Region khác → không dùng được.

**❌ Đáp án C:**
- Tạo hosted zones riêng cho mỗi customer → operational overhead cao, không cần thiết. Wildcard DNS record là đủ.

**❌ Đáp án E:**
- Tạo multiple API endpoints cho mỗi customer → operational overhead rất cao, không cần vì API Gateway hỗ trợ custom domain name mapping.

## 6. MẸO GHI NHỚ (MEMORY HOOK)
🧠 *"1 wildcard cert + 1 custom domain = all customers. ACM must be same Region as API Gateway."*
