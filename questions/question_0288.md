# Question #288 - Topic 1

A company is migrating a Linux-based web server group to AWS. The web servers must access files in a shared file store for some content. The company must not make any changes to the application. What should a solutions architect do to meet these requirements?

## Options

**A.** Create an Amazon S3 Standard bucket with access to the web servers.

**B.** Configure an Amazon CloudFront distribution with an Amazon S3 bucket as the origin.

**C.** Create an Amazon Elastic File System (Amazon EFS) file system. Mount the EFS file system on all web servers.

**D.** Configure a General Purpose SSD (gp3) Amazon Elastic Block Store (Amazon EBS) volume. Mount the EBS volume to all web servers.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Linux web servers cần shared file store. No app changes allowed.
- **Existing Resources:** Linux web servers (migrating to AWS).
- **Current Issue/Goal:** Shared file storage cho Linux servers, không sửa code.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `Linux-based web server` | Cần NFS-compatible storage. |
| `shared file store` | Nhiều server cùng truy cập một file system. |
| `must not make any changes to the application` | Phải dùng standard file system API (POSIX), không thể dùng S3 SDK. |
| `Amazon EFS` | Managed NFS file system, có thể mount trên nhiều Linux EC2 instances. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Which solution meets requirements
- **Constraints:** No code changes, Linux, shared access

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- EFS là managed NFS (Network File System) cho Linux, có thể mount đồng thời lên nhiều EC2 instances.
- Sử dụng file system API tiêu chuẩn (POSIX) → application không cần thay đổi code.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- S3 không support standard file system API (POSIX). Để truy cập S3 cần SDK hoặc CLI → phải thay đổi code.

**❌ Đáp án B:**
- CloudFront là CDN, không phải shared file store. Chỉ dùng cache và phân phối nội dung tĩnh.

**❌ Đáp án D:**
- EBS volume chỉ attach được 1 EC2 instance tại một thời điểm (trừ multi-attach EBS cho một số loại đặc biệt như io1/io2 với giới hạn).

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Linux + shared file store + no code change → EFS (NFS). EBS = 1 instance. S3 = cần SDK."*
