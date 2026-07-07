# 📂 Tài nguyên Tuần 5 — Messaging + Step Functions + Caching

> Crawl từ tài liệu AWS chính thức. Về [file học Tuần 5](../../week-05.md) · [Kế hoạch tổng](../../../DVA-C02-STUDY-PLAN.md)

| # | Tài nguyên (file local) | Chủ đề | Nguồn AWS |
|---|---|---|---|
| 1 | [sqs-standard-vs-fifo.md](sqs-standard-vs-fifo.md) | `SQS` Standard vs FIFO: at-least-once vs exactly-once, ordering, throughput (300/3.000/30.000) | https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-queue-types.html |
| 2 | [sqs-visibility-timeout.md](sqs-visibility-timeout.md) | Visibility timeout (default 30s, max 12h), in-flight ~120k, `ChangeMessageVisibility`, DLQ | https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-visibility-timeout.html |
| 3 | [sqs-long-polling.md](sqs-long-polling.md) | Short vs long polling; `WaitTimeSeconds` max 20s; giảm empty response & chi phí | https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-short-and-long-polling.html |
| 4 | [sns-message-filtering.md](sns-message-filtering.md) | `SNS` filter policy (JSON), scope MessageAttributes vs MessageBody | https://docs.aws.amazon.com/sns/latest/dg/sns-message-filtering.html |
| 5 | [kinesis-data-streams-concepts.md](kinesis-data-streams-concepts.md) | `Kinesis Data Streams`: shard (1MB/s ghi, 2MB/s đọc), partition key, retention 24h–365d, KCL | https://docs.aws.amazon.com/streams/latest/dev/key-concepts.html |
| 6 | [stepfunctions-standard-vs-express.md](stepfunctions-standard-vs-express.md) | `Step Functions` Standard (1 năm, exactly-once) vs Express (5 phút, at-least-once) | https://docs.aws.amazon.com/step-functions/latest/dg/concepts-standard-vs-express.html |
| 7 | [rds-proxy.md](rds-proxy.md) | `RDS Proxy` connection pooling cho `Lambda`, IAM/`Secrets Manager`, quota (20 proxy, 200 secrets) | https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/rds-proxy.html |

## Gợi ý thứ tự đọc
1. **`SQS` core (1 → 2 → 3):** hiểu Standard vs FIFO trước, rồi visibility timeout (bẫy xử-lý-trùng), rồi long polling (bẫy chi phí). Đây là cụm bị hỏi nhiều nhất Domain 1.
2. **`SNS` (4):** message filtering — ghép với fan-out `SNS`→nhiều `SQS` trong file tuần.
3. **`Kinesis Data Streams` (5):** thuộc số liệu shard + retention + phân biệt với `Firehose` (không replay).
4. **`Step Functions` (6):** bảng Standard vs Express — nhớ mốc 1 năm / 5 phút và exactly-once / at-least-once.
5. **`RDS Proxy` (7):** đọc cuối — keyword "`Lambda` connection storm tới RDS" → `RDS Proxy`.
