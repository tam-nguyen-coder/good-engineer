# Question #120 - Topic 1

A company has implemented a self-managed DNS solution on three Amazon EC2 instances behind a Network Load Balancer (NLB) in the us-west- 2 Region. Most of the company's users are located in the United States and Europe. The company wants to improve the performance and availability of the solution. The company launches and configures three EC2 instances in the eu-west-1 Region and adds the EC2 instances as targets for a new NLB. Which solution can the company use to route traffic to all the EC2 instances?

## Options

**A.** Create an Amazon Route 53 geolocation routing policy to route requests to one of the two NLBs. Create an Amazon CloudFront distribution. Use the Route 53 record as the distribution’s origin.

**B.** Create a standard accelerator in AWS Global Accelerator. Create endpoint groups in us-west-2 and eu-west-1. Add the two NLBs as endpoints for the endpoint groups.

**C.** Attach Elastic IP addresses to the six EC2 instances. Create an Amazon Route 53 geolocation routing policy to route requests to one of the six EC2 instances. Create an Amazon CloudFront distribution. Use the Route 53 record as the distribution's origin.

**D.** Replace the two NLBs with two Application Load Balancers (ALBs). Create an Amazon Route 53 latency routing policy to route requests to one of the two ALBs. Create an Amazon CloudFront distribution. Use the Route 53 record as the distribution’s origin.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Self-managed DNS on EC2 + NLB in us-west-2. Added new NLB + EC2 in eu-west-1. Need to route traffic globally.
- **Existing Resources:** NLB + EC2 in us-west-2, NLB + EC2 in eu-west-1.
- **Current Issue/Goal:** Global traffic routing, improve performance + availability.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `United States and Europe` | Multi-Region traffic routing |
| `performances and availability` | **Global Accelerator** (Anycast IP, health checks) |
| `Network Load Balancer` | NLB for TCP/UDP (DNS) |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Global networking + Performance
- **Constraints:** NLB, multi-Region, DNS traffic

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- **AWS Global Accelerator** — dùng Anycast IP, routing traffic đến endpoint group gần nhất.
- Tạo endpoint groups us-west-2 và eu-west-1, thêm NLB làm endpoints.
- Health checks tự động, failover giữa Regions.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- CloudFront dùng cho HTTP/HTTPS, không phù hợp cho DNS traffic (TCP/UDP).

**❌ Đáp án C:**
- Route traffic đến từng EC2 instance — không scale, CloudFront không phù hợp cho DNS.

**❌ Đáp án D:**
- ALB dùng cho HTTP/HTTPS, DNS cần TCP/UDP → NLB mới đúng.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Global Accelerator = Anycast IP + multi-Region routing. NLB = TCP/UDP. ALB = HTTP/HTTPS"*
