# Question #464 - Topic 1

A company hosts an online shopping application that stores all orders in an Amazon RDS for PostgreSQL Single-AZ DB instance. Management wants to eliminate single points of failure and has asked a solutions architect to recommend an approach to minimize database downtime without requiring any changes to the application code. Which solution meets these requirements?

## Options

**A.** Convert the existing database instance to a Multi-AZ deployment by modifying the database instance and specifying the Multi-AZ option.

**B.** Create a new RDS Multi-AZ deployment. Take a snapshot of the current RDS instance and restore the new Multi-AZ deployment with the snapshot.

**C.** Create a read-only replica of the PostgreSQL database in another Availability Zone. Use Amazon Route 53 weighted record sets to distribute requests across the databases.

**D.** Place the RDS for PostgreSQL database in an Amazon EC2 Auto Scaling group with a minimum group size of two. Use Amazon Route 53 weighted record sets to distribute requests across instances.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Online shopping app, RDS PostgreSQL Single-AZ. Management muốn eliminate SPOF.
- **Existing Resources:** RDS PostgreSQL Single-AZ instance.
- **Current Issue/Goal:** Minimize downtime, no application code changes.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `Single-AZ` | Hiện tại chỉ có 1 AZ → SPOF. |
| `eliminate single points of failure` | Cần Multi-AZ để failover tự động. |
| `without requiring any changes to the application code` | Multi-AZ dùng cùng endpoint, app không cần thay đổi. |
| `minimize database downtime` | Multi-AZ failover tự động nhanh chóng. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Minimize downtime, no code changes
- **Constraints:** No app code changes, eliminate SPOF

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- Modify existing RDS instance to Multi-AZ: zero-downtime modification (AWS tự tạo standby, replicate).
- Multi-AZ: synchronous replication sang standby trong AZ khác.
- Khi failover, AWS tự động chuyển đổi DNS → app không cần thay đổi code.
- Endpoint giữ nguyên.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Tạo mới + snapshot restore: gây downtime (phải stop app để chụp snapshot), phức tạp hơn so với modify trực tiếp.

**❌ Đáp án C:**
- Read replica không hỗ trợ writes. Nếu primary fails, read replica không tự động promote thành primary (cần manual).
- Route 53 weighted: app phải thay đổi code để handle multiple endpoints.
- Không phải là giải pháp HA cho writes.

**❌ Đáp án D:**
- RDS không chạy trong Auto Scaling group. Auto Scaling group dành cho EC2, không phải RDS.
- Route 53 weighted với RDS instances → không đúng, RDS không hoạt động như cluster kiểu đó.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Single-AZ → Multi-AZ: modify instance, không cần tạo mới, app không cần thay đổi code."*
