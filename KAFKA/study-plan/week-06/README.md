# 🟦 Tuần 6 — Kafka Streams

> **Domain CCDAK:** Kafka Streams (STREAMS, 12%) + Application Testing (TEST, phần `TopologyTestDriver`) · **Thời lượng:** ~11h (4 buổi) · **Vị trí:** Tuần 6/10 — tuần duy nhất dành cho Streams; không có checkpoint riêng nhưng là 1/3 của mini-mock CONNECT+STREAMS+TEST ở Tuần 7
>
> **Điều hướng:** [⬅️ Tuần 5](../week-05/README.md) · [🏠 Kế hoạch tổng](../../KAFKA-STUDY-PLAN.md) · [Tuần 7 ➡️](../week-07/README.md)

## 🎯 Mục tiêu tuần này

- **Giải thích được** vì sao `Kafka Streams` là **library** (không có cluster riêng), scale bằng cách chạy thêm instance cùng `application.id`, và tính đúng số **task** = số partition lớn nhất của input topic trong sub-topology.
- **Phân biệt được** `KStream` (insert) / `KTable` (upsert, tombstone) / `GlobalKTable` (bản sao đầy đủ) trong 5 giây, và nói được stream-table duality bằng 1 câu.
- **Chỉ ra được** phép nào đổi key → sinh repartition topic, phép nào stateful → sinh state store + changelog topic; đọc tên `<app.id>-<name>-repartition` / `<app.id>-<store>-changelog` là biết nguồn gốc.
- **Chọn đúng** 1 trong 4 loại window (tumbling / hopping / sliding / session) + grace period + `suppress` theo mô tả nghiệp vụ; giải thích vì sao `count()` không emit mỗi record.
- **Thuộc lòng** join matrix: join nào cần window, join nào cần co-partition, join nào chỉ inner/left.
- **Cấu hình được** `processing.guarantee=exactly_once_v2`, các exception handler (deserialization / production / processing), `StreamsUncaughtExceptionHandler`, `num.standby.replicas`, và nói được default của từng cái.
- **Tự tay** viết WordCount + windowed aggregation + join bằng Java 17, chạy 2 instance thấy chia task, và **unit test bằng `TopologyTestDriver`** không cần broker.

## 📚 Nội dung học chi tiết

### 🅰️ Buổi A — Lý thuyết (~3h)

**1. `Kafka Streams` là gì — library, không phải cluster (câu định nghĩa kinh điển)**

- `Kafka Streams` là **1 JAR** (`org.apache.kafka:kafka-streams`) nhúng vào ứng dụng **JVM** (Java 11+ với Kafka 4.x); app chạy ở **bất kỳ đâu** (VM, container, K8s), **không chạy trong broker**, không cần cluster xử lý riêng như Flink/Spark. Đầu vào và đầu ra đều là **Kafka topic**; mọi trạng thái được bảo vệ bằng **topic nội bộ**.
- **Scale ngang** = chạy thêm **instance cùng `application.id`** → `application.id` chính là consumer **`group.id`** → Kafka tự chia partition (task) giữa các instance qua rebalance. Không có "master", không có deploy job.
- **Topology** = DAG các **processor node**: **source processor** (đọc topic, không có upstream) → **stream processor** (biến đổi) → **sink processor** (ghi topic, không có downstream). Một topology bị cắt thành **sub-topology** tại các repartition topic (mỗi sub-topology đọc/ghi topic độc lập).
- 2 cách viết: **DSL** (`StreamsBuilder` → `KStream`/`KTable`, khai báo, 90% use case) và **Processor API** (`Topology.addSource/addProcessor/addStateStore/addSink`, cấp thấp, kiểm soát từng record + punctuation). DSL được **xây trên** PAPI; nhúng PAPI vào DSL bằng `process()` / `processValues()`.
- Vòng đời: `new KafkaStreams(topology, props)` → `start()` → xử lý → `close()`. `Topology.describe()` in ra sub-topology, node, topic nội bộ — công cụ debug số 1.

**2. Task, thread, instance — đếm cho đúng (đề hỏi số)**

- **Số task** của 1 sub-topology = **số partition lớn nhất** trong các input topic của nó. Topic A 6 partition join topic B 6 partition → **6 task**. Task là **đơn vị song song nhỏ nhất**, mỗi task sở hữu partition của mình + state store riêng.
- **`num.stream.threads`** (mặc định **1**) = số thread trong 1 instance; mỗi thread chạy ≥ 1 task. Tổng thread hữu ích trên mọi instance **≤ số task**; thừa → **idle**. Ví dụ: 6 task, 4 instance × 2 thread = 8 thread → 2 thread ngồi chơi; instance thứ 7 cũng idle.
- Muốn song song hơn số task → **tăng partition input topic** (như consumer group), không phải tăng thread.
- Assignment do **`StreamsPartitionAssignor`** (client-side, protocol `classic`) hoặc **broker-side** với **KIP-1071** (`group.protocol=streams`, GA **4.2**, xem mục 13).
- **Depth-first**: mỗi record đi hết sub-topology trước khi lấy record kế → không có buffer giữa processor → **không cần backpressure** (consumer pull tự điều tiết).

**3. `KStream` vs `KTable` vs `GlobalKTable` + stream-table duality (BẢNG BẮT BUỘC)**

| | `KStream` | `KTable` | `GlobalKTable` |
|---|---|---|---|
| Ngữ nghĩa | **Event / INSERT** — 2 record cùng key độc lập | **Changelog / UPSERT** theo key — record sau ghi đè record trước; value `null` = **tombstone** (delete) | Như `KTable` về ngữ nghĩa |
| Dữ liệu mỗi instance | **1 phần** partition (chia theo task) | **1 phần** partition (chia theo task) | **Toàn bộ** partition — mỗi instance giữ **bản sao đầy đủ** |
| Tạo từ | `builder.stream(topic)` | `builder.table(topic, Materialized.as(...))` | `builder.globalTable(topic, Materialized.as(...))` |
| State store | Không (trừ khi stateful) | Có (RocksDB + changelog) | Có (RocksDB, restore thẳng từ **source topic**, không changelog riêng) |
| Join với `KStream` | Windowed, co-partition | Không window, **cần co-partition**, chỉ stream trigger | Không window, **không cần co-partition**, `KeyValueMapper` chọn key bất kỳ |
| Dùng khi | Luồng sự kiện (order, click, log) | Bảng lớn thay đổi liên tục (account balance, inventory) | Bảng tham chiếu **nhỏ**, ít đổi (country code, product catalog) — lookup/enrich |
| Bẫy | `count()` trên KStream = **đếm event** | `count()` trên KTable = đếm **key hiện hữu** (có subtractor) | Load hết vào RAM/disk mỗi instance → không dùng cho bảng lớn |

- **Stream-table duality:** stream là **changelog** của table (replay stream → dựng lại table); table là **snapshot** giá trị mới nhất mỗi key (đọc table → stream). Vì thế `KTable.toStream()` và `KStream.toTable()` là 2 chiều tự nhiên; changelog topic **compacted** chính là "stream dạng table".
- Đọc **cùng 1 topic** thành `KStream` → giữ mọi event; thành `KTable` → chỉ giữ giá trị cuối. Câu "consumer phải luôn thấy giá trị **mới nhất** của mỗi key" → `KTable`; "phải xử lý **từng** sự kiện" → `KStream`.

**4. Stateless operations & luật repartition (rất hay hỏi)**

- Nhóm **không đổi key → không repartition:** `filter`, `filterNot`, `mapValues`, `flatMapValues`, `peek` (side effect, trả stream), `foreach` (terminal), `print`, `merge` (gộp 2 KStream cùng kiểu, không đảm bảo thứ tự giữa 2 nguồn), `split().branch(pred, Branched.as(...))` (thay `branch()` đã xoá), `to(topic)` / `toTable()`, `processValues`.
- Nhóm **đổi key → đánh dấu repartition:** `map`, `flatMap`, `selectKey`, `groupBy`, `process` (PAPI có thể đổi key). Streams **chỉ thực sự tạo repartition topic khi có phép stateful phía sau** (aggregate/count/reduce/join) → topic `<application.id>-<operator-name>-repartition`, số partition = số partition input (hoặc theo `Repartitioned.numberOfPartitions`). Không có stateful phía sau → không tốn gì.
- **`groupByKey()` không repartition** (key giữ nguyên) trừ khi stream đã bị đánh dấu trước đó; **`groupBy(mapper)` luôn repartition**. Đề hỏi "aggregate theo key hiện có, tránh network overhead" → `groupByKey`.
- `repartition(Repartitioned.numberOfPartitions(n).withName("x"))` (thay `through()` đã xoá ở 4.0): ép tạo repartition topic tường minh — dùng để **đổi số partition** giữa topology hoặc **co-partition** trước join.
- Bẫy hiệu năng: `map` để chỉ đổi value → vẫn bị đánh dấu repartition → dùng **`mapValues`**.

**5. Stateful operations, state store, changelog, standby**

- `KGroupedStream` (từ `groupBy/groupByKey`) → **`count()`**, **`reduce(Reducer)`** (giữ kiểu value), **`aggregate(Initializer, Aggregator, Materialized)`** (đổi kiểu: `<String,Long>` từ `<String,String>`). Kết quả luôn là **`KTable`** (windowed → `KTable<Windowed<K>, V>`). `KGroupedTable.aggregate` cần thêm **subtractor** (`adder` cho value mới, `subtractor` cho value cũ khi key được update/xoá).
- **`Materialized.<K,V,KeyValueStore<Bytes,byte[]>>as("store-name")`** đặt tên store → bắt buộc nếu muốn **Interactive Query**; `.withKeySerde/.withValueSerde` khi không có default serde; `.withRetention`, `.withCachingDisabled`, `.withLoggingDisabled`.
- **State store**: mặc định **RocksDB persistent** trên đĩa tại `state.dir` (mặc định `/tmp/kafka-streams` → production phải dùng volume bền); hoặc **in-memory** (`Stores.inMemoryKeyValueStore`) — nhanh, mất khi restart. **Cả hai đều fault-tolerant** nhờ **changelog topic** `<application.id>-<store-name>-changelog`: **compacted** với key-value store; `compact,delete` với window/session store (key có timestamp, xoá theo retention + `windowstore.changelog.additional.retention.ms` = 1 ngày).
- **Restore**: task bị chuyển sang instance khác / restart → replay changelog vào RocksDB trước khi xử lý → thời gian phụ thuộc kích cỡ state. `state.dir` còn dữ liệu → chỉ replay phần thiếu (checkpoint; từ 4.3 offset lưu trong RocksDB, KIP-1035).
- **`num.standby.replicas`** (mặc định **0**): bản sao **nóng** của state store trên instance khác, liên tục đọc changelog → failover **gần tức thời**; chi phí **2× storage** + cần **n+1 instance**. `acceptable.recovery.lag` (10.000) quyết định instance "đủ gần" để nhận task. `withLoggingDisabled()` → **không changelog → không standby → mất state khi hỏng**.
- **Record cache** `statestore.cache.max.bytes` (mặc định **10 MB**, chia đều cho thread; tên cũ `cache.max.bytes.buffering` deprecated): read cache + write-back + **gom update cùng key** trước khi forward downstream / ghi changelog. Cache flush khi đầy hoặc mỗi **`commit.interval.ms`** → đây là lý do **"`count()` không emit mỗi record"**. Cache = 0 → downstream nhận **mọi** update trung gian; kết quả cuối **giống nhau** dù cache bật/tắt.

**6. Windowing — 4 loại + grace + suppress (BẢNG BẮT BUỘC)**

| Loại | API (Kafka 4.x) | Hình dạng | 1 record thuộc | Dùng khi |
|---|---|---|---|---|
| **Tumbling** | `TimeWindows.ofSizeWithNoGrace(Duration.ofMinutes(5))` / `ofSizeAndGrace(size, grace)` | Cố định, **không chồng**, không khe hở; size = advance; căn theo epoch | **đúng 1** window | "mỗi 5 phút", báo cáo theo khoảng, đếm/phút |
| **Hopping** | `TimeWindows.ofSizeAndGrace(size, grace).advanceBy(advance)` với advance < size | Cố định, **chồng nhau** | **nhiều** window (size/advance) | "5 phút, cập nhật mỗi 1 phút", moving average |
| **Sliding** | `SlidingWindows.ofTimeDifferenceAndGrace(diff, grace)` | Window định nghĩa theo **khoảng cách giữa các record**, chỉ tạo khi có record → không có window rỗng | Các record cách nhau ≤ diff | "2 sự kiện trong vòng 10 phút của nhau", aggregation theo cửa sổ trượt chính xác |
| **Session** | `SessionWindows.ofInactivityGapAndGrace(gap, grace)` / `ofInactivityGapWithNoGrace` | **Kích cỡ động**, mở rộng khi có record, đóng khi **im lặng > gap**; session gần nhau **merge** (cần `Merger`) | 1 session/key | Phiên người dùng, "user hoạt động liên tục", clickstream |

- API cũ `TimeWindows.of(size)` (grace ngầm **24 h**), `JoinWindows.of`, `SessionWindows.with` **bị xoá ở 4.0** → 4.x bắt buộc khai báo grace tường minh (`WithNoGrace` / `AndGrace`).
- **Grace period**: record đến (theo **stream time**) sau `window end + grace` là **late** → **bị drop** (metric `dropped-records-total`), không lỗi. Grace lớn → đúng hơn nhưng emit kết quả cuối chậm hơn và giữ window lâu hơn (retention ≥ size + grace).
- **`suppress(Suppressed.untilWindowCloses(BufferConfig.unbounded()))`** → chỉ emit **1 kết quả cuối** mỗi window sau `end + grace`; bắt buộc buffer strict (`unbounded()` hoặc `maxBytes/maxRecords(...).shutDownWhenFull()`). `untilTimeLimit(duration, buffer)` → rate-limit update cho KTable bất kỳ (được `emitEarlyWhenFull`). Không suppress → nhiều update trung gian (cache chỉ gom bớt, không chặn).
- Bẫy suppress: window chỉ đóng khi **stream time tiến** → topic ít dữ liệu → kết quả cuối "kẹt" tới khi có record mới (dùng dummy/heartbeat record nếu cần).
- Key kết quả là **`Windowed<K>`** với `window().start()/end()`; ghi ra topic thường `map((w, v) -> KeyValue.pair(w.key() + "@" + w.window().start(), v))`. Window store retention mặc định = size + grace, tăng bằng `Materialized.withRetention`.

**7. Time semantics — event / processing / ingestion / stream time**

| Loại thời gian | Ai gán | Streams lấy bằng | Ghi chú |
|---|---|---|---|
| **Event-time** | Producer (`CreateTime`, mặc định topic) hoặc field trong payload | `default.timestamp.extractor` = **`FailOnInvalidTimestamp`** (dùng record timestamp) hoặc custom `TimestampExtractor.extract(record, partitionTime)` | Chuẩn cho windowing; timestamp âm → **ném lỗi** (đổi `LogAndSkipOnInvalidTimestamp` để drop, `UsePartitionTimeOnInvalidTimestamp` để ước lượng) |
| **Ingestion-time** | Broker khi topic `message.timestamp.type=LogAppendTime` | Cùng extractor mặc định (record timestamp) | Không cần đổi code Streams |
| **Processing-time** | Lúc app xử lý | `WallclockTimestampExtractor` | Kết quả không tái lập khi replay |
| **Stream time** | Streams tính | max timestamp đã thấy **trong task** | Chỉ **tiến khi có record mới** → window/suppress/`STREAM_TIME` punctuator phụ thuộc vào nó |

- Output record kế thừa timestamp theo luật: stateless → giữ timestamp input; aggregation → **max** timestamp của các input; join → max của 2 bên. `context.forward(record.withTimestamp(...))` để ghi đè trong PAPI.
- `max.task.idle.ms` (mặc định **0**): task có nhiều input partition chờ bao lâu để đủ dữ liệu mọi partition rồi mới chọn record timestamp nhỏ nhất → tăng lên để join stream-table đúng thứ tự thời gian hơn (đổi lấy latency).

**8. Joins — join matrix + co-partitioning (BẢNG BẮT BUỘC)**

| Join | Window? | Co-partition? | Loại | Ai trigger output | Kết quả |
|---|---|---|---|---|---|
| `KStream` ⋈ `KStream` | **Có** — `JoinWindows.ofTimeDifferenceWithNoGrace(d)` / `ofTimeDifferenceAndGrace` | **Cần** | inner / left / outer | Record mới **cả 2 bên**, khớp với **mọi** record bên kia trong window (n×m output) | `KStream` |
| `KStream` ⋈ `KTable` | Không | **Cần** | inner / left | **Chỉ record bên stream**; table update chỉ đổi state | `KStream` |
| `KTable` ⋈ `KTable` | Không | **Cần** | inner / left / outer | Update **cả 2 bên**; tombstone sinh tombstone kết quả | `KTable` |
| `KTable` ⋈ `KTable` **foreign-key** | Không | **Không** (Streams tự tạo subscription/response topic nội bộ) | inner / left | Update cả 2 bên; 1 update bảng phải → join lại **mọi** record trái khớp FK | `KTable` |
| `KStream` ⋈ `GlobalKTable` | Không | **Không** | inner / left | Chỉ record bên stream; `KeyValueMapper(key, value)` chọn key lookup **bất kỳ** | `KStream` |
| `KTable` ⋈ `GlobalKTable` | — | — | **Không hỗ trợ** | — | — |

- **Co-partitioning** = 2 input có **cùng số partition** **và** **cùng chiến lược partition** (cùng key → cùng số partition, tức cùng partitioner/serializer key). Streams **chỉ kiểm tra được số partition** lúc start (`TopologyException: ... not co-partitioned`), **không kiểm tra được partitioner** → producer viết vào 2 topic phải dùng cùng cách partition. Lệch số partition → `repartition(Repartitioned.numberOfPartitions(n))` bên ít hơn (hoặc để Streams tự repartition khi đã có phép đổi key).
- Stream-stream: record null key/null value **bị bỏ qua**; left/outer emit bản "không khớp" **chỉ sau khi window + grace đóng** (từ 3.1, tránh kết quả giả). Serde qua `StreamJoined.with(keySerde, leftSerde, rightSerde)`.
- Stream-table: `Joined.with(keySerde, valueSerde, otherValueSerde)`; table **versioned store** (3.5+) cho phép lookup **đúng phiên bản theo timestamp** của record stream (temporal join) + `Joined.withGracePeriod`.
- Table-table: value null bên input = tombstone → xoá khỏi kết quả (không trigger joiner). FK join: `left.join(right, foreignKeyExtractor, joiner)`, không có outer.
- Chọn nhanh: **enrich bằng bảng tham chiếu nhỏ, key khác nhau** → `GlobalKTable`; **bảng lớn cùng key** → `KTable`; **2 luồng sự kiện gần nhau về thời gian** (click ↔ impression, payment ↔ order trong 10 phút) → `KStream-KStream` windowed; **bảng lớn key khác nhau** → `KTable` FK join.

**9. `processing.guarantee` — at_least_once vs exactly_once_v2 (BẢNG BẮT BUỘC)**

| | `at_least_once` (**mặc định**) | `exactly_once_v2` (2.6+, broker ≥ 2.5) |
|---|---|---|
| Cơ chế | Consumer commit offset **sau** khi ghi output; crash giữa chừng → **xử lý lại** → duplicate ở output + state | Ghi output + ghi changelog + commit offset trong **1 transaction** (`transactional.id` tự sinh, **1 producer/thread**); consumer `read_committed` chỉ thấy record đã commit |
| `commit.interval.ms` | **30.000** ms | **100** ms (Streams tự đổi default) — mỗi commit = 1 transaction, ảnh hưởng latency end-to-end |
| Client override | consumer `enable.auto.commit=false`, `auto.offset.reset=earliest` | thêm producer `enable.idempotence=true`, consumer `isolation.level=read_committed` |
| Yêu cầu broker | — | `transaction.state.log.replication.factor` (3) & `min.isr` (2) → **≥ 3 broker** với default; broker ≥ 2.5 |
| State khi crash | Có thể có "dirty write" → không rebuild | State lệch changelog → **xoá store, rebuild từ changelog** |
| Chi phí | Thấp nhất | Overhead coordinator + marker; throughput giảm vài %; chỉ EOS **Kafka → Kafka** (sink ngoài cần idempotent) |
| Giá trị đã xoá | — | `exactly_once` (1 producer/task) và `exactly_once_beta` **bị xoá ở 4.0** |

- Bẫy: EOS trong Streams **không** bảo vệ side effect trong `peek/foreach` (gọi HTTP, ghi DB) — chỉ bảo vệ **topic Kafka + state store + offset**.

**10. Error handling — 3 handler + uncaught handler + DLQ**

| Handler (config 4.x) | Bắt lỗi ở đâu | Mặc định | Lựa chọn |
|---|---|---|---|
| `deserialization.exception.handler` (tên cũ `default.deserialization.exception.handler` deprecated KIP-1056) | Record đầu vào **không deserialize được** (poison pill, sai schema) | **`LogAndFailExceptionHandler`** → app dừng | `LogAndContinueExceptionHandler` → log + **skip record** |
| `production.exception.handler` | Lỗi khi **ghi ra broker**: `RecordTooLargeException`, serialization lỗi, auth… | `DefaultProductionExceptionHandler` → **FAIL** | Custom trả `FAIL` / `CONTINUE` / `RETRY`; 4.2: set **`errors.deadletterqueue.topic.name`** → handler mặc định gửi record lỗi vào DLQ (KIP-1034) |
| `processing.exception.handler` (**3.9+**, KIP-1033) | Exception ném từ **user code**: lambda `map/filter`, `Processor#process`, punctuator | `LogAndFailProcessingExceptionHandler` | `LogAndContinueProcessingExceptionHandler`; 4.3 mở rộng cho global store (`processing.exception.handler.global.enabled`) |

- **DLQ Streams (KIP-1034, 4.2)**: header `__streams.errors.exception` / `.message` / `.stacktrace` / `.topic` / `.partition` / `.offset`; app **tự tạo topic DLQ**. Khác Connect: Connect DLQ chỉ cho **sink connector** với `errors.tolerance=all`.
- **`KafkaStreams#setUncaughtExceptionHandler(StreamsUncaughtExceptionHandler)`** (KIP-671; bản nhận `Thread.UncaughtExceptionHandler` đã xoá) trả 1 trong 3: **`REPLACE_THREAD`** (thay thread mới, task xử lý lại — có thể duplicate ở ALOS; mặc định khi không set là **SHUTDOWN_CLIENT**), **`SHUTDOWN_CLIENT`** (dừng instance này), **`SHUTDOWN_APPLICATION`** (dừng **mọi** instance cùng `application.id` qua rebalance protocol — dùng khi lỗi chắc chắn lặp lại ở mọi instance như bug logic/schema).
- `task.timeout.ms` (**300.000**): lỗi tạm (`TimeoutException` tới broker) được retry trong 5 phút trước khi ném ra; đặt 0 → fail ngay.

**11. `KafkaStreams.State` lifecycle & `StateListener`**

- Trạng thái: **`CREATED` → `REBALANCING` → `RUNNING`** ↔ `REBALANCING` (mỗi lần thêm/bớt instance) → `PENDING_SHUTDOWN` → `NOT_RUNNING`; lỗi không phục hồi → **`PENDING_ERROR` → `ERROR`** (terminal, phải tạo instance mới). `state().isRunningOrRebalancing()` để health check.
- `setStateListener((newState, oldState) -> ...)` để log/metrics/readiness probe; **phải gọi trước `start()`**. Interactive Query chỉ hợp lệ khi `RUNNING` (query lúc `REBALANCING` → `InvalidStateStoreException`, retry).
- `close(Duration)` → chờ thread dừng, flush state; luôn thêm `Runtime.getRuntime().addShutdownHook(new Thread(streams::close))`. `cleanUp()` xoá `state.dir` cục bộ — **chỉ gọi khi app không chạy** (dev/reset); production không gọi bừa vì phải restore lại toàn bộ từ changelog.
- Reset ứng dụng Streams (đổi logic, chạy lại từ đầu): `kafka-streams-application-reset.sh --application-id <id> --input-topics ... [--to-earliest]` (xoá internal topic, reset offset input) + `cleanUp()` local, hoặc đơn giản **đổi `application.id`** (= app mới, internal topic mới).

**12. Interactive Queries — state store là "database nhúng"**

- Query state store cục bộ: `streams.store(StoreQueryParameters.fromNameAndType("counts-store", QueryableStoreTypes.keyValueStore()))` → `ReadOnlyKeyValueStore.get(key)/range/all`. Store phải được **đặt tên** qua `Materialized.as(...)` và app đang `RUNNING`.
- **Phân tán**: mỗi instance chỉ có 1 phần key → set **`application.server=host:port`** trên từng instance; dùng `streams.queryMetadataForKey(store, key, keySerializer)` → `KeyQueryMetadata.activeHost()` (và `standbyHosts()`) → tự viết REST/gRPC để **chuyển tiếp request** tới instance đúng. Streams **không** cung cấp RPC layer.
- Từ 3.x có **IQv2**: `streams.query(StateQueryRequest.inStore("x").withQuery(KeyQuery.withKey(k)))` — cho phép query standby (`enableExecutionInfo`, `requireActive`). Đề hiện tại chủ yếu hỏi IQv1 (`store()` + `application.server`).
- ksqlDB **pull query** chính là Interactive Query bọc bằng SQL.

**13. Processor API — `Processor`, `ProcessorContext`, punctuation, attach store**

- Interface **`org.apache.kafka.streams.processor.api.Processor<KIn,VIn,KOut,VOut>`** (bản cũ `org.apache.kafka.streams.processor.Processor` **xoá ở 4.0**): `init(ProcessorContext)` (lấy store, schedule punctuator) → `process(Record<KIn,VIn>)` (mỗi record) → `close()` (huỷ punctuator; **không đóng store**, library quản lý).
- **`ProcessorContext`**: `forward(Record)` / `forward(record, childName)`, `schedule(Duration, PunctuationType, Punctuator)` → `Cancellable`, `commit()` (yêu cầu commit sớm, không đồng bộ), `getStateStore(name)`, `recordMetadata()` (`Optional` — **rỗng trong punctuator**), `applicationId()`, `taskId()`.
- **Punctuation** — 2 loại, đề rất thích hỏi số lần gọi:
  - **`STREAM_TIME`**: theo **event-time**, chỉ tiến khi có record mới; 60 record timestamp 1..60 s + `schedule(10 s)` → gọi **6 lần** bất kể xử lý nhanh chậm; stream idle → **không gọi**.
  - **`WALL_CLOCK_TIME`**: theo đồng hồ hệ thống, độc lập dữ liệu; xử lý 60 record đó trong 20 s → **2 lần**; trong 5 s → **0 lần**. Dùng cho "flush định kỳ mỗi 30 s dù không có dữ liệu".
- **Attach state store**: `Stores.keyValueStoreBuilder(Stores.persistentKeyValueStore("Counts"), Serdes.String(), Serdes.Long())` (RocksDB) hoặc `Stores.inMemoryKeyValueStore` → `topology.addStateStore(builder, "ProcessorName")` hoặc `ProcessorSupplier#stores()` (`ConnectedStoreProvider`) hoặc `KStream.process(supplier, "storeName")`. Có `.withLoggingEnabled(config)` (mặc định) / `.withLoggingDisabled()` / `.withCachingEnabled()`.
- **`ProcessorSupplier#get()` phải trả instance mới mỗi lần** (1 processor / task) — trả singleton → state lẫn lộn giữa task (bug kinh điển trong đề).
- **`processValues(FixedKeyProcessorSupplier)`** đảm bảo không đổi key → không repartition; `process(ProcessorSupplier)` có thể đổi key → repartition (thay `transform/transformValues` đã xoá).
- Store nâng cao: **Timestamped** (`timestampedKeyValueStoreBuilder`, mặc định cho KTable), **Versioned** (`persistentVersionedKeyValueStore(name, historyRetention)` — nhiều phiên bản theo thời gian, cho temporal join; không cache, không IQ).

**14. KIP-1071 Streams Rebalance Protocol + các thay đổi 4.x**

- **KIP-1071** (EA **4.1**, **GA 4.2**): `group.protocol=streams` → app đăng ký thành **streams group** (không phải consumer group), gửi **topology** (sub-topology, source/repartition/changelog topic) lên broker; **group coordinator tính assignment** active/standby/warmup và phát qua `StreamsGroupHeartbeat` — cùng tinh thần **KIP-848** (incremental, không stop-the-world). Tool `kafka-streams-groups.sh` (list/describe/delete/reset-offsets); `kafka-consumer-groups.sh` **không** thấy streams group. Không migrate online classic ↔ streams (dừng hết instance, đổi config). Broker config `group.streams.*` (`group.streams.num.standby.replicas`, `group.streams.session.timeout.ms`…).
- Đã xoá ở 4.0: `through()` → `repartition()`; `branch()` → `split()`; `transform*` → `process/processValues`; `TimeWindows.of/JoinWindows.of/SessionWindows.with`; `exactly_once`/`exactly_once_beta`; PAPI package cũ. 4.3: `kafka-streams-scala` deprecated (KIP-1244), `dsl.store.format=HEADERS` (KIP-1285), changelog offset lưu trong RocksDB (KIP-1035).

**15. `TopologyTestDriver` — unit test không cần broker (domain TEST)**

- Dependency `org.apache.kafka:kafka-streams-test-utils` (scope test, cùng version). `new TopologyTestDriver(topology, props)` với `application.id` + `bootstrap.servers` (giá trị giả, bắt buộc) → thay `KafkaStreams`; xử lý **đồng bộ** (pipe vào → đọc ra ngay), chạy **mili-giây**, không Docker.
- `createInputTopic(topic, keySerializer, valueSerializer)` → `pipeInput(k, v[, timestamp])`, `pipeKeyValueList`, `advanceTime(Duration)` (đẩy event time → đóng window, kích `suppress`); `createOutputTopic(topic, keyDeser, valueDeser)` → `readKeyValue()`, `readRecord()` (kèm timestamp/header), `readKeyValuesToList()`, `readKeyValuesToMap()` (giá trị cuối/key), `isEmpty()`.
- **Thời gian**: `STREAM_TIME` punctuator tự chạy theo timestamp pipe vào; **`WALL_CLOCK_TIME` phải gọi `testDriver.advanceWallClockTime(Duration)`**. Truy cập store: `getKeyValueStore("name")`, `getWindowStore`, `getSessionStore`. Luôn `close()` (try-with-resources) để xoá RocksDB tạm; nên set `state.dir` = temp dir.
- Cache trong test driver flush sau **mỗi record** → thấy **từng** update trung gian (khác production 10 MB). Không test được rebalance/nhiều instance/mạng → cần Testcontainers/EmbeddedKafka (Tuần 7). **`MockProcessorContext`** test 1 `Processor` riêng: bắt `forwarded()`, `committed()`, gọi punctuator **thủ công** qua `scheduledPunctuators()`.

**16. ksqlDB — nhận diện (CCDAK không hỏi cú pháp sâu)**

- **Streaming SQL trên Kafka Streams**: mỗi **persistent query** (`CREATE STREAM ... AS SELECT` = CSAS, `CREATE TABLE ... AS SELECT` = CTAS) biên dịch thành 1 topology chạy trong **ksqlDB Server** (REST **8088**), kết quả ghi ra **topic mới**, DDL lưu trong **command topic**, nhiều server cùng `ksql.service.id` = 1 cụm chia task.
- **STREAM** (immutable, append-only ≈ `KStream`) vs **TABLE** (`PRIMARY KEY`, giá trị mới nhất/key ≈ `KTable`). **Push query** `SELECT ... EMIT CHANGES` → stream kết quả liên tục tới client; **pull query** `SELECT ... FROM table WHERE key = ...` (không `EMIT CHANGES`) → snapshot hiện tại rồi kết thúc (= Interactive Query).
- Window SQL: `WINDOW TUMBLING (SIZE 1 MINUTE, GRACE PERIOD 10 SECONDS)`, `HOPPING (SIZE 5 MINUTES, ADVANCE BY 1 MINUTE)`, `SESSION (5 MINUTES)`; join stream-stream cần `WITHIN`. Interactive mode vs **headless** (`--queries-file`, production).
- Chọn: **Streams** = library Java, kiểm soát tối đa, unit test `TopologyTestDriver`; **ksqlDB** = SQL, server riêng, prototyping/ETL nhanh, không cần Java; **Connect** = di chuyển dữ liệu vào/ra, không xử lý logic phức tạp.

**Java `StreamsConfig` — snippet để nhớ tên config (đề hỏi theo tên Java):**

```java
Properties p = new Properties();
p.put(StreamsConfig.APPLICATION_ID_CONFIG, "orders-enricher");            // = group.id, prefix internal topics, thư mục state
p.put(StreamsConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092,localhost:9094");
p.put(StreamsConfig.DEFAULT_KEY_SERDE_CLASS_CONFIG, Serdes.String().getClass());
p.put(StreamsConfig.DEFAULT_VALUE_SERDE_CLASS_CONFIG, Serdes.String().getClass());
p.put(StreamsConfig.PROCESSING_GUARANTEE_CONFIG, StreamsConfig.EXACTLY_ONCE_V2); // mặc định AT_LEAST_ONCE
p.put(StreamsConfig.COMMIT_INTERVAL_MS_CONFIG, 100);                       // 30000 ALOS → 100 EOS
p.put(StreamsConfig.STATESTORE_CACHE_MAX_BYTES_CONFIG, 10 * 1024 * 1024L); // 10 MB
p.put(StreamsConfig.NUM_STREAM_THREADS_CONFIG, 2);                         // mặc định 1
p.put(StreamsConfig.NUM_STANDBY_REPLICAS_CONFIG, 1);                       // mặc định 0
p.put(StreamsConfig.STATE_DIR_CONFIG, "/var/lib/kafka-streams");           // mặc định /tmp/kafka-streams
p.put(StreamsConfig.REPLICATION_FACTOR_CONFIG, 3);                         // internal topics
p.put(StreamsConfig.APPLICATION_SERVER_CONFIG, "10.0.0.5:7070");           // Interactive Queries
p.put(StreamsConfig.DEFAULT_TIMESTAMP_EXTRACTOR_CLASS_CONFIG, WallclockTimestampExtractor.class);
p.put(StreamsConfig.DESERIALIZATION_EXCEPTION_HANDLER_CLASS_CONFIG, LogAndContinueExceptionHandler.class);
p.put(StreamsConfig.PROCESSING_EXCEPTION_HANDLER_CLASS_CONFIG, LogAndContinueProcessingExceptionHandler.class);
p.put(StreamsConfig.PRODUCTION_EXCEPTION_HANDLER_CLASS_CONFIG, DefaultProductionExceptionHandler.class);
p.put("errors.deadletterqueue.topic.name", "orders-enricher-dlq");         // KIP-1034, 4.2
p.put(StreamsConfig.GROUP_PROTOCOL_CONFIG, "streams");                     // KIP-1071, mặc định classic
p.put(StreamsConfig.producerPrefix(ProducerConfig.COMPRESSION_TYPE_CONFIG), "lz4"); // override client
p.put(StreamsConfig.topicPrefix(TopicConfig.MIN_IN_SYNC_REPLICAS_CONFIG), "2");     // config internal topic
```

### 🅱️ Buổi B — Hands-on (~3.5h)

> 🧪 **Lab cầm tay chỉ việc (từng bước + lệnh + code):** [labs.md](labs.md). Tuần này **bắt buộc Java 17 + Gradle** vì `Kafka Streams` là library JVM; người không muốn Java có Option ksqlDB (Lab 6.7). Dùng lại cluster 3 node Tuần 1 (`docker-compose.cluster.yml`).

- **Lab 6.1 ⭐ — WordCount:** `flatMapValues → groupBy → count → toStream → to`; chạy **2 instance** cùng `application.id` thấy chia task; `kt --list` thấy `-repartition` và `-changelog`; `Topology.describe()` in 2 sub-topology.
- **Lab 6.2 — Windowed aggregation:** tumbling 1 phút + grace 10 s, **có và không `suppress`** → so số update trung gian; thử record late bị drop.
- **Lab 6.3 ⭐ — Join:** `KStream(orders)` ⋈ `KTable(customers)` (co-partition) + `KStream` ⋈ `GlobalKTable(products)` (key khác, không co-partition); cố tình tạo topic lệch partition để thấy `TopologyException`.
- **Lab 6.4 — EOS:** `processing.guarantee=exactly_once_v2` vs `at_least_once`, `kill -9` giữa chừng, đếm duplicate ở output bằng `kcc --isolation-level read_committed`.
- **Lab 6.5 ⭐ — `TopologyTestDriver`:** unit test WordCount + windowed (`advanceTime`) + punctuator (`advanceWallClockTime`), chạy `./gradlew test` không cần broker.
- **Lab 6.6 — Processor API punctuator:** `Processor` + state store + `WALL_CLOCK_TIME` flush mỗi 10 s so với `STREAM_TIME`.
- **Lab 6.7 — Option ksqlDB:** container `cp-ksqldb-server`, `CREATE STREAM`, `CREATE TABLE AS SELECT COUNT`, push query `EMIT CHANGES`, pull query.

### 🅲️ Buổi C — Bổ sung (~2.5h)

**Bảng quyết định: bài toán → API Streams**

| Bài toán | Chọn | Vì sao |
|---|---|---|
| Đếm/sum theo key, key đã đúng | `groupByKey().count()` | Không repartition |
| Đếm theo field trong value | `groupBy((k,v) -> v.field).count()` hoặc `selectKey` + `groupByKey` | Đổi key → 1 repartition topic |
| Chỉ đổi value | `mapValues` | `map` bị đánh dấu repartition dù không đổi key |
| Chia luồng theo điều kiện | `split().branch(...).defaultBranch()` | `branch()` xoá ở 4.0 |
| Enrich event bằng bảng nhỏ (country, product) | `KStream ⋈ GlobalKTable` | Không co-partition, key tuỳ ý |
| Enrich event bằng bảng lớn cùng key | `KStream ⋈ KTable` | Co-partition, chỉ stream trigger |
| Ghép 2 luồng sự kiện trong 10 phút | `KStream ⋈ KStream` + `JoinWindows` | Cần window |
| Bảng orders ⋈ bảng customers (key khác) | `KTable` FK join | Streams tự repartition nội bộ |
| "1 kết quả cuối mỗi window" | `windowedBy(...ofSizeAndGrace).count().suppress(untilWindowCloses)` | Không suppress → nhiều update |
| Phiên người dùng | `SessionWindows.ofInactivityGapAndGrace` | Window động |
| Lookup state qua REST | `Materialized.as("store")` + `application.server` + `queryMetadataForKey` | Interactive Query |
| Flush định kỳ dù không có dữ liệu | PAPI `schedule(..., WALL_CLOCK_TIME, ...)` | `STREAM_TIME` không chạy khi idle |
| Không bao giờ duplicate output | `exactly_once_v2` + consumer `read_committed` | ALOS duplicate khi crash |
| Poison pill làm app chết | `LogAndContinueExceptionHandler` (+ DLQ 4.2) | Mặc định LogAndFail |
| Failover state nhanh | `num.standby.replicas=1` + `state.dir` bền | Mặc định 0, restore từ changelog |

**Streams vs ksqlDB vs Connect vs Consumer thuần**

| | Consumer/Producer thuần | `Kafka Streams` | `ksqlDB` | `Kafka Connect` |
|---|---|---|---|---|
| Mục đích | Xử lý tuỳ ý, tích hợp app | Xử lý stream stateful, window, join | Cùng Streams nhưng bằng SQL | Di chuyển dữ liệu vào/ra hệ thống ngoài |
| Chạy ở | App của bạn | App của bạn (library) | ksqlDB Server (cluster riêng) | Connect worker |
| State | Tự quản | RocksDB + changelog | RocksDB + changelog (ẩn) | Offset nội bộ |
| EOS | Tự viết transaction | `exactly_once_v2` | `processing.guarantee` ksql | Source EOS (3.3+), sink tuỳ connector |
| Test | `MockProducer/MockConsumer` | `TopologyTestDriver` | Test harness ksqlDB | Integration |
| Ngôn ngữ | Bất kỳ | **JVM** | SQL | Cấu hình JSON |

**Đọc thêm (30–40 phút):** `resources/streams-core-concepts-architecture.md` (task, thread, cache, depth-first), `resources/streams-joins.md` (thuộc bảng join), `resources/streams-upgrade-kip-1071-dlq.md` (những gì mới ở 4.x); sách *Kafka: The Definitive Guide* 2nd ed. **Chương 14 (Stream Processing)**; Confluent Developer course *Kafka Streams 101*.

### 🅳 Buổi D — Practice + Review (~2h)

> 📝 **Bộ câu hỏi luyện tập của tuần:** [questions.md](questions.md) — đáp án & giải thích: [answers.md](answers.md). *(bằng tiếng Anh — văn phong đề CCDAK.)*

- Làm 28 câu **không tra tài liệu**, tự chấm, **ghi sổ câu sai** theo nhóm: (1) task/thread/repartition, (2) window/grace/suppress, (3) join matrix, (4) EOS/config default, (5) PAPI/punctuate, (6) testing.
- Tự viết lại **4 bảng bắt buộc** bằng trí nhớ: KStream/KTable/GlobalKTable · 4 window · join matrix · ALOS vs EOS v2.
- **Spaced repetition** mốc **1 / 3 / 7 ngày** cho bộ số: 30.000 → 100 / 10 MB / 1 thread / 0 standby / 24 h grace cũ / 300.000 task.timeout / 8088 / GA 4.2 (KIP-1071, DLQ) / 3.9 (ProcessingExceptionHandler).
- Tuần 7 có **mini-mock CONNECT+STREAMS+TEST ≥70%** → Streams là 12/35 điểm của cụm đó.

## 🧠 PHẢI NHỚ tuần này

| Fact | Con số / Ghi nhớ |
|---|---|
| Kafka Streams là gì | **Library JVM** (Java 11+), không cluster riêng; scale = thêm instance cùng **`application.id` = `group.id`** |
| Số task | = **số partition lớn nhất** của input topic trong sub-topology; thread/instance thừa → **idle** |
| `num.stream.threads` | **1** |
| `num.standby.replicas` | **0**; đặt 1 → failover tức thời, 2× storage, n+1 instance |
| `processing.guarantee` | **`at_least_once`** / `exactly_once_v2` (2.6+, broker ≥ 2.5, ≥ 3 broker mặc định); `exactly_once`/`_beta` xoá 4.0 |
| `commit.interval.ms` | **30.000** ALOS → **100** EOS |
| `statestore.cache.max.bytes` | **10 MB** (10.485.760); lý do `count()` không emit mỗi record; cache=0 → mọi update |
| Internal topics | `<app.id>-<name>-repartition` (đổi key + stateful) · `<app.id>-<store>-changelog` (**compacted**; window store `compact,delete`) |
| Repartition | `map/flatMap/selectKey/groupBy/process` đánh dấu; `groupByKey/mapValues/filter/processValues` **không** |
| `KStream` / `KTable` / `GlobalKTable` | insert / upsert + tombstone / bản sao **đầy đủ** mỗi instance |
| 4 window | Tumbling (`ofSizeWithNoGrace`) · Hopping (`advanceBy` < size) · Sliding (`ofTimeDifferenceAndGrace`) · Session (`ofInactivityGapAndGrace`) |
| Grace | Late record > end + grace → **drop**; API cũ grace ngầm **24 h** (xoá 4.0) |
| `suppress` | `untilWindowCloses(BufferConfig.unbounded())` → 1 kết quả cuối/window; cần stream time tiến |
| Join cần window | **Chỉ KStream-KStream** (`JoinWindows`) |
| Join không cần co-partition | **KStream-GlobalKTable** và **KTable-KTable FK** |
| Co-partition | Cùng **số partition** + cùng **partitioner**; Streams chỉ check số partition (`TopologyException`) |
| Time | Event (`FailOnInvalidTimestamp` mặc định) / ingestion (`LogAppendTime`) / processing (`WallclockTimestampExtractor`); stream time = max đã thấy, chỉ tiến khi có record |
| Punctuate | `STREAM_TIME` (theo dữ liệu, idle không chạy) vs `WALL_CLOCK_TIME` (theo đồng hồ) |
| Exception handlers | deserialization **LogAndFail** (→ LogAndContinue) · production **Default = FAIL** · processing (3.9) LogAndFail; DLQ `errors.deadletterqueue.topic.name` (**4.2**) |
| `StreamsUncaughtExceptionHandler` | `REPLACE_THREAD` / `SHUTDOWN_CLIENT` / `SHUTDOWN_APPLICATION` |
| `KafkaStreams.State` | CREATED → REBALANCING ↔ RUNNING → PENDING_SHUTDOWN → NOT_RUNNING; PENDING_ERROR → **ERROR** (terminal) |
| Interactive Query | `Materialized.as(name)` + `store()`; phân tán cần **`application.server`** + `queryMetadataForKey` |
| `TopologyTestDriver` | `kafka-streams-test-utils`; không broker, đồng bộ; wall-clock cần **`advanceWallClockTime`** |
| KIP-1071 | Streams Rebalance Protocol, **GA 4.2**, `group.protocol=streams`, `kafka-streams-groups.sh` |
| `state.dir` / `task.timeout.ms` | `/tmp/kafka-streams` (đổi sang volume bền) / **300.000** ms |
| ksqlDB | Port **8088**; STREAM vs TABLE; push (`EMIT CHANGES`) vs pull; CSAS/CTAS = persistent query |

## ⚠️ Bẫy đề hay gặp

- Thấy "topic 6 partition, muốn 12 thread xử lý song song" → dễ chọn `num.stream.threads=12`, nhưng đúng là **tối đa 6 task** → phải **tăng partition** input topic; thread thứ 7+ idle.
- Thấy "Streams cần cluster riêng để deploy" → **sai**; Streams là library, deploy như app thường; scale bằng instance cùng `application.id`.
- Thấy "dùng `map` để đổi value rồi `groupByKey().count()`" → tưởng không repartition, nhưng `map` **đã đánh dấu** repartition → topic `-repartition` xuất hiện; dùng **`mapValues`**.
- Thấy "`count()` mà output không có mỗi record" → dễ nghĩ bug/mất dữ liệu, nhưng đó là **record cache 10 MB + `commit.interval.ms`** gom update; đặt `statestore.cache.max.bytes=0` để thấy từng update (kết quả cuối không đổi).
- Thấy "join 2 KStream" thiếu `JoinWindows` → **compile không qua**; KStream-KStream **luôn** windowed. Ngược lại, KStream-KTable **không** có window.
- Thấy "join stream với bảng tham chiếu key khác nhau, topic khác số partition" → chọn `KTable` là **sai** (cần co-partition) → **`GlobalKTable`** với `KeyValueMapper`.
- Thấy "2 topic cùng 6 partition nhưng producer dùng partitioner khác" → tưởng co-partitioned; Streams **không phát hiện được** → join sai lệch âm thầm.
- Thấy "record đến muộn vẫn phải được tính" → tăng **grace period**, không phải tăng window size; record sau end + grace **bị drop im lặng** (metric `dropped-records`).
- Thấy "`suppress(untilWindowCloses)` nhưng không thấy kết quả" → không phải bug; **stream time chưa tiến** qua end + grace vì không có record mới.
- Thấy "`exactly_once_v2` cũng chống duplicate khi gọi REST trong `foreach`" → **sai**; EOS chỉ bao **Kafka topic + state + offset**; side effect ngoài cần idempotent.
- Thấy "`exactly_once_v2` trên cluster 1 broker dev" → fail vì `transaction.state.log.replication.factor=3`/`min.isr=2` mặc định → hạ 2 config đó hoặc dùng ≥ 3 broker.
- Thấy "poison pill làm app dừng, muốn bỏ qua" → chọn `StreamsUncaughtExceptionHandler.REPLACE_THREAD` là **sai** (thread mới đọc lại record đó, lặp vô hạn) → **`LogAndContinueExceptionHandler`** cho deserialization.
- Thấy "bug logic ném exception ở mọi instance" → `REPLACE_THREAD` chỉ kéo dài sự cố → **`SHUTDOWN_APPLICATION`**.
- Thấy "punctuator `STREAM_TIME` 1 phút không chạy dù đã chờ 5 phút" → vì **không có record mới**; muốn theo đồng hồ dùng **`WALL_CLOCK_TIME`**.
- Thấy "ProcessorSupplier trả cùng 1 object" → tưởng tiết kiệm, nhưng **mỗi task cần instance riêng** → state lẫn giữa task.
- Thấy "Interactive Query trả `InvalidStateStoreException` lúc khởi động" → không phải cấu hình sai; app đang **`REBALANCING`** → retry khi `RUNNING`.
- Thấy "test topology với `TopologyTestDriver`, punctuator wall-clock không chạy" → phải gọi **`advanceWallClockTime`**; test driver không có đồng hồ thật.
- Thấy "đổi `application.id` để deploy version mới" → mất **toàn bộ state + offset** (app mới); giữ id nếu muốn tiếp tục, `kafka-streams-application-reset.sh` nếu muốn reset có kiểm soát.
- Thấy "ksqlDB `SELECT * FROM table WHERE id=5`" → là **pull query** (snapshot, kết thúc); thêm `EMIT CHANGES` mới là **push**.

## 🔁 Phản xạ nhanh (keyword → đáp án)

| Thấy từ khoá | Bật ngay |
|---|---|
| "stream processing library, no separate cluster" | **Kafka Streams** |
| "scale Streams app horizontally" | Thêm instance **cùng `application.id`** (≤ số partition) |
| "maximum parallelism of a Streams app" | **Số partition** input (task) |
| "latest value per key / upsert / tombstone" | **`KTable`** |
| "each record is an independent event" | **`KStream`** |
| "small reference data replicated to every instance" | **`GlobalKTable`** |
| "internal topic `-repartition`" | Đổi key (`selectKey/map/groupBy`) + stateful |
| "internal topic `-changelog`, compacted" | State store backup → restore/standby |
| "fast failover of state stores" | **`num.standby.replicas=1`** |
| "fixed, non-overlapping windows" | **Tumbling** `TimeWindows.ofSizeWithNoGrace` |
| "overlapping windows, advance interval" | **Hopping** `.advanceBy` |
| "windows based on record time difference / join" | **Sliding** `SlidingWindows` / `JoinWindows` |
| "inactivity gap / user session" | **Session** `SessionWindows.ofInactivityGapAndGrace` |
| "late-arriving records" | **Grace period**; sau grace → drop |
| "emit only the final result per window" | **`suppress(untilWindowCloses(unbounded()))`** |
| "join two event streams within N minutes" | **KStream-KStream** + `JoinWindows` + co-partition |
| "enrich stream with table, different key, no co-partitioning" | **KStream-GlobalKTable** + `KeyValueMapper` |
| "join two tables on foreign key" | **KTable-KTable FK join** |
| "`TopologyException ... not co-partitioned`" | Số partition khác → `repartition()` |
| "no duplicates in output after crash" | **`processing.guarantee=exactly_once_v2`** |
| "commit every 100 ms" | EOS v2 default `commit.interval.ms` |
| "why aggregation output is batched" | **`statestore.cache.max.bytes` 10 MB** + `commit.interval.ms` |
| "skip records that fail to deserialize" | **`LogAndContinueExceptionHandler`** |
| "exception in user lambda, keep running" | **`processing.exception.handler`** = `LogAndContinueProcessingExceptionHandler` (3.9+) |
| "send failed records to a DLQ topic in Streams" | **`errors.deadletterqueue.topic.name`** (KIP-1034, 4.2) |
| "stop all instances on unrecoverable error" | **`SHUTDOWN_APPLICATION`** |
| "periodic action based on system clock" | **`WALL_CLOCK_TIME`** punctuator |
| "periodic action driven by event time" | **`STREAM_TIME`** punctuator (idle → không chạy) |
| "query state store from another instance" | **`application.server`** + `queryMetadataForKey` |
| "unit test topology without broker" | **`TopologyTestDriver`** (`kafka-streams-test-utils`) |
| "test wall-clock punctuator" | **`advanceWallClockTime`** |
| "broker-side task assignment for Streams" | **KIP-1071** `group.protocol=streams` (GA 4.2) |
| "SQL over Kafka, continuous query" | **ksqlDB** push query `EMIT CHANGES` |
| "SQL lookup current value, returns once" | ksqlDB **pull query** |

## 🧪 Lab checklist

- [ ] Lab 6.1 ⭐ — WordCount chạy; 2 instance chia task (log `Assigned tasks`); `kt --list` có `wordcount-app-KSTREAM-AGGREGATE-STATE-STORE-0000000003-repartition` và `-changelog`; `Topology.describe()` in 2 sub-topology.
- [ ] Lab 6.2 — Windowed count tumbling 1 phút: bản không suppress ra nhiều dòng/window, bản suppress ra đúng 1 dòng/window; record late bị drop.
- [ ] Lab 6.3 ⭐ — `orders ⋈ customers` (KTable) và `⋈ products` (GlobalKTable) ra bản ghi enriched; topic lệch partition → `TopologyException`.
- [ ] Lab 6.4 — `kill -9` với `at_least_once` thấy duplicate ở output, với `exactly_once_v2` + `read_committed` không duplicate.
- [ ] Lab 6.5 ⭐ — `./gradlew test` xanh: WordCount, windowed (`advanceTime`), punctuator (`advanceWallClockTime`).
- [ ] Lab 6.6 — PAPI punctuator `WALL_CLOCK_TIME` flush mỗi 10 s dù không có record; đổi `STREAM_TIME` thấy khác.
- [ ] Lab 6.7 (Option) — ksqlDB `CREATE STREAM`, `CTAS COUNT`, push query, pull query.
- [ ] Tự viết lại 4 bảng bắt buộc bằng trí nhớ.

## 🚪 Cổng tự kiểm tra (phải trả lời trôi chảy mới sang tuần sau)

- **Topic input 8 partition, chạy 3 instance mỗi instance 4 thread. Bao nhiêu thread có việc? Muốn dùng hết 12 thread thì làm gì?**
  **Đáp án gọn:** 8 task → 8 thread có việc, 4 idle. Tăng partition input ≥ 12 (không thể giảm sau đó, phá key mapping).
- **`selectKey(...).groupByKey().count()` sinh ra topic nội bộ gì? `groupByKey().count()` thì sao?**
  **Đáp án gọn:** `<app>-<name>-repartition` (vì `selectKey` đổi key + stateful) và `<app>-<store>-changelog`. Không đổi key → chỉ có `-changelog`.
- **Kể 4 loại window và 1 câu mô tả nghiệp vụ cho mỗi loại.**
  **Đáp án gọn:** Tumbling (đếm mỗi 5 phút không chồng), Hopping (5 phút cập nhật mỗi 1 phút), Sliding (2 sự kiện cách nhau ≤ 10 phút), Session (phiên đóng khi im lặng > 30 phút).
- **Join nào cần window? Join nào không cần co-partition? Co-partition gồm 2 điều kiện gì?**
  **Đáp án gọn:** Chỉ KStream-KStream cần `JoinWindows`. KStream-GlobalKTable và KTable FK join không cần co-partition. Co-partition = cùng số partition + cùng partitioner (Streams chỉ kiểm tra số partition).
- **`exactly_once_v2` đổi những default nào và cần broker ra sao?**
  **Đáp án gọn:** `commit.interval.ms` 30.000 → 100; producer idempotent + transactional (1/thread); consumer `read_committed`; broker ≥ 2.5, `transaction.state.log` RF 3 / min.isr 2 → ≥ 3 broker.
- **Vì sao `count()` không emit mỗi record? Làm sao để emit đúng 1 lần/window?**
  **Đáp án gọn:** Record cache 10 MB gom update cùng key, flush theo `commit.interval.ms`. Emit 1 lần/window → `suppress(untilWindowCloses(unbounded()))` + window có grace.
- **Poison pill làm app chết — sửa config nào? Bug logic ném exception ở mọi instance — handler nên trả gì?**
  **Đáp án gọn:** `deserialization.exception.handler=LogAndContinueExceptionHandler` (thêm DLQ 4.2). `StreamsUncaughtExceptionHandler` trả `SHUTDOWN_APPLICATION` (REPLACE_THREAD chỉ lặp lỗi).
- **`STREAM_TIME` vs `WALL_CLOCK_TIME`: 60 record timestamp 1..60 s, schedule 10 s, xử lý xong trong 20 s — mỗi loại gọi bao nhiêu lần? Trong `TopologyTestDriver` khác gì?**
  **Đáp án gọn:** STREAM_TIME 6 lần; WALL_CLOCK_TIME 2 lần. Test driver: stream-time tự chạy theo timestamp pipe vào, wall-clock phải `advanceWallClockTime`.

## 📎 Tài nguyên tuần này

> 📂 **Đã crawl sẵn tài liệu chính thức vào** [`resources/`](resources/INDEX.md) — đọc offline được (8 file: concepts/architecture, DSL, joins, config, Processor API, testing, KIP-1071/DLQ, ksqlDB).

- Apache Kafka Docs: [Kafka Streams](https://kafka.apache.org/documentation/streams/) — *Core Concepts*, *Architecture*, *Developer Guide* (DSL API, Processor API, Configuring, Testing, Interactive Queries, Memory Management), *Upgrade Guide*; [Streams Configs](https://kafka.apache.org/documentation/#streamsconfigs); [KafkaStreams Javadoc 4.3](https://kafka.apache.org/43/javadoc/org/apache/kafka/streams/KafkaStreams.html).
- Confluent Docs: [Kafka Streams for Confluent Platform](https://docs.confluent.io/platform/current/streams/overview.html) (bản sao có ghi chú CP version) · [ksqlDB Concepts](https://docs.confluent.io/platform/current/ksqldb/concepts/index.html).
- KIP: [KIP-1071 Streams Rebalance Protocol](https://cwiki.apache.org/confluence/display/KAFKA/KIP-1071%3A+Streams+Rebalance+Protocol) · [KIP-1034 Dead letter queue in Kafka Streams](https://cwiki.apache.org/confluence/display/KAFKA/KIP-1034%3A+Dead+letter+queue+in+Kafka+Streams) · [KIP-1033 ProcessingExceptionHandler](https://cwiki.apache.org/confluence/display/KAFKA/KIP-1033%3A+Add+Kafka+Streams+exception+handler+for+exceptions+occurring+during+processing) · [KIP-671 StreamsUncaughtExceptionHandler](https://cwiki.apache.org/confluence/display/KAFKA/KIP-671%3A+Introduce+Kafka+Streams+Specific+Uncaught+Exception+Handler).
- Khoá học: Confluent Developer — *Kafka Streams 101* (miễn phí, có hands-on) + *ksqlDB 101*; Stephane Maarek — *Apache Kafka Series: Kafka Streams for Data Processing*; sách *Kafka: The Definitive Guide* 2nd ed. — **Chương 14 Stream Processing**; *Kafka Streams in Action* 2nd ed. (Bill Bejeck) — chương DSL, windowing, joins, Processor API, testing.

## ✅ Checklist hoàn thành Tuần 6

- [ ] Hoàn thành 4 buổi A/B/C/D
- [ ] Thuộc lòng bảng "PHẢI NHỚ" (30.000 → 100 / 10 MB / 1 / 0 / GA 4.2 / 3.9 / 8088)
- [ ] Tự viết lại 4 bảng bắt buộc (KStream–KTable–GlobalKTable, 4 window, join matrix, ALOS vs EOS v2) bằng trí nhớ
- [ ] Hoàn thành 6 lab Java (6.1, 6.3, 6.5 bắt buộc) hoặc 6.7 ksqlDB thay 6.1 nếu không dùng Java
- [ ] Làm xong 28 câu [questions.md](questions.md) ≥ 70%, xem lại 100% câu sai
- [ ] Vượt Cổng tự kiểm tra (8 câu)
