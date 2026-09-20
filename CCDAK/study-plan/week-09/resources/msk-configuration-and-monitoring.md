# Amazon MSK — Custom/default configuration + CloudWatch metrics levels + Open Monitoring (Prometheus)

> **Nguồn (official):** https://docs.aws.amazon.com/msk/latest/developerguide/msk-configuration-properties.html · https://docs.aws.amazon.com/msk/latest/developerguide/msk-default-configuration.html · https://docs.aws.amazon.com/msk/latest/developerguide/metrics-details.html · https://docs.aws.amazon.com/msk/latest/developerguide/open-monitoring.html
> **Tuần:** 9 — Kafka trên AWS (`Amazon MSK`) + Design patterns · **Loại:** AWS Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- **MSK Configuration** = tập con `server.properties` bạn được sửa (`auto.create.topics.enable`, `default.replication.factor`, `min.insync.replicas`, `num.partitions`, `log.retention.hours/ms`, `message.max.bytes`, `log.cleanup.policy`, `unclean.leader.election.enable`, `num.io.threads`, `compression.type`, `transaction.max.timeout.ms`, `offsets.retention.minutes`, `replica.lag.time.max.ms` (10.000–30.000)...). Áp dụng bằng **rolling restart** do MSK điều phối. Thuộc tính không có trong danh sách (`broker.id`, `listeners`, `log.dirs`, `zookeeper.connect`...) **không sửa được**.
- **Default MSK khác Apache Kafka**: `auto.create.topics.enable=false` (Kafka: true) · `default.replication.factor=3` (3 AZ) / 2 (2 AZ) · `min.insync.replicas=2` (3 AZ) / 1 (2 AZ) · `num.network.threads=5` · `num.io.threads=8` · `num.replica.fetchers=2` · `unclean.leader.election.enable=true` (Kafka: false; tiered cluster: false) · `allow.everyone.if.no.acl.found=true` · `log.segment.bytes` 1 GiB (tiered: 128 MiB) · tiered `retention.ms` tối thiểu **3 ngày**.
- **4 mức CloudWatch monitoring**: `DEFAULT` (miễn phí) → `PER_BROKER` → `PER_TOPIC_PER_BROKER` → `PER_TOPIC_PER_PARTITION` (có phí, mức sau bao gồm mức trước). Metric đẩy mỗi **1 phút**.
- Metric cấp cluster (DEFAULT): `ActiveControllerCount` (**phải = 1**), `OfflinePartitionsCount` (**phải = 0**), `GlobalPartitionCount`, `GlobalTopicCount`; cấp broker: `UnderReplicatedPartitions` (**phải = 0**), `UnderMinIsrPartitionCount`, `KafkaDataLogsDiskUsed` (% — kích storage auto-scaling), `CpuUser`+`CpuSystem` (khuyến nghị < 60%), `BytesInPerSec`/`BytesOutPerSec`, `ConnectionCount`, `LeaderCount`, `PartitionCount`, `BurstBalance` (EBS).
- **Consumer lag** ngay ở DEFAULT (theo consumer group + topic): `EstimatedMaxTimeLag` (giây để tiêu hết `MaxOffsetLag`), `MaxOffsetLag`, `SumOffsetLag`; cấp partition (`PER_TOPIC_PER_PARTITION`): `EstimatedTimeLag`, `OffsetLag`. Yêu cầu tên consumer group ASCII.
- PER_BROKER: `RequestHandlerAvgIdlePercent`, `NetworkProcessorAvgIdlePercent`, throttle metrics, `IAMTooManyConnections` (>0 = vượt 100 conn/s), `KafkaFileDescriptorsUsagePercent` (< 80%), tiered storage `RemoteCopyLagBytes`, `RemoteFetchBytesPerSec`.
- **Open Monitoring với Prometheus**: bật **JMX Exporter (port 11001)** và **Node Exporter (port 11002)** trên broker; miễn phí (chỉ phí cross-AZ transfer); security group phải mở 11001/11002 cho Prometheus server. **KRaft/Express không thể bật đồng thời open monitoring + public access.**
- Bẫy: "muốn xem lag từng partition" ⇒ `PER_TOPIC_PER_PARTITION`; "disk đầy" ⇒ `KafkaDataLogsDiskUsed` + storage auto-scaling / tiered storage; "cần Grafana/Prometheus" ⇒ Open Monitoring chứ không phải CloudWatch agent.

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Custom Amazon MSK configurations

You can use Amazon MSK to create a custom MSK configuration where you set the following Apache Kafka configuration properties. Properties that you don't set explicitly get the values they have in the Default Amazon MSK configuration.

| Name | Description |
| --- | --- |
| allow.everyone.if.no.acl.found | If you set this property to false and you don't first define Apache Kafka ACLs, you lose access to the cluster. |
| auto.create.topics.enable | Enables topic auto-creation on the server. |
| compression.type | The final compression type for a given topic (gzip, snappy, lz4, zstd, uncompressed, producer). |
| connections.max.idle.ms | Idle connections timeout in milliseconds. |
| custom.advertised.listeners | Configures custom domain names for client-facing listeners, e.g. `LISTENER_NAME://b-{broker_id}.kafka.mycompany.com:9000+{broker_id}`. Allowed listener names: CLIENT, CLIENT_SECURE, CLIENT_SECURE_PUBLIC, CLIENT_SASL_SCRAM, CLIENT_SASL_SCRAM_PUBLIC, CLIENT_IAM, CLIENT_IAM_PUBLIC. |
| default.replication.factor | The default replication factor for automatically created topics. |
| delete.topic.enable | Enables the delete topic operation. |
| group.initial.rebalance.delay.ms | Time the group coordinator waits for more consumers to join a new group before the first rebalance. |
| group.max.session.timeout.ms / group.min.session.timeout.ms | Max/min session timeout for registered consumers. |
| leader.imbalance.per.broker.percentage | The ratio of leader imbalance allowed per broker. |
| log.cleaner.delete.retention.ms | Amount of time to retain deleted records (tombstones). Minimum 0. |
| log.cleaner.min.cleanable.ratio | 0–1; by default Kafka avoids cleaning a log if more than 50% of the log has been compacted. |
| log.cleanup.policy | delete and/or compact. **For Tiered Storage enabled clusters, valid policy is delete only.** |
| log.flush.interval.messages / log.flush.interval.ms | Flush thresholds. |
| log.message.timestamp.type | CreateTime or LogAppendTime. |
| log.retention.bytes / log.retention.hours / log.retention.minutes / log.retention.ms | Retention size/time (ms > minutes > hours precedence). |
| log.roll.ms | Maximum time before a new log segment is rolled out. |
| log.segment.bytes | Maximum size of a single log file. |
| max.incremental.fetch.session.cache.slots | Max incremental fetch sessions maintained. |
| message.max.bytes | Largest record batch size that Kafka allows. Can be set per topic with `max.message.bytes`. |
| min.insync.replicas | When a producer sets acks to "all", the minimum number of replicas that must acknowledge a write. E.g. RF=3, min.insync.replicas=2, acks=all. |
| num.io.threads / num.network.threads | Threads for processing requests / network I/O. |
| num.partitions | Default number of log partitions per topic. |
| num.recovery.threads.per.data.dir | Threads per data directory for log recovery at startup. |
| num.replica.fetchers | Fetcher threads used to replicate messages from a source broker. |
| offsets.retention.minutes | Retention of offsets after a consumer group becomes empty. |
| offsets.topic.replication.factor | Replication factor for the offsets topic. |
| replica.fetch.max.bytes / replica.fetch.response.max.bytes | Replica fetch sizes. |
| replica.lag.time.max.ms | Follower removed from ISR if not caught up for this long. **MinValue 10000, MaxValue 30000.** |
| replica.selector.class | Set to `org.apache.kafka.common.replica.RackAwareReplicaSelector` to allow consumers to fetch from the closest replica (Kafka ≥ 2.4.1). |
| socket.receive.buffer.bytes / socket.send.buffer.bytes / socket.request.max.bytes | Socket buffers. |
| transaction.max.timeout.ms | Maximum timeout for transactions. |
| transaction.state.log.min.isr / transaction.state.log.replication.factor | Settings for the transaction topic. |
| transactional.id.expiration.ms | Time before the coordinator expires a transactional ID. |
| unclean.leader.election.enable | Whether replicas not in the ISR can become leader as a last resort (possible data loss). |
| zookeeper.connection.timeout.ms / zookeeper.session.timeout.ms | ZooKeeper mode clusters only; 6000–18000. |

When you update your existing MSK cluster with a custom MSK configuration, Amazon MSK does **rolling restarts** when necessary, and lets each broker catch up on data it might have missed before moving to the next broker.

In addition, you can **dynamically** set cluster-level and broker-level configuration properties that don't require a broker restart (properties not marked read-only in Apache Kafka Broker Configs) and **topic-level** properties with the Apache Kafka tools.

### Default Amazon MSK configuration

| Name | Default (non-tiered) | Default (tiered storage-enabled) |
| --- | --- | --- |
| allow.everyone.if.no.acl.found | true | true |
| auto.create.topics.enable | **false** | false |
| auto.leader.rebalance.enable | true | true |
| default.replication.factor | **3 for clusters in 3 AZs, 2 for clusters in 2 AZs** | same |
| local.retention.bytes / local.retention.ms | -2 (unlimited) | -2 |
| log.segment.bytes | 1073741824 | 134217728 |
| min.insync.replicas | **2 for 3 AZs, 1 for 2 AZs** | same |
| num.io.threads | 8 | max(8, vCPUs) |
| num.network.threads | 5 | max(5, vCPUs / 2) |
| num.partitions | 1 | 1 |
| num.replica.fetchers | 2 | max(2, vCPUs / 4) |
| remote.storage.enable | false | false (topic-level enables tiered storage; disabling is permanent) |
| replica.lag.time.max.ms | 30000 | 30000 |
| retention.ms (tiered) | — | Mandatory; minimum 259,200,000 ms (3 days); -1 infinite |
| socket.receive.buffer.bytes / socket.send.buffer.bytes | 102400 | 102400 |
| socket.request.max.bytes | 104857600 | 104857600 |
| unclean.leader.election.enable | **true** | false |
| zookeeper.session.timeout.ms | 18000 | 18000 |

### Amazon MSK metrics for monitoring with CloudWatch

Metrics are automatically collected and pushed to CloudWatch at **1 minute intervals**. You can set the monitoring level to `DEFAULT`, `PER_BROKER`, `PER_TOPIC_PER_BROKER`, or `PER_TOPIC_PER_PARTITION`. **`DEFAULT`-level metrics are free.**

#### DEFAULT level (selected)

| Name | Dimensions | Description |
| --- | --- | --- |
| ActiveControllerCount | Cluster Name | Only one controller per cluster should be active at any given time. |
| OfflinePartitionsCount | Cluster Name | Total number of partitions that are offline in the cluster. |
| GlobalPartitionCount | Cluster Name | Number of partitions across all topics, excluding replicas. |
| GlobalTopicCount | Cluster Name | Total number of topics across all brokers. |
| UnderReplicatedPartitions | Cluster Name, Broker ID | Number of under-replicated partitions for the broker. |
| UnderMinIsrPartitionCount | Cluster Name, Broker ID | Number of under minIsr partitions for the broker. |
| KafkaDataLogsDiskUsed | Cluster Name, Broker ID | Percentage of disk space used for data logs. |
| KafkaAppLogsDiskUsed / RootDiskUsed | Cluster Name, Broker ID | Percentage of disk used for app logs / root disk. |
| BurstBalance | Cluster Name, Broker ID | Remaining EBS I/O burst credits. |
| BytesInPerSec / BytesOutPerSec | Cluster Name, Broker ID, Topic | Bytes per second received from / sent to clients (per broker and per topic). |
| MessagesInPerSec | Cluster Name, Broker ID | Incoming messages per second. |
| CpuUser / CpuSystem / CpuIdle / CpuIoWait | Cluster Name, Broker ID | CPU percentages. |
| ConnectionCount / ClientConnectionCount | Cluster Name, Broker ID (, Client Authentication) | Active connections. |
| LeaderCount / PartitionCount | Cluster Name, Broker ID | Leaders per broker (no replicas) / partitions per broker (incl. replicas). |
| MemoryUsed / MemoryFree / HeapMemoryAfterGC | Cluster Name, Broker ID | Memory metrics. |
| ProduceTotalTimeMsMean / RequestTime | Cluster Name, Broker ID | Mean produce time / request processing time. |
| TrafficShaping | Cluster Name, Broker ID | Packets shaped due to exceeding network allocations. |
| **EstimatedMaxTimeLag** | Cluster Name, Consumer Group, Topic | Time estimate (seconds) to drain MaxOffsetLag. |
| **MaxOffsetLag** | Cluster Name, Consumer Group, Topic | Maximum offset lag across all partitions in a topic. |
| **SumOffsetLag** | Cluster Name, Consumer Group, Topic | Aggregated offset lag for all partitions in a topic. |
| RollingEstimatedTimeLagMax | Cluster Name, Consumer Group, Topic | Rolling max time estimate to drain lag. |
| ZooKeeperRequestLatencyMsMean / ZooKeeperSessionState | Cluster Name, Broker ID | ZooKeeper-based clusters only. |

Consumer lag metrics require ASCII-only consumer group names.

#### PER_BROKER level (paid, adds to DEFAULT) — selected

`BwInAllowanceExceeded`, `BwOutAllowanceExceeded`, `ConntrackAllowanceExceeded`, `PpsAllowanceExceeded`, `ConnectionCreationRate`, `ConnectionCloseRate`, `CpuCreditUsage`, `FetchConsumer*TimeMsMean`, `FetchFollower*TimeMsMean`, `FetchThrottleTime/ByteRate/QueueSize`, `ProduceThrottleTime/ByteRate/QueueSize`, `RequestThrottleTime`, `IAMNumberOfConnectionRequests`, `IAMTooManyConnections` (number of connections attempted beyond 100; >0 means the throttle limit is being exceeded), `KafkaFileDescriptorsUsagePercent` (keep below 80%), `KafkaMemoryMappedFilesUsagePercent`, `NetworkProcessorAvgIdlePercent`, `RequestHandlerAvgIdlePercent`, `ReplicationBytesInPerSec/OutPerSec`, `VolumeQueueLength`, `VolumeRead/WriteBytes/Ops`, tiered storage: `RemoteFetchBytesPerSec`, `RemoteCopyBytesPerSec`, `RemoteCopyLagBytes`, `RemoteLogSizeBytes`, `RemoteFetchErrorsPerSec`, `RemoteCopyErrorsPerSec`.

#### PER_TOPIC_PER_BROKER level (dimensions Cluster Name, Broker ID, Topic)

`FetchMessageConversionsPerSec`, `MessagesInPerSec`, `ProduceMessageConversionsPerSec`, tiered `RemoteFetchBytesPerSec`, `RemoteCopyBytesPerSec`, `RemoteLogSizeBytes`... Metrics appear only after their values become nonzero for the first time.

#### PER_TOPIC_PER_PARTITION level (dimensions Consumer Group, Topic, Partition)

| Name | Description |
| --- | --- |
| EstimatedTimeLag | Time estimate (in seconds) to drain the partition offset lag. |
| OffsetLag | Partition-level consumer lag in number of offsets. |
| RollingEstimatedTimeLag | Rolling time estimate (seconds) to drain the partition offset lag. |

### Monitor an MSK Provisioned cluster with Prometheus (Open Monitoring)

You can monitor your MSK Provisioned cluster with Prometheus. You can publish this data to **Amazon Managed Service for Prometheus** using remote write, or use tools compatible with Prometheus-formatted metrics (Datadog, Lenses, New Relic, Sumo Logic). **Open monitoring is available for free but charges apply for the transfer of data across Availability Zones.**

Enable via the cluster's `OpenMonitoring` setting: `Prometheus.JmxExporter.EnabledInBroker=true` (exposes broker JMX metrics on **port 11001**) and `Prometheus.NodeExporter.EnabledInBroker=true` (host metrics on **port 11002**). The cluster security group must allow inbound 11001/11002 from the Prometheus server. Example scrape config:

```yaml
scrape_configs:
  - job_name: 'msk-jmx'
    static_configs:
      - targets: ['b-1.demo.xxxx.c2.kafka.us-east-1.amazonaws.com:11001', 'b-2....:11001', 'b-3....:11001']
  - job_name: 'msk-node'
    static_configs:
      - targets: ['b-1....:11002', 'b-2....:11002', 'b-3....:11002']
```

> **Note:** KRaft metadata mode and MSK Express brokers can't have open monitoring and public access both enabled.
