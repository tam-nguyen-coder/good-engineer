# Question #570 - Topic 1

A company has a large workload that runs every Friday evening. The workload runs on Amazon EC2 instances that are in two Availability Zones in the us-east-1 Region. Normally, the company must run no more than two instances at all times. However, the company wants to scale up to six instances each Friday to handle a regularly repeating increased workload. Which solution will meet these requirements with the LEAST operational overhead?

## Options

**A.** Create a reminder in Amazon EventBridge to scale the instances.

**B.** Create an Auto Scaling group that has a scheduled action.

**C.** Create an Auto Scaling group that uses manual scaling.

**D.** Create an Auto Scaling group that uses automatic scaling.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Workload lớn chạy mỗi tối thứ Sáu. Thường chạy tối đa 2 instances, nhưng cần scale lên 6 instances vào thứ Sáu. Scheduling predictable.
- **Existing Resources:** EC2 instances, ASG cần tạo.
- **Current Issue/Goal:** Auto scaling theo lịch, ít operational overhead.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `every Friday evening` | Lịch đều đặn, có thể dự đoán trước |
| `regularly repeating` | Cần scheduled action |
| `scale up to six instances` | Tăng từ 2 lên 6 |
| `Auto Scaling group scheduled action` | Thay đổi capacity theo thời gian định trước |
| `LEAST operational overhead` | Tự động, không cần can thiệp thủ công |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Least operational overhead
- **Constraints:** Predictable weekly schedule, specific capacity (2→6→2)

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- Auto Scaling group scheduled action cho phép thay đổi desired/min/max capacity theo thời gian cụ thể (cron schedule).
- Cấu hình: schedule vào Friday evening set desired capacity = 6, sau đó set desired = 2 khi workload kết thúc.
- AWS tự động thực hiện scaling action mà không cần can thiệp thủ công.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A (EventBridge reminder):** EventBridge reminder chỉ gửi thông báo, không thể trực tiếp scale instances. Cần kết hợp với Lambda để gọi ASG API – operational overhead cao hơn scheduled action.

**❌ Đáp án C (Manual scaling):** Manual scaling yêu cầu người vận hành thủ công chỉnh sửa ASG capacity mỗi tuần. Operational overhead rất cao.

**❌ Đáp án D (Automatic scaling – dynamic):** Automatic scaling dựa trên metrics (CPU, memory, request count). Không phù hợp vì workload có thể không generate đủ metrics để trigger scale trước khi bắt đầu. Scheduled action phù hợp hơn cho predictable patterns.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Predictable weekly schedule = ASG scheduled action. Know exactly when + how much to scale. Dynamic scaling = metric-based, good for unpredictable patterns."*
