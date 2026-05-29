# Question #92 - Topic 1

A company is storing sensitive user information in an Amazon S3 bucket. The company wants to provide secure access to this bucket from the application tier running on Amazon EC2 instances inside a VPC. Which combination of steps should a solutions architect take to accomplish this? (Choose two.)

## Options

**A.** Configure a VPC gateway endpoint for Amazon S3 within the VPC.

**B.** Create a bucket policy to make the objects in the S3 bucket public.

**C.** Create a bucket policy that limits access to only the application tier running in the VPC.

**D.** Create an IAM user with an S3 access policy and copy the IAM credentials to the EC2 instance.

**E.** Create a NAT instance and have the EC2 instances use the NAT instance to access the S3 bucket.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Sensitive data in S3, EC2 in VPC cần access.
- **Existing Resources:** S3 bucket, VPC with EC2 instances.
- **Current Issue/Goal:** Secure private access từ VPC đến S3.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `secure access` | VPC endpoint + bucket policy |
| `sensitive user information` | Không public, access từ VPC only |
| `VPC gateway endpoint` | Private connection to S3 |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Security + Networking
- **Constraints:** Chọn 2 đáp án

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A và C**

**Giải thích:**
- **A: VPC Gateway Endpoint** — kết nối private từ VPC đến S3.
- **C: Bucket policy restrict to VPC** — chỉ cho phép access từ VPC (dùng `aws:SourceVpc` condition).
- Kết hợp: private network + access control = secure solution.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Public bucket — không secure cho sensitive data.

**❌ Đáp án D:**
- IAM user credentials trên EC2 (access key/secret key) — không secure (long-lived credentials), nên dùng IAM role.

**❌ Đáp án E:**
- NAT instance — traffic đi qua internet, không private, thêm chi phí.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"S3 Gateway Endpoint + bucket policy restrict to VPC = private + secure. Credentials trên EC2 = bad practice"*
