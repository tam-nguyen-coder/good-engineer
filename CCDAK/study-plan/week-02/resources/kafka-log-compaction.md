# Apache Kafka Design — Log Compaction

> **Nguồn (official):** https://kafka.apache.org/43/design/design/#log-compaction
> **Tuần:** 2 — Độ tin cậy & lưu trữ · **Loại:** Apache Kafka Docs (4.3)
> ⚠️ Nội dung dưới đây được crawl tự động (qua curl + chuyển HTML → Markdown, có rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- **Log compaction** giữ lại **ít nhất giá trị cuối cùng cho mỗi key** trong một partition (thay cho retention theo thời gian/kích cỡ). Bật bằng topic config `cleanup.policy=compact` (broker default `log.cleanup.policy=delete`). Có thể dùng **cả hai** `compact,delete`.
- Dùng cho: **changelog/CDC** (database change subscription), **event sourcing**, **journaling state** (Kafka Streams changelog), và topic nội bộ **`__consumer_offsets`** (compacted).
- **Compacted topic BẮT BUỘC có key.** Record **key + value null = tombstone** (đánh dấu xoá); tombstone bị dọn sau **`delete.retention.ms` = 86 400 000 ms (24 h)**. Consumer đọc từ đầu phải tới head trong < 24 h mới thấy đủ tombstone.
- **Head** (chưa compact, offset liền mạch) vs **tail** (đã compact, offset **giữ nguyên**, có "lỗ"). Offset **không bao giờ đổi**; đọc tại offset đã bị compact sẽ trả về offset kế tiếp còn tồn tại.
- **4 đảm bảo:** (1) consumer bám head thấy mọi message; (2) **thứ tự không đổi**; (3) offset không đổi; (4) đọc từ đầu thấy **ít nhất trạng thái cuối** của mọi key + tombstone (nếu kịp trong `delete.retention.ms`).
- Compaction chạy **nền bởi log cleaner threads** (`log.cleaner.enable` mặc định true, deprecated — sẽ luôn bật ở 5.0), chỉ compact **segment đã đóng**; **active segment KHÔNG bao giờ bị compact** → lab cần `segment.ms` nhỏ để ép roll.
- Điều kiện được compact: **`min.cleanable.dirty.ratio` = 0.5** (dirty/total ≥ 50%); `min.compaction.lag.ms` (**0**) = thời gian tối thiểu message ở head; `max.compaction.lag.ms` (**MAX_LONG**) = deadline tối đa trước khi head đủ điều kiện compact (cho topic produce chậm).
- **Compaction KHÔNG đảm bảo chỉ còn đúng 1 record mỗi key** tại một thời điểm (head có thể còn trùng) — chỉ đảm bảo "ít nhất giá trị cuối".
- Cleaner dùng **24 byte/entry** cho hash map offset; 8 GB buffer dọn ~366 GB head (message 1 kB). Metrics theo dõi: `uncleanable-partitions-count`, `max-clean-time-secs`, `max-compaction-delay-secs`.
- **Tiered storage không hỗ trợ compacted topic** (xem tài nguyên tiered storage).

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Log Compaction

Log compaction ensures that Kafka will always retain at least the last known value for each message key within the log of data for a single topic partition. It addresses use cases and scenarios such as restoring state after application crashes or system failure, or reloading caches after application restarts during operational maintenance.

So far we have described only the simpler approach to data retention where old log data is discarded after a fixed period of time or when the log reaches some predetermined size. This works well for temporal event data such as logging where each record stands alone. However an important class of data streams are the log of changes to keyed, mutable data (for example, the changes to a database table).

Say we have a topic containing user email addresses; every time a user updates their email address we send a message to this topic using their user id as the primary key:

```
123 => bill@microsoft.com
        .
123 => bill@gatesfoundation.org
        .
123 => bill@gmail.com
```

Log compaction gives us a more granular retention mechanism so that we are guaranteed to retain at least the last update for each primary key (e.g. `bill@gmail.com`). By doing this we guarantee that the log contains a full snapshot of the final value for every key not just keys that changed recently. This means downstream consumers can restore their own state off this topic without us having to retain a complete log of all changes.

Use cases:

1. **Database change subscription.** It is often necessary to have a data set in multiple data systems, and often one of these systems is a database of some kind. Each change to the database will need to be reflected in the cache, the search cluster, and eventually in Hadoop. If you want to be able to reload the cache or restore a failed search node you may need a complete data set.
2. **Event sourcing.** This is a style of application design which co-locates query processing with application design and uses a log of changes as the primary store for the application.
3. **Journaling for high-availability.** A process that does local computation can be made fault-tolerant by logging out changes that it makes to its local state so another process can reload these changes and carry on if it should fail. A concrete example of this is handling counts, aggregations, and other "group by"-like processing in a stream query system.

Log compaction is a mechanism to give finer-grained per-record retention, rather than the coarser-grained time-based retention. The idea is to selectively remove records where we have a more recent update with the same primary key. This way the log is guaranteed to have at least the last state for each key.

This retention policy can be set per-topic, so a single cluster can have some topics where retention is enforced by size or time and other topics where retention is enforced by compaction.

### Log Compaction Basics

The head of the log is identical to a traditional Kafka log. It has dense, sequential offsets and retains all messages. Log compaction adds an option for handling the tail of the log. Note that the messages in the tail of the log retain the original offset assigned when they were first written — that never changes. Note also that all offsets remain valid positions in the log, even if the message with that offset has been compacted away; in this case this position is indistinguishable from the next highest offset that does appear in the log. For example, the offsets 36, 37, and 38 are all equivalent positions and a read beginning at any of these offsets would return a message set beginning with 38.

Compaction also allows for deletes. A message with a key and a null payload will be treated as a delete from the log. Such a record is sometimes referred to as a tombstone. This delete marker will cause any prior message with that key to be removed (as would any new message with that key), but delete markers are special in that they will themselves be cleaned out of the log after a period of time to free up space. The point in time at which deletes are no longer retained is marked as the "delete retention point".

The compaction is done in the background by periodically recopying log segments. Cleaning does not block reads and can be throttled to use no more than a configurable amount of I/O throughput to avoid impacting producers and consumers.

### What guarantees does log compaction provide?

1. Any consumer that stays caught-up to within the head of the log will see every message that is written; these messages will have sequential offsets. The topic's `min.compaction.lag.ms` can be used to guarantee the minimum length of time must pass after a message is written before it could be compacted, that is, it provides a lower bound on how long each message will remain in the (uncompacted) head. The topic's `max.compaction.lag.ms` can be used to guarantee the maximum delay between the time a message is written and the time the message becomes eligible for compaction.
2. Ordering of messages is always maintained. Compaction will never re-order messages, just remove some.
3. The offset for a message never changes. It is the permanent identifier for a position in the log.
4. Any consumer progressing from the start of the log will see at least the final state of all records in the order they were written. Additionally, all delete markers for deleted records will be seen, provided the consumer reaches the head of the log in a time period less than the topic's `delete.retention.ms` setting (the default is 24 hours). In other words: since the removal of delete markers happens concurrently with reads, it is possible for a consumer to miss delete markers if it lags by more than `delete.retention.ms`.

### Log Compaction Details

Log compaction is handled by the log cleaner, a pool of background threads that recopy log segment files, removing records whose key appears in the head of the log. Each compactor thread works as follows:

1. It chooses the log that has the highest ratio of log head to log tail
2. It creates a succinct summary of the last offset for each key in the head of the log
3. It recopies the log from beginning to end removing keys which have a later occurrence in the log. New, clean segments are swapped into the log immediately so the additional disk space required is just one additional log segment (not a full copy of the log).
4. The summary of the log head is essentially just a space-compact hash table. It uses exactly 24 bytes per entry. As a result with 8GB of cleaner buffer one cleaner iteration can clean around 366GB of log head (assuming 1kB messages).

### Configuring The Log Cleaner

The log cleaner is enabled by default. This will start the pool of cleaner threads. To enable log cleaning on a particular topic, add the log-specific property

```
log.cleanup.policy=compact
```

The `log.cleanup.policy` property is a broker configuration setting defined in the broker's `server.properties` file; it affects all of the topics in the cluster that do not have a configuration override in place. The log cleaner can be configured to retain a minimum amount of the uncompacted "head" of the log. This is enabled by setting the compaction time lag.

```
log.cleaner.min.compaction.lag.ms
```

This can be used to prevent messages newer than a minimum message age from being subject to compaction. If not set, all log segments are eligible for compaction except for the last segment, i.e. the one currently being written to. The active segment will not be compacted even if all of its messages are older than the minimum compaction time lag. The log cleaner can be configured to ensure a maximum delay after which the uncompacted "head" of the log becomes eligible for log compaction.

```
log.cleaner.max.compaction.lag.ms
```

This can be used to prevent log with low produce rate from remaining ineligible for compaction for an unbounded duration. If not set, logs that do not exceed min.cleanable.dirty.ratio are not compacted. Note that this compaction deadline is not a hard guarantee since it is still subjected to the availability of log cleaner threads and the actual compaction time. You will want to monitor the uncleanable-partitions-count, max-clean-time-secs and max-compaction-delay-secs metrics.

### Cleaner-related configs (broker → topic override), Kafka 4.3

| Broker config | Topic override | Default | Description |
|---|---|---|---|
| `log.cleanup.policy` | `cleanup.policy` | `delete` | `delete` discards old segments by time/size; `compact` retains the latest value per key; both allowed: `compact,delete` |
| `log.cleaner.delete.retention.ms` | `delete.retention.ms` | 86400000 (1 day) | Time to retain tombstone markers for compacted topics; also bounds the time a consumer must complete a read from offset 0 |
| `log.cleaner.min.cleanable.ratio` | `min.cleanable.dirty.ratio` | 0.5 | Minimum ratio of dirty log to total log for a log to be eligible for cleaning |
| `log.cleaner.min.compaction.lag.ms` | `min.compaction.lag.ms` | 0 | Minimum time a message will remain uncompacted |
| `log.cleaner.max.compaction.lag.ms` | `max.compaction.lag.ms` | 9223372036854775807 | Maximum time a message will remain ineligible for compaction |
| `log.cleaner.enable` | — | true | Deprecated, removed in 5.0 (always on). Must be enabled for `__consumer_offsets` |
| `log.roll.ms` / `log.roll.hours` | `segment.ms` | 7 days (604800000 ms) | Force roll even if the segment is not full "to ensure that retention can delete or compact old data" |
