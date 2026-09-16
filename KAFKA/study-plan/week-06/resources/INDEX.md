# 📂 Tài nguyên Tuần 6 — Kafka Streams

> Crawl từ tài liệu chính thức (Confluent Docs ≡ Apache Kafka Streams Docs). Về [file học Tuần 6](../README.md) · [Kế hoạch tổng](../../../KAFKA-STUDY-PLAN.md)
>
> ℹ️ Lúc crawl, các path `kafka.apache.org/43/documentation/streams/...` trả 404/redirect nên dùng bản Confluent Platform (nội dung Streams docs của Confluent là bản sao của Apache, có thêm ghi chú version CP). Link Apache tương ứng ghi trong header từng file.

| # | Tài nguyên (file local) | Chủ đề | Nguồn |
|---|---|---|---|
| 1 | [streams-core-concepts-architecture.md](streams-core-concepts-architecture.md) | Library (không cluster), topology, time semantics, stream-table duality, `KStream`/`KTable`/`GlobalKTable`, **task = max partition**, thread, state store + changelog + standby, record cache, depth-first | https://docs.confluent.io/platform/current/streams/concepts.html · .../architecture.html |
| 2 | [streams-dsl-api.md](streams-dsl-api.md) | Stateless ops & repartition marking, `aggregate/count/reduce` + `Materialized`, 4 loại window, grace, retention, `suppress` | https://docs.confluent.io/platform/current/streams/developer-guide/dsl-api.html |
| 3 | [streams-joins.md](streams-joins.md) | **Join matrix** (window? co-partition? inner/left/outer), KStream-KStream / KStream-KTable / KTable-KTable (+FK) / KStream-GlobalKTable, null & tombstone semantics | https://docs.confluent.io/platform/current/streams/developer-guide/dsl-api.html#joining |
| 4 | [streams-config.md](streams-config.md) | `application.id`, `processing.guarantee`, `commit.interval.ms` 30000/100, `statestore.cache.max.bytes` 10 MB, `num.stream.threads`, `num.standby.replicas`, serde, timestamp extractor, exception handlers, client overrides | https://docs.confluent.io/platform/current/streams/developer-guide/config-streams.html |
| 5 | [streams-processor-api.md](streams-processor-api.md) | `Processor`/`ProcessorContext`, punctuate `STREAM_TIME` vs `WALL_CLOCK_TIME`, `Stores` (RocksDB vs in-memory, logging), timestamped/versioned store, `Topology.addSource/addProcessor/addStateStore/addSink` | https://docs.confluent.io/platform/current/streams/developer-guide/processor-api.html |
| 6 | [streams-testing-topologytestdriver.md](streams-testing-topologytestdriver.md) | `kafka-streams-test-utils`, `TopologyTestDriver` (không broker, đồng bộ), `TestInputTopic/TestOutputTopic`, `advanceWallClockTime`, state store access, `MockProcessorContext` | https://docs.confluent.io/platform/current/streams/developer-guide/test-streams.html |
| 7 | [streams-upgrade-kip-1071-dlq.md](streams-upgrade-kip-1071-dlq.md) | **KIP-1071** Streams Rebalance Protocol (`group.protocol=streams`, GA 4.2, `kafka-streams-groups.sh`), **KIP-1034** DLQ, **KIP-1033** `ProcessingExceptionHandler`, API bị xoá ở 4.0, `StreamsUncaughtExceptionHandler` | https://docs.confluent.io/platform/current/streams/upgrade-guide.html (+ KIP cwiki) |
| 8 | [ksqldb-concepts.md](ksqldb-concepts.md) | ksqlDB trên Kafka Streams: STREAM vs TABLE, persistent query (CSAS/CTAS), push (`EMIT CHANGES`) vs pull query, window SQL, port 8088, command topic | https://docs.confluent.io/platform/current/ksqldb/concepts/index.html |

## Gợi ý thứ tự đọc

1. **Nền tảng (1):** đọc trước để hiểu "library, không cluster", task = max partition, stream-table duality, changelog/standby. Không hiểu phần này thì mọi câu hỏi scale/fault-tolerance đều đoán mò.
2. **DSL (2 → 3):** học stateless (nhớ nhóm nào đổi key → repartition) rồi stateful + window + `suppress`; sau đó **bảng join** ở file 3 — thuộc lòng 4 dòng "window? / co-partition?".
3. **Config (4):** đọc cùng lúc làm Lab 6.1–6.4; ghim `commit.interval.ms` 30000 → 100 khi EOS, cache 10 MB, `num.standby.replicas` 0.
4. **PAPI + Testing (5 → 6):** PAPI đủ để trả lời câu punctuate & state store; testing là domain TEST 8% — `TopologyTestDriver` xuất hiện gần như chắc chắn.
5. **Mới trong 4.x (7):** KIP-1071 / DLQ / ProcessingExceptionHandler — đề mới bắt đầu hỏi; ít nhất nhận diện được `group.protocol=streams` và `errors.deadletterqueue.topic.name`.
6. **ksqlDB (8):** đọc cuối, 15 phút, chỉ để phân biệt push vs pull query và STREAM vs TABLE.
