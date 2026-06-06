# Question #142 - Topic 1

A gaming company is designing a highly available architecture. The application runs on a modified Linux kernel and supports only UDP-based traffic. The company needs the front-end tier to provide the best possible user experience. That tier must have low latency, route traffic to the nearest edge location, and provide static IP addresses for entry into the application endpoints. What should a solutions architect do to meet these requirements?

## Options

**A.** Configure Amazon Route 53 to forward requests to an Application Load Balancer. Use AWS Lambda for the application in AWS Application Auto Scaling.

**B.** Configure Amazon CloudFront to forward requests to a Network Load Balancer. Use AWS Lambda for the application in an AWS Application Auto Scaling group.

**C.** Configure AWS Global Accelerator to forward requests to a Network Load Balancer. Use Amazon EC2 instances for the application in an EC2 Auto Scaling group.

**D.** Configure Amazon API Gateway to forward requests to an Application Load Balancer. Use Amazon EC2 instances for the application in an EC2 Auto Scaling group.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Gaming app, UDP traffic only, low latency, nearest edge, static IPs.
- **Existing Resources:** Chưa có.
- **Current Issue/Goal:** Low latency, UDP, static IP, edge routing.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `UDP-based traffic` | **NLB** (hỗ trợ UDP), ALB không hỗ trợ UDP |
| `static IP addresses` | **Global Accelerator** (2 Anycast static IPs) |
| `route traffic to the nearest edge location` | Global Accelerator Anycast |
| `low latency` | Global Accelerator |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Global networking + Gaming
- **Constraints:** UDP, static IP, edge, low latency

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- **Global Accelerator** — 2 static Anycast IPs, route traffic đến nearest edge location.
- **NLB** — hỗ trợ UDP traffic.
- **EC2 ASG** — application compute, auto-scaling.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- **ALB** không hỗ trợ UDP.
- Route 53 không cung cấp static IP.

**❌ Đáp án B:**
- **CloudFront** hỗ trợ HTTP/HTTPS/WebSocket, **không hỗ trợ UDP**.
- Lambda không phù hợp cho gaming app (UDP).

**❌ Đáp án D:**
- **API Gateway** — HTTP/HTTPS/WebSocket, không UDP.
- ALB không hỗ trợ UDP.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Global Accelerator = static IP + edge routing. NLB = UDP. ALB = HTTP/HTTPS only"*
