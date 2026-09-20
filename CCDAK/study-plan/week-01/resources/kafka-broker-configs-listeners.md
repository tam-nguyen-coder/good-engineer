# Apache Kafka — Broker Configs (listeners, log.*, replication defaults) + Listener Configuration

> **Nguồn (official):** https://kafka.apache.org/43/configuration/broker-configs/ · https://kafka.apache.org/43/security/listener-configuration/ · bổ trợ: https://www.confluent.io/blog/kafka-listeners-explained/
> **Tuần:** 1 — Kiến trúc Kafka & `KRaft` + Dựng cluster + CLI · **Loại:** Apache Kafka Docs + Confluent Blog
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- `listeners` = nơi broker **bind** (mặc định `PLAINTEXT://:9092`, dạng `{LISTENER_NAME}://{host}:{port}`); `advertised.listeners` = địa chỉ broker **quảng bá cho client và broker khác** qua metadata. Client luôn dùng địa chỉ **advertised** sau bước bootstrap.
- Luồng kết nối 3 bước: (1) nối tới **1** địa chỉ trong `bootstrap.servers`; (2) nhận **metadata** có host:port advertised của **mọi** broker + leader từng partition; (3) nối **thẳng** tới broker/leader theo địa chỉ advertised. "Even if you can make the initial connection… the address returned in the metadata may still be for a hostname that is not accessible from your client" → bẫy Docker.
- Bẫy Docker: advertise `kafka0:9092` → client trên host bootstrap **được** nhưng không resolve `kafka0` → timeout/`ENOTFOUND`. Fix: **2 listener** (nội bộ advertise hostname container, host advertise `localhost:<port>`), map bằng `listener.security.protocol.map`, chọn `inter.broker.listener.name` cho listener nội bộ.
- 4 security protocol (không phân biệt hoa/thường): `PLAINTEXT`, `SSL`, `SASL_PLAINTEXT`, `SASL_SSL`. Inter-broker: đặt `inter.broker.listener.name` **hoặc** `security.inter.broker.protocol` (mặc định `PLAINTEXT`) — **không đặt cả hai**.
- KRaft: controller có listener riêng qua `controller.listener.names` (thường `CONTROLLER`, port **9093**), **không được trùng** inter-broker listener; controller listener **không** nằm trong `advertised.listeners`.
- Quorum: `controller.quorum.voters` (`{id}@{host}:{port}`, static, deprecated) vs `controller.quorum.bootstrap.servers` (dynamic). `process.roles` ∈ {broker, controller}; `node.id` ≥ 0 duy nhất toàn cluster.
- Topic defaults: `num.partitions` **1**, `default.replication.factor` **1**, `min.insync.replicas` **1** (áp dụng khi `acks=all`), `auto.create.topics.enable` **true**.
- Log: `log.segment.bytes` **1073741824** (1 GiB, tối thiểu 1 MiB), `log.roll.hours` **168**, `log.retention.hours` **168**, `log.retention.bytes` **-1**, `log.retention.check.interval.ms` **300000** (5 phút), `log.index.interval.bytes` **4096**, `log.message.timestamp.type` **CreateTime**, `message.max.bytes` **1048588** (tính **sau** nén, mức batch).
- Replication/leader: `replica.lag.time.max.ms` **30000**, `unclean.leader.election.enable` **false**, `auto.leader.rebalance.enable` **true**, `leader.imbalance.check.interval.seconds` **300**.
- Khác: `offsets.topic.num.partitions` **50**, `group.initial.rebalance.delay.ms` **3000**, `num.io.threads` **8**, `num.recovery.threads.per.data.dir` **2** (4.0 đổi từ 1, KIP-1030). Debug advertised bằng `kafkacat -L` (hoặc `kafka-broker-api-versions.sh`).

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Broker Configs (selected entries — Kafka 4.3)

| Name | Description | Type | Default | Importance | Update Mode |
| --- | --- | --- | --- | --- | --- |
| `advertised.listeners` | Specifies the listener addresses that the Kafka brokers will advertise to clients and other brokers. The config is useful where the actual listener configuration `listeners` does not represent the addresses that clients should use to connect, such as in cloud environments. In IaaS environments, this may need to be different from the interface to which the broker binds. If this is not set, the value for `listeners` will be used. Unlike `listeners`, it is not valid to advertise the 0.0.0.0 meta-address. Also unlike `listeners`, there can be duplicated ports in this property, so that one listener can be configured to advertise another listener's address. | list | null | high | per-broker |
| `listeners` | Listener List — Comma-separated list of URIs we will listen on and the listener names. If the listener name is not a security protocol, `listener.security.protocol.map` must also be set. Listener names and port numbers must be unique unless one listener is an IPv4 address and the other listener is an IPv6 address (for the same port). Specify hostname as 0.0.0.0 to bind to all interfaces. Leave hostname empty to bind to default interface. Examples: `PLAINTEXT://myhost:9092,SSL://:9091`, `CLIENT://0.0.0.0:9092,REPLICATION://localhost:9093` | list | `PLAINTEXT://:9092` | high | per-broker |
| `listener.security.protocol.map` | Map between listener names and security protocols. This must be defined for the same security protocol to be usable in more than one port or IP. Keys and values are separated by a colon and map entries are separated by commas. Each listener name should only appear once in the map. Different security (SSL and SASL) settings can be configured for each listener by adding a normalised prefix (the listener name is lowercased) to the config name, e.g. `listener.name.internal.ssl.keystore.location`. | string | `SASL_SSL:SASL_SSL,SASL_PLAINTEXT:SASL_PLAINTEXT,SSL:SSL,PLAINTEXT:PLAINTEXT,CONTROLLER:PLAINTEXT` | low | per-broker |
| `inter.broker.listener.name` | Name of listener used for communication between brokers. If this is unset, the listener name is defined by `security.inter.broker.protocol`. It is an error to set this and `security.inter.broker.protocol` properties at the same time. | string | null | medium | read-only |
| `controller.listener.names` | A comma-separated list of the names of the listeners used by the controller. This is required when communicating with the controller quorum; the broker will use the first listener in the list. | list | null | high | read-only |
| `controller.quorum.voters` | Map of id/endpoint information for the set of voters in a comma-separated list of `{id}@{host}:{port}` entries. For example: `1@localhost:9092,2@localhost:9093,3@localhost:9094` | list | "" | high | read-only |
| `controller.quorum.bootstrap.servers` | List of endpoints to use for bootstrapping the cluster metadata. The endpoints are specified in comma-separated list of `{host}:{port}` entries. For example: `localhost:9092,localhost:9093,localhost:9094`. | list | "" | high | read-only |
| `process.roles` | The roles that this process plays: `broker`, `controller`, or `broker,controller` if it is both. | list | "" (must be set) | high | read-only |
| `node.id` | The node ID associated with the roles this process is playing when `process.roles` is non-empty. This is required configuration when running in KRaft mode. | int | -1 (must be set) | high | read-only |
| `log.dirs` | A comma-separated list of the directories where the log data is stored. If not set, the value in `log.dir` is used. | list | null | high | read-only |
| `num.partitions` | The default number of log partitions per topic | int | 1 | medium | read-only |
| `default.replication.factor` | The default replication factors for automatically created topics. | int | 1 | medium | read-only |
| `min.insync.replicas` | When a producer sets acks to "all" (or "-1"), `min.insync.replicas` specifies the minimum number of replicas that must acknowledge a write for the write to be considered successful. If this minimum cannot be met, then the producer will raise an exception (either `NotEnoughReplicas` or `NotEnoughReplicasAfterAppend`). When used together, `min.insync.replicas` and acks allow you to enforce greater durability guarantees. A typical scenario would be to create a topic with a replication factor of 3, set `min.insync.replicas` to 2, and produce with acks of "all". | int | 1 | high | cluster-wide |
| `auto.create.topics.enable` | Enable auto creation of topic on the server. | boolean | true | high | read-only |
| `log.segment.bytes` | The maximum size of a single log file | int | 1073741824 (1 gibibyte) | high | cluster-wide |
| `log.roll.hours` | The maximum time before a new log segment is rolled out (in hours), secondary to `log.roll.ms` property | int | 168 | high | read-only |
| `log.retention.hours` | The number of hours to keep a log file before deleting it (in hours), tertiary to `log.retention.ms` property | int | 168 | high | read-only |
| `log.retention.bytes` | The maximum size of the log before deleting it | long | -1 | high | cluster-wide |
| `log.retention.check.interval.ms` | The frequency in milliseconds that the log cleaner checks whether any log is eligible for deletion | long | 300000 (5 minutes) | medium | read-only |
| `log.index.interval.bytes` | The interval with which we add an entry to the offset index. | int | 4096 (4 kibibytes) | medium | cluster-wide |
| `log.message.timestamp.type` | Define whether the timestamp in the message is message create time or log append time. The value should be either `CreateTime` or `LogAppendTime`. | string | CreateTime | medium | cluster-wide |
| `message.max.bytes` | The largest record batch size allowed by Kafka (after compression if compression is enabled). If this is increased and there are consumers older than 0.10.2, the consumers' fetch size must also be increased so that they can fetch record batches this large. This can be set per topic with the topic level `max.message.bytes` config. | int | 1048588 | high | cluster-wide |
| `replica.lag.time.max.ms` | If a follower hasn't sent any fetch requests or hasn't consumed up to the leader's log end offset for at least this time, the leader will remove the follower from ISR | long | 30000 (30 seconds) | high | read-only |
| `unclean.leader.election.enable` | Indicates whether to enable replicas not in the ISR set to be elected as leader as a last resort, even though doing so may result in data loss | boolean | false | high | cluster-wide |
| `auto.leader.rebalance.enable` | Enables auto leader balancing. A background thread checks the distribution of partition leaders at regular intervals, configurable by `leader.imbalance.check.interval.seconds`. If the leader imbalance exceeds `leader.imbalance.per.broker.percentage`, leader rebalance to the preferred leader for partitions is triggered. | boolean | true | high | read-only |
| `leader.imbalance.check.interval.seconds` | The frequency with which the partition rebalance check is triggered by the controller | long | 300 | high | read-only |
| `num.io.threads` | The number of threads that the server uses for processing requests, which may include disk I/O | int | 8 | high | cluster-wide |
| `num.recovery.threads.per.data.dir` | The number of threads per data directory to be used for log recovery at startup and flushing at shutdown | int | 2 | high | cluster-wide |
| `offsets.topic.num.partitions` | The number of partitions for the offset commit topic (should not change after deployment) | int | 50 | high | read-only |
| `group.initial.rebalance.delay.ms` | The amount of time the group coordinator will wait for more consumers to join a new group before performing the first rebalance. A longer delay means potentially fewer rebalances, but increases the time until processing begins. | int | 3000 (3 seconds) | medium | read-only |

---

### Listener Configuration (Security → 7.2)

In order to secure a Kafka cluster, it is necessary to secure the channels that are used to communicate with the servers. Each server must define the set of listeners that are used to receive requests from clients as well as other servers. Each listener may be configured to authenticate clients using various mechanisms and to ensure traffic between the server and the client is encrypted.

Kafka servers support listening for connections on multiple ports. This is configured through the **`listeners`** property in the server configuration, which accepts a comma-separated list of the listeners to enable. At least one listener must be defined on each server. The format of each listener defined in `listeners` is given below:

```
{LISTENER_NAME}://{hostname}:{port}
```

The `LISTENER_NAME` is usually a descriptive name which defines the purpose of the listener. For example, many configurations use a separate listener for client traffic, so they might refer to the corresponding listener as `CLIENT` in the configuration:

```
listeners=CLIENT://localhost:9092
```

The security protocol of each listener is defined in a separate configuration: **`listener.security.protocol.map`**. The value is a comma-separated list of each listener mapped to its security protocol. For example, the follow value configuration specifies that the `CLIENT` listener will use SSL while the `BROKER` listener will use plaintext.

```
listener.security.protocol.map=CLIENT:SSL,BROKER:PLAINTEXT
```

Possible options (case-insensitive) for the security protocol are: **`PLAINTEXT`, `SSL`, `SASL_PLAINTEXT`, `SASL_SSL`**.

Once each listener has been configured with its security protocol, the listener security protocol settings depend on the mechanism chosen. If the listener name is itself one of the security protocols, the mapping is inferred automatically.

**Inter-broker listener.** In KRaft mode, `inter.broker.listener.name` (or, if unset, the listener corresponding to `security.inter.broker.protocol`, which defaults to `PLAINTEXT`) is used for communication between brokers. It is an error to set both. **Controllers receive requests both from other controllers and from brokers**, so a KRaft controller must have a listener defined with **`controller.listener.names`**; the controller listener must not be the same as the inter-broker listener. Brokers use the first entry in `controller.listener.names` to talk to the quorum.

Example configuration for a **broker-only** node in a cluster that uses SSL for clients and inter-broker traffic and a separate controller listener:

```
process.roles=broker
listeners=BROKER://localhost:9092
inter.broker.listener.name=BROKER
controller.quorum.bootstrap.servers=localhost:9093
controller.listener.names=CONTROLLER
listener.security.protocol.map=BROKER:SASL_SSL,CONTROLLER:SASL_SSL
```

Example for a **combined** (broker + controller) node:

```
process.roles=broker,controller
listeners=BROKER://localhost:9092,CONTROLLER://localhost:9093
inter.broker.listener.name=BROKER
controller.quorum.bootstrap.servers=localhost:9093
controller.listener.names=CONTROLLER
listener.security.protocol.map=BROKER:SASL_SSL,CONTROLLER:SASL_SSL
```

---

### Kafka Listeners — Explained (Confluent blog, Robin Moffatt) — the Docker trap

**How Kafka clients connect.** When a client starts it (1) connects to a bootstrap broker using the address given in `bootstrap.servers`, (2) sends a metadata request and receives cluster metadata that includes the **advertised host and port for each broker**, and (3) connects directly to the brokers using those advertised addresses — not necessarily the bootstrap address. "Even if you can make the initial connection to the broker, the address returned in the metadata may still be for a hostname that is not accessible from your client."

**The four settings:**

- `listeners` (`KAFKA_LISTENERS`): what interfaces/ports Kafka binds to.
- `advertised.listeners` (`KAFKA_ADVERTISED_LISTENERS`): what is returned in metadata to clients — "how clients can connect".
- `listener.security.protocol.map` (`KAFKA_LISTENER_SECURITY_PROTOCOL_MAP`): maps listener names to security protocols.
- `inter.broker.listener.name` (`KAFKA_INTER_BROKER_LISTENER_NAME`): which listener brokers use to talk to each other.

**The Docker problem.** With only an internal listener:

```
KAFKA_LISTENERS: PLAINTEXT://kafka0:9092
KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka0:9092
```

a client on the host connects to `localhost:9092` (port published by Docker), receives `kafka0:9092` in the metadata, cannot resolve `kafka0` on the host network, and times out.

**Multi-listener solution:**

```
KAFKA_LISTENERS: LISTENER_BOB://kafka0:29092,LISTENER_FRED://kafka0:9092
KAFKA_ADVERTISED_LISTENERS: LISTENER_BOB://kafka0:29092,LISTENER_FRED://localhost:9092
KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: LISTENER_BOB:PLAINTEXT,LISTENER_FRED:PLAINTEXT
KAFKA_INTER_BROKER_LISTENER_NAME: LISTENER_BOB
```

Clients connecting on port 29092 (inside the Docker network) get `kafka0:29092` back; clients connecting on 9092 (from the host) get `localhost:9092` back. The same pattern applies to cloud VMs with split internal/external DNS:

```
listeners=INTERNAL://0.0.0.0:19092,EXTERNAL://0.0.0.0:9092
listener.security.protocol.map=INTERNAL:PLAINTEXT,EXTERNAL:PLAINTEXT
advertised.listeners=INTERNAL://ip-172-31-18-160.us-west-2.compute.internal:19092,EXTERNAL://ec2-54-191-84-122.us-west-2.compute.amazonaws.com:9092
inter.broker.listener.name=INTERNAL
```

**Debugging.** `kafkacat -b kafka0:9092 -L` prints the metadata the broker returns (`broker 0 at localhost:9092`) — if you see a hostname that is not resolvable from where the client runs, `advertised.listeners` is wrong. Typical error: `Local: Host resolution failure: ip-172-31-18-160.us-west-2.compute.internal:9092`.
