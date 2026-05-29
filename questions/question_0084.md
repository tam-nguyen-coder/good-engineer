# Question #84 - Topic 1

A company wants to reduce the cost of its existing three-tier web architecture. The web, application, and database servers are running on Amazon EC2 instances for the development, test, and production environments. The EC2 instances average 30% CPU utilization during peak hours and 10% CPU utilization during non-peak hours. The production EC2 instances run 24 hours a day. The development and test EC2 instances run for at least 8 hours each day. The company plans to implement automation to stop the development and test EC2 instances when they are not in use. Which EC2 instance purchasing solution will meet the company's requirements MOST cost-effectively?

## Options

**A.** Use Spot Instances for the production EC2 instances. Use Reserved Instances for the development and test EC2 instances.

**B.** Use Reserved Instances for the production EC2 instances. Use On-Demand Instances for the development and test EC2 instances.

**C.** Use Spot blocks for the production EC2 instances. Use Reserved Instances for the development and test EC2 instances.

**D.** Use On-Demand Instances for the production EC2 instances. Use Spot blocks for the development and test EC2 instances.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Three-tier web app trên EC2 (dev, test, prod). Prod chạy 24/7. Dev/test chạy 8h/ngày.
- **Existing Resources:** EC2 instances cho web, app, DB.
- **Current Issue/Goal:** Cost-effective purchasing: prod steady state, dev/test part-time.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `production EC2 instances run 24 hours a day` | Steady state → **Reserved Instances** (giảm ~40-60%) |
| `development and test EC2 instances run at least 8 hours` | Part-time, sẽ stop khi không dùng → **On-Demand** |
| `most cost-effectively` | Kết hợp RI + On-Demand |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Cost optimization
- **Constraints:** Prod 24/7, dev/test 8h/day (will be stopped)

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- **Reserved Instances** cho production — chạy 24/7, hưởng discount lớn nhất (1 năm hoặc 3 năm).
- **On-Demand Instances** cho dev/test — sẽ stop khi không dùng, chỉ trả cho thời gian chạy. Không cam kết dài hạn vì không chạy full-time.
- Không dùng Spot cho production (risk interruption).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- **Spot Instances** cho production — có thể bị terminate bất kỳ lúc nào, không phù hợp cho production workload.

**❌ Đáp án C:**
- **Spot blocks** đã bị deprecated và không còn available.
- Reserved cho dev/test không tối ưu vì không chạy 24/7.

**❌ Đáp án D:**
- On-Demand cho production — đắt hơn Reserved.
- Spot blocks deprecated.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Reserved = 24/7 steady state. On-Demand = part-time/stopable. Spot = interruptible (not for prod)"*
