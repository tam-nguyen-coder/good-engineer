# Apache Kafka 4.3 — Basic Kafka Operations: sửa topic, cordon log dir, graceful shutdown

> **Nguồn (official):** https://kafka.apache.org/43/operations/basic-kafka-operations/
> **Tuần:** 2 — Cluster Config I · **Loại:** Apache Kafka Docs (operations)
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có rút gọn — chỉ giữ phần liên quan Tuần 2) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- Sửa config topic **không dùng `kafka-topics.sh --alter --config`** nữa (đã bỏ từ lâu) mà dùng **`kafka-configs.sh --entity-type topics --alter --add-config/--delete-config`**. `kafka-topics.sh --alter` giờ chỉ còn để **tăng partition**.
- **Không giảm được số partition:** "Kafka does not currently support reducing the number of partitions for a topic." Đây là câu hỏi lặp lại — mọi phương án "giảm partition từ 12 xuống 6" đều sai.
- **Cordon (KIP-1066)** là cách chuẩn để rút một ổ đĩa hoặc một broker khỏi vòng phân bổ mà **không làm gián đoạn partition đang chạy trên đó**: `cordoned.log.dirs=/data/dir1` cordon một thư mục, `cordoned.log.dirs="*"` cordon cả broker.
- Cordon xong mới **unregister** broker: `kafka-cluster.sh unregister --id <id>`. Làm ngược thứ tự thì broker vẫn nhận partition mới trong lúc bạn đang rút nó ra.
- Khi broker **đã tắt**, vẫn gỡ cordon được bằng cách nói chuyện thẳng với controller: `--bootstrap-controller localhost:9093`. Nhớ cặp `--bootstrap-server` (broker) vs `--bootstrap-controller` (controller) — KRaft mới có cái thứ hai.
- **Graceful shutdown** dựa vào `controlled.shutdown.enable=true` (mặc định): broker "sync all its logs to disk" và "migrate any partitions the server is the leader for to other replicas" trước khi tắt. `kill -9` bỏ qua cả hai → khởi động lại phải **log recovery** (đây là lúc `num.recovery.threads.per.data.dir` = 2 quyết định mất bao lâu).
- Sau bảo trì, trả leader về đúng chỗ bằng `kafka-leader-election.sh --election-type preferred --all-topic-partitions`.

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Modifying topics

To add configurations to a topic:

```
$ bin/kafka-configs.sh --bootstrap-server localhost:9092 --entity-type topics \
  --entity-name my_topic_name --alter --add-config x=y
```

To remove a configuration:

```
$ bin/kafka-configs.sh --bootstrap-server localhost:9092 --entity-type topics \
  --entity-name my_topic_name --alter --delete-config x
```

> "Kafka does not currently support reducing the number of partitions for a topic."

Adding partitions (lệnh còn lại của `kafka-topics.sh --alter`):

```
$ bin/kafka-topics.sh --bootstrap-server localhost:9092 --alter \
  --topic my_topic_name --partitions 40
```

### Decommissioning: cordoning brokers và log directories

**Cordoning a broker** (cordon toàn bộ log dir của broker 1):

```
$ bin/kafka-configs.sh --bootstrap-server localhost:9092 --alter \
  --add-config cordoned.log.dirs="*" --entity-type brokers --entity-name 1
```

**Cordoning a log directory** (chỉ một thư mục):

```
$ bin/kafka-configs.sh --bootstrap-server localhost:9092 --alter \
  --add-config cordoned.log.dirs=/data/dir1 --entity-type brokers --entity-name 1
```

**Unregistering a broker** (sau khi đã chuyển hết replica đi):

```
$ bin/kafka-cluster.sh unregister --bootstrap-server localhost:9092 --id 1
```

**Uncordoning khi broker đang offline** (đi thẳng vào controller):

```
$ bin/kafka-configs.sh --bootstrap-controller localhost:9093 --alter \
  --delete-config cordoned.log.dirs --entity-type brokers --entity-name 1
```

### Graceful shutdown

Enable controlled shutdown via `controlled.shutdown.enable=true`.

Khi bật, broker sẽ:

- "sync all its logs to disk" — tránh phải log recovery lúc khởi động lại;
- "migrate any partitions the server is the leader for to other replicas" — việc chuyển leader diễn ra **trước** khi tắt, nên downtime của từng partition chỉ còn vài mili giây.

### Balancing leadership

```
$ bin/kafka-leader-election.sh --bootstrap-server localhost:9092 \
  --election-type preferred --all-topic-partitions
```

> 📌 Broker cũng tự làm việc này khi `auto.leader.rebalance.enable=true` (mặc định) mỗi `leader.imbalance.check.interval.seconds` = 300 s. Chạy tay khi cần trả leader về ngay sau rolling restart thay vì chờ 5 phút.
