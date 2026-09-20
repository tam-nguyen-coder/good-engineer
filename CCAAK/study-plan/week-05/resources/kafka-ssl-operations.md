# Apache Kafka 4.3 Docs — Encryption and Authentication using SSL (góc vận hành)

> **Nguồn (official):** https://kafka.apache.org/43/security/encryption-and-authentication-using-ssl/
> **Tuần:** 5 — Security administration · **Loại:** Apache Kafka Docs (Security → Encryption and Authentication using SSL)
> ⚠️ Nội dung dưới đây được crawl tự động (WebFetch, có rút gọn) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.
> 🔁 Bản CCDAK của trang này ở [`../../../../CCDAK/study-plan/week-07/resources/kafka-security-ssl.md`](../../../../CCDAK/study-plan/week-07/resources/kafka-security-ssl.md) tóm tắt theo **góc client**. File này tóm tắt theo **góc người vận hành PKI cho cả cluster**.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- **Một broker = một keypair.** Docs nói thẳng "*the keystore file contains the private and public keys of this broker, therefore it needs to be kept safe*" → không dùng chung một keystore cho N broker trong production; sinh key **ngay trên máy broker** để private key không đi qua mạng.
- Định dạng keystore: **PKCS12 là mặc định từ Java 9** (docs luôn thêm `-storetype pkcs12`); JKS đã deprecated; **PEM hỗ trợ từ 2.7.0** với `ssl.keystore.key`, `ssl.keystore.certificate.chain`, `ssl.truststore.certificates` — PEM **không dùng** `ssl.keystore.password`, key mã hoá thì dùng `ssl.key.password`.
- **Hostname verification bật mặc định từ 2.0.0** cho **cả client lẫn inter-broker**. Cert phải có **SAN** khớp host mà client gõ. SAN phải được thêm **ngay từ lúc tạo CSR** (`-ext SAN=DNS:{FQDN},IP:{IPADDRESS1}`) và CA phải **copy extension** khi ký.
- Tắt hostname verification = đặt `ssl.endpoint.identification.algorithm` thành **chuỗi rỗng** — docs xếp vào loại "strongly discouraged". Điều đáng nhớ cho admin: có thể tắt/bật **lúc chạy** bằng dynamic config theo từng listener:
  `kafka-configs.sh --bootstrap-server localhost:9093 --entity-type brokers --entity-name 0 --alter --add-config "listener.name.internal.ssl.endpoint.identification.algorithm="`.
- **`ssl.client.auth` có 3 giá trị**: `none` (mặc định — chỉ mã hoá, client vào **ẩn danh** với principal `User:ANONYMOUS`) · `requested` (hỏi cert nhưng **không cert vẫn vào được** → "an toàn giả", đừng dùng) · `required` (**mTLS thật**).
- Với mTLS, **principal mặc định là toàn bộ DN** (`CN=svc-orders,OU=Payments,O=Acme,C=VN`). Muốn ACL viết gọn `User:svc-orders` thì cần `ssl.principal.mapping.rules`, ví dụ `RULE:^CN=(.*?),OU=.*$/$1/` (thêm `/L` hoặc `/U` để ép thường/hoa), kết thúc bằng `DEFAULT`.
- Bẫy PKI doanh nghiệp thường gặp (docs liệt kê ở mục Common Pitfalls): (1) **Extended Key Usage thiếu `clientAuth`** — broker vừa là server vừa là client khi replicate nên cert cần **cả `serverAuth` và `clientAuth`**; (2) **chuỗi intermediate CA** không import đủ; (3) **SAN bị rớt** khi CA ký. Kiểm nhanh: `openssl x509 -in certificate.crt -text -noout`.
- Bật TLS cho replication bằng `security.inter.broker.protocol=SSL` (hoặc trỏ `inter.broker.listener.name` vào listener SSL). Trong lúc migration thì mở **đồng thời** `listeners=PLAINTEXT://host:port,SSL://host:port`.
- Client chỉ mã hoá → cần `security.protocol=SSL` + **truststore**. Thêm mTLS mới cần **keystore** client (`ssl.keystore.location`, `ssl.keystore.password`, `ssl.key.password`).
- Tuỳ chọn hay dùng khi tune: `ssl.cipher.suites`, `ssl.enabled.protocols`, `ssl.keystore.type`, `ssl.truststore.type`. TLS làm **mất zero-copy `sendfile`** ở đường fetch → luôn tính thêm CPU khi sizing broker.

---

## 📄 Nội dung (trích từ tài liệu gốc)

Apache Kafka allows clients to use SSL for encryption of traffic as well as authentication. By default, SSL is disabled but can be turned on if needed. The following paragraphs explain in detail how to set up your own PKI infrastructure, use it to create certificates and configure Kafka to use these.

### Generate SSL key and certificate for each Kafka broker

The first step of deploying one or more brokers with SSL support is to generate a public/private keypair for every server. Since Kafka expects all keys and certificates to be stored in keystores we will use Java's keytool command for this task. The tool supports two different keystore formats, the Java specific jks format which has been deprecated by now, as well as PKCS12. PKCS12 is the default format as of Java version 9.

```
keytool -keystore {keystorefile} -alias localhost -validity {validity} -genkey -keyalg RSA -storetype pkcs12
```

You need to specify two parameters in the above command:

1. `keystorefile`: the keystore file that stores the keys (and later the certificate) for this broker. The keystore file contains the private and public keys of this broker, therefore it needs to be kept safe. Ideally this step is run on the Kafka broker that the key will be used on, as this key should never be transmitted/leave the server that it is intended for.
2. `validity`: the valid time of the key in days. Please note that this differs from the validity period for the certificate, which will be determined in the Signing the certificate section. You can use the same key to request multiple certificates: if your keys have a very long validity period, your certificates should be valid for a shorter period.

#### Configuring Host Name Verification

From Kafka version 2.0.0 onwards, host name verification of servers is enabled by default for client connections as well as inter-broker connections to prevent man-in-the-middle attacks. Server host name verification may be disabled by setting `ssl.endpoint.identification.algorithm` to an empty string. For dynamically configured broker listeners, hostname verification may be disabled using `kafka-configs.sh`:

```
bin/kafka-configs.sh --bootstrap-server localhost:9093 --entity-type brokers --entity-name 0 --alter --add-config "listener.name.internal.ssl.endpoint.identification.algorithm="
```

Note:

Normally there is no good reason to disable hostname verification apart from being the quickest way to "just get it to work" followed by the promise to "fix it later when there's more time"! Getting host name verification right is not that hard when done at the right time but gets much harder once the cluster is up and running — do yourself a favor and do it now!

If host name verification is enabled, clients will verify the server's fully qualified domain name (FQDN) or IP address against one of the following two fields:

1. Common Name (CN)
2. Subject Alternative Name (SAN)

While Kafka checks both fields, usage of the common name field for hostname verification has been deprecated since 2000 and should be avoided if possible. In addition the SAN field is much more flexible, allowing for multiple DNS and IP entries to be declared in a certificate.

Another advantage is that if the SAN field is used for hostname verification the common name can be set to a more meaningful value for authorization purposes. Since we need the SAN field to be contained in the signed certificate, it will be specified when generating the signing request. It can also be specified when generating the keypair:

```
keytool -keystore server.keystore.jks -alias localhost -validity {validity} -genkey -keyalg RSA -destkeystoretype pkcs12 -ext SAN=DNS:{FQDN},IP:{IPADDRESS1}
```

### Creating your own CA

After this step each machine in the cluster has a public-private key pair which can already be used to encrypt traffic and a certificate signing request, which is the basis for creating a certificate. To add authentication capabilities this signing request needs to be signed by a trusted authority, which will be created in this step.

A certificate authority (CA) is responsible for signing certificates. A CA works like a government that issues passports — the government stamps (signs) each passport so that the passport becomes difficult to forge. Other governments verify the stamps to ensure the passport is authentic. Similarly, the CA signs the certificates, and the cryptography guarantees that a signed certificate is computationally difficult to forge. Thus, as long as the CA is a genuine and trusted authority, the clients have a strong assurance that they are connecting to the authentic machines.

```
openssl req -x509 -config openssl-ca.cnf -newkey rsa:4096 -sha256 -nodes -out cacert.pem -outform PEM
```

The generated CA is simply a public-private key pair and certificate, and it is intended to sign other certificates. The next step is to add the generated CA to the clients' truststore so that the clients can trust this CA:

```
keytool -keystore client.truststore.jks -alias CARoot -import -file ca-cert
```

Note: If you configure the Kafka brokers to require client authentication by setting `ssl.client.auth` to be `requested` or `required` in the Kafka brokers config then you must provide a truststore for the Kafka brokers as well and it should have all the CA certificates that clients' keys were signed by.

In contrast to the keystore in step 1 that stores each machine's own identity, the truststore of a client stores all the certificates that the client should trust. Importing a certificate into one's truststore also means trusting all certificates that are signed by that certificate. As the analogy above, trusting the government (CA) also means trusting all passports (certificates) that it has issued. This attribute is called the chain of trust, and it is particularly useful when deploying SSL on a large Kafka cluster. You can sign all certificates in the cluster with a single CA, and have all machines share the same truststore that trusts the CA. That way all machines can authenticate all other machines.

### Signing the certificate

```
openssl ca -config openssl-ca.cnf -policy signing_policy -extensions signing_req -out {server certificate} -infiles {certificate signing request}
```

Then you need to import both the certificate of the CA and the signed certificate into the keystore:

```
keytool -keystore {keystore} -alias CARoot -import -file {CA certificate}
keytool -keystore {keystore} -alias localhost -import -file cert-signed
```

### Configuring Kafka Brokers

If SSL is not enabled for inter-broker communication, both PLAINTEXT and SSL ports will be necessary.

```
listeners=PLAINTEXT://host.name:port,SSL://host.name:port
```

Following SSL configs are needed on the broker side:

```
ssl.keystore.location=/var/private/ssl/server.keystore.jks
ssl.keystore.password=test1234
ssl.key.password=test1234
ssl.truststore.location=/var/private/ssl/server.truststore.jks
ssl.truststore.password=test1234
```

Note: `ssl.truststore.password` is technically optional but highly recommended. If a password is not set, access to the truststore is still available but integrity checking is disabled.

Optional settings that are worth considering:

1. `ssl.client.auth=none` (`required` => client authentication is required, `requested` => client authentication is requested and client without certs can still connect. The usage of `requested` is discouraged as it provides a false sense of security and misconfigured clients will still connect successfully.)
2. `ssl.cipher.suites` (Optional). A cipher suite is a named combination of authentication, encryption, MAC and key exchange algorithm used to negotiate the security settings for a network connection using TLS or SSL network protocol.
3. `ssl.enabled.protocols=TLSv1.2,TLSv1.1,TLSv1`
4. `ssl.keystore.type=JKS`
5. `ssl.truststore.type=JKS`

If you want to enable SSL for inter-broker communication, add the following to the server.properties file:

```
security.inter.broker.protocol=SSL
```

Once you start the broker you should be able to see in the server.log:

```
with addresses: PLAINTEXT -> EndPoint(192.168.64.1,9092,PLAINTEXT),SSL -> EndPoint(192.168.64.1,9093,SSL)
```

To check quickly if the server keystore and truststore are set up properly you can run the following command:

```
openssl s_client -debug -connect localhost:9093 -tls1_2
```

(Note: `TLSv1` should be listed under `ssl.enabled.protocols`). In the output of this command you should see the server's certificate.

### Configuring Kafka Clients

SSL is supported only for the new Kafka Producer and Consumer; the older API is not supported. The configs for SSL will be the same for both producer and consumer.

If client authentication is not required in the broker, then the following is a minimal configuration example:

```
security.protocol=SSL
ssl.truststore.location=/var/private/ssl/client.truststore.jks
ssl.truststore.password=test1234
```

Note: `ssl.truststore.password` is technically optional but highly recommended.

If client authentication is required, then a keystore must be created like in step 1 and the following must also be configured:

```
ssl.keystore.location=/var/private/ssl/client.keystore.jks
ssl.keystore.password=test1234
ssl.key.password=test1234
```

Examples using console-producer and console-consumer:

```
kafka-console-producer.sh --bootstrap-server localhost:9093 --topic test --producer.config client-ssl.properties
kafka-console-consumer.sh --bootstrap-server localhost:9093 --topic test --consumer.config client-ssl.properties
```

### Using PEM format (since 2.7.0)

From 2.7.0 onwards, SSL key and trust stores can be configured for Kafka brokers and clients directly in the configuration in PEM format, using `ssl.keystore.key`, `ssl.keystore.certificate.chain` and `ssl.truststore.certificates`. Password for the private key is configured using `ssl.key.password` (not `ssl.keystore.password`).

### Common Pitfalls in Production

- Extended Key Usage: certificates may contain an extension field that controls the purpose for which the certificate can be used. If this field is empty, there are no restrictions on the usage, but if any usage is specified in there, valid SSL implementations have to enforce these usages. Relevant usages for Kafka are `clientAuth` and `serverAuth`. Kafka brokers need both usages to be allowed, as for intra-cluster communication they will act in both roles.
- Intermediate Certificates: root CAs are often kept offline for security reasons and intermediate CAs are used to issue certificates. It is necessary to provide the full chain of trust when generating keystores.
- Failure to copy extension fields when signing: CA operators are often hesitant to copy and requested extension fields from CSRs and prefer to specify these themselves as this makes it harder for a malicious party to obtain certificates with potentially misleading or fraudulent values. It is advisable to double check signed certificates, whether these contain all requested SAN fields and enable true hostname verification: `openssl x509 -in certificate.crt -text -noout`.
