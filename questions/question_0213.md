# Question #213 - Topic 1

A company is developing a new mobile app. The company must implement proper traffic filtering to protect its Application Load Balancer (ALB) against common application-level attacks, such as cross-site scripting or SQL injection. The company has minimal infrastructure and operational staff. The company needs to reduce its share of the responsibility in managing, updating, and securing servers for its AWS environment. What should a solutions architect recommend to meet these requirements?

## Options

**A.** Configure AWS WAF rules and associate them with the ALB.

**B.** Deploy the application using Amazon S3 with public hosting enabled.

**C.** Deploy AWS Shield Advanced and add the ALB as a protected resource.

**D.** Create a new ALB that directs traffic to an Amazon EC2 instance running a third-party firewall, which then passes the traffic to the current ALB.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Mobile app, ALB. Need protection against XSS, SQL injection. Minimal staff, reduce management responsibility.
- **Existing Resources:** ALB.
- **Current Issue/Goal:** Managed WAF protection.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `cross-site scripting or SQL injection` | **AWS WAF** (web application firewall) |
| `minimal infrastructure and operational staff` | Managed service |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Security / WAF
- **Constraints:** App-level attack protection, managed

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- **AWS WAF** — protect ALB khỏi common web exploits (XSS, SQL injection, etc.).
- Managed rules — AWS cung cấp sẵn rule sets.
- Associate WAF Web ACL với ALB → zero server management.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- S3 public hosting — không phù hợp cho dynamic app, không có WAF.

**❌ Đáp án C:**
- Shield Advanced — DDoS protection, không phải application-level filtering.

**❌ Đáp án D:**
- Third-party firewall on EC2 — operational overhead (manage, update, secure server).

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"WAF = app-level attacks (XSS/SQLi). Shield = DDoS. Third-party firewall = more overhead"*
