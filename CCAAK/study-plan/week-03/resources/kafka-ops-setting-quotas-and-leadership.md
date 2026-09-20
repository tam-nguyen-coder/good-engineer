# Apache Kafka Operations — Setting quotas (`kafka-configs.sh`) + Balancing leadership

> **Nguồn (official):** https://kafka.apache.org/43/operations/basic-kafka-operations/#setting-quotas · https://kafka.apache.org/43/operations/basic-kafka-operations/#balancing-leadership
> **Tuần:** 3 — Cluster Config II: quotas, preferred leader · **Loại:** Apache Kafka 4.3 Documentation (Operations)
> ⚠️ Nội dung dưới đây được crawl tự động từ trang gốc (có cắt bớt phần ngoài chủ đề) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- **Mặc định client có quota vô hạn** ("By default, clients receive an unlimited quota"). Quota chỉ tồn tại khi admin tạo ra.
- Công cụ duy nhất: **`kafka-configs.sh`** với `--bootstrap-server`. Entity type là **`users`** và **`clients`** (không phải `brokers`/`topics`). Ghép 2 `--entity-type` trong **một** lệnh để đặt quota cho cặp (user, client-id).
- **`--entity-name <tên>`** = quota cho đúng entity đó · **`--entity-default`** = quota **mặc định** cho cả nhóm. Chỉ khác nhau một flag, nhưng rơi vào **hai mức ưu tiên khác nhau** trong bảng 8 mức.
- Config quota truyền qua `--add-config`: `producer_byte_rate`, `consumer_byte_rate`, `request_percentage` (và `controller_mutation_rate` theo KIP-599). Đơn vị byte_rate là **bytes/giây/broker**.
- `--describe` **không kèm `--entity-name`** → liệt kê **mọi** entity của type đó. Đây là cách audit nhanh "cluster này đang có những quota nào".
- Xoá quota: `--alter --delete-config 'producer_byte_rate'` (không phải `--add-config producer_byte_rate=-1`).
- **Preferred replica**: replica **đầu tiên** trong danh sách `Replicas:` của partition. Broker khởi động lại chỉ làm **follower** cho mọi partition của nó → cluster mất cân bằng leader, một số broker gánh hết traffic.
- `auto.leader.rebalance.enable` mặc định **true**; controller kiểm tra mất cân bằng mỗi `leader.imbalance.check.interval.seconds` = **300** giây. Cả hai config đều là **read-only** → muốn đổi phải **restart broker**.
- Nếu tắt auto rebalance thì phải chạy tay: `kafka-leader-election.sh --bootstrap-server ... --election-type preferred --all-topic-partitions`. (Công cụ cũ `kafka-preferred-replica-election.sh --zookeeper` đã **bị gỡ** — gặp nó trong đáp án là bẫy version.)
- `broker.rack` khiến replica trải qua **`min(#racks, replication-factor)`** rack khác nhau; thuật toán vẫn giữ số leader mỗi broker không đổi (chi tiết ở Tuần 4).
- Khi reassign có throttle, metric để theo dõi follower bắt kịp là `kafka.server:type=FetcherLagMetrics,name=ConsumerLag,...` — "The lag should constantly decrease during replication. If the metric does not decrease the administrator should increase the throttle throughput."

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Setting quotas

Quotas overrides and defaults may be configured at (user, client-id), user or client-id levels as described here. **By default, clients receive an unlimited quota.** It is possible to set custom quotas for each (user, client-id), user or client-id group.

Configure custom quota for (user=user1, client-id=clientA):

```
$ bin/kafka-configs.sh --bootstrap-server localhost:9092 --alter --add-config 'producer_byte_rate=1024,consumer_byte_rate=2048,request_percentage=200' --entity-type users --entity-name user1 --entity-type clients --entity-name clientA
Updated config for entity: user-principal 'user1', client-id 'clientA'.
```

Configure custom quota for user=user1:

```
$ bin/kafka-configs.sh --bootstrap-server localhost:9092 --alter --add-config 'producer_byte_rate=1024,consumer_byte_rate=2048,request_percentage=200' --entity-type users --entity-name user1
Updated config for entity: user-principal 'user1'.
```

Configure custom quota for client-id=clientA:

```
$ bin/kafka-configs.sh --bootstrap-server localhost:9092 --alter --add-config 'producer_byte_rate=1024,consumer_byte_rate=2048,request_percentage=200' --entity-type clients --entity-name clientA
Updated config for entity: client-id 'clientA'.
```

It is possible to set default quotas for each (user, client-id), user or client-id group by specifying `--entity-default` option instead of `--entity-name`.

Configure default client-id quota for user=user1:

```
$ bin/kafka-configs.sh --bootstrap-server localhost:9092 --alter --add-config 'producer_byte_rate=1024,consumer_byte_rate=2048,request_percentage=200' --entity-type users --entity-name user1 --entity-type clients --entity-default
Updated config for entity: user-principal 'user1', default client-id.
```

Configure default quota for user:

```
$ bin/kafka-configs.sh --bootstrap-server localhost:9092 --alter --add-config 'producer_byte_rate=1024,consumer_byte_rate=2048,request_percentage=200' --entity-type users --entity-default
Updated config for entity: default user-principal.
```

Configure default quota for client-id:

```
$ bin/kafka-configs.sh --bootstrap-server localhost:9092 --alter --add-config 'producer_byte_rate=1024,consumer_byte_rate=2048,request_percentage=200' --entity-type clients --entity-default
Updated config for entity: default client-id.
```

Here's how to describe the quota for a given (user, client-id):

```
$ bin/kafka-configs.sh --bootstrap-server localhost:9092 --describe --entity-type users --entity-name user1 --entity-type clients --entity-name clientA
Configs for user-principal 'user1', client-id 'clientA' are producer_byte_rate=1024,consumer_byte_rate=2048,request_percentage=200
```

Describe quota for a given user:

```
$ bin/kafka-configs.sh --bootstrap-server localhost:9092 --describe --entity-type users --entity-name user1
Configs for user-principal 'user1' are producer_byte_rate=1024,consumer_byte_rate=2048,request_percentage=200
```

Describe quota for a given client-id:

```
$ bin/kafka-configs.sh --bootstrap-server localhost:9092 --describe --entity-type clients --entity-name clientA
Configs for client-id 'clientA' are producer_byte_rate=1024,consumer_byte_rate=2048,request_percentage=200
```

Describe default quota for user:

```
$ bin/kafka-configs.sh --bootstrap-server localhost:9092 --describe --entity-type users --entity-default
Quota configs for the default user-principal are consumer_byte_rate=2048.0, request_percentage=200.0, producer_byte_rate=1024.0
```

Describe default quota for client-id:

```
$ bin/kafka-configs.sh --bootstrap-server localhost:9092 --describe --entity-type clients --entity-default
Quota configs for the default client-id are consumer_byte_rate=2048.0, request_percentage=200.0, producer_byte_rate=1024.0
```

**If entity name is not specified, all entities of the specified type are described.** For example, describe all users:

```
$ bin/kafka-configs.sh --bootstrap-server localhost:9092 --describe --entity-type users
Configs for user-principal 'user1' are producer_byte_rate=1024,consumer_byte_rate=2048,request_percentage=200
Configs for default user-principal are producer_byte_rate=1024,consumer_byte_rate=2048,request_percentage=200
```

Similarly for (user, client):

```
$ bin/kafka-configs.sh --bootstrap-server localhost:9092 --describe --entity-type users --entity-type clients
Configs for user-principal 'user1', default client-id are producer_byte_rate=1024,consumer_byte_rate=2048,request_percentage=200
Configs for user-principal 'user1', client-id 'clientA' are producer_byte_rate=1024,consumer_byte_rate=2048,request_percentage=200
```

### Balancing leadership

Whenever a broker stops or crashes, leadership for that broker's partitions transfers to other replicas. **When the broker is restarted it will only be a follower for all its partitions, meaning it will not be used for client reads and writes.**

To avoid this imbalance, Kafka has a notion of **preferred replicas**. If the list of replicas for a partition is 1,5,9 then node 1 is preferred as the leader to either node 5 or 9 because it is earlier in the replica list. By default the Kafka cluster will try to restore leadership to the preferred replicas. This behaviour is configured with:

```
auto.leader.rebalance.enable=true
```

You can also set this to false, but you will then need to manually restore leadership to the restored replicas by running the command:

```
$ bin/kafka-leader-election.sh --bootstrap-server localhost:9092 --election-type preferred --all-topic-partitions
```

### Graceful shutdown (bối cảnh của preferred leader)

The Kafka cluster will automatically detect any broker shutdown or failure and elect new leaders for the partitions on that machine. This will occur whether a server fails or it is brought down intentionally for maintenance or configuration changes. For the later cases Kafka supports a more graceful mechanism for stopping a server than just killing it. When a server is stopped gracefully it has two optimizations it will take advantage of: […] the controlled leadership migration requires using a special setting:

```
controlled.shutdown.enable=true
```

Note that controlled shutdown will only succeed if all the partitions hosted on the broker have replicas (i.e. the replication factor is greater than 1 and at least one of these replicas is alive). This is generally what you want since shutting down the last replica would make that topic partition unavailable.

### Balancing replicas across racks (tham chiếu chéo Tuần 4)

The rack awareness feature spreads replicas of the same partition across different racks. This extends the guarantees Kafka provides for broker-failure to cover rack-failure, limiting the risk of data loss should all the brokers on a rack fail at once. The feature can also be applied to other broker groupings such as availability zones in EC2.

You can specify that a broker belongs to a particular rack by adding a property to the broker config:

```
broker.rack=my-rack-id
```

When a topic is created, modified or replicas are redistributed, the rack constraint will be honoured, ensuring replicas span as many racks as they can (**a partition will span `min(#racks, replication-factor)` different racks**).

The algorithm used to assign replicas to brokers ensures that the number of leaders per broker will be constant, regardless of how brokers are distributed across racks. This ensures balanced throughput.

### Theo dõi follower bắt kịp sau reassignment

```
kafka.server:type=FetcherLagMetrics,name=ConsumerLag,clientId=([-.\w]+),topic=([-.\w]+),partition=([0-9]+)
```

The lag should constantly decrease during replication. If the metric does not decrease the administrator should increase the throttle throughput as described above.

### Bảng tra nhanh — quota config ↔ mức ưu tiên (tự tổng hợp từ 2 trang trên)

| Lệnh `kafka-configs.sh` | Entity thực tế | Mức ưu tiên |
|---|---|---|
| `--entity-type users --entity-name u --entity-type clients --entity-name c` | (user `u`, client-id `c`) | **1** |
| `--entity-type users --entity-name u --entity-type clients --entity-default` | (user `u`, default client-id) | **2** |
| `--entity-type users --entity-name u` | user `u` | **3** |
| `--entity-type users --entity-default --entity-type clients --entity-name c` | (default user, client-id `c`) | **4** |
| `--entity-type users --entity-default --entity-type clients --entity-default` | (default user, default client-id) | **5** |
| `--entity-type users --entity-default` | default user | **6** |
| `--entity-type clients --entity-name c` | client-id `c` | **7** |
| `--entity-type clients --entity-default` | default client-id | **8** |
