# 📝 Practice Questions — Week 3: Amazon DynamoDB Deep Dive

> **28 questions** · real DVA-C02 exam style, difficulty ≥ real exam · covers the full Week 3 material.
> 🔒 **Answers & explanations are in a separate file:** [answers.md](answers.md). Attempt everything first.
> Tag: `[Domain.Task · Service · type]`. Multi = multiple-response (number to choose is stated).
> Back to [week plan](README.md) · [master plan](../../DVA-C02-STUDY-PLAN.md)

---

### Question 1 — `[D1.3 · DynamoDB · Single]`
An ecommerce company stores orders in Amazon DynamoDB. The primary access pattern is: "retrieve all orders for **one** customer within **a date range**, sorted by time." A developer must choose a primary key schema that supports the most efficient `Query` without resorting to a `Scan`.

- A. Partition key = `OrderId` (no sort key).
- B. Partition key = `CustomerId`, sort key = `OrderDate`.
- C. Partition key = `OrderDate`, sort key = `CustomerId`.
- D. Partition key = a concatenated string `CustomerId#OrderId`, no sort key.

### Question 2 — `[D1.3 · DynamoDB · Single]`
An application must store, for each product, a **1–3 MB** PDF description together with metadata (name, price, stock). A developer wants to use Amazon DynamoDB as the metadata store at the lowest cost while avoiding errors. Which design is correct?

- A. Store the entire PDF as base64 in a `Binary` attribute of the item.
- B. Split the PDF into multiple items of ≤ 400 KB each and reassemble them on read.
- C. Store the PDF in Amazon S3, and keep only a **pointer** (S3 key/URL) plus the metadata in the DynamoDB item.
- D. Raise the table's item size limit to 5 MB with `update-table`.

### Question 3 — `[D1.3 · DynamoDB · Single]`
A table uses **provisioned** capacity mode. An application reads a single **8 KB** item using **strongly consistent** reads, **10 times per second**. How many **RCUs** must be provisioned?

- A. 10 RCUs
- B. 20 RCUs
- C. 40 RCUs
- D. 5 RCUs

### Question 4 — `[D1.3 · DynamoDB · Single]`
On the same provisioned table, an application reads a single **12 KB** item but accepts **eventually consistent** reads, **20 times per second**. How many **RCUs** are required?

- A. 60 RCUs
- B. 30 RCUs
- C. 15 RCUs
- D. 20 RCUs

### Question 5 — `[D1.3 · DynamoDB · Single]`
An application writes a single **3 KB** item to a provisioned table, **6 times per second** (standard writes, not transactional). How many **WCUs** are required?

- A. 18 WCUs
- B. 6 WCUs
- C. 12 WCUs
- D. 24 WCUs

### Question 6 — `[D1.3 · DynamoDB · Single]`
A financial service uses `TransactWriteItems` to write a single **2 KB** item, running **5 transactions per second**. How many **WCUs** must be provisioned for this write workload?

- A. 10 WCUs
- B. 40 WCUs
- C. 20 WCUs
- D. 5 WCUs

### Question 7 — `[D1.3 · DynamoDB · Single]`
An API is slow and consumes a lot of capacity. It retrieves user profiles by running a full-table `Scan` with a `FilterExpression` on `UserId` (the partition key). A developer wants to reduce latency and consumed RCUs with minimal code changes. What should the developer do?

- A. Replace the `Scan` with a `Query` using a condition on the `UserId` partition key.
- B. Enable **parallel scan** to split the table into multiple segments.
- C. Add a more restrictive `FilterExpression` so that less data is read.
- D. Increase the `Scan` `Limit` to retrieve everything in a single call.

### Question 8 — `[D4.3 · DynamoDB · Single]`
During a review, a developer claims: "adding a `FilterExpression` to a `Scan` will **reduce consumed RCUs** because fewer items are returned." Which statement is **correct** about how `FilterExpression` affects capacity?

- A. Correct — `FilterExpression` is applied before the read, so RCUs are only charged for items matching the filter.
- B. Correct, but only when the same GSI is used.
- C. `FilterExpression` moves filtering to the client side, so it consumes no RCUs at all.
- D. Incorrect — `FilterExpression` is applied **after** the read; RCUs are still charged on **all data scanned**, and the filter only reduces the data returned.

### Question 9 — `[D1.3 · DynamoDB · Single]`
A `Query` returns about 1 MB of results and then stops, but the developer knows more matching data exists. The response contains a `LastEvaluatedKey` field. What is the correct way to retrieve the following pages?

- A. Re-run the `Query` with `ConsistentRead=true` to get everything in a single call.
- B. Pass the `LastEvaluatedKey` value into the `ExclusiveStartKey` parameter of the next call, repeating until no `LastEvaluatedKey` is returned.
- C. Increase `Limit` above 1 MB to bypass pagination.
- D. Switch to `Scan` because `Query` does not support pagination.

### Question 10 — `[D1.3 · DynamoDB · Single]`
A `Users` table has partition key = `UserId`. A new requirement arrives: query users by `Email` (not the original key), with low latency, and the table is already in production with millions of items. Which solution is most appropriate?

- A. Create an LSI on `Email`.
- B. Run a `Scan` with a `FilterExpression` on `Email`.
- C. Create a GSI with partition key = `Email`.
- D. Create a new table with partition key = `Email` and migrate all data.

### Question 11 — `[D1.3 · DynamoDB · Single]`
An `Orders` table (partition key = `CustomerId`, sort key = `OrderDate`) has been running for 6 months. The team needs to add the ability to query by `Status`. They want **no table re-creation and no downtime**. Which index type, and why?

- A. LSI on `Status` — because an LSI shares throughput, saving cost.
- B. GSI on `Status` — because a GSI can be **added to an existing table** at any time, whereas an LSI can only be created at table creation.
- C. LSI on `Status` — because an LSI supports strongly consistent reads.
- D. Not possible — adding an index requires re-creating the table.

### Question 12 — `[D1.3 · DynamoDB · Single]`
A table uses partition key = `AccountId`, sort key = `TxnTime`. Requirement: query transactions for the same `AccountId` sorted by `Amount`, and reads **must be strongly consistent** (real-time balance). Which index type meets this?

- A. LSI with partition key = `AccountId`, sort key = `Amount`.
- B. GSI with partition key = `Amount`.
- C. GSI with partition key = `AccountId`, sort key = `Amount`.
- D. No index needed; set `ConsistentRead=true` on a `Scan`.

### Question 13 — `[D1.3 · DynamoDB · Single]`
A team enables `DynamoDB Streams` to sync changes to a search index; each record must contain **both the before and after values** of the change to compute a diff. Which `StreamViewType` should they choose?

- A. `KEYS_ONLY`
- B. `NEW_IMAGE`
- C. `OLD_IMAGE`
- D. `NEW_AND_OLD_IMAGES`

### Question 14 — `[D1.3 · DynamoDB · Single]`
A `Lambda` consumer reading a `DynamoDB Streams` fails and stops running over a weekend (about 40 hours). When it recovers, some older change records have **disappeared** from the stream. What is the correct cause?

- A. The stream only retains records for **24 hours**; older data is trimmed automatically.
- B. `Lambda` deleted the records after the failed reads.
- C. The stream only retains **1 MB** of data and then overwrites it.
- D. TTL must be enabled on the stream, otherwise records are deleted immediately.

### Question 15 — `[D1.3 · DynamoDB · Single]`
A read-heavy application needs **strongly consistent reads** for wallet balances, along with many repeated **eventually consistent reads** on a product catalog. The team puts `DAX` in front of the table and is surprised that wallet-balance reads **do not get faster**. What is the correct explanation?

- A. `DAX` only caches items smaller than 4 KB, and the wallet balance is larger.
- B. `DAX` **only caches eventually consistent reads**; strongly consistent reads are **passed through** directly to the table (not cached).
- C. `DAX` requires `ConsistentRead=true` to be enabled before it can cache.
- D. `DAX` only accelerates writes, not reads.

### Question 16 — `[D1.3 · DynamoDB · Single]`
Multiple processes can concurrently create a profile for the same `UserId`. A developer wants `PutItem` to **succeed only when the item does not yet exist**, avoiding overwriting an existing record, without reading first. What is the correct approach?

- A. `PutItem` with `ConditionExpression="attribute_not_exists(UserId)"`.
- B. `GetItem` first, and if absent then `PutItem` (read-then-write).
- C. Use `BatchWriteItem` so DynamoDB prevents duplicates automatically.
- D. Enable strongly consistent reads on the table to prevent overwrites.

### Question 17 — `[D1.3 · DynamoDB · Single]`
Two clients read the same item with attribute `Version = 3`, then both attempt to update it. Only **one** update should be allowed to win (optimistic locking). Which update expression implements this correctly?

- A. `UpdateItem` without any condition, relying on strongly consistent reads.
- B. `TransactWriteItems` with two `Put` operations on the same item.
- C. `UpdateItem` with `SET ... Version = :new` and `ConditionExpression="Version = :current"` (`:current = 3`); if the condition fails → `ConditionalCheckFailedException`.
- D. `PutItem` with `attribute_exists(Version)`.

### Question 18 — `[D1.3 · DynamoDB · Single]`
A page wants to increment a `ViewCount` counter **safely under many concurrent requests**, without race conditions and without reading first and then writing back. Which approach is most appropriate?

- A. `GetItem` to read `ViewCount`, add 1 in the application, then `PutItem` it back.
- B. Run a periodic `Scan` to recount.
- C. Use `TransactWriteItems` for each view.
- D. `UpdateItem` with an **atomic counter**: `SET ViewCount = ViewCount + :inc` (or `ADD ViewCount :inc`).

### Question 19 — `[D1.3 · DynamoDB · Single]`
A table stores sessions; each item has an `ExpiresAt` attribute in **epoch (seconds)**. The team enables **TTL** on `ExpiresAt`. Which statement is **correct** about the deletion behavior?

- A. The item is deleted **exactly** at the `ExpiresAt` time and consumes WCUs for each deletion.
- B. Expired items are deleted **within a few days** after expiration (not immediately) and consume **no WCUs**; if exact behavior is needed, filter with an expression on read.
- C. TTL deletes immediately and emits a `REMOVE` record to the stream even before expiration.
- D. TTL requires an ISO-8601 string attribute, not epoch.

### Question 20 — `[D1.3 · DynamoDB · Single]`
A developer familiar with SQL wants to run `SELECT/INSERT/UPDATE/DELETE` on Amazon DynamoDB using SQL-like syntax to reduce the team's learning curve. What does AWS provide for this?

- A. Connect to DynamoDB over JDBC as if it were an RDBMS.
- B. Use **PartiQL** — a SQL-compatible language for DynamoDB (still operating on the underlying key mechanism).
- C. Enable "SQL mode" in the table configuration.
- D. Run Athena queries directly against the DynamoDB table.

### Question 21 — `[D4.1 · DynamoDB · Single]`
A provisioned table has spare total capacity, yet the application continually receives `ProvisionedThroughputExceededException` on writes. Investigation shows most writes concentrate on a single `PartitionKey` (a flash-sale product). What is the root cause and the immediate client-side mitigation?

- A. **Hot partition**: traffic concentrates on one partition key → the SDK should **retry with exponential backoff (+ jitter)** while the key design / write sharding is reworked.
- B. The table is missing an LSI; add an LSI to distribute the write load.
- C. Items exceed 400 KB; reduce the item size.
- D. It is due to eventual consistency; enable strongly consistent writes to stop the errors.

### Question 22 — `[D1.3 · DynamoDB · Multi — Choose 2]`
An architecture team is comparing **GSI** and **LSI**. Choose **2** statements that are **CORRECT**.

- A. An LSI has a **different** partition key from the base table, while a GSI must share the base table's partition key.
- B. A GSI has its **own throughput (WCU/RCU)**, separate from the base table; an LSI **shares** throughput with the base table.
- C. An LSI **supports strongly consistent reads**, while queries on a GSI are **eventually consistent only**.
- D. A GSI **must** be created at table creation; an LSI can be added at any time.
- E. LSIs are unlimited in number, while GSIs are capped at 5 per table.

### Question 23 — `[D4.3 · DynamoDB · Multi — Choose 2]`
A team is evaluating `DAX` for a DynamoDB table. Choose **2** scenarios where `DAX` is **appropriate / delivers a clear benefit**.

- A. A read-heavy workload that **reads the same set of items repeatedly** and accepts eventual consistency — requiring **microsecond** latency.
- B. Relieving read pressure on a **hot key** (for example, a product read very heavily during a sale) to save RCUs.
- C. A **write-intensive** workload that needs faster writes.
- D. An application that requires **strongly consistent reads** for every query.
- E. Performing complex aggregation/join at the cache layer.

### Question 24 — `[D1.3 · DynamoDB · Multi — Choose 2]`
A developer wants a `Lambda` function to be triggered **whenever an item in the `Orders` table changes** so it can process the change. Choose **2** steps required to set this up.

- A. Enable `DynamoDB Streams` on the table (choosing a `StreamViewType`, for example `NEW_AND_OLD_IMAGES`).
- B. Create an **event source mapping** so `Lambda` polls the stream (with an IAM role granting `Lambda` permission to read the stream).
- C. Configure the table to call an HTTP webhook directly to a `Lambda` URL on every write.
- D. Enable TTL so that `Lambda` is invoked when an item expires.
- E. Create a GSI so that `Lambda` reads the changes from the index.

### Question 25 — `[D1.3 · DynamoDB · Multi — Choose 2]`
A ticket-booking application has a **race condition**: two concurrent requests update the same seat and both overwrite each other. The team does not want to use a transaction for a single simple item. Choose **2** DynamoDB techniques appropriate for preventing overwrites / ensuring consistency on update.

- A. **Optimistic locking** with a `Version` attribute + `ConditionExpression="Version = :current"`.
- B. **Conditional write** with a state condition (for example `ConditionExpression="SeatStatus = :available"`).
- C. Switch the table to **on-demand** to automatically prevent race conditions.
- D. Use `BatchWriteItem` to group writes into a single atomic unit.
- E. Enable `DAX` to serialize writes through the cache.

### Question 26 — `[D1.3 · DynamoDB · Multi — Choose 2]`
A team needs to decrement inventory and create an order such that **either both succeed, or neither does**. They are weighing `TransactWriteItems` against `BatchWriteItem`. Choose **2** statements that are **CORRECT**.

- A. `TransactWriteItems` is **all-or-nothing** (ACID); it groups up to **100 actions** across up to 100 items, with a total size ≤ **4 MB**.
- B. `BatchWriteItem` is **not** all-or-nothing — some operations may succeed, and the failed ones are returned in **`UnprocessedItems`** to retry.
- C. `TransactWriteItems` consumes **1× WCU** per item (the same as a standard write).
- D. `BatchWriteItem` guarantees ACID if all items are in the same table.
- E. `TransactWriteItems` has no limit on the number of actions per call.

### Question 27 — `[D4.3 · DynamoDB · Multi — Choose 2]`
A table is being **throttled** because write traffic concentrates on a few partition key values (for example, partition key = `Status` with only `active`/`inactive`), even though total capacity is spare. Choose **2** root-cause fixes to distribute the load more evenly.

- A. Choose a partition key with **higher cardinality / better distribution** (many distinct values).
- B. Apply **write sharding**: add a random/calculated suffix to the partition key to spread writes across many partitions.
- C. Increase the item size so each write uses more WCUs.
- D. Add more LSIs to spread writes across other partitions.
- E. Set `ConsistentRead=true` on all reads to reduce write throttling.

### Question 28 — `[D1.3 · DynamoDB · Multi — Choose 2]`
A team is designing a new table for a just-launched app with **spiky, unpredictable** traffic. Choose **2** statements that are **CORRECT** about choosing a capacity mode.

- A. **On-demand** is the **default and AWS-recommended** mode for most workloads — no capacity planning, automatic scaling, pay per request.
- B. For a **stable, predictable** workload, **provisioned + Auto Scaling** is usually cheaper and keeps costs steady.
- C. Provisioned mode automatically scales to zero and only charges when there are requests.
- D. On-demand requires declaring peak RCUs/WCUs in advance to avoid throttling.
- E. You cannot switch between on-demand and provisioned after a table is created.
