# Question #150 - Topic 1

A company is migrating an application from on-premises servers to Amazon EC2 instances. As part of the migration design requirements, a solutions architect must implement infrastructure metric alarms. The company does not need to take action if CPU utilization increases to more than 50% for a short burst of time. However, if the CPU utilization increases to more than 50% and read IOPS on the disk are high at the same time, the company needs to act as soon as possible. The solutions architect also must reduce false alarms. Which solution should the solutions architect do to meet these requirements?

## Options

**A.** Create Amazon CloudWatch composite alarms where possible.

**B.** Create Amazon CloudWatch dashboards to visualize the metrics and react to issues quickly.

**C.** Create Amazon CloudWatch Synthetics canaries to monitor the application and raise an alarm.

**D.** Create single Amazon CloudWatch metric alarms with multiple metric thresholds where possible.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** EC2 metrics monitoring. CPU > 50% alone = no action. CPU > 50% AND high read IOPS = action needed.
- **Existing Resources:** EC2 instances.
- **Current Issue/Goal:** Alarm chỉ khi cả 2 metrics cùng vượt threshold.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `CPU utilization... AND read IOPS... high at the same time` | **Composite alarm** — kết hợp nhiều điều kiện |
| `reduce false alarms` | Chỉ alarm khi cả 2 metrics breach |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Monitoring
- **Constraints:** Combined condition, reduce false alarms

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- **CloudWatch composite alarms** — kết hợp nhiều metric alarms với AND/OR logic.
- Tạo 2 metric alarms (CPU > 50%, ReadIOPS high), composite alarm chỉ trigger khi **cả 2** đều ALARM.
- Giảm false alarms so với single metric alarm.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Dashboards — hiển thị metrics, không tự động alarm.

**❌ Đáp án C:**
- Synthetics canaries — monitor endpoints, không phải infrastructure metrics.

**❌ Đáp án D:**
- Single metric alarm — không thể kết hợp multiple conditions với AND logic.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Composite alarm = AND/OR multiple conditions. Reduces false alarms. Single alarm = one metric only"*
