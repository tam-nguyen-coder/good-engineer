# 📂 Tài nguyên Tuần 9 — Observability & Optimization

> Crawl từ tài liệu AWS chính thức (`CloudWatch` / `X-Ray` / `CloudTrail` / `EventBridge` / `Lambda` metrics). Về [file học Tuần 9](../README.md) · [Kế hoạch tổng](../../../DVA-C02-STUDY-PLAN.md)

| # | Tài nguyên (file local) | Chủ đề | Nguồn AWS |
|---|---|---|---|
| 1 | [cloudwatch-concepts.md](cloudwatch-concepts.md) | Metrics: namespace, dimension (≤30), resolution (1 phút / 1 giây), retention rollup, statistics, percentiles, alarm cơ bản | https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/cloudwatch_concepts.html |
| 2 | [cloudwatch-logs.md](cloudwatch-logs.md) | Logs: log group/stream, retention (mặc định vô hạn), metric filter, Logs Insights, Live Tail, log classes | https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/WhatIsCloudWatchLogs.html |
| 3 | [cloudwatch-alarms.md](cloudwatch-alarms.md) | Alarms: 3 trạng thái `OK`/`ALARM`/`INSUFFICIENT_DATA`, actions (`SNS`/EC2/Auto Scaling), composite alarm, history 30 ngày | https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/AlarmThatSendsEmail.html |
| 4 | [cloudtrail-overview.md](cloudtrail-overview.md) | Audit API: Event history 90 ngày, CloudTrail Lake, Trails → S3/CloudWatch Logs/EventBridge | https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-user-guide.html |
| 5 | [eventbridge-overview.md](eventbridge-overview.md) | Event bus vs pipes vs Scheduler; rule theo event pattern / schedule (`cron`/`rate`) | https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-what-is.html |
| 6 | [xray-concepts.md](xray-concepts.md) | Segment/subsegment, service graph, sampling, tracing header, **annotations (index) vs metadata (không index)** | https://docs.aws.amazon.com/xray/latest/devguide/xray-concepts.html |
| 7 | [lambda-metrics.md](lambda-metrics.md) | Metric mặc định `Lambda`: Invocations/Duration/Errors/Throttles/ConcurrentExecutions/IteratorAge (1 phút, miễn phí) | https://docs.aws.amazon.com/lambda/latest/dg/monitoring-metrics.html |

## Gợi ý thứ tự đọc
1. **cloudwatch-concepts.md** — nền tảng metric (namespace/dimension/resolution/retention) trước khi học mọi thứ khác.
2. **cloudwatch-logs.md** — log group/stream, retention, metric filter (nối tiếp sang alarm).
3. **cloudwatch-alarms.md** — alarm states + actions; hiểu composite alarm để giảm nhiễu.
4. **lambda-metrics.md** — áp metric mặc định `Lambda` vào alarm; nhớ `IteratorAge` cho stream.
5. **cloudtrail-overview.md** — chốt ranh giới `CloudWatch` (hiệu năng/log) vs `CloudTrail` (ai gọi API gì / audit).
6. **eventbridge-overview.md** — rule schedule `cron`/`rate` để chạy `Lambda` định kỳ.
7. **xray-concepts.md** — ⭐ trọng tâm: annotations vs metadata, sampling, service map, tracing header.

## 🔑 Số liệu PHẢI thuộc (rút gọn)
- Metric resolution: **standard 1 phút / high-res 1 giây**; dimension **≤ 30/metric**; namespace **≤ 255 ký tự**.
- Metric retention rollup: `<60s`→3h · `60s`→15 ngày · `300s`→63 ngày · `3600s`→455 ngày (15 tháng).
- Logs retention **mặc định vô hạn** — phải tự set (1 ngày → 10 năm).
- Alarm history giữ **30 ngày**; composite alarm **không** làm EC2/Auto Scaling action.
- CloudTrail Event history = **90 ngày**, miễn phí; Lake giữ tới **~10 năm** (3.653 ngày) / **~7 năm** (2.557 ngày).
- X-Ray: segment doc **≤ 64 kB**; index **≤ 50 annotations/trace**; sampling mặc định **1 req/giây + 5%**; trace & service graph retention **30 ngày**; daemon nghe **UDP cổng 2000** (xem file học tuần).
- Lambda metric mặc định: **1 phút, miễn phí**, không cần thêm quyền role.
