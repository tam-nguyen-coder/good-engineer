# Question #660 - Topic 1

A company hosts an application on Amazon EC2 On-Demand Instances in an Auto Scaling group. Application peak hours occur at the same time each day. Application users report slow application performance at the start of peak hours. The application performs normally 2-3 hours after peak hours begin. The company wants to ensure that the application works properly at the start of peak hours. Which solution will meet these requirements?

## Options

**A.** Configure an Application Load Balancer to distribute traffic properly to the instances.

**B.** Configure a dynamic scaling policy for the Auto Scaling group to launch new instances based on memory utilization.

**C.** Configure a dynamic scaling policy for the Auto Scaling group to launch new instances based on CPU utilization.

**D.** Configure a scheduled scaling policy for the Auto Scaling group to launch new instances before peak hours.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** ASG with EC2 On-Demand. Peak hours same time daily. Slow at start of peak, normalizes 2-3 hours later.
- **Existing Resources:** Auto Scaling group, EC2 instances.
- **Current Issue/Goal:** Application must perform well at start of peak hours.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `peak hours occur at the same time each day` | Predictable pattern → scheduled scaling. |
| `slow at the start of peak hours` | Dynamic scaling reacts too slowly (need time to launch instances). |
| `scheduled scaling` | Scale out BEFORE peak hours → instances ready when traffic arrives. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Meet requirements
- **Constraints:** Predictable daily peak, need zero lag at start

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- Scheduled scaling policy: scale out trước peak hours (e.g., 15-30 phút trước).
- Khi peak bắt đầu, instances đã sẵn sàng → không bị slow.
- Phù hợp với pattern predictable (cùng giờ mỗi ngày).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- ALB chỉ phân phối traffic, không giải quyết vấn đề thiếu capacity.

**❌ Đáp án B:**
- Dynamic scaling based on memory utilization: reactive, có độ trễ (launch instance mất vài phút).

**❌ Đáp án C:**
- Dynamic scaling based on CPU utilization: reactive, có độ trễ.
- CPU increase sau khi traffic đã đến → slow xảy ra trước khi scale.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Predictable peak → Scheduled scaling (proactive). Dynamic scaling = reactive (slow)."*
