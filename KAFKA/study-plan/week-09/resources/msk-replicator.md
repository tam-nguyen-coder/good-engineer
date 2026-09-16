# Amazon MSK Replicator — managed cross-cluster / cross-region replication

> **Nguồn (official):** https://docs.aws.amazon.com/msk/latest/developerguide/msk-replicator.html · https://docs.aws.amazon.com/msk/latest/developerguide/msk-replicator-topic-naming.html · https://docs.aws.amazon.com/msk/latest/developerguide/limits.html#msk-replicator-quotas
> **Tuần:** 9 — Kafka trên AWS (`Amazon MSK`) + Design patterns · **Loại:** AWS Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- `MSK Replicator` = **managed replication** giữa cluster MSK (**cùng region SRR** hoặc **khác region CRR**), và từ **Kafka tự quản (on-prem/EC2/cloud khác) → MSK Provisioned** (di cư). Thay cho việc tự vận hành **MirrorMaker 2** (Tuần 8). Source + target phải **cùng AWS account**; tự scale, không quản hạ tầng, không cần tự dựng networking cross-region.
- Replicate **data + metadata**: topic configuration, **ACLs**, và **consumer group offsets** (offset sync → failover consumer đọc tiếp ở chỗ đã đọc) — **bất đồng bộ** (asynchronous).
- 2 chế độ tên topic: **Prefixed** (mặc định) → topic đích là `<sourceKafkaClusterAlias>.topic`, consumer nên subscribe wildcard `.*topic1` ở cả 2 region; tránh vòng lặp replicate; phù hợp **active-active**. **Identical topic name** (2024) → giữ nguyên tên, client **không cần đổi cấu hình khi failover** (active-passive), tránh loop bằng header `__mskmr` nhúng cluster/topic nguồn; dùng cho aggregation nhiều cluster → 1 (mỗi source 1 Replicator) và migration.
- Quota: **15 Replicator/account**, **750 topic/Replicator** (sorted order; cần nhiều hơn → tạo Replicator khác), ingress **1 GB/s/Replicator**, record tối đa **10 MB cross-region / 20 MB same-region**.
- Metrics: `ReplicationLatency`, `MessageLag`, `ReplicatorThroughput`, `ReplicatorBytesInPerSec`, `TopicCount` (Prefixed: `ReplicatorBytesInPerSec` = `ReplicatorThroughput` vì không lọc).
- Use case: multi-region HA/DR, low-latency read ở region khác, phân phối data cho partner, aggregate analytics, "write locally – read globally" (multi-active), migration.
- Bẫy: "cross-region DR cho MSK, tối thiểu code/ops" ⇒ MSK Replicator (không phải MM2 tự dựng, không phải Kinesis); "cần consumer failover tiếp đúng offset" ⇒ bật **consumer group offset sync**; "client không muốn đổi tên topic khi failover" ⇒ **Identical topic name**.

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Amazon MSK Replicator

Amazon MSK Replicator is a fully managed feature of Amazon MSK that enables you to reliably replicate data across Amazon MSK clusters in different or the same AWS Region. MSK Replicator also supports data replication from **self-managed Apache Kafka clusters** (including on-premises, self-hosted on AWS, or other cloud providers) to Amazon MSK Provisioned clusters. **Both the source and target clusters must be in the same AWS account** when replicating between MSK clusters. With MSK Replicator, you can build regionally resilient streaming applications for increased availability and business continuity, and migrate Apache Kafka workloads from self-managed environments to Amazon MSK. MSK Replicator provides **automatic asynchronous replication of data and consumer group offsets** between MSK clusters, eliminating the need to write custom code, manage infrastructure, or set up cross-region networking.

MSK Replicator automatically scales the underlying resources so that you can replicate data on-demand without having to monitor or scale capacity. MSK Replicator also replicates the necessary Kafka metadata including **topic configurations, Access Control Lists (ACLs), and consumer group offsets**. If an unexpected event occurs in a Region, you can failover to the other AWS Region and seamlessly resume processing.

MSK Replicator supports both **cross-region replication (CRR)** and **same-region replication (SRR)**. You need to create source and target MSK clusters before using them with MSK Replicator.

Common uses for Amazon MSK Replicator:

- **Build multi-region streaming applications**: highly available and fault-tolerant streaming applications for increased resiliency without setting up custom solutions.
- **Lower latency data access**: provide lower latency data access to consumers in different geographic regions.
- **Distribute data to your partners**: copy data from one Apache Kafka cluster to many, so that different teams/partners have their own copies of data.
- **Aggregate data for analytics**: copy data from multiple Apache Kafka clusters into one cluster.
- **Write locally, access your data globally**: set up multi-active replication to automatically propagate writes performed in one AWS Region to other Regions.
- **Migrate from self-managed Kafka clusters**: migrate to Amazon MSK Provisioned clusters with consumer group offset synchronization for seamless application cutover.

### Topic naming (Prefixed vs Identical)

MSK Replicator has two topic name configuration modes: **Prefixed** (default) or **Identical** topic name replication.

**Prefixed topic name replication** — By default, MSK Replicator creates new topics in the target cluster with an auto-generated prefix added to the source cluster topic name, such as `<sourceKafkaClusterAlias>.topic`. This distinguishes the replicated topics from others in the target cluster and **avoids circular replication** of data between the clusters. You can find the prefix under the `sourceKafkaClusterAlias` field using the `DescribeReplicator` API or the Replicator details page on the MSK console.

To make sure your consumers can reliably restart processing from the standby cluster, configure your consumers to read data from the topics using a wildcard operator `.*`. For example, your consumers would need to consume using `.*topic1` in both AWS Regions (this would also include a topic such as `footopic1`, so adjust the wildcard accordingly).

Use Prefixed topic name replication when you want to keep replicated data in a separate topic in the target cluster, such as for **active-active** cluster setups. For Prefixed configuration, both `ReplicatorBytesInPerSec` and `ReplicatorThroughput` will have the same value as no data will be filtered by MSK Replicator.

**Identical topic name replication** — Amazon MSK Replicator allows you to create a Replicator with topic replication set to Identical topic name replication (**Keep the same topics name** in console). Identically-named replicated topics let you avoid reconfiguring clients to read from replicated topics. Advantages:

- Retains identical topic names during replication while **automatically avoiding infinite replication loops**.
- Simplifies multi-cluster streaming architectures since you can avoid reconfiguring clients.
- Streamlines the **failover process for active-passive architectures**, allowing applications to seamlessly failover without topic name changes or client reconfigurations.
- Can **consolidate data from multiple MSK clusters into a single cluster** for data aggregation or centralized analytics (requires separate Replicators for each source cluster).
- Can streamline **data migration** from one MSK cluster to another.

Amazon MSK Replicator uses Kafka headers to automatically avoid data being replicated back to the topic it originated from. MSK Replicator embeds identifiers for source cluster and topic into the header of each record being replicated (**`__mskmr`**). You should verify that your clients are able to read replicated data as expected.

### Replicator configuration concepts (summary of the concepts pages)

- **Source cluster / target cluster** — MSK Provisioned clusters (target) with IAM access control enabled; the Replicator uses a service-linked role and creates ENIs in the source cluster's VPC (multi-VPC connectivity for cross-region).
- **Topics to replicate** — allow list (regex) and exclude list; **Detect and copy new topics** automatically; copy topic configurations; copy access control lists.
- **Starting position** — replicate from **earliest** offset (all existing data) or **latest** (only new data after creation).
- **Consumer group replication** — allow/exclude lists; **Synchronise consumer group offsets** so consumers can resume from the target cluster after failover; offsets are translated to the target topic offsets.
- **Failover / failback** — active-passive: point clients to the standby Region's bootstrap when the primary is impaired; to fail back, create a Replicator in the reverse direction (or use a bidirectional pair with Prefixed naming for active-active).

### MSK Replicator quotas

- A maximum of **15 MSK Replicators per account**.
- MSK Replicator only replicates up to **750 topics** in sorted order. If you need to replicate more topics, create a separate Replicator. Monitor the number of topics being replicated using the `TopicCount` metric.
- A maximum ingress throughput of **1 GB per second per MSK Replicator**.
- MSK Replicator record size — a maximum record size of **10 MB for cross-region replication and 20 MB for same-region replication** (`message.max.bytes`).
