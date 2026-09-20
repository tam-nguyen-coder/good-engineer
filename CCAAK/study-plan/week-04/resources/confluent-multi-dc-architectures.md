# Confluent Platform — Kiến trúc multi-datacenter, RPO/RTO và stretch cluster

> **Nguồn (official):** https://docs.confluent.io/platform/current/multi-dc-deployments/multi-region-architectures.html · https://docs.confluent.io/platform/current/multi-dc-deployments/index.html · https://docs.confluent.io/platform/current/multi-dc-deployments/multi-region.html
> **Tuần:** 4 — Deployment Architecture · **Loại:** Confluent Platform Docs
> ⚠️ Nội dung dưới đây được crawl tự động (HTTP → Markdown, có rút gọn) — luôn đối chiếu link gốc để đầy đủ và cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- **RPO** = *"at which point in the data's history does the failover need to resume from?"* → **mất bao nhiêu dữ liệu**. **RTO** = *"how much time can elapse while a failover takes place?"* → **mất bao lâu để lên lại**. Mọi câu hỏi DR của CCAAK quy về 2 chữ này.
- **Stretch cluster = MỘT cluster trải nhiều DC** → replication là **đồng bộ** (chính là ISR) → **RPO = 0** và **RTO ≈ 0**. Giá phải trả: cần mạng **ổn định, độ trễ dưới 100 ms** (docs khuyên "dark fiber"), và mọi ghi `acks=all` phải chờ replica ở DC khác.
- **2 DC là KHÔNG đủ cho stretch cluster** — quorum số chẵn, mất 1 DC là mất đa số. Giải pháp là **"2.5 DC"**: 2 DC chạy broker + controller đầy đủ, **DC thứ ba chỉ chạy controller** để giữ quorum. Đây là kiến trúc đề rất hay hỏi.
- **Stretch 3 DC**: node rải đều 3 DC, quorum controller trải cả 3 → RPO = 0, RTO ≈ 0. Ví dụ địa lý docs đưa ra: các bang lân cận (NY, NJ, Boston).
- **Cluster tách rời + replication** (active-passive, active-active, hub-and-spoke) là **bất đồng bộ** → **RPO > 0, RTO > 0** dù dùng MM2 hay Cluster Linking. Dùng khi DC *"far apart, have high network latency, or have unpredictable network latency"*.
- Bảng so sánh chính thức của Confluent: **Cluster Linking** RPO > 0 / RTO > 0 · **MirrorMaker** (KIP-382) RPO > 0 / RTO > 0 · **Multi-Region Clusters (MRC)** RPO = 0 **hoặc** > 0, RTO ≥ 0 — MRC **chỉ có ở Confluent Platform**.
- **Active-active** (`A->B, B->A`) đòi ứng dụng chạy ở **mọi** DC; RTO gần 0 nhưng RPO > 0 và phải xử lý topic hai chiều (`orders` + `B.orders`). **Active-passive** (`A->B`) đơn giản hơn nhưng RTO > 0 vì phải bật ứng dụng lên ở đích.
- **Aggregation / hub-and-spoke** (`A->K, B->K, C->K`): nhiều cluster vùng gom về một cluster trung tâm để phân tích toàn cục. Nếu `DefaultReplicationPolicy` thì cluster trung tâm có `A.orders`, `B.orders`, `C.orders` — nhìn tên là biết nguồn.
- **Observer** (Confluent MRC) là replica **không nằm trong ISR**: replicate bất đồng bộ qua vùng xa nên `acks=all` không phải chờ nó, nhưng có thể được **tự động promote** vào ISR khi suy giảm (`observerPromotionPolicy`: `under-min-isr` mặc định từ placement version 2, `under-replicated`, `leader-is-observer`).
- Với cấu hình `min.insync.replicas=3` + "2 replica và 1 observer mỗi vùng", stretch 2.5 DC đạt **RPO = 0**.

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Key definitions

**RPO (Recovery Point Objective):** "In the event of failure, at which point in the data's history does the failover need to resume from?"

**RTO (Recovery Time Objective):** "In the event of failure, how much time can elapse while a failover takes place?"

### Available multi-datacenter solutions

1. **Cluster Linking** — "directly connect clusters together and mirror topics from one cluster to another without the need for Connect."
2. **Confluent Replicator** — "allows two distinct Kafka clusters to replicate data in either active-passive or active-active architectures."
3. **Built-in Multi-Region Replication (MRC)** — "deploy Confluent Platform across regional datacenters with automated client failover... enables synchronous and asynchronous replication by topic, and all the replication is offset preserving" (Confluent Platform only).

### Architecture patterns

#### Stretched 3-datacenter cluster

A single KRaft cluster spanning three datacenters with low-latency, stable networking (sub-100 ms). Confluent Server nodes are distributed evenly across the locations, forming one unified cluster.

- RPO = 0 and RTO ≈ 0 are possible.
- Requires a "stable, low-latency network, usually a 'dark fiber' network".
- Node placement: distributed evenly across three datacenters.
- Controller quorum: established across all three locations.
- Typical geography: neighbouring states (for example NY, NJ, Boston).

**When to use:** when "extremely high availability is paramount" and three datacenters exist with stable sub-100 ms connectivity.

#### Stretched 2.5-datacenter cluster

Two fully operational datacenters plus one lightweight datacenter running **only KRaft controller nodes** to maintain quorum.

- RPO = 0 or > 0 depending on configuration.
- RTO ≥ 0, approaching zero with automatic observer promotion.
- Brokers and controllers: two equal deployments, one per operational datacenter.
- Controllers only: a minimal deployment in the third datacenter.
- Replica configuration is critical: `min.ISR=3` with "two replicas and one observer per location" achieves RPO = 0.

**When to use:** extreme high availability is needed and three connected datacenters exist with stable, low-latency links.

#### Active-passive (2 clusters)

One fully operational cluster serves all traffic; the passive cluster mirrors data asynchronously.

- RPO > 0 (asynchronous replication).
- RTO > 0 (failover time required).
- Applications run only in the active cluster during normal operation.
- All events replicate asynchronously to the passive backup.

**When to use:** datacenters are "far apart, have high network latency, or have unpredictable network latency."

#### Active-active (2 or more clusters)

Multiple fully independent, identical clusters each serving traffic simultaneously.

- RPO > 0 (asynchronous replication between clusters).
- RTO near 0 or > 0 depending on the application deployment strategy.
- Applications are duplicated and deployed in all operational datacenters.
- "At least one cluster running at all times."

**When to use:** multiple datacenters "strategically located in areas of low-latency or low-cost" with a business advantage from simultaneous multi-region operation.

#### Hub-and-spoke (aggregation)

One or many regional clusters replicate data to a central aggregate cluster.

- Multi-directional replication pattern.
- Local operations per region with global visibility.
- Common in Retail, Entertainment, Transportation and Manufacturing.
- Supports both geographic distribution and cross-team data governance.

### Comparison table

| Product | Cloud support | RPO | RTO | Description |
|---|---|---|---|---|
| **Cluster Linking** | Yes | > 0 | > 0 | Built-in replication mirroring topics and metadata |
| **MirrorMaker** | Yes | > 0 | > 0 | KIP-382 based asynchronous replication |
| **Multi-Region Clusters (MRC)** | Platform only | = 0 or > 0 | ≥ 0 | Seamless failover, simpler multi-DC architectures |

### Network requirements

Stretched clusters require that "data centers are connected by a low latency (sub-100ms) and stable... network."

Avoid stretched clusters when "data centers are far apart... or when network performance is > 100 ms, unstable, or unknown."

---

## 📄 Multi-Region Clusters — follower fetching, observers, replica placement

> Trích https://docs.confluent.io/platform/current/multi-dc-deployments/multi-region.html

Multi-Region Clusters enable Confluent Server to run across availability zones or nearby datacenters, mitigating latency, throughput and cost issues through three capabilities: **follower fetching**, **observers**, and **replica placement**.

**Follower fetching** — clients can consume from followers instead of only leaders, reducing cross-datacenter traffic:

```properties
# broker (server.properties)
replica.selector.class=org.apache.kafka.common.replica.RackAwareReplicaSelector
broker.rack=<region>

# consumer
client.rack=<rack_id>
```

`broker.rack` identifies the broker's location and "doesn't have to be a physical rack"; `broker.rack=us-west` / `broker.rack=us-east` maps brokers to regions.

**Observers** are a third replica type that replicate data from leaders without joining the in-sync replicas (ISR) by default. They enable asynchronous cross-region replication while maintaining synchronous replication within a region. Clients with follower fetching can also consume from observers.

**Automatic observer promotion** — observers can be promoted into the ISR during degraded scenarios. The `observerPromotionPolicy` field controls this:

- `under-min-isr` — promoted if the ISR drops below `min.insync.replicas` (default in replica placement version 2).
- `under-replicated` — promoted if the ISR drops below the configured replica count.
- `leader-is-observer` — requires manual intervention via unclean leader election.

**Replica placement** is defined per topic with JSON set as `confluent.placement.constraints`:

```json
{
  "version": 2,
  "replicas": [
    { "count": 2, "constraints": { "rack": "us-west" } },
    { "count": 2, "constraints": { "rack": "us-east" } }
  ],
  "observers": [
    { "count": 1, "constraints": { "rack": "us-central" } }
  ],
  "observerPromotionPolicy": "under-min-isr"
}
```

Each unique `rack` string appears at most once in `replicas` and once in `observers`.

**Synchronous vs asynchronous replication.** Topics with replica placement can define synchronous replicas in one region (joined to the ISR) and asynchronous observers in other regions. The leader only waits for ISR members before acknowledging `acks=all` producers, which avoids the throughput penalty of high-latency cross-region links.
