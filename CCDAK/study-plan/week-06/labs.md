# 🧪 Hands-on Labs — Tuần 6: Kafka Streams

> Lab cầm tay chỉ việc, chạy hoàn toàn local bằng Docker (không tốn phí). LUÔN chạy phần Dọn dẹp cuối mỗi lab (trừ khi lab sau nói "giữ").
> ⚙️ Yêu cầu chung: Docker Desktop, **Java 17+**, **Gradle 8.x**, cluster 3 node từ Tuần 1 (Lab 1.2), Node.js 24 (chỉ cho 1 script producer có timestamp). Tổng ~3.5h.
> Về [plan tuần](README.md) · [Câu hỏi luyện tập](questions.md) · [Kế hoạch tổng](../../CCDAK-STUDY-PLAN.md)

---

## 🔧 Chuẩn bị chung (làm 1 lần, dùng cho mọi lab)

### ⚠️ Vì sao tuần này bắt buộc Java (và Option cho người không muốn Java)

`Kafka Streams` là **library JVM** (`org.apache.kafka:kafka-streams`) — không có bản Node.js/Python chính thức, không có REST API, không chạy trong broker. Muốn *nhìn thấy* task, repartition topic, changelog, `suppress`, `TopologyTestDriver`… thì phải viết Java (hoặc Kotlin/Scala). Đề CCDAK hỏi Streams theo **tên API/config Java** nên đây cũng là cách ôn đúng nhất. Code tuần này ngắn (mỗi app 40–80 dòng), không cần biết Java sâu.

- **Option A (khuyến nghị):** Java 17 + Gradle — Lab 6.1 → 6.6.
- **Option B (không Java):** `ksqlDB` container — Lab 6.7 (SQL, thấy được STREAM/TABLE, push/pull query, internal topic). Làm 6.7 thay 6.1 và đọc code Java của các lab còn lại để hiểu.

### 1) Khởi động cluster 3 broker (dùng lại `docker-compose.cluster.yml` của Tuần 1)

```bash
cd ~/kafka-labs
docker compose -f docker-compose.cluster.yml up -d
export KAFKA_CTR=kafka-1 KAFKA_BS=kafka-1:19092        # alias kt/kcp/kcc/kcg trỏ vào cluster 3 node
kt --list                                              # cluster sống
```

> 2 file compose chuẩn được định nghĩa ở [Tuần 1 — Lab 1.1 / 1.2](../week-01/labs.md). Tuần này cần **3 broker** vì Lab 6.4 dùng `exactly_once_v2` (`transaction.state.log.replication.factor=3`, `min.isr=2` mặc định) và internal topic của Streams tạo với `replication.factor=3`.

### 2) Cài Java 17 + Gradle

```bash
# macOS (Homebrew)
brew install openjdk@17 gradle
sudo ln -sfn "$(brew --prefix openjdk@17)/libexec/openjdk.jdk" /Library/Java/JavaVirtualMachines/openjdk-17.jdk
# Linux/WSL2: dùng SDKMAN
#   curl -s "https://get.sdkman.io" | bash && source ~/.sdkman/bin/sdkman-init.sh
#   sdk install java 17.0.12-tem && sdk install gradle 8.10.2

java -version      # openjdk version "17.x" (21 cũng được)
gradle -v          # Gradle 8.x
```

### 3) Tạo project `~/kafka-labs/streams-lab/`

Cấu trúc thư mục (Gradle chuẩn, mọi lab dùng chung 1 project, mỗi lab 1 class `main`):

```
~/kafka-labs/streams-lab/
├── build.gradle.kts
├── settings.gradle.kts
├── gradlew, gradle/                      # sinh bởi `gradle wrapper`
└── src/
    ├── main/java/lab/
    │   ├── Common.java                   # props + shutdown hook dùng chung
    │   ├── WordCountApp.java             # Lab 6.1 + 6.5
    │   ├── WindowedApp.java              # Lab 6.2 + 6.5
    │   ├── JoinApp.java                  # Lab 6.3
    │   ├── EosApp.java                   # Lab 6.4
    │   └── PunctuatorApp.java            # Lab 6.6 + 6.5
    └── test/java/lab/
        ├── WordCountTopologyTest.java    # Lab 6.5
        ├── WindowedTopologyTest.java     # Lab 6.5
        └── PunctuatorTopologyTest.java   # Lab 6.5
```

```bash
mkdir -p ~/kafka-labs/streams-lab/src/main/java/lab ~/kafka-labs/streams-lab/src/test/java/lab
cd ~/kafka-labs/streams-lab
```

`settings.gradle.kts`:

```kotlin
rootProject.name = "streams-lab"
```

`build.gradle.kts` (in đầy đủ — copy nguyên văn):

```kotlin
// ~/kafka-labs/streams-lab/build.gradle.kts
plugins {
    java
    application
}

group = "lab"
version = "1.0"

repositories {
    mavenCentral()
}

java {
    toolchain {
        languageVersion.set(JavaLanguageVersion.of(17))   // Kafka 4.x clients/Streams cần Java 11+, chọn 17 cho đồng nhất với broker
    }
}

dependencies {
    implementation("org.apache.kafka:kafka-streams:4.3.1")            // kéo theo kafka-clients 4.3.1 + RocksDB
    implementation("org.slf4j:slf4j-simple:2.0.16")                   // log ra stderr, đủ cho lab

    testImplementation("org.apache.kafka:kafka-streams-test-utils:4.3.1")   // TopologyTestDriver, TestInputTopic, MockProcessorContext
    testImplementation(platform("org.junit:junit-bom:5.11.4"))
    testImplementation("org.junit.jupiter:junit-jupiter")
    testRuntimeOnly("org.junit.platform:junit-platform-launcher")
}

application {
    // chạy app khác nhau bằng: ./gradlew run -PmainClass=lab.WindowedApp
    mainClass.set(providers.gradleProperty("mainClass").getOrElse("lab.WordCountApp"))
    applicationDefaultJvmArgs = listOf(
        "-Dorg.slf4j.simpleLogger.defaultLogLevel=info",
        "-Dorg.slf4j.simpleLogger.log.org.apache.kafka.clients=warn",     // bớt ồn từ consumer/producer nội bộ
        "-Dorg.slf4j.simpleLogger.log.org.apache.kafka.common=warn"
    )
}

tasks.test {
    useJUnitPlatform()
    testLogging {
        events("passed", "skipped", "failed")
        showStandardStreams = true
    }
}
```

`src/main/java/lab/Common.java` (dùng chung cho mọi app):

```java
// ~/kafka-labs/streams-lab/src/main/java/lab/Common.java
package lab;

import org.apache.kafka.common.serialization.Serdes;
import org.apache.kafka.streams.KafkaStreams;
import org.apache.kafka.streams.StreamsConfig;

import java.time.Duration;
import java.util.Properties;
import java.util.concurrent.CountDownLatch;

public final class Common {
    private Common() {}

    /** Từ host: bootstrap qua listener PLAINTEXT_HOST của 3 broker (Tuần 1). */
    public static final String BOOTSTRAP =
            System.getenv().getOrDefault("BOOTSTRAP", "localhost:9092,localhost:9094,localhost:9096");

    public static Properties props(String applicationId) {
        Properties p = new Properties();
        p.put(StreamsConfig.APPLICATION_ID_CONFIG, applicationId);           // = consumer group.id + prefix internal topics + thư mục state
        p.put(StreamsConfig.BOOTSTRAP_SERVERS_CONFIG, BOOTSTRAP);
        p.put(StreamsConfig.DEFAULT_KEY_SERDE_CLASS_CONFIG, Serdes.String().getClass());
        p.put(StreamsConfig.DEFAULT_VALUE_SERDE_CLASS_CONFIG, Serdes.String().getClass());
        p.put(StreamsConfig.REPLICATION_FACTOR_CONFIG, 3);                    // internal topics RF=3 (cluster 3 broker)
        // 2 instance trên CÙNG máy phải dùng state.dir khác nhau (RocksDB lock) → STATE_DIR=/tmp/kafka-streams-lab-2
        p.put(StreamsConfig.STATE_DIR_CONFIG, System.getenv().getOrDefault("STATE_DIR", "/tmp/kafka-streams-lab"));
        if (System.getenv("COMMIT_MS") != null) {                             // mặc định 30000 (ALOS) / 100 (EOS)
            p.put(StreamsConfig.COMMIT_INTERVAL_MS_CONFIG, Integer.parseInt(System.getenv("COMMIT_MS")));
        }
        if ("0".equals(System.getenv("CACHE"))) {                             // mặc định 10 MB; 0 = thấy mọi update trung gian
            p.put(StreamsConfig.STATESTORE_CACHE_MAX_BYTES_CONFIG, 0L);
        }
        if (System.getenv("THREADS") != null) {                               // mặc định 1
            p.put(StreamsConfig.NUM_STREAM_THREADS_CONFIG, Integer.parseInt(System.getenv("THREADS")));
        }
        return p;
    }

    /** start + log state transitions + shutdown hook; block tới khi Ctrl+C. */
    public static void run(KafkaStreams streams) {
        CountDownLatch latch = new CountDownLatch(1);
        streams.setStateListener((newState, oldState) ->
                System.out.printf("[state] %s -> %s%n", oldState, newState));      // CREATED → REBALANCING → RUNNING ...
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            streams.close(Duration.ofSeconds(10));
            latch.countDown();
        }));
        streams.start();
        try {
            latch.await();
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
}
```

Sinh wrapper và build lần đầu (tải dependency ~1–2 phút):

```bash
cd ~/kafka-labs/streams-lab
gradle wrapper --gradle-version 8.10.2
./gradlew build -x test          # chưa có test; build phải BUILD SUCCESSFUL sau khi thêm code Lab 6.1
```

### 4) Script producer có timestamp (Node.js, dùng ở Lab 6.2)

```bash
cd ~/kafka-labs && cat > ts-producer.mjs <<'EOF'
// ~/kafka-labs/ts-producer.mjs — gửi 1 record với EVENT TIMESTAMP tự chọn (để thử window/grace/late record)
// Dùng: node ts-producer.mjs <topic> <key> <value> <offsetSecondsFromBase>
import { Kafka, logLevel } from "kafkajs";
const [topic, key, value, offsetSec] = process.argv.slice(2);
const BASE = Number(process.env.BASE_MS ?? Date.UTC(2026, 0, 1, 0, 0, 0));   // 2026-01-01T00:00:00Z
const timestamp = String(BASE + Number(offsetSec ?? 0) * 1000);
const kafka = new Kafka({ clientId: "ts-producer", brokers: ["localhost:9092", "localhost:9094", "localhost:9096"], logLevel: logLevel.ERROR });
const producer = kafka.producer();
await producer.connect();
const [m] = await producer.send({ topic, messages: [{ key, value, timestamp }] });
console.log(`sent ${key}=${value} ts=${new Date(Number(timestamp)).toISOString()} -> p${m.partition} off=${m.baseOffset}`);
await producer.disconnect();
EOF
```

---

## Lab 6.1 — WordCount: topology, 2 instance chia task, repartition & changelog ⭐

**🎯 Mục tiêu:** Viết topology `flatMapValues → groupBy → count → toStream → to`, chạy **2 instance** cùng `application.id` để thấy Kafka chia **task** giữa chúng, và nhìn thấy 2 internal topic `-repartition` / `-changelog` bằng `kt --list`.
**🧩 Luyện kỹ năng (liên quan đề):**

- `StreamsBuilder`, `KStream`, `KGroupedStream`, `KTable`, `Materialized.as`, `Grouped.with`, `Topology.describe()`.
- Task = số partition input; instance thứ 2 → rebalance; `application.id` = `group.id` (thấy bằng `kcg --describe`).
- `groupBy` đổi key → repartition topic; `count` → state store + changelog compacted.

**⏱️ ~35 phút** · **Yêu cầu trước:** Chuẩn bị chung xong, cluster 3 node đang chạy.

### Các bước

1. Tạo topic input **3 partition** và output.

   ```bash
   kt --create --topic words-input --partitions 3 --replication-factor 3
   kt --create --topic words-output --partitions 3 --replication-factor 3
   ```
2. Tạo `src/main/java/lab/WordCountApp.java`.

   ```java
   // ~/kafka-labs/streams-lab/src/main/java/lab/WordCountApp.java — Lab 6.1
   package lab;

   import org.apache.kafka.common.serialization.Serdes;
   import org.apache.kafka.common.utils.Bytes;
   import org.apache.kafka.streams.KafkaStreams;
   import org.apache.kafka.streams.StreamsBuilder;
   import org.apache.kafka.streams.Topology;
   import org.apache.kafka.streams.kstream.Consumed;
   import org.apache.kafka.streams.kstream.Grouped;
   import org.apache.kafka.streams.kstream.KStream;
   import org.apache.kafka.streams.kstream.KTable;
   import org.apache.kafka.streams.kstream.Materialized;
   import org.apache.kafka.streams.kstream.Produced;
   import org.apache.kafka.streams.state.KeyValueStore;

   import java.util.Arrays;
   import java.util.Locale;

   public class WordCountApp {
       public static final String INPUT = "words-input";
       public static final String OUTPUT = "words-output";

       /** Tách topology ra để Lab 6.5 test bằng TopologyTestDriver. */
       public static Topology buildTopology() {
           StreamsBuilder builder = new StreamsBuilder();

           KStream<String, String> lines = builder.stream(INPUT, Consumed.with(Serdes.String(), Serdes.String()));

           KTable<String, Long> counts = lines
                   // stateless, KHÔNG đổi key → không repartition
                   .flatMapValues(line -> Arrays.asList(line.toLowerCase(Locale.ROOT).split("\\W+")))
                   .filter((key, word) -> !word.isBlank())
                   // groupBy ĐỔI key (key mới = word) → đánh dấu repartition; vì count() là stateful → tạo topic
                   //   wordcount-app-words-repartition (tên lấy từ Grouped.with("words", ...))
                   .groupBy((key, word) -> word, Grouped.with("words", Serdes.String(), Serdes.String()))
                   // stateful → state store RocksDB "word-counts" + changelog wordcount-app-word-counts-changelog (compacted)
                   .count(Materialized.<String, Long, KeyValueStore<Bytes, byte[]>>as("word-counts")
                           .withKeySerde(Serdes.String())
                           .withValueSerde(Serdes.Long()));

           counts.toStream().to(OUTPUT, Produced.with(Serdes.String(), Serdes.Long()));
           return builder.build();
       }

       public static void main(String[] args) {
           Topology topology = buildTopology();
           System.out.println(topology.describe());   // 2 sub-topology, cắt tại repartition topic
           KafkaStreams streams = new KafkaStreams(topology, Common.props("wordcount-app"));
           Common.run(streams);
       }
   }
   ```
3. **Terminal 1:** chạy instance 1 (giữ chạy).

   ```bash
   cd ~/kafka-labs/streams-lab && COMMIT_MS=1000 ./gradlew run -PmainClass=lab.WordCountApp
   ```
   Đọc output `describe()`:
   ```
   Topologies:
      Sub-topology: 0
       Source: KSTREAM-SOURCE-0000000000 (topics: [words-input])
         --> KSTREAM-FLATMAPVALUES-0000000001
       ...
       Sink: words-repartition-sink (topic: words-repartition)
         <-- words-repartition-filter
     Sub-topology: 1
       Source: words-repartition-source (topics: [words-repartition])
         --> KSTREAM-AGGREGATE-0000000003
       Processor: KSTREAM-AGGREGATE-0000000003 (stores: [word-counts])
         --> KTABLE-TOSTREAM-0000000007
       ...
       Sink: KSTREAM-SINK-0000000008 (topic: words-output)
   ```
   Rồi thấy `[state] CREATED -> REBALANCING`, `[state] REBALANCING -> RUNNING`, và trong log Streams dòng kiểu `Assigned tasks ... 0_0, 0_1, 0_2, 1_0, 1_1, 1_2` (**6 task** = 3 partition × 2 sub-topology, tất cả về instance 1).
4. **Terminal 2:** xem internal topic + consumer group.

   ```bash
   export KAFKA_CTR=kafka-1 KAFKA_BS=kafka-1:19092
   kt --list | grep wordcount-app
   #   wordcount-app-word-counts-changelog
   #   wordcount-app-words-repartition
   kt --describe --topic wordcount-app-word-counts-changelog | head -1     # PartitionCount: 3, Configs: cleanup.policy=compact,...
   kt --describe --topic wordcount-app-words-repartition | head -1         # cleanup.policy=delete, retention.ms=-1 (Streams tự purge)
   kcg --describe --group wordcount-app                                    # group.id = application.id; 6 partition (3 input + 3 repartition)
   ```
5. **Terminal 2:** produce vài dòng text, rồi consume output (value là `Long` → phải chỉ deserializer).

   ```bash
   printf 'kafka streams is a library\nkafka is a log\nstreams scale with partitions\n' | \
     docker exec -i kafka-1 /opt/kafka/bin/kafka-console-producer.sh --bootstrap-server kafka-1:19092 --topic words-input

   kcc --topic words-output --from-beginning --property print.key=true \
     --value-deserializer org.apache.kafka.common.serialization.LongDeserializer --timeout-ms 8000
   ```
   Output mẫu (mỗi word 1 dòng với count hiện tại; `kafka 2`, `streams 2`, `is 2`, `a 2`…). Nếu produce lại cùng câu, count tăng tiếp (state được giữ trong RocksDB + changelog).
6. **Terminal 3:** chạy **instance 2** cùng `application.id`, **state.dir khác** (2 process cùng máy).

   ```bash
   cd ~/kafka-labs/streams-lab && STATE_DIR=/tmp/kafka-streams-lab-2 COMMIT_MS=1000 ./gradlew run -PmainClass=lab.WordCountApp
   ```
   Cả 2 terminal in `[state] RUNNING -> REBALANCING` rồi `REBALANCING -> RUNNING`; log `Assigned tasks` giờ chia đôi (ví dụ instance 1: `0_0, 0_2, 1_1`; instance 2: `0_1, 1_0, 1_2`). `kcg --describe --group wordcount-app` cho thấy 2 `CONSUMER-ID` khác nhau.
7. Chạy thử **instance 3 và 4** (`STATE_DIR=/tmp/kafka-streams-lab-3`, `-4`) → tổng 6 task chia cho 4 instance; **instance thứ 7** sẽ không có task (idle) — không cần chạy tới đó, chỉ cần hiểu.
8. Ctrl+C instance 2 → instance 1 nhận lại task; state của các task đó được **restore từ changelog** (log `Restoration took ... ms`).

### ✅ Kiểm chứng

- `kt --list` có đúng 2 internal topic: `wordcount-app-words-repartition` (đổi key + stateful) và `wordcount-app-word-counts-changelog` (`cleanup.policy=compact`), **cùng 3 partition** với input.
- `describe()` in **2 sub-topology**, cắt tại repartition topic; 6 task tổng cộng.
- 2 instance → mỗi instance giữ 1 phần task; `kcg --describe --group wordcount-app` thấy 2 member.
- Đổi `groupBy(...)` thành `selectKey((k, w) -> w).groupByKey(Grouped.with(...))` → **vẫn** có repartition (selectKey đổi key). Đổi thành `groupByKey()` không `selectKey` → count theo key gốc (null) và **không** có repartition topic — thử nếu còn thời gian.

### 🧹 Dọn dẹp

```bash
# Ctrl+C mọi instance trước (reset tool yêu cầu app đã dừng)
docker exec kafka-1 /opt/kafka/bin/kafka-streams-application-reset.sh --bootstrap-server kafka-1:19092 \
  --application-id wordcount-app --input-topics words-input      # xoá internal topics + reset offset input
rm -rf /tmp/kafka-streams-lab*/wordcount-app
kt --delete --topic words-input
kt --delete --topic words-output
# GIỮ cluster cho Lab 6.2
```

### 🧠 Ý nghĩa với đề thi

- **Scale Streams = thêm instance cùng `application.id`**; `application.id` chính là `group.id` (nhìn thấy bằng `kafka-consumer-groups.sh`). Số task cố định theo partition → instance thừa idle.
- `groupBy` / `selectKey` / `map` **đổi key** → topic `<app.id>-<name>-repartition` chỉ khi có stateful phía sau; `groupByKey` / `mapValues` / `flatMapValues` / `filter` không repartition.
- Mọi state store có changelog `<app.id>-<store>-changelog` **compacted**, cùng số partition với task; instance chết → task migrate + restore từ changelog.
- `Topology.describe()` là cách nhanh nhất để đếm sub-topology, task và thấy internal topic trước khi deploy.

---

## Lab 6.2 — Windowed aggregation: tumbling 1 phút + grace + `suppress` vs không suppress

**🎯 Mục tiêu:** Đếm page view mỗi user theo **tumbling window 1 phút, grace 10 s**; chạy 2 biến thể **không `suppress`** (thấy nhiều update trung gian) và **có `suppress(untilWindowCloses)`** (đúng 1 kết quả cuối/window); gửi record **late** để thấy bị drop.
**🧩 Luyện kỹ năng (liên quan đề):**

- `TimeWindows.ofSizeAndGrace`, `Windowed<K>`, `Suppressed.untilWindowCloses(BufferConfig.unbounded())`.
- **Stream time** chỉ tiến khi có record mới → suppress "kẹt" nếu không có dữ liệu.
- `statestore.cache.max.bytes=0` để thấy từng update; late record sau `end + grace` → drop.

**⏱️ ~30 phút** · **Yêu cầu trước:** Lab 6.1 (project build được), `ts-producer.mjs`.

### Các bước

1. Tạo topic.

   ```bash
   kt --create --topic page-views --partitions 3 --replication-factor 3
   kt --create --topic views-per-minute --partitions 3 --replication-factor 3
   ```
2. Tạo `src/main/java/lab/WindowedApp.java`.

   ```java
   // ~/kafka-labs/streams-lab/src/main/java/lab/WindowedApp.java — Lab 6.2
   package lab;

   import org.apache.kafka.common.serialization.Serdes;
   import org.apache.kafka.common.utils.Bytes;
   import org.apache.kafka.streams.KafkaStreams;
   import org.apache.kafka.streams.StreamsBuilder;
   import org.apache.kafka.streams.Topology;
   import org.apache.kafka.streams.kstream.Consumed;
   import org.apache.kafka.streams.kstream.Grouped;
   import org.apache.kafka.streams.kstream.KTable;
   import org.apache.kafka.streams.kstream.Materialized;
   import org.apache.kafka.streams.kstream.Produced;
   import org.apache.kafka.streams.kstream.Suppressed;
   import org.apache.kafka.streams.kstream.Suppressed.BufferConfig;
   import org.apache.kafka.streams.kstream.TimeWindows;
   import org.apache.kafka.streams.kstream.Windowed;
   import org.apache.kafka.streams.state.WindowStore;

   import java.time.Duration;

   public class WindowedApp {
       public static final String INPUT = "page-views";
       public static final String OUTPUT = "views-per-minute";
       public static final Duration WINDOW = Duration.ofMinutes(1);
       public static final Duration GRACE = Duration.ofSeconds(10);

       public static Topology buildTopology(boolean suppress) {
           StreamsBuilder builder = new StreamsBuilder();

           KTable<Windowed<String>, Long> perMinute = builder
                   .stream(INPUT, Consumed.with(Serdes.String(), Serdes.String()))   // key = user, value = page; timestamp = event-time
                   .groupByKey(Grouped.with(Serdes.String(), Serdes.String()))        // key giữ nguyên → không repartition
                   .windowedBy(TimeWindows.ofSizeAndGrace(WINDOW, GRACE))             // tumbling: size = advance; record muộn > end+grace bị drop
                   .count(Materialized.<String, Long, WindowStore<Bytes, byte[]>>as("views-window-store")
                           .withKeySerde(Serdes.String())
                           .withValueSerde(Serdes.Long()));

           if (suppress) {
               // chỉ emit 1 kết quả CUỐI mỗi window, sau khi stream time > end + grace
               perMinute = perMinute.suppress(Suppressed.untilWindowCloses(BufferConfig.unbounded()));
           }

           perMinute
                   .toStream((windowedKey, count) ->
                           windowedKey.key() + "@" + windowedKey.window().startTime())   // Windowed<K> → String key "alice@2026-01-01T00:00:00Z"
                   .to(OUTPUT, Produced.with(Serdes.String(), Serdes.Long()));

           return builder.build();
       }

       public static void main(String[] args) {
           boolean suppress = "true".equalsIgnoreCase(System.getenv().getOrDefault("SUPPRESS", "false"));
           String appId = suppress ? "views-app-suppress" : "views-app-plain";
           System.out.println("suppress=" + suppress + " application.id=" + appId);
           KafkaStreams streams = new KafkaStreams(buildTopology(suppress), Common.props(appId));
           Common.run(streams);
       }
   }
   ```
3. **Terminal 1:** chạy bản **không suppress**, tắt cache để thấy mọi update.

   ```bash
   cd ~/kafka-labs/streams-lab && CACHE=0 COMMIT_MS=1000 ./gradlew run -PmainClass=lab.WindowedApp
   ```
4. **Terminal 2:** consumer đọc output.

   ```bash
   kcc --topic views-per-minute --property print.key=true \
     --value-deserializer org.apache.kafka.common.serialization.LongDeserializer
   ```
5. **Terminal 3:** gửi 3 view của `alice` trong window đầu (00:00–01:00), timestamp 5 s, 20 s, 40 s.

   ```bash
   cd ~/kafka-labs
   node ts-producer.mjs page-views alice /home 5
   node ts-producer.mjs page-views alice /cart 20
   node ts-producer.mjs page-views alice /pay  40
   ```
   **Terminal 2** in **3 dòng**: `alice@2026-01-01T00:00:00Z 1`, `... 2`, `... 3` — mỗi record 1 update (vì cache = 0). Tắt `CACHE=0` (dùng mặc định 10 MB) và lặp lại → chỉ thấy vài dòng, thường chỉ `3` sau `commit.interval.ms`.
6. Ctrl+C terminal 1, chạy bản **có suppress** (app id khác nên đọc lại từ đầu topic — `auto.offset.reset=earliest` là mặc định Streams).

   ```bash
   cd ~/kafka-labs/streams-lab && SUPPRESS=true COMMIT_MS=1000 ./gradlew run -PmainClass=lab.WindowedApp
   ```
   **Terminal 2:** **không có dòng mới** dù app đã đọc 3 record — window `[00:00, 01:00)` chưa đóng vì stream time = 00:00:40 < 01:00 + 10 s grace.
7. Đẩy stream time qua `end + grace`: gửi 1 record ở giây **71**.

   ```bash
   node ts-producer.mjs page-views bob /home 71
   ```
   **Terminal 2:** xuất hiện **đúng 1 dòng** `alice@2026-01-01T00:00:00Z 3` (kết quả cuối). Record của `bob` thuộc window `[01:00, 02:00)` — chưa đóng nên chưa có gì.
8. Gửi record **late** cho window đầu (timestamp 50 s, nhưng stream time đã là 71 s > 70 s).

   ```bash
   node ts-producer.mjs page-views alice /late 50
   ```
   **Terminal 2:** không có gì (bản suppress); bản không suppress cũng **không** tăng lên 4 — record bị **drop** vì đến sau `end + grace`. Log app có thể có dòng `Skipping record for expired window` (mức WARN, phụ thuộc version). Đổi `GRACE` thành 30 s và lặp lại từ bước 6 → record 50 s **được tính** (4).

### ✅ Kiểm chứng

- Không suppress + cache 0: 3 record → 3 update (`1, 2, 3`). Có suppress: 0 dòng cho tới khi có record timestamp > 70 s, rồi đúng **1** dòng `3`.
- Record timestamp 50 s gửi sau khi stream time = 71 s → không thay đổi kết quả (late, drop).
- `kt --list | grep views-app-suppress` có thêm `...-KTABLE-SUPPRESS-STATE-STORE-...-changelog` (buffer của suppress cũng là state store) và `views-app-suppress-views-window-store-changelog` với `cleanup.policy=compact,delete`.

### 🧹 Dọn dẹp

```bash
# Ctrl+C app + consumer
for id in views-app-plain views-app-suppress; do
  docker exec kafka-1 /opt/kafka/bin/kafka-streams-application-reset.sh --bootstrap-server kafka-1:19092 --application-id $id --input-topics page-views
done
rm -rf /tmp/kafka-streams-lab*/views-app-*
kt --delete --topic page-views
kt --delete --topic views-per-minute
```

### 🧠 Ý nghĩa với đề thi

- **Tumbling** = `TimeWindows.ofSizeAndGrace(size, grace)` không `advanceBy`; thêm `.advanceBy(1 phút)` → **hopping**. API cũ `TimeWindows.of()` (grace 24 h ngầm) đã bị xoá ở 4.0.
- "Chỉ muốn 1 kết quả cuối mỗi window" → `suppress(untilWindowCloses(unbounded()))`; cần **grace** và **stream time tiến** (không có record mới → kết quả kẹt).
- "Sao `count()` không emit mỗi record" → **record cache 10 MB** + `commit.interval.ms`; đặt 0 để thấy hết, kết quả cuối không đổi.
- Late record (> `end + grace`) bị **drop im lặng**; muốn nhận → tăng **grace**, không phải tăng window.
- Key kết quả windowed là **`Windowed<K>`** → phải map sang key phẳng trước khi `to()`.

---

## Lab 6.3 — Join: `KStream` ⋈ `KTable` (co-partition) + `KStream` ⋈ `GlobalKTable` (không co-partition) ⭐

**🎯 Mục tiêu:** Enrich luồng `orders` (key = `customerId`) với bảng `customers` (`KTable`, cùng key, cùng 3 partition) rồi với bảng `products` (`GlobalKTable`, key khác = `productId`, **1 partition**) qua `KeyValueMapper`; cố tình tạo bảng customers **6 partition** để thấy `TopologyException` co-partition.
**🧩 Luyện kỹ năng (liên quan đề):**

- `builder.table` / `builder.globalTable` + `Materialized`, `Joined.with`, `ValueJoiner`, `KeyValueMapper`.
- Stream-table join: **chỉ record bên stream trigger**; table update chỉ đổi state.
- Co-partitioning check lúc start; `GlobalKTable` bỏ qua check, cho phép join theo foreign key.

**⏱️ ~40 phút** · **Yêu cầu trước:** Lab 6.1.

### Các bước

1. Tạo topic. `customers`/`products` compacted (bảng); `customers-bad` 6 partition để thử lỗi.

   ```bash
   kt --create --topic orders --partitions 3 --replication-factor 3
   kt --create --topic customers --partitions 3 --replication-factor 3 --config cleanup.policy=compact
   kt --create --topic products  --partitions 1 --replication-factor 3 --config cleanup.policy=compact
   kt --create --topic orders-enriched --partitions 3 --replication-factor 3
   kt --create --topic customers-bad --partitions 6 --replication-factor 3 --config cleanup.policy=compact
   ```
2. Tạo `src/main/java/lab/JoinApp.java`. Value dùng chuỗi phân cách `|` để không cần thư viện JSON: order = `orderId|productId|qty`.

   ```java
   // ~/kafka-labs/streams-lab/src/main/java/lab/JoinApp.java — Lab 6.3
   package lab;

   import org.apache.kafka.common.serialization.Serdes;
   import org.apache.kafka.common.utils.Bytes;
   import org.apache.kafka.streams.KafkaStreams;
   import org.apache.kafka.streams.StreamsBuilder;
   import org.apache.kafka.streams.Topology;
   import org.apache.kafka.streams.kstream.Consumed;
   import org.apache.kafka.streams.kstream.GlobalKTable;
   import org.apache.kafka.streams.kstream.Joined;
   import org.apache.kafka.streams.kstream.KStream;
   import org.apache.kafka.streams.kstream.KTable;
   import org.apache.kafka.streams.kstream.KeyValueMapper;
   import org.apache.kafka.streams.kstream.Materialized;
   import org.apache.kafka.streams.kstream.Produced;
   import org.apache.kafka.streams.kstream.ValueJoiner;
   import org.apache.kafka.streams.state.KeyValueStore;

   public class JoinApp {
       public static final String ORDERS = "orders";                 // key = customerId, value = orderId|productId|qty
       public static final String CUSTOMERS = System.getenv().getOrDefault("CUSTOMERS_TOPIC", "customers"); // key = customerId, value = name
       public static final String PRODUCTS = "products";             // key = productId, value = name
       public static final String OUTPUT = "orders-enriched";

       public static Topology buildTopology() {
           StreamsBuilder builder = new StreamsBuilder();

           KStream<String, String> orders = builder.stream(ORDERS, Consumed.with(Serdes.String(), Serdes.String()));

           // KTable: mỗi instance chỉ giữ partition của task mình → PHẢI co-partition với orders (cùng 3 partition, cùng key customerId)
           KTable<String, String> customers = builder.table(CUSTOMERS,
                   Consumed.with(Serdes.String(), Serdes.String()),
                   Materialized.<String, String, KeyValueStore<Bytes, byte[]>>as("customers-store"));

           // GlobalKTable: mỗi instance giữ TOÀN BỘ topic (1 partition cũng được) → không cần co-partition, join theo key bất kỳ
           GlobalKTable<String, String> products = builder.globalTable(PRODUCTS,
                   Consumed.with(Serdes.String(), Serdes.String()),
                   Materialized.<String, String, KeyValueStore<Bytes, byte[]>>as("products-store"));

           // 1) KStream-KTable inner join: chỉ record bên orders trigger; order của customer chưa có trong bảng → bị bỏ (dùng leftJoin nếu muốn giữ)
           ValueJoiner<String, String, String> withCustomer = (order, customerName) -> order + "|customer=" + customerName;
           KStream<String, String> ordersWithCustomer = orders.join(customers, withCustomer,
                   Joined.with(Serdes.String(), Serdes.String(), Serdes.String()));

           // 2) KStream-GlobalKTable join: KeyValueMapper lấy productId (field thứ 2 của value) làm key lookup
           KeyValueMapper<String, String, String> productIdFromOrder = (customerId, value) -> value.split("\\|")[1];
           ValueJoiner<String, String, String> withProduct = (value, productName) -> value + "|product=" + productName;
           KStream<String, String> enriched = ordersWithCustomer.join(products, productIdFromOrder, withProduct);

           enriched.to(OUTPUT, Produced.with(Serdes.String(), Serdes.String()));
           return builder.build();
       }

       public static void main(String[] args) {
           Topology topology = buildTopology();
           System.out.println(topology.describe());
           KafkaStreams streams = new KafkaStreams(topology, Common.props("join-app"));
           Common.run(streams);
       }
   }
   ```
3. Nạp **bảng trước** (customers, products) bằng console producer có key.

   ```bash
   printf 'c1:Alice\nc2:Bob\nc3:Carol\n' | docker exec -i kafka-1 /opt/kafka/bin/kafka-console-producer.sh \
     --bootstrap-server kafka-1:19092 --topic customers --property parse.key=true --property key.separator=:
   printf 'p1:Keyboard\np2:Monitor\np3:Mouse\n' | docker exec -i kafka-1 /opt/kafka/bin/kafka-console-producer.sh \
     --bootstrap-server kafka-1:19092 --topic products --property parse.key=true --property key.separator=:
   ```
4. **Terminal 1:** chạy app. `describe()` cho thấy `GlobalStore` riêng cho `products-store` và **không** có repartition topic.

   ```bash
   cd ~/kafka-labs/streams-lab && COMMIT_MS=1000 ./gradlew run -PmainClass=lab.JoinApp
   ```
5. **Terminal 2:** consumer output; **Terminal 3:** produce orders (key = customerId).

   ```bash
   kcc --topic orders-enriched --property print.key=true
   ```
   ```bash
   printf 'c1:o100|p1|2\nc2:o101|p3|1\nc9:o102|p2|5\nc3:o103|p9|1\n' | docker exec -i kafka-1 /opt/kafka/bin/kafka-console-producer.sh \
     --bootstrap-server kafka-1:19092 --topic orders --property parse.key=true --property key.separator=:
   ```
   **Terminal 2** in 2 dòng:
   ```
   c1   o100|p1|2|customer=Alice|product=Keyboard
   c2   o101|p3|1|customer=Bob|product=Mouse
   ```
   `o102` (customer `c9` không có) bị inner join bỏ; `o103` (product `p9` không có) bị GlobalKTable inner join bỏ.
6. Update bảng **không sinh output**: đổi tên `c1` rồi xem.

   ```bash
   printf 'c1:Alice Nguyen\n' | docker exec -i kafka-1 /opt/kafka/bin/kafka-console-producer.sh \
     --bootstrap-server kafka-1:19092 --topic customers --property parse.key=true --property key.separator=:
   # Terminal 2: KHÔNG có dòng mới (table update chỉ đổi state)
   printf 'c1:o104|p2|1\n' | docker exec -i kafka-1 /opt/kafka/bin/kafka-console-producer.sh \
     --bootstrap-server kafka-1:19092 --topic orders --property parse.key=true --property key.separator=:
   # Terminal 2: c1  o104|p2|1|customer=Alice Nguyen|product=Monitor  ← order mới trigger, thấy tên mới
   ```
7. Thí nghiệm **co-partition sai**: Ctrl+C app, chạy lại với bảng 6 partition.

   ```bash
   CUSTOMERS_TOPIC=customers-bad ./gradlew run -PmainClass=lab.JoinApp
   ```
   App **fail ngay lúc start**:
   ```
   org.apache.kafka.streams.errors.TopologyException: Invalid topology: stream-thread [...] Topics not co-partitioned: [orders, customers-bad]
   ```
   (`orders` 3 partition ≠ `customers-bad` 6). Sửa bằng `orders.repartition(Repartitioned.numberOfPartitions(6))` trước join, hoặc tạo topic cùng số partition. Lưu ý `products` 1 partition ≠ 3 **không** gây lỗi vì là `GlobalKTable`.
8. (Tuỳ chọn) Đổi `orders.join(customers, ...)` thành `orders.leftJoin(customers, ...)` → `o102` ra với `customer=null`.

### ✅ Kiểm chứng

- Chỉ order có **cả** customer và product khớp mới ra ở `orders-enriched` (inner join 2 tầng).
- Update `customers` **không** sinh record output; order mới sau đó thấy giá trị mới.
- `customers-bad` (6 partition) → `TopologyException ... not co-partitioned`; `products` (1 partition) qua `GlobalKTable` → không lỗi.
- `kt --list | grep join-app` chỉ có `join-app-customers-store-changelog` — `GlobalKTable` **không** có changelog (restore thẳng từ `products`), và không có repartition topic.

### 🧹 Dọn dẹp

```bash
# Ctrl+C app + consumer
docker exec kafka-1 /opt/kafka/bin/kafka-streams-application-reset.sh --bootstrap-server kafka-1:19092 \
  --application-id join-app --input-topics orders,customers,products
rm -rf /tmp/kafka-streams-lab*/join-app
for t in orders customers products orders-enriched customers-bad; do kt --delete --topic $t; done
```

### 🧠 Ý nghĩa với đề thi

- **Join matrix:** KStream-KTable **không window, cần co-partition, chỉ stream trigger**; KStream-GlobalKTable **không co-partition, `KeyValueMapper` chọn key bất kỳ**; KStream-KStream **bắt buộc `JoinWindows`**.
- Co-partition = **cùng số partition + cùng partitioner**; Streams chỉ kiểm tra được **số partition** (`TopologyException`) — partitioner lệch là lỗi âm thầm.
- "Enrich bằng bảng tham chiếu nhỏ, key khác" → `GlobalKTable`; "bảng lớn cùng key" → `KTable`.
- `GlobalKTable` không có changelog riêng, bootstrap đầy đủ trước khi xử lý, tốn RAM/disk mỗi instance.

---

## Lab 6.4 — `exactly_once_v2` vs `at_least_once`: `kill -9` giữa chừng, đếm duplicate

**🎯 Mục tiêu:** Chạy cùng 1 topology với 2 `processing.guarantee`, `kill -9` app khi đang xử lý, restart, rồi **đếm duplicate** ở output topic bằng `kcc --isolation-level read_committed`. Thấy ALOS sinh duplicate, EOS v2 không.
**🧩 Luyện kỹ năng (liên quan đề):**

- `StreamsConfig.PROCESSING_GUARANTEE_CONFIG` = `EXACTLY_ONCE_V2`; default `commit.interval.ms` 30 000 → 100.
- EOS = output + changelog + offset commit trong 1 transaction; consumer `read_committed` không thấy record của transaction bị abort.
- Yêu cầu broker: `transaction.state.log.replication.factor=3`/`min.isr=2` → cluster 3 broker.

**⏱️ ~35 phút** · **Yêu cầu trước:** Lab 6.1; cluster 3 broker (không dùng single node).

### Các bước

1. Tạo topic + nạp **300 record** có số thứ tự (value = `msg-N`).

   ```bash
   kt --create --topic eos-input --partitions 3 --replication-factor 3
   kt --create --topic eos-output --partitions 3 --replication-factor 3
   docker exec kafka-1 bash -c 'for i in $(seq 1 300); do echo "k$((i % 3)):msg-$i"; done | \
     /opt/kafka/bin/kafka-console-producer.sh --bootstrap-server kafka-1:19092 --topic eos-input \
     --property parse.key=true --property key.separator=:'
   ```
2. Tạo `src/main/java/lab/EosApp.java` — xử lý **chậm** (200 ms/record ≈ 5 record/s) để kịp `kill -9` giữa chừng.

   ```java
   // ~/kafka-labs/streams-lab/src/main/java/lab/EosApp.java — Lab 6.4
   package lab;

   import org.apache.kafka.common.serialization.Serdes;
   import org.apache.kafka.streams.KafkaStreams;
   import org.apache.kafka.streams.StreamsBuilder;
   import org.apache.kafka.streams.StreamsConfig;
   import org.apache.kafka.streams.kstream.Consumed;
   import org.apache.kafka.streams.kstream.Produced;

   import java.util.Properties;

   public class EosApp {
       public static void main(String[] args) {
           boolean eos = "true".equalsIgnoreCase(System.getenv().getOrDefault("EOS", "false"));
           String appId = eos ? "eos-app-v2" : "eos-app-alos";

           Properties props = Common.props(appId);
           props.put(StreamsConfig.PROCESSING_GUARANTEE_CONFIG,
                   eos ? StreamsConfig.EXACTLY_ONCE_V2 : StreamsConfig.AT_LEAST_ONCE);   // mặc định at_least_once
           // KHÔNG set commit.interval.ms → dùng default: 30000 (ALOS) / 100 (EOS)
           props.remove(StreamsConfig.COMMIT_INTERVAL_MS_CONFIG);
           System.out.println("processing.guarantee=" + props.get(StreamsConfig.PROCESSING_GUARANTEE_CONFIG));

           StreamsBuilder builder = new StreamsBuilder();
           builder.stream("eos-input", Consumed.with(Serdes.String(), Serdes.String()))
                   .mapValues(v -> {
                       try {
                           Thread.sleep(200);                    // giả lập xử lý chậm ~5 record/s
                       } catch (InterruptedException e) {
                           Thread.currentThread().interrupt();
                       }
                       return v.toUpperCase();
                   })
                   .peek((k, v) -> System.out.println("processed " + v))
                   .to("eos-output", Produced.with(Serdes.String(), Serdes.String()));

           Common.run(new KafkaStreams(builder.build(), props));
       }
   }
   ```
3. **Vòng 1 — `at_least_once`.** Terminal 1 chạy app; sau khi thấy khoảng `processed MSG-60` (≈ 12 s, **chưa tới commit đầu ở 30 s**) thì terminal 2 `kill -9`.

   ```bash
   # Terminal 1
   cd ~/kafka-labs/streams-lab && EOS=false ./gradlew run -PmainClass=lab.EosApp
   # Terminal 2 (sau ~12 giây)
   pkill -9 -f 'lab.EosApp'
   ```
4. Restart app (terminal 1) và **chờ xử lý hết 300 record** (~60 s, thấy `processed MSG-300` rồi im). Ctrl+C. Đếm output:

   ```bash
   kcc --topic eos-output --from-beginning --isolation-level read_committed --timeout-ms 10000 2>/dev/null | sort > /tmp/alos.txt
   wc -l < /tmp/alos.txt                 # > 300 (ví dụ 360)
   sort /tmp/alos.txt | uniq -d | wc -l  # số value bị lặp (≈ 60 — những record đã ghi output nhưng offset chưa commit)
   ```
5. **Vòng 2 — `exactly_once_v2`.** Reset output, chạy lại với `EOS=true`, kill sau ~12 s, restart, đếm.

   ```bash
   kt --delete --topic eos-output && kt --create --topic eos-output --partitions 3 --replication-factor 3
   # Terminal 1
   EOS=true ./gradlew run -PmainClass=lab.EosApp
   # Terminal 2 sau ~12 s
   pkill -9 -f 'lab.EosApp'
   # Terminal 1: chạy lại EOS=true, chờ xong (log có "transactional.id = eos-app-v2-<uuid>-<thread>"), Ctrl+C
   kcc --topic eos-output --from-beginning --isolation-level read_committed --timeout-ms 10000 2>/dev/null | sort > /tmp/eos.txt
   wc -l < /tmp/eos.txt                  # đúng 300
   sort /tmp/eos.txt | uniq -d | wc -l   # 0
   ```
6. Đọc lại với `--isolation-level read_uncommitted` (mặc định của console consumer) → có thể thấy **nhiều hơn 300** dòng: đó là record của transaction bị **abort** lúc `kill -9` (vẫn nằm trong log, có marker ABORT), consumer `read_committed` lọc bỏ.

   ```bash
   kcc --topic eos-output --from-beginning --isolation-level read_uncommitted --timeout-ms 10000 2>/dev/null | wc -l
   ```
7. Quan sát config Streams tự ghi đè khi EOS: trong log khởi động của vòng 2 tìm `isolation.level = read_committed` (consumer), `enable.idempotence = true` và `transactional.id = eos-app-v2-...` (producer), `commit.interval.ms = 100`.

### ✅ Kiểm chứng

- ALOS: tổng output > 300, `uniq -d` > 0 → **duplicate** (record xử lý lại từ offset commit cuối).
- EOS v2: `read_committed` đúng **300**, `uniq -d` = 0; `read_uncommitted` có thể > 300 (record aborted).
- Log EOS có `transactional.id`, `read_committed`, `commit.interval.ms = 100` mà bạn **không** set tay.

### 🧹 Dọn dẹp

```bash
for id in eos-app-alos eos-app-v2; do
  docker exec kafka-1 /opt/kafka/bin/kafka-streams-application-reset.sh --bootstrap-server kafka-1:19092 --application-id $id --input-topics eos-input
done
rm -rf /tmp/kafka-streams-lab*/eos-app-* /tmp/alos.txt /tmp/eos.txt
kt --delete --topic eos-input
kt --delete --topic eos-output
```

### 🧠 Ý nghĩa với đề thi

- `processing.guarantee` mặc định **`at_least_once`** → crash giữa 2 commit = xử lý lại = **duplicate** ở output và state.
- **`exactly_once_v2`**: 1 transactional producer / **thread**, `commit.interval.ms` → **100 ms**, consumer nội bộ `read_committed`; downstream phải đọc `read_committed` mới thấy exactly-once. Giá trị `exactly_once`/`exactly_once_beta` bị xoá ở 4.0.
- EOS chỉ bao **Kafka → Kafka** (topic + state store + offset); `Thread.sleep`/REST trong `mapValues`/`peek` vẫn chạy lại sau crash.
- Cluster 1 broker dev → EOS fail vì `transaction.state.log.replication.factor=3`/`min.isr=2` mặc định.

---

## Lab 6.5 — `TopologyTestDriver`: unit test WordCount, windowed + suppress, punctuator ⭐

**🎯 Mục tiêu:** Viết 3 test JUnit 5 chạy **không cần broker** trong < 5 giây: WordCount (`pipeInput`/`readKeyValuesToMap`), windowed + suppress (`advanceTime` để đóng window), wall-clock punctuator (`advanceWallClockTime`). Đây là kỹ năng domain **TEST**.
**🧩 Luyện kỹ năng (liên quan đề):**

- `kafka-streams-test-utils`: `TopologyTestDriver`, `TestInputTopic`, `TestOutputTopic`, `getKeyValueStore`.
- Event-time điều khiển bằng timestamp/`advanceTime`; wall-clock bằng `advanceWallClockTime`.
- `bootstrap.servers` giả bắt buộc; `state.dir` temp; `close()` bằng try-with-resources.

**⏱️ ~35 phút** · **Yêu cầu trước:** Lab 6.1, 6.2 (có `buildTopology`), Lab 6.6 code `PunctuatorApp` (viết trước, chạy sau cũng được — copy class ở Lab 6.6 bước 2 vào project trước khi chạy test thứ 3).

### Các bước

1. `src/test/java/lab/WordCountTopologyTest.java`.

   ```java
   // ~/kafka-labs/streams-lab/src/test/java/lab/WordCountTopologyTest.java — Lab 6.5
   package lab;

   import org.apache.kafka.common.serialization.LongDeserializer;
   import org.apache.kafka.common.serialization.StringDeserializer;
   import org.apache.kafka.common.serialization.StringSerializer;
   import org.apache.kafka.streams.StreamsConfig;
   import org.apache.kafka.streams.TestInputTopic;
   import org.apache.kafka.streams.TestOutputTopic;
   import org.apache.kafka.streams.TopologyTestDriver;
   import org.apache.kafka.streams.state.KeyValueStore;
   import org.junit.jupiter.api.Test;

   import java.nio.file.Files;
   import java.util.Map;
   import java.util.Properties;

   import static org.junit.jupiter.api.Assertions.assertEquals;
   import static org.junit.jupiter.api.Assertions.assertTrue;

   class WordCountTopologyTest {

       static Properties testProps(String appId) throws Exception {
           Properties p = new Properties();
           p.put(StreamsConfig.APPLICATION_ID_CONFIG, appId);
           p.put(StreamsConfig.BOOTSTRAP_SERVERS_CONFIG, "dummy:1234");        // bắt buộc có, không dùng
           p.put(StreamsConfig.STATE_DIR_CONFIG, Files.createTempDirectory("tt-" + appId).toString());
           return p;
       }

       @Test
       void countsWordsAcrossLines() throws Exception {
           try (TopologyTestDriver driver = new TopologyTestDriver(WordCountApp.buildTopology(), testProps("wc-test"))) {
               TestInputTopic<String, String> in = driver.createInputTopic(
                       WordCountApp.INPUT, new StringSerializer(), new StringSerializer());
               TestOutputTopic<String, Long> out = driver.createOutputTopic(
                       WordCountApp.OUTPUT, new StringDeserializer(), new LongDeserializer());

               in.pipeInput("l1", "Kafka Streams is a library");
               in.pipeInput("l2", "kafka is a log");

               // test driver flush cache sau mỗi record → thấy từng update; readKeyValuesToMap lấy giá trị CUỐI mỗi key
               Map<String, Long> counts = out.readKeyValuesToMap();
               assertEquals(2L, counts.get("kafka"));
               assertEquals(2L, counts.get("is"));
               assertEquals(2L, counts.get("a"));
               assertEquals(1L, counts.get("library"));
               assertTrue(out.isEmpty());

               // state store cũng truy cập được trực tiếp
               KeyValueStore<String, Long> store = driver.getKeyValueStore("word-counts");
               assertEquals(2L, store.get("kafka"));
           }
       }
   }
   ```
2. `src/test/java/lab/WindowedTopologyTest.java` — điểm mấu chốt: **suppress không emit** cho tới khi event time vượt `end + grace`.

   ```java
   // ~/kafka-labs/streams-lab/src/test/java/lab/WindowedTopologyTest.java — Lab 6.5
   package lab;

   import org.apache.kafka.common.serialization.LongDeserializer;
   import org.apache.kafka.common.serialization.StringDeserializer;
   import org.apache.kafka.common.serialization.StringSerializer;
   import org.apache.kafka.streams.KeyValue;
   import org.apache.kafka.streams.TestInputTopic;
   import org.apache.kafka.streams.TestOutputTopic;
   import org.apache.kafka.streams.TopologyTestDriver;
   import org.junit.jupiter.api.Test;

   import java.time.Duration;
   import java.time.Instant;
   import java.util.List;

   import static org.junit.jupiter.api.Assertions.assertEquals;
   import static org.junit.jupiter.api.Assertions.assertTrue;

   class WindowedTopologyTest {
       static final Instant T0 = Instant.parse("2026-01-01T00:00:00Z");

       @Test
       void withoutSuppressEmitsEveryUpdate() throws Exception {
           try (TopologyTestDriver driver = new TopologyTestDriver(
                   WindowedApp.buildTopology(false), WordCountTopologyTest.testProps("win-plain"))) {
               TestInputTopic<String, String> in = driver.createInputTopic(WindowedApp.INPUT, new StringSerializer(), new StringSerializer());
               TestOutputTopic<String, Long> out = driver.createOutputTopic(WindowedApp.OUTPUT, new StringDeserializer(), new LongDeserializer());

               in.pipeInput("alice", "/home", T0.plusSeconds(5));
               in.pipeInput("alice", "/cart", T0.plusSeconds(20));
               in.pipeInput("alice", "/pay", T0.plusSeconds(40));

               List<KeyValue<String, Long>> updates = out.readKeyValuesToList();
               assertEquals(3, updates.size());                                   // 1, 2, 3 — mỗi record 1 update
               assertEquals(new KeyValue<>("alice@" + T0, 3L), updates.get(2));
           }
       }

       @Test
       void withSuppressEmitsOnlyFinalResultAfterWindowCloses() throws Exception {
           try (TopologyTestDriver driver = new TopologyTestDriver(
                   WindowedApp.buildTopology(true), WordCountTopologyTest.testProps("win-suppress"))) {
               TestInputTopic<String, String> in = driver.createInputTopic(WindowedApp.INPUT, new StringSerializer(), new StringSerializer());
               TestOutputTopic<String, Long> out = driver.createOutputTopic(WindowedApp.OUTPUT, new StringDeserializer(), new LongDeserializer());

               in.pipeInput("alice", "/home", T0.plusSeconds(5));
               in.pipeInput("alice", "/cart", T0.plusSeconds(20));
               in.pipeInput("alice", "/pay", T0.plusSeconds(40));
               assertTrue(out.isEmpty(), "window [00:00,01:00) chưa đóng → suppress chưa emit");

               // stream time phải vượt end (60 s) + grace (10 s): record ở giây 71 của KEY KHÁC vẫn đẩy stream time của task
               in.pipeInput("bob", "/home", T0.plusSeconds(71));

               assertEquals(new KeyValue<>("alice@" + T0, 3L), out.readKeyValue());   // đúng 1 kết quả cuối
               assertTrue(out.isEmpty());                                             // window của bob chưa đóng

               // record LATE cho window đầu (ts 50 s, stream time đã 71 s > 70 s) → drop, không có output mới
               in.pipeInput("alice", "/late", T0.plusSeconds(50));
               in.advanceTime(Duration.ofSeconds(1));
               assertTrue(out.isEmpty());
           }
       }
   }
   ```
   > 📌 Test này giả định `page-views` chỉ có 1 partition trong test driver (luôn đúng — driver mô phỏng 1 partition/topic), nên record của `bob` và `alice` cùng task → cùng stream time. Trên cluster thật 3 partition, `bob` có thể rơi vào partition khác → stream time của task giữ `alice` không tiến (đó là lý do Lab 6.2 bước 7 dùng key `bob` vẫn hoạt động chỉ khi cùng partition; nếu không thấy output hãy gửi thêm `alice` ở giây 71).
3. `src/test/java/lab/PunctuatorTopologyTest.java` — cần class `PunctuatorApp` ở Lab 6.6 (copy trước).

   ```java
   // ~/kafka-labs/streams-lab/src/test/java/lab/PunctuatorTopologyTest.java — Lab 6.5
   package lab;

   import org.apache.kafka.common.serialization.LongDeserializer;
   import org.apache.kafka.common.serialization.StringDeserializer;
   import org.apache.kafka.common.serialization.StringSerializer;
   import org.apache.kafka.streams.KeyValue;
   import org.apache.kafka.streams.TestInputTopic;
   import org.apache.kafka.streams.TestOutputTopic;
   import org.apache.kafka.streams.TopologyTestDriver;
   import org.apache.kafka.streams.processor.PunctuationType;
   import org.junit.jupiter.api.Test;

   import java.time.Duration;
   import java.util.Map;

   import static org.junit.jupiter.api.Assertions.assertEquals;
   import static org.junit.jupiter.api.Assertions.assertTrue;

   class PunctuatorTopologyTest {

       @Test
       void wallClockPunctuatorFiresOnlyWhenTestAdvancesWallClock() throws Exception {
           try (TopologyTestDriver driver = new TopologyTestDriver(
                   PunctuatorApp.buildTopology(PunctuationType.WALL_CLOCK_TIME, Duration.ofSeconds(10)),
                   WordCountTopologyTest.testProps("punct-wall"))) {
               TestInputTopic<String, String> in = driver.createInputTopic(PunctuatorApp.INPUT, new StringSerializer(), new StringSerializer());
               TestOutputTopic<String, Long> out = driver.createOutputTopic(PunctuatorApp.OUTPUT, new StringDeserializer(), new LongDeserializer());

               in.pipeInput("alice", "x");
               in.pipeInput("alice", "y");
               in.pipeInput("bob", "z");
               assertTrue(out.isEmpty(), "processor chỉ ghi store, chưa forward");

               driver.advanceWallClockTime(Duration.ofSeconds(10));               // KHÔNG gọi → punctuator không bao giờ chạy trong test
               Map<String, Long> snapshot = out.readKeyValuesToMap();
               assertEquals(2L, snapshot.get("alice"));
               assertEquals(1L, snapshot.get("bob"));
           }
       }

       @Test
       void streamTimePunctuatorFiresAsEventTimeAdvances() throws Exception {
           try (TopologyTestDriver driver = new TopologyTestDriver(
                   PunctuatorApp.buildTopology(PunctuationType.STREAM_TIME, Duration.ofSeconds(10)),
                   WordCountTopologyTest.testProps("punct-stream"))) {
               TestInputTopic<String, String> in = driver.createInputTopic(PunctuatorApp.INPUT, new StringSerializer(), new StringSerializer());
               TestOutputTopic<String, Long> out = driver.createOutputTopic(PunctuatorApp.OUTPUT, new StringDeserializer(), new LongDeserializer());

               // 60 record, timestamp 1..60 s → stream time tiến 60 s → punctuator 10 s chạy ~6 lần, KHÔNG phụ thuộc wall clock
               for (int s = 1; s <= 60; s++) {
                   in.pipeInput("alice", "v" + s, java.time.Instant.ofEpochSecond(s));
               }
               long fires = out.readKeyValuesToList().stream().filter(kv -> kv.key.equals("alice")).count();
               assertTrue(fires >= 5 && fires <= 6, "expected ~6 stream-time punctuations, got " + fires);
           }
       }
   }
   ```
4. Chạy test.

   ```bash
   cd ~/kafka-labs/streams-lab && ./gradlew test
   ```
   Output mẫu:
   ```
   WordCountTopologyTest > countsWordsAcrossLines() PASSED
   WindowedTopologyTest > withoutSuppressEmitsEveryUpdate() PASSED
   WindowedTopologyTest > withSuppressEmitsOnlyFinalResultAfterWindowCloses() PASSED
   PunctuatorTopologyTest > wallClockPunctuatorFiresOnlyWhenTestAdvancesWallClock() PASSED
   PunctuatorTopologyTest > streamTimePunctuatorFiresAsEventTimeAdvances() PASSED
   BUILD SUCCESSFUL in 4s
   ```
   Tắt cluster Docker rồi chạy lại `./gradlew test` → **vẫn xanh** (không cần broker).
5. Thử **phá** để hiểu: trong test suppress, xoá dòng `in.pipeInput("bob", ...)` → `readKeyValue()` ném `NoSuchElementException` (không có output vì window chưa đóng). Trong test wall-clock, xoá `advanceWallClockTime` → fail vì output rỗng.

### ✅ Kiểm chứng

- 5 test PASSED, `./gradlew test` < 10 s, không cần Docker.
- Test suppress chỉ có output **sau** khi pipe record timestamp > 70 s; test wall-clock chỉ có output **sau** `advanceWallClockTime`.

### 🧹 Dọn dẹp

```bash
rm -rf /tmp/tt-*        # state.dir tạm của test driver (driver.close() đã xoá phần lớn)
```

### 🧠 Ý nghĩa với đề thi

- `TopologyTestDriver` (artifact **`kafka-streams-test-utils`**) = unit test topology **không broker**, **đồng bộ**, nhanh; `bootstrap.servers` giả bắt buộc; luôn `close()`.
- Event-time: pipe record với **timestamp** hoặc `advanceTime`; wall-clock punctuator: **`advanceWallClockTime`**. Stream-time punctuator tự chạy theo timestamp.
- Test driver **flush cache mỗi record** → thấy từng update (khác production 10 MB); kết quả cuối giống nhau.
- Không test được rebalance/nhiều instance → integration test với Testcontainers/EmbeddedKafka (Tuần 7).

---

## Lab 6.6 — Processor API: state store + punctuator `WALL_CLOCK_TIME` vs `STREAM_TIME`

**🎯 Mục tiêu:** Viết `Processor` đếm record theo key vào RocksDB store và **flush định kỳ 10 s** bằng punctuator; chạy với `WALL_CLOCK_TIME` (chạy đều dù không có dữ liệu) rồi `STREAM_TIME` (chỉ chạy khi có record mới) để thấy khác biệt.
**🧩 Luyện kỹ năng (liên quan đề):**

- `org.apache.kafka.streams.processor.api.Processor`, `ProcessorContext`, `Record`, `context.schedule`, `context.forward`.
- `Topology.addSource/addProcessor/addStateStore/addSink`, `Stores.persistentKeyValueStore`.
- `ProcessorSupplier#get()` trả instance mới mỗi lần (method reference `CountingProcessor::new`).

**⏱️ ~25 phút** · **Yêu cầu trước:** Lab 6.1.

### Các bước

1. Tạo topic.

   ```bash
   kt --create --topic punct-input --partitions 3 --replication-factor 3
   kt --create --topic punct-output --partitions 3 --replication-factor 3
   ```
2. Tạo `src/main/java/lab/PunctuatorApp.java`.

   ```java
   // ~/kafka-labs/streams-lab/src/main/java/lab/PunctuatorApp.java — Lab 6.6 (+ test ở Lab 6.5)
   package lab;

   import org.apache.kafka.common.serialization.Serdes;
   import org.apache.kafka.streams.KafkaStreams;
   import org.apache.kafka.streams.KeyValue;
   import org.apache.kafka.streams.Topology;
   import org.apache.kafka.streams.processor.PunctuationType;
   import org.apache.kafka.streams.processor.api.Processor;
   import org.apache.kafka.streams.processor.api.ProcessorContext;
   import org.apache.kafka.streams.processor.api.Record;
   import org.apache.kafka.streams.state.KeyValueIterator;
   import org.apache.kafka.streams.state.KeyValueStore;
   import org.apache.kafka.streams.state.Stores;

   import java.time.Duration;

   public class PunctuatorApp {
       public static final String INPUT = "punct-input";
       public static final String OUTPUT = "punct-output";
       public static final String STORE = "punct-counts";

       /** Đếm record theo key vào store; punctuator định kỳ forward toàn bộ store xuống sink. */
       static final class CountingProcessor implements Processor<String, String, String, Long> {
           private final PunctuationType type;
           private final Duration interval;
           private ProcessorContext<String, Long> context;
           private KeyValueStore<String, Long> store;

           CountingProcessor(PunctuationType type, Duration interval) {
               this.type = type;
               this.interval = interval;
           }

           @Override
           public void init(ProcessorContext<String, Long> context) {
               this.context = context;
               this.store = context.getStateStore(STORE);
               context.schedule(interval, type, timestamp -> {          // Punctuator: (long timestamp) -> void
                   System.out.printf("[punctuate %s] ts=%d%n", type, timestamp);
                   try (KeyValueIterator<String, Long> it = store.all()) {
                       while (it.hasNext()) {
                           KeyValue<String, Long> kv = it.next();
                           context.forward(new Record<>(kv.key, kv.value, timestamp));
                       }
                   }
                   // recordMetadata() rỗng trong punctuator — không có record đang xử lý
               });
           }

           @Override
           public void process(Record<String, String> record) {
               Long old = store.get(record.key());
               store.put(record.key(), old == null ? 1L : old + 1);    // chỉ ghi store, KHÔNG forward
           }

           @Override
           public void close() {
               // không đóng store — library quản lý
           }
       }

       public static Topology buildTopology(PunctuationType type, Duration interval) {
           Topology topology = new Topology();
           topology.addSource("Source", Serdes.String().deserializer(), Serdes.String().deserializer(), INPUT);
           // ProcessorSupplier phải trả INSTANCE MỚI mỗi lần get() → lambda tạo new mỗi lần
           topology.addProcessor("Count", () -> new CountingProcessor(type, interval), "Source");
           topology.addStateStore(
                   Stores.keyValueStoreBuilder(Stores.persistentKeyValueStore(STORE), Serdes.String(), Serdes.Long()), // RocksDB + changelog (logging mặc định bật)
                   "Count");
           topology.addSink("Sink", OUTPUT, Serdes.String().serializer(), Serdes.Long().serializer(), "Count");
           return topology;
       }

       public static void main(String[] args) {
           PunctuationType type = PunctuationType.valueOf(System.getenv().getOrDefault("PUNCT", "WALL_CLOCK_TIME"));
           Topology topology = buildTopology(type, Duration.ofSeconds(10));
           System.out.println(topology.describe());
           Common.run(new KafkaStreams(topology, Common.props("punct-app-" + type.name().toLowerCase())));
       }
   }
   ```
3. **Terminal 1:** chạy với `WALL_CLOCK_TIME`; **Terminal 2:** consumer output.

   ```bash
   cd ~/kafka-labs/streams-lab && COMMIT_MS=1000 PUNCT=WALL_CLOCK_TIME ./gradlew run -PmainClass=lab.PunctuatorApp
   ```
   ```bash
   kcc --topic punct-output --property print.key=true --property print.timestamp=true \
     --value-deserializer org.apache.kafka.common.serialization.LongDeserializer
   ```
   Terminal 1 in `[punctuate WALL_CLOCK_TIME] ts=...` **mỗi 10 s cho mỗi task** (3 task → 3 dòng/10 s) dù chưa có dữ liệu; terminal 2 chưa có gì (store rỗng).
4. **Terminal 3:** gửi vài record rồi **ngồi chờ**.

   ```bash
   printf 'alice:a\nalice:b\nbob:c\n' | docker exec -i kafka-1 /opt/kafka/bin/kafka-console-producer.sh \
     --bootstrap-server kafka-1:19092 --topic punct-input --property parse.key=true --property key.separator=:
   ```
   Terminal 2: sau ≤ 10 s thấy `alice 2`, `bob 1`; **và cứ mỗi 10 s lại thấy lại** (punctuator forward toàn bộ store) dù không gửi thêm gì.
5. Ctrl+C, chạy với `STREAM_TIME`.

   ```bash
   COMMIT_MS=1000 PUNCT=STREAM_TIME ./gradlew run -PmainClass=lab.PunctuatorApp
   ```
   Terminal 1: **không** có dòng `[punctuate STREAM_TIME]` nào dù chờ 1 phút — stream time không tiến vì không có record. Gửi lại 3 record → punctuator chạy khi stream time nhảy ≥ 10 s so với lần trước (record đầu tiên khởi tạo stream time; gửi thêm sau > 10 s thực tế → timestamp `CreateTime` mới lớn hơn 10 s → chạy 1 lần). Gửi 5 record trong 1 giây → chỉ **0–1** lần, không phải 5.

### ✅ Kiểm chứng

- `WALL_CLOCK_TIME`: log punctuate đều 10 s/task bất kể dữ liệu; output lặp lại snapshot store.
- `STREAM_TIME`: im lặng khi idle; chỉ chạy khi timestamp record mới vượt mốc 10 s.
- `kt --list | grep punct-app` có `punct-app-wall_clock_time-punct-counts-changelog` (store PAPI cũng có changelog).

### 🧹 Dọn dẹp

```bash
for id in punct-app-wall_clock_time punct-app-stream_time; do
  docker exec kafka-1 /opt/kafka/bin/kafka-streams-application-reset.sh --bootstrap-server kafka-1:19092 --application-id $id --input-topics punct-input 2>/dev/null
done
rm -rf /tmp/kafka-streams-lab*/punct-app-*
kt --delete --topic punct-input
kt --delete --topic punct-output
```

### 🧠 Ý nghĩa với đề thi

- **`STREAM_TIME`** = theo event time, **chỉ tiến khi có record** (idle → không chạy); **`WALL_CLOCK_TIME`** = theo đồng hồ hệ thống, chạy đều. Câu "60 record 1..60 s, schedule 10 s, xử lý trong 20 s" → 6 lần vs 2 lần.
- `ProcessorSupplier#get()` phải **new** mỗi lần; `close()` **không** đóng store; `recordMetadata()` rỗng trong punctuator; `commit()` chỉ là yêu cầu.
- Store PAPI tạo qua `Stores.keyValueStoreBuilder(persistentKeyValueStore | inMemoryKeyValueStore)`, gắn bằng `addStateStore(builder, processorName)`; logging mặc định bật → có changelog.
- Package đúng ở 4.x: `org.apache.kafka.streams.processor.api.*` (bản cũ đã xoá).

---

## Lab 6.7 — Option không Java: ksqlDB (`CREATE STREAM`, `CTAS COUNT`, push vs pull query)

**🎯 Mục tiêu:** Chạy `ksqlDB Server` (port 8088) trên cluster hiện có, khai báo STREAM từ topic, tạo TABLE bằng `CREATE TABLE ... AS SELECT COUNT(*)` (persistent query = 1 Kafka Streams topology), chạy **push query** (`EMIT CHANGES`) và **pull query**, và nhìn internal topic mà ksqlDB tạo — y hệt Lab 6.1 nhưng bằng SQL.
**🧩 Luyện kỹ năng (liên quan đề):**

- STREAM (≈ `KStream`) vs TABLE (≈ `KTable`, cần `PRIMARY KEY`); CSAS/CTAS; command topic.
- Push query stream liên tục vs pull query snapshot (= Interactive Query).
- Nhận ra `_confluent-ksql-<service.id>...` và `...-repartition`/`-changelog` do Streams bên dưới tạo.

**⏱️ ~25 phút** · **Yêu cầu trước:** cluster 3 node đang chạy. Không cần Java.

### Các bước

1. Tạo file compose **override** thêm 2 service (server + CLI), chạy cùng file cluster.

   ```yaml
   # ~/kafka-labs/docker-compose.ksqldb.yml — thêm ksqlDB vào cluster 3 node
   services:
     ksqldb-server:
       image: confluentinc/cp-ksqldb-server:8.0.0
       container_name: ksqldb-server
       depends_on: [kafka-1, kafka-2, kafka-3]
       ports:
         - "8088:8088"
       environment:
         KSQL_LISTENERS: http://0.0.0.0:8088
         KSQL_BOOTSTRAP_SERVERS: kafka-1:19092,kafka-2:19092,kafka-3:19092   # listener nội bộ
         KSQL_KSQL_SERVICE_ID: lab_ksql_                                     # nhiều server cùng id = 1 cụm; prefix command topic
         KSQL_KSQL_STREAMS_REPLICATION_FACTOR: 3
         KSQL_KSQL_INTERNAL_TOPIC_REPLICAS: 3
         KSQL_KSQL_LOGGING_PROCESSING_TOPIC_AUTO_CREATE: "true"
         KSQL_KSQL_LOGGING_PROCESSING_STREAM_AUTO_CREATE: "true"

     ksqldb-cli:
       image: confluentinc/cp-ksqldb-cli:8.0.0
       container_name: ksqldb-cli
       depends_on: [ksqldb-server]
       entrypoint: /bin/sh
       tty: true
   ```
   ```bash
   cd ~/kafka-labs
   docker compose -f docker-compose.cluster.yml -f docker-compose.ksqldb.yml up -d
   curl -s http://localhost:8088/info | head -c 300; echo      # {"KsqlServerInfo":{"version":"8.0.0",...,"serverStatus":"RUNNING"}}
   ```
2. Tạo topic + nạp dữ liệu JSON.

   ```bash
   kt --create --topic ksql-pageviews --partitions 3 --replication-factor 3
   printf 'alice:{"page":"/home"}\nalice:{"page":"/cart"}\nbob:{"page":"/home"}\nalice:{"page":"/pay"}\n' | \
     docker exec -i kafka-1 /opt/kafka/bin/kafka-console-producer.sh --bootstrap-server kafka-1:19092 \
     --topic ksql-pageviews --property parse.key=true --property key.separator=:
   ```
3. Vào CLI và khai báo STREAM (metadata thôi, không copy dữ liệu).

   ```bash
   docker exec -it ksqldb-cli ksql http://ksqldb-server:8088
   ```
   ```sql
   SET 'auto.offset.reset' = 'earliest';

   CREATE STREAM pageviews (user_id VARCHAR KEY, page VARCHAR)
     WITH (kafka_topic = 'ksql-pageviews', value_format = 'JSON');

   SHOW STREAMS;
   SELECT user_id, page FROM pageviews EMIT CHANGES LIMIT 4;     -- push query trên STREAM: 4 dòng rồi dừng vì LIMIT
   ```
4. Tạo TABLE bằng **persistent query** (CTAS) — đây chính là `groupByKey().count()` của Lab 6.1.

   ```sql
   CREATE TABLE views_per_user AS
     SELECT user_id, COUNT(*) AS cnt
     FROM pageviews
     GROUP BY user_id
     EMIT CHANGES;

   SHOW QUERIES;        -- CTAS_VIEWS_PER_USER_x  | PERSISTENT | RUNNING | sink: VIEWS_PER_USER
   SHOW TOPICS;         -- thấy topic VIEWS_PER_USER (kết quả) + _confluent-ksql-lab_ksql_command_topic + ...-changelog/-repartition
   ```
5. **Push query** vs **pull query** trên TABLE.

   ```sql
   -- Pull query: snapshot hiện tại, trả 1 dòng rồi KẾT THÚC (= Interactive Query / lookup)
   SELECT user_id, cnt FROM views_per_user WHERE user_id = 'alice';
   --  alice | 3

   -- Push query: chạy liên tục, in mỗi khi count đổi (Ctrl+C để dừng)
   SELECT user_id, cnt FROM views_per_user EMIT CHANGES;
   ```
   Giữ push query chạy; **terminal khác** produce thêm `bob:{"page":"/pay"}` vào `ksql-pageviews` → push query in `bob | 2` ngay. Chạy lại pull query cho `bob` → `2`.
6. (Tuỳ chọn) Window bằng SQL — so với `TimeWindows` ở Lab 6.2.

   ```sql
   CREATE TABLE views_per_minute AS
     SELECT user_id, WINDOWSTART AS ws, COUNT(*) AS cnt
     FROM pageviews
     WINDOW TUMBLING (SIZE 1 MINUTE, GRACE PERIOD 10 SECONDS)
     GROUP BY user_id
     EMIT CHANGES;
   SELECT * FROM views_per_minute EMIT CHANGES LIMIT 3;
   ```
7. Xem internal topic từ phía Kafka (terminal host): ksqlDB đặt `application.id` = `_confluent-ksql-<service.id>query_<QUERY_ID>`.

   ```bash
   kt --list | grep -i ksql
   # _confluent-ksql-lab_ksql__command_topic
   # _confluent-ksql-lab_ksql_query_CTAS_VIEWS_PER_USER_1-Aggregate-Aggregate-Materialize-changelog
   # _confluent-ksql-lab_ksql_query_CTAS_VIEWS_PER_USER_1-Aggregate-GroupBy-repartition   (nếu ksqlDB cần repartition)
   # VIEWS_PER_USER
   kcg --list | grep ksql          # consumer group = application.id của topology Streams bên dưới
   ```

### ✅ Kiểm chứng

- `SHOW QUERIES` có persistent query `RUNNING`; `SHOW TOPICS` có sink topic `VIEWS_PER_USER` + changelog + command topic.
- Pull query trả **1 dòng rồi thoát**; push query **treo** và in update khi produce thêm.
- `kcg --list` thấy group của query → chứng minh ksqlDB chỉ là Kafka Streams được sinh từ SQL.

### 🧹 Dọn dẹp

```sql
-- trong ksql CLI
TERMINATE ALL;
DROP TABLE views_per_minute DELETE TOPIC;
DROP TABLE views_per_user DELETE TOPIC;
DROP STREAM pageviews;
exit
```
```bash
docker compose -f docker-compose.cluster.yml -f docker-compose.ksqldb.yml stop ksqldb-server ksqldb-cli
docker compose -f docker-compose.cluster.yml -f docker-compose.ksqldb.yml rm -f ksqldb-server ksqldb-cli
kt --delete --topic ksql-pageviews
# Kết thúc tuần: tắt cluster (GIỮ compose + streams-lab/ cho Tuần 7 dùng lại TopologyTestDriver/Testcontainers)
docker compose -f docker-compose.cluster.yml down
```

### 🧠 Ý nghĩa với đề thi

- ksqlDB = **SQL trên Kafka Streams**: mỗi CSAS/CTAS = 1 topology + consumer group + internal topic; server REST **8088**; DDL lưu trong **command topic**; `ksql.service.id` định danh cụm.
- **STREAM** = append-only (`KStream`); **TABLE** = giá trị mới nhất theo `PRIMARY KEY` (`KTable`).
- **Push query** `EMIT CHANGES` = liên tục; **pull query** (không `EMIT CHANGES`) = snapshot từ materialized view = Interactive Query.
- Chọn ksqlDB khi cần SQL/prototyping/không muốn Java; chọn Streams khi cần kiểm soát code, unit test `TopologyTestDriver`, nhúng vào service.

---

> ✅ Xong 6–7 lab? Giữ lại `~/kafka-labs/streams-lab/` (Tuần 7 dùng lại `TopologyTestDriver` + thêm Testcontainers) và `ts-producer.mjs`. Đối chiếu [Lab checklist trong README](README.md#-lab-checklist) rồi làm [bộ câu hỏi luyện tập](questions.md) trước khi sang Tuần 7.
