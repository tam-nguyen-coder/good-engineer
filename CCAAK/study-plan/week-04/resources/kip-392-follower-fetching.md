# KIP-392 — Follower fetching: cho consumer đọc từ replica gần nhất

> **Nguồn (official):** https://cwiki.apache.org/confluence/display/KAFKA/KIP-392%3A+Allow+consumers+to+fetch+from+closest+replica
> **Nguồn phụ đã crawl được:** https://kafka.apache.org/43/configuration/consumer-configs/ (`client.rack`) · https://docs.confluent.io/platform/current/multi-dc-deployments/multi-region.html (follower fetching trong Multi-Region Clusters)
> **Tuần:** 4 — Deployment Architecture · **Loại:** KIP + Docs
> ⚠️ **Trang cwiki không crawl được từ môi trường này (kết nối bị chặn)** — phần "Nội dung" bên dưới **tổng hợp từ docs** Apache Kafka 4.3 và Confluent Platform đã crawl được, cộng với nội dung KIP-392 đã được cộng đồng dẫn lại. Đối chiếu link gốc trước ngày thi.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- **Vấn đề KIP-392 giải:** trước Kafka 2.4, consumer **luôn** đọc từ **leader**. Cluster trải nhiều AZ → mọi fetch đi xuyên AZ → **hoá đơn cross-AZ** (và độ trễ) tăng theo lưu lượng đọc, dù ngay trong AZ của consumer đã có một replica y hệt.
- **Cần đủ 3 mảnh, thiếu 1 là không có tác dụng:**
  1. **Broker**: `broker.rack=<az>` — khai báo broker nằm ở đâu.
  2. **Broker**: `replica.selector.class=org.apache.kafka.common.replica.RackAwareReplicaSelector` — mặc định là `LeaderSelector`, tức **luôn trả về leader**.
  3. **Consumer**: `client.rack=<az>` — docs Kafka 4.3 ghi: *"A rack identifier for this client... It corresponds with the broker config 'broker.rack'"*, kiểu `string`, **mặc định `""`** (rỗng).
- Cơ chế: consumer gửi `Fetch` kèm `rackId`; broker **leader** chạy `ReplicaSelector` và trả về trường **`PreferredReadReplica`** trong `FetchResponse`. Consumer ghi nhận và các fetch kế tiếp gửi thẳng tới replica đó.
- Consumer **quay lại leader** khi: preferred replica hết hạn theo `metadata.max.age.ms` (**300000** ms = 5 phút), hoặc replica đó trả lỗi (`NOT_LEADER_OR_FOLLOWER`, `OFFSET_NOT_AVAILABLE`, `REPLICA_NOT_AVAILABLE`), hoặc offset cần đọc nằm ngoài vùng follower đang có.
- **Chỉ replica trong ISR mới đủ điều kiện** làm read replica. Follower chỉ trả dữ liệu **tới high watermark** — giống leader — nên **không đọc được dữ liệu chưa commit**; nhưng follower có thể **chậm hơn leader vài trăm ms** → follower fetching đổi **chi phí lấy độ trễ**, không phải tăng throughput.
- **Producer vẫn luôn ghi vào leader.** Follower fetching **chỉ ảnh hưởng đọc**. Câu hỏi "giảm latency ghi" mà đáp án là follower fetching là bẫy.
- Phân biệt 3 thứ dễ lẫn: `broker.rack` = **đặt replica ở đâu** (placement, KIP-36) · `client.rack` + `replica.selector.class` = **đọc từ đâu** (fetching, KIP-392) · `RackAwareAssignor`/KIP-881 = **chia partition cho consumer nào** (assignment). Đề CCAAK thích trộn ba cái này.
- Ở **Confluent Platform Multi-Region Clusters**, cùng cặp config này còn cho consumer đọc từ **observer** (replica bất đồng bộ, không nằm trong ISR).

---

## 📄 Nội dung (tổng hợp từ docs — không crawl được trang KIP gốc)

### Motivation (KIP-392)

Kafka replicas are spread across racks or availability zones for fault tolerance, but consumers have always been required to fetch from the partition leader. When a cluster spans availability zones, this means that most fetch traffic crosses a zone boundary even though a copy of the same data is available locally. Cloud providers charge for cross-zone traffic, and the cross-zone hop also adds latency. KIP-392 allows a consumer to be served by the **closest** in-sync replica instead of the leader.

### Public interfaces

**New consumer configuration** (from the Apache Kafka 4.3 consumer configs page):

| Name | Description | Type | Default | Importance |
|---|---|---|---|---|
| `client.rack` | "A rack identifier for this client. This can be any string value which indicates where this client is physically located. It corresponds with the broker config `broker.rack`" | string | `""` | low |

**New broker configuration:**

| Name | Description | Default |
|---|---|---|
| `replica.selector.class` | The fully qualified class name that implements `ReplicaSelector`. This is used by the broker to find the preferred read replica. By default, the broker returns the leader. | null → behaves as `LeaderSelector` |

Kafka ships two implementations:

- `org.apache.kafka.common.replica.LeaderSelector` — the default behaviour: always return the leader.
- `org.apache.kafka.common.replica.RackAwareReplicaSelector` — match the client's `client.rack` against each replica's `broker.rack`, and prefer an in-sync replica in the same rack. If no in-sync replica matches the client's rack, fall back to the leader.

**The `ReplicaSelector` interface** lets an operator plug in a custom policy:

```java
public interface ReplicaSelector extends Configurable, Closeable {
    Optional<ReplicaView> select(TopicPartition topicPartition,
                                 ClientMetadata clientMetadata,
                                 PartitionView partitionView);
}
```

`ClientMetadata` carries the client's rack id, client id, listener name, principal and address; `PartitionView` carries the set of replicas (with their log end offsets and last-caught-up times) and the current leader.

### Protocol change

The `FetchResponse` gains a **`PreferredReadReplica`** field per partition. The flow is:

1. The consumer sends a `Fetch` request to the **leader**, including its `rackId` (taken from `client.rack`).
2. The leader runs the configured `ReplicaSelector` and, if it selects a replica other than itself, returns that replica's id in `PreferredReadReplica` (with an empty record set for that partition).
3. The consumer remembers the preferred read replica and sends subsequent fetches for that partition directly to it.
4. The consumer reverts to the leader when the preferred replica is no longer valid.

### When the consumer goes back to the leader

- The cached preferred read replica expires after `metadata.max.age.ms` (default **300000** ms), so the consumer periodically re-asks the leader.
- The follower returns an error indicating it cannot serve the fetch: `NOT_LEADER_OR_FOLLOWER`, `REPLICA_NOT_AVAILABLE`, `OFFSET_NOT_AVAILABLE`, or `FENCED_LEADER_EPOCH`.
- The requested offset is outside the range the follower currently holds.

`OFFSET_NOT_AVAILABLE` is a retriable error introduced for the case where a follower has not yet learned the current high watermark or leader epoch; the consumer retries rather than resetting its position.

### Correctness constraints

- Only **in-sync** replicas are eligible to be a preferred read replica; a replica that has fallen out of the ISR is never selected.
- A follower will not return records beyond the **high watermark** it knows about, exactly like the leader. Consumers therefore never observe uncommitted data, but they may observe data slightly **later** than a consumer reading from the leader, because the high watermark propagates to followers on the next fetch round.
- `OffsetsForLeaderEpoch` and offset-lookup requests (`ListOffsets`) are also served by the follower so that a consumer reading from a follower can still truncate and reset correctly after a leader change.
- `acks` and produce traffic are unaffected: **producers always write to the leader.**

### Confluent Platform — follower fetching in Multi-Region Clusters

> Trích https://docs.confluent.io/platform/current/multi-dc-deployments/multi-region.html

Clients can consume from followers instead of only leaders, reducing cross-datacenter traffic. Configuration requires:

**Broker-side (`server.properties`):**

```properties
replica.selector.class=org.apache.kafka.common.replica.RackAwareReplicaSelector
broker.rack=<region>
```

`broker.rack` identifies the broker's location and "doesn't have to be a physical rack" — `broker.rack=us-west` / `broker.rack=us-east` is a common mapping to datacenters or regions.

**Consumer-side:**

```properties
client.rack=<rack_id>
```

Apache Kafka 2.3+ clients read from followers whose `broker.rack` matches. In Multi-Region Clusters, clients with follower fetching can also consume from **observers** — a third replica type that replicates from the leader without joining the ISR, giving asynchronous cross-region replication while replication inside a region stays synchronous.
