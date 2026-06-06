# Question #268 - Topic 1

A gaming company has a web application that displays scores. The application runs on Amazon EC2 instances behind an Application Load Balancer. The application stores data in an Amazon RDS for MySQL database. Users are starting to experience long delays and interruptions that are caused by database read performance. The company wants to improve the user experience while minimizing changes to the application's architecture. What should a solutions architect do to meet these requirements?

## Options

**A.** Use Amazon ElastiCache in front of the database.

**B.** Use RDS Proxy between the application and the database.

**C.** Migrate the application from EC2 instances to AWS Lambda.

**D.** Migrate the database from Amazon RDS for MySQL to Amazon DynamoDB.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Gaming scores app, EC2 + ALB + RDS MySQL. DB read performance causing delays.
- **Existing Resources:** EC2, ALB, RDS MySQL.
- **Current Issue/Goal:** Improve read performance, minimize arch changes.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `database read performance` | Caching — **ElastiCache** |
| `minimizing changes to the application's architecture` | Cache-aside pattern, ít code changes |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Database / Caching
- **Constraints:** Read performance, minimal changes

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- **ElastiCache** — in-memory cache, giảm read load trên RDS.
- Cache frequently accessed data (scores) → giảm latency.
- Minimal application changes (thêm cache read/write logic).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- RDS Proxy — connection pooling, không cải thiện read performance.

**❌ Đáp án C:**
- Migrate to Lambda — major architectural change.

**❌ Đáp án D:**
- Migrate to DynamoDB — major architectural change.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"ElastiCache = read performance (caching). RDS Proxy = connection pooling. Major migration = too much change"*
