# Dynamic config: 5 mức ưu tiên, update mode và cách đọc synonyms

> **Nguồn (official):** https://docs.confluent.io/platform/current/kafka/dynamic-config.html · đối chiếu https://kafka.apache.org/43/configuration/broker-configs/ (mục *Updating Broker Configs*) · https://cwiki.apache.org/confluence/display/KAFKA/KIP-226+-+Dynamic+Broker+Configuration
> **Tuần:** 2 — Cluster Config I · **Loại:** Confluent Docs + Apache Kafka Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch). Trang Confluent liệt kê **3 mức** cho riêng broker config; **5 mức đầy đủ** (gồm 2 mức topic/default) đến từ `DynamicBrokerConfig` trong mã nguồn Kafka và mục *Updating Broker Configs* của docs Apache — phần đó **không crawl được nguyên văn, tổng hợp từ docs**. Luôn kiểm bằng `--describe --all` trên cluster thật.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- **Thứ tự ưu tiên đầy đủ, từ mạnh đến yếu** — thuộc lòng đúng thứ tự này:
  1. **`DYNAMIC_TOPIC_CONFIG`** — override đặt trên chính topic (`--entity-type topics --entity-name <topic>`).
  2. **`DYNAMIC_BROKER_CONFIG`** — dynamic **cho một broker cụ thể** (`--entity-type brokers --entity-name <id>`).
  3. **`DYNAMIC_DEFAULT_BROKER_CONFIG`** — dynamic **cluster-wide default** (`--entity-type brokers --entity-default`).
  4. **`STATIC_BROKER_CONFIG`** — giá trị trong `server.properties` lúc broker khởi động.
  5. **`DEFAULT_CONFIG`** — mặc định dựng sẵn trong Kafka.
- Hệ quả vận hành quan trọng nhất: **đặt cluster-wide default không đè được override đã có trên topic**. Sửa `min.insync.replicas` hay `retention.ms` ở mức broker rồi tưởng đã xong là sai — phải kiểm từng topic.
- **3 update mode** quyết định có cần restart hay không:
  - `read-only` — "Requires a broker restart for update".
  - `per-broker` — "May be updated dynamically for each broker".
  - `cluster-wide` — "May be updated dynamically as a cluster-wide default. May also be updated as a per-broker value for testing".
- `kafka-configs.sh --describe --all` in **mọi** config đang hiệu lực kèm `sensitive=` và **`synonyms={...}`**. Đọc synonyms từ trái sang phải: **phần tử đầu tiên là nguồn đang thắng**, các phần tử sau là những nơi cùng định nghĩa config đó nhưng bị che. Đây là cách duy nhất trả lời chắc chắn câu "giá trị này đến từ đâu".
- `--entity-type` nhận **`topics` · `brokers` · `users` · `clients` · `groups` · `ips`**; `--entity-default` = "áp cho tất cả entity chưa có override riêng" (dùng được với `brokers`, `users`, `clients`, `ips`).
- Trong Kafka 4.x (KRaft-only) các override này nằm trong **metadata log**, **không còn znode ZooKeeper**. Mọi câu trả lời nhắc `/config/brokers/<id>` trong ZooKeeper hay cờ `--zookeeper` đều là kiến thức của Kafka ≤ 3.x.
- Gỡ override bằng `--delete-config` **không đưa về mặc định in trong docs** — nó đưa về mức ưu tiên kế tiếp còn tồn tại.

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Configuration Precedence Order (Confluent docs — phần broker)

> When a broker configuration is defined at multiple levels, this hierarchy applies:
>
> 1. "Dynamic per-broker configuration"
> 2. "Dynamic cluster-wide default configuration"
> 3. "Static broker configuration from the `broker.properties` file"

### Update Modes (Confluent docs, nguyên văn)

- **read-only**: "Requires a broker restart for update"
- **per-broker**: "May be updated dynamically for each broker"
- **cluster-wide**: "May be updated dynamically as a cluster-wide default. May also be updated as a per-broker value for testing"

### `kafka-configs` command examples (nguyên văn)

**Alter per-broker setting:**

```
bin/kafka-configs --bootstrap-server localhost:9092 --entity-type brokers \
--entity-name 0 --alter --add-config log.cleaner.threads=2
```

**Describe per-broker settings:**

```
bin/kafka-configs --bootstrap-server localhost:9092 --entity-type brokers \
--entity-name 0 --describe
```

**Delete configuration override:**

```
bin/kafka-configs --bootstrap-server localhost:9092 --entity-type brokers \
--entity-name 0 --alter --delete-config log.cleaner.threads
```

**Cluster-wide default configuration:**

```
bin/kafka-configs --bootstrap-server localhost:9092 --entity-type brokers \
--entity-default --alter --add-config log.cleaner.threads=2
```

**Describe cluster defaults:**

```
bin/kafka-configs --bootstrap-server localhost:9092 --entity-type brokers \
--entity-default --describe
```

### Topic-level (Apache Kafka — *Basic Kafka Operations → Modifying topics*)

```
$ bin/kafka-configs.sh --bootstrap-server localhost:9092 --entity-type topics \
  --entity-name my_topic_name --alter --add-config x=y

$ bin/kafka-configs.sh --bootstrap-server localhost:9092 --entity-type topics \
  --entity-name my_topic_name --alter --delete-config x
```

### Đọc output `--describe --all` (dạng thực tế trên cluster 4.3)

Lệnh:

```
bin/kafka-configs.sh --bootstrap-server kafka-1:19092 --describe --all \
  --entity-type topics --entity-name orders
```

Mỗi dòng có dạng:

```
  retention.ms=60000 sensitive=false synonyms={DYNAMIC_TOPIC_CONFIG:retention.ms=60000, STATIC_BROKER_CONFIG:log.retention.ms=604800000, DEFAULT_CONFIG:log.retention.hours=168}
```

Cách đọc: giá trị hiệu lực là **60000**, đến từ **`DYNAMIC_TOPIC_CONFIG`** (phần tử đầu tiên). Hai phần tử sau chỉ cho biết *nếu gỡ override topic thì sẽ rơi xuống đâu*. Trên broker:

```
bin/kafka-configs.sh --bootstrap-server kafka-1:19092 --describe --all \
  --entity-type brokers --entity-name 2
```

sẽ in ra các synonym theo thứ tự `DYNAMIC_BROKER_CONFIG` → `DYNAMIC_DEFAULT_BROKER_CONFIG` → `STATIC_BROKER_CONFIG` → `DEFAULT_CONFIG`.

### Các nhóm config được nêu riêng trong mục *Updating Broker Configs* của docs Apache

Trang `/43/configuration/broker-configs/` có các tiểu mục hướng dẫn cập nhật động:

- Updating Password Configs Dynamically
- Updating SSL Keystore of an Existing Listener
- Updating SSL Truststore of an Existing Listener
- **Updating Default Topic Configuration**
- **Updating Log Cleaner Configs**
- **Updating Thread Configs**
- Updating ConnectionQuota Configs
- Adding and Removing Listeners

> 📌 Hai tiểu mục in đậm là phần trực tiếp của Tuần 2: **Updating Log Cleaner Configs** (`log.cleaner.threads`, `log.cleaner.dedupe.buffer.size`, `log.cleaner.io.buffer.size`, `log.cleaner.io.max.bytes.per.second`, `log.cleaner.backoff.ms`) và **Updating Thread Configs** (`num.network.threads`, `num.io.threads`, `num.replica.fetchers`, `num.recovery.threads.per.data.dir`, `background.threads`) — tất cả đều `cluster-wide`, đổi nóng được.
