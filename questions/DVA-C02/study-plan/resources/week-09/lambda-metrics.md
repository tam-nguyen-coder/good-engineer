# Using CloudWatch metrics with Lambda

> **Nguồn (AWS official):** https://docs.aws.amazon.com/lambda/latest/dg/monitoring-metrics.html
> **Tuần:** 9 — Observability & Optimization · **Loại:** AWS Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.
>
> ℹ️ Trang gốc là trang tổng quan ngắn; chi tiết từng metric nằm ở trang con **Types of metrics for Lambda functions** (`monitoring-metrics-types.html`). Bảng dưới đây bổ sung các metric hay thi từ trang con đó để học offline đủ ý.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)
- **`Lambda` tự động gửi metric lên `CloudWatch` mỗi 1 phút** khi function xử lý xong event. **Không cần cấp thêm quyền cho execution role**, và **không tính phí** cho các metric mặc định này.
- Các nhóm metric: **invocation, performance, concurrency, asynchronous invocation, event source mapping**.
- Metric mặc định cần thuộc: **`Invocations`**, **`Duration`**, **`Errors`**, **`Throttles`**, **`ConcurrentExecutions`**, và **`IteratorAge`** (chỉ với event source dạng **stream** như `Kinesis`/`DynamoDB Streams` — đo độ trễ xử lý record).
- Muốn insight dưới 1 phút → tự tạo **high-resolution custom metric** (tính phí). Custom metric và CloudWatch alarm đều tính phí.
- `Duration` cao / `Throttles` cao → hướng tối ưu memory (CPU tăng theo tỉ lệ) và **Provisioned Concurrency** cho cold start.

## 📊 Bảng metric `Lambda` hay thi (bổ sung từ trang con `monitoring-metrics-types`)

| Metric | Nhóm | Ý nghĩa |
|---|---|---|
| `Invocations` | Invocation | Số lần function được gọi (thành công + lỗi). |
| `Errors` | Invocation | Số lần gọi trả lỗi do function (lỗi code, timeout). |
| `Throttles` | Invocation | Số lần gọi bị **throttle** (vượt concurrency limit) — KHÔNG tính vào `Errors`. |
| `DeadLetterErrors` / `DestinationDeliveryFailures` | Async | Lỗi gửi event sang DLQ / destination. |
| `Duration` | Performance | Thời gian handler chạy (ms); có `p50/p99` để xem đuôi trễ. |
| `ConcurrentExecutions` | Concurrency | Số instance đang chạy đồng thời (theo Region/function). |
| `ProvisionedConcurrencyUtilization` | Concurrency | Tỉ lệ dùng provisioned concurrency. |
| `IteratorAge` | Event source mapping | Với **stream** (`Kinesis`/`DynamoDB Streams`): tuổi record cuối cùng khi được xử lý → đo **độ trễ xử lý stream** (cao = tụt hậu). |

---

## 📄 Nội dung (trích từ tài liệu gốc)

# Using CloudWatch metrics with Lambda

When your AWS Lambda function finishes processing an event, Lambda automatically sends metrics about the invocation to Amazon CloudWatch. You don't need to grant any additional permissions to your execution role to receive function metrics, and there's no additional charge for these metrics.

There are many types of metrics associated with Lambda functions. These include invocation metrics, performance metrics, concurrency metrics, asynchronous invocation metrics, and event source mapping metrics. For more information, see [Types of metrics for Lambda functions](monitoring-metrics-types.html).

In the CloudWatch console, you can view these metrics and build graphs and dashboards with them. You can also set alarms to respond to changes in utilization, performance, or error rates. **Lambda sends metric data to CloudWatch in 1-minute intervals.** For more immediate insight into your Lambda function, you can create high-resolution custom metrics. Charges apply for custom metrics and CloudWatch alarms.
