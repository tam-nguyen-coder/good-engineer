# Bản đồ chương sách *Kafka: The Definitive Guide* (2nd ed.) → tuần trong plan

> **Nguồn:** **tổng hợp** — ánh xạ mục lục sách sang lộ trình 10 tuần của repo này. Không crawl từ tài liệu chính thức.
> Sách: *Kafka: The Definitive Guide, 2nd Edition* — Gwen Shapira, Todd Palino, Rajini Sivaram, Krit Petty (O'Reilly, 2021). Confluent phát hành bản PDF miễn phí.
> **Tuần:** 10 — Tuần chốt · **Loại:** Tổng hợp
> Về [file học Tuần 10](../README.md) · [Kế hoạch tổng](../../../KAFKA-STUDY-PLAN.md)

## 🎯 Cách dùng bản đồ này

- Sách viết cho **Kafka 2.x** nên nhiều **giá trị mặc định đã lỗi thời** (`acks=1`, `linger.ms=0`, `session.timeout.ms=10000`, và toàn bộ phần ZooKeeper). Đọc sách để hiểu **cơ chế**, lấy **con số** từ [`../../VALIDATION.md`](../../VALIDATION.md) và §6 của kế hoạch tổng.
- Sách **không** phủ: KRaft ở mức vận hành thật, KIP-848, share groups (Queues for Kafka), ELR, tiered storage. Bốn chủ đề này chỉ có trong tài liệu tuần tương ứng của repo.
- Dùng khi bạn muốn **đào sâu một chủ đề đã học**, không dùng thay cho lộ trình.

## Bảng ánh xạ

| Chương | Tên chương | Tuần | Ghi chú khi đọc |
|---|---|---|---|
| 1 | Meet Kafka | 1 | Bối cảnh và mô hình publish/subscribe; bỏ qua phần lịch sử LinkedIn nếu gấp |
| 2 | Installing Kafka | 1 | **Đã lỗi thời nặng** — toàn bộ phần ZooKeeper không còn đúng; dùng lab Docker KRaft của Tuần 1 thay thế |
| 3 | Kafka Producers | **3** | Chương quan trọng nhất cho domain DEV; đối chiếu lại mọi giá trị mặc định |
| 4 | Kafka Consumers | **4** | Đọc kỹ phần offset commit và rebalance listener; phần assignor chưa có KIP-848 |
| 5 | Managing Kafka Programmatically | 4, 8 | AdminClient — hữu ích cho lab đo lag và quản trị bằng code |
| 6 | Kafka Internals | 1, 2 | Controller, replication, request processing, physical storage; phần controller nay là KRaft |
| 7 | Reliable Data Delivery | **2** | `acks` × `min.insync.replicas`, unclean election, delivery semantics — nền của nhiều câu FUND |
| 8 | Exactly-Once Semantics | **3** | Idempotent producer và transactions; ghép với KIP-98 trong `week-03/resources/` |
| 9 | Building Data Pipelines | 5 | Khái niệm pipeline, đặt nền cho Connect |
| 10 | Cross-Cluster Data Mirroring | **8** | MirrorMaker 2, active-active/active-passive, offset translation |
| 11 | Securing Kafka | **7** | TLS, SASL, ACL, quotas — cấu trúc gần trùng khớp với Buổi A tuần 7 |
| 12 | Administering Kafka | 8 | CLI quản trị, reassignment, cấu hình động |
| 13 | Monitoring Kafka | **8** | Bảng JMX metric; tên metric vẫn đúng, ngưỡng vẫn dùng được |
| 14 | Stream Processing | **6** | Khái niệm stream/table, windowing, join; API Streams trong sách còn thiếu vài bổ sung mới |
| Phụ lục A | Installing Kafka Clients | 1 | Tham khảo nhanh |
| Phụ lục B | Other Kafka Clients | 1 | Bối cảnh cho quyết định dùng `kafkajs` trong labs |

## Thứ tự đọc đề xuất nếu chỉ có thời gian cho 5 chương

1. **Ch.3 Producers** → nền của 28% đề.
2. **Ch.4 Consumers** → phần còn lại của 28% đề.
3. **Ch.7 Reliable Data Delivery** → xương sống của domain Fundamentals.
4. **Ch.8 Exactly-Once Semantics** → chủ đề dễ mất điểm nhất vì hay bị hiểu nửa vời.
5. **Ch.13 Monitoring** → phủ gần trọn domain Observability.

## Chỗ sách nói khác thực tế 4.x — đọc với cảnh giác

| Sách (2.x) | Thực tế 4.3 |
|---|---|
| ZooKeeper quản metadata, `--zookeeper` trong CLI | **KRaft**, `--bootstrap-server`, `__cluster_metadata` |
| `acks` mặc định `1`, idempotence tắt | `acks=all`, `enable.idempotence=true` (từ 3.0) |
| `linger.ms=0` | **`5`** (từ 4.0) |
| `session.timeout.ms=10000` | **`45000`** (từ 3.0) |
| Rebalance chỉ có eager và cooperative phía client | Thêm **KIP-848** (broker tính assignment, GA 4.0) |
| Không có khái niệm queue | **Share groups** (KIP-932, GA 4.2) |
| Leader chỉ chọn trong ISR | Thêm **ELR** (opt-in 4.0, mặc định cho cluster mới từ 4.1) |
| Lưu trữ chỉ trên disk broker | Thêm **tiered storage** (KIP-405) |
