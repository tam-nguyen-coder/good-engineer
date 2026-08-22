# Question #282 - Topic 1

A company runs a web application that is deployed on Amazon EC2 instances in the private subnet of a VPC. An Application Load Balancer (ALB) that extends across the public subnets directs web traffic to the EC2 instances. The company wants to implement new security measures to restrict inbound traffic from the ALB to the EC2 instances while preventing access from any other source inside or outside the private subnet of the EC2 instances. Which solution will meet these requirements?

## Options

**A.** Configure a route in a route table to direct traffic from the internet to the private IP addresses of the EC2 instances.

**B.** Configure the security group for the EC2 instances to only allow traffic that comes from the security group for the ALB.

**C.** Move the EC2 instances into the public subnet. Give the EC2 instances a set of Elastic IP addresses.

**D.** Configure the security group for the ALB to allow any TCP traffic on any port.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** EC2 instances ở private subnet, ALB ở public subnet. Cần giới hạn traffic chỉ từ ALB vào EC2, không cho phép nguồn nào khác.
- **Existing Resources:** VPC, ALB (public subnets), EC2 (private subnet).
- **Current Issue/Goal:** Restrict inbound traffic to EC2 only from ALB, block all other sources.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `security group` | SG reference → có thể trỏ SG nguồn (ALB's SG) thay vì CIDR. |
| `private subnet` | Không có internet gateway mặc định, chỉ nhận traffic qua ALB. |
| `restrict inbound traffic from the ALB` | Security group chaining: dùng SG của ALB làm nguồn cho SG của EC2. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Which solution meets requirements
- **Constraints:** Only ALB → EC2, block all other sources

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- Security group chaining: gán security group cho ALB, sau đó cấu hình security group của EC2 chỉ cho phép inbound traffic từ security group của ALB (dùng SG ID làm source).
- Điều này đảm bảo chỉ traffic từ ALB mới được phép, block mọi nguồn khác (kể cả trong private subnet).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Route table không kiểm soát inbound traffic (chỉ kiểm soát outbound). Không thể dùng route table để chặn traffic đến private IPs.

**❌ Đáp án C:**
- Đưa EC2 ra public subnet với Elastic IP là ngược lại yêu cầu (làm EC2 public hơn, mất kiểm soát).

**❌ Đáp án D:**
- ALB's security group nên giới hạn traffic vào ALB, không phải là giải pháp để kiểm soát traffic từ ALB đến EC2. Không bảo vệ EC2.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"SG chaining: ALB's SG in EC2's SG inbound rule = only ALB can reach EC2."*
