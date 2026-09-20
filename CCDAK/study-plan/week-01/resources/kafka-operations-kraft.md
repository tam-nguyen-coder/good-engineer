# Apache Kafka — Operations: KRaft (process roles, quorum, storage tool, metadata tools) + KRaft vs ZooKeeper + ELR

> **Nguồn (official):** https://kafka.apache.org/43/operations/kraft/ · https://kafka.apache.org/43/getting-started/zk2kraft/ · https://kafka.apache.org/43/operations/eligible-leader-replicas/
> **Tuần:** 1 — Kiến trúc Kafka & `KRaft` + Dựng cluster + CLI · **Loại:** Apache Kafka Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- `process.roles` = **`broker`** | **`controller`** | **`broker,controller`** (combined). Combined "simpler to operate for small use cases like a development environment" nhưng **"not recommended in critical deployment environments"** → production **tách riêng**.
- Quorum controller chọn **3 hoặc 5** node: 3 controller chịu **1** lỗi, 5 controller chịu **2** lỗi; tổng quát **2N+1** controller chịu N lỗi. Mọi node (kể cả broker-only) phải biết đường tới quorum.
- **Static quorum**: `controller.quorum.voters=id@host:port,...` (mọi node khai đủ id). **Dynamic quorum** (KRaft version **1+**, KIP-853): `controller.quorum.bootstrap.servers=host:port,...` — chỉ cần địa chỉ; đổi thành viên online. Kiểm tra loại quorum: `kafka-features.sh --bootstrap-controller localhost:9093 describe` → `kraft.version`.
- **Storage tool**: `kafka-storage.sh random-uuid` sinh `cluster.id`; `format --cluster-id <ID> --standalone` (controller đầu tiên là voter duy nhất); `format --initial-controllers "id@host:port:dirUUID,..."` (format đồng loạt nhiều controller); `format --no-initial-controllers` (broker / controller vào sau, join quorum sẵn có). Broker **không start** nếu chưa format.
- Đổi thành viên online: `kafka-metadata-quorum.sh --bootstrap-server ... add-controller` (sau khi controller mới đã catch up), `remove-controller --controller-id <id> --controller-directory-id <uuid>` **trước** khi tắt máy.
- 3 tool debug KRaft: `kafka-metadata-quorum.sh describe --status` (LeaderId, HighWatermark, voters/observers); `kafka-dump-log.sh --cluster-metadata-decoder --files .../__cluster_metadata-0/00000000000000000000.log`; `kafka-metadata-shell.sh --snapshot .../__cluster_metadata-0/<offset>-<epoch>.checkpoint`.
- Tài nguyên khuyến nghị cho controller: ~**5 GB RAM** và **5 GB đĩa** cho metadata log directory.
- Migration ZK → KRaft **phải qua bridge release**; "The last bridge release is **Kafka 3.9**". Kafka 4.x **không** còn ZooKeeper mode.
- Config bị **gỡ** trong KRaft: `zookeeper.connect`, `zookeeper.session.timeout.ms`, `broker.id.generation.enable`/`reserved.broker.max.id` (thay bằng `node.id`), `inter.broker.protocol.version` (thay bằng `metadata.version` qua `kafka-features.sh`), `control.plane.listener.name` (thay bằng `controller.listener.names`), `controlled.shutdown.max.retries`, `password.encoder.*`.
- **ELR (Eligible Leader Replicas, KIP-966)**: tập replica **ngoài ISR nhưng vẫn an toàn làm leader** vì HW không thể tiến khi ISR < min.isr. Thứ tự bầu leader: **ISR → ELR (unfenced) → last known leader**. Feature `eligible.leader.replicas.version`: 0 = tắt (mặc định 4.0), 1 = bật; **bật mặc định cho cluster mới từ 4.1**. Khi bật, không được xoá `min.insync.replicas` cấp cluster; `min.insync.replicas` cấp broker bị deprecated.

---

## 📄 Nội dung (trích từ tài liệu gốc)

### KRaft — Configuration

#### Process Roles

In KRaft mode each Kafka server can be configured as a controller, a broker, or both using the `process.roles` property. This property can have the following values:

- If `process.roles` is set to `broker`, the server acts as a broker.
- If `process.roles` is set to `controller`, the server acts as a controller.
- If `process.roles` is set to `broker,controller`, the server acts as both a broker and a controller.

Kafka servers that act as both brokers and controllers are referred to as **"combined" servers**. Combined servers are simpler to operate for small use cases like a development environment. The key disadvantage is that the controller will be less isolated from the rest of the system. For example, it is not possible to roll or scale the controllers separately from the brokers in combined mode. **Combined mode is not recommended in critical deployment environments.**

#### Controllers

In KRaft mode, specific Kafka servers are selected to be controllers. The servers selected to be controllers will participate in the metadata quorum. Each controller is either an active or a hot standby for the current active controller.

A Kafka admin will typically select **3 or 5 servers** for this role, depending on factors like cost and the number of concurrent failures your system should withstand without availability impact. A majority of the controllers must be alive in order to maintain availability. **With 3 controllers, the cluster can tolerate 1 controller failure; with 5 controllers, the cluster can tolerate 2 controller failures.**

All of the servers in a Kafka cluster discover the active controller using the `controller.quorum.bootstrap.servers` property. All the controllers should be enumerated in this property. Each controller is identified with their `host` and `port` information. For example:

```
controller.quorum.bootstrap.servers=host1:port1,host2:port2,host3:port3
```

If a Kafka cluster has 3 controllers named controller1, controller2 and controller3, then controller1 may have the following configuration:

```
process.roles=controller
node.id=1
listeners=CONTROLLER://controller1.example.com:9093
controller.quorum.bootstrap.servers=controller1.example.com:9093,controller2.example.com:9093,controller3.example.com:9093
controller.listener.names=CONTROLLER
```

Every broker and controller must set the `controller.quorum.bootstrap.servers` property.

#### Static versus Dynamic KRaft Quorums

There are two ways to run KRaft: the old way using **static controller quorums**, and the new way using **KIP-853 dynamic controller quorums**.

When using a static quorum, the configuration file for each broker and controller must specify the IDs, hostnames, and ports of all controllers in **`controller.quorum.voters`**. In contrast, when using a dynamic quorum, you should set **`controller.quorum.bootstrap.servers`** instead. This configuration key need not contain all the controllers, but it should contain as many as possible so that all the servers can locate the quorum. In other words, its function is much like the `bootstrap.servers` configuration used by Kafka clients.

If you are not sure whether you are using static or dynamic quorums, you can determine this by running something like the following:

```bash
$ bin/kafka-features.sh --bootstrap-controller localhost:9093 describe
```

If the `kraft.version` field is level 0 or absent, you are using a static quorum. If it is 1 or above, you are using a dynamic quorum. Note that static quorums are **deprecated**; new clusters should always use dynamic quorums.

#### Provisioning Nodes

The `bin/kafka-storage.sh random-uuid` command can be used to generate a cluster ID for your new cluster. This cluster ID must be used by all the servers in the cluster.

Before starting a node, you must format its storage directory. This is because Kafka nodes must be formatted before they can start, and the format command validates configuration such as the cluster ID and node ID. If `process.roles` includes `controller`, the node must also know whether it is part of the initial quorum:

**Bootstrap a Standalone Controller** — the recommended method for creating a new KRaft controller cluster is to bootstrap it with one voter and dynamically add the rest of the controllers:

```bash
$ bin/kafka-storage.sh format --cluster-id <ID> --standalone --config config/controller.properties
```

**Bootstrap with Multiple Controllers** — the KRaft cluster metadata partition can also be bootstrapped with more than one voter. This can be done by using the `--initial-controllers` flag:

```bash
$ CLUSTER_ID="$(bin/kafka-storage.sh random-uuid)"
$ CONTROLLER_0_UUID="$(bin/kafka-storage.sh random-uuid)"
$ CONTROLLER_1_UUID="$(bin/kafka-storage.sh random-uuid)"
$ CONTROLLER_2_UUID="$(bin/kafka-storage.sh random-uuid)"

# In each controller execute
$ bin/kafka-storage.sh format --cluster-id ${CLUSTER_ID} \
  --initial-controllers "0@controller-0:1234:${CONTROLLER_0_UUID},1@controller-1:1234:${CONTROLLER_1_UUID},2@controller-2:1234:${CONTROLLER_2_UUID}" \
  --config config/controller.properties
```

This command must be executed on each controller with the same set of initial controllers; each entry has the form `{node.id}@{host}:{port}:{directory.id}`.

**Formatting Brokers and New Controllers** — when provisioning new broker and controller nodes that we want to add to an existing Kafka cluster, use the `--no-initial-controllers` flag:

```bash
$ bin/kafka-storage.sh format --cluster-id <ID> --config config/server.properties --no-initial-controllers
```

#### Controller membership changes

**Add New Controller** — if a dynamic controller cluster already exists, it can be expanded by first provisioning a new controller using the `kafka-storage.sh` tool and starting the controller. After starting the controller, the replication to the new controller can be monitored using the `kafka-metadata-quorum.sh describe --replication` command. Once the new controller has caught up to the active controller, it can be added to the cluster:

```bash
$ bin/kafka-metadata-quorum.sh --bootstrap-server localhost:9092 add-controller
```

**Remove Controller** — if the dynamic controller cluster already exists, it can be shrunk. Note that the controller should be removed from the quorum **before** it is shut down:

```bash
$ bin/kafka-metadata-quorum.sh --bootstrap-server localhost:9092 remove-controller --controller-id <id> --controller-directory-id <directory-id>
```

#### Debugging

**Metadata Quorum Tool** — used to describe the runtime state of the cluster metadata partition:

```bash
$ bin/kafka-metadata-quorum.sh --bootstrap-server localhost:9092 describe --status
ClusterId:              fMCL8kv1SWm87L_Md-I2hg
LeaderId:               3002
LeaderEpoch:            2
HighWatermark:          10
MaxFollowerLag:         0
MaxFollowerLagTimeMs:   -1
CurrentVoters:          [{"id": 3000, "directoryId": "ILZ5MPTeRWakmJu99uBJCA", "endpoints": ["CONTROLLER://localhost:9093"]}, ...]
CurrentObservers:       [{"id": 0, "directoryId": "3Db5QLSqSZieL3rJBUUegA"}, ...]
```

**Dump Log Tool** — can be used to debug the log segments and snapshots for the cluster metadata directory. The tool will scan the provided files and decode the metadata records:

```bash
$ bin/kafka-dump-log.sh --cluster-metadata-decoder --files metadata_log_dir/__cluster_metadata-0/00000000000000000000.log
```

**Metadata Shell** — can be used to interactively inspect the state of the cluster metadata partition:

```bash
$ bin/kafka-metadata-shell.sh --snapshot metadata_log_dir/__cluster_metadata-0/00000000000000007228-0000000001.checkpoint
>> ls /
brokers  local  metadataQuorum  topicIds  topics
>> ls /topics
foo
>> cat /topics/foo/0/data
{ "partitionId" : 0, "topicId" : "5zoAlv-xEh9xRANKXt1Lbg", "replicas" : [ 1 ], "isr" : [ 1 ], "removingReplicas" : null, "addingReplicas" : null, "leader" : 1, "leaderEpoch" : 0, "partitionEpoch" : 0 }
>> exit
```

#### Deploying Considerations

- Kafka server's `process.roles` should be set to either `broker` or `controller` but not both. Combined mode can be used in development environments, but it should be avoided in critical deployment environments.
- For redundancy, a Kafka cluster should use 3 or more controllers, depending on factors like cost and the number of concurrent failures your system should withstand without availability impact. For the KRaft controller cluster to withstand N concurrent failures the controller cluster must include **2N + 1** controllers.
- The Kafka controllers store all the metadata for the cluster in memory and on disk. We believe that for a typical Kafka cluster **5GB of main memory and 5GB of disk space** on the metadata log director is sufficient.

#### ZooKeeper to KRaft Migration

In order to migrate from ZooKeeper to KRaft you need to use a bridge release. **The last bridge release is Kafka 3.9.** See the ZooKeeper to KRaft Migration steps in the 3.9 documentation.

---

### KRaft vs ZooKeeper — differences (getting-started/zk2kraft)

**Removed configurations** — in KRaft mode the following are no longer used:

- `zookeeper.connect`, `zookeeper.session.timeout.ms`, `zookeeper.connection.timeout.ms`, `zookeeper.set.acl`, and all `zookeeper.ssl.*` settings.
- `broker.id.generation.enable` and `reserved.broker.max.id` — replaced by **`node.id`** (KRaft does not generate ids).
- `inter.broker.protocol.version` — replaced by **`metadata.version`**, managed with `bin/kafka-features.sh`.
- `control.plane.listener.name` — replaced by `controller.listener.names` together with `listeners` and `listener.security.protocol.map`.
- `controlled.shutdown.max.retries` and `controlled.shutdown.retry.backoff.ms` — controlled shutdown is handled through the broker heartbeat with the controller.
- `password.encoder.secret`, `password.encoder.cipher.algorithm`, `password.encoder.key.length` and other `password.encoder.*` — Kafka stores sensitive data in records, so encryption is not needed.

**Removed features / behavior changes:**

- Dynamic configuration changes for controllers are applied with the `--bootstrap-controller` flag; controllers will apply all applicable cluster-level dynamic configurations.
- `leader.imbalance.per.broker.percentage` is not used in KRaft.
- Policy plugins (`CreateTopicPolicy`, `AlterConfigPolicy`) now run on the **controllers**, so they must be installed on controller nodes.
- Custom `KafkaPrincipalBuilder` implementations must also implement `KafkaPrincipalSerde`.
- ZooKeeper-related metrics (e.g. `ControlPlaneNetworkProcessorAvgIdlePercent` and ZooKeeper controller event/stats metrics) are removed.

---

### Eligible Leader Replicas (ELR, KIP-966)

Starting from Apache Kafka 4.0, the Eligible Leader Replicas feature is available. Kafka replication has a "strict min ISR" rule: **the high watermark for the data partition can't advance if the size of the ISR is smaller than the min ISR**. This means that replicas which were recently removed from the ISR (because the ISR shrank below `min.insync.replicas`) still contain every committed record, so they are safe to become the leader. The KRaft controller stores these replicas in a `PartitionRecord` field called **Eligible Leader Replicas**.

**Leader election order:**

1. If ISR is not empty, select one of them.
2. If ELR is not empty, select one that is not fenced.
3. Select the last known leader if it is unfenced (when all replicas are offline the controller records the last leader; it is elected only if it comes back).

**Enablement:** the feature is controlled with `eligible.leader.replicas.version`. Version 0 = disabled (default for clusters created with 4.0); version 1 = the KRaft controller tracks ELR. ELR is enabled by default on new clusters starting with version 4.1. For upgrades, run the features tool to set `eligible.leader.replicas.version=1`. Downgrade is supported by setting the version back to 0.

**Configuration constraints when ELR is enabled:** the removal of `min.insync.replicas` at the cluster level is not allowed (the controller adds a cluster-level value if it is missing); broker-level `min.insync.replicas` is deprecated and will be removed. Topics and partitions expose `Elr` and `LastKnownElr` in `kafka-topics.sh --describe` output through the `DescribeTopicPartitions` API.
