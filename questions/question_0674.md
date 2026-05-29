# Question #674 - Topic 1

A company runs a web application on Amazon EC2 instances in an Auto Scaling group. The application uses a database that runs on an Amazon RDS for PostgreSQL DB instance. The application performs slowly when traffic increases. The database experiences a heavy read load during periods of high traffic. Which actions should a solutions architect take to resolve these performance issues? (Choose two.)

## Options

**A.** Turn on auto scaling for the DB instance.

**B.** Create a read replica for the DB instance. Configure the application to send read traffic to the read replica.

**C.** Convert the DB instance to a Multi-AZ DB instance deployment. Configure the application to send read traffic to the standby DB instance.

**D.** Create an Amazon ElastiCache cluster. Configure the application to cache query results in the ElastiCache cluster.

**E.** Configure the Auto Scaling group subnets to ensure that the EC2 instances are provisioned in the same Availability Zone as the DB instance.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Web app on ASG, RDS PostgreSQL. Slow when traffic increases, heavy read load on database.
- **Existing Resources:** ASG (EC2), RDS PostgreSQL.
- **Current Issue/Goal:** Reduce read load on primary database.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `heavy read load` | Need to offload read traffic from primary DB. |
| `read replica` | Offload read queries to replica. |
| `Amazon ElastiCache` | Cache query results → giảm read load dramatically. |
| `Multi-AZ standby` | Standby không serving read traffic (chỉ dùng cho failover). |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Resolve performance issues (choose two)
- **Constraints:** Heavy read load on RDS PostgreSQL

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B và D**

**Giải thích:**
- **B:** Read replica offload read queries từ primary → giảm load.
- **D:** ElastiCache caching query results → repeated queries không cần đọc DB, giảm read load significantly.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- RDS auto scaling chỉ scale storage, không scale compute cho read load.

**❌ Đáp án C:**
- Multi-AZ standby không serve read traffic (chỉ failover). Không giảm read load.

**❌ Đáp án E:**
- EC2 và DB cùng AZ không giúp giảm read load, chỉ giảm network latency.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Heavy read load → Read Replica (offload queries) + ElastiCache (cache results). Standby ≠ read replica."*
