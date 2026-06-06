# Question #246 - Topic 1

A company runs a web application on Amazon EC2 instances in multiple Availability Zones. The EC2 instances are in private subnets. A solutions architect implements an internet-facing Application Load Balancer (ALB) and specifies the EC2 instances as the target group. However, the internet traffic is not reaching the EC2 instances. How should the solutions architect reconfigure the architecture to resolve this issue?

## Options

**A.** Replace the ALB with a Network Load Balancer. Configure a NAT gateway in a public subnet to allow internet traffic.

**B.** Move the EC2 instances to public subnets. Add a rule to the EC2 instances' security groups to allow outbound traffic to 0.0.0.0/0.

**C.** Update the route tables for the EC2 instances' subnets to send 0.0.0.0/0 traffic through the internet gateway route. Add a rule to the EC2 instances' security groups to allow outbound traffic to 0.0.0.0/0.

**D.** Create public subnets in each Availability Zone. Associate the public subnets with the ALB. Update the route tables for the public subnets with a route to the private subnets.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** EC2 in private subnets, internet-facing ALB created. Traffic không đến được EC2.
- **Existing Resources:** EC2 (private subnets), ALB.
- **Current Issue/Goal:** ALB cần public subnets để receive internet traffic.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `internet-facing ALB` | Phải ở **public subnets** |
| `EC2 instances are in private subnets` | ALB có thể target private instances |
| `internet traffic is not reaching` | ALB không có public subnets |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Networking / ALB
- **Constraints:** Internet-facing ALB, private EC2

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- ALB internet-facing cần **public subnets** (với route đến IGW).
- EC2 instances vẫn ở private subnets.
- ALB trong public subnet → route traffic đến private EC2 instances.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- NLB + NAT — NLB cũng cần public subnets, NAT không giải quyết ALB placement.

**❌ Đáp án B:**
- Move EC2 to public — không cần, ALB có thể target private instances.

**❌ Đáp án C:**
- Route table → IGW — EC2 vẫn private, không cần IGW route cho instances.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Internet-facing ALB = public subnets. EC2 can stay private. No need to move instances"*
