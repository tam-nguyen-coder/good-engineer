# Question #56 - Topic 1

A company has registered its domain name with Amazon Route 53. The company uses Amazon API Gateway in the ca-central-1 Region as a public interface for its backend microservice APIs. Third-party services consume the APIs securely. The company wants to design its API Gateway URL with the company's domain name and corresponding certificate so that the third-party services can use HTTPS. Which solution will meet these requirements?

## Options

**A.** Create stage variables in API Gateway with Name="Endpoint-URL" and Value="Company Domain Name" to overwrite the default URL. Import the public certificate associated with the company's domain name into AWS Certificate Manager (ACM).

**B.** Create Route 53 DNS records with the company's domain name. Point the alias record to the Regional API Gateway stage endpoint. Import the public certificate associated with the company's domain name into AWS Certificate Manager (ACM) in the us-east-1 Region.

**C.** Create a Regional API Gateway endpoint. Associate the API Gateway endpoint with the company's domain name. Import the public certificate associated with the company's domain name into AWS Certificate Manager (ACM) in the same Region. Attach the certificate to the API Gateway endpoint. Configure Route 53 to route traffic to the API Gateway endpoint.

**D.** Create a Regional API Gateway endpoint. Associate the API Gateway endpoint with the company's domain name. Import the public certificate associated with the company's domain name into AWS Certificate Manager (ACM) in the us-east-1 Region. Attach the certificate to the API Gateway APIs. Create Route 53 DNS records with the company's domain name. Point an A record to the company's domain name.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** API Gateway Regional endpoint in ca-central-1, cần custom domain + HTTPS.
- **Existing Resources:** Route 53 domain, API Gateway in ca-central-1.
- **Current Issue/Goal:** Custom domain URL + SSL certificate cho third-party HTTPS access.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `Regional API Gateway endpoint` | Không phải edge-optimized — cert phải cùng Region |
| `corresponding certificate` | Cần ACM certificate gắn với custom domain |
| `Route 53` | Alias record trỏ đến API Gateway endpoint |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Networking + Security
- **Constraints:** Regional endpoint, custom domain, HTTPS

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- Với **Regional API Gateway endpoint**, certificate phải được import vào ACM **cùng Region** với API Gateway (ca-central-1).
- **Custom domain name** trong API Gateway cho phép map domain riêng.
- Route 53 alias record trỏ đến API Gateway endpoint (Regional).
- ACM certificate ở cùng Region được attach vào custom domain.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Stage variables không thể override URL endpoint của API Gateway.

**❌ Đáp án B:**
- us-east-1 chỉ dùng cho **CloudFront** (edge-optimized) API Gateway, không phải Regional endpoint.
- Cert phải cùng Region với Regional endpoint.

**❌ Đáp án D:**
- Cert ở us-east-1 là sai (phải cùng Region ca-central-1).
- A record trỏ đến domain name là sai (phải trỏ đến API Gateway endpoint).

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Regional API Gateway → cert cùng Region. Edge-optimized → cert us-east-1 (vì CloudFront)"*
