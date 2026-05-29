# Question #256 - Topic 1

A solutions architect is implementing a document review application using an Amazon S3 bucket for storage. The solution must prevent accidental deletion of the documents and ensure that all versions of the documents are available. Users must be able to download, modify, and upload documents. Which combination of actions should be taken to meet these requirements? (Choose two.)

## Options

**A.** Enable a read-only bucket ACL.

**B.** Enable versioning on the bucket.

**C.** Attach an IAM policy to the bucket.

**D.** Enable MFA Delete on the bucket.

**E.** Encrypt the bucket using AWS KMS.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Document review app, S3 storage. Prevent accidental deletion, keep all versions. Users download/modify/upload.
- **Existing Resources:** S3 bucket.
- **Current Issue/Goal:** Versioning + MFA Delete.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `all versions of the documents are available` | **S3 Versioning** |
| `prevent accidental deletion` | **MFA Delete** |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Storage / Security
- **Constraints:** Chọn 2, versioning + deletion prevention

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B và D**

**Giải thích:**
- **B: Versioning** — giữ tất cả versions của documents.
- **D: MFA Delete** — yêu cầu MFA code để delete objects → prevent accidental deletion.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Read-only ACL — ngăn users upload/modify.

**❌ Đáp án C:**
- IAM policy — cần thiết cho permissions nhưng không prevent deletion hay giữ versions.

**❌ Đáp án E:**
- KMS encryption — mã hoá, không prevent deletion.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Versioning = keep all versions. MFA Delete = prevent accidental deletion. Read-only ACL = blocks uploads"*
