# Question #45 - Topic 1

A company has a data ingestion workflow that consists of the following: • An Amazon Simple Notification Service (Amazon SNS) topic for notifications about new data deliveries • An AWS Lambda function to process the data and record metadata The company observes that the ingestion workflow fails occasionally because of network connectivity issues. When such a failure occurs, the Lambda function does not ingest the corresponding data unless the company manually reruns the job. Which combination of actions should a solutions architect take to ensure that the Lambda function ingests all data in the future? (Choose two.)

## Options

**A.** Deploy the Lambda function in multiple Availability Zones.

**B.** Create an Amazon Simple Queue Service (Amazon SQS) queue, and subscribe it to the SNS topic.

**C.** Increase the CPU and memory that are allocated to the Lambda function.

**D.** Increase provisioned throughput for the Lambda function.

**E.** Modify the Lambda function to read from an Amazon Simple Queue Service (Amazon SQS) queue.



## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Công ty sở hữu workflow ingest dữ liệu gồm một `Amazon SNS` topic để nhận thông báo khi có dữ liệu mới, và một `AWS Lambda` function để xử lý dữ liệu cùng ghi metadata.
- **Existing Resources:** `SNS` topic, `Lambda` function (được trigger trực tiếp bởi `SNS`).
- **Current Issue/Goal:** Workflow thất bại thỉnh thoảng do lỗi kết nối mạng (network connectivity issues). Khi xảy ra lỗi, `Lambda` không ingest dữ liệu tương ứng trừ khi được rerun thủ công. Yêu cầu là đảm bảo `Lambda` ingest **toàn bộ** dữ liệu trong tương lai mà không cần can thiệp tay.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa |
|---------|---------|
| `Amazon SNS` | Pub/sub notification service. Khi gửi message đến `Lambda` (async), `SNS` chỉ retry giới hạn (2 lần); nếu vẫn lỗi, message có thể bị mất nếu không có `DLQ`. |
| Network connectivity issues | Lỗi kết nối mạng tạm thời khiến `Lambda` không thể xử lý hoặc ghi metadata thành công. |
| `Amazon SQS` | Message queue bền vững, lưu trữ message cho đến khi consumer xử lý thành công và xóa đi, hỗ trợ retry tự động thông qua visibility timeout. |
| Ingest all data | Yêu cầu về **durability** và **reliability**: không được phép mất message, phải tự động retry khi có lỗi tạm thời. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Multiple choice, chọn **2 đáp án** (Combination).
- **Constraints:** Giải pháp phải loại bỏ việc rerun thủ công; phải xử lý được lỗi mạng tạm thời mà không làm mất dữ liệu.

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B và E**

**Giải thích:**  
Kiến trúc hiện tại `SNS` → `Lambda` (trực tiếp) không đảm bảo durability khi `Lambda` gặp lỗi. Để đảm bảo **không mất message** và **tự động retry**, cần đưa `SQS` vào làm buffer bền vững giữa `SNS` và `Lambda`:

- **B:** Tạo `SQS` queue và subscribe queue đó vào `SNS` topic. Khi có thông báo, `SNS` sẽ gửi message vào `SQS`. Message được lưu an toàn trong queue ngay cả khi `Lambda` đang bị lỗi hoặc offline.
- **E:** Sửa đổi `Lambda` function để đọc từ `SQS` queue (sử dụng `Event Source Mapping`). `Lambda` sẽ poll message từ queue. Nếu xử lý thất bại do lỗi mạng, message tự động quay lại queue sau khi `visibility timeout` hết hạn và được retry cho đến khi thành công hoặc chuyển vào `DLQ`. Nhờ đó, không cần rerun thủ công và dữ liệu không bị mất.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:** `AWS Lambda` là dịch vụ regional và đã tự động chạy trên nhiều `Availability Zones`. Bạn không thể "triển khai" `Lambda` vào các AZ cụ thể. Hơn nữa, lỗi connectivity là vấn đề mạng tạm thời, không phải do thiếu AZ.

**❌ Đáp án C:** Tăng CPU và memory cho `Lambda` không giải quyết được lỗi network connectivity. Đây là vấn đề về độ tin cậy (reliability) và durability, không phải thiếu tài nguyên tính toán.

**❌ Đáp án D:** `Lambda` không có khái niệm "provisioned throughput" — đây là thuật ngữ của `DynamoDB` hoặc `EBS`. Ngay cả nếu ám chỉ `provisioned concurrency`, nó chỉ giúp giảm cold start, hoàn toàn không giải quyết việc retry khi lỗi mạng hay đảm bảo không mất message.

## 6. MẸO GHI NHỚ
🧠 *Trong đề thi `SAA-C03`, khi gặp tình huống `SNS` + `Lambda` bị lỗi tạm thời, dẫn đến mất message hoặc phải rerun thủ công → Hãy nghĩ ngay đến pattern **SNS → SQS → Lambda**. `SQS` đóng vai trò buffer bền vững, còn `Event Source Mapping` của `Lambda` tự động quản lý polling, retry và xóa message khi thành công. Đây là best practice cho event-driven architecture cần high reliability.*
