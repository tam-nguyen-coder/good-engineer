# Question #392 - Topic 1

A company wants to deploy a new public web application on AWS. The application includes a web server tier that uses Amazon EC2 instances. The application also includes a database tier that uses an Amazon RDS for MySQL DB instance. The application must be secure and accessible for global customers that have dynamic IP addresses. How should a solutions architect configure the security groups to meet these requirements?

## Options

**A.** Configure the security group for the web servers to allow inbound traffic on port 443 from 0.0.0.0/0. Configure the security group for the DB instance to allow inbound traffic on port 3306 from the security group of the web servers.

**B.** Configure the security group for the web servers to allow inbound traffic on port 443 from the IP addresses of the customers. Configure the security group for the DB instance to allow inbound traffic on port 3306 from the security group of the web servers.

**C.** Configure the security group for the web servers to allow inbound traffic on port 443 from the IP addresses of the customers. Configure the security group for the DB instance to allow inbound traffic on port 3306 from the IP addresses of the customers.

**D.** Configure the security group for the web servers to allow inbound traffic on port 443 from 0.0.0.0/0. Configure the security group for the DB instance to allow inbound traffic on port 3306 from 0.0.0.0/0.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Public web app, EC2 web + RDS MySQL. Global customers with dynamic IPs. Must be secure.
- **Existing Resources:** (none specified)
- **Current Issue/Goal:** Security group configuration for public web + private database.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `dynamic IP addresses` | Không thể whitelist IP → phải allow từ 0.0.0.0/0 cho web tier. |
| `public web application` | Web servers must accept HTTPS from anywhere (0.0.0.0/0). |
| `security group chaining` | DB SG chỉ accept traffic từ web servers' SG (private, không expose ra internet). |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Secure security group configuration
- **Constraints:** Global customers, dynamic IPs, public web, private DB

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- Web SG: allow HTTPS (443) from 0.0.0.0/0 → public web app accessible globally.
- DB SG: allow MySQL (3306) only from web servers' SG (SG chaining) → không expose database ra internet.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Không thể whitelist IP của global customers với dynamic IPs.

**❌ Đáp án C:**
- DB SG allow from customer IPs → database exposed to internet (kém bảo mật). Không thể whitelist dynamic IPs.

**❌ Đáp án D:**
- DB SG allow from 0.0.0.0/0 → database exposed to internet, không an toàn.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Public web + dynamic IPs → web SG 0.0.0.0/0 (HTTPS). DB → only web SG (SG chaining)."*
