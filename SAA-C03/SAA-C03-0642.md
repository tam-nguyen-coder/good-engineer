# Question #642 - Topic 1

A company wants to run a gaming application on Amazon EC2 instances that are part of an Auto Scaling group in the AWS Cloud. The application will transmit data by using UDP packets. The company wants to ensure that the application can scale out and in as traffic increases and decreases. What should a solutions architect do to meet these requirements?

## Options

**A.** Attach a Network Load Balancer to the Auto Scaling group.

**B.** Attach an Application Load Balancer to the Auto Scaling group.

**C.** Deploy an Amazon Route 53 record set with a weighted policy to route traffic appropriately.

**D.** Deploy a NAT instance that is configured with port forwarding to the EC2 instances in the Auto Scaling group.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Gaming app on EC2 in ASG, transmits data via UDP packets, needs to scale in/out with traffic.
- **Existing Resources:** EC2 instances in Auto Scaling group.
- **Current Issue/Goal:** Load balancer hỗ trợ UDP + tự động scale với ASG.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `UDP packets` | Application Load Balancer (ALB) chỉ hỗ trợ HTTP/HTTPS (TCP). Network Load Balancer (NLB) hỗ trợ UDP. |
| `Auto Scaling group` | Cần load balancer gắn với ASG để scale. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most suitable / Meet requirements
- **Constraints:** UDP protocol, Auto Scaling support

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- NLB hỗ trợ UDP (Layer 4), trong khi ALB chỉ hỗ trợ HTTP/HTTPS (Layer 7).
- NLB có thể gắn trực tiếp với Auto Scaling group → tự động đăng ký/hủy đăng ký instance.
- NLB phù hợp cho gaming/VoIP applications sử dụng UDP.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- ALB không hỗ trợ UDP, chỉ HTTP/HTTPS và gRPC.

**❌ Đáp án C:**
- Route 53 weighted policy chỉ phân phối DNS traffic, không hỗ trợ health check tự động scale như load balancer.

**❌ Đáp án D:**
- NAT instance dùng cho outbound traffic từ private subnet ra internet, không phải inbound load balancing.
- Không tự động scale với ASG.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"UDP → NLB. ALB = HTTP/HTTPS only."*
