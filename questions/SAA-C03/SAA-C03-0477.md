# Question #477 - Topic 1

A group requires permissions to list an Amazon S3 bucket and delete objects from that bucket. An administrator has created the following IAM policy to provide access to the bucket and applied that policy to the group. The group is not able to delete objects in the bucket. The company follows least-privilege access rules. Which statement should a solutions architect add to the policy to correct bucket access?

## Options

(Original question text does not include the actual IAM policy or options. Based on standard AWS S3 IAM patterns:)

**Common Scenario:** The existing policy likely has `s3:ListBucket` at the bucket level ARN but is missing `s3:DeleteObject` at the object level ARN, or the `s3:DeleteObject` action points to the wrong resource.

**Typical Corrective Action:** Add a statement granting `s3:DeleteObject` on `arn:aws:s3:::bucket-name/*`.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** IAM group cần list bucket và delete objects. Administrator đã tạo policy nhưng nhóm không delete được objects.
- **Existing Resources:** IAM policy attached to group, S3 bucket.
- **Current Issue/Goal:** Sửa policy để cho phép delete objects, follow least-privilege.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `list an Amazon S3 bucket` | Cần `s3:ListBucket` với resource `arn:aws:s3:::bucket-name`. |
| `delete objects from that bucket` | Cần `s3:DeleteObject` với resource `arn:aws:s3:::bucket-name/*`. |
| `least-privilege` | Không grant quyền rộng hơn cần thiết. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** IAM policy correction
- **Constraints:** Least privilege, S3 list + delete

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: Thêm statement với `s3:DeleteObject` action và resource `arn:aws:s3:::bucket-name/*`**

**Giải thích:**
- `s3:ListBucket` yêu cầu resource là bucket ARN (`bucket-name`).
- `s3:DeleteObject` và các object-level operations yêu cầu resource là object ARN (`bucket-name/*`).
- Policy hiện tại có thể thiếu `s3:DeleteObject` hoặc chỉ có `s3:ListBucket`.

## 5. CÁC ĐÁP ÁN SAI
(Không có đầy đủ options trong đề gốc, nhưng typical mistakes:)
- Chỉ grant `s3:DeleteObject` ở bucket-level ARN (thiếu `/*`): không hoạt động.
- Grant `s3:*` (quá rộng, không least-privilege).
- Dùng `s3:DeleteObjectVersion` thay vì `s3:DeleteObject`.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"S3 policy: ListBucket = bucket ARN. DeleteObject/PutObject/GetObject = object ARN (bucket-name/*)."*
