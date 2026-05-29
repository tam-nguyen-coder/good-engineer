# Question #572 - Topic 1

A company runs an application on AWS. The application receives inconsistent amounts of usage. The application uses AWS Direct Connect to connect to an on-premises MySQL-compatible database. The on-premises database consistently uses a minimum of 2 GiB of memory. The company wants to migrate the on-premises database to a managed AWS service. The company wants to use auto scaling capabilities to manage unexpected workload increases. Which solution will meet these requirements with the LEAST administrative overhead?

## Options

**A.** Provision an Amazon DynamoDB database with default read and write capacity settings.

**B.** Provision an Amazon Aurora database with a minimum capacity of 1 Aurora capacity unit (ACU).

**C.** Provision an Amazon Aurora Serverless v2 database with a minimum capacity of 1 Aurora capacity unit (ACU).

**D.** Provision an Amazon RDS for MySQL database with 2 GiB of memory.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Application dùng Direct Connect kết nối MySQL-compatible DB on-prem, muốn migrate lên managed service, có auto scaling, inconsistent usage.
- **Existing Resources:** Direct Connect, on-prem MySQL database (min 2 GiB memory).
- **Current Issue/Goal:** Migrate lên managed service, auto scaling, least admin overhead.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `MySQL-compatible` | Cần MySQL-compatible managed service (Aurora MySQL, RDS MySQL). |
| `auto scaling` | Aurora Serverless v2 có khả năng auto scale ACUs. |
| `Aurora Serverless v2` | Auto scaling capacity, quản lý theo ACU (1 ACU ≈ 2 GiB memory). |
| `least administrative overhead` | Serverless: không cần quản lý instance, auto scaling built-in. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Least administrative overhead
- **Constraints:** MySQL-compatible, auto scaling, min 2 GiB memory

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- Aurora Serverless v2 tự động scale capacity dựa trên workload, không cần quản lý instance.
- Minimum capacity 1 ACU ≈ 2 GiB memory, đáp ứng yêu cầu min 2 GiB.
- MySQL-compatible (Aurora MySQL).
- Serverless = least administrative overhead (không patching, không scaling config thủ công).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- DynamoDB là NoSQL, không MySQL-compatible.

**❌ Đáp án B:**
- Aurora (provisioned) không auto scaling; phải manual scale hoặc dùng auto scaling policies → nhiều admin overhead hơn Serverless v2.

**❌ Đáp án D:**
- RDS MySQL với 2 GiB fixed size, không auto scaling → không đáp ứng yêu cầu auto scale.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"MySQL + auto scale + least admin → Aurora Serverless v2. Provisioned Aurora/RDS = manual scaling = more overhead."*
