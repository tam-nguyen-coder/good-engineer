# Question #589 - Topic 1

A company runs a web application on Amazon EC2 instances in an Auto Scaling group behind an Application Load Balancer that has sticky sessions enabled. The web server currently hosts the user session state. The company wants to ensure high availability and avoid user session state loss in the event of a web server outage. Which solution will meet these requirements?

## Options

**A.** Use an Amazon ElastiCache for Memcached instance to store the session data. Update the application to use ElastiCache for Memcached to store the session state.

**B.** Use Amazon ElastiCache for Redis to store the session state. Update the application to use ElastiCache for Redis to store the session state.

**C.** Use an AWS Storage Gateway cached volume to store session data. Update the application to use AWS Storage Gateway cached volume to store the session state.

**D.** Use Amazon RDS to store the session state. Update the application to use Amazon RDS to store the session state.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Web app với sticky sessions (ALB), session state trên web server hiện tại. Muốn HA và avoid session loss khi web server outage.
- **Existing Resources:** EC2 ASG, ALB with sticky sessions.
- **Current Issue/Goal:** External session store, HA, no session loss.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `sticky sessions` | Session affinity → session state cần được lưu bên ngoài web server. |
| `avoid user session state loss` | Cần external session store có HA + persistence. |
| `ElastiCache for Redis` | Supports persistence, replication, HA. Dùng cho session state. |
| `ElastiCache for Memcached` | In-memory only, no persistence → mất data khi restart. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** High availability + avoid data loss
- **Constraints:** External session store, HA

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- ElastiCache for Redis hỗ trợ persistence (AOF snapshots) và replication → không mất session data khi fail.
- Multi-AZ replication group → HA.
- Được sử dụng rộng rãi làm session store cho web apps.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Memcached: không có persistence → mất session data khi instance restart/fail. Không đảm bảo "avoid session state loss".

**❌ Đáp án C:**
- Storage Gateway cached volume: dùng cho file storage, không phù hợp session store (latency cao, không tối ưu cho frequent read/write nhỏ).

**❌ Đáp án D:**
- RDS: có thể dùng lưu session nhưng overkill, latency cao hơn Redis. Không tối ưu cho session use case.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Session store → ElastiCache for Redis (persistence + HA). Memcached = no persistence → data loss."*
