# Question #254 - Topic 1

A company is reviewing a recent migration of a three-tier application to a VPC. The security team discovers that the principle of least privilege is not being applied to Amazon EC2 security group ingress and egress rules between the application tiers. What should a solutions architect do to correct this issue?

## Options

**A.** Create security group rules using the instance ID as the source or destination.

**B.** Create security group rules using the security group ID as the source or destination.

**C.** Create security group rules using the VPC CIDR blocks as the source or destination.

**D.** Create security group rules using the subnet CIDR blocks as the source or destination.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Three-tier app, security groups between tiers not following least privilege.
- **Existing Resources:** EC2 instances, security groups.
- **Current Issue/Goal:** Restrict traffic between tiers to specific SGs only.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `principle of least privilege` | Chỉ allow specific sources → **security group ID** |
| `between the application tiers` | SG-to-SG rules |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Security / Networking
- **Constraints:** Least privilege, tier-to-tier

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- Dùng **security group ID** làm source → chỉ instances thuộc SG đó mới được phép.
- Chính xác nhất: web tier SG chỉ allow app tier SG, app tier SG chỉ allow DB tier SG.
- Không cần biết IP — tự động update khi instances thay đổi.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Instance ID — security group rules không hỗ trợ instance ID làm source.

**❌ Đáp án C:**
- VPC CIDR — quá rộng, bao gồm tất cả resources trong VPC.

**❌ Đáp án D:**
- Subnet CIDR — vẫn quá rộng, bao gồm instances không liên quan.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"SG ID as source = least privilege. CIDR = too broad. Instance ID = not supported"*
