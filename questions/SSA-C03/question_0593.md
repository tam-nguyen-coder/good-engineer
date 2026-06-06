# Question #593 - Topic 1

A solutions architect is designing a highly available Amazon ElastiCache for Redis based solution. The solutions architect needs to ensure that failures do not result in performance degradation or loss of data locally and within an AWS Region. The solution needs to provide high availability at the node level and at the Region level. Which solution will meet these requirements?

## Options

**A.** Use Multi-AZ Redis replication groups with shards that contain multiple nodes.

**B.** Use Redis shards that contain multiple nodes with Redis append only files (AOF) turned on.

**C.** Use a Multi-AZ Redis cluster with more than one read replica in the replication group.

**D.** Use Redis shards that contain multiple nodes with Auto Scaling turned on.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** ElastiCache for Redis HA solution, không mất data, không performance degradation, HA tại node level và Region level.
- **Existing Resources:** ElastiCache for Redis.
- **Current Issue/Goal:** HA + data durability within Region.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `node level` | Multi-AZ replication group: tự động failover nếu primary node fails. |
| `Region level` | Cross-AZ deployment (trong cùng Region). |
| `shards that contain multiple nodes` | Redis Cluster mode: sharding để scale writes, replication trong mỗi shard. |
| `no loss of data` | Redis AOF persistence + replication. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Highly available + data durability
- **Constraints:** Node level + Region level HA, no data loss

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- Multi-AZ Redis replication groups: tự động failover khi primary node fails → node level HA.
- Shards với multiple nodes (replication group per shard): phân tán dữ liệu, mỗi shard có primary + replica → Region level HA và no data loss.
- Cung cấp cả HA và durability.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- AOF chỉ đảm bảo durability (persistence), không HA. Nếu node fails, vẫn có downtime.

**❌ Đáp án C:**
- Multi-AZ Redis cluster with read replicas: có HA nhưng "more than one read replica" không cần thiết; cần mô tả chính xác hơn. Tuy nhiên, option A (shards + multi-node) toàn diện hơn.

**❌ Đáp án D:**
- Auto Scaling chỉ scale số lượng nodes, không đảm bảo HA hay data durability.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Redis HA node + Region level → Multi-AZ + shards with replicas. AOF = persistence only, not HA."*
