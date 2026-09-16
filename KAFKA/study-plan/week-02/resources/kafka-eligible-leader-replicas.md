# Apache Kafka — Eligible Leader Replicas (ELR, KIP-966) & Leader Election Order

> **Nguồn (official):** https://kafka.apache.org/43/operations/eligible-leader-replicas/ · bổ sung https://kafka.apache.org/43/design/design/#replication (*Unclean leader election*, *Availability and Durability Guarantees*, *Replica Management*)
> **Tuần:** 2 — Độ tin cậy & lưu trữ · **Loại:** Apache Kafka Docs (4.3) · *(KIP gốc: https://cwiki.apache.org/confluence/display/KAFKA/KIP-966%3A+Eligible+Leader+Replicas — cwiki không crawl được lúc viết; phần "Bối cảnh KIP-966" bên dưới tổng hợp từ docs, ghi rõ)*
> ⚠️ Nội dung dưới đây được crawl tự động (curl + chuyển HTML → Markdown, rút gọn) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- **Vấn đề ELR giải quyết:** trước 4.0, leader chỉ được chọn **trong ISR**. Khi ISR co về **1** (chỉ còn leader) rồi leader chết → **không còn ai trong ISR** → hoặc **unavailable** (chờ) hoặc **unclean election** (mất dữ liệu). Nhưng nhờ quy tắc **"strict min ISR"** — high watermark **không tiến** khi `|ISR| < min.insync.replicas` — các follower vừa rời ISR khi ISR đã dưới min.isr **vẫn giữ đủ mọi record committed** → **an toàn để làm leader**. KRaft controller lưu chúng vào trường **`Eligible Leader Replicas`** của `PartitionRecord`.
- **Thứ tự bầu leader khi ELR bật:** (1) **ISR** còn ai → chọn trong ISR; (2) ISR trống → chọn replica **trong ELR** chưa bị fence; (3) cả hai trống → chọn **last known leader** nếu unfenced (giống hành vi trước 4.0 khi mọi replica offline). Cột `Elr:` và `LastKnownElr:` hiện trong `kafka-topics.sh --describe` (API `DescribeTopicPartitions`).
- **Phiên bản:** KIP-966 Part 1 có từ **4.0** (phải bật tay `eligible.leader.replicas.version=1`); **bật mặc định trên cluster mới từ 4.1**. Hạ cấp an toàn: `eligible.leader.replicas.version=0`. Kiểm tra bằng `kafka-features.sh describe`.
- **Ràng buộc `min.insync.replicas` khi ELR bật (rất dễ ra đề):** config `min.insync.replicas` phải đặt ở **cluster-level** (`kafka-configs.sh --entity-type brokers --entity-default`); **không được** alter/ xoá ở **broker-level** (giá trị static broker-level cũ bị **gỡ**); **mọi thay đổi** `min.insync.replicas` ở cluster-level (dù giữ nguyên giá trị) hoặc topic-level → **xoá sạch trạng thái ELR** của partition liên quan.
- **ELR không thay `unclean.leader.election.enable`:** vẫn mặc định **false**. ELR mở rộng tập "an toàn để bầu"; unclean election chỉ xảy ra nếu bật `true` và cả ISR + ELR đều không có ai.
- **Kết hợp chuẩn production:** RF=3 + `min.insync.replicas=2` + `acks=all` + ELR → mất 1 broker vẫn ghi; mất 2 broker ngừng ghi nhưng **không mất dữ liệu**; leader chết sau đó vẫn có ELR để bầu thay vì chờ/unclean.
- **Replica management:** controller bầu leader **theo lô** cho mọi partition bị ảnh hưởng (nhanh); leadership cân bằng qua **preferred leader** (`auto.leader.rebalance.enable=true`, kiểm tra mỗi `leader.imbalance.check.interval.seconds=300`, ngưỡng `leader.imbalance.per.broker.percentage=10`); ép tay bằng `kafka-leader-election.sh --election-type PREFERRED|UNCLEAN`.

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Eligible Leader Replicas — Overview

Starting from Apache Kafka 4.0, Eligible Leader Replicas (KIP-966 Part 1) is available for the users to an improvement to Kafka replication (ELR is enabled by default on new clusters starting 4.1). As the "strict min ISR" rule has been generally applied, which means the high watermark for the data partition can't advance if the size of the ISR is smaller than the min ISR (`min.insync.replicas`), it makes some replicas that are not in the ISR safe to become the leader. The KRaft controller stores such replicas in the PartitionRecord field called `Eligible Leader Replicas`. During the leader election, the controller will select the leaders with the following order:

- If ISR is not empty, select one of them.
- If ELR is not empty, select one that is not fenced.
- Select the last known leader if it is unfenced. This is a similar behavior prior to the 4.0 when all the replicas are offline.

### Upgrade & Downgrade

The ELR is not enabled by default for 4.0. To enable the new protocol on the server, set `eligible.leader.replicas.version=1`. After that the upgrade, the KRaft controller will start tracking the ELR.

Downgrades are safe to perform by setting `eligible.leader.replicas.version=0`.

### Tool

The ELR fields can be checked through the API DescribeTopicPartitions. The admin client can fetch the ELR info by describing the topics.

Note that when the ELR feature is enabled:

- The cluster-level `min.insync.replicas` config will be added if there is not any. The value is the same as the static config in the active controller.
- The removal of `min.insync.replicas` config at the cluster-level is not allowed.
- If the cluster-level `min.insync.replicas` is updated, even if the value is unchanged, all the ELR state will be cleaned.
- The previously set `min.insync.replicas` value at the broker-level config will be removed. Please set at the cluster-level if necessary.
- The alteration of `min.insync.replicas` config at the broker-level is not allowed.
- If `min.insync.replicas` is updated for a topic, the ELR state will be cleaned.

```
# Kiểm tra / bật / tắt feature (KRaft)
$ bin/kafka-features.sh --bootstrap-server localhost:9092 describe
# ... eligible.leader.replicas.version  SupportedMinVersion: 0  SupportedMaxVersion: 1  FinalizedVersionLevel: 1 ...
$ bin/kafka-features.sh --bootstrap-server localhost:9092 upgrade --feature eligible.leader.replicas.version=1
$ bin/kafka-features.sh --bootstrap-server localhost:9092 downgrade --feature eligible.leader.replicas.version=0

# Xem ELR trong describe
$ bin/kafka-topics.sh --bootstrap-server localhost:9092 --describe --topic orders
Topic: orders  Partition: 0  Leader: 2  Replicas: 2,3,4  Isr: 2  Elr: 3  LastKnownElr:
```

### Unclean leader election: What if they all die? (Design)

Note that Kafka's guarantee with respect to data loss is predicated on at least one replica remaining in sync. If all the nodes replicating a partition die, this guarantee no longer holds.

However a practical system needs to do something reasonable when all the replicas die. If you are unlucky enough to have this occur, it is important to consider what will happen. There are two behaviors that could be implemented:

1. Wait for a replica in the ISR to come back to life and choose this replica as the leader (hopefully it still has all its data).
2. Choose the first replica (not necessarily in the ISR) that comes back to life as the leader.

This is a simple tradeoff between availability and consistency. If we wait for replicas in the ISR, then we will remain unavailable as long as those replicas are down. If such replicas were destroyed or their data was lost, then we are permanently down. If, on the other hand, a non-in-sync replica comes back to life and we allow it to become leader, then its log becomes the source of truth even though it is not guaranteed to have every committed message. By default from version 0.11.0.0, Kafka chooses the first strategy and favor waiting for a consistent replica. This behavior can be changed using configuration property `unclean.leader.election.enable`, to support use cases where uptime is preferable to consistency.

### Availability and Durability Guarantees (Design)

When writing to Kafka, producers can choose whether they wait for the message to be acknowledged by 0, 1 or all (-1) replicas. Note that "acknowledgement by all replicas" does not guarantee that the full set of assigned replicas have received the message. By default, when `acks=all`, acknowledgement happens as soon as all the current in-sync replicas have received the message. For example, if a topic is configured with only two replicas and one fails (i.e., only one in sync replica remains), then writes that specify `acks=all` will succeed. However, these writes could be lost if the remaining replica also fails. Although this ensures maximum availability of the partition, this behavior may be undesirable to some users who prefer durability over availability. Therefore, we provide two topic-level configurations that can be used to prefer message durability over availability:

1. Disable unclean leader election — if all replicas become unavailable, then the partition will remain unavailable until the most recent leader becomes available again. This effectively prefers unavailability over the risk of message loss.
2. Specify a minimum ISR size — the partition will only accept writes if the size of the ISR is above a certain minimum, in order to prevent the loss of messages that were written to just a single replica, which subsequently becomes unavailable. This setting only takes effect if the producer uses `acks=all` and guarantees that the message will be acknowledged by at least this many in-sync replicas. This setting offers a trade-off between consistency and availability. A higher setting for minimum ISR size guarantees better consistency since the message is guaranteed to be written to more replicas which reduces the probability that it will be lost. However, it reduces availability since the partition will be unavailable for writes if the number of in-sync replicas drops below the minimum threshold.

### Replica Management (Design)

The above discussion on replicated logs really covers only a single log, i.e. one topic partition. However a Kafka cluster will manage hundreds or thousands of these partitions. We attempt to balance partitions within a cluster in a round-robin fashion to avoid clustering all partitions for high-volume topics on a small number of nodes. Likewise we try to balance leadership so that each node is the leader for a proportional share of its partitions.

It is also important to optimize the leadership election process as that is the critical window of unavailability. A naive implementation of leader election would end up running an election per partition for all partitions a node hosted when that node failed. As discussed above in the section on replication, Kafka clusters have a special role known as the "controller" which is responsible for managing the registration of brokers. If the controller detects the failure of a broker, it is responsible for electing one of the remaining members of the ISR to serve as the new leader. The result is that we are able to batch together many of the required leadership change notifications which makes the election process far cheaper and faster for a large number of partitions.

### Bối cảnh KIP-966 (tổng hợp từ docs — không crawl được cwiki)

- KIP-966 gồm nhiều phần; **Part 1 (ELR)** đã GA. Ý tưởng: ISR có thể co xuống dưới `min.insync.replicas` (ví dụ RF=3, min.isr=2, ISR co về `{leader}`); vì HW **không tiến** khi ISR < min.isr, các replica vừa bị loại **không thiếu record committed nào** → được đưa vào **ELR**. Khi leader duy nhất trong ISR chết, controller bầu 1 replica trong ELR thay vì phải chờ (unavailable) hay unclean election (mất dữ liệu).
- Replica trong ELR **rời ELR** khi: quay lại ISR (đuổi kịp leader) hoặc bị phát hiện **mất dữ liệu / log dir hỏng** (ví dụ khởi động lại với đĩa trống — broker báo cho controller qua registration). `LastKnownElr` lưu tập ELR cuối cùng trước khi ISR/ELR trống hẳn để controller có "ứng viên cuối".
- Liên hệ config: `min.insync.replicas` trở thành **cluster-level** (nên đặt bằng `kafka-configs.sh --entity-type brokers --entity-default --alter --add-config min.insync.replicas=2`), topic override vẫn dùng được nhưng đổi giá trị sẽ **reset ELR** của topic đó.
