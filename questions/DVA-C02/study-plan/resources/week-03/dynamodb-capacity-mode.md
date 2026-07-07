# DynamoDB Throughput Capacity — On-Demand vs Provisioned

> **Nguồn (AWS official):** https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/HowItWorks.ReadWriteCapacityMode.html
> **Tuần:** 3 — DynamoDB · **Loại:** AWS Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)
- DynamoDB có **2 chế độ throughput**: `On-demand` (serverless, pay-per-request) và `Provisioned` (tự khai báo RCU/WCU trước).
- `On-demand` là **mặc định và khuyến nghị** cho hầu hết workload — không cần capacity planning, tự scale từ nhỏ tới hàng triệu request/giây, chỉ trả tiền theo request thực dùng (scale-to-zero).
- `Provisioned` phù hợp workload **ổn định, dự đoán được**; bạn trả tiền theo capacity đã cấp phát theo giờ (RCU/WCU) **bất kể có dùng hết hay không** → chi phí dự đoán được, khống chế request rate.
- Bẫy thi: chọn `On-demand` khi traffic **spiky / không đoán trước / mới launch app**; chọn `Provisioned` khi traffic **đều, dự báo được** và muốn tối ưu chi phí (có thể kèm Auto Scaling + Reserved Capacity).
- Throughput mode quyết định cả **cách quản lý capacity** lẫn **cách tính tiền** read/write.
- Có thể chuyển đổi giữa 2 chế độ (xem trang "switching capacity modes" — có ràng buộc tần suất).

---

## 📄 Nội dung (trích từ tài liệu gốc)

# DynamoDB throughput capacity

This section provides an overview of the two throughput modes available for your DynamoDB table and considerations in selecting the appropriate capacity mode for your application. A table's throughput mode determines how the capacity of a table is managed. Throughput mode also determines how you're charged for the read and write operations on your tables. In Amazon DynamoDB, you can choose between **on-demand mode** and **provisioned mode** for your tables to accommodate different workload requirements.

**Topics**
- On-demand mode
- Provisioned mode
- DynamoDB on-demand capacity mode (`on-demand-capacity-mode.html`)
- DynamoDB provisioned capacity mode (`provisioned-capacity-mode.html`)
- Understanding DynamoDB warm throughput (`warm-throughput.html`)
- DynamoDB burst and adaptive capacity (`burst-adaptive-capacity.html`)
- Considerations when switching capacity modes in DynamoDB (`bp-switching-capacity-modes.html`)

## On-demand mode

Amazon DynamoDB on-demand mode is a serverless throughput option that simplifies database management and automatically scales to support customers' most demanding applications. DynamoDB on-demand enables you to create a table without worrying about capacity planning, monitoring usage, and configuring scaling policies. DynamoDB on-demand offers pay-per-request pricing for read and write requests so that you only pay for what you use. For on-demand mode tables, you don't need to specify how much read and write throughput you expect your application to perform.

On-demand mode is the **default and recommended** throughput option for most DynamoDB workloads. DynamoDB handles all aspects of throughput management and scaling to support workloads that can start small and scale to millions of requests per second. You can read and write to your DynamoDB tables as needed without managing throughput capacity on the table.

## Provisioned mode

In provisioned mode, you must specify the number of reads and writes per second that you require for your application. You'll be charged based on the hourly read and write capacity you have provisioned, **not how much of that provisioned capacity you actually consumed**. This helps you govern your DynamoDB use to stay at or below a defined request rate in order to obtain cost predictability.

You can choose to use provisioned capacity if you have steady workloads with predictable growth, and if you can reliably forecast capacity requirements for your application.
