# Question #596 - Topic 1

An ecommerce application uses a PostgreSQL database that runs on an Amazon EC2 instance. During a monthly sales event, database usage increases and causes database connection issues for the application. The traffic is unpredictable for subsequent monthly sales events, which impacts the sales forecast. The company needs to maintain performance when there is an unpredictable increase in traffic. Which solution resolves this issue in the MOST cost-effective way?

## Options

**A.** Migrate the PostgreSQL database to Amazon Aurora Serverless v2.

**B.** Enable auto scaling for the PostgreSQL database on the EC2 instance to accommodate increased usage.

**C.** Migrate the PostgreSQL database to Amazon RDS for PostgreSQL with a larger instance type.

**D.** Migrate the PostgreSQL database to Amazon Redshift to accommodate increased usage.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** PostgreSQL on EC2, monthly sales event causes connection issues, unpredictable traffic.
- **Existing Resources:** PostgreSQL on EC2.
- **Current Issue/Goal:** Handle unpredictable traffic spikes, cost-effective.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `unpredictable` | Aurora Serverless v2 auto scales dựa trên actual workload. |
| `database connection issues` | Cần database có thể scale để handle nhiều connections. |
| `Aurora Serverless v2` | Auto scale ACUs, pay per second, handle unpredictable workloads. |
| `MOST cost-effective` | Serverless: chỉ trả cho resources đã dùng. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most cost-effective
- **Constraints:** PostgreSQL, unpredictable traffic spikes

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- Aurora Serverless v2 tự động scale capacity (ACUs) dựa trên workload → không cần provision for peak.
- MySQL-compatible, PostgreSQL-compatible.
- Cost-effective: trả theo dung lượng sử dụng, không tốn cho idle capacity ngoài giờ cao điểm.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- EC2 auto scaling cho PostgreSQL: phức tạp (cần clustering, replication setup). Không phải managed solution.

**❌ Đáp án C:**
- RDS PostgreSQL larger instance: provision cho peak → tốn cost 24/7. Không cost-effective cho occasional spikes.

**❌ Đáp án D:**
- Redshift là data warehouse (OLAP), không phải OLTP database cho ecommerce app.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Unpredictable spikes + cost-effective → Aurora Serverless v2 (auto scale, pay per use). Provisioned = wasted idle capacity."*
