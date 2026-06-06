# Question #410 - Topic 1

A company is deploying a new application on Amazon EC2 instances. The application writes data to Amazon Elastic Block Store (Amazon EBS) volumes. The company needs to ensure that all data that is written to the EBS volumes is encrypted at rest. Which solution will meet this requirement?

## Options

**A.** Create an IAM role that specifies EBS encryption. Attach the role to the EC2 instances.

**B.** Create the EBS volumes as encrypted volumes. Attach the EBS volumes to the EC2 instances.

**C.** Create an EC2 instance tag that has a key of Encrypt and a value of True. Tag all instances that require encryption at the EBS level.

**D.** Create an AWS Key Management Service (AWS KMS) key policy that enforces EBS encryption in the account. Ensure that the key policy is active.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** EC2 writes data to EBS. Need all data encrypted at rest.
- **Existing Resources:** EC2 instances, EBS volumes.
- **Current Issue/Goal:** Ensure EBS encryption at rest.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `encrypted at rest` | EBS encryption using KMS. |
| `EBS volumes` | Encryption enabled at volume creation time. |
| `all data` | Every volume must be encrypted. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Security / Encryption
- **Constraints:** All EBS volumes encrypted at rest

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- Create EBS volumes with encryption enabled (checkbox or --encrypted flag).
- Attach to EC2 instances. Data at rest được mã hóa tự động.
- Có thể dùng default KMS key hoặc custom KMS key.
- Encryption xảy ra transparently (không ảnh hưởng application).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- IAM role không thể "specify EBS encryption". IAM role gán permissions, không enable encryption.

**❌ Đáp án C:**
- Tags chỉ là metadata, không tự động enable encryption. Cần action từ bên ngoài (e.g., Lambda check tags) mới có tác dụng.

**❌ Đáp án D:**
- KMS key policy: kiểm soát ai dùng được key, không enforce encryption trên EBS. Để enforce cần dùng IAM policy hoặc account-level setting (encryption by default).

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"EBS encryption = enable at volume creation. Tags/IAM/KMS policy không tự encrypt."*

