# Question #349 - Topic 1

A company stores confidential data in an Amazon Aurora PostgreSQL database in the ap-southeast-3 Region. The database is encrypted with an AWS Key Management Service (AWS KMS) customer managed key. The company was recently acquired and must securely share a backup of the database with the acquiring company's AWS account in ap-southeast-3. What should a solutions architect do to meet these requirements?

## Options

**A.** Create a database snapshot. Copy the snapshot to a new unencrypted snapshot. Share the new snapshot with the acquiring company's AWS account.

**B.** Create a database snapshot. Add the acquiring company's AWS account to the KMS key policy. Share the snapshot with the acquiring company's AWS account.

**C.** Create a database snapshot that uses a different AWS managed KMS key. Add the acquiring company's AWS account to the KMS key alias. Share the snapshot with the acquiring company's AWS account.

**D.** Create a database snapshot. Download the database snapshot. Upload the database snapshot to an Amazon S3 bucket. Update the S3 bucket policy to allow access from the acquiring company's AWS account.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Aurora PostgreSQL encrypted with KMS CMK. Cần share database backup với acquiring company (cùng Region).
- **Existing Resources:** Aurora PostgreSQL encrypted with KMS CMK, KMS key.
- **Current Issue/Goal:** Share encrypted snapshot với cross-account.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `encrypted with KMS customer managed key` | Snapshot cũng được encrypt bằng KMS key đó. |
| `share the snapshot` | Cần share snapshot cross-account + share KMS key. |
| `KMS key policy` | Add acquiring account's permissions để decrypt snapshot. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Securely share encrypted snapshot
- **Constraints:** Cross-account, same Region, encrypted snapshot

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- Create encrypted snapshot (tự động dùng KMS CMK của database).
- Modify KMS key policy: add acquiring company's AWS account (cho phép decrypt).
- Share snapshot với acquiring account.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Không thể copy encrypted snapshot → unencrypted (bỏ encryption làm mất tính bảo mật).

**❌ Đáp án C:**
- AWS managed KMS key không thể share cross-account (chỉ dùng trong account). KMS key alias không thể cấp permissions.

**❌ Đáp án D:**
- Download + upload S3: quá phức tạp, không cần thiết. KMS key policy + share snapshot là cách chính thống.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Share encrypted snapshot cross-account → share KMS key (key policy) + share snapshot. Không thể bỏ encryption."*
