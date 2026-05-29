# Question #466 - Topic 1

A company designed a stateless two-tier application that uses Amazon EC2 in a single Availability Zone and an Amazon RDS Multi-AZ DB instance. New company management wants to ensure the application is highly available. What should a solutions architect do to meet this requirement?

## Options

**A.** Configure the application to use Multi-AZ EC2 Auto Scaling and create an Application Load Balancer

**B.** Configure the application to take snapshots of the EC2 instances and send them to a different AWS Region

**C.** Configure the application to use Amazon Route 53 latency-based routing to feed requests to the application

**D.** Configure Amazon Route 53 rules to handle incoming requests and create a Multi-AZ Application Load Balancer

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Stateless two-tier app: EC2 single AZ, RDS Multi-AZ (đã HA cho database).
- **Existing Resources:** EC2 single AZ, RDS Multi-AZ.
- **Current Issue/Goal:** Làm cho application (EC2 tier) highly available.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `stateless` | EC2 instances không giữ state → dễ scale và HA. |
| `single Availability Zone` | Hiện tại EC2 chỉ ở 1 AZ → SPOF. |
| `RDS Multi-AZ` | Database đã HA, chỉ cần fix EC2 tier. |
| `highly available` | EC2 cần chạy ở nhiều AZ + ALB distribute traffic. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** High availability
- **Constraints:** RDS đã Multi-AZ, cần HA cho EC2 tier

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- Multi-AZ Auto Scaling: EC2 instances chạy ở ít nhất 2 AZ → nếu 1 AZ fail, instances AZ khác vẫn hoạt động.
- ALB: phân phối traffic giữa các instances ở nhiều AZ. ALB tự động health check và loại bỏ instances unhealthy.
- Stateless → không cần concern về session state.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Snapshots + cross-region: không làm HA, chỉ là backup/disaster recovery. Không giải quyết vấn đề single AZ failure.

**❌ Đáp án C:**
- Route 53 latency-based routing: cần instances ở nhiều region để có ý nghĩa. Trong cùng region, latency giữa các AZ không đáng kể. Quan trọng hơn, không tự động failover khi instance fail.

**❌ Đáp án D:**
- "Create a Multi-AZ Application Load Balancer" → ALB đã là multi-AZ tự nhiên (tự động phân phối traffic qua các subnets). Tuy nhiên, thiếu Auto Scaling group để đảm bảo có EC2 instances ở nhiều AZ khi 1 AZ fail.
- Route 53 rules → không rõ ràng, có thể là routing policies.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"EC2 HA = Multi-AZ ASG + ALB. Database đã Multi-AZ rồi thì khỏi đụng."*
