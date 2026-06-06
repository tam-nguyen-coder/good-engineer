# Question #564 - Topic 1

A company is building an ecommerce application and needs to store sensitive customer information. The company needs to give customers the ability to complete purchase transactions on the website. The company also needs to ensure that sensitive customer data is protected, even from database administrators. Which solution meets these requirements?

## Options

**A.** Store sensitive data in an Amazon Elastic Block Store (Amazon EBS) volume. Use EBS encryption to encrypt the data. Use an IAM instance role to restrict access.

**B.** Store sensitive data in Amazon RDS for MySQL. Use AWS Key Management Service (AWS KMS) client-side encryption to encrypt the data.

**C.** Store sensitive data in Amazon S3. Use AWS Key Management Service (AWS KMS) server-side encryption to encrypt the data. Use S3 bucket policies to restrict access.

**D.** Store sensitive data in Amazon FSx for Windows Server. Mount the file share on application servers. Use Windows file permissions to restrict access.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Ecommerce application lưu sensitive customer information. Khách hàng cần thực hiện purchase transactions. Dữ liệu phải được bảo vệ ngay cả khỏi database administrators.
- **Existing Resources:** Chưa có.
- **Current Issue/Goal:** Bảo vệ sensitive data – kể cả DBAs cũng không thể đọc được.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `protected, even from database administrators` | DBAs không thể decrypt data → cần client-side encryption |
| `sensitive customer information` | Thông tin nhạy cảm (thẻ tín dụng, SSN, v.v.) |
| `KMS client-side encryption` | Mã hóa trước khi gửi lên database, DBAs chỉ thấy ciphertext |
| `server-side encryption` | AWS mã hóa ở server, nhưng DBAs (có DB access) vẫn có thể đọc |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most appropriate solution
- **Constraints:** Bảo vệ data from DBAs (insider threat)

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- Client-side encryption với AWS KMS: dữ liệu được mã hóa ở phía client (application) trước khi gửi lên RDS. DBAs chỉ nhìn thấy ciphertext trong database.
- DBAs có thể có quyền truy cập database, có thể query, nhưng không thể decrypt vì không có KMS decrypt permissions.
- Application server giữ decryption keys hoặc gọi KMS API để decrypt.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A (EBS + encryption + IAM role):** EBS encryption bảo vệ dữ liệu-at-rest trên disk. Nhưng nếu application đọc data từ EBS volume và decrypt (vì cần hiển thị cho user), DBAs có quyền truy cập instance có thể đọc dữ liệu. EBS encryption không bảo vệ khỏi người có quyền truy cập OS.

**❌ Đáp án C (S3 + SSE-KMS + bucket policies):** Server-side encryption (SSE-KMS) mã hóa ở phía AWS S3. Nhưng nếu DBAs có quyền truy cập S3 và KMS decrypt permissions, họ có thể đọc data. SSE không bảo vệ khỏi authorized users có KMS access.

**❌ Đáp án D (FSx + Windows permissions):** Windows file permissions không bảo vệ khỏi administrators (admin có thể lấy quyền). FSx encryption at rest bảo vệ data trên disk, nhưng admins có quyền truy cập server vẫn đọc được.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Protect data from DBAs = client-side encryption. Only application can decrypt. Server-side (SSE) = AWS can decrypt, DBAs with access can read."*
