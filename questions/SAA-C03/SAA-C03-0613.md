# Question #613 - Topic 1

A company uses Amazon Elastic Kubernetes Service (Amazon EKS) to run a container application. The EKS cluster stores sensitive information in the Kubernetes secrets object. The company wants to ensure that the information is encrypted. Which solution will meet these requirements with the LEAST operational overhead?

## Options

**A.** Use the container application to encrypt the information by using AWS Key Management Service (AWS KMS).

**B.** Enable secrets encryption in the EKS cluster by using AWS Key Management Service (AWS KMS).

**C.** Implement an AWS Lambda function to encrypt the information by using AWS Key Management Service (AWS KMS).

**D.** Use AWS Systems Manager Parameter Store to encrypt the information by using AWS Key Management Service (AWS KMS).

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** EKS cluster lưu sensitive information trong Kubernetes secrets, cần encrypt.
- **Existing Resources:** Amazon EKS cluster.
- **Current Issue/Goal:** Encrypt Kubernetes secrets với least operational overhead.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `EKS cluster` | Amazon Elastic Kubernetes Service. |
| `Kubernetes secrets object` | Built-in Kubernetes secrets. |
| `encrypted` | Cần encryption at rest. |
| `least operational overhead` | EKS hỗ trợ KMS encryption cho secrets built-in. |
| `Enable secrets encryption` | Tính năng của EKS: dùng KMS key để tự động encrypt/decrypt secrets. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Least operational overhead
- **Constraints:** Encrypt Kubernetes secrets in EKS

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- EKS hỗ trợ built-in "Secrets Encryption" using AWS KMS.
- Kích hoạt tính năng này trên EKS cluster → tất cả Kubernetes secrets sẽ tự động được encrypt bằng KMS key.
- Zero code, zero application changes → least operational overhead.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Application tự encrypt bằng KMS: cần sửa code application, operational overhead cao hơn.

**❌ Đáp án C:**
- Lambda function encrypt: cần viết, maintain Lambda, tích hợp với EKS → operational overhead cao.

**❌ Đáp án D:**
- Parameter Store: thay đổi cách lưu secrets, không dùng Kubernetes secrets object nữa → operational overhead do migration.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"EKS secrets encryption → enable built-in KMS encryption on cluster. Không cần code."*
