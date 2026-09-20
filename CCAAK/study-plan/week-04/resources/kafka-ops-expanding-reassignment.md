# Apache Kafka — Mở rộng cluster, reassignment, throttle, rack awareness (Basic Kafka Operations)

> **Nguồn (official):** https://kafka.apache.org/43/operations/basic-kafka-operations/ · phụ lục Cruise Control: https://github.com/linkedin/cruise-control
> **Tuần:** 4 — Deployment Architecture · **Loại:** Apache Kafka 4.3 Docs (§6.1 Basic Kafka Operations)
> ⚠️ Nội dung dưới đây được crawl tự động (HTTP → Markdown, có rút gọn) — luôn đối chiếu link gốc để đầy đủ và cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- **Broker mới KHÔNG tự nhận partition.** Docs nói thẳng: *"these new servers will not automatically be assigned any data partitions"* — chúng chỉ nhận partition của **topic tạo mới sau đó**. Muốn cân bằng phải chạy `kafka-reassign-partitions.sh`.
- **3 chế độ loại trừ nhau** của `kafka-reassign-partitions.sh`: `--generate` (đề xuất, in ra **2 JSON**: current để rollback + proposed), `--execute` (áp dụng), `--verify` (kiểm tra **và gỡ throttle**).
- `--generate` cần `--topics-to-move-json-file` + `--broker-list "5,6"`. `--execute`/`--verify` cần `--reassignment-json-file`.
- **Throttle** đặt bằng `--throttle <bytes/s>` lúc `--execute`. Tool tự đặt 4 config: broker-level `leader.replication.throttled.rate` và `follower.replication.throttled.rate` (mặc định `9223372036854775807` = không giới hạn), topic-level `leader.replication.throttled.replicas` và `follower.replication.throttled.replicas`. Đổi log dir dùng `--replica-alter-log-dirs-throttle`.
- ⚠️ **Throttle không tự biến mất.** Docs cảnh báo phải gỡ *"in a timely manner once reassignment completes (by running `--verify`)"*. Quên chạy `--verify` → replication bị bóp mãi mãi → URP dai dẳng sau này. Đây là câu hỏi lặp lại của CCAAK.
- **Tăng RF** cũng bằng chính tool này: viết JSON thêm replica (`"replicas":[5,6,7]`) rồi `--execute`. **Không** có lệnh `--alter --replication-factor`.
- **Decommission** (4.x): `cordoned.log.dirs="*"` qua `kafka-configs.sh` để controller **không đặt partition mới** lên broker sắp bỏ → reassign hết partition đi → tắt broker → `kafka-cluster.sh unregister --id <n>`. Bỏ cordon bằng `--bootstrap-controller` + `--delete-config`.
- **Balancing leadership**: `auto.leader.rebalance.enable=true` (mặc định) chạy nền theo `leader.imbalance.check.interval.seconds` **300**; làm ngay bằng `kafka-leader-election.sh --election-type preferred --all-topic-partitions`. Election **chỉ đổi leader, không copy data** — khác hẳn reassignment.
- **Graceful shutdown**: `controlled.shutdown.enable=true` (mặc định) khiến broker *"sync all its logs to disk"* và *"migrate any partitions the server is the leader for to other replicas prior to shutting down"* → downtime vài ms thay vì một vòng leader election.
- **Rack awareness**: `broker.rack=<id>` (read-only, cần restart). Kafka rải replica sao cho một partition trải **`min(#racks, replication-factor)`** rack khác nhau. Docs khuyến nghị **số broker mỗi rack bằng nhau**; rack lệch nhau → phân bố replica lệch.
- **Cruise Control** (LinkedIn, ngoài Apache Kafka) là lớp tự động hoá phía trên: theo dõi tải, sinh proposal theo **goal** (hard goal như `RackAwareGoal`, `ReplicaCapacityGoal`, `DiskCapacityGoal`; soft goal như `ReplicaDistributionGoal`), tự chữa khi broker chết. Nó **vẫn thực thi bằng cơ chế reassignment**, chỉ là không phải bạn viết JSON tay.

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Expanding your cluster

Adding servers to a Kafka cluster is easy, just assign them a unique broker id and start up Kafka on your new servers. However these new servers will not automatically be assigned any data partitions, so unless partitions are moved to them they won't be doing any work until new topics are created. So usually when you add machines to your cluster you will want to migrate some existing data to these machines.

The process of migrating data is manually initiated but fully automated. Under the covers what happens is that Kafka will add the new server as a follower of the partition it is migrating and allow it to fully replicate the existing data in that partition. When the new server has fully replicated the contents of this partition and joined the in-sync replica one of the existing replicas will delete their partition's data.

The partition reassignment tool can be used to move partitions across brokers. An ideal partition distribution would ensure even data load and partition sizes across all brokers. The partition reassignment tool does not have the capability to automatically study the data distribution in a Kafka cluster and move partitions around to attain an even load distribution. As such, the admin has to figure out which topics or partitions should be moved around.

The partition reassignment tool can run in 3 mutually exclusive modes:

- `--generate`: In this mode, given a list of topics and a list of brokers, the tool generates a candidate reassignment to move all partitions of the specified topics to the new brokers. This option merely provides a convenient way to generate a partition reassignment plan given a list of topics and target brokers.
- `--execute`: In this mode, the tool kicks off the reassignment of partitions based on the user provided reassignment plan.
- `--verify`: In this mode, the tool verifies the status of the reassignment for all partitions listed during the last `--execute`. The status can be either of successfully completed, failed or in progress.

### Automatically migrating data to new machines

Say we have topics `foo1` and `foo2` and we want to move all partitions of these topics to the new brokers 5 and 6. First, create the JSON file with the list of topics:

```json
{
  "topics": [
    { "topic": "foo1" },
    { "topic": "foo2" }
  ],
  "version": 1
}
```

Then generate a candidate assignment:

```bash
$ bin/kafka-reassign-partitions.sh --bootstrap-server localhost:9092 \
    --topics-to-move-json-file topics-to-move.json --broker-list "5,6" --generate
Current partition replica assignment
{"version":1,"partitions":[{"topic":"foo1","partition":0,"replicas":[2,1]}, ...]}

Proposed partition reassignment configuration
{"version":1,"partitions":[{"topic":"foo1","partition":0,"replicas":[6,5]}, ...]}
```

The tool generates a candidate assignment that will move all partitions from topics `foo1`, `foo2` to brokers 5,6. Note, however, that at this point, the partition movement has not started, it merely tells you the current assignment and the proposed new assignment. **The current assignment should be saved in case you want to rollback to it.**

Then execute it with the `--execute` option:

```bash
$ bin/kafka-reassign-partitions.sh --bootstrap-server localhost:9092 \
    --reassignment-json-file expand-cluster-reassignment.json --execute
```

Finally, verify:

```bash
$ bin/kafka-reassign-partitions.sh --bootstrap-server localhost:9092 \
    --reassignment-json-file expand-cluster-reassignment.json --verify
Status of partition reassignment:
Reassignment of partition [foo1,0] is completed
Reassignment of partition [foo1,1] is still in progress
...
```

### Custom partition assignment and migration

The partition reassignment tool can also be used to selectively move replicas of a partition to a specific set of brokers. Craft the reassignment JSON by hand:

```json
{"version":1,"partitions":[{"topic":"foo1","partition":0,"replicas":[5,6]},
                           {"topic":"foo2","partition":1,"replicas":[2,3]}]}
```

Then use `--execute` and `--verify` as above.

### Decommissioning brokers

Before a broker can be decommissioned, its log directories should be cordoned so that the controller does not place new partitions on them:

```bash
$ bin/kafka-configs.sh --bootstrap-server localhost:9092 --alter \
    --add-config cordoned.log.dirs="*" --entity-type brokers --entity-name 1
```

A specific log directory can also be cordoned:

```bash
$ bin/kafka-configs.sh --bootstrap-server localhost:9092 --alter \
    --add-config cordoned.log.dirs=/data/dir1 --entity-type brokers --entity-name 1
```

Once all partitions have been reassigned away from the broker and the broker has been shut down, it can be unregistered from the cluster:

```bash
$ bin/kafka-cluster.sh unregister --bootstrap-server localhost:9092 --id 1
```

To uncordon (for example after aborting a decommission), the configuration is removed through the controller:

```bash
$ bin/kafka-configs.sh --bootstrap-controller localhost:9093 --alter \
    --delete-config cordoned.log.dirs --entity-type brokers --entity-name 1
```

### Increasing replication factor

Increasing the replication factor of an existing partition is easy. Just specify the extra replicas in the custom reassignment JSON file and use it with the `--execute` option to increase the replication factor of the specified partitions.

For instance, the following example increases the replication factor of partition 0 of topic `foo` from 1 to 3. Before increasing the replication factor, the partition's only replica existed on broker 5. As part of increasing the replication factor, we will add more replicas on brokers 6 and 7:

```json
{"version":1,"partitions":[{"topic":"foo","partition":0,"replicas":[5,6,7]}]}
```

### Limiting bandwidth usage during data migration

Kafka lets you apply a throttle to replication traffic, setting an upper bound on the bandwidth used to move replicas from machine to machine. This is useful when rebalancing a cluster, bootstrapping a new broker or adding or removing brokers, as it limits the impact these data-intensive operations will have on users.

There are two interfaces that can be used to engage a throttle. The simplest, and safest, is to apply a throttle when invoking the reassign partitions tool:

```bash
$ bin/kafka-reassign-partitions.sh --bootstrap-server localhost:9092 --execute \
    --reassignment-json-file bigger-cluster.json --throttle 50000000 \
    --replica-alter-log-dirs-throttle 100000000
```

When you execute this script you will see the throttle engage:

```
The inter-broker throttle limit was set to 50000000 B/s
The replica-alter-dir throttle limit was set to 100000000 B/s
Successfully started partition reassignment for foo1-0
```

Should you wish to alter the throttle, during a rebalance, say to increase the throughput so it completes quicker, you can do this by re-running the execute command with the `--additional` option, passing the same reassignment-json-file.

Once the rebalance completes the administrator can check the status of the rebalance using the `--verify` option. If the rebalance has completed, the throttle will be removed via the `--verify` command. **It is important that administrators remove the throttle in a timely manner once rebalancing completes by running the command with the `--verify` option.** Failure to do so could cause regular replication traffic to be throttled.

When the `--verify` option is executed, and the reassignment has completed, the script will confirm that the throttle was removed:

```
Status of partition reassignment:
Reassignment of partition [my-topic,1] completed successfully
Reassignment of partition [my-topic,0] completed successfully

Clearing broker-level throttles on brokers 1,2,3
Clearing topic-level throttles on topic my-topic
```

The administrator can also validate the assigned configs using `kafka-configs.sh`. There are two pairs of throttle configuration used to manage the throttling process. First pair refers to the throttle value itself. This is configured, at a broker level, using the dynamic properties:

```
leader.replication.throttled.rate
follower.replication.throttled.rate
replica.alter.log.dirs.io.max.bytes.per.second
```

Then there is the configuration pair of enumerated sets of throttled replicas, applied at a topic level:

```
leader.replication.throttled.replicas
follower.replication.throttled.replicas
```

### Balancing leadership

Whenever a broker stops or crashes, leadership for that broker's partitions transfers to other replicas. When the broker is restarted it will only be a follower for all its partitions, meaning it will not be used for client reads and writes.

To avoid this imbalance, Kafka has a notion of preferred replicas. If the list of replicas for a partition is 1,5,9 then node 1 is preferred as the leader to either node 5 or 9 because it is earlier in the replica list.

By default the Kafka cluster will try to restore leadership to the preferred replicas. This behaviour is configured with:

```
auto.leader.rebalance.enable=true
```

You can also set this to false, but you will then need to manually restore leadership to the restored replicas by running the command:

```bash
$ bin/kafka-leader-election.sh --bootstrap-server localhost:9092 \
    --election-type preferred --all-topic-partitions
```

### Graceful shutdown

The Kafka cluster will automatically detect any broker shutdown or failure and elect new leaders for the partitions on that machine. This will occur whether a server fails or it is brought down intentionally for maintenance or configuration changes. For the latter cases Kafka supports a more graceful mechanism for stopping a server than just killing it. When a server is stopped gracefully it has two optimizations it will take advantage of:

1. It will sync all its logs to disk to avoid needing to do any log recovery when it restarts (i.e. validating the checksum for all messages in the tail of the log). Log recovery takes time so this speeds up intentional restarts.
2. It will migrate any partitions the server is the leader for to other replicas prior to shutting down. This will make the leadership transfer faster and minimize the time each partition is unavailable to a few milliseconds.

Syncing the logs will happen automatically whenever the server is stopped other than by a hard kill, but the controlled leadership migration requires using a special setting:

```
controlled.shutdown.enable=true
```

Note that controlled shutdown will only succeed if all the partitions hosted on the broker have replicas (i.e. the replication factor is greater than 1 and at least one of these replicas is alive). This is generally what you want since shutting down the last replica would make that topic partition unavailable.

### Balancing replicas across racks

The rack awareness feature spreads replicas of the same partition across different racks. This extends the guarantees Kafka provides for broker-failure to cover rack-failure, limiting the risk of data loss should all the brokers on a rack fail at once. The feature can also be applied to other broker groupings such as availability zones in EC2.

You can specify that a broker belongs to a particular rack by adding a property to the broker config:

```
broker.rack=my-rack-id
```

When a topic is created, modified or replicas are redistributed, the rack constraint will be honoured, ensuring replicas span as many racks as they can (a partition will span `min(#racks, replication-factor)` different racks).

The algorithm used to assign replicas to brokers ensures that the number of leaders per broker will be constant, regardless of how brokers are distributed across racks. This ensures balanced throughput.

However if brokers are assigned different numbers of racks, the assignment of replicas will not be even. Racks with fewer brokers will get more replicas, meaning they will use more storage and put more resources into replication. Hence it is sensible to configure an equal number of brokers per rack.

---

## 📎 Phụ lục — Cruise Control (LinkedIn)

> **Nguồn:** https://github.com/linkedin/cruise-control (README) — **không** thuộc Apache Kafka, là dự án riêng của LinkedIn.

Cruise Control addresses operational scalability challenges in large Kafka deployments: *"Due to the popularity of Apache Kafka, many companies have increasingly large Kafka clusters with hundreds of brokers."* At that scale broker failures become frequent and manual workload balancing becomes prohibitively expensive.

**Main features**

- **Workload monitoring** — resource utilization tracking for brokers, topics and partitions; cluster state queries showing partition status, replica synchronization and distribution.
- **Rebalancing** — multi-goal proposal generation accounting for rack-awareness, capacity violations and resource balance; admin operations including broker addition, removal, demotion and rebalance execution.
- **Anomaly detection and self-healing** — detection of goal violations, broker failures, metric anomalies and disk failures, with automatic mitigation.

**Components:** Load Monitor (collects metrics) · Analyzer (generates proposals) · Anomaly Detector (identifies issues) · Executor (implements changes).

**Goals** run with configurable priorities:

- **Hard goals (constraints):** `RackAwareGoal`, `ReplicaCapacityGoal`, `DiskCapacityGoal`, `NetworkInboundCapacityGoal`, `NetworkOutboundCapacityGoal`, `CpuCapacityGoal`.
- **Soft goals (optimization):** `ReplicaDistributionGoal`, `DiskUsageDistributionGoal`, `LeaderReplicaDistributionGoal`, `TopicReplicaDistributionGoal`.

Cruise Control exposes a **REST API** for users to interact with. Nó **không thay thế** cơ chế reassignment của Kafka — Executor vẫn chuyển replica bằng chính cơ chế đó; điểm khác là bạn nêu *mục tiêu* thay vì viết JSON assignment tay.
