# Bảo mật Kafka Connect — REST HTTPS/basic auth, credential worker, client override, ACL

> **Nguồn (official):** https://docs.confluent.io/platform/current/connect/security.html · https://kafka.apache.org/43/kafka-connect/user-guide/ (mục *Security*) · https://kafka.apache.org/43/generated/connect_config.html
> **Tuần:** 6 — Kafka Connect operations · **Loại:** Confluent Platform Docs + Apache Kafka Docs
> ⚠️ Nội dung dưới đây được crawl tự động (WebFetch) ngày 2026-09-20 — luôn đối chiếu link gốc.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- Worker Connect là **một client Kafka bình thường**: cluster bật SASL/TLS thì worker phải khai `security.protocol`, `sasl.mechanism`, `sasl.jaas.config`, `ssl.truststore.*` — ở **mức worker** và lặp lại với prefix `producer.`, `consumer.`, `admin.` nếu muốn tách.
- Ba prefix, ba mục đích: `producer.` = source task ghi Kafka · `consumer.` = sink task đọc Kafka · `admin.` = tạo internal topic và **ghi DLQ / error reporting** của sink.
- **Bẫy ACL kinh điển:** cấp đủ quyền cho topic dữ liệu nhưng quên `admin.` → sink connector chạy được cho tới khi gặp record hỏng, rồi chết vì không tạo được DLQ topic.
- Worker cần ACL: `Create` trên **Cluster** (để tạo 3 internal topic), `Read`+`Write` trên 3 **internal topic**, `Read` trên **Group** = `group.id` của worker.
- Connector cần thêm: source → `Write` trên topic đích; sink → `Read` trên topic nguồn **và** `Read` trên **Group `connect-<connector-name>`**. Thiếu quyền Group là nguyên nhân số 1 của `GroupAuthorizationException` ở sink.
- **REST HTTPS:** đặt `listeners=https://localhost:8443` và cấu hình TLS bằng prefix riêng **`listeners.https.*`** (không dùng `ssl.*` chung, vì `ssl.*` là cho kết nối tới broker). Khi bật HTTPS phải đặt `rest.advertised.listener=https` để worker khác forward request đúng scheme.
- **REST basic auth** không có sẵn trong Apache Kafka — bật bằng REST extension: `rest.extension.classes=org.apache.kafka.connect.rest.basic.auth.extension.BasicAuthSecurityRestExtension` (mặc định `rest.extension.classes` là `""`, tức REST **mở hoàn toàn**).
- **REST mở = quyền admin trên toàn bộ pipeline.** Ai POST được connector thì đọc/ghi được mọi topic mà worker có quyền — và với policy `All`, còn đổi được cả `sasl.jaas.config` để mượn principal khác.
- `connector.client.config.override.policy`: `None` (cấm hết) · `Principal` (chỉ cho override `security.protocol`, `sasl.jaas.config`, `sasl.mechanism`) · `All` (cho hết) · **`Allowlist`** (4.2+, liệt kê tường minh config được phép). Apache Kafka 4.3 mặc định **`All`**; docs khuyến nghị chuyển sang `Allowlist` và **5.0 sẽ lấy `Allowlist` làm mặc định**.
  - ⚠️ **Hai nguồn ghi khác nhau:** trang Confluent Platform *Connect Security* vẫn ghi `None (default)`. Trang `connect_config.html` của Apache Kafka 4.3 ghi rõ default là **`All`** (đổi từ 3.0, KIP-722). Với đề neo theo Apache Kafka 4.3, lấy **`All`**.
- **Externalize secret** bằng `ConfigProvider`: `FileConfigProvider` với cú pháp `${file:/path:key}`, `EnvVarConfigProvider` với `${env:VAR}`. Secret **không** bị ghi vào connector config, log hay response REST.
- **Mọi worker phải giải được mọi biến** trong cả worker config lẫn connector config — file secret phải có mặt trên **tất cả** worker, nếu không task sẽ FAILED trên đúng worker thiếu file.

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Securing worker connections to Kafka

"If you have enabled authentication in your Kafka cluster, then you must make sure that Kafka Connect is also configured for security."

Core properties: `security.protocol` (e.g. `SASL_SSL`, `SSL`), `sasl.mechanism` (GSSAPI, SCRAM, PLAIN), `sasl.jaas.config`.

### Producer, consumer and admin prefixes

- `producer.` prefix controls "producer behavior for source connectors"
- `consumer.` prefix controls "consumer behavior for sink connectors"
- `admin.` prefix handles "error reporting in sink connectors"

### Per-connector credentials

Override defaults with `producer.override.`, `consumer.override.` and `admin.override.`, enabled by `connector.client.config.override.policy`.

Policies documented by Confluent:

- `None` — "Does not allow any configuration overrides"
- `Principal` — allows "security.protocol, sasl.jaas.config, and sasl.mechanism" overrides
- `All` — "Allows overrides for all configuration properties"

From the Apache Kafka 4.3 Connect User Guide, *Security*:

> "Since Kafka 4.2.0, it's recommended to set `connector.client.config.override.policy` to `Allowlist`, this will be the default from Kafka 5.0.0, and explicitly only allow configurations that you need to override."

From `connect_config.html` (Apache Kafka 4.3):

| Configuration | Description | Type | Default | Importance |
|---|---|---|---|---|
| `connector.client.config.override.policy` | "Policy class defining which client configs connectors can override" | string | **All** | medium |

### Securing the REST interface

```
listeners=https://localhost:8443
```

Required TLS properties include `ssl.keystore.location`, `ssl.keystore.password`, `ssl.key.password`, `ssl.truststore.location`.

"For REST-specific configuration: use the `listeners.https` prefix" instead of the generic `ssl.*` settings.

Inter-node communication is controlled with `rest.advertised.listener`, `rest.advertised.host.name`, `rest.advertised.port`.

From `connect_config.html`:

| Configuration | Default |
|---|---|
| `listeners` | `http://:8083` |
| `rest.advertised.listener` | null |
| `rest.advertised.host.name` | null |
| `rest.advertised.port` | null |
| `rest.extension.classes` | "" |

### ACL requirements for workers

| Operation | Resource | Purpose |
|---|---|---|
| Create | Cluster | For `config.storage.topic`, `offset.storage.topic`, `status.storage.topic` |
| Read / Write | Topic | For internal storage topics |
| Read | Group | For `group.id` |

### ACL requirements for connectors

- **Source connectors**: need "WRITE permission to any topics that they need to write to"
- **Sink connectors**: need "READ permission to any topics they read from" plus "Group READ permission"

Sink connector group naming: "`connect-{name}`" where `name` is the connector identifier.

### Externalizing secrets

`FileConfigProvider`:

```
config.providers=file
config.providers.file.class=org.apache.kafka.common.config.provider.FileConfigProvider
```

Variable syntax: `${file:/path/to/file:property.key}`

`EnvVarConfigProvider`:

```
config.providers=env
config.providers.env.class=org.apache.kafka.common.config.provider.EnvVarConfigProvider
```

Variable syntax: `${env:ENVIRONMENT_VARIABLE}`

"Secrets are never persisted in connector configurations, logs, or in REST API requests and responses."

`InternalSecretConfigProvider` requires RBAC and uses the Confluent "Secret Registry" for encrypted credential storage.

> "Every worker in a Connect cluster must be able to resolve every variable in the worker configuration, and must be able to resolve all variables used in every connector configuration."
