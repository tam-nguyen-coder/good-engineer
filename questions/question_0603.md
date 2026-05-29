# Question #603 - Topic 1

A company recently migrated to the AWS Cloud. The company wants a serverless solution for large-scale parallel on-demand processing of a semistructured dataset. The data consists of logs, media files, sales transactions, and IoT sensor data that is stored in Amazon S3. The company wants the solution to process thousands of items in the dataset in parallel. Which solution will meet these requirements with the MOST operational efficiency?

## Options

**A.** Use the AWS Step Functions Map state in Inline mode to process the data in parallel.

**B.** Use the AWS Step Functions Map state in Distributed mode to process the data in parallel.

**C.** Use AWS Glue to process the data in parallel.

**D.** Use several AWS Lambda functions to process the data in parallel.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Serverless solution for large-scale parallel on-demand processing của semistructured dataset (logs, media files, sales transactions, IoT sensor data) từ S3. Cần xử lý thousands of items song song.
- **Existing Resources:** Data stored in Amazon S3.
- **Current Issue/Goal:** Large-scale parallel processing với most operational efficiency.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `large-scale parallel` | Cần xử lý hàng ngàn items song song → Step Functions Map Distributed mode (concurrency không giới hạn). |
| `serverless` | Không quản lý infrastructure. |
| `semistructured dataset` | Logs, media, transactions, IoT → có thể xử lý linh hoạt. |
| `thousands of items in parallel` | Inline mode giới hạn 40 concurrent children. Distributed mode không giới hạn. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most operational efficiency
- **Constraints:** Serverless, parallel processing of thousands of items, data in S3

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- Step Functions Map state trong Distributed mode có thể xử lý không giới hạn số lượng items song song.
- Phù hợp với "thousands of items" – Inline mode chỉ hỗ trợ tối đa 40 concurrent children.
- Serverless, pay-per-execution, tích hợp với Lambda và các dịch vụ AWS khác.
- Operational efficiency cao vì Step Functions quản lý hoàn toàn việc điều phối parallel execution.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Inline mode giới hạn 40 concurrent children → không đủ cho thousands of items.

**❌ Đáp án C:**
- AWS Glue là ETL service dùng Apache Spark, phù hợp cho batch processing có cấu trúc.
- Operational overhead cao hơn (cần tạo job, quản lý DPU) và không tối ưu cho on-demand processing không đồng nhất (media files + logs + IoT).

**❌ Đáp án D:**
- "Several Lambda functions" → phải tự code orchestration, error handling, retry logic.
- Operational efficiency thấp hơn Step Functions vì không có built-in orchestration.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Thousands of parallel tasks → Step Functions Map Distributed (unlimited concurrency). Inline = max 40."*
