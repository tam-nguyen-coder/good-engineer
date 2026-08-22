# Question #191 - Topic 1

A company has an ordering application that stores customer information in Amazon RDS for MySQL. During regular business hours, employees run one-time queries for reporting purposes. Timeouts are occurring during order processing because the reporting queries are taking a long time to run. The company needs to eliminate the timeouts without preventing employees from performing queries. What should a solutions architect do to meet these requirements?

## Options

**A.** Create a read replica. Move reporting queries to the read replica.

**B.** Create a read replica. Distribute the ordering application to the primary DB instance and the read replica.

**C.** Migrate the ordering application to Amazon DynamoDB with on-demand capacity.

**D.** Schedule the reporting queries for non-peak hours.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Ordering app on RDS MySQL. Reporting queries during work hours cause timeouts. Need to stop timeouts without blocking queries.
- **Existing Resources:** RDS MySQL, ordering app.
- **Current Issue/Goal:** Separate reporting traffic from OLTP traffic.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `one-time queries for reporting` | Heavy read workload |
| `timeouts` | Reporting queries interfere with OLTP |
| `without preventing employees from performing queries` | **Read replica** for reporting |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Database / Performance
- **Constraints:** Keep both apps running, no timeouts

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- **Read replica** — offload reporting queries, không ảnh hưởng primary DB.
- Read replica có endpoint riêng → move reporting queries to read replica.
- Ordering app (OLTP) vẫn chạy trên primary.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Distributing ordering app to read replica — ordering is write-heavy, read replica không accept writes.

**❌ Đáp án C:**
- Migrate to DynamoDB — major change, không cần thiết.

**❌ Đáp án D:**
- Schedule queries non-peak hours — prevents employees from querying during work hours.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Read replica = offload reporting. Primary = OLTP. Schedule queries = prevents access"*
