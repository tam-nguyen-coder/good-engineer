# Question #568 - Topic 1

A solutions architect is designing the storage architecture for a new web application used for storing and viewing engineering drawings. All application components will be deployed on the AWS infrastructure. The application design must support caching to minimize the amount of time that users wait for the engineering drawings to load. The application must be able to store petabytes of data. Which combination of storage and caching should the solutions architect use?

## Options

**A.** Amazon S3 with Amazon CloudFront

**B.** Amazon S3 Glacier with Amazon ElastiCache

**C.** Amazon Elastic Block Store (Amazon EBS) volumes with Amazon CloudFront

**D.** AWS Storage Gateway with Amazon ElastiCache

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Web application lưu và xem engineering drawings. Cần caching để giảm thời gian load. Cần lưu trữ petabytes dữ liệu.
- **Existing Resources:** Chưa có.
- **Current Issue/Goal:** Petabyte-scale storage + caching.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `petabytes of data` | Cần storage có khả năng mở rộng đến petabyte scale |
| `caching` | Giảm latency cho users |
| `engineering drawings` | Dạng files (hình ảnh kỹ thuật) – có thể cache bằng CDN |
| `Amazon S3` | Object storage, petabyte scale, giá rẻ |
| `Amazon CloudFront` | CDN, caching at edge locations |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most appropriate solution
- **Constraints:** Petabytes storage, caching for fast load

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- Amazon S3: object storage có thể lưu trữ petabytes dữ liệu, chi phí thấp, độ bền cao (11 9s). Phù hợp cho engineering drawings (files).
- Amazon CloudFront: CDN toàn cầu, cache nội dung tại các edge locations gần người dùng. Giảm thời gian tải drawings (caching).
- Kết hợp S3 (origin) + CloudFront (CDN) là pattern chuẩn cho phân phối nội dung tĩnh.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B (S3 Glacier + ElastiCache):** S3 Glacier là archive storage, không thiết kế cho truy cập thường xuyên (retrieval time từ phút đến giờ). Không thể dùng làm primary storage cho web application. ElastiCache không thể cache petabytes từ Glacier.

**❌ Đáp án C (EBS + CloudFront):** EBS volumes không thể scale đến petabytes (tối đa 16 TB/volume). EBS gắn với một EC2 instance, không phải là shared storage. CloudFront không thể lấy origin từ EBS trực tiếp.

**❌ Đáp án D (Storage Gateway + ElastiCache):** Storage Gateway là hybrid storage (on-prem → cloud), không phải là primary storage cho web application trên AWS. ElastiCache có kích thước giới hạn (không thể cache petabytes).

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Petabytes + caching = S3 + CloudFront. S3 = scalable object storage. CloudFront = edge caching."*
