# Question #436 - Topic 1

A company moved its on-premises PostgreSQL database to an Amazon RDS for PostgreSQL DB instance. The company successfully launched a new product. The workload on the database has increased. The company wants to accommodate the larger workload without adding infrastructure. Which solution will meet these requirements MOST cost-effectively?

## Options

**A.** Buy reserved DB instances for the total workload. Make the Amazon RDS for PostgreSQL DB instance larger.

**B.** Make the Amazon RDS for PostgreSQL DB instance a Multi-AZ DB instance.

**C.** Buy reserved DB instances for the total workload. Add another Amazon RDS for PostgreSQL DB instance.

**D.** Make the Amazon RDS for PostgreSQL DB instance an on-demand DB instance.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** PostgreSQL migrated to RDS. Increased workload. Need to accommodate without adding infrastructure.
- **Existing Resources:** RDS for PostgreSQL DB instance.
- **Current Issue/Goal:** Handle larger workload, most cost-effective.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `without adding infrastructure` | Scale up (larger instance), không scale out (add instances). |
| `cost-effectively` | Reserved Instances (giảm giá so với On-Demand). |
| `larger workload` | More CPU/RAM → larger instance size. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Cost optimization / Scaling
- **Constraints:** No new infrastructure, accommodate larger workload

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- Reserved Instances: commit 1-3 năm → giảm giá đáng kể so với On-Demand.
- Scale up: increase DB instance class (e.g., db.r5.large → db.r5.xlarge) → more CPU/RAM.
- Không thêm infrastructure (vẫn 1 DB instance).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Multi-AZ: high availability, không tăng compute capacity (standby không dùng cho workload).

**❌ Đáp án C:**
- Add another instance: thêm infrastructure → không đáp ứng "without adding infrastructure".

**❌ Đáp án D:**
- On-demand: không giảm giá, đắt hơn Reserved cho workload ổn định.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Without adding infra → scale up (bigger instance) + Reserved (cost saving)."*