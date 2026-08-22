# 📂 Tài nguyên Tuần 3 — DynamoDB toàn tập

> Crawl từ tài liệu AWS chính thức. Về [file học Tuần 3](../README.md) · [Kế hoạch tổng](../../../DVA-C02-STUDY-PLAN.md)

| # | Tài nguyên (file local) | Chủ đề | Nguồn AWS |
|---|---|---|---|
| 1 | [dynamodb-capacity-mode.md](dynamodb-capacity-mode.md) | Throughput capacity: On-demand vs Provisioned | https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/HowItWorks.ReadWriteCapacityMode.html |
| 2 | [dynamodb-secondary-indexes.md](dynamodb-secondary-indexes.md) | Secondary indexes: GSI vs LSI (bảng so sánh, quota) | https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/SecondaryIndexes.html |
| 3 | [dynamodb-streams.md](dynamodb-streams.md) | DynamoDB Streams (CDC, StreamViewType, 24h, shard) | https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Streams.html |
| 4 | [dynamodb-dax.md](dynamodb-dax.md) | DAX in-memory cache (khi dùng / khi không) | https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DAX.html |
| 5 | [dynamodb-transactions.md](dynamodb-transactions.md) | Transactions ACID (giới hạn 100 action / 4 MB, isolation) | https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/transactions.html |
| 6 | [dynamodb-partition-key-design.md](dynamodb-partition-key-design.md) | Thiết kế partition key, hot partition, 3000 RCU / 1000 WCU | https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/bp-partition-key-design.html |
| 7 | [dynamodb-faqs.md](dynamodb-faqs.md) | FAQ tổng hợp (item 400KB, table class, Global Tables, TTL, mã hóa, pricing) | https://aws.amazon.com/dynamodb/faqs/ |

## Gợi ý thứ tự đọc
1. **dynamodb-capacity-mode** — nền tảng: hiểu On-demand vs Provisioned và cách tính RCU/WCU trước tiên.
2. **dynamodb-partition-key-design** — cách DynamoDB chia partition, giới hạn 3000/1000 mỗi partition, tránh hot key. Bổ trợ trực tiếp cho capacity.
3. **dynamodb-secondary-indexes** — GSI vs LSI: bảng so sánh là "must-memorize" cho đề thi.
4. **dynamodb-transactions** — ACID, các giới hạn số (100 action / 4 MB / 2× capacity), isolation levels.
5. **dynamodb-streams** — CDC, 4 StreamViewType, retention 24h, tiền đề cho Global Tables + Lambda triggers.
6. **dynamodb-dax** — caching microsecond, chỉ tăng tốc eventually consistent read, khi nào KHÔNG dùng.
7. **dynamodb-faqs** — quét cuối để chốt số liệu & so sánh (item 400KB, table class, Global Tables prereq, TTL, encryption, VPC endpoint, free tier).
