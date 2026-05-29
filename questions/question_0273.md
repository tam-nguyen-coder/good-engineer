# Question #273 - Topic 1

A rapidly growing ecommerce company is running its workloads in a single AWS Region. A solutions architect must create a disaster recovery (DR) strategy that includes a different AWS Region. The company wants its database to be up to date in the DR Region with the least possible latency. The remaining infrastructure in the DR Region needs to run at reduced capacity and must be able to scale up if necessary. Which solution will meet these requirements with the LOWEST recovery time objective (RTO)?

## Options

**A.** Use an Amazon Aurora global database with a pilot light deployment.

**B.** Use an Amazon Aurora global database with a warm standby deployment.

**C.** Use an Amazon RDS Multi-AZ DB instance with a pilot light deployment.

**D.** Use an Amazon RDS Multi-AZ DB instance with a warm standby deployment.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Single Region → add DR Region. DB up-to-date with least latency. DR infra at reduced capacity, can scale up.
- **Existing Resources:** Single Region workload.
- **Current Issue/Goal:** Cross-Region DR, lowest RTO.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `database up to date... least possible latency` | **Aurora Global Database** (< 1 sec replication) |
| `reduced capacity... able to scale up` | **Warm standby** |
| `lowest recovery time objective (RTO)` | Warm standby > Pilot light |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Disaster Recovery
- **Constraints:** Cross-Region, low latency, lowest RTO

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- **Aurora Global Database** — cross-Region replication với latency < 1 giây.
- **Warm standby** — DR infrastructure chạy ở reduced capacity, có thể scale up → lowest RTO.
- Pilot light có RTO cao hơn (cần provision resources).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Pilot light — RTO cao hơn warm standby.

**❌ Đáp án C:**
- RDS Multi-AZ — chỉ trong 1 Region, không cross-Region.

**❌ Đáp án D:**
- RDS Multi-AZ — không cross-Region.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Aurora Global Database + warm standby = lowest RTO cross-Region. Pilot light = higher RTO"*
