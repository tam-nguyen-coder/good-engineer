# Question #308 - Topic 1

A company has multiple AWS accounts that use consolidated billing. The company runs several active high performance Amazon RDS for Oracle On-Demand DB instances for 90 days. The company's finance team has access to AWS Trusted Advisor in the consolidated billing account and all other AWS accounts. The finance team needs to use the appropriate AWS account to access the Trusted Advisor check recommendations for RDS. The finance team must review the appropriate Trusted Advisor check to reduce RDS costs. Which combination of steps should the finance team take to meet these requirements? (Choose two.)

## Options

**A.** Use the Trusted Advisor recommendations from the account where the RDS instances are running.

**B.** Use the Trusted Advisor recommendations from the consolidated billing account to see all RDS instance checks at the same time.

**C.** Review the Trusted Advisor check for Amazon RDS Reserved Instance Optimization.

**D.** Review the Trusted Advisor check for Amazon RDS Idle DB Instances.

**E.** Review the Trusted Advisor check for Amazon Redshift Reserved Node Optimization.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Multiple accounts, consolidated billing. RDS Oracle On-Demand chạy 90 ngày. Cần dùng Trusted Advisor để giảm RDS cost.
- **Existing Resources:** Multiple AWS accounts, RDS Oracle On-Demand instances (90 days).
- **Current Issue/Goal:**
   - 1. Chọn đúng account để xem Trusted Advisor (see all RDS checks)
   - 2. Chọn đúng Trusted Advisor check để giảm RDS cost

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `consolidated billing` | Master/payer account có thể xem Trusted Advisor checks cho tất cả member accounts. |
| `active high performance RDS for Oracle On-Demand` | Chạy 90 ngày → on-demand đang đắt, có thể dùng Reserved Instances. |
| `reduce RDS costs` | Trusted Advisor check: RDS Reserved Instance Optimization (recommend Reserved Instances cho instances chạy lâu). |
| `Trusted Advisor` | Tool recommend optimization (cost, performance, security, fault tolerance). |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Choose two
- **Constraints:** Consolidated billing, RDS cost reduction

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B và C**

**Giải thích:**
- **B:** Consolidated billing account cho phép xem Trusted Advisor recommendations cho tất cả member accounts cùng lúc (không cần login từng account).
- **C:** RDS Reserved Instance Optimization check identify những instances đã chạy đủ lâu để mua Reserved Instances → significant cost savings.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Từng account riêng lẻ không thấy được tổng thể, không hiệu quả bằng consolidated billing account.

**❌ Đáp án D:**
- RDS Idle DB Instances check tìm instances không hoạt động. Ở đây instances đang active → không applicable.

**❌ Đáp án E:**
- Redshift Reserved Node Optimization check dành cho Amazon Redshift, không liên quan RDS.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Consolidated billing account → xem Trusted Advisor cho all accounts. RDS active 90 days → Reserved Instance Optimization."*
