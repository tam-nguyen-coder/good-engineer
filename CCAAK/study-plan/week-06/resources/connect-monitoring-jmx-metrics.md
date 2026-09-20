# Kafka Connect — JMX metrics cho người vận hành (Apache Kafka 4.3)

> **Nguồn (official):** https://kafka.apache.org/43/operations/monitoring/ (mục *Connect Monitoring*)
> **Tuần:** 6 — Kafka Connect operations · **Loại:** Apache Kafka Docs — Operations/Monitoring
> ⚠️ Nội dung dưới đây được crawl tự động (WebFetch) ngày 2026-09-20 — luôn đối chiếu link gốc.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- **6 nhóm MBean** cần thuộc: `connect-worker-metrics` (mức worker) · `connect-worker-rebalance-metrics` (mức cluster) · `connector-metrics` (mức connector) · `connector-task-metrics` (mức task, chung) · `sink-task-metrics` / `source-task-metrics` (mức task, theo loại) · `task-error-metrics` (lỗi & DLQ).
- `connector-count` và `task-count` là **số connector/task đang chạy trên CHÍNH worker này**, không phải toàn cluster. Sau khi kill một worker, hai số này ở worker còn lại **tăng lên** — đó là bằng chứng rebalance đã xảy ra.
- `connector-metrics → status` nhận các giá trị *"unassigned, running, paused, **stopped**, failed, restarting"*. `connector-task-metrics → status` nhận *"unassigned, running, paused, failed, restarting"* — **không có `stopped`**, vì `STOPPED` huỷ hẳn task nên task không còn để báo trạng thái. Đây là chi tiết phân biệt connector-level và task-level.
- Alert **PHẢI có**: bất kỳ connector/task nào ở `failed`, `rebalancing = true` kéo dài, `offset-commit-failure-percentage` > 0, `deadletterqueue-produce-failures` > 0.
- Nhịp độ dữ liệu: source dùng `source-record-poll-rate` (trước transform) và `source-record-write-rate` (sau transform, đã ghi Kafka); sink dùng `sink-record-read-rate` (trước transform) và `sink-record-send-rate` (sau transform, đã đưa vào `put()`). **Poll/read cao mà write/send = 0 → SMT `Filter` đang loại hết record**, không phải connector chết.
- `partition-count` (sink-task-metrics) = số partition **task này** đang giữ. Đây là metric chứng minh **task dư nằm không**: task thứ 4,5,6 trên topic 3 partition có `partition-count = 0` mà vẫn `status = running`.
- `sink-record-active-count` = record đã đọc từ Kafka nhưng **chưa flush/commit xong** → tăng đều = hệ đích chậm hơn Kafka.
- `sink-record-lag-max` = lag lớn nhất của task so với position của consumer — đo lag **không cần** `kafka-consumer-groups.sh`.
- `task-error-metrics` là bộ đếm DLQ: `deadletterqueue-produce-requests` (số lần **thử** ghi DLQ) vs `deadletterqueue-produce-failures` (số lần **ghi hỏng**). `total-record-errors` vs `total-record-failures` vs `total-records-skipped` phân biệt "có lỗi", "lỗi làm task chết" và "bỏ qua nhờ `errors.tolerance=all`".
- `time-since-last-rebalance-ms` reset về 0 mỗi lần rebalance xong → đồ thị răng cưa liên tục = cluster đang **rebalance loop** (thường do worker OOM/restart lặp hoặc `session.timeout.ms` 10 s quá ngắn cho môi trường mạng kém).
- `leader-name` và `epoch` cho biết **worker nào đang là leader** và generation hiện tại — dùng khi nghi ngờ split brain.

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Connect Worker Metrics

**MBean:** `kafka.connect:type=connect-worker-metrics`

| Attribute | Description |
|---|---|
| `connector-count` | "The number of connectors run in this worker." |
| `connector-startup-attempts-total` | "The total number of connector startups that this worker has attempted." |
| `connector-startup-failure-percentage` | "The average percentage of this worker's connectors starts that failed." |
| `connector-startup-failure-total` | "The total number of connector starts that failed." |
| `connector-startup-success-percentage` | "The average percentage of this worker's connectors starts that succeeded." |
| `connector-startup-success-total` | "The total number of connector starts that succeeded." |
| `task-count` | "The number of tasks run in this worker." |
| `task-startup-attempts-total` | "The total number of task startups that this worker has attempted." |
| `task-startup-failure-percentage` | "The average percentage of this worker's tasks starts that failed." |
| `task-startup-failure-total` | "The total number of task starts that failed." |
| `task-startup-success-percentage` | "The average percentage of this worker's tasks starts that succeeded." |
| `task-startup-success-total` | "The total number of task starts that succeeded." |

### Connect Worker Rebalance Metrics

**MBean:** `kafka.connect:type=connect-worker-rebalance-metrics`

| Attribute | Description |
|---|---|
| `completed-rebalances-total` | "The total number of rebalances completed by this worker." |
| `connect-protocol` | "The Connect protocol used by this cluster" |
| `epoch` | "The epoch or generation number of this worker." |
| `leader-name` | "The name of the group leader." |
| `rebalance-avg-time-ms` | "The average time in milliseconds spent by this worker to rebalance." |
| `rebalance-max-time-ms` | "The maximum time in milliseconds spent by this worker to rebalance." |
| `rebalancing` | "Whether this worker is currently rebalancing." |
| `time-since-last-rebalance-ms` | "The time in milliseconds since this worker completed the most recent rebalance." |

### Connector Metrics

**MBean:** `kafka.connect:type=connector-metrics,connector="{connector}"`

| Attribute | Description |
|---|---|
| `connector-class` | "The name of the connector class." |
| `connector-type` | "The type of the connector. One of 'source' or 'sink'." |
| `connector-version` | "The version of the connector class, as reported by the connector." |
| `status` | "The status of the connector. One of 'unassigned', 'running', 'paused', 'stopped', 'failed', or 'restarting'." |

### Connector Task Metrics

**MBean:** `kafka.connect:type=connector-task-metrics,connector="{connector}",task="{task}"`

| Attribute | Description |
|---|---|
| `batch-size-avg` | "The average number of records in the batches the task has processed so far." |
| `batch-size-max` | "The number of records in the largest batch the task has processed so far." |
| `connector-class` | "The name of the connector class." |
| `connector-type` | "The type of the connector. One of 'source' or 'sink'." |
| `connector-version` | "The version of the connector class, as reported by the connector." |
| `offset-commit-avg-time-ms` | "The average time in milliseconds taken by this task to commit offsets." |
| `offset-commit-failure-percentage` | "The average percentage of this task's offset commit attempts that failed." |
| `offset-commit-max-time-ms` | "The maximum time in milliseconds taken by this task to commit offsets." |
| `offset-commit-success-percentage` | "The average percentage of this task's offset commit attempts that succeeded." |
| `pause-ratio` | "The fraction of time this task has spent in the pause state." |
| `running-ratio` | "The fraction of time this task has spent in the running state." |
| `status` | "The status of the connector task. One of 'unassigned', 'running', 'paused', 'failed', or 'restarting'." |

### Sink Task Metrics

**MBean:** `kafka.connect:type=sink-task-metrics,connector="{connector}",task="{task}"`

| Attribute | Description |
|---|---|
| `offset-commit-completion-rate` | "The average per-second number of offset commit completions that were completed successfully." |
| `offset-commit-completion-total` | "The total number of offset commit completions that were completed successfully." |
| `offset-commit-seq-no` | "The current sequence number for offset commits." |
| `offset-commit-skip-rate` | "The average per-second number of offset commit completions that were received too late and skipped/ignored." |
| `offset-commit-skip-total` | "The total number of offset commit completions that were received too late and skipped/ignored." |
| `partition-count` | "The number of topic partitions assigned to this task belonging to the named sink connector in this worker." |
| `put-batch-avg-time-ms` | "The average time taken by this task to put a batch of sinks records." |
| `put-batch-max-time-ms` | "The maximum time taken by this task to put a batch of sinks records." |
| `sink-record-active-count` | "The number of records that have been read from Kafka but not yet completely committed/flushed/acknowledged by the sink task." |
| `sink-record-active-count-avg` | "The average number of records that have been read from Kafka but not yet completely committed/flushed/acknowledged by the sink task." |
| `sink-record-active-count-max` | "The maximum number of records that have been read from Kafka but not yet completely committed/flushed/acknowledged by the sink task." |
| `sink-record-lag-max` | "The maximum lag in terms of number of records that the sink task is behind the consumer's position for any topic partitions." |
| `sink-record-read-rate` | "The average per-second number of records read from Kafka for this task belonging to the named sink connector in this worker. **This is before transformations are applied.**" |
| `sink-record-read-total` | "The total number of records read from Kafka by this task belonging to the named sink connector in this worker, since the task was last restarted." |
| `sink-record-send-rate` | "The average per-second number of records output from the transformations and sent/put to this task belonging to the named sink connector in this worker. **This is after transformations are applied and excludes any records filtered out by the transformations.**" |
| `sink-record-send-total` | "The total number of records output from the transformations and sent/put to this task belonging to the named sink connector in this worker, since the task was last restarted." |

### Source Task Metrics

**MBean:** `kafka.connect:type=source-task-metrics,connector="{connector}",task="{task}"`

| Attribute | Description |
|---|---|
| `poll-batch-avg-time-ms` | "The average time in milliseconds taken by this task to poll for a batch of source records." |
| `poll-batch-max-time-ms` | "The maximum time in milliseconds taken by this task to poll for a batch of source records." |
| `source-record-active-count` | "The number of records that have been produced by this task but not yet completely written to Kafka." |
| `source-record-active-count-avg` | "The average number of records that have been produced by this task but not yet completely written to Kafka." |
| `source-record-active-count-max` | "The maximum number of records that have been produced by this task but not yet completely written to Kafka." |
| `source-record-poll-rate` | "The average per-second number of records produced/polled (before transformation) by this task belonging to the named source connector in this worker." |
| `source-record-poll-total` | "The total number of records produced/polled (before transformation) by this task belonging to the named source connector in this worker." |
| `source-record-write-rate` | "The average per-second number of records written to Kafka for this task belonging to the named source connector in this worker, since the task was last restarted." |
| `source-record-write-total` | "The number of records output written to Kafka for this task belonging to the named source connector in this worker, since the task was last restarted." |

### Task Error Metrics

**MBean:** `kafka.connect:type=task-error-metrics,connector="{connector}",task="{task}"`

| Attribute | Description |
|---|---|
| `deadletterqueue-produce-failures` | "The number of failed writes to the dead letter queue." |
| `deadletterqueue-produce-requests` | "The number of attempted writes to the dead letter queue." |
| `last-error-timestamp` | "The epoch timestamp when this task last encountered an error." |
| `total-errors-logged` | "The number of errors that were logged." |
| `total-record-errors` | "The number of record processing errors in this task." |
| `total-record-failures` | "The number of record processing failures in this task." |
| `total-records-skipped` | "The number of records skipped due to errors." |
| `total-retries` | "The number of operations retried." |
