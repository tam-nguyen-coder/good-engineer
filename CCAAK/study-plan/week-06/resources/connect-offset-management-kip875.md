# Quản lý offset của connector — KIP-875, STOPPED state, source vs sink

> **Nguồn (official):** https://cwiki.apache.org/confluence/display/KAFKA/KIP-875%3A+First-class+offsets+support+in+Kafka+Connect (mirror: https://kafka-options-explorer.conduktor.io/kip/875/) · https://docs.confluent.io/platform/current/connect/references/restapi.html · https://kafka.apache.org/43/kafka-connect/user-guide/ · https://kafka.apache.org/43/generated/source_connector_config.html
> **Tuần:** 6 — Kafka Connect operations · **Loại:** KIP + Confluent Docs + Apache Kafka Docs
> ⚠️ **cwiki.apache.org chặn WebFetch.** Phần shape request/response và mã lỗi lấy **nguyên văn từ trang REST API của Confluent đã crawl được**; phần lịch sử version tổng hợp từ mirror KIP Explorer và kết quả tìm kiếm — đối chiếu link gốc trước ngày thi.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- **Hai thế giới offset hoàn toàn khác nhau**, và đây là nguồn câu hỏi nhiều nhất của domain Connect:
  - **Source connector** — offset là cặp key/value **do connector tự định nghĩa** (vd `{"filename":"/data/in.txt"}` → `{"position":1024}`), lưu trong internal topic **`connect-offsets`** (`offset.storage.topic`), commit theo `offset.flush.interval.ms` (**60000** mặc định). **Không** có consumer group.
  - **Sink connector** — mỗi task là **consumer** trong consumer group **`connect-<connector-name>`**; offset nằm trong **`__consumer_offsets`** như mọi consumer group khác. Reset được bằng `kafka-consumer-groups.sh`.
- **Bẫy vận hành số 1:** `DELETE /connectors/<name>` **không xoá offset**. Tạo lại connector **cùng tên** → source tiếp tục từ offset cũ, sink tiếp tục từ committed offset của group `connect-<name>`. Muốn chạy lại từ đầu phải xoá offset **một cách có chủ đích**.
- **KIP-875 Part 1 (Kafka 3.5):** thêm `GET /connectors/{name}/offsets` và trạng thái mới **`STOPPED`** cùng `PUT /connectors/{name}/stop`.
- **KIP-875 Part 2 (Kafka 3.6):** thêm `PATCH /connectors/{name}/offsets` (sửa offset) và `DELETE /connectors/{name}/offsets` (reset toàn bộ).
- **`PATCH` và `DELETE` bắt buộc connector ở trạng thái `STOPPED`.** `PAUSED` là **chưa đủ** — pause giữ task sống, stop mới huỷ task và giải phóng consumer group. Gọi khi đang RUNNING/PAUSED sẽ bị từ chối.
- Quy trình reset offset chuẩn bằng REST: `PUT /stop` → `DELETE /offsets` (hoặc `PATCH`) → `PUT /resume`.
- `PATCH` với `"offset": null` cho một partition = **xoá offset của partition đó** (không phải đặt về 0).
- Với sink, `DELETE /offsets` thực chất **xoá consumer group `connect-<name>`** ở phía broker → nếu group còn member (connector chưa STOPPED) thì thao tác trả **500**.
- Cách "cổ điển" vẫn đúng và vẫn được hỏi: reset sink bằng `kafka-consumer-groups.sh --group connect-<name> --reset-offsets --to-earliest --topic <t> --execute` — với hai điều kiện quen thuộc: group phải **inactive** và phải có **`--execute`** (mặc định là dry-run).
- **Không nên** sửa tay bằng cách produce record vào `connect-offsets`: topic này compacted, key do connector định nghĩa, gõ sai một byte là connector đọc lại từ đầu hoặc nhảy cóc mất dữ liệu. REST API tồn tại chính là để thay thế thủ thuật đó.
- Source connector có thể dùng **offset topic riêng** cho một connector duy nhất: `offsets.storage.topic` ở mức connector (mặc định `null`, dùng chung `connect-offsets` của worker). Hữu ích khi tách quyền hoặc khi migrate connector giữa các Connect cluster.

---

## 📄 Nội dung (trích từ tài liệu gốc)

### GET /connectors/{connector}/offsets

Source connector response — cặp partition/offset **do connector định nghĩa**:

```json
{
  "offsets": [
    {
      "partition": { "…": "Connector-defined source partition" },
      "offset": { "…": "Connector-defined source offset" }
    }
  ]
}
```

Sink connector response — luôn là toạ độ Kafka:

```json
{
  "offsets": [
    {
      "partition": {
        "kafka_topic": "topic-name",
        "kafka_partition": 0
      },
      "offset": {"kafka_offset": 100}
    }
  ]
}
```

### PATCH /connectors/{connector}/offsets

> "Note that the connector must exist and be in the stopped state."

```json
{
  "offsets": [
    {
      "partition": {"kafka_topic": "T", "kafka_partition": 3},
      "offset": null
    }
  ]
}
```

"Setting offset to `null` resets that partition's offset."

### DELETE /connectors/{connector}/offsets

"Reset all offsets for a connector. Connector must be stopped." → `200 OK`.

Three documented outcomes:

- **Case 1 (200 OK)** — connector implements `alterOffsets` and succeeds:
  ```json
  {"message": "The offsets for this connector have been reset successfully"}
  ```
- **Case 2 (200 OK)** — framework-managed offsets only:
  ```json
  {"message": "The framework-managed offsets… have been reset successfully. However, if this connector manages offsets externally…"}
  ```
- **Case 3 (500 Error)** — failure (consumer group deletion, zombie fencing, etc.):
  ```json
  {"error_code": 500, "message": "Exception message here"}
  ```

### PUT /connectors/{connector}/stop

"Stops the connector but does not delete the connector. All tasks for the connector are shut down completely." → `202 Accepted`.

So sánh với pause: "Pause the connector and its tasks, which stops message processing until the connector is resumed. This call asynchronous and the tasks will not transition to `PAUSED` state at the same time."

### Timeline của KIP-875

*(Tổng hợp từ mirror KIP Explorer và trang KIP — cwiki không crawl được.)*

| Kafka | Nội dung |
|---|---|
| **3.5** | KIP-875 Part 1: `GET /connectors/{name}/offsets`, trạng thái **`STOPPED`**, `PUT /connectors/{name}/stop` |
| **3.6** | KIP-875 Part 2: `PATCH /connectors/{name}/offsets`, `DELETE /connectors/{name}/offsets` |
| 3.9 | KIP-980: tạo connector thẳng ở trạng thái `STOPPED` (`initial.state`) |
| 3.9 | KIP-995: đặt offset khởi điểm ngay khi tạo connector (`offsets` trong body `POST /connectors`) |

Mục tiêu của KIP: cho phép quản trị viên **đọc, sửa và reset offset của connector qua REST**, thay vì phải thao tác trực tiếp lên internal topic `connect-offsets` hoặc lên consumer group ở phía broker.

### Source connector — offset topic riêng

Từ `source_connector_config.html` (Kafka 4.3):

| Configuration | Type | Default | Valid Values | Description |
|---|---|---|---|---|
| `offsets.storage.topic` | string | null | non-empty string | "Name of a separate offsets topic to use for this connector" |

### Worker config liên quan

| Configuration | Default | Description |
|---|---|---|
| `offset.storage.topic` | (none, bắt buộc) | "The name of the Kafka topic where source connector offsets are stored" |
| `offset.storage.partitions` | 25 | Số partition của offset topic |
| `offset.storage.replication.factor` | 3 | RF của offset topic |
| `offset.flush.interval.ms` | 60000 (1 min) | "Interval at which to try committing offsets for tasks." |
| `offset.flush.timeout.ms` | 5000 (5 sec) | "Maximum milliseconds to wait for records to flush and offsets to commit" |
| `offset.storage.file.filename` | — | **Chỉ standalone**: file local lưu offset của source connector |
