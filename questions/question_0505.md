# Question #505 - Topic 1

A company has Amazon EC2 instances that run nightly batch jobs to process data. The EC2 instances run in an Auto Scaling group that uses On-Demand billing. If a job fails on one instance, another instance will reprocess the job. The batch jobs run between 12:00 AM and 06:00 AM local time every day. Which solution will provide EC2 instances to meet these requirements MOST cost-effectively?

## Options

**A.** Purchase a 1-year Savings Plan for Amazon EC2 that covers the instance family of the Auto Scaling group that the batch job uses.

**B.** Purchase a 1-year Reserved Instance for the specific instance type and operating system of the instances in the Auto Scaling group that the batch job uses.

**C.** Create a new launch template for the Auto Scaling group. Set the instances to Spot Instances. Set a policy to scale out based on CPU usage.

**D.** Create a new launch template for the Auto Scaling group. Increase the instance size. Set a policy to scale out based on CPU usage.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Batch job chạy nightly (00:00-06:00), chỉ 6 tiếng/ngày. Nếu job fail, instance khác sẽ reprocess (fault-tolerant).
- **Existing Resources:** Auto Scaling group dùng On-Demand instances.
- **Current Issue/Goal:** Giảm chi phí cho workload không chạy 24/7.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `nightly batch jobs` | Chạy không liên tục (6h/ngày). |
| `if a job fails, another instance will reprocess` | Fault-tolerant → có thể dùng Spot. |
| `MOST cost-effectively` | Cần giải pháp rẻ nhất. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most cost-effective
- **Constraints:** Fault-tolerant batch, only runs 6 hours/day

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- Spot Instances: chi phí thấp hơn On-Demand đến 90%. Vì workload fault-tolerant (job fail → reprocess), Spot là lựa chọn lý tưởng.
- ASG với Spot instances + scale policy → tự động quản lý capacity.
- Batch chạy 6h/ngày không đủ để Savings Plan hoặc RI có lợi (cần chạy gần như 24/7).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- 1-year Savings Plan: commit 1 năm, phù hợp cho workload 24/7 ổn định. Với workload chỉ 6h/ngày, không tối ưu.
- Bạn trả tiền cho cả thời gian không dùng.

**❌ Đáp án B:**
- 1-year Reserved Instance: tương tự Savings Plan, cam kết 1 năm. Workload 6h/ngày không đủ để hồi vốn.
- Spot rẻ hơn nhiều.

**❌ Đáp án D:**
- Tăng instance size + scale policy: chi phí cao hơn (instance lớn hơn). Không giải quyết bài toán cost-effectiveness.
- Vẫn dùng On-Demand.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Fault-tolerant batch + short-lived → Spot Instances. RI/Savings Plan chỉ hợp lý cho workload 24/7."*
