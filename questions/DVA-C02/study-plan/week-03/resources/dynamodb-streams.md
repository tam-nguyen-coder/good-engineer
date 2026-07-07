# DynamoDB Streams — Change Data Capture

> **Nguồn (AWS official):** https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Streams.html
> **Tuần:** 3 — DynamoDB · **Loại:** AWS Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)
- `DynamoDB Streams` ghi lại **time-ordered sequence** các thay đổi item-level, lưu log **tối đa 24 giờ**; near-real-time.
- **4 loại `StreamViewType`** (chọn khi bật stream): `KEYS_ONLY`, `NEW_IMAGE`, `OLD_IMAGE`, `NEW_AND_OLD_IMAGES`.
- **Đảm bảo:** mỗi record xuất hiện **đúng một lần** (exactly once) và **đúng thứ tự** thay đổi cho từng item.
- **KHÔNG sửa được `StreamViewType`** sau khi tạo — phải tắt stream cũ và tạo stream mới (sẽ có stream descriptor/ARN khác).
- Endpoint riêng: app phải kết nối **DynamoDB Streams endpoint** (khác endpoint DynamoDB); cùng Region.
- Stream gồm các **shard**; record trong shard bị **xóa tự động sau 24h**. Xử lý parent shard trước child shard. **Tối đa 2 process đọc cùng 1 shard** cùng lúc (quá 2 → throttling).
- Bẫy: `PutItem`/`UpdateItem` **không làm đổi dữ liệu** thì **không** sinh stream record.
- **DynamoDB Streams vs Kinesis Data Streams:** Streams giữ 24h, exactly-once + ordering; Kinesis giữ lâu hơn, throughput cao hơn nhưng **KHÔNG** đảm bảo ordering/deduplication.
- Thường dùng với **AWS Lambda triggers** (xử lý event khi item thay đổi) và là **điều kiện tiên quyết cho Global Tables**.

---

## 📄 Nội dung (trích từ tài liệu gốc)

# Change data capture for DynamoDB Streams

DynamoDB Streams captures a time-ordered sequence of item-level modifications in any DynamoDB table and stores this information in a log for **up to 24 hours**. Applications can access this log and view the data items as they appeared before and after they were modified, in near-real time.

Encryption at rest encrypts the data in DynamoDB streams.

A *DynamoDB stream* is an ordered flow of information about changes to items in a DynamoDB table. When you enable a stream on a table, DynamoDB captures information about every modification to data items in the table. Whenever an application creates, updates, or deletes items in the table, DynamoDB Streams writes a *stream record* with the primary key attributes of the items that were modified. You can configure the stream so that the stream records capture additional information, such as the "before" and "after" images of modified items.

DynamoDB Streams helps ensure the following:
- Each stream record appears **exactly once** in the stream.
- For each item that is modified, the stream records appear in the **same sequence** as the actual modifications to the item.

## Endpoints for DynamoDB Streams

AWS maintains **separate endpoints** for DynamoDB and DynamoDB Streams. To work with tables and indexes, your application must access a DynamoDB endpoint. To read and process DynamoDB Streams records, your application must access a DynamoDB Streams endpoint **in the same Region**.

DynamoDB Streams offers two sets of endpoints:
- **IPv4-only endpoints:** `streams.dynamodb.{region}.amazonaws.com`
- **Dual-stack endpoints** (IPv4 + IPv6): `streams-dynamodb.{region}.api.aws`

The AWS SDKs provide separate clients for DynamoDB and DynamoDB Streams. To connect to both endpoints, your application must instantiate two clients.

## Enabling a stream

You can enable a stream on a new table when you create it, or enable/disable/change settings on an existing table. DynamoDB Streams operates asynchronously, so there is **no performance impact** on a table if you enable a stream.

`StreamViewType` options — the information written to the stream whenever data is modified:
- `KEYS_ONLY` — Only the key attributes of the modified item.
- `NEW_IMAGE` — The entire item, as it appears **after** it was modified.
- `OLD_IMAGE` — The entire item, as it appeared **before** it was modified.
- `NEW_AND_OLD_IMAGES` — Both the new and the old images of the item.

The `StreamSpecification` parameter (in `CreateTable`/`UpdateTable`):
- `StreamEnabled` — `true` or `false`.
- `StreamViewType` — one of the four values above.

You receive a `ValidationException` if you try to enable a stream on a table that already has one, or disable a stream on a table that doesn't have one. When you set `StreamEnabled` to `true`, DynamoDB creates a new stream with a unique stream descriptor. If you disable and then re-enable a stream, a new stream is created with a **different** stream descriptor.

Every stream is identified by an ARN, for example:
```
arn:aws:dynamodb:us-west-2:111122223333:table/TestTable/stream/2015-05-11T21:21:33.291
```
Use `DescribeTable` and look for `LatestStreamArn` to get the latest stream descriptor.

**Note:** It is **not possible to edit a `StreamViewType`** once a stream has been set up. To make changes, you must disable the current stream and create a new one.

## Reading and processing a stream

A stream consists of *stream records*; each represents a single data modification and is assigned a **sequence number** reflecting the publish order. Stream records are organized into groups, or **shards**. Each shard contains multiple stream records. The stream records within a shard are **removed automatically after 24 hours**.

Shards are **ephemeral** — created and deleted automatically as needed. A shard can **split** into multiple new shards automatically (e.g., in response to high write activity), so applications can process records from multiple shards in parallel. Because shards have a lineage (parent/children), an application must always process a **parent shard before its child shard** to keep records in the correct order. (The DynamoDB Streams Kinesis Adapter handles this for you.)

If you disable a stream, open shards are closed, and the data remains readable for 24 hours.

**Note:** If you perform a `PutItem` or `UpdateItem` operation that **does not change any data** in an item, DynamoDB Streams does **not** write a stream record.

**Note:** No more than **two processes** at most should be reading from the same stream's shard at the same time. Having more than two readers per shard can result in **throttling**.

DynamoDB Streams API actions:
- `ListStreams` — Returns a list of stream descriptors for the current account and endpoint.
- `DescribeStream` — Returns information about a stream (status, ARN, composition of its shards, corresponding table). Optional `ShardFilter` field to retrieve child shards of a parent.
- `GetShardIterator` — Returns a *shard iterator* describing a location within a shard (oldest point, newest point, or a particular point).
- `GetRecords` — Returns the stream records from within a given shard (requires the shard iterator from `GetShardIterator`).

### Shard discovery
Two methods to track new shards:
- **Polling the entire stream topology** — use `DescribeStream` to regularly poll; compare results over time to detect new shards.
- **Discovering child shards** — use `DescribeStream` with `ShardFilter` specifying a parent shard; DynamoDB returns its immediate child shards. Useful for transitioning from a closed shard to its child shard efficiently.

### Data retention limit for DynamoDB Streams
All data in DynamoDB Streams is subject to a **24-hour lifetime**. Data older than 24 hours is susceptible to trimming (removal) at any moment. If you disable a stream, the data remains readable for 24 hours, then expires and is automatically deleted. **There is no mechanism for manually deleting an existing stream** — you must wait until the 24-hour retention limit expires.
