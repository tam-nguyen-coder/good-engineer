# Question #300 - Topic 1

A company needs to migrate a legacy application from an on-premises data center to the AWS Cloud because of hardware capacity constraints. The application runs 24 hours a day, 7 days a week. The application's database storage continues to grow over time. What should a solutions architect do to meet these requirements MOST cost-effectively?

## Options

**A.** Migrate the application layer to Amazon EC2 Spot Instances. Migrate the data storage layer to Amazon S3.

**B.** Migrate the application layer to Amazon EC2 Reserved Instances. Migrate the data storage layer to Amazon RDS On-Demand Instances.

**C.** Migrate the application layer to Amazon EC2 Reserved Instances. Migrate the data storage layer to Amazon Aurora Reserved Instances.

**D.** Migrate the application layer to Amazon EC2 On-Demand Instances. Migrate the data storage layer to Amazon RDS Reserved Instances.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Legacy app migrate from on-premises to AWS. App runs 24/7, database storage grows over time.
- **Existing Resources:** Legacy on-premises app.
- **Current Issue/Goal:** Migration with most cost-effective solution.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `runs 24 hours a day, 7 days a week` | Workload liên tục → Reserved Instances (1-3 year) tiết kiệm nhất. Spot không phù hợp (có thể bị terminate). |
| `database storage continues to grow` | Cần storage auto-scaling → Aurora (tự động scale storage từ 10 GB lên 128 TB) tốt hơn RDS. |
| `most cost-effectively` | Reserved Instances cho 24/7 + Aurora cho growing storage. |
| `Aurora Reserved Instances` | Giảm giá cho Aurora instance, storage tự scale. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most cost-effective
- **Constraints:** 24/7 workload, growing database storage, migration

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- EC2 Reserved Instances: tiết kiệm đến 72% so với On-Demand cho workload 24/7.
- Aurora Reserved Instances: Aurora tự động scale storage, Reserved giảm giá cho compute (instance) cost. Aurora phù hợp cho database có storage growing.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Spot Instances không phù hợp cho workload 24/7 (có thể bị reclaim khi AWS cần capacity).
- S3 không phải database storage (không support SQL, transactions).

**❌ Đáp án B:**
- RDS On-Demand instances đắt hơn Reserved cho 24/7 workload. RDS storage không tự động scale (cần manual resize).

**❌ Đáp án D:**
- EC2 On-Demand đắt hơn Reserved cho 24/7 workload.
- RDS Reserved tốt hơn On-Demand nhưng vẫn kém Aurora về storage auto-scaling.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"24/7 workload → Reserved (not Spot/On-Demand). Growing storage → Aurora (auto-scale storage)."*
