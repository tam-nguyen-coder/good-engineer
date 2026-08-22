# Question #577 - Topic 1

A company uses an Amazon CloudFront distribution to serve content pages for its website. The company needs to ensure that clients use a TLS certificate when accessing the company's website. The company wants to automate the creation and renewal of the TLS certificates. Which solution will meet these requirements with the MOST operational efficiency?

## Options

**A.** Use a CloudFront security policy to create a certificate.

**B.** Use a CloudFront origin access control (OAC) to create a certificate.

**C.** Use AWS Certificate Manager (ACM) to create a certificate. Use DNS validation for the domain.

**D.** Use AWS Certificate Manager (ACM) to create a certificate. Use email validation for the domain.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** CloudFront distribution, cần TLS certificate, automate creation và renewal.
- **Existing Resources:** CloudFront distribution.
- **Current Issue/Goal:** Automated TLS certificate lifecycle.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `automate the creation and renewal` | DNS validation: tự động renew (kiểm tra CNAME record). |
| `DNS validation` | ACM tự động renew khi DNS record tồn tại → operational efficiency. |
| `email validation` | Manual: cần click link trong email mỗi lần renew → không automated. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most operational efficiency
- **Constraints:** CloudFront, TLS certificate, automated renewal

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- ACM tạo certificate miễn phí cho CloudFront.
- DNS validation: ACM tự động kiểm tra CNAME record trong DNS zone → auto-renewal khi certificate sắp hết hạn.
- Không cần can thiệp thủ công → operational efficiency cao nhất.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- CloudFront security policy chỉ cấu hình TLS version/cipher, không tạo certificate.

**❌ Đáp án B:**
- OAC dùng để authenticate requests từ CloudFront đến origin, không tạo certificate.

**❌ Đáp án D:**
- Email validation: cần click link trong email mỗi lần renew → không automated.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Automated cert renewal → ACM + DNS validation. Email validation = manual click each time."*
