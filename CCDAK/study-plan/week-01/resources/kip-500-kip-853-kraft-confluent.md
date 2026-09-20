# KIP-500 (Replace ZooKeeper) & KIP-853 (KRaft Controller Membership Changes) + Confluent KRaft learn page

> **Nguồn (official):** https://cwiki.apache.org/confluence/display/KAFKA/KIP-500%3A+Replace+ZooKeeper+with+a+Self-Managed+Metadata+Quorum · https://cwiki.apache.org/confluence/display/KAFKA/KIP-853%3A+KRaft+Controller+Membership+Changes · https://developer.confluent.io/learn/kraft/ · https://developer.confluent.io/courses/architecture/control-plane/ · https://docs.confluent.io/platform/current/kafka-metadata/config-kraft.html
> **Tuần:** 1 — Kiến trúc Kafka & `KRaft` + Dựng cluster + CLI · **Loại:** KIP + Confluent Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất. **Hai trang cwiki KIP-500 / KIP-853 không phản hồi khi crawl** → phần KIP bên dưới được **tổng hợp từ docs** (không crawl được, tổng hợp từ docs); các phần Confluent crawl thành công.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- **KIP-500 — vì sao bỏ ZooKeeper:** (1) phải vận hành, bảo mật, giám sát **2 hệ thống** khác nhau; (2) metadata bị **chia đôi** (ZooKeeper vs cache trong controller) → dễ **lệch** (divergence); (3) controller mới phải **load toàn bộ metadata từ ZK** — thời gian failover **O(số partition)**; (4) giới hạn thực tế ~**200 000 partition**/cluster.
- **KRaft** = *Kafka Raft*: "consensus protocol introduced in KIP-500 to remove Kafka's dependency on ZooKeeper for metadata management"; metadata trở thành **event log** (event-sourced) trong topic nội bộ **`__cluster_metadata`** (**1 partition**), do **controller quorum** replicate bằng biến thể **event-based Raft**.
- **Active controller** = leader của partition metadata, nhận **mọi write** metadata; controller khác là **follower** (hot standby, đã có state trong RAM); **broker là observer** — **fetch** thay đổi (pull) thay vì bị push. Nhờ vậy failover **"near-instantaneous"**, không cần load state.
- Metadata record được **flush xuống đĩa ngay** khi ghi vào local log; leader election của quorum dùng **majority vote** (khác data partition dùng ISR). Ứng viên gửi `VoteRequest` kèm last offset/epoch; follower chỉ vote nếu offset ứng viên ≥ của mình; thắng khi đủ **đa số** → gửi `BeginQuorumEpoch`.
- **Snapshot**: controller và broker định kỳ snapshot in-memory metadata → cắt log cũ; broker khởi động = load snapshot → replay local log → fetch tiếp từ active controller.
- Lợi ích Confluent nêu: đơn giản vận hành, **một security model**, scale tới **hàng triệu partition** (thí nghiệm **2 triệu partition** vs ZK tối đa ~200k), recovery nhanh "at least 10x", "lightweight, single-process way to get started". **Production-ready từ 3.3**; 3.9 bridge release cuối; 4.0 KRaft-only.
- **KIP-853 — Dynamic quorum:** bỏ yêu cầu mọi node khai `controller.quorum.voters` tĩnh; dùng **`controller.quorum.bootstrap.servers`**; voter được định danh bằng **`node.id` + directory.id (UUID của log dir)** để tránh voter "hồi sinh" với đĩa trống lại được vote; feature **`kraft.version=1`** (0 = static). Có từ **3.9**.
- Lệnh KIP-853: `kafka-storage.sh format --standalone` | `--initial-controllers "id@host:port:dirUUID,..."` | `--no-initial-controllers`; `kafka-metadata-quorum.sh add-controller` / `remove-controller --controller-id --controller-directory-id` / `describe --status|--replication`; `kafka-features.sh upgrade --feature kraft.version=1` để nâng cluster static → dynamic.
- Confluent khuyến nghị **≥ 3 controller** (2n+1 chịu n lỗi), RAM ≥ 4 GB, SSD ≥ 64 GB, heap 1 GB; **combined mode không hỗ trợ production**; `controller.listener.names` phải có trong `listeners` nhưng **không** trong `advertised.listeners`.
- Đổi từ ZK sang KRaft, **client không đổi gì**: `bootstrap.servers=broker:9092`; tool đổi `--zookeeper zk:2181` → `--bootstrap-server broker:9092`; Schema Registry đổi `kafkastore.connection.url` → `kafkastore.bootstrap.servers`.

---

## 📄 Nội dung (trích từ tài liệu gốc)

### KIP-500: Replace ZooKeeper with a Self-Managed Metadata Quorum *(không crawl được, tổng hợp từ docs)*

**Motivation.** Currently, Kafka uses ZooKeeper to store its metadata about partitions and brokers, and to elect a broker to be the Kafka Controller. Removing this dependency on ZooKeeper has several benefits: it enables Kafka to manage its own metadata in a more scalable and robust way, supports more partitions, simplifies deployment and configuration, and allows a single security model for the whole system.

**Metadata as an event log.** We often talk about the benefits of managing state as a stream of events. A single number, the offset, describes a consumer's position in the stream. Multiple consumers can quickly catch up to the latest state simply by replaying all the events newer than their current offset. The log establishes a clear ordering between events, and ensures that the consumers always move along a single timeline. However, although our users enjoy these benefits, Kafka itself has been left out. We treat changes to metadata as isolated changes with no relationship to each other. When the controller pushes out state change notifications (such as LeaderAndIsrRequest) to other brokers in the cluster, it is possible for brokers to get some of the changes, but not all. Although the controller retries several times, it eventually gives up. This can leave brokers in a divergent state.

**Controller failover.** Worse still, although ZooKeeper is the store of record, the state in ZooKeeper often doesn't match the state that is held in memory in the controller. For example, when a partition leader changes its ISR in ZK, the controller will typically not learn about these changes for many seconds. There is no generic way for the controller to follow the ZooKeeper event log. When the controller is restarted, or a new controller is elected, it must load the full state of the cluster from ZooKeeper. As the number of partitions grows, this becomes a longer and longer process, making controller failover a period of unavailability that is **O(number of partitions)**. This also limits the number of partitions a single cluster can hold (in practice around 200,000).

**Simpler deployment and configuration.** ZooKeeper is a separate system, with its own configuration file syntax, management tools, and deployment patterns. This means that system administrators need to learn how to manage and deploy two separate distributed systems in order to deploy Kafka. Configuring both systems consistently (for example, security settings, timeouts) is error-prone, and the two systems have to be monitored separately.

**Proposed Changes.** Kafka will manage its metadata in a **self-managed metadata quorum** — a set of controller nodes running a Raft-like consensus protocol (KRaft). The metadata is stored as an ordered log (`__cluster_metadata`), and the **active controller** is the leader of that log. Other controllers are followers with a hot copy of the metadata in memory, so on failover a new controller becomes active without loading state from an external system. **Brokers fetch the metadata log from the active controller** (pull) instead of receiving pushed updates, so every broker consumes the same ordered timeline of changes. Brokers register with the controller and send periodic **heartbeats**; a broker that stops heartbeating is **fenced** and its partitions get new leaders. Periodic **snapshots** of the metadata state allow the log to be truncated and let brokers and controllers restart quickly.

**Compatibility.** A **bridge release** is required: clusters must first upgrade to a release that supports both modes, migrate their metadata into KRaft, and only then move to a KRaft-only release (the last bridge release is 3.9; 4.0 removes ZooKeeper). Client applications are unaffected because clients never talked to ZooKeeper directly since the `--bootstrap-server` era; tools that still accepted `--zookeeper` had that option removed.

### KIP-853: KRaft Controller Membership Changes *(không crawl được, tổng hợp từ docs)*

**Motivation.** With static quorums, every broker and controller must list all voters in `controller.quorum.voters`. Adding, removing or replacing a controller therefore requires editing the configuration of every node and restarting them, and a node reformatted with an empty disk but the same `node.id` could rejoin as a voter and vote from a blank log, risking metadata loss.

**Proposed changes.** KIP-853 (available since Kafka 3.9) makes the voter set part of the metadata log itself (`VotersRecord`), so it can be changed online with `AddRaftVoter` / `RemoveRaftVoter` RPCs. Each voter is identified by its `node.id` **and** a **directory id** (a UUID written to `meta.properties` when the log directory is formatted), so a replica with a freshly formatted disk is a different replica and cannot vote on behalf of the old one. Nodes discover the quorum through **`controller.quorum.bootstrap.servers`** (host:port only, like clients' `bootstrap.servers`) instead of `controller.quorum.voters`. The feature is gated by the **`kraft.version`** feature flag: version 0 = static quorum, version 1 = dynamic quorum.

**Public interfaces.**

```bash
# bootstrap the first controller as the only voter
bin/kafka-storage.sh format --cluster-id <ID> --standalone -c controller.properties
# or bootstrap several voters at once
bin/kafka-storage.sh format --cluster-id <ID> --initial-controllers "1@c1:9093:<dirUUID1>,2@c2:9093:<dirUUID2>,3@c3:9093:<dirUUID3>" -c controller.properties
# nodes that join later (brokers, extra controllers)
bin/kafka-storage.sh format --cluster-id <ID> --no-initial-controllers -c server.properties

# change membership online
bin/kafka-metadata-quorum.sh --bootstrap-server b:9092 add-controller
bin/kafka-metadata-quorum.sh --bootstrap-server b:9092 remove-controller --controller-id 4 --controller-directory-id <dirUUID>
bin/kafka-metadata-quorum.sh --bootstrap-server b:9092 describe --status
bin/kafka-metadata-quorum.sh --bootstrap-server b:9092 describe --replication

# check / upgrade the feature
bin/kafka-features.sh --bootstrap-controller c1:9093 describe
bin/kafka-features.sh --bootstrap-server b:9092 upgrade --feature kraft.version=1
```

**Compatibility.** Existing static clusters keep working (`kraft.version=0`, `controller.quorum.voters` deprecated but supported). Upgrading to a dynamic quorum requires all controllers on a release ≥ 3.9 and upgrading `kraft.version` to 1; downgrading `kraft.version` is not supported.

---

### Confluent Developer — KRaft: Apache Kafka Without ZooKeeper *(crawl thành công)*

Apache Kafka Raft (KRaft) is the consensus protocol that was introduced in KIP-500 to remove Apache Kafka's dependency on ZooKeeper for metadata management. This greatly simplifies Kafka's architecture by consolidating responsibility for metadata into Kafka itself, rather than splitting it between two different systems: ZooKeeper and Kafka. KRaft mode makes use of a new quorum controller service in Kafka which replaces the previous controller and makes use of an event-based variant of the Raft consensus protocol.

**Benefits of Kafka's new quorum controller:**

- Enables right-sized clusters, meaning clusters that are sized with the appropriate number of brokers and compute to satisfy a use case's throughput and latency requirements, with the potential to scale up to millions of partitions.
- Improves stability, simplifies the software, and makes it easier to monitor, administer, and support Kafka.
- Allows Kafka to have a single security model for the whole system.
- Provides a lightweight, single-process way to get started with Kafka.
- Makes controller failover near-instantaneous.

**How it works.** The quorum controllers use the new KRaft protocol to ensure that metadata is accurately replicated across the quorum. The quorum controller stores its state using an event-sourced storage model, which ensures that the internal state machines can always be accurately recreated. The event log used to store this state (also known as the metadata topic) is periodically abridged by snapshots to guarantee that the log cannot grow indefinitely. The other controllers within the quorum follow the active controller by responding to the events that it creates and stores in its log. Thus, should one node pause due to a partitioning event, for example, it can quickly catch up on any events it missed by accessing the log when it rejoins. This significantly decreases the unavailability window, improving the worst-case recovery time of the system. Unlike the ZooKeeper-based controller, **the quorum controller does not need to load state from ZooKeeper before it becomes active.**

| Component | ZooKeeper mode | KRaft mode |
| --- | --- | --- |
| Client configuration | `zookeeper.connect=zookeeper:2181` | `bootstrap.servers=broker:9092` |
| Schema Registry | `kafkastore.connection.url=zookeeper:2181` | `kafkastore.bootstrap.servers=broker:9092` |
| Admin tools | `kafka-topics --zookeeper zookeeper:2181` | `kafka-topics --bootstrap-server broker:9092` |

KRaft mode is production ready for new clusters as of Apache Kafka 3.3.

### Confluent Developer course — Kafka Internal Architecture: Control Plane *(crawl thành công)*

Historically, one designated broker served as controller, communicating with an external ZooKeeper ensemble; the metadata for the cluster is persisted in ZooKeeper and the controller propagated changes to other brokers.

Running Kafka in KRaft mode eliminates the need to run a ZooKeeper cluster alongside every Kafka cluster. A subset of brokers are designated as controllers, and these controllers provide the consensus services that used to be provided by ZooKeeper. All cluster metadata are now stored in Kafka topics and managed internally. All of the controller brokers maintain an in-memory metadata cache that is kept up to date, so that any controller can take over as the active controller if needed.

In KRaft mode, cluster metadata, reflecting the current state of all controller managed resources, is stored in a **single partition Kafka topic called `__cluster_metadata`**. The active controller is the leader of this internal metadata topic's single partition. Other controllers are replica followers. Brokers are replica observers. So, rather than the controller broadcasting metadata changes to the other controllers or to brokers, **they each fetch the changes**. Metadata records are flushed to disk immediately as they are written to each node's local log, and **leader election is done via quorum, rather than an in-sync replica set**.

**Leader election.** When election is needed, a candidate controller sends a `VoteRequest` to the other controllers including the candidate's last offset and the epoch. Followers grant votes if the latest offset passed in by the candidate is the same or higher than its own. Once achieving a majority of the votes, the candidate sends a `BeginQuorumEpoch` request to inform the others that it is the new leader.

**Broker metadata fetching.** When restarting, a broker loads its most recent snapshot into memory. Then starting from the EndOffset of its snapshot, it adds available records from its local `__cluster_metadata` log. It then begins fetching records from the active controller. Periodically, each of the controllers and brokers takes a snapshot of its in-memory metadata cache; all data in the metadata log that is older than the snapshot's offset and epoch is then safely stored and can be removed.

**KRaft advantages over ZooKeeper:** simpler deployment and administration with a much smaller operational footprint; improved scalability, with recovery from controller failures "at least 10x" faster; and more efficient metadata propagation through the log-based, event-driven mechanism.

### Confluent Platform docs — Configure KRaft *(crawl thành công)*

- `process.roles`: `controller`, `broker`, or `broker,controller` (combined mode for local testing only). `node.id`: a unique integer for each server regardless of role.
- Controller discovery: **dynamic quorum** (recommended) with `controller.quorum.bootstrap.servers=controller1.example.com:9093,controller2.example.com:9093`, which allows adding/removing controllers without restarting all nodes; **static quorum** (legacy) with `controller.quorum.voters=1@host1:port1,2@host2:port2,3@host3:port3`, which requires configuration updates on all nodes to modify the controller set.
- `controller.listener.names`: required comma-separated list of listeners the controller uses (e.g. `CONTROLLER`). These listeners must appear in `listeners` but **not** in `advertised.listeners`. Controllers must also configure `inter.broker.listener.name` to communicate with brokers, though the controller does not listen on that endpoint.

```properties
process.roles=controller
node.id=1
controller.quorum.bootstrap.servers=controller1:9093,controller2:9093,controller3:9093
controller.listener.names=CONTROLLER
listeners=CONTROLLER://controller1:9093
inter.broker.listener.name=BROKER
listener.security.protocol.map=CONTROLLER:SSL,BROKER:SSL
```

- Storage formatting: `kafka-storage format` with `--standalone` (first controller as sole voter), `--initial-controllers` (all controllers upfront with identical voter set) or `--no-initial-controllers` (brokers and additional controllers joining an existing quorum).
- Dynamic controllers require `kraft.version=1`; verify with `kafka-features describe` and upgrade with `kafka-features upgrade --feature kraft.version=1`. Manage the quorum with `kafka-metadata-quorum add-controller`, `remove-controller` and `describe --status`.
- Run **at least 3 KRaft controllers** in production (minimum 4 GB RAM, SSD storage 64 GB+, 1 GB JVM heap). An ensemble of 2n+1 controllers tolerates n failures. Combined mode is unsupported for production workloads; controllers in isolated mode provide better operational separation.
