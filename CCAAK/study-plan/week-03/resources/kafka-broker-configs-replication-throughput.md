# Broker Configs 4.3 — nhóm replication, durability, fetcher, quota window (kèm Update Mode)

> **Nguồn (official):** https://kafka.apache.org/43/generated/kafka_config.html
> **Tuần:** 3 — Cluster Config II: replication & durability, quotas, throughput · **Loại:** Apache Kafka 4.3 Documentation (Configuration → Broker Configs)
> ⚠️ Nội dung dưới đây được crawl tự động từ trang gốc và **lọc lấy đúng nhóm config của Tuần 3** (mô tả giữ nguyên tiếng Anh) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- **Cột `Update Mode` quan trọng ngang cột `Default`.** `cluster-wide` / `per-broker` = đổi được **lúc chạy** bằng `kafka-configs.sh`; **`read-only` = phải restart broker**. Đề CCAAK rất hay hỏi "sửa thế nào mà **không restart**".
- Đổi được lúc chạy (cluster-wide): **`num.replica.fetchers`**, `num.io.threads`, `num.network.threads`, `background.threads`, `min.insync.replicas`, **`unclean.leader.election.enable`**, `compression.type`, `message.max.bytes`, `num.recovery.threads.per.data.dir`.
- **Phải restart (read-only)**: `replica.lag.time.max.ms`, `auto.leader.rebalance.enable`, `leader.imbalance.check.interval.seconds`, `replica.fetch.max.bytes`, `replica.fetch.response.max.bytes`, `queued.max.requests`, `socket.send/receive.buffer.bytes`, `controlled.shutdown.enable`, `offsets.topic.replication.factor`, `transaction.state.log.*`.
- **Durability mặc định là YẾU**: `default.replication.factor` **1**, `min.insync.replicas` **1**, `num.partitions` **1**. Production phải chủ động đặt **RF 3 / min.isr 2**. Ngược lại, internal topic mặc định đã **mạnh**: `offsets.topic.replication.factor` **3**, `transaction.state.log.replication.factor` **3**, `transaction.state.log.min.isr` **2** → cluster lab **1 broker** phải hạ cả ba xuống **1** nếu không sẽ lỗi khi tạo topic internal.
- `replica.lag.time.max.ms` **30000** — cũng là ngưỡng duy nhất quyết định follower rơi khỏi ISR. Docs khuyến cáo `replica.fetch.wait.max.ms` (**500**) phải **luôn nhỏ hơn** nó, nếu không ISR co giãn liên tục với topic ít traffic.
- Tăng tốc follower bắt kịp: **`num.replica.fetchers`** mặc định **1**. Tổng số fetcher trên mỗi broker bị chặn bởi `num.replica.fetchers × số broker`. Tăng → tăng song song I/O, đổi lại tốn CPU và bộ nhớ.
- Kích thước fetch của follower: `replica.fetch.max.bytes` **1048576** (1 MiB, **per partition**) và `replica.fetch.response.max.bytes` **10485760** (10 MiB, **cả response**). Cả hai **không phải trần tuyệt đối** — batch đầu tiên lớn hơn vẫn được trả để không kẹt. Trần thật của record batch là `message.max.bytes` (**1048588**) / topic `max.message.bytes`.
- `compression.type` ở broker mặc định **`producer`** = **giữ nguyên codec của producer, KHÔNG giải nén rồi nén lại**. Đặt giá trị khác (`zstd`, `lz4`…) buộc broker **recompress** → tốn CPU broker và phá zero-copy khi gửi cho consumer.
- Thread & hàng đợi: `num.network.threads` **3** (mỗi listener một pool riêng), `num.io.threads` **8**, `background.threads` **10**, `queued.max.requests` **500**, `num.recovery.threads.per.data.dir` **2** (đổi từ 1 ở 4.0).
- Socket: `socket.send.buffer.bytes` / `socket.receive.buffer.bytes` **102400** (100 KiB) cho client; riêng **`replica.socket.receive.buffer.bytes` = 65536 (64 KiB)** cho đường replication — đây là con số dễ nhầm.
- Cửa sổ đo quota: `quota.window.num` **11** × `quota.window.size.seconds` **1** giây; tương tự `controller.quota.window.*` và `replication.quota.window.*` (dùng cho throttle khi reassign).
- `broker.session.timeout.ms` **9000** — KRaft dùng nó để kết luận broker offline (khác hẳn `session.timeout.ms` 45000 của consumer).

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Nhóm 1 — Durability & replication factor

| Config | Type | Default | Update Mode | Mô tả (nguyên văn, rút gọn) |
|---|---|---|---|---|
| `min.insync.replicas` | int | **1** | **cluster-wide** | "Specifies the minimum number of in-sync replicas (including the leader) required for a write to succeed when a producer sets `acks` to 'all' (or '-1'). […] If `acks=all` and the current ISR set contains fewer than `min.insync.replicas` members, then the producer will raise an exception (either `NotEnoughReplicas` or `NotEnoughReplicasAfterAppend`). […] A typical scenario would be to create a topic with a replication factor of 3, set `min.insync.replicas` to 2, and produce with `acks` of 'all'. […] Note that when the Eligible Leader Replicas feature is enabled, the semantics of this config changes." |
| `default.replication.factor` | int | **1** | read-only | Dùng cho auto topic creation, internal Streams topic creation, và `AdminClient#createTopics` khi RF = -1. |
| `offsets.topic.replication.factor` | short | **3** | read-only | RF của `__consumer_offsets`. |
| `transaction.state.log.replication.factor` | short | **3** | read-only | RF của `__transaction_state`. |
| `transaction.state.log.min.isr` | int | **2** | read-only | "Overridden `min.insync.replicas` config for the transaction topic." |
| `unclean.leader.election.enable` | boolean | **false** | **cluster-wide** | "Indicates whether to enable replicas not in the ISR set to be elected as leader as a last resort, even though doing so may result in data loss. **Note: In KRaft mode, when enabling this config dynamically, it needs to wait for the unclean leader election thread to trigger election periodically (default is 5 minutes). Please run `kafka-leader-election.sh` with unclean option to trigger the unclean leader election immediately if needed.**" |

### Nhóm 2 — ISR, leader election, high watermark

| Config | Type | Default | Update Mode | Mô tả (nguyên văn, rút gọn) |
|---|---|---|---|---|
| `replica.lag.time.max.ms` | long | **30000 (30 seconds)** | read-only | "If a follower hasn't sent any fetch requests or hasn't consumed up to the leader's log end offset for at least this time, the leader will remove the follower from ISR." |
| `auto.leader.rebalance.enable` | boolean | **true** | read-only | "Enables auto leader balancing. A background thread checks the distribution of partition leaders at regular intervals, configurable by `leader.imbalance.check.interval.seconds`. If the leader is imbalanced, leader rebalance to the preferred leader for partitions is triggered." |
| `leader.imbalance.check.interval.seconds` | long | **300** | read-only | "The frequency with which the partition rebalance check is triggered by the controller." |
| `replica.high.watermark.checkpoint.interval.ms` | long | **5000 (5 seconds)** | read-only | "The frequency with which the high watermark is saved out to disk." |
| `broker.session.timeout.ms` | int | **9000 (9 seconds)** | read-only | Thời gian controller chờ heartbeat trước khi coi broker offline (KRaft). |
| `controlled.shutdown.enable` | boolean | **true** | read-only | Bật chuyển leader có trật tự khi tắt broker. |

### Nhóm 3 — Follower fetcher & throughput của replication

| Config | Type | Default | Update Mode | Mô tả (nguyên văn, rút gọn) |
|---|---|---|---|---|
| `num.replica.fetchers` | int | **1** | **cluster-wide** | "Number of fetcher threads used to replicate records from each source broker. The total number of fetchers on each broker is bound by `num.replica.fetchers` multiplied by the number of brokers in the cluster. Increasing this value can increase the degree of I/O parallelism in the follower and leader broker at the cost of higher CPU and memory utilization." |
| `replica.fetch.max.bytes` | int | **1048576 (1 mebibyte)** | read-only | "The number of bytes of messages to attempt to fetch for each partition. **This is not an absolute maximum**, if the first record batch in the first non-empty partition of the fetch is larger than this value, the record batch will still be returned to ensure that progress can be made. The maximum record batch size accepted by the broker is defined via `message.max.bytes` (broker config) or `max.message.bytes` (topic config)." |
| `replica.fetch.response.max.bytes` | int | **10485760 (10 mebibytes)** | read-only | "Maximum bytes expected for the entire fetch response. Records are fetched in batches, and if the first record batch in the first non-empty partition of the fetch is larger than this value, the record batch will still be returned to ensure that progress can be made. As such, this is not an absolute maximum." |
| `replica.fetch.min.bytes` | int | **1** | read-only | "Minimum bytes expected for each fetch response. If not enough bytes, wait up to `replica.fetch.wait.max.ms`." |
| `replica.fetch.wait.max.ms` | int | **500** | read-only | "The maximum wait time for each fetcher request issued by follower replicas. **This value should always be less than the `replica.lag.time.max.ms` at all times to prevent frequent shrinking of ISR for low throughput topics.**" |
| `replica.socket.receive.buffer.bytes` | int | **65536 (64 kibibytes)** | read-only | "The socket receive buffer for network requests to the leader for replicating data." |
| `replica.socket.timeout.ms` | int | **30000 (30 seconds)** | read-only | "The socket timeout for network requests. Its value should be at least `replica.fetch.wait.max.ms`." |
| `replica.selector.class` | string | **null** | read-only | "The fully qualified class name that implements `ReplicaSelector`. This is used by the broker to find the preferred read replica. By default, we use an implementation that returns the leader." |
| `num.replica.alter.log.dirs.threads` | int | **null** | read-only | "The number of threads that can move replicas between log directories… The default value is equal to the number of directories specified in the `log.dir` or `log.dirs` configuration property." |

### Nhóm 4 — Thread, hàng đợi, socket, nén phía broker

| Config | Type | Default | Update Mode | Mô tả (nguyên văn, rút gọn) |
|---|---|---|---|---|
| `num.io.threads` | int | **8** | **cluster-wide** | "The number of threads that the server uses for processing requests, which may include disk I/O." |
| `num.network.threads` | int | **3** | **cluster-wide** | "The number of threads that the server uses for receiving requests from the network and sending responses to the network. **Noted: each listener (except for controller listener) creates its own thread pool.**" |
| `background.threads` | int | **10** | **cluster-wide** | "The number of threads to use for various background processing tasks." |
| `queued.max.requests` | int | **500** | read-only | Số request tối đa xếp hàng chờ I/O thread. |
| `num.recovery.threads.per.data.dir` | int | **2** | **cluster-wide** | "The number of threads per data directory to be used for log recovery at startup and flushing at shutdown." |
| `socket.send.buffer.bytes` | int | **102400 (100 kibibytes)** | read-only | Socket buffer gửi cho client. |
| `socket.receive.buffer.bytes` | int | **102400 (100 kibibytes)** | read-only | Socket buffer nhận từ client. |
| `compression.type` | string | **producer** | **cluster-wide** | "Specify the final compression type for a given topic. This configuration accepts the standard compression codecs ('gzip', 'snappy', 'lz4', 'zstd'). It additionally accepts 'uncompressed' which is equivalent to no compression; and **'producer' which means retain the original compression codec set by the producer**." |
| `message.max.bytes` | int | **1048588** | **cluster-wide** | Kích thước record batch lớn nhất broker chấp nhận. |

### Nhóm 5 — Cửa sổ đo quota (quota window)

| Config | Type | Default | Update Mode | Mô tả (nguyên văn) |
|---|---|---|---|---|
| `quota.window.num` | int | **11** | read-only | "The number of samples to retain in memory for client quotas." |
| `quota.window.size.seconds` | int | **1** | read-only | "The time span of each sample for client quotas." |
| `controller.quota.window.num` | int | **11** | read-only | "The number of samples to retain in memory for controller mutation quotas." |
| `controller.quota.window.size.seconds` | int | **1** | read-only | "The time span of each sample for controller mutations quotas." |
| `replication.quota.window.num` | int | **11** | read-only | "The number of samples to retain in memory for replication quotas." |
| `replication.quota.window.size.seconds` | int | **1** | read-only | "The time span of each sample for replication quotas." |
| `alter.log.dirs.replication.quota.window.num` | int | **11** | read-only | "The number of samples to retain in memory for alter log dirs replication quotas." |
| `client.quota.callback.class` | class | null | read-only | "The fully qualified name of a class that implements the `ClientQuotaCallback` interface, which is used to determine quota limits applied to client requests. By default, the `<user>` and `<client-id>` quotas that are stored and applied. **For any given request, the most specific quota that matches the user principal of the session and the client-id of the request is applied.**" |

### Cách tự kiểm chứng trên cluster của bạn

```bash
# In ra giá trị hiệu lực + nguồn (synonyms) của một nhóm config trên broker id 2
kafka-configs.sh --bootstrap-server kafka-1:19092 --describe --entity-type brokers --entity-name 2 --all \
  | grep -E "^\s+(min.insync.replicas|unclean.leader.election.enable|replica.lag.time.max.ms|num.replica.fetchers|replica.fetch.max.bytes|replica.fetch.response.max.bytes|auto.leader.rebalance.enable|leader.imbalance.check.interval.seconds|compression.type|num.io.threads|num.network.threads|quota.window.num)="
```

> Dòng kết quả có dạng `min.insync.replicas=2 sensitive=false synonyms={STATIC_BROKER_CONFIG:min.insync.replicas=2, DEFAULT_CONFIG:min.insync.replicas=1}` — đọc **synonym đầu tiên** để biết giá trị đang tới từ đâu (dynamic topic → dynamic broker → dynamic default → static → default).
