# 🟦 Tuần 8 — Observability & Operations

> **Domain CCDAK:** Observability (OBS, 13%) · **Thời lượng:** ~11h (4 buổi) · **Vị trí:** Tuần 8/10 — tuần cuối phủ kiến thức thi, **có CHECKPOINT: mini-mock toàn domain (Tuần 1–8) ≥72%**
>
> **Điều hướng:** [⬅️ Tuần 7](../week-07/README.md) · [🏠 Kế hoạch tổng](../../KAFKA-STUDY-PLAN.md) · [Tuần 9 ➡️](../week-09/README.md)

## 🎯 Mục tiêu tuần này

- **Phân biệt được** 4 nhóm metric broker "sống còn" (`UnderReplicatedPartitions`, `OfflinePartitionsCount`, `ActiveControllerCount`, `RequestHandlerAvgIdlePercent`) — nhìn giá trị bất thường là biết ngay chuyện gì đang xảy ra và sửa ở đâu.
- **Tự tay** dựng stack `JMX` → `Prometheus JMX Exporter` → `Prometheus` → `Grafana` trên cluster 3 node của Tuần 1 và đọc `UnderReplicatedPartitions` tăng khi kill broker.
- **Giải thích được** consumer lag (LEO − committed offset), đọc trôi chảy `kafka-consumer-groups.sh --describe`, và chọn đúng cách xử lý theo nguyên nhân (consumer chậm / ít consumer / rebalance liên tục / key skew).
- **Đọc tên exception là biết** nguyên nhân + cách sửa (bảng cheat-sheet 14 exception), đặc biệt **poison pill** (`SerializationException`) làm consumer kẹt vòng lặp → DLQ.
- **Cấu hình được** các thao tác vận hành thi hay hỏi: `kafka-reassign-partitions.sh` (`--generate/--execute --throttle/--verify`), `kafka-leader-election.sh`, rolling restart, `kafka-features.sh upgrade`, tiered storage (`remote.storage.enable`), `MirrorMaker 2` (3 connector + `ReplicationPolicy`).
- **Tính được** số partition / dung lượng đĩa theo công thức capacity planning và nhận ra hot partition do key skew.
- **Chốt checkpoint:** mini-mock trộn Tuần 1–8 (~40 câu) đạt **≥72%** trước khi sang Tuần 9 (AWS + patterns + FULL MOCK #1).

## 📚 Nội dung học chi tiết

### 🅰️ Buổi A — Lý thuyết (~3h)

**1. `JMX` — cửa duy nhất để lấy metric của Kafka (broker + client Java)**

- Broker dùng **Yammer Metrics**, client Java dùng **Kafka Metrics**; cả hai **expose qua `JMX`** (MBean). Mọi metric dạng `*-rate` có bản đếm tích luỹ `*-total`.
- Remote JMX **tắt mặc định**. Bật bằng biến môi trường **`JMX_PORT`** (ví dụ `JMX_PORT=9999`) cho tiến trình khởi động qua script CLI; bảo mật (auth/SSL, `java.rmi.server.hostname` khi chạy trong container) đặt qua **`KAFKA_JMX_OPTS`**. Production **phải** bật auth — mặc định JMX không xác thực.
- **Tên MBean** dạng `<domain>:type=<Type>,name=<Name>[,topic=...|request=...|client-id=...]`. Domain theo thành phần: `kafka.server` (ReplicaManager, BrokerTopicMetrics, KafkaRequestHandlerPool…), `kafka.network` (RequestMetrics, SocketServer, RequestChannel), `kafka.controller` (KafkaController), `kafka.log` (LogFlushStats, LogCleaner), `kafka.producer`, `kafka.consumer`, `kafka.connect`, `kafka.streams`. Kafka 4.x (**KIP-1100**) chuẩn hoá tên theo `kafka.COMPONENT:type=...,name=...`; tên legacy vẫn còn ở 4.3.
- Công cụ đọc nhanh: **`jconsole`** (GUI, browse toàn bộ MBean), **`JmxTool`** (`kafka-run-class.sh org.apache.kafka.tools.JmxTool --jmx-url service:jmx:rmi:///jndi/rmi://host:9999/jmxrmi --object-name ... --one-time`; tên cũ `kafka.tools.JmxTool` đã bỏ ở 4.0), hoặc `metric.reporters` tuỳ biến (mặc định `JmxReporter`).
- **Stack chuẩn production:** `Prometheus JMX Exporter` chạy dạng **Java agent** trong JVM broker (`KAFKA_OPTS=-javaagent:/opt/jmx_prometheus_javaagent.jar=7071:/opt/kafka-jmx.yml`) → đọc MBean theo **rules YAML** (regex `pattern` → `name`/`labels`/`type`) → expose HTTP `/metrics` port 7071 → `Prometheus` scrape → `Grafana` vẽ + alert. Không cần mở remote JMX ra ngoài. Client Java cũng gắn agent y hệt; `kafkajs` không có JMX → dùng `instrumentationEvents`/tự đẩy metric.
- Bảng so sánh cách lấy metric:

| Cách | Cần gì | Ưu | Nhược | Dùng khi |
|---|---|---|---|---|
| `jconsole` / `JmxTool` | `JMX_PORT` mở | Không cài thêm, thấy đủ MBean | Thủ công, không lưu lịch sử, không alert | Debug tức thời |
| JMX Exporter (javaagent) + Prometheus + Grafana | jar + rules yaml + Prometheus | Chuẩn de-facto, có history/alert, không mở JMX ra ngoài | Phải viết rules; metric tên đổi theo rules | Production, lab 8.1 |
| `kafka-consumer-groups.sh --describe` | CLI | Lag theo committed offset, không cần JMX | Snapshot, không lịch sử | Kiểm tra nhanh lag |
| Burrow / kafka-lag-exporter | Service riêng | Lag theo **xu hướng** (Burrow) / lag theo thời gian (lag-exporter), không cần chạm consumer | Thêm hạ tầng | Alert lag production |
| Confluent Control Center / `Amazon MSK` Open Monitoring | Managed | Có sẵn dashboard | Không phải OSS / có phí | Managed cluster |

**2. Broker metrics PHẢI NHỚ — tên → ý nghĩa → ngưỡng → hành động**

| Metric (MBean rút gọn) | Ý nghĩa | Bình thường / Ngưỡng | Hành động khi lệch |
|---|---|---|---|
| `kafka.server:type=ReplicaManager,name=UnderReplicatedPartitions` | Số partition có \|ISR\| < \|replicas\| | **0**; >0 quá vài phút → alert | Broker chết / follower tụt (`replica.lag.time.max.ms`=30 s): kiểm tra broker, disk, network, GC; tăng `num.replica.fetchers` nếu follower không kịp |
| `...ReplicaManager,name=UnderMinIsrPartitionCount` | \|ISR\| < `min.insync.replicas` → producer `acks=all` **bị chặn** (`NotEnoughReplicasException`) | **0** | Mất khả năng ghi → khôi phục broker ngay |
| `...ReplicaManager,name=AtMinIsrPartitionCount` | \|ISR\| = min.isr — chỉ còn 1 lỗi nữa là chặn ghi | 0 | Cảnh báo sớm |
| `kafka.controller:type=KafkaController,name=OfflinePartitionsCount` | Partition **không có leader** → mất availability cả đọc lẫn ghi | **0**; >0 = sự cố nghiêm trọng | Bật lại broker giữ replica; đường cùng: unclean election |
| `...KafkaController,name=ActiveControllerCount` | Node này có phải active controller | Tổng toàn cluster **= 1** | ≠1 → sự cố quorum (0 = không ai điều khiển, 2 = split) |
| `...ReplicaManager,name=IsrShrinksPerSec` / `IsrExpandsPerSec` | Tần suất ISR co / nở | **0** ngoài lúc broker up/down | Dao động liên tục = "ISR flapping": GC pause, network, disk chậm |
| `kafka.server:type=KafkaRequestHandlerPool,name=RequestHandlerAvgIdlePercent` | % rảnh của **I/O (request handler) thread** | 0–1, **> 0.3**; <0.3 cảnh báo, <0.1 nghiêm trọng | Tăng `num.io.threads` (mặc định **8**), giảm tải, thêm broker |
| `kafka.network:type=SocketServer,name=NetworkProcessorAvgIdlePercent` | % rảnh của **network thread** | **> 0.3** | Tăng `num.network.threads` (mặc định **3**) |
| `kafka.server:type=BrokerTopicMetrics,name=BytesInPerSec` / `BytesOutPerSec` / `MessagesInPerSec` (thêm `,topic=X` để lọc) | Throughput vào/ra từ client | Baseline riêng | Capacity planning; `BytesOutPerSec` không gồm replication (có `ReplicationBytesOutPerSec` riêng) |
| `...BrokerTopicMetrics,name=BytesRejectedPerSec` | Batch bị từ chối vì > `message.max.bytes` | 0 | Sửa `max.request.size`/`message.max.bytes` |
| `kafka.network:type=RequestMetrics,name=TotalTimeMs,request=Produce\|FetchConsumer\|FetchFollower` | Tổng latency 1 request theo loại (xem mục 3) | p99 ổn định | Tách theo 5 pha để tìm nghẽn |
| `kafka.network:type=RequestChannel,name=RequestQueueSize` | Request chờ I/O thread | Nhỏ | Đầy = thiếu io thread |
| `...KafkaController,name=LeaderElectionRateAndTimeMs` | Tần suất + thời gian bầu leader | 0 ngoài lúc failover | Cao = broker chết liên tục |
| `...KafkaController,name=UncleanLeaderElectionsPerSec` | Bầu leader **ngoài ISR** (có thể mất data) | **0 tuyệt đối** | >0 → đã bật `unclean.leader.election.enable=true`, xem lại |
| `...ReplicaManager,name=PartitionCount` / `LeaderCount` | Số partition / leader trên broker | **Đều nhau** giữa các broker | Lệch → `kafka-leader-election.sh --election-type preferred` / reassignment / Cruise Control |
| `kafka.log:type=LogFlushStats,name=LogFlushRateAndTimeMs` | Tần suất + thời gian fsync | Ổn định | Tăng vọt = disk chậm |
| `kafka.server:type=ReplicaFetcherManager,name=MaxLag,clientId=Replica` | Follower tụt leader bao nhiêu message | Nhỏ | Tăng → sắp rời ISR |
| KRaft: `kafka.server:type=raft-metrics` (`current-state`, `current-leader`, `high-watermark`, `commit-latency-avg`), `kafka.controller:...,name=MetadataErrorCount` / `FencedBrokerCount` / `LastAppliedRecordLagMs` | Sức khoẻ quorum + broker fenced | `MetadataErrorCount` = 0, `FencedBrokerCount` = 0 | Broker fenced = không heartbeat tới controller |
| JVM: `java.lang:type=GarbageCollector` (`CollectionTime`), `java.lang:type=Memory` heap | GC pause dài → ISR shrink, session timeout | GC pause < vài trăm ms | Heap broker **~6 GB là đủ**; RAM còn lại để **OS page cache** — Kafka đọc/ghi qua page cache nên **page cache quan trọng hơn heap** |

**3. Mổ xẻ latency 1 request — `TotalTimeMs` = 5 pha (câu hỏi "vì sao produce chậm")**

```
TotalTimeMs = RequestQueueTimeMs + LocalTimeMs + RemoteTimeMs + ResponseQueueTimeMs + ResponseSendTimeMs
              │ chờ io thread     │ leader xử lý │ chờ "bên ngoài"  │ chờ network thread │ gửi response
              │ (thiếu io thread) │ (ghi log,    │ Produce: chờ     │ (thiếu network     │ (network chậm /
              │                   │  disk chậm)  │  follower ack    │  thread)           │  response to)
              │                   │              │  khi acks=all    │                    │
              │                   │              │ Fetch: chờ đủ    │                    │
              │                   │              │  fetch.min.bytes │                    │
              │                   │              │  / fetch.max.wait│                    │
```

- **`RemoteTimeMs` cao với `Produce`** = leader chờ follower trong ISR ghi xong (`acks=all`) → follower chậm/network liên broker. **`RemoteTimeMs` cao với `FetchConsumer`** = broker "cố ý" chờ đủ `fetch.min.bytes` (mặc định 1) tới `fetch.max.wait.ms` (500) → **bình thường**, không phải lỗi (đề hay bẫy chỗ này).
- `RequestQueueTimeMs` cao ↔ `RequestHandlerAvgIdlePercent` thấp → tăng `num.io.threads`. `ResponseQueueTimeMs`/`ResponseSendTimeMs` cao ↔ `NetworkProcessorAvgIdlePercent` thấp → tăng `num.network.threads`. `LocalTimeMs` cao → disk / `LogFlushRateAndTimeMs`.

**4. Producer metrics (`kafka.producer:type=producer-metrics,client-id=…`) — đọc để tune Tuần 3**

| Metric | Nghĩa là gì | Đọc thế nào |
|---|---|---|
| `record-send-rate` / `record-send-total` | Record gửi thành công/giây | Baseline throughput |
| `record-error-rate` | Record lỗi **sau hết retry** | Phải **0**; >0 → xem exception (`RecordTooLarge`, auth, timeout) |
| `record-retry-rate` | Record phải retry | >0 liên tục = leader đổi / ISR thiếu / network |
| `request-latency-avg` / `-max` | Thời gian 1 ProduceRequest round-trip | Cao → broker chậm / `RemoteTimeMs` (acks=all) |
| `batch-size-avg` | Byte trung bình 1 batch/partition | **Nhỏ hơn nhiều so với `batch.size` (16 KB)** → batch không đầy → **tăng `linger.ms`** (mặc định 5) |
| `records-per-request-avg` | Record/request | Thấp = batching kém |
| `compression-rate-avg` | Tỉ lệ nén = size nén / size gốc | **Càng nhỏ càng nén tốt** (0.3 tốt hơn 0.8); 1.0 = không nén |
| `record-queue-time-avg` | Thời gian batch nằm trong accumulator | ≈ `linger.ms` là bình thường; cao hơn nhiều = sender thread không kịp |
| `buffer-available-bytes` ↓ 0, `bufferpool-wait-time-total` ↑, `waiting-threads` > 0 | Buffer **32 MB** đầy | `send()` block `max.block.ms` (60 s) → `TimeoutException`/`BufferExhaustedException`: producer nhanh hơn broker |
| `produce-throttle-time-avg` / `-max` | Thời gian bị broker **throttle** vì quota | >0 = đụng `producer_byte_rate` quota (Tuần 7), không phải lỗi mạng |
| `requests-in-flight` | Request đang chờ response | ≤ `max.in.flight.requests.per.connection` (5) |

**5. Consumer metrics (`kafka.consumer:type=consumer-fetch-manager-metrics` / `consumer-coordinator-metrics` / `consumer-metrics`)**

| Metric | Nghĩa là gì | Đọc thế nào |
|---|---|---|
| `records-lag-max` / `records-lag` (per partition) | Lag lớn nhất / từng partition theo **current position** (đã fetch, chưa cần commit) | Tăng đều = consumer không kịp; **khác** LAG của CLI (tính theo committed offset) |
| `records-lead-min` | Khoảng cách từ position tới **log start offset** (KIP-92) | **Tiến về 0 = record sắp bị retention xoá trước khi đọc → sắp MẤT DATA** |
| `fetch-latency-avg` / `fetch-rate` / `fetch-size-avg` | Latency 1 fetch / số fetch/giây / byte mỗi fetch | `fetch-latency` ≈ `fetch.max.wait.ms` khi ít data là bình thường |
| `records-consumed-rate` / `bytes-consumed-rate` | Throughput tiêu thụ | So với `MessagesInPerSec` của topic để biết có kịp không |
| `commit-latency-avg` / `commit-rate` | Thời gian/tần suất commit | Cao → coordinator chậm |
| `rebalance-latency-avg` / `-max` / `-total`, `rebalance-total`, `rebalance-rate-per-hour` | Thời gian + số lần rebalance | `rebalance-rate-per-hour` cao = **rebalance storm** |
| `failed-rebalance-total` / `-rate-per-hour` | Rebalance thất bại | >0 → member rời/join liên tục, timeout |
| `last-rebalance-seconds-ago` | Bao lâu rồi chưa rebalance | Nhỏ liên tục = đang rebalance liên tục |
| `time-between-poll-avg` / `-max` | Khoảng cách giữa 2 `poll()` | So với **`max.poll.interval.ms` (300 s)**: `-max` tiến gần = sắp bị kick khỏi group |
| `last-poll-seconds-ago` | Lần poll cuối | Lớn = poll loop treo |
| `poll-idle-ratio-avg` | Tỉ lệ thời gian **chờ trong poll** so với xử lý | ≈1: consumer rảnh (chờ data); ≈0: **user code xử lý chậm** → nguyên nhân lag |
| `fetch-throttle-time-avg` | Bị throttle vì `consumer_byte_rate` quota | >0 = quota |
| `assigned-partitions` | Số partition được gán | 0 = consumer **idle** (nhiều consumer hơn partition) |

- **Kafka Streams** (`kafka.streams`, 4 tầng client → thread → task → processor/state-store; `metrics.recording.level` = `info`/`debug`/`trace`): thread `process-rate`, `commit-latency-avg`, `poll-rate`; task `record-lateness-avg/max` (record tới muộn so với stream time), `dropped-records-total` (drop vì quá grace / null key), `active-process-ratio`. **Kafka Connect** (`kafka.connect`): `connector-count`, `task-count`, connector/task `status` (`running/paused/failed/unassigned`), source `source-record-poll-rate`/`source-record-write-rate`, sink `sink-record-read-rate`/`sink-record-lag-max`, error `deadletterqueue-produce-requests`, `total-record-errors`, `total-records-skipped`. Nhận diện tên là đủ cho đề.

**6. Consumer lag — định nghĩa, đo, nguyên nhân → xử lý**

- **Lag** (per partition) = **Log End Offset (LEO / high watermark) − committed offset** của group = số record đang chờ xử lý. Lag theo thời gian (record cũ bao lâu) = "consumer latency", CLI/JMX **không** đo trực tiếp (Burrow/kafka-lag-exporter ước lượng).
- **`kafka-consumer-groups.sh --describe --group X`** in: `TOPIC PARTITION CURRENT-OFFSET LOG-END-OFFSET LAG CONSUMER-ID HOST CLIENT-ID`. `CURRENT-OFFSET` = committed offset; `LAG = LOG-END-OFFSET − CURRENT-OFFSET`; **`CONSUMER-ID` = `-`** → partition **không ai giữ** (group inactive hoặc không được gán). `--state` xem coordinator + trạng thái (`Stable`/`PreparingRebalance`/`CompletingRebalance`/`Empty`/`Dead`), `--members --verbose` xem assignment. Không đo được lag cho consumer dùng `assign()` (không qua group).
- Hai góc nhìn lệch nhau: client `records-lag-max` theo **position đã fetch**; CLI theo **committed offset** (auto commit mỗi 5 s) → CLI luôn cao hơn/chậm hơn client một chút — **không phải lỗi**.
- Bảng nguyên nhân → xử lý (BẮT BUỘC thuộc):

| Triệu chứng | Nguyên nhân | Xử lý |
|---|---|---|
| Lag tăng đều trên **mọi** partition, `poll-idle-ratio-avg` ≈ 0 | Consumer **xử lý chậm** hơn tốc độ vào | Thêm consumer (tới **= số partition**), tối ưu code (batch, async I/O), giảm `max.poll.records` nếu vượt `max.poll.interval.ms` |
| Lag chỉ trên vài partition, `assigned-partitions` lệch | **Ít consumer hơn partition** → 1 consumer gánh nhiều | Thêm consumer instance (≤ số partition) |
| Consumer có `assigned-partitions=0`, lag vẫn cao | **Nhiều consumer hơn partition** → consumer dư idle | **Tăng partition** (cân nhắc phá key ordering) hoặc bớt consumer |
| Lag răng cưa, `rebalance-rate-per-hour` cao, log `group is rebalancing` | **Rebalance liên tục** (poll quá `max.poll.interval.ms`, session timeout, pod restart) | Static membership (`group.instance.id`), `CooperativeStickyAssignor`/KIP-848, tăng `max.poll.interval.ms`, giảm `max.poll.records` |
| Lag chỉ ở **1 partition** dù đủ consumer | **Key skew / hot partition** (1 key chiếm đa số) | Đổi key (thêm salt/sub-key), custom partitioner, tăng partition; **thêm consumer không giúp** |
| Lag tăng nhưng `records-consumed-rate` = 0, consumer "sống" | Consumer **kẹt** (poison pill, deadlock, chờ I/O ngoài) | Xem `last-poll-seconds-ago`, `time-between-poll-max`; DLQ record hỏng |
| Lag tăng "giả" với `read_committed` | Transaction mở lâu giữ **LSO** (Tuần 3) | Kiểm tra producer transactional treo, `transaction.timeout.ms` |
| `records-lead-min` → 0 | Consumer chậm tới mức **retention xoá data trước khi đọc** | Tăng `retention.ms` tạm thời + scale consumer ngay |

**7. Rebalance diagnostics — đọc log là biết**

| Log / Exception | Nghĩa | Fix |
|---|---|---|
| `Attempt to heartbeat failed since group is rebalancing` | Heartbeat thread thấy group đang rebalance → consumer phải rejoin | Bình thường khi thêm/bớt consumer; liên tục = storm |
| `CommitFailedException: ... the group has already rebalanced and assigned the partitions to another member. This means that the time between subsequent calls to poll() was longer than the configured max.poll.interval.ms` | Xử lý 1 batch quá **300 s** → bị đuổi khỏi group, commit bị từ chối | Giảm `max.poll.records` (500), tăng `max.poll.interval.ms`, đẩy xử lý nặng sang thread khác + `pause()`/`resume()` |
| `Member ... sending LeaveGroup request ... due to consumer poll timeout has expired` | Chính consumer tự rời vì poll quá lâu | Như trên |
| `Consumer group member ... has failed, removing it from the group` (coordinator) | Không heartbeat trong `session.timeout.ms` (45 s) | GC pause, network, pod bị kill; static membership để không rebalance khi restart nhanh |
| `rebalance-total` tăng mỗi lần deploy | Eager rebalance stop-the-world | `CooperativeStickyAssignor` hoặc `group.protocol=consumer` (KIP-848 — rebalance incremental, server-side) |

**8. Exception cheat-sheet — tên → nguyên nhân → fix (BẢNG BẮT BUỘC)**

| Exception | Phía | Retriable? | Nguyên nhân | Fix |
|---|---|---|---|---|
| `TimeoutException` (`Expiring N record(s)... since batch creation`) | Producer | Hết `delivery.timeout.ms` (120 s) | Broker chậm/unreachable, ISR thiếu, `max.block.ms` chờ metadata/buffer | Kiểm tra broker/URP, `advertised.listeners`; tăng `delivery.timeout.ms` sau cùng |
| `NotLeaderOrFollowerException` (4.0 đổi tên từ `NotLeaderForPartitionException`) | Producer/Consumer | ✅ | Leader đổi, metadata client cũ | Client tự refresh metadata + retry — không cần làm gì |
| `NotEnoughReplicasException` / `NotEnoughReplicasAfterAppendException` | Producer | ✅ | \|ISR\| < `min.insync.replicas` với `acks=all` | Khôi phục broker; đây là **đúng thiết kế** (thà chặn ghi hơn mất data) |
| `RecordTooLargeException` | Producer (hoặc consumer khi fetch) | ❌ | Record > `max.request.size` (1 MB) / `message.max.bytes` (1 048 588) / `max.message.bytes` | Tăng cả 3 + `replica.fetch.max.bytes` + `max.partition.fetch.bytes`; hoặc nén; hoặc claim-check |
| `OffsetOutOfRangeException` | Consumer | — | Offset commit/seek **không còn tồn tại** (retention xoá, topic tạo lại) | `auto.offset.reset=earliest|latest` (mặc định latest); `none` → ném exception để app tự xử |
| `CommitFailedException` | Consumer | ❌ | Rebalance đã gán partition cho member khác (poll quá `max.poll.interval.ms`) | Xem mục 7 |
| `UnknownTopicOrPartitionException` | Cả hai | ✅ | Topic chưa tồn tại / metadata cũ / `auto.create.topics.enable=false` | Tạo topic; kiểm tra tên; retry tự động |
| `LeaderNotAvailableException` | Cả hai | ✅ | Đang bầu leader (topic mới tạo, broker vừa chết) | Chờ + retry tự động |
| `TopicAuthorizationException` / `GroupAuthorizationException` / `ClusterAuthorizationException` | Cả hai | ❌ | Thiếu **ACL** (Tuần 7): `Write`/`Read` trên topic, `Read` trên group, `IdempotentWrite`/`Create` trên cluster | `kafka-acls.sh --add --allow-principal ...`; log `kafka-authorizer.log` |
| `SaslAuthenticationException` / `SslAuthenticationException` | Cả hai | ❌ | Sai credential SASL / cert không tin cậy / hostname mismatch | Sửa `sasl.jaas.config`, truststore, `ssl.endpoint.identification.algorithm` |
| `ProducerFencedException` / `InvalidProducerEpochException` | Producer (txn) | ❌ fatal | Producer khác cùng `transactional.id` đã `initTransactions()` → epoch cao hơn (zombie fencing) | **`close()`** producer, không retry/abort |
| `OutOfOrderSequenceException` | Producer (idempotent) | ❌ fatal | Broker nhận sequence không liên tục (mất batch giữa chừng, `max.in.flight` > 5 không idempotent) | Tạo producer mới; giữ mặc định idempotent |
| `SerializationException` / `RecordDeserializationException` | Producer (ném ngay tại `send()`) / **Consumer** (ném từ `poll()`) | ❌ | Dữ liệu không đúng format / schema ID lạ / **poison pill** | Consumer: **kẹt vòng lặp** vì offset không tiến — `seek(offset+1)`, gửi **DLQ topic** + header lý do, hoặc `ErrorHandlingDeserializer` (Spring) / `try/catch` quanh parse (kafkajs) |
| `KafkaStorageException` | Broker | — | Disk lỗi / `log.dirs` không ghi được → broker đánh dấu log dir offline | Thay đĩa, JBOD: partition trên đĩa đó offline, còn lại chạy |
| `InvalidReplicationFactorException` / `InvalidPartitionsException` | Admin | ❌ | RF > số broker; giảm partition | Sửa lệnh (RF ≤ broker; partition chỉ tăng) |

**9. Logging & tracing**

- Kafka 4.0 chuyển sang **Log4j2** (`config/log4j2.yaml`, KIP-653). File log broker: **`server.log`** (chính), **`state-change.log`** (mọi thay đổi leader/ISR/partition — đọc khi truy vết failover), **`controller.log`** (quorum, election, broker register/fence), **`kafka-authorizer.log`** (ACL: mặc định log **DENIED ở INFO**, ALLOWED ở DEBUG — bật để debug `TopicAuthorizationException`), `kafka-request.log` (request logger, DEBUG/TRACE **rất nặng**, chỉ bật ngắn), `log-cleaner.log` (compaction).
- Đổi log level **không restart**: `kafka-configs.sh --alter --entity-type broker-loggers --entity-name 2 --add-config kafka.request.logger=DEBUG` (đề hỏi "dynamic broker logger").
- **Tracing:** Kafka không có tracing sẵn; chuẩn là **OpenTelemetry** — Java agent tự instrument producer/consumer, **truyền context qua record headers** (`traceparent` W3C); `kafkajs` truyền tay header `traceparent`. Header **không** ảnh hưởng partition.

**10. Operations — thao tác vận hành đề hay hỏi**

- **Thêm broker mới ≠ tự nhận partition.** Broker mới chỉ nhận partition của **topic tạo sau đó**. Muốn cân bằng phải **`kafka-reassign-partitions.sh`** — 3 mode loại trừ nhau:
  1. `--generate --topics-to-move-json-file topics.json --broker-list 2,3,5` → in **current assignment** (lưu để rollback) + **proposed assignment**.
  2. `--execute --reassignment-json-file reassign.json [--throttle 50000000]` (byte/giây liên broker; sinh config động `leader.replication.throttled.rate`/`follower.replication.throttled.rate` + `*.replication.throttled.replicas` trên topic). Throttle < tốc độ ghi vào → **không bao giờ xong**. Đổi throttle giữa chừng: `--execute --additional --throttle N`.
  3. `--verify --reassignment-json-file reassign.json` → "completed successfully" **và gỡ throttle**. **Quên `--verify` = throttle còn nguyên**, replication thường cũng bị bóp.
  - Cùng tool: **tăng RF** (viết tay JSON thêm replica), **đổi log dir** (`log_dirs`, `--replica-alter-log-dirs-throttle`), decommission (reassign hết partition ra; 4.3 có `cordoned.log.dirs` KIP-1066 để controller không đặt partition mới lên broker sắp bỏ).
- **`kafka-leader-election.sh --election-type preferred|unclean --all-topic-partitions | --topic X --partition N | --path-to-json-file`**: `preferred` trả leader về replica **đầu danh sách** (sau rolling restart leader dồn về broker khởi động sớm); `auto.leader.rebalance.enable=true` tự làm mỗi `leader.imbalance.check.interval.seconds` (300) khi lệch > `leader.imbalance.per.broker.percentage` (10%). `unclean` = chấp nhận **mất data** để có leader cho partition offline.
- **Cruise Control** (LinkedIn, OSS): tự phân tích tải (CPU/disk/network/replica count) → sinh + thực thi reassignment theo **goal** (hard: rack-aware, capacity; soft: distribution), anomaly detection + self-healing (broker failure, goal violation, disk failure), REST API port **9090** (`/kafkacruisecontrol/rebalance`, `add_broker`, `remove_broker`, `demote_broker`). Confluent có **Self-Balancing Clusters**; Strimzi tích hợp Cruise Control; `Amazon MSK` có auto-rebalance. Đề: "tự động cân bằng partition khi thêm broker" → Cruise Control.
- **Partition: tăng được, giảm KHÔNG được.** `kafka-topics.sh --alter --partitions N` chỉ tăng; tăng → `hash(key) % N` đổi → **phá ordering theo key**, compaction "1 key 1 partition" sai, consumer `auto.offset.reset=latest` có thể bỏ lỡ message vào partition mới trước khi refresh metadata (`metadata.max.age.ms` 5 phút). **Không bao giờ** tăng partition topic nội bộ (`__consumer_offsets`, `__transaction_state`, `__share_group_state`). Giảm → tạo topic mới + migrate (MM2/Streams).
- **`kafka-delete-records.sh --offset-json-file`**: xoá record **từ đầu partition tới offset chỉ định** (dời log start offset) — không xoá lẻ ở giữa; `offset: -1` = xoá tới LEO. Dùng khi cần "purge" nhanh không đợi retention.
- **Rolling restart:** **1 broker/lần**; trước khi sang broker kế: chờ **`UnderReplicatedPartitions` = 0** trên toàn cluster (hoặc `kafka-topics.sh --describe --under-replicated-partitions` rỗng) và `ActiveControllerCount` = 1. `controlled.shutdown.enable=true` (mặc định): broker sync log + **chuyển leadership** trước khi tắt → downtime vài ms; chỉ thành công khi partition có replica khác sống. Sau vòng restart chạy preferred election. Restart controller (KRaft) cuối cùng; quorum 3 node chịu 1 lỗi.
- **Upgrade KRaft** (Tuần 1 ôn): rolling restart code mới → verify → **finalize** `kafka-features.sh --bootstrap-server ... upgrade --release-version 4.3` (hoặc `--metadata 4.3` / `--feature metadata.version=X`); xem `kafka-features.sh describe` (`metadata.version`, `kraft.version`, `group.version`, `share.version`, `eligible.leader.replicas.version`, `transaction.version`). `metadata.version` thay `inter.broker.protocol.version` cũ; **downgrade chỉ khi không có metadata change** giữa 2 version (4.3 = `IBP_4_3_IV0(30,...,true)` → không downgrade được; 4.2 `IBP_4_2_IV1(29,...,false)` → được). 4.x chỉ KRaft; ZK phải migrate qua **3.9** trước; upgrade lên 4.x cần metadata ≥ 3.3.
- **Tiered storage (KIP-405):**

| | Local tier | Remote tier |
|---|---|---|
| Ở đâu | Disk broker | S3 / HDFS / GCS qua plugin `RemoteStorageManager` (Kafka **không ship sẵn**; Aiven plugin, `LocalTieredStorage` test jar) |
| Chứa gì | Active segment + segment mới (tail read qua page cache) | **Segment đã đóng** đã upload; metadata trong topic nội bộ `__remote_log_metadata` |
| Config | Broker `remote.log.storage.system.enable=true` + `remote.log.storage.manager.class.name/path` + `remote.log.metadata.manager.listener.name` | Topic `remote.storage.enable=true`, **`local.retention.ms`/`local.retention.bytes`** (giữ local bao lâu, xoá local **chỉ sau khi upload**), `retention.ms`/`retention.bytes` = tổng (áp cho remote) |
| Lợi | Disk broker nhỏ, recovery/reassignment nhanh (chỉ copy local) | Retention "vô hạn", tách compute–storage |
| Hạn chế | — | **Không hỗ trợ compacted topic**; phải tắt trên mọi topic trước khi tắt broker; tắt topic: `remote.log.copy.disable=true` (read-only remote) hoặc `remote.storage.enable=false` + `remote.log.delete.on.disable=true` |

- **MirrorMaker 2 (MM2)** — xây trên **Kafka Connect**, MM1 **xoá ở 4.0**; replicate topic (data + config), consumer group + offset, ACL, giữ partitioning, tự phát hiện topic mới.

| Connector | Việc | Topic tạo ra |
|---|---|---|
| `MirrorSourceConnector` | Copy record (giữ partition), sync topic config + ACL, tạo topic đích | `<source>.<topic>` ở đích (theo policy); `mm2-offset-syncs.<target>.internal` (mặc định ở **source**) |
| `MirrorCheckpointConnector` | **Dịch offset** consumer group source → target; `sync.group.offsets.enabled=true` ghi thẳng vào `__consumer_offsets` đích (khi group ở đích **inactive**) | `<source>.checkpoints.internal` ở đích |
| `MirrorHeartbeatConnector` | Phát heartbeat để đo **liveness + latency end-to-end** | `heartbeats` ở đích (replicate tiếp thành `<source>.heartbeats`) |

  - Cấu hình `mm2.properties`: `clusters = A, B` + `A.bootstrap.servers`/`B.bootstrap.servers` + **`A->B.enabled = true`** (flow mặc định **tắt**) + `A->B.topics = orders.*`. Chạy `connect-mirror-maker.sh mm2.properties [--clusters B]` (dedicated mode; `--clusters <target>` = chỉ chạy herder có đích đó — best practice **"consume từ xa, produce gần"**: đặt MM2 cạnh cluster **đích**). Hoặc deploy 3 connector lên Connect cluster có sẵn qua REST.
  - **`DefaultReplicationPolicy`**: topic đích đổi tên **`A.orders`** (chống loop trong active/active, tránh ghi chung partition với producer local). **`IdentityReplicationPolicy`**: **giữ nguyên tên** — dùng cho migration / active-passive / thay MM1; **không chống loop → không dùng active/active**.
  - Pattern: active/passive `A->B`; active/active `A->B, B->A` (consumer đọc `orders` + `B.orders`); aggregation `A->K, B->K`; fan-out `K->A, K->B`. Failover: consumer dùng `RemoteClusterUtils.translateOffsets()` / offset đã sync để tiếp tục ở đích. Exactly-once (3.5+): `B.exactly.once.source.support=enabled`. Metric: `replication-latency-ms`, `record-age-ms`, `checkpoint-latency-ms` (`kafka.connect.mirror`).
- **Capacity planning:**
  - Số partition ≈ **max(T/P, T/C)** với T = throughput mục tiêu, P = throughput 1 partition (ghi ~10 MB/s tuỳ disk), C = throughput 1 consumer → thêm dư 20–30%, và **≥ số consumer dự kiến**. Quá nhiều partition: nhiều file mở, failover lâu, latency end-to-end tăng, producer buffer nhiều batch. Kinh nghiệm: ≤ **4 000 partition/broker**, ≤ 200 000/cluster thời ZK; KRaft nâng lên hàng triệu nhưng broker vẫn có giới hạn file handle/RAM.
  - **Disk** = throughput ghi × retention × **RF** (+ 30–40% headroom, + segment chưa xoá). Ví dụ 10 MB/s × 7 ngày × RF 3 ≈ 18 TB. Tiered storage giảm phần local còn `local.retention.*`.
  - Thread: `num.network.threads` **3**, `num.io.threads` **8** (≥ số đĩa), `num.replica.fetchers` **1** (tăng khi URP kéo dài vì follower không kịp), `num.recovery.threads.per.data.dir` **2**. **JBOD `log.dirs`** nhiều đĩa: partition mới đặt lên đĩa **ít partition nhất** (không theo dung lượng!) → có thể lệch; 1 đĩa lỗi → `KafkaStorageException`, chỉ partition trên đĩa đó offline.
  - **Key skew / hot partition**: 1 key chiếm đa số → 1 partition/1 consumer/1 broker quá tải; nhận diện qua `MessagesInPerSec,topic=X` lệch giữa broker + lag 1 partition; xử lý bằng key phức hợp (`userId#bucket`), custom partitioner tách key VIP, hoặc bỏ key nếu không cần ordering.

### 🅱️ Buổi B — Hands-on (~3.5h)

> 🧪 **Lab cầm tay chỉ việc (từng bước + lệnh + code):** [labs.md](labs.md). Dùng cluster 3 node Tuần 1 + file override `docker-compose.monitoring.yml` (Prometheus + Grafana + JMX Exporter).

- **Lab 8.1 ⭐ — JMX + Prometheus + Grafana:** mount `jmx_prometheus_javaagent.jar` + rules `kafka-jmx.yml` vào 3 broker qua `KAFKA_OPTS=-javaagent:...=7071:...`, thêm service `prometheus` + `grafana`; curl `/metrics` thấy `kafka_server_replicamanager_underreplicatedpartitions`; vẽ 4 panel PromQL.
- **Lab 8.2 ⭐ — Tạo lag & chẩn đoán:** `kafka-producer-perf-test.sh` 100k record, consumer `kafkajs` sleep 100 ms/record → `kcg --describe` LAG tăng; script `lag-watch.mjs` tính lag bằng Admin API; thêm instance → lag giảm; 5 consumer / 3 partition → 2 idle.
- **Lab 8.3 — URP & ISR shrink:** `docker stop kafka-3` → `UnderReplicatedPartitions` qua `JmxTool` và exporter; `IsrShrinksPerSec`; bật lại → về 0.
- **Lab 8.4 ⭐ — Partition reassignment:** topic 6 partition, giả lập decommission broker 4 bằng `--generate --broker-list 2,3`, `--execute --throttle 1000000`, `--verify`; rồi `kafka-leader-election.sh --election-type preferred`.
- **Lab 8.5 — Poison pill → DLQ:** gửi JSON hỏng, consumer `kafkajs` crash loop → fix try/catch + gửi `orders-dlq` với header lý do.
- **Lab 8.6 — MirrorMaker 2 local:** cluster B 1 node port 9192, `mm2.properties` `A->B.enabled=true`, `topics=orders.*` → thấy `A.orders`, `heartbeats`, `A.checkpoints.internal` ở B.
- **Lab 8.7 — Rolling restart + `kafka-features.sh describe`:** restart từng broker, chờ URP = 0, đọc `metadata.version`, `kraft.version`, `share.version`.

### 🅲️ Buổi C — Bổ sung (~2.5h)

**Bảng quyết định: triệu chứng → metric cần xem → hành động**

| Triệu chứng | Nhìn metric nào | Hành động |
|---|---|---|
| Producer `TimeoutException`, `record-error-rate` > 0 | `UnderMinIsrPartitionCount`, `OfflinePartitionsCount`, `request-latency-avg`, `RemoteTimeMs{Produce}` | Broker/ISR trước, sau đó `delivery.timeout.ms` |
| Producer throughput thấp | `batch-size-avg` vs 16 KB, `record-queue-time-avg`, `compression-rate-avg`, `produce-throttle-time-avg` | Tăng `linger.ms`/`batch.size`, bật nén, kiểm tra quota |
| Consumer lag tăng | `records-lag-max`, `poll-idle-ratio-avg`, `assigned-partitions`, `rebalance-rate-per-hour`, `records-lead-min` | Bảng mục 6 |
| Rebalance liên tục | `rebalance-total`, `failed-rebalance-total`, `time-between-poll-max` vs 300 s, log `CommitFailedException` | Static membership, cooperative/KIP-848, `max.poll.*` |
| Produce chậm dù broker rảnh | `RemoteTimeMs{Produce}` cao | Follower chậm (`acks=all`) → network liên broker / disk follower |
| Fetch "chậm" nhưng consumer vẫn kịp | `RemoteTimeMs{FetchConsumer}` ≈ `fetch.max.wait.ms` | **Bình thường** (chờ `fetch.min.bytes`) |
| Broker CPU cao, request chậm | `RequestHandlerAvgIdlePercent` < 0.3, `RequestQueueSize`, `RequestQueueTimeMs` | Tăng `num.io.threads`, giảm tải, thêm broker |
| Sau rolling restart, 1 broker gánh hết leader | `LeaderCount` lệch | `kafka-leader-election.sh --election-type preferred --all-topic-partitions` |
| Thêm broker mới nhưng vẫn rỗng | `PartitionCount` broker mới = 0 | `kafka-reassign-partitions.sh` / Cruise Control |
| Disk đầy nhanh | `Size` per partition (`kafka-log-dirs.sh`), `BytesInPerSec` | Giảm `retention.*`, tiered storage, `kafka-delete-records.sh` |
| `UncleanLeaderElectionsPerSec` > 0 | — | Ai đó bật `unclean.leader.election.enable` → xem lại durability |

**So sánh nhanh công cụ vận hành**

| Việc | Tool | Tham số nhớ |
|---|---|---|
| Cân bằng partition khi thêm/bớt broker | `kafka-reassign-partitions.sh` | `--generate` / `--execute --throttle` / `--verify` (gỡ throttle) |
| Tự động cân bằng + self-healing | Cruise Control (LinkedIn) | REST `:9090/kafkacruisecontrol/rebalance` |
| Trả leader về preferred | `kafka-leader-election.sh` | `--election-type preferred --all-topic-partitions` |
| Partition offline, chấp nhận mất data | `kafka-leader-election.sh` | `--election-type unclean` |
| Purge record | `kafka-delete-records.sh` | `--offset-json-file` (offset -1 = tới LEO) |
| Xem/đặt feature & metadata version | `kafka-features.sh` | `describe` / `upgrade --release-version 4.3` |
| Sao chép cluster/DR | MirrorMaker 2 | `connect-mirror-maker.sh mm2.properties --clusters B` |
| Lag group | `kafka-consumer-groups.sh` | `--describe --group` / `--reset-offsets ... --execute` (group inactive) |
| Đổi log level không restart | `kafka-configs.sh` | `--entity-type broker-loggers --add-config kafka.request.logger=DEBUG` |
| Dung lượng partition per broker | `kafka-log-dirs.sh` | `--describe --topic-list X` |

**Đọc thêm (30–40 phút):** *Kafka: The Definitive Guide* 2nd ed. — Chương 12 (Administering Kafka), Chương 13 (Monitoring Kafka — bảng metric, request latency), Chương 10 (Cross-Cluster Data Mirroring — MM2); Confluent Developer course *Kafka Internals* (Request processing) và blog "Monitoring Kafka Performance Metrics" (Datadog, 3 phần); KIP-405 Tiered Storage; KIP-382 MirrorMaker 2.0.

### 🅳 Buổi D — Practice + Review (~2h) ⭐ CHECKPOINT

> 📝 **Bộ câu hỏi luyện tập của tuần:** [questions.md](questions.md) — đáp án & giải thích: [answers.md](answers.md). *(bằng tiếng Anh — văn phong đề CCDAK.)*

- Làm **28 câu** của tuần không tra tài liệu, chấm bằng answer key; mỗi câu sai → quay lại đúng bảng ở Buổi A và **ghi sổ** (nhầm metric? nhầm tool? nhầm ngưỡng?).
- **⭐ MINI-MOCK TOÀN DOMAIN (~40 câu, 60 phút):** trộn ngẫu nhiên 5 câu/tuần từ `questions.md` Tuần 1→8 (ưu tiên câu đã sai trước đó) — tỉ lệ gợi ý FUND 9 · DEV 11 · CONNECT 6 · STREAMS 5 · TEST 3 · OBS 6. Chấm theo domain, ghi domain nào < 60%.
- Tự vẽ lại **từ trí nhớ**: sơ đồ 5 pha `TotalTimeMs`; bảng 3 connector MM2; luồng `--generate → --execute --throttle → --verify`.
- **Spaced repetition** mốc **1 / 3 / 7 ngày** cho bộ số: 0.3 idle · 300 s poll · 45 s session · 30 s replica lag · 7071 · 9999 · 9090 (Cruise Control) · 16 KB batch · 32 MB buffer · 4 000 partition/broker · `A.topic`.
- Chỉ sang Tuần 9 khi mini-mock **≥72%** và **không domain nào < 60%**. Domain yếu → ôn README tuần đó trước.

## 🧠 PHẢI NHỚ tuần này

| Fact | Con số / Ghi nhớ |
|---|---|
| Bật remote JMX | Biến môi trường **`JMX_PORT`** (thường 9999/9101); bảo mật qua **`KAFKA_JMX_OPTS`**; mặc định **tắt** và **không auth** |
| JMX Exporter | Java agent `-javaagent:jmx_prometheus_javaagent.jar=**7071**:rules.yml` → `/metrics` cho Prometheus; rules = regex `pattern` → `name`/`labels` |
| `UnderReplicatedPartitions` | `kafka.server:type=ReplicaManager`; bình thường **0**; >0 = follower tụt / broker chết |
| `UnderMinIsrPartitionCount` | **0**; >0 = producer `acks=all` bị chặn (`NotEnoughReplicas`) |
| `OfflinePartitionsCount` | `kafka.controller:type=KafkaController`; **0**; >0 = partition không leader → **mất availability** |
| `ActiveControllerCount` | Tổng toàn cluster **đúng 1** |
| `RequestHandlerAvgIdlePercent` / `NetworkProcessorAvgIdlePercent` | 0–1; **> 0.3**; <0.3 → tăng `num.io.threads` (**8**) / `num.network.threads` (**3**) |
| `TotalTimeMs` = 5 pha | `RequestQueue` + `Local` + **`Remote`** + `ResponseQueue` + `ResponseSend`; Remote{Produce} = chờ follower `acks=all`; Remote{Fetch} = chờ `fetch.min.bytes` (bình thường) |
| `UncleanLeaderElectionsPerSec` | **0 tuyệt đối** |
| Heap vs page cache | Heap broker ~**6 GB** đủ; **page cache quan trọng hơn heap** |
| Producer `batch-size-avg` nhỏ | Batch không đầy 16 KB → **tăng `linger.ms`** (5 ms) |
| `compression-rate-avg` | Nén / gốc → **nhỏ = tốt**; 1.0 = không nén |
| `produce-throttle-time-avg` / `fetch-throttle-time-avg` | >0 = **quota** (`producer_byte_rate`/`consumer_byte_rate`), không phải mạng |
| `records-lag-max` vs CLI LAG | Client theo **position đã fetch**; CLI theo **committed offset** → CLI cao hơn một chút là bình thường |
| `records-lead-min` → 0 | Sắp **mất data vì retention** xoá trước khi đọc |
| `time-between-poll-max` | So với `max.poll.interval.ms` = **300 000 ms**; vượt → `CommitFailedException` + rebalance |
| `poll-idle-ratio-avg` | ≈1 consumer rảnh; **≈0 user code chậm** |
| Lag | **LEO − committed offset**; `kcg --describe`: `CURRENT-OFFSET`, `LOG-END-OFFSET`, `LAG`, `CONSUMER-ID` = `-` là không ai giữ; không đo được với `assign()` |
| Consumer ↔ partition | Consumer hữu ích **≤ số partition**; 5 consumer / 3 partition → **2 idle**; hot partition → **thêm consumer không giúp** |
| Poison pill | `SerializationException` ở consumer → **kẹt vòng lặp** (offset không tiến) → seek qua / **DLQ + header lý do** / `ErrorHandlingDeserializer` |
| `OffsetOutOfRangeException` | Offset không còn (retention) → `auto.offset.reset` (**latest** mặc định / earliest / none) |
| Thêm broker | **Không tự nhận partition** → `kafka-reassign-partitions.sh --generate/--execute --throttle/--verify`; **`--verify` mới gỡ throttle** |
| Partition | **Tăng được, giảm KHÔNG** (phá `hash(key) % N`); không đụng topic nội bộ |
| Leader election | `kafka-leader-election.sh --election-type **preferred**\|**unclean**`; auto rebalance mỗi **300 s**, lệch > **10%** |
| Rolling restart | **1 broker/lần**, chờ **URP = 0**, `controlled.shutdown.enable=true` chuyển leader trước khi tắt |
| Upgrade | Rolling code → `kafka-features.sh upgrade --release-version 4.3`; `metadata.version` thay IBP; downgrade chỉ khi **không có metadata change** |
| Tiered storage | Broker `remote.log.storage.system.enable` + plugin; topic `remote.storage.enable=true` + **`local.retention.ms/bytes`**; **không hỗ trợ compacted topic**; chỉ tier segment **đã đóng** |
| MM2 | 3 connector **Source / Checkpoint / Heartbeat** trên Connect; `A->B.enabled=true`; `DefaultReplicationPolicy` → **`A.topic`**, `IdentityReplicationPolicy` giữ tên (không cho active/active); `connect-mirror-maker.sh mm2.properties --clusters B`; MM1 xoá ở 4.0 |
| Cruise Control | LinkedIn, goal-based rebalance + anomaly detection + self-healing, REST **9090** |
| Capacity | partition ≈ **max(T/P, T/C)**; disk = **throughput × retention × RF** (+30–40%); ≤ ~4 000 partition/broker; `num.replica.fetchers` **1** (tăng khi URP kéo dài) |
| Log files | `server.log`, **`state-change.log`** (leader/ISR), `controller.log`, **`kafka-authorizer.log`** (ACL denied), Log4j2 từ 4.0; đổi level động qua `broker-loggers` |

## ⚠️ Bẫy đề hay gặp

- Thấy "`RemoteTimeMs` cao cho FetchConsumer" → dễ chọn "follower chậm / network", nhưng đúng là **broker chờ `fetch.min.bytes`/`fetch.max.wait.ms` — bình thường**; RemoteTime chỉ đáng lo với **Produce** (`acks=all` chờ ISR).
- Thấy "producer `TimeoutException`" → dễ chọn tăng `request.timeout.ms`, nhưng đúng là kiểm tra **`UnderMinIsrPartitionCount`/`OfflinePartitionsCount`** trước; timeout là triệu chứng, ISR thiếu là bệnh.
- Thấy "lag cao trên 1 partition duy nhất, đã thêm consumer" → dễ chọn thêm nữa, nhưng đúng là **key skew / hot partition** — sửa **key/partitioner**, không phải số consumer.
- Thấy "5 consumer, 3 partition, lag vẫn tăng" → dễ nghĩ consumer chậm, nhưng **2 consumer idle**; đúng là **tăng partition** (hoặc tối ưu 3 consumer đang chạy).
- Thấy "`records-lag-max` = 0 nhưng `kcg --describe` LAG = 200" → dễ nghĩ lỗi tool, nhưng đúng là **client tính theo position đã fetch, CLI theo committed offset** (auto commit 5 s).
- Thấy "`CommitFailedException`" → dễ chọn tăng `session.timeout.ms`, nhưng đúng là **poll quá `max.poll.interval.ms` (300 s)** → giảm `max.poll.records` / tăng `max.poll.interval.ms`; `session.timeout.ms` liên quan **heartbeat**, không liên quan xử lý chậm.
- Thấy "consumer đọc record hỏng, crash, restart, crash lại" → dễ chọn `auto.offset.reset=latest`, nhưng offset đã commit rồi nên reset không có tác dụng; đúng là **DLQ / seek qua / `ErrorHandlingDeserializer`** — poison pill.
- Thấy "thêm broker mới, cluster vẫn lệch tải" → dễ nghĩ Kafka tự cân bằng, nhưng đúng là **phải `kafka-reassign-partitions.sh`** (hoặc Cruise Control); chỉ topic **mới** mới lên broker mới.
- Thấy "reassignment đã xong nhưng replication vẫn chậm" → dễ nghĩ disk, nhưng đúng là **quên `--verify` → throttle còn nguyên**.
- Thấy "throttle 1 MB/s, topic ghi vào 5 MB/s, reassignment mãi không xong" → đúng là **throttle < tốc độ ghi → không bao giờ bắt kịp**; tăng throttle (`--additional --execute --throttle`).
- Thấy "cần giảm partition từ 12 xuống 6" → dễ chọn `--alter --partitions 6`, nhưng **không giảm được**; tạo topic mới + migrate.
- Thấy "sau rolling restart, broker đầu tiên khởi động gánh hết leader" → dễ chọn reassign partition, nhưng đúng là **`kafka-leader-election.sh --election-type preferred`** (replica không đổi, chỉ leader).
- Thấy "rolling restart 3 broker cùng lúc để nhanh" → sai: **1 broker/lần, chờ URP = 0** giữa mỗi lần; RF=3/min.isr=2 chỉ chịu 1 broker vắng.
- Thấy "bật tiered storage cho topic compacted `__consumer_offsets`/changelog" → **không hỗ trợ compacted topic**.
- Thấy "MM2 active/active, muốn topic giữ nguyên tên" → dễ chọn `IdentityReplicationPolicy`, nhưng nó **không chống loop** → chỉ dùng active/passive/migration; active/active phải `DefaultReplicationPolicy` (`A.topic`).
- Thấy "MM2 cần cluster Connect riêng" → không bắt buộc: `connect-mirror-maker.sh` chạy **dedicated mode** tự dựng worker; cũng có thể deploy 3 connector lên Connect có sẵn.
- Thấy "downgrade metadata 4.3 → 4.2" → dễ nghĩ được như rollback code, nhưng **4.3 có metadata change → không downgrade được**.
- Thấy "tăng heap broker lên 32 GB để nhanh hơn" → sai hướng: heap ~6 GB, **RAM còn lại cho page cache**; heap to → GC pause dài → ISR shrink.
- Thấy "`ActiveControllerCount` = 1 trên **mỗi** broker" → sai: **tổng** = 1, chỉ **1 node** có giá trị 1.

## 🔁 Phản xạ nhanh (keyword → đáp án)

| Thấy từ khoá | Bật ngay |
|---|---|
| "enable remote JMX on broker" | **`JMX_PORT`** env (+ `KAFKA_JMX_OPTS` cho auth/SSL) |
| "scrape Kafka metrics into Prometheus" | **JMX Exporter javaagent** (`-javaagent:...=7071:rules.yml`) |
| "partition has no leader" | **`OfflinePartitionsCount`** > 0 |
| "follower out of sync / replica lagging" | **`UnderReplicatedPartitions`** > 0 |
| "`acks=all` producers failing, ISR shrunk" | **`UnderMinIsrPartitionCount`** > 0 → `NotEnoughReplicasException` |
| "two brokers think they are controller / no controller" | **`ActiveControllerCount`** ≠ 1 |
| "request handler idle < 30%" | Tăng **`num.io.threads`** |
| "produce latency dominated by RemoteTimeMs" | Chờ **follower ack (`acks=all`)** |
| "fetch RemoteTimeMs ≈ 500 ms, consumer fine" | **`fetch.min.bytes`/`fetch.max.wait.ms`** — bình thường |
| "batch-size-avg ≪ batch.size" | **Tăng `linger.ms`** |
| "produce-throttle-time-avg > 0" | **Quota** `producer_byte_rate` |
| "records-lead-min approaching 0" | **Sắp mất data vì retention** |
| "time-between-poll-max near 300000" | **Sắp vượt `max.poll.interval.ms`** → `CommitFailedException` |
| "poll-idle-ratio ≈ 0" | **Xử lý chậm** trong user code |
| "LAG grows, CONSUMER-ID is `-`" | **Không consumer nào giữ partition** (group chết/inactive) |
| "lag on one partition only" | **Hot key / key skew** → đổi key/partitioner |
| "more consumers than partitions" | **Idle consumers** → tăng partition |
| "consumer crash-loops on one record" | **Poison pill** → DLQ / seek / `ErrorHandlingDeserializer` |
| "offset no longer exists" | **`OffsetOutOfRangeException`** → `auto.offset.reset` |
| "`Attempt to heartbeat failed since group is rebalancing`" | Rebalance đang diễn ra → static membership / cooperative nếu liên tục |
| "new broker receives no partitions" | **`kafka-reassign-partitions.sh`** (`--generate/--execute/--verify`) |
| "limit bandwidth during reassignment" | **`--throttle`** (B/s), gỡ bằng **`--verify`** |
| "automatically rebalance + self-heal" | **Cruise Control** |
| "restore leadership after restart" | **`kafka-leader-election.sh --election-type preferred`** |
| "offline partition, accept data loss" | **`--election-type unclean`** |
| "purge topic data now" | **`kafka-delete-records.sh`** |
| "finalize upgrade / set metadata version" | **`kafka-features.sh upgrade --release-version 4.3`** |
| "graceful broker shutdown moves leaders" | **`controlled.shutdown.enable=true`** |
| "infinite retention, small broker disk" | **Tiered storage** (`remote.storage.enable`, `local.retention.ms`) |
| "replicate topics + consumer offsets to DR cluster" | **MirrorMaker 2** (`MirrorSource` + `MirrorCheckpoint` + `MirrorHeartbeat`) |
| "topic appears as `A.orders` on target" | **`DefaultReplicationPolicy`** |
| "keep topic names during migration" | **`IdentityReplicationPolicy`** (không active/active) |
| "who changed leader/ISR at 03:00?" | **`state-change.log`** |
| "why `TopicAuthorizationException`?" | **`kafka-authorizer.log`** |
| "trace a message across services" | **OpenTelemetry**, context trong **record headers** |
| "how many partitions for 100 MB/s" | **max(T/P, T/C)** + dư 20–30% |

## 🧪 Lab checklist

- [ ] Lab 8.1 ⭐ — `docker-compose.monitoring.yml` lên; `curl localhost:7071/metrics | grep underreplicated` trả 0; Prometheus 3 target UP; Grafana vẽ được `BytesInPerSec` và `TotalTimeMs{request="Produce"}`.
- [ ] Lab 8.2 ⭐ — `kcg --describe` thấy LAG ~100k rồi giảm khi thêm consumer; `lag-watch.mjs` in lag khớp CLI; 5 consumer / 3 partition → 2 dòng `partitions=[]`.
- [ ] Lab 8.3 — `docker stop kafka-3` → `UnderReplicatedPartitions` > 0 (JmxTool + exporter + Grafana), `IsrShrinksPerSec` nhích; `docker start` → về 0.
- [ ] Lab 8.4 ⭐ — `--generate` in current + proposed; `--execute --throttle 1000000` thấy config `leader.replication.throttled.rate`; `--verify` báo completed + gỡ throttle; broker 4 không còn replica; preferred election trả leader.
- [ ] Lab 8.5 — Consumer v1 crash loop trên record hỏng; v2 gửi vào `orders-dlq` với header `error`, `originalTopic`, `originalPartition`, `originalOffset`, `failedAt` rồi đi tiếp.
- [ ] Lab 8.6 — Cluster B nhận `A.orders` (đủ số record), có `heartbeats`, `A.checkpoints.internal`; offset group được dịch sang B.
- [ ] Lab 8.7 — Rolling restart 3 broker không có message lỗi ở producer; `kafka-features.sh describe` đọc được `metadata.version`/`kraft.version`/`share.version`.

## 🚪 Cổng tự kiểm tra (phải trả lời trôi chảy mới sang tuần sau)

- **Ba metric broker nào phải alert ngay và giá trị bình thường của chúng?**
  **Đáp án gọn:** `UnderReplicatedPartitions` = 0, `OfflinePartitionsCount` = 0, `ActiveControllerCount` tổng = 1 (thêm `UnderMinIsrPartitionCount` = 0, `UncleanLeaderElectionsPerSec` = 0).
- **Produce request có `RemoteTimeMs` cao nghĩa là gì? Còn với Fetch?**
  **Đáp án gọn:** Produce: leader chờ follower trong ISR ghi xong vì `acks=all` → follower/network chậm. Fetch: broker chờ đủ `fetch.min.bytes` tới `fetch.max.wait.ms` → bình thường.
- **Consumer lag tính thế nào và 4 nguyên nhân chính → xử lý?**
  **Đáp án gọn:** LEO − committed offset. Consumer chậm → thêm consumer/tối ưu code; ít consumer hơn partition → thêm consumer; nhiều consumer hơn partition → tăng partition; rebalance liên tục → static membership/cooperative + `max.poll.*`; key skew → đổi key (thêm consumer không giúp).
- **Consumer gặp `SerializationException` trên 1 record thì chuyện gì xảy ra và fix ra sao?**
  **Đáp án gọn:** Offset không tiến → poll lại đúng record đó → kẹt vòng lặp (poison pill). Fix: seek qua offset, gửi DLQ topic kèm header lý do, hoặc `ErrorHandlingDeserializer`/try-catch quanh parse.
- **Thêm 1 broker vào cluster, cần làm gì để nó nhận tải? Nêu 3 bước và bẫy.**
  **Đáp án gọn:** `kafka-reassign-partitions.sh --generate` (lấy proposed) → `--execute --throttle N` → `--verify` (xác nhận + **gỡ throttle**). Bẫy: quên `--verify` để throttle lại; throttle < tốc độ ghi thì không xong; hoặc dùng Cruise Control.
- **Vì sao không giảm được partition? Tăng partition có hại gì?**
  **Đáp án gọn:** Không có cơ chế merge log; tăng làm `hash(key) % N` đổi → phá ordering theo key, compaction sai, consumer `latest` có thể bỏ lỡ message vào partition mới.
- **MM2 gồm connector nào, topic đích tên gì, khi nào dùng `IdentityReplicationPolicy`?**
  **Đáp án gọn:** `MirrorSourceConnector` (data + config + ACL), `MirrorCheckpointConnector` (dịch offset group), `MirrorHeartbeatConnector` (latency). Mặc định `A.orders` (`DefaultReplicationPolicy`, chống loop). Identity giữ nguyên tên — chỉ active/passive/migration, không active/active.
- **Rolling restart / upgrade đúng cách?**
  **Đáp án gọn:** 1 broker/lần, `controlled.shutdown.enable=true` chuyển leader, chờ URP = 0 trước broker kế; sau vòng: preferred election; upgrade thì finalize `kafka-features.sh upgrade --release-version 4.3`, nhớ downgrade chỉ khi không có metadata change.
- **⭐ CHECKPOINT:** đã đạt **≥72%** mini-mock toàn domain (Tuần 1–8) và không domain nào < 60%? Nếu chưa → **KHÔNG** sang Tuần 9, ôn domain yếu trước.

## 📎 Tài nguyên tuần này

> 📂 **Đã crawl sẵn tài liệu chính thức vào** [`resources/`](resources/INDEX.md) — đọc offline được.

- Apache Kafka Docs: [Operations — Monitoring](https://kafka.apache.org/43/operations/monitoring/) (JMX, broker/producer/consumer/Connect/Streams metrics, KRaft metrics) · [Basic Kafka Operations](https://kafka.apache.org/43/operations/basic-kafka-operations/) (consumer groups, expanding cluster, reassignment, throttling, graceful shutdown, leader balancing) · [Geo-Replication (MirrorMaker 2)](https://kafka.apache.org/43/operations/geo-replication-cross-cluster-data-mirroring/) · [Tiered Storage](https://kafka.apache.org/43/operations/tiered-storage/) · [Upgrading](https://kafka.apache.org/43/getting-started/upgrade/) (rolling upgrade KRaft, `kafka-features.sh`, notable changes 4.x).
- KIP: [KIP-405 Tiered Storage](https://cwiki.apache.org/confluence/display/KAFKA/KIP-405%3A+Kafka+Tiered+Storage) · [KIP-382 MirrorMaker 2.0](https://cwiki.apache.org/confluence/display/KAFKA/KIP-382%3A+MirrorMaker+2.0) · [KIP-92 records-lead metric](https://cwiki.apache.org/confluence/display/KAFKA/KIP-92+-+Add+per+partition+lag+metrics+to+KafkaConsumer) · KIP-1066 cordoned log dirs.
- Confluent: [Monitor Consumer Lag](https://docs.confluent.io/platform/current/monitor/monitor-consumer-lag.html) · [Kafka Monitoring (JMX)](https://docs.confluent.io/platform/current/kafka/monitoring.html) · [Kafka Connect Monitoring](https://docs.confluent.io/platform/current/connect/monitoring.html) · Confluent Developer *Kafka Internals* (Request processing, Replication).
- Công cụ: [Prometheus JMX Exporter](https://github.com/prometheus/jmx_exporter) (README + example `kafka-2_0_0.yml` rules) · [LinkedIn Cruise Control](https://github.com/linkedin/cruise-control) · [Burrow](https://github.com/linkedin/Burrow) · [kafka-lag-exporter](https://github.com/seglo/kafka-lag-exporter) · Datadog blog *Monitoring Kafka performance metrics* (3 phần).
- Khoá học: Confluent Developer — *Kafka Internals* + *Apache Kafka 101* (Consumer lag); Stephane Maarek — *Apache Kafka Series: Kafka Monitoring & Operations* và *Kafka Cluster Setup & Administration*; sách *Kafka: The Definitive Guide* 2nd ed. — Ch.10 Cross-Cluster Data Mirroring, Ch.12 Administering Kafka, Ch.13 Monitoring Kafka.

## ✅ Checklist hoàn thành Tuần 8

- [ ] Hoàn thành 4 buổi A/B/C/D
- [ ] Thuộc lòng bảng "PHẢI NHỚ" (đặc biệt 4 metric sống còn, 5 pha `TotalTimeMs`, 3 connector MM2, bộ lệnh reassign)
- [ ] Tự viết lại bằng trí nhớ: bảng exception → fix (≥10 dòng), bảng lag nguyên nhân → xử lý (≥5 dòng)
- [ ] Hoàn thành 7 lab (8.1, 8.2, 8.4 bắt buộc), giữ `docker-compose.monitoring.yml` cho Tuần 9–10
- [ ] Làm xong 28 câu [questions.md](questions.md), xem lại 100% câu sai
- [ ] **Đạt ≥72% MINI-MOCK toàn domain (Tuần 1–8), không domain nào < 60%** — CHECKPOINT
- [ ] Vượt Cổng tự kiểm tra (9 câu)
