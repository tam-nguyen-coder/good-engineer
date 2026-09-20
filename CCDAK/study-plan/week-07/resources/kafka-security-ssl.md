# Apache Kafka 4.3 Docs — Encryption and Authentication using SSL

> **Nguồn (official):** https://kafka.apache.org/43/security/encryption-and-authentication-using-ssl/
> **Tuần:** 7 — Security & Testing · **Loại:** Apache Kafka Docs (Security → Encryption and Authentication using SSL)
> ⚠️ Nội dung dưới đây được crawl tự động (qua curl + WebFetch, có rút gọn) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- **Keystore = "tôi là ai"** (private key + cert của chính node, phải giữ bí mật, lý tưởng sinh ngay trên broker); **truststore = "tôi tin ai"** (chỉ chứa CA cert, **không nhạy cảm**, có thể dùng chung 1 file cho mọi client/broker). Client TLS 1 chiều **chỉ cần truststore**; cần thêm keystore khi broker `ssl.client.auth=required`/`requested`.
- Định dạng keystore: **PKCS12 là mặc định từ Java 9**, JKS đã deprecated → docs luôn thêm `-storetype pkcs12`. Kafka nhận `JKS` / `PKCS12` / **`PEM` (từ 2.7)**.
- **Hostname verification bật mặc định từ Kafka 2.0.0** (`ssl.endpoint.identification.algorithm=https`) cho cả client và inter-broker. Kiểm tra FQDN/IP của server với **SAN** (khuyến nghị) hoặc CN (**deprecated từ năm 2000**). Tắt = đặt rỗng (`ssl.endpoint.identification.algorithm=`), docs nói "không có lý do tốt nào để tắt".
- SAN phải nằm trong **CSR** (thêm `-ext SAN=DNS:{FQDN},IP:{IP}` lúc `keytool`) và CA phải **copy extension** vào cert (`copy_extensions = copy` trong `openssl-ca.cnf`, dùng module `openssl ca` thay `x509` vì bug không copy SAN). Kiểm tra bằng `openssl x509 -in cert -text -noout`.
- **`ssl.client.auth`**: `none` (mặc định) · `requested` (client không cert **vẫn nối được** → "false sense of security", **không khuyến nghị**) · **`required` = mTLS**. Khi bật, **broker cũng cần truststore** chứa CA đã ký cert client.
- Config broker bắt buộc: `ssl.keystore.location` / `ssl.keystore.password` / `ssl.key.password` / `ssl.truststore.location` / `ssl.truststore.password` (truststore password "kỹ thuật là tuỳ chọn" nhưng thiếu thì mất integrity check). Tuỳ chọn: `ssl.cipher.suites`, `ssl.enabled.protocols`, `ssl.keystore.type`, `ssl.secure.random.implementation=SHA1PRNG` (non-blocking, đo ~50 MB/s produce + replication mỗi broker).
- Bật TLS cho replication: `security.inter.broker.protocol=SSL` (hoặc `inter.broker.listener.name` trỏ listener SSL). Nếu không, cần **cả** cổng PLAINTEXT và SSL.
- Cert broker cần Extended Key Usage **cả `serverAuth` và `clientAuth`** vì broker vừa là server vừa là client (replication); CA doanh nghiệp hay cấp profile webserver chỉ có serverAuth → **handshake fail**. Cert ký bởi intermediate CA phải import **cả chain** tới root.
- **PEM (2.7+)**: `ssl.keystore.key` (private key), `ssl.keystore.certificate.chain`, `ssl.truststore.certificates` inline (multi-line với `\`), **không dùng** `ssl.keystore.password`/`ssl.truststore.password`; key mã hoá → `ssl.key.password`.
- Kiểm tra nhanh listener SSL: `openssl s_client -debug -connect localhost:9093 -tls1_2` phải in `-----BEGIN CERTIFICATE-----` của server. Client console: `kafka-console-producer.sh --bootstrap-server localhost:9093 --topic test --command-config client-ssl.properties` (console producer/consumer 4.x cũng nhận `--producer.config` / `--consumer.config`).
- Tách **validity của key** (`-validity` trong keytool, có thể 10 năm) và **validity của cert** (do CA quyết định, `default_days = 1000` trong ví dụ): một key có thể xin nhiều cert theo thời gian.

---

## 📄 Nội dung (trích từ tài liệu gốc)

Apache Kafka allows clients to use SSL for encryption of traffic as well as authentication. By default, SSL is disabled but can be turned on if needed. The following paragraphs explain in detail how to set up your own PKI infrastructure, use it to create certificates and configure Kafka to use these.

### Generate SSL key and certificate for each Kafka broker

The first step of deploying one or more brokers with SSL support is to generate a public/private keypair for every server. Since Kafka expects all keys and certificates to be stored in keystores we will use Java's keytool command for this task. The tool supports two different keystore formats, the Java specific jks format which has been deprecated by now, as well as PKCS12. PKCS12 is the default format as of Java version 9, to ensure this format is being used regardless of the Java version in use all following commands explicitly specify the PKCS12 format.

```bash
$ keytool -keystore {keystorefile} -alias localhost -validity {validity} -genkey -keyalg RSA -storetype pkcs12
```

You need to specify two parameters in the above command:

- **keystorefile**: the keystore file that stores the keys (and later the certificate) for this broker. The keystore file contains the private and public keys of this broker, therefore it needs to be kept safe. Ideally this step is run on the Kafka broker that the key will be used on, as this key should never be transmitted/leave the server that it is intended for.
- **validity**: the valid time of the key in days. Please note that this differs from the validity period for the certificate, which will be determined in Signing the certificate. You can use the same key to request multiple certificates: if your key has a validity of 10 years, but your CA will only sign certificates that are valid for one year, you can use the same key with 10 certificates over time.

To obtain a certificate that can be used with the private key that was just created a certificate signing request needs to be created. This signing request, when signed by a trusted CA results in the actual certificate which can then be installed in the keystore and used for authentication purposes.

```bash
$ keytool -keystore server.keystore.jks -alias localhost -validity {validity} -genkey -keyalg RSA -destkeystoretype pkcs12 -ext SAN=DNS:{FQDN},IP:{IPADDRESS1}
```

This command assumes that you want to add hostname information to the certificate, if this is not the case, you can omit the extension parameter `-ext SAN=DNS:{FQDN},IP:{IPADDRESS1}`.

#### Host Name Verification

Host name verification, when enabled, is the process of checking attributes from the certificate that is presented by the server you are connecting to against the actual hostname or ip address of that server to ensure that you are indeed connecting to the correct server.

The main reason for this check is to prevent man-in-the-middle attacks. For Kafka, this check has been disabled by default for a long time, but as of Kafka 2.0.0 host name verification of servers is enabled by default for client connections as well as inter-broker connections.

Server host name verification may be disabled by setting `ssl.endpoint.identification.algorithm` to an empty string. For dynamically configured broker listeners, hostname verification may be disabled using `kafka-configs.sh`:

```bash
$ bin/kafka-configs.sh --bootstrap-server localhost:9093 --entity-type brokers --entity-name 0 --alter --add-config "listener.name.internal.ssl.endpoint.identification.algorithm="
```

> Note: Normally there is no good reason to disable hostname verification apart from being the quickest way to "just get it to work" followed by the promise to "fix it later when there is more time"! Getting hostname verification right is not that hard when done at the right time, but gets much harder once the cluster is up and running - do yourself a favor and do it now!

If host name verification is enabled, clients will verify the server's fully qualified domain name (FQDN) or ip address against one of the following two fields:

- Common Name (CN)
- Subject Alternative Name (SAN)

While Kafka checks both fields, usage of the common name field for hostname verification has been deprecated since 2000 and should be avoided if possible. In addition the SAN field is much more flexible, allowing for multiple DNS and IP entries to be declared in a certificate. Another advantage is that if the SAN field is used for hostname verification the common name can be set to a more meaningful value for authorization purposes. Since we need the SAN field to be contained in the signed certificate, it will be specified when generating the signing request. It can also be specified when generating the keypair, but this will not automatically be copied into the signing request.

### Creating your own CA

After this step each machine in the cluster has a public/private key pair which can already be used to encrypt traffic and a certificate signing request, which is the basis for creating a certificate. To add authentication capabilities this signing request needs to be signed by a trusted authority, which will be created in this step.

A certificate authority (CA) is responsible for signing certificates. CAs works likes a government that issues passports - the government stamps (signs) each passport so that the passport becomes difficult to forge. Other governments verify the stamps to ensure the passport is authentic. Similarly, the CA signs the certificates, and the cryptography guarantees that a signed certificate is computationally difficult to forge. Thus, as long as the CA is a genuine and trusted authority, the clients have a strong assurance that they are connecting to the authentic machines.

For this guide we will be our own Certificate Authority. When setting up a production cluster in a corporate environment these certificates would usually be signed by a corporate CA that is trusted throughout the company.

Due to a bug in OpenSSL, the x509 module will not copy requested extension fields from CSRs into the final certificate. Since we want the SAN extension to be present in our certificate to enable hostname verification, we'll use the ca module instead. This requires some additional configuration to be in place before we generate our CA keypair. Save the following listing into a file called `openssl-ca.cnf` and adjust the values for validity and common attributes as necessary.

```ini
HOME            = .
RANDFILE        = $ENV::HOME/.rnd
####################################################################
[ ca ]
default_ca    = CA_default      # The default ca section

[ CA_default ]
base_dir      = .
certificate   = $base_dir/cacert.pem   # The CA certificate
private_key   = $base_dir/cakey.pem    # The CA private key
new_certs_dir = $base_dir              # Location for new certs after signing
database      = $base_dir/index.txt    # Database index file
serial        = $base_dir/serial.txt   # The current serial number

default_days     = 1000         # How long to certify for
default_crl_days = 30           # How long before next CRL
default_md       = sha256       # Use public key default MD
preserve         = no           # Keep passed DN ordering

x509_extensions = ca_extensions # The extensions to add to the cert
email_in_dn     = no            # Don't concat the email in the DN
copy_extensions = copy          # Required to copy SANs from CSR to cert
####################################################################
[ req ]
default_bits       = 4096
default_keyfile    = cakey.pem
distinguished_name = ca_distinguished_name
x509_extensions    = ca_extensions
string_mask        = utf8only
####################################################################
[ ca_distinguished_name ]
countryName         = Country Name (2 letter code)
countryName_default = DE
stateOrProvinceName         = State or Province Name (full name)
stateOrProvinceName_default = Test Province
localityName                = Locality Name (eg, city)
localityName_default        = Test Town
organizationName            = Organization Name (eg, company)
organizationName_default    = Test Company
organizationalUnitName         = Organizational Unit (eg, division)
organizationalUnitName_default = Test Unit
commonName         = Common Name (e.g. server FQDN or YOUR name)
commonName_default = Test Name
emailAddress         = Email Address
emailAddress_default = test@test.com
####################################################################
[ ca_extensions ]
subjectKeyIdentifier   = hash
authorityKeyIdentifier = keyid:always, issuer
basicConstraints       = critical, CA:true
keyUsage               = keyCertSign, cRLSign
####################################################################
[ signing_policy ]
countryName            = optional
stateOrProvinceName    = optional
localityName           = optional
organizationName       = optional
organizationalUnitName = optional
commonName             = supplied
emailAddress           = optional
####################################################################
[ signing_req ]
subjectKeyIdentifier   = hash
authorityKeyIdentifier = keyid,issuer
basicConstraints       = CA:FALSE
keyUsage               = digitalSignature, keyEncipherment
```

Then create a database and serial number file, these will be used to keep track of which certificates were signed with this CA. Both of these are simply text files that reside in the same directory as your CA keys.

```bash
$ echo 01 > serial.txt
$ touch index.txt
```

With these steps done you are now ready to generate your CA that will be used to sign certificates later.

```bash
$ openssl req -x509 -config openssl-ca.cnf -newkey rsa:4096 -sha256 -nodes -out cacert.pem -outform PEM
```

The CA is simply a public/private key pair and certificate that is signed by itself, and is only intended to sign other certificates. This keypair should be kept very safe, if someone gains access to it, they can create and sign certificates that will be trusted by your infrastructure, which means they will be able to impersonate anybody when connecting to any service that trusts this CA.

The next step is to add the generated CA to the clients' truststore so that the clients can trust this CA:

```bash
$ keytool -keystore client.truststore.jks -alias CARoot -import -file ca-cert
```

> Note: If you configure the Kafka brokers to require client authentication by setting `ssl.client.auth` to be "requested" or "required" in the Kafka brokers config then you must provide a truststore for the Kafka brokers as well and it should have all the CA certificates that clients' keys were signed by.

```bash
$ keytool -keystore server.truststore.jks -alias CARoot -import -file ca-cert
```

In contrast to the keystore in step 1 that stores each machine's own identity, the truststore of a client stores all the certificates that the client should trust. Importing a certificate into one's truststore also means trusting all certificates that are signed by that certificate. As the analogy above, trusting the government (CA) also means trusting all passports (certificates) that it has issued. This attribute is called the chain of trust, and it is particularly useful when deploying SSL on a large Kafka cluster. You can sign all certificates in the cluster with a single CA, and have all machines share the same truststore that trusts the CA. That way all machines can authenticate all other machines.

### Signing the certificate

Then sign it with the CA:

```bash
$ openssl ca -config openssl-ca.cnf -policy signing_policy -extensions signing_req -out {server certificate} -infiles {certificate signing request}
```

Finally, you need to import both the certificate of the CA and the signed certificate into the keystore:

```bash
$ keytool -keystore {keystore} -alias CARoot -import -file {CA certificate}
$ keytool -keystore {keystore} -alias localhost -import -file cert-signed
```

This will leave you with one truststore called `truststore.jks` - this can be the same for all clients and brokers and does not contain any sensitive information, so there is no need to secure this. Additionally you will have one `server.keystore.jks` file per node which contains that nodes keys, certificate and your CAs certificate.

### SSL key and certificates in PEM format

From 2.7.0 onwards, SSL key and trust stores can be configured for Kafka brokers and clients directly in the configuration in PEM format. This avoids the need to store separate files on the file system and benefits from password protection features of Kafka configuration. PEM may also be used as the store type for file-based key and trust stores in addition to JKS and PKCS12. To configure PEM key store directly in the broker or client configuration, private key in PEM format should be provided in `ssl.keystore.key` and the certificate chain in PEM format should be provided in `ssl.keystore.certificate.chain`. To configure trust store, trust certificates, e.g. public certificate of CA, should be provided in `ssl.truststore.certificates`. Since PEM is typically stored as multi-line base-64 strings, the configuration value can be included in Kafka configuration as multi-line strings with lines terminating in backslash ('\') for line continuation.

Store password configs `ssl.keystore.password` and `ssl.truststore.password` are not used for PEM. If private key is encrypted using a password, the key password must be provided in `ssl.key.password`. Private keys may be provided in unencrypted form without a password.

### Common Pitfalls in Production

**Extended Key Usage.** Certificates may contain an extension field that controls the purpose for which the certificate can be used. If this field is empty, there are no restrictions on the usage, but if any usage is specified in here, valid SSL implementations have to enforce these usages. Relevant usages for Kafka are: Client authentication, Server authentication. Kafka brokers need both these usages to be allowed, as for intra-cluster communication every broker will behave as both the client and the server towards other brokers. It is not uncommon for corporate CAs to have a signing profile for webservers and use this for Kafka as well, which will only contain the serverAuth usage value and cause the SSL handshake to fail.

**Intermediate Certificates.** Corporate Root CAs are often kept offline for security reasons. To enable day-to-day usage, so called intermediate CAs are created, which are then used to sign the final certificates. When importing a certificate into the keystore that was signed by an intermediate CA it is necessary to provide the entire chain of trust up to the root CA. This can be done by simply cat-ing the certificate files into one combined certificate file and then importing this with keytool.

**Failure to copy extension fields.** CA operators are often hesitant to copy and requested extension fields from CSRs and prefer to specify these themselves. It is advisable to double check signed certificates, whether these contain all requested SAN fields to enable proper hostname verification:

```bash
$ openssl x509 -in certificate.crt -text -noout
```

### Configuring Kafka Brokers

If SSL is not enabled for inter-broker communication (see below for how to enable it), both PLAINTEXT and SSL ports will be necessary.

```properties
listeners=PLAINTEXT://host.name:port,SSL://host.name:port
```

Following SSL configs are needed on the broker side:

```properties
ssl.keystore.location=/var/private/ssl/server.keystore.jks
ssl.keystore.password=test1234
ssl.key.password=test1234
ssl.truststore.location=/var/private/ssl/server.truststore.jks
ssl.truststore.password=test1234
```

Note: `ssl.truststore.password` is technically optional but highly recommended. If a password is not set access to the truststore is still available, but integrity checking is disabled. Optional settings that are worth considering:

- `ssl.client.auth=none` ("required" => client authentication is required, "requested" => client authentication is requested and client without certs can still connect. The usage of "requested" is discouraged as it provides a false sense of security and misconfigured clients will still connect successfully.)
- `ssl.cipher.suites` (Optional). A cipher suite is a named combination of authentication, encryption, MAC and key exchange algorithm used to negotiate the security settings for a network connection using TLS or SSL network protocol. (Default is an empty list)
- `ssl.enabled.protocols=TLSv1.2,TLSv1.1,TLSv1` (list out the SSL protocols that you are going to accept from clients. Do note that SSL is deprecated in favor of TLS and using SSL in production is not recommended)
- `ssl.keystore.type=JKS`
- `ssl.truststore.type=JKS`
- `ssl.secure.random.implementation=SHA1PRNG`

If you want to enable SSL for inter-broker communication, add the following to the server.properties file (it defaults to PLAINTEXT):

```properties
security.inter.broker.protocol=SSL
```

Once you start the broker you should be able to see in the server.log:

```
with addresses: PLAINTEXT -> EndPoint(192.168.64.1,9092,PLAINTEXT),SSL -> EndPoint(192.168.64.1,9093,SSL)
```

To check quickly if the server keystore and truststore are setup properly you can run the following command:

```bash
$ openssl s_client -debug -connect localhost:9093 -tls1
```

In the output of this command you should see server's certificate (`-----BEGIN CERTIFICATE-----` … `subject=… issuer=…`). If the certificate does not show up or if there are any other error messages then your keystore is not setup properly.

### Configuring Kafka Clients

SSL is supported only for the new Kafka Producer and Consumer, the older API is not supported. The configs for SSL will be the same for both producer and consumer. If client authentication is not required in the broker, then the following is a minimal configuration example:

```properties
security.protocol=SSL
ssl.truststore.location=/var/private/ssl/client.truststore.jks
ssl.truststore.password=test1234
```

If client authentication is required, then a keystore must be created like in step 1 and the following must also be configured:

```properties
ssl.keystore.location=/var/private/ssl/client.keystore.jks
ssl.keystore.password=test1234
ssl.key.password=test1234
```

Other configuration settings that may also be needed depending on our requirements and the broker configuration: `ssl.provider`, `ssl.cipher.suites`, `ssl.enabled.protocols` (should list at least one of the protocols configured on the broker side), `ssl.truststore.type=JKS`, `ssl.keystore.type=JKS`.

Examples using console-producer and console-consumer:

```bash
$ bin/kafka-console-producer.sh --bootstrap-server localhost:9093 --topic test --command-config client-ssl.properties
$ bin/kafka-console-consumer.sh --bootstrap-server localhost:9093 --topic test --command-config client-ssl.properties
```

### Ghi chú thêm (từ trang Authorization and ACLs, liên quan mTLS)

By default, the SSL user name will be of the form `CN=writeuser,OU=Unknown,O=Unknown,L=Unknown,ST=Unknown,C=Unknown`. One can change that by setting `ssl.principal.mapping.rules` to a customized rule in server.properties. The rules are evaluated in order and the first rule that matches a distinguished name is used to map it to a short name. Format: `RULE:pattern/replacement/` or `RULE:pattern/replacement/[LU]`, ending with `DEFAULT`. Example:

```properties
ssl.principal.mapping.rules=RULE:^CN=(.*?),OU=ServiceUsers.*$/$1/,RULE:^CN=(.*?),OU=(.*?),O=(.*?),L=(.*?),ST=(.*?),C=(.*?)$/$1@$2/L,RULE:^.*[Cc][Nn]=([a-zA-Z0-9.]*).*$/$1/L,DEFAULT
```

Above rules translate distinguished name `CN=serviceuser,OU=ServiceUsers,O=Unknown,L=Unknown,ST=Unknown,C=Unknown` to `serviceuser` and `CN=adminUser,OU=Admin,O=Unknown,L=Unknown,ST=Unknown,C=Unknown` to `adminuser@admin`.
