# Question #119 - Topic 1

A global company is using Amazon API Gateway to design REST APIs for its loyalty club users in the us-east-1 Region and the ap-southeast-2 Region. A solutions architect must design a solution to protect these API Gateway managed REST APIs across multiple accounts from SQL injection and cross-site scripting attacks. Which solution will meet these requirements with the LEAST amount of administrative effort?

## Options

**A.** Set up AWS WAF in both Regions. Associate Regional web ACLs with an API stage.

**B.** Set up AWS Firewall Manager in both Regions. Centrally configure AWS WAF rules.

**C.** Set up AWS Shield in bath Regions. Associate Regional web ACLs with an API stage.

**D.** Set up AWS Shield in one of the Regions. Associate Regional web ACLs with an API stage.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** API Gateway REST APIs across 2 Regions (us-east-1, ap-southeast-2), multiple accounts. Protect from SQL injection + XSS.
- **Existing Resources:** API Gateway in 2 Regions.
- **Current Issue/Goal:** WAF protection, least admin effort across multiple accounts.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `SQL injection and cross-site scripting` | Cần **AWS WAF** |
| `across multiple accounts` | Cần central management → **Firewall Manager** |
| `least amount of administrative effort` | Centralized policy management |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Security
- **Constraints:** Multi-account, multi-Region, SQL injection + XSS

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- **AWS Firewall Manager** — quản lý WAF rules tập trung xuyên suốt accounts và Regions.
- Tự động deploy WAF web ACLs với SQL injection + XSS rules.
- **Least administrative effort** — không cần cấu hình từng account/Region riêng.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- AWS WAF từng Region riêng — phải cấu hình thủ công mỗi account/Region → nhiều effort hơn.

**❌ Đáp án C:**
- **AWS Shield** chống DDoS (layer 3/4), không chống SQL injection hay XSS (layer 7).

**❌ Đáp án D:**
- Shield + 1 Region — không đủ, XSS/SQL injection cần WAF.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Firewall Manager = central WAF for multi-account. WAF = SQL injection + XSS. Shield = DDoS only"*
