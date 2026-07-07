# DynamoDB Transactions — ACID / TransactWriteItems / TransactGetItems

> **Nguồn (AWS official):**
> - Tổng quan: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/transactions.html
> - How it works (chi tiết giới hạn & isolation): https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/transaction-apis.html
> **Tuần:** 3 — DynamoDB · **Loại:** AWS Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)
- Transactions cho **ACID**, all-or-nothing, trong và ngang qua nhiều table (cùng account, cùng Region).
- **`TransactWriteItems`**: gom tối đa **100 action** (`Put`, `Update`, `Delete`, `ConditionCheck`) trên tối đa **100 item riêng biệt**; tổng size ≤ **4 MB**.
- **`TransactGetItems`**: gom tối đa **100 `Get` action** trên tối đa **100 item**; tổng size ≤ **4 MB**.
- **Chi phí = 2× capacity/item:** DynamoDB thực hiện 2 lần đọc/ghi ngầm cho MỖI item (prepare + commit). VD ghi transaction 1 item cần **2 WCU**. Capacity vẫn bị tiêu thụ **kể cả khi transaction bị hủy/thất bại**.
- **Không có chi phí phụ** để bật transactions — chỉ trả cho read/write thuộc transaction.
- Không được nhắm cùng 1 item bằng nhiều action trong cùng transaction; **transactions không dùng được trên index**.
- **Idempotency:** dùng `ClientRequestToken` (client token) → token hợp lệ trong **10 phút**; đổi tham số mà reuse token → `IdempotentParameterMismatch`.
- **Isolation:** `TransactWriteItems`/`TransactGetItems` là **SERIALIZABLE** với `GetItem`, `PutItem`, `UpdateItem`, `DeleteItem`, và transaction khác; nhưng chỉ **READ-COMMITTED** với `Query`, `Scan`, `BatchGetItem` (xét theo đơn vị); `BatchWriteItem` (xét theo đơn vị) là **NOT serializable**.
- **Lỗi:** conflict item-level → `TransactionConflictException`; nếu bất kỳ action trong transaction bị từ chối → `TransactionCanceledException` (SDK **không** retry). Item > **400 KB** → validation error.
- **Global Tables:** ACID chỉ đảm bảo **trong Region** nơi gọi API; **không** hỗ trợ transaction xuyên Region — Region khác có thể thấy transaction hoàn thành **một phần** trong lúc replicate.
- So sánh: `TransactWriteItems` = tất cả thành công hoặc không gì cả; `BatchWriteItem` = có thể một phần thành công, một phần không (không phải transaction).

---

## 📄 Nội dung (trích từ tài liệu gốc)

# Managing complex workflows with DynamoDB transactions

Amazon DynamoDB transactions simplify the developer experience of making coordinated, all-or-nothing changes to multiple items both within and across tables. Transactions provide **atomicity, consistency, isolation, and durability (ACID)** in DynamoDB.

With the transaction write API, you can group multiple `Put`, `Update`, `Delete`, and `ConditionCheck` actions, then submit them as a single `TransactWriteItems` operation that either succeeds or fails as a unit. The same is true for multiple `Get` actions, grouped and submitted as a single `TransactGetItems` operation.

There is **no additional cost** to enable transactions. You pay only for the reads or writes that are part of your transaction. DynamoDB performs **two underlying reads or writes of every item** in the transaction: one to prepare the transaction and one to commit it. These two underlying operations are visible in your Amazon CloudWatch metrics.

## TransactWriteItems API

`TransactWriteItems` is a **synchronous and idempotent** write operation that groups **up to 100 write actions** in a single all-or-nothing operation. These actions can target **up to 100 distinct items** in one or more DynamoDB tables within the **same AWS account and in the same Region**. The aggregate size of the items in the transaction **cannot exceed 4 MB**.

**Note:** A `TransactWriteItems` operation differs from a `BatchWriteItem` operation in that **all** the actions must complete successfully, or **no** changes are made at all. With `BatchWriteItem`, it is possible that only some of the actions succeed while others do not. **Transactions cannot be performed using indexes.**

You **can't target the same item** with multiple operations within the same transaction (e.g., you can't do a `ConditionCheck` and an `Update` on the same item in the same transaction).

Action types you can add:
- `Put` — Create a new item or replace an old item, conditionally or without condition.
- `Update` — Edit an existing item's attributes or add a new item if it doesn't exist.
- `Delete` — Delete a single item identified by its primary key.
- `ConditionCheck` — Check that an item exists or check the condition of specific attributes.

When a transaction completes, its changes start propagating to GSIs, streams, and backups **gradually** — stream records from the same transaction might appear at different times and be interleaved with records from other transactions. Stream consumers **shouldn't assume transaction atomicity or ordering**. To get an atomic snapshot, use `TransactGetItems`.

### Idempotency
You can optionally include a **client token** when you make a `TransactWriteItems` call to ensure the request is idempotent. If the original call was successful, subsequent calls with the same client token return successfully without making changes.
- A client token is valid for **10 minutes** after the request that uses it finishes. After 10 minutes, a request with the same token is treated as new.
- If you repeat a request with the same client token within the 10-minute window but **change some other parameter**, DynamoDB returns an `IdempotentParameterMismatch` exception.

### Error handling for writing
Write transactions don't succeed when:
- A condition in one of the condition expressions is not met.
- More than one action in the same operation targets the same item (validation error).
- A `TransactWriteItems` request conflicts with an ongoing `TransactWriteItems` on one or more items → fails with `TransactionCanceledException`.
- There is insufficient provisioned capacity.
- An item size becomes too large (**larger than 400 KB**), an LSI becomes too large, or a similar validation error occurs.
- There is a user error (e.g., invalid data format).

## TransactGetItems API

`TransactGetItems` is a **synchronous read operation** that groups **up to 100 `Get` actions**. These can target **up to 100 distinct items** in one or more tables within the same account and Region. Aggregate size **can't exceed 4 MB**. Get actions are performed atomically — either all succeed or all fail.

Read transactions don't succeed when:
- A `TransactGetItems` request conflicts with an ongoing `TransactWriteItems` on one or more items → `TransactionCanceledException`.
- There is insufficient provisioned capacity.
- There is a user error (invalid data format).

## Isolation levels for DynamoDB transactions

### SERIALIZABLE
Serializable isolation ensures the results of multiple concurrent operations are the same as if no operation begins until the previous one finished. There is serializable isolation between:
- Any transactional operation and any standard write (`PutItem`, `UpdateItem`, `DeleteItem`).
- Any transactional operation and any standard read (`GetItem`).
- A `TransactWriteItems` operation and a `TransactGetItems` operation.

There is **no** serializable isolation between the transaction and the `BatchWriteItem` operation **as a unit**, nor between the transaction and the `BatchGetItem` operation **as a unit** (that is read-committed). Individual writes/reads within those batch operations are serializable.

### READ-COMMITTED
Read-committed isolation ensures read operations always return committed values — the read never presents a state from a transactional write that did not ultimately succeed. It does **not** prevent modifications immediately after the read. The isolation level is read-committed between any transactional operation and any read that involves multiple standard reads (`BatchGetItem`, `Query`, or `Scan`).

### Operation summary

| Operation | Isolation Level |
| --- | --- |
| `DeleteItem` | *Serializable* |
| `PutItem` | *Serializable* |
| `UpdateItem` | *Serializable* |
| `GetItem` | *Serializable* |
| `BatchGetItem` | *Read-committed* \* |
| `BatchWriteItem` | *NOT Serializable* \* |
| `Query` | *Read-committed* |
| `Scan` | *Read-committed* |
| Other transactional operation | *Serializable* |

\* Applies to the operation **as a unit**. Individual actions within those operations have a *serializable* isolation level.

## Transaction conflict handling in DynamoDB
A transactional conflict can occur during concurrent item-level requests on an item within a transaction:
- A `PutItem`/`UpdateItem`/`DeleteItem` conflicts with an ongoing `TransactWriteItems` including the same item.
- An item within a `TransactWriteItems` is part of another ongoing `TransactWriteItems`.
- An item within a `TransactGetItems` is part of an ongoing `TransactWriteItems`, `BatchWriteItem`, `PutItem`, `UpdateItem`, or `DeleteItem`.

**Note:** When a `PutItem`/`UpdateItem`/`DeleteItem` is rejected → `TransactionConflictException`. If any item-level request within `TransactWriteItems`/`TransactGetItems` is rejected → `TransactionCanceledException`, and **AWS SDKs do not retry** the request. The `TransactionConflict` CloudWatch metric is incremented for each failed item-level request.

## Using transactional APIs in DAX
`TransactWriteItems` and `TransactGetItems` are both supported in DAX with the **same isolation levels** as in DynamoDB. `TransactWriteItems` writes through DAX (DAX passes the call to DynamoDB, then calls `TransactGetItems` in the background to populate the cache — consuming additional RCU). `TransactGetItems` calls are passed through without local caching (same as strongly consistent reads in DAX).

## Capacity management for transactions
DynamoDB performs **two underlying reads or writes of every item** (prepare + commit). This capacity **is consumed even when a transaction does not succeed** (e.g., a `ConditionalCheckFailed` cancellation still consumes the underlying capacity).

Example: 1 transaction/second, each writing three 500-byte items → each item requires **2 WCUs** (prepare + commit) → provision **6 WCUs**. With DAX, add 2 RCUs per item → **6 additional RCUs**. Default SDK behavior retries transactions on `TransactionInProgressException`; plan for the additional RCUs those retries consume.

## Best practices for transactions
- Enable auto scaling, or ensure enough provisioned throughput for the two read/write operations per item.
- If not using an AWS-provided SDK, include a `ClientRequestToken` to ensure idempotency.
- Don't group operations in a transaction unnecessarily — simpler transactions improve throughput and are more likely to succeed.
- Multiple transactions updating the same items simultaneously can cause conflicts that cancel the transactions — follow data-modeling best practices to minimize conflicts.
- If a set of attributes is often updated across items in one transaction, consider grouping them into a single item.
- **Avoid using transactions for bulk ingestion — use `BatchWriteItem` instead.**

## Using transactional APIs with global tables
Transactional operations provide ACID guarantees **only within the AWS Region** where the write API was invoked. **Transactions aren't supported across Regions** in global tables. You may observe **partially completed transactions** in another Region as changes are replicated (changes are replicated only after committed in the source Region).

## DynamoDB Transactions vs. the AWSLabs transactions client library
DynamoDB transactions provide a more cost-effective, robust, and performant replacement for the AWSLabs transactions client library. Update your applications to use the native, server-side transaction APIs.
