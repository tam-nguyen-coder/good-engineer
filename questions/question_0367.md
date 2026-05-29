# Question #367 - Topic 1

A company is using Amazon Route 53 latency-based routing to route requests to its UDP-based application for users around the world. The application is hosted on redundant servers in the company's on-premises data centers in the United States, Asia, and Europe. The company's compliance requirements state that the application must be hosted on premises. The company wants to improve the performance and availability of the application. What should a solutions architect do to meet these requirements?

## Options

**A.** Configure three Network Load Balancers (NLBs) in the three AWS Regions to address the on-premises endpoints. Create an accelerator by using AWS Global Accelerator, and register the NLBs as its endpoints. Provide access to the application by using a CNAME that points to the accelerator DNS.

**B.** Configure three Application Load Balancers (ALBs) in the three AWS Regions to address the on-premises endpoints. Create an accelerator by using AWS Global Accelerator, and register the ALBs as its endpoints. Provide access to the application by using a CNAME that points to the accelerator DNS.

**C.** Configure three Network Load Balancers (NLBs) in the three AWS Regions to address the on-premises endpoints. In Route 53, create a latency-based record that points to the three NLBs, and use it as an origin for an Amazon CloudFront distribution. Provide access to the application by using a CNAME that points to the CloudFront DNS.

**D.** Configure three Application Load Balancers (ALBs) in the three AWS Regions to address the on-premises endpoints. In Route 53, create a latency-based record that points to the three ALBs, and use it as an origin for an Amazon CloudFront distribution. Provide access to the application by using a CNAME that points to the CloudFront DNS.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** UDP app on-premises (3 regions: US, Asia, Europe). Route 53 latency routing. Must stay on-premises. Improve performance and availability.
- **Existing Resources:** On-premises servers, Route 53 latency records.
- **Current Issue/Goal:** Better performance/availability with Global Accelerator.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `UDP-based application` | Global Accelerator supports UDP. ALB = HTTP/HTTPS only (no UDP). CloudFront = no UDP. |
| `on premises` | NLB can route to on-premises endpoints via IP addresses. |
| `AWS Global Accelerator` | Anycast IP, route to nearest endpoint via AWS global network. |
| `Network Load Balancer` | Supports UDP + TCP, can target IP addresses (on-premises). |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Improve performance and availability
- **Constraints:** UDP, on-premises, global users

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- NLB (Network Load Balancer): supports UDP, có thể target on-premises endpoints (by IP).
- Global Accelerator: Anycast IP → user traffic routed to nearest endpoint via AWS backbone → lower latency and improved availability.
- Compliance: on-premises servers retained, NLBs chỉ là front-end.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- ALB không support UDP (HTTP/HTTPS only).

**❌ Đáp án C:**
- CloudFront không support UDP.

**❌ Đáp án D:**
- CloudFront không support UDP. ALB không support UDP.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"UDP app + on-premises + global → NLB + Global Accelerator. ALB = HTTP only. CloudFront = không UDP."*
