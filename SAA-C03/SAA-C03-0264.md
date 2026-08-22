# Question #264 - Topic 1

A company has a web application hosted over 10 Amazon EC2 instances with traffic directed by Amazon Route 53. The company occasionally experiences a timeout error when attempting to browse the application. The networking team finds that some DNS queries return IP addresses of unhealthy instances, resulting in the timeout error. What should a solutions architect implement to overcome these timeout errors?

## Options

**A.** Create a Route 53 simple routing policy record for each EC2 instance. Associate a health check with each record.

**B.** Create a Route 53 failover routing policy record for each EC2 instance. Associate a health check with each record.

**C.** Create an Amazon CloudFront distribution with EC2 instances as its origin. Associate a health check with the EC2 instances.

**D.** Create an Application Load Balancer (ALB) with a health check in front of the EC2 instances. Route to the ALB from Route 53.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** 10 EC2 instances, Route 53 DNS. DNS returns unhealthy instance IPs → timeouts.
- **Existing Resources:** EC2 instances, Route 53.
- **Current Issue/Goal:** Health check routing to healthy instances only.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `DNS queries return IP addresses of unhealthy instances` | Cần health check + only healthy instances |
| `timeout error` | **ALB health checks** — tự động route đến healthy instances |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Load balancing / DNS
- **Constraints:** Route to healthy instances only

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- **ALB** — tự động health check instances, chỉ forward traffic đến healthy targets.
- Route 53 trỏ đến ALB (1 IP/record) → ALB distributes đến healthy EC2.
- Không cần per-instance DNS records.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Simple routing — không hỗ trợ health checks.

**❌ Đáp án B:**
- Failover routing — chỉ primary/secondary, không cho 10 instances.

**❌ Đáp án C:**
- CloudFront + EC2 origins — CloudFront không health check EC2 trực tiếp.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"ALB health checks = route to healthy instances. Simple routing = no health check"*
