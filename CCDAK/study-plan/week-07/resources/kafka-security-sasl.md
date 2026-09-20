# Apache Kafka 4.3 Docs — Authentication using SASL (PLAIN / SCRAM / GSSAPI / OAUTHBEARER / Delegation Tokens)

> **Nguồn (official):** https://kafka.apache.org/43/security/authentication-using-sasl/
> **Tuần:** 7 — Security & Testing · **Loại:** Apache Kafka Docs (Security → Authentication using SASL)
> ⚠️ Nội dung dưới đây được crawl tự động (qua curl + WebFetch, có rút gọn) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- SASL đi trên transport `SASL_PLAINTEXT` hoặc `SASL_SSL`; dùng `SASL_SSL` thì **phải cấu hình SSL** kèm. 5 mechanism: **GSSAPI, PLAIN, SCRAM-SHA-256, SCRAM-SHA-512, OAUTHBEARER**. Broker liệt kê trong `sasl.enabled.mechanisms` (nhiều được), inter-broker chỉ **1** trong `sasl.mechanism.inter.broker.protocol`.
- **JAAS broker**: ưu tiên (1) property `listener.name.{listener}.{mechanism}.sasl.jaas.config` → (2) section `{listener}.KafkaServer` trong file tĩnh → (3) section `KafkaServer`. Mỗi property chỉ **1 login module**; nhiều mechanism trên 1 listener → mỗi mechanism 1 property.
- **JAAS client**: property **`sasl.jaas.config`** (khuyến nghị — mỗi client 1 credential trong cùng JVM) **thắng** file tĩnh `-Djava.security.auth.login.config` (section `KafkaClient`, 1 user cho cả JVM). Giá trị phải kết thúc bằng **`;`**.
- 4 login module phải thuộc: `com.sun.security.auth.module.Krb5LoginModule` (GSSAPI) · `org.apache.kafka.common.security.plain.PlainLoginModule` · `org.apache.kafka.common.security.scram.ScramLoginModule` · `org.apache.kafka.common.security.oauthbearer.OAuthBearerLoginModule`.
- **PLAIN**: user/password **tĩnh** trong JAAS broker dạng `user_alice="alice-secret"`; `username`/`password` trong section broker là credential **inter-broker**. **Chỉ dùng với SSL** (password đi rõ). Muốn không lưu password rõ / xác thực bằng server ngoài → `sasl.server.callback.handler.class` (từ 2.0).
- **SCRAM (RFC 5802)**: credential (salt, iterations, StoredKey, ServerKey) lưu trong **metadata log**. Tạo **trước khi broker lên** cho inter-broker bằng `kafka-storage.sh format --add-scram 'SCRAM-SHA-256=[name="admin",password="admin-secret"]'`; tạo/đổi **runtime** cho client bằng `kafka-configs.sh --alter --add-config 'SCRAM-SHA-256=[iterations=8192,password=alice-secret]' --entity-type users --entity-name alice`; xem `--describe`, xoá `--delete-config 'SCRAM-SHA-256'`. Iterations mặc định **4096** (tối thiểu 4096); vẫn **nên đi với TLS**.
- **GSSAPI/Kerberos**: keytab + principal `kafka/hostname@REALM`; broker `sasl.kerberos.service.name=kafka`; client dùng keytab hoặc `useTicketCache=true`. Reverse DNS chậm nếu không dùng FQDN trong `bootstrap.servers`/`advertised.listeners`.
- **OAUTHBEARER (RFC 7628)**: bản **mặc định = Unsecured JWT**, **chỉ non-production** (`unsecuredLoginStringClaim_sub="alice"`, token sống 3600 s). Production: broker `OAuthBearerValidatorCallbackHandler` + `sasl.oauthbearer.jwks.endpoint.url`, `expected.audience/issuer`; client `sasl.oauthbearer.token.endpoint.url` + client credentials (`client.id`/`client.secret`) **hoặc client assertion** (RFC 7523, KIP-1258: `sasl.oauthbearer.assertion.private.key.file`, `.algorithm=RS256`, `.claim.iss/sub/aud`) **hoặc** `jwt-bearer` với `sasl.oauthbearer.jwt.retriever.class=JwtBearerJwtRetriever`. Thứ tự ưu tiên: file assertion > assertion tự sinh > client secret (chọn 1 lần lúc config, không fallback runtime).
- Principal = `username` (PLAIN/SCRAM) · phần primary của Kerberos principal (GSSAPI, sửa bằng `sasl.kerberos.principal.to.local.rules`) · `principalName` của token (OAUTHBEARER) · **owner** của token (delegation token).
- **Delegation token (KIP-48)**: shared secret broker↔client cho framework phân tán (Spark/Flink) thay việc phát keytab/keystore; **đi trên SCRAM** với `tokenauth="true"`, `username`=tokenID, `password`=HMAC; `delegation.token.secret.key` **giống trên mọi broker và controller**; renew mỗi **24 h**, tối đa **7 ngày** (`delegation.token.expiry.time.ms`, `delegation.token.max.lifetime.ms`); tạo bằng `kafka-delegation-tokens.sh --create`; **không** tạo được token khi đã auth bằng token.
- Đổi mechanism trên cluster đang chạy: thêm mechanism mới vào `sasl.enabled.mechanisms` + JAAS → **rolling bounce** → chuyển client → đổi `sasl.mechanism.inter.broker.protocol` (bounce) → gỡ mechanism cũ (bounce).

---

## 📄 Nội dung (trích từ tài liệu gốc)

### JAAS configuration

Kafka uses the Java Authentication and Authorization Service (JAAS) for SASL configuration.

#### JAAS configuration for Kafka brokers

`KafkaServer` is the section name in the JAAS file used by each KafkaServer/Broker. This section provides SASL configuration options for the broker including any SASL client connections made by the broker for inter-broker communication. If multiple listeners are configured to use SASL, the section name may be prefixed with the listener name in lower-case followed by a period, e.g. `sasl_ssl.KafkaServer`.

Brokers may also configure JAAS using the broker configuration property `sasl.jaas.config`. The property name must be prefixed with the listener prefix including the SASL mechanism, i.e. `listener.name.{listenerName}.{saslMechanism}.sasl.jaas.config`. Only one login module may be specified in the config value. If multiple mechanisms are configured on a listener, configs must be provided for each mechanism using the listener and mechanism prefix. For example,

```properties
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

1. Broker configuration property `listener.name.{listenerName}.{saslMechanism}.sasl.jaas.config`
2. `{listenerName}.KafkaServer` section of static JAAS configuration
3. `KafkaServer` section of static JAAS configuration

#### JAAS configuration for Kafka clients

Clients may configure JAAS using the client configuration property `sasl.jaas.config` or using the static JAAS config file similar to brokers.

Clients may specify JAAS configuration as a producer or consumer property without creating a physical configuration file. This mode also enables different producers and consumers within the same JVM to use different credentials by specifying different properties for each client. If both static JAAS configuration system property `java.security.auth.login.config` and client property `sasl.jaas.config` are specified, the client property will be used.

To configure SASL authentication on the clients using static JAAS config file, add a JAAS config file with a client login section named `KafkaClient`, e.g.:

```
KafkaClient {
    com.sun.security.auth.module.Krb5LoginModule required
    useKeyTab=true
    storeKey=true
    keyTab="/etc/security/keytabs/kafka_client.keytab"
    principal="kafka-client-1@EXAMPLE.COM";
};
```

and pass the JAAS config file location as JVM parameter to each client JVM: `-Djava.security.auth.login.config=/etc/kafka/kafka_client_jaas.conf`.

### SASL configuration

SASL may be used with PLAINTEXT or SSL as the transport layer using the security protocol `SASL_PLAINTEXT` or `SASL_SSL` respectively. If `SASL_SSL` is used, then SSL must also be configured.

Kafka supports the following SASL mechanisms: GSSAPI (Kerberos), PLAIN, SCRAM-SHA-256, SCRAM-SHA-512, OAUTHBEARER.

**SASL configuration for Kafka brokers:** Configure a SASL port in server.properties, by adding at least one of `SASL_PLAINTEXT` or `SASL_SSL` to the `listeners` parameter:

```properties
listeners=SASL_PLAINTEXT://host.name:port
```

If you are only configuring a SASL port (or if you want the Kafka brokers to authenticate each other using SASL) then make sure you set the same SASL protocol for inter-broker communication: `security.inter.broker.protocol=SASL_PLAINTEXT (or SASL_SSL)`. Select one or more supported mechanisms to enable in the broker and follow the steps to configure SASL for the mechanism.

> Note: When establishing connections to brokers via SASL, clients may perform a reverse DNS lookup of the broker address. Due to how the JRE implements reverse DNS lookups, clients may observe slow SASL handshakes if fully qualified domain names are not used, for both the client's `bootstrap.servers` and a broker's `advertised.listeners`.

### Authentication using SASL/PLAIN

SASL/PLAIN is a simple username/password authentication mechanism that is typically used with TLS for encryption to implement secure authentication. Under the default implementation of `principal.builder.class`, the username is used as the authenticated Principal for configuration of ACLs etc.

**Configuring Kafka Brokers** — add a JAAS file (`kafka_server_jaas.conf`):

```
KafkaServer {
    org.apache.kafka.common.security.plain.PlainLoginModule required
    username="admin"
    password="admin-secret"
    user_admin="admin-secret"
    user_alice="alice-secret";
};
```

This configuration defines two users (admin and alice). The properties `username` and `password` in the `KafkaServer` section are used by the broker to initiate connections to other brokers. In this example, admin is the user for inter-broker communication. The set of properties `user_userName` defines the passwords for all users that connect to the broker and the broker validates all client connections including those from other brokers using these properties. Pass the JAAS config file location as JVM parameter: `-Djava.security.auth.login.config=/etc/kafka/kafka_server_jaas.conf`, then in server.properties:

```properties
listeners=SASL_SSL://host.name:port
security.inter.broker.protocol=SASL_SSL
sasl.mechanism.inter.broker.protocol=PLAIN
sasl.enabled.mechanisms=PLAIN
```

**Configuring Kafka Clients:**

```properties
sasl.jaas.config=org.apache.kafka.common.security.plain.PlainLoginModule required \
    username="alice" \
    password="alice-secret";
security.protocol=SASL_SSL
sasl.mechanism=PLAIN
```

**Use of SASL/PLAIN in production:**

- SASL/PLAIN should be used only with SSL as transport layer to ensure that clear passwords are not transmitted on the wire without encryption.
- The default implementation of SASL/PLAIN in Kafka specifies usernames and passwords in the JAAS configuration file. From Kafka version 2.0 onwards, you can avoid storing clear passwords on disk by configuring your own callback handlers that obtain username and password from an external source using the configuration options `sasl.server.callback.handler.class` and `sasl.client.callback.handler.class`.
- In production systems, external authentication servers may implement password authentication. From Kafka version 2.0 onwards, you can plug in your own callback handlers that use external authentication servers for password verification by configuring `sasl.server.callback.handler.class`.

### Authentication using SASL/SCRAM

Salted Challenge Response Authentication Mechanism (SCRAM) is a family of SASL mechanisms that addresses the security concerns with traditional mechanisms that perform username/password authentication like PLAIN and DIGEST-MD5. The mechanism is defined in RFC 5802. Kafka supports SCRAM-SHA-256 and SCRAM-SHA-512 which can be used with TLS to perform secure authentication. Under the default implementation of `principal.builder.class`, the username is used as the authenticated Principal for configuration of ACLs etc. The default SCRAM implementation in Kafka stores SCRAM credentials in the metadata log.

#### Creating SCRAM Credentials

The SCRAM implementation in Kafka uses the metadata log as credential store. Credentials can be created in the metadata log using `kafka-storage.sh` or `kafka-configs.sh`. For each SCRAM mechanism enabled, credentials must be created by adding a config with the mechanism name. Credentials for inter-broker communication must be created before Kafka brokers are started. `kafka-storage.sh` can format storage with initial credentials. Client credentials may be created and updated dynamically and updated credentials will be used to authenticate new connections. `kafka-configs.sh` can be used to create and update credentials after Kafka brokers are started.

Create initial SCRAM credentials for user admin with password admin-secret:

```bash
$ bin/kafka-storage.sh format -t $(bin/kafka-storage.sh random-uuid) -c config/server.properties --add-scram 'SCRAM-SHA-256=[name="admin",password="admin-secret"]'
```

Create SCRAM credentials for user alice with password alice-secret:

```bash
$ bin/kafka-configs.sh --bootstrap-server localhost:9092 --alter --add-config 'SCRAM-SHA-256=[iterations=8192,password=alice-secret]' --entity-type users --entity-name alice --command-config client.properties
```

The default iteration count of 4096 is used if iterations are not specified. A random salt is created if it's not specified. The SCRAM identity consisting of salt, iterations, StoredKey and ServerKey are stored in the metadata log.

Existing credentials may be listed using the `--describe` option:

```bash
$ bin/kafka-configs.sh --bootstrap-server localhost:9092 --describe --entity-type users --entity-name alice --command-config client.properties
```

Credentials may be deleted for one or more SCRAM mechanisms using the `--alter --delete-config` option:

```bash
$ bin/kafka-configs.sh --bootstrap-server localhost:9092 --alter --delete-config 'SCRAM-SHA-256' --entity-type users --entity-name alice --command-config client.properties
```

**Configuring Kafka Brokers:**

```
KafkaServer {
    org.apache.kafka.common.security.scram.ScramLoginModule required
    username="admin"
    password="admin-secret";
};
```

```properties
listeners=SASL_SSL://host.name:port
security.inter.broker.protocol=SASL_SSL
sasl.mechanism.inter.broker.protocol=SCRAM-SHA-256 (or SCRAM-SHA-512)
sasl.enabled.mechanisms=SCRAM-SHA-256 (or SCRAM-SHA-512)
```

**Configuring Kafka Clients:**

```properties
sasl.jaas.config=org.apache.kafka.common.security.scram.ScramLoginModule required \
    username="alice" \
    password="alice-secret";
security.protocol=SASL_SSL
sasl.mechanism=SCRAM-SHA-256 (or SCRAM-SHA-512)
```

**Security Considerations for SASL/SCRAM:**

- The default implementation of SASL/SCRAM in Kafka stores SCRAM credentials in the metadata log. This is suitable for production use in installations where KRaft controllers are secure and on a private network.
- Kafka supports only the strong hash functions SHA-256 and SHA-512 with a minimum iteration count of 4096. Strong hash functions combined with strong passwords and high iteration counts protect against brute force attacks if KRaft controllers security is compromised.
- SCRAM should be used only with TLS-encryption to prevent interception of SCRAM exchanges. This protects against dictionary or brute force attacks and against impersonation if KRaft controllers security is compromised.
- From Kafka version 2.0 onwards, the default SASL/SCRAM credential store may be overridden using custom callback handlers by configuring `sasl.server.callback.handler.class`.

### Authentication using SASL/Kerberos (GSSAPI) — tóm lược

Prerequisites: a Kerberos server (KDC) and a principal for each broker of the form `kafka/{hostname}@{REALM}` with a keytab. Broker JAAS uses `com.sun.security.auth.module.Krb5LoginModule required useKeyTab=true storeKey=true keyTab="/etc/security/keytabs/kafka_server.keytab" principal="kafka/kafka1.hostname.com@EXAMPLE.COM";`. Broker config: `sasl.mechanism.inter.broker.protocol=GSSAPI`, `sasl.enabled.mechanisms=GSSAPI`, `sasl.kerberos.service.name=kafka` (must match the primary name of the broker principals). Clients use their own keytab/principal or `useTicketCache=true`, with `security.protocol=SASL_SSL` (or `SASL_PLAINTEXT`), `sasl.mechanism=GSSAPI`, `sasl.kerberos.service.name=kafka`.

### Authentication using SASL/OAUTHBEARER

The SASL OAUTHBEARER mechanism enables the use of the OAuth 2 framework in a SASL (i.e. a non-HTTP) context; it is defined in RFC 7628. The default OAUTHBEARER implementation in Kafka creates and validates Unsecured JSON Web Tokens and is only suitable for use in non-production Kafka installations. Recent versions of Apache Kafka have added production-ready OAUTHBEARER implementations that support interaction with an OAuth 2.0-standards compliant identity provider. Under the default implementation of `principal.builder.class`, the `principalName` of `OAuthBearerToken` is used as the authenticated Principal for configuration of ACLs etc.

**Non-production brokers** (Unsecured JWT):

```
KafkaServer {
    org.apache.kafka.common.security.oauthbearer.OAuthBearerLoginModule required
    unsecuredLoginStringClaim_sub="admin";
};
```

```properties
listeners=SASL_SSL://host.name:port (or SASL_PLAINTEXT if non-production)
security.inter.broker.protocol=SASL_SSL (or SASL_PLAINTEXT if non-production)
sasl.mechanism.inter.broker.protocol=OAUTHBEARER
sasl.enabled.mechanisms=OAUTHBEARER
```

**Production brokers:**

```properties
listeners=SASL_SSL://host.name:port
security.inter.broker.protocol=SASL_SSL
sasl.mechanism.inter.broker.protocol=OAUTHBEARER
sasl.enabled.mechanisms=OAUTHBEARER
listener.name.<listener name>.oauthbearer.sasl.server.callback.handler.class=org.apache.kafka.common.security.oauthbearer.OAuthBearerValidatorCallbackHandler
listener.name.<listener name>.oauthbearer.sasl.oauthbearer.jwks.endpoint.url=https://example.com/oauth2/v1/keys
```

The OAUTHBEARER broker configuration includes: `sasl.oauthbearer.clock.skew.seconds`, `sasl.oauthbearer.expected.audience`, `sasl.oauthbearer.expected.issuer`, `sasl.oauthbearer.jwks.endpoint.refresh.ms`, `sasl.oauthbearer.jwks.endpoint.retry.backoff.max.ms`, `sasl.oauthbearer.jwks.endpoint.retry.backoff.ms`, `sasl.oauthbearer.jwks.endpoint.url`, `sasl.oauthbearer.scope.claim.name`, `sasl.oauthbearer.sub.claim.name`.

**Non-production clients:**

```properties
sasl.jaas.config=org.apache.kafka.common.security.oauthbearer.OAuthBearerLoginModule required \
    unsecuredLoginStringClaim_sub="alice";
security.protocol=SASL_SSL (or SASL_PLAINTEXT if non-production)
sasl.mechanism=OAUTHBEARER
```

`unsecuredLoginLifetimeSeconds` — set to an integer value if the token expiration is to be set to something other than the default value of 3600 seconds (which is 1 hour). The default implementation of SASL/OAUTHBEARER depends on the jackson-databind library (optional dependency).

**Production clients** — `sasl.jaas.config=org.apache.kafka.common.security.oauthbearer.OAuthBearerLoginModule required ;`. The `sasl.oauthbearer.jwt.retriever.class` property defaults to `DefaultJwtRetriever`, which automatically delegates to `ClientCredentialsJwtRetriever` for HTTP/HTTPS token endpoint URLs and `FileJwtRetriever` for `file://` URLs. If using the OAuth `client_credentials` grant type with a client secret:

```properties
security.protocol=SASL_SSL
sasl.mechanism=OAUTHBEARER
sasl.oauthbearer.client.credentials.client.id=jdoe
sasl.oauthbearer.client.credentials.client.secret=$3cr3+
sasl.oauthbearer.scope=my-application-scope
sasl.oauthbearer.token.endpoint.url=https://example.com/oauth2/v1/token
```

Alternatively, the `client_credentials` grant type also supports client assertion authentication as defined in RFC 7523. Instead of sending a client secret, the client authenticates by presenting a signed JWT assertion to the OAuth identity provider. This provides enhanced security since private keys never leave the client and assertions are short-lived. See KIP-1258 for details.

```properties
security.protocol=SASL_SSL
sasl.mechanism=OAUTHBEARER
sasl.oauthbearer.token.endpoint.url=https://example.com/oauth2/v1/token
sasl.oauthbearer.assertion.private.key.file=/path/to/private-key.pem
sasl.oauthbearer.assertion.algorithm=RS256
sasl.oauthbearer.assertion.claim.iss=my-kafka-client
sasl.oauthbearer.assertion.claim.sub=my-service-account
sasl.oauthbearer.assertion.claim.aud=https://example.com
sasl.oauthbearer.assertion.claim.exp.seconds=300
sasl.oauthbearer.assertion.claim.jti.include=true
sasl.oauthbearer.scope=my-application-scope
```

A pre-generated JWT assertion can also be read from a file (`sasl.oauthbearer.assertion.file=/path/to/assertion.jwt`). When both client assertion and client secret configurations are present, the `ClientCredentialsJwtRetriever` uses a three-tier preference order: (1) file-based assertion — highest priority; (2) locally-generated assertion (`sasl.oauthbearer.assertion.claim.iss` with private key); (3) client secret — fallback. This selection is made at configuration time; runtime failures do not cause fallback to an alternative method. For the `urn:ietf:params:oauth:grant-type:jwt-bearer` grant type, the `JwtBearerJwtRetriever` must be configured explicitly via `sasl.oauthbearer.jwt.retriever.class=org.apache.kafka.common.security.oauthbearer.JwtBearerJwtRetriever`.

Production use cases may alternatively provide a custom implementation of `org.apache.kafka.common.security.auth.AuthenticateCallbackHandler` that can handle an instance of `OAuthBearerTokenCallback` and declaring it via `sasl.login.callback.handler.class` for a non-broker client or via `listener.name.sasl_ssl.oauthbearer.sasl.login.callback.handler.class` for brokers.

### Enabling multiple SASL mechanisms in a broker

Specify configuration for the login modules of all enabled mechanisms in the `KafkaServer` section of the JAAS config file, then enable the SASL mechanisms in server.properties:

```properties
sasl.enabled.mechanisms=GSSAPI,PLAIN,SCRAM-SHA-256,SCRAM-SHA-512,OAUTHBEARER
security.inter.broker.protocol=SASL_PLAINTEXT (or SASL_SSL)
sasl.mechanism.inter.broker.protocol=GSSAPI (or one of the other enabled mechanisms)
```

### Modifying SASL mechanism in a Running Cluster

1. Enable new SASL mechanism by adding the mechanism to `sasl.enabled.mechanisms` in server.properties for each broker. Update JAAS config file to include both mechanisms. Incrementally bounce the cluster nodes.
2. Restart clients using the new mechanism.
3. To change the mechanism of inter-broker communication (if this is required), set `sasl.mechanism.inter.broker.protocol` in server.properties to the new mechanism and incrementally bounce the cluster again.
4. To remove old mechanism (if this is required), remove the old mechanism from `sasl.enabled.mechanisms` in server.properties and remove the entries for the old mechanism from JAAS config file. Incrementally bounce the cluster again.

### Authentication using Delegation Tokens

Delegation token based authentication is a lightweight authentication mechanism to complement existing SASL/SSL methods. Delegation tokens are shared secrets between kafka brokers and clients. Delegation tokens will help processing frameworks to distribute the workload to available workers in a secure environment without the added cost of distributing Kerberos TGT/keytabs or keystores when 2-way SSL is used. See KIP-48 for more details. Under the default implementation of `principal.builder.class`, the owner of delegation token is used as the authenticated Principal for configuration of ACLs etc.

**Token Management.** A secret is used to generate and verify delegation tokens. This is supplied using config option `delegation.token.secret.key`. The same secret key must be configured across all the brokers. The controllers must also be configured with the secret using the same config option. If the secret is not set or set to empty string, delegation token authentication and API operations will fail. A token has a current life, and a maximum renewable life. By default, tokens must be renewed once every 24 hours for up to 7 days. These can be configured using `delegation.token.expiry.time.ms` and `delegation.token.max.lifetime.ms` config options.

**Creating Delegation Tokens.** Delegation token requests (create/renew/expire/describe) should be issued only on SASL or SSL authenticated channels. Tokens can not be requests if the initial authentication is done through delegation token.

```bash
$ bin/kafka-delegation-tokens.sh --bootstrap-server localhost:9092 --create --max-life-time-period -1 --command-config client.properties --renewer-principal User:user1
$ bin/kafka-delegation-tokens.sh --bootstrap-server localhost:9092 --renew --renew-time-period -1 --command-config client.properties --hmac ABCDEFGHIJK
$ bin/kafka-delegation-tokens.sh --bootstrap-server localhost:9092 --expire --expiry-time-period -1 --command-config client.properties --hmac ABCDEFGHIJK
$ bin/kafka-delegation-tokens.sh --bootstrap-server localhost:9092 --describe --command-config client.properties --owner-principal User:user1
```

**Token Authentication.** Delegation token authentication piggybacks on the current SASL/SCRAM authentication mechanism:

```properties
sasl.jaas.config=org.apache.kafka.common.security.scram.ScramLoginModule required \
    username="tokenID123" \
    password="lAYYSFmLs4bTjf+lTZ1LCHR/ZZFNA==" \
    tokenauth="true";
```

The options `username` and `password` are used by clients to configure the token id and token HMAC. And the option `tokenauth` is used to indicate the server about token authentication.
