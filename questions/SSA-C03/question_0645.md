# Question #645 - Topic 1

A company is required to use cryptographic keys in its on-premises key manager. The key manager is outside of the AWS Cloud because of regulatory and compliance requirements. The company wants to manage encryption and decryption by using cryptographic keys that are retained outside of the AWS Cloud and that support a variety of external key managers from different vendors. Which solution will meet these requirements with the LEAST operational overhead?

## Options

**A.** Use AWS CloudHSM key store backed by a CloudHSM cluster.

**B.** Use an AWS Key Management Service (AWS KMS) external key store backed by an external key manager.

**C.** Use the default AWS Key Management Service (AWS KMS) managed key store.

**D.** Use a custom key store backed by an AWS CloudHSM cluster.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Keys must be stored in on-premises key manager due to compliance. Support various external key managers from different vendors.
- **Existing Resources:** On-premises key manager, AWS account.
- **Current Issue/Goal:** Encrypt/decrypt with keys outside AWS Cloud, vendor-agnostic, least operational overhead.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `on-premises key manager` | Keys retained outside AWS Cloud. |
| `variety of external key managers from different vendors` | Cần giải pháp vendor-agnostic. |
| `least operational overhead` | AWS managed service thay vì tự quản lý. |
| `AWS KMS external key store (XKS)` | Cho phép dùng KMS với key stored bên ngoài AWS. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Least operational overhead
- **Constraints:** Keys must be outside AWS, support multiple vendor key managers

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- AWS KMS External Key Store (XKS) cho phép sử dụng KMS API với key được lưu trữ bên ngoài AWS (on-premises).
- Hỗ trợ nhiều vendor key managers khác nhau.
- Tích hợp sẵn với AWS services, operational overhead thấp nhất.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- CloudHSM key store: keys stored trong CloudHSM cluster (trong AWS), không phải on-premises.

**❌ Đáp án C:**
- Default KMS managed key store: keys stored trong AWS, không đáp ứng yêu cầu lưu key bên ngoài.

**❌ Đáp án D:**
- Custom key store backed by CloudHSM: keys stored trong CloudHSM (trong AWS), không phải on-premises.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Keys outside AWS → KMS External Key Store (XKS). CloudHSM = inside AWS."*
