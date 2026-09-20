# Apache Kafka 4.3 Docs — Security Overview & Listener Configuration

> **Nguồn (official):** https://kafka.apache.org/43/security/security-overview/ · https://kafka.apache.org/43/security/listener-configuration/
> **Tuần:** 7 — Security & Testing · **Loại:** Apache Kafka Docs (Security → Overview + Listener Configuration)
> ⚠️ Nội dung dưới đây được crawl tự động (qua curl + WebFetch, có rút gọn) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- Kafka có **3 trụ security**: **authentication** (SSL cert hoặc SASL) cho kết nối client↔broker, broker↔broker, tool↔broker; **encryption** in-transit bằng SSL/TLS (có **giảm hiệu năng**, mức độ tuỳ CPU + JVM); **authorization** read/write bằng ACL, **pluggable** (tích hợp dịch vụ ngoài).
- 4 nhóm SASL mechanism và version xuất hiện: **GSSAPI** (Kerberos, 0.9.0.0) · **PLAIN** (0.10.0.0) · **SCRAM-SHA-256/512** (0.10.2.0) · **OAUTHBEARER** (2.0). Không có "encryption at rest" trong danh sách → Kafka **không** mã hoá đĩa built-in.
- **Security là tuỳ chọn**: cluster không bảo mật vẫn hỗ trợ, và có thể **trộn** client authenticated/unauthenticated, encrypted/non-encrypted trên cùng cluster (nhiều listener).
- Cú pháp listener: `{LISTENER_NAME}://{hostname}:{port}`; **ít nhất 1 listener** mỗi server; tên listener tự do (`CLIENT`, `BROKER`, `INTERNAL`…), map sang giao thức qua **`listener.security.protocol.map`** (ví dụ `CLIENT:SSL,BROKER:PLAINTEXT`).
- 4 giá trị security protocol (**không phân biệt hoa thường**): `PLAINTEXT` · `SSL` · `SASL_PLAINTEXT` · `SASL_SSL`. Nếu mỗi listener dùng giao thức khác nhau có thể đặt **tên listener = tên giao thức** và bỏ map, nhưng docs **khuyến nghị đặt tên rõ nghĩa**.
- **`inter.broker.listener.name`** chọn listener cho replication broker↔broker; nếu không set thì suy ra từ `security.inter.broker.protocol` (mặc định **PLAINTEXT**). **Không set cả hai**.
- KRaft: controller phải dùng listener **riêng** qua **`controller.listener.names`**, **không được trùng** inter-broker listener. Broker-only (`process.roles=broker`) **vẫn phải khai** `controller.listener.names` + security cho nó dù không đưa vào `listeners`; combined node phải đưa `CONTROLLER://…` vào `listeners`.
- `controller.quorum.bootstrap.servers` phải trỏ tới đúng host:port của controller listener đang mở. Nhiều controller listener được phép; **listener đầu tiên** trong danh sách dùng cho request đi ra.
- Thông lệ: **listener riêng cho client**, tách mạng với listener nội bộ; client **không bao giờ** nối vào controller listener — request cần controller sẽ được broker **forward** (Envelope).
- Quy trình đổi listener controller không downtime: 2 vòng roll (1 vòng thêm listener mới, 1 vòng bỏ listener cũ).

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Security Overview

The following security measures are currently supported:

- Authentication of connections to brokers from clients (producers and consumers), other brokers and tools, using either SSL or SASL. Kafka supports the following SASL mechanisms:
  - SASL/GSSAPI (Kerberos) - starting at version 0.9.0.0
  - SASL/PLAIN - starting at version 0.10.0.0
  - SASL/SCRAM-SHA-256 and SASL/SCRAM-SHA-512 - starting at version 0.10.2.0
  - SASL/OAUTHBEARER - starting at version 2.0
- Encryption of data transferred between brokers and clients, between brokers, or between brokers and tools using SSL (Note that there is a performance degradation when SSL is enabled, the magnitude of which depends on the CPU type and the JVM implementation.)
- Authorization of read / write operations by clients
- Authorization is pluggable and integration with external authorization services is supported

It's worth noting that security is optional - non-secured clusters are supported, as well as a mix of authenticated, unauthenticated, encrypted and non-encrypted clients. The guides below explain how to configure and use the security features in both clients and brokers.

### Listener Configuration

In order to secure a Kafka cluster, it is necessary to secure the channels that are used to communicate with the servers. Each server must define the set of listeners that are used to receive requests from clients as well as other servers. Each listener may be configured to authenticate clients using various mechanisms and to ensure traffic between the server and the client is encrypted. This section provides a primer for the configuration of listeners.

Kafka servers support listening for connections on multiple ports. This is configured through the `listeners` property in the server configuration, which accepts a comma-separated list of the listeners to enable. At least one listener must be defined on each server. The format of each listener defined in `listeners` is given below:

```
{LISTENER_NAME}://{hostname}:{port}
```

The `LISTENER_NAME` is usually a descriptive name which defines the purpose of the listener. For example, many configurations use a separate listener for client traffic, so they might refer to the corresponding listener as `CLIENT` in the configuration:

```properties
listeners=CLIENT://localhost:9092
```

The security protocol of each listener is defined in a separate configuration: `listener.security.protocol.map`. The value is a comma-separated list of each listener mapped to its security protocol. For example, the follow value configuration specifies that the `CLIENT` listener will use SSL while the `BROKER` listener will use plaintext.

```properties
listener.security.protocol.map=CLIENT:SSL,BROKER:PLAINTEXT
```

Possible options (case-insensitive) for the security protocol are given below:

- PLAINTEXT
- SSL
- SASL_PLAINTEXT
- SASL_SSL

The plaintext protocol provides no security and does not require any additional configuration. In the following sections, this document covers how to configure the remaining protocols.

If each required listener uses a separate security protocol, it is also possible to use the security protocol name as the listener name in `listeners`. Using the example above, we could skip the definition of the `CLIENT` and `BROKER` listeners using the following definition:

```properties
listeners=SSL://localhost:9092,PLAINTEXT://localhost:9093
```

However, we recommend users to provide explicit names for the listeners since it makes the intended usage of each listener clearer.

Among the listeners in this list, it is possible to declare the listener to be used for inter-broker communication by setting the `inter.broker.listener.name` configuration to the name of the listener. The primary purpose of the inter-broker listener is partition replication. If not defined, then the inter-broker listener is determined by the security protocol defined by `security.inter.broker.protocol`, which defaults to `PLAINTEXT`.

In a KRaft cluster, a broker is any server which has the `broker` role enabled in `process.roles` and a controller is any server which has the `controller` role enabled. Listener configuration depends on the role. The listener defined by `inter.broker.listener.name` is used exclusively for requests between brokers. Controllers, on the other hand, must use separate listener which is defined by the `controller.listener.names` configuration. This cannot be set to the same value as the inter-broker listener.

Controllers receive requests both from other controllers and from brokers. For this reason, even if a server does not have the `controller` role enabled (i.e. it is just a broker), it must still define the controller listener along with any security properties that are needed to configure it. For example, we might use the following configuration on a standalone broker:

```properties
process.roles=broker
listeners=BROKER://localhost:9092
inter.broker.listener.name=BROKER
controller.quorum.bootstrap.servers=localhost:9093
controller.listener.names=CONTROLLER
listener.security.protocol.map=BROKER:SASL_SSL,CONTROLLER:SASL_SSL
```

The controller listener is still configured in this example to use the `SASL_SSL` security protocol, but it is not included in `listeners` since the broker does not expose the controller listener itself. The port that will be used in this case comes from the `controller.quorum.voters` configuration, which defines the complete list of controllers.

For KRaft servers which have both the broker and controller role enabled, the configuration is similar. The only difference is that the controller listener must be included in `listeners`:

```properties
process.roles=broker,controller
listeners=BROKER://localhost:9092,CONTROLLER://localhost:9093
inter.broker.listener.name=BROKER
controller.quorum.bootstrap.servers=localhost:9093
controller.listener.names=CONTROLLER
listener.security.protocol.map=BROKER:SASL_SSL,CONTROLLER:SASL_SSL
```

It is a requirement that the host and port defined in `controller.quorum.bootstrap.servers` is routed to the exposed controller listeners. For example, here the `CONTROLLER` listener is bound to `localhost:9093`. The connection string defined by `controller.quorum.bootstrap.servers` must then also use `localhost:9093`, as it does here.

The controller will accept requests on all listeners defined by `controller.listener.names`. Typically there would be just one controller listener, but it is possible to have more. For example, this provides a way to change the active listener from one port or security protocol to another through a roll of the cluster (one roll to expose the new listener, and one roll to remove the old listener). When multiple controller listeners are defined, the first one in the list will be used for outbound requests.

It is conventional in Kafka to use a separate listener for clients. This allows the inter-cluster listeners to be isolated at the network level. In the case of the controller listener in KRaft, the listener should be isolated since clients do not work with it anyway. Clients are expected to connect to any other listener configured on a broker. Any requests that are bound for the controller will be forwarded as described below.

In the following section, this document covers how to enable SSL on a listener for encryption as well as authentication. The subsequent section will then cover additional authentication mechanisms using SASL.

### Ghi chú thêm (tổng hợp từ docs, không nằm trong 2 trang trên)

- `advertised.listeners` (Broker Configs): địa chỉ broker **công bố cho client** trong metadata; nếu khác `listeners` (Docker/NAT/cloud) phải set riêng, cùng định dạng `NAME://host:port`. Client dùng `bootstrap.servers` chỉ để lấy metadata, sau đó nối tới địa chỉ advertised.
- Cấu hình theo listener: mọi config SSL/SASL có thể override bằng prefix `listener.name.<tên-listener-viết-thường>.<config>` (ví dụ `listener.name.external.ssl.keystore.location`), cho phép mỗi listener có keystore/JAAS riêng.
- Phía client, `security.protocol` **phải khớp** giao thức của cổng đang nối. Client `PLAINTEXT` nối vào cổng `SSL` → broker log `SSL handshake failed`, client thấy `Bootstrap broker ... disconnected` — đây là lỗi **lệch giao thức**, không phải lỗi ACL.
