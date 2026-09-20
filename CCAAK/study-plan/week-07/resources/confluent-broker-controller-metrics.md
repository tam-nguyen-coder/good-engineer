# Confluent Platform — Broker and Controller Metrics: 3 alert tối thiểu

> **Nguồn (official):** https://docs.confluent.io/platform/current/kafka/broker-metrics.html
> **Tuần:** 7 — Observability + Troubleshooting playbook · **Loại:** Confluent Platform Docs
> ⚠️ Nội dung dưới đây được crawl tự động (HTTP → Markdown, có rút gọn) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- Confluent nêu thẳng **3 alert TỐI THIỂU** phải có trên mọi cluster — nhớ đúng 3 cái này là trả lời được câu "alert nào bắt buộc":
  1. **`ActiveControllerCount`** — *"Alert if the aggregated sum across all brokers in the cluster is anything other than 1"*. Chú ý chữ **aggregated sum**: alert trên **tổng cụm**, không alert trên từng node (mỗi node hợp lệ là 0 **hoặc** 1).
  2. **`OfflinePartitionsCount`** — *"Alert if value is greater than 0"*. Partition không có leader → **không đọc được và không ghi được**.
  3. **`UncleanLeaderElectionsPerSec`** — *"Should be 0"*. Khác 0 = đã có leader được bầu ngoài ISR → có khả năng **mất dữ liệu đã ack**.
- **`UnderReplicatedPartitions`** — `|ISR| < |current replicas|`; *"Alert if the value is greater than 0"*. Nhưng đây là alert **tạo ticket**, không phải alert gọi dậy: URP > 0 vài phút lúc rolling restart là **bình thường** → dùng `for:` để lọc.
- **`UnderMinIsrPartitionCount`** — `|ISR| < min.insync.replicas` → producer `acks=all` **đang bị chặn** (`NotEnoughReplicasException`). Khác URP ở chỗ: URP = giảm độ bền, UnderMinIsr = **mất khả năng ghi**.
- **`RequestHandlerAvgIdlePercent`** — *"Values are between 0 meaning all resources are used and 1 meaning all resources are available"*. Đây là thước đo tải broker trực tiếp nhất.
- `IsrShrinksPerSec` / `IsrExpandsPerSec`: khi một broker tắt thì ISR co lại, khi nó lên thì nở ra — *"Other than that, the expected value for both metrics is 0"*. Hai số dao động **cùng nhau** ngoài lúc up/down chính là ISR flapping.
- **KRaft metadata:** `LastAppliedRecordLagMs` (*"For active controllers the value of this lag is always zero"* — nên chỉ có ý nghĩa trên **standby controller và broker**), `MetadataErrorCount`, `MetadataLoaderIdleRatio` (broker áp dụng update của controller nhanh hay chậm).

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Broker and Controller Metrics

Confluent Platform reports a number of JMX metrics at the broker and controller level that you can monitor to troubleshoot issues with your cluster.

### Minimum recommended monitoring and alerting

At a minimum, you should monitor and set alerts on the following metrics:

**ActiveControllerCount**

The number of active controllers in the cluster. Valid values are '0' or '1'. Alert if the aggregated sum across all brokers in the cluster is anything other than 1 because there should be exactly one controller per cluster.

```
kafka.controller:type=KafkaController,name=ActiveControllerCount
```

**OfflinePartitionsCount**

The number of partitions that don't have an active leader and are therefore not writable or readable. Alert if value is greater than 0.

```
kafka.controller:type=KafkaController,name=OfflinePartitionsCount
```

**UncleanLeaderElectionsPerSec**

The unclean broker leader election rate. Should be 0.

```
kafka.controller:type=ControllerStats,name=UncleanLeaderElectionsPerSec
```

### Additional replication health metrics

**UnderReplicatedPartitions**

The number of under-replicated partitions (`| ISR | < | current replicas |`). Alert if the value is greater than 0.

```
kafka.server:type=ReplicaManager,name=UnderReplicatedPartitions
```

**UnderMinIsrPartitionCount**

The number of partitions whose in-sync replicas count is less than `min.insync.replicas`. Producers using `acks=all` cannot write to these partitions.

```
kafka.server:type=ReplicaManager,name=UnderMinIsrPartitionCount
```

**IsrShrinksPerSec / IsrExpandsPerSec**

The rate at which the pool of in-sync replicas (ISR) shrinks / expands. When a broker is brought down, the ISR for some partitions shrinks. When that broker is up again, the ISR is expanded once the replicas are fully caught up. Other than that, the expected value for both metrics is 0.

### Request handling

**RequestHandlerAvgIdlePercent**

The average fraction of time the request handler threads are idle. Values are between `0` meaning all resources are used and `1` meaning all resources are available.

```
kafka.server:type=KafkaRequestHandlerPool,name=RequestHandlerAvgIdlePercent
```

**NetworkProcessorAvgIdlePercent**

The average fraction of time the network processor threads are idle.

```
kafka.network:type=SocketServer,name=NetworkProcessorAvgIdlePercent
```

### KRaft metadata metrics

**LastAppliedRecordLagMs**

The difference between the current time and the timestamp of the last record from the cluster metadata partition that was applied. For active controllers the value of this lag is always zero.

```
kafka.controller:type=KafkaController,name=LastAppliedRecordLagMs
```

**MetadataErrorCount**

The number of times this node has encountered an error during metadata log processing.

```
kafka.controller:type=KafkaController,name=MetadataErrorCount
```

**MetadataLoaderIdleRatio**

The ratio of time the broker's metadata loader spends idle. A low value means the broker is struggling to keep up with the controller's metadata updates.
