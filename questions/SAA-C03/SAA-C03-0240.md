# Question #240 - Topic 1

A company previously migrated its data warehouse solution to AWS. The company also has an AWS Direct Connect connection. Corporate office users query the data warehouse using a visualization tool. The average size of a query returned by the data warehouse is 50 MB and each webpage sent by the visualization tool is approximately 500 KB. Result sets returned by the data warehouse are not cached. Which solution provides the LOWEST data transfer egress cost for the company?

## Options

**A.** Host the visualization tool on premises and query the data warehouse directly over the internet.

**B.** Host the visualization tool in the same AWS Region as the data warehouse. Access it over the internet.

**C.** Host the visualization tool on premises and query the data warehouse directly over a Direct Connect connection at a location in the same AWS Region.

**D.** Host the visualization tool in the same AWS Region as the data warehouse and access it over a Direct Connect connection at a location in the same Region.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Data warehouse on AWS. Visualization tool queries data (50MB responses) and generates webpages (500KB). Direct Connect available. Lowest egress cost.
- **Existing Resources:** Data warehouse, Direct Connect.
- **Current Issue/Goal:** Minimize data transfer costs.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `50 MB` query result | Large data — giữ trong AWS để tránh egress cost |
| `500 KB` webpage | Smaller data — xuất ra ngoài |
| `lowest data transfer egress cost` | Viz tool trong AWS Region (50MB free internal) |
| `Direct Connect` | Chi phí thấp hơn internet egress |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Cost optimization / Networking
- **Constraints:** Lowest egress cost

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- Viz tool trong **cùng Region** với data warehouse → 50MB query results là internal traffic (free).
- Corporate users access viz tool (500KB webpages) qua **Direct Connect** → egress cost thấp hơn internet.
- Không cần truyền 50MB query results qua Direct Connect.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Internet — egress cost cao nhất cho cả query results và webpages.

**❌ Đáp án B:**
- Trong Region + internet — viz tool trong Region (query free), nhưng users access qua internet (webpage egress cost cao).

**❌ Đáp án C:**
- On-prem viz tool + Direct Connect — 50MB query results phải truyền qua Direct Connect (costly).

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Keep big data in AWS (free internal). Send small data over Direct Connect (cheapest egress)"*
