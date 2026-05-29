# Question #73 - Topic 1

A company recently launched Linux-based application instances on Amazon EC2 in a private subnet and launched a Linux-based bastion host on an Amazon EC2 instance in a public subnet of a VPC. A solutions architect needs to connect from the on-premises network, through the company's internet connection, to the bastion host, and to the application servers. The solutions architect must make sure that the security groups of all the EC2 instances will allow that access. Which combination of steps should the solutions architect take to meet these requirements? (Choose two.)

## Options

**A.** Replace the current security group of the bastion host with one that only allows inbound access from the application instances.

**B.** Replace the current security group of the bastion host with one that only allows inbound access from the internal IP range for the company.

**C.** Replace the current security group of the bastion host with one that only allows inbound access from the external IP range for the company.

**D.** Replace the current security group of the application instances with one that allows inbound SSH access from only the private IP address of the bastion host.

**E.** Replace the current security group of the application instances with one that allows inbound SSH access from only the public IP address of the bastion host.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Bastion host (public subnet) + app instances (private subnet). Connect from on-prem qua internet.
- **Existing Resources:** VPC, public subnet (bastion), private subnet (app).
- **Current Issue/Goal:** Allow on-prem → bastion → app servers.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `on-premises network, through the company's internet connection` | Kết nối từ external IP của company |
| `bastion host` | Jump box — SSH từ on-prem rồi SSH tiếp đến app |
| `private IP address of the bastion host` | App servers chỉ accept từ bastion's private IP |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Network security
- **Constraints:** Chọn 2 đáp án

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C và D**

**Giải thích:**
- **C: Bastion SG allow inbound SSH từ external IP range của company** — on-prem connect từ public IP range của công ty.
- **D: App instances SG allow inbound SSH từ private IP của bastion** — bastion trong cùng VPC nên dùng private IP để SSH đến app.
- Security group best practice: chỉ allow specific source IP/SG, không allow 0.0.0.0/0.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Bastion cần inbound từ on-prem (bên ngoài), không phải từ app instances.

**❌ Đáp án B:**
- On-prem connect qua internet → public IP, không phải internal IP range.

**❌ Đáp án E:**
- Bastion's public IP có thể thay đổi (trừ khi Elastic IP). Dùng private IP an toàn và ổn định hơn trong cùng VPC.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Bastion SG allow from on-prem external IP. App SG allow from bastion private IP = 2-hop SSH"*
