# Question #103 - Topic 1

A company has an AWS Glue extract, transform, and load (ETL) job that runs every day at the same time. The job processes XML data that is in an Amazon S3 bucket. New data is added to the S3 bucket every day. A solutions architect notices that AWS Glue is processing all the data during each run. What should the solutions architect do to prevent AWS Glue from reprocessing old data?

## Options

**A.** Edit the job to use job bookmarks.

**B.** Edit the job to delete data after the data is processed.

**C.** Edit the job by setting the NumberOfWorkers field to 1.

**D.** Use a FindMatches machine learning (ML) transform.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** AWS Glue ETL job chạy daily, xử lý XML từ S3. New data added daily.
- **Existing Resources:** AWS Glue job, S3 bucket.
- **Current Issue/Goal:** Glue xử lý lại tất cả data mỗi lần chạy — cần incremental processing.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `processing all the data during each run` | Cần **job bookmarks** để track vị trí đã xử lý |
| `new data is added every day` | Incremental processing |
| `prevent reprocessing old data` | Chỉ xử lý dữ liệu mới |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** ETL / Data processing
- **Constraints:** Incremental processing, Glue

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- **AWS Glue job bookmarks** — track dữ liệu đã được xử lý, chỉ xử lý dữ liệu mới trong lần chạy tiếp theo.
- Lưu trạng thái processed data, tự động skip old data.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Delete data sau khi process — nguy hiểm, mất data gốc, không phải best practice.

**❌ Đáp án C:**
- NumberOfWorkers = 1 — chỉ giảm parallelism, không ngăn reprocessing.

**❌ Đáp án D:**
- **FindMatches ML transform** — dùng để deduplicate/fuzzy matching, không phải incremental processing.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Job bookmarks = incremental processing (chỉ xử lý data mới). FindMatches = deduplication"*
