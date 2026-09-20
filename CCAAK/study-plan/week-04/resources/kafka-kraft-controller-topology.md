# Apache Kafka 4.3 — KRaft: controller topology, quorum sizing, thêm/bớt controller

> **Nguồn (official):** https://kafka.apache.org/43/operations/kraft/
> **Tuần:** 4 — Deployment Architecture · **Loại:** Apache Kafka 4.3 Docs (§6.10 KRaft)
> ⚠️ Nội dung dưới đây được crawl tự động (HTTP → Markdown, có rút gọn) — luôn đối chiếu link gốc để đầy đủ và cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- **`process.roles`** nhận 3 giá trị: `broker`, `controller`, `broker,controller` (combined). Docs nói combined *"are simpler to operate for small use cases like a development environment"* nhưng *"the controller will be less isolated from the rest of the system"* và **"Combined mode is not recommended in critical deployment environments"** → production **tách riêng**.
- **Quorum 3 hoặc 5 controller** (số lẻ). 3 controller chịu mất **1**; 5 controller chịu mất **2**. Công thức docs: để chịu **N** lỗi đồng thời cần **2N + 1** controller. *"A majority of the controllers must be alive in order to maintain availability."*
- **Controller nhẹ hơn broker rất nhiều**: docs gợi ý khoảng **5 GB RAM và 5 GB disk** cho metadata (Confluent deployment guide gợi ý 4 GB RAM + 64 GB SSD). Đừng sizing controller như broker — đó là lãng phí và là bẫy đề.
- Mất **đa số** quorum → **control plane đóng băng** (không tạo topic, không bầu leader mới, không đăng ký broker) nhưng **data plane vẫn phục vụ** produce/fetch cho partition không đổi leader, vì broker dùng metadata đã cache.
- **Static quorum**: `controller.quorum.voters = 1@host1:9093,2@host2:9093,3@host3:9093` — mọi id/host/port cố định trong file config, muốn đổi phải restart cả cụm. **Dynamic quorum (KIP-853)**: `controller.quorum.bootstrap.servers`, thêm/bớt controller lúc chạy.
- Phân biệt bằng feature: `kafka-features.sh --bootstrap-controller localhost:9093 describe` → **`kraft.version` ≥ 1 = dynamic**, `0` = static.
- Format storage: `--standalone` (1 controller đầu tiên) · `--initial-controllers "0@host0:port:uuid,..."` (nhiều controller) · `--no-initial-controllers` (controller thêm vào sau). Mọi node phải dùng **cùng `cluster-id`**, sai → `InconsistentClusterId`.
- Thêm/bớt controller ở dynamic quorum: `kafka-metadata-quorum.sh add-controller` (sau khi node đã format và **bắt kịp** log) và `remove-controller --controller-id <id> --controller-directory-id <dir-id>`.
- Công cụ chẩn đoán: `kafka-metadata-quorum.sh describe --status` (leader, voters, observers, high watermark) · `kafka-dump-log.sh --cluster-metadata-decoder` · `kafka-metadata-shell.sh`.
- Broker là **observer** của metadata log: fetch metadata nhưng **không vote**. Trong output `describe --status`, broker nằm ở `CurrentObservers`, controller ở `CurrentVoters`.
- Đặt controller ở đâu: **rải qua các AZ/rack khác nhau**, không dồn 2 trong 3 controller vào cùng một AZ — mất AZ đó là mất đa số.

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Configuration — Process Roles

In KRaft mode each Kafka server can be configured as a controller, as a broker, or as both using the `process.roles` property. This property can have the following values:

- If `process.roles` is set to `broker`, the server acts as a broker.
- If `process.roles` is set to `controller`, the server acts as a controller.
- If `process.roles` is set to `broker,controller`, the server acts as both a broker and a controller.

Kafka servers that act as both brokers and controllers are referred to as "combined" servers. Combined servers are simpler to operate for small use cases like a development environment. The key disadvantage is that the controller will be less isolated from the rest of the system. For example, it is not possible to roll or scale the controllers separately from the brokers in combined mode. **Combined mode is not recommended in critical deployment environments.**

### Controllers

In KRaft mode, specific Kafka servers are selected to be controllers. The servers selected to be controllers will participate in the metadata quorum. Each controller is either an active or a hot standby for the current active controller.

A Kafka admin will typically select 3 or 5 servers for this role, depending on factors like cost and the number of concurrent failures your system should withstand without availability impact. **A majority of the controllers must be alive in order to maintain availability.** With 3 controllers, the cluster can tolerate 1 controller failure; with 5 controllers, the cluster can tolerate 2 controller failures.

### Provisioning nodes

The `bin/kafka-storage.sh random-uuid` command can be used to generate a cluster ID for your new cluster. This cluster ID must be used when formatting each server in the cluster with the `bin/kafka-storage.sh format` command.

**Bootstrapping a standalone controller.** To bootstrap a cluster with a single initial controller:

```bash
$ bin/kafka-storage.sh format --cluster-id <CLUSTER_ID> --standalone --config controller.properties
```

**Bootstrapping with multiple controllers.** The KRaft cluster metadata partition can also be bootstrapped with more than one voter:

```bash
$ bin/kafka-storage.sh format --cluster-id <CLUSTER_ID> \
    --initial-controllers "0@controller-0:1234:3Db5QLSqSZieL3rJBUUegA,1@controller-1:1234:eq7bOtN9QnOWkgQ2zpXxTw,2@controller-2:1234:MvDxzVmcRsaTz33bUuRU6A" \
    --config controller.properties
```

**Formatting brokers and new controllers.** When provisioning new broker and controller nodes that are to be added to an existing Kafka cluster, use the `--no-initial-controllers` flag:

```bash
$ bin/kafka-storage.sh format --cluster-id <CLUSTER_ID> --config server.properties --no-initial-controllers
```

### Controller membership changes

**Static versus dynamic KRaft quorums.** There are two ways to run KRaft: the old way using static controller quorums, and the new way using KRaft-based dynamic quorums.

When using a static quorum, the configuration file for each broker and controller must specify the IDs, hostnames, and ports of all controllers in `controller.quorum.voters`.

In contrast, when using dynamic quorums, you should set `controller.quorum.bootstrap.servers` instead. This configuration key need not contain all the controllers, just a majority of them, or even a single controller — the rest are discovered dynamically.

To determine which mode a cluster is in, run:

```bash
$ bin/kafka-features.sh --bootstrap-controller localhost:9093 describe
```

If the `kraft.version` field is at level 1 or above, you are using dynamic controller quorums. If it is level 0 or absent, you are using static controller quorums.

**Add a new controller.** If a dynamic controller cluster already exists, it can be expanded by first provisioning a new controller using the `kafka-storage.sh format --no-initial-controllers` command, then starting the controller. After starting the controller, the replication to the new controller can be monitored using `bin/kafka-metadata-quorum.sh describe --replication`. Once the new controller has caught up to the active controller, it can be added to the cluster:

```bash
$ bin/kafka-metadata-quorum.sh --bootstrap-server localhost:9092 add-controller
```

**Remove a controller.** If the dynamic controller cluster already exists, it can be shrunk using the `bin/kafka-metadata-quorum.sh remove-controller` command. Until KIP-996 (pre-vote) has been implemented, it is recommended to shutdown the controller that will be removed before running this command:

```bash
$ bin/kafka-metadata-quorum.sh --bootstrap-server localhost:9092 remove-controller \
    --controller-id <id> --controller-directory-id <directory-id>
```

### Debugging

**Metadata quorum tool.** The `kafka-metadata-quorum` tool can be used to describe the runtime state of the cluster metadata partition:

```bash
$ bin/kafka-metadata-quorum.sh --bootstrap-server broker_host:port describe --status
ClusterId:              fMCL8kv1SWm87L_Md-I2hg
LeaderId:               3002
LeaderEpoch:            2
HighWatermark:          10
MaxFollowerLag:         0
MaxFollowerLagTimeMs:   -1
CurrentVoters:          [{"id": 3000, ...}, {"id": 3001, ...}, {"id": 3002, ...}]
CurrentObservers:       [{"id": 0, ...}, {"id": 1, ...}, {"id": 2, ...}]
```

```bash
$ bin/kafka-metadata-quorum.sh --bootstrap-server broker_host:port describe --replication
NodeId  DirectoryId  LogEndOffset  Lag  LastFetchTimestamp  LastCaughtUpTimestamp  Status
3000    ...          234           0    1670104416757       1670104416757          Leader
...
```

**Dump log tool.** The `kafka-dump-log` tool can be used to debug the log segments and snapshots for the cluster metadata directory:

```bash
$ bin/kafka-dump-log.sh --cluster-metadata-decoder --files metadata_log_dir/__cluster_metadata-0/*.log
```

**Metadata shell.** The `kafka-metadata-shell` tool can be used to interactively inspect the state of the cluster metadata:

```bash
$ bin/kafka-metadata-shell.sh --snapshot metadata_log_dir/__cluster_metadata-0/00000000000000000000.checkpoint
```

### Deployment considerations

- Kafka server's `process.roles` should be set to either `broker` or `controller` but not both. Combined mode can be used in development environments, but it should be avoided in critical deployment environments.
- For redundancy, a Kafka cluster should use 3 or more controllers, depending on factors like cost and the number of concurrent failures your system should withstand without availability impact. For the KRaft controller cluster to withstand N concurrent failures the controller cluster must include **2N + 1** controllers.
- The Kafka controllers store all the metadata for the cluster in memory and on disk. We believe that for a typical Kafka cluster 5GB of main memory and 5GB of disk space on the metadata log director is sufficient.

### Missing features

The following features are not fully implemented in KRaft mode: configuring SCRAM users via the `--zookeeper` flag (removed), and modifying certain dynamic configurations on the standalone KRaft controller.
