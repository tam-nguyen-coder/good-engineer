# Kafka Connect REST API — tham chiếu vận hành đầy đủ

> **Nguồn (official):** https://docs.confluent.io/platform/current/connect/references/restapi.html
> **Tuần:** 6 — Kafka Connect operations · **Loại:** Confluent Platform Docs
> ⚠️ Nội dung dưới đây được crawl tự động (WebFetch, có rút gọn) ngày 2026-09-20 — luôn đối chiếu link gốc. Ví dụ `version` trong docs là bản CP cũ, không ảnh hưởng shape của response.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- REST chạy trên **8083**, mọi request/response là `application/json`. Gọi được vào **bất kỳ worker nào** — worker không phải leader sẽ **forward** request tới leader (đây là lý do `rest.advertised.*` phải đúng).
- `POST /connectors` nhận body **có bọc**: `{"name": ..., "config": {...}}`. `PUT /connectors/{n}/config` nhận body **phẳng** (chỉ phần config) và là **upsert**: 201 khi tạo mới, 200 khi cập nhật. Nhầm hai shape này là lỗi 400/422 kinh điển.
- `GET /connectors/{n}/status` là **lệnh chẩn đoán số 1**: trả `connector.state`, `worker_id`, và mảng `tasks[]` gồm `id`, `state`, `worker_id`, và **`trace`** (stack trace) khi task FAILED.
- **Task FAILED không tự khởi động lại và không gây rebalance.** Phải gọi `POST /connectors/{n}/restart?includeTasks=true&onlyFailed=true`. Không có `includeTasks=true` thì chỉ restart **đối tượng connector**, task vẫn FAILED.
- Mã trả về của restart: **200** (chỉ connector) · **202** (có task được restart) · **204** · **404** không có connector · **409** đang rebalance.
- **409 Conflict** trả về bất cứ khi nào group đang rebalance — retry sau vài giây là hành vi đúng, không phải lỗi cấu hình.
- `pause` = giữ task, ngừng poll/put (bất đồng bộ, task chuyển PAUSED **không đồng thời**). `stop` = **huỷ hẳn task**, giữ config và offset. `resume` đưa cả hai về RUNNING.
- **Offset (KIP-875):** `GET /connectors/{n}/offsets` đọc được cả source lẫn sink. `PATCH` và `DELETE` **bắt buộc connector ở trạng thái STOPPED**. `PATCH` với `"offset": null` = xoá offset của partition đó.
- Shape offset của **sink** luôn là `{"partition":{"kafka_topic":…,"kafka_partition":…},"offset":{"kafka_offset":…}}`; của **source** là cặp key/value **do connector tự định nghĩa**.
- `GET /connector-plugins` mặc định `connectorsOnly=true`; thêm `?connectorsOnly=false` để thấy cả converter/transformation/predicate. `PUT /connector-plugins/{class}/config/validate` kiểm config **trước khi** tạo connector (trả `error_count` và lỗi từng field).
- `GET /connectors?expand=status&expand=info` — một lần gọi lấy trạng thái **toàn bộ** connector, dùng cho dashboard/alert thay vì loop từng cái.
- Connect **che** field password/sensitive bằng dấu `*` trong mọi response REST.

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Overview

"Since Kafka Connect is intended to be run as a service, it also supports a REST API for managing connectors. By default, this service runs on port `8083`."

### GET /

```json
{
  "version": "5.5.0",
  "commit": "e5741b90cde98052",
  "kafka_cluster_id": "I4ZmrWqfT2e-upky_4fdPA"
}
```

### GET /connectors

Query parameters:

- `?expand=status` – returns connector and task state information
- `?expand=info` – returns configuration and metadata
- Both can be combined: `?expand=status&expand=info`

```json
["my-jdbc-source", "my-hdfs-sink"]
```

### POST /connectors

Request:

```json
{
  "name": "hdfs-sink-connector",
  "config": {
    "connector.class": "io.confluent.connect.hdfs.HdfsSinkConnector",
    "tasks.max": "10",
    "topics": "test-topic"
  }
}
```

Response `201 Created`:

```json
{
  "name": "hdfs-sink-connector",
  "config": { "...": "..." },
  "tasks": [
    {"connector": "hdfs-sink-connector", "task": 1},
    {"connector": "hdfs-sink-connector", "task": 2}
  ]
}
```

### GET /connectors/{name} · GET /connectors/{name}/config

`GET /connectors/{name}` returns name, config and active tasks. `GET /connectors/{name}/config` returns the configuration map only:

```json
{
  "connector.class": "io.confluent.connect.hdfs.HdfsSinkConnector",
  "tasks.max": "10",
  "topics": "test-topic"
}
```

### PUT /connectors/{name}/config

Creates or updates. The payload is **not** wrapped in `{"config": {}}`. "Return `409 (Conflict)` if rebalance is in process."

### GET /connectors/{name}/status

```json
{
  "name": "hdfs-sink-connector",
  "connector": {
    "state": "RUNNING",
    "worker_id": "fakehost:8083"
  },
  "tasks": [
    {
      "id": 0,
      "state": "RUNNING",
      "worker_id": "fakehost:8083"
    },
    {
      "id": 1,
      "state": "FAILED",
      "worker_id": "fakehost:8083",
      "trace": "org.apache.kafka.common.errors.RecordTooLargeException\n"
    }
  ]
}
```

### POST /connectors/{name}/restart

Query parameters:

- `includeTasks=<true|false>` (default: **false**) – restart tasks in addition to the connector
- `onlyFailed=<true|false>` (default: **false**) – restart only failed instances

Response codes:

- `200 OK` – only the connector restarted (`includeTasks=false`, `onlyFailed=false`)
- `202 ACCEPTED` – failed or running instances restarted (`includeTasks=true` or `onlyFailed=true`)
- `204 NO CONTENT` – operation succeeded, no content
- `404 NOT FOUND` – connector doesn't exist
- `409 CONFLICT` – rebalance in progress

Example 202 body:

```json
{
  "name": "my-connector",
  "connector": {"state": "RUNNING", "worker_id": "fakehost1:8083"},
  "tasks": [
    {"id": 0, "state": "RUNNING", "worker_id": "fakehost2:8083"},
    {"id": 1, "state": "RESTARTING", "worker_id": "fakehost3:8083"}
  ]
}
```

### GET /connectors/{name}/tasks · GET /connectors/{name}/tasks/{taskId}/status · POST /connectors/{name}/tasks/{taskId}/restart

```json
[
  {
    "id": {"connector": "hdfs-sink-connector", "task": 0},
    "config": {
      "task.class": "io.confluent.connect.hdfs.HdfsSinkTask",
      "topics": "test-topic"
    }
  }
]
```

```json
{"state": "RUNNING", "id": 1, "worker_id": "192.168.86.101:8083"}
```

`POST /connectors/{name}/tasks/{taskId}/restart` restarts an individual task and returns `200 OK` with no content.

### PUT /connectors/{name}/pause · /resume · /stop

- **pause** — "Pause the connector and its tasks, which stops message processing until the connector is resumed. This call asynchronous and the tasks will not transition to `PAUSED` state at the same time." → `202 Accepted`
- **resume** — resume a paused connector or do nothing if it is not paused → `202 Accepted`
- **stop** — "Stops the connector but does not delete the connector. All tasks for the connector are shut down completely." → `202 Accepted`

### DELETE /connectors/{name}

Deletes the connector and halts all of its tasks → `204 No Content`.

### GET /connectors/{name}/topics · PUT /connectors/{name}/topics/reset

```json
{
  "hdfs-sink-connector": {
    "topics": ["test-topic-1", "test-topic-2", "test-topic-3"]
  }
}
```

`PUT /connectors/{name}/topics/reset` resets the tracked topic set → `200 OK`.

### GET /connectors/{connector}/offsets

Source connector response:

```json
{
  "offsets": [
    {
      "partition": { "…": "connector-defined source partition" },
      "offset": { "…": "connector-defined source offset" }
    }
  ]
}
```

Sink connector response:

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

"Note that the connector must exist and be in the stopped state."

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

Setting an offset to `null` resets that partition's offset.

### DELETE /connectors/{connector}/offsets

Resets all offsets for a connector. The connector must be stopped. Possible outcomes:

- `200 OK`, connector implements `alterOffsets` and succeeded: `{"message": "The offsets for this connector have been reset successfully"}`
- `200 OK`, framework-managed offsets only: `{"message": "The framework-managed offsets… have been reset successfully. However, if this connector manages offsets externally…"}`
- `500`, failure (consumer group deletion, zombie fencing, …): `{"error_code": 500, "message": "Exception message here"}`

### GET /connector-plugins/

Query parameter `?connectorsOnly=<true|false>` (default **true**).

```json
[
  {"class": "io.confluent.connect.hdfs.HdfsSinkConnector", "type": "sink", "version": "10.2.1"},
  {"class": "io.confluent.connect.jdbc.JdbcSourceConnector", "type": "source", "version": "10.6.4"}
]
```

### PUT /connector-plugins/{name}/config/validate

```json
{
  "name": "FileStreamSinkConnector",
  "error_count": 1,
  "groups": ["Common"],
  "configs": [
    {
      "definition": {"name": "file", "type": "STRING", "required": true, "documentation": "Destination filename."},
      "value": {"name": "file", "value": null, "errors": ["Missing required configuration \"file\" which has no default value."]}
    }
  ]
}
```

### Connector & task states

**Connector states:** `RUNNING` (actively processing) · `FAILED` (encountered an error) · `PAUSED` (processing stopped by user) · `RESTARTING` (restart in progress). Connect 3.5+ adds `STOPPED`, and `UNASSIGNED` appears while a connector/task is not yet assigned to a worker.

**Task states:** `RUNNING` · `FAILED` · `PAUSED` · `RESTARTING` (plus `UNASSIGNED`).

### Error handling

"Clients should check the HTTP status, especially before attempting to parse and use response entities."

```json
{
  "error_code": 422,
  "message": "config may not be empty"
}
```

- "Connect masks sensitive and password-type configuration fields in REST API responses with asterisks (`*`) to prevent data exposure."
- HTTP 409 is returned "while the worker group rebalance is in process as the leader may change during rebalance."
