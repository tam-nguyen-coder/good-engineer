# Apache Kafka — Basic Kafka Operations: bộ CLI của người vận hành

> **Nguồn (official):** https://kafka.apache.org/43/operations/basic-kafka-operations/
> **Tuần:** 1 — Nền tảng vận hành + `KRaft` in production · **Loại:** Apache Kafka Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- **Mọi lệnh admin trong Kafka 4.x đều dùng `--bootstrap-server`** (hoặc `--bootstrap-controller` khi nói chuyện trực tiếp với controller). Không còn `--zookeeper` ở bất kỳ tool nào — thấy `--zookeeper` trong một phương án là dấu hiệu gần như chắc chắn của đáp án sai.
- Tăng partition bằng `kafka-topics.sh --alter --partitions 40`. Docs cảnh báo thẳng: việc này **đổi cách key ánh xạ sang partition** — record cùng key sau đó rơi vào partition khác, và consumer đang `auto.offset.reset=latest` có thể **bỏ sót** message ở partition mới. **Không giảm được partition.** Và **tuyệt đối không sửa tay** topic nội bộ (`__consumer_offsets`, `__transaction_state`).
- `controlled.shutdown.enable=true` (mặc định) cho broker **đồng bộ log xuống đĩa và chuyển leadership đi trước khi tắt** → giảm thời gian partition không có leader. Đây là lý do rolling restart phải tắt broker "đúng cách" thay vì `kill -9`.
- `auto.leader.rebalance.enable=true` (mặc định) tự trả leader về **preferred replica** (replica **đầu tiên** trong danh sách `Replicas`). Muốn làm ngay lập tức: `kafka-leader-election.sh --election-type preferred --all-topic-partitions`.
- `broker.rack=<id>` làm Kafka **rải replica của cùng một partition sang các rack khác nhau** → chịu được mất cả một rack/AZ, không chỉ một broker.
- Mở rộng cluster là **3 bước có thứ tự**: `--generate` (sinh plan từ `topics-to-move.json` + `--broker-list`) → `--execute` → `--verify`. Broker mới **không tự nhận partition** nào; không chạy reassignment thì nó nằm không.
- **Throttle khi reassign**: `--throttle 50000000` (byte/s) lúc `--execute`; đổi giữa chừng bằng `--additional --execute --throttle ...`. Throttle được ghi thành broker config `leader.replication.throttled.rate` / `follower.replication.throttled.rate` + danh sách replica bị throttle ở topic — **`--verify` là bước gỡ throttle**, quên chạy là cluster bị bóp băng thông replication vĩnh viễn.
- **Tăng replication factor** không làm bằng `kafka-topics.sh`, mà bằng `kafka-reassign-partitions.sh` với file JSON liệt kê đủ replica mới.
- Rút broker khỏi cluster (Kafka 4.x): **cordon** log dir (`kafka-configs.sh --add-config cordoned.log.dirs="*" --entity-type brokers --entity-name 1`) → reassign partition đi nơi khác → `kafka-cluster.sh unregister --id 1`.
- Quota đặt bằng `kafka-configs.sh` với `--entity-type users` và/hoặc `--entity-type clients`: `producer_byte_rate`, `consumer_byte_rate`, `request_percentage`.
- `kafka-consumer-groups.sh --describe` in cột `CURRENT-OFFSET / LOG-END-OFFSET / LAG` — **LAG = LOG-END-OFFSET − CURRENT-OFFSET**, tức lag tính theo **offset đã commit**, không phải theo vị trí đọc hiện tại của client.

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Adding and Removing Topics

```bash
$ bin/kafka-topics.sh --bootstrap-server localhost:9092 --create --topic my_topic_name \
    --partitions 20 --replication-factor 3 --config x=y
```

"The replication factor controls how many servers will replicate each message" — a factor of 2 or 3 is recommended. The partition count affects how data is distributed across brokers and bounds consumer parallelism.

```bash
$ bin/kafka-topics.sh --bootstrap-server localhost:9092 --delete --topic my_topic_name
```

### Modifying Topics

Add partitions:

```bash
$ bin/kafka-topics.sh --bootstrap-server localhost:9092 --alter --topic my_topic_name \
    --partitions 40
```

**Critical warning**: increasing partitions changes key-distribution logic. Messages with identical keys may route to different partitions after the expansion. Consumers with `auto.offset.reset=latest` risk missing messages in the new partitions. Never manually modify internal topics such as `__consumer_offsets` or `__transaction_state`.

Add and remove configs:

```bash
$ bin/kafka-configs.sh --bootstrap-server localhost:9092 --entity-type topics \
    --entity-name my_topic_name --alter --add-config x=y

$ bin/kafka-configs.sh --bootstrap-server localhost:9092 --entity-type topics \
    --entity-name my_topic_name --alter --delete-config x
```

### Graceful Shutdown

```
controlled.shutdown.enable=true
```

This allows the broker to "sync all its logs to disk" and migrate leadership before stopping, minimizing partition unavailability.

### Balancing Leadership

```
auto.leader.rebalance.enable=true
```

Or manually restore preferred replicas:

```bash
$ bin/kafka-leader-election.sh --bootstrap-server localhost:9092 \
    --election-type preferred --all-topic-partitions
```

The system designates preferred leaders based on replica list position.

### Balancing Replicas Across Racks

```
broker.rack=my-rack-id
```

This "spreads replicas of the same partition across different racks", extending failure tolerance beyond individual broker loss.

### Checking Consumer Position

```bash
$ bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --describe --group my-group

TOPIC    PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG    CONSUMER-ID  HOST         CLIENT-ID
my-topic 0          2               4               2      consumer-1   /127.0.0.1   consumer-1
```

### Managing Consumer Groups

```bash
$ bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --list
test-consumer-group

$ bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --describe \
    --group my-group --members

$ bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --delete \
    --group my-group --group my-other-group

$ bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --reset-offsets \
    --group my-group --topic topic1 --to-latest
```

Reset scenarios include `--to-datetime`, `--to-earliest`, `--shift-by`, `--from-file`, `--by-duration`.

### Managing Share Groups

```bash
$ bin/kafka-share-groups.sh --bootstrap-server localhost:9092 --list
my-share-group

$ bin/kafka-share-groups.sh --bootstrap-server localhost:9092 --describe --group my-share-group

$ bin/kafka-share-groups.sh --bootstrap-server localhost:9092 --reset-offsets \
    --group my-share-group --topic topic1 --to-latest --execute
```

### Expanding Your Cluster

`topics-to-move.json`:

```json
{
  "topics": [
    { "topic": "foo1" },
    { "topic": "foo2" }
  ],
  "version": 1
}
```

Generate a reassignment plan:

```bash
$ bin/kafka-reassign-partitions.sh --bootstrap-server localhost:9092 \
    --topics-to-move-json-file topics-to-move.json --broker-list "5,6" --generate
```

Execute, then verify:

```bash
$ bin/kafka-reassign-partitions.sh --bootstrap-server localhost:9092 \
    --reassignment-json-file expand-cluster-reassignment.json --execute

$ bin/kafka-reassign-partitions.sh --bootstrap-server localhost:9092 \
    --reassignment-json-file expand-cluster-reassignment.json --verify
```

Custom partition assignment:

```json
{"version":1,"partitions":[{"topic":"foo1","partition":0,"replicas":[5,6]},
{"topic":"foo2","partition":1,"replicas":[2,3]}]}
```

### Decommissioning Brokers

```bash
$ bin/kafka-configs.sh --bootstrap-server localhost:9092 --alter \
    --add-config cordoned.log.dirs="*" --entity-type brokers --entity-name 1
```

Reassign partitions away, then unregister:

```bash
$ bin/kafka-cluster.sh unregister --bootstrap-server localhost:9092 --id 1
```

### Decommissioning Log Directories

```bash
$ bin/kafka-configs.sh --bootstrap-server localhost:9092 --alter \
    --add-config cordoned.log.dirs=/data/dir1 --entity-type brokers --entity-name 1
```

After reassigning and stopping the broker, uncordon:

```bash
$ bin/kafka-configs.sh --bootstrap-controller localhost:9093 --alter \
    --delete-config cordoned.log.dirs --entity-type brokers --entity-name 1
```

### Increasing Replication Factor

`increase-replication-factor.json`:

```json
{"version":1,
 "partitions":[{"topic":"foo","partition":0,"replicas":[5,6,7]}]}
```

```bash
$ bin/kafka-reassign-partitions.sh --bootstrap-server localhost:9092 \
    --reassignment-json-file increase-replication-factor.json --execute
```

### Limiting Bandwidth During Data Migration

```bash
$ bin/kafka-reassign-partitions.sh --bootstrap-server localhost:9092 --execute \
    --reassignment-json-file bigger-cluster.json --throttle 50000000 \
    --replica-alter-log-dirs-throttle 100000000
```

Alter the throttle mid-rebalance:

```bash
$ bin/kafka-reassign-partitions.sh --bootstrap-server localhost:9092 --additional \
    --execute --reassignment-json-file bigger-cluster.json --throttle 700000000
```

Throttle parameters include `leader.replication.throttled.rate`, `follower.replication.throttled.rate`, and per-topic throttled replica lists.

### Setting Quotas

```bash
$ bin/kafka-configs.sh --bootstrap-server localhost:9092 --alter \
    --add-config 'producer_byte_rate=1024,consumer_byte_rate=2048,request_percentage=200' \
    --entity-type users --entity-name user1 --entity-type clients --entity-name clientA

$ bin/kafka-configs.sh --bootstrap-server localhost:9092 --describe \
    --entity-type users --entity-name user1
```
