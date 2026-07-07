# Uploading and copying objects using multipart upload (`Amazon S3`)

> **Nguồn (AWS official):** https://docs.aws.amazon.com/AmazonS3/latest/userguide/mpuoverview.html
> **Tuần:** 4 — `API Gateway` + `S3` (góc Developer) · **Loại:** AWS Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)
- `multipart upload` = chia object thành **nhiều part**, upload **song song / theo thứ tự bất kỳ**, S3 ghép lại. **Best practice khi object ≥ 100 MB**. Lợi ích: throughput cao (upload song song), phục hồi nhanh khi lỗi mạng (chỉ retry part hỏng), pause/resume, upload khi chưa biết kích thước cuối.
- Quy trình **3 bước**: (1) `CreateMultipartUpload` → nhận **upload ID**; (2) `UploadPart` nhiều lần; (3) `CompleteMultipartUpload`. Muốn huỷ → `AbortMultipartUpload` (action `s3:AbortMultipartUpload`).
- ⚠️ Số liệu HAY THI: **part number từ 1 đến 10.000**; mỗi lần `ListParts`/`ListMultipartUploads` trả tối đa **1.000** phần tử. Ví dụ file 100 GB, part 100 MB → **1.002 API call** (1 create + 1000 upload + 1 complete).
- Part number **không cần liên tiếp** (trừ khi dùng **Checksums** thì phải liên tiếp bắt đầu từ 1, nếu không → **HTTP 500 Internal Server error**). Upload lại cùng part number → **ghi đè** part cũ.
- Bạn phải **tự lưu part number + ETag** của mỗi part để đưa vào request Complete. **KHÔNG** dùng kết quả `ListParts` để complete. Object hoàn tất có 1 ETag = "checksum of checksums" (không phải MD5 của object).
- ⚠️ Chi phí (bẫy): sau khi khởi tạo, các part **vẫn bị tính phí lưu trữ** cho tới khi bạn **Complete hoặc Abort**. Không có expiry tự động → nên đặt **lifecycle rule `AbortIncompleteMultipartUpload`** để xoá multipart dở dang.
- Khi bucket bật **Versioning**: complete multipart luôn tạo **version mới**; nếu nhiều multipart cùng key thì version hiện hành = cái **khởi tạo (createdDate) gần nhất**.
- Có thể dùng **conditional write** trên `PutObject`/`CompleteMultipartUpload` để tránh ghi đè object cùng key.

---

## 📄 Nội dung (trích từ tài liệu gốc)

# Uploading and copying objects using multipart upload in Amazon S3

Multipart upload allows you to upload a single object to Amazon S3 as a set of parts. Each part is a contiguous portion of the object's data. You can upload these object parts independently, and in any order. If transmission of any part fails, you can retransmit that part without affecting other parts. After all parts of your object are uploaded, Amazon S3 assembles them to create the object. **It's a best practice to use multipart upload for objects that are 100 MB or larger** instead of uploading them in a single operation.

Advantages:
- **Improved throughput** – upload parts in parallel.
- **Quick recovery from any network issues** – smaller part size minimizes the impact of restarting a failed upload.
- **Pause and resume object uploads** – after you initiate a multipart upload, there is no expiry; you must explicitly complete or stop the multipart upload.
- **Begin an upload before you know the final object size**.

Recommended usage:
- Over a stable high-bandwidth network, use multipart upload to maximize bandwidth via parallel part uploads.
- Over a spotty network, use multipart upload to increase resiliency; you only retry interrupted parts, not restart from the beginning.

## Multipart upload process

Three-step process: initiate the upload, upload the object parts, and complete the multipart upload.

**Multipart upload initiation** – specify a checksum type. S3 returns an **upload ID** (unique identifier), required when you upload parts, list parts, complete, or stop an upload. Provide metadata in the initiate request. Anonymous users cannot initiate multipart uploads.

**Parts upload** – specify a **part number (between 1 and 10,000)** in addition to the upload ID. The part number uniquely identifies a part and its position; it doesn't need to be consecutive (e.g., 1, 5, and 14). Uploading a new part with the same part number as a previous part **overwrites** the previous part. For each part upload, record the **part number and the ETag value** — you must include these in the complete request. Each part has its own ETag; once complete and consolidated, all parts belong to one ETag as a checksum of checksums.

**Important:** After you initiate a multipart upload and upload one or more parts, you must either complete or stop the upload to stop incurring charges for storage of the uploaded parts. After stopping, you can't upload any part using that upload ID again.

**Multipart upload completion** – S3 concatenates parts in ascending order by part number. Your complete request must include the upload ID and a list of part numbers and their corresponding ETag values. The response ETag uniquely identifies the combined object data (not necessarily an MD5 hash). Full-object checksum is validated server-side; mismatch → `BadDigest` error.

**Sample multipart upload calls** – For a 100 GB file: **1,002 API calls total** = one `CreateMultipartUpload` + **1,000** `UploadPart` calls (each 100 MB) + one `CompleteMultipartUpload`.

**Multipart upload listings** – `ListParts` returns up to **1,000 parts** per request; `ListMultipartUploads` returns at most **1,000** in-progress uploads per request. An in-progress multipart upload is one you have initiated but not completed or stopped.

**Important:** Do not use the result of listing when sending a complete request. Maintain your own list of part numbers and corresponding ETag values.

## Checksums with multipart upload operations

By default the AWS SDK and S3 console use an algorithm for all uploads. If an uploaded object doesn't have a specified checksum (older SDK), S3 automatically uses **CRC-64/NVME (`CRC64NVME`)**.

**Important:** If you're using a multipart upload with Checksums, the part numbers must be **consecutive and begin with 1**. Otherwise, completing with nonconsecutive part numbers generates an **`HTTP 500 Internal Server` error**.

Three APIs perform the multipart upload: `CreateMultipartUpload`, `UploadPart`, `CompleteMultipartUpload`. Checksum types: **Full object** (CRC64NVME, CRC32, CRC32C) and **Composite** (CRC32, CRC32C, SHA-1, SHA-256, MD5, XXHash64/3/128, SHA-512).

## Concurrent multipart upload operations

Multiple multipart uploads can use the same object key. When Versioning is enabled, completing a multipart upload always creates a new version; the current version is determined by which upload **started most recently (`createdDate`)**. Example: a request started at 11:00 AM becomes the current version over one started at 10:00 AM, even if the 10:00 AM upload completes later. For non-versioned buckets, another request received between initiate and complete might take precedence.

## Prevent uploading objects with identical key names during multipart upload

Use a **conditional write** on upload operations to check for existence before creating; validates no existing object with the same key. Supported for `PutObject` or `CompleteMultipartUpload`.

## Multipart upload and pricing

After you initiate a multipart upload, S3 retains all parts until you complete or stop the upload. You are billed for all storage, bandwidth, and requests for the multipart upload and its parts. Parts are billed at the storage class specified at upload (Glacier Flexible Retrieval / Deep Archive parts billed as staging storage at S3 Standard rates until complete). If you stop the upload, S3 deletes artifacts and parts; no early delete charges for incomplete multipart uploads regardless of storage class.

**Note:** To minimize storage costs, configure a lifecycle rule to delete incomplete multipart uploads after a specified number of days using the **`AbortIncompleteMultipartUpload`** action.

## API / CLI / SDK support

REST API operations: `CreateMultipartUpload`, `UploadPart`, `UploadPartCopy`, `CompleteMultipartUpload`, `AbortMultipartUpload`, `ListParts`, `ListMultipartUploads`.

## Multipart upload API and permissions

| Action | Required permissions |
| --- | --- |
| Create / Initiate Multipart Upload | `s3:PutObject` |
| Upload Part | `s3:PutObject` |
| Upload Part (Copy) | `s3:PutObject` + `s3:GetObject` on the source object |
| Complete Multipart Upload | `s3:PutObject` |
| Stop (Abort) Multipart Upload | `s3:AbortMultipartUpload` (bucket owner + initiator by default) |
| List Parts | `s3:ListMultipartUploadParts` |
| List Multipart Uploads | `s3:ListBucketMultipartUploads` |
| AWS KMS encrypt/decrypt (SSE-KMS) | `kms:Decrypt` (and related) — S3 must decrypt encrypted parts before completing |
| SSE-C | Must provide the SSE-C key on `CompleteMultipartUpload`, or the object is created without a checksum |

Related: `AbortIncompleteMultipartUpload` lifecycle configuration, Amazon S3 multipart upload limits (part number 1–10,000).
