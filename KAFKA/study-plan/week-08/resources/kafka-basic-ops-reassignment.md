# Apache Kafka — Basic Operations: Consumer Groups, Expanding Cluster, Reassignment & Throttling

> **Nguồn (official):** https://kafka.apache.org/43/operations/basic-kafka-operations/ (mục 6.1 Basic Kafka Operations)
> **Tuần:** 8 — Observability & Operations · **Loại:** Apache Kafka Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua HTTP + chuyển HTML → Markdown, có rút gọn) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- **Tăng partition được, giảm KHÔNG được** (`kafka-topics.sh --alter --partitions N`). Tăng partition làm `hash(key) % N` đổi → **phá ordering theo key**; consumer `auto.offset.reset=latest` có thể **bỏ lỡ** message vào partition mới trước khi phát hiện (`metadata.max.age.ms`). **Không bao giờ** tăng partition của `__consumer_offsets`, `__transaction_state`, `__share_group_state`, `__cluster_metadata`.
- **Graceful shutdown**: `controlled.shutdown.enable=true` → broker sync log + **chuyển leadership** trước khi tắt (downtime vài ms); chỉ thành công nếu mọi partition trên broker có replica khác còn sống (RF > 1).
- **Preferred leader**: replica đứng **đầu** danh sách replicas là preferred; `auto.leader.rebalance.enable=true` (mặc định) tự trả leader về; thủ công: `kafka-leader-election.sh --election-type preferred --all-topic-partitions` (hoặc `unclean` khi chấp nhận mất data).
- **`kafka-consumer-groups.sh --describe --group X`** in `CURRENT-OFFSET`, `LOG-END-OFFSET`, `LAG` (= LEO − current), `CONSUMER-ID`, `HOST`, `CLIENT-ID`; `CONSUMER-ID` = `-` nghĩa là **không ai giữ partition** (group inactive hoặc partition không được gán). `--members --verbose` xem assignment; `--state` xem coordinator, assignor, state, số member.
- **`--reset-offsets`** yêu cầu group **inactive**; scenario: `--to-earliest`, `--to-latest`, `--to-offset`, `--shift-by ±n`, `--to-datetime YYYY-MM-DDThh:mm:ss.sss`, `--by-duration PnDTnHnMnS`, `--to-current`, `--from-file`; mặc định chỉ **dry-run**, cần `--execute` (hoặc `--export` CSV). Offset ngoài range được kéo về offset end hợp lệ.
- **Thêm broker ≠ tự nhận partition**: phải dùng `kafka-reassign-partitions.sh` với 3 mode loại trừ nhau: `--generate` (từ `--topics-to-move-json-file` + `--broker-list`), `--execute` (`--reassignment-json-file`), `--verify` (cùng file JSON). Output của `--generate` in cả **current assignment (lưu để rollback)** và proposed.
- **Tăng RF** = viết tay JSON reassignment thêm replica (`"replicas":[5,6,7]`) rồi `--execute`; broker mới trở thành follower, sync xong vào ISR. **Decommission** (4.3): `kafka-configs.sh --alter --add-config cordoned.log.dirs="*" --entity-type brokers --entity-name 1` (KIP-1066) → reassign hết partition đi → `kafka-cluster.sh unregister --id 1`.
- **Throttle** khi reassign: `--throttle 50000000` (B/s inter-broker) và `--replica-alter-log-dirs-throttle` (giữa disk); sinh ra config động `leader.replication.throttled.rate` / `follower.replication.throttled.rate` (broker) + `leader/follower.replication.throttled.replicas` (topic). **Chạy `--verify` sau khi xong để gỡ throttle**, nếu không replication thường cũng bị bóp. Throttle < `BytesInPerSec` → reassignment **không bao giờ xong**; theo dõi `FetcherLagMetrics,name=ConsumerLag` phải giảm dần. Đổi throttle giữa chừng: `--additional --execute --throttle N`.
- Quota client: `kafka-configs.sh --alter --add-config 'producer_byte_rate=1024,consumer_byte_rate=2048,request_percentage=200' --entity-type users --entity-name user1 --entity-type clients --entity-name clientA`.

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Modifying topics

To add partitions you can do

```
$ bin/kafka-topics.sh --bootstrap-server localhost:9092 --alter --topic my_topic_name --partitions 40
```

**Note:** Dynamically increasing the number of partitions for a topic has several important considerations and potential side effects:

- **Key Distribution Changes**: If data is partitioned by `hash(key) % number_of_partitions`, the default partitioner's mapping logic changes when the partition count increases. This means that messages with the same key may be routed to different partitions after the expansion, potentially affecting message ordering guarantees for existing keys. Kafka will not attempt to automatically redistribute existing data.
- **Potential Data Loss with `auto.offset.reset=latest`**: Existing consumers configured with `auto.offset.reset=latest` might miss messages produced to the new partitions during the window between partition creation and consumer discovery.
- **Metadata Propagation Delay**: New partitions are not immediately visible to producers and consumers due to metadata refresh intervals (controlled by `metadata.max.age.ms`).
- **Risks with Internal Topics**: Users should **never** manually increase partitions for Kafka's internal state topics such as `__consumer_offsets`, `__transaction_state`, `__share_group_state`, or `__cluster_metadata`.

Kafka does not currently support reducing the number of partitions for a topic.

### Graceful shutdown

When a server is stopped gracefully it has two optimizations it will take advantage of:

- It will sync all its logs to disk to avoid needing to do any log recovery when it restarts. Log recovery takes time so this speeds up intentional restarts.
- It will migrate any partitions the server is the leader for to other replicas prior to shutting down. This will make the leadership transfer faster and minimize the time each partition is unavailable to a few milliseconds. The controlled leadership migration requires using a special setting:

```
controlled.shutdown.enable=true
```

Note that controlled shutdown will only succeed if all the partitions hosted on the broker have replicas (i.e. the replication factor is greater than 1 and at least one of these replicas is alive).

### Balancing leadership

Whenever a broker stops or crashes, leadership for that broker's partitions transfers to other replicas. When the broker is restarted it will only be a follower for all its partitions, meaning it will not be used for client reads and writes.

To avoid this imbalance, Kafka has a notion of preferred replicas. If the list of replicas for a partition is 1,5,9 then node 1 is preferred as the leader to either node 5 or 9 because it is earlier in the replica list. By default the Kafka cluster will try to restore leadership to the preferred replicas. This behaviour is configured with:

```
auto.leader.rebalance.enable=true
```

You can also set this to false, but you will then need to manually restore leadership to the restored replicas by running the command:

```
$ bin/kafka-leader-election.sh --bootstrap-server localhost:9092 --election-type preferred --all-topic-partitions
```

### Checking consumer position

```
$ bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --describe --group my-group
TOPIC                          PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG        CONSUMER-ID                                       HOST                           CLIENT-ID
my-topic                       0          2               4               2          consumer-1-029af89c-873c-4751-a720-cefd41a669d6   /127.0.0.1                     consumer-1
my-topic                       1          2               3               1          consumer-1-029af89c-873c-4751-a720-cefd41a669d6   /127.0.0.1                     consumer-1
my-topic                       2          2               3               1          consumer-2-42c1abd4-e3b2-425d-a8bb-e1ea49b29bb2   /127.0.0.1                     consumer-2
```

### Managing consumer groups

The consumer group can be deleted manually, or automatically when the last committed offset for that group expires. Manual deletion works only if the group does not have any active members.

```
$ bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --list
$ bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --describe --group my-group --members --verbose
CONSUMER-ID                                    HOST            CLIENT-ID       #PARTITIONS     ASSIGNMENT
consumer1-3fc8d6f1-581a-4472-bdf3-3515b4aee8c1 /127.0.0.1      consumer1       2               topic1(0), topic2(0)
consumer4-117fe4d3-c6c1-4178-8ee9-eb4a3954bee0 /127.0.0.1      consumer4       1               topic3(2)
consumer2-e76ea8c3-5d30-4299-9005-47eb41f3d3c4 /127.0.0.1      consumer2       3               topic2(1), topic3(0,1)
consumer3-ecea43e4-1f01-479f-8349-f9130b75d8ee /127.0.0.1      consumer3       0               -

$ bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --describe --group my-group --state
COORDINATOR (ID)          ASSIGNMENT-STRATEGY       STATE                #MEMBERS
localhost:9092 (0)        range                     Stable               4

$ bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --delete --group my-group --group my-other-group
```

To reset offsets of a consumer group, `--reset-offsets` option can be used. This option supports one consumer group at the time. It requires defining following scopes: `--all-topics` or `--topic`. Also, first make sure that the consumer instances are inactive. It has 3 execution options: (default) to display which offsets to reset; `--execute`: to execute the process; `--export`: to export the results to a CSV format.

`--reset-offsets` also has the following scenarios to choose from: `--to-datetime <String: datetime>` (Format: 'YYYY-MM-DDThh:mm:ss.sss'), `--to-earliest`, `--to-latest`, `--shift-by <Long: number-of-offsets>` (positive or negative), `--from-file`, `--to-current`, `--by-duration <String: duration>` (Format: 'PnDTnHnMnS'), `--to-offset`.

Please note, that out of range offsets will be adjusted to available offset end. For example, if offset end is at 10 and offset shift request is of 15, then, offset at 10 will actually be selected.

```
$ bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --reset-offsets --group my-group --topic topic1 --to-latest
TOPIC                          PARTITION  NEW-OFFSET
topic1                         0          0
```

### Expanding your cluster

Adding servers to a Kafka cluster is easy, just assign them a unique broker id and start up Kafka on your new servers. However these new servers will not automatically be assigned any data partitions, so unless partitions are moved to them they won't be doing any work until new topics are created. So usually when you add machines to your cluster you will want to migrate some existing data to these machines.

The process of migrating data is manually initiated but fully automated. Under the covers what happens is that Kafka will add the new server as a follower of the partition it is migrating and allow it to fully replicate the existing data in that partition. When the new server has fully replicated the contents of this partition and joined the in-sync replica one of the existing replicas will delete their partition's data.

The partition reassignment tool does not have the capability to automatically study the data distribution in a Kafka cluster and move partitions around to attain an even load distribution. As such, the admin has to figure out which topics or partitions should be moved around.

The partition reassignment tool can run in 3 mutually exclusive modes:

- `--generate`: In this mode, given a list of topics and a list of brokers, the tool generates a candidate reassignment to move all partitions of the specified topics to the new brokers.
- `--execute`: In this mode, the tool kicks off the reassignment of partitions based on the user provided reassignment plan (using the `--reassignment-json-file` option).
- `--verify`: In this mode, the tool verifies the status of the reassignment for all partitions listed during the last `--execute`. The status can be either of successfully completed, failed or in progress.

#### Automatically migrating data to new machines

```
$ cat topics-to-move.json
{
  "topics": [
    { "topic": "foo1" },
    { "topic": "foo2" }
  ],
  "version": 1
}

$ bin/kafka-reassign-partitions.sh --bootstrap-server localhost:9092 --topics-to-move-json-file topics-to-move.json --broker-list "5,6" --generate
Current partition replica assignment
{"version":1,
 "partitions":[{"topic":"foo1","partition":0,"replicas":[2,1],"log_dirs":["any"]},
               {"topic":"foo1","partition":1,"replicas":[1,3],"log_dirs":["any"]},
               {"topic":"foo2","partition":0,"replicas":[4,2],"log_dirs":["any"]}]
}
Proposed partition reassignment configuration
{"version":1,
 "partitions":[{"topic":"foo1","partition":0,"replicas":[6,5],"log_dirs":["any"]},
               {"topic":"foo1","partition":1,"replicas":[5,6],"log_dirs":["any"]},
               {"topic":"foo2","partition":0,"replicas":[5,6],"log_dirs":["any"]}]
}
```

Note, however, that at this point, the partition movement has not started, it merely tells you the current assignment and the proposed new assignment. The current assignment should be saved in case you want to rollback to it. The new assignment should be saved in a json file (e.g. expand-cluster-reassignment.json) to be input to the tool with the `--execute` option:

```
$ bin/kafka-reassign-partitions.sh --bootstrap-server localhost:9092 --reassignment-json-file expand-cluster-reassignment.json --execute
Current partition replica assignment
{...}
Save this to use as the --reassignment-json-file option during rollback
Successfully started partition reassignments for foo1-0,foo1-1,foo1-2,foo2-0,foo2-1,foo2-2

$ bin/kafka-reassign-partitions.sh --bootstrap-server localhost:9092 --reassignment-json-file expand-cluster-reassignment.json --verify
Status of partition reassignment:
Reassignment of partition [foo1,0] is completed
Reassignment of partition [foo1,1] is still in progress
Reassignment of partition [foo2,0] is completed
```

#### Custom partition assignment and migration

```
$ cat custom-reassignment.json
{"version":1,"partitions":[{"topic":"foo1","partition":0,"replicas":[5,6]},{"topic":"foo2","partition":1,"replicas":[2,3]}]}
$ bin/kafka-reassign-partitions.sh --bootstrap-server localhost:9092 --reassignment-json-file custom-reassignment.json --execute
```

### Decommissioning brokers

The first step to decommission brokers is to mark them as cordoned via the Admin API. For example to cordon broker 1:

```
$ bin/kafka-configs.sh --bootstrap-server localhost:9092 --alter --add-config cordoned.log.dirs="*" --entity-type brokers --entity-name 1
```

Then reassign all the partitions from that broker to other brokers in the cluster. The partition reassignment tool does not have the ability to automatically generate a reassignment plan for decommissioning brokers yet. Once all the reassignment is done, shutdown the broker and unregister it to remove it from the cluster:

```
$ bin/kafka-cluster.sh unregister --bootstrap-server localhost:9092 --id 1
```

### Increasing replication factor

Increasing the replication factor of an existing partition is easy. Just specify the extra replicas in the custom reassignment json file and use it with the `--execute` option. For instance, the following example increases the replication factor of partition 0 of topic foo from 1 to 3 (replica existed on broker 5; add replicas on brokers 6 and 7):

```
$ cat increase-replication-factor.json
{"version":1,
 "partitions":[{"topic":"foo","partition":0,"replicas":[5,6,7]}]}
$ bin/kafka-reassign-partitions.sh --bootstrap-server localhost:9092 --reassignment-json-file increase-replication-factor.json --execute
$ bin/kafka-topics.sh --bootstrap-server localhost:9092 --topic foo --describe
Topic:foo	PartitionCount:1	ReplicationFactor:3	Configs:
  Topic: foo	Partition: 0	Leader: 5	Replicas: 5,6,7	Isr: 5,6,7
```

### Limiting bandwidth usage during data migration

Kafka lets you apply a throttle to replication traffic, setting an upper bound on the bandwidth used to move replicas from machine to machine and from disk to disk. This is useful when rebalancing a cluster, adding or removing brokers or adding or removing disks, as it limits the impact these data-intensive operations will have on users.

```
$ bin/kafka-reassign-partitions.sh --bootstrap-server localhost:9092 --execute --reassignment-json-file bigger-cluster.json --throttle 50000000 --replica-alter-log-dirs-throttle 100000000
The inter-broker throttle limit was set to 50000000 B/s
The replica-alter-dir throttle limit was set to 100000000 B/s
Successfully started partition reassignment for foo1-0
```

Should you wish to alter the throttle, during a rebalance, you can do this by re-running the execute command with the `--additional` option passing the same reassignment-json-file:

```
$ bin/kafka-reassign-partitions.sh --bootstrap-server localhost:9092 --additional --execute --reassignment-json-file bigger-cluster.json --throttle 700000000
```

Once the rebalance completes the administrator can check the status of the rebalance using the `--verify` option. If the rebalance has completed, the throttle will be removed via the `--verify` command. It is important that administrators remove the throttle in a timely manner once rebalancing completes by running the command with the `--verify` option. Failure to do so could cause regular replication traffic to be throttled.

```
$ bin/kafka-reassign-partitions.sh --bootstrap-server localhost:9092 --verify --reassignment-json-file bigger-cluster.json
Status of partition reassignment:
Reassignment of partition [my-topic,1] is completed
Reassignment of partition [my-topic,0] is completed
Clearing broker-level throttles on brokers 1,2,3
Clearing topic-level throttles on topic my-topic
```

There are two sets of throttle configuration used to manage the throttling process. First set refers to the throttle value itself, configured at a broker level using the dynamic properties `leader.replication.throttled.rate`, `follower.replication.throttled.rate`, `replica.alter.log.dirs.io.max.bytes.per.second`. Then there is the configuration pair of enumerated sets of throttled replicas `leader.replication.throttled.replicas`, `follower.replication.throttled.replicas`, configured per topic. All five config values are automatically assigned by kafka-reassign-partitions.sh.

By default kafka-reassign-partitions.sh will apply the leader throttle to all replicas that exist before the rebalance, any one of which might be leader. It will apply the follower throttle to all move destinations.

#### Safe usage of throttled replication

(1) Throttle Removal: The throttle should be removed in a timely manner once reassignment completes (by running `bin/kafka-reassign-partitions.sh --verify`).

(2) Ensuring Progress: If the throttle is set too low, in comparison to the incoming write rate, it is possible for replication to not make progress. This occurs when: `max(BytesInPerSec) > throttle`. The administrator can monitor whether replication is making progress using the metric `kafka.server:type=FetcherLagMetrics,name=ConsumerLag,clientId=([-.\w]+),topic=([-.\w]+),partition=([0-9]+)`. The lag should constantly decrease during replication.

### Setting quotas

```
$ bin/kafka-configs.sh --bootstrap-server localhost:9092 --alter --add-config 'producer_byte_rate=1024,consumer_byte_rate=2048,request_percentage=200' --entity-type users --entity-name user1 --entity-type clients --entity-name clientA
```
