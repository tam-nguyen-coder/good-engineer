# Confluent Platform — Monitor Consumer Lag: hai cách đo, và cái không đo được

> **Nguồn (official):** https://docs.confluent.io/platform/current/monitor/monitor-consumer-lag.html
> **Tuần:** 7 — Observability + Troubleshooting playbook · **Loại:** Confluent Platform Docs
> ⚠️ Nội dung dưới đây được crawl tự động (HTTP → Markdown, có rút gọn) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất. Một số đoạn bổ sung từ trang **Apache Kafka 4.3 Monitoring** (đã đánh dấu rõ) vì trang Confluent không nêu thẳng tên metric client.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- **Định nghĩa chính thức:** consumer lag = *"the number of consumer offsets between the latest message produced in a partition and the last message consumed by a consumer"* — tức **LOG-END-OFFSET − CURRENT-OFFSET (committed)** cho mỗi partition.
- **Bẫy lớn nhất của tuần:** *"You cannot monitor consumer lag with consumers that use the `assign()` method"* — vì group coordinator **không quản lý** assignment cho consumer dùng `assign()`. Ứng dụng standalone (không group) sẽ **không xuất hiện** trong `kafka-consumer-groups.sh` và không có lag đo được từ phía broker.
- **Hai con số lag khác nhau và CẢ HAI ĐỀU ĐÚNG:**
  - **Theo committed offset** — `kafka-consumer-groups.sh --describe` và metric broker-side. Cập nhật mỗi lần commit (auto commit mặc định **5000 ms**) → **trễ hơn** thực tế.
  - **Theo fetch position** — client metric `records-lag-max` (`kafka.consumer:type=consumer-fetch-manager-metrics`). Tính theo vị trí **đã fetch**, chưa cần commit → **thấp hơn** con số CLI.
  - Chênh lệch giữa hai số **không phải lỗi**; nó chính bằng lượng record đã fetch mà chưa commit.
- Broker-side lag của Confluent Platform bật bằng `confluent.consumer.lag.emitter.enabled=true`, chu kỳ `confluent.consumer.lag.emitter.interval.ms` mặc định **60000 ms** — nghĩa là con số lag từ nguồn này **trễ tới 1 phút**, đừng alert với `for:` ngắn hơn.
- **`records-lead-min`** *(nguồn: Apache Kafka Monitoring)* — khoảng cách từ fetch position tới **log start offset**. Tiến về **0** nghĩa là retention đang **xoá record trước khi consumer kịp đọc** → sắp mất dữ liệu. Đây là metric cảnh báo sớm mà `records-lag-max` **không** cho biết.
- Lag theo **thời gian** ("consumer đang chậm mấy phút") không có metric sẵn — cần công cụ ngoài (Burrow, kafka-lag-exporter) hoặc tự tính từ timestamp record.

---

## 📄 Nội dung (trích từ tài liệu gốc)

### What is consumer lag?

Consumer lag refers to the delay between the production and consumption of messages in Apache Kafka®. Specifically, it is the number of consumer offsets between the latest message produced in a partition and the last message consumed by a consumer.

Monitoring consumer lag is important because a growing lag indicates that consumers are not keeping up with producers, which eventually leads to increased end-to-end latency and, if the lag exceeds the retention of the topic, to data loss for that consumer.

### Monitor consumer lag with JMX

To enable consumer lag monitoring on the brokers, set the following broker properties:

| Property | Description | Default |
|---|---|---|
| `confluent.consumer.lag.emitter.enabled` | Set to `true` to enable the consumer lag emitter | `false` |
| `confluent.consumer.lag.emitter.interval.ms` | How often the lag is computed and emitted | `60000` |

The `consumer-lag-offset` MBean provides the difference between the last offset stored by the broker and the last committed offset for that consumer group, client, topic and partition.

### Important limitation

You cannot monitor consumer lag with consumers that use the `assign()` method. This is because the coordinator of a consumer group does not manage consumer assignment for consumers assigned to topics and partitions using `assign()`.

### Monitor consumer lag with the CLI

```bash
$ bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --describe --group my-group
```

The `LAG` column is `LOG-END-OFFSET` minus `CURRENT-OFFSET`, where `CURRENT-OFFSET` is the **committed** offset of the group. A `CONSUMER-ID` of `-` means no member currently owns that partition.

### Monitor consumer lag with Control Center

Confluent Control Center can monitor consumer latency and lets you create a consumer group trigger for consumer lag, which fires an action (for example an email) when the lag for a group crosses a threshold.

---

### Bổ sung — client-side lag metrics (nguồn: https://kafka.apache.org/43/operations/monitoring/)

| Metric | Description | Mbean name |
|---|---|---|
| `records-lag` | The latest lag of the partition. | `kafka.consumer:type=consumer-fetch-manager-metrics,partition=([-.\w]+),topic=([-.\w]+),client-id=([-.\w]+)` |
| `records-lag-max` | The maximum lag in terms of number of records for any partition in this window. | `kafka.consumer:type=consumer-fetch-manager-metrics,client-id=([-.\w]+)` |
| `records-lead` | The latest lead of the partition. | `kafka.consumer:type=consumer-fetch-manager-metrics,partition=([-.\w]+),topic=([-.\w]+),client-id=([-.\w]+)` |
| `records-lead-min` | The minimum lead in terms of number of records for any partition in this window. | `kafka.consumer:type=consumer-fetch-manager-metrics,client-id=([-.\w]+)` |

### Bổ sung — consumer group / coordinator metrics đi kèm khi chẩn đoán lag (nguồn: https://kafka.apache.org/43/operations/monitoring/)

| Metric | Description | Mbean name |
|---|---|---|
| `records-consumed-rate` | The average number of records consumed per second. | `kafka.consumer:type=consumer-fetch-manager-metrics,client-id=([-.\w]+)` |
| `fetch-rate` | The number of fetch requests per second. | `kafka.consumer:type=consumer-fetch-manager-metrics,client-id=([-.\w]+)` |
| `fetch-size-avg` | The average number of bytes fetched per request. | `kafka.consumer:type=consumer-fetch-manager-metrics,client-id=([-.\w]+)` |
| `assigned-partitions` | The number of partitions currently assigned to this consumer. | `kafka.consumer:type=consumer-coordinator-metrics,client-id=([-.\w]+)` |
| `commit-latency-avg` | The average time taken for a commit request. | `kafka.consumer:type=consumer-coordinator-metrics,client-id=([-.\w]+)` |
| `commit-rate` | The number of commit calls per second. | `kafka.consumer:type=consumer-coordinator-metrics,client-id=([-.\w]+)` |
| `rebalance-latency-avg` | The average time taken for a group to complete a rebalance. | `kafka.consumer:type=consumer-coordinator-metrics,client-id=([-.\w]+)` |
| `rebalance-rate-per-hour` | The number of rebalances per hour. | `kafka.consumer:type=consumer-coordinator-metrics,client-id=([-.\w]+)` |
| `failed-rebalance-rate-per-hour` | The number of failed rebalance events per hour. | `kafka.consumer:type=consumer-coordinator-metrics,client-id=([-.\w]+)` |
| `last-rebalance-seconds-ago` | The number of seconds since the last rebalance event. | `kafka.consumer:type=consumer-coordinator-metrics,client-id=([-.\w]+)` |
| `time-between-poll-avg` / `time-between-poll-max` | The average / maximum delay between invocations of `poll()`. | `kafka.consumer:type=consumer-metrics,client-id=([-.\w]+)` |
| `last-poll-seconds-ago` | The number of seconds since the last `poll()` invocation. | `kafka.consumer:type=consumer-metrics,client-id=([-.\w]+)` |
| `poll-idle-ratio-avg` | The average fraction of time the consumer's `poll()` is idle as opposed to waiting for the user code to process records. | `kafka.consumer:type=consumer-metrics,client-id=([-.\w]+)` |
| `fetch-throttle-time-avg` / `fetch-throttle-time-max` | The average / maximum throttle time in ms. | `kafka.consumer:type=consumer-fetch-manager-metrics,client-id=([-.\w]+)` |

### Cách đọc ba metric này khi chẩn đoán (áp dụng cho cây quyết định lag)

- `assigned-partitions = 0` trên một member → member đó **idle**: group có nhiều consumer hơn partition. Thêm consumer nữa sẽ không giúp gì.
- `poll-idle-ratio-avg ≈ 0` → consumer gần như không bao giờ rảnh trong `poll()`, tức là **user code là nút thắt**. Ngược lại, giá trị gần 1 nghĩa là consumer đang chờ dữ liệu — không phải nó chậm.
- `rebalance-rate-per-hour` cao đi kèm `last-rebalance-seconds-ago` liên tục nhỏ → group đang ở trạng thái **rebalance storm**; lag sẽ có hình răng cưa chứ không tăng đều.
- `time-between-poll-max` tiến gần `max.poll.interval.ms` (mặc định 300000 ms) → member sắp bị đuổi khỏi group.
- `fetch-throttle-time-avg > 0` → consumer đang bị chặn bởi `consumer_byte_rate` quota, không phải bị broker chậm.
