# Question #338 - Topic 1

A solutions architect must create a disaster recovery (DR) plan for a high-volume software as a service (SaaS) platform. All data for the platform is stored in an Amazon Aurora MySQL DB cluster. The DR plan must replicate data to a secondary AWS Region. Which solution will meet these requirements MOST cost-effectively?

## Options

**A.** Use MySQL binary log replication to an Aurora cluster in the secondary Region. Provision one DB instance for the Aurora cluster in the secondary Region.

**B.** Set up an Aurora global database for the DB cluster. When setup is complete, remove the DB instance from the secondary Region.

**C.** Use AWS Database Migration Service (AWS DMS) to continuously replicate data to an Aurora cluster in the secondary Region. Remove the DB instance from the secondary Region.

**D.** Set up an Aurora global database for the DB cluster. Specify a minimum of one DB instance in the secondary Region.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** DR plan, Aurora MySQL, replicate data to secondary Region. Most cost-effective.
- **Existing Resources:** Aurora MySQL DB cluster (primary Region).
- **Current Issue/Goal:** Cross-Region DR, cheapest option.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `most cost-effectively` | Eliminate cost of DB instances in secondary Region khi không cần. |
| `Aurora global database` | Built-in cross-Region replication với 1s lag, separate storage và compute. |
| `without a DB instance` | Aurora global database cho phép secondary cluster chỉ có storage (0 instances) → chỉ trả storage cost. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most cost-effective
- **Constraints:** Cross-Region replication, Aurora MySQL, DR

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- Aurora global database: cross-Region replication built-in, không cần binlog replication.
- Sau khi setup global database, có thể remove DB instance in secondary Region → chỉ trả chi phí storage cho secondary Region (không trả compute instance cost).
- Khi cần DR failover, có thể provision instance nhanh chóng.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- MySQL binlog replication: phức tạp, operational overhead cao. Vẫn phải provision instance ở secondary Region.

**❌ Đáp án C:**
- DMS continuous replication: operational overhead cao hơn Aurora global database. Vẫn cần Aurora cluster có storage + compute.

**❌ Đáp án D:**
- Giống B nhưng có 1 DB instance ở secondary → cost cao hơn (trả compute).

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Aurora cross-Region DR cheapest → global database, remove secondary instance (chỉ pay storage)."*
