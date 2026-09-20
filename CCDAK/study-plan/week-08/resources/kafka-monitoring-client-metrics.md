# Apache Kafka — Monitoring: Producer / Consumer / Connect / Streams Metrics

> **Nguồn (official):** https://kafka.apache.org/43/operations/monitoring/ (mục Producer monitoring, Consumer monitoring, Connect Monitoring, Streams Monitoring)
> **Tuần:** 8 — Observability & Operations · **Loại:** Apache Kafka Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua HTTP + chuyển HTML → Markdown, có rút gọn) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- **Producer** (`kafka.producer:type=producer-metrics,client-id=...`): `record-send-rate`, `record-error-rate` (phải 0), `record-retry-rate`, `request-latency-avg/max`, `batch-size-avg` (so với `batch.size`=16 KB → batching có hiệu quả không), `records-per-request-avg`, `compression-rate-avg` (tỉ lệ nén/không nén — càng **nhỏ** càng nén tốt), `record-queue-time-avg` (thời gian batch chờ trong accumulator ≈ `linger.ms`), `requests-in-flight`.
- Buffer producer: `buffer-available-bytes` giảm về 0 + `bufferpool-wait-time-ns-total`/`bufferpool-wait-ratio` tăng + `waiting-threads` > 0 → buffer 32 MB đầy, `send()` sẽ block tới `max.block.ms`=60 s rồi ném `TimeoutException`. `buffer-exhausted-rate` = record bị drop do hết buffer.
- `produce-throttle-time-avg` > 0 = broker đang **throttle vì quota** (`producer_byte_rate`); tương tự consumer có `fetch-throttle-time-avg`.
- **Consumer** (`kafka.consumer:type=consumer-fetch-manager-metrics`): `records-lag-max` (lag lớn nhất, **tính theo current position, không phải committed offset**), `records-lag` per partition, `records-lead-min` (khoảng cách tới **log start offset** — gần 0 = sắp bị retention xoá → mất data, KIP-92), `fetch-latency-avg`, `fetch-rate`, `fetch-size-avg`, `records-consumed-rate`, `bytes-consumed-rate`.
- Consumer coordinator (`consumer-coordinator-metrics`): `commit-latency-avg`, `commit-rate`, `rebalance-latency-avg/max/total`, `rebalance-total`, `rebalance-rate-per-hour`, `failed-rebalance-total`, `last-rebalance-seconds-ago`, `join-rate`/`sync-rate`, `heartbeat-rate`, `assigned-partitions`, `partitions-revoked-latency-avg`.
- Consumer poll loop (`consumer-metrics`): `time-between-poll-avg/max` (so với `max.poll.interval.ms`=300 s — tiến gần là sắp bị kick), `last-poll-seconds-ago`, `poll-idle-ratio-avg` (gần 1 = consumer chờ dữ liệu; gần 0 = user code xử lý chậm).
- **Connect**: worker `connector-count`, `task-count`, `connector-startup-failure-total`; per connector `status` (`running/paused/stopped/failed/unassigned/restarting`); task `status`, `batch-size-avg`, `offset-commit-failure-percentage`; source `source-record-poll-rate`, `source-record-write-rate`, `source-record-active-count`; sink `sink-record-read-rate`, `sink-record-send-rate`, `sink-record-lag-max`, `put-batch-avg-time-ms`; error `deadletterqueue-produce-requests`, `deadletterqueue-produce-failures`, `total-record-errors`, `total-record-failures`, `total-records-skipped`, `total-retries`.
- **Streams**: 4 tầng client → thread → task → processor node/state store; `metrics.recording.level` = `info` (mặc định) / `debug` / `trace`. Thread: `process-rate`, `poll-rate`, `commit-latency-avg`, `punctuate-rate`. Task: `record-lateness-avg/max` (stream time − record timestamp), `dropped-records-total` (record bị drop vì quá grace / null key), `active-process-ratio`, `enforced-processing-rate`.

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Producer monitoring

The following metrics are available on producer instances.

| Metric/Attribute name | Description | Mbean name |
|---|---|---|
| waiting-threads | The number of user threads blocked waiting for buffer memory to enqueue their records. | `kafka.producer:type=producer-metrics,client-id=([-.\w]+)` |
| buffer-total-bytes | The maximum amount of buffer memory the client can use (whether or not it is currently used). | `kafka.producer:type=producer-metrics,client-id=([-.\w]+)` |
| buffer-available-bytes | The total amount of buffer memory that is not being used (either unallocated or in the free list). | `kafka.producer:type=producer-metrics,client-id=([-.\w]+)` |
| buffer-exhausted-rate | The average per-second number of record sends that are dropped due to buffer exhaustion | `kafka.producer:type=producer-metrics,client-id=([-.\w]+)` |
| bufferpool-wait-ratio | The fraction of time an appender waits for space allocation. | `kafka.producer:type=producer-metrics,client-id=([-.\w]+)` |
| bufferpool-wait-time-ns-total | The total time an appender waits for space allocation in nanoseconds. | `kafka.producer:type=producer-metrics,client-id=([-.\w]+)` |
| flush-time-ns-total | The total time the Producer spent in Producer.flush in nanoseconds. | `kafka.producer:type=producer-metrics,client-id=([-.\w]+)` |
| txn-init-time-ns-total / txn-begin-time-ns-total / txn-commit-time-ns-total / txn-abort-time-ns-total | The total time the Producer spent initializing / beginning / committing / aborting transactions in nanoseconds (for EOS). | `kafka.producer:type=producer-metrics,client-id=([-.\w]+)` |
| metadata-wait-time-ns-total | the total time in nanoseconds that has spent waiting for metadata from the Kafka broker | `kafka.producer:type=producer-metrics,client-id=([-.\w]+)` |

#### Producer Sender Metrics

| Metric/Attribute name | Description | Mbean name |
|---|---|---|
| batch-size-avg | The average number of bytes sent per partition per-request. | `kafka.producer:type=producer-metrics,client-id="{client-id}"` |
| batch-size-max | The max number of bytes sent per partition per-request. | `kafka.producer:type=producer-metrics,client-id="{client-id}"` |
| batch-split-rate | The average number of batch splits per second | `kafka.producer:type=producer-metrics,client-id="{client-id}"` |
| compression-rate-avg | The average compression rate of record batches, defined as the average ratio of the compressed batch size over the uncompressed size. | `kafka.producer:type=producer-metrics,client-id="{client-id}"` |
| metadata-age | The age in seconds of the current producer metadata being used. | `kafka.producer:type=producer-metrics,client-id="{client-id}"` |
| produce-throttle-time-avg | The average time in ms a request was throttled by a broker | `kafka.producer:type=producer-metrics,client-id="{client-id}"` |
| produce-throttle-time-max | The maximum time in ms a request was throttled by a broker | `kafka.producer:type=producer-metrics,client-id="{client-id}"` |
| record-error-rate | The average per-second number of record sends that resulted in errors | `kafka.producer:type=producer-metrics,client-id="{client-id}"` |
| record-error-total | The total number of record sends that resulted in errors | `kafka.producer:type=producer-metrics,client-id="{client-id}"` |
| record-queue-time-avg | The average time in ms record batches spent in the send buffer. | `kafka.producer:type=producer-metrics,client-id="{client-id}"` |
| record-queue-time-max | The maximum time in ms record batches spent in the send buffer. | `kafka.producer:type=producer-metrics,client-id="{client-id}"` |
| record-retry-rate | The average per-second number of retried record sends | `kafka.producer:type=producer-metrics,client-id="{client-id}"` |
| record-send-rate | The average number of records sent per second. | `kafka.producer:type=producer-metrics,client-id="{client-id}"` |
| record-send-total | The total number of records sent. | `kafka.producer:type=producer-metrics,client-id="{client-id}"` |
| record-size-avg / record-size-max | The average / maximum record size | `kafka.producer:type=producer-metrics,client-id="{client-id}"` |
| records-per-request-avg | The average number of records per request. | `kafka.producer:type=producer-metrics,client-id="{client-id}"` |
| request-latency-avg | The average request latency in ms | `kafka.producer:type=producer-metrics,client-id="{client-id}"` |
| request-latency-max | The maximum request latency in ms | `kafka.producer:type=producer-metrics,client-id="{client-id}"` |
| requests-in-flight | The current number of in-flight requests awaiting a response. | `kafka.producer:type=producer-metrics,client-id="{client-id}"` |
| byte-rate | The average number of bytes sent per second for a topic. | `kafka.producer:type=producer-topic-metrics,client-id="{client-id}",topic="{topic}"` |
| compression-rate | The average compression rate of record batches for a topic. | `kafka.producer:type=producer-topic-metrics,client-id="{client-id}",topic="{topic}"` |
| record-error-rate / record-retry-rate / record-send-rate (per topic) | Per-topic versions of the sender metrics. | `kafka.producer:type=producer-topic-metrics,client-id="{client-id}",topic="{topic}"` |

### Consumer monitoring

The following metrics are available on consumer instances.

| Metric/Attribute name | Description | Mbean name |
|---|---|---|
| time-between-poll-avg | The average delay between invocations of poll(). | `kafka.consumer:type=consumer-metrics,client-id=([-.\w]+)` |
| time-between-poll-max | The max delay between invocations of poll(). | `kafka.consumer:type=consumer-metrics,client-id=([-.\w]+)` |
| last-poll-seconds-ago | The number of seconds since the last poll() invocation. | `kafka.consumer:type=consumer-metrics,client-id=([-.\w]+)` |
| poll-idle-ratio-avg | The average fraction of time the consumer's poll() is idle as opposed to waiting for the user code to process records. | `kafka.consumer:type=consumer-metrics,client-id=([-.\w]+)` |
| committed-time-ns-total | The total time the Consumer spent in committed in nanoseconds. | `kafka.consumer:type=consumer-metrics,client-id=([-.\w]+)` |
| commit-sync-time-ns-total | The total time the Consumer spent committing offsets in nanoseconds (for AOS). | `kafka.consumer:type=consumer-metrics,client-id=([-.\w]+)` |

#### Consumer Group Metrics

| Metric/Attribute name | Description | Mbean name |
|---|---|---|
| commit-latency-avg | The average time taken for a commit request | `kafka.consumer:type=consumer-coordinator-metrics,client-id=([-.\w]+)` |
| commit-latency-max | The max time taken for a commit request | `kafka.consumer:type=consumer-coordinator-metrics,client-id=([-.\w]+)` |
| commit-rate | The number of commit calls per second | `kafka.consumer:type=consumer-coordinator-metrics,client-id=([-.\w]+)` |
| assigned-partitions | The number of partitions currently assigned to this consumer | `kafka.consumer:type=consumer-coordinator-metrics,client-id=([-.\w]+)` |
| heartbeat-response-time-max | The max time taken to receive a response to a heartbeat request | `kafka.consumer:type=consumer-coordinator-metrics,client-id=([-.\w]+)` |
| heartbeat-rate | The average number of heartbeats per second | `kafka.consumer:type=consumer-coordinator-metrics,client-id=([-.\w]+)` |
| join-time-avg / join-time-max | The average / max time taken for a group rejoin | `kafka.consumer:type=consumer-coordinator-metrics,client-id=([-.\w]+)` |
| join-rate | The number of group joins per second | `kafka.consumer:type=consumer-coordinator-metrics,client-id=([-.\w]+)` |
| sync-time-avg / sync-time-max | The average / max time taken for a group sync | `kafka.consumer:type=consumer-coordinator-metrics,client-id=([-.\w]+)` |
| sync-rate | The number of group syncs per second | `kafka.consumer:type=consumer-coordinator-metrics,client-id=([-.\w]+)` |
| rebalance-latency-avg | The average time taken for a group rebalance | `kafka.consumer:type=consumer-coordinator-metrics,client-id=([-.\w]+)` |
| rebalance-latency-max | The max time taken for a group rebalance | `kafka.consumer:type=consumer-coordinator-metrics,client-id=([-.\w]+)` |
| rebalance-latency-total | The total time taken for group rebalances so far | `kafka.consumer:type=consumer-coordinator-metrics,client-id=([-.\w]+)` |
| rebalance-total | The total number of group rebalances participated | `kafka.consumer:type=consumer-coordinator-metrics,client-id=([-.\w]+)` |
| rebalance-rate-per-hour | The number of group rebalance participated per hour | `kafka.consumer:type=consumer-coordinator-metrics,client-id=([-.\w]+)` |
| failed-rebalance-total | The total number of failed group rebalances | `kafka.consumer:type=consumer-coordinator-metrics,client-id=([-.\w]+)` |
| failed-rebalance-rate-per-hour | The number of failed group rebalance event per hour | `kafka.consumer:type=consumer-coordinator-metrics,client-id=([-.\w]+)` |
| last-rebalance-seconds-ago | The number of seconds since the last rebalance event | `kafka.consumer:type=consumer-coordinator-metrics,client-id=([-.\w]+)` |
| last-heartbeat-seconds-ago | The number of seconds since the last controller heartbeat | `kafka.consumer:type=consumer-coordinator-metrics,client-id=([-.\w]+)` |
| partitions-revoked-latency-avg / -max | The average / max time taken by the on-partitions-revoked rebalance listener callback | `kafka.consumer:type=consumer-coordinator-metrics,client-id=([-.\w]+)` |
| partitions-assigned-latency-avg / -max | The average / max time taken by the on-partitions-assigned rebalance listener callback | `kafka.consumer:type=consumer-coordinator-metrics,client-id=([-.\w]+)` |
| partitions-lost-latency-avg / -max | The average / max time taken by the on-partitions-lost rebalance listener callback | `kafka.consumer:type=consumer-coordinator-metrics,client-id=([-.\w]+)` |

#### Consumer Fetch Metrics

| Metric/Attribute name | Description | Mbean name |
|---|---|---|
| bytes-consumed-rate | The average number of bytes consumed per second | `kafka.consumer:type=consumer-fetch-manager-metrics,client-id="{client-id}"` |
| fetch-latency-avg | The average time taken for a fetch request. | `kafka.consumer:type=consumer-fetch-manager-metrics,client-id="{client-id}"` |
| fetch-latency-max | The max time taken for any fetch request. | `kafka.consumer:type=consumer-fetch-manager-metrics,client-id="{client-id}"` |
| fetch-rate | The number of fetch requests per second. | `kafka.consumer:type=consumer-fetch-manager-metrics,client-id="{client-id}"` |
| fetch-size-avg | The average number of bytes fetched per request | `kafka.consumer:type=consumer-fetch-manager-metrics,client-id="{client-id}"` |
| fetch-size-max | The maximum number of bytes fetched per request | `kafka.consumer:type=consumer-fetch-manager-metrics,client-id="{client-id}"` |
| fetch-throttle-time-avg | The average throttle time in ms | `kafka.consumer:type=consumer-fetch-manager-metrics,client-id="{client-id}"` |
| fetch-throttle-time-max | The maximum throttle time in ms | `kafka.consumer:type=consumer-fetch-manager-metrics,client-id="{client-id}"` |
| records-consumed-rate | The average number of records consumed per second | `kafka.consumer:type=consumer-fetch-manager-metrics,client-id="{client-id}"` |
| records-lag-max | The maximum lag in terms of number of records for any partition in this window. NOTE: This is based on current offset and not committed offset | `kafka.consumer:type=consumer-fetch-manager-metrics,client-id="{client-id}"` |
| records-lead-min | The minimum lead in terms of number of records for any partition in this window | `kafka.consumer:type=consumer-fetch-manager-metrics,client-id="{client-id}"` |
| records-per-request-avg | The average number of records in each request | `kafka.consumer:type=consumer-fetch-manager-metrics,client-id="{client-id}"` |
| preferred-read-replica | The current read replica for the partition, or -1 if reading from leader. | `kafka.consumer:type=consumer-fetch-manager-metrics,partition="{partition}",topic="{topic}",client-id="{client-id}"` |
| records-lag | The latest lag of the partition. | `kafka.consumer:type=consumer-fetch-manager-metrics,partition="{partition}",topic="{topic}",client-id="{client-id}"` |
| records-lag-avg / records-lag-max (per partition) | The average / max lag of the partition. | `kafka.consumer:type=consumer-fetch-manager-metrics,partition="{partition}",topic="{topic}",client-id="{client-id}"` |
| records-lead | The latest lead of the partition. | `kafka.consumer:type=consumer-fetch-manager-metrics,partition="{partition}",topic="{topic}",client-id="{client-id}"` |
| records-lead-avg / records-lead-min (per partition) | The average / min lead of the partition. | `kafka.consumer:type=consumer-fetch-manager-metrics,partition="{partition}",topic="{topic}",client-id="{client-id}"` |

### Connect Monitoring

A Connect worker process contains all the producer and consumer metrics as well as metrics specific to Connect. The worker process itself has a number of metrics, while each connector and task have additional metrics.

| Metric/Attribute name | Description | Mbean name |
|---|---|---|
| connector-count | The number of connectors run in this worker. | `kafka.connect:type=connect-worker-metrics` |
| connector-startup-failure-total | The total number of connector starts that failed. | `kafka.connect:type=connect-worker-metrics` |
| task-count | The number of tasks run in this worker. | `kafka.connect:type=connect-worker-metrics` |
| task-startup-failure-total | The total number of task starts that failed. | `kafka.connect:type=connect-worker-metrics` |
| connector-failed-task-count / connector-running-task-count / connector-paused-task-count / connector-unassigned-task-count | The number of failed / running / paused / unassigned tasks of the connector on the worker. | `kafka.connect:type=connect-worker-metrics,connector="{connector}"` |
| completed-rebalances-total | The total number of rebalances completed by this worker. | `kafka.connect:type=connect-worker-rebalance-metrics` |
| connect-protocol | The Connect protocol used by this cluster | `kafka.connect:type=connect-worker-rebalance-metrics` |
| rebalance-avg-time-ms / rebalance-max-time-ms | The average / maximum time in milliseconds spent by this worker to rebalance. | `kafka.connect:type=connect-worker-rebalance-metrics` |
| rebalancing | Whether this worker is currently rebalancing. | `kafka.connect:type=connect-worker-rebalance-metrics` |
| time-since-last-rebalance-ms | The time in milliseconds since this worker completed the most recent rebalance. | `kafka.connect:type=connect-worker-rebalance-metrics` |
| connector-type | The type of the connector. One of 'source' or 'sink'. | `kafka.connect:type=connector-metrics,connector="{connector}"` |
| status | The status of the connector. One of 'unassigned', 'running', 'paused', 'stopped', 'failed', or 'restarting'. | `kafka.connect:type=connector-metrics,connector="{connector}"` |
| batch-size-avg / batch-size-max | The average / largest number of records in the batches the task has processed so far. | `kafka.connect:type=connector-task-metrics,connector="{connector}",task="{task}"` |
| offset-commit-avg-time-ms | The average time in milliseconds taken by this task to commit offsets. | `kafka.connect:type=connector-task-metrics,connector="{connector}",task="{task}"` |
| offset-commit-failure-percentage | The average percentage of this task's offset commit attempts that failed. | `kafka.connect:type=connector-task-metrics,connector="{connector}",task="{task}"` |
| running-ratio / pause-ratio | The fraction of time this task has spent in the running / pause state. | `kafka.connect:type=connector-task-metrics,connector="{connector}",task="{task}"` |
| status | The status of the connector task. One of 'unassigned', 'running', 'paused', 'failed', or 'restarting'. | `kafka.connect:type=connector-task-metrics,connector="{connector}",task="{task}"` |
| partition-count | The number of topic partitions assigned to this task belonging to the named sink connector in this worker. | `kafka.connect:type=sink-task-metrics,connector="{connector}",task="{task}"` |
| put-batch-avg-time-ms / put-batch-max-time-ms | The average / maximum time taken by this task to put a batch of sinks records. | `kafka.connect:type=sink-task-metrics,connector="{connector}",task="{task}"` |
| sink-record-active-count | The number of records that have been read from Kafka but not yet completely committed/flushed/acknowledged by the sink task. | `kafka.connect:type=sink-task-metrics,connector="{connector}",task="{task}"` |
| sink-record-lag-max | The maximum lag in terms of number of records that the sink task is behind the consumer's position for any topic partitions. | `kafka.connect:type=sink-task-metrics,connector="{connector}",task="{task}"` |
| sink-record-read-rate | The average per-second number of records read from Kafka for this task. This is before transformations are applied. | `kafka.connect:type=sink-task-metrics,connector="{connector}",task="{task}"` |
| sink-record-send-rate | The average per-second number of records output from the transformations and sent/put to this task. This is after transformations are applied and excludes any records filtered out by the transformations. | `kafka.connect:type=sink-task-metrics,connector="{connector}",task="{task}"` |
| poll-batch-avg-time-ms | The average time in milliseconds taken by this task to poll for a batch of source records. | `kafka.connect:type=source-task-metrics,connector="{connector}",task="{task}"` |
| source-record-active-count | The number of records that have been produced by this task but not yet completely written to Kafka. | `kafka.connect:type=source-task-metrics,connector="{connector}",task="{task}"` |
| source-record-poll-rate | The average per-second number of records produced/polled (before transformation) by this task. | `kafka.connect:type=source-task-metrics,connector="{connector}",task="{task}"` |
| source-record-write-rate | The average per-second number of records written to Kafka for this task. This is after transformations are applied, and excludes any records filtered out by the transformations. | `kafka.connect:type=source-task-metrics,connector="{connector}",task="{task}"` |
| transaction-size-avg / -max / -min | The number of records in the transactions the task has committed so far (exactly-once source). | `kafka.connect:type=source-task-metrics,connector="{connector}",task="{task}"` |
| deadletterqueue-produce-failures | The number of failed writes to the dead letter queue. | `kafka.connect:type=task-error-metrics,connector="{connector}",task="{task}"` |
| deadletterqueue-produce-requests | The number of attempted writes to the dead letter queue. | `kafka.connect:type=task-error-metrics,connector="{connector}",task="{task}"` |
| last-error-timestamp | The epoch timestamp when this task last encountered an error. | `kafka.connect:type=task-error-metrics,connector="{connector}",task="{task}"` |
| total-errors-logged | The number of errors that were logged. | `kafka.connect:type=task-error-metrics,connector="{connector}",task="{task}"` |
| total-record-errors | The number of record processing errors in this task. | `kafka.connect:type=task-error-metrics,connector="{connector}",task="{task}"` |
| total-record-failures | The number of record processing failures in this task. | `kafka.connect:type=task-error-metrics,connector="{connector}",task="{task}"` |
| total-records-skipped | The number of records skipped due to errors. | `kafka.connect:type=task-error-metrics,connector="{connector}",task="{task}"` |
| total-retries | The number of operations retried. | `kafka.connect:type=task-error-metrics,connector="{connector}",task="{task}"` |

### Streams Monitoring

A Kafka Streams instance contains all the producer and consumer metrics as well as additional metrics specific to Streams. The metrics have three recording levels: `info`, `debug`, and `trace`.

Note that the metrics have a 4-layer hierarchy. At the top level there are client-level metrics for each started Kafka Streams client. Each client has stream threads, with their own metrics. Each stream thread has tasks, with their own metrics. Each task has a number of processor nodes, with their own metrics. Each task also has a number of state stores and record caches, all with their own metrics.

```
metrics.recording.level="info"
```

#### Thread Metrics (selected)

| Metric/Attribute name | Description | Mbean name |
|---|---|---|
| commit-latency-avg / -max | The average / maximum execution time in ms, for committing, across all running tasks of this thread. | `kafka.streams:type=stream-thread-metrics,thread-id=([-.\w]+)` |
| poll-latency-avg / -max | The average / maximum execution time in ms, for consumer polling. | `kafka.streams:type=stream-thread-metrics,thread-id=([-.\w]+)` |
| punctuate-latency-avg / -max | The average / maximum execution time in ms, for punctuating. | `kafka.streams:type=stream-thread-metrics,thread-id=([-.\w]+)` |
| commit-rate / poll-rate / punctuate-rate | The average number of commits / consumer poll calls / punctuate calls per sec. | `kafka.streams:type=stream-thread-metrics,thread-id=([-.\w]+)` |
| poll-records-avg / -max | The average / maximum number of records polled from consumer within an iteration. | `kafka.streams:type=stream-thread-metrics,thread-id=([-.\w]+)` |
| process-rate | The average number of processed records per sec. | `kafka.streams:type=stream-thread-metrics,thread-id=([-.\w]+)` |
| task-created-rate / task-closed-rate | The average number of tasks created / closed per sec. | `kafka.streams:type=stream-thread-metrics,thread-id=([-.\w]+)` |

#### Task Metrics (recording level `debug`, except dropped-records-* and active-process-ratio which are `info`)

| Metric/Attribute name | Description | Mbean name |
|---|---|---|
| process-latency-avg / -max | The average / maximum execution time in ns, for processing. | `kafka.streams:type=stream-task-metrics,thread-id=([-.\w]+),task-id=([-.\w]+)` |
| process-rate | The average number of processed records per sec across all source processor nodes of this task. | `kafka.streams:type=stream-task-metrics,thread-id=([-.\w]+),task-id=([-.\w]+)` |
| record-lateness-avg | The average observed lateness in ms of records (stream time - record timestamp). | `kafka.streams:type=stream-task-metrics,thread-id=([-.\w]+),task-id=([-.\w]+)` |
| record-lateness-max | The max observed lateness in ms of records (stream time - record timestamp). | `kafka.streams:type=stream-task-metrics,thread-id=([-.\w]+),task-id=([-.\w]+)` |
| enforced-processing-rate | The average number of enforced processings per sec. | `kafka.streams:type=stream-task-metrics,thread-id=([-.\w]+),task-id=([-.\w]+)` |
| dropped-records-rate / dropped-records-total | The average number / total of records dropped within this task. | `kafka.streams:type=stream-task-metrics,thread-id=([-.\w]+),task-id=([-.\w]+)` |
| active-process-ratio | The fraction of time the stream thread spent on processing this task among all assigned active tasks. | `kafka.streams:type=stream-task-metrics,thread-id=([-.\w]+),task-id=([-.\w]+)` |
| active-buffer-count | The count of buffered records that are polled from consumer and not yet processed for this active task. | `kafka.streams:type=stream-task-metrics,thread-id=([-.\w]+),task-id=([-.\w]+)` |
| record-rate / update-rate | The average number of records restored / updated per second (state store restoration). | `kafka.streams:type=stream-task-metrics,thread-id=([-.\w]+),task-id=([-.\w]+)` |

Processor node metrics live under `kafka.streams:type=stream-processor-node-metrics,thread-id=...,task-id=...,processor-node-id=...`; state store metrics under `kafka.streams:type=stream-state-metrics,thread-id=...,task-id=...,[store-scope]-state-id=...` (put/get/fetch/flush/restore latency & rate; RocksDB-specific metrics such as `bytes-written-rate`, `memtable-hit-ratio`, `block-cache-data-hit-ratio`, `num-running-compactions`).
