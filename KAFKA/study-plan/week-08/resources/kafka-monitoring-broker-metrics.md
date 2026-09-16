# Apache Kafka — Monitoring: JMX & Broker / Controller Metrics

> **Nguồn (official):** https://kafka.apache.org/43/operations/monitoring/ (mục 6.8 Monitoring của Kafka Documentation)
> **Tuần:** 8 — Observability & Operations · **Loại:** Apache Kafka Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua HTTP + chuyển HTML → Markdown, có rút gọn) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- Broker dùng **Yammer Metrics**, client Java dùng **Kafka Metrics**; cả hai expose qua **JMX**. Remote JMX **tắt mặc định** → bật bằng biến môi trường `JMX_PORT`; bảo mật (auth/SSL) qua `KAFKA_JMX_OPTS`. Mọi metric `*-rate` đều có bản đếm tích luỹ `*-total`.
- **`UnderReplicatedPartitions`** (`kafka.server:type=ReplicaManager`) — số partition có |ISR| < |replicas|; bình thường **0**. >0 kéo dài = follower tụt / broker down.
- **`UnderMinIsrPartitionCount`** (|ISR| < `min.insync.replicas`) và **`AtMinIsrPartitionCount`** (|ISR| = min.isr) — bình thường **0**; UnderMinIsr > 0 nghĩa là producer `acks=all` sẽ bị `NotEnoughReplicasException`.
- **`OfflinePartitionsCount`** (`kafka.controller:type=KafkaController`) — partition không có leader → **mất availability**; bình thường **0**.
- **`ActiveControllerCount`** — chỉ **đúng 1** node trong cluster có giá trị 1; tổng ≠ 1 là sự cố controller.
- **`IsrShrinksPerSec` / `IsrExpandsPerSec`** — bình thường **0** ngoài lúc broker down/up; dao động liên tục = "ISR flapping" (mạng/GC/disk chậm, `replica.lag.time.max.ms`=30 s).
- **`RequestHandlerAvgIdlePercent`** (io thread) và **`NetworkProcessorAvgIdlePercent`** (network thread): giá trị 0–1, **lý tưởng > 0.3**; thấp hơn → tăng `num.io.threads` (mặc định 8) / `num.network.threads` (mặc định 3).
- **`TotalTimeMs`** per request `{Produce|FetchConsumer|FetchFollower}` = `RequestQueueTimeMs` + `LocalTimeMs` + `RemoteTimeMs` + `ResponseQueueTimeMs` + `ResponseSendTimeMs`. **`RemoteTimeMs` khác 0 với Produce khi `acks=-1`** (chờ follower); với Fetch = chờ đủ `fetch.min.bytes`/`fetch.max.wait.ms`.
- **`LeaderElectionRateAndTimeMs`** khác 0 khi broker fail; **`UncleanLeaderElectionsPerSec`** phải **0** (unclean = có thể mất data). **`LogFlushRateAndTimeMs`** đo fsync. **`PartitionCount`/`LeaderCount`** nên **đều nhau** giữa các broker.
- Throughput: `BytesInPerSec`, `BytesOutPerSec`, `MessagesInPerSec` (`BrokerTopicMetrics`, bỏ `topic=` để lấy tổng); `ReplicationBytesIn/OutPerSec` là traffic giữa broker; `BytesRejectedPerSec` = batch vượt `message.max.bytes`.
- KRaft: `kafka.server:type=raft-metrics` (current-state, current-leader, high-watermark, commit latency), `kafka.server:type=MetadataLoader,name=CurrentMetadataVersion`, controller `LastAppliedRecordLagMs`, `FencedBrokerCount`, `MetadataErrorCount`.
- Từ Kafka 4.x, KIP-1100 chuẩn hoá tên MBean thành `kafka.COMPONENT:type=...,name=...` (`kafka.server`, `kafka.network`, `kafka.controller`, `kafka.log`); các tên legacy vẫn giữ trong 4.3.

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Monitoring

Kafka uses Yammer Metrics for metrics reporting in the server. The Java clients use Kafka Metrics, a built-in metrics registry that minimizes transitive dependencies pulled into client applications. Both expose metrics via JMX and can be configured to report stats using pluggable stats reporters to hook up to your monitoring system.

All Kafka rate metrics have a corresponding cumulative count metric with suffix `-total`. For example, `records-consumed-rate` has a corresponding metric named `records-consumed-total`.

The easiest way to see the available metrics is to fire up jconsole and point it at a running kafka client or server; this will allow browsing all metrics with JMX.

### Security Considerations for Remote Monitoring using JMX

Apache Kafka disables remote JMX by default. You can enable remote monitoring using JMX by setting the environment variable `JMX_PORT` for processes started using the CLI or standard Java system properties to enable remote JMX programmatically. You must enable security when enabling remote JMX in production scenarios to ensure that unauthorized users cannot monitor or control your broker or application as well as the platform on which these are running. Note that authentication is disabled for JMX by default in Kafka and security configs must be overridden for production deployments by setting the environment variable `KAFKA_JMX_OPTS` for processes started using the CLI or by setting appropriate Java system properties.

### Graphing and alerting metrics (broker)

| Description | Mbean name | Normal value |
|---|---|---|
| Message in rate | `kafka.server:type=BrokerTopicMetrics,name=MessagesInPerSec,topic=([-.\w]+)` | Incoming message rate per topic. Omitting `topic=(...)` will yield the all-topic rate. |
| Byte in rate from clients | `kafka.server:type=BrokerTopicMetrics,name=BytesInPerSec,topic=([-.\w]+)` | Byte in (from the clients) rate per topic. |
| Byte in rate from other brokers | `kafka.server:type=BrokerTopicMetrics,name=ReplicationBytesInPerSec` | Byte in (from the other brokers) rate across all topics. |
| Byte out rate to clients | `kafka.server:type=BrokerTopicMetrics,name=BytesOutPerSec,topic=([-.\w]+)` | Byte out (to the clients) rate per topic. |
| Byte out rate to other brokers | `kafka.server:type=BrokerTopicMetrics,name=ReplicationBytesOutPerSec` | Byte out (to the other brokers) rate across all topics |
| Rejected byte rate | `kafka.server:type=BrokerTopicMetrics,name=BytesRejectedPerSec,topic=([-.\w]+)` | Rejected byte rate per topic, due to the record batch size being greater than max.message.bytes configuration. |
| Controller Event queue size | `kafka.controller:type=ControllerEventManager,name=EventQueueSize` | Size of the ControllerEventManager's queue. |
| Controller Event queue time | `kafka.controller:type=ControllerEventManager,name=EventQueueTimeMs` | Time that takes for any event (except the Idle event) to wait in the ControllerEventManager's queue before being processed |
| Request rate | `kafka.network:type=RequestMetrics,name=RequestsPerSec,request={Produce\|FetchConsumer\|FetchFollower},version=([0-9]+)` | |
| Error rate | `kafka.network:type=RequestMetrics,name=ErrorsPerSec,request=([-.\w]+),error=([-.\w]+)` | Number of errors in responses counted per-request-type, per-error-code. error=NONE indicates successful responses. |
| Produce request rate | `kafka.server:type=BrokerTopicMetrics,name=TotalProduceRequestsPerSec,topic=([-.\w]+)` | Produce request rate per topic. |
| Fetch request rate | `kafka.server:type=BrokerTopicMetrics,name=TotalFetchRequestsPerSec,topic=([-.\w]+)` | Fetch request (from clients or followers) rate per topic. |
| Failed produce request rate | `kafka.server:type=BrokerTopicMetrics,name=FailedProduceRequestsPerSec,topic=([-.\w]+)` | Failed Produce request rate per topic. |
| Failed fetch request rate | `kafka.server:type=BrokerTopicMetrics,name=FailedFetchRequestsPerSec,topic=([-.\w]+)` | Failed Fetch request (from clients or followers) rate per topic. |
| Request Queue Size | `kafka.network:type=RequestChannel,name=RequestQueueSize` | Size of the request queue. |
| Message validation failure rate due to no key specified for compacted topic | `kafka.server:type=BrokerTopicMetrics,name=NoKeyCompactedTopicRecordsPerSec` | 0 |
| Message validation failure rate due to incorrect crc checksum | `kafka.server:type=BrokerTopicMetrics,name=InvalidMessageCrcRecordsPerSec` | 0 |
| Message validation failure rate due to non-continuous offset or sequence number in batch | `kafka.server:type=BrokerTopicMetrics,name=InvalidOffsetOrSequenceRecordsPerSec` | 0 |
| Log flush rate and time | `kafka.log:type=LogFlushStats,name=LogFlushRateAndTimeMs` | |
| # of offline log directories | `kafka.log:type=LogManager,name=OfflineLogDirectoryCount` | 0 |
| Leader election rate | `kafka.controller:type=ControllerStats,name=LeaderElectionRateAndTimeMs` | non-zero when there are broker failures |
| Unclean leader election rate | `kafka.controller:type=ControllerStats,name=UncleanLeaderElectionsPerSec` | 0 |
| Election from Eligible leader replicas rate | `kafka.controller:type=ControllerStats,name=ElectionFromEligibleLeaderReplicasPerSec` | 0 |
| Is controller active on broker | `kafka.controller:type=KafkaController,name=ActiveControllerCount` | only one broker in the cluster should have 1 |
| Pending topic deletes | `kafka.controller:type=KafkaController,name=TopicsToDeleteCount` | |
| Pending replica deletes | `kafka.controller:type=KafkaController,name=ReplicasToDeleteCount` | |
| # of under replicated partitions (\|ISR\| < \|all replicas\|) | `kafka.server:type=ReplicaManager,name=UnderReplicatedPartitions` | 0 |
| # of under minIsr partitions (\|ISR\| < min.insync.replicas) | `kafka.server:type=ReplicaManager,name=UnderMinIsrPartitionCount` | 0 |
| # of at minIsr partitions (\|ISR\| = min.insync.replicas) | `kafka.server:type=ReplicaManager,name=AtMinIsrPartitionCount` | 0 |
| Producer Id counts | `kafka.server:type=ReplicaManager,name=ProducerIdCount` | Count of all producer ids created by transactional and idempotent producers in each replica on the broker |
| Partition counts | `kafka.server:type=ReplicaManager,name=PartitionCount` | mostly even across brokers |
| Offline Replica counts | `kafka.server:type=ReplicaManager,name=OfflineReplicaCount` | 0 |
| Leader replica counts | `kafka.server:type=ReplicaManager,name=LeaderCount` | mostly even across brokers |
| ISR shrink rate | `kafka.server:type=ReplicaManager,name=IsrShrinksPerSec` | If a broker goes down, ISR for some of the partitions will shrink. When that broker is up again, ISR will be expanded once the replicas are fully caught up. Other than that, the expected value for both ISR shrink rate and expansion rate is 0. |
| ISR expansion rate | `kafka.server:type=ReplicaManager,name=IsrExpandsPerSec` | See above |
| Failed ISR update rate | `kafka.server:type=ReplicaManager,name=FailedIsrUpdatesPerSec` | 0 |
| Max lag in messages btw follower and leader replicas | `kafka.server:type=ReplicaFetcherManager,name=MaxLag,clientId=Replica` | lag should be proportional to the maximum batch size of a produce request. |
| Lag in messages per follower replica | `kafka.server:type=FetcherLagMetrics,name=ConsumerLag,clientId=([-.\w]+),topic=([-.\w]+),partition=([0-9]+)` | lag should be proportional to the maximum batch size of a produce request. |
| Requests waiting in the producer purgatory | `kafka.server:type=DelayedOperationPurgatory,name=PurgatorySize,delayedOperation=Produce` | non-zero if ack=-1 is used |
| Requests waiting in the fetch purgatory | `kafka.server:type=DelayedOperationPurgatory,name=PurgatorySize,delayedOperation=Fetch` | size depends on fetch.wait.max.ms in the consumer |
| Request total time | `kafka.network:type=RequestMetrics,name=TotalTimeMs,request={Produce\|FetchConsumer\|FetchFollower}` | broken into queue, local, remote and response send time |
| Time the request waits in the request queue | `kafka.network:type=RequestMetrics,name=RequestQueueTimeMs,request={Produce\|FetchConsumer\|FetchFollower}` | |
| Time the request is processed at the leader | `kafka.network:type=RequestMetrics,name=LocalTimeMs,request={Produce\|FetchConsumer\|FetchFollower}` | |
| Time the request waits for the follower | `kafka.network:type=RequestMetrics,name=RemoteTimeMs,request={Produce\|FetchConsumer\|FetchFollower}` | non-zero for produce requests when ack=-1 |
| Time the request waits in the response queue | `kafka.network:type=RequestMetrics,name=ResponseQueueTimeMs,request={Produce\|FetchConsumer\|FetchFollower}` | |
| Time to send the response | `kafka.network:type=RequestMetrics,name=ResponseSendTimeMs,request={Produce\|FetchConsumer\|FetchFollower}` | |
| Number of messages the consumer lags behind the producer by. Published by the consumer, not broker. | `kafka.consumer:type=consumer-fetch-manager-metrics,client-id={client-id}` Attribute: `records-lag-max` | |
| The average fraction of time the network processors are idle | `kafka.network:type=SocketServer,name=NetworkProcessorAvgIdlePercent` | between 0 and 1, ideally > 0.3 |
| The average fraction of time the request handler threads are idle | `kafka.server:type=KafkaRequestHandlerPool,name=RequestHandlerAvgIdlePercent` | between 0 and 1, ideally > 0.3 |
| Bandwidth quota metrics per (user, client-id), user or client-id | `kafka.server:type={Produce\|Fetch},user=([-.\w]+),client-id=([-.\w]+)` | Two attributes. throttle-time indicates the amount of time in ms the client was throttled. Ideally = 0. byte-rate indicates the data produce/consume rate of the client in bytes/sec. |
| Request quota metrics per (user, client-id), user or client-id | `kafka.server:type=Request,user=([-.\w]+),client-id=([-.\w]+)` | throttle-time indicates the amount of time in ms the client was throttled. Ideally = 0. request-time indicates the percentage of time spent in broker network and I/O threads to process requests from client group. |
| Max time to load group metadata | `kafka.server:type=group-coordinator-metrics,name=partition-load-time-max` | maximum time, in milliseconds, it took to load offsets and group metadata from the consumer offset partitions loaded in the last 30 seconds |
| Number of reassigning partitions | `kafka.server:type=ReplicaManager,name=ReassigningPartitions` | The number of reassigning leader partitions on a broker. |
| Outgoing byte rate of reassignment traffic | `kafka.server:type=BrokerTopicMetrics,name=ReassignmentBytesOutPerSec` | 0; non-zero when a partition reassignment is in progress. |
| Incoming byte rate of reassignment traffic | `kafka.server:type=BrokerTopicMetrics,name=ReassignmentBytesInPerSec` | 0; non-zero when a partition reassignment is in progress. |
| Size of a partition on disk (in bytes) | `kafka.log:type=Log,name=Size,topic=([-.\w]+),partition=([0-9]+)` | The size of a partition on disk, measured in bytes. |
| Partition size as a percentage of retention bytes limit | `kafka.log:type=Log,name=RetentionSizeInPercent,topic=([-.\w]+),partition=([0-9]+)` | Returns 0 for topics with tiered storage enabled or when retention bytes is unlimited. May exceed 100% if retention cleanup is delayed. |
| Number of log segments in a partition | `kafka.log:type=Log,name=NumLogSegments,topic=([-.\w]+),partition=([0-9]+)` | |
| First offset in a partition | `kafka.log:type=Log,name=LogStartOffset,topic=([-.\w]+),partition=([0-9]+)` | |
| Last offset in a partition | `kafka.log:type=Log,name=LogEndOffset,topic=([-.\w]+),partition=([0-9]+)` | |
| Remaining logs to recover | `kafka.log:type=LogManager,name=remainingLogsToRecover` | The number of remaining logs for each log.dir to be recovered. |
| Log directory offline status | `kafka.log:type=LogManager,name=LogDirectoryOffline` | Indicates if a log directory is offline (1) or online (0). |

### Tiered Storage Monitoring (selected)

| Metric/Attribute name | Description | Mbean name |
|---|---|---|
| Remote Fetch Bytes Per Sec | Rate of bytes read from remote storage per topic. | `kafka.server:type=BrokerTopicMetrics,name=RemoteFetchBytesPerSec,topic=([-.\w]+)` |
| Remote Fetch Errors Per Sec | Rate of read errors from remote storage per topic. | `kafka.server:type=BrokerTopicMetrics,name=RemoteFetchErrorsPerSec,topic=([-.\w]+)` |
| Remote Copy Bytes Per Sec | Rate of bytes copied to remote storage per topic. | `kafka.server:type=BrokerTopicMetrics,name=RemoteCopyBytesPerSec,topic=([-.\w]+)` |
| Remote Copy Lag Bytes | Bytes which are eligible for tiering, but are not in remote storage yet. | `kafka.server:type=BrokerTopicMetrics,name=RemoteCopyLagBytes,topic=([-.\w]+)` |
| Remote Delete Lag Segments | Tiered segments which are eligible for deletion, but have not been deleted yet. | `kafka.server:type=BrokerTopicMetrics,name=RemoteDeleteLagSegments,topic=([-.\w]+)` |
| Remote Log Size Bytes | The total size of a remote log in bytes. | `kafka.server:type=BrokerTopicMetrics,name=RemoteLogSizeBytes,topic=([-.\w]+)` |
| RemoteLogReader Avg Idle Percent | Average idle percent of thread pool for processing remote storage read tasks | `org.apache.kafka.storage.internals.log:type=RemoteStorageThreadPool,name=RemoteLogReaderAvgIdlePercent` |
| Local Retention Size In Percent | Local log size as a percentage of the configured local.retention.bytes limit. | `kafka.log.remote:type=RemoteLogManager,name=LocalRetentionSizeInPercent,topic=([-.\w]+),partition=([0-9]+)` |

### KRaft Monitoring Metrics

The set of metrics that allow monitoring of the KRaft quorum and the metadata log. Note that some exposed metrics depend on the role of the node as defined by `process.roles`.

#### KRaft Quorum Monitoring Metrics (reported on both Controllers and Brokers)

| Metric/Attribute name | Description | Mbean name |
|---|---|---|
| Current State | The current state of this member; possible values are leader, candidate, voted, follower, unattached, observer. | `kafka.server:type=raft-metrics` |
| Current Leader | The current quorum leader's id; -1 indicates unknown. | `kafka.server:type=raft-metrics` |
| Current Epoch | The current quorum epoch. | `kafka.server:type=raft-metrics` |
| High Watermark | The high watermark maintained on this member; -1 if it is unknown. | `kafka.server:type=raft-metrics` |
| Log End Offset | The current raft log end offset. | `kafka.server:type=raft-metrics` |
| Average Commit Latency | The average time in milliseconds to commit an entry in the raft log. | `kafka.server:type=raft-metrics` |
| Average Election Latency | The average time in milliseconds spent on electing a new leader. | `kafka.server:type=raft-metrics` |
| Average Poll Idle Ratio | The ratio of time the Raft IO thread is idle as opposed to doing work | `kafka.server:type=raft-metrics` |
| Current Metadata Version | Outputs the feature level of the current effective metadata version. | `kafka.server:type=MetadataLoader,name=CurrentMetadataVersion` |
| Metadata Snapshot Load Count | The total number of times we have loaded a KRaft snapshot since the process was started. | `kafka.server:type=MetadataLoader,name=HandleLoadSnapshotCount` |
| Latest Metadata Snapshot Age | The interval in milliseconds since the latest snapshot that the node has generated. | `kafka.server:type=SnapshotEmitter,name=LatestSnapshotGeneratedAgeMs` |

#### KRaft Controller Monitoring Metrics

| Metric/Attribute name | Description | Mbean name |
|---|---|---|
| Active Controller Count | The number of Active Controllers on this node. Valid values are '0' or '1'. | `kafka.controller:type=KafkaController,name=ActiveControllerCount` |
| Event Queue Time Ms | A Histogram of the time in milliseconds that requests spent waiting in the Controller Event Queue. | `kafka.controller:type=ControllerEventManager,name=EventQueueTimeMs` |
| Fenced Broker Count | The number of fenced brokers as observed by this Controller. | `kafka.controller:type=KafkaController,name=FencedBrokerCount` |
| Active Broker Count | The number of active brokers as observed by this Controller. | `kafka.controller:type=KafkaController,name=ActiveBrokerCount` |
| Global Topic Count / Global Partition Count | The number of global topics / partitions as observed by this Controller. | `kafka.controller:type=KafkaController,name=GlobalTopicCount` / `GlobalPartitionCount` |
| Offline Partition Count | The number of offline topic partitions (non-internal) as observed by this Controller. | `kafka.controller:type=KafkaController,name=OfflinePartitionsCount` |
| Preferred Replica Imbalance Count | The count of topic partitions for which the leader is not the preferred leader. | `kafka.controller:type=KafkaController,name=PreferredReplicaImbalanceCount` |
| Metadata Error Count | The number of times this controller node has encountered an error during metadata log processing. | `kafka.controller:type=KafkaController,name=MetadataErrorCount` |
| Last Applied Record Lag Ms | The difference between now and the timestamp of the last record from the cluster metadata partition that was applied by the controller. For active Controllers the value of this lag is always zero. | `kafka.controller:type=KafkaController,name=LastAppliedRecordLagMs` |
| Timed-out Broker Heartbeat Count | The number of broker heartbeats that timed out on this controller since the process was started. | `kafka.controller:type=KafkaController,name=TimedOutBrokerHeartbeatCount` |
| Number Of New Controller Elections | Counts the number of times this node has seen a new controller elected. | `kafka.controller:type=KafkaController,name=NewActiveControllersCount` |

#### KRaft Broker Monitoring Metrics

| Metric/Attribute name | Description | Mbean name |
|---|---|---|
| Last Applied Record Offset | The offset of the last record from the cluster metadata partition that was applied by the broker | `kafka.server:type=broker-metadata-metrics` |
| Last Applied Record Lag Ms | The difference between now and the timestamp of the last record from the cluster metadata partition that was applied by the broker | `kafka.server:type=broker-metadata-metrics` |
| Metadata Load Error Count | The number of errors encountered by the BrokerMetadataListener while loading the metadata log | `kafka.server:type=broker-metadata-metrics` |
| Metadata Apply Error Count | The number of errors encountered by the BrokerMetadataPublisher while applying a new MetadataImage | `kafka.server:type=broker-metadata-metrics` |
