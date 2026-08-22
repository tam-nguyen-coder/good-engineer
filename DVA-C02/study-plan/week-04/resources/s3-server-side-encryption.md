# Protecting data with server-side encryption (`Amazon S3`)

> **Nguồn (AWS official):** https://docs.aws.amazon.com/AmazonS3/latest/userguide/serv-side-encryption.html
> **Tuần:** 4 — `API Gateway` + `S3` (góc Developer) · **Loại:** AWS Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)
- ⚠️ MẶC ĐỊNH quan trọng: từ **5/1/2023**, mọi object mới upload lên S3 **tự động mã hoá at-rest**, mức nền là **`SSE-S3`** — miễn phí, không ảnh hưởng hiệu năng. Mọi bucket đều có encryption cấu hình sẵn.
- **4 lựa chọn server-side encryption loại trừ lẫn nhau** (không áp 2 loại lên cùng object):
  - **`SSE-S3`**: AWS quản lý khoá, **AES-256**, mỗi object 1 khoá riêng; root key tự xoay vòng. Đơn giản, mặc định.
  - **`SSE-KMS`**: tích hợp `AWS KMS` → **kiểm soát khoá nhiều hơn**: xem khoá riêng, sửa policy, **theo dõi qua `CloudTrail`** (audit); dùng customer managed key hoặc AWS managed key.
  - **`DSSE-KMS`**: giống SSE-KMS nhưng **2 lớp AES-256** độc lập (dual-layer) — phục vụ yêu cầu tuân thủ multilayer.
  - **`SSE-C`**: **khách tự quản khoá**, gửi khoá theo mỗi request; S3 mã hoá/giải mã nhưng **không lưu khoá**.
- Đề hỏi "cần **audit** ai dùng khoá + **rotation** + kiểm soát quyền khoá" → **`SSE-KMS`** (không phải `SSE-S3`). Hỏi "khách **tự giữ khoá**, AWS không lưu" → **`SSE-C`**.
- Đổi default encryption của bucket sang SSE-KMS **KHÔNG** đổi mã hoá các object đã tồn tại → muốn mã lại object cũ dùng **`S3 Batch Operations`** + **`S3 Inventory`** (action Copy objects).
- presigned URL hoạt động **giống nhau** cho object mã hoá và không mã hoá; list object cũng trả mọi object bất kể mã hoá.
- ⚠️ Cập nhật mới (4/2026): bucket general purpose **mới** **mặc định TẮT `SSE-C`** cho write request; muốn dùng SSE-C phải chủ động bật qua `PutBucketEncryption`.

---

## 📄 Nội dung (trích từ tài liệu gốc)

# Protecting data with server-side encryption

**Important (Apr 2026):** Amazon S3 now applies a new default bucket security setting that automatically **disables server-side encryption with customer-provided keys (SSE-C)** for all new general purpose buckets. Applications that need SSE-C must deliberately enable it using the `PutBucketEncryption` API after creating a new bucket.

**Important (Jan 5, 2023):** Amazon S3 applies **server-side encryption with Amazon S3 managed keys (SSE-S3) as the base level of encryption for every bucket**. All new object uploads are automatically encrypted at rest at no additional cost and with no impact on performance. Encryption status is available in CloudTrail logs, S3 Inventory, S3 Storage Lens, the S3 console, and as an additional API response header in the CLI and SDKs.

Server-side encryption is the encryption of data at its destination by the application or service that receives it. Amazon S3 encrypts your data at the object level as it writes it to disks in AWS data centers and decrypts it for you when you access it. As long as you authenticate your request and have access permissions, there is no difference in the way you access encrypted or unencrypted objects. For example, a presigned URL works the same way for both encrypted and unencrypted objects. List API operations return all objects, regardless of whether they are encrypted.

All Amazon S3 buckets have encryption configured by default, and all new objects uploaded are automatically encrypted at rest. **SSE-S3 is the default encryption configuration for every bucket.** To use a different type, specify the type in your `PUT` requests, or update the default encryption configuration in the destination bucket.

For different encryption in `PUT` requests, you can use SSE-KMS, DSSE-KMS, or SSE-C. For a different default encryption configuration in the destination bucket, you can use SSE-KMS or DSSE-KMS.

When you change the default encryption configuration of your bucket to SSE-KMS, the encryption type of the **existing** objects is **not changed**. To change the encryption type of pre-existing objects, use **S3 Batch Operations** (with the Copy objects action) — a single job can operate on billions of objects. If you need to encrypt existing objects, use S3 Batch Operations and S3 Inventory.

**Note:** You can't apply different types of server-side encryption to the same object simultaneously.

When storing data in Amazon S3 you have **four mutually exclusive options** for server-side encryption, depending on how you choose to manage the encryption keys and the number of encryption layers.

**Server-side encryption with Amazon S3 managed keys (SSE-S3)**
All S3 buckets have encryption configured by default; the default option is SSE-S3. Each object is encrypted with a unique key. As an additional safeguard, SSE-S3 encrypts the key itself with a root key that it regularly rotates. SSE-S3 uses **256-bit Advanced Encryption Standard (AES-256)** to encrypt your data.

**Server-side encryption with AWS Key Management Service (AWS KMS) keys (SSE-KMS)**
Provided through an integration of AWS KMS with Amazon S3. With AWS KMS you have more control over your keys: view separate keys, edit control policies, and **follow the keys in AWS CloudTrail**. You can create and manage customer managed keys or use AWS managed keys that are unique to you, your service, and your Region.

**Dual-layer server-side encryption with AWS KMS keys (DSSE-KMS)**
Similar to SSE-KMS, but DSSE-KMS applies **two independent layers of AES-256 encryption** instead of one: first using an AWS KMS data encryption key, then using a separate Amazon S3-managed encryption key. Because both layers are applied server-side, you can use a wide range of AWS services and tools to analyze data in S3 while satisfying compliance requirements for multilayer encryption.

**Server-side encryption with customer-provided keys (SSE-C)**
With SSE-C, **you manage the encryption keys**, and Amazon S3 manages the encryption as it writes to disks and the decryption when you access your objects.

**Note:** Objects encrypted with SSE-C do not support annotations. For all other encryption types, annotations inherit the encryption configuration of the parent object. S3 Bucket Keys are supported for annotations on SSE-KMS encrypted objects.

**Note (Amazon FSx via S3 access points):** All Amazon FSx file systems have encryption configured by default and are encrypted at rest with keys managed using AWS Key Management Service. Data is automatically encrypted/decrypted by the file system as it is written and read.
