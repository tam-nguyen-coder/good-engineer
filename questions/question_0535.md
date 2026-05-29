# Question #535 - Topic 1

A company is building an Amazon Elastic Kubernetes Service (Amazon EKS) cluster for its workloads. All secrets that are stored in Amazon EKS must be encrypted in the Kubernetes etcd key-value store. Which solution will meet these requirements?

## Options

**A.** Create a new AWS Key Management Service (AWS KMS) key. Use AWS Secrets Manager to manage, rotate, and store all secrets in Amazon EKS.

**B.** Create a new AWS Key Management Service (AWS KMS) key. Enable Amazon EKS KMS secrets encryption on the Amazon EKS cluster.

**C.** Create the Amazon EKS cluster with default options. Use the Amazon Elastic Block Store (Amazon EBS) Container Storage Interface (CSI) driver as an add-on.

**D.** Create a new AWS Key Management Service (AWS KMS) key with the alias/aws/ebs alias. Enable default Amazon Elastic Block Store (Amazon EBS) volume encryption for the account.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Cần encrypt secrets trong EKS etcd store.
- **Existing Resources:** EKS cluster (building).
- **Current Issue/Goal:** Encrypt secrets trong etcd key-value store của Kubernetes.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `secrets in EKS` | Kubernetes secrets lưu trong etcd |
| `encrypted in etcd` | EKS supports envelope encryption of Kubernetes secrets using AWS KMS |
| `EKS KMS secrets encryption` | Tính năng native của EKS để encrypt secrets trong etcd |
| `AWS KMS key` | Customer managed key để encrypt/decrypt secrets |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Security
- **Constraints:** Encrypt secrets in etcd

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- Amazon EKS hỗ trợ KMS secrets encryption: tính năng native dùng AWS KMS để encrypt Kubernetes secrets trong etcd.
- Khi enable, EKS tự động encrypt secrets khi ghi vào etcd và decrypt khi đọc.
- Chỉ cần tạo KMS key và enable tính năng này trên EKS cluster.
- Đây là encryption at rest cho secrets, bảo vệ dữ liệu nhạy cảm.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Secrets Manager dùng để lưu secrets riêng, không encrypt etcd của EKS.
- Kubernetes secrets vẫn được lưu trong etcd dạng plaintext nếu không bật EKS KMS encryption.

**❌ Đáp án C:**
- EBS CSI driver dùng để quản lý persistent volumes, không liên quan đến encrypt etcd secrets.
- Default options không bật KMS encryption cho etcd.

**❌ Đáp án D:**
- EBS volume encryption encrypt dữ liệu trên EBS volumes, không phải etcd secrets.
- `alias/aws/ebs` là alias cho EBS encryption, không phải cho EKS secrets.

## 6. MẸO GHI NHỚ (MEMORY HOOK)
🧠 *"EKS etcd encryption = EKS KMS secrets encryption. EBS CSI driver = volumes, không phải etcd."*
