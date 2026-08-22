# DynamoDB Partition Key Design — Best Practices

> **Nguồn (AWS official):** https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/bp-partition-key-design.html
> **Tuần:** 3 — DynamoDB · **Loại:** AWS Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)
- **Giới hạn mỗi partition:** tối đa **3,000 read units/giây** và **1,000 write units/giây**. Đây là con số hay bị hỏi trong đề.
- **Định nghĩa unit:** 1 read unit = 1 strongly consistent read/s **hoặc** 2 eventually consistent reads/s, cho item **≤ 4 KB**. 1 write unit = 1 write/s cho item **≤ 1 KB**.
- **Mục tiêu thiết kế:** phân bổ hoạt động **đồng đều (uniform)** trên tất cả partition key → tránh **hot partition / hot key**.
- Phải tính **item size** khi ước lượng throughput: item 20 KB → 1 strongly consistent read tốn **5 read units** → chỉ ~600 consistent reads/s trên 1 item trước khi chạm limit partition.
- **Adaptive capacity** áp dụng cho CẢ on-demand lẫn provisioned mode — tự dồn capacity cho partition "nóng".
- Kỹ thuật chống hot key: **write sharding** (thêm random/calculated suffix vào partition key để trải đều), và phân bổ tải khi bulk upload.
- Bẫy: dùng key có cardinality thấp (VD status = "active/inactive") làm partition key → dồn traffic vào ít partition → throttling dù tổng capacity còn dư.

---

## 📄 Nội dung (trích từ tài liệu gốc)

# Best practices for designing and using partition keys effectively in DynamoDB

The primary key that uniquely identifies each item in an Amazon DynamoDB table can be **simple** (a partition key only) or **composite** (a partition key combined with a sort key).

You should design your application for **uniform activity across all partition keys** in the table and its secondary indexes. You can determine the access patterns that your application requires, and the read and write units that each table and secondary index requires.

**Note:** Adaptive capacity applies to **on-demand mode and provisioned capacity**.

Every partition in a DynamoDB table is designed to deliver a maximum capacity of **3,000 read units per second** and **1,000 write units per second**.
- One **read unit** represents one strongly consistent read operation per second, or **two eventually consistent** read operations per second, for an item **up to 4 KB** in size.
- One **write unit** represents one write operation per second for an item **up to 1 KB** in size.

You must factor in the **item size** when evaluating the partition throughput limits for your table. For example, if the table has an item size of **20 KB**, a single consistent read operation will consume **5 read units**. This means you can concurrently drive **600 consistent read operations per second** on that single item before reaching the partition limits.

The total throughput across all partitions in the table can be constrained by the provisioned throughput in **provisioned mode**, or by the **table-level throughput limit** in on-demand mode. See Service Quotas for more information.

**Topics**
- Designing partition keys to distribute your workload in DynamoDB (`bp-partition-key-uniform-load.html`)
- Using write sharding to distribute workloads evenly in your DynamoDB table (`bp-partition-key-sharding.html`)
- Distributing write activity efficiently during data upload in DynamoDB (`bp-partition-key-data-upload.html`)
