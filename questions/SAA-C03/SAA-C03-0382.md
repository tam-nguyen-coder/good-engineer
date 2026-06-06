# Question #382 - Topic 1

A company has a three-tier application on AWS that ingests sensor data from its users' devices. The traffic flows through a Network Load Balancer (NLB), then to Amazon EC2 instances for the web tier, and finally to EC2 instances for the application tier. The application tier makes calls to a database. What should a solutions architect do to improve the security of the data in transit?

## Options

**A.** Configure a TLS listener. Deploy the server certificate on the NLB.

**B.** Configure AWS Shield Advanced. Enable AWS WAF on the NLB.

**C.** Change the load balancer to an Application Load Balancer (ALB). Enable AWS WAF on the ALB.

**D.** Encrypt the Amazon Elastic Block Store (Amazon EBS) volume on the EC2 instances by using AWS Key Management Service (AWS KMS).

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** NLB → EC2 web → EC2 app → database. Cần improve security of data in transit.
- **Existing Resources:** NLB, EC2 instances, database.
- **Current Issue/Goal:** Encrypt traffic in transit.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `data in transit` | Encrypt network traffic (TLS). |
| `NLB` | NLB hỗ trợ TLS termination (TLS listener). |
| `TLS listener` | NLB decrypt TLS at edge, forward to targets. |
| `server certificate` | Deploy certificate on NLB for TLS. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Improve security of data in transit
- **Constraints:** NLB, EC2

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- NLB supports TLS listeners: deploy server certificate on NLB, NLB terminates TLS.
- Client → NLB: encrypted (TLS). NLB → EC2: can be encrypted or not (depends on configuration).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Shield Advanced: DDoS protection. WAF on NLB: NLB doesn't support AWS WAF (ALB and API Gateway do).

**❌ Đáp án C:**
- Change to ALB + WAF: major architecture change, adds WAF (security filtering) not encryption.

**❌ Đáp án D:**
- EBS encryption: data at rest encryption, không phải in transit.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Data in transit with NLB → TLS listener + server certificate. WAF = filtering. EBS = at rest."*
