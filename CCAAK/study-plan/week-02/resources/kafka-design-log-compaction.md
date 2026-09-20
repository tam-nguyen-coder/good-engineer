# Apache Kafka 4.3 — Design: Log Compaction (+ zero-copy, segment)

> **Nguồn (official):** https://kafka.apache.org/43/design/design/#log-compaction (trang cha: https://kafka.apache.org/43/design/design/)
> **Tuần:** 2 — Cluster Config I · **Loại:** Apache Kafka Docs (design)
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có rút gọn) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- Compaction đảm bảo **4 điều** — đề hay hỏi "cái nào KHÔNG được đảm bảo":
  1. Consumer **bám head** thấy **mọi** message, offset liên tiếp.
  2. **Thứ tự không bao giờ đổi** — compaction chỉ xoá bớt, không sắp xếp lại.
  3. **Offset của một message không bao giờ đổi** — nó là định danh vĩnh viễn của vị trí trong log.
  4. Consumer đọc **từ đầu log** thấy **ít nhất trạng thái cuối cùng** của mọi record, theo đúng thứ tự ghi.
  ➜ Cái **KHÔNG** được đảm bảo: "mỗi key chỉ còn đúng 1 bản ghi" — phần **head** chưa compact vẫn còn nhiều bản của cùng key.
- **Head vs tail:** head = phần mới, offset dày và liên tiếp, giữ mọi message; tail = phần đã compact, offset **giữ nguyên nhưng có lỗ**. Đọc một offset đã bị dọn → nhận offset kế tiếp còn tồn tại (không lỗi).
- **Tombstone** = record có value `null`. Nó xoá key, rồi **chính nó** bị dọn sau **`delete.retention.ms` (mặc định 24 h)**. Hệ quả: consumer bootstrap từ offset 0 **phải bắt kịp head trong 24 h**, nếu không sẽ bỏ lỡ tombstone và dựng lại state sai (một key đã xoá lại "sống dậy").
- **Log cleaner** là thread nền: chọn log có **tỉ lệ head/tail cao nhất**, dựng bản đồ offset cuối cùng theo key, copy lại segment sạch rồi hoán đổi ngay.
- Điều kiện để cleaner đụng vào một log: `min.cleanable.dirty.ratio` **0.5** (phải bẩn ≥ 50%), `min.compaction.lag.ms` **0** (chặn dọn record quá mới), `max.compaction.lag.ms` **Long.MAX** (deadline ép dọn cho topic ghi chậm). Và **luôn luôn**: cleaner chỉ làm việc trên **segment đã đóng**, không bao giờ đụng active segment.
- Kafka đọc/ghi nhanh nhờ **zero-copy** (`sendfile`): dữ liệu đi thẳng từ pagecache ra socket, không qua user space. Đây là lý do **page cache quan trọng hơn heap** khi sizing broker, và là lý do broker nén lại (`compression.type` khác `producer`) thì mất zero-copy.

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Log Compaction Guarantees

1. **Head Coverage** — "Any consumer that stays caught-up to within the head of the log will see every message that is written; these messages will have sequential offsets."
2. **Message Ordering** — "Ordering of messages is always maintained. Compaction will never re-order messages, just remove some."
3. **Offset Permanence** — "The offset for a message never changes. It is the permanent identifier for a position in the log."
4. **Final State Visibility** — "Any consumer progressing from the start of the log will see at least the final state of all records in the order they were written."

### Tail vs. Head

The log maintains a traditional **head** with dense, sequential offsets retaining all messages, while the compacted **tail** selectively removes records where newer updates exist for the same key. Original offsets remain valid permanently.

### Delete markers (tombstones)

Messages with null payloads function as deletion markers. These "tombstones" remove prior messages with matching keys but are themselves cleaned after **`delete.retention.ms`** expires (default **24 hours**).

### Timing controls

- **`log.cleaner.min.compaction.lag.ms`** — "Prevents messages newer than specified age from compaction"
- **`log.cleaner.max.compaction.lag.ms`** — "Ensures maximum delay before eligibility"

### Log cleaner process

Background threads recopying segments work by:

1. selecting the log with the **highest ratio of head to tail**,
2. summarizing the **last offset for each key** in the head,
3. recopying segments from beginning to end, **removing records whose key appears later** in the log,
4. swapping the clean segment into the log immediately.

### Configuring The Log Cleaner

Bật compaction cho một topic:

```
$ bin/kafka-configs.sh --bootstrap-server localhost:9092 --entity-type topics \
  --entity-name my-topic --alter --add-config cleanup.policy=compact
```

Các config điều khiển cleaner ở broker: `log.cleaner.threads`, `log.cleaner.dedupe.buffer.size`, `log.cleaner.io.buffer.size`, `log.cleaner.io.max.bytes.per.second`, `log.cleaner.backoff.ms`, `log.cleaner.min.cleanable.ratio`, `log.cleaner.delete.retention.ms`, `log.cleaner.min.compaction.lag.ms`, `log.cleaner.max.compaction.lag.ms`.

### Zero-copy (mục *Efficiency*)

> The design leverages `sendfile` system calls to transfer data directly from pagecache to network sockets, eliminating unnecessary kernel-to-user-space copies and enabling message consumption approaching network bandwidth limits.

### Log structure (mục *Implementation → Log*)

> "Each log file is named with the offset of the first message it contains. So the first file created will be `00000000000000000000.log`, and each additional file will have an integer name roughly *S* bytes from the previous file where *S* is the max log file size given in the configuration."

**Reads** — "Reads are done by giving the 64-bit logical offset of a message and an *S*-byte max chunk size. This will return an iterator over the messages contained in the *S*-byte buffer." Việc định vị dữ liệu gồm: tìm segment file chứa offset đó, tính offset cục bộ trong file từ offset toàn cục, rồi đọc từ vị trí đó.

**Deletes** — "Data is deleted one log segment at a time. The log manager applies two metrics to identify segments which are eligible for deletion: time and size."

**Guarantees** — "The log provides a configuration parameter *M* which controls the maximum number of messages that are written before forcing a flush to disk." (tương ứng `log.flush.interval.messages`, mặc định `Long.MAX` → thực tế không fsync theo message.)

> 📌 Câu **"Data is deleted one log segment at a time"** chính là gốc của bẫy kinh điển: đặt `retention.ms=1 giờ` nhưng để `segment.bytes` mặc định 1 GiB thì segment chưa bao giờ đóng → **không có gì bị xoá**. Muốn retention đúng hạn phải hạ `segment.ms` (hoặc `segment.bytes`) trước.
