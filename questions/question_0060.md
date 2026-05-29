# Question #60 - Topic 1

A company has a website hosted on AWS. The website is behind an Application Load Balancer (ALB) that is configured to handle HTTP and HTTPS separately. The company wants to forward all requests to the website so that the requests will use HTTPS. What should a solutions architect do to meet this requirement?

## Options

**A.** Update the ALB's network ACL to accept only HTTPS traffic.

**B.** Create a rule that replaces the HTTP in the URL with HTTPS.

**C.** Create a listener rule on the ALB to redirect HTTP traffic to HTTPS.

**D.** Replace the ALB with a Network Load Balancer configured to use Server Name Indication (SNI).

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Website sau ALB, ALB đang handle cả HTTP và HTTPS riêng.
- **Existing Resources:** ALB với HTTP + HTTPS listeners.
- **Current Issue/Goal:** Forward tất cả requests → HTTPS.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `forward all requests to use HTTPS` | Redirect HTTP → HTTPS |
| `Application Load Balancer` | ALB hỗ trợ redirect action |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Network optimization
- **Constraints:** ALB, HTTP→HTTPS redirect

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- **ALB listener rule** có built-in **redirect action** — có thể redirect HTTP 80 → HTTPS 443.
- Không cần thay đổi application code hoặc infrastructure.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- **Network ACL** là stateless firewall ở subnet level, không làm redirect. Chỉ block traffic, không chuyển hướng.

**❌ Đáp án B:**
- URL rewriting không phải tính năng của ALB. Không có "rule that replaces HTTP in URL".

**❌ Đáp án D:**
- **NLB** không hỗ trợ HTTP redirect (NLB là layer 4).
- SNI dùng cho multiple TLS certificates, không phải redirect.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"ALB listener rule → redirect action: HTTP 80 → HTTPS 443. NLB = layer 4, no redirect"*
