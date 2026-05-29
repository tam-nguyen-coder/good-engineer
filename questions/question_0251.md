# Question #251 - Topic 1

An Amazon EC2 instance is located in a private subnet in a new VPC. This subnet does not have outbound internet access, but the EC2 instance needs the ability to download monthly security updates from an outside vendor. What should a solutions architect do to meet these requirements?

## Options

**A.** Create an internet gateway, and attach it to the VPC. Configure the private subnet route table to use the internet gateway as the default route.

**B.** Create a NAT gateway, and place it in a public subnet. Configure the private subnet route table to use the NAT gateway as the default route.

**C.** Create a NAT instance, and place it in the same subnet where the EC2 instance is located. Configure the private subnet route table to use the NAT instance as the default route.

**D.** Create an internet gateway, and attach it to the VPC. Create a NAT instance, and place it in the same subnet where the EC2 instance is located. Configure the private subnet route table to use the internet gateway as the default route.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** EC2 in private subnet needs outbound internet access for security updates.
- **Existing Resources:** Private subnet, VPC.
- **Current Issue/Goal:** Outbound-only internet access.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `private subnet` | Không thể direct IGW |
| `download... from an outside vendor` | Outbound internet only |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Networking / NAT
- **Constraints:** Private subnet, outbound internet

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- **NAT Gateway** trong public subnet — cho phép instances trong private subnet kết nối ra internet (outbound only).
- Private subnet route table trỏ default route (0.0.0.0/0) đến NAT Gateway.
- Managed service, HA trong AZ.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- IGW trực tiếp — private subnet không thể route trực tiếp đến IGW (cần public IP).

**❌ Đáp án C:**
- NAT instance in same subnet — NAT instance cần ở public subnet.

**❌ Đáp án D:**
- IGW + NAT instance in private subnet — NAT instance cần public subnet.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"NAT Gateway in public subnet + route from private = outbound internet. IGW = public subnets only"*
