# ✅ Answers & Explanations — Week 5

> Open only after you have attempted every question in [questions.md](questions.md).
> Back to [week plan](README.md) · [master plan](../../CCDAK-STUDY-PLAN.md)

**Answer key:** 1-B · 2-C · 3-A · 4-AD · 5-C · 6-B · 7-D · 8-B · 9-AC · 10-C · 11-D · 12-AC · 13-ACE · 14-BD · 15-C · 16-A · 17-B · 18-BD · 19-C · 20-A · 21-D · 22-AC · 23-B · 24-C · 25-B · 26-BE · 27-A · 28-AD · 29-C · 30-B

---

### Question 1 — Answer: **B**

- **Why correct:** `KafkaAvroSerializer` writes the Confluent **wire format**: byte 0 is the magic byte `0x00`, bytes 1–4 are the **schema ID (int32, big-endian)**, and the rest is Avro binary. A plain console consumer prints those **5 bytes** as unreadable characters followed by binary data. Use `kafka-avro-console-consumer` (or `KafkaAvroDeserializer` with `schema.registry.url`) to decode.
- **Why the others are wrong:** A — compression is applied to the whole batch and is transparently decompressed by any consumer; it would not produce a fixed 5-byte prefix. C — the serializer is working (no producer errors); Java serialization is not involved. D — there is no message-format mismatch here; the consumer reads the bytes fine, it just does not interpret them.
- 🧠 **Key point / trap:** "garbage characters at the start of every record" → **wire format (magic byte + schema ID)**, not corruption.
- 📎 Source: `resources/schema-registry-wire-format-serdes.md` (Wire Format table).

### Question 2 — Answer: **C**

- **Why correct:** The default compatibility level is **`BACKWARD`**: a consumer with the new schema must be able to read old data. Old records have no `currency`, so the new field **must have a default** (`["null","string"]` with `"default": null`, or any default value). With a default, the registration succeeds as version 2.
- **Why the others are wrong:** A — a union `["string","null"]` **without** a `default` is still a required field for backward compatibility (and Avro requires the default to match the first union branch, so `null` must come first). B — a new subject avoids the check but breaks the `TopicNameStrategy` mapping to the topic and does not fix the incompatibility. D — `auto.register.schemas=true` still goes through the same compatibility check and gets the same 409.
- 🧠 **Key point / trap:** **409 on adding a field** → add a **default**. Do not reach for `NONE`.
- 📎 Source: `resources/schema-registry-compatibility.md` (Backward compatibility, Avro-specific rules).

### Question 3 — Answer: **A**

- **Why correct:** `FORWARD` means **data written with the new schema can be read by consumers on the old schema**. Adding a field is allowed; old consumers simply ignore it. Therefore **producers are upgraded first**, consumers later.
- **Why the others are wrong:** B — consumers-first is the rule for `BACKWARD` (the default). C — only `FULL` allows any order. D — simultaneous upgrades are what compatibility rules exist to avoid (that is the `NONE` situation).
- 🧠 **Key point / trap:** BACKWARD → **consumers** first; FORWARD → **producers** first; FULL → any order.
- 📎 Source: `resources/schema-registry-compatibility.md` (Order of upgrading clients).

### Question 4 — Answer: **A, D**

- **Why correct:** `FULL` = backward **and** forward compatible. The only changes that satisfy both directions are **adding an optional field (with default)** and **removing an optional field (with default)**.
- **Why the others are wrong:** B — adding a required field breaks backward compatibility (new reader cannot fill it from old data). C — type changes are incompatible under every level except `NONE`. E — removing a field without a default breaks forward compatibility (old reader expects it and has no default).
- 🧠 **Key point / trap:** `FULL` → **only fields with defaults**, both add and remove.
- 📎 Source: `resources/schema-registry-compatibility.md` (Summary of allowed changes table).

### Question 5 — Answer: **C**

- **Why correct:** `TopicRecordNameStrategy` derives the subject as `<topic>-<fully.qualified.RecordName>`, so several record types can share one topic **and** compatibility is checked **per topic**, letting `order-events` evolve `OrderCreated` independently from another topic that also uses `OrderCreated`.
- **Why the others are wrong:** A — a union schema under `TopicNameStrategy` works but couples all types into one subject and needs `use.latest.version=true`; it does not give per-type subjects. B — `RecordNameStrategy` subject is just the record name, so compatibility is checked **across all topics** using that record, which the team explicitly does not want. D — `NONE` disables checks entirely; it is a workaround, not a strategy.
- 🧠 **Key point / trap:** "multiple types in one topic" → `RecordNameStrategy` (shared across topics) vs `TopicRecordNameStrategy` (**per topic**).
- 📎 Source: `resources/schema-registry-wire-format-serdes.md` (Subject name strategy table).

### Question 6 — Answer: **B**

- **Why correct:** The schema **ID is global**: registering an identical schema string anywhere returns the same ID. The **version** is a counter **within a subject** (4 in one, 1 in the other). The wire format embeds only the **ID**, which is why the same bytes are decodable regardless of subject.
- **Why the others are wrong:** A — IDs are assigned per unique schema, not per subject. C — registering an existing schema in a new subject is allowed (it is version 1 there). D — versions are per subject, not global.
- 🧠 **Key point / trap:** same schema → **same ID, different version**. `GET /schemas/ids/<id>` resolves what is in the payload.
- 📎 Source: `resources/schema-registry-rest-api.md` (POST /subjects/{subject}/versions description) and `resources/schema-registry-wire-format-serdes.md` (Schema ID vs version).

### Question 7 — Answer: **D**

- **Why correct:** With `auto.register.schemas=false`, the serializer only **looks up** the schema; if it is not registered, serialization fails (`40403 Schema not found`). The governed fix is to **register the schema through the CI/CD pipeline or REST API** (`POST /subjects/<topic>-value/versions`) before deploying, keeping auto-registration off so an unexpected schema still fails fast.
- **Why the others are wrong:** A — defeats the policy and lets the producer silently create new versions. B — `use.latest.version=true` makes the serializer use the latest registered version; if the producer's object does not match it, `latest.compatibility.strict=true` fails anyway, and it does not register the missing schema. C — compatibility level has nothing to do with a missing schema.
- 🧠 **Key point / trap:** production = `auto.register.schemas=false` + **schemas registered by CI**; error `40403` means "register it first".
- 📎 Source: `resources/schema-registry-wire-format-serdes.md` (Core configuration properties).

### Question 8 — Answer: **B**

- **Why correct:** `POST /compatibility/subjects/<subject>/versions/latest` tests a candidate schema against the latest version using the subject's (or global) compatibility level and returns `{"is_compatible": true|false}` **without registering** anything (`?verbose=true` adds reasons).
- **Why the others are wrong:** A — only reads the current schema. C — **registers** the schema (and returns 409 if incompatible), which the pipeline must not do at this stage. D — changes the compatibility level, it does not test a schema.
- 🧠 **Key point / trap:** "check compatibility without registering" → **`/compatibility/subjects/.../versions/latest`**.
- 📎 Source: `resources/schema-registry-rest-api.md` (Compatibility section).

### Question 9 — Answer: **A, C**

- **Why correct:** Schema Registry persists everything in the Kafka topic **`_schemas`** (`kafkastore.topic`), which has **1 partition** so all writes are strictly ordered, and **`cleanup.policy=compact`** so any instance can rebuild its in-memory state by replaying it.
- **Why the others are wrong:** B — there is no embedded database; Kafka is the store. D — a single partition is required; multiple instances form a **leader/follower** cluster where only the leader writes. E — followers **forward** write requests to the leader.
- 🧠 **Key point / trap:** `_schemas` = **1 partition, compacted, leader writes only**.
- 📎 Source: `resources/schema-registry-rest-api.md` (Deployment notes (HA)).

### Question 10 — Answer: **C**

- **Why correct:** The team already maintains **`.proto`** definitions for gRPC across Java/Go/Python. `KafkaProtobufSerializer` reuses those definitions, gives strong typing and compact binary encoding, and Schema Registry supports Protobuf natively (wire format adds a message-index byte after the schema ID).
- **Why the others are wrong:** A — JSON Schema payloads are text and the largest of the three; readability was not the requirement. B — plain JSON has no schema governance and large payloads. D — Schema Registry supports **Avro, Protobuf and JSON Schema**; Avro would force the team to maintain a second schema language.
- 🧠 **Key point / trap:** "already gRPC / multi-language / strongly typed" → **Protobuf**; "Kafka ecosystem default, best evolution" → Avro; "human readable, existing JSON" → JSON Schema.
- 📎 Source: Week 5 `README.md` (Buổi A, mục 2 — Avro vs Protobuf vs JSON Schema) and `resources/schema-registry-wire-format-serdes.md`.

### Question 11 — Answer: **D**

- **Why correct:** Under `BACKWARD` the candidate is compared **only with the latest version** (version 2, which has no `sku`). Re-adding `sku` **without a default** is "add a required field" → **rejected (409)**. Even with a default the non-transitive check would pass, but a consumer on version 3 replaying version-1 data is only **guaranteed** readable if the subject uses **`BACKWARD_TRANSITIVE`** (checks against all versions). Compacted, replayed topics are the classic reason to choose a transitive level.
- **Why the others are wrong:** A — the field has no default, so it is rejected; and "restoring" compatibility with v1 is not what the non-transitive check evaluates. B — plain `BACKWARD` compares with the **latest** version only. C — a transitive level would make the check **stricter**, not accept the schema.
- 🧠 **Key point / trap:** non-transitive = **latest version only**; replay-from-beginning workloads → **`*_TRANSITIVE`**.
- 📎 Source: `resources/schema-registry-compatibility.md` (Transitive vs non-transitive).

### Question 12 — Answer: **A, C**

- **Why correct:** A consumer needs the Avro **deserializer** (`KafkaAvroDeserializer`) and the address of the registry (`schema.registry.url`) to resolve the schema ID found in bytes 1–4 of each record.
- **Why the others are wrong:** B — `auto.register.schemas` is a **serializer** (producer) setting. D — `value.converter` is a **Kafka Connect** property, not a consumer property. E — `use.latest.version` is a serializer option used with `auto.register.schemas=false`; the deserializer always uses the embedded ID. (`specific.avro.reader=true` is optional, only to get generated classes.)
- 🧠 **Key point / trap:** consumer = **deserializer + `schema.registry.url`**; do not mix in Connect (`converter`) or producer-only properties.
- 📎 Source: `resources/schema-registry-wire-format-serdes.md` (Serializer and Deserializer classes, example consumer configuration).

### Question 13 — Answer: **A, C, E**

- **Why correct:** `config.storage.topic` (`connect-configs`) must have **exactly 1 partition** to keep configuration updates totally ordered. All three internal topics must be **compacted** so the latest config/offset/status per key survives. Defaults when auto-created: `offset.storage.partitions=25`, `status.storage.partitions=5` (replication factor 3).
- **Why the others are wrong:** B — offsets must never expire; `delete` retention would lose positions → compaction is required. D — the status topic may have several partitions (default 5); only the **config** topic is restricted to 1.
- 🧠 **Key point / trap:** **1 / 25 / 5**, all **compacted**. Only `connect-configs` is single-partition.
- 📎 Source: `resources/connect-user-guide-configs-rest.md` (Distributed mode, worker configuration table).

### Question 14 — Answer: **B, D**

- **Why correct:** Distributed workers share a **`group.id`**, keep connector configs, offsets and statuses in **Kafka topics**, and receive connector definitions through the **REST API on 8083** (configs are **not** passed on the command line).
- **Why the others are wrong:** A — the offsets **file** belongs to **standalone** mode. C — Connect (like Kafka 4.x) does not use ZooKeeper; coordination uses Kafka's group protocol. E — it is the reverse: exactly-once source support exists **only in distributed** mode.
- 🧠 **Key point / trap:** standalone = 1 process + offsets file + CLI properties; distributed = `group.id` + REST + 3 topics + HA + EOS source.
- 📎 Source: `resources/connect-user-guide-configs-rest.md` (Running Kafka Connect) and `resources/kafka-connect-101-course.md` (Deployment models).

### Question 15 — Answer: **C**

- **Why correct:** The topic holds **Avro/Schema Registry** bytes (first byte `0x00`). `JsonConverter` tries to parse them as JSON and fails at byte 0. The converter must match the data on the topic: **`AvroConverter`** with `value.converter.schema.registry.url`.
- **Why the others are wrong:** A — `schemas.enable` only controls the JSON envelope; the bytes are not JSON at all. B — SMTs run **after** the converter on a sink; the failure happens before any SMT. D — `errors.tolerance=all` would skip **every** record, producing an empty sink, not a fix.
- 🧠 **Key point / trap:** converter mismatch: `JsonConverter` on Avro → parse error; `AvroConverter` on JSON → `Unknown magic byte!`.
- 📎 Source: `resources/kafka-connect-101-course.md` (Common converter errors table).

### Question 16 — Answer: **A**

- **Why correct:** `JsonConverter` has **`schemas.enable=true` by default** and expects every message to be `{"schema": {...}, "payload": {...}}`. Plain JSON from the Node.js app lacks that envelope → `DataException`. Fix: `value.converter.schemas.enable=false` for schemaless processing, or switch to Avro/Protobuf/JSON Schema if the JDBC sink needs a schema to create tables.
- **Why the others are wrong:** B — the bytes are valid JSON, not the wire format. C — `HoistField` wraps a primitive into a struct; the converter fails before transformations run. D — `tasks.max` never causes a conversion error.
- 🧠 **Key point / trap:** the exact string `requires "schema" and "payload" fields` → **`schemas.enable`**.
- 📎 Source: `resources/kafka-connect-101-course.md` (Converters / Common converter errors).

### Question 17 — Answer: **B**

- **Why correct:** On a **sink**, records have already been read from their Kafka topics. `RegexRouter` rewrites the record's **topic field**, which sink connectors use to derive the destination entity name (table, index, bucket prefix). The JDBC sink therefore writes to tables `orders` and `customers`.
- **Why the others are wrong:** A — the connector still subscribes to the original topics (`topics`/`topics.regex`); SMTs never change what is consumed. C — Kafka topics are never renamed by an SMT. D — `RegexRouter` works on both source (changes the destination Kafka topic) and sink (changes the logical destination name).
- 🧠 **Key point / trap:** `RegexRouter`/`TimestampRouter`: **source → Kafka topic name; sink → destination table/index name**.
- 📎 Source: `resources/connect-transforms-predicates.md` (Where SMTs sit in the pipeline).

### Question 18 — Answer: **B, D**

- **Why correct:** `InsertField$Value` with `timestamp.field=ingested_at` inserts the record timestamp as a new field. `MaskField$Value` with `fields=ssn` replaces the field with a type-appropriate null/empty value (or `replacement`). Both run on the source before the converter, so Kafka never sees the raw SSN.
- **Why the others are wrong:** A — `ReplaceField` renames or drops fields; it neither masks nor adds a timestamp. C — `ExtractField` replaces the whole value with the `ssn` field — the opposite of masking. E — `TimestampRouter` changes the **topic name**, not the record content.
- 🧠 **Key point / trap:** add metadata → **`InsertField`**; hide PII → **`MaskField`**; rename/drop → `ReplaceField`; route → `RegexRouter`/`TimestampRouter`.
- 📎 Source: `resources/connect-transforms-predicates.md` (Included transformations table).

### Question 19 — Answer: **C**

- **Why correct:** `Filter` drops records **only when combined with a predicate**. `RecordIsTombstone` is true for records with a `null` value, so `Filter` + `RecordIsTombstone` removes Debezium tombstones before `put()`.
- **Why the others are wrong:** A — `Filter` without a predicate drops **every** record. B — a null value is not an error; `errors.tolerance` applies to converter/SMT/put exceptions, and the crash inside the connector may not even be a `RetriableException`. D — `ByteArrayConverter` still passes a null value through.
- 🧠 **Key point / trap:** `Filter` **always** needs `predicate=`; built-in predicates: `TopicNameMatches`, `HasHeaderKey`, `RecordIsTombstone`.
- 📎 Source: `resources/connect-transforms-predicates.md` (Predicates).

### Question 20 — Answer: **A**

- **Why correct:** `errors.deadletterqueue.*` properties apply to **sink connectors only**. A failed source record has not been written to Kafka yet and has connector-specific `sourcePartition`/`sourceOffset` rather than a topic-partition-offset, so the framework can only **log and skip** it (`errors.tolerance=all`).
- **Why the others are wrong:** B — headers only add context; they do not enable the DLQ, and sources have no DLQ regardless. C — the worker's admin client auto-creates the DLQ topic for sinks. D — retry timeout controls retries, not DLQ routing.
- 🧠 **Key point / trap:** **DLQ = sink only.** Source connectors get retry + log + skip.
- 📎 Source: `resources/connect-error-handling-dlq-kip298.md` (Configuration table, "Why no DLQ for source connectors").

### Question 21 — Answer: **D**

- **Why correct:** A task failure is treated as exceptional: **it does not trigger a rebalance and the framework never restarts it automatically**. The operator must use the REST API — `POST /connectors/<name>/restart?includeTasks=true&onlyFailed=true` (or restart the single task) — after fixing the cause.
- **Why the others are wrong:** A — `scheduled.rebalance.max.delay.ms` (5 min) applies to **worker** departures, not task failures. B — changing `tasks.max` reconfigures the connector but does not clear the failed state and may not even create more tasks. C — worker restarts are unnecessary; restarting the worker also restarts every other connector's tasks.
- 🧠 **Key point / trap:** task `FAILED` → **manual REST restart**; worker down → automatic rebalance.
- 📎 Source: `resources/connect-user-guide-configs-rest.md` (REST API table, Task rebalancing).

### Question 22 — Answer: **A, C**

- **Why correct:** A DLQ only receives records when `errors.tolerance=all` (default `none` fails the task instead). The `__connect.errors.*` headers (`topic`, `partition`, `offset`, `connector.name`, `task.id`, `stage`, `exception.*`) are added only when `errors.deadletterqueue.context.headers.enable=true` (default `false`).
- **Why the others are wrong:** B — infinite retries delay processing; deserialization errors are not retriable and retries are not required for DLQ routing. D — `errors.log.include.messages` writes record contents to the **worker log**, not to the DLQ. E — the replication factor default is 3, which is fine on a 3-broker cluster; it is not required (only needed on a single-broker dev cluster).
- 🧠 **Key point / trap:** DLQ recipe (sink): `errors.tolerance=all` + `errors.deadletterqueue.topic.name` + `errors.deadletterqueue.context.headers.enable=true`.
- 📎 Source: `resources/connect-error-handling-dlq-kip298.md` (Dead letter queue behaviour, headers table).

### Question 23 — Answer: **B**

- **Why correct:** `tasks.max` is a **ceiling**. The connector's `taskConfigs()` decides the actual count. Log-based CDC connectors such as Debezium PostgreSQL read one replication slot and therefore always create **one task**; parallelism comes from running several connectors.
- **Why the others are wrong:** A — a single worker can run many tasks; worker count never limits task count to 1. C — a paused connector still shows its tasks (in `PAUSED` state). D — offset topic partitions are unrelated to task count.
- 🧠 **Key point / trap:** `tasks.max` = **upper bound**, default 1; FileStream and Debezium = 1 task; JDBC source ≈ number of tables; sink ≤ partitions.
- 📎 Source: `resources/debezium-postgres-cdc.md` (Key connector configuration, Limitations) and `resources/kafka-connect-101-course.md` (Workers, connectors and tasks).

### Question 24 — Answer: **C**

- **Why correct:** `PUT /connectors/<name>/config` is the **idempotent upsert**: it creates the connector if absent (201) or **updates the configuration** of a running connector (200). Connect reconfigures the connector in place; offsets are untouched because they are keyed by connector name.
- **Why the others are wrong:** A — delete + create works but is two calls, causes a rebalance, and is unnecessary. B — there is no `POST .../config`; `POST` is only for `/connectors` (create) and `/restart`. D — `PATCH /offsets` alters **offsets**, not configuration, and requires the connector to be stopped.
- 🧠 **Key point / trap:** update config → **`PUT /connectors/<n>/config`**; body is the bare config object (no `name` wrapper).
- 📎 Source: `resources/connect-user-guide-configs-rest.md` (REST API table).

### Question 25 — Answer: **B**

- **Why correct:** `DELETE /connectors/<name>` removes the configuration but **leaves the connector's offsets** in `connect-offsets` (keyed by connector name + source partition). Recreating with the same name resumes from that offset. Since Kafka 3.6, offsets can be reset via REST: `PUT .../stop` → `DELETE /connectors/<name>/offsets` → `PUT .../resume` (offset operations require `STOPPED` state).
- **Why the others are wrong:** A — the file is unchanged; the connector thinks it has already read it. C — `group.id` is a worker-level cluster identifier, not a connector setting. D — deleting a connector never deletes topics.
- 🧠 **Key point / trap:** delete ≠ reset. Reset offsets = **stop + `DELETE /offsets`** (or rename the connector).
- 📎 Source: `resources/connect-exactly-once-source-kip618.md` (Offsets in Connect — summary) and `resources/connect-user-guide-configs-rest.md` (REST API table).

### Question 26 — Answer: **B, E**

- **Why correct:** KIP-618 (Kafka 3.3+) delivers exactly-once for **source** connectors by writing records and source offsets in one transaction. It needs the worker cluster set to `exactly.once.source.support=enabled` (rolling upgrade through `preparing`) **and** the connector to request it; `exactly.once.support=required` adds a **preflight check** that fails connector creation if the worker or the connector class cannot guarantee EOS (`requested` is best-effort).
- **Why the others are wrong:** A — idempotence only prevents duplicates from producer retries within a session; it does not make record + offset writes atomic. C — `errors.tolerance` handles bad records, not delivery semantics. D — `processing.guarantee=exactly_once_v2` is a **Kafka Streams** property.
- 🧠 **Key point / trap:** EOS source = **worker `enabled` + connector `required`**; distributed mode only; sinks are **not** covered.
- 📎 Source: `resources/connect-exactly-once-source-kip618.md` (Worker-level and connector-level properties).

### Question 27 — Answer: **A**

- **Why correct:** Sink connectors consume through a consumer group named **`connect-<connector-name>`** (`connect-es-orders`), whose offsets live in `__consumer_offsets`. `kafka-consumer-groups.sh --describe --group connect-es-orders` shows `LOG-END-OFFSET − CURRENT-OFFSET` per partition. As learned in Week 4, `--reset-offsets` is only allowed when the group has **no active members**, so the connector must be stopped (or paused; `stop` is cleanest) first.
- **Why the others are wrong:** B — the group name carries the `connect-` prefix, and reset fails on an active group. C — `connect-offsets` stores **source** connector offsets, not sink offsets; `PATCH .../config` does not exist. D — the status endpoint shows state, not lag; `connect-status` is unrelated to positions.
- 🧠 **Key point / trap:** sink offsets = consumer group **`connect-<name>`**; source offsets = `connect-offsets`. Reset needs the group **inactive** (Week 4 rule).
- 📎 Source: `resources/connect-exactly-once-source-kip618.md` (Offsets in Connect — summary) and Week 4 `README.md` (offset reset rules).

### Question 28 — Answer: **A, D**

- **Why correct:** For a `DELETE`, Debezium emits a **delete event** with `op: "d"`, `before` holding the old row (primary key only unless `REPLICA IDENTITY FULL`) and `after: null`, followed by a **tombstone** (same key, `null` value) because `tombstones.on.delete=true` by default — this lets log compaction eventually remove the key.
- **Why the others are wrong:** B — `u` is an update; Debezium does not fake deletes as updates (the `__deleted` flag only appears if you use `ExtractNewRecordState` with rewrite mode). C — `r` is the snapshot read operation. E — log-based CDC is precisely what captures deletes; polling JDBC source does not.
- 🧠 **Key point / trap:** Debezium `op`: **c / u / d / r**; delete = `d` event **+ tombstone**; sinks that cannot handle null → `Filter` + `RecordIsTombstone` or `tombstones.on.delete=false`.
- 📎 Source: `resources/debezium-postgres-cdc.md` (Change event structure, Delete events).

### Question 29 — Answer: **C**

- **Why correct:** Per-connector client overrides (`consumer.override.*`, `producer.override.*`, `admin.override.*`, KIP-458) are governed by the worker's **`connector.client.config.override.policy`**: `All` (default since 3.0), `Principal` (security-related keys only), `None` (no overrides), and `Allowlist` (Kafka 4.2, explicit list). A disallowed override is rejected at **validation time**, exactly as described.
- **Why the others are wrong:** A — `consumer.override.` is the correct connector-level prefix; the bare `consumer.` prefix is the **worker**-level default. B — the whole point of overrides is to avoid worker-wide changes. D — sinks override the **consumer**, sources override the **producer**; both are supported.
- 🧠 **Key point / trap:** "override rejected" → check **`connector.client.config.override.policy`** (`None`/`Principal`/`Allowlist` vs `All`).
- 📎 Source: `resources/connect-user-guide-configs-rest.md` (Overriding producer/consumer settings per connector).

### Question 30 — Answer: **B**

- **Why correct:** With EOS source support, the worker writes records and offsets inside **Kafka transactions**. A consumer with the Java default `isolation.level=read_uncommitted` reads up to the high watermark and therefore sees records from transactions that are later **aborted** (which the connector then re-emits after recovery — hence apparent duplicates). `read_committed` reads only up to the **LSO** and filters aborted records, matching the connector's committed output exactly (Week 3).
- **Why the others are wrong:** A — auto-commit affects the consumer's own offsets, not visibility of aborted data. C — `auto.offset.reset` only matters when the group has no committed offset. D — the KIP-848 protocol changes rebalancing, not transaction visibility.
- 🧠 **Key point / trap:** anything transactional upstream (EOS producer, Streams EOS, EOS source connector) → consumer needs **`isolation.level=read_committed`**.
- 📎 Source: `resources/connect-exactly-once-source-kip618.md` (How a transaction wraps records and offsets) and Week 3 `README.md` (Transactions, `isolation.level`).
