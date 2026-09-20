# Apache Kafka 4.3 — Hardware and OS: đĩa, JBOD vs RAID, filesystem, page cache

> **Nguồn (official):** https://kafka.apache.org/43/operations/hardware-and-os/ · bổ sung metric từ https://kafka.apache.org/43/operations/monitoring/
> **Tuần:** 2 — Cluster Config I · **Loại:** Apache Kafka Docs (operations)
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có rút gọn) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- **Kafka khuyến nghị JBOD hơn RAID.** Lý do docs nêu thẳng: RAID "is usually a big performance hit for write throughput and reduces the available disk space", và rebuild RAID nặng tới mức "it effectively disables the server, so this does not provide much real availability improvement". Dư thừa đã có sẵn ở tầng ứng dụng: "Since Kafka has replication the redundancy provided by RAID can also be provided at the application level."
- **Cách Kafka rải partition trên nhiều `log.dirs`:** "partitions will be assigned round-robin to data directories. Each partition will be entirely in one of the data directories." Cụ thể hơn: partition mới được đặt vào thư mục **đang có ít partition nhất** — **theo SỐ PARTITION, không theo dung lượng trống**. Đây là câu hỏi CCAAK kinh điển, và cũng là lý do "load imbalance between disks" vẫn xảy ra dù Kafka rải đều về số lượng.
- Một partition **nằm trọn trong một thư mục** — không bao giờ trải qua 2 ổ. Vì vậy một topic có vài partition rất to sẽ làm lệch đĩa dù số partition đã đều.
- **Một ổ hỏng ≠ broker chết.** Từ khi JBOD được hỗ trợ trong KRaft, log dir hỏng chỉ đưa **các partition trên ổ đó** về offline; broker vẫn phục vụ những partition ở ổ khác. Quan sát bằng `kafka.log:type=LogManager,name=OfflineLogDirectoryCount` và `kafka.log:type=LogManager,name=LogDirectoryOffline`.
- **Filesystem:** XFS được khuyến nghị — "XFS resulted in much better local times (160ms vs. 250ms+ for the best EXT4 configuration), as well as lower average wait times", và "The XFS performance also showed less variability in disk performance".
- **Đừng bật fsync ứng dụng.** Mặc định "disable application fsync entirely", dựa vào background flush của OS; bật fsync "can introduce latency as fsync in most Linux filesystems blocks writes to the file whereas the background flushing does much more granular page-level locking".
- **Page cache là tài nguyên chính**, không phải heap. Heap broker ~6 GB, phần RAM còn lại để OS làm page cache (xem §6 của [`CCAAK-STUDY-PLAN.md`](../../../CCAAK-STUDY-PLAN.md)).

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Disks and Filesystem — RAID vs JBOD

> "RAID can potentially do better at balancing load between disks" — nhưng:
>
> - "it is usually a big performance hit for write throughput and reduces the available disk space";
> - rebuild RAID array "effectively disables the server, so this does not provide much real availability improvement";
> - "Since Kafka has replication the redundancy provided by RAID can also be provided at the application level."

### Multiple data directories

> "partitions will be assigned round-robin to data directories. Each partition will be entirely in one of the data directories."

Docs cũng cảnh báo: phân bố partition không đều "can lead to load imbalance between disks".

### Flush management và page cache

> Mặc định "disable application fsync entirely. This means relying on the background flush done by the OS and Kafka's own background flush."
>
> Lý do: application-level flushing "can introduce latency as fsync in most Linux filesystems blocks writes to the file whereas the background flushing does much more granular page-level locking."

### Filesystem Selection — XFS vs EXT4

> "XFS resulted in much better local times (160ms vs. 250ms+ for the best EXT4 configuration), as well as lower average wait times."
>
> "The XFS performance also showed less variability in disk performance."

Với EXT4, các tuỳ chọn như `data=writeback` và tắt journaling tăng throughput nhưng đánh đổi an toàn khi mất điện nhiều máy cùng lúc.

### Metric liên quan tới storage (từ trang Monitoring)

| MBean | Dùng để |
|---|---|
| `kafka.log:type=LogManager,name=OfflineLogDirectoryCount` | Số log dir đang offline trên broker này — **alert ở > 0** |
| `kafka.log:type=LogManager,name=LogDirectoryOffline` | Cờ log dir offline |
| `kafka.log:type=Log,name=Size,topic=([-.\w]+),partition=([0-9]+)` | Dung lượng từng partition — dùng để tìm partition làm đầy đĩa |
| `kafka.log:type=Log,name=LogStartOffset,topic=([-.\w]+),partition=([0-9]+)` | Offset đầu tiên còn tồn tại — **tăng lên nghĩa là retention vừa xoá segment** |
| `kafka.log:type=Log,name=LogEndOffset,topic=([-.\w]+),partition=([0-9]+)` | Offset cuối |
| `kafka.log:type=LogFlushStats,name=LogFlushRateAndTimeMs` | Nhịp và thời gian flush |
| `kafka.server:type=KafkaRequestHandlerPool,name=RequestHandlerAvgIdlePercent` | Độ rảnh của I/O thread pool → chỉnh `num.io.threads` |
| `kafka.network:type=SocketServer,name=NetworkProcessorAvgIdlePercent` | Độ rảnh của network thread → chỉnh `num.network.threads` |
| `kafka.network:type=RequestChannel,name=RequestQueueSize` | Hàng đợi request, so với `queued.max.requests` = 500 |
| `kafka.server:type=ReplicaManager,name=UnderReplicatedPartitions` | URP → chỉnh `num.replica.fetchers` |
| `kafka.server:type=ReplicaManager,name=UnderMinIsrPartitionCount` | ISR đã dưới `min.insync.replicas` |
| `kafka.controller:type=KafkaController,name=OfflinePartitionsCount` | Partition không có leader |
| `kafka.log.remote:type=RemoteLogManager,name=RemoteLogSizeBytes,topic=([-.\w]+),partition=([0-9]+)` | Dung lượng đã đẩy lên tiered storage |

> 📌 Phân rã `TotalTimeMs` của request gồm: `RequestQueueTimeMs` (chờ trong hàng đợi) → `LocalTimeMs` (xử lý ở leader) → `RemoteTimeMs` (chờ follower, chỉ có với `acks=all`) → `ResponseQueueTimeMs` → `ResponseSendTimeMs`. Đĩa chậm hiện ra ở **`LocalTimeMs`**; thiếu I/O thread hiện ra ở **`RequestQueueTimeMs`**. Phân biệt hai cái này là mấu chốt để không tăng nhầm config.
