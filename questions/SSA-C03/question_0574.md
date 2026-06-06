# Question #574 - Topic 1

A financial services company launched a new application that uses an Amazon RDS for MySQL database. The company uses the application to track stock market trends. The company needs to operate the application for only 2 hours at the end of each week. The company needs to optimize the cost of running the database. Which solution will meet these requirements MOST cost-effectively?

## Options

**A.** Migrate the existing RDS for MySQL database to an Aurora Serverless v2 MySQL database cluster.

**B.** Migrate the existing RDS for MySQL database to an Aurora MySQL database cluster.

**C.** Migrate the existing RDS for MySQL database to an Amazon EC2 instance that runs MySQL. Purchase an instance reservation for the EC2 instance.

**D.** Migrate the existing RDS for MySQL database to an Amazon Elastic Container Service (Amazon ECS) cluster that uses MySQL container images to run tasks.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** RDS for MySQL cho stock market tracking, chỉ chạy 2 giờ cuối mỗi tuần.
- **Existing Resources:** RDS for MySQL DB instance.
- **Current Issue/Goal:** Optimize cost cho workload chạy không thường xuyên.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `only 2 hours at the end of each week` | Workload rất thấp, cần service có thể pause khi không dùng. |
| `MOST cost-effectively` | Aurora Serverless v2 có thể scale xuống 0 ACU khi không hoạt động (hoặc rất thấp). |
| `Aurora Serverless v2` | Pay per ACU, auto scale, có thể pause. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most cost-effectively
- **Constraints:** MySQL-compatible, 2h/tuần

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- Aurora Serverless v2 chỉ tính phí khi hoạt động. Có thể scale xuống gần 0 khi không dùng.
- 2h/tuần → cost rất thấp so với provisioned instances chạy 24/7.
- MySQL-compatible (Aurora MySQL).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Aurora MySQL provisioned: chạy 24/7, tốn phí dù không dùng.

**❌ Đáp án C:**
- EC2 + reservation: cam kết 1-3 năm, dù chỉ dùng 2h/tuần → lãng phí.

**❌ Đáp án D:**
- ECS + MySQL container: vẫn cần EC2 instances chạy 24/7, tốn phí compute.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Only 2h/week → Aurora Serverless v2 (scale to near zero). Provisioned = 24/7 cost = wasteful."*
