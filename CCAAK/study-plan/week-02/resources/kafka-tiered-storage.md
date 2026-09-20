# Apache Kafka 4.3 — Tiered Storage (góc cấu hình)

> **Nguồn (official):** https://kafka.apache.org/43/operations/tiered-storage/ · config reference: https://kafka.apache.org/43/configuration/tiered-storage-configs/
> **Tuần:** 2 — Cluster Config I · **Loại:** Apache Kafka Docs (operations)
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có rút gọn) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- Tiered storage là **hai công tắc, hai tầng**: bật ở cluster bằng broker config **`remote.log.storage.system.enable=true`** (read-only → cần restart), rồi bật cho từng topic bằng **`remote.storage.enable=true`**. Chỉ bật một trong hai là không chạy.
- Khi bật, retention tách làm hai: **`local.retention.ms` / `local.retention.bytes`** quyết định giữ bao lâu trên **đĩa broker**, còn **`retention.ms` / `retention.bytes`** quyết định giữ bao lâu **tổng cộng** (kể cả trên remote). Mặc định local là **-2** = "kế thừa giá trị retention tổng" → bật tiered storage mà quên hạ local retention thì **không tiết kiệm được đĩa nào**.
- Đây chính là cách trả lời câu "cần retention 1 năm nhưng không muốn mua thêm đĩa broker": bật tiered storage + `local.retention.ms` nhỏ (vài giờ), `retention.ms` = 1 năm.
- **Không hỗ trợ compacted topic.** Một topic `cleanup.policy=compact` (hoặc `compact,delete`) không dùng được tiered storage. Kết hợp `remote.storage.enable=true` với JBOD nhiều `log.dirs` cũng không được hỗ trợ.
- **Không tắt được ở mức cluster** khi còn topic đang bật: phải xoá/tắt hết topic có `remote.storage.enable=true` trước rồi mới hạ `remote.log.storage.system.enable`.
- Ngoài hai công tắc còn 3 config bắt buộc ở broker: `remote.log.storage.manager.class.name`, `remote.log.storage.manager.class.path`, `remote.log.metadata.manager.listener.name`.
- `remote.log.copy.disable=true` (topic) = ngừng đẩy segment mới lên remote nhưng vẫn đọc được cái đã đẩy — bước đầu của quy trình gỡ tiered storage khỏi một topic.
- Quan sát bằng `kafka.log.remote:type=RemoteLogManager,name=RemoteLogSizeBytes,topic=...,partition=...`.

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Broker-Level Configuration

To enable tiered storage at the broker level, set:

```
remote.log.storage.system.enable=true
```

Additional required broker configurations include:

- `remote.log.storage.manager.class.name` — specifies the `RemoteStorageManager` implementation
- `remote.log.storage.manager.class.path` — path to the implementation JAR
- `remote.log.metadata.manager.listener.name` — mandatory property for the default metadata manager implementation

### Topic-Level Configuration

Enable tiered storage per topic using:

```
remote.storage.enable=true
```

When enabled, configure local retention separately from overall retention:

- `local.retention.ms` — time before local segments move to remote storage
- `local.retention.bytes` — size threshold for local segments
- `retention.ms` — overall retention period (segments in remote storage deleted after this time)
- `retention.bytes` — overall size limit

> "If local retention settings are unset, the system defaults to `retention.ms` and `retention.bytes` values."

### Quick-Start Example

Create a tiered topic:

```
$ bin/kafka-topics.sh --create --topic tieredTopic \
--bootstrap-server localhost:9092 --config remote.storage.enable=true \
--config local.retention.ms=1000 --config retention.ms=3600000 \
--config segment.bytes=1048576
```

Modify topic configuration:

```
$ bin/kafka-configs.sh --bootstrap-server localhost:9092 \
--alter --entity-type topics --entity-name tieredTopic \
--add-config 'remote.storage.enable=true,remote.log.copy.disable=true'
```

### Unsupported Features

- **Compacted topics**
- Log segments lacking producer snapshot files (topic tạo trước v2.8.0)
- Disabling tiered storage requires deletion of all enabled topics before broker-level disablement

> 📌 Chú ý trong ví dụ quick-start: họ đặt `segment.bytes=1048576` (1 MiB). Không phải ngẫu nhiên — **chỉ segment đã đóng mới được đẩy lên remote**, y như retention và compaction. Segment 1 GiB mặc định trên topic thử nghiệm thưa dữ liệu thì chẳng bao giờ có gì lên remote cả.
