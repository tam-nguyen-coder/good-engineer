# Question #644 - Topic 1

An international company has a subdomain for each country that the company operates in. The subdomains are formatted as example.com, country1.example.com, and country2.example.com. The company's workloads are behind an Application Load Balancer. The company wants to encrypt the website data that is in transit. Which combination of steps will meet these requirements? (Choose two.)

## Options

**A.** Use the AWS Certificate Manager (ACM) console to request a public certificate for the apex top domain example com and a wildcard certificate for *.example.com.

**B.** Use the AWS Certificate Manager (ACM) console to request a private certificate for the apex top domain example.com and a wildcard certificate for *.example.com.

**C.** Use the AWS Certificate Manager (ACM) console to request a public and private certificate for the apex top domain example.com.

**D.** Validate domain ownership by email address. Switch to DNS validation by adding the required DNS records to the DNS provider.

**E.** Validate domain ownership for the domain by adding the required DNS records to the DNS provider.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Multi-country subdomains (example.com, country1.example.com, etc.), workloads behind ALB, need encryption in transit (HTTPS).
- **Existing Resources:** Application Load Balancer, multiple subdomains.
- **Current Issue/Goal:** Deploy SSL/TLS certificates cho apex domain + wildcard subdomains.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `apex top domain` | example.com – cần certificate riêng. |
| `wildcard certificate` | *.example.com – bao phủ tất cả subdomains. |
| `public certificate` | ACM public cert cho internet-facing ALB. |
| `DNS validation` | ACM khuyến nghị DNS validation (tự động renew). |
| `encrypt data in transit` | SSL/TLS certificate trên ALB. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Meet requirements
- **Constraints:** Public-facing ALB, multiple subdomains, choose two

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A và E**

**Giải thích:**
- **A:** Cần public certificate (vì ALB public-facing). Apex domain + wildcard *.example.com bao phủ tất cả subdomains.
- **E:** DNS validation khuyến nghị bởi ACM vì tự động renew khi còn hạn, không cần can thiệp thủ công. Thêm CNAME records vào DNS provider.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Private certificate dùng cho internal resources (NLB internal, API Gateway private), không dùng được với internet-facing ALB.

**❌ Đáp án C:**
- Chỉ request 1 cert cho apex domain → không cover subdomains.
- Public + private cert không cần thiết.

**❌ Đáp án D:**
- Email validation + chuyển sang DNS validation là thừa thãi. Nên chọn DNS validation ngay từ đầu.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"ALB public → ACM public cert. Apex + wildcard *.example.com = all domains. DNS validation for auto-renew."*
