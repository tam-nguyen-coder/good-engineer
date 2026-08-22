# Question #48 - Topic 1

A company's website uses an Amazon EC2 instance store for its catalog of items. The company wants to make sure that the catalog is highly available and that the catalog is stored in a durable location. What should a solutions architect do to meet these requirements?

## Options

**A.** Move the catalog to Amazon ElastiCache for Redis.

**B.** Deploy a larger EC2 instance with a larger instance store.

**C.** Move the catalog from the instance store to Amazon S3 Glacier Deep Archive.

**D.** Move the catalog to an Amazon Elastic File System (Amazon EFS) file system.



---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Website đang sử dụng `Amazon EC2 instance store` để lưu trữ catalog các mặt hàng.
- **Existing Resources:** `EC2 instance` với `instance store` (ephemeral storage gắn liền với host vật lý).
- **Current Issue/Goal:** Đảm bảo catalog có tính **highly available (HA)** và được lưu trữ tại vị trí **durable** (bền vững, không mất dữ liệu khi instance gặp sự cố).

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa |
|---------|---------|
| `EC2 instance store` | Bộ nhớ tạm (ephemeral) gắn liền với instance. Dữ liệu bị mất khi instance stop, terminate hoặc hardware failure. Không durable, không HA. |
| Highly available | Dữ liệu phải sẵn sàng truy cập ngay cả khi một instance hoặc một AZ gặp sự cố. |
| Durable | Dữ liệu được bảo toàn lâu dài, độc lập với vòng đời của EC2 instance. |
| `Amazon EFS` | Managed file system, tự động replicate dữ liệu across multiple AZs. Có thể mount đồng thời vào hàng trăm `EC2 instances`. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Chọn giải pháp thay thế storage để đạt HA và durability.
- **Constraints:** Loại bỏ hoàn toàn rủi ro của `instance store`; giải pháp mới phải phù hợp cho website đang hoạt động (active data).

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**
**Giải thích:** `Amazon Elastic File System (Amazon EFS)` là managed file system có tính highly available và durable theo thiết kế, tự động lưu trữ dữ liệu redundantly across nhiều Availability Zones. `EFS` có thể được mount đồng thời vào nhiều `EC2 instances`, giúp website duy trì khả năng truy cập catalog ngay cả khi một instance bị lỗi hoặc thay thế. Việc chuyển catalog từ `instance store` (dễ mất dữ liệu) sang `EFS` đáp ứng đồng thời cả hai yêu cầu: **durability** (dữ liệu được bảo vệ lâu dài) và **high availability** (truy cập từ nhiều instance trên nhiều AZ).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:** `Amazon ElastiCache for Redis` là dịch vụ caching in-memory, được thiết kế để tăng tốc độ đọc dữ liệu (cache layer), không phải primary storage. Mặc dù có tùy chọn persistence, nó không được thiết kế để làm nơi lưu trữ catalog chính thức với độ bền cao như yêu cầu.

**❌ Đáp án B:** Triển khai `EC2 instance` lớn hơn với `instance store` lớn hơn không giải quyết được vấn đề cốt lõi. `Instance store` vẫn là ephemeral storage — dữ liệu sẽ bị mất hoàn toàn nếu instance stop, terminate, hoặc underlying hardware fail. Không cung cấp tính durable cũng như highly available.

**❌ Đáp án C:** `Amazon S3 Glacier Deep Archive` là storage class dành cho dữ liệu lưu trữ dài hạn (archiving) với chi phí cực thấp. Thời gian truy xuất dữ liệu rất chậm (12–48 giờ), hoàn toàn không phù hợp để làm backend cho website catalog cần truy cập thường xuyên và tức thì.

## 6. MẸO GHI NHỚ
🧠 *`EC2 Instance Store` = ephemeral (tạm thời), mất dữ liệu khi instance hỏng → không bao giờ durable. Khi đề bài yêu cầu HA + durability cho dữ liệu gắn với EC2, hãy nghĩ đến `EFS` (multi-AZ, shared file system) hoặc `S3` (object storage). `EBS` chỉ durable nhưng chỉ ở single AZ nên chưa đủ HA. `Glacier` là archive, không dùng cho active website data. `ElastiCache` là cache, không phải primary durable store.*
