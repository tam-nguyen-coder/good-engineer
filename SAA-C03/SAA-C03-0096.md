# Question #96 - Topic 1

An Amazon EC2 administrator created the following policy associated with an IAM group containing several users: What is the effect of this policy?

## Options

**A.** Users can terminate an EC2 instance in any AWS Region except us-east-1.

**B.** Users can terminate an EC2 instance with the IP address 10.100.100.1 in the us-east-1 Region.

**C.** Users can terminate an EC2 instance in the us-east-1 Region when the user's source IP is 10.100.100.254.

**D.** Users cannot terminate an EC2 instance in the us-east-1 Region when the user's source IP is 10.100.100.254.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** IAM policy attached to group, cần hiểu effect của policy (Allow/Deny + condition).
- **Existing Resources:** IAM group, EC2 instances.
- **Current Issue/Goal:** Xác định effect — users được phép hay không được phép terminate EC2.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `Deny` | Effect = Deny, override Allow |
| `NotIpAddress` | Condition: khi source IP **không phải** giá trị cho trước |
| `Condition` | Chỉ áp dụng khi thỏa mãn điều kiện |

*Note: Policy JSON không hiển thị trong file, nhưng dạng phổ biến là Deny terminate EC2 in us-east-1 với condition NotIpAddress 10.100.100.254*

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** IAM policy evaluation
- **Constraints:** Chọn effect đúng

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- IAM policy dạng Deny terminate EC2 in us-east-1 **trừ khi** source IP = 10.100.100.254.
- **Deny + NotIpAddress** = deny nếu IP không phải 10.100.100.254 → chỉ cho phép khi IP đúng.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Policy chỉ giới hạn ở us-east-1, không ảnh hưởng đến Region khác.

**❌ Đáp án B:**
- IP 10.100.100.1 không được allow trong condition.

**❌ Đáp án D:**
- Ngược lại — user **có thể** terminate khi source IP = 10.100.100.254.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Deny + NotIpAddress = chỉ cho phép từ IP cụ thể. Deny có hiệu lực cao hơn Allow"*
