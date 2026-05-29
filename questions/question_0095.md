# Question #95 - Topic 1

An application allows users at a company's headquarters to access product data. The product data is stored in an Amazon RDS MySQL DB instance. The operations team has isolated an application performance slowdown and wants to separate read traffic from write traffic. A solutions architect needs to optimize the application's performance quickly. What should the solutions architect recommend?

## Options

**A.** Change the existing database to a Multi-AZ deployment. Serve the read requests from the primary Availability Zone.

**B.** Change the existing database to a Multi-AZ deployment. Serve the read requests from the secondary Availability Zone.

**C.** Create read replicas for the database. Configure the read replicas with half of the compute and storage resources as the source database.

**D.** Create read replicas for the database. Configure the read replicas with the same compute and storage resources as the source database.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** RDS MySQL, cần separate read traffic from write traffic để improve performance.
- **Existing Resources:** RDS MySQL DB instance.
- **Current Issue/Goal:** Tách read/write, optimize performance quickly.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `separate read traffic from write traffic` | Cần **read replicas** |
| `optimize the application's performance quickly` | Giải pháp nhanh, đơn giản |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Performance optimization
- **Constraints:** Tách read/write, nhanh

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- **Read replicas** — tách read queries khỏi primary DB instance.
- **Cùng compute và storage resources** — để read replica có đủ khả năng xử lý read traffic.
- Nếu replica nhỏ hơn (½ resources), nó có thể không theo kịp read load hoặc replication lag.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Multi-AZ là cho HA (failover), không tách read traffic.

**❌ Đáp án B:**
- Multi-AZ **standby instance không serve reads** cho RDS MySQL (chỉ Aurora mới làm được).

**❌ Đáp án C:**
- Replica với ½ resources — có thể không đủ capacity, gây replication lag hoặc performance issue.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Read replica = tách read traffic. Multi-AZ standby ≠ readable (RDS MySQL). Replica nên cùng size"*
