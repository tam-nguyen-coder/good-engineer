# Question #231 - Topic 1

An application runs on an Amazon EC2 instance that has an Elastic IP address in VPC A. The application requires access to a database in VPC B. Both VPCs are in the same AWS account. Which solution will provide the required access MOST securely?

## Options

**A.** Create a DB instance security group that allows all traffic from the public IP address of the application server in VPC A.

**B.** Configure a VPC peering connection between VPC A and VPC B.

**C.** Make the DB instance publicly accessible. Assign a public IP address to the DB instance.

**D.** Launch an EC2 instance with an Elastic IP address into VPC B. Proxy all requests through the new EC2 instance.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** EC2 in VPC A needs to access DB in VPC B. Same account.
- **Existing Resources:** VPC A, VPC B.
- **Current Issue/Goal:** Private connectivity between VPCs.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `same AWS account` | **VPC peering** |
| `most securely` | Private connection, no internet |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Networking / VPC
- **Constraints:** Cross-VPC, private, same account

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- **VPC peering** — kết nối trực tiếp giữa 2 VPCs qua AWS internal network.
- Traffic không qua internet → secure.
- Có thể dùng security groups để kiểm soát access.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- SG allow từ public IP — traffic qua internet (EIP), kém secure.

**❌ Đáp án C:**
- Publicly accessible DB — expose database ra internet.

**❌ Đáp án D:**
- Proxy EC2 — thêm complexity, single point of failure.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"VPC peering = private cross-VPC. Public IP/DB = internet exposure (less secure)"*
