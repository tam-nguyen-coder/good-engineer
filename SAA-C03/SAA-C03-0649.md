# Question #649 - Topic 1

An ecommerce company runs a PostgreSQL database on premises. The database stores data by using high IOPS Amazon Elastic Block Store (Amazon EBS) block storage. The daily peak I/O transactions per second do not exceed 15,000 IOPS. The company wants to migrate the database to Amazon RDS for PostgreSQL and provision disk IOPS performance independent of disk storage capacity. Which solution will meet these requirements MOST cost-effectively?

## Options

**A.** Configure the General Purpose SSD (gp2) EBS volume storage type and provision 15,000 IOPS.

**B.** Configure the Provisioned IOPS SSD (io1) EBS volume storage type and provision 15,000 IOPS.

**C.** Configure the General Purpose SSD (gp3) EBS volume storage type and provision 15,000 IOPS.

**D.** Configure the EBS magnetic volume type to achieve maximum IOPS.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Migrate on-prem PostgreSQL to RDS for PostgreSQL, peak 15,000 IOPS, need IOPS independent of storage capacity.
- **Existing Resources:** On-prem PostgreSQL database.
- **Current Issue/Goal:** IOPS independent of storage size, cost-effective.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `IOPS performance independent of disk storage capacity` | gp3 và io1/io2 hỗ trợ IOPS độc lập với dung lượng. gp2 IOPS phụ thuộc vào dung lượng. |
| `15,000 IOPS` | gp3 hỗ trợ 3,000 IOPS baseline, có thể provision thêm lên đến 16,000 IOPS. |
| `most cost-effectively` | gp3 rẻ hơn io1. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most cost-effective
- **Constraints:** IOPS independent of storage, max 15,000 IOPS

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- gp3 hỗ trợ IOPS độc lập với storage capacity (3,000 baseline + provision thêm).
- 15,000 IOPS có thể provision trên gp3 với chi phí thấp hơn io1/io2.
- gp3 là thế hệ mới, thay thế gp2 với nhiều cải tiến.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- gp2: IOPS phụ thuộc vào dung lượng volume (3 IOPS/GB). Để đạt 15,000 IOPS cần 5TB storage → không độc lập.

**❌ Đáp án B:**
- io1 hỗ trợ IOPS độc lập nhưng đắt hơn gp3 cho cùng 15,000 IOPS.

**❌ Đáp án D:**
- Magnetic (standard): tối đa ~100 IOPS, không đáp ứng 15,000 IOPS.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"gp3 = IOPS independent + cheaper than io1. gp2 IOPS = f(storage size)."*
