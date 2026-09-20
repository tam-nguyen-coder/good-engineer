# Prometheus — JMX Exporter rules + Alerting rules: từ MBean tới alert biết im lặng đúng lúc

> **Nguồn (official):** https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/ · https://prometheus.io/docs/practices/alerting/ · https://github.com/prometheus/jmx_exporter · https://prometheus.github.io/jmx_exporter/1.4.0/configuration/rules/
> **Tuần:** 7 — Observability + Troubleshooting playbook · **Loại:** Prometheus Docs (alerting) + Prometheus JMX Exporter Docs (rules)
> ⚠️ Nội dung dưới đây được crawl tự động (HTTP → Markdown, có rút gọn) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- **Triết lý một câu:** *"keep alerting simple, alert on symptoms, have good consoles to allow pinpointing causes, and avoid having pages where there is nothing to do."* Dịch sang Kafka: alert vào **triệu chứng người dùng thấy** (`OfflinePartitionsCount`, `UnderMinIsrPartitionCount` — mất đọc/ghi) chứ không alert mọi nguyên nhân.
- **`for:` là cách chống alert fatigue.** Điều kiện đúng nhưng chưa đủ `for:` thì alert ở trạng thái **`pending`**, chưa **`firing`**. Đây chính là cơ chế để `UnderReplicatedPartitions > 0` **trong 30 giây** lúc rolling restart không đánh thức ai, còn **trong 10 phút** thì có.
- **`keep_firing_for:`** giữ alert firing thêm một khoảng sau khi điều kiện hết đúng — chống **flapping** (đúng thứ cần cho `IsrShrinksPerSec` dao động).
- Docs khuyên: *"Allow tolerance for minor fluctuations"* và *"Alerts should link to relevant consoles"* → annotation nên có `runbook_url` trỏ tới playbook.
- **Batch/offline job:** *"Thresholds should allow for at least two full job cycles"* — áp cho Kafka nghĩa là ngưỡng alert lag phải rộng hơn **2 chu kỳ** tính lag (Confluent emitter mặc định 60 s → `for:` ≥ 2–3 phút).
- **Capacity:** *"Alert when approaching capacity limits, as human intervention often prevents future outages"* → disk sắp đầy **là** alert gọi dậy, vì disk đầy thì broker chết và không sửa nhanh được.
- **Metamonitoring:** phải giám sát chính hệ giám sát. Nếu Prometheus chết thì mọi alert Kafka đều "im lặng" — đó là **im lặng giả**, không phải cluster khoẻ. Template trong annotation: `{{ $labels.<labelname> }}` và `{{ $value }}` — dùng để in thẳng tên broker và giá trị metric vào nội dung alert.

**Phần JMX Exporter — đường ống đưa MBean vào Prometheus:**

- JMX Exporter là *"a process for collecting metrics using JMX MBeans for Prometheus consumption"* — nó **không** sinh metric mới, chỉ **dịch MBean sẵn có** sang định dạng Prometheus.
- **Hai chế độ, chọn đúng là một câu hỏi vận hành:**
  - **Java agent** — *"Recommended for most users because it avoids remote JMX/RMI setup"*. Gắn vào chính JVM broker, expose HTTP `/metrics`. **Không cần mở remote JMX ra ngoài** → an toàn hơn hẳn.
  - **Standalone (HTTP server)** — *"when you must scrape a JVM over remote JMX/RMI"*; *"requires the target application to expose remote JMX correctly"*. Chỉ dùng khi không sửa được lệnh khởi động JVM.
- Cú pháp gắn agent: `-javaagent:<jar>=<port>:<config.yaml>` đặt trong `KAFKA_OPTS`. Vì `KAFKA_OPTS` áp cho **mọi** script trong `bin/`, chạy `kafka-topics.sh` trên chính máy broker sẽ cố bind lại port đó → `Address already in use`. Đây là bẫy vận hành thật. **Rule fields:** `pattern` (regex khớp chuỗi sinh từ ObjectName + attribute), `name` (tên metric, dùng `$1`/`$2` cho capture group), `value`, `valueFactor` (mặc định `1.0`), `labels`, `help`, `cache` (mặc định `false`), `type` = `GAUGE` | `COUNTER` | `UNTYPED`, `attrNameSnakeCase` (mặc định `false`).
- **Không khớp rule nào** → *"attributes are exported using the default JMX Exporter naming behavior"* — nghĩa là metric vẫn ra nhưng tên xấu và số lượng khổng lồ. Viết rule hẹp là cách giảm tải scrape.
- `excludeJvmMetrics: true` để tắt metric JVM dựng sẵn; từ 1.4.0 có thêm hỗ trợ biến môi trường cho mật khẩu HTTP Basic và SSL. Docs khuyên **lấy nguyên văn dòng scrape thật** rồi mới viết pattern: *"use exact examples from scraped output when building production rules"* — tức `curl localhost:7071/metrics` trước, viết regex sau.

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Alerting rules — syntax

Alerting rules allow you to define alert conditions based on Prometheus expression language expressions and to send notifications about firing alerts to an external service.

```yaml
groups:
- name: example
  labels:
    team: myteam
  rules:
  - alert: HighRequestLatency
    expr: job:request_latency_seconds:mean5m{job="myjob"} > 0.5
    for: 10m
    keep_firing_for: 5m
    labels:
      severity: page
    annotations:
      summary: High request latency
```

The optional `for` clause causes Prometheus to wait for a certain duration between first encountering a new expression output vector element and counting an alert as firing for this element. In this case, Prometheus will check that the alert continues to be active during each evaluation for 10 minutes before firing the alert. Elements that are active, but not firing yet, are in the **pending** state. Alerting rules without the `for` clause will become active on the first evaluation.

The optional `keep_firing_for` clause tells Prometheus to keep this alert firing for the specified duration after the firing condition was last met. This can be used to prevent situations such as flapping alerts, false resolutions due to lack of data loss, etc.

The `labels` clause allows specifying a set of additional labels to be attached to the alert. Any existing conflicting labels will be overwritten.

The `annotations` clause specifies a set of informational labels that can be used to store longer additional information such as alert descriptions or runbook links.

### Templating

Annotation values can be templated. Available variables:

- `{{ $labels.<labelname> }}` — the label values of the alert instance.
- `{{ $value }}` — the value of the alert expression.
- `$externalLabels` — the configured external labels.

```yaml
groups:
- name: example
  rules:
  - alert: InstanceDown
    expr: up == 0
    for: 5m
    labels:
      severity: page
    annotations:
      summary: "Instance {{ $labels.instance }} down"
      description: "{{ $labels.instance }} of job {{ $labels.job }} has been down for more than 5 minutes."
```

### Alerting — best practices

The [My Philosophy on Alerting](https://docs.google.com/document/d/199PqyG3UsyXlwieHaqbGiWVa8eMWi8zzAn0YfcApr8Q/edit) is based on Rob Ewaschuk's observations at Google. In short: keep alerting simple, alert on symptoms, have good consoles to allow pinpointing causes, and avoid having pages where there is nothing to do.

#### What to alert on

Try to keep the number of alerts low by alerting on high-level symptoms that are tied to user impact, rather than trying to catch every possible way that something could go wrong. Alerts should link to relevant consoles and make it easy to figure out which component is at fault. Allow slack in alerting to accommodate small blips.

#### Online serving systems

Typically alert on high latency and error rates as high up in the stack as possible.

Only page on latency at one point in a stack. If a lower-level component is slower than it should be, but the overall user latency is fine, then there is no need to page.

For error rates, page on user-visible errors. If there are errors further down the stack that will cause such a failure, there is no need to page on them separately. However, if some failures are not user-visible, but are otherwise severe enough to require human involvement (for example, you are losing a lot of money), add pages to be sent on those.

You may need alerting thresholds for different types of request that you serve.

#### Offline processing

For offline processing systems, the key metric is how long data takes to get through the system, so page if that gets high enough to cause user impact.

#### Batch jobs

For batch jobs it makes sense to alert if the batch job has not succeeded recently enough, and this will cause user-visible problems.

This should generally be at least enough time for 2 full runs of the batch job. For a job that runs every 4 hours and takes an hour, 10 hours would be a reasonable threshold. If you cannot withstand a single run failing, run the job more frequently, as a single failure should not require human intervention.

#### Capacity

While not a problem causing immediate user impact, being close to capacity often requires human intervention to avoid an outage in the near future.

#### Metamonitoring

It is important to have confidence that monitoring is working. Accordingly, have alerts to ensure that Prometheus servers, Alertmanagers, PushGateways, and other monitoring infrastructure are available and running correctly.

As always, if it is possible to alert on symptoms rather than causes, this helps to reduce noise. For example, a blackbox test that alerts are getting from PushGateway to Prometheus to Alertmanager to email is better than individual alerts on each.

Supplementing the whitebox monitoring of Prometheus with external blackbox monitoring can catch problems that are otherwise invisible, and also serves as a fallback in case internal systems completely fail.

---

## 📄 Nội dung phần 2 — Prometheus JMX Exporter (trích từ tài liệu gốc)

### What it is

> A process for collecting metrics using JMX MBeans for Prometheus consumption.

License: Apache 2.0. Requires Java 8+. Documentation at https://prometheus.github.io/jmx_exporter/.

### Modes

**Java Agent**

Recommended for most users because it avoids remote JMX/RMI setup. Use it when you can start or attach an agent inside the target JVM.

**Standalone (HTTP server)**

Use it when you must scrape a JVM over remote JMX/RMI. This mode requires the target application to expose remote JMX correctly.

### Release highlights (1.4.0)

- `excludeJvmMetrics` support for disabling JVM metrics.
- Environment-variable support for HTTP Basic password and HTTP SSL passwords.

### Rules configuration

| Field | Description |
|---|---|
| `pattern` | Regex pattern matched against the formatted MBean and attribute input. Required when `name` is set. |
| `name` | Metric name. Capture groups can be referenced with `$1`, `$2`, and so on. |
| `value` | Static value or capture-group expression. |
| `valueFactor` | Numeric multiplier. Default `1.0`. |
| `labels` | Label map. Requires `name`. |
| `help` | Help text. Requires `name`. |
| `cache` | Cache rule match and mismatch results. Default `false`. |
| `type` | `GAUGE`, `COUNTER`, or `UNTYPED`. |
| `attrNameSnakeCase` | Convert attribute names to snake case. Default `false`. |
| `excludeJvmMetrics` | Exclude built-in JVM MBeans from collection when set to `true`. |

Patterns match against a generated string built from the MBean ObjectName, attribute name, and value path. Use exact examples from scraped output when building production rules.

If no rule matches, attributes are exported using the default JMX Exporter naming behavior.

### Kafka-shaped example (viết theo đúng cú pháp trên, đối chiếu với Lab 8.1 CCDAK)

```yaml
lowercaseOutputName: true
lowercaseOutputLabelNames: true
rules:
  # Gauge → attribute Value
  - pattern: kafka.server<type=ReplicaManager, name=(UnderReplicatedPartitions|UnderMinIsrPartitionCount|AtMinIsrPartitionCount)><>Value
    name: kafka_server_replicamanager_$1
    type: GAUGE

  # Controller (KRaft: MBean này chỉ có trên node process.roles=controller)
  - pattern: kafka.controller<type=KafkaController, name=(OfflinePartitionsCount|ActiveControllerCount|FencedBrokerCount|ActiveBrokerCount)><>Value
    name: kafka_controller_kafkacontroller_$1
    type: GAUGE

  # Histogram/Timer → chọn percentile cụ thể, gắn label request
  - pattern: kafka.network<type=RequestMetrics, name=(TotalTimeMs|RequestQueueTimeMs|LocalTimeMs|RemoteTimeMs|ResponseQueueTimeMs|ResponseSendTimeMs), request=(Produce|FetchConsumer|FetchFollower)><>(Mean|99thPercentile)
    name: kafka_network_requestmetrics_$1_$3
    labels:
      request: "$2"
    type: GAUGE
```
