# Apache Kafka 4.3 Docs — Security Overview & Listener Configuration

> **Nguồn (official):** https://kafka.apache.org/43/security/security-overview/ · https://kafka.apache.org/43/security/listener-configuration/
> **Tuần:** 5 — Security administration · **Loại:** Apache Kafka Docs (Security → Overview, Listener Configuration)
> ⚠️ Nội dung dưới đây được crawl tự động (WebFetch, có rút gọn) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- Kafka có **4 nhóm tính năng bảo mật**: (1) authentication cho client↔broker, broker↔broker, tool↔broker bằng **SSL hoặc SASL**; (2) **encryption in transit** bằng SSL, docs ghi rõ "*performance cost dependent on CPU and JVM*"; (3) authorization đọc/ghi cho client; (4) authorization **cắm ngoài được** (pluggable). Trang overview **không hề nhắc encryption at rest** — đây là bằng chứng docs cho câu hỏi "Kafka mã hoá dữ liệu trên đĩa không?" → **không có sẵn**.
- Lịch sử SASL theo version — hay bị hỏi "mechanism nào có từ bao giờ": **GSSAPI 0.9.0.0** · **PLAIN 0.10.0.0** · **SCRAM-SHA-256/512 0.10.2.0** · **OAUTHBEARER 2.0**.
- "*Security is optional — non-secured clusters are supported, as well as a mix of authenticated, unauthenticated, encrypted and non-encrypted clients*". Nghĩa là **một cluster chạy nhiều listener khác mức bảo mật cùng lúc** là hợp lệ và là kiến trúc chuẩn cho migration.
- Cú pháp listener: `{LISTENER_NAME}://{hostname}:{port}`, **ít nhất một listener** mỗi node. Tên listener **tự do đặt** (`CLIENT`, `INTERNAL`, `EXTERNAL`…); khi tên ≠ tên giao thức thì **bắt buộc** khai `listener.security.protocol.map`.
- **4 security protocol** (không phân biệt hoa thường): `PLAINTEXT` · `SSL` · `SASL_PLAINTEXT` · `SASL_SSL`. Nếu mỗi listener dùng một protocol riêng thì được phép lấy luôn tên protocol làm tên listener (`listeners=SSL://localhost:9092,PLAINTEXT://localhost:9093`).
- **Inter-broker**: chọn listener bằng `inter.broker.listener.name`. Nếu **không** khai thì Kafka rơi về `security.inter.broker.protocol`, mặc định **`PLAINTEXT`**. **Không được khai cả hai** cùng lúc. Mục đích chính của listener này là **replication**.
- **KRaft — broker-only node**: vẫn **phải** khai `controller.listener.names` (để gọi ra controller) nhưng **không** đưa listener controller vào `listeners`; thêm `controller.quorum.bootstrap.servers`.
- **KRaft — node combined (`broker,controller`)**: **cả hai** listener phải nằm trong `listeners`.
- Docs khẳng định: "*Controllers must use separate listener which is defined by the `controller.listener.names` configuration. **This cannot be set to the same value as the inter-broker listener***" → trùng tên là lỗi cấu hình, broker không lên.
- Cho phép **nhiều controller listener**; **cái đầu tiên trong danh sách** được dùng cho request đi ra. Đây chính là cơ chế **rolling update đổi security protocol hoặc đổi cổng của controller mà không downtime**.
- Host/port trong `controller.quorum.bootstrap.servers` **phải route được tới đúng controller listener đang expose**, nếu không quorum không hình thành.
- Quy ước: **tách riêng một listener cho client** để cô lập traffic nội bộ ở tầng mạng. Client nối vào listener không phải controller; "*Any requests that are bound for the controller will be forwarded*" (broker chuyển tiếp hộ qua Envelope).
- ⚠️ **Bẫy version:** `control.plane.listener.name` là listener của thời ZooKeeper (controller đẩy metadata sang broker). KRaft không dùng nó — thấy phương án nào nhắc `control.plane.listener.name` hoặc `zookeeper.connect` trong đề Kafka 4.x thì loại ngay.

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Security Overview

In release 0.9.0.0, the Kafka community added a number of features that, used either separately or together, increases security in a Kafka cluster. The following security measures are currently supported:

1. Authentication of connections to brokers from clients (producers and consumers), other brokers and tools, using either SSL or SASL. Kafka supports the following SASL mechanisms:
   - SASL/GSSAPI (Kerberos) — starting at version 0.9.0.0
   - SASL/PLAIN — starting at version 0.10.0.0
   - SASL/SCRAM-SHA-256 and SASL/SCRAM-SHA-512 — starting at version 0.10.2.0
   - SASL/OAUTHBEARER — starting at version 2.0
2. Encryption of data transferred between brokers and clients, between brokers, or between brokers and tools using SSL. Note that there is a performance degradation when SSL is enabled, the magnitude of which depends on the CPU type and the JVM implementation.
3. Authorization of read / write operations by clients.
4. Authorization is pluggable and integration with external authorization services is supported.

It's worth noting that security is optional — non-secured clusters are supported, as well as a mix of authenticated, unauthenticated, encrypted and non-encrypted clients.

### Listener Configuration

In order to secure a Kafka cluster, it is necessary to secure the channels that are used to communicate with the servers. Each server must define the set of listeners that are used to receive requests from clients as well as other servers. Each listener may be configured to authenticate clients using various mechanisms and to ensure traffic between the server and the client is encrypted. This section provides a primer for the configuration of listeners.

Kafka servers support listening for connections on multiple ports. This is configured through the `listeners` property in the server configuration, which accepts a comma-separated list of the listeners to enable. At least one listener must be defined on each server. The format of each listener defined in `listeners` is given below:

```
{LISTENER_NAME}://{hostname}:{port}
```

The `LISTENER_NAME` is usually a descriptive name which defines the purpose of the listener. For example, many configurations use a separate listener for client traffic, so they might refer to the corresponding listener as `CLIENT` in the configuration:

```
listeners=CLIENT://localhost:9092
```

The security protocol of each listener is defined in a separate configuration: `listener.security.protocol.map`. The value is a comma-separated list of each listener mapped to its security protocol. For example, the following value configuration specifies that the `CLIENT` listener will use SSL while the `BROKER` listener will use plaintext.

```
listener.security.protocol.map=CLIENT:SSL,BROKER:PLAINTEXT
```

Possible options (case-insensitive) for the security protocol are given below:

1. `PLAINTEXT`
2. `SSL`
3. `SASL_PLAINTEXT`
4. `SASL_SSL`

The plaintext protocol provides no security and does not require any additional configuration. In the following sections, this document covers how to configure the remaining protocols.

If each required listener uses a separate security protocol, it is also possible to use the security protocol name as the listener name in `listeners`. Using the example above, we could skip the definition of the `CLIENT` and `BROKER` listeners using the following definition:

```
listeners=SSL://localhost:9092,PLAINTEXT://localhost:9093
```

However, we recommend users to provide explicit names for the listeners since it makes the intended usage of each listener clearer.

Among the listeners in this list, it is possible to declare the listener to be used for inter-broker communication by setting the `inter.broker.listener.name` configuration to the name of the listener. The primary purpose of the inter-broker listener is partition replication. If not defined, then the inter-broker listener is determined by the security protocol defined by `security.inter.broker.protocol`, which defaults to `PLAINTEXT`.

In a KRaft cluster, a broker is any server which has the `broker` role enabled in `process.roles` and a controller is any server which has the `controller` role enabled. Listener configuration depends on the role. The listener defined by `inter.broker.listener.name` is used exclusively for requests between brokers. Controllers, on the other hand, must use separate listener which is defined by the `controller.listener.names` configuration. This cannot be set to the same value as the inter-broker listener.

Controllers receive requests both from other controllers and from brokers. For this reason, even if a server does not have the `controller` role enabled (i.e. it is just a broker), it must still define the controller listener along with any security properties that are needed to configure it. For example, we might use the following configuration on a standalone broker:

```
process.roles=broker
listeners=BROKER://localhost:9092
inter.broker.listener.name=BROKER
controller.quorum.bootstrap.servers=localhost:9093
controller.listener.names=CONTROLLER
listener.security.protocol.map=BROKER:SASL_SSL,CONTROLLER:SASL_SSL
```

The controller listener is still configured in this example to use the `SASL_SSL` security protocol, but it is not included in `listeners` since the broker does not expose the controller listener itself. The port that will be used in this case comes from the `controller.quorum.bootstrap.servers` configuration, which defines the full list of controllers.

For KRaft servers which have both the broker and controller role enabled, the configuration is similar. The only difference is that the controller listener must be included in `listeners`:

```
process.roles=broker,controller
listeners=BROKER://localhost:9092,CONTROLLER://localhost:9093
inter.broker.listener.name=BROKER
controller.quorum.bootstrap.servers=localhost:9093
controller.listener.names=CONTROLLER
listener.security.protocol.map=BROKER:SASL_SSL,CONTROLLER:SASL_SSL
```

It is a requirement for the port defined in `controller.quorum.bootstrap.servers` to exactly match one of the exposed controller listeners. For example, here the `CONTROLLER` listener is bound to port 9093. The connection string defined by `controller.quorum.bootstrap.servers` must then also use port 9093, as it does here.

The controller will accept requests on all listeners defined by `controller.listener.names`. Typically there would be just one controller listener, but it is possible to have more. For example, this provides a way to change the active listener from one port or security protocol to another through a roll of the cluster (one roll to expose the new listener, and one roll to remove the old listener). When multiple controller listeners are defined, the first one in the list will be used for outbound requests.

It is conventional in Kafka to use a separate listener for clients. This allows the inter-cluster listeners to be isolated at the network level. In the case of the controller listener in KRaft, the listener should be isolated since clients do not work with it anyway. Clients are expected to connect to any other listener configured on a broker. Any requests that are bound for the controller will be forwarded.
