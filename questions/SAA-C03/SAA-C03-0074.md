# Question #74 - Topic 1

A solutions architect is designing a two-tier web application. The application consists of a public-facing web tier hosted on Amazon EC2 in public subnets. The database tier consists of Microsoft SQL Server running on Amazon EC2 in a private subnet. Security is a high priority for the company. How should security groups be configured in this situation? (Choose two.)

## Options

**A.** Configure the security group for the web tier to allow inbound traffic on port 443 from 0.0.0.0/0.

**B.** Configure the security group for the web tier to allow outbound traffic on port 443 from 0.0.0.0/0.

**C.** Configure the security group for the database tier to allow inbound traffic on port 1433 from the security group for the web tier.

**D.** Configure the security group for the database tier to allow outbound traffic on ports 443 and 1433 to the security group for the web tier.

**E.** Configure the security group for the database tier to allow inbound traffic on ports 443 and 1433 from the security group for the web tier.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Two-tier app: web tier (public subnet) + SQL Server DB tier (private subnet).
- **Existing Resources:** Web EC2 (public), SQL Server EC2 (private).
- **Current Issue/Goal:** Security group configuration for high security.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `Microsoft SQL Server` | Port **1433** (SQL Server default) |
| `public-facing web tier` | Allow HTTPS port 443 từ internet |
| `security group for the database tier` | Allow inbound từ web tier SG (not CIDR) |
| `security is a high priority` | Dùng security group referencing (least privilege) |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Network security
- **Constraints:** Chọn 2 đáp án

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A và C**

**Giải thích:**
- **A: Web SG inbound port 443 từ 0.0.0.0/0** — public web tier cần accept HTTPS từ internet.
- **C: DB SG inbound port 1433 từ Web SG** — SQL Server port 1433, allow chỉ từ web tier (security group referencing), không expose database ra ngoài.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Outbound rule không cần thiết cho security vì security groups là stateful — response traffic tự động được allow.

**❌ Đáp án D:**
- DB tier không cần outbound đến web tier (stateful).
- Port 443 không phải SQL Server.

**❌ Đáp án E:**
- Port 443 không phải SQL Server (SQL Server dùng 1433).
- Inbound từ web SG đúng, nhưng sai port.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Web: inbound 443 from internet. SQL Server: inbound 1433 from web SG. Security groups = stateful"*
