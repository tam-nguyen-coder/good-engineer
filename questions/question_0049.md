# Question #49 - Topic 1

A company stores call transcript files on a monthly basis. Users access the files randomly within 1 year of the call, but users access the files infrequently after 1 year. The company wants to optimize its solution by giving users the ability to query and retrieve files that are less than 1-year- old as quickly as possible. A delay in retrieving older files is acceptable. Which solution will meet these requirements MOST cost-effectively?

## Options

**A.** Store individual files with tags in Amazon S3 Glacier Instant Retrieval. Query the tags to retrieve the files from S3 Glacier Instant Retrieval.

**B.** Store individual files in Amazon S3 Intelligent-Tiering. Use S3 Lifecycle policies to move the files to S3 Glacier Flexible Retrieval after 1 year. Query and retrieve the files that are in Amazon S3 by using Amazon Athena. Query and retrieve the files that are in S3 Glacier by using S3 Glacier Select.

**C.** Store individual files with tags in Amazon S3 Standard storage. Store search metadata for each archive in Amazon S3 Standard storage. Use S3 Lifecycle policies to move the files to S3 Glacier Instant Retrieval after 1 year. Query and retrieve the files by searching for metadata from Amazon S3.

**D.** Store individual files in Amazon S3 Standard storage. Use S3 Lifecycle policies to move the files to S3 Glacier Deep Archive after 1 year. Store search metadata in Amazon RDS. Query the files from Amazon RDS. Retrieve the files from S3 Glacier Deep Archive.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Công ty lưu trữ file ghi âm cuộc gọi theo tháng. File < 1 năm được truy cập thường xuyên (random), file > 1 năm ít được truy cập.
- **Existing Resources:** Chưa có hạ tầng lưu trữ cụ thể.
- **Current Issue/Goal:** Tối ưu chi phí: truy vấn nhanh file < 1 năm, chấp nhận chậm cho file > 1 năm.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `most cost-effectively` | Ưu tiên chi phí thấp nhất có thể |
| `query and retrieve files < 1 year as quickly as possible` | Cần query nhanh trên S3 (Athena) |
| `delay in retrieving older files is acceptable` | File > 1 năm có thể chuyển sang storage rẻ hơn, chậm hơn |
| `access files infrequently after 1 year` | Phù hợp Glacier Flexible Retrieval (không cần Instant) |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most cost-effective
- **Constraints:** Query nhanh file < 1 tuổi, chậm hơn cho file cũ hơn

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- **S3 Intelligent-Tiering** tự động tối ưu chi phí khi access pattern không xác định — file < 1 năm được truy cập random, phù hợp.
- **S3 Lifecycle** chuyển file > 1 năm xuống **S3 Glacier Flexible Retrieval** — chi phí thấp, chấp nhận độ trễ khi retrieve.
- **Amazon Athena** query trực tiếp trên S3 (file < 1 năm) — không cần metadata riêng.
- **S3 Glacier Select** query trên dữ liệu đã archive — tránh phải restore toàn bộ file.
- Đáp án duy nhất tối ưu chi phí cho cả 2 giai đoạn.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- S3 Glacier Instant Retrieval đắt hơn Standard và Intelligent-Tiering.
- Tags trên S3 không phải công cụ query hiệu quả (chỉ filter cơ bản, không phải SQL).

**❌ Đáp án C:**
- Glacier Instant Retrieval sau 1 năm là tốn kém hơn so với Glacier Flexible Retrieval — vì đề đã nói "delay chấp nhận được".
- Duy trì metadata riêng trên S3 Standard phát sinh thêm chi phí lưu trữ.

**❌ Đáp án D:**
- S3 Glacier Deep Archive là rẻ nhất nhưng retrieval có thể mất 12–48 giờ.
- Thêm RDS làm tăng operational overhead và chi phí — không cần thiết khi Athena có thể query S3 trực tiếp.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Intelligent-Tiering cho unknown access pattern + Glacier Flexible Retrieval cho data cũ = cost-effective cho 2 giai đoạn"*
