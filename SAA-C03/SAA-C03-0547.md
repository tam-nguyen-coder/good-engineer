# Question #547 - Topic 1

A company has data collection sensors at different locations. The data collection sensors stream a high volume of data to the company. The company wants to design a platform on AWS to ingest and process high-volume streaming data. The solution must be scalable and support data collection in near real time. The company must store the data in Amazon S3 for future reporting. Which solution will meet these requirements with the LEAST operational overhead?

## Options

**A.** Use Amazon Kinesis Data Firehose to deliver streaming data to Amazon S3.

**B.** Use AWS Glue to deliver streaming data to Amazon S3.

**C.** Use AWS Lambda to deliver streaming data and store the data to Amazon S3.

**D.** Use AWS Database Migration Service (AWS DMS) to deliver streaming data to Amazon S3.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Công ty có sensors thu thập dữ liệu từ nhiều địa điểm, stream lượng lớn dữ liệu. Cần ingest và process high-volume streaming data, lưu vào S3 cho future reporting.
- **Existing Resources:** Sensors, data stream.
- **Current Issue/Goal:** Giải pháp scalable, near real-time, lưu S3, ít operational overhead nhất.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `streaming data` | Dữ liệu stream liên tục |
| `high volume` | Lượng dữ liệu lớn |
| `near real time` | Gần như thời gian thực |
| `store the data in Amazon S3` | Đích đến là S3 |
| `LEAST operational overhead` | Giải pháp managed, ít cấu hình nhất |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Least operational overhead
- **Constraints:** Scalable, near real-time, lưu S3, high-volume

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- Amazon Kinesis Data Firehose là dịch vụ fully managed để load streaming data vào S3 (và các đích khác).
- Không cần quản lý infrastructure, tự động scale theo dung lượng dữ liệu.
- Firehose có thể buffer, transform, nén, và ghi dữ liệu vào S3 theo batch với độ trễ thấp (60-900 giây).
- Tích hợp sẵn với S3, không cần code.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B (AWS Glue):** AWS Glue là ETL service cho batch processing, không phải streaming. Glue có thể xử lý dữ liệu trong S3 nhưng không phải để ingest streaming data.

**❌ Đáp án C (Lambda):** Lambda có thể xử lý streaming data (qua Kinesis Data Streams trigger), nhưng không tối ưu cho high-volume streaming. Lambda có giới hạn concurrency, duration, và payload size. Operational overhead cao hơn Firehose.

**❌ Đáp án D (DMS):** AWS Database Migration Service dùng để migrate database, không phải để ingest streaming data từ sensors.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Streaming data → S3 = Kinesis Data Firehose. Fully managed, auto-scale, no code needed."*
