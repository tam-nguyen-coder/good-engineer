# Question #389 - Topic 1

A company has a large dataset for its online advertising business stored in an Amazon RDS for MySQL DB instance in a single Availability Zone. The company wants business reporting queries to run without impacting the write operations to the production DB instance. Which solution meets these requirements?

## Options

**A.** Deploy RDS read replicas to process the business reporting queries.

**B.** Scale out the DB instance horizontally by placing it behind an Elastic Load Balancer.

**C.** Scale up the DB instance to a larger instance type to handle write operations and queries.

**D.** Deploy the DB instance in multiple Availability Zones to process the business reporting queries.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** RDS MySQL Single-AZ. Business reporting queries must not impact write operations.
- **Existing Resources:** RDS MySQL Single-AZ.
- **Current Issue/Goal:** Offload reporting queries without impacting writes.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `without impacting the write operations` | Read replica offload read traffic. |
| `RDS read replicas` | Read-only copies, xử lý reporting queries, không ảnh hưởng primary. |
| `business reporting queries` | Read-heavy workload → read replicas. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Which solution meets requirements
- **Constraints:** No write impact, reporting queries

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- RDS read replicas: async replication từ primary, có thể serve read queries (reporting) mà không ảnh hưởng primary writes.
- Reporting queries chạy trên read replicas → primary chỉ tập trung vào production writes.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- RDS không thể "đứng sau ELB" (RDS không phải HTTP target). DB không scale horizontally với ELB.

**❌ Đáp án C:**
- Scale up: tăng instance size, nhưng reporting queries vẫn chạy trên primary → có thể ảnh hưởng writes.

**❌ Đáp án D:**
- Multi-AZ: HA/failover. Multi-AZ standby không thể serve read queries.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Reporting queries không ảnh hưởng writes → Read Replicas. Multi-AZ standby = không đọc được. Scale up = vẫn chạy chung."*
