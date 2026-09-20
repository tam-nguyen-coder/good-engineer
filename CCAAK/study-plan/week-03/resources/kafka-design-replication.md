# Apache Kafka Design — Replication, ISR, `acks` × `min.insync.replicas`, Unclean Leader Election

> **Nguồn (official):** https://kafka.apache.org/43/design/design/#replication
> **Tuần:** 3 — Cluster Config II: replication & durability · **Loại:** Apache Kafka 4.3 Documentation (Design)
> ⚠️ Nội dung dưới đây được crawl tự động từ trang gốc (có cắt bớt phần ngoài chủ đề) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- Đơn vị replication là **topic partition**. Mỗi partition có **1 leader + 0..n follower**; tổng số bản sao (kể cả leader) = **replication factor**. **Mọi ghi đi vào leader**; đọc có thể từ leader hoặc follower (follower fetching, KIP-392).
- Broker được coi là "sống" khi thoả **2 điều kiện**: (1) giữ được **session với controller** (KRaft: heartbeat trong `broker.session.timeout.ms` = **9000** ms); (2) follower phải **fetch kịp** leader. Vi phạm một trong hai → bị **loại khỏi ISR**.
- Ngưỡng "tụt quá xa" là **`replica.lag.time.max.ms` = 30000** ms (30 giây). Đây là ngưỡng **theo thời gian**, không phải theo số message (config cũ `replica.lag.max.messages` đã bị bỏ từ 0.9).
- **Committed message** = message đã tới **tất cả replica trong ISR**. Consumer **chỉ thấy** message đã committed → consumer không bao giờ đọc phải dữ liệu có thể mất khi leader chết.
- Kafka **KHÔNG** dùng majority vote như Raft/Zab cho dữ liệu, mà dùng **ISR động**. Với `f+1` replica, Kafka chịu được **`f`** lỗi mà không mất message đã commit — rẻ hơn majority vote (cần `2f+1`).
- `acks`: **0** = không chờ · **1** = chỉ leader ghi xong · **all/-1** = mọi replica **hiện đang trong ISR** ghi xong. ⚠️ `acks=all` **không** nghĩa là "mọi replica được gán" — nó là "mọi replica *đang* trong ISR".
- `min.insync.replicas` **chỉ có hiệu lực khi producer dùng `acks=all`**. ISR nhỏ hơn giá trị này → leader từ chối ghi bằng **`NotEnoughReplicasException`** hoặc **`NotEnoughReplicasAfterAppendException`**.
- Bộ ba production chính tắc trong docs: **RF=3 + `min.insync.replicas=2` + `acks=all`** → chịu mất **đúng 1** broker mà vẫn ghi được và không mất dữ liệu. Đặt `min.insync.replicas=3` là **over-correction**: mất 1 broker là **ngừng ghi**.
- Dù `acks` bằng bao nhiêu, message **không hiển thị cho consumer** cho đến khi (1) đã nhân bản tới **tất cả** ISR **và** (2) số ISR **≥ `min.insync.replicas`**. Đây chính là quy tắc "strict min ISR" chặn **high watermark** tiến lên.
- `unclean.leader.election.enable` mặc định **false** (từ 0.11.0.0). Bật = cho replica **ngoài ISR** lên làm leader → **được ghi tiếp nhưng mất dữ liệu**. Đây là đánh đổi availability ↔ consistency, và luôn là **lựa chọn cuối cùng** trong đề.
- Cảnh báo trong docs: topic **RF=2** mà mất 1 broker thì `acks=all` **vẫn thành công** (ISR còn 1) — và những ghi đó **sẽ mất** nếu replica còn lại chết. Đây là lý do phải đặt `min.insync.replicas`.

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Replication

Kafka replicates the log for each topic's partitions across a configurable number of servers (you can set this replication factor on a topic-by-topic basis). This allows automatic failover to these replicas when a server in the cluster fails so messages remain available in the presence of failures.

Other messaging systems provide some replication-related features, but, in our (totally biased) opinion, this appears to be a tacked-on thing, not heavily used, and with large downsides: replicas are inactive, throughput is heavily impacted, it requires fiddly manual configuration, etc. Kafka is meant to be used with replication by default–in fact we implement un-replicated topics as replicated topics where the replication factor is one.

The unit of replication is the topic partition. Under non-failure conditions, each partition in Kafka has a single leader and zero or more followers. The total number of replicas including the leader constitute the replication factor. All writes go to the leader of the partition, and reads can go to the leader or the followers of the partition. Typically, there are many more partitions than brokers and the leaders are evenly distributed among brokers. The logs on the followers are identical to the leader's log–all have the same offsets and messages in the same order (though, of course, at any given time the leader may have a few as-yet unreplicated messages at the end of its log).

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

At its heart a Kafka partition is a replicated log. […]

The fundamental guarantee a log replication algorithm must provide is that if we tell the client a message is committed, and the leader fails, the new leader we elect must also have that message. This yields a tradeoff: if the leader waits for more followers to acknowledge a message before declaring it committed then there will be more potentially electable leaders.

If you choose the number of acknowledgements required and the number of logs that must be compared to elect a leader such that there is guaranteed to be an overlap, then this is called a Quorum.

A common approach to this tradeoff is to use a majority vote for both the commit decision and the leader election. This is not what Kafka does […] Let's say we have 2f+1 replicas. If f+1 replicas must receive a message prior to a commit being declared by the leader, and if we elect a new leader by electing the follower with the most complete log from at least f+1 replicas, then, with no more than f failures, the leader is guaranteed to have all committed messages.

There are a rich variety of algorithms in this family including ZooKeeper's Zab, Raft, and Viewstamped Replication. The most similar academic publication we are aware of to Kafka's actual implementation is PacificA from Microsoft.

The downside of majority vote is that it doesn't take many failures to leave you with no electable leaders. To tolerate one failure requires three copies of the data, and to tolerate two failures requires five copies of the data. […]

**Kafka takes a slightly different approach to choosing its quorum set.** Instead of majority vote, Kafka dynamically maintains a set of in-sync replicas (ISR) that are caught-up to the leader. Only members of this set are eligible for election as leader. A write to a Kafka partition is not considered committed until all in-sync replicas have received the write. This ISR set is persisted in the cluster metadata whenever it changes. Because of this, any replica in the ISR is eligible to be elected leader. This is an important factor for Kafka's usage model where there are many partitions and ensuring leadership balance is important. **With this ISR model and f+1 replicas, a Kafka topic can tolerate f failures without losing committed messages.**

In practice, to tolerate f failures, both the majority vote and the ISR approach will wait for the same number of replicas to acknowledge before committing a message (e.g. to survive one failure a majority quorum needs three replicas and one acknowledgement and the ISR approach requires two replicas and one acknowledgement).

Another important design distinction is that Kafka does not require that crashed nodes recover with all their data intact. […] Our protocol for allowing a replica to rejoin the ISR ensures that before rejoining, it must fully re-sync again even if it lost unflushed data in its crash.

### Unclean leader election: What if they all die?

Note that Kafka's guarantee with respect to data loss is predicated on at least one replica remaining in sync. If all the nodes replicating a partition die, this guarantee no longer holds.

However a practical system needs to do something reasonable when all the replicas die. If you are unlucky enough to have this occur, it is important to consider what will happen. There are two behaviors that could be implemented:

1. Wait for a replica in the ISR to come back to life and choose this replica as the leader (hopefully it still has all its data).
2. Choose the first replica (not necessarily in the ISR) that comes back to life as the leader.

This is a simple tradeoff between availability and consistency. If we wait for replicas in the ISR, then we will remain unavailable as long as those replicas are down. If such replicas were destroyed or their data was lost, then we are permanently down. If, on the other hand, a non-in-sync replica comes back to life and we allow it to become leader, then its log becomes the source of truth even though it is not guaranteed to have every committed message. **By default from version 0.11.0.0, Kafka chooses the first strategy and favor waiting for a consistent replica. This behavior can be changed using configuration property `unclean.leader.election.enable`, to support use cases where uptime is preferable to consistency.**

This dilemma is not specific to Kafka. It exists in any quorum-based scheme. For example in a majority voting scheme, if a majority of servers suffer a permanent failure, then you must either choose to lose 100% of your data or violate consistency by taking what remains on an existing server as your new source of truth.

### Availability and Durability Guarantees

When writing to Kafka, producers can choose whether they wait for the message to be acknowledged by 0, 1 or all (-1) replicas. **Note that "acknowledgement by all replicas" does not guarantee that the full set of assigned replicas have received the message. By default, when `acks=all`, acknowledgement happens as soon as all the current in-sync replicas have received the message.** For example, if a topic is configured with only two replicas and one fails (i.e., only one in sync replica remains), then writes that specify `acks=all` will succeed. However, these writes could be lost if the remaining replica also fails. Although this ensures maximum availability of the partition, this behavior may be undesirable to some users who prefer durability over availability. Therefore, we provide two topic configurations that can be used to prefer message durability over availability:

1. **Disable unclean leader election** — if all replicas become unavailable, then the partition will remain unavailable until the most recent leader becomes available again. This effectively prefers unavailability over the risk of message loss. See the previous section on Unclean Leader Election for clarification.
2. **Specify a minimum ISR size** — the partition will only accept writes if the size of the ISR is above a certain minimum, in order to prevent the loss of messages that were written to just a single replica, which subsequently becomes unavailable. **This setting only takes effect if the producer uses `acks=all`** and guarantees that the message will be acknowledged by at least this many in-sync replicas. This setting offers a trade-off between consistency and availability. A higher setting for minimum ISR size guarantees better consistency since the message is guaranteed to be written to more replicas which reduces the probability that it will be lost. **However, it reduces availability since the partition will be unavailable for writes if the number of in-sync replicas drops below the minimum threshold.**

### Replica Management

The above discussion on replicated logs really covers only a single log, i.e. one topic partition. However a Kafka cluster will manage hundreds or thousands of these partitions. We attempt to balance partitions within a cluster in a round-robin fashion to avoid clustering all partitions for high-volume topics on a small number of nodes. Likewise we try to balance leadership so that each node is the leader for a proportional share of its partitions.

It is also important to optimize the leadership election process as that is the critical window of unavailability. A naive implementation of leader election would end up running an election per partition for all partitions a node hosted when that node failed. As discussed above in the section on replication, Kafka clusters have a special role known as the "controller" which is responsible for managing the registration of brokers. If the controller detects the failure of a broker, it is responsible for electing one of the remaining members of the ISR to serve as the new leader. The result is that we are able to batch together many of the required leadership change notifications which makes the election process far cheaper and faster for a large number of partitions. If the controller itself fails, then another controller will be elected.

### Bổ sung — mô tả chính thức của `min.insync.replicas` (Broker Configs)

> Specifies the minimum number of in-sync replicas (including the leader) required for a write to succeed when a producer sets `acks` to "all" (or "-1"). In the `acks=all` case, every in-sync replica must acknowledge a write for it to be considered successful. E.g., if a topic has `replication.factor` of 3 and the ISR set includes all three replicas, then all three replicas must acknowledge an `acks=all` write for it to succeed, even if `min.insync.replicas` happens to be less than 3. **If `acks=all` and the current ISR set contains fewer than `min.insync.replicas` members, then the producer will raise an exception (either `NotEnoughReplicas` or `NotEnoughReplicasAfterAppend`).** Regardless of the `acks` setting, the messages will not be visible to the consumers until they are replicated to all in-sync replicas and the `min.insync.replicas` condition is met. When used together, `min.insync.replicas` and `acks` allow you to enforce greater durability guarantees. **A typical scenario would be to create a topic with a replication factor of 3, set `min.insync.replicas` to 2, and produce with `acks` of "all".** This ensures that a majority of replicas must persist a write before it's considered successful by the producer and it's visible to consumers. Note that when the Eligible Leader Replicas feature is enabled, the semantics of this config changes. Please refer to the ELR section for more info.
>
> Type: `int` · Default: **1** · Valid Values: `[1,...]` · Importance: high · Update Mode: **cluster-wide**
