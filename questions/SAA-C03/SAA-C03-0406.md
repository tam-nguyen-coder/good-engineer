# Question #406 - Topic 1

A solutions architect is designing a two-tiered architecture that includes a public subnet and a database subnet. The web servers in the public subnet must be open to the internet on port 443. The Amazon RDS for MySQL DB instance in the database subnet must be accessible only to the web servers on port 3306. Which combination of steps should the solutions architect take to meet these requirements? (Choose two.)

## Options

**A.** Create a network ACL for the public subnet. Add a rule to deny outbound traffic to 0.0.0.0/0 on port 3306.

**B.** Create a security group for the DB instance. Add a rule to allow traffic from the public subnet CIDR block on port 3306.

**C.** Create a security group for the web servers in the public subnet. Add a rule to allow traffic from 0.0.0.0/0 on port 443.

**D.** Create a security group for the DB instance. Add a rule to allow traffic from the web servers' security group on port 3306.

**E.** Create a security group for the DB instance. Add a rule to deny all traffic except traffic from the web servers' security group on port 3306.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Two-tier: public subnet (web) + database subnet (RDS MySQL). Web open internet 443. DB only accessible from web on 3306.
- **Existing Resources:** VPC, public subnet, database subnet.
- **Current Issue/Goal:** Secure access with SGs, only web can reach DB.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `security group` | Stateful firewall. Allow rules only (default deny all). |
| `web servers' security group` | SG-to-SG rule: allow DB SG from web SG. |
| `Choose two` | 2 answers required. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Security / Networking - SG configuration
- **Constraints:** Web: 443 from internet. DB: 3306 from web only.

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C, D**

**Giải thích:**
- **C:** SG web servers: inbound rule allow 443 from 0.0.0.0/0 → internet traffic to web.
- **D:** SG DB: inbound rule allow 3306 from web servers' SG ID → chỉ web mới access được DB.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- NACL deny outbound 3306 không cần thiết (SG đã deny mặc định). NACL stateless → phải config cả inbound/outbound phức tạp.

**❌ Đáp án B:**
- Allow from public subnet CIDR on 3306: quá rộng, bất kỳ instance nào trong public subnet (kể cả instance khác) cũng access được DB.

**❌ Đáp án E:**
- Security groups: deny rules không được support (implicit deny all). Chỉ có allow rules.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"DB SG → reference web SG (not CIDR). SG = allow-only, no deny rules."*