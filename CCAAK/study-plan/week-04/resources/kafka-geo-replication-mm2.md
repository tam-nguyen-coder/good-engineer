# Apache Kafka — Geo-Replication (Cross-Cluster Mirroring) với MirrorMaker 2

> **Nguồn (official):** https://kafka.apache.org/43/operations/geo-replication-cross-cluster-data-mirroring/ · tham chiếu KIP-382 (MirrorMaker 2.0)
> **Tuần:** 4 — Deployment Architecture · **Loại:** Apache Kafka 4.3 Docs (§6.3 Geo-Replication)
> ⚠️ Nội dung dưới đây được crawl tự động (HTTP → Markdown, có rút gọn) — luôn đối chiếu link gốc để đầy đủ và cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- **MM2 chạy trên Kafka Connect**, không phải một daemon riêng. MM1 đã bị **xoá ở Kafka 4.0** — mọi phương án nhắc `kafka-mirror-maker.sh`/`--whitelist` là sai với 4.x.
- **3 connector**, phải thuộc tên và nhiệm vụ: `MirrorSourceConnector` (copy **record + topic config + ACL**, giữ nguyên partition, tự phát hiện topic/partition mới) · `MirrorCheckpointConnector` (dịch offset consumer group → topic `{source}.checkpoints.internal`) · `MirrorHeartbeatConnector` (topic `heartbeats`, đo liveness và latency).
- **Flow mặc định TẮT.** Khai báo `clusters = A, B` + `A.bootstrap.servers` không đủ; phải có **`A->B.enabled = true`**. Đây là lỗi vận hành số 1 khi dựng MM2 lần đầu.
- **`DefaultReplicationPolicy`** đổi tên topic đích thành **`{source}.{topic}`** (ví dụ `us-west.foo-topic`) để **chống replication loop**; separator đổi bằng `replication.policy.separator` (mặc định `.`). **`IdentityReplicationPolicy`** giữ nguyên tên → chỉ dùng cho **active/passive và migration**, KHÔNG dùng cho active/active.
- Mặc định `topics = .*`, `topics.exclude = .*[\-\.]internal, .*\.replica, __.*`; `groups = .*`, **`groups.exclude = console-consumer-.*, connect-.*, __.*`** → group của console consumer **không** được replicate (bẫy lab: "sao group của tôi không sang cluster đích?").
- **Offset translation**: checkpoint ghi cặp `upstreamOffset`/`downstreamOffset`; `sync.group.offsets.enabled = true` tự ghi thẳng vào `__consumer_offsets` của cluster đích **khi group ở đích đang inactive**. Client cũng dịch được bằng `RemoteClusterUtils.translateOffsets()`. Dịch là **conservative** (không bao giờ vượt) → consumer phải idempotent.
- **Topology** bằng cách ghép flow: active/active `A->B, B->A` · active/passive `A->B` · aggregation `A->K, B->K, C->K` · fan-out `K->A, K->B` · forwarding `A->B, B->C`.
- **Exactly-once từ 3.5.0** cho dedicated MM2: `{target}.exactly.once.source.support = enabled` (cluster cũ nâng qua 2 bước `preparing` → `enabled`) + `dedicated.mode.enable.internal.rest = true` + `listeners`; nên đặt `{source}.consumer.isolation.level = read_committed`.
- **"Consume from remote, produce to local"**: chạy process MM2 **gần cluster đích** và truyền `--clusters <target>`. Lý do: producer chịu latency kém hơn consumer.
- `tasks.max` nên **≥ 2** (thực tế đặt bằng tổng số partition cần copy) — để mặc định 1 thì MM2 chỉ có 1 task và không scale.
- Đổi config MM2 phải **restart**; nhiều process cùng target mà config lệch nhau sẽ **tranh nhau** (race, một bên thắng).
- Metric nhóm **`kafka.connect.mirror`**, tag `source`/`target`/`topic`/`partition`: `record-count`, `record-rate`, `byte-rate`, `record-age-ms`, **`replication-latency-ms`** (MirrorSource) và **`checkpoint-latency-ms`** (MirrorCheckpoint).

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Geo-Replication Overview

Kafka administrators can define data flows that cross the boundaries of individual Kafka clusters, data centers, or geo-regions. Common scenarios include geo-replication, disaster recovery, feeding edge clusters into a central aggregate cluster, physical isolation of clusters (production vs. testing), cloud migration or hybrid cloud deployments, and legal/compliance requirements.

Administrators can set up such inter-cluster data flows with Kafka's MirrorMaker (version 2), a tool to replicate data between different Kafka environments in a streaming manner. MirrorMaker is built on top of the Kafka Connect framework and supports features such as:

- Replicates topics (data plus configurations)
- Replicates consumer groups including offsets to migrate applications between clusters
- Replicates ACLs
- Preserves partitioning
- Automatically detects new topics and partitions
- Provides a wide range of metrics, such as end-to-end replication latency across multiple data centers/clusters
- Fault-tolerant and horizontally scalable operations

Note: Geo-replication with MirrorMaker replicates data **across** Kafka clusters. This inter-cluster replication is different from Kafka's intra-cluster replication, which replicates data **within** the same Kafka cluster.

### What Are Replication Flows

With MirrorMaker, Kafka administrators can replicate topics, topic configurations, consumer groups and their offsets, and ACLs from one or more source Kafka clusters to one or more target Kafka clusters.

These directional flows from source to target clusters are called **replication flows**. They are defined with the format `{source_cluster}->{target_cluster}` in the MirrorMaker configuration file. Example patterns:

- Active/Active high availability deployments: `A->B, B->A`
- Active/Passive or Active/Standby high availability deployments: `A->B`
- Aggregation (e.g., from many clusters to one): `A->K, B->K, C->K`
- Fan-out (e.g., from one to many clusters): `K->A, K->B, K->C`
- Forwarding: `A->B, B->C, C->D`

By default, a flow replicates all topics and consumer groups (except excluded ones). However, each replication flow can be configured independently. For instance, you can define that only specific topics or consumer groups are replicated from the source cluster to the target cluster.

### Configuring Geo-Replication

The following sections describe how to configure and run a dedicated MirrorMaker cluster. The configuration file is typically named `connect-mirror-maker.properties`.

First, define the source and target clusters along with their connection information:

```properties
# Define the clusters and their connection settings
clusters = primary, secondary
primary.bootstrap.servers = broker3-primary:9092
secondary.bootstrap.servers = broker5-secondary:9092

# Enable a replication flow and pick topics
primary->secondary.enabled = true
primary->secondary.topics = foobar-topic, quux-.*
```

Replication flows must be explicitly enabled by setting `{source}->{target}.enabled = true`. If needed, further customize the flow.

**Configuring Kafka Connect and connector settings.** Settings can be applied at three levels, in order of increasing precedence: top-level defaults for all flows; per-flow (`{source}->{target}.`) and per-connector settings; and per-cluster Kafka Connect settings (`{cluster}.`).

```properties
# Kafka Connect settings used by a specific target cluster
us-west.offset.storage.topic = my-mirrormaker-offsets

# Consumer settings used when reading from the source cluster
us-west.consumer.isolation.level = read_committed

# Producer settings used when writing to the target cluster
us-east.producer.compression.type = gzip
us-east.producer.buffer.memory = 32768
```

**Configuring which topics and groups are replicated.** By default, all topics and consumer groups are replicated except for an exclusion list.

| Setting | Default |
|---|---|
| `topics` | `.*` |
| `topics.exclude` | `.*[\-\.]internal, .*\.replica, __.*` |
| `groups` | `.*` |
| `groups.exclude` | `console-consumer-.*, connect-.*, __.*` |
| `{source}->{target}.enabled` | `false` |

```properties
us-west->us-east.topics = foo.*, bar.*
us-west->us-east.topics.exclude = foo.internal.*
us-west->us-east.groups = group1, group2.*
```

### Topic Naming — Replication Policy

By default, replicated topics are renamed based on the `DefaultReplicationPolicy`: the topic `foo-topic` from cluster `us-west` becomes `us-west.foo-topic` on the target cluster. This prevents replication cycles ("loops") when several flows are active, and makes it clear where a topic's data originated.

The separator can be customized:

```properties
us-west->us-east.replication.policy.separator = _
```

If you need identical topic names on both sides — for example when migrating applications from one cluster to another, or in a strict active/passive setup — use the alternative policy:

```properties
replication.policy.class = org.apache.kafka.connect.mirror.IdentityReplicationPolicy
```

### Consumer Offset Translation and Checkpoints

`MirrorCheckpointConnector` periodically emits checkpoints containing, for each replicated consumer group, the last committed offset on the source cluster and the corresponding offset on the target cluster. These checkpoints are written to the internal topic `{source}.checkpoints.internal` on the target cluster, and the mapping between source and target offsets is maintained in the `mm2-offset-syncs.{source}.internal` topic.

Setting `sync.group.offsets.enabled = true` lets MirrorMaker write the translated offsets directly into the target cluster's `__consumer_offsets` topic, so that a consumer group failing over to the target cluster resumes from approximately the right position. Offsets are only written while the group is **not active** on the target cluster.

Applications can also translate offsets themselves with `RemoteClusterUtils.translateOffsets()` from the `connect-mirror-client` library.

### Exactly-Once Semantics

Exactly-once semantics are supported for dedicated MirrorMaker clusters as of version 3.5.0. For new MirrorMaker clusters, set the `exactly.once.source.support` property to `enabled` for all targets:

```properties
us-east.exactly.once.source.support = enabled
```

For existing MirrorMaker clusters, a two-step upgrade is necessary: first set to `preparing` on all nodes, then set to `enabled`.

It is also necessary to enable intra-cluster communication between the MirrorMaker nodes:

```properties
dedicated.mode.enable.internal.rest = true
listeners = http://localhost:8080
```

In order to avoid reading records that may be aborted, it is recommended to configure the consumer:

```properties
us-west.consumer.isolation.level = read_committed
```

### Starting Geo-Replication

Start a MirrorMaker node with:

```bash
$ bin/connect-mirror-maker.sh connect-mirror-maker.properties
```

After startup, it may take a few minutes until a MirrorMaker node first starts to replicate data. Optionally, `--clusters` can be used to make a node process only a subset of the replication flows:

```bash
$ bin/connect-mirror-maker.sh connect-mirror-maker.properties --clusters us-west
```

This implements the best practice of "consume from remote, produce to local": run the MirrorMaker processes close to their target cluster, because a producer suffers more from high latency than a consumer does.

### Monitoring Geo-Replication

MirrorMaker emits metrics in the `kafka.connect.mirror` metric group. Metrics are tagged with the following properties: `source` (alias of the source cluster), `target` (alias of the target cluster), `topic` (replicated topic on the target cluster), `partition` (partition being replicated).

Metrics are tracked for each replicated topic; the source cluster can be inferred from the topic name. Key metrics include:

```
# MBean: kafka.connect.mirror:type=MirrorSourceConnector,target=([-.\w]+),topic=([-.\w]+),partition=([0-9]+)
record-count            # number of records replicated source -> target
record-age-ms           # age of records when they were replicated
record-age-ms-min / -max / -avg
replication-latency-ms  # time it takes records to propagate source -> target
byte-rate               # average number of bytes/second in replicated records

# MBean: kafka.connect.mirror:type=MirrorCheckpointConnector,source=([-.\w]+),target=([-.\w]+)
checkpoint-latency-ms   # time it takes to replicate consumer offsets
```

### Production Considerations

- Ensure `tasks.max` is set to at least 2 (preferably higher) so that the replication workload can be distributed across the MirrorMaker nodes.
- Configuration changes require a restart of the MirrorMaker processes.
- All MirrorMaker processes that write to the same target cluster share configuration; inconsistent settings between processes cause a race in which only one configuration wins.
- Security settings follow the standard Kafka Connect format (`{cluster}.security.protocol`, `{cluster}.sasl.*`, `{cluster}.ssl.*`).
