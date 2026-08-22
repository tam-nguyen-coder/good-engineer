# Question #371 - Topic 1

A company needs to create an Amazon Elastic Kubernetes Service (Amazon EKS) cluster to host a digital media streaming application. The EKS cluster will use a managed node group that is backed by Amazon Elastic Block Store (Amazon EBS) volumes for storage. The company must encrypt all data at rest by using a customer managed key that is stored in AWS Key Management Service (AWS KMS). Which combination of actions will meet this requirement with the LEAST operational overhead? (Choose two.)

## Options

**A.** Use a Kubernetes plugin that uses the customer managed key to perform data encryption.

**B.** After creation of the EKS cluster, locate the EBS volumes. Enable encryption by using the customer managed key.

**C.** Enable EBS encryption by default in the AWS Region where the EKS cluster will be created. Select the customer managed key as the default key.

**D.** Create the EKS cluster. Create an IAM role that has a policy that grants permission to the customer managed key. Associate the role with the EKS cluster.

**E.** Store the customer managed key as a Kubernetes secret in the EKS cluster. Use the customer managed key to encrypt the EBS volumes.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** EKS cluster with managed node group + EBS. Cần encryption at rest with KMS CMK. Least operational overhead.
- **Existing Resources:** (none specified)
- **Current Issue/Goal:** Encryption at rest for EBS volumes in EKS.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `EBS encryption by default` | Enable at Region level → tất cả EBS volumes tự động encrypted với CMK. |
| `customer managed key` | KMS key. EKS cluster cần IAM role với KMS permissions. |
| `least operational overhead` | Default encryption + IAM role = tự động, không cần can thiệp per volume. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Choose two, least operational overhead
- **Constraints:** EKS, EBS, KMS CMK encryption at rest

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C và D**

**Giải thích:**
- **C:** Enable EBS encryption by default at Region level với CMK → tất cả EBS volumes created trong Region (including by EKS managed node group) tự động encrypted.
- **D:** IAM role cho EKS cluster với KMS permissions → EKS có quyền sử dụng CMK để encrypt/decrypt EBS volumes.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Kubernetes plugin không cần thiết khi EBS encryption đã được AWS native support.

**❌ Đáp án B:**
- Manual encryption sau khi tạo → operational overhead cao hơn default encryption.

**❌ Đáp án E:**
- Kubernetes secret không phải cách để encrypt EBS volumes (Kubernetes secrets lưu sensitive data, không encrypt storage).

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"EKS EBS encryption → Region-level default encryption (CMK) + IAM role for KMS. Kubernetes plugin/secret = unnecessary."*
