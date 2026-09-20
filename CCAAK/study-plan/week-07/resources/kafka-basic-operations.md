# Apache Kafka 4.3 — Basic Operations: leader election, reassignment, graceful shutdown, log dir cordoning

> **Nguồn (official):** https://kafka.apache.org/43/operations/basic-kafka-operations/
> **Tuần:** 7 — Observability + Troubleshooting playbook · **Loại:** Apache Kafka Docs (§6.1 Basic Kafka Operations)
> ⚠️ Nội dung dưới đây được crawl tự động (HTTP → Markdown, có rút gọn) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- **Preferred replica** = broker **đầu tiên** trong danh sách replica của partition. `auto.leader.rebalance.enable=true` (mặc định) để controller tự trả leader về preferred; chạy tay bằng `kafka-leader-election.sh --election-type preferred --all-topic-partitions`. Đây là **hành động rẻ và đảo ngược được** sau khi restart broker.
- **`kafka-reassign-partitions.sh` có 3 mode loại trừ nhau:** `--generate` (sinh plan từ `--topics-to-move-json-file` + `--broker-list`), `--execute` (áp dụng `--reassignment-json-file`), `--verify` (kiểm tra tiến độ). **`--verify` khi hoàn tất sẽ tự gỡ throttle** — quên chạy `--verify` là để throttle treo vĩnh viễn, một sự cố vận hành kinh điển.
- Throttle băng thông: `--throttle 50000000` (byte/s cho replication giữa broker) và `--replica-alter-log-dirs-throttle 100000000` (di chuyển giữa log dir trên **cùng** broker).
- **Graceful shutdown** (`controlled.shutdown.enable=true`, mặc định): broker **sync log xuống đĩa** (tránh log recovery chậm khi start lại) và **chuyển leadership** sang replica khác trước khi tắt. Docs ghi rõ: chỉ thành công khi **mọi partition có replica và ít nhất 1 replica còn sống** — đây là lý do rolling restart phải **chờ URP về 0** giữa hai broker.
- `kafka-consumer-groups.sh --describe --group X` in các cột: `TOPIC PARTITION CURRENT-OFFSET LOG-END-OFFSET LAG CONSUMER-ID HOST CLIENT-ID`. Biến thể: `--members`, `--members --verbose` (xem assignment từng member → phát hiện skew), `--state` (in `COORDINATOR ASSIGNMENT-STRATEGY STATE #MEMBERS`).
- **`cordoned.log.dirs`** (config động ở mức broker) — "rào" một log dir lại: Kafka không đặt partition mới lên đó nữa, để bạn di chuyển dữ liệu đi trước khi rút ổ. Gỡ rào bằng `--delete-config cordoned.log.dirs`, rồi mới sửa `log.dirs` và restart.
- `kafka-configs.sh` chấp nhận cả `--bootstrap-server` (qua broker) và `--bootstrap-controller` (thẳng tới controller) — hữu ích khi broker đang có vấn đề.
- Thêm broker mới **không** tự nhận partition: phải reassignment. Đây là câu hỏi lặp lại trong đề.

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Balancing leadership

Whenever a broker stops or crashes, leadership for that broker's partitions transfers to other replicas. When the broker is restarted it will only be a follower for all its partitions, meaning it will not be used for client reads and writes.

To avoid this imbalance, Kafka has a notion of preferred replicas. If the list of replicas for a partition is 1,5,9 then node 1 is preferred as the leader to either node 5 or 9 because it is earlier in the replica list.

By default the Kafka cluster will try to restore leadership to the preferred replicas. This behaviour is configured with:

```
auto.leader.rebalance.enable=true
```

You can also set this to false, but you will then need to manually restore leadership to the restored replicas by running the command:

```bash
$ bin/kafka-leader-election.sh --bootstrap-server localhost:9092 --election-type preferred --all-topic-partitions
```

### Expanding your cluster

Adding servers to a Kafka cluster is easy, just assign them a unique broker id and start up Kafka on your new servers. However these new servers will not automatically be assigned any data partitions, so unless partitions are moved to them they won't be doing any work until new topics are created. So usually when you add machines to your cluster you will want to migrate some existing data to these machines.

The process of migrating data is manually initiated but fully automated. Under the covers what happens is that Kafka will add the new server as a follower of the partition it is migrating and allow it to fully replicate the existing data in that partition. When the new server has fully replicated the contents of this partition and joined the in-sync replica one of the existing replicas will delete their partition's data.

The partition reassignment tool can run in 3 mutually exclusive modes:

- `--generate`: In this mode, given a list of topics and a list of brokers, the tool generates a candidate reassignment to move all partitions of the specified topics to the new brokers. This option merely provides a convenient way to generate a partition reassignment plan given a list of topics and target brokers.
- `--execute`: In this mode, the tool kicks off the reassignment of partitions based on the user provided reassignment plan. (using the `--reassignment-json-file` option). This can either be a custom reassignment plan hand crafted by the admin or provided by using the `--generate` option.
- `--verify`: In this mode, the tool verifies the status of the reassignment for all partitions listed during the last `--execute`. The status can be either of successfully completed, failed or in progress.

Example — generate a plan:

```bash
$ bin/kafka-reassign-partitions.sh --bootstrap-server localhost:9092 --topics-to-move-json-file topics-to-move.json --broker-list "5,6" --generate
```

Example — execute:

```bash
$ bin/kafka-reassign-partitions.sh --bootstrap-server localhost:9092 --reassignment-json-file expand-cluster-reassignment.json --execute
```

Example — verify:

```bash
$ bin/kafka-reassign-partitions.sh --bootstrap-server localhost:9092 --reassignment-json-file expand-cluster-reassignment.json --verify
```

### Throttling data migration

Kafka lets you apply a throttle to replication traffic, setting an upper bound on the bandwidth used to move replicas from machine to machine. This is useful when rebalancing a cluster, bootstrapping a new broker or adding or removing brokers, as it limits the impact these data-intensive operations will have on users.

```bash
$ bin/kafka-reassign-partitions.sh --bootstrap-server localhost:9092 --execute --reassignment-json-file bigger-cluster.json --throttle 50000000 --replica-alter-log-dirs-throttle 100000000
```

When you execute this script you will see the throttle engage. Note that the throttle value is in bytes per second.

Once the rebalance completes the administrator can check the status of the rebalance using the `--verify` command. If the rebalance has completed, the throttle will be removed via the `--verify` command. It is important that administrators remove the throttle in a timely manner once rebalancing completes by running the command with the `--verify` option. Failure to do so could cause regular replication traffic to be throttled.

### Graceful shutdown

The Kafka cluster will automatically detect any broker shutdown or failure and elect new leaders for the partitions on that machine. This will occur whether a server fails or it is brought down intentionally for maintenance or configuration changes. For the latter cases Kafka supports a more graceful mechanism for stopping a server than just killing it. When a server is stopped gracefully it has two optimizations it will take advantage of:

1. It will sync all its logs to disk to avoid needing to do any log recovery when it restarts (i.e. validating the checksum for all messages in the tail of the log). Log recovery takes time so this speeds up intentional restarts.
2. It will migrate any partitions the server is the leader for to other replicas prior to shutting down. This will make the leadership transfer faster and minimize the time each partition is unavailable to a few milliseconds.

Syncing the logs will happen automatically whenever the server is stopped other than by a hard kill, but the controlled leadership migration requires using a special setting:

```
controlled.shutdown.enable=true
```

Note that controlled shutdown will only succeed if all the partitions hosted on the broker have replicas (i.e. the replication factor is greater than 1 and at least one of these replicas is alive). This is generally what you want since shutting down the last replica would make that topic partition unavailable.

### Checking consumer position

Sometimes it's useful to see the position of your consumers. We have a tool that will show the position of all consumers in a consumer group as well as how far behind the end of the log they are.

```bash
$ bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --describe --group my-group

TOPIC           PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG  CONSUMER-ID    HOST            CLIENT-ID
my-topic        0          2               4               2    consumer-1-... /127.0.0.1      consumer-1
my-topic        1          2               3               1    consumer-1-... /127.0.0.1      consumer-1
my-topic        2          2               3               1    consumer-2-... /127.0.0.1      consumer-2
```

To view the members of a group:

```bash
$ bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --describe --group my-group --members
```

Adding `--verbose` also lists the partitions assigned to each member. To get an overview of the group:

```bash
$ bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --describe --group my-group --state

COORDINATOR (ID)          ASSIGNMENT-STRATEGY  STATE     #MEMBERS
localhost:9092 (0)        range                Stable    4
```

### Decommissioning a log directory

Before removing a log directory from `log.dirs`, cordon it so that no new partitions are placed on it:

```bash
$ bin/kafka-configs.sh --bootstrap-server localhost:9092 --alter --add-config cordoned.log.dirs=/data/dir1 --entity-type brokers --entity-name 1
```

After the partitions have been moved off the directory, uncordon it and update the broker configuration:

```bash
$ bin/kafka-configs.sh --bootstrap-controller localhost:9093 --alter --delete-config cordoned.log.dirs --entity-type brokers --entity-name 1
```

Then remove the directory from `log.dirs` and restart the broker.
