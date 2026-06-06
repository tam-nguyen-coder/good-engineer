# Question #611 - Topic 1

A company has an application with a REST-based interface that allows data to be received in near-real time from a third-party vendor. Once received, the application processes and stores the data for further analysis. The application is running on Amazon EC2 instances. The third-party vendor has received many 503 Service Unavailable Errors when sending data to the application. When the data volume spikes, the compute capacity reaches its maximum limit and the application is unable to process all requests. Which design should a solutions architect recommend to provide a more scalable solution?

## Options

**A.** Use Amazon Kinesis Data Streams to ingest the data. Process the data using AWS Lambda functions.

**B.** Use Amazon API Gateway on top of the existing application. Create a usage plan with a quota limit for the third-party vendor.

**C.** Use Amazon Simple Notification Service (Amazon SNS) to ingest the data. Put the EC2 instances in an Auto Scaling group behind an Application Load Balancer.

**D.** Repackage the application as a container. Deploy the application using Amazon Elastic Container Service (Amazon ECS) using the EC2 launch type with an Auto Scaling group.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** REST API nhận near-real time data từ third-party vendor. Gặp 503 errors khi data volume spikes vì compute capacity max out.
- **Existing Resources:** Amazon EC2 instances.
- **Current Issue/Goal:** Giải quyết scalability khi data volume tăng đột biến.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `503 Service Unavailable` | Backend không đủ capacity → cần decouple ingestion và processing. |
| `data volume spikes` | Lưu lượng không ổn định, cần buffer. |
| `near-real time` | Cần xử lý gần real-time. |
| `Kinesis Data Streams` | Dịch vụ streaming data, có thể buffer và scale ingestion. |
| `Lambda` | Serverless compute, auto-scale để xử lý data từ Kinesis. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Scalable solution
- **Constraints:** Near-real time, handle spikes, REST-based interface

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- Kinesis Data Streams: ingestion layer có thể buffer spikes và scale shards để tăng throughput.
- Lambda: auto-scale dựa trên số lượng records trong stream, xử lý data gần real-time.
- Decouple ingestion (Kinesis) khỏi processing (Lambda) → giải quyết triệt để vấn đề 503 khi spike.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- API Gateway + usage plan với quota limit → giới hạn số lượng requests, không giải quyết scalability.
- Spikes vẫn gây 503 nếu backend không scale kịp.

**❌ Đáp án C:**
- SNS + EC2 Auto Scaling + ALB: SNS không có buffer (push-based), nếu EC2 không kịp xử lý → messages bị mất.
- Không có persistent buffer như Kinesis.

**❌ Đáp án D:**
- ECS with EC2 launch type + Auto Scaling: vẫn cần giải quyết vấn đề decoupling ingestion và processing.
- Chỉ thay đổi deployment platform, không giải quyết root cause.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Data spikes + near-real time → Kinesis (buffer) + Lambda (auto-scale). SNS không có buffer."*
