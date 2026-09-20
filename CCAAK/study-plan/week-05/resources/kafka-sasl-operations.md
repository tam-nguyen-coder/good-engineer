# Apache Kafka 4.3 Docs — Authentication using SASL (góc vận hành credential)

> **Nguồn (official):** https://kafka.apache.org/43/security/authentication-using-sasl/
> **Tuần:** 5 — Security administration · **Loại:** Apache Kafka Docs (Security → Authentication using SASL)
> ⚠️ Nội dung dưới đây được crawl tự động (WebFetch, có rút gọn) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.
> 🔁 Bản CCDAK ở [`../../../../CCDAK/study-plan/week-07/resources/kafka-security-sasl.md`](../../../../CCDAK/study-plan/week-07/resources/kafka-security-sasl.md) nhìn từ **client**. File này nhìn từ **người giữ credential của cả cluster**.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- **Thứ tự ưu tiên JAAS phía broker (phải thuộc, hay ra đề):**
  1. `listener.name.{listenerName}.{saslMechanism}.sasl.jaas.config` (config property — **ưu tiên cao nhất**)
  2. Section `{listenerName}.KafkaServer` trong file JAAS tĩnh
  3. Section `KafkaServer` trong file JAAS tĩnh
  Phía client: `sasl.jaas.config` inline **thắng** file JAAS tĩnh section `KafkaClient`.
- Tên listener trong key JAAS viết **chữ thường**: `listener.name.sasl_ssl.scram-sha-256.sasl.jaas.config=...`. Điều này cho phép **mỗi listener bật một tập mechanism khác nhau** — đúng nhu cầu multi-tenant.
- Bật nhiều mechanism cùng lúc: `sasl.enabled.mechanisms=PLAIN,SCRAM-SHA-256,SCRAM-SHA-512`, mỗi mechanism cần một dòng JAAS riêng. Inter-broker chọn **đúng một** bằng `sasl.mechanism.inter.broker.protocol`; controller có key riêng `sasl.mechanism.controller.protocol` (**mặc định `GSSAPI`** — đối chiếu `kafka_config.html` 4.3).
- **SCRAM tối thiểu 4096 iterations.** Tạo user **trước khi cluster lên** (dùng cho inter-broker) bằng
  `kafka-storage.sh format -t <uuid> -c config/server.properties --add-scram 'SCRAM-SHA-256=[name="admin",password="admin-secret"]'`;
  tạo/sửa **lúc đang chạy** bằng
  `kafka-configs.sh --bootstrap-server localhost:9092 --alter --add-config 'SCRAM-SHA-256=[iterations=8192,password=alice-secret]' --entity-type users --entity-name alice --command-config client.properties`.
  Xem bằng `--describe`, thu hồi bằng `--delete-config`.
- Docs nói SCRAM "*stores credentials in the metadata log*" → **không có file credential trên đĩa broker**, xoay/thu hồi **không cần restart**, và bảo mật phụ thuộc vào việc **controller KRaft nằm trong mạng riêng**.
- **PLAIN** dùng credential **tĩnh trong JAAS của broker** → thêm/xoá user = **sửa file + restart broker** (trừ khi viết custom callback handler nối LDAP). Docs: PLAIN "*should be used only with SSL as transport layer*".
- **Quy trình đổi SASL mechanism trên cluster đang chạy** (kiểu câu list-order): (1) thêm mechanism mới vào `sasl.enabled.mechanisms` → (2) **bounce lần 1** toàn cluster → (3) đổi client sang mechanism mới → (4) đổi `sasl.mechanism.inter.broker.protocol` nếu cần rồi **bounce lần 2** → (5) gỡ mechanism cũ khỏi cấu hình và bounce lần cuối.
- **Delegation token**: bí mật ngắn hạn cho job phân tán; `delegation.token.secret.key` **phải giống hệt trên mọi broker và controller**; mặc định `delegation.token.expiry.time.ms` **86400000** (1 ngày), `delegation.token.max.lifetime.ms` **604800000** (7 ngày). Token chỉ được **tạo trên kênh đã SASL/SCRAM** (không tạo được bằng chính token).
- **OAUTHBEARER** production phải cắm callback handler hoặc JWT retriever thật; bản `unsecured` (JAAS `unsecuredLoginStringClaim_sub`) **chỉ dành cho dev**.
- Bổ sung cho admin: `connections.max.reauth.ms` mặc định **0** = **tắt re-authentication**. Khi tắt, **thu hồi credential không cắt được kết nối đang mở** — client vẫn chạy tới khi tự reconnect. Bật (ví dụ 3600000) để ép client xác thực lại định kỳ, đây mới là cách làm "revoke có hiệu lực thật".

---

## 📄 Nội dung (trích từ tài liệu gốc)

### JAAS configuration

Kafka uses the Java Authentication and Authorization Service (JAAS) for SASL configuration.

#### JAAS configuration for Kafka brokers

`KafkaServer` is the section name in the JAAS file used by each broker. This section provides SASL configuration options for the broker including any SASL client connections made by the broker for inter-broker communication. If multiple listeners are configured to use SASL, the section name may be prefixed with the listener name in lower-case followed by a period, e.g. `sasl_ssl.KafkaServer`.

JAAS configuration for Kafka brokers may alternatively be configured using the broker configuration property `sasl.jaas.config`. The property name must be prefixed with the listener prefix including the SASL mechanism, i.e. `listener.name.{listenerName}.{saslMechanism}.sasl.jaas.config`. Only one login module may be specified in the config value. If multiple mechanisms are configured on a listener, configs must be provided for each mechanism using the listener and mechanism prefix. For example:

```
listener.name.sasl_ssl.scram-sha-256.sasl.jaas.config=org.apache.kafka.common.security.scram.ScramLoginModule required \
    username="admin" \
    password="admin-secret";
listener.name.sasl_ssl.plain.sasl.jaas.config=org.apache.kafka.common.security.plain.PlainLoginModule required \
    username="admin" \
    password="admin-secret" \
    user_admin="admin-secret" \
    user_alice="alice-secret";
```

If JAAS configuration is defined at different levels, the order of precedence used is:

- Broker configuration property `listener.name.{listenerName}.{saslMechanism}.sasl.jaas.config`
- `{listenerName}.KafkaServer` section of static JAAS configuration
- `KafkaServer` section of static JAAS configuration

Note that ZooKeeper JAAS config is only applicable to legacy deployments.

#### JAAS configuration for Kafka clients

Clients may configure JAAS using the client configuration property `sasl.jaas.config` or using the static JAAS config file similar to brokers. Clients use the login section named `KafkaClient`. This option allows only one user for all client connections from a JVM.

### SASL configuration

SASL may be used with PLAINTEXT or SSL as the transport layer using the security protocol `SASL_PLAINTEXT` or `SASL_SSL` respectively. If `SASL_SSL` is used, then SSL must also be configured.

#### SASL mechanisms

Kafka supports the following SASL mechanisms:

- GSSAPI (Kerberos)
- PLAIN
- SCRAM-SHA-256
- SCRAM-SHA-512
- OAUTHBEARER

#### SASL configuration for Kafka brokers

1. Configure a SASL port in `server.properties`, by adding at least one of `SASL_PLAINTEXT` or `SASL_SSL` to the `listeners` parameter, which contains one or more comma-separated values:

```
listeners=SASL_PLAINTEXT://host.name:port
```

If you are only configuring a SASL port (or if you want the Kafka brokers to authenticate each other using SASL) then make sure you set the same SASL protocol for inter-broker communication:

```
security.inter.broker.protocol=SASL_PLAINTEXT (or SASL_SSL)
```

2. Select one or more supported mechanisms to enable in the broker and follow the steps to configure SASL for the mechanism. To enable multiple mechanisms in the broker, follow the steps for each mechanism.

### Authentication using SASL/SCRAM

Salted Challenge Response Authentication Mechanism (SCRAM) is a family of SASL mechanisms that addresses the security concerns with traditional mechanisms that perform username/password authentication like PLAIN and DIGEST-MD5. Kafka supports SCRAM-SHA-256 and SCRAM-SHA-512 which can be used with TLS to perform secure authentication.

The default implementation of SASL/SCRAM in Kafka stores SCRAM credentials in the metadata log. This is suitable for production use in installations where KRaft controllers are on a private network.

#### Creating SCRAM Credentials

The SCRAM implementation in Kafka uses the metadata log as credential store. Credentials can be created during the formatting of the storage directories, or using `kafka-configs.sh` once the cluster is running.

Create SCRAM credentials for the user `admin` when formatting storage:

```
bin/kafka-storage.sh format -t $(bin/kafka-storage.sh random-uuid) -c config/server.properties --add-scram 'SCRAM-SHA-256=[name="admin",password="admin-secret"]'
```

Create SCRAM credentials for user `alice` on a running cluster:

```
bin/kafka-configs.sh --bootstrap-server localhost:9092 --alter --add-config 'SCRAM-SHA-256=[iterations=8192,password=alice-secret]' --entity-type users --entity-name alice --command-config client.properties
```

The default iteration count of 4096 is used if iterations are not specified. A random salt is created and the SCRAM identity consisting of salt, iterations, StoredKey and ServerKey are stored. See RFC 5802 for details on SCRAM identity and the individual fields.

Existing credentials may be listed and deleted using the `--describe` and `--delete-config 'SCRAM-SHA-256'` options.

#### Configuring Kafka Brokers for SCRAM

1. Add a suitably modified JAAS file similar to the one below to each Kafka broker's config directory:

```
KafkaServer {
    org.apache.kafka.common.security.scram.ScramLoginModule required
    username="admin"
    password="admin-secret";
};
```

The properties `username` and `password` in the `KafkaServer` section are used by the broker to initiate connections to other brokers. In this example, `admin` is the user for inter-broker communication.

2. Configure SASL port and SASL mechanisms in `server.properties`:

```
listeners=SASL_SSL://host.name:port
security.inter.broker.protocol=SASL_SSL
sasl.mechanism.inter.broker.protocol=SCRAM-SHA-256 (or SCRAM-SHA-512)
sasl.enabled.mechanisms=SCRAM-SHA-256 (or SCRAM-SHA-512)
```

#### Security Considerations for SASL/SCRAM

- The default implementation of SASL/SCRAM in Kafka stores SCRAM credentials in the metadata log. This is suitable for production use in installations where KRaft controllers are on a private network.
- Kafka supports only the strong hash functions SHA-256 and SHA-512 with a minimum iteration count of 4096. Strong hash functions combined with strong passwords and high iteration counts protect against brute force attacks if the metadata log security is compromised.
- SCRAM should be used only with TLS-encryption to prevent interception of SCRAM exchanges. This protects against dictionary or brute force attacks and against impersonation if the metadata log is compromised.

### Authentication using SASL/PLAIN

SASL/PLAIN is a simple username/password authentication mechanism that is typically used with TLS for encryption to implement secure authentication. Kafka supports a default implementation for SASL/PLAIN which can be extended for production use as described here.

The username is used as the authenticated Principal for configuration of ACLs etc.

```
KafkaServer {
    org.apache.kafka.common.security.plain.PlainLoginModule required
    username="admin"
    password="admin-secret"
    user_admin="admin-secret"
    user_alice="alice-secret";
};
```

This configuration defines two users (`admin` and `alice`). The properties `username` and `password` in the `KafkaServer` section are used by the broker to initiate connections to other brokers. In this example, `admin` is the user for inter-broker communication. The set of properties `user_userName` defines the passwords for all users that connect to the broker and the broker validates all client connections including those from other brokers using these properties.

SASL/PLAIN should be used only with SSL as transport layer to ensure that clear passwords are not transmitted on the wire without encryption.

The default implementation of SASL/PLAIN in Kafka specifies usernames and passwords in the JAAS configuration file as shown here. From Kafka version 2.0 onwards, you can avoid storing clear passwords on disk by configuring your own callback handlers that obtain username and password from an external source using the configuration options `sasl.server.callback.handler.class` and `sasl.client.callback.handler.class`.

In production systems, external authentication servers may implement password authentication. Kafka brokers can be integrated with these servers by adding your own callback handlers.

### Enabling multiple SASL mechanisms in a broker

1. Specify configuration for the login modules of all enabled mechanisms in the `KafkaServer` section of the JAAS config file (or via the listener-and-mechanism-prefixed `sasl.jaas.config` properties).
2. Enable the SASL mechanisms in `server.properties`: `sasl.enabled.mechanisms=PLAIN,SCRAM-SHA-256`
3. Specify the SASL security protocol and mechanism for inter-broker communication in `server.properties` if required: `security.inter.broker.protocol=SASL_PLAINTEXT` (or `SASL_SSL`), `sasl.mechanism.inter.broker.protocol=GSSAPI` (or one of the other enabled mechanisms)
4. Follow the mechanism-specific steps to configure SASL for the enabled mechanisms.

### Modifying SASL mechanism in a Running Cluster

SASL mechanism can be modified in a running cluster using the following sequence:

1. Enable new SASL mechanism by adding the mechanism to `sasl.enabled.mechanisms` in `server.properties` for each broker. Update JAAS config file to include both mechanisms as described here. Incrementally bounce the cluster nodes.
2. Restart clients using the new mechanism.
3. To change the mechanism of inter-broker communication (if this is required), set `sasl.mechanism.inter.broker.protocol` in `server.properties` to the new mechanism and incrementally bounce the cluster again.
4. To remove old mechanism (if this is required), remove the old mechanism from `sasl.enabled.mechanisms` in `server.properties` and remove the entries for the old mechanism from JAAS config file. Incrementally bounce the cluster again.

### Authentication using Delegation Tokens

Delegation token based authentication is a lightweight authentication mechanism to complement existing SASL/SSL methods. Delegation tokens are shared secrets between Kafka brokers and clients. Delegation tokens will help processing frameworks to distribute the workload to available workers in a secure environment without the added cost of distributing Kerberos TGT/keytabs or keystores when 2-way SSL is used.

Note that the `delegation.token.secret.key` must be configured with the same value across all brokers and controllers. If the secret is not set or set to empty string, delegation token authentication and API operations will fail.

Tokens can be created, renewed, expired and described using the `kafka-delegation-tokens.sh` tool. Clients authenticate using SASL/SCRAM with the token HMAC as the password and `tokenauth="true"` in the JAAS configuration.
