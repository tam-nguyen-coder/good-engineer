# Question #218 - Topic 1

A company has a web server running on an Amazon EC2 instance in a public subnet with an Elastic IP address. The default security group is assigned to the EC2 instance. The default network ACL has been modified to block all traffic. A solutions architect needs to make the web server accessible from everywhere on port 443. Which combination of steps will accomplish this task? (Choose two.)

## Options

**A.** Create a security group with a rule to allow TCP port 443 from source 0.0.0.0/0.

**B.** Create a security group with a rule to allow TCP port 443 to destination 0.0.0.0/0.

**C.** Update the network ACL to allow TCP port 443 from source 0.0.0.0/0.

**D.** Update the network ACL to allow inbound/outbound TCP port 443 from source 0.0.0.0/0 and to destination 0.0.0.0/0.

**E.** Update the network ACL to allow inbound TCP port 443 from source 0.0.0.0/0 and outbound TCP port 32768-65535 to destination 0.0.0.0/0.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** EC2 web server with EIP, default SG, NACL blocks all traffic. Need port 443 from everywhere.
- **Existing Resources:** EC2 instance, EIP.
- **Current Issue/Goal:** Allow HTTPS traffic through SG + NACL.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `default security group` | Cần modify hoặc tạo mới |
| `network ACL has been modified to block all traffic` | NACL stateless — cần inbound + outbound rules |
| `port 443` | HTTPS |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Networking / Security
- **Constraints:** Chọn 2, SG + NACL

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A và E**

**Giải thích:**
- **A: SG inbound allow 443 from 0.0.0.0/0** — SG stateful, chỉ cần inbound rule.
- **E: NACL inbound allow 443 + outbound ephemeral ports** — NACL stateless, return traffic dùng ephemeral ports (32768-65535).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- SG destination — cú pháp sai, SG inbound dùng source.

**❌ Đáp án C:**
- NACL inbound only — NACL stateless, thiếu outbound rule.

**❌ Đáp án D:**
- NACL outbound on 443 — sai, return traffic dùng ephemeral ports, không phải 443.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"SG stateful = inbound only. NACL stateless = inbound + outbound (ephemeral). 32768-65535 = return traffic"*
