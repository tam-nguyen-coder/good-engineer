# Question #506 - Topic 1

A social media company is building a feature for its website. The feature will give users the ability to upload photos. The company expects significant increases in demand during large events and must ensure that the website can handle the upload traffic from users. Which solution meets these requirements with the MOST scalability?

## Options

**A.** Upload files from the user's browser to the application servers. Transfer the files to an Amazon S3 bucket.

**B.** Provision an AWS Storage Gateway file gateway. Upload files directly from the user's browser to the file gateway.

**C.** Generate Amazon S3 presigned URLs in the application. Upload files directly from the user's browser into an S3 bucket.

**D.** Provision an Amazon Elastic File System (Amazon EFS) file system. Upload files directly from the user's browser to the file system.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Social media website cần tính năng upload photos. Demand tăng đột biến trong các sự kiện lớn.
- **Existing Resources:** Website application.
- **Current Issue/Goal:** Upload nhiều photos cùng lúc, scalability cao nhất.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `significant increases in demand during large events` | Cần giải pháp scale ngang không giới hạn. |
| `MOST scalability` | Offload upload traffic khỏi application servers. |
| `upload photos` | Object storage (S3) là lựa chọn phù hợp cho file upload. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most scalability
- **Constraints:** Unpredictable spikes, photo uploads

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- Presigned URL: application server tạo URL có thời hạn cho phép browser upload trực tiếp lên S3 mà không qua application server.
- Giải pháp này offload hoàn toàn upload traffic khỏi compute tier → application server không bị ảnh hưởng bởi số lượng/lưu lượng upload.
- S3 scale vô hạn, không cần provisioning trước.
- Presigned URL pattern là best practice cho direct-to-S3 upload.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Upload qua application server tạo bottleneck. Server phải nhận file rồi mới transfer lên S3 → tốn bandwidth, CPU, memory.
- Khi có spike, server dễ bị quá tải. Không scalable.

**❌ Đáp án B:**
- Storage Gateway File Gateway dùng cho hybrid cloud (on-prem → AWS), không phải cho browser upload.
- Browser không thể upload trực tiếp vào File Gateway.

**❌ Đáp án D:**
- EFS là file system dùng cho EC2, không phải cho browser upload trực tiếp.
- Không có API endpoint cho browser upload.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Direct upload → S3 presigned URL. Không qua application server → scalable vô hạn."*
