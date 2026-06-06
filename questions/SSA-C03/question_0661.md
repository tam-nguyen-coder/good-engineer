# Question #661 - Topic 1

A company runs applications on AWS that connect to the company's Amazon RDS database. The applications scale on weekends and at peak times of the year. The company wants to scale the database more effectively for its applications that connect to the database. Which solution will meet these requirements with the LEAST operational overhead?

## Options

**A.** Use Amazon DynamoDB with connection pooling with a target group configuration for the database. Change the applications to use the DynamoDB endpoint.

**B.** Use Amazon RDS Proxy with a target group for the database. Change the applications to use the RDS Proxy endpoint.

**C.** Use a custom proxy that runs on Amazon EC2 as an intermediary to the database. Change the applications to use the custom proxy endpoint.

**D.** Use an AWS Lambda function to provide connection pooling with a target group configuration for the database. Change the applications to use the Lambda function.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Applications connecting to RDS database. Apps scale on weekends and peaks. Need effective database scaling.
- **Existing Resources:** RDS database, applications.
- **Current Issue/Goal:** Connection pooling, reduce operational overhead.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `scale on weekends and at peak times` | Many concurrent connections → need connection pooling. |
| `RDS Proxy` | AWS managed connection pooling service for RDS. |
| `least operational overhead` | RDS Proxy (managed) > custom proxy (self-managed). |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Least operational overhead
- **Constraints:** Connection pooling, RDS database, app scaling

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- RDS Proxy là managed service chuyên dụng cho connection pooling → giảm connection stress trên RDS.
- Tự động scale connections khi applications scale.
- Chỉ cần thay đổi endpoint trong applications → operational overhead thấp nhất.
- Bảo vệ database khỏi connection storms khi app scale đột ngột.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- DynamoDB là NoSQL, không compatible với RDS (relational) database.
- Connection pooling + target group không phải feature của DynamoDB.

**❌ Đáp án C:**
- Custom proxy trên EC2: cần tự quản lý (OS, scaling, patches) → operational overhead cao.

**❌ Đáp án D:**
- Lambda không phải connection pool proxy.
- Lambda bị timeout (max 15 phút), không phù hợp làm database proxy.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"RDS connection pooling → RDS Proxy (managed, auto-scale). Custom proxy = extra overhead."*
