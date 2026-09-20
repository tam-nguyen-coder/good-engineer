# Apache Kafka Monitoring — metric làm **tín hiệu tuning** cho replication, thread và quota

> **Nguồn (official):** https://kafka.apache.org/43/operations/monitoring/
> **Tuần:** 3 — Cluster Config II: durability, quotas, throughput tuning · **Loại:** Apache Kafka 4.3 Documentation (Operations → Monitoring)
> ⚠️ Nội dung dưới đây được crawl tự động từ trang gốc và **chỉ giữ những metric dùng để QUYẾT ĐỊNH chỉnh config trong Tuần 3** (toàn bộ hệ thống metric và alerting ở Tuần 7) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- Hai ngưỡng thread phải thuộc: **`RequestHandlerAvgIdlePercent`** và **`NetworkProcessorAvgIdlePercent`**, cả hai nằm trong khoảng **0–1**, **lý tưởng > 0.3** (nguyên văn docs: "between 0 and 1, ideally > 0.3"). Dưới ngưỡng → tăng `num.io.threads` / `num.network.threads` tương ứng.
- Phân biệt **3 metric ISR** dễ nhầm:
  - `UnderReplicatedPartitions` = **|ISR| < |all replicas|** → có replica đang tụt, **ghi vẫn OK**.
  - `UnderMinIsrPartitionCount` = **|ISR| < `min.insync.replicas`** → **`acks=all` ĐANG BỊ TỪ CHỐI**. Đây mới là báo động đỏ.
  - `AtMinIsrPartitionCount` = **|ISR| = `min.insync.replicas`** → đang ở ngưỡng, **mất thêm 1 replica là ngừng ghi**. Cảnh báo sớm.
  - Cả ba đều **kỳ vọng 0**.
- `IsrShrinksPerSec` / `IsrExpandsPerSec`: "Other than that, the expected value for both ISR shrink rate and expansion rate is **0**." Dao động liên tục (flapping) ⇒ nghi **GC pause** hoặc **disk latency**, chứ không phải lý do để nâng `replica.lag.time.max.ms`.
- `UncleanLeaderElectionsPerSec` kỳ vọng **0** — khác 0 nghĩa là **đã có dữ liệu bị mất**.
- Metric riêng cho ELR: **`kafka.controller:type=ControllerStats,name=ElectionFromEligibleLeaderReplicasPerSec`**, kỳ vọng **0**. Khác 0 = ELR vừa cứu bạn khỏi một lần offline partition.
- `PreferredReplicaImbalanceCount` = số partition **leader không phải preferred leader** → đúng con số để xác nhận `auto.leader.rebalance.enable` đã kéo leader về chỗ cũ chưa sau khi restart broker.
- `TotalTimeMs` tách thành 5 pha: **queue → local → remote → response queue → response send**. Với Produce, **`RemoteTimeMs` cao là bình thường khi `acks=all`** ("non-zero for produce requests when ack=-1") vì đó là thời gian chờ follower. Đừng vội chỉnh thread khi thấy `RemoteTimeMs` cao.
- Quota: MBean phía broker **`kafka.server:type={Produce|Fetch},user=...,client-id=...`** với thuộc tính `throttle-time` (**lý tưởng 0**) và `byte-rate`; **`kafka.server:type=Request,...`** với `throttle-time` + `request-time`. Phía client: `produce-throttle-time-avg` / `fetch-throttle-time-avg`.
- `ReplicationBytesInPerSec` = lưu lượng **từ broker khác** (replication), tách khỏi `BytesInPerSec` (**từ client**). Khi tăng `num.replica.fetchers`, chính con số này phải nhảy lên.
- `kafka.server:type=ReplicaFetcherManager,name=MaxLag,clientId=Replica` = lag tối đa (theo message) giữa follower và leader — "lag should be proportional to the maximum batch size of a produce request".

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Replication & ISR

| Description | MBean name | Normal value |
|---|---|---|
| # of under replicated partitions (`\|ISR\| < \|all replicas\|`) | `kafka.server:type=ReplicaManager,name=UnderReplicatedPartitions` | **0** |
| # of under minIsr partitions (`\|ISR\| < min.insync.replicas`) | `kafka.server:type=ReplicaManager,name=UnderMinIsrPartitionCount` | **0** |
| # of at minIsr partitions (`\|ISR\| = min.insync.replicas`) | `kafka.server:type=ReplicaManager,name=AtMinIsrPartitionCount` | **0** |
| Offline Replica counts | `kafka.server:type=ReplicaManager,name=OfflineReplicaCount` | **0** |
| Partition counts | `kafka.server:type=ReplicaManager,name=PartitionCount` | mostly even across brokers |
| Leader replica counts | `kafka.server:type=ReplicaManager,name=LeaderCount` | mostly even across brokers |
| ISR shrink rate | `kafka.server:type=ReplicaManager,name=IsrShrinksPerSec` | "If a broker goes down, ISR for some of the partitions will shrink. When that broker is up again, ISR will be expanded once the replicas are fully caught up. **Other than that, the expected value for both ISR shrink rate and expansion rate is 0.**" |
| ISR expansion rate | `kafka.server:type=ReplicaManager,name=IsrExpandsPerSec` | See above |
| Failed ISR update rate | `kafka.server:type=ReplicaManager,name=FailedIsrUpdatesPerSec` | **0** |
| Max lag in messages btw follower and leader replicas | `kafka.server:type=ReplicaFetcherManager,name=MaxLag,clientId=Replica` | "lag should be proportional to the maximum batch size of a produce request" |
| Lag in messages per follower replica | `kafka.server:type=FetcherLagMetrics,name=ConsumerLag,clientId=([-.\w]+),topic=([-.\w]+),partition=([0-9]+)` | "lag should be proportional to the maximum batch size of a produce request" |

### Controller & leader election

| Description | MBean name | Normal value |
|---|---|---|
| Leader election rate | `kafka.controller:type=ControllerStats,name=LeaderElectionRateAndTimeMs` | non-zero when there are broker failures |
| **Unclean leader election rate** | `kafka.controller:type=ControllerStats,name=UncleanLeaderElectionsPerSec` | **0** |
| **Election from Eligible leader replicas rate** | `kafka.controller:type=ControllerStats,name=ElectionFromEligibleLeaderReplicasPerSec` | **0** |
| Is controller active on broker | `kafka.controller:type=KafkaController,name=ActiveControllerCount` | "only one broker in the cluster should have 1" |
| Offline Partition Count | `kafka.controller:type=KafkaController,name=OfflinePartitionsCount` | "The number of offline topic partitions (non-internal) as observed by this Controller." |
| **Preferred Replica Imbalance Count** | `kafka.controller:type=KafkaController,name=PreferredReplicaImbalanceCount` | "The count of topic partitions for which the leader is not the preferred leader." |

### Thread & request pipeline

| Description | MBean name | Normal value |
|---|---|---|
| **The average fraction of time the request handler threads are idle** | `kafka.server:type=KafkaRequestHandlerPool,name=RequestHandlerAvgIdlePercent` | **between 0 and 1, ideally > 0.3** |
| **The average fraction of time the network processors are idle** | `kafka.network:type=SocketServer,name=NetworkProcessorAvgIdlePercent` | **between 0 and 1, ideally > 0.3** |
| Request total time | `kafka.network:type=RequestMetrics,name=TotalTimeMs,request={Produce\|FetchConsumer\|FetchFollower}` | "broken into queue, local, remote and response send time" |
| Time the request waits in the request queue | `kafka.network:type=RequestMetrics,name=RequestQueueTimeMs,request={...}` | — |
| Time the request is processed at the leader | `kafka.network:type=RequestMetrics,name=LocalTimeMs,request={...}` | — |
| **Time the request waits for the follower** | `kafka.network:type=RequestMetrics,name=RemoteTimeMs,request={...}` | **"non-zero for produce requests when ack=-1"** |
| Time the request waits in the response queue | `kafka.network:type=RequestMetrics,name=ResponseQueueTimeMs,request={...}` | — |
| Time to send the response | `kafka.network:type=RequestMetrics,name=ResponseSendTimeMs,request={...}` | — |
| Requests waiting in the producer purgatory | `kafka.server:type=DelayedOperationPurgatory,name=PurgatorySize,delayedOperation=Produce` | **"non-zero if ack=-1 is used"** |
| Requests waiting in the fetch purgatory | `kafka.server:type=DelayedOperationPurgatory,name=PurgatorySize,delayedOperation=Fetch` | "size depends on `fetch.wait.max.ms` in the consumer" |

### Throughput

| Description | MBean name |
|---|---|
| Message in rate | `kafka.server:type=BrokerTopicMetrics,name=MessagesInPerSec,topic=([-.\w]+)` |
| **Byte in rate from clients** | `kafka.server:type=BrokerTopicMetrics,name=BytesInPerSec,topic=([-.\w]+)` |
| **Byte in rate from other brokers** | `kafka.server:type=BrokerTopicMetrics,name=ReplicationBytesInPerSec` — "Byte in (from the other brokers) rate across all topics." |
| Failed produce request rate | `kafka.server:type=BrokerTopicMetrics,name=FailedProduceRequestsPerSec,topic=([-.\w]+)` |
| Reassignment byte-in rate | `kafka.server:type=BrokerTopicMetrics,name=ReassignmentBytesInPerSec` |

### Quota / throttling

| Description | MBean name | Ghi chú nguyên văn |
|---|---|---|
| Bandwidth quota metrics per (user, client-id), user or client-id | `kafka.server:type={Produce\|Fetch},user=([-.\w]+),client-id=([-.\w]+)` | "Two attributes. `throttle-time` indicates the amount of time in ms the client was throttled. **Ideally = 0.** `byte-rate` indicates the data produce/consume rate of the client in bytes/sec. For (user, client-id) quotas, both user and client-id are specified. If per-client-id quota is applied to the client, user is not specified. If per-user quota is applied, client-id is not specified." |
| Request quota metrics per (user, client-id), user or client-id | `kafka.server:type=Request,user=([-.\w]+),client-id=([-.\w]+)` | "Two attributes. `throttle-time` … Ideally = 0. `request-time` indicates the percentage of time spent in broker network and I/O threads to process requests from client group." |
| Requests exempt from throttling | `kafka.server:type=Request` | "`exempt-throttle-time` indicates the percentage of time spent in broker network and I/O threads to process requests that are exempt from throttling." |
| Producer client metric | `produce-throttle-time-avg` / `produce-throttle-time-max` | "The average / maximum time in ms a request was throttled by a broker" |
| Consumer client metric | `fetch-throttle-time-avg` / `fetch-throttle-time-max` | "The average / maximum throttle time in ms" |

### Bảng phản xạ rút ra từ các metric trên (tự tổng hợp)

| Metric bất thường | Kết luận | Config đụng tới |
|---|---|---|
| `RequestHandlerAvgIdlePercent` < 0.3 | thiếu I/O thread | tăng `num.io.threads` (cluster-wide, không cần restart) |
| `NetworkProcessorAvgIdlePercent` < 0.3 | thiếu network thread | tăng `num.network.threads` (cluster-wide) |
| `UnderReplicatedPartitions` > 0 kéo dài, broker đã sống | follower bắt kịp chậm | tăng `num.replica.fetchers` (cluster-wide) |
| `UnderMinIsrPartitionCount` > 0 | `acks=all` **đang bị từ chối** | khôi phục replica; **không** hạ `min.insync.replicas` trong hoảng loạn |
| `AtMinIsrPartitionCount` > 0 | sát ngưỡng, mất thêm 1 replica là ngừng ghi | cảnh báo sớm, điều tra broker chậm |
| `IsrShrinksPerSec`/`IsrExpandsPerSec` dao động | GC pause hoặc disk chậm | GC log, `KAFKA_HEAP_OPTS`, disk latency — **không** chỉnh `replica.lag.time.max.ms` trước |
| `UncleanLeaderElectionsPerSec` > 0 | **đã mất dữ liệu** | kiểm tra ai bật `unclean.leader.election.enable` |
| `ElectionFromEligibleLeaderReplicasPerSec` > 0 | ELR vừa cứu một partition | bình thường, nhưng nghĩa là ISR đã từng co về rỗng |
| `PreferredReplicaImbalanceCount` > 0 lâu | leader chưa về preferred | chờ `leader.imbalance.check.interval.seconds` (300 s) hoặc chạy `kafka-leader-election.sh --election-type preferred` |
| `throttle-time` > 0 trên MBean `Produce`/`Fetch`/`Request` | **quota đang chặn**, không phải lỗi | nâng quota hoặc giảm tốc client |
| `RemoteTimeMs` (Produce) cao, các pha khác thấp | chờ follower ack | bình thường với `acks=all`; kiểm tra follower/`num.replica.fetchers` |
