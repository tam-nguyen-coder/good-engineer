# ✅ Answers & Explanations — Week 3: Amazon DynamoDB Deep Dive

> Open only after you have attempted every question in [questions.md](questions.md).
> Back to [week plan](README.md) · [master plan](../../DVA-C02-STUDY-PLAN.md)

**Answer key:** 1-B · 2-C · 3-B · 4-B · 5-A · 6-C · 7-A · 8-D · 9-B · 10-C · 11-B · 12-A · 13-D · 14-A · 15-B · 16-A · 17-C · 18-D · 19-B · 20-B · 21-A · 22-BC · 23-AB · 24-AB · 25-AB · 26-AB · 27-AB · 28-AB

---

### Question 1 — Answer: **B**
- **Why correct:** The access pattern "all orders for **one** customer across **a date range**" needs a composite key: partition key = `CustomerId` (groups all of a customer's orders into one partition), sort key = `OrderDate` (enables a `Query` with a range condition on the sort key, returning already-sorted results).
- **Why the others are wrong:** A — partition key `OrderId` scatters each order separately; you can only fetch one order by id, and finding a customer's orders requires a `Scan`. C — keys reversed: partitioning by date jams all customers of the same day into one partition and cannot be queried cleanly per customer. D — concatenating `CustomerId#OrderId` fragments each customer, losing the ability to query a date range for one customer.
- 🧠 **Key point / trap:** "Query by one value + a range" ⇒ that value is the **partition key**, the range criterion is the **sort key**.
- 📎 Source: README §Data model; `resources/dynamodb-partition-key-design.md`.

### Question 2 — Answer: **C**
- **Why correct:** A DynamoDB item is at most **400 KB**; a 1–3 MB file exceeds the limit. The standard pattern: store the file in Amazon S3 and keep only a **pointer** (S3 key/URL) + metadata in the item.
- **Why the others are wrong:** A — base64 inflates the file and will certainly exceed 400 KB. B — self-splitting items and reassembling is an anti-pattern: complex and consumes more capacity. D — there is **no** way to raise the item size limit; 400 KB is a hard limit.
- 🧠 **Key point / trap:** Large BLOBs/images/PDFs ⇒ Amazon S3 + a pointer in DynamoDB, never stuffed into the item.
- 📎 Source: `resources/dynamodb-faqs.md` (max item size 400 KB, store pointer to S3).

### Question 3 — Answer: **B**
- **Why correct:** 1 RCU = 1 strongly consistent read for an item ≤ 4 KB. An 8 KB item ⇒ `ceil(8/4) = 2` RCUs/read. × 10 reads/s = **20 RCUs**.
- **Why the others are wrong:** A (10) is the result if you compute for eventual (halved) — but the question requires strong. C (40) doubles unnecessarily. D (5) uses the wrong formula.
- 🧠 **Key point / trap:** Reads round UP to multiples of **4 KB**; strong = full value (not halved).
- 📎 Source: README §Capacity (worked examples); `resources/dynamodb-partition-key-design.md`.

### Question 4 — Answer: **B**
- **Why correct:** A 12 KB item ⇒ `ceil(12/4) = 3` RCUs/read if strong. Eventually consistent ⇒ **halved**: `3 × 20 / 2 = 30 RCUs`.
- **Why the others are wrong:** A (60) is the **strong** figure (forgot to halve for eventual). C (15) halves twice. D (20) mistakenly uses an 8 KB size.
- 🧠 **Key point / trap:** When you see **eventually consistent** in an RCU calculation ⇒ remember to **halve** relative to strong.
- 📎 Source: README §Capacity + §Self-check gate question 2.

### Question 5 — Answer: **A**
- **Why correct:** 1 WCU = 1 write/s for an item ≤ 1 KB. A 3 KB item ⇒ `ceil(3/1) = 3` WCUs/write. × 6 = **18 WCUs**.
- **Why the others are wrong:** B (6) ignores size. C (12) uses the wrong multiple. D (24) over-multiplies.
- 🧠 **Key point / trap:** Writes round UP to multiples of **1 KB** (different from the 4 KB for reads).
- 📎 Source: README §Capacity + §Self-check gate question 6.

### Question 6 — Answer: **C**
- **Why correct:** A standard write of a 2 KB item = `ceil(2/1) = 2` WCUs. **A transactional write = 2× WCUs** ⇒ 4 WCUs/transaction. × 5 = **20 WCUs**.
- **Why the others are wrong:** A (10) forgets the ×2 for the transaction. B (40) over-multiplies (×4). D (5) uses the wrong formula.
- 🧠 **Key point / trap:** A transaction = **2× capacity** (prepare + commit); this applies to both reads (2× RCUs) and writes (2× WCUs). Capacity is still consumed **even if the transaction is cancelled**.
- 📎 Source: `resources/dynamodb-transactions.md` (2 underlying writes/item).

### Question 7 — Answer: **A**
- **Why correct:** Since the filter is on `UserId`, the partition key, using `Query` directly reads only the relevant partition → far faster and far fewer RCUs than a full-table `Scan`.
- **Why the others are wrong:** B — parallel scan is faster but still scans the whole table and still consumes RCUs. C — the filter runs after the read, so it does not reduce RCUs. D — increasing `Limit` only changes pagination; it still scans the whole table.
- 🧠 **Key point / trap:** Being able to query by the base key while using `Scan` is a sign of a design mistake — always prefer **Query**.
- 📎 Source: README §Query vs Scan.

### Question 8 — Answer: **D**
- **Why correct:** `FilterExpression` is applied **after** `Query`/`Scan` has read the data. RCUs are charged on **all data scanned/read**, not on the post-filter data; the filter only reduces the volume **returned to the client**.
- **Why the others are wrong:** A, B — the filter does not run "before the read" and does not save RCUs. C — the filter runs on the DynamoDB server side, not on the client.
- 🧠 **Key point / trap:** "Filter saves RCUs" is the classic trap → **FALSE**. To genuinely reduce RCUs, narrow with a key condition (Query), not a filter.
- 📎 Source: README §Query vs Scan (Filter expression), §Common exam traps.

### Question 9 — Answer: **B**
- **Why correct:** `Query`/`Scan` returns at most **1 MB per call**. When more data exists, the response contains a `LastEvaluatedKey`; pass it back into `ExclusiveStartKey` to get the next page; repeat until the response **no longer** contains a `LastEvaluatedKey`.
- **Why the others are wrong:** A — `ConsistentRead` only affects consistency, not the 1 MB limit. C — `Limit` cannot exceed 1 MB per call. D — `Scan` is also limited to 1 MB and must also paginate; switching to Scan is the wrong direction.
- 🧠 **Key point / trap:** "Results truncated / more data remaining" ⇒ paginate with `LastEvaluatedKey` → `ExclusiveStartKey`.
- 📎 Source: README §Query vs Scan (Pagination).

### Question 10 — Answer: **C**
- **Why correct:** Querying by `Email` (not the original partition key `UserId`) needs a partition key **different** from the base table ⇒ a **GSI** (partition key = `Email`) is required. A GSI can be added to a running table with no downtime.
- **Why the others are wrong:** A — an LSI **cannot** change the partition key (always = `UserId`), so it cannot help query by `Email`. B — `Scan` + filter is slow and RCU-costly, not a low-latency solution. D — creating a new table + migrating is far too expensive compared with adding a GSI.
- 🧠 **Key point / trap:** "Query by an attribute other than the base partition key" ⇒ **GSI** (not LSI).
- 📎 Source: `resources/dynamodb-secondary-indexes.md`; README §Exam traps.

### Question 11 — Answer: **B**
- **Why correct:** An LSI **must be created at table creation** and cannot be added/removed later. To add an index to an **existing table** with no downtime ⇒ only a **GSI** can do it (create/delete at any time via `update-table`).
- **Why the others are wrong:** A, C — you cannot create an LSI on a running table, so any "choose LSI" reasoning is moot here. D — no table re-creation is needed; a GSI can be added online.
- 🧠 **Key point / trap:** "Add an index after the table already exists" ⇒ **GSI**; the moment you see an LSI answer, eliminate it.
- 📎 Source: `resources/dynamodb-secondary-indexes.md` (Online Index Operations).

### Question 12 — Answer: **A**
- **Why correct:** You need to query within the **same partition key** (`AccountId`) by a different sort key (`Amount`) and be **strongly consistent** ⇒ an **LSI** (same partition key as the table, supports strong reads).
- **Why the others are wrong:** B — a GSI changes the partition key to `Amount` (wrong pattern) and is **eventual only**. C — a GSI is **eventually consistent only**, so it cannot meet the strong requirement. D — `Scan` + consistent read is slow and does not address sorting by `Amount`.
- 🧠 **Key point / trap:** "Strongly consistent reads on an index" ⇒ **LSI** (a GSI cannot do this).
- 📎 Source: `resources/dynamodb-secondary-indexes.md` (Read Consistency).

### Question 13 — Answer: **D**
- **Why correct:** You need **both before and after** the change to compute a diff ⇒ `NEW_AND_OLD_IMAGES` (records both the old image and the new image).
- **Why the others are wrong:** A `KEYS_ONLY` has keys only. B `NEW_IMAGE` has the after version only. C `OLD_IMAGE` has the before version only.
- 🧠 **Key point / trap:** 4 view types: `KEYS_ONLY` / `NEW_IMAGE` / `OLD_IMAGE` / `NEW_AND_OLD_IMAGES`. You **cannot change** the view type after enabling — you must disable and create a new stream.
- 📎 Source: `resources/dynamodb-streams.md` (StreamViewType).

### Question 14 — Answer: **A**
- **Why correct:** `DynamoDB Streams` retains records for **up to 24 hours**; older data is **trimmed automatically**. A consumer down for ~40 h ⇒ loses the records older than 24 h.
- **Why the others are wrong:** B — `Lambda` does not delete records on the stream. C — there is no "1 MB then overwrite" limit for the stream. D — TTL is a table feature, not the stream's record-retention mechanism.
- 🧠 **Key point / trap:** Streams = a **24 h** window. A consumer down longer than 24 h ⇒ data loss → alarm/monitor `IteratorAge`.
- 📎 Source: `resources/dynamodb-streams.md` (24-hour lifetime, trimming).

### Question 15 — Answer: **B**
- **Why correct:** `DAX` **only caches eventually consistent reads**. Strongly consistent reads are **passed through** directly to the table (not served from cache) ⇒ wallet-balance reads (strong) do not speed up. The catalog (eventual) is cached and accelerated.
- **Why the others are wrong:** A — DAX does not gate caching on a 4 KB threshold like that. C — enabling `ConsistentRead=true` is precisely what makes it **not** use the cache. D — DAX accelerates **reads**, not writes.
- 🧠 **Key point / trap:** "Needs strongly consistent reads" ⇒ **DAX does not help**. DAX is a read cache for **eventual** reads, in-VPC, microsecond, write-through; not suited to write-heavy workloads.
- 📎 Source: `resources/dynamodb-dax.md`.

### Question 16 — Answer: **A**
- **Why correct:** `PutItem` + `ConditionExpression="attribute_not_exists(UserId)"` writes only when the partition key does not yet exist → prevents overwriting an existing record, is **atomic server-side**, and needs no prior read. On violation → `ConditionalCheckFailedException`.
- **Why the others are wrong:** B — read-then-write has a race condition between the read and the write. C — `BatchWriteItem` does **not** check existence and is not all-or-nothing. D — strongly consistent reads cannot prevent overwrites.
- 🧠 **Key point / trap:** "Create new, do not overwrite an existing record" ⇒ **conditional write** `attribute_not_exists`.
- 📎 Source: README §Session B (conditional write); §Exam traps.

### Question 17 — Answer: **C**
- **Why correct:** Optimistic locking: `UpdateItem` sets the new value **and** `Version = :new`, with `ConditionExpression="Version = :current"`. Only the update matching the `Version` that was read wins; a later update finds `Version` already changed → `ConditionalCheckFailedException`, and the app retries.
- **Why the others are wrong:** A — an update with no condition overwrites (exactly the race condition). B — two `Put` operations on the same item in one transaction is a validation error (you cannot target the same item twice). D — `attribute_exists(Version)` does not compare the version value, so it cannot detect a concurrent change.
- 🧠 **Key point / trap:** Optimistic locking = **version number + condition on the version**, no real lock needed.
- 📎 Source: README §Session B (optimistic locking).

### Question 18 — Answer: **D**
- **Why correct:** **Atomic counter** — `UpdateItem` with `SET ViewCount = ViewCount + :inc` (or `ADD`). DynamoDB performs the increment right on the server, safe under many concurrent requests, with no prior read.
- **Why the others are wrong:** A — read-then-write has a race condition; two requests read the same value then overwrite → miscount. B — a periodic `Scan` is expensive and not real time. C — a transaction per view is overkill (2× WCUs, needlessly complex).
- 🧠 **Key point / trap:** "Safe increment/decrement" ⇒ **atomic counter** (`x = x + :n`). Note: an atomic counter is **not** idempotent if the request is resent.
- 📎 Source: README §Session B (atomic counters); §Quick reflexes.

### Question 19 — Answer: **B**
- **Why correct:** TTL is based on an **epoch (seconds)** attribute; expired items are deleted **within a few days** (not immediately) and consume **no WCUs**. If the app must guarantee it never reads an expired item, it must **filter with an expression** on query/scan.
- **Why the others are wrong:** A — it does not delete exactly at the timestamp and does **not** consume WCUs. C — TTL does not delete before expiration. D — TTL requires a **numeric epoch**, not an ISO-8601 string.
- 🧠 **Key point / trap:** TTL deletes "within a few days" (older docs/exams often say ~48 h) and consumes **no WCUs**. Need exactness ⇒ filter expression.
- 📎 Source: README §Session C (TTL); `resources/dynamodb-faqs.md` (TTL consumes no write throughput).

### Question 20 — Answer: **B**
- **Why correct:** **PartiQL** is a SQL-compatible language for DynamoDB (`SELECT/INSERT/UPDATE/DELETE`) — familiar to SQL folks, but it still operates on the underlying key mechanism (so you still need good key/index design to avoid full-table scans).
- **Why the others are wrong:** A — DynamoDB is not an RDBMS and has no SQL-engine JDBC. C — there is no "SQL mode" to enable on a table. D — Athena queries data on S3/federated sources, not the standard way to manipulate DynamoDB items.
- 🧠 **Key point / trap:** "SQL-like on DynamoDB" ⇒ **PartiQL** (careful: a careless `SELECT` can become a full-table scan).
- 📎 Source: README §Session C (PartiQL); §Quick reflexes.

### Question 21 — Answer: **A**
- **Why correct:** Spare total capacity yet still `ProvisionedThroughputExceededException` + traffic concentrated on one partition key ⇒ **hot partition** (each partition caps at ~1,000 write units/s, 3,000 read units/s). Immediate client-side: **SDK retry with exponential backoff (+ jitter)**; concurrently rework the key design / write sharding.
- **Why the others are wrong:** B — an LSI does not distribute writes by partition key. C — if items do not exceed 400 KB, this is not the cause. D — unrelated to consistency; "strong write" does not exist as a "fix" and does not solve a hot partition.
- 🧠 **Key point / trap:** Throttling despite spare capacity = **hot partition**. `ProvisionedThroughputExceededException` ⇒ **exponential backoff** + fix the key design.
- 📎 Source: `resources/dynamodb-partition-key-design.md`; README §Session C, §Quick reflexes.

### Question 22 — Answer: **B, C**
- **Why correct:** B — a GSI has its **own throughput** (its queries/scans consume the index's capacity); an LSI **shares** the base table's WCU/RCU. C — an LSI **supports strongly consistent reads**; queries on a GSI are **eventually consistent only**.
- **Why the others are wrong:** A — reversed: an **LSI** shares the base table's partition key, and a **GSI** is the one with a different partition key. D — reversed: an **LSI** must be created at table creation, a **GSI** can be added at any time. E — reversed: LSIs are capped at **5 per table**, GSIs default to **20 per table**.
- 🧠 **Key point / trap:** Memorize the comparison: GSI = different key + own throughput + eventual only + create anytime; LSI = same partition key + shared throughput + supports strong + create at table creation.
- 📎 Source: `resources/dynamodb-secondary-indexes.md` (comparison table).

### Question 23 — Answer: **A, B**
- **Why correct:** A — DAX is ideal for **read-heavy, repeated reads** (high hit rate) accepting eventual consistency, needing microsecond latency. B — DAX relieves read pressure on a **hot key** (for example, a sale product), saving RCUs.
- **Why the others are wrong:** C — DAX is **not** suited to write-intensive workloads (more writes → more replication, more risk). D — DAX does **not** cache strongly consistent reads. E — DAX does not perform complex aggregation/join at the cache layer.
- 🧠 **Key point / trap:** DAX = a read cache for **eventual** reads, great when the **cache hit rate > 90%** and there are **repeated reads / a hot key**; not for write-heavy or strong reads.
- 📎 Source: `resources/dynamodb-dax.md` (Use cases / NOT ideal).

### Question 24 — Answer: **A, B**
- **Why correct:** A — enable `DynamoDB Streams` (choose a `StreamViewType`). B — create an **event source mapping** so `Lambda` polls the stream, with an IAM role allowing `Lambda` to read the stream (`GetRecords`, `GetShardIterator`, `DescribeStream`, `ListStreams`).
- **Why the others are wrong:** C — the table does not call a webhook directly to `Lambda`; the mechanism is polling via an event source mapping. D — TTL only relates to deleting expired items, not to triggering on every change. E — a GSI does not emit change events to `Lambda`.
- 🧠 **Key point / trap:** "React when an item changes / trigger Lambda" ⇒ **Streams + event source mapping** (Lambda **polls**, the table does not push).
- 📎 Source: README §Session B Step 3; `resources/dynamodb-streams.md`.

### Question 25 — Answer: **A, B**
- **Why correct:** A — **optimistic locking** with a `Version` attribute + a condition on the version. B — **conditional write** checks the seat state (`SeatStatus = :available`) before updating; on violation → `ConditionalCheckFailedException`. Both ensure only one valid write wins.
- **Why the others are wrong:** C — on-demand is only a capacity mode and does **not** prevent race conditions. D — `BatchWriteItem` is **not** atomic and does not check conditions. E — DAX is a read cache, it does not serialize writes.
- 🧠 **Key point / trap:** A race condition on **a single item** ⇒ conditional write / optimistic locking, no transaction needed yet.
- 📎 Source: README §Session B (conditional write + optimistic locking); §Exam traps.

### Question 26 — Answer: **A, B**
- **Why correct:** A — `TransactWriteItems` is **all-or-nothing** (ACID), up to **100 actions / 100 items / 4 MB** per call. B — `BatchWriteItem` is **not** all-or-nothing; failed items are returned in **`UnprocessedItems`** to retry yourself (for bulk writes, not transactions).
- **Why the others are wrong:** C — a transaction consumes **2× WCUs** per item (prepare + commit), not 1×. D — `BatchWriteItem` does **not** guarantee ACID even within the same table. E — `TransactWriteItems` **does** have a 100-action / 4 MB limit.
- 🧠 **Key point / trap:** "Both succeed or both fail" ⇒ **`TransactWriteItems`** (100/4MB, 2× WCUs). Bulk writes with no atomicity needed ⇒ **`BatchWriteItem`** (remember `UnprocessedItems`). Batched reads with no atomicity ⇒ `BatchGetItem`.
- 📎 Source: `resources/dynamodb-transactions.md` (limits, BatchWriteItem vs Transact).

### Question 27 — Answer: **A, B**
- **Why correct:** A — choose a partition key with **high cardinality / good distribution** so traffic spreads evenly across all partitions. B — **write sharding**: add a random/calculated suffix to the partition key to split one hot key across many partitions.
- **Why the others are wrong:** C — increasing item size **consumes more** WCUs, making throttling worse. D — an LSI shares the table's partition key, so it does **not** distribute writes. E — `ConsistentRead` is a read option, unrelated to write throttling.
- 🧠 **Key point / trap:** A hot partition from low key cardinality (like `Status`) ⇒ **distribute the key + write sharding**. Adaptive capacity helps somewhat, but the root cause is key design.
- 📎 Source: `resources/dynamodb-partition-key-design.md` (uniform load, write sharding).

### Question 28 — Answer: **A, B**
- **Why correct:** A — **on-demand** is the **default & recommended** mode for most workloads: no capacity planning, auto-scales to millions of req/s, pay per request (great for new/spiky apps). B — a **stable, predictable** workload is usually cheaper with **provisioned + Auto Scaling**, which also keeps costs steady.
- **Why the others are wrong:** C — it is **on-demand** that scales to zero / pay-per-request; provisioned charges for the capacity provisioned regardless of usage. D — on-demand does **not** require declaring RCUs/WCUs in advance. E — you **can** switch between the two modes (with frequency constraints); it is not permanently fixed.
- 🧠 **Key point / trap:** New/spiky/unpredictable app ⇒ **on-demand** (the default). Steady/predictable traffic + cost optimization ⇒ **provisioned + Auto Scaling**.
- 📎 Source: `resources/dynamodb-capacity-mode.md`; README §Capacity.
