# ksqlDB — Concepts (streams, tables, push/pull queries, persistent queries)

> **Nguồn (official):** https://docs.confluent.io/platform/current/ksqldb/concepts/index.html (tham khảo thêm https://docs.ksqldb.io/en/latest/concepts/)
> **Tuần:** 6 — Kafka Streams · **Loại:** Confluent Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có rút gọn) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất. CCDAK chỉ yêu cầu **nhận diện** ksqlDB, không hỏi cú pháp sâu.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- **ksqlDB** = "streaming SQL database" **xây trên Kafka Streams**: mỗi persistent query được biên dịch thành một **Kafka Streams topology** chạy trong ksqlDB Server → không cần viết Java. Không phải database truyền thống; dữ liệu vẫn nằm trong Kafka topic.
- **STREAM** = tập sự kiện **immutable, append-only** (≈ `KStream`) · **TABLE** = **mutable, giá trị mới nhất mỗi key** (≈ `KTable`, cần `PRIMARY KEY`). Cùng một topic có thể khai báo thành STREAM hoặc TABLE (stream-table duality).
- **Persistent query**: `CREATE STREAM ... AS SELECT` (CSAS) / `CREATE TABLE ... AS SELECT` (CTAS) — chạy **liên tục**, ghi kết quả vào **topic mới**, sống sót qua restart server (lưu trong **command topic**).
- **Push query** (`SELECT ... EMIT CHANGES`) → stream kết quả **liên tục** tới client (dashboard real-time). **Pull query** (`SELECT ... FROM table WHERE key = ...`, không `EMIT CHANGES`) → trả **snapshot hiện tại** từ materialized view rồi kết thúc (giống lookup DB / Interactive Query).
- Window trong SQL: `WINDOW TUMBLING (SIZE 1 MINUTE)`, `WINDOW HOPPING (SIZE 5 MINUTES, ADVANCE BY 1 MINUTE)`, `WINDOW SESSION (5 MINUTES)`, thêm `GRACE PERIOD`.
- Join: stream-stream (cần `WITHIN`), stream-table, table-table — cùng quy tắc co-partition như Streams.
- Kiến trúc: **ksqlDB Server** (REST API port **8088**), **ksqlDB CLI**, **command topic** (`_confluent-ksql-<service.id>_command_topic`) lưu DDL/DML; `ksql.service.id` định danh cụm ksqlDB (nhiều server cùng id = 1 cụm, chia task như Streams instance).
- **Interactive mode** (nhận query qua CLI/REST) vs **Headless mode** (chạy file `.sql` cố định, không nhận query mới — production).
- So sánh: Kafka Streams = library Java, kiểm soát tối đa, unit test bằng `TopologyTestDriver`; ksqlDB = SQL, triển khai server riêng, prototyping/ETL nhanh; Connect = di chuyển dữ liệu (không biến đổi phức tạp).

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Overview

ksqlDB is a streaming SQL database built on Apache Kafka and Kafka Streams that enables real-time data processing using SQL queries. It provides a familiar SQL interface for stream processing without requiring Java development. Under the hood every persistent query is executed as a Kafka Streams application inside the ksqlDB server processes.

### Core data structures — streams vs tables

**Streams** represent immutable, append-only collections of events. Each new record is added to the stream without modifying existing data. Streams are ideal for event logs and time-series data.

**Tables** represent mutable collections where the latest value for each key is maintained. Tables store the current state and are updated when new records arrive with an existing key. Tables are suitable for maintaining state or dimension data. A table requires a `PRIMARY KEY`.

```sql
CREATE STREAM events (id INT KEY, name STRING)
  WITH (kafka_topic='events', value_format='JSON', partitions=3);

CREATE TABLE users (id INT PRIMARY KEY, name STRING)
  WITH (kafka_topic='users', value_format='JSON');
```

Both streams and tables are backed by Kafka topics; declaring one is metadata only (no data is copied) unless created with `AS SELECT`.

### Query types

**Persistent queries** run continuously and write results to new Kafka topics. Created using `CREATE STREAM AS SELECT` or `CREATE TABLE AS SELECT`, they process data indefinitely and are restarted automatically when the server restarts.

```sql
CREATE STREAM filtered_events AS
  SELECT id, name FROM events WHERE id > 100 EMIT CHANGES;

CREATE TABLE events_per_id AS
  SELECT id, COUNT(*) AS cnt FROM events GROUP BY id EMIT CHANGES;
```

**Push queries** stream results to clients as they arrive, using `EMIT CHANGES`. They are useful for real-time dashboards and monitoring; the query runs until the client disconnects.

```sql
SELECT id, name FROM events EMIT CHANGES;
```

**Pull queries** retrieve the current state from materialized views (tables), returning a finite result set and then terminating — comparable to a key lookup against a database or a Kafka Streams interactive query.

```sql
SELECT * FROM events_per_id WHERE id = 5;
```

### Materialized views

Materialized views are tables created from persistent queries (typically aggregations) that maintain an up-to-date view of processed data. They are what pull queries read from; they are backed by Kafka Streams state stores and changelog topics.

### Windows

ksqlDB supports time-based windowing for aggregations:

- **Tumbling windows**: fixed-size, non-overlapping time intervals.
- **Hopping windows**: fixed-size intervals that overlap (`ADVANCE BY`).
- **Session windows**: dynamic windows based on inactivity periods.

```sql
SELECT id, WINDOWSTART, WINDOWEND, COUNT(*) FROM events
  WINDOW TUMBLING (SIZE 1 MINUTE, GRACE PERIOD 10 SECONDS)
  GROUP BY id EMIT CHANGES;
```

### Joins

ksqlDB supports joining streams with tables, streams with streams (windowed with `WITHIN`), and tables with tables, enabling correlation of data from multiple topics based on key columns or time windows. Inputs must be co-partitioned (same partition count and key format), otherwise ksqlDB repartitions automatically when possible.

```sql
CREATE STREAM enriched AS
  SELECT o.id, o.total, u.name
  FROM orders o
  LEFT JOIN users u ON o.user_id = u.id
  EMIT CHANGES;
```

### Architecture

- **ksqlDB Server**: the runtime engine processing queries, exposing a REST API on port 8088 by default. Multiple servers with the same `ksql.service.id` form a cluster and share the work of persistent queries (like Kafka Streams instances sharing tasks).
- **ksqlDB CLI**: interactive command-line interface for executing statements and managing the cluster.
- **REST API**: programmatic access to ksqlDB functionality via HTTP endpoints (`/ksql`, `/query`, `/query-stream`).
- **Command topic**: internal Kafka topic storing DDL and DML statements for cluster coordination and recovery.
- **`ksql.service.id`**: configuration parameter identifying the ksqlDB cluster, enabling multiple independent deployments against the same Kafka cluster.

### Deployment modes

- **Interactive mode**: clients connect to the server (CLI/REST) for live statement execution and management.
- **Headless mode**: the server starts with a fixed SQL file (`--queries-file`) and does not accept new statements — suitable for locked-down production deployments.
