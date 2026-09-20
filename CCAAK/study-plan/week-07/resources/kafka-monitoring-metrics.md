# Apache Kafka 4.3 — Monitoring: metric đèn đỏ, 5 pha request, KRaft quorum

> **Nguồn (official):** https://kafka.apache.org/43/operations/monitoring/
> **Tuần:** 7 — Observability + Troubleshooting playbook · **Loại:** Apache Kafka Docs (§6.8 Monitoring)
> ⚠️ Nội dung dưới đây được crawl tự động (HTTP → Markdown, có rút gọn) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- Broker dùng **Yammer Metrics**, client Java dùng **Kafka Metrics** — cả hai expose qua **JMX**. Remote JMX **tắt mặc định**, bật bằng biến môi trường **`JMX_PORT`**; production **bắt buộc** bật auth qua **`KAFKA_JMX_OPTS`** vì JMX mặc định **không xác thực**. Mọi metric `*-rate` đều có bản đếm tích luỹ `*-total`.
- **4 metric đèn đỏ + ngưỡng docs ghi thẳng:** `UnderReplicatedPartitions` = **0**, `UnderMinIsrPartitionCount` = **0**, `AtMinIsrPartitionCount` = **0**, `OfflinePartitionsCount` = **0**, và `ActiveControllerCount` — *"Only one broker should have 1"* nên **tổng toàn cluster phải = 1**.
- `IsrShrinksPerSec` / `IsrExpandsPerSec` bình thường = **0** *"except during broker failures"* — dao động liên tục ngoài lúc broker up/down chính là **ISR flapping**.
- `UncleanLeaderElectionsPerSec` phải **= 0**. Khác 0 nghĩa là ai đó đã bật `unclean.leader.election.enable=true` và cluster **đã chấp nhận mất dữ liệu** để đổi lấy availability.
- `RequestHandlerAvgIdlePercent` (io thread) và `NetworkProcessorAvgIdlePercent` (network thread): docs ghi **"Ideally > 0.3"** — dưới ngưỡng thì tăng `num.io.threads` (mặc định **8**) / `num.network.threads` (mặc định **3**).
- `PartitionCount` và `LeaderCount` phải **"mostly even across brokers"** — lệch nghĩa là cần preferred leader election hoặc reassignment.
- **`TotalTimeMs` tách 5 pha** (cùng label `request={Produce|FetchConsumer|FetchFollower}`): `RequestQueueTimeMs` (chờ io thread) + `LocalTimeMs` (leader xử lý) + `RemoteTimeMs` (*"Follower Wait Time"* — chờ follower ack khi `acks=all`, hoặc chờ đủ `fetch.min.bytes`) + `ResponseQueueTimeMs` (chờ network thread) + `ResponseSendTimeMs` (gửi response). Mỗi pha trỏ về **một nút thắt khác nhau**.
- **KRaft quorum metrics** (`kafka.server:type=raft-metrics`): `current-state` (leader/candidate/voted/follower/unattached/**observer**), `current-leader` (**-1 nếu chưa biết**), `current-epoch`, `high-watermark`, `log-end-offset`, `commit-latency-avg/max`, `election-latency-avg/max`.
- **KRaft controller metrics** (`kafka.controller:type=KafkaController`): `ActiveControllerCount` (**valid values 0 hoặc 1** trên mỗi node), `FencedBrokerCount`, `ActiveBrokerCount`, `OfflinePartitionsCount`, `MetadataErrorCount`, `LastAppliedRecordLagMs`, `TimedOutBrokerHeartbeatCount` — metric cuối là dấu hiệu trực tiếp của broker mất heartbeat tới controller.
- **KRaft broker metrics** (`kafka.server:type=broker-metadata-metrics`): `last-applied-record-offset`, `last-applied-record-lag-ms`, `metadata-load-error-count` — broker tụt metadata sẽ phục vụ client bằng metadata **cũ**.
- `kafka.server:type=MetadataLoader,name=CurrentMetadataVersion` cho feature level của `metadata.version` đang hiệu lực — dùng để xác minh rolling upgrade đã finalize chưa. Consumer client: `records-lag-max` (lag lớn nhất theo **fetch position**) và **`records-lead-min`** (khoảng cách tới log start offset) — `records-lead-min` tiến về **0** nghĩa là retention sắp xoá record trước khi consumer kịp đọc.
- Kafka Streams có 3 mức ghi metric qua `metrics.recording.level`: `info` / `debug` / `trace`.

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Monitoring

Kafka uses Yammer Metrics for metrics reporting in the server. The Java clients use Kafka Metrics, a built-in metrics registry that minimizes transitive dependencies pulled into client applications. Both expose metrics via JMX and can be configured to report stats using pluggable stats reporters to hook up to your monitoring system.

All Kafka rate metrics have a corresponding cumulative count metric with suffix `-total`. For example, `records-consumed-rate` has a corresponding metric named `records-consumed-total`.

The easiest way to see the available metrics is to fire up jconsole and point it at a running kafka client or server; this will allow browsing all metrics with JMX.

### Security Considerations for Remote Monitoring using JMX

Apache Kafka disables remote JMX by default. You can enable remote monitoring using JMX by setting the environment variable `JMX_PORT` for processes started using the CLI or standard Java system properties to enable remote JMX programmatically.

You must enable security when enabling remote JMX in production scenarios to ensure that unauthorized users cannot monitor or control your broker or application as well as the platform on which these are running. Note that authentication is disabled for JMX by default in Kafka and security configs must be overridden for production deployments by setting the environment variable `KAFKA_JMX_OPTS` for processes started using the CLI or by setting appropriate Java system properties.

### Graphing and alerting: the metrics that matter

| Description | Mbean name | Normal value |
|---|---|---|
| Under-replicated partitions | `kafka.server:type=ReplicaManager,name=UnderReplicatedPartitions` | 0 |
| Under min ISR partition count | `kafka.server:type=ReplicaManager,name=UnderMinIsrPartitionCount` | 0 |
| At min ISR partition count | `kafka.server:type=ReplicaManager,name=AtMinIsrPartitionCount` | 0 |
| Partition counts | `kafka.server:type=ReplicaManager,name=PartitionCount` | mostly even across brokers |
| Leader replica counts | `kafka.server:type=ReplicaManager,name=LeaderCount` | mostly even across brokers |
| ISR shrink rate | `kafka.server:type=ReplicaManager,name=IsrShrinksPerSec` | If a broker goes down, ISR for some of the partitions will shrink. When that broker is up again, ISR will be expanded once the replicas are fully caught up. Other than that, the expected value for both ISR shrink rate and expansion rate is 0. |
| ISR expansion rate | `kafka.server:type=ReplicaManager,name=IsrExpandsPerSec` | See above |
| Leader election rate | `kafka.controller:type=ControllerStats,name=LeaderElectionRateAndTimeMs` | non-zero when there are broker failures |
| Unclean leader election rate | `kafka.controller:type=ControllerStats,name=UncleanLeaderElectionsPerSec` | 0 |
| Is controller active on broker | `kafka.controller:type=KafkaController,name=ActiveControllerCount` | only one broker in the cluster should have 1 |
| Log flush rate and time | `kafka.log:type=LogFlushStats,name=LogFlushRateAndTimeMs` | — |
| Request handler average idle percentage | `kafka.server:type=KafkaRequestHandlerPool,name=RequestHandlerAvgIdlePercent` | between 0 and 1, ideally > 0.3 |
| The average fraction of time the network processors are idle | `kafka.network:type=SocketServer,name=NetworkProcessorAvgIdlePercent` | between 0 and 1, ideally > 0.3 |

### Request time broken down by stage

| Description | Mbean name |
|---|---|
| Total time in ms to serve the specified request | `kafka.network:type=RequestMetrics,name=TotalTimeMs,request={Produce|FetchConsumer|FetchFollower}` |
| Time the request waits in the request queue | `kafka.network:type=RequestMetrics,name=RequestQueueTimeMs,request={Produce|FetchConsumer|FetchFollower}` |
| Time the request is processed at the leader | `kafka.network:type=RequestMetrics,name=LocalTimeMs,request={Produce|FetchConsumer|FetchFollower}` |
| Time the request waits for the follower | `kafka.network:type=RequestMetrics,name=RemoteTimeMs,request={Produce|FetchConsumer|FetchFollower}` |
| Time the request waits in the response queue | `kafka.network:type=RequestMetrics,name=ResponseQueueTimeMs,request={Produce|FetchConsumer|FetchFollower}` |
| Time to send the response | `kafka.network:type=RequestMetrics,name=ResponseSendTimeMs,request={Produce|FetchConsumer|FetchFollower}` |

Note: `RemoteTimeMs` is non-zero for produce requests when `acks=-1` (the leader waits for the followers), and for fetch requests it reflects the purgatory wait for `fetch.min.bytes` / `fetch.max.wait.ms`.

### KRaft Quorum Monitoring Metrics (controllers and brokers)

| Metric | Description | Mbean name |
|---|---|---|
| Current State | The current state of this member; possible values are leader, candidate, voted, follower, unattached, observer. | `kafka.server:type=raft-metrics,name=current-state` |
| Current Leader | The current quorum leader's id; -1 indicates unknown. | `kafka.server:type=raft-metrics,name=current-leader` |
| Current Epoch | The current quorum epoch. | `kafka.server:type=raft-metrics,name=current-epoch` |
| High Watermark | The high watermark maintained on this member; -1 if it is unknown. | `kafka.server:type=raft-metrics,name=high-watermark` |
| Log End Offset | The current raft log end offset. | `kafka.server:type=raft-metrics,name=log-end-offset` |
| Average Commit Latency | The average time in milliseconds to commit an entry in the raft log. | `kafka.server:type=raft-metrics,name=commit-latency-avg` |
| Maximum Commit Latency | The maximum time in milliseconds to commit an entry in the raft log. | `kafka.server:type=raft-metrics,name=commit-latency-max` |
| Average Election Latency | The average time in milliseconds spent on electing a new leader. | `kafka.server:type=raft-metrics,name=election-latency-avg` |
| Current Metadata Version | Outputs the feature level of the current effective metadata version. | `kafka.server:type=MetadataLoader,name=CurrentMetadataVersion` |

### KRaft Controller Monitoring Metrics

| Metric | Description | Mbean name |
|---|---|---|
| Active Controller Count | The number of active controllers on this node. Valid values are '0' or '1'. | `kafka.controller:type=KafkaController,name=ActiveControllerCount` |
| Fenced Broker Count | The number of fenced brokers as observed by this Controller. | `kafka.controller:type=KafkaController,name=FencedBrokerCount` |
| Active Broker Count | The number of active brokers as observed by this Controller. | `kafka.controller:type=KafkaController,name=ActiveBrokerCount` |
| Offline Partition Count | The number of non-internal partitions that the Controller believes to be offline. | `kafka.controller:type=KafkaController,name=OfflinePartitionsCount` |
| Metadata Error Count | The number of times this controller node has encountered an error during metadata log processing. | `kafka.controller:type=KafkaController,name=MetadataErrorCount` |
| Last Applied Record Lag Ms | The difference between now and the timestamp of the last record from the cluster metadata partition that was applied. For active controllers the value of this lag is always zero. | `kafka.controller:type=KafkaController,name=LastAppliedRecordLagMs` |
| Timed Out Broker Heartbeat Count | The number of broker heartbeats that timed out on this controller since the process was started. | `kafka.controller:type=KafkaController,name=TimedOutBrokerHeartbeatCount` |

### KRaft Broker Monitoring Metrics

| Metric | Description | Mbean name |
|---|---|---|
| Last Applied Record Offset | The offset of the last record from the cluster metadata partition that was applied by the broker. | `kafka.server:type=broker-metadata-metrics,name=last-applied-record-offset` |
| Last Applied Record Lag Ms | The difference between now and the timestamp of the last record from the cluster metadata partition that was applied by the broker. | `kafka.server:type=broker-metadata-metrics,name=last-applied-record-lag-ms` |
| Metadata Load Error Count | The number of errors encountered by the BrokerMetadataListener while loading the metadata log. | `kafka.server:type=broker-metadata-metrics,name=metadata-load-error-count` |

### Consumer Fetch Metrics

| Metric | Description | Mbean name |
|---|---|---|
| records-lag-max | The maximum lag in terms of number of records for any partition in this window. | `kafka.consumer:type=consumer-fetch-manager-metrics,client-id=([-.\w]+)` |
| records-lead-min | The minimum lead in terms of number of records for any partition in this window. | `kafka.consumer:type=consumer-fetch-manager-metrics,client-id=([-.\w]+)` |
| bytes-consumed-rate | The average number of bytes consumed per second. | `kafka.consumer:type=consumer-fetch-manager-metrics,client-id=([-.\w]+)` |
| fetch-latency-avg / fetch-latency-max | The average / maximum time taken for a fetch request. | `kafka.consumer:type=consumer-fetch-manager-metrics,client-id=([-.\w]+)` |

### Common monitoring metrics for producer/consumer/connect/streams

The following metrics are available on producer/consumer/connector/streams instances:

| Metric | Description |
|---|---|
| connection-close-rate | Connections closed per second in the window. |
| connection-creation-rate | New connections established per second in the window. |
| network-io-rate | The average number of network operations (reads or writes) on all connections per second. |
| outgoing-byte-rate | The average number of outgoing bytes sent per second to all servers. |
| incoming-byte-rate | Bytes/second read off all sockets. |
| request-rate | The average number of requests sent per second. |
| response-rate | Responses received per second. |

Note: Kafka Streams metrics have three recording levels configured with `metrics.recording.level`: `info`, `debug` and `trace`.
