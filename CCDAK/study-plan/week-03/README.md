# 🟦 Tuần 3 — Producer chuyên sâu + Transactions (EOS phía producer)

> **Domain CCDAK:** Application Development (28%) · **Thời lượng:** ~11h (4 buổi) · **Vị trí:** Tuần 3/10 — tuần "nặng điểm" nhất cùng Tuần 4 (Consumer), không có checkpoint nhưng là nền của mini-mock Tuần 4
>
> **Điều hướng:** [⬅️ Tuần 2](../week-02/README.md) · [🏠 Kế hoạch tổng](../../CCDAK-STUDY-PLAN.md) · [Tuần 4 ➡️](../week-04/README.md)

## 🎯 Mục tiêu tuần này

- **Vẽ lại được** đường đi của 1 record trong producer: `send()` → `Serializer` → `Partitioner` → `RecordAccumulator` (batch theo partition) → `Sender` thread → leader broker → callback.
- **Phân biệt được** `acks=0/1/all` theo trục latency ↔ durability và ghép đúng với `min.insync.replicas` (ôn Tuần 2).
- **Cấu hình được** retry an toàn: `retries`, `delivery.timeout.ms` ≥ `linger.ms` + `request.timeout.ms`, `retry.backoff.ms`; đọc tên exception biết ngay retriable hay fatal.
- **Giải thích được** idempotent producer (PID + sequence number) chống duplicate + giữ order khi retry, và vì sao ràng buộc `max.in.flight.requests.per.connection ≤ 5`, `acks=all`.
- **Tự tay** đo tác dụng của `linger.ms` / `batch.size` / `compression.type` bằng `kafka-producer-perf-test.sh` và giải thích số liệu.
- **Viết được** consume-transform-produce với `transactional.id`, `sendOffsetsToTransaction`, consumer `isolation.level=read_committed`; nói rõ giới hạn EOS khi sink nằm ngoài Kafka.
- **Thuộc** bảng defaults Kafka 4.3 của producer (đề CCDAK hỏi theo tên config Java, dù bạn code bằng `kafkajs`).

## 📚 Nội dung học chi tiết

### 🅰️ Buổi A — Lý thuyết (~3h)

**1. Kiến trúc producer — đường đi của 1 record**

```
ProducerRecord(topic, [partition], [key], value, [headers], [timestamp])
   │  producer.send(record, callback)  → trả Future<RecordMetadata> NGAY (async)
   ▼
key.serializer / value.serializer  → byte[]           (SerializationException = fatal, ném NGAY tại send())
   ▼
Partitioner  → chọn partition (record.partition > key hash murmur2 > sticky khi key=null)
   ▼
RecordAccumulator  → 1 deque batch / partition, mỗi batch ≤ batch.size, chờ tối đa linger.ms
   ▼
Sender thread (1 I/O thread nền)  → gom batch cùng leader thành ProduceRequest ≤ max.request.size
   ▼
Leader broker  → ghi log, chờ theo acks → trả offset/timestamp hoặc lỗi
   ▼
Callback / Future hoàn tất (thứ tự callback trong CÙNG partition được đảm bảo)
```

- **`send()` là async**: chỉ đưa record vào buffer rồi return. Có 2 trường hợp **block**: (1) chưa có metadata topic (lần đầu gửi) → chờ tối đa `max.block.ms` = **60.000 ms**; (2) buffer đầy (`buffer.memory` = **32 MB**) → block tối đa `max.block.ms`, hết thì `BufferExhaustedException`/`TimeoutException`.
- 3 kiểu gửi: **fire-and-forget** (không xem kết quả — có thể mất), **synchronous** (`send().get()` — chậm, 1 record/lần), **asynchronous + callback** (`Callback.onCompletion(RecordMetadata, Exception)` — chuẩn production). Callback chạy trên **I/O thread** → phải nhanh, không block.
- `flush()`: block tới khi toàn bộ batch đang chờ được gửi xong (không đóng producer). `close()`/`close(Duration)`: flush + đóng; `close(0)` = drop batch chưa gửi.
- **Thread-safety:** `KafkaProducer` **thread-safe**, 1 instance dùng chung nhiều thread **nhanh hơn** nhiều instance (share batch + connection). `KafkaConsumer` thì ngược lại (Tuần 4).
- `RecordMetadata` gồm topic, partition, offset, timestamp. Nếu `acks=0` → **offset = -1** (không chờ broker).
- `partitionsFor(topic)` để **preload metadata** giảm latency lần gửi đầu; metadata topic idle bị xoá sau `metadata.max.idle.ms` (5 phút); refresh cưỡng bức mỗi `metadata.max.age.ms` (**300.000 ms**).

**2. `acks` + `min.insync.replicas` (ôn Tuần 2, nhưng đề hỏi theo góc producer)**

| `acks` | Producer chờ gì | Latency | Durability | Bẫy |
|---|---|---|---|---|
| `0` | Không chờ gì (gửi xong coi như OK) | Thấp nhất | Mất data khi broker/network lỗi; `retries` **vô nghĩa** vì không biết lỗi; offset trong metadata = -1 | Không dùng được với idempotence |
| `1` | Leader ghi xong log cục bộ | Trung bình | Mất data nếu leader chết **trước** khi follower fetch | Đề gọi là "leader acknowledgement" |
| `all` / `-1` (**mặc định từ 3.0**) | Tất cả replica **trong ISR** ghi xong (không phải tất cả replica) | Cao nhất | Không mất khi ≥1 ISR còn sống; **chỉ có ý nghĩa khi `min.insync.replicas` ≥ 2** | ISR co còn 1 → `acks=all` = `acks=1`; ISR < min.isr → `NotEnoughReplicasException` (retriable) |

- Công thức chuẩn production: **RF=3 + `min.insync.replicas=2` + `acks=all`** → chịu được 1 broker chết mà vẫn ghi được, chịu 2 broker chết mà không mất data (ngừng ghi).
- `acks` được set **trên producer**, `min.insync.replicas` set **trên broker/topic** — đề hay hỏi "sửa ở đâu".

**3. Retry & timeout — chuỗi thời gian phải nhớ**

- `retries` mặc định **Integer.MAX_VALUE** (2.147.483.647) → thực tế **`delivery.timeout.ms` mới là giới hạn**: **120.000 ms** (2 phút), là tổng thời gian tối đa từ khi `send()` return đến khi báo thành công/thất bại (gồm thời gian chờ trong batch + gửi + retry).
- Ràng buộc bắt buộc: **`delivery.timeout.ms` ≥ `linger.ms` + `request.timeout.ms`** (mặc định 120.000 ≥ 5 + 30.000). Vi phạm → producer **ném `ConfigException` ngay lúc khởi tạo**.
- `request.timeout.ms` = **30.000 ms**: thời gian chờ **1 response** từ broker; hết → coi request đó thất bại → retry (nếu còn `delivery.timeout.ms`).
- `retry.backoff.ms` = **100 ms** (khởi điểm), tăng exponential tới `retry.backoff.max.ms` = **1.000 ms** (KIP-580).
- Hết `delivery.timeout.ms` → callback nhận **`TimeoutException`** ("Expiring N record(s) for topic-partition: ... ms has passed since batch creation") — đây là exception đặc trưng khi broker chậm/không reachable.
- **Retriable vs non-retriable (fatal):**

| Loại | Exception tiêu biểu | Producer làm gì | Ứng xử của bạn |
|---|---|---|---|
| **Retriable** (`RetriableException`) | `NotLeaderOrFollowerException` (leader đổi), `NotEnoughReplicasException` / `NotEnoughReplicasAfterAppendException` (ISR < min.isr), `NetworkException`, `TimeoutException` (request), `UnknownTopicOrPartitionException` (metadata cũ), `LeaderNotAvailableException`, `CorruptRecordException` | Tự retry tới hết `delivery.timeout.ms`, refresh metadata | Không code retry thủ công (sẽ tạo duplicate nếu không idempotent) |
| **Non-retriable (fatal)** | `RecordTooLargeException` (> `max.request.size` phía client hoặc > `message.max.bytes` phía broker), `SerializationException` (ném **đồng bộ** tại `send()`), `InvalidTopicException`, `TopicAuthorizationException` / `ClusterAuthorizationException`, `InvalidRequiredAcksException`, `UnsupportedVersionException` | Báo lỗi ngay qua callback/Future (hoặc ném thẳng) | Sửa config/dữ liệu/ACL; log + DLQ topic |
| **Fatal cho idempotent/txn** | `OutOfOrderSequenceException`, `ProducerFencedException`, `InvalidProducerEpochException`, `UnknownProducerIdException` | Producer chuyển trạng thái lỗi | Đóng producer, tạo instance mới |

**4. Idempotent producer (`enable.idempotence=true` — mặc định từ 3.0)**

- Broker gán mỗi producer 1 **PID (producer ID)**; mỗi batch gửi kèm **sequence number** tăng dần theo partition. Broker nhớ (PID, partition, seq) của **5 batch gần nhất** → batch **trùng seq** bị bỏ qua (chống duplicate do retry), batch **nhảy seq** bị từ chối `OutOfOrderSequenceException` (giữ order).
- Điều kiện bắt buộc (vi phạm → `ConfigException`): `acks=all`, `retries > 0`, **`max.in.flight.requests.per.connection ≤ 5`**. Mặc định 5/5/all nên "để mặc định là idempotent".
- Vì sao **5**? Broker chỉ cache metadata 5 batch/partition để sắp lại thứ tự khi retry. Với idempotence bật, **`max.in.flight=5` vẫn giữ đúng order** — đề cũ bảo "muốn giữ order phải `max.in.flight=1`" là cách của thời **chưa có idempotence**.
- Giới hạn: chỉ chống duplicate **trong 1 session producer** và cho **retry nội bộ**; app tự gọi `send()` lại thì vẫn duplicate. Không atomic đa partition → cần Transactions.
- Chi phí: gần như **không** (thêm vài byte header PID/seq), nên 3.0 bật mặc định.

**5. Batching & latency (`linger.ms`, `batch.size`, `buffer.memory`)**

- `batch.size` = **16.384 byte** (16 KB): kích thước **tối đa** 1 batch/partition (không phải "đợi đủ mới gửi"). Record lớn hơn `batch.size` vẫn gửi được (1 record/batch) — nhưng không được vượt `max.request.size` = **1.048.576** (1 MB).
- `linger.ms` = **5 ms** (đổi từ 0 ở Kafka 4.0, KIP-1030; đề cũ ghi 0): thời gian **tối đa** batch chờ thêm record. Batch **gửi khi đủ `batch.size` HOẶC hết `linger.ms`** (cái nào trước). Tăng `linger.ms` → batch to → throughput ↑, nén tốt hơn, nhưng latency ↑.
- `buffer.memory` = **33.554.432** (32 MB): tổng bộ nhớ buffer; đầy → `send()` block `max.block.ms` (**60.000 ms**) → `BufferExhaustedException` (subclass `TimeoutException`). Đây là dấu hiệu **producer nhanh hơn broker** → tăng buffer/batch, thêm partition, hoặc bật nén.
- Metrics nhận diện batching (Tuần 8 sâu): `batch-size-avg` (thấp = batch nhỏ, tăng `linger.ms`), `record-queue-time-avg` (thời gian record nằm trong accumulator), `records-per-request-avg`, `buffer-available-bytes`, `request-latency-avg`, `record-send-rate`, `record-error-rate`, `record-retry-rate`, `compression-rate-avg`.

**6. Compression (`compression.type`) — nén theo BATCH**

| `compression.type` | Tỉ lệ nén | CPU | Tốc độ | Ghi chú thi |
|---|---|---|---|---|
| `none` (**mặc định**) | — | 0 | nhanh nhất | Tốn network/disk |
| `gzip` | Cao nhất | Cao | Chậm | Level `compression.gzip.level` (mặc định -1 = 6) |
| `snappy` | Trung bình | Thấp | Nhanh | Google, cân bằng; không có level |
| `lz4` | Trung bình | Thấp | **Nhanh nhất** giải nén | Khuyến nghị chung cho throughput; `compression.lz4.level` (mặc định 9) |
| `zstd` | Cao (gần gzip) | Trung bình | Nhanh | Kafka ≥ 2.1 (KIP-110); `compression.zstd.level` (mặc định 3); tốt nhất về ratio/CPU |

- Nén áp dụng **cho cả batch** → **batch càng to nén càng tốt** → thường bật nén đi cùng tăng `linger.ms`/`batch.size`.
- Broker **giữ nguyên batch nén** (zero-copy, không giải nén) nếu topic `compression.type=producer` (mặc định); nếu topic đặt codec khác → broker phải giải nén + nén lại (tốn CPU broker). Consumer luôn tự giải nén.
- Nén giảm byte trên mạng/đĩa → gián tiếp tăng throughput và giảm khả năng đụng `max.request.size`/`message.max.bytes` (kiểm tra kích thước **sau** nén).

**7. Partitioner — record đi vào partition nào**

- Thứ tự quyết định: (1) `record.partition` chỉ định tay → dùng ngay; (2) có **key** → `murmur2(keyBytes) mod numPartitions` (built-in, **giống nhau giữa các client Java-compatible**); (3) key **null** → **sticky partitioner**.
- **Sticky partitioner** (KIP-480, Kafka 2.4): dính 1 partition đến khi batch đầy/hết linger rồi đổi partition → batch to hơn, p99 latency giảm so với round-robin. **KIP-794** (Kafka 3.3, "strictly uniform sticky"): tích hợp thẳng vào `KafkaProducer`, đổi partition theo **byte** (`batch.size`) thay vì theo batch; thêm `partitioner.adaptive.partitioning.enable` (**true**, ưu tiên broker nhanh), `partitioner.availability.timeout.ms` (**0**), `partitioner.ignore.keys` (**false** — true = bỏ hash key, dùng sticky kể cả có key → **mất ordering theo key**). `DefaultPartitioner`/`UniformStickyPartitioner` bị deprecate; `partitioner.class` mặc định **null**.
- **Bẫy lớn:** **thêm partition** vào topic → `hash mod N` đổi → **cùng key sang partition khác** → mất ordering theo key giữa cũ/mới, phá vỡ compaction giả định "1 key 1 partition". Kế hoạch số partition từ đầu; nếu phải thêm → dùng topic mới + migrate.
- Custom: implement `Partitioner.partition(topic, key, keyBytes, value, valueBytes, cluster)` + `configure()` + `close()`; đặt `partitioner.class`. `RoundRobinPartitioner` có sẵn (bỏ qua key, xoay vòng — cũng mất ordering theo key).
- Key phân bố lệch (hot key) → hot partition → 1 consumer quá tải; giải pháp: key phức hợp/salt, tăng partition (chấp nhận đổi mapping), hoặc custom partitioner tách key VIP ra partition riêng.

**8. Serializer, headers, interceptor, các config còn lại**

- Built-in serializer: `StringSerializer`, `IntegerSerializer`, `LongSerializer`, `DoubleSerializer`, `ByteArraySerializer`, `BytesSerializer`, `UUIDSerializer`, `VoidSerializer`… Custom: implement `Serializer<T>` (`serialize(topic, data)` → `byte[]`, `configure`, `close`). Avro/Protobuf/JSON Schema qua `Schema Registry` (Tuần 5). Mismatch serializer ↔ deserializer = lỗi lúc consume, không phải lúc produce.
- **Headers** (`record.headers().add(key, byte[])`): metadata ngoài payload (trace ID, schema hint, source) — có thể dùng cho routing/filter phía consumer, **không** ảnh hưởng partition.
- **`ProducerInterceptor`** (`interceptor.classes`): `onSend(record)` chạy **trước serializer** (có thể sửa record: thêm header, đổi topic), `onAcknowledgement(metadata, exception)` chạy trên I/O thread khi có ack/lỗi (đếm metric, audit); chain theo thứ tự cấu hình. Không ném exception ra ngoài (bị log & nuốt).
- `client.id`: chuỗi định danh logical cho log/metrics/**quota** broker (`client.id` + `user` là 2 chiều quota). `max.request.size` (**1 MB**) giới hạn phía **client**; broker có `message.max.bytes` (**1.048.588**) và topic `max.message.bytes` — record lớn cần chỉnh **cả 3** + consumer `max.partition.fetch.bytes`/`replica.fetch.max.bytes`.
- Timestamp: topic `message.timestamp.type=CreateTime` (mặc định, lấy từ producer) hoặc `LogAppendTime` (broker ghi đè).

**9. Transactions — EOS phía producer (KIP-98, Kafka 0.11)**

- Mục tiêu: **atomic multi-partition/multi-topic write** + **offset commit nằm chung transaction** → consume-transform-produce **exactly-once** trong Kafka.
- Bắt buộc `transactional.id` (unique, **ổn định qua restart** — thường theo shard/partition của app). Set `transactional.id` → idempotence **tự bật**. Topic đích nên RF ≥ 3, `min.insync.replicas` = 2.
- API (tất cả **blocking**, ném exception): `initTransactions()` (đăng ký với coordinator, **fence zombie**, gọi **1 lần**) → `beginTransaction()` → `send()` ×N → `sendOffsetsToTransaction(offsets, consumer.groupMetadata())` → `commitTransaction()` hoặc `abortTransaction()`. Chỉ **1 transaction mở/producer**; đã set `transactional.id` thì **mọi** `send()` phải nằm trong transaction.
- Xử lý lỗi: `ProducerFencedException` / `OutOfOrderSequenceException` / `AuthorizationException` → **không recover được → `close()`** producer; `KafkaException` khác → `abortTransaction()` rồi thử lại.
- **Transaction coordinator** = module trên mỗi broker; `transactional.id` hash → partition của topic nội bộ **`__transaction_state`** (**50 partitions**, compacted, RF `transaction.state.log.replication.factor`=3) → broker leader partition đó là coordinator. Log chứa **trạng thái** (Ongoing / PrepareCommit / PrepareAbort / CompleteCommit / CompleteAbort), không chứa data.
- **Zombie fencing**: mỗi `initTransactions()` **tăng producer epoch**; request từ epoch cũ bị từ chối `ProducerFencedException` → instance cũ bị "treo" không thể commit nữa.
- Luồng: FindCoordinator → InitProducerId (PID + epoch) → AddPartitionsToTxn (khi `send()` tới partition mới) → Produce (record thường, kèm PID/epoch/seq) → AddOffsetsToTxn + TxnOffsetCommit → EndTxn → coordinator ghi PrepareCommit → **ghi control record (COMMIT/ABORT marker) vào từng partition** (2-phase commit) → CompleteCommit.
- **Consumer**: `isolation.level=read_committed` → chỉ đọc tới **LSO (last stable offset)** = offset của transaction **đang mở** sớm nhất; record của transaction **abort** bị lọc bỏ phía client dựa vào marker; `read_uncommitted` (**mặc định**) đọc tới high watermark, thấy cả record chưa commit/đã abort. Transaction mở lâu → LSO đứng → **consumer lag tăng giả**.
- Timeout: `transaction.timeout.ms` = **60.000 ms** (coordinator tự abort transaction mở quá lâu); broker `transaction.max.timeout.ms` = **900.000 ms** (15 phút) → producer đòi lớn hơn bị `InvalidTxnTimeoutException`; `transactional.id.expiration.ms` = **7 ngày** (id không hoạt động bị quên). Kafka Streams EOS commit mỗi **100 ms**.
- Chi phí: overhead **không phụ thuộc số message** trong transaction; theo Confluent, ghi 1 KB record, commit mỗi 100 ms → throughput giảm ~**3%**; consumer `read_committed` **không** giảm throughput (lọc server-side + marker). Transaction càng dài → end-to-end latency càng cao (consumer phải chờ commit).
- **Giới hạn:** EOS chỉ trong **Kafka → Kafka**. Sink là DB/HTTP/S3 → transaction Kafka **không** bao phủ → cần **idempotent sink** (upsert theo key/offset), **outbox pattern**, hoặc **Kafka Connect** sink quản lý offset (Tuần 5/9).

**10. Bảng tổng: idempotent vs transactional**

| | Idempotent producer | Transactional producer |
|---|---|---|
| Config | `enable.idempotence=true` (mặc định) | `transactional.id=<unique>` (kéo theo idempotence) |
| Chống | Duplicate + mất order do **retry nội bộ**, trong **1 partition**, **1 session** | Ghi **một phần** (partial write) đa partition/topic; duplicate do app crash giữa produce & commit offset; **zombie** |
| Phạm vi atomic | 1 batch → 1 partition | Nhiều partition + nhiều topic + offset commit (`__consumer_offsets`) |
| API đổi | Không | `initTransactions/begin/commit/abort/sendOffsetsToTransaction` |
| Consumer cần | Không đổi | `isolation.level=read_committed` |
| Chi phí | ~0 | Coordinator RPC, marker, latency theo commit interval |
| Dùng khi | Mọi producer thường | Consume-transform-produce, Streams EOS, ghi nhiều topic phải cùng thành/bại |

**Java `ProducerConfig` — snippet để nhớ tên config (đề hỏi theo tên Java):**

```java
Properties p = new Properties();
p.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092,localhost:9094");
p.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
p.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
p.put(ProducerConfig.ACKS_CONFIG, "all");                                  // mặc định
p.put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, true);                     // mặc định
p.put(ProducerConfig.MAX_IN_FLIGHT_REQUESTS_PER_CONNECTION, 5);            // ≤5 khi idempotent
p.put(ProducerConfig.DELIVERY_TIMEOUT_MS_CONFIG, 120_000);                 // ≥ linger + request.timeout
p.put(ProducerConfig.REQUEST_TIMEOUT_MS_CONFIG, 30_000);
p.put(ProducerConfig.LINGER_MS_CONFIG, 5);                                 // 4.0: 5 (cũ: 0)
p.put(ProducerConfig.BATCH_SIZE_CONFIG, 16_384);
p.put(ProducerConfig.BUFFER_MEMORY_CONFIG, 33_554_432L);
p.put(ProducerConfig.MAX_BLOCK_MS_CONFIG, 60_000);
p.put(ProducerConfig.COMPRESSION_TYPE_CONFIG, "lz4");                      // none mặc định
p.put(ProducerConfig.MAX_REQUEST_SIZE_CONFIG, 1_048_576);
p.put(ProducerConfig.PARTITIONER_CLASS_CONFIG, MyPartitioner.class.getName()); // null = built-in
p.put(ProducerConfig.INTERCEPTOR_CLASSES_CONFIG, AuditInterceptor.class.getName());
p.put(ProducerConfig.TRANSACTIONAL_ID_CONFIG, "orders-txn-" + shardId);    // bật transactions
p.put(ProducerConfig.TRANSACTION_TIMEOUT_CONFIG, 60_000);
```

### 🅱️ Buổi B — Hands-on (~3.5h)

> 🧪 **Lab cầm tay chỉ việc (từng bước + lệnh + code):** [labs.md](labs.md). Dùng lại cluster 3 node Tuần 1 (`docker-compose.cluster.yml`, `min.insync.replicas=2`, RF=3).

**Lab 3.1 ⭐ — Callback + đo latency theo `acks`:** gửi 500 message với `acks` = 0 / 1 / -1 trong `kafkajs`, in p50/p99; gửi 1 message/`send()` vs 100 message/`send()` để thấy batching. Thấy `acks=0` trả `offset=-1`.

**Lab 3.2 — `kafka-producer-perf-test.sh`:** 6 lần chạy chéo `linger.ms=0/50` × `batch.size=16384/262144` × `compression.type=none/lz4/zstd` → điền bảng records/sec, MB/sec, avg/99th latency.

**Lab 3.3 — Partitioner:** 1.000 message key `null` vs key `user-N`; consumer in phân bố partition; `--alter --partitions 6` → cùng key sang partition khác (bẫy); custom partitioner `createPartitioner` đưa key VIP vào partition 0.

**Lab 3.4 — Idempotence dưới lỗi mạng:** `idempotent: true`, `docker pause` broker leader giữa lúc gửi rồi `unpause`; đếm message ở consumer = số đã gửi (không duplicate, đúng thứ tự).

**Lab 3.5 ⭐ — Transactions EOS:** `producer.transaction()` + `sendOffsets` consume-transform-produce; abort giữa chừng; consumer `read_committed` không thấy, `read_uncommitted` thấy.

**Lab 3.6 — Bảng lỗi thực nghiệm:** `RecordTooLarge` (console producer `max.request.size`), `TimeoutException` (`delivery.timeout.ms` nhỏ + `docker pause`), `InvalidTopic`, `ConfigException` (`delivery.timeout.ms` < `linger.ms` + `request.timeout.ms`) → phân loại retriable/fatal.

### 🅲️ Buổi C — Bổ sung (~2.5h)

**Bảng quyết định: tối ưu producer theo mục tiêu**

| Mục tiêu | Chỉnh gì | Đánh đổi |
|---|---|---|
| Latency thấp nhất, chấp nhận mất | `acks=0`, `linger.ms=0`, không nén | Mất data, không retry được, không idempotent |
| Không mất data | `acks=all` + topic `min.insync.replicas=2` + RF=3, `enable.idempotence=true`, `retries` mặc định, `delivery.timeout.ms` đủ lớn | Latency ↑ (chờ ISR) |
| Throughput cao | Tăng `linger.ms` (10–100), `batch.size` (64–256 KB), `compression.type=lz4/zstd`, nhiều partition | Latency ↑, CPU nén |
| Giữ order theo key | Có key + idempotence (`max.in.flight ≤ 5`) hoặc `max.in.flight=1`; **không** thêm partition; không `partitioner.ignore.keys` | Throughput ↓ nếu in-flight = 1 |
| Không duplicate trong 1 partition | `enable.idempotence=true` | ~0 |
| Atomic nhiều topic / EOS read-process-write | `transactional.id` + `sendOffsetsToTransaction` + consumer `read_committed` | Latency theo commit interval, coordinator overhead |
| Record > 1 MB | Tăng `max.request.size` (client) + `message.max.bytes` (broker) / `max.message.bytes` (topic) + `replica.fetch.max.bytes` + consumer `max.partition.fetch.bytes`; hoặc **claim-check** (lưu S3, gửi pointer) | Bộ nhớ/GC broker |
| Buffer đầy, `send()` block | Tăng `buffer.memory`, giảm tốc producer, bật nén, thêm partition/broker | RAM |

**So sánh 3 mức delivery semantics phía producer (ôn Tuần 2 → ghép config)**

| Semantics | Producer config | Điều kiện thêm |
|---|---|---|
| At-most-once | `acks=0` hoặc `retries=0` | Consumer commit trước xử lý |
| At-least-once | `acks=all`, `retries>0`, **`enable.idempotence=false`** (hiếm) | Consumer commit sau xử lý; app phải idempotent |
| Exactly-once (Kafka→Kafka) | `enable.idempotence=true` (1 partition) → `transactional.id` (đa partition + offset) | Consumer `read_committed`; sink ngoài Kafka cần idempotent/outbox |

**`kafkajs` ↔ Java — map config để không lẫn khi thi**

| Java `ProducerConfig` | `kafkajs` | Ghi chú |
|---|---|---|
| `acks` | `producer.send({ acks: -1 \| 1 \| 0 })` | Per-send, mặc định -1 |
| `enable.idempotence` | `kafka.producer({ idempotent: true })` | kafkajs yêu cầu `maxInFlightRequests: 1` (Java cho phép ≤5) |
| `max.in.flight.requests.per.connection` | `maxInFlightRequests` | Mặc định kafkajs: không giới hạn |
| `retries` / `retry.backoff.ms` | `retry: { retries, initialRetryTime, maxRetryTime }` | Mặc định 5 lần, 300 ms |
| `linger.ms` / `batch.size` | **không có** — batching = số message trong 1 `send()`/`sendBatch()` | Dùng `kafka-producer-perf-test.sh` để đo thật |
| `compression.type` | `send({ compression: CompressionTypes.GZIP })` | snappy/lz4/zstd cần codec ngoài |
| `partitioner.class` | `createPartitioner` | `Partitioners.DefaultPartitioner` = murmur2 tương thích Java |
| `transactional.id` / `transaction.timeout.ms` | `transactionalId`, `transactionTimeout` | `producer.transaction()` → `send/sendOffsets/commit/abort` |
| `isolation.level` (consumer) | `readUncommitted: false` (**mặc định** kafkajs = read_committed!) | Java mặc định read_uncommitted |
| `max.request.size` | `maxRequestSize`? **không có** | Dùng console producer để thí nghiệm |

**Đọc thêm:** *Kafka: The Definitive Guide* 2nd ed. — Chương 3 (Kafka Producers) + Chương 8 (Exactly-Once Semantics); Confluent blog "Transactions in Apache Kafka"; KIP-98, KIP-480/794, KIP-1030 trong `resources/`.

### 🅳 Buổi D — Practice + Review (~2h)

> 📝 **Bộ câu hỏi luyện tập của tuần:** [questions.md](questions.md) — đáp án & giải thích: [answers.md](answers.md). *(bằng tiếng Anh — văn phong đề CCDAK.)*

- Làm 28 câu, chấm bằng answer key; mỗi câu sai → tìm lại mục Buổi A tương ứng và **ghi sổ**.
- Tự viết lại bảng `acks` 0/1/all, bảng retriable vs fatal, bảng idempotent vs transactional **bằng trí nhớ** rồi so với README.
- **Spaced repetition** mốc **1 / 3 / 7 ngày** cho bộ số: 120.000 / 30.000 / 5 / 16.384 / 32 MB / 60.000 / 1 MB / 5 in-flight / 60.000 txn / 15 phút / 7 ngày / 50 partition.
- Tuần 4 có **mini-mock FUND+DEV ≥70%** → producer chiếm nửa phần DEV, chuẩn bị từ tuần này.

## 🧠 PHẢI NHỚ tuần này

| Fact | Con số / Ghi nhớ |
|---|---|
| `acks` mặc định | **`all`** (từ 3.0); `0` → offset -1, không retry; `1` → leader; `all` → toàn bộ **ISR** |
| `enable.idempotence` | **true** mặc định (3.0); yêu cầu `acks=all`, `retries>0`, `max.in.flight ≤ 5` |
| `max.in.flight.requests.per.connection` | **5**; idempotent + 5 vẫn giữ order; không idempotent muốn giữ order → **1** |
| `retries` | **Integer.MAX_VALUE**; dùng `delivery.timeout.ms` để giới hạn |
| `delivery.timeout.ms` | **120.000 ms**; phải ≥ `linger.ms` + `request.timeout.ms`, vi phạm → `ConfigException` |
| `request.timeout.ms` | **30.000 ms** (1 request) |
| `retry.backoff.ms` / `.max.ms` | **100 ms** / **1.000 ms** (exponential) |
| `linger.ms` | **5 ms** (Kafka 4.0, KIP-1030; đề cũ: 0); batch gửi khi đủ size **hoặc** hết linger |
| `batch.size` | **16.384 byte** (16 KB) mỗi partition; là **cận trên**, không phải ngưỡng chờ |
| `buffer.memory` / `max.block.ms` | **32 MB** / **60.000 ms** → `BufferExhaustedException` |
| `max.request.size` (client) vs `message.max.bytes` (broker) | **1.048.576** vs **1.048.588**; vượt → `RecordTooLargeException` (fatal) |
| `compression.type` | **none**; none/gzip/snappy/lz4/zstd; nén **theo batch**; zstd ratio tốt nhất/CPU, lz4 nhanh nhất |
| Partitioner | key → **murmur2 mod N**; null key → **sticky** (KIP-480 2.4, KIP-794 3.3); `partitioner.ignore.keys=false`; thêm partition → **đổi mapping key** |
| `metadata.max.age.ms` | **300.000 ms** (5 phút) |
| Thread-safety | `KafkaProducer` **thread-safe** — 1 instance share nhiều thread; callback chạy trên **I/O thread** |
| `transactional.id` | Bắt buộc cho transactions, unique + ổn định; set → idempotence tự bật; mỗi `initTransactions()` **tăng epoch** → fence zombie |
| `transaction.timeout.ms` / broker `transaction.max.timeout.ms` | **60.000 ms** / **900.000 ms** (15 phút) |
| `transactional.id.expiration.ms` | **7 ngày** |
| `__transaction_state` | **50 partitions**, compacted; coordinator = leader partition tương ứng hash(`transactional.id`) |
| `isolation.level` | **read_uncommitted** (mặc định Java) / `read_committed` đọc tới **LSO**; `kafkajs` mặc định `readUncommitted: false` |
| EOS end-to-end | Chỉ **Kafka → Kafka**; sink ngoài → idempotent sink / outbox / Connect |

## ⚠️ Bẫy đề hay gặp

- Thấy "muốn giữ thứ tự khi retry" → dễ chọn `max.in.flight.requests.per.connection=1`, nhưng với **idempotence bật (mặc định)** thì **≤5 vẫn giữ order**; đáp án `1` chỉ đúng khi đề nói rõ `enable.idempotence=false`.
- Thấy "`acks=all` mà vẫn mất data" → dễ nghĩ bug Kafka, nhưng đúng là **`min.insync.replicas=1`** (ISR co còn leader) → phải đặt `min.insync.replicas=2` **trên topic/broker**, không phải trên producer.
- Thấy "tăng `retries` để đảm bảo delivery" → nhưng `retries` mặc định đã là MAX; thứ cần chỉnh là **`delivery.timeout.ms`**. Và `retries` **vô nghĩa với `acks=0`**.
- Thấy `TimeoutException: Expiring N record(s)... ms has passed since batch creation` → dễ chọn tăng `request.timeout.ms`, nhưng đó là **`delivery.timeout.ms`** hết hạn (broker chậm/ISR thiếu); kiểm tra cluster trước, rồi mới tăng `delivery.timeout.ms`.
- Thấy "`delivery.timeout.ms=20000`, `linger.ms=5000`, `request.timeout.ms=30000`" → tưởng chạy được, nhưng **20.000 < 5.000 + 30.000** → producer **không khởi tạo được** (`ConfigException`).
- Thấy "record 2 MB bị từ chối, đã tăng `max.request.size`" → vẫn lỗi vì còn **`message.max.bytes`** (broker) / `max.message.bytes` (topic) và consumer `max.partition.fetch.bytes`.
- Thấy `SerializationException` → dễ nghĩ producer retry, nhưng nó ném **đồng bộ ngay tại `send()`**, không đi qua callback, **không retry**.
- Thấy "message không key phân bố lệch, 1 partition nhận nhiều trong vài ms" → tưởng bug partitioner, nhưng đó là **sticky partitioner** hoạt động đúng (dính 1 partition tới khi batch đầy); tổng thể vẫn đều.
- Thấy "thêm partition để tăng throughput" → quên rằng **cùng key sẽ hash sang partition khác** → mất ordering/compaction theo key.
- Thấy "idempotent producer đảm bảo exactly-once end-to-end" → **sai**: idempotence chỉ chống duplicate **retry nội bộ, 1 partition, 1 session**; EOS đa partition + offset cần **transactions**; sink ngoài Kafka cần idempotent sink.
- Thấy "`transactional.id` sinh ngẫu nhiên mỗi lần khởi động (UUID)" → tưởng an toàn, nhưng làm **mất zombie fencing** (epoch không kế thừa) → phải **ổn định theo shard/partition**.
- Thấy "consumer `read_committed` bị lag dù producer vẫn ghi" → không phải consumer chậm, mà **transaction đang mở giữ LSO** → xem `transaction.timeout.ms`/producer treo.
- Thấy `ProducerFencedException` → dễ chọn `abortTransaction()` rồi retry, nhưng đây là **fatal** → **`close()`** producer (instance khác đã lấy epoch cao hơn).
- Thấy "nén để tiết kiệm nhưng CPU broker tăng vọt" → topic đặt `compression.type` **khác producer** → broker phải nén lại; để `producer` (mặc định).

## 🔁 Phản xạ nhanh (keyword → đáp án)

| Thấy từ khoá | Bật ngay |
|---|---|
| "lowest latency, can tolerate loss" | **`acks=0`** (offset -1, không retry) |
| "no data loss, tolerate 1 broker failure" | **`acks=all` + `min.insync.replicas=2` + RF=3** |
| "duplicates after retries" / "reordering on retry" | **`enable.idempotence=true`** (PID + sequence) |
| "`OutOfOrderSequenceException`" | idempotent producer phát hiện lệch seq → fatal, tạo producer mới |
| "how long producer keeps retrying" | **`delivery.timeout.ms`** (120 s), không phải `retries` |
| "`Expiring N records ... since batch creation`" | `delivery.timeout.ms` hết → kiểm tra broker/ISR |
| "`ConfigException` on startup about timeout" | `delivery.timeout.ms` < `linger.ms` + `request.timeout.ms` |
| "increase throughput, reduce requests" | **↑`linger.ms`, ↑`batch.size`, `compression.type`** |
| "`send()` blocks / `BufferExhaustedException`" | `buffer.memory` đầy → `max.block.ms`; tăng buffer / chậm producer |
| "best compression ratio with reasonable CPU" | **`zstd`**; "fastest" → **`lz4`**; "highest ratio, CPU heavy" → `gzip` |
| "same key → same partition" | murmur2 hash mod N; **đừng thêm partition** |
| "null key, small batches, high latency" | **sticky partitioner** (KIP-480/794) đã xử lý; tăng `linger.ms` |
| "distribute evenly even with keys" | `partitioner.ignore.keys=true` / `RoundRobinPartitioner` (mất order theo key) |
| "record bigger than 1 MB" | `max.request.size` + `message.max.bytes` + `max.message.bytes` + fetch sizes, hoặc claim-check |
| "atomic write to multiple topics" | **transactions** (`transactional.id`, `commitTransaction`) |
| "read-process-write exactly once" | `sendOffsetsToTransaction` + consumer **`read_committed`** |
| "zombie producer after restart" | `transactional.id` ổn định → **epoch bump → `ProducerFencedException`** |
| "consumer never sees aborted records" | `isolation.level=read_committed`, đọc tới **LSO** |
| "coordinator aborts long transaction" | `transaction.timeout.ms` (60 s) ≤ `transaction.max.timeout.ms` (15 phút) |
| "EOS when writing to a database" | **Không** có transaction Kafka → idempotent sink / outbox / Connect |
| "share producer across threads" | OK — `KafkaProducer` thread-safe, 1 instance nhanh hơn |
| "add header / mutate record before send" | **`ProducerInterceptor.onSend`** |

## 🧪 Lab checklist

- [ ] Lab 3.1 ⭐ — Callback + đo latency `acks=0/1/-1`, thấy `offset=-1` với `acks=0`, batch 100 msg/`send()` nhanh hơn 1 msg/`send()`.
- [ ] Lab 3.2 — Điền bảng `kafka-producer-perf-test.sh` 6 cấu hình `linger.ms` × `batch.size` × `compression.type`.
- [ ] Lab 3.3 — Phân bố partition key null vs key user-N; quan sát cùng key đổi partition sau `--alter --partitions 6`; custom partitioner.
- [ ] Lab 3.4 — Idempotent producer sống qua `docker pause` leader, không duplicate, đúng thứ tự.
- [ ] Lab 3.5 ⭐ — Transaction commit/abort; consumer `read_committed` vs `read_uncommitted` thấy khác nhau; `sendOffsets` trong transaction.
- [ ] Lab 3.6 — Bảng lỗi thực nghiệm: `RecordTooLarge`, `TimeoutException`, `InvalidTopic`, `ConfigException`.

## 🚪 Cổng tự kiểm tra (phải trả lời trôi chảy mới sang tuần sau)

- **Producer mặc định Kafka 4.3 có mất data hay duplicate khi retry không? Vì sao?**
  **Đáp án gọn:** Không: `acks=all` + `enable.idempotence=true` + `retries=MAX` + `max.in.flight=5` → broker dedup theo PID/sequence, giữ order. Nhưng chỉ khi topic có `min.insync.replicas ≥ 2` mới thực sự bền.
- **`delivery.timeout.ms`, `request.timeout.ms`, `linger.ms` liên hệ thế nào?**
  **Đáp án gọn:** `delivery.timeout.ms` (120 s) ≥ `linger.ms` (5) + `request.timeout.ms` (30 s); delivery là tổng thời gian sống của record trong producer, request là thời gian chờ 1 response.
- **Kể 3 exception retriable, 3 exception fatal.**
  **Đáp án gọn:** Retriable: `NotLeaderOrFollower`, `NotEnoughReplicas`, `NetworkException`. Fatal: `RecordTooLarge`, `SerializationException`, `TopicAuthorizationException` (+ `OutOfOrderSequence`, `ProducerFenced` với idempotent/txn).
- **Vì sao thêm partition là bẫy với keyed messages?**
  **Đáp án gọn:** partition = murmur2(key) mod N; N đổi → cùng key sang partition khác → mất ordering theo key và phá compaction.
- **Idempotent khác transactional ở đâu?**
  **Đáp án gọn:** Idempotent: chống duplicate/reorder do retry nội bộ, 1 partition, 1 session, không đổi API. Transactional: atomic đa partition/topic + offset commit, cần `transactional.id`, epoch fencing, consumer `read_committed`.
- **Consumer `read_committed` đọc tới đâu? Điều gì làm lag tăng giả?**
  **Đáp án gọn:** Tới LSO (last stable offset = offset của transaction đang mở sớm nhất); transaction mở lâu/producer treo giữ LSO → lag tăng dù không có record mới committed.
- **Vì sao `transactional.id` không được random mỗi lần start?**
  **Đáp án gọn:** Fencing dựa trên epoch của **cùng** `transactional.id`; id mới → epoch mới độc lập → zombie cũ không bị fence, có thể commit trùng.
- **Ghi kết quả vào PostgreSQL sau khi consume — Kafka transaction có bảo vệ không?**
  **Đáp án gọn:** Không. Transaction chỉ bao Kafka topics + `__consumer_offsets`. Cần idempotent upsert / lưu offset cùng bảng nghiệp vụ / outbox pattern.

## 📎 Tài nguyên tuần này

> 📂 **Đã crawl sẵn tài liệu chính thức vào** [`resources/`](resources/INDEX.md) — đọc offline được.

- Apache Kafka Docs: [Producer Configs](https://kafka.apache.org/documentation/#producerconfigs) · [Producer API](https://kafka.apache.org/documentation/#producerapi) · [Message Delivery Semantics](https://kafka.apache.org/documentation/#semantics) · [KafkaProducer Javadoc 4.3](https://kafka.apache.org/43/javadoc/org/apache/kafka/clients/producer/KafkaProducer.html).
- KIP: [KIP-98 Exactly Once Delivery and Transactional Messaging](https://cwiki.apache.org/confluence/display/KAFKA/KIP-98+-+Exactly+Once+Delivery+and+Transactional+Messaging) · [KIP-480 Sticky Partitioner](https://cwiki.apache.org/confluence/display/KAFKA/KIP-480%3A+Sticky+Partitioner) · [KIP-794 Strictly Uniform Sticky Partitioner](https://cwiki.apache.org/confluence/display/KAFKA/KIP-794%3A+Strictly+Uniform+Sticky+Partitioner) · [KIP-1030 defaults 4.0](https://cwiki.apache.org/confluence/display/KAFKA/KIP-1030%3A+Change+constraints+and+default+values+for+various+configurations).
- Confluent: [Producer for Confluent Platform](https://docs.confluent.io/platform/current/clients/producer.html) · [Producer Configuration Reference](https://docs.confluent.io/platform/current/installation/configuration/producer-configs.html) · [Delivery semantics](https://docs.confluent.io/kafka/design/delivery-semantics.html) · Blog [Transactions in Apache Kafka](https://www.confluent.io/blog/transactions-apache-kafka/) · Blog [Sticky Partitioner](https://www.confluent.io/blog/apache-kafka-producer-improvements-sticky-partitioner/).
- Khoá học: Confluent Developer — *Apache Kafka 101* (Producers) + *Kafka Internals* (Producer); Stephane Maarek — *Apache Kafka Series: Learn Apache Kafka for Beginners v3* (mục Producer Configurations, Idempotent Producer, Message Compression, Batching, Partitioner) + *Kafka Connect/Streams* sau; sách *Kafka: The Definitive Guide* 2nd ed. — Ch.3 Kafka Producers, Ch.8 Exactly-Once Semantics.
- `kafkajs` docs: [Producing Messages](https://kafka.js.org/docs/producing) · [Transactions](https://kafka.js.org/docs/transactions) · [Custom Partitioner](https://kafka.js.org/docs/producing#custom-partitioner).

## ✅ Checklist hoàn thành Tuần 3

- [ ] Hoàn thành 4 buổi A/B/C/D
- [ ] Thuộc lòng bảng "PHẢI NHỚ" (đặc biệt chuỗi timeout 120.000/30.000/5 và bộ transactions 60.000/15 phút/7 ngày/50)
- [ ] Tự vẽ lại được send flow và bảng retriable vs fatal bằng trí nhớ
- [ ] Hoàn thành 6 lab (3.1 và 3.5 bắt buộc)
- [ ] Làm xong 28 câu questions.md, xem lại 100% câu sai
- [ ] Vượt Cổng tự kiểm tra
