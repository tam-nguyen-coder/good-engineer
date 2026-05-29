# Question #669 - Topic 1

A company runs its databases on Amazon RDS for PostgreSQL. The company wants a secure solution to manage the master user password by rotating the password every 30 days. Which solution will meet these requirements with the LEAST operational overhead?

## Options

**A.** Use Amazon EventBridge to schedule a custom AWS Lambda function to rotate the password every 30 days.

**B.** Use the modify-db-instance command in the AWS CLI to change the password.

**C.** Integrate AWS Secrets Manager with Amazon RDS for PostgreSQL to automate password rotation.

**D.** Integrate AWS Systems Manager Parameter Store with Amazon RDS for PostgreSQL to automate password rotation.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** RDS PostgreSQL, need to rotate master password every 30 days.
- **Existing Resources:** RDS for PostgreSQL.
- **Current Issue/Goal:** Secure password rotation, least operational overhead.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `rotate the password every 30 days` | Tự động rotation định kỳ. |
| `AWS Secrets Manager` | Managed service chuyên cho secret rotation, tích hợp sẵn với RDS. |
| `least operational overhead` | Secrets Manager (built-in rotation) > custom Lambda. |
| `Parameter Store` | Lưu secrets nhưng không có built-in rotation cho RDS. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Least operational overhead
- **Constraints:** Every 30 days, secure

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- AWS Secrets Manager tích hợp sẵn với RDS PostgreSQL để tự động rotation.
- Chỉ cần enable automatic rotation trong Secrets Manager, chọn interval 30 days.
- Không cần code custom, operational overhead thấp nhất.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Custom Lambda + EventBridge → operational overhead cao hơn Secrets Manager built-in.

**❌ Đáp án B:**
- CLI command thủ công (hoặc script) → không tự động, operational overhead cao.

**❌ Đáp án D:**
- Parameter Store lưu secrets nhưng không có built-in rotation capability cho RDS như Secrets Manager.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"RDS password rotation → AWS Secrets Manager (built-in, auto). Custom Lambda = more overhead."*
