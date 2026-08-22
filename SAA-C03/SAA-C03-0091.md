# Question #91 - Topic 1

A company has applications that run on Amazon EC2 instances in a VPC. One of the applications needs to call the Amazon S3 API to store and read objects. According to the company's security regulations, no traffic from the applications is allowed to travel across the internet. Which solution will meet these requirements?

## Options

**A.** Configure an S3 gateway endpoint.

**B.** Create an S3 bucket in a private subnet.

**C.** Create an S3 bucket in the same AWS Region as the EC2 instances.

**D.** Configure a NAT gateway in the same subnet as the EC2 instances.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** EC2 in VPC cần access S3 API, không được dùng internet.
- **Existing Resources:** EC2 instances in VPC, S3 bucket.
- **Current Issue/Goal:** Private S3 access, no internet.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `no traffic from the applications is allowed to travel across the internet` | Cần **VPC Gateway Endpoint** |
| `S3 API` | AWS service, có VPC endpoint |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Network security
- **Constraints:** No internet traffic

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- **S3 Gateway Endpoint** — cho phép EC2 access S3 qua AWS private network, không qua internet.
- Free, không cần NAT gateway/IGW.
- Traffic hoàn toàn ở trong AWS network.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- S3 bucket là global resource, không thể tạo "trong subnet".

**❌ Đáp án C:**
- Cùng Region không đảm bảo traffic không qua internet.

**❌ Đáp án D:**
- **NAT gateway** — traffic đi qua internet để đến S3 (NAT gateway → internet → S3).

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"S3 Gateway Endpoint = private access (free, no internet). NAT gateway = internet access (cost)"*
