# Question #378 - Topic 1

A company is developing a real-time multiplayer game that uses UDP for communications between the client and servers in an Auto Scaling group. Spikes in demand are anticipated during the day, so the game server platform must adapt accordingly. Developers want to store gamer scores and other non-relational data in a database solution that will scale without intervention. Which solution should a solutions architect recommend?

## Options

**A.** Use Amazon Route 53 for traffic distribution and Amazon Aurora Serverless for data storage.

**B.** Use a Network Load Balancer for traffic distribution and Amazon DynamoDB on-demand for data storage.

**C.** Use a Network Load Balancer for traffic distribution and Amazon Aurora Global Database for data storage.

**D.** Use an Application Load Balancer for traffic distribution and Amazon DynamoDB global tables for data storage.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Real-time multiplayer game, UDP, Auto Scaling, non-relational data, scale without intervention.
- **Existing Resources:** (none specified)
- **Current Issue/Goal:** UDP traffic distribution + non-relational auto-scaling database.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `UDP` | NLB hỗ trợ UDP. ALB = HTTP/HTTPS only. Route 53 = DNS, không phải traffic distribution. |
| `non-relational data` | DynamoDB (NoSQL). Aurora = relational (SQL). |
| `scale without intervention` | DynamoDB on-demand mode tự động scale không cần can thiệp. |
| `spikes in demand` | DynamoDB on-demand phù hợp cho unpredictable traffic. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Which solution to recommend
- **Constraints:** UDP, non-relational, auto-scaling database

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- NLB: supports UDP, phù hợp cho game server traffic distribution.
- DynamoDB on-demand: NoSQL (non-relational), tự động scale không cần can thiệp (good for spikes).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Route 53: DNS, không phải traffic distribution cho real-time UDP. Aurora Serverless: relational (SQL), không non-relational.

**❌ Đáp án C:**
- Aurora Global Database: relational (SQL), không non-relational. Cross-Region replication không cần thiết.

**❌ Đáp án D:**
- ALB: không support UDP. DynamoDB global tables: cross-Region replication, không cần thiết.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"UDP game + non-relational + auto-scale → NLB + DynamoDB on-demand. ALB = HTTP only. Aurora = SQL."*
