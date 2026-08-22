# Question #216 - Topic 1

A company has a serverless website with millions of objects in an Amazon S3 bucket. The company uses the S3 bucket as the origin for an Amazon CloudFront distribution. The company did not set encryption on the S3 bucket before the objects were loaded. A solutions architect needs to enable encryption for all existing objects and for all objects that are added to the S3 bucket in the future. Which solution will meet these requirements with the LEAST amount of effort?

## Options

**A.** Create a new S3 bucket. Turn on the default encryption settings for the new S3 bucket. Download all existing objects to temporary local storage. Upload the objects to the new S3 bucket.

**B.** Turn on the default encryption settings for the S3 bucket. Use the S3 Inventory feature to create a .csv file that lists the unencrypted objects. Run an S3 Batch Operations job that uses the copy command to encrypt those objects.

**C.** Create a new encryption key by using AWS Key Management Service (AWS KMS). Change the settings on the S3 bucket to use server-side encryption with AWS KMS managed encryption keys (SSE-KMS). Turn on versioning for the S3 bucket.

**D.** Navigate to Amazon S3 in the AWS Management Console. Browse the S3 bucket's objects. Sort by the encryption field. Select each unencrypted object. Use the Modify button to apply default encryption settings to every unencrypted object in the S3 bucket.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** S3 bucket with millions of objects, no encryption. Need to encrypt existing + future objects.
- **Existing Resources:** S3 bucket, CloudFront distribution.
- **Current Issue/Goal:** Encrypt all objects, least effort.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `millions of objects` | Cần automated solution — **S3 Batch Operations** |
| `encryption for all existing objects` | Default encryption chỉ áp dụng cho new objects |
| `least amount of effort` | S3 Batch Operations + Copy |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Security / Encryption
- **Constraints:** Millions of objects, existing + future

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- **Default encryption** — encrypt future objects tự động.
- **S3 Inventory** — tạo danh sách objects chưa encrypted.
- **S3 Batch Operations** — dùng COPY command (in-place) để encrypt existing objects với default encryption.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Download/upload — quá nhiều effort cho millions of objects.

**❌ Đáp án C:**
- SSE-KMS + versioning — không encrypt existing objects.

**❌ Đáp án D:**
- Manual via Console — không khả thi cho millions of objects.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Default encryption = future. S3 Batch Operations + Copy = encrypt existing. Manual = not scalable"*
