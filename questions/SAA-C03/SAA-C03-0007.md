# Question #7 - Topic 1

A company has an application that ingests incoming messages. Dozens of other applications and microservices then quickly consume these messages. The number of messages varies drastically and sometimes increases suddenly to 100,000 each second. The company wants to decouple the solution and increase scalability. Which solution meets these requirements?

## Options

**A.** Persist the messages to Amazon Kinesis Data Analytics. Configure the consumer applications to read and process the messages.

**B.** Deploy the ingestion application on Amazon EC2 instances in an Auto Scaling group to scale the number of EC2 instances based on CPU metrics.

**C.** Write the messages to Amazon Kinesis Data Streams with a single shard. Use an AWS Lambda function to preprocess messages and store them in Amazon DynamoDB. Configure the consumer applications to read from DynamoDB to process the messages.

**D.** Publish the messages to an Amazon Simple Notification Service (Amazon SNS) topic with multiple Amazon Simple Queue Service (Amazon SOS) subscriptions. Configure the consumer applications to process the messages from the queues.



## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Một ứng dụng nhận (`ingests`) message đầu vào. Hàng chục ứng dụng và microservice khác cần tiêu thụ (`consume`) các message này một cách nhanh chóng.
- **Existing Resources:** Không có tài nguyên cụ thể nào được đề cập; cần thiết kế kiến trúc mới.
- **Current Issue/Goal:** Lưu lượng message biến động mạnh, đột biến lên đến 100,000 message/giây. Công ty muốn `decouple` (tách rời) giải pháp và tăng khả năng mở rộng (`scalability`).

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa |
|---------|---------|
| `ingests incoming messages` | Tầng nhận dữ liệu đầu vào, vai trò producer |
| `dozens of other applications and microservices` | Nhiều consumer độc lập → pattern phân phối fan-out |
| `varies drastically` | Lưu lượng không ổn định, khó dự đoán |
| `100,000 each second` | Throughput cực cao, yêu cầu dịch vụ có khả năng scale gần như không giới hạn |
| `decouple` | Tách biệt producer khỏi consumer, tránh phụ thuộc trực tiếp |
| `increase scalability` | Cần tự động mở rộng để đáp ứng spike mà không bị mất message |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Lựa chọn kiến trúc tối ưu (Architecture Design)
- **Constraints:** 
  - Phải `decouple` hoàn toàn giữa ingestion và consumption.
  - Hỗ trợ throughput rất cao và đột biến (100,000 msg/s).
  - Một producer, nhiều consumer (fan-out).

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**
**Giải thích:** 
- `Amazon SNS` (Standard Topic) hỗ trợ throughput gần như không giới hạn, dễ dàng xử lý spike 100,000 message/giây.
- Kết hợp với nhiều `Amazon SQS` queues (qua `SNS topic subscriptions`) tạo thành pattern **fan-out** kinh điển: mỗi microservice/ứng dụng consumer có một hàng đợi riêng, đảm bảo message được phân phối đến tất cả consumer.
- `SQS` đóng vai trò buffer (đệm), giúp consumer xử lý message theo tốc độ của riêng mình mà không ảnh hưởng đến producer hay các consumer khác.
- Giải pháp này hoàn toàn `decoupled`, `serverless`, và tự động scale.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:** `Amazon Kinesis Data Analytics` là dịch vụ xử lý và phân tích dữ liệu streaming bằng SQL hoặc Apache Flink, **không phải** nơi lưu trữ persistence để các ứng dụng consumer trực tiếp đọc message từ đó. Consumer không thể "đọc" từ Data Analytics như một message broker.

**❌ Đáp án B:** Triển khai ingestion trên `EC2` với `Auto Scaling group` chỉ scale tầng nhận message, hoàn toàn **không giải quyết được việc decouple** producer với consumer. Các microservice vẫn phụ thuộc trực tiếp vào ingestion layer, và việc scale dựa trên CPU không đảm bảo xử lý được spike 100,000 msg/s một cách hiệu quả.

**❌ Đáp án C:** `Amazon Kinesis Data Streams` với **single shard** có giới hạn throughput rất thấp (tối đa 1 MB/giây hoặc 1,000 records/giây cho write), hoàn toàn **không đủ** cho 100,000 message/giây. Ngoài ra, thêm bước `Lambda` + `DynamoDB` tạo ra độ trễ và chi phí không cần thiết, trong khi đề bài chỉ yêu cầu các consumer nhanh chóng nhận và xử lý message.

## 6. MẸO GHI NHỚ
🧠 *Khi đề bài xuất hiện: 1 producer + Nhiều consumer + Decouple + Spike traffic → Nghĩ ngay đến `SNS` + `SQS` (fan-out pattern).*
🧠 *`Kinesis Data Streams` dùng cho real-time analytics/aggregation, nhưng cần nhiều shard để scale; `single shard` là red flag cho throughput cao.*
🧠 *`Kinesis Data Analytics` = xử lý dữ liệu (process), không phải message broker để lưu trữ và phân phối.*


