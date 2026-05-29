# Question #90 - Topic 1

A company is using a SQL database to store movie data that is publicly accessible. The database runs on an Amazon RDS Single-AZ DB instance. A script runs queries at random intervals each day to record the number of new movies that have been added to the database. The script must report a final total during business hours. The company's development team notices that the database performance is inadequate for development tasks when the script is running. A solutions architect must recommend a solution to resolve this issue. Which solution will meet this requirement with the LEAST operational overhead?

## Options

**A.** Modify the DB instance to be a Multi-AZ deployment.

**B.** Create a read replica of the database. Configure the script to query only the read replica.

**C.** Instruct the development team to manually export the entries in the database at the end of each day.

**D.** Use Amazon ElastiCache to cache the common queries that the script runs against the database.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** RDS Single-AZ, script chạy query random intervals, gây chậm cho development tasks.
- **Existing Resources:** RDS MySQL Single-AZ.
- **Current Issue/Goal:** Tách read traffic (script) khỏi dev tasks, least overhead.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `read replica` | Offload read queries |
| `script runs queries` | Read-only workload |
| `database performance is inadequate for development tasks` | Cần tách read load |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Performance optimization
- **Constraints:** Least operational overhead

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- **Read replica** — tạo bản sao read-only của database.
- Script query read replica → không ảnh hưởng đến performance của primary DB cho development.
- Dễ dàng tạo, least operational overhead.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- **Multi-AZ** là cho high availability, không tách read traffic — standby không serve reads (trừ Aurora).

**❌ Đáp án C:**
- Manual export — không tự động, không giải quyết performance issue real-time.

**❌ Đáp án D:**
- **ElastiCache** — caching giúp nếu queries lặp lại, nhưng script chạy random intervals → cache hit ratio thấp. Operational overhead cao hơn read replica.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Read replica = offload read traffic. Multi-AZ = HA (standby không serve reads)"*
