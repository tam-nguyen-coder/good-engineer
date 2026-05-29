# Question #169 - Topic 1

A company is concerned about the security of its public web application due to recent web attacks. The application uses an Application Load Balancer (ALB). A solutions architect must reduce the risk of DDoS attacks against the application. What should the solutions architect do to meet this requirement?

## Options

**A.** Add an Amazon Inspector agent to the ALB.

**B.** Configure Amazon Macie to prevent attacks.

**C.** Enable AWS Shield Advanced to prevent attacks.

**D.** Configure Amazon GuardDuty to monitor the ALB.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Public web app behind ALB, need to reduce DDoS risk.
- **Existing Resources:** ALB.
- **Current Issue/Goal:** DDoS protection.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `DDoS attacks` | **AWS Shield** (Advanced for ALB protection) |
| `reduce the risk` | Proactive prevention |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Security / DDoS
- **Constraints:** DDoS prevention for ALB

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- **AWS Shield Advanced** — cung cấp DDoS protection cho ALB, CloudFront, Route 53.
- Includes DDoS cost protection, 24/7 DDoS response team, real-time metrics.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Amazon Inspector — vulnerability assessment cho EC2, không phải DDoS.

**❌ Đáp án B:**
- Amazon Macie — phát hiện sensitive data trong S3, không phải DDoS.

**❌ Đáp án D:**
- Amazon GuardDuty — threat detection (monitoring), không phải prevention.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Shield Advanced = DDoS protection for ALB. Inspector = vuln scan. Macie = data privacy. GuardDuty = threat detection"*
