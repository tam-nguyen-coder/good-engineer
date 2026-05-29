# Question #104 - Topic 1

A solutions architect must design a highly available infrastructure for a website. The website is powered by Windows web servers that run on Amazon EC2 instances. The solutions architect must implement a solution that can mitigate a large-scale DDoS attack that originates from thousands of IP addresses. Downtime is not acceptable for the website. Which actions should the solutions architect take to protect the website from such an attack? (Choose two.)

## Options

**A.** Use AWS Shield Advanced to stop the DDoS attack.

**B.** Configure Amazon GuardDuty to automatically block the attackers.

**C.** Configure the website to use Amazon CloudFront for both static and dynamic content.

**D.** Use an AWS Lambda function to automatically add attacker IP addresses to VPC network ACLs.

**E.** Use EC2 Spot Instances in an Auto Scaling group with a target tracking scaling policy that is set to 80% CPU utilization.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Windows web servers trên EC2, mitigate large-scale DDoS từ thousands of IPs.
- **Existing Resources:** EC2 Windows web servers.
- **Current Issue/Goal:** DDoS protection, zero downtime.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `DDoS attack` | Cần **AWS Shield Advanced** |
| `thousands of IP addresses` | Không thể block manually từng IP |
| `Downtime is not acceptable` | Cần CDN/edge protection |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Security / DDoS mitigation
- **Constraints:** Chọn 2 đáp án, zero downtime

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A và C**

**Giải thích:**
- **A: AWS Shield Advanced** — managed DDoS protection, bao gồm detection + mitigation, cost protection.
- **C: CloudFront** — CDN hấp thụ DDoS traffic tại edge, giảm tải cho origin servers, bảo vệ khỏi layer 3/4 DDoS.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- **GuardDuty** — phát hiện threats (threat detection), nhưng không tự động block DDoS.

**❌ Đáp án D:**
- Lambda + NACL — không hiệu quả cho DDoS từ "thousands of IPs" (NACL giới hạn số rules).

**❌ Đáp án E:**
- Spot Instances — không phù hợp production, không giúp chống DDoS.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Shield Advanced = DDoS protection. CloudFront = absorb DDoS at edge. GuardDuty = threat detection (not mitigation)"*
