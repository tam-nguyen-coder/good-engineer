# Question #530 - Topic 1

A company has an online gaming application that has TCP and UDP multiplayer gaming capabilities. The company uses Amazon Route 53 to point the application traffic to multiple Network Load Balancers (NLBs) in different AWS Regions. The company needs to improve application performance and decrease latency for the online game in preparation for user growth. Which solution will meet these requirements?

## Options

**A.** Add an Amazon CloudFront distribution in front of the NLBs. Increase the Cache-Control max-age parameter.

**B.** Replace the NLBs with Application Load Balancers (ALBs). Configure Route 53 to use latency-based routing.

**C.** Add AWS Global Accelerator in front of the NLBs. Configure a Global Accelerator endpoint to use the correct listener ports.

**D.** Add an Amazon API Gateway endpoint behind the NLBs. Enable API caching. Override method caching for the different stages.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Online gaming app với TCP và UDP. Hiện tại dùng Route 53 trỏ đến multi-Region NLBs. Cần giảm latency.
- **Existing Resources:** Route 53, multi-Region NLBs.
- **Current Issue/Goal:** Improve performance, decrease latency, support user growth.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `TCP and UDP` | NLB hỗ trợ cả TCP và UDP, ALB chỉ hỗ trợ HTTP/HTTPS |
| `decrease latency` | AWS Global Accelerator: anycast IP, đi qua AWS backbone network |
| `multiple AWS Regions` | Global Accelerator hỗ trợ multi-Region endpoints |
| `Global Accelerator` | Dùng static anycast IP, traffic đi AWS backbone → giảm latency, không qua public internet |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Performance / Latency
- **Constraints:** TCP + UDP gaming traffic, multi-Region

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- AWS Global Accelerator cung cấp 2 static anycast IP → traffic được định tuyến qua AWS backbone network đến NLB gần nhất → giảm latency.
- Global Accelerator hỗ trợ cả TCP và UDP, phù hợp với gaming application.
- Global Accelerator cũng cung cấp health checks, failover tự động giữa các Regions.
- Không cần thay đổi Route 53 hay NLB hiện tại.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- CloudFront chỉ hỗ trợ HTTP/HTTPS, không hỗ trợ TCP và UDP → không phù hợp với gaming app.
- Gaming traffic real-time không thể cache.

**❌ Đáp án B:**
- ALB không hỗ trợ UDP → mất tính năng multiplayer UDP gaming.
- Latency-based routing của Route 53 dựa trên DNS, có thể bị caching, không real-time như Global Accelerator.

**❌ Đáp án D:**
- API Gateway chỉ hỗ trợ HTTP/HTTPS và REST APIs, không hỗ trợ TCP/UDP.
- API Gateway không phải là giải pháp giảm latency cho gaming.

## 6. MẸO GHI NHỚ (MEMORY HOOK)
🧠 *"TCP/UDP gaming + multi-Region + low latency → Global Accelerator + NLB. CloudFront = HTTP only."*
