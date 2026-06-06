# Question #170 - Topic 1

A company's web application is running on Amazon EC2 instances behind an Application Load Balancer. The company recently changed its policy, which now requires the application to be accessed from one specific country only. Which configuration will meet this requirement?

## Options

**A.** Configure the security group for the EC2 instances.

**B.** Configure the security group on the Application Load Balancer.

**C.** Configure AWS WAF on the Application Load Balancer in a VPC.

**D.** Configure the network ACL for the subnet that contains the EC2 instances.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** ALB + EC2, need to restrict access to one specific country.
- **Existing Resources:** ALB, EC2 instances.
- **Current Issue/Goal:** Geo-restriction by country.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `one specific country` | **Geo-match** via **AWS WAF** |
| `Application Load Balancer` | WAF can be associated with ALB |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Security / Geo-restriction
- **Constraints:** Country-level access control

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- **AWS WAF** có geo-match condition — cho phép / chặn traffic từ specific countries.
- Associate WAF Web ACL với ALB → filter traffic trước khi đến application.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Security group — IP-based, không thể detect country.

**❌ Đáp án B:**
- Security group — ALB cũng là IP-based, không hỗ trợ geo.

**❌ Đáp án D:**
- NACL — IP-based, stateless, không hỗ trợ geo.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"WAF geo-match = country blocking. Security group/NACL = IP only (no country)"*
