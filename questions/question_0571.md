# Question #571 - Topic 1

A company is creating a REST API. The company has strict requirements for the use of TLS. The company requires TLSv1.3 on the API endpoints. The company also requires a specific public third-party certificate authority (CA) to sign the TLS certificate. Which solution will meet these requirements?

## Options

**A.** Use a local machine to create a certificate that is signed by the third-party CImport the certificate into AWS Certificate Manager (ACM). Create an HTTP API in Amazon API Gateway with a custom domain. Configure the custom domain to use the certificate.

**B.** Create a certificate in AWS Certificate Manager (ACM) that is signed by the third-party CA. Create an HTTP API in Amazon API Gateway with a custom domain. Configure the custom domain to use the certificate.

**C.** Use AWS Certificate Manager (ACM) to create a certificate that is signed by the third-party CA. Import the certificate into AWS Certificate Manager (ACM). Create an AWS Lambda function with a Lambda function URL. Configure the Lambda function URL to use the certificate.

**D.** Create a certificate in AWS Certificate Manager (ACM) that is signed by the third-party CA. Create an AWS Lambda function with a Lambda function URL. Configure the Lambda function URL to use the certificate.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Công ty đang tạo REST API, yêu cầu TLSv1.3 và muốn dùng một third-party CA cụ thể để ký TLS certificate.
- **Existing Resources:** Chưa có resources.
- **Current Issue/Goal:** Cần đáp ứng TLSv1.3 + certificate từ third-party CA cho API endpoints.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `third-party CA` | ACM không thể tạo certificate signed bởi third-party CA → phải tự tạo và import vào ACM. |
| `ACM` | Dùng để lưu trữ và quản lý certificate, nhưng ACM's private CA không phải third-party CA. |
| `API Gateway custom domain` | Cần custom domain để gắn certificate. |
| `TLSv1.3` | API Gateway hỗ trợ TLSv1.3 với custom domain. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Which solution meets requirements
- **Constraints:** TLSv1.3, specific third-party CA, REST API

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- ACM không thể tạo certificate signed bởi third-party CA; ACM chỉ dùng Amazon's own CA hoặc cho phép import certificate từ ngoài.
- Dùng local machine tạo CSR, gửi đến third-party CA ký, sau đó import certificate vào ACM.
- API Gateway với custom domain cho phép gắn certificate từ ACM.
- API Gateway hỗ trợ TLSv1.3 trên custom domain endpoints.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- ACM không thể tạo certificate signed bởi third-party CA. ACM chỉ tạo certificate từ Amazon's own CA (private hoặc public trusted CA của Amazon).

**❌ Đáp án C:**
- ACM không thể tạo certificate signed bởi third-party CA. Lambda Function URL không hỗ trợ gắn certificate tùy chỉnh (chỉ dùng HTTPS mặc định của AWS).

**❌ Đáp án D:**
- Giống B và C: ACM không thể tạo certificate signed bởi third-party CA, Lambda Function URL không support custom certificate.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Third-party CA cert → create locally → import ACM → API Gateway custom domain. ACM creates certs using Amazon's own CA, not third-party."*
