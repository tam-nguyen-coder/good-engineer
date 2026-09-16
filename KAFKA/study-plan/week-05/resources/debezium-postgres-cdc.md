# Debezium PostgreSQL CDC Source Connector — Overview

> **Nguồn (official):** https://debezium.io/documentation/reference/stable/connectors/postgresql.html · bản tóm tắt trên Confluent Hub: https://docs.confluent.io/kafka-connectors/debezium-postgres-source/current/overview.html
> **Tuần:** 5 — Schema Registry & Serialization + Kafka Connect · **Loại:** Debezium Docs (qua Confluent Docs)
> ⚠️ Trang debezium.io trả 403 khi crawl; nội dung lấy từ trang Confluent tương ứng (crawl thành công) và bổ sung từ tài liệu Debezium — luôn đối chiếu link gốc.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- **CDC (Change Data Capture) log-based**: Debezium đọc **WAL** của Postgres qua **logical decoding** (plugin `pgoutput` có sẵn từ PG 10+, cũ hơn: `decoderbufs`/`wal2json`) → **không polling bảng**, bắt được cả **DELETE** (JDBC source polling theo timestamp/incrementing **không** bắt được delete).
- Yêu cầu DB: `wal_level=logical`, user có quyền `REPLICATION`, một **replication slot** (`slot.name`, mặc định `debezium`) + **publication** (`publication.name`, mặc định `dbz_publication`). Slot giữ WAL chưa đọc → connector dừng lâu có thể làm **đầy đĩa WAL**.
- Hai giai đoạn: **snapshot** ban đầu (đọc toàn bộ bảng, event `op=r`) → **streaming** liên tục. `snapshot.mode`: `initial` (mặc định), `always`, `never`, `initial_only`, `no_data`, `when_needed`…
- Topic mỗi bảng: **`<topic.prefix>.<schema>.<table>`** (ví dụ `pg1.public.customers`); metadata/schema-change topic tên `<topic.prefix>`.
- Envelope event: `before`, `after`, `source` (lsn, txId, ts_ms, db, schema, table), **`op`** = `c` (create/insert), `u` (update), `d` (delete), `r` (read/snapshot), `t` (truncate), `m` (message); `ts_ms`.
- **Delete** → 1 event `op=d` (`after=null`) + **1 tombstone** (value `null`, cùng key) để log compaction xoá key (`tombstones.on.delete=true` mặc định). Sink không xử lý được null → dùng SMT `Filter`+`RecordIsTombstone` hoặc tắt tombstone.
- `before` chỉ đầy đủ khi bảng có **`REPLICA IDENTITY FULL`**; mặc định (`DEFAULT`) chỉ có primary key trong `before`.
- Key record = **primary key** của hàng → cùng hàng luôn vào cùng partition → giữ thứ tự thay đổi theo hàng.
- Connector chỉ hỗ trợ **`tasks.max=1`** (1 replication slot = 1 stream); scale bằng nhiều connector/nhiều DB.
- SMT hay dùng: `io.debezium.transforms.ExtractNewRecordState` (unwrap, chỉ giữ `after`, thêm `__op`, `__deleted`), `RegexRouter` bỏ prefix topic. **Outbox pattern** (tuần 9) dùng Debezium + `EventRouter` SMT.
- Debezium chạy **trên Kafka Connect** (`debezium/connect` image hoặc plugin vào cp-kafka-connect); MSK Connect hỗ trợ Debezium làm custom plugin (tuần 9).

---

## 📄 Nội dung (trích/tổng hợp từ tài liệu gốc)

### Overview

The Debezium PostgreSQL connector captures row-level changes in the schemas of a PostgreSQL database. The first time it connects to a PostgreSQL server or cluster, the connector takes a **consistent snapshot** of all schemas (tables) it is configured to capture. After that snapshot is complete, the connector continuously captures row-level changes that insert, update, and delete database content and that were committed to a PostgreSQL database. The connector generates data change event records and streams them to Kafka topics. For each table, the default behavior is that the connector streams all generated events to a separate Kafka topic for that table. Applications and services consume data change event records from that topic.

### How the connector works

PostgreSQL's **logical decoding** feature (introduced in version 9.4) extracts the changes committed to the transaction log (WAL) and processes them in a user-friendly manner with the help of an **output plug-in**. The output plug-in enables clients to consume the changes. Supported plug-ins:

- **`pgoutput`** — the standard logical decoding output plug-in in PostgreSQL 10+. It is maintained by the PostgreSQL community and requires no extra installation; it is the **default** (`plugin.name=pgoutput`) and works with publications.
- `decoderbufs` — Protobuf-based, maintained by the Debezium community (must be installed on the server).
- (`wal2json` — JSON-based, deprecated/removed in recent Debezium versions.)

The connector:

1. Connects to the database, creates (or reuses) a **replication slot** (`slot.name`, default `debezium`) and, for `pgoutput`, a **publication** (`publication.name`, default `dbz_publication`; `publication.autocreate.mode=all_tables|disabled|filtered`).
2. Performs the **snapshot** according to `snapshot.mode` — reads the current content of each captured table inside a repeatable-read transaction and emits one `op=r` ("read") event per row.
3. Starts **streaming** from the WAL position (LSN) recorded at the start of the snapshot; every committed change becomes a `c`/`u`/`d` event. The connector periodically records the LSN it has processed as its Connect **source offset** (`{"lsn": ..., "txId": ..., "ts_usec": ...}`), so after a restart it resumes from the last confirmed LSN — records are delivered **at least once**; duplicates are possible after an unclean restart.

Server prerequisites: `wal_level = logical` in `postgresql.conf` (restart required), `max_wal_senders` and `max_replication_slots` ≥ 1, a database user with `REPLICATION` and `LOGIN` privileges plus `SELECT` on the captured tables (or superuser in dev). The replication slot prevents the server from discarding WAL segments the connector has not yet consumed, so a connector that is stopped for a long time can cause **WAL disk growth**; monitor `pg_replication_slots` and drop unused slots.

### Topic names

By default, the PostgreSQL connector writes change events for all `INSERT`, `UPDATE`, and `DELETE` operations that occur in a table to a single Apache Kafka topic that is specific to that table. The connector uses the following convention to name change event topics:

```
<topic.prefix>.<schemaName>.<tableName>
```

For example, with `topic.prefix=pg1` and a table `public.customers`, events go to **`pg1.public.customers`**. The connector also writes schema-change events to a topic named `<topic.prefix>` (e.g. `pg1`) and, if a transaction metadata topic is enabled, `<topic.prefix>.transaction`. Use `RegexRouter` (`regex=pg1\.public\.(.*)`, `replacement=$1`) to strip the prefix if downstream expects plain table names.

### Change event structure

Every event has a **key** (a struct containing the table's primary key columns) and a **value** envelope:

```json
{
  "schema": { "...": "Kafka Connect schema describing the payload (omitted when schemas.enable=false)" },
  "payload": {
    "before": { "id": 1001, "first_name": "Sally", "email": "sally@acme.com" },
    "after":  { "id": 1001, "first_name": "Sally", "email": "sally@example.org" },
    "source": {
      "version": "3.x", "connector": "postgresql", "name": "pg1",
      "ts_ms": 1726400000000, "snapshot": "false", "db": "shop",
      "schema": "public", "table": "customers", "txId": 556, "lsn": 24023128, "xmin": null
    },
    "op": "u",
    "ts_ms": 1726400000123,
    "transaction": null
  }
}
```

| Field | Meaning |
|---|---|
| `before` | Row state **before** the change. `null` for `c` and `r`. For `u`/`d` it contains only the primary-key columns unless the table has `REPLICA IDENTITY FULL`. |
| `after` | Row state **after** the change. `null` for `d`. |
| `source` | Metadata: connector name (`topic.prefix`), database, schema, table, LSN, transaction ID, commit timestamp `ts_ms`, `snapshot` flag (`true`/`last`/`false`). |
| `op` | **`c`** = create (INSERT), **`u`** = update, **`d`** = delete, **`r`** = read (snapshot), **`t`** = truncate, **`m`** = logical decoding message. |
| `ts_ms` | Time at which the connector processed the event (compare with `source.ts_ms` to measure lag). |

**Delete events**: a `DELETE` produces a delete change event (`op=d`, `after=null`) and, by default, a second record with the same key and a **`null` value** — a **tombstone** — so that Kafka log compaction can remove all messages for that key (`tombstones.on.delete=true`). Sinks that cannot handle null values should drop tombstones (`Filter` + `RecordIsTombstone` predicate) or the property can be set to `false`.

**`REPLICA IDENTITY`**: PostgreSQL decides how much of the old row is written to the WAL per table: `DEFAULT` (primary key only), `NOTHING`, `INDEX <name>`, or **`FULL`** (`ALTER TABLE customers REPLICA IDENTITY FULL;`) which is required for a complete `before` image on updates/deletes, and for capturing changes to tables **without** a primary key.

### Key connector configuration

| Property | Default | Description |
|---|---|---|
| `connector.class` | — | `io.debezium.connector.postgresql.PostgresConnector` |
| `tasks.max` | `1` | The connector always uses a single task (one replication slot). |
| `database.hostname` / `database.port` / `database.user` / `database.password` / `database.dbname` | — / `5432` / — / — / — | Connection to the PostgreSQL server; the connector captures **one** database. |
| `topic.prefix` | — (required) | Logical name that provides a namespace for the server; used as the prefix of all topic names (formerly `database.server.name`). |
| `plugin.name` | `pgoutput` | Logical decoding plug-in: `pgoutput`, `decoderbufs`. |
| `slot.name` | `debezium` | Name of the PostgreSQL logical decoding slot; must be unique per connector. |
| `publication.name` | `dbz_publication` | Publication used with `pgoutput`. |
| `publication.autocreate.mode` | `all_tables` | `all_tables`, `disabled`, `filtered` (only tables in `table.include.list`). |
| `schema.include.list` / `schema.exclude.list` | — | Regex of schemas to capture / skip. |
| `table.include.list` / `table.exclude.list` | — | Regex of fully-qualified `schema.table` identifiers to capture, e.g. `public.customers,public.orders`. |
| `column.include.list` / `column.exclude.list` | — | Column filtering; `column.mask.hash.*`, `column.truncate.to.N.chars` for PII handling. |
| `snapshot.mode` | `initial` | `initial` (snapshot once, then stream), `initial_only`, `always`, `never` (stream only; deprecated → `no_data`), `no_data` (schema only), `when_needed`, `configuration_based`, `custom`. |
| `tombstones.on.delete` | `true` | Emit a tombstone after each delete event. |
| `decimal.handling.mode` | `precise` | `precise` (Connect `Decimal` / bytes), `double`, `string`. |
| `time.precision.mode` | `adaptive` | Temporal type mapping. |
| `heartbeat.interval.ms` | `0` | Emit heartbeat messages to `__debezium-heartbeat.<prefix>` so the LSN advances on idle databases (prevents WAL growth). |
| `key.converter` / `value.converter` | worker default | Typically `AvroConverter` + Schema Registry in production, or `JsonConverter` with `schemas.enable=false` for readability. |
| `transforms` | — | Common: `unwrap` = `io.debezium.transforms.ExtractNewRecordState` (`delete.handling.mode`, `add.fields=op,table`), `route` = `RegexRouter`. |

Example connector (JSON for `POST /connectors`):

```json
{
  "name": "pg-orders-cdc",
  "config": {
    "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
    "tasks.max": "1",
    "database.hostname": "postgres",
    "database.port": "5432",
    "database.user": "postgres",
    "database.password": "postgres",
    "database.dbname": "shop",
    "topic.prefix": "pg1",
    "plugin.name": "pgoutput",
    "slot.name": "dbz_shop",
    "publication.autocreate.mode": "filtered",
    "table.include.list": "public.customers",
    "snapshot.mode": "initial",
    "key.converter": "org.apache.kafka.connect.json.JsonConverter",
    "key.converter.schemas.enable": "false",
    "value.converter": "org.apache.kafka.connect.json.JsonConverter",
    "value.converter.schemas.enable": "false"
  }
}
```

### Limitations and operational notes

- The connector **supports running only one task**, so parallelism comes from running multiple connectors (one per database) rather than `tasks.max`.
- Hosted PostgreSQL offerings must allow logical replication (`rds.logical_replication=1` on Amazon RDS/Aurora; Heroku Postgres does not support the needed plug-ins).
- If the connector is stopped, the replication slot **retains WAL** — configure `heartbeat.interval.ms` and monitor `pg_replication_slots` / `pg_wal` size; drop the slot if the connector is decommissioned.
- Failover to a PostgreSQL replica loses the replication slot (slots are not replicated before PG 17 without extra setup) → a new snapshot may be required.
- Delivery is **at-least-once**; downstream consumers/sinks should be idempotent (upsert by primary key). Exactly-once source support (KIP-618) can be enabled at the Connect level for Debezium connectors that declare support.
- Debezium runs **inside Kafka Connect**: install the plug-in on `plugin.path` (or use the `debezium/connect` image, or `quay.io/debezium/connect`), then manage it through the Connect REST API like any other connector. `MirrorMaker 2` and `MSK Connect` use the same Connect framework.
