# Question #144 - Topic 1

A company recently started using Amazon Aurora as the data store for its global ecommerce application. When large reports are run, developers report that the ecommerce application is performing poorly. After reviewing metrics in Amazon CloudWatch, a solutions architect finds that the ReadIOPS and CPUUtilizalion metrics are spiking when monthly reports run. What is the MOST cost-effective solution?

## Options

**A.** Migrate the monthly reporting to Amazon Redshift.

**B.** Migrate the monthly reporting to an Aurora Replica.

**C.** Migrate the Aurora database to a larger instance class.

**D.** Increase the Provisioned IOPS on the Aurora instance.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Aurora cho ecommerce, monthly reports cause ReadIOPS + CPU spikes → app slow.
- **Existing Resources:** Aurora DB.
- **Current Issue/Goal:** Offload reporting read traffic, cost-effective.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `ReadIOPS and CPUUtilization spiking` | Read-heavy workload → **Aurora Replica** |
| `monthly reports` | Read-only, có thể tách riêng |
| `most cost-effective` | Thêm Aurora Replica (rẻ hơn upgrade instance) |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Performance optimization + Cost
- **Constraints:** Offload read traffic, cost-effective

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- **Aurora Replica** — tách read traffic (reports) khỏi primary instance.
- Aurora hỗ trợ tới 15 read replicas, replication lag thấp.
- Rẻ hơn upgrade instance class hoặc migrate sang Redshift.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Redshift — quá đắt và nặng nề cho monthly reports. Overkill.

**❌ Đáp án C:**
- Larger instance class — giải quyết triệu chứng nhưng tốn kém hơn Aurora Replica.

**❌ Đáp án D:**
- Tăng Provisioned IOPS — tốn kém, không giải quyết CPU spike.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Aurora Replica = offload read traffic. Rẻ hơn upgrade. Redshift = overkill for monthly reports"*
