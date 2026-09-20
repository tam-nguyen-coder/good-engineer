# Confluent Platform — Dynamic Broker Configuration & xoay keystore/truststore không restart

> **Nguồn (official):** https://docs.confluent.io/platform/current/kafka/dynamic-config.html
> **Tuần:** 5 — Security administration · **Loại:** Confluent Platform Docs (Kafka Operations → Dynamic configurations)
> ⚠️ Nội dung dưới đây được crawl tự động (WebFetch, có rút gọn) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- Đây là **lời giải cho câu hỏi kinh điển "xoay chứng chỉ sắp hết hạn mà không downtime"**. Keystore và truststore của một listener **đã tồn tại** là **per-broker dynamic config** → đổi bằng `kafka-configs.sh`, **không restart, không rolling bounce**.
- **3 update mode** phải phân biệt: **read-only** (cần restart) · **per-broker** (đổi được cho từng broker lúc chạy) · **cluster-wide** (đặt mặc định cả cluster, hoặc đè cho 1 broker khi thử nghiệm).
- **Thứ tự ưu tiên khi cùng một config xuất hiện nhiều nơi**: dynamic **per-broker** > dynamic **cluster-wide default** > file `server.properties` tĩnh.
- Cú pháp: `--entity-type brokers --entity-name <broker-id>` cho một broker, `--entity-type brokers --entity-default` cho cả cluster; `--describe` để xem, `--delete-config` để gỡ override, `--add-config-file` để nạp nhiều config một lượt.
- Config kiểu **list** phải bọc trong **ngoặc vuông**: `--add-config 'ssl.enabled.protocols=[TLSv1.2,TLSv1.3]'`.
- **Keystore đổi được lúc chạy (per-broker only)**: `listener.name.{listenerName}.ssl.keystore.type` · `.ssl.keystore.location` · `.ssl.keystore.password` · `.ssl.key.password`.
- **Truststore đổi được lúc chạy**: `listener.name.{listenerName}.ssl.truststore.type` · `.ssl.truststore.location` · `.ssl.truststore.password`.
- **Hai luật kiểm tra tin cậy của inter-broker listener — dễ ra đề, ngược chiều nhau:**
  - Đổi **keystore**: chỉ cho phép nếu **keystore MỚI được truststore hiện tại tin**.
  - Đổi **truststore**: chỉ cho phép nếu **keystore hiện tại được truststore MỚI tin**.
  - Listener khác (không phải inter-broker) **không kiểm tra gì cả** → sai là client rớt ngay.
  → Hệ quả vận hành: **luôn thêm CA mới vào truststore TRƯỚC, đổi keystore SAU**. Làm ngược thứ tự sẽ bị broker từ chối hoặc làm đứt replication.
- Nếu không khai config theo listener thì Kafka **rơi về config chung** (`ssl.keystore.location`) → mẹo thực dụng: giữ **nguyên mật khẩu** cho keystore mới thì chỉ cần đổi mỗi `location`, khỏi phải bật cơ chế mã hoá mật khẩu.
- Muốn đổi **mật khẩu** bằng dynamic config thì broker phải có `password.encoder.secret` trong file tĩnh; và "*All dynamically updated password settings must be provided in every alter request*" — thiếu một cái là **mất hết** những cái đã đặt trước.
- Từ Confluent Platform 7.7 (tương ứng KRaft ở Apache Kafka), tool có thể trỏ thẳng vào controller bằng `--bootstrap-controller`; **không được** dùng đồng thời với `--bootstrap-server`.

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Overview

Confluent Platform allows updates to certain broker and topic configurations without restarting brokers. The `kafka-configs` tool manages these dynamic changes, which persist through restarts.

Each broker setting has an **Update Mode**:

- **read-only**: Requires a broker restart for the update to take effect.
- **per-broker**: May be updated dynamically for each broker.
- **cluster-wide**: May be updated dynamically as a cluster-wide default. May also be updated as a per-broker value for testing.

### kafka-configs command syntax

Per-broker configuration:

```bash
bin/kafka-configs --bootstrap-server localhost:9092 \
  --entity-type brokers --entity-name 0 \
  --alter --add-config log.cleaner.threads=2
```

Cluster-wide default configuration:

```bash
bin/kafka-configs --bootstrap-server localhost:9092 \
  --entity-type brokers --entity-default \
  --alter --add-config log.cleaner.threads=2
```

Describe the currently configured dynamic broker configs:

```bash
bin/kafka-configs --bootstrap-server localhost:9092 \
  --entity-type brokers --entity-name 0 --describe

bin/kafka-configs --bootstrap-server localhost:9092 \
  --entity-type brokers --entity-default --describe
```

Delete a config override and revert to the statically configured or default value:

```bash
bin/kafka-configs --bootstrap-server localhost:9092 \
  --entity-type brokers --entity-name 0 \
  --alter --delete-config log.cleaner.threads
```

### Configuration precedence

Some configs may be configured at multiple levels. The precedence, from highest to lowest, is:

1. Dynamic per-broker config stored in the cluster metadata
2. Dynamic cluster-wide default config stored in the cluster metadata
3. Static broker config from `server.properties`

### Batch updates

Use `--add-config-file` to update several settings at once:

```bash
bin/kafka-configs --bootstrap-server localhost:9092 \
  --entity-type brokers --entity-default \
  --alter --add-config-file new.properties
```

### List values

When updating list-type configurations, enclose the comma-separated values in square brackets:

```bash
kafka-configs --bootstrap-server <host>:<port> \
  --entity-type brokers --entity-name 1 \
  --alter --add-config 'ssl.enabled.protocols=[TLSv1.2,TLSv1.3]'
```

### Updating TLS/SSL keystore of an existing listener

You can update the TLS/SSL keystore of an existing listener dynamically, without restarting the broker. The configuration must be prefixed with the listener name:

```bash
kafka-configs --bootstrap-server hostname:port \
  --entity-type brokers --entity-name <broker-ID> \
  --alter --add-config \
  listener.name.<listener-name>.ssl.keystore.location=<path-to-new-keystore>
```

The following settings may be updated at **per-broker level only**:

- `listener.name.{listenerName}.ssl.keystore.type`
- `listener.name.{listenerName}.ssl.keystore.location`
- `listener.name.{listenerName}.ssl.keystore.password`
- `listener.name.{listenerName}.ssl.key.password`

If the listener is the inter-broker listener, the update is allowed only if the new key store is trusted by the trust store configured for that listener. For other listeners, no trust validation is performed on the key store by the broker.

### Updating TLS/SSL truststore of an existing listener

You can update the TLS/SSL truststore of an existing listener dynamically to add or remove certificates, without restarting the broker:

```bash
kafka-configs --bootstrap-server hostname:port \
  --entity-type brokers --entity-name <broker-ID> \
  --alter --add-config \
  listener.name.<listener-name>.ssl.truststore.location=<path-to-new-truststore>
```

The following settings may be updated at per-broker level only:

- `listener.name.{listenerName}.ssl.truststore.type`
- `listener.name.{listenerName}.ssl.truststore.location`
- `listener.name.{listenerName}.ssl.truststore.password`

If the listener is the inter-broker listener, the update is allowed only if the existing key store for that listener is trusted by the new trust store. For other listeners, no trust validation is performed by the broker.

If the config for the listener name is not set, the config will fall back to the generic config (that is, `ssl.keystore.location` / `ssl.truststore.location`).

### Updating password configurations dynamically

Password configuration values that are dynamically updated are encrypted before being stored in the cluster metadata. The broker configuration `password.encoder.secret` must be configured in `server.properties` to enable dynamic update of password configurations. The secret may be different on different brokers.

```bash
bin/kafka-configs --bootstrap-server localhost:9092 \
  --entity-type brokers --entity-name 0 \
  --alter --add-config \
  'listener.name.internal.ssl.key.password=key-password'
```

All dynamically updated password settings must be provided in every alter request when updating configurations using `kafka-configs`, even if the password configuration is not being altered.

### Adding and removing listeners

Listeners may be added or removed dynamically. When a new listener is added, security configs of the listener must be provided as listener configs with the listener prefix `listener.name.{listenerName}`. Listeners may be removed by updating the `listeners` config; however, the inter-broker listener and the controller listener cannot be updated dynamically.

### KRaft controllers

Starting with Confluent Platform 7.7, you can direct the tool at the KRaft controller quorum instead of the brokers:

```bash
bin/kafka-cluster cluster-id --bootstrap-controller localhost:9092
```

You cannot specify both `--bootstrap-server` and `--bootstrap-controller` in the same command.
