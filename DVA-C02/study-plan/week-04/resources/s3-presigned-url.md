# Download and upload objects with presigned URLs (`Amazon S3`)

> **Nguồn (AWS official):** https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html
> **Tuần:** 4 — `API Gateway` + `S3` (góc Developer) · **Loại:** AWS Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)
- `presigned URL` = cấp quyền truy cập object **có giới hạn thời gian** mà **KHÔNG cần sửa bucket policy** và **không cần chia credential AWS** cho bên nhận. Dùng `GET` để download, **`PUT` để upload**, `HEAD` đọc metadata.
- ⚠️ CỰC HAY THI: URL **kế thừa quyền của IAM principal đã tạo ra nó**. Người tạo phải có quyền thực hiện thao tác đó (vd `s3:GetObject`) thì URL mới dùng được. presigned URL là **bearer token** — ai cầm cũng dùng được trong hạn.
- **Hạn dùng (bẫy số liệu):**
  - Console: từ **1 phút đến 12 giờ**.
  - AWS CLI / SDK: tối đa **7 ngày** (với **SigV4** + IAM user credentials).
  - **Temporary credentials** (STS AssumeRole, IAM role, EC2 instance profile): URL **hết hạn khi credential hết hạn**, dù bạn đặt thời gian dài hơn. STS AssumeRole mặc định **1 giờ**; EC2 instance profile / role tối đa **~6 giờ**.
- Có thể tạo URL nhiều lần dùng được **tới thời điểm hết hạn**. S3 kiểm hạn tại **thời điểm gửi request**: đang tải file lớn mà quá hạn thì vẫn tải xong; nhưng nếu **rớt mạng rồi restart sau hạn** thì fail.
- Giới hạn quyền URL: dùng bucket policy với condition **`s3:signatureAge`** (chặn nếu signature quá cũ, vd > 10 phút = `600000` ms) hoặc network path (`aws:SourceIp`, `aws:SourceVpc`, `aws:SourceVpce`).
- Lỗi hay gặp: **403 Forbidden** (thiếu quyền `s3:GetObject` hoặc bucket policy deny); **`ExpiredToken`** (credential tạo URL đã hết hạn); **`SignatureDoesNotMatch`** (lệch đồng hồ NTP / proxy sửa header).

---

## 📄 Nội dung (trích từ tài liệu gốc)

# Download and upload objects with presigned URLs

You can use presigned URLs to grant time-limited access to objects in Amazon S3 without updating your bucket policy. A presigned URL can be entered in a browser or used by a program to download an object. The credentials used by the presigned URL are those of the AWS Identity and Access Management (IAM) principal who generated the URL.

You can also use presigned URLs to allow someone to upload a specific object to your Amazon S3 bucket. This allows an upload without requiring another party to have AWS security credentials or permissions. If an object with the same key already exists in the bucket as specified in the presigned URL, Amazon S3 replaces the existing object with the uploaded object.

You can use the presigned URL multiple times, up to the expiration date and time.

When you create a presigned URL, you must provide your security credentials, and then specify the following:
- An Amazon S3 bucket
- An object key (if downloading this object will be in your Amazon S3 bucket, if uploading this is the file name to be uploaded)
- An HTTP method (`GET` for downloading objects, `PUT` for uploading, `HEAD` for reading object metadata, etc)
- An expiration time interval

When using presigned URLs to upload objects, you can verify object integrity using checksums. Presigned URLs created with AWS Signature Version 2 only support MD5 checksums; presigned URLs created with AWS Signature Version 4 support additional algorithms including CRC-64/NVME, CRC32, CRC32C, SHA-1, SHA-256, MD5, XXHash64, XXHash3, XXHash128, and SHA-512.

## Who can create a presigned URL

Anyone with valid security credentials can create a presigned URL. But for someone to successfully access an object, the presigned URL must be created by someone who has permission to perform the operation that the presigned URL is based upon.

Types of credentials you can use to create a presigned URL:
- **IAM user** – Valid up to **7 days** when you're using AWS Signature Version 4. To create a presigned URL valid for up to 7 days, first delegate IAM user credentials (access key and secret key) to the method you're using to create the presigned URL.
- **Temporary security credentials** – Can't be valid for longer than the credentials themselves. These include:
  - **IAM role credentials** – The presigned URL expires when the role session expires, even if you specify a longer expiration time.
  - **IAM role credentials used by Amazon EC2 instances** – Valid for the duration of the role credentials (typically **6 hours**).
  - **AWS Security Token Service credentials** – Valid only for the duration of the temporary credentials.

**Note:** If you created a presigned URL using a temporary credential, the URL expires when the credential expires. In general, a presigned URL expires when the credential you used to create it is revoked, deleted, or deactivated — this is true even if the URL was created with a later expiration time.

## Expiration time for presigned URLs

A presigned URL remains valid for the period of time specified when the URL is generated. If you create a presigned URL with the Amazon S3 console, the expiration time can be set between **1 minute and 12 hours**. If you use the AWS CLI or AWS SDKs, the expiration time can be set as high as **7 days**.

If you created a presigned URL by using a temporary token, then the URL expires when the token expires.

Amazon S3 checks the expiration date and time of a signed URL at the time of the HTTP request. For example, if a client begins to download a large file immediately before the expiration time, the download continues even if the expiration time passes during the download. However, if the connection drops and the client tries to restart the download after the expiration time passes, the download fails.

## Limiting presigned URL capabilities

The capabilities of a presigned URL are limited by the permissions of the user who created it. Presigned URLs are bearer tokens that grant access to those who possess them — protect them appropriately.

**AWS Signature Version 4 (SigV4)** — use condition keys in bucket/access point policies. Example: deny any presigned URL request if the signature is more than 10 minutes old using `s3:signatureAge`:

```json
{
    "Version":"2012-10-17",
    "Statement": [
        {
            "Sid": "Deny a presigned URL request if the signature is more than 10 min old",
            "Effect": "Deny",
            "Principal": { "AWS": "*" },
            "Action": "s3:*",
            "Resource": "arn:aws:s3:::amzn-s3-demo-bucket/*",
            "Condition": {
                "NumericGreaterThan": { "s3:signatureAge": "600000" }
            }
        }
    ]
}
```

**Network path restriction** — write IAM policies on the principal, bucket, or both. Use `aws:SourceIp` for the public endpoint; use `aws:SourceVpc` or `aws:SourceVpce` for a VPC endpoint.

```json
{
    "Sid": "NetworkRestrictionForIAMPrincipal",
    "Effect": "Deny",
    "Action": "*",
    "Resource": "*",
    "Condition": {
        "NotIpAddressIfExists": {"aws:SourceIp": "IP-address-range"},
        "BoolIfExists": {"aws:ViaAWSService": "false"}
    }
}
```

## Frequently asked questions for presigned URLs

**Q: Why do my presigned URLs expire earlier than the configured expiration time?**
Presigned URLs remain valid only while their underlying credentials are valid. A presigned URL expires at either its configured expiration time or when its associated credentials expire, whichever occurs first. For ECS tasks/containers, role credentials typically rotate every 1-6 hours. With STS AssumeRole, the URL expires when the role session ends (default 1 hour). For EC2 instance profiles, metadata credentials rotate periodically with a maximum validity of approximately 6 hours.

**Q: Why am I getting a 403 Forbidden error when accessing a presigned URL?**
Verify permissions before generating. The IAM user or role generating the URL must have the required permissions, such as `s3:GetObject`. Also check that the S3 bucket policy doesn't explicitly deny access.

**Q: Why am I getting an `AccessDenied` error with `HeadersNotSigned: if-range`?**
When `Range` is in `X-Amz-SignedHeaders`, S3 requires `If-Range` also be signed if present. Add `If-Range` to `X-Amz-SignedHeaders` when generating the URL.

**Q: I'm getting `SignatureDoesNotMatch` errors.**
Ensure system clock is synchronized with NTP; corporate proxies might modify headers/query strings; verify all request parameters (HTTP method, headers, query string) match exactly between URL generation and usage.

**Q: I'm getting `ExpiredToken` errors.**
The AWS credentials used to generate the URL are no longer valid. Refresh credentials before generating new URLs; implement credential refresh logic for long-running apps; verify STS AssumeRole session duration meets your needs.
