# Apache Kafka 4.0.0 Release Announcement (18/03/2025) — KRaft-only, KIP-848 GA, Queues (KIP-932), ELR, Java 17

> **Nguồn (official):** https://kafka.apache.org/blog/2025/03/18/apache-kafka-4.0.0-release-announcement/
> **Tuần:** 1 — Kiến trúc Kafka & `KRaft` + Dựng cluster + CLI · **Loại:** Apache Kafka Blog
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- Kafka **4.0** = bản major **đầu tiên chạy hoàn toàn không có ZooKeeper**; chỉ còn `KRaft`. Không thể migrate trực tiếp ZK → 4.0, phải qua **bridge release 3.9**.
- **KIP-848** (next-gen consumer rebalance protocol) **GA**: hết "stop-the-world" rebalance, assignment tính ở **broker** (server-side assignor), client opt-in bằng **`group.protocol=consumer`**. (Classic protocol bị deprecate ở 4.3.)
- **KIP-932 Queues for Kafka** — **share groups**: nhiều consumer hơn số partition, ack **từng record**, hàng đợi cộng tác trên topic thường; **early access ở 4.0** (preview 4.1, **GA 4.2**).
- **KIP-966 Eligible Leader Replicas (ELR)** — **preview ở 4.0**: tập con replica đảm bảo đủ dữ liệu tới high-watermark, bầu leader an toàn không mất dữ liệu (GA/enable-by-default cho cluster mới từ 4.1).
- **Java**: clients + Kafka Streams cần **Java 11+**; broker, Connect, tools cần **Java 17+**.
- **Breaking**: gỡ API version cũ (**KIP-896**) và message format **v0/v1** (**KIP-724**) → client 4.0 chỉ nói chuyện được với broker **≥ 2.1**; broker 4.0 chỉ chấp nhận client ≥ 2.1 (baseline protocol 2.1).
- **KIP-1030** đổi default: `linger.ms` **0 → 5 ms**, `num.recovery.threads.per.data.dir` **1 → 2**, siết validation (ví dụ `segment.bytes` tối thiểu 1 MB). Đề cũ ghi `linger.ms=0` → hiểu là đã đổi.
- **KIP-653**: broker chuyển **Log4j → Log4j2**; **KIP-1032**: Connect lên **Jakarta EE 10** (đổi namespace `javax` → `jakarta`).
- Các KIP đáng nhớ khác: **KIP-890** (transaction server-side defense chống zombie), **KIP-996** (Pre-Vote giảm election vô ích trong KRaft), **KIP-1076** (client metrics), **KIP-1106** (duration-based `auto.offset.reset`, ví dụ `by_duration:PT1H`), **KIP-1102** (client re-bootstrap khi timeout), **KIP-1043/1099** (`kafka-groups.sh`, tool cho consumer/share group).
- Streams: **KIP-1104** (foreign-key extract từ cả key và value), **KIP-1112** (ProcessorWrapper), **KIP-1065** (`RETRY` cho ProductionExceptionHandler), **KIP-1091** (metrics). Connect: **KIP-1074** (replicate topic nội bộ do user tạo), **KIP-1089** (tắt heartbeat replication), gỡ endpoint `task-configs` (**KIP-970**).

---

## 📄 Nội dung (trích từ tài liệu gốc)

We are proud to announce the release of Apache Kafka 4.0.0. This release contains many new features and improvements. This blog post will highlight some of the more prominent features. For a full list of changes, be sure to check the release notes.

**Apache Kafka 4.0 is a significant milestone, marking the first major release to operate entirely without Apache ZooKeeper™️.** By running in KRaft mode by default, Kafka simplifies deployment and management, eliminating the complexity of maintaining a separate ZooKeeper ensemble. This change significantly reduces operational overhead, enhances scalability, and streamlines administrative tasks. We want to take this as an opportunity to express our gratitude to the ZooKeeper community and say thank you! ZooKeeper was the backbone of Kafka for more than 10 years, and it did serve Kafka very well. Kafka would most likely not be what it is today without it. We don't take this for granted, and highly appreciate all of the hard work the community invested to build ZooKeeper. Thank you!

**Kafka 4.0 also brings the general availability of KIP-848**, introducing a new consumer group protocol designed to dramatically improve rebalance performance. This optimization significantly reduces downtime and latency, enhancing the reliability and responsiveness of consumer groups, especially in large-scale deployments. Consumers must opt in to the new protocol by setting `group.protocol=consumer`.

Additionally, we're excited to offer **early access to Queues for Kafka (KIP-932)**, enabling Kafka to support traditional queue semantics directly. This feature extends Kafka's versatility, making it an ideal choice for a broader range of use cases, particularly those requiring point-to-point messaging patterns. Share groups allow the number of consumers to exceed the number of partitions and provide per-record acknowledgement.

Kafka 4.0 also removes a number of deprecated APIs and includes changes to the supported Java versions. Before upgrading, please review the "Notable changes" and "Upgrading" sections of the documentation.

### Kafka Broker, Controller, Producer, Consumer and Admin Client

- **KIP-848: The Next Generation of the Consumer Rebalance Protocol** — The new protocol moves the assignment logic from the client to the group coordinator on the broker (server-side assignors `uniform` and `range`) and replaces the global synchronization barrier with incremental, per-member reconciliation. Rebalances no longer stop the whole group. The protocol is generally available in 4.0; the classic protocol remains the default (`group.protocol=classic`).
- **KIP-890: Transactions Server-Side Defense** — Strengthens the transaction protocol against zombie producers by verifying partition additions on the server side, reducing the risk of hanging transactions. Version 2 of the transaction protocol is enabled by default on new clusters.
- **KIP-932: Queues for Kafka (Early Access)** — Introduces the concept of share groups: a new type of group in which consumers cooperatively consume records from the same partitions, records are acquired for a limited time, and each record is explicitly acknowledged (accept, release or reject). Not for production use in 4.0.
- **KIP-966: Eligible Leader Replicas (Preview)** — Introduces the ELR, a subset of replicas that are guaranteed to have complete data up to the high-watermark. Replicas in the ELR can be safely elected as leader when the ISR is empty, without data loss. The feature is controlled by the `eligible.leader.replicas.version` feature flag.
- **KIP-996: Pre-Vote** — Adds a pre-vote phase to the KRaft protocol so that a replica that has lost contact with the leader does not disrupt the quorum with unnecessary elections.
- **KIP-1076: Metrics for client applications KIP-714 extension** — Allows applications built on the Kafka client to register their own metrics and push them to the broker using the client telemetry mechanism.
- **KIP-1106: Add duration based offset reset option for consumer clients** — Adds `by_duration:<ISO-8601 duration>` to `auto.offset.reset` (e.g. `by_duration:PT1H`), and `--to-duration` to the consumer group tool.
- **KIP-1043: An additional API to list groups** — Adds `kafka-groups.sh` to list all groups (consumer, share, streams) regardless of type.
- **KIP-1099: Extend kafka-consumer-groups command line tool to support new consumer group** — Shows the group type and the new protocol in `kafka-consumer-groups.sh --describe`.
- **KIP-1102: Enable clients to rebootstrap based on timeout or error code** — Clients automatically re-bootstrap from `bootstrap.servers` when metadata cannot be refreshed within `metadata.recovery.rebootstrap.trigger.ms` or when the broker returns `REBOOTSTRAP_REQUIRED`.
- **KIP-653: Upgrade log4j to log4j2** — Broker and tools now use Log4j 2; the `log4j.properties` files are replaced by `log4j2.yaml`.
- **KIP-1030: Change constraints and default values for various configurations** — Updates several defaults to safer values, notably `linger.ms` from 0 to 5 ms, `num.recovery.threads.per.data.dir` from 1 to 2, and adds minimum constraints (e.g. `segment.bytes` ≥ 1 MB, `segment.ms` ≥ 1 minute).

### Kafka Streams

- **KIP-1104: Allow Foreign Key Extraction from Both Key and Value in KTable Joins** — foreign-key joins can now use a `BiFunction` over key and value.
- **KIP-1112: Allow custom processor wrapping** — A `ProcessorWrapper` interface lets users wrap every processor in the topology (e.g. for cross-cutting logging or tracing).
- **KIP-1065: Add "retry" return-option to ProductionExceptionHandler** — The handler can return `RETRY` to retry sending a record instead of failing or skipping.
- **KIP-1091: Improved Kafka Streams operator metrics** — Adds client-instance-level state metrics and thread-level metrics for better observability.

### Kafka Connect

- **KIP-970: Deprecate and remove Connect's redundant task configurations endpoint** — The `/connectors/{connector}/tasks-config` endpoint is removed; use `/connectors/{connector}/tasks`.
- **KIP-1074: Allow the replication of user internal topics** — MirrorMaker 2 can replicate topics that use the internal naming convention when configured to.
- **KIP-1089: Allow disabling heartbeats replication in MirrorSourceConnector** — Adds `emit.heartbeats.enabled` per replication flow.
- **KIP-1032: Upgrade to Jakarta and JavaEE 10 in Kafka 4** — Connect's REST layer moves to Jakarta EE 10 (Jetty 12), changing `javax.*` to `jakarta.*` for REST extensions.

### Notable changes

- Java 17 is now required for the broker, Kafka Connect and the tools; Java 11 remains the minimum for clients and Kafka Streams.
- Message format versions v0 and v1 are no longer supported (KIP-724); the old client protocol API versions are removed (KIP-896). As a consequence, brokers must be at least version 2.1 before upgrading Java clients to 4.0, and 4.0 brokers cannot be contacted by clients older than 2.1.
- ZooKeeper mode is removed. Clusters running in ZooKeeper mode must first migrate to KRaft on a 3.9.x bridge release.
- Deprecated `--zookeeper` options are removed from all command line tools; `--bootstrap-server` (or `--bootstrap-controller`) is the only way to connect.

### Summary

Apache Kafka 4.0 is a major step forward: KRaft-only operation, a faster consumer rebalance protocol, queue semantics through share groups, and a leaner codebase with old APIs removed. To learn more, read the release notes and check out the "Upgrading" documentation before moving production clusters.
