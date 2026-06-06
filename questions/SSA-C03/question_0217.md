# Question #217 - Topic 1

A company runs a global web application on Amazon EC2 instances behind an Application Load Balancer. The application stores data in Amazon Aurora. The company needs to create a disaster recovery solution and can tolerate up to 30 minutes of downtime and potential data loss. The solution does not need to handle the load when the primary infrastructure is healthy. What should a solutions architect do to meet these requirements?

## Options

**A.** Deploy the application with the required infrastructure elements in place. Use Amazon Route 53 to configure active-passive failover. Create an Aurora Replica in a second AWS Region.

**B.** Host a scaled-down deployment of the application in a second AWS Region. Use Amazon Route 53 to configure active-active failover. Create an Aurora Replica in the second Region.

**C.** Replicate the primary infrastructure in a second AWS Region. Use Amazon Route 53 to configure active-active failover. Create an Aurora database that is restored from the latest snapshot.

**D.** Back up data with AWS Backup. Use the backup to create the required infrastructure in a second AWS Region. Use Amazon Route 53 to configure active-passive failover. Create an Aurora second primary instance in the second Region.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Global web app on EC2+ALB+Aurora. Need DR, tolerate 30 min downtime + data loss. DR doesn't handle load when primary is healthy.
- **Existing Resources:** Primary Region infrastructure.
- **Current Issue/Goal:** Pilot light / warm standby DR.

## 2. KEYWORDS QUAN TRỌNG
| Quote | Ý nghĩa / Gợi ý |
|--------|-----------------|
| `tolerate up to 30 minutes of downtime and potential data loss` | **Active-passive** failover, cross-Region Aurora Replica |
| `does not need to handle the load when primary is healthy` | **Pilot light** — scaled-down infra |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Disaster Recovery
- **Constraints:** 30 min RTO, some data loss OK, passive DR

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- **Active-passive** — DR không serve traffic khi primary healthy.
- **Aurora Replica in second Region** — cross-Region replica, promote khi failover.
- Deploy infrastructure in DR Region, Route 53 active-passive failover.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Active-active — DR sẽ serve traffic, không phù hợp yêu cầu.

**❌ Đáp án C:**
- Active-active + snapshot restore — không cần replicate full infra, snapshot không real-time.

**❌ Đáp án D:**
- AWS Backup + snapshot restore — chậm hơn Aurora Replica, RTO có thể > 30 phút.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Aurora cross-Region replica + active-passive = pilot light DR. Snapshot = slower RTO"*
