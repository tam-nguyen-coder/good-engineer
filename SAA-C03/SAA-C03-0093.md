# Question #93 - Topic 1

A company runs an on-premises application that is powered by a MySQL database. The company is migrating the application to AWS to increase the application's elasticity and availability. The current architecture shows heavy read activity on the database during times of normal operation. Every 4 hours, the company's development team pulls a full export of the production database to populate a database in the staging environment. During this period, users experience unacceptable application latency. The development team is unable to use the staging environment until the procedure completes. A solutions architect must recommend replacement architecture that alleviates the application latency issue. The replacement architecture also must give the development team the ability to continue using the staging environment without delay. Which solution meets these requirements?

## Options

**A.** Use Amazon Aurora MySQL with Multi-AZ Aurora Replicas for production. Populate the staging database by implementing a backup and restore process that uses the mysqldump utility.

**B.** Use Amazon Aurora MySQL with Multi-AZ Aurora Replicas for production. Use database cloning to create the staging database on-demand.

**C.** Use Amazon RDS for MySQL with a Multi-AZ deployment and read replicas for production. Use the standby instance for the staging database.

**D.** Use Amazon RDS for MySQL with a Multi-AZ deployment and read replicas for production. Populate the staging database by implementing a backup and restore process that uses the mysqldump utility.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** MySQL on-prem migration to AWS. Heavy read. Full export to staging every 4 hours causes latency + staging unavailable.
- **Existing Resources:** MySQL database, staging environment.
- **Current Issue/Goal:** Fix latency during export, staging available immediately.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `full export of the production database` | mysqldump gây performance impact |
| `heavy read activity` | Read replicas for read scaling |
| `database cloning` | **Aurora cloning** — instant, no performance impact |
| `staging environment without delay` | Clone tạo staging nhanh, không block |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Performance + Database
- **Constraints:** Không latency khi export, staging available ngay

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- **Aurora MySQL** — hiệu năng cao, có **Aurora Replicas** cho read scaling.
- **Aurora database cloning** — tạo staging database từ production snapshot **siêu nhanh** (copy-on-write), không ảnh hưởng performance production.
- Staging available ngay lập tức.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- mysqldump vẫn gây performance impact trên production.

**❌ Đáp án C:**
- RDS MySQL **standby instance không serve reads** (unlike Aurora).
- Không thể dùng standby cho staging.

**❌ Đáp án D:**
- mysqldump vẫn gây performance impact.
- Cần backup/restore mất thời gian.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Aurora cloning = instant copy, no performance impact. mysqldump = slow, impacts production. Standby RDS ≠ readable"*
