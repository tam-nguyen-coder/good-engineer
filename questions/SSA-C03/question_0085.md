# Question #85 - Topic 1

A company has a production web application in which users upload documents through a web interface or a mobile app. According to a new regulatory requirement. new documents cannot be modified or deleted after they are stored. What should a solutions architect do to meet this requirement?

## Options

**A.** Store the uploaded documents in an Amazon S3 bucket with S3 Versioning and S3 Object Lock enabled.

**B.** Store the uploaded documents in an Amazon S3 bucket. Configure an S3 Lifecycle policy to archive the documents periodically.

**C.** Store the uploaded documents in an Amazon S3 bucket with S3 Versioning enabled. Configure an ACL to restrict all access to read-only.

**D.** Store the uploaded documents on an Amazon Elastic File System (Amazon EFS) volume. Access the data by mounting the volume in read- only mode.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Web/mobile app upload documents. Regulatory: documents cannot be modified or deleted after stored.
- **Existing Resources:** Web application, mobile app.
- **Current Issue/Goal:** Immutable storage — WORM (Write Once Read Many).

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `cannot be modified or deleted after they are stored` | Cần **S3 Object Lock** (WORM) |
| `regulatory requirement` | Compliance — Object Lock |
| `S3 Versioning` | Yêu cầu để enable Object Lock |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Compliance / Security
- **Constraints:** Không modify/delete sau khi store

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- **S3 Object Lock** — prevent objects từ bị modify hoặc delete trong retention period (WORM).
- **S3 Versioning** — required để enable Object Lock, giữ tất cả versions.
- Đáp ứng regulatory requirement: không ai có thể xoá/sửa documents sau khi upload.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Lifecycle policy chỉ move/delete objects, không prevent modification/deletion.

**❌ Đáp án C:**
- ACL có thể bị thay đổi bởi user có quyền — không đảm bảo immutable.
- Versioning giữ versions nhưng không prevent deletion (vẫn có thể delete object, chỉ là tạo delete marker).

**❌ Đáp án D:**
- EFS volume có thể remount ở chế độ read-write — không đảm bảo immutable.
- EFS không có WORM feature như S3 Object Lock.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"S3 Object Lock = WORM (Write Once Read Many). Versioning cần để enable Object Lock"*
