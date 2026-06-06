# Question #511 - Topic 1

A company is developing software that uses a PostgreSQL database schema. The company needs to configure multiple development environments and databases for the company's developers. On average, each development environment is used for half of the 8-hour workday. Which solution will meet these requirements MOST cost-effectively?

## Options

**A.** Configure each development environment with its own Amazon Aurora PostgreSQL database

**B.** Configure each development environment with its own Amazon RDS for PostgreSQL Single-AZ DB instances

**C.** Configure each development environment with its own Amazon Aurora On-Demand PostgreSQL-Compatible database

**D.** Configure each development environment with its own Amazon S3 bucket by using Amazon S3 Object Select

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Dev environments dùng PostgreSQL, mỗi dev có database riêng. Dùng 4 tiếng/ngày (nửa ngày làm việc).
- **Existing Resources:** PostgreSQL development environments.
- **Current Issue/Goal:** Database cho dev với chi phí thấp nhất khi workload không liên tục.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `development environments` | Không yêu cầu production-grade availability. |
| `used for half of the 8-hour workday` | Workload không liên tục (50% thời gian). |
| `MOST cost-effectively` | Cần giải pháp chỉ trả tiền khi dùng. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most cost-effective
- **Constraints:** PostgreSQL, development (không production), intermittent usage

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- Aurora On-Demand (Aurora Serverless v1/v2) tự động scale và chỉ tính phí khi có hoạt động (ACU per second). Khi dev không dùng, database pause → không tốn chi phí.
- Với workload 4h/ngày, Aurora Serverless rẻ hơn nhiều so với provisioned (trả tiền 24/7).
- PostgreSQL-compatible: Aurora hỗ trợ PostgreSQL.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Aurora PostgreSQL provisioned: bạn trả tiền cho instance chạy 24/7 dù chỉ dùng 4h/ngày → lãng phí.

**❌ Đáp án B:**
- RDS PostgreSQL Single-AZ: tương tự, trả tiền cho instance chạy 24/7. Rẻ hơn Aurora provisioned nhưng vẫn đắt hơn Aurora Serverless cho use case intermittent.

**❌ Đáp án D:**
- S3 Object Select dùng để query dữ liệu có cấu trúc trong S3 (Parquet, CSV, JSON). Không phải PostgreSQL database.
- Không thể thay thế relation database cho dev environment.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Dev database dùng ít → Aurora Serverless (chỉ trả tiền khi dùng). RDS/Aurora provisioned = trả 24/7."*
