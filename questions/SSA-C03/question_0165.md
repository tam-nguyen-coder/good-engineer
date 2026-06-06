# Question #165 - Topic 1

A solutions architect must design a solution that uses Amazon CloudFront with an Amazon S3 origin to store a static website. The company's security policy requires that all website traffic be inspected by AWS WAF. How should the solutions architect comply with these requirements?

## Options

**A.** Configure an S3 bucket policy to accept requests coming from the AWS WAF Amazon Resource Name (ARN) only.

**B.** Configure Amazon CloudFront to forward all incoming requests to AWS WAF before requesting content from the S3 origin.

**C.** Configure a security group that allows Amazon CloudFront IP addresses to access Amazon S3 only. Associate AWS WAF to CloudFront.

**D.** Configure Amazon CloudFront and Amazon S3 to use an origin access identity (OAI) to restrict access to the S3 bucket. Enable AWS WAF on the distribution.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** CloudFront + S3 static website. All traffic inspected by AWS WAF.
- **Existing Resources:** S3 bucket, CloudFront distribution.
- **Current Issue/Goal:** WAF inspection + secure access.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `AWS WAF` | Web ACL gắn với CloudFront |
| `static website` | S3 origin |
| `origin access identity (OAI)` | Chỉ CloudFront mới access được S3 |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Security / CDN
- **Constraints:** WAF inspection, S3+CloudFront

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- **OAI** — CloudFront identity, S3 bucket policy chỉ allow OAI → user không thể access S3 trực tiếp.
- **AWS WAF on CloudFront** — inspect tất cả traffic tại edge trước khi đến origin.
- Kết hợp: OAI secure origin, WAF filter malicious requests.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- WAF không có ARN kiểu này. S3 bucket policy không thể reference WAF ARN.

**❌ Đáp án B:**
- CloudFront không "forward to WAF" — WAF được associate với CloudFront distribution.

**❌ Đáp án C:**
- Security groups không áp dụng cho S3 (S3 không phải EC2).

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"OAI = CloudFront-only S3 access. WAF on CloudFront = inspect at edge. S3 + security group = wrong"*
