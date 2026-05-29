# Question #473 - Topic 1

A company hosts a website on Amazon EC2 instances behind an Application Load Balancer (ALB). The website serves static content. Website traffic is increasing, and the company is concerned about a potential increase in cost.

## Options

**A.** Create an Amazon CloudFront distribution to cache state files at edge locations

**B.** Create an Amazon ElastiCache cluster. Connect the ALB to the ElastiCache cluster to serve cached files

**C.** Create an AWS WAF web ACL and associate it with the ALB. Add a rule to the web ACL to cache static files

**D.** Create a second ALB in an alternative AWS Region. Route user traffic to the closest Region to minimize data transfer costs

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Website static content, EC2 sau ALB, traffic tăng, lo ngại chi phí.
- **Existing Resources:** EC2 + ALB.
- **Current Issue/Goal:** Reduce cost với static content.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `static content` | CloudFront: CDN cache tại edge, giảm tải cho origin (EC2/ALB). |
| `increasing traffic` | CloudFront giảm data transfer cost và giảm request đến origin. |
| `concerned about cost` | CloudFront: pay per request, giảm load trên EC2 → giảm cost. |
| `state files` | Có thể typo "static files". |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Cost reduction
- **Constraints:** Static content, increasing traffic

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- CloudFront: cache static content tại edge locations gần user.
- Giảm số lượng request đến EC2/ALB origin → giảm cost EC2 và data transfer.
- Có thể customized error pages, SSL termination, DDoS protection.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- ElastiCache: dùng để cache dynamic data, không phải static files.
- ALB không thể "connect" trực tiếp đến ElastiCache.

**❌ Đáp án C:**
- AWS WAF: web application firewall, bảo vệ khỏi web exploits, không phải caching service.
- Không có "rule to cache static files" trong WAF.

**❌ Đáp án D:**
- Tạo ALB ở region khác: tăng complexity và cost (multi-region). Không giải quyết vấn đề cost.
- Data transfer giữa regions còn tốn kém hơn.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Static content + traffic cao + lo cost → CloudFront CDN. WAF = firewall, không cache."*
