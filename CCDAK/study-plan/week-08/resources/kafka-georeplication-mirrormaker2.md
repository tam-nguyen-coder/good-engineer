# Apache Kafka — Geo-Replication (Cross-Cluster Data Mirroring) với MirrorMaker 2

> **Nguồn (official):** https://kafka.apache.org/43/operations/geo-replication-cross-cluster-data-mirroring/ (mục 6.3 Geo-Replication) · tham chiếu KIP-382: MirrorMaker 2.0
> **Tuần:** 8 — Observability & Operations · **Loại:** Apache Kafka Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua HTTP + chuyển HTML → Markdown, có rút gọn) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- **MirrorMaker 2 (MM2)** xây trên **Kafka Connect**; MM1 đã bị **xoá ở Kafka 4.0**. Replicate **topic (data + config)**, **consumer group + offset**, **ACL**, **giữ nguyên partitioning**, tự phát hiện topic/partition mới, có metric latency end-to-end.
- Ba connector: **`MirrorSourceConnector`** (copy record + config topic + ACL), **`MirrorCheckpointConnector`** (dịch offset consumer group → topic `<source>.checkpoints.internal`), **`MirrorHeartbeatConnector`** (topic `heartbeats` để đo liveness/latency).
- Replication flow định nghĩa dạng `{source}->{target}`: `clusters = A, B` + `A.bootstrap.servers` + **`A->B.enabled = true`** (mặc định flow **không** bật). Pattern: active/active `A->B, B->A`; active/passive `A->B`; aggregation `A->K, B->K`; fan-out `K->A, K->B`; forwarding `A->B, B->C`.
- **`DefaultReplicationPolicy`** đổi tên topic đích thành **`{source}.{topic}`** (`us-west.foo-topic`) để chống loop và tránh ghi chung partition; separator đổi qua `replication.policy.separator`. **`IdentityReplicationPolicy`** giữ nguyên tên (dùng cho migration/active-passive; đề cũ hay gọi "legacy MM1 behavior") — không chống loop, không dùng cho active/active.
- Mặc định `topics = .*`, `groups = .*`; `groups.exclude = console-consumer-.*, connect-.*, __.*` → console consumer **không** được replicate group.
- Offset translation: `MirrorCheckpointConnector` + `sync.group.offsets.enabled=true` tự ghi offset đã dịch vào `__consumer_offsets` đích (khi group ở đích **inactive**); client dùng `RemoteClusterUtils.translateOffsets()` / `MirrorClient` để seek khi failover.
- Exactly-once (3.5+): `{target}.exactly.once.source.support = enabled` + `dedicated.mode.enable.internal.rest = true` (nâng cấp cluster cũ qua bước `preparing`); nên đặt `{source}.consumer.isolation.level = read_committed`.
- Best practice **"consume from remote, produce to local"**: chạy MM2 gần cluster **đích**, dùng `--clusters <target>`; producer chịu latency kém hơn consumer. Khởi động: `bin/connect-mirror-maker.sh connect-mirror-maker.properties [--clusters us-west]`. Đổi config phải **restart**; các process cùng target chia sẻ config → cấu hình lệch nhau gây **race** (chỉ 1 bên thắng).
- Metric MM2 nhóm `kafka.connect.mirror`: `MirrorSourceConnector` → `record-count`, `record-rate`, `record-age-ms`, **`replication-latency-ms`**, `byte-rate`; `MirrorCheckpointConnector` → **`checkpoint-latency-ms`**.

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Geo-Replication Overview

Kafka administrators can define data flows that cross the boundaries of individual Kafka clusters, data centers, or geo-regions. Common scenarios include: Geo-replication; Disaster recovery; Feeding edge clusters into a central, aggregate cluster; Physical isolation of clusters (such as production vs. testing); Cloud migration or hybrid cloud deployments; Legal and compliance requirements.

Administrators can set up such inter-cluster data flows with Kafka's MirrorMaker (version 2), a tool to replicate data between different Kafka environments in a streaming manner. MirrorMaker is built on top of the Kafka Connect framework and supports features such as:

- Replicates topics (data plus configurations)
- Replicates consumer groups including offsets to migrate applications between clusters
- Replicates ACLs
- Preserves partitioning
- Automatically detects new topics and partitions
- Provides a wide range of metrics, such as end-to-end replication latency across multiple data centers/clusters
- Fault-tolerant and horizontally scalable operations

Note: Geo-replication with MirrorMaker replicates data across Kafka clusters. This inter-cluster replication is different from Kafka's intra-cluster replication, which replicates data within the same Kafka cluster.

### What Are Replication Flows

With MirrorMaker, Kafka administrators can replicate topics, topic configurations, consumer groups and their offsets, and ACLs from one or more source Kafka clusters to one or more target Kafka clusters. In a nutshell, MirrorMaker uses Connectors to consume from source clusters and produce to target clusters.

These directional flows from source to target clusters are called replication flows. They are defined with the format `{source_cluster}->{target_cluster}` in the MirrorMaker configuration file. Example patterns:

- Active/Active high availability deployments: `A->B, B->A`
- Active/Passive or Active/Standby high availability deployments: `A->B`
- Aggregation (e.g., from many clusters to one): `A->K, B->K, C->K`
- Fan-out (e.g., from one to many clusters): `K->A, K->B, K->C`
- Forwarding: `A->B, B->C, C->D`

By default, a flow replicates all topics and consumer groups (except excluded ones). Here is a first example on how to configure data replication from a `primary` cluster to a `secondary` cluster (an active/passive setup):

```
# Basic settings
clusters = primary, secondary
primary.bootstrap.servers = broker3-primary:9092
secondary.bootstrap.servers = broker5-secondary:9092

# Define replication flows
primary->secondary.enabled = true
primary->secondary.topics = foobar-topic, quux-.*
```

### Configuring Geo-Replication

The following sections describe how to configure and run a dedicated MirrorMaker cluster. If you want to run MirrorMaker within an existing Kafka Connect cluster or other supported deployment setups, please refer to KIP-382: MirrorMaker 2.0 and be aware that the names of configuration settings may vary between deployment modes.

The MirrorMaker configuration file is typically named `connect-mirror-maker.properties`. You can configure a variety of components in this file: MirrorMaker settings (global, per replication flow), Kafka Connect and connector settings, Kafka producer/consumer/admin client settings.

#### Exactly once

Exactly-once semantics are supported for dedicated MirrorMaker clusters as of version 3.5.0. For new MirrorMaker clusters, set the `exactly.once.source.support` property to enabled for all targeted Kafka clusters that should be written to with exactly-once semantics:

```
us-east.exactly.once.source.support = enabled
```

For existing MirrorMaker clusters, a two-step upgrade is necessary. Instead of immediately setting the property to enabled, first set it to `preparing` on all nodes in the cluster. Once this is complete, it can be set to `enabled` on all nodes, in a second round of restarts.

In either case, it is also necessary to enable intra-cluster communication between the MirrorMaker nodes, as described in KIP-710. To do this, the `dedicated.mode.enable.internal.rest` property must be set to `true`:

```
dedicated.mode.enable.internal.rest = true
listeners = http://localhost:8080
```

It is also recommended to filter records from aborted transactions out from replicated data when running MirrorMaker. To do this, ensure that the consumer used to read from source clusters is configured with `isolation.level` set to `read_committed`:

```
us-west.consumer.isolation.level = read_committed
```

#### Creating and Enabling Replication Flows

- `clusters` (required): comma-separated list of Kafka cluster "aliases"
- `{clusterAlias}.bootstrap.servers` (required): connection information for the specific cluster; comma-separated list of "bootstrap" Kafka brokers

```
clusters = primary, secondary
primary.bootstrap.servers = broker10-primary:9092,broker-11-primary:9092
secondary.bootstrap.servers = broker5-secondary:9092,broker6-secondary:9092
```

Secondly, you must explicitly enable individual replication flows with `{source}->{target}.enabled = true` as needed. Remember that flows are directional: if you need two-way (bidirectional) replication, you must enable flows in both directions.

```
# Enable replication from primary to secondary
primary->secondary.enabled = true
```

By default, a replication flow will replicate all but a few special topics and consumer groups from the source cluster to the target cluster, and automatically detect any newly created topics and groups. The names of replicated topics in the target cluster will be prefixed with the name of the source cluster. For example, the topic `foo` in the source cluster `us-west` would be replicated to a topic named `us-west.foo` in the target cluster `us-east`.

#### Configuring Replication Flows

The configuration of a replication flow is a combination of top-level default settings (e.g., `topics`), on top of which flow-specific settings, if any, are applied (e.g., `us-west->us-east.topics`). The most important settings are:

- `topics`: list of topics or a regular expression that defines which topics in the source cluster to replicate (default: `topics = .*`)
- `topics.exclude`: topics to exclude; takes precedence over `topics` (default: `topics.exclude = .*[\-\.]internal, .*\.replica, __.*`)
- `groups`: list of consumer groups or a regular expression to replicate (default: `groups = .*`)
- `groups.exclude`: consumer groups to exclude (default: `groups.exclude = console-consumer-.*, connect-.*, __.*`)
- `{source}->{target}.enable`: set to `true` to enable the replication flow (default: `false`)

#### Custom Naming of Replicated Topics in Target Clusters

Replicated topics in a target cluster—sometimes called remote topics—are renamed according to a replication policy. MirrorMaker uses this policy to ensure that events (aka records, messages) from different clusters are not written to the same topic-partition. By default as per DefaultReplicationPolicy, the names of replicated topics in the target clusters have the format `{source}.{source_topic_name}`:

```
us-west         us-east
=========       =================
                bar-topic
foo-topic  -->  us-west.foo-topic
```

You can customize the separator (default: `.`) with the `replication.policy.separator` setting:

```
# Defining a custom separator
us-west->us-east.replication.policy.separator = _
```

If you need further control over how replicated topics are named, you can implement a custom `ReplicationPolicy` and override `replication.policy.class` (default is `DefaultReplicationPolicy`) in the MirrorMaker configuration.

#### Preventing Configuration Conflicts

MirrorMaker processes share configuration via their target Kafka clusters. This behavior may cause conflicts when configurations differ among MirrorMaker processes that operate against the same target cluster. For example, two processes with `A->B.topics = foo` and `A->B.topics = bar` will share configuration via cluster `B`, which causes a conflict. Depending on which of the two processes is the elected "leader", the result will be that either the topic `foo` or the topic `bar` is replicated, but not both. It is therefore important to keep the MirrorMaker configuration consistent across replication flows to the same target cluster.

#### Best Practice: Consume from Remote, Produce to Local

To minimize latency ("producer lag"), it is recommended to locate MirrorMaker processes as close as possible to their target clusters, i.e., the clusters that it produces data to. That's because Kafka producers typically struggle more with unreliable or high-latency network connections than Kafka consumers.

```
First DC          Second DC
==========        =========================
primary --------- MirrorMaker --> secondary
(remote)                           (local)

# Run in secondary's data center, reading from the remote `primary` cluster
$ bin/connect-mirror-maker.sh connect-mirror-maker.properties --clusters secondary
```

The `--clusters secondary` tells the MirrorMaker process that the given cluster(s) are nearby, and prevents it from replicating data or sending configuration to clusters at other, remote locations.

#### Example: Active/Passive High Availability Deployment

```
# Unidirectional flow (one-way) from primary to secondary cluster
primary.bootstrap.servers = broker1-primary:9092
secondary.bootstrap.servers = broker2-secondary:9092
primary->secondary.enabled = true
secondary->primary.enabled = false
primary->secondary.topics = foo.*  # only replicate some topics
```

#### Example: Active/Active High Availability Deployment

```
# Bidirectional flow (two-way) between us-west and us-east clusters
clusters = us-west, us-east
us-west.bootstrap.servers = broker1-west:9092,broker2-west:9092
us-east.bootstrap.servers = broker3-east:9092,broker4-east:9092
us-west->us-east.enabled = true
us-east->us-west.enabled = true
```

Note on preventing replication "loops" (where topics will be originally replicated from A to B, then the replicated topics will be replicated yet again from B to A, and so forth): As long as you define the above flows in the same MirrorMaker configuration file, you do not need to explicitly add `topics.exclude` settings to prevent replication loops between the two clusters.

### Starting Geo-Replication

Because MirrorMaker is based on Kafka Connect, MirrorMaker processes that are configured to replicate the same Kafka clusters run in a distributed setup: They will find each other, share configuration, load balance their work, and so on. To increase the throughput of replication flows, one option is to run additional MirrorMaker processes in parallel.

```
$ bin/connect-mirror-maker.sh connect-mirror-maker.properties
# Note: The cluster alias us-west must be defined in the configuration file
$ bin/connect-mirror-maker.sh connect-mirror-maker.properties --clusters us-west
```

After startup, it may take a few minutes until a MirrorMaker process first begins to replicate data. Note when testing replication of consumer groups: By default, MirrorMaker does not replicate consumer groups created by the kafka-console-consumer.sh tool (default: `groups.exclude = console-consumer-.*, connect-.*, __.*`).

To make configuration changes take effect, the MirrorMaker process(es) must be restarted. You can stop a running MirrorMaker process by sending a SIGTERM signal (`kill <MirrorMaker pid>`).

### Monitoring Geo-Replication

MirrorMaker is built on the Connect framework and inherits all of Connect's metrics, such `source-record-poll-rate`. In addition, MirrorMaker produces its own metrics under the `kafka.connect.mirror` metric group. Metrics are tagged with `source`, `target`, `topic`, `partition`.

```
# MBean: kafka.connect.mirror:type=MirrorSourceConnector,target=([-.w]+),topic=([-.w]+),partition=([0-9]+)
record-count            # number of records replicated source -> target
record-rate             # average number of records/sec in replicated records
record-age-ms           # age of records when they are replicated
record-age-ms-min / -max / -avg
replication-latency-ms  # time it takes records to propagate source->target
replication-latency-ms-min / -max / -avg
byte-rate               # average number of bytes/sec in replicated records
byte-count              # number of bytes replicated source -> target

# MBean: kafka.connect.mirror:type=MirrorCheckpointConnector,source=([-.w]+),target=([-.w]+),group=([-.w]+),topic=([-.w]+),partition=([0-9]+)
checkpoint-latency-ms   # time it takes to replicate consumer offsets
checkpoint-latency-ms-min / -max / -avg
```
