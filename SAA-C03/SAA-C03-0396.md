# Question #396 - Topic 1

A company has implemented a self-managed DNS service on AWS. The solution consists of the following: • Amazon EC2 instances in different AWS Regions • Endpoints of a standard accelerator in AWS Global Accelerator The company wants to protect the solution against DDoS attacks. What should a solutions architect do to meet this requirement?

## Options

**A.** Subscribe to AWS Shield Advanced. Add the accelerator as a resource to protect.

**B.** Subscribe to AWS Shield Advanced. Add the EC2 instances as resources to protect.

**C.** Create an AWS WAF web ACL that includes a rate-based rule. Associate the web ACL with the accelerator.

**D.** Create an AWS WAF web ACL that includes a rate-based rule. Associate the web ACL with the EC2 instances.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Self-managed DNS on EC2 (multi-Region) + Global Accelerator endpoints. Need DDoS protection.
- **Existing Resources:** EC2 instances, Global Accelerator.
- **Current Issue/Goal:** DDoS protection.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `DDoS attacks` | AWS Shield Advanced: DDoS protection, supports Global Accelerator. |
| `DNS service` | UDP-based → WAF không support UDP (HTTP/HTTPS only). |
| `AWS Shield Advanced` | Protects against DDoS, can protect Global Accelerator, Route 53, CloudFront. |
| `Global Accelerator` | Shield Advanced có thể protect accelerator endpoints. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** DDoS protection
- **Constraints:** DNS (UDP), Global Accelerator, multi-Region

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- AWS Shield Advanced: managed DDoS protection service.
- Global Accelerator được supported bởi Shield Advanced → add accelerator as resource to protect.
- DNS (UDP) không thể dùng WAF (WAF only HTTP/HTTPS).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Shield Advanced có thể protect EC2, nhưng với Global Accelerator đã có, nên bảo vệ ở accelerator layer (trước khi traffic đến EC2).

**❌ Đáp án C:**
- WAF không support UDP (DNS), chỉ HTTP/HTTPS. Global Accelerator không support WAF association.

**❌ Đáp án D:**
- WAF không support UDP. EC2 không thể "associate web ACL" trực tiếp.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"DNS (UDP) + DDoS → Shield Advanced + Global Accelerator. WAF = HTTP only, không support UDP."*
