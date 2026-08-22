# Question #681 - Topic 1

A company uses Amazon EC2 instances and stores data on Amazon Elastic Block Store (Amazon EBS) volumes. The company must ensure that all data is encrypted at rest by using AWS Key Management Service (AWS KMS). The company must be able to control rotation of the encryption keys. Which solution will meet these requirements with the LEAST operational overhead?

## Options

**A.** Create a customer managed key. Use the key to encrypt the EBS volumes.

**B.** Use an AWS managed key to encrypt the EBS volumes. Use the key to configure automatic key rotation.

**C.** Create an external KMS key with imported key material. Use the key to encrypt the EBS volumes.

**D.** Use an AWS owned key to encrypt the EBS volumes.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** EC2 with EBS volumes. Must encrypt at rest using KMS. Must control key rotation.
- **Existing Resources:** EC2 instances, EBS volumes.
- **Current Issue/Goal:** EBS encryption with controllable key rotation.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `control rotation of the encryption keys` | Customer managed key: có thể enable auto rotation hoặc manual rotation. |
| `AWS managed key` | Tự động rotate mỗi năm, không thể control schedule. |
| `AWS owned key` | AWS quản lý hoàn toàn, không thể control. |
| `external key` | Key material imported từ bên ngoài, không thể auto rotate. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Least operational overhead
- **Constraints:** KMS encryption, control key rotation

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- Customer managed key (CMK): cho phép bạn control rotation (enable auto rotation with customizable schedule).
- Tích hợp sẵn với EBS encryption → chỉ cần specify key khi tạo volume.
- Operational overhead thấp: KMS tự động xoay key, bạn chỉ cần enable rotation.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- AWS managed key: AWS tự động rotate mỗi năm, bạn không thể control schedule.

**❌ Đáp án C:**
- External key với imported key material: không thể auto rotate (phải re-import manually), operational overhead cao.

**❌ Đáp án D:**
- AWS owned key: bạn không có control gì cả.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Control key rotation → Customer Managed Key. AWS managed = no control, external = manual rotation."*
