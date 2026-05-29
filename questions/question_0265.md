# Question #265 - Topic 1

A solutions architect needs to design a highly available application consisting of web, application, and database tiers. HTTPS content delivery should be as close to the edge as possible, with the least delivery time. Which solution meets these requirements and is MOST secure?

## Options

**A.** Configure a public Application Load Balancer (ALB) with multiple redundant Amazon EC2 instances in public subnets. Configure Amazon CloudFront to deliver HTTPS content using the public ALB as the origin.

**B.** Configure a public Application Load Balancer with multiple redundant Amazon EC2 instances in private subnets. Configure Amazon CloudFront to deliver HTTPS content using the EC2 instances as the origin.

**C.** Configure a public Application Load Balancer (ALB) with multiple redundant Amazon EC2 instances in private subnets. Configure Amazon CloudFront to deliver HTTPS content using the public ALB as the origin.

**D.** Configure a public Application Load Balancer with multiple redundant Amazon EC2 instances in public subnets. Configure Amazon CloudFront to deliver HTTPS content using the EC2 instances as the origin.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** HA app (web + app + DB). HTTPS at edge, least delivery time. Most secure.
- **Existing Resources:** None.
- **Current Issue/Goal:** CloudFront + ALB + private EC2.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `close to the edge` | **CloudFront** |
| `most secure` | EC2 in **private subnets** |
| `public ALB` | ALB trong public subnet, CloudFront origin là ALB |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** CDN / Security
- **Constraints:** Edge delivery, secure

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- **CloudFront** — global edge, giảm latency.
- **Public ALB** — origin, internet-facing.
- **EC2 in private subnets** — không exposed trực tiếp → most secure.
- CloudFront → ALB (public) → EC2 (private).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- EC2 in public subnets — kém secure hơn private subnets.

**❌ Đáp án B:**
- EC2 instances as origin — không thể dùng EC2 trực tiếp làm CloudFront origin (cần ALB).

**❌ Đáp án D:**
- EC2 in public subnets — kém secure. EC2 origin — không tối ưu.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"CloudFront + public ALB + private EC2 = most secure. EC2 in public = less secure"*
