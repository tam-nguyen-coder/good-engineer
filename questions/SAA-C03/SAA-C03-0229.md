# Question #229 - Topic 1

A company manages its own Amazon EC2 instances that run MySQL databases. The company is manually managing replication and scaling as demand increases or decreases. The company needs a new solution that simplifies the process of adding or removing compute capacity to or from its database tier as needed. The solution also must offer improved performance, scaling, and durability with minimal effort from operations. Which solution meets these requirements?

## Options

**A.** Migrate the databases to Amazon Aurora Serverless for Aurora MySQL.

**B.** Migrate the databases to Amazon Aurora Serverless for Aurora PostgreSQL.

**C.** Combine the databases into one larger MySQL database. Run the larger database on larger EC2 instances.

**D.** Create an EC2 Auto Scaling group for the database tier. Migrate the existing databases to the new environment.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Self-managed MySQL on EC2, manual replication/scaling. Need simplified scaling, improved performance/durability.
- **Existing Resources:** MySQL on EC2.
- **Current Issue/Goal:** Managed, auto-scaling, MySQL-compatible.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `MySQL databases` | **Aurora Serverless for MySQL** (compatible) |
| `simplifies adding or removing compute capacity` | **Aurora Serverless** (auto-scale) |
| `minimal effort from operations` | Serverless |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Database / Migration
- **Constraints:** MySQL-compatible, auto-scaling, minimal ops

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- **Aurora Serverless for MySQL** — MySQL-compatible, tự động scale compute capacity dựa trên demand.
- Improved durability (6 replicas across 3 AZs).
- No server management → minimal operational effort.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Aurora Serverless for PostgreSQL — không MySQL-compatible.

**❌ Đáp án C:**
- Larger EC2 — vẫn self-managed, không auto-scale.

**❌ Đáp án D:**
- ASG for database — không appropriate cho stateful database.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Aurora Serverless MySQL = auto-scale + MySQL-compatible. PostgreSQL = not compatible. EC2 = self-managed"*
