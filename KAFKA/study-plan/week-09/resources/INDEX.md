# 📂 Tài nguyên Tuần 9 — Kafka trên AWS (`Amazon MSK`) + Design patterns

> Crawl từ tài liệu chính thức (AWS Docs, microservices.io, Debezium, Confluent). Về [file học Tuần 9](../README.md) · [Kế hoạch tổng](../../../KAFKA-STUDY-PLAN.md)

| # | Tài nguyên (file local) | Chủ đề | Nguồn |
| - | --- | --- | --- |
| 1 | [msk-cluster-types-provisioned-express-serverless.md](msk-cluster-types-provisioned-express-serverless.md) | MSK là gì; Provisioned Standard vs **Express brokers** (3× throughput, 20× scale, 90% recovery, 3 AZ) vs **Serverless** (chỉ IAM; 200/400 MBps, 2.400 partition); ports 9092/9094/9096/9098 (+9194/9196/9198); quota | https://docs.aws.amazon.com/msk/latest/developerguide/what-is-msk.html · .../msk-broker-types-express.html · .../serverless.html · .../limits.html · .../port-info.html |
| 2 | [msk-iam-access-control.md](msk-iam-access-control.md) | IAM access control: `kafka-cluster:*` actions + required actions, 4 loại ARN (cluster/topic/group/transactional-id), `client.properties` (`AWS_MSK_IAM`, `IAMLoginModule`), signer lib non-Java | https://docs.aws.amazon.com/msk/latest/developerguide/iam-access-control.html · .../kafka-actions.html · .../configure-clients-for-iam-access-control.html |
| 3 | [msk-connect.md](msk-connect.md) | MSK Connect: custom plugin (S3), worker configuration, connector capacity provisioned/autoscaled, **MCU = 1 vCPU/4 GiB**, service execution role, log delivery, quota 100/100/60/10 | https://docs.aws.amazon.com/msk/latest/developerguide/msk-connect.html · .../msk-connect-capacity.html · .../msk-connect-workers.html |
| 4 | [msk-replicator.md](msk-replicator.md) | MSK Replicator: SRR/CRR, **Prefixed vs Identical** topic name, offset sync, header `__mskmr`, quota 15 replicator / 750 topic / 1 GB/s | https://docs.aws.amazon.com/msk/latest/developerguide/msk-replicator.html · .../msk-replicator-topic-naming.html |
| 5 | [msk-configuration-and-monitoring.md](msk-configuration-and-monitoring.md) | MSK Configuration (subset `server.properties`), default MSK khác Kafka (`auto.create.topics.enable=false`, RF=3, min.isr=2), 4 mức CloudWatch, lag metrics, Open Monitoring 11001/11002 | https://docs.aws.amazon.com/msk/latest/developerguide/msk-configuration-properties.html · .../msk-default-configuration.html · .../metrics-details.html · .../open-monitoring.html |
| 6 | [lambda-msk-event-source-mapping.md](lambda-msk-event-source-mapping.md) | Lambda ESM (poll): `StartingPosition`, `BatchSize` 100/10.000, batching window ≤300 s, `ConsumerGroupId`, filter, on-failure destination, provisioned pollers, `AWSLambdaMSKExecutionRole`, self-managed Kafka `SourceAccessConfigurations`, event JSON base64 | https://docs.aws.amazon.com/lambda/latest/dg/with-msk.html · .../msk-esm-parameters.html · .../with-msk-permissions.html · .../with-kafka.html |
| 7 | [glue-schema-registry.md](glue-schema-registry.md) | Glue Schema Registry: miễn phí, Avro/JSON/Protobuf, 8 compatibility mode (`*_ALL`), checkpoint, quota 100 registry/10.000 version/170 KB, so với Confluent SR | https://docs.aws.amazon.com/glue/latest/dg/schema-registry.html |
| 8 | [transactional-outbox-debezium.md](transactional-outbox-debezium.md) | Dual-write → **Transactional Outbox** (polling publisher vs log tailing) + Debezium `EventRouter` SMT (`aggregatetype` → `outbox.event.${routedByValue}`, key = `aggregateid`, header `id`) | https://microservices.io/patterns/data/transactional-outbox.html · https://debezium.io/documentation/reference/stable/transformations/outbox-event-router.html |
| 9 | [kafka-error-handling-retry-dlq.md](kafka-error-handling-retry-dlq.md) | 4 pattern lỗi: Stop on error / DLQ / Retry topic (mất ordering) / Ordered retries; headers khuyến nghị; Connect sink DLQ, Streams exception handlers; blocking vs non-blocking retry | https://www.confluent.io/blog/error-handling-patterns-in-kafka/ · https://developer.confluent.io/patterns/event-processing/dead-letter-stream/ |

## Gợi ý thứ tự đọc

1. **MSK tổng quan (1):** nắm 3 lựa chọn Provisioned Standard / Express / Serverless và bảng port trước — mọi câu hỏi AWS đều xoay quanh "chọn loại nào" và "port nào".
2. **IAM access control (2):** đọc kỹ cột *Required actions* (`ReadData` cần `AlterGroup`), 4 loại ARN, rồi so sánh với Kafka ACL đã học Tuần 7.
3. **Config + Monitoring (5):** thuộc default MSK khác Kafka và 4 mức metric; nối với JMX/lag Tuần 8.
4. **MSK Connect (3) → MSK Replicator (4):** đối chiếu với Kafka Connect Tuần 5 và MirrorMaker 2 Tuần 8 — phần "managed" khác gì.
5. **Lambda ESM (6) + Glue SR (7):** phần dễ ghép với DVA-C02 (poll vs push, batch, filter, IAM role) — làm Lab 9.2 ngay sau khi đọc.
6. **Design patterns (8 → 9):** Outbox/CDC giải dual-write, rồi retry/DLQ topics — làm Lab 9.3 → 9.5. Đây là 2 file nền cho phần ARCH của câu hỏi.
