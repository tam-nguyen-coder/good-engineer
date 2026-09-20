# Confluent Platform — Monitor Consumer Lag

> **Nguồn (official):** https://docs.confluent.io/platform/current/monitor/monitor-consumer-lag.html · bổ trợ: https://docs.confluent.io/platform/current/kafka/monitoring.html (JMX monitoring — trang broker-metrics/consumer-metrics chi tiết không crawl được trong phiên này; phần bảng ngưỡng bên dưới tổng hợp từ trang monitoring.html + Apache Kafka docs)
> **Tuần:** 8 — Observability & Operations · **Loại:** Confluent Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có rút gọn) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- **Consumer lag** = số offset giữa **message mới nhất** của partition (log end offset / high watermark) và **offset cuối consumer đã đọc/commit** → số message đang chờ xử lý. Confluent nhấn mạnh lag = **offset lag** + **consumer latency** (thời gian); `kafka-consumer-groups.sh --describe` và JMX chỉ đo **offset lag**.
- Hai góc nhìn: **client-side** `records-lag-max` (tính theo **current position** đã fetch, chưa cần commit) vs **broker/tool-side** `LAG = LOG-END-OFFSET − CURRENT-OFFSET` (theo **committed offset** trong `__consumer_offsets`) → nếu commit chậm (auto commit 5 s) thì lag tool luôn cao hơn lag client.
- **Không đo được lag cho consumer dùng `assign()`** (không qua group coordinator, không commit vào group) — chỉ consumer dùng `subscribe()` với `group.id`.
- Nguyên nhân lag (Confluent chia 2 nhóm): **cấu hình** — số consumer/partition lệch (consumer > partition → idle; consumer < partition → 1 consumer gánh nhiều), partition ít, `fetch.max.bytes`/`fetch.min.bytes`/`fetch.max.wait.ms`/`max.poll.records` không hợp; **hiệu năng** — network latency, message lớn, xử lý chậm, throughput vào vượt khả năng consumer.
- Xử lý theo thứ tự: **thêm consumer** (tối đa = số partition) → **tăng partition** (cân nhắc phá key ordering) → tối ưu code xử lý (batch, async worker, giảm I/O đồng bộ) → chỉnh fetch (`max.poll.records` **giảm** nếu vượt `max.poll.interval.ms`, `fetch.min.bytes` tăng để giảm round-trip) → kiểm tra **key skew** (hot partition không giải được bằng thêm consumer).
- Công cụ: `kafka-consumer-groups.sh --describe`, JMX `records-lag-max`, Confluent **Control Center**, broker-side **consumer lag emitter** (`confluent.consumer.lag.emitter.enabled=true`, interval 60 s, MBean `consumer-lag-offset` — chỉ Confluent Server), OSS: **Burrow** (LinkedIn, đánh giá lag theo *xu hướng* OK/WARN/STALL/STOP, không cần ngưỡng cố định), **kafka-lag-exporter** (Prometheus, có cả lag theo thời gian ước lượng), Kafka Minion/kminion.
- Ngưỡng cảnh báo hay dùng: `ActiveControllerCount` ≠ 1, `OfflinePartitionsCount` > 0, `UnderReplicatedPartitions` > 0 kéo dài > 5 phút, `UnderMinIsrPartitionCount` > 0, `RequestHandlerAvgIdlePercent` < 0.3 (cảnh báo) / < 0.1 (nghiêm trọng), lag **tăng đơn điệu** thay vì tuyệt đối.

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Definition

Consumer lag represents the delay between message production and consumption in Apache Kafka. Specifically, it refers to the number of consumer offsets between the latest message in a partition and the last consumed message by a consumer — essentially, the count of unconsumed messages awaiting processing.

### Measurement

Consumer lag is a combination of both offset lag and consumer latency. The offset lag component can be monitored using the `consumer-lag-offset` MBean, which provides the difference between the broker's last stored offset and the consumer group's last committed offset for a specific topic and partition. The emitter provides offset lag measurements only, excluding latency considerations.

### Configuration for Monitoring (Confluent Server broker-side emitter)

To enable consumer lag monitoring on brokers, set two properties in the broker configuration file (`$CONFLUENT_HOME/etc/kafka/broker.properties`):

1. `confluent.consumer.lag.emitter.enabled` = `true` (default is false)
2. `confluent.consumer.lag.emitter.interval.ms` = desired interval (default is 60000 milliseconds, or 1 minute)

**Important Limitation:** You cannot monitor consumer lag with consumers that use the `assign()` method since the group coordinator doesn't manage assignment for directly assigned partitions.

### Root Causes

Consumer lag stems from two main categories:

**Configuration Issues:**

- Misconfigured consumer groups causing uneven message distribution
- Topics with insufficient partitions or low replication factors
- Improper consumer properties such as `fetch.max.bytes`, `fetch.min.bytes`, `fetch.max.wait.ms`, and `max.poll.records`

**Performance Issues:**

- High network latency between cluster and consumers
- Large message sizes overwhelming consumers
- Slow consumer processing speeds
- High message throughput exceeding consumer capacity

### Monitoring Tools

Confluent Platform provides two primary monitoring approaches: JMX metrics via the `consumer-lag-offset` MBean, and Confluent Control Center for comprehensive visibility.

### JMX monitoring overview (from docs.confluent.io/platform/current/kafka/monitoring.html)

Java Management Extensions (JMX) and Managed Beans (MBeans) are enabled by default for Kafka and Confluent Platform. To enable remote JMX monitoring, set environment variables before starting brokers or clients:

- `JMX_PORT`: the port for JMX connections (typically 9999 for brokers)
- `KAFKA_JMX_OPTS`: JMX authentication / SSL / hostname settings
- `KAFKA_OPTS`: pass `-javaagent:` parameters (e.g. Prometheus JMX Exporter) for monitoring integration

Features that are not enabled in your deployment will not generate MBeans. Metric categories: Broker and Controller Metrics, Log and Network Metrics, Group Coordinator Metrics, Producer Metrics, Consumer Metrics, Share Consumer Metrics, Security Metrics, plus Connect metrics, Kafka Streams metrics and Cluster linking metrics.

#### Broker metrics to alert on

| MBean | Description | Recommended threshold |
|---|---|---|
| `kafka.controller:type=KafkaController,name=ActiveControllerCount` | Number of active controllers in cluster | Sum across cluster should equal 1 |
| `kafka.controller:type=KafkaController,name=OfflinePartitionsCount` | Partitions with no leader | Alert if > 0 |
| `kafka.server:type=ReplicaManager,name=UnderReplicatedPartitions` | Partitions with fewer in-sync replicas than configured | Alert if > 0 (sustained) |
| `kafka.server:type=ReplicaManager,name=UnderMinIsrPartitionCount` | Partitions with ISR below `min.insync.replicas` | Alert if > 0 (producers with `acks=all` fail) |
| `kafka.server:type=ReplicaManager,name=IsrShrinksPerSec` | Rate of in-sync replica shrinkage | Monitor for sustained non-zero (flapping) |
| `kafka.server:type=KafkaRequestHandlerPool,name=RequestHandlerAvgIdlePercent` | Average idle percentage of request handler (I/O) threads | Alert if < 0.3; critical < 0.1 |
| `kafka.network:type=SocketServer,name=NetworkProcessorAvgIdlePercent` | Average idle percentage of network processors | Alert if < 0.3; critical < 0.1 |
| `kafka.network:type=RequestMetrics,name=TotalTimeMs,request={Produce\|FetchConsumer\|FetchFollower}` | Total request latency (ms), broken down into queue / local / remote / response | Alert on p99 significantly above baseline |
| `kafka.server:type=BrokerTopicMetrics,name=BytesInPerSec` / `BytesOutPerSec` | Incoming / outgoing bytes per second across all topics | Baseline dependent; watch for imbalance across brokers |

#### Producer metrics

| MBean / attribute | Description | Threshold |
|---|---|---|
| `kafka.producer:type=producer-metrics,client-id=*` `record-send-rate` | Records sent per second | Baseline dependent |
| `record-error-rate` / `record-error-total` | Failed sends per second / total | Alert if > 0 |
| `record-retry-rate` | Retried sends per second | Sustained > 0 indicates broker/network trouble |
| `request-latency-avg` / `request-latency-max` | Producer request latency (ms) | Alert if significantly elevated |
| `batch-size-avg` | Average batch bytes per partition per request | Compare with `batch.size`; low means little batching benefit |
| `record-queue-time-avg` | Time batches wait in the accumulator (ms) | Roughly `linger.ms`; much higher means sender back-pressure |
| `buffer-available-bytes`, `waiting-threads`, `bufferpool-wait-ratio` | Buffer pressure | Alert when available bytes approach 0 |
| `produce-throttle-time-avg` | Time throttled by broker quotas | Should be 0 |

#### Consumer metrics

| MBean / attribute | Description | Threshold |
|---|---|---|
| `kafka.consumer:type=consumer-fetch-manager-metrics,client-id=*` `records-lag-max` | Maximum consumer lag across partitions (current position based) | Alert if increasing |
| `records-lag` (per partition) | Latest lag for the partition | Alert on sustained growth |
| `records-lead-min` | Minimum distance to log start offset | Alert if approaching 0 (data may be deleted before consumption) |
| `records-consumed-rate` / `bytes-consumed-rate` | Records / bytes consumed per second | Baseline dependent |
| `fetch-latency-avg` / `fetch-rate` / `fetch-size-avg` | Fetch behaviour | High latency + small size → tune `fetch.min.bytes`/`fetch.max.wait.ms` |
| `kafka.consumer:type=consumer-coordinator-metrics,client-id=*` `commit-latency-avg` | Average offset commit latency (ms) | Alert if significantly elevated |
| `rebalance-latency-avg` / `rebalance-total` / `failed-rebalance-total` | Rebalance activity | Frequent rebalances = unstable group |
| `assigned-partitions` | Number of assigned partitions | 0 for extra consumers beyond partition count (idle) |
| `kafka.consumer:type=consumer-metrics,client-id=*` `time-between-poll-max` | Max delay between poll() calls | Compare with `max.poll.interval.ms` (300000 ms) |

Refer to Control Center for out-of-the-box Kafka cluster monitoring, or Health+ for intelligent alerts and cluster health management.
