# Apache Kafka — Share Groups (Queues for Kafka, KIP-932): Design, Configs & Tools

> **Nguồn (official):** https://kafka.apache.org/43/design/design/#share-groups (Design → *The Share Consumer*) · https://kafka.apache.org/43/operations/basic-kafka-operations/#managing-share-groups · https://kafka.apache.org/43/generated/group_config.html · https://kafka.apache.org/43/generated/kafka_config.html (`group.share.*`) · Javadoc `KafkaShareConsumer` 4.3
> **Tuần:** 2 — Độ tin cậy & lưu trữ · **Loại:** Apache Kafka Docs (4.3) · *(KIP gốc: https://cwiki.apache.org/confluence/display/KAFKA/KIP-932%3A+Queues+for+Kafka — cwiki không crawl được lúc viết, nội dung lấy từ docs 4.3 đã GA)*
> ⚠️ Nội dung dưới đây được crawl tự động (curl + chuyển HTML → Markdown, rút gọn) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- **Share group** = loại group **thứ hai** tồn tại **song song** consumer group, cho workload kiểu **queue** truyền thống. Lộ trình KIP-932: early access **4.0** → preview **4.1** → **GA 4.2**. Consumer trong share group gọi là **share consumer** (`KafkaShareConsumer`), API "quen mà khác".
- **4 khác biệt cốt lõi so với consumer group:** (1) consumer **cùng chia sẻ 1 partition** (partition có thể gán cho **nhiều** consumer); (2) số consumer **được vượt** số partition; (3) **acknowledge từng record** (vẫn tối ưu theo batch); (4) **đếm số lần giao** (delivery count) → tự xử lý record "độc" (poison). Đổi lại: **mất thứ tự** (docs: "at the expense of record ordering").
- **Acquisition lock:** record fetch về được **khoá theo thời gian** cho consumer đó; hết hạn → tự **release** cho consumer khác. Mặc định **30 s** — group config **`share.record.lock.duration.ms`** (broker default `group.share.record.lock.duration.ms` = 30 000; min 15 000, max 60 000). ⚠️ Tên khái niệm là *acquisition lock* nhưng tên config là `share.record.lock.duration.ms`.
- **5 cách xử lý record đang giữ lock:** **ACCEPT** (xử lý xong, không giao lại) · **RELEASE** (lỗi tạm, giao lại) · **REJECT** (không xử lý được, **không giao lại nữa**) · **renew** (gia hạn lock vì còn đang xử lý, `share.renew.acknowledge.enable=true`) · **không làm gì** (hết lock → tự release).
- **Delivery count limit:** group config `share.delivery.count.limit` = **5** (min 2, broker cap `group.share.max.delivery.count.limit` = 10). Vượt → record bị **archive** (không giao nữa) — tương đương DLQ ngầm.
- **Giới hạn lock đồng thời:** `share.partition.max.record.locks` = **2000** record/share-partition (min 100, max 4000). Đầy → fetch **tạm trả rỗng** cho tới khi lock hết hạn.
- **Ack mode client:** `share.acknowledgement.mode` = **`implicit`** (mặc định — `poll()`/`commitSync()`/`commitAsync()` kế tiếp tự ACCEPT cả batch trước) | **`explicit`** (phải `acknowledge(record, AcknowledgeType)` từng record **trước** `poll()` kế, thiếu → `IllegalStateException`).
- **Group configs khác:** `share.auto.offset.reset` = **`latest`** (earliest / latest / `by_duration:PnDTnHnMn.nS`); `share.isolation.level` = **`read_uncommitted`**; `share.session.timeout.ms` **45 000**; `share.heartbeat.interval.ms` **5 000**. Broker: `group.share.max.size` **200** member/group; `group.share.max.share.sessions` 2000/broker; assignor server-side `group.share.assignors=simple`.
- **State lưu ở đâu:** **share coordinator** ghi vào topic nội bộ **`__share_group_state`** (`share.coordinator.state.topic.num.partitions` **50**, RF **3**, min.isr **2**) — khác consumer group dùng `__consumer_offsets`.
- **Tools:** `kafka-console-share-consumer.sh --bootstrap-server … --topic t --group g` (nhiều instance cùng group chia nhau **1** partition); `kafka-share-groups.sh --list | --describe --group g [--members | --state | --offsets] | --reset-offsets --to-earliest/--to-latest/--to-datetime --execute | --delete-offsets | --delete`. Output `--describe` có cột **START-OFFSET** (offset sớm nhất của record in-flight) và **LAG**.
- **Bật tính năng:** feature flag **`share.version`** — kiểm tra `kafka-features.sh describe`; bật bằng `kafka-features.sh upgrade --feature share.version=1` (4.1+). Client Node.js: `kafkajs` **không** hỗ trợ share group; `@confluentinc/kafka-javascript` có.

---

## 📄 Nội dung (trích từ tài liệu gốc)

### The Share Consumer (Design)

Most consumption of data from Kafka is performed by consumers in consumer groups. The way that consumer groups assign partitions to members of the group gives a powerful combination of ordering and scalability. However, some traditional messaging workloads are not a good fit for consumer groups.

Share groups are another type of group, existing alongside traditional consumer groups. They offer an alternative to consumer groups, particularly when applications require finer-grained sharing of partitions and records. Share groups enable consumers to cooperatively consume and process records from topics. The consumers in a share group are called share consumers, and they use a familiar but different programming interface.

The fundamental differences between a share group and a consumer group are:

- The consumers in a share group cooperatively consume records, and partitions may be assigned to multiple consumers.
- The number of consumers in a share group can exceed the number of partitions in a topic.
- Records are acknowledged individually, though the system is optimized for batch processing to improve efficiency.
- Delivery attempts to consumers in a share group are counted, which enables automated handling of unprocessable records.

All share consumers in the same share group subscribed to the same topic will cooperatively consume the records of that topic. If a topic is accessed by consumers in multiple share groups, each share group consumes from that topic independently of the others.

Each share consumer can dynamically set its list of subscribed topics. In practice, all consumers in a share group typically subscribe to the same topic or topics.

When a share consumer fetches records, it receives available records from any of the topic-partitions matching its subscriptions. Records are acquired for delivery to this share consumer with a time-limited acquisition lock. While a record is acquired, it is unavailable to other consumers in the same share group for the duration of the lock.

By default, the lock duration is 30 seconds, but you can control it using the group configuration parameter `share.record.lock.duration.ms`. The lock is released automatically once its duration elapses, making the record available to another delivery attempt. A share consumer holding the lock can handle the record in the following ways:

- Acknowledge successful processing of the record.
- Release the record, making it available for another delivery attempt.
- Reject the record, indicating it's unprocessable and preventing further delivery attempts for that record.
- Renew the record, extending the delivery attempt because the record is still being processed.
- Do nothing, in which case the lock is automatically released when its duration elapses.

The Kafka cluster limits the number of records for each topic-partition acquired by share consumers in each share group. Once this limit is reached, fetching operations will temporarily yield no further records until the number of acquired records decreases (as locks naturally time out). This limit is controlled by the broker configuration property `group.share.partition.max.record.locks`. By limiting the duration of the acquisition lock and automatically releasing the locks, the broker ensures delivery progresses even in the presence of consumer failures.

### KafkaShareConsumer (Javadoc 4.3, summarized)

Unlike consumer groups where each partition is assigned to a single consumer, share groups allow multiple consumers to consume from the same partitions. This provides more flexible sharing of records than a consumer group, at the expense of record ordering. All consumers with the same `group.id` belong to the same share group, and the group automatically rebalances when members join, leave, or fail.

Acknowledgement types:

| `AcknowledgeType` | Meaning |
|---|---|
| `ACCEPT` | The record was processed successfully; it will not be re-delivered. |
| `RELEASE` | Processing failed transiently; the record remains eligible for another delivery attempt. |
| `REJECT` | The record is unprocessable (semantic error); it is not eligible for further delivery attempts. |

Acknowledgement modes (`share.acknowledgement.mode`):

- **`implicit`** (default): the consumer acknowledges the records of the previous batch by calling `poll()`, `commitSync()` or `commitAsync()` — all records are treated as `ACCEPT`.
- **`explicit`**: the consumer must call `acknowledge(record, AcknowledgeType)` for every record before the next `poll()`; otherwise `IllegalStateException` is thrown.

```java
// explicit acknowledgement
Properties props = new Properties();
props.setProperty("bootstrap.servers", "localhost:9092");
props.setProperty("group.id", "test");
props.setProperty("key.deserializer", "org.apache.kafka.common.serialization.StringDeserializer");
props.setProperty("value.deserializer", "org.apache.kafka.common.serialization.StringDeserializer");
props.setProperty("share.acknowledgement.mode", "explicit");

KafkaShareConsumer<String, String> consumer = new KafkaShareConsumer<>(props);
consumer.subscribe(Arrays.asList("foo"));
while (true) {
    ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(1000));
    for (ConsumerRecord<String, String> record : records) {
        try {
            doProcessing(record);
            consumer.acknowledge(record, AcknowledgeType.ACCEPT);
        } catch (Exception e) {
            consumer.acknowledge(record, AcknowledgeType.REJECT);
        }
    }
    consumer.commitSync();
}
```

Key methods: `subscribe(Collection)`, `poll(Duration)`, `acknowledge(ConsumerRecord, AcknowledgeType)`, `commitSync()` / `commitAsync()`, `acquisitionLockTimeoutMs()`, `wakeup()`, `close()`. `share.isolation.level` = `read_uncommitted` (all records) | `read_committed` (only committed transactional records).

### Group configs for share groups (`group_config.html`, Kafka 4.3)

| Group config | Default | Valid values | Description |
|---|---|---|---|
| `share.record.lock.duration.ms` | 30000 (30 seconds) | [1000,...] | The record acquisition lock duration in milliseconds for share groups. |
| `share.delivery.count.limit` | 5 | [2,...] | The maximum number of delivery attempts for a record delivered to a share group. |
| `share.partition.max.record.locks` | 2000 | [100,...] | Share-group record lock limit per share-partition. |
| `share.auto.offset.reset` | latest | [latest, earliest, by_duration:PnDTnHnMn.nS] | The strategy to initialize the share-partition start offset. |
| `share.isolation.level` | read_uncommitted | [read_committed, read_uncommitted] | Controls how to read records written transactionally. |
| `share.renew.acknowledge.enable` | true | | Whether the renew acknowledge type is enabled for the share group. |
| `share.session.timeout.ms` | 45000 (45 seconds) | [1,...] | The timeout to detect client failures when using the share group protocol. |
| `share.heartbeat.interval.ms` | 5000 (5 seconds) | [1,...] | The heartbeat interval given to the members of a share group. |
| `share.assignment.interval.ms` | 1000 (1 second) | [0,...] | The interval between assignment updates for a share group. |

### Broker configs (`kafka_config.html`, Kafka 4.3)

| Broker config | Default | Description |
|---|---|---|
| `group.share.record.lock.duration.ms` | 30000 (30 seconds) | The record acquisition lock duration in milliseconds for share groups. |
| `group.share.min.record.lock.duration.ms` / `group.share.max.record.lock.duration.ms` | 15000 / 60000 | Bounds for the group configuration of record acquisition lock duration. |
| `group.share.delivery.count.limit` | 5 | The maximum number of delivery attempts for a record delivered to a share group. |
| `group.share.min.delivery.count.limit` / `group.share.max.delivery.count.limit` | 2 / 10 | Bounds for the group configuration of the delivery count limit. |
| `group.share.partition.max.record.locks` | 2000 | Share-group record lock limit per share-partition. |
| `group.share.min.partition.max.record.locks` / `group.share.max.partition.max.record.locks` | 100 / 4000 | Bounds for the record lock limit per share-partition. |
| `group.share.max.size` | 200 | The maximum number of members that a single share group can accommodate. |
| `group.share.max.share.sessions` | 2000 | The maximum number of share sessions per broker. |
| `group.share.session.timeout.ms` | 45000 (45 seconds) | The timeout to detect client failures when using the share group protocol. |
| `group.share.heartbeat.interval.ms` | 5000 (5 seconds) | The heartbeat interval given to the members of a share group. |
| `group.share.assignors` | simple | The server-side assignors (a single assignor). |
| `share.coordinator.state.topic.num.partitions` | 50 | The number of partitions for the share-group state topic (`__share_group_state`). |
| `share.coordinator.state.topic.replication.factor` | 3 | Replication factor for the share-group state topic. Topic creation will fail until the cluster size meets this replication factor requirement. |
| `share.coordinator.state.topic.min.isr` | 2 | Overridden min.insync.replicas for the share-group state topic. |
| `share.coordinator.state.topic.segment.bytes` | 104857600 (100 mebibytes) | The log segment size for the share-group state topic. |
| `share.coordinator.snapshot.update.records.per.snapshot` | 500 | The number of update records the share coordinator writes between snapshot records. |

### Managing share groups (Operations)

Use the ShareGroupCommand tool to list, describe, or delete the share groups. Only share groups without any active members can be deleted. For example, to list all share groups in a cluster:

```
$ bin/kafka-share-groups.sh --bootstrap-server localhost:9092 --list
my-share-group
```

To view the current start offset and lag, use the `--describe` option:

```
$ bin/kafka-share-groups.sh --bootstrap-server localhost:9092 --describe --group my-share-group
GROUP           TOPIC   PARTITION  START-OFFSET  LAG
my-share-group  topic1  0          4             0
```

The start offset is the earliest offset for in-flight records being evaluated for delivery to share consumers. Some records after the start offset may already have completed delivery. NOTE: The admin client needs DESCRIBE access to all the topics used in the group. There are many `--describe` options that provide more detailed information about a share group:

- `--members`: Describes active members in the share group.

```
$ bin/kafka-share-groups.sh --bootstrap-server localhost:9092 --describe --group my-share-group --members
GROUP           CONSUMER-ID             HOST        CLIENT-ID               #PARTITIONS  ASSIGNMENT
my-share-group  94wrSQNmRda9Q6sk6jMO6Q  /127.0.0.1  console-share-consumer  1            topic1:0
my-share-group  EfI0sha8QSKSrL_-I_zaTA  /127.0.0.1  console-share-consumer  1            topic1:0
```

You can see that both members have been assigned the same partition which they are sharing.

- `--offsets`: The default describe option. This provides the same output as the `--describe` option.
- `--state`: Describes a summary of the state of the share group.

```
$ bin/kafka-share-groups.sh --bootstrap-server localhost:9092 --describe --group my-share-group --state
GROUP           COORDINATOR (ID)     STATE   #MEMBERS
my-share-group  localhost:9092 (1)   Stable  2
```

To reset the offsets of a share group, use the `--reset-offsets` option. It has 2 execution options: `--dry-run` (display which offsets to reset) and `--execute`. Scenarios: `--to-datetime <YYYY-MM-DDThh:mm:ss.sss>`, `--to-earliest`, `--to-latest`.

```
$ bin/kafka-share-groups.sh --bootstrap-server localhost:9092 --reset-offsets --group my-share-group --topic topic1 --to-latest --execute
GROUP           TOPIC   PARTITION  NEW-OFFSET
my-share-group  topic1  0          10
```

To delete the offsets of individual topics in the share group, use `--delete-offsets --group my-share-group --topic topic1`. To delete one or more share groups, use `--delete --group my-share-group`.

### Share Consumer API

The Share Consumer API enables applications in a share group to cooperatively consume and process data from Kafka topics. To use the share consumer, add the Maven dependency `org.apache.kafka:kafka-clients:4.3.1`. Examples of using the share consumer are shown in the javadocs.
