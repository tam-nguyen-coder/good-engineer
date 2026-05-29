# Question #431 - Topic 1

A company has developed a new video game as a web application. The application is in a three-tier architecture in a VPC with Amazon RDS for MySQL in the database layer. Several players will compete concurrently online. The game's developers want to display a top-10 scoreboard in near- real time and offer the ability to stop and restore the game while preserving the current scores. What should a solutions architect do to meet these requirements?

## Options

**A.** Set up an Amazon ElastiCache for Memcached cluster to cache the scores for the web application to display.

**B.** Set up an Amazon ElastiCache for Redis cluster to compute and cache the scores for the web application to display.

**C.** Place an Amazon CloudFront distribution in front of the web application to cache the scoreboard in a section of the application.

**D.** Create a read replica on Amazon RDS for MySQL to run queries to compute the scoreboard and serve the read traffic to the web application.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Online game, concurrent players. Need top-10 scoreboard near-real time + stop/restore game preserving scores.
- **Existing Resources:** Three-tier VPC, RDS for MySQL.
- **Current Issue/Goal:** Real-time leaderboard + data persistence across stop/restore.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `top-10 scoreboard` | Redis sorted sets (ZADD, ZRANGE) for leaderboard. |
| `near-real time` | In-memory (Redis). |
| `stop and restore game preserving scores` | Redis persistence (RDB/AOF). |
| `Memcached` | Caching only, no persistence, no data structures. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Performance / Real-time data
- **Constraints:** Real-time leaderboard, persistence across stop/restore

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- Redis: in-memory data store, sorted sets cho top-10 leaderboard (O(log N) operations).
- Persistence (RDB/AOF): scores retained khi stop/restore game.
- Memcached: pure cache, không có sorted sets, không persistence.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Memcached: không hỗ trợ sorted sets (không compute top-10), không persistence.

**❌ Đáp án C:**
- CloudFront: CDN cache, không compute real-time scoreboard.

**❌ Đáp án D:**
- RDS read replica: slower than in-memory, không real-time.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Real-time leaderboard = Redis sorted sets. Memcached = cache only, no compute/persistence."*