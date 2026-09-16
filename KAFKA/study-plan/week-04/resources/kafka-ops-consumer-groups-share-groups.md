# Apache Kafka 4.3 Operations — Managing Consumer Groups & Managing Share Groups (`kafka-consumer-groups.sh`, `kafka-share-groups.sh`)

> **Nguồn (official):** https://kafka.apache.org/43/operations/basic-kafka-operations/ (mục *Managing Consumer Groups*, *Managing Share Groups*)
> **Tuần:** 4 — Consumer chuyên sâu: group, rebalance, offset · **Loại:** Apache Kafka Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có rút gọn) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- `kafka-consumer-groups.sh --describe --group g` in **`TOPIC PARTITION CURRENT-OFFSET LOG-END-OFFSET LAG CONSUMER-ID HOST CLIENT-ID`**; **LAG = LOG-END-OFFSET − CURRENT-OFFSET** (CURRENT-OFFSET = committed offset).
- `--members` (số partition mỗi member), `--members --verbose` (kèm cột ASSIGNMENT — dùng để thấy consumer **idle** có `#PARTITIONS 0`), `--state` (COORDINATOR, ASSIGNMENT-STRATEGY, STATE, #MEMBERS).
- `--delete --group g` chỉ thành công khi group **không còn member active**.
- `--reset-offsets` cần **group inactive** (không consumer nào đang chạy); **mặc định chỉ hiển thị (dry-run)** — phải thêm **`--execute`** để áp dụng; `--export` xuất CSV để dùng lại với `--from-file`.
- 8 scenario reset: `--to-datetime YYYY-MM-DDThh:mm:ss.sss`, `--by-duration PnDTnHnMnS`, `--to-earliest`, `--to-latest`, `--shift-by ±N`, `--to-offset N`, `--to-current`, `--from-file file.csv`; scope `--topic t` (hoặc `t:0,1`) hay `--all-topics`. Offset ngoài range được tự chỉnh về range hợp lệ.
- Share group có tool riêng `kafka-share-groups.sh`: `--describe` in **`START-OFFSET`** và `LAG` (không có CURRENT-OFFSET vì không commit theo offset); `--members` cho thấy **nhiều member cùng 1 partition** (`topic1:0` xuất hiện ở 2 dòng); reset chỉ có `--to-datetime/--to-earliest/--to-latest`.
- Console consumer cho share group: `kafka-console-share-consumer.sh`; `kafka-console-consumer.sh` **không** đọc được theo share group.

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Managing Consumer Groups

With the ConsumerGroupCommand tool, we can list, describe, or delete the consumer groups. The consumer group can be deleted manually, or automatically when the last committed offset for that group expires. Manual deletion works only if the group does not have any active members.

For example, to list all consumer groups across all topics:

```bash
$ bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --list
test-consumer-group
```

To view offsets, as mentioned earlier, we "describe" the consumer group like this:

```bash
$ bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --describe --group my-group
TOPIC           PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG             CONSUMER-ID                                    HOST            CLIENT-ID
topic3          0          241019          395308          154289          consumer2-e76ea8c3-5d30-4299-9005-47eb41f3d3c4 /127.0.0.1      consumer2
topic2          1          520678          803288          282610          consumer2-e76ea8c3-5d30-4299-9005-47eb41f3d3c4 /127.0.0.1      consumer2
topic3          1          241018          398817          157799          consumer2-e76ea8c3-5d30-4299-9005-47eb41f3d3c4 /127.0.0.1      consumer2
topic1          0          854144          855809          1665            consumer1-3fc8d6f1-581a-4472-bdf3-3515b4aee8c1 /127.0.0.1      consumer1
topic2          0          460537          803290          342753          consumer1-3fc8d6f1-581a-4472-bdf3-3515b4aee8c1 /127.0.0.1      consumer1
topic3          2          243655          398812          155157          consumer4-117fe4d3-c6c1-4178-8ee9-eb4a3954bee0 /127.0.0.1      consumer4
```

There are a number of additional "describe" options that can be used to provide more detailed information about a consumer group:

- `--members`: This option provides the list of all active members in the consumer group.

```bash
$ bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --describe --group my-group --members
CONSUMER-ID                                    HOST            CLIENT-ID       #PARTITIONS
consumer1-3fc8d6f1-581a-4472-bdf3-3515b4aee8c1 /127.0.0.1      consumer1       2
consumer4-117fe4d3-c6c1-4178-8ee9-eb4a3954bee0 /127.0.0.1      consumer4       1
consumer2-e76ea8c3-5d30-4299-9005-47eb41f3d3c4 /127.0.0.1      consumer2       3
consumer3-ecea43e4-1f01-479f-8349-f9130b75d8ee /127.0.0.1      consumer3       0
```

- `--members --verbose`: On top of the information reported by the `--members` option above, this option also provides the partitions assigned to each member.

```bash
$ bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --describe --group my-group --members --verbose
CONSUMER-ID                                    HOST            CLIENT-ID       #PARTITIONS     ASSIGNMENT
consumer1-3fc8d6f1-581a-4472-bdf3-3515b4aee8c1 /127.0.0.1      consumer1       2               topic1(0), topic2(0)
consumer4-117fe4d3-c6c1-4178-8ee9-eb4a3954bee0 /127.0.0.1      consumer4       1               topic3(2)
consumer2-e76ea8c3-5d30-4299-9005-47eb41f3d3c4 /127.0.0.1      consumer2       3               topic2(1), topic3(0,1)
consumer3-ecea43e4-1f01-479f-8349-f9130b75d8ee /127.0.0.1      consumer3       0               -
```

- `--offsets`: This is the default describe option and provides the same output as the "--describe" option.
- `--state`: This option provides useful group-level information.

```bash
$ bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --describe --group my-group --state
COORDINATOR (ID)          ASSIGNMENT-STRATEGY       STATE                #MEMBERS
localhost:9092 (0)        range                     Stable               4
```

To manually delete one or multiple consumer groups, the `--delete` option can be used:

```bash
$ bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --delete --group my-group --group my-other-group
Deletion of requested consumer groups ('my-group', 'my-other-group') was successful.
```

To reset offsets of a consumer group, `--reset-offsets` option can be used. This option supports one consumer group at the time. It requires defining following scopes: `--all-topics` or `--topic`. One scope must be selected, unless you use `--from-file` scenario. Also, first make sure that the consumer instances are inactive.

It has 3 execution options:

- (default) to display which offsets to reset.
- `--execute` : to execute `--reset-offsets` process.
- `--export` : to export the results to a CSV format.

`--reset-offsets` also has following scenarios to choose from (at least one scenario must be selected):

- `--to-datetime <String: datetime>` : Reset offsets to offsets from datetime. Format: 'YYYY-MM-DDThh:mm:ss.sss'
- `--to-earliest` : Reset offsets to earliest offset.
- `--to-latest` : Reset offsets to latest offset.
- `--shift-by <Long: number-of-offsets>` : Reset offsets shifting current offset by 'n', where 'n' can be positive or negative.
- `--from-file` : Reset offsets to values defined in CSV file.
- `--to-current` : Resets offsets to current offset.
- `--by-duration <String: duration>` : Reset offsets to offset by duration from current timestamp. Format: 'PnDTnHnMnS'
- `--to-offset` : Reset offsets to a specific offset.

Please note, that out of range offsets will be adjusted to available offset end. For example, if offset end is at 10 and offset shift request is of 15, then, offset at 10 will actually be selected.

For example, to reset offsets of a consumer group to the latest offset:

```bash
$ bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --reset-offsets --group consumergroup1 --topic topic1 --to-latest
TOPIC                          PARTITION  NEW-OFFSET
topic1                         0          0
```

### Managing Share Groups

With the ShareGroupCommand tool, we can list, describe, or delete the share groups. The share group can be deleted manually. Manual deletion works only if the group does not have any active members.

For example, to list all share groups across all topics:

```bash
$ bin/kafka-share-groups.sh --bootstrap-server localhost:9092 --list
my-share-group
```

To view the start offset and lag, we "describe" the share group like this:

```bash
$ bin/kafka-share-groups.sh --bootstrap-server localhost:9092 --describe --group my-share-group
GROUP           TOPIC           PARTITION  START-OFFSET  LAG
my-share-group  topic1          0          4             0
```

The start offset indicates the earliest offset for in-flight records under evaluation for delivery. The admin client requires DESCRIBE access to all group topics.

- `--members`: This option provides the list of all active members in the share group.

```bash
$ bin/kafka-share-groups.sh --bootstrap-server localhost:9092 --describe --group my-share-group --members
GROUP           CONSUMER-ID            HOST            CLIENT-ID              #PARTITIONS  ASSIGNMENT
my-share-group  94wrSQNmRda9Q6sk6jMO6Q /127.0.0.1      console-share-consumer 1            topic1:0
my-share-group  EfI0sha8QSKSrL_-I_zaTA /127.0.0.1      console-share-consumer 1            topic1:0
```

- `--state`: This option provides useful group-level information.

```bash
$ bin/kafka-share-groups.sh --bootstrap-server localhost:9092 --describe --group my-share-group --state
GROUP           COORDINATOR (ID)          STATE           #MEMBERS
my-share-group  localhost:9092  (1)       Stable          2
```

To reset offsets of a share group, `--reset-offsets` option can be used. This option supports one share group at the time. It requires defining following scopes: `--all-topics` or `--topic`. One scope must be selected. Also, first make sure that the share group is empty.

It has 2 execution options: `--dry-run` (to display which offsets to reset) and `--execute` (to execute the reset). Scenarios: `--to-datetime <String: datetime>` (format 'YYYY-MM-DDThh:mm:ss.sss'), `--to-earliest`, `--to-latest`.

```bash
$ bin/kafka-share-groups.sh --bootstrap-server localhost:9092 --reset-offsets --group my-share-group --topic topic1 --to-latest --execute
GROUP           TOPIC           PARTITION  NEW-OFFSET
my-share-group  topic1          0          10
```

To delete the offsets of a topic in a share group, the `--delete-offsets` option can be used:

```bash
$ bin/kafka-share-groups.sh --bootstrap-server localhost:9092 --delete-offsets --group my-share-group --topic topic1
TOPIC           STATUS
topic1          Successful
```

To manually delete one or multiple share groups, the `--delete` option can be used:

```bash
$ bin/kafka-share-groups.sh --bootstrap-server localhost:9092 --delete --group my-share-group
Deletion of requested share groups ('my-share-group') was successful.
```

A console share consumer is provided for testing: `bin/kafka-console-share-consumer.sh --bootstrap-server localhost:9092 --topic topic1 --group my-share-group` (the classic `kafka-console-consumer.sh` cannot consume as a share group member).
