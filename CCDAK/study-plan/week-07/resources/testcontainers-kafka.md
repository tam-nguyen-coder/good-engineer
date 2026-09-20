# Testcontainers for Java — Kafka Module (`org.testcontainers.kafka.KafkaContainer`)

> **Nguồn (official):** https://java.testcontainers.org/modules/kafka/
> **Tuần:** 7 — Security & Testing · **Loại:** Testcontainers Docs (Java module `testcontainers-kafka`)
> ⚠️ Nội dung dưới đây được crawl tự động (qua curl + WebFetch, có rút gọn) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- Testcontainers tự **khởi tạo và quản lý container Kafka thật** trong test → integration test đúng hành vi broker (rebalance, transaction, `read_committed`, ACL/TLS/SASL), khác với mock (`MockProducer`/`MockConsumer`) chỉ test logic client.
- 2 class hiện hành (artifact **`org.testcontainers:testcontainers-kafka`**, version docs = **2.0.5**): **`org.testcontainers.kafka.KafkaContainer`** cho image **`apache/kafka`** và **`apache/kafka-native`** (GraalVM native, khởi động < 1 s); **`org.testcontainers.kafka.ConfluentKafkaContainer`** cho **`confluentinc/cp-kafka`** ≥ **7.4.0**. Class cũ `org.testcontainers.containers.KafkaContainer` **deprecated**.
- Lợi ích docs nêu: "single node Kafka installation with just one line of code" và **không cần ZooKeeper** (KRaft). `withKraft()` chỉ còn ý nghĩa với class deprecated (KRaft production-ready từ 3.3.1 / cp-kafka 7.3.x).
- Sau `start()`, lấy địa chỉ bằng **`kafka.getBootstrapServers()`** (dạng `PLAINTEXT://localhost:<random-port>` hoặc `localhost:<port>`) → gán vào `bootstrap.servers` của `KafkaProducer`/`KafkaConsumer`/`AdminClient` thật.
- Cần **listener bổ sung** khi client nằm trong **container khác cùng network** (kcat, app under test, Toxiproxy): `withListener("kafka:19092")` + `withNetwork(network)` — đúng bài `advertised.listeners` của Tuần 1.
- JUnit 5: dùng `@Testcontainers` + `@Container static KafkaContainer kafka = new KafkaContainer("apache/kafka:4.3.1")` (module `org.testcontainers:junit-jupiter`) để container **dùng chung cho cả class** (start 1 lần); Ryuk tự dọn container khi JVM thoát.
- Chi phí: ~giây khởi động (native < 1 s), cần Docker daemon trên CI runner; đổi lại **đúng version broker production** (khác `EmbeddedKafka` spring-kafka-test chạy trong JVM, lệch version).
- Có bản cho ngôn ngữ khác: Node **`@testcontainers/kafka`** (`new KafkaContainer('apache/kafka:4.3.1').start()` → `getBootstrapServers()`), Go, Python, .NET… → "broker thật trong test, mọi ngôn ngữ" = Testcontainers.
- Kết hợp thường gặp trong đề: Testcontainers Kafka + Schema Registry container (`confluentinc/cp-schema-registry`) hoặc `mock://` cho serde; test consumer lag bằng `AdminClient.listConsumerGroupOffsets` so với `endOffsets`.

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Kafka Module

Testcontainers can be used to automatically instantiate and manage Apache Kafka containers. Currently, two different Kafka images are supported:

- `org.testcontainers.kafka.ConfluentKafkaContainer` supports `confluentinc/cp-kafka`
- `org.testcontainers.kafka.KafkaContainer` supports `apache/kafka` and `apache/kafka-native`

> **Note:** `org.testcontainers.containers.KafkaContainer` is deprecated. Please use `org.testcontainers.kafka.ConfluentKafkaContainer` or `org.testcontainers.kafka.KafkaContainer` instead, depending on the used image.

### Benefits

- Running a single node Kafka installation with just one line of code
- No need to manage external Zookeeper installation, required by Kafka.

### Example

#### Using org.testcontainers.kafka.KafkaContainer

Create a `KafkaContainer` to use it in your tests:

```java
KafkaContainer kafka = new KafkaContainer("apache/kafka-native:3.8.0")
```

Now your tests or any other process running on your machine can get access to running Kafka broker by using the following bootstrap server location:

```java
kafka.getBootstrapServers()
```

#### Using org.testcontainers.kafka.ConfluentKafkaContainer

> **Note:** Compatible with `confluentinc/cp-kafka` images version 7.4.0 and later.

```java
ConfluentKafkaContainer kafka = new ConfluentKafkaContainer("confluentinc/cp-kafka:7.4.0")
```

### Options

#### Using Kraft mode

> **Note:** Only available for `org.testcontainers.containers.KafkaContainer`. KRaft mode was declared production ready in 3.3.1 (confluentinc/cp-kafka:7.3.x)

```java
KafkaContainer kafka = new KafkaContainer(DockerImageName.parse("confluentinc/cp-kafka:7.4.0")).withKraft()
```

See the versions interoperability matrix for more details.

#### Register listeners

There are scenarios where additional listeners are needed because the consumer/producer can be in another container in the same network or a different process where the port to connect differs from the default exposed port. E.g Toxiproxy.

Register additional listener:

```java
KafkaContainer kafka = new KafkaContainer("apache/kafka-native:3.8.0")
    .withListener("kafka:19092")
    .withNetwork(network);
```

Container defined in the same network:

```java
GenericContainer<?> kcat = new GenericContainer<>("confluentinc/cp-kcat:7.9.0")
    .withCreateContainerCmdModifier(cmd -> {
        cmd.withEntrypoint("sh");
    })
    .withCopyToContainer(Transferable.of("Message produced by kcat"), "/data/msgs.txt")
    .withNetwork(network)
    .withCommand("-c", "tail -f /dev/null")
```

Client using the new registered listener:

```java
kcat.execInContainer("kcat", "-b", "kafka:19092", "-t", "msgs", "-P", "-l", "/data/msgs.txt");
String stdout = kcat
    .execInContainer("kcat", "-b", "kafka:19092", "-C", "-t", "msgs", "-c", "1")
    .getStdout();
```

### Adding this module to your project dependencies

Add the following dependency to your pom.xml/build.gradle file:

Gradle:

```groovy
testImplementation "org.testcontainers:testcontainers-kafka:2.0.5"
```

Maven:

```xml
<dependency>
    <groupId>org.testcontainers</groupId>
    <artifactId>testcontainers-kafka</artifactId>
    <version>2.0.5</version>
    <scope>test</scope>
</dependency>
```

### Ghi chú thêm (tổng hợp từ Testcontainers docs khác, không nằm trong trang trên)

- **Testcontainers 1.x vs 2.x:** artifact 1.x là `org.testcontainers:kafka:1.21.x` (class `org.testcontainers.kafka.KafkaContainer` đã có từ 1.20). Testcontainers **2.0** đổi tên artifact thành `testcontainers-kafka` và yêu cầu Java 17+; class name giữ nguyên. Lab tuần này dùng `org.testcontainers:kafka:1.21.3` + `org.testcontainers:junit-jupiter:1.21.3` (ổn định với Gradle không cần BOM) — đổi sang `testcontainers-kafka:2.0.5` nếu muốn theo docs mới nhất.
- **JUnit 5 lifecycle:**

```java
@Testcontainers
class OrdersIntegrationTest {
    @Container
    static KafkaContainer kafka = new KafkaContainer("apache/kafka:4.3.1");   // static = share cho mọi test method

    @Test
    void producesAndConsumes() {
        Properties p = new Properties();
        p.put("bootstrap.servers", kafka.getBootstrapServers());
        // ... KafkaProducer / KafkaConsumer thật
    }
}
```

- **Node.js:** `npm i -D @testcontainers/kafka testcontainers`; `const kafka = await new KafkaContainer('apache/kafka:4.3.1').start(); const brokers = [kafka.getBootstrapServers()];` → `new Kafka({ brokers })` (kafkajs); `await kafka.stop()` trong `afterAll`.
- **Cấu hình broker trong container:** `withEnv("KAFKA_AUTO_CREATE_TOPICS_ENABLE", "false")`, `withEnv("KAFKA_TRANSACTION_STATE_LOG_MIN_ISR", "1")` (đã mặc định 1 cho single node) — mọi biến `KAFKA_*` như compose Tuần 1.
- **Vị trí trong test pyramid:** unit (`MockProducer`/`MockConsumer`, `TopologyTestDriver`) → **integration (Testcontainers / EmbeddedKafka)** → contract test schema (Schema Registry `/compatibility`) → e2e/chaos trên staging.
