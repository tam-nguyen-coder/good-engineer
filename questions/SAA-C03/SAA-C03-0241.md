# Question #241 - Topic 1

An online learning company is migrating to the AWS Cloud. The company maintains its student records in a PostgreSQL database. The company needs a solution in which its data is available and online across multiple AWS Regions at all times. Which solution will meet these requirements with the LEAST amount of operational overhead?

## Options

**A.** Migrate the PostgreSQL database to a PostgreSQL cluster on Amazon EC2 instances.

**B.** Migrate the PostgreSQL database to an Amazon RDS for PostgreSQL DB instance with the Multi-AZ feature turned on.

**C.** Migrate the PostgreSQL database to an Amazon RDS for PostgreSQL DB instance. Create a read replica in another Region.

**D.** Migrate the PostgreSQL database to an Amazon RDS for PostgreSQL DB instance. Set up DB snapshots to be copied to another Region.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** PostgreSQL student records. Need data available online across multiple Regions.
- **Existing Resources:** PostgreSQL database.
- **Current Issue/Goal:** Cross-Region availability.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `across multiple AWS Regions` | **Cross-Region read replica** |
| `available and online` | Read replica luôn online, có thể promoted lên primary |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Database / Disaster Recovery
- **Constraints:** Multi-Region, least overhead

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- **RDS PostgreSQL with cross-Region read replica** — dữ liệu available online ở cả 2 Regions.
- Read replica ở Region khác luôn sync, có thể promote lên primary nếu cần.
- Managed service → least operational overhead.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- PostgreSQL cluster on EC2 — self-managed, operational overhead cao.

**❌ Đáp án B:**
- Multi-AZ — chỉ trong 1 Region, không cross-Region.

**❌ Đáp án D:**
- Snapshots — không online, cần restore mới dùng được.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Cross-Region read replica = multi-Region online. Multi-AZ = single Region. Snapshots = not online"*
