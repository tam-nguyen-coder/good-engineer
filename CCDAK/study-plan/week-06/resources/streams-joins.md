# Kafka Streams DSL — Joining (join matrix, co-partitioning)

> **Nguồn (official):** https://docs.confluent.io/platform/current/streams/developer-guide/dsl-api.html#joining
> (bản Apache tương ứng: https://kafka.apache.org/documentation/streams/developer-guide/dsl-api.html#joining)
> **Tuần:** 6 — Kafka Streams · **Loại:** Confluent Docs (nội dung trùng Apache Kafka Docs)
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có rút gọn) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- **Co-partitioning** = 2 input phải có **cùng số partition** + **cùng chiến lược partition** (cùng key → cùng số partition). Streams **chỉ kiểm tra được số partition** lúc runtime (ném `TopologyException`), **không** kiểm tra được partitioner → bạn tự đảm bảo.
- **Không cần co-partition:** `KStream-GlobalKTable` (mỗi instance có full copy) và `KTable-KTable foreign-key join` (Streams tự xử lý nội bộ).
- **Join matrix:**
  - `KStream-KStream`: **windowed** (`JoinWindows`), inner/left/outer, **cần co-partition**. Mỗi record mới bên này khớp với **mọi** record bên kia trong window → có thể ra nhiều output.
  - `KTable-KTable`: **không window**, inner/left/outer; kết quả là `KTable`; **cần co-partition** (trừ FK join: inner/left, `join(other, foreignKeyExtractor, joiner)`).
  - `KStream-KTable`: **không window**, inner/left; **chỉ record bên stream mới trigger join** (table chỉ update state, không sinh output); kết quả `KStream`; **cần co-partition**.
  - `KStream-GlobalKTable`: **không window**, inner/left; dùng `KeyValueMapper` chọn **key bất kỳ** từ stream để lookup; **không cần co-partition**.
- `JoinWindows.ofTimeDifferenceWithNoGrace(Duration)` / `ofTimeDifferenceAndGrace` — API cũ `JoinWindows.of()` đã bỏ. Left/outer stream-stream join chỉ emit bản "không khớp" **sau khi grace hết** (từ 3.1, tránh kết quả giả).
- Record `null` key hoặc `null` value bên stream → **bỏ qua**; bên table `null` value = **tombstone** (xoá, có thể sinh tombstone ở kết quả).
- Left join: gọi `ValueJoiner(leftValue, null)`; outer join gọi cả `(null, rightValue)`.
- **Versioned state store** (3.5+) cho KTable giúp KStream-KTable join tra cứu đúng phiên bản theo timestamp; `Joined.withGracePeriod` bên stream-table join cần table là versioned store.
- Chọn nhanh: **enrich stream bằng bảng tham chiếu nhỏ** → `GlobalKTable`; **bảng lớn, cùng key** → `KTable`; **2 luồng sự kiện gần nhau về thời gian** (click ↔ impression) → `KStream-KStream` windowed.

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Co-partitioning requirements

For equi-joins to work correctly, input data must be co-partitioned. This ensures records with matching keys reach the same stream task. You are responsible for verifying co-partitioning. Requirements:

- Input topics must have the **same number of partitions**.
- All applications writing to input topics must use the **same partitioning strategy** so that records with the same key are delivered to the same partition number.

Kafka Streams verifies the partition count at runtime (throwing a `TopologyException` on mismatch) but cannot verify matching partitioning strategies — you must ensure this manually. If inputs are not co-partitioned, use `repartition()` (or an operation that marks for repartitioning followed by the join) to align the partition count.

**Exceptions:** co-partitioning is not required for KStream-GlobalKTable joins (GlobalKTable instances contain all partitions) or for KTable-KTable foreign-key joins (Kafka Streams handles co-partitioning internally via repartition topics).

### Join operations overview

| Join operands | Type | (INNER) JOIN | LEFT JOIN | OUTER JOIN | Co-partitioning required |
|---|---|---|---|---|---|
| KStream-to-KStream | Windowed | Supported | Supported | Supported | Yes |
| KTable-to-KTable | Non-windowed | Supported | Supported | Supported | Yes |
| KTable-to-KTable Foreign-Key | Non-windowed | Supported | Supported | Not supported | No (handled internally) |
| KStream-to-KTable | Non-windowed | Supported | Supported | Not supported | Yes |
| KStream-to-GlobalKTable | Non-windowed | Supported | Supported | Not supported | No |
| KTable-to-GlobalKTable | N/A | Not supported | Not supported | Not supported | — |

### KStream-KStream join (windowed)

Sliding window joins combine records "close" in time. New input on one side produces output for **each** matching record on the other side within the window. The join is symmetric.

```java
import java.time.Duration;

KStream<String, Long> left = ...;
KStream<String, Double> right = ...;

KStream<String, String> joined = left.join(right,
    (leftValue, rightValue) -> "left=" + leftValue + ", right=" + rightValue, /* ValueJoiner */
    JoinWindows.ofTimeDifferenceWithNoGrace(Duration.ofMinutes(5)),
    StreamJoined.with(
      Serdes.String(),  /* key */
      Serdes.Long(),    /* left value */
      Serdes.Double())  /* right value */
);
// leftJoin(...) and outerJoin(...) share the same signature
```

**Behavior:**

- Input records with `null` key or `null` value are ignored and do not trigger the join.
- The join is triggered whenever new input is received on either side, for each matching record within the window (time difference ≤ configured window).
- For LEFT JOIN: a left record with no match produces `ValueJoiner(leftValue, null)` — since 3.1 this "left-only" result is emitted only after the window's grace period has passed (to avoid spurious results).
- For OUTER JOIN: unmatched records from both sides produce `(leftValue, null)` / `(null, rightValue)` after the window closes.

### KTable-KTable join (non-windowed)

Symmetric join operating on the current table state (like a join between two materialized views). The result is a continuously updating KTable (changelog stream).

```java
KTable<String, Long> left = ...;
KTable<String, Double> right = ...;

KTable<String, String> joined = left.join(right,
    (leftValue, rightValue) -> "left=" + leftValue + ", right=" + rightValue);
// leftJoin(...), outerJoin(...)
```

**Behavior:**

- Input records with `null` key are ignored.
- Records with `null` value are interpreted as **tombstones** for the corresponding key, which indicate the deletion of the key from the table. Tombstones do not trigger the join but do trigger an output tombstone if the key already exists in the result table.
- The join is triggered whenever either side receives an update; LEFT JOIN calls `ValueJoiner(leftValue, null)` for unmatched left records, OUTER JOIN additionally calls `ValueJoiner(null, rightValue)`.

### KTable-KTable foreign-key join

Joins tables on different key types: the left table is keyed by its primary key; a `Function` extracts a **foreign key** from each left record and it is looked up against the right table's primary key (many-to-one).

```java
KTable<String, Long> left = ...;    // e.g. orders keyed by orderId, value contains customerId
KTable<Long, Double> right = ...;   // e.g. customers keyed by customerId

Function<Long, Long> foreignKeyExtractor = (leftValue) -> leftValue;   // extract FK from left value

KTable<String, String> joined = left.join(right,
    foreignKeyExtractor,
    (leftValue, rightValue) -> "left=" + leftValue + ", right=" + rightValue);
// leftJoin(right, foreignKeyExtractor, joiner) is also supported; no outer join
```

**Behavior:**

- Records for which the `foreignKeyExtractor` produces `null` are ignored (LEFT JOIN emits `(leftValue, null)` for them).
- A single right-table update triggers joins with **all** matching left records.
- Requires no manual co-partitioning; Kafka Streams creates internal subscription/response repartition topics.

### KStream-KTable join (non-windowed)

Asymmetric join performing a **table lookup** for each stream record. KTable updates refresh the table state but do **not** produce output. The result is a KStream.

```java
KStream<String, Long> stream = ...;
KTable<String, Double> table = ...;

KStream<String, String> joined = stream.join(table,
    (streamValue, tableValue) -> "stream=" + streamValue + ", table=" + tableValue,
    Joined.keySerde(Serdes.String())
      .withValueSerde(Serdes.Long())
      .withOtherValueSerde(Serdes.Double())
      .withGracePeriod(Duration.ZERO));   // grace requires a versioned table store
// leftJoin(...)
```

**Behavior:**

- "The join will be triggered whenever new input is received on the stream side"; table-side input only updates the internal state.
- Stream records with `null` key or `null` value are ignored; table records with `null` value are tombstones that delete the key.
- With a **versioned** table store, the lookup uses the table version matching the stream record's timestamp (temporal join). Kafka Streams uses timestamps to synchronize the two inputs (`max.task.idle.ms`), but timestamp-based ordering is best-effort.

### KStream-GlobalKTable join

A special case that requires **no co-partitioning**, because each GlobalKTable instance maintains all partitions locally. Supports non-key-based joins via a `KeyValueMapper` that computes the lookup key from the stream record's key and value.

```java
KStream<String, Long> stream = ...;
GlobalKTable<Integer, String> table = ...;

KStream<String, String> joined = stream.join(table,
    (leftKey, leftValue) -> leftKey.length(),   /* KeyValueMapper: derive the table key from the stream record */
    (leftValue, rightValue) -> "left=" + leftValue + ", right=" + rightValue);
// leftJoin(...)
```

**Behavior:**

- Triggered only by stream-side records; GlobalKTable updates only refresh the local state.
- The GlobalKTable is bootstrapped fully before processing starts; each instance holds a complete copy (suitable for small/medium reference data).
- Because there is no co-partitioning, the stream can be joined on a **foreign key** or any derived key, and the GlobalKTable topic may have a different partition count than the stream.
