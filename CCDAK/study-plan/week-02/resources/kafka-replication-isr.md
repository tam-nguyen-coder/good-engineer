# Apache Kafka Design — Replication, ISR, acks & Unclean Leader Election

> **Nguồn (official):** https://kafka.apache.org/43/design/design/#replication
> **Tuần:** 2 — Độ tin cậy & lưu trữ · **Loại:** Apache Kafka Docs (4.3)
> ⚠️ Nội dung dưới đây được crawl tự động (qua curl + chuyển HTML → Markdown, có rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- **Đơn vị replication = partition.** Mỗi partition có **1 leader + 0..N follower**; RF = tổng số replica (kể cả leader). Mọi **ghi** đều qua leader; đọc mặc định từ leader (follower fetching là tuỳ chọn, Tuần 4).
- **Follower kéo (pull)** dữ liệu từ leader như một consumer → tự nhiên batch được; không phải leader đẩy.
- **Broker "in sync" cần 2 điều kiện:** (1) giữ session/heartbeat với KRaft controller (`broker.session.timeout.ms`); (2) follower không tụt quá `replica.lag.time.max.ms` (**30 000 ms** mặc định) so với log end offset của leader. Vi phạm → bị **loại khỏi ISR** (ISR shrink); bắt kịp lại → **ISR expand**.
- **Committed message** = đã được **tất cả replica trong ISR** ghi vào log. Consumer **chỉ đọc được message committed** (tới **high watermark**). Kafka cam kết không mất message committed **miễn còn ≥1 replica trong ISR sống**.
- **`acks`** quyết định producer chờ gì: `0` không chờ; `1` chờ leader ghi local log; `all`/`-1` chờ **toàn bộ ISR hiện tại**. `min.insync.replicas` **chỉ có tác dụng khi `acks=all`**: ISR < min.isr → broker từ chối ghi (`NotEnoughReplicasException`).
- **Bẫy:** `acks=all` KHÔNG có nghĩa "tất cả replica được gán" — chỉ là **ISR hiện tại**. Topic RF=2 mất 1 broker → ISR=1 → `acks=all` vẫn thành công (nếu min.isr=1) và có thể mất dữ liệu. Muốn bền → **RF=3 + `min.insync.replicas=2` + `acks=all`** (chịu mất 1 broker, vẫn ghi được).
- Kafka dùng **ISR** thay cho **majority quorum**: với **f+1 replica chịu được f lỗi** (quorum cần 2f+1). Nhược: phải chờ replica chậm nhất trong ISR (nhưng lag quá thì bị loại).
- **Unclean leader election:** khi cả ISR chết, mặc định (`unclean.leader.election.enable=false`) Kafka **chờ replica trong ISR sống lại** (ưu tiên consistency, chấp nhận unavailable). Bật `true` → bầu replica **ngoài ISR** làm leader → **có thể mất dữ liệu committed** nhưng khôi phục availability.
- Replica **không cần** khôi phục với dữ liệu nguyên vẹn (không fsync mỗi lần ghi) — trước khi rejoin ISR phải **đồng bộ lại đầy đủ**.
- **Controller** (KRaft) phát hiện broker chết và **bầu leader mới từ ISR theo lô** cho mọi partition bị ảnh hưởng → nhanh; Kafka cân bằng leadership để mỗi broker là leader cho một phần partition tương ứng (preferred leader, `auto.leader.rebalance.enable=true`, kiểm tra mỗi `leader.imbalance.check.interval.seconds=300`).
- Kafka chịu được **node failure** (sau thời gian failover ngắn) nhưng **không đảm bảo** available khi **network partition**.

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Replication

Kafka replicates the log for each topic's partitions across a configurable number of servers (you can set this replication factor on a topic-by-topic basis). This allows automatic failover to these replicas when a server in the cluster fails so messages remain available in the presence of failures.

Kafka is meant to be used with replication by default — in fact we implement un-replicated topics as replicated topics where the replication factor is one.

The unit of replication is the topic partition. Under non-failure conditions, each partition in Kafka has a single leader and zero or more followers. The total number of replicas including the leader constitute the replication factor. All writes go to the leader of the partition, and reads can go to the leader or the followers of the partition. Typically, there are many more partitions than brokers and the leaders are evenly distributed among brokers. The logs on the followers are identical to the leader's log — all have the same offsets and messages in the same order (though, of course, at any given time the leader may have a few as-yet unreplicated messages at the end of its log).

Followers consume messages from the leader just as a normal Kafka consumer would and apply them to their own log. Having the followers pull from the leader has the nice property of allowing the follower to naturally batch together log entries they are applying to their log.

As with most distributed systems, automatically handling failures requires a precise definition of what it means for a node to be "alive." In Kafka, a special node known as the "controller" is responsible for managing the registration of brokers in the cluster. Broker liveness has two conditions:

1. Brokers must maintain an active session with the controller in order to receive regular metadata updates.
2. Brokers acting as followers must replicate the writes from the leader and not fall "too far" behind.

What is meant by an "active session" depends on the cluster configuration. For KRaft clusters, an active session is maintained by sending periodic heartbeats to the controller. If the controller fails to receive a heartbeat before the timeout configured by `broker.session.timeout.ms` expires, then the node is considered offline.

We refer to nodes satisfying these two conditions as being "in sync" to avoid the vagueness of "alive" or "failed". The leader keeps track of the set of "in sync" replicas, which is known as the ISR. If either of these conditions fail to be satisfied, then the broker will be removed from the ISR. For example, if a follower dies, then the controller will notice the failure through the loss of its session, and will remove the broker from the ISR. On the other hand, if the follower lags too far behind the leader but still has an active session, then the leader can also remove it from the ISR. The determination of lagging replicas is controlled through the `replica.lag.time.max.ms` configuration. Replicas that cannot catch up to the end of the log on the leader within the max time set by this configuration are removed from the ISR.

In distributed systems terminology we only attempt to handle a "fail/recover" model of failures where nodes suddenly cease working and then later recover (perhaps without knowing that they have died). Kafka does not handle so-called "Byzantine" failures in which nodes produce arbitrary or malicious responses (perhaps due to bugs or foul play).

Only committed messages are ever given out to the consumer. This means that the consumer need not worry about potentially seeing a message that could be lost if the leader fails. Producers, on the other hand, have the option of either waiting for the message to be committed or not, depending on their preference for tradeoff between latency and durability. This preference is controlled by the `acks` setting that the producer uses. Note that topics have a setting for the minimum number of in-sync replicas (`min.insync.replicas`) that is checked when the producer requests acknowledgment that a message has been written to the full set of in-sync replicas. If a less stringent acknowledgment is requested by the producer, then the message is committed asynchronously across the set of in-sync replicas if `acks=0`, or synchronously only on the leader if `acks=1`. Regardless of the `acks` setting, the messages will not be visible to the consumers until all the following conditions are met:

1. The messages are replicated to all the in-sync replicas.
2. The number of the in-sync replicas is no less than the `min.insync.replicas` setting.

The guarantee that Kafka offers is that a committed message will not be lost, as long as there is at least one in sync replica alive, at all times.

Kafka will remain available in the presence of node failures after a short fail-over period, but may not remain available in the presence of network partitions.

### Replicated Logs: Quorums, ISRs, and State Machines (Oh my!)

At its heart a Kafka partition is a replicated log. A replicated log models the process of coming into consensus on the order of a series of values (generally numbering the log entries 0, 1, 2, ...). The simplest and fastest is with a leader who chooses the ordering of values provided to it. As long as the leader remains alive, all followers need to only copy the values and ordering the leader chooses.

When the leader does die we need to choose a new leader from among the followers. But followers themselves may fall behind or crash so we must ensure we choose an up-to-date follower. The fundamental guarantee a log replication algorithm must provide is that if we tell the client a message is committed, and the leader fails, the new leader we elect must also have that message. This yields a tradeoff: if the leader waits for more followers to acknowledge a message before declaring it committed then there will be more potentially electable leaders.

If you choose the number of acknowledgements required and the number of logs that must be compared to elect a leader such that there is guaranteed to be an overlap, then this is called a Quorum.

A common approach to this tradeoff is to use a majority vote for both the commit decision and the leader election. This is not what Kafka does. Let's say we have 2f+1 replicas. If f+1 replicas must receive a message prior to a commit being declared by the leader, and if we elect a new leader by electing the follower with the most complete log from at least f+1 replicas, then, with no more than f failures, the leader is guaranteed to have all committed messages. This majority vote approach has a very nice property: the latency is dependent on only the fastest servers.

The downside of majority vote is that it doesn't take many failures to leave you with no electable leaders. To tolerate one failure requires three copies of the data, and to tolerate two failures requires five copies of the data.

Kafka takes a slightly different approach to choosing its quorum set. Instead of majority vote, Kafka dynamically maintains a set of in-sync replicas (ISR) that are caught-up to the leader. Only members of this set are eligible for election as leader. A write to a Kafka partition is not considered committed until all in-sync replicas have received the write. This ISR set is persisted in the cluster metadata whenever it changes. Because of this, any replica in the ISR is eligible to be elected leader. This is an important factor for Kafka's usage model where there are many partitions and ensuring leadership balance is important. With this ISR model and f+1 replicas, a Kafka topic can tolerate f failures without losing committed messages.

In practice, to tolerate f failures, both the majority vote and the ISR approach will wait for the same number of replicas to acknowledge before committing a message (e.g. to survive one failure a majority quorum needs three replicas and one acknowledgement and the ISR approach requires two replicas and one acknowledgement). The ability to commit without the slowest servers is an advantage of the majority vote approach. However, we think it is ameliorated by allowing the client to choose whether they block on the message commit or not, and the additional throughput and disk space due to the lower required replication factor is worth it.

Another important design distinction is that Kafka does not require that crashed nodes recover with all their data intact. First, disk errors are the most common problem we observe in real operation of persistent data systems and they often do not leave data intact. Secondly, we do not want to require the use of fsync on every write for our consistency guarantees as this can reduce performance by two to three orders of magnitude. Our protocol for allowing a replica to rejoin the ISR ensures that before rejoining, it must fully re-sync again even if it lost unflushed data in its crash.

### Unclean leader election: What if they all die?

Note that Kafka's guarantee with respect to data loss is predicated on at least one replica remaining in sync. If all the nodes replicating a partition die, this guarantee no longer holds.

There are two behaviors that could be implemented:

1. Wait for a replica in the ISR to come back to life and choose this replica as the leader (hopefully it still has all its data).
2. Choose the first replica (not necessarily in the ISR) that comes back to life as the leader.

This is a simple tradeoff between availability and consistency. If we wait for replicas in the ISR, then we will remain unavailable as long as those replicas are down. If such replicas were destroyed or their data was lost, then we are permanently down. If, on the other hand, a non-in-sync replica comes back to life and we allow it to become leader, then its log becomes the source of truth even though it is not guaranteed to have every committed message. By default from version 0.11.0.0, Kafka chooses the first strategy and favor waiting for a consistent replica. This behavior can be changed using configuration property `unclean.leader.election.enable`, to support use cases where uptime is preferable to consistency.

### Availability and Durability Guarantees

When writing to Kafka, producers can choose whether they wait for the message to be acknowledged by 0, 1 or all (-1) replicas. Note that "acknowledgement by all replicas" does not guarantee that the full set of assigned replicas have received the message. By default, when acks=all, acknowledgement happens as soon as all the current in-sync replicas have received the message. For example, if a topic is configured with only two replicas and one fails (i.e., only one in sync replica remains), then writes that specify acks=all will succeed. However, these writes could be lost if the remaining replica also fails. Although this ensures maximum availability of the partition, this behavior may be undesirable to some users who prefer durability over availability. Therefore, we provide two topic configurations that can be used to prefer message durability over availability:

1. Disable unclean leader election — if all replicas become unavailable, then the partition will remain unavailable until the most recent leader becomes available again. This effectively prefers unavailability over the risk of message loss.
2. Specify a minimum ISR size — the partition will only accept writes if the size of the ISR is above a certain minimum, in order to prevent the loss of messages that were written to just a single replica, which subsequently becomes unavailable. This setting only takes effect if the producer uses acks=all and guarantees that the message will be acknowledged by at least this many in-sync replicas. This setting offers a trade-off between consistency and availability. A higher setting for minimum ISR size guarantees better consistency since the message is guaranteed to be written to more replicas which reduces the probability that it will be lost. However, it reduces availability since the partition will be unavailable for writes if the number of in-sync replicas drops below the minimum threshold.

### Replica Management

A Kafka cluster will manage hundreds or thousands of these partitions. We attempt to balance partitions within a cluster in a round-robin fashion to avoid clustering all partitions for high-volume topics on a small number of nodes. Likewise we try to balance leadership so that each node is the leader for a proportional share of its partitions.

It is also important to optimize the leadership election process as that is the critical window of unavailability. Kafka clusters have a special role known as the "controller" which is responsible for managing the registration of brokers. If the controller detects the failure of a broker, it is responsible for electing one of the remaining members of the ISR to serve as the new leader. The result is that we are able to batch together many of the required leadership change notifications which makes the election process far cheaper and faster for a large number of partitions. If the controller itself fails, then another controller will be elected.

### Related broker configs (from `kafka_config.html`, Kafka 4.3)

| Config | Default | Ghi chú |
|---|---|---|
| `replica.lag.time.max.ms` | 30000 (30 s) | If a follower hasn't sent any fetch requests or hasn't consumed up to the leader's log end offset for at least this time, the leader will remove the follower from ISR |
| `min.insync.replicas` | 1 | Minimum number of in-sync replicas (including the leader) required for a write to succeed when a producer sets `acks=all` |
| `unclean.leader.election.enable` | false | Enable replicas not in the ISR set to be elected as leader as a last resort, even though doing so may result in data loss |
| `auto.leader.rebalance.enable` | true | Background thread checks leader distribution every `leader.imbalance.check.interval.seconds` (300); rebalances to preferred leader |
| `broker.rack` | null | Rack of the broker, used in rack-aware replica assignment (e.g. `RACK1`, `us-east-1d`) |
| `default.replication.factor` | 1 | Default RF for auto-created topics |
