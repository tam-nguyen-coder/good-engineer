# Question #405 - Topic 1

A solutions architect is designing the architecture for a software demonstration environment. The environment will run on Amazon EC2 instances in an Auto Scaling group behind an Application Load Balancer (ALB). The system will experience significant increases in traffic during working hours but is not required to operate on weekends. Which combination of actions should the solutions architect take to ensure that the system can scale to meet demand? (Choose two.)

## Options

**A.** Use AWS Auto Scaling to adjust the ALB capacity based on request rate.

**B.** Use AWS Auto Scaling to scale the capacity of the VPC internet gateway.

**C.** Launch the EC2 instances in multiple AWS Regions to distribute the load across Regions.

**D.** Use a target tracking scaling policy to scale the Auto Scaling group based on instance CPU utilization.

**E.** Use scheduled scaling to change the Auto Scaling group minimum, maximum, and desired capacity to zero for weekends. Revert to the default values at the start of the week.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Software demo environment. ALB → ASG → EC2. Traffic spikes during work hours, idle on weekends.
- **Existing Resources:** ALB, Auto Scaling group, EC2 instances.
- **Current Issue/Goal:** Scale to meet demand + save cost on weekends.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `scale to meet demand` | Target tracking scaling policy (e.g., CPU). |
| `not required on weekends` | Scheduled scaling → 0 capacity off-hours. |
| `Choose two` | 2 answers required. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Cost-effective scaling
- **Constraints:** Handle workday spikes, no weekend operation

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D, E**

**Giải thích:**
- **D:** Target tracking scaling policy based on CPU utilization → tự động scale out/in theo demand trong giờ làm việc.
- **E:** Scheduled scaling → set min/max/desired = 0 vào cuối tuần, restore đầu tuần → tiết kiệm cost tối đa.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- ALB tự động scale, không cần cấu hình Auto Scaling cho ALB.

**❌ Đáp án B:**
- Internet Gateway tự động scale, không cần can thiệp.

**❌ Đáp án C:**
- Multi-Region không cần thiết cho demo environment, tăng complexity + cost.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Workday spikes → target tracking (CPU). Weekends off → scheduled scaling to zero."*

