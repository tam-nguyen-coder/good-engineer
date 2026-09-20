# Apache Kafka — Introduction (Main Concepts & Terminology) + Quickstart

> **Nguồn (official):** https://kafka.apache.org/43/getting-started/introduction/ · https://kafka.apache.org/43/getting-started/quickstart/
> **Tuần:** 1 — Kiến trúc Kafka & `KRaft` + Dựng cluster + CLI · **Loại:** Apache Kafka Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- Kafka = **event streaming platform** với **3 khả năng**: publish/subscribe, **store** bền vững "as long as you want", **process** (real-time hoặc retrospectively). Cộng `Kafka Connect` và `Admin API` → **5 API**: `Admin`, `Producer`, `Consumer`, `Kafka Streams`, `Kafka Connect`.
- Kafka là hệ phân tán gồm **servers** (broker = storage layer; Connect server = import/export) và **clients**, nói chuyện qua **TCP** protocol tự định nghĩa.
- **Event/record** = key + value + timestamp + optional **headers**. Producer và consumer **fully decoupled** — đây là lý do Kafka scale.
- **Topic**: zero/one/many producer và consumer; **event KHÔNG bị xoá sau khi consume**, giữ theo **retention per-topic** → "topic là log, không phải queue".
- **Partition** = "bucket" rải trên nhiều broker. Cùng **key → cùng partition**; Kafka **chỉ đảm bảo thứ tự trong 1 topic-partition** ("exactly the same order as they were written").
- **Replication factor 3** là "common production setting" — luôn có 3 bản sao dữ liệu, thực hiện ở mức **topic-partition**.
- Quickstart 4.3.1 yêu cầu **Java 17+**; khởi động KRaft = `kafka-storage.sh random-uuid` → `kafka-storage.sh format --standalone -t <id> -c config/server.properties` → `kafka-server-start.sh`.
- Docker: `docker run -p 9092:9092 apache/kafka:4.3.1` — image tự format storage. Mọi CLI dùng **`--bootstrap-server localhost:9092`** (không còn `--zookeeper`).
- Bộ 3 lệnh quickstart phải thuộc: `kafka-topics.sh --create/--describe`, `kafka-console-producer.sh --topic`, `kafka-console-consumer.sh --topic --from-beginning`.
- Teardown xoá dữ liệu local: `rm -rf /tmp/kafka-logs /tmp/kraft-combined-logs` — `log.dirs` mặc định của cấu hình combined là `/tmp/kraft-combined-logs`.

---

## 📄 Nội dung (trích từ tài liệu gốc)

### What is event streaming?

Event streaming is the digital equivalent of the human body's central nervous system. It is the technological foundation for the 'always-on' world where businesses are increasingly software-defined and automated, and where the user of software is more software.

Technically speaking, event streaming is the practice of capturing data in real-time from event sources like databases, sensors, mobile devices, cloud services, and software applications in the form of streams of events; storing these event streams durably for later retrieval; manipulating, processing, and reacting to the event streams in real-time as well as retrospectively; and routing the event streams to different destination technologies as needed. Event streaming thus ensures a continuous flow and interpretation of data so that the right information is at the right place, at the right time.

### Apache Kafka is an event streaming platform. What does that mean?

Kafka combines three key capabilities so you can implement your use cases for event streaming end-to-end with a single battle-tested solution:

1. To **publish** (write) and **subscribe to** (read) streams of events, including continuous import/export of your data from other systems.
2. To **store** streams of events durably and reliably for as long as you want.
3. To **process** streams of events as they occur or retrospectively.

And all this functionality is provided in a distributed, highly scalable, elastic, fault-tolerant, and secure manner. Kafka can be deployed on bare-metal hardware, virtual machines, and containers, and on-premises as well as in the cloud.

### How does Kafka work in a nutshell?

Kafka is a distributed system consisting of **servers** and **clients** that communicate via a high-performance **TCP network protocol**.

**Servers**: Kafka is run as a cluster of one or more servers that can span multiple datacenters or cloud regions. Some of these servers form the storage layer, called the **brokers**. Other servers run **Kafka Connect** to continuously import and export data as event streams to integrate Kafka with your existing systems such as relational databases as well as other Kafka clusters. A Kafka cluster is highly scalable and fault-tolerant: if any of its servers fails, the other servers will take over their work to ensure continuous operations without any data loss.

**Clients**: They allow you to write distributed applications and microservices that read, write, and process streams of events in parallel, at scale, and in a fault-tolerant manner even in the case of network problems or machine failures. Kafka ships with some such clients included, which are augmented by dozens of clients provided by the Kafka community.

### Main Concepts and Terminology

An **event** records the fact that "something happened" in the world or in your business. It is also called record or message in the documentation. When you read or write data to Kafka, you do this in the form of events. Conceptually, an event has a **key, value, timestamp, and optional metadata headers**. Here's an example event:

- Event key: "Alice"
- Event value: "Made a payment of $200 to Bob"
- Event timestamp: "Jun. 25, 2020 at 2:06 p.m."

**Producers** are those client applications that publish (write) events to Kafka, and **consumers** are those that subscribe to (read and process) these events. In Kafka, producers and consumers are **fully decoupled and agnostic of each other**, which is a key design element to achieve the high scalability that Kafka is known for. For example, producers never need to wait for consumers. Kafka provides various guarantees such as the ability to process events exactly-once.

Events are organized and durably stored in **topics**. Very simplified, a topic is similar to a folder in a filesystem, and the events are the files in that folder. An example topic name could be "payments". Topics in Kafka are always multi-producer and multi-subscriber: a topic can have **zero, one, or many producers** that write events to it, as well as **zero, one, or many consumers** that subscribe to these events. Events in a topic can be read as often as needed — unlike traditional messaging systems, **events are not deleted after consumption**. Instead, you define for how long Kafka should retain your events through a **per-topic configuration setting**, after which old events will be discarded. Kafka's performance is effectively constant with respect to data size, so storing data for a long time is perfectly fine.

Topics are **partitioned**, meaning a topic is spread over a number of "buckets" located on different Kafka brokers. This distributed placement of your data is very important for scalability because it allows client applications to both read and write the data from/to many brokers at the same time. When a new event is published to a topic, it is actually appended to one of the topic's partitions. **Events with the same event key** (e.g., a customer or vehicle ID) **are written to the same partition**, and Kafka **guarantees that any consumer of a given topic-partition will always read that partition's events in exactly the same order as they were written**.

To make your data fault-tolerant and highly-available, every topic can be **replicated**, even across geo-regions or datacenters, so that there are always multiple brokers that have a copy of the data just in case things go wrong, you want to do maintenance on the brokers, and so on. A common production setting is a **replication factor of 3**, i.e., there will always be three copies of your data. This replication is performed at the level of topic-partitions.

### Kafka APIs

In addition to command line tooling for management and administration tasks, Kafka has five core APIs for Java and Scala:

- The **Admin API** to manage and inspect topics, brokers, and other Kafka objects.
- The **Producer API** to publish (write) a stream of events to one or more Kafka topics.
- The **Consumer API** to subscribe to (read) one or more topics and to process the stream of events produced to them.
- The **Kafka Streams API** to implement stream processing applications and microservices. It provides higher-level functions to process event streams, including transformations, stateful operations like aggregations and joins, windowing, processing based on event-time, and more. Input is read from one or more topics in order to generate output to one or more topics, effectively transforming the input streams to output streams.
- The **Kafka Connect API** to build and run reusable data import/export connectors that consume (read) or produce (write) streams of events from and to external systems and applications so they can integrate with Kafka. For example, a connector to a relational database like PostgreSQL might capture every change to a set of tables. However, in practice, you typically don't need to implement your own connectors because the Kafka community already provides hundreds of ready-to-use connectors.

---

### Quickstart (Kafka 4.3.1)

#### Step 1: Get Kafka

Download the latest Kafka release and extract it:

```bash
$ tar -xzf kafka_2.13-4.3.1.tgz
$ cd kafka_2.13-4.3.1
```

#### Step 2: Start the Kafka environment

NOTE: Your local environment must have **Java 17+** installed.

**Kafka with KRaft — using downloaded files.** Generate a Cluster UUID:

```bash
$ KAFKA_CLUSTER_ID="$(bin/kafka-storage.sh random-uuid)"
```

Format Log Directories:

```bash
$ bin/kafka-storage.sh format --standalone -t $KAFKA_CLUSTER_ID -c config/server.properties
```

Start the Kafka Server:

```bash
$ bin/kafka-server-start.sh config/server.properties
```

Once the Kafka server has successfully launched, you will have a basic Kafka environment running and ready to use.

**Kafka with KRaft — using Docker image.** Get the Docker image and start the Kafka Docker container:

```bash
$ docker pull apache/kafka:4.3.1
$ docker run -p 9092:9092 apache/kafka:4.3.1
```

#### Step 3: Create a topic to store your events

Kafka is a distributed event streaming platform that lets you read, write, store, and process events (also called records or messages) across many machines. Before you can write your first events, you must create a topic:

```bash
$ bin/kafka-topics.sh --create --topic quickstart-events --bootstrap-server localhost:9092
```

All of Kafka's command line tools have additional options: run the `kafka-topics.sh` command without any arguments to display usage information. For example, it can also show you details such as the partition count of the new topic:

```bash
$ bin/kafka-topics.sh --describe --topic quickstart-events --bootstrap-server localhost:9092
Topic: quickstart-events        TopicId: NPmZHyhbR9y00wMglMH2sg PartitionCount: 1       ReplicationFactor: 1	Configs:
    Topic: quickstart-events Partition: 0    Leader: 0   Replicas: 0 Isr: 0
```

#### Step 4: Write some events into the topic

A Kafka client communicates with the Kafka brokers via the network for writing (or reading) events. Once received, the brokers will store the events in a durable and fault-tolerant manner for as long as you need — even forever. Run the console producer client to write a few events into your topic. By default, each line you enter will result in a separate event being written to the topic.

```bash
$ bin/kafka-console-producer.sh --topic quickstart-events --bootstrap-server localhost:9092
>This is my first event
>This is my second event
```

#### Step 5: Read the events

Open another terminal session and run the console consumer client to read the events you just created:

```bash
$ bin/kafka-console-consumer.sh --topic quickstart-events --from-beginning --bootstrap-server localhost:9092
This is my first event
This is my second event
```

Because events are durably stored in Kafka, they can be read as many times and by as many consumers as you want. You can easily verify this by opening yet another terminal session and re-running the previous command again.

#### Step 6: Import/export your data as streams of events with Kafka Connect

Kafka Connect allows you to continuously ingest data from external systems into Kafka, and vice versa. It is an extensible tool that runs connectors, which implement the custom logic for interacting with an external system. The quickstart edits `plugin.path` in `config/connect-standalone.properties`, then runs `bin/connect-standalone.sh` with a FileStream source and sink connector.

#### Step 8: Terminate the Kafka environment

Stop the producer and consumer clients with `Ctrl-C`, stop the Kafka broker with `Ctrl-C`. If you also want to delete any data of your local Kafka environment including any events you have created along the way, run:

```bash
$ rm -rf /tmp/kafka-logs /tmp/kraft-combined-logs
```
