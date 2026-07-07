# DynamoDB Secondary Indexes — GSI vs LSI

> **Nguồn (AWS official):** https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/SecondaryIndexes.html
> **Tuần:** 3 — DynamoDB · **Loại:** AWS Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)
- **GSI (Global Secondary Index):** partition key + (tùy chọn) sort key **khác** base table; scale/throughput **riêng**; chỉ **eventual consistency**; tạo/xóa **bất cứ lúc nào** (kể cả sau khi tạo table); tối đa **20 GSI/table** (default quota).
- **LSI (Local Secondary Index):** **cùng partition key** với base table, sort key khác; **phải tạo cùng lúc với table**, **không thể thêm/xóa sau**; hỗ trợ **cả eventual & strong consistency**; tối đa **5 LSI/table**.
- **Giới hạn 10 GB:** LSI có ràng buộc — tổng size mọi item cho mỗi partition key value **≤ 10 GB**. GSI **không** có giới hạn size này.
- **Capacity:** GSI có RCU/WCU **riêng** (query/scan tiêu thụ capacity của index). LSI **dùng chung** RCU/WCU của **base table**.
- **Projected attributes:** với **GSI**, query chỉ trả về attribute đã project (DynamoDB **không** fetch từ table). Với **LSI**, có thể xin cả attribute chưa project — DynamoDB tự fetch từ table (tốn thêm capacity).
- Key attribute của index phải là top-level scalar: `String`, `Number`, hoặc `Binary` (không dùng document/set làm key).
- Bẫy: cần đổi partition key để query → dùng **GSI**; cần strong consistency trên index → chỉ **LSI** làm được; cần thêm index sau khi table đã chạy → chỉ **GSI**.

---

## 📄 Nội dung (trích từ tài liệu gốc)

# Improving data access with secondary indexes in DynamoDB

Amazon DynamoDB provides fast access to items in a table by specifying primary key values. However, many applications might benefit from having one or more secondary (or alternate) keys available, to allow efficient access to data with attributes other than the primary key. To address this, you can create one or more secondary indexes on a table and issue `Query` or `Scan` requests against these indexes.

A *secondary index* is a data structure that contains a subset of attributes from a table, along with an alternate key to support `Query` operations. You can retrieve data from the index using a `Query`, in much the same way as you use `Query` with a table. A table can have multiple secondary indexes.

**Note**
You can also `Scan` an index, in much the same way as you would `Scan` a table. Cross-account access for secondary index scan operations is currently not supported with resource-based policies.

Every secondary index is associated with exactly one table, from which it obtains its data. This is called the *base table* for the index. When you create an index, you define an alternate key for the index (partition key and sort key). You also define the attributes that you want to be *projected*, or copied, from the base table into the index. DynamoDB copies these attributes into the index, along with the primary key attributes from the base table.

Every secondary index is automatically maintained by DynamoDB. When you add, modify, or delete items in the base table, any indexes on that table are also updated to reflect these changes.

DynamoDB supports two types of secondary indexes:
- **Global secondary index (GSI)** — An index with a partition key and a sort key that can be **different** from those on the base table. A global secondary index is considered "global" because queries on the index can span all of the data in the base table, across all partitions. A global secondary index is stored in its own partition space away from the base table and **scales separately** from the base table.
- **Local secondary index (LSI)** — An index that has the **same partition key** as the base table, but a different sort key. A local secondary index is "local" in the sense that every partition of a local secondary index is scoped to a base table partition that has the same partition key value.

## Comparison: GSI vs LSI

| Characteristic | Global secondary index | Local secondary index |
| --- | --- | --- |
| Key Schema | Primary key can be either simple (partition key) or composite (partition key + sort key). | Primary key **must be composite** (partition key + sort key). |
| Key Attributes | Index partition key and sort key (if present) can be any base table attribute of type string, number, or binary. | Partition key is the **same** attribute as the base table partition key. Sort key can be any base table attribute of type string, number, or binary. |
| Size Restrictions Per Partition Key Value | **No size restrictions.** | For each partition key value, the total size of all indexed items must be **10 GB or less**. |
| Online Index Operations | Can be created at the same time as the table. You can also **add** a new GSI to an existing table, or **delete** an existing GSI. | Created **at the same time** as the table. You **cannot add** an LSI to an existing table, nor **delete** any existing LSIs. |
| Queries and Partitions | Lets you query over the **entire table**, across all partitions. | Lets you query over a **single partition**, as specified by the partition key value in the query. |
| Read Consistency | Queries support **eventual consistency only**. | You can choose **either eventual consistency or strong consistency**. |
| Provisioned Throughput Consumption | Every GSI has its **own** provisioned throughput settings. Queries/scans consume capacity units **from the index**, not the base table. GSI on global tables consumes write capacity units. | Queries/scans consume RCU **from the base table**. Writes to the table also update its LSIs, consuming WCU **from the base table**. |
| Projected Attributes | You can only request attributes **projected into the index**. DynamoDB does **not** fetch other attributes from the table. | You can request attributes **not projected** into the index. DynamoDB **automatically fetches** those from the table. |

If you want to create more than one table with secondary indexes, you must do so **sequentially**. If you try to concurrently create more than one table with a secondary index, DynamoDB returns a `LimitExceededException`.

Each secondary index uses the same **table class** and **capacity mode** as the base table it is associated with. For each secondary index, you must specify:
- The type of index — GSI or LSI.
- A name for the index (naming rules same as tables; must be unique for the base table).
- The key schema for the index. Every attribute in the index key schema must be a top-level attribute of type `String`, `Number`, or `Binary`. Documents and sets are **not allowed** as keys.
  - For a **GSI**, the partition key can be any scalar attribute of the base table. A sort key is optional and can be any scalar attribute.
  - For an **LSI**, the partition key must be the **same** as the base table's partition key, and the sort key must be a non-key base table attribute.
- Additional attributes to **project** from the base table into the index (in addition to the table's key attributes, which are automatically projected into every index). You can project attributes of any data type, including scalars, documents, and sets.
- Provisioned throughput settings, if necessary:
  - For a **GSI**, you must specify read and write capacity unit settings, **independent** of the base table.
  - For an **LSI**, you do **not** need to specify RCU/WCU; operations draw from the base table's provisioned throughput.

For maximum query flexibility, you can create up to **20 global secondary indexes** (default quota) and up to **5 local secondary indexes** per table.

To get a detailed listing of secondary indexes on a table, use the `DescribeTable` operation. It returns the name, storage size, and item counts for every secondary index. These values are **not updated in real time** but are refreshed approximately **every six hours**.

You can access the data in a secondary index using either the `Query` or `Scan` operation. When you delete a table, all of the indexes associated with that table are also deleted.
