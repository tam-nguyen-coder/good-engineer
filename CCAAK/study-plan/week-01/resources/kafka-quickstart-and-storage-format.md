# Apache Kafka — Quickstart & `kafka-storage.sh`: vòng đời một node từ đĩa trắng tới "Kafka Server started"

> **Nguồn (official):** https://kafka.apache.org/43/getting-started/quickstart/ · https://kafka.apache.org/43/operations/kraft/
> **Tuần:** 1 — Nền tảng vận hành + `KRaft` in production · **Loại:** Apache Kafka Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- **Java 17+ là yêu cầu để chạy Kafka 4.x** ("Your local environment must have Java 17+ installed"). Ghi nhớ cặp số của Kafka 4.0: **Java 17** cho broker / Connect / tools, **Java 11** cho client Java; **baseline giao thức client là 2.1** (client cũ hơn 2.1 không nói chuyện được với broker 4.x).
- **Ba lệnh dựng một node KRaft**, đúng thứ tự — đề dạng *list order* rất hay hỏi:
  1. `kafka-storage.sh random-uuid` → sinh `cluster.id`
  2. `kafka-storage.sh format --standalone -t $KAFKA_CLUSTER_ID -c config/server.properties`
  3. `kafka-server-start.sh config/server.properties`
- **Bước 2 là bắt buộc, không bỏ được.** Khác hẳn thời ZooKeeper (broker tự đăng ký khi start). Chưa format mà start → broker chết ngay với lỗi log dir chưa được format.
- **`cluster.id` phải giống nhau trên mọi node** của cùng cluster. Sinh **một lần**, rồi truyền cho tất cả. Đây là nguồn gốc của `InconsistentClusterIdException` — lỗi #1 khi dựng cluster bằng tay hoặc bằng script tự động hoá.
- `format` ghi file **`meta.properties`** vào từng thư mục trong `log.dirs` (và vào `metadata.log.dir` nếu có), chứa `cluster.id`, `node.id`, `directory.id` (UUID ngẫu nhiên, dùng cho KIP-853), `version`.
- Image Docker chính thức: **`apache/kafka:4.3.1`** (JVM) và **`apache/kafka-native:4.3.1`** (GraalVM native, start nhanh hơn nhiều). Image tự chạy `kafka-storage.sh format` giúp bạn khi biến môi trường `CLUSTER_ID` được đặt — **đó là vì sao lab Docker không thấy bước format**, nhưng đề thi thì có.
- Dọn dẹp một node = xoá thư mục log (`rm -rf /tmp/kafka-logs /tmp/kraft-combined-logs`). Xoá xong là **mất luôn `meta.properties`** → lần start sau phải format lại. Trên production, xoá nhầm log dir của controller = mất một voter của quorum.
- Topic tạo bằng `kafka-topics.sh --create --topic <t> --bootstrap-server localhost:9092`; kiểm tra bằng `--describe`. **Không có `--zookeeper`** ở bất kỳ đâu trong quickstart 4.x.

---

## 📄 Nội dung (trích từ tài liệu gốc)

### System requirements

"Your local environment must have Java 17+ installed."

### Step 1: Get Kafka

Download and extract the latest release (4.3.1) to access the Kafka binaries and configuration files.

### Step 2: Start the Kafka environment

Three commands initialize a standalone Kafka environment in KRaft mode:

```bash
# Generate a Cluster UUID
KAFKA_CLUSTER_ID="$(bin/kafka-storage.sh random-uuid)"

# Format log directories
bin/kafka-storage.sh format --standalone -t $KAFKA_CLUSTER_ID -c config/server.properties

# Start the Kafka server
bin/kafka-server-start.sh config/server.properties
```

#### Docker alternative

```bash
docker run -p 9092:9092 apache/kafka:4.3.1
```

A native GraalVM variant also exists:

```bash
docker run -p 9092:9092 apache/kafka-native:4.3.1
```

### Step 3: Create a topic to store your events

```bash
bin/kafka-topics.sh --create --topic quickstart-events --bootstrap-server localhost:9092
bin/kafka-topics.sh --describe --topic quickstart-events --bootstrap-server localhost:9092
```

### Step 4 & 5: Write and read events

Use `kafka-console-producer.sh` to write messages line by line, and `kafka-console-consumer.sh --from-beginning` in another terminal session to read them.

### Step 6 & 7: Kafka Connect and Kafka Streams

Configure connectors in `config/connect-standalone.properties` and run source/sink connectors for file integration. Process events with the Kafka Streams library using operations such as `flatMapValues`, `groupBy` and `count`.

### Step 8: Terminate the Kafka environment

Stop all clients and servers, then remove local data:

```bash
rm -rf /tmp/kafka-logs /tmp/kraft-combined-logs
```

---

### 📌 Chi tiết `kafka-storage.sh` cần cho vận hành (từ trang Operations → KRaft)

```bash
# 1) sinh cluster id — CHỈ MỘT LẦN cho cả cluster
bin/kafka-storage.sh random-uuid
# → q1Sh-9_ISia_zwGINzRvyQ

# 2a) controller ĐẦU TIÊN, tự nó là voter duy nhất
bin/kafka-storage.sh format --cluster-id <ID> --standalone --config config/controller.properties

# 2b) format cả quorum cùng lúc, khai đủ id@host:port:directoryUUID
bin/kafka-storage.sh format --cluster-id <ID> \
  --initial-controllers "0@controller-0:9093:<uuid0>,1@controller-1:9093:<uuid1>,2@controller-2:9093:<uuid2>" \
  --config config/controller.properties

# 2c) broker, và controller GIA NHẬP SAU
bin/kafka-storage.sh format --cluster-id <ID> --config config/server.properties --no-initial-controllers
```

Nội dung `meta.properties` sinh ra (ví dụ, trên một broker):

```properties
#
#Sat Sep 20 09:14:22 UTC 2026
directory.id=Zq4rYpXvSk6LmN1oPqRsTu
node.id=2
version=1
cluster.id=q1Sh-9_ISia_zwGINzRvyQ
```

> 🧠 Đọc file này là **bước chẩn đoán đầu tiên** khi một broker không join được cluster: so `cluster.id` trong `meta.properties` với `ClusterId` mà `kafka-metadata-quorum.sh describe --status` in ra. Khác nhau → `InconsistentClusterIdException`.
