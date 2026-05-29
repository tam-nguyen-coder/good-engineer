# Question #180 - Topic 1

A company is designing a cloud communications platform that is driven by APIs. The application is hosted on Amazon EC2 instances behind a Network Load Balancer (NLB). The company uses Amazon API Gateway to provide external users with access to the application through APIs. The company wants to protect the platform against web exploits like SQL injection and also wants to detect and mitigate large, sophisticated DDoS attacks. Which combination of solutions provides the MOST protection? (Choose two.)

## Options

**A.** Use AWS WAF to protect the NLB.

**B.** Use AWS Shield Advanced with the NLB.

**C.** Use AWS WAF to protect Amazon API Gateway.

**D.** Use Amazon GuardDuty with AWS Shield Standard

**E.** Use AWS Shield Standard with Amazon API Gateway.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** API Gateway → NLB → EC2. Need WAF (web exploits) + DDoS protection.
- **Existing Resources:** API Gateway, NLB, EC2.
- **Current Issue/Goal:** Web exploit protection + DDoS mitigation.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `SQL injection` | **AWS WAF** (web application firewall) |
| `large, sophisticated DDoS attacks` | **AWS Shield Advanced** |
| `Network Load Balancer` | WAF không hỗ trợ NLB, Shield Advanced hỗ trợ NLB |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Security / WAF + DDoS
- **Constraints:** Chọn 2, most protection

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B và C**

**Giải thích:**
- **B: Shield Advanced with NLB** — bảo vệ NLB khỏi DDoS, bao gồm cost protection.
- **C: WAF on API Gateway** — chặn SQL injection, XSS, web exploits ở API Gateway.
- WAF không support NLB, chỉ support ALB, API Gateway, CloudFront.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- WAF không hỗ trợ NLB.

**❌ Đáp án D:**
- GuardDuty là threat detection (monitoring), không phải prevention.

**❌ Đáp án E:**
- Shield Standard — free, basic protection, không detect sophisticated DDoS.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"WAF on API Gateway/ALB/CloudFront only (not NLB). Shield Advanced for NLB DDoS"*
