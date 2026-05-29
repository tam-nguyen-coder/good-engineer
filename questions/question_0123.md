# Question #123 - Topic 1

A company has a dynamic web application hosted on two Amazon EC2 instances. The company has its own SSL certificate, which is on each instance to perform SSL termination. There has been an increase in traffic recently, and the operations team determined that SSL encryption and decryption is causing the compute capacity of the web servers to reach their maximum limit. What should a solutions architect do to increase the application's performance?

## Options

**A.** Create a new SSL certificate using AWS Certificate Manager (ACM). Install the ACM certificate on each instance.

**B.** Create an Amazon S3 bucket Migrate the SSL certificate to the S3 bucket. Configure the EC2 instances to reference the bucket for SSL termination.

**C.** Create another EC2 instance as a proxy server. Migrate the SSL certificate to the new instance and configure it to direct connections to the existing EC2 instances.

**D.** Import the SSL certificate into AWS Certificate Manager (ACM). Create an Application Load Balancer with an HTTPS listener that uses the SSL certificate from ACM.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** EC2 instances tự SSL termination → CPU max. Cần offload SSL.
- **Existing Resources:** 2 EC2 instances, SSL certificate.
- **Current Issue/Goal:** Giảm CPU load by offloading SSL.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `SSL encryption and decryption is causing... maximum limit` | Cần offload SSL → **ALB** |
| `Application Load Balancer` | ALB có thể terminate SSL |
| `increase the application's performance` | Giảm CPU trên EC2 |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Performance optimization
- **Constraints:** Offload SSL from EC2

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- **Import SSL cert vào ACM** — dùng cert hiện tại.
- **ALB với HTTPS listener** — ALB làm SSL termination, EC2 chỉ nhận HTTP traffic.
- Giảm CPU load trên EC2 instances.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- ACM cert trên EC2 — SSL vẫn do EC2 xử lý, không offload.

**❌ Đáp án B:**
- S3 không thể làm SSL termination cho EC2.

**❌ Đáp án C:**
- Proxy EC2 instance — vẫn là EC2 xử lý SSL, không khác biệt.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"ALB HTTPS listener = offload SSL from EC2. ACM = import + manage cert. EC2 SSL = CPU overhead"*
