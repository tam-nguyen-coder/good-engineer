# Question #80 - Topic 1

A company recently signed a contract with an AWS Managed Service Provider (MSP) Partner for help with an application migration initiative. A solutions architect needs ta share an Amazon Machine Image (AMI) from an existing AWS account with the MSP Partner's AWS account. The AMI is backed by Amazon Elastic Block Store (Amazon EBS) and uses an AWS Key Management Service (AWS KMS) customer managed key to encrypt EBS volume snapshots. What is the MOST secure way for the solutions architect to share the AMI with the MSP Partner's AWS account?

## Options

**A.** Make the encrypted AMI and snapshots publicly available. Modify the key policy to allow the MSP Partner's AWS account to use the key.

**B.** Modify the launchPermission property of the AMI. Share the AMI with the MSP Partner's AWS account only. Modify the key policy to allow the MSP Partner's AWS account to use the key.

**C.** Modify the launchPermission property of the AMI. Share the AMI with the MSP Partner's AWS account only. Modify the key policy to trust a new KMS key that is owned by the MSP Partner for encryption.

**D.** Export the AMI from the source account to an Amazon S3 bucket in the MSP Partner's AWS account, Encrypt the S3 bucket with a new KMS key that is owned by the MSP Partner. Copy and launch the AMI in the MSP Partner's AWS account.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Share AMI (EBS-backed, KMS-encrypted) với MSP Partner account.
- **Existing Resources:** AMI encrypted với KMS customer managed key.
- **Current Issue/Goal:** Most secure way to share AMI.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `KMS customer managed key` | Cần modify key policy để cho phép account khác dùng |
| `MOST secure` | Least privilege — chỉ share với specific account |
| `launchPermission` | AMI sharing mechanism |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Security + Account sharing
- **Constraints:** KMS-encrypted AMI, secure sharing

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- **Modify launchPermission** — share AMI chỉ với MSP account (không public).
- **Modify KMS key policy** — grant decrypt permission cho MSP account.
- MSP account có thể launch EC2 từ AMI vì có thể decrypt snapshot bằng KMS key.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Publicly available — không secure, ai cũng có thể launch AMI.

**❌ Đáp án C:**
- Không thể đổi encryption của AMI snapshot sang KMS key của MSP — snapshot đã được encrypt bằng source key.

**❌ Đáp án D:**
- Export AMI → S3 — phức tạp, không cần thiết.
- Thêm nhiều bước thủ công, tăng risk.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Share AMI: launchPermission + KMS key policy. Không public, không export S3"*
