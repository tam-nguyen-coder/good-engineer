# 🛠️ Tuần 5 — Security administration: thiết kế listener, TLS/mTLS, SASL, ACL ở quy mô, xoay credential không downtime

> **Domain CCAAK:** Apache Kafka Security (15%) · **Thời lượng:** ~11h (4 buổi) · **Vị trí:** Tuần 5/8 — có 🎯 **CHECKPOINT mini-mock SEC ≥70%**
>
> **Điều hướng:** [⬅️ Tuần 4](../week-04/README.md) · [🏠 Kế hoạch tổng](../../CCAAK-STUDY-PLAN.md) · [Tuần 6 ➡️](../week-06/README.md)

## 🔁 Ôn nhanh từ CCDAK (~20 phút)

CCDAK Tuần 7 đã dạy bạn **bảo mật nhìn từ client**: "ứng dụng của tôi cần config gì để kết nối vào cluster đã bảo mật". Tuần này lật ngược góc nhìn: **"làm sao vận hành bảo mật cho cả cluster, hàng trăm principal, mà không có phút downtime nào"**. Đọc lại đúng 6 chỗ dưới đây rồi vào Buổi A — **không học lại từ đầu**.

| Khái niệm | File CCDAK cần đọc lại | Vì sao cần cho tuần này |
| --- | --- | --- |
| 3 trụ security + 4 `security.protocol` + bảng listener | [`week-07/README.md`](../../../CCDAK/study-plan/week-07/README.md) mục 1–2 | Tuần này **không** giải thích lại `PLAINTEXT`/`SSL`/`SASL_PLAINTEXT`/`SASL_SSL`. Buổi A đi thẳng vào **thiết kế nhiều listener cho nhiều đối tượng** trên một cluster thật |
| Keystore vs truststore, SAN, hostname verification | [`week-07/resources/kafka-security-ssl.md`](../../../CCDAK/study-plan/week-07/resources/kafka-security-ssl.md) | Bạn đã biết **tạo** cert. Tuần này học **thay** cert khi cluster đang phục vụ — nếu quên "truststore = tôi tin ai" thì không hiểu nổi thứ tự xoay |
| 4 SASL mechanism + JAAS inline | [`week-07/resources/kafka-security-sasl.md`](../../../CCDAK/study-plan/week-07/resources/kafka-security-sasl.md) | Bảng mechanism ở Buổi A là **bản mở rộng** của bảng này, thêm cột "vận hành thế nào ở quy mô" |
| Mô hình ACL, Deny thắng Allow, `--producer`/`--consumer` | [`week-07/resources/kafka-security-authorization-acls.md`](../../../CCDAK/study-plan/week-07/resources/kafka-security-authorization-acls.md) | Tuần này bắt đầu từ chỗ đó và đi tiếp tới **PREFIXED theo tenant, audit bằng `kafka-authorizer.log`, thu hồi nhầm rồi khôi phục** |
| Quota 4 loại + 8 mức ưu tiên + cơ chế throttle | [`week-07/resources/kafka-quotas.md`](../../../CCDAK/study-plan/week-07/resources/kafka-quotas.md) | Tuần này chỉ nhắc quota ở vai trò **công cụ bảo vệ multi-tenant**; phần chi tiết đã làm ở [Tuần 3](../week-03/README.md) |
| Lab TLS/SCRAM/ACL cơ bản | [`week-07/labs.md`](../../../CCDAK/study-plan/week-07/labs.md) Lab 7.1–7.4 | Lab tuần này **giả định bạn đã chạy qua** 4 lab đó trên cluster 1 node. Tuần 5 làm lại trên **cluster 3 broker + controller tách riêng**, tức là mọi thao tác phải **rolling** |

## 🎯 Mục tiêu tuần này

- **Thiết kế được** sơ đồ listener cho một cluster production 4 đối tượng (client nội bộ, client ngoài, inter-broker, controller), viết đúng 5 config `listeners` / `advertised.listeners` / `listener.security.protocol.map` / `inter.broker.listener.name` / `controller.listener.names` mà không tra tài liệu.
- **Tự tay xoay** một bộ chứng chỉ sắp hết hạn trên cluster đang chạy, theo đúng thứ tự **truststore trước — keystore sau**, và chứng minh bằng một client chạy liên tục rằng **không có giây downtime nào**.
- **Vận hành credential SASL**: thêm, xoay mật khẩu và **thu hồi** một principal lúc chạy; giải thích được vì sao thu hồi **chưa chắc** cắt ngay kết nối đang mở và phải đặt config nào để nó cắt thật.
- **Quản trị ACL ở quy mô**: đặt quy ước tên topic để một ACL `PREFIXED` phủ cả tenant, đọc `kafka-authorizer.log` để biết **chính xác** quyền nào đang thiếu, và cấp lại **quyền tối thiểu** thay vì cấp `All`.
- **Chẩn đoán được** 3 họ lỗi bảo mật chỉ bằng thông điệp: lỗi **handshake/protocol** (sai listener) vs lỗi **authentication** (sai credential) vs lỗi **authorization** (thiếu ACL) — và biết mỗi họ đọc log nào.
- **Nhận diện bẫy version**: `AclAuthorizer` vs `StandardAuthorizer`, `--zookeeper` vs `--bootstrap-server`, `zookeeper.set.acl`, `control.plane.listener.name` — mọi thứ thuộc thế giới ZooKeeper đều là đáp án sai ở Kafka 4.x.
- **Chốt checkpoint:** đạt **≥70%** ở MINI-MOCK SEC (~30 câu) trước khi sang Tuần 6.

## 📚 Nội dung học chi tiết

### 🅰️ Buổi A — Lý thuyết (~3h)

**1. Ba lớp bảo mật, đọc lại bằng câu hỏi của người vận hành**

| Lớp | CCDAK hỏi (client) | CCAAK hỏi (admin) | Hỏng thì thấy gì |
| --- | --- | --- | --- |
| **Encryption in transit** (TLS) | "client cần truststore nào?" | "cert của 12 broker hết hạn tháng sau, thay thế nào để không downtime? TLS ăn thêm bao nhiêu CPU khi sizing?" | `SSLHandshakeException`, broker log *"Failed authentication ... SSL handshake failed"* |
| **Authentication** (mTLS / SASL) | "điền `sasl.jaas.config` sao cho đúng?" | "một nhân viên nghỉ việc, thu hồi credential của service họ giữ trong bao lâu? thêm 50 principal mới có phải restart broker không?" | `SaslAuthenticationException` (fatal, client **không** retry), `UnsupportedSaslMechanismException` |
| **Authorization** (ACL) | "tôi thiếu quyền gì để consume?" | "300 topic, 80 service — viết bao nhiêu ACL là đủ? ai vừa bị từ chối và vì sao?" | `TopicAuthorizationException` / `GroupAuthorizationException` / `ClusterAuthorizationException`, dòng DENY trong `kafka-authorizer.log` |
| **Encryption at rest** | — | "Kafka mã hoá đĩa không?" → **KHÔNG có sẵn** | Không có triệu chứng — đây là câu hỏi kiến trúc, không phải sự cố |

> 🧠 Câu thần chú phân loại lỗi: **"không bắt tay được"** = sai listener/protocol · **"bắt tay xong bị đuổi"** = sai credential · **"vào được nhưng không làm được"** = thiếu ACL. Ba họ lỗi, ba chỗ đọc log khác nhau, đừng trộn.

**2. Thiết kế listener cho một cluster thật — phần bị xem nhẹ nhất và ra đề nhiều nhất**

Một cluster production hiếm khi có **một** listener. Điển hình là **bốn** đối tượng, mỗi đối tượng một mức bảo mật:

| Listener (tên **tự đặt**) | Phục vụ ai | Security protocol điển hình | Vì sao tách riêng |
| --- | --- | --- | --- |
| `INTERNAL` | Broker ↔ broker (replication) | `PLAINTEXT` trong VPC tin cậy, hoặc `SSL` nếu chính sách bắt buộc | Replication là đường **nặng nhất**; bật TLS ở đây làm **mất zero-copy `sendfile`** và tăng CPU đáng kể → quyết định có bật hay không là bài toán chi phí, không phải bài toán đúng/sai |
| `EXTERNAL` | Ứng dụng của các team / đối tác | `SASL_SSL` | Nơi duy nhất principal "người dùng" xuất hiện → nơi đặt ACL và quota |
| `CONTROLLER` | Broker → controller, controller ↔ controller | `PLAINTEXT` trong mạng riêng, hoặc `SASL_SSL` | **Bắt buộc tách**, và **không được trùng tên** với inter-broker listener |
| `ADMIN` (tuỳ chọn) | Công cụ vận hành, bastion host | `SASL_SSL` với mechanism riêng | Cho phép admin vào ngay cả khi listener client bị quota/ACL siết hoặc quá tải |

Năm config phải viết khớp nhau — sai một cái là cluster không lên hoặc client không nối được:

| Config | Nghĩa chính xác | Bẫy |
| --- | --- | --- |
| `listeners` | Broker **bind** vào đâu. Dạng `{TÊN}://{host}:{port}`, host trống = mọi interface | Tên listener **tự do** (`INTERNAL`, `EXTERNAL`…); dùng tên tự do thì **bắt buộc** có protocol map |
| `advertised.listeners` | Địa chỉ broker **trả cho client** trong `MetadataResponse` | Sai ở đây = "bootstrap OK nhưng produce timeout". Listener controller **không** advertise |
| `listener.security.protocol.map` | Ánh xạ **tên → protocol** | Thiếu một entry = broker không start. Ví dụ `INTERNAL:PLAINTEXT,EXTERNAL:SASL_SSL,CONTROLLER:PLAINTEXT` |
| `inter.broker.listener.name` | Listener dùng cho **replication** | **Không được** khai cùng lúc với `security.inter.broker.protocol`. Không khai gì cả → rơi về `security.inter.broker.protocol`, mặc định **`PLAINTEXT`** |
| `controller.listener.names` | Listener của **quorum KRaft** | **Không được trùng** inter-broker. Broker-only **vẫn phải khai** (để gọi ra controller) nhưng **không** đưa vào `listeners`. Nhận **nhiều giá trị**; cái **đầu tiên** dùng cho request đi ra → đây là cơ chế đổi cổng/protocol controller bằng 2 lần rolling |

Config theo từng listener dùng tiền tố **`listener.name.<tên-viết-thường>.<config>`** — ví dụ `listener.name.external.ssl.keystore.location`, `listener.name.external.scram-sha-512.sasl.jaas.config`. Không khai theo listener thì Kafka **rơi về config chung** (`ssl.keystore.location`). Chính cơ chế "theo listener + fallback" này là nền tảng của mọi thao tác xoay chứng chỉ ở mục 3.

**3. TLS vận hành — PKI nội bộ và bài toán xoay chứng chỉ**

- **PKI nội bộ**: một CA nội bộ ký cert cho **tất cả** broker → mọi node dùng **chung một truststore** (chỉ chứa CA) trong khi **mỗi node một keystore riêng**. Đây là lý do docs nhấn mạnh keystore "*needs to be kept safe*" và nên sinh **ngay trên máy broker**.
- **Định dạng**: `PKCS12` là mặc định từ **Java 9** (JKS đã deprecated), `PEM` hỗ trợ từ **2.7** qua `ssl.keystore.key` / `ssl.keystore.certificate.chain` / `ssl.truststore.certificates` (PEM **không** dùng `ssl.keystore.password`).
- **SAN là bắt buộc**: hostname verification bật mặc định từ **2.0** (`ssl.endpoint.identification.algorithm=https`). SAN phải nằm trong **CSR** và CA phải **copy extension** khi ký. Cert broker cần Extended Key Usage **cả `serverAuth` lẫn `clientAuth`** vì broker vừa là server (phục vụ client) vừa là client (đi fetch replication).
- **`ssl.client.auth` — 3 giá trị, phải thuộc:**

| Giá trị | Broker làm gì | Principal của client | Dùng khi nào |
| --- | --- | --- | --- |
| `none` (**mặc định**) | Không hỏi cert client | `User:ANONYMOUS` | Chỉ cần **mã hoá**, xác thực bằng SASL ở tầng trên |
| `requested` | **Hỏi** cert, nhưng không có vẫn cho vào | Có cert → DN; không cert → `User:ANONYMOUS` | ⚠️ **Gần như không bao giờ.** Docs gọi là "*false sense of security*": client cấu hình sai vẫn kết nối thành công và bạn không biết |
| `required` | Bắt buộc cert hợp lệ | **DN đầy đủ** của cert | **mTLS thật** |

- **Principal mapping**: mặc định principal của mTLS là **toàn bộ DN** `CN=svc-orders,OU=Payments,O=Acme,C=VN` → ACL viết `User:svc-orders` sẽ **không khớp**. Sửa bằng `ssl.principal.mapping.rules=RULE:^CN=(.*?),.*$/$1/,DEFAULT` (thêm `/L` để ép chữ thường). Quy tắc đánh giá **theo thứ tự, cái đầu tiên khớp thắng**, luôn kết thúc bằng `DEFAULT`.
- **Xoay chứng chỉ không downtime — thứ tự bất biến:**
  1. **Thêm CA mới vào truststore** của **mọi** broker và **mọi** client (truststore chứa **cả** CA cũ và CA mới) — lúc này chưa ai dùng cert mới, nhưng tất cả đã **sẵn sàng tin**.
  2. Đợi bước 1 phủ khắp (client là phần chậm nhất, có thể mất nhiều ngày).
  3. **Đổi keystore từng broker một**: hoặc **dynamic config** `listener.name.<l>.ssl.keystore.location` (**không restart**), hoặc rolling restart (thay file → restart → **chờ `UnderReplicatedPartitions` về 0** → broker kế tiếp).
  4. Khi mọi cert cũ đã bị thay: **gỡ CA cũ** khỏi truststore.
  > ⚠️ Hai luật kiểm tra tin cậy của **inter-broker listener** giải thích vì sao thứ tự này là bắt buộc: đổi **keystore** chỉ được phép nếu keystore **mới** được truststore **hiện tại** tin; đổi **truststore** chỉ được phép nếu keystore **hiện tại** được truststore **mới** tin. Làm ngược ("đổi cert trước rồi mới phát CA") thì broker **từ chối** hoặc replication **đứt**. Listener không phải inter-broker thì broker **không kiểm tra gì** — sai là client rớt ngay lập tức, còn tệ hơn.

**4. SASL vận hành — chọn mechanism theo bài toán *quản trị credential*, không theo bài toán *kết nối***

| Mechanism | Credential lưu ở đâu | Thêm/xoay/thu hồi **lúc chạy**? | Cần TLS? | Chọn khi nào (góc admin) |
| --- | --- | --- | --- | --- |
| `PLAIN` | **File JAAS tĩnh** trên từng broker (`user_alice="..."`) hoặc custom callback handler (LDAP) | ❌ **Phải sửa file + restart broker** cho mỗi user mới | ✅ **Bắt buộc** (mật khẩu đi trần) | Chỉ khi có callback handler nối vào hệ danh tính sẵn có. Tự nó **không mở rộng được**: 50 service = 50 lần rolling restart |
| `SCRAM-SHA-256` / `SCRAM-SHA-512` | **Metadata log `__cluster_metadata`**, salt + hash, **≥4096 iterations** | ✅ `kafka-configs.sh --alter --add-config 'SCRAM-SHA-512=[password=...]' --entity-type users --entity-name <u>` — hiệu lực ngay | ✅ Khuyến nghị mạnh | **Mặc định hợp lý cho Apache Kafka thuần.** Seed user đầu tiên (cho inter-broker) bằng `kafka-storage.sh format --add-scram 'SCRAM-SHA-512=[name=admin,password=...]'` vì lúc đó cluster chưa chạy |
| `GSSAPI` (Kerberos) | KDC / Active Directory; broker và client giữ **keytab** | ✅ (quản ở KDC, không đụng Kafka) | Không bắt buộc, nhưng data vẫn trần nếu không có TLS | Doanh nghiệp **đã có** Kerberos. Chi phí vận hành nằm ở **phân phối keytab** và đồng bộ giờ |
| `OAUTHBEARER` / OIDC | **IdP bên ngoài** (Keycloak, Okta, Entra ID, AWS IAM); JWT ngắn hạn, broker verify bằng **JWKS** | ✅ token tự hết hạn và tự refresh | ✅ Bắt buộc ở production | Nhiều cluster, nhiều môi trường, muốn **một nơi duy nhất** quản danh tính. Thu hồi = thu hồi ở IdP, không đụng Kafka |

- **Thứ tự ưu tiên JAAS phía broker** (3 mức, học thuộc): `listener.name.{listener}.{mechanism}.sasl.jaas.config` → section `{listener}.KafkaServer` trong file JAAS tĩnh → section `KafkaServer`. Dùng mức 1 để **mỗi listener một tập mechanism** (ví dụ `EXTERNAL` chỉ SCRAM, `ADMIN` chỉ OAUTHBEARER).
- `sasl.enabled.mechanisms` khai được **per-listener**: `listener.name.external.sasl.enabled.mechanisms=SCRAM-SHA-512`. Inter-broker chọn **đúng một** bằng `sasl.mechanism.inter.broker.protocol`; controller có key riêng `sasl.mechanism.controller.protocol` (mặc định **`GSSAPI`**).
- **Thu hồi credential ≠ cắt kết nối.** `connections.max.reauth.ms` mặc định **0** = **không** có re-authentication → kết nối đã xác thực **sống mãi** cho tới khi tự đứt. Xoá SCRAM credential chỉ chặn **lần kết nối sau**. Muốn thu hồi có hiệu lực trong vòng N mili-giây thì đặt `connections.max.reauth.ms=N` (ví dụ `3600000`) trên listener đó — client hiện đại sẽ tự xác thực lại, client cũ bị **ngắt** khi hết hạn.
- **Delegation token** (chỉ cần nhận diện): bí mật ngắn hạn cấp cho job phân tán thay vì phát keytab/keystore; auth qua SCRAM với `tokenauth="true"`; `delegation.token.secret.key` **phải giống hệt trên mọi broker và controller**; mặc định hết hạn **86400000 ms (1 ngày)**, vòng đời tối đa **604800000 ms (7 ngày)**.
- **Đổi mechanism trên cluster đang chạy** (dạng câu list-order): thêm mechanism mới vào `sasl.enabled.mechanisms` → **bounce lần 1** → đổi client → đổi `sasl.mechanism.inter.broker.protocol` + **bounce lần 2** → gỡ mechanism cũ → **bounce lần 3**.

**5. ACL ở quy mô — từ "tạo một ACL" sang "quản 300 topic × 80 service"**

- **Bật đúng class**: `authorizer.class.name=org.apache.kafka.metadata.authorizer.StandardAuthorizer` trên **mọi broker VÀ mọi controller**. `kafka.security.authorizer.AclAuthorizer` là bản **ZooKeeper**, đã bị gỡ ở 4.0 → khai nhầm thì **node không khởi động**.
- **Câu định nghĩa chuẩn** (đề hay trích nguyên văn): *"Principal {P} is [Allowed|Denied] Operation {O} From Host {H} on any Resource {R} matching ResourcePattern {RP}"*.
- **Bảng operation × resource type** — cột bên phải là thứ phải cấp, không phải thứ nghe có lý:

| Việc client làm | Operation + Resource cần | Ghi chú vận hành |
| --- | --- | --- |
| Produce thường | `Write` + `Describe` trên **Topic** | `--producer` sinh **Write + Describe + Create** |
| Producer **idempotent** (mặc định bật từ 3.0) | Chỉ `Write` trên **Topic** (broker ≥ 2.8) | Broker cũ hơn cần thêm **`IdempotentWrite` trên Cluster** — đây là bẫy "giá trị cũ" |
| Producer **transactional** | `Write` + `Describe` trên **TransactionalId** (+ quyền topic) | Dùng **PREFIXED** theo tiền tố `transactional.id` |
| Consume theo group | `Read` + `Describe` trên **Topic**, **`Read` trên Group** | `--consumer --group g` sinh đủ bộ. Thiếu vế Group → `GroupAuthorizationException` |
| Tạo topic | `Create` trên **Cluster** *hoặc* `Create` trên **Topic** | Auto-create cũng đi qua đúng luật này |
| Xoá topic / xoá record | `Delete` trên **Topic** | |
| Tăng partition | `Alter` trên **Topic** | |
| Xem / sửa config | `DescribeConfigs` / `AlterConfigs` trên **Topic** hoặc **Cluster** | `AlterConfigs` **ngầm cho** `DescribeConfigs` |
| Reassign partition, elect leader | `Alter` trên **Cluster** | Quyền của **người vận hành**, không phải của app |
| Quản ACL | `Alter` trên **Cluster** (xem: `Describe` trên Cluster) | |
| Liệt kê group | `Describe` trên **Cluster** | Vì sao `--list` group của một service thường thất bại dù nó consume được bình thường |
| Tạo / xem delegation token cho user khác | `CreateTokens` / `DescribeTokens` trên **User** | |
| Follower fetch (broker) | `ClusterAction` trên **Cluster** | Lý do broker phải nằm trong `super.users` hoặc có ACL riêng |

- **Quy tắc đánh giá**: **Deny thắng Allow** trong mọi trường hợp → không có ACL khớp thì **từ chối**. `allow.everyone.if.no.acl.found=true` chỉ nới cho resource **chưa có bất kỳ ACL nào**; thêm **một** ACL vào topic đó là nó quay lại luật thường ngay (bẫy kinh điển: "tôi thêm một ACL cho team A, cả công ty mất quyền vào topic"). `super.users=User:a;User:b` — **dấu chấm phẩy**, bỏ qua **toàn bộ** ACL, **không nhận wildcard**.
- **Operation ngầm** (quyết định "quyền tối thiểu" thật sự là gì): cấp `Read`/`Write`/`Delete` ⟹ **tự có `Describe`**; cấp `AlterConfigs` ⟹ **tự có `DescribeConfigs`**.
- **Pattern**: `LITERAL` (mặc định; `*` = mọi resource) và `PREFIXED`. Hai giá trị `any` và `match` **chỉ dùng khi truy vấn/xoá** — `--resource-pattern-type match` liệt kê **mọi ACL ảnh hưởng tới** một tên resource (literal + prefixed + wildcard), là lệnh cứu mạng khi debug.
- **Chiến lược đặt tên để tận dụng PREFIXED** — đây là câu trả lời cho "300 topic":
  `<tenant>.<domain>.<dataset>.<version>`, ví dụ `payments.orders.created.v1`. Khi đó **một** ACL `--topic payments. --resource-pattern-type prefixed` phủ cả tenant, thêm topic mới **không cần đụng ACL**. Áp dụng cùng quy ước cho `group.id` (`payments.billing-etl`) và `transactional.id` (`payments.tx-`).
- **Một principal cho một ứng dụng.** Dùng chung tài khoản thì audit vô nghĩa và thu hồi bất khả thi.
- **Audit**: authorizer ghi vào **`kafka-authorizer.log`** (logger `kafka.authorizer.logger`). Mặc định **DENY ở mức INFO**, **ALLOW ở mức DEBUG** → muốn audit đầy đủ phải hạ logger xuống DEBUG và chấp nhận log rất lớn. Dòng DENY cho bạn **principal, operation, resource, host** — tức là **đúng thứ cần cấp**, không phải đoán.
- ⚠️ **ACL áp dụng eventually consistent.** `kafka-acls.sh --add` thành công nghĩa là **controller** đã ghi record vào `__cluster_metadata`; broker còn phải replay log. Vài trăm mili-giây đầu client vẫn có thể bị từ chối — thử lại trước khi kết luận sai ACL.

**6. Quota như công cụ bảo vệ multi-tenant (nhắc lại ngắn)**

Bảo mật không chỉ là "ai được vào" mà còn là "ai được chiếm bao nhiêu". `producer_byte_rate` / `consumer_byte_rate` / `request_percentage` / `controller_mutation_rate` áp theo `(user, client-id)` > `user` > `client-id`, ghi vào metadata log nên **hiệu lực ngay, không restart**. Broker **trì hoãn response** chứ **không ném exception** → triệu chứng là "throughput chạm trần mà log sạch bong". Chi tiết và 8 mức ưu tiên: [Tuần 3](../week-03/README.md).

**7. Encryption at rest — câu trả lời ngắn nhất của tuần**

Kafka **không có** mã hoá dữ liệu trên đĩa. Hai lựa chọn: (a) **mã hoá volume/disk** ở tầng hạ tầng (LUKS, EBS encryption, KMS của cloud) — trong suốt với Kafka, không đụng client; hoặc (b) **mã hoá payload phía client** trước khi produce — bảo vệ cả khỏi admin của cluster, nhưng **phá compaction theo nội dung, phá mọi xử lý phía broker** và bạn phải tự quản khoá. Trang security overview của Kafka **không hề nhắc** encryption at rest — đó chính là bằng chứng cho đáp án.

### 🅱️ Buổi B — Hands-on (~3.5h)

> 🧪 **Lab cầm tay chỉ việc (từng bước + lệnh):** [labs.md](labs.md). Dùng lại cluster 3 broker + controller tách riêng (`docker-compose.cluster.yml` từ [CCDAK Tuần 1](../../../CCDAK/study-plan/week-01/labs.md)) và alias `kt`/`kcp`/`kcc`/`kcg`/`kcfg`.

- **Lab 5.1 ⭐ — Thiết kế nhiều listener:** `INTERNAL` PLAINTEXT cho inter-broker + `EXTERNAL` SASL_SSL cho client + `CONTROLLER` riêng; chứng minh **cả hai đường đều chạy** cùng lúc.
- **Lab 5.2 ⭐ — Xoay chứng chỉ không downtime:** tạo CA mới → nạp vào truststore → đổi keystore từng broker bằng **dynamic config** (và phương án rolling restart) → client chạy liên tục suốt quá trình **không đứt một giây**.
- **Lab 5.3 — SCRAM vận hành:** tạo 3 user, xoay mật khẩu 1 user lúc chạy, **thu hồi** 1 user và chứng minh client của user đó chết còn user khác không hề hấn; đo ảnh hưởng của `connections.max.reauth.ms`.
- **Lab 5.4 ⭐ — ACL ở quy mô:** bật `StandardAuthorizer`, ACL **PREFIXED** theo tenant, tái hiện `TopicAuthorizationException` rồi `GroupAuthorizationException`, chứng minh **Deny thắng Allow**, tra bằng `--list --principal` và `--resource-pattern-type match`.
- **Lab 5.5 — 💥 Gây hỏng rồi sửa:** thu hồi **nhầm** ACL của một service đang chạy → đọc `kafka-authorizer.log` tìm ra **đúng** quyền thiếu → cấp lại **quyền tối thiểu**.
- **Lab 5.6 — 💥 Gây hỏng rồi sửa:** cấu hình `AclAuthorizer` (class ZooKeeper cũ) → broker **không start** → đọc log → sửa sang `StandardAuthorizer`.
- **Lab 5.7 — mTLS + principal mapping:** so sánh principal **trước** (DN đầy đủ) và **sau** khi có `ssl.principal.mapping.rules`.

### 🅲️ Buổi C — Bổ sung (~2.5h)

**Bảng quyết định 1 — "Tôi cần làm việc này, có phải restart không?"**

| Việc cần làm | Restart? | Cách làm |
| --- | --- | --- |
| Thêm / xoá / xoay user **SCRAM** | ❌ | `kafka-configs.sh --alter --entity-type users --entity-name <u>` |
| Thêm / xoá **ACL** | ❌ | `kafka-acls.sh --add/--remove` (eventually consistent, chờ vài trăm ms) |
| Đặt / gỡ **quota** | ❌ | `kafka-configs.sh --alter --entity-type users|clients` |
| **Xoay keystore / truststore** của listener **đã có** | ❌ | `kafka-configs.sh --entity-type brokers --entity-name <id> --add-config listener.name.<l>.ssl.keystore.location=...` (per-broker) |
| Bật / tắt **hostname verification** của một listener | ❌ | `--add-config "listener.name.<l>.ssl.endpoint.identification.algorithm="` |
| Thêm / xoá user **PLAIN** | ✅ rolling | Sửa JAAS trên từng broker rồi bounce |
| **Thêm listener mới** hoặc đổi **protocol** của listener | ✅ rolling | Quy trình **4 pha**: mở cổng mới → đổi client → bật inter-broker → đóng cổng cũ |
| Đổi `inter.broker.listener.name` / `controller.listener.names` | ✅ rolling | Read-only config; controller đổi được nhờ khai **nhiều** listener rồi bỏ cái cũ |
| Bật **`authorizer.class.name`** lần đầu | ✅ rolling | Nhớ đặt `super.users` **trước** khi bật, nếu không tự khoá chính mình ra ngoài |
| Đổi **SASL mechanism** | ✅ 2–3 lần bounce | Thêm mechanism → bounce → đổi client → đổi inter-broker + bounce → gỡ cũ + bounce |

**Bảng quyết định 2 — "Client báo lỗi này, nhìn vào đâu?"**

| Thông điệp client thấy | Tầng hỏng | Đọc gì đầu tiên |
| --- | --- | --- |
| `Bootstrap broker ... disconnected` + broker log *"SSL handshake failed"* | Protocol/listener | `security.protocol` của client có khớp `listener.security.protocol.map` của cổng đó không |
| `SSLHandshakeException: No subject alternative names present` | TLS / PKI | SAN của cert broker; **cấp lại cert**, đừng tắt hostname verification |
| `SSLHandshakeException: PKIX path building failed` | TLS / truststore | Truststore client thiếu CA (hoặc thiếu **intermediate**) |
| `SaslAuthenticationException` | Authentication | Credential sai / đã bị thu hồi. Lỗi **fatal**, client không retry |
| `UnsupportedSaslMechanismException` | Authentication | `sasl.mechanism` client không nằm trong `sasl.enabled.mechanisms` của **listener đó** |
| `TopicAuthorizationException: Not authorized to access topics: [X]` | Authorization | `kafka-authorizer.log` dòng DENY → thiếu operation nào trên Topic |
| `GroupAuthorizationException: Not authorized to access group: g` | Authorization | Thiếu **`Read` trên Group** — quyền topic đã đúng rồi |
| `ClusterAuthorizationException` | Authorization | Thao tác cấp cluster (tạo topic, reassign, quản ACL) |
| `TransactionalIdAuthorizationException` | Authorization | Thiếu `Write`/`Describe` trên **TransactionalId** |
| Nối được, không lỗi, nhưng throughput chạm trần phẳng lì | Quota | `produce-throttle-time-avg` / `fetch-throttle-time-avg` |

**Đọc thêm:** [`resources/INDEX.md`](resources/INDEX.md) theo đúng thứ tự gợi ý; chương 11 *Securing Kafka* trong *Kafka: The Definitive Guide* 2nd ed.; Confluent Developer course *Kafka Security*.

### 🅳 Buổi D — Practice + Review (~2h) ⭐ CHECKPOINT

> 📝 **Bộ câu hỏi luyện tập của tuần:** [questions.md](questions.md) — đáp án & giải thích: [answers.md](answers.md). *(tiếng Anh, văn phong CCAAK.)*

- Làm **30 câu** của tuần trong **45 phút**, không mở tài liệu. Chấm theo bảng ở cuối [answers.md](answers.md).
- **⭐ MINI-MOCK SEC — ngưỡng ≥70% (21/30).** Đây là **cổng chặn**: chưa đạt thì **không** sang Tuần 6.
  - 70–79% → ôn lại đúng mục Buổi A tương ứng với các câu sai, làm lại lab của mục đó, rồi tự trộn một bộ 30 câu khác từ questions.md Tuần 1–5.
  - <70% → làm lại **toàn bộ** Lab 5.1, 5.2, 5.4, 5.5 trước khi thử lại. Security là domain mà lab thay thế được lý thuyết, không chiều ngược lại.
- **Ghi sổ câu sai** và phân loại theo 5 nhóm: listener · TLS/rotation · SASL/credential · ACL · version trap.
- **Spaced repetition** theo mốc **1 / 3 / 7 ngày** cho các con số: 4096 iterations · 1 ngày / 7 ngày token · `connections.max.reauth.ms`=0 · 3 giá trị `ssl.client.auth` · 3 mức ưu tiên JAAS · 4 pha bật bảo mật.

## 🧠 PHẢI NHỚ tuần này

| Fact | Con số / Ghi nhớ |
| --- | --- |
| 4 security protocol | `PLAINTEXT` · `SSL` · `SASL_PLAINTEXT` · `SASL_SSL` — tên listener thì **tự do**, phải map bằng `listener.security.protocol.map` |
| Inter-broker khi không khai gì | Rơi về `security.inter.broker.protocol` = **`PLAINTEXT`**; **không** khai cùng lúc với `inter.broker.listener.name` |
| Controller listener | Khai bằng `controller.listener.names`, **không được trùng** inter-broker; broker-only **vẫn phải khai** nhưng **không** đưa vào `listeners`; nhận **nhiều** giá trị, cái **đầu** dùng cho outbound |
| `ssl.client.auth` | `none` (**mặc định**, principal `User:ANONYMOUS`) · `requested` (**an toàn giả**) · `required` (**mTLS**) |
| Cert broker: 3 điều kiện | **Hostname verification** bật mặc định từ **2.0** (`ssl.endpoint.identification.algorithm=https`) → phải có **SAN**, tắt = đặt rỗng (không nên) · định dạng **PKCS12 mặc định từ Java 9**, **PEM từ 2.7** · **EKU cần cả `serverAuth` lẫn `clientAuth`** vì broker cũng là client khi replicate |
| Principal mTLS mặc định | **Toàn bộ DN**; rút gọn bằng `ssl.principal.mapping.rules=RULE:^CN=(.*?),.*$/$1/,DEFAULT` |
| Xoay chứng chỉ | Thứ tự bất biến **truststore (CA mới) TRƯỚC → keystore SAU → gỡ CA cũ CUỐI** · đổi được **lúc chạy**, per-broker dynamic: `listener.name.<l>.ssl.keystore.location` / `.ssl.truststore.location` · luật inter-broker: đổi **keystore** cần keystore **mới** được truststore **hiện tại** tin, đổi **truststore** cần keystore **hiện tại** được truststore **mới** tin |
| SCRAM vs PLAIN | **SCRAM**: lưu trong `__cluster_metadata`, salt+hash, **≥4096 iterations**, thêm/xoay/thu hồi **lúc chạy** bằng `kafka-configs.sh --entity-type users`, seed admin bằng `kafka-storage.sh format --add-scram`. **PLAIN**: credential **tĩnh trong JAAS** → mỗi user mới là một **rolling restart**; chỉ dùng trên `SASL_SSL` |
| Thứ tự ưu tiên JAAS (broker) | `listener.name.{l}.{mech}.sasl.jaas.config` > `{l}.KafkaServer` > `KafkaServer` |
| `connections.max.reauth.ms` | Mặc định **0** = **không re-auth** → **thu hồi credential không cắt kết nối đang mở** |
| Delegation token | `delegation.token.secret.key` giống nhau **mọi broker + controller**; hết hạn **1 ngày**, vòng đời tối đa **7 ngày** |
| Authorizer KRaft | `org.apache.kafka.metadata.authorizer.StandardAuthorizer` (từ **3.2.0**), khai trên **broker VÀ controller**; `AclAuthorizer` là ZooKeeper, **đã gỡ ở 4.0** |
| Định nghĩa ACL | *"Principal {P} is [Allowed|Denied] Operation {O} From Host {H} on any Resource {R} matching ResourcePattern {RP}"* |
| Luật ACL | **Deny thắng Allow**; không khớp → **từ chối**; `allow.everyone.if.no.acl.found` chỉ nới cho resource **chưa có ACL nào**; `super.users` ngăn bằng **`;`**, bỏ qua toàn bộ ACL, **không wildcard** |
| Resource × operation × pattern | **6 resource** (Topic, Group, Cluster, TransactionalId, DelegationToken, User) × **13 operation**; Read/Write/Delete ⟹ ngầm **Describe** · pattern `literal` (mặc định) và `prefixed` **tạo được**, `any`/`match` **chỉ để truy vấn** |
| ACL của producer/consumer | `--producer` = **Write + Describe + Create** · `--consumer --group g` = **Read + Describe** trên Topic **+ Read** trên Group · idempotent chỉ cần `Write` trên Topic với broker ≥2.8 (broker cũ cần **`IdempotentWrite` trên Cluster**) · transactional cần **`Write` trên TransactionalId** |
| Audit | `kafka-authorizer.log` (`kafka.authorizer.logger`): **DENY = INFO**, **ALLOW = DEBUG** |
| Bật bảo mật cho cluster đang chạy | **4 pha**: mở cổng mới → đổi client → bật inter-broker → **đóng PLAINTEXT cuối cùng**; SIGTERM + chờ **URP về 0** giữa mỗi node |
| Encryption at rest | Kafka **KHÔNG có sẵn** → mã hoá volume/disk, hoặc mã hoá payload phía client |

## 🚨 Playbook: triệu chứng → hành động

| Triệu chứng quan sát được | Nguyên nhân khả dĩ | Hành động đầu tiên |
| --- | --- | --- |
| Toàn bộ client ngoài mất kết nối ngay sau khi thay cert, client nội bộ vẫn chạy | Đổi keystore **trước khi** CA mới có trong truststore client; listener không phải inter-broker **không được kiểm tra** trước khi đổi | Khôi phục keystore cũ bằng `kafka-configs.sh --delete-config listener.name.<l>.ssl.keystore.location`, rồi làm lại đúng thứ tự truststore-trước |
| Replication đứt, `UnderReplicatedPartitions` vọt lên sau khi đụng vào TLS | Truststore mới **không tin** keystore hiện tại của inter-broker listener | Đọc `server.log` tìm `SSLHandshakeException` giữa các broker; trả truststore về bản có **cả hai** CA |
| Một service báo `TopicAuthorizationException`, các service khác bình thường | ACL của riêng principal đó bị xoá/hết hiệu lực, hoặc topic mới không khớp prefix | `grep DENY /opt/kafka/logs/kafka-authorizer.log` lấy **principal + operation + resource**, rồi `kafka-acls.sh --list --principal User:<p>` |
| Client báo `GroupAuthorizationException` nhưng produce vẫn được | Thiếu **`Read` trên Group** (quyền Topic đã đủ) | `kafka-acls.sh --add --allow-principal User:<p> --operation Read --group <g>` |
| ACL vừa thêm mà client vẫn bị từ chối vài giây | Áp dụng **eventually consistent** — broker chưa replay xong record trong `__cluster_metadata` | Chờ và thử lại; nếu quá 5–10 giây thì kiểm `kafka-metadata-quorum.sh describe --status` xem broker có bị tụt log không |
| Sau khi bật authorizer, **chính admin** cũng không làm gì được | Quên `super.users` hoặc principal của admin không khớp (DN đầy đủ thay vì CN) | Vào bằng `--bootstrap-controller`, hoặc tạm thêm `super.users` rồi rolling restart; kiểm principal thật trong `kafka-authorizer.log` |
| Broker **không khởi động**, log có `ConfigException ... could not be found` | Khai class thời ZooKeeper (`AclAuthorizer`) hoặc sai package | Sửa sang `org.apache.kafka.metadata.authorizer.StandardAuthorizer` trên **mọi** node |
| Đã xoá credential SCRAM của một user nhưng client của họ **vẫn ghi được** | `connections.max.reauth.ms=0` → không có re-authentication, kết nối cũ sống tiếp | Đặt `connections.max.reauth.ms` cho listener đó; biện pháp tức thời: thêm **Deny ACL** cho principal đó |
| Client mới không nối được listener SASL, client cũ vẫn chạy | `sasl.mechanism` của client không nằm trong `sasl.enabled.mechanisms` **của listener đó** | Đối chiếu `listener.name.<l>.sasl.enabled.mechanisms`; lỗi là `UnsupportedSaslMechanismException`, **không phải** ACL |
| Broker mới thêm vào cluster không join được quorum sau khi bật TLS | `controller.listener.names` / `controller.quorum.bootstrap.servers` không khớp cổng và protocol đang expose | So `listeners`, `listener.security.protocol.map` và chuỗi quorum; controller listener **không** nằm trong `advertised.listeners` |
| Throughput của một tenant phẳng lì ở một mức, log hoàn toàn sạch | **Quota**, không phải bảo mật | `kafka-configs.sh --describe --entity-type users --entity-name <u>`; xem `produce-throttle-time-avg` |
| CPU broker tăng vọt sau khi bật TLS cho inter-broker | Mất **zero-copy `sendfile`** ở đường replication | Đây là hành vi **bình thường**; tính lại sizing hoặc cân nhắc giữ inter-broker trong mạng riêng |

## ⚠️ Bẫy đề hay gặp

- Thấy "bật authorization cho cluster KRaft" → dễ chọn `kafka.security.authorizer.AclAuthorizer`, nhưng đúng là **`org.apache.kafka.metadata.authorizer.StandardAuthorizer`**; class cũ là của **ZooKeeper** và đã bị gỡ ở 4.0 → node **không start**. *(bẫy version)*
- Thấy "quản ACL / tạo user SCRAM / đặt quota" mà phương án có **`--zookeeper`** hoặc `zookeeper.set.acl` → **luôn sai** ở Kafka 4.x; mọi tool đã thống nhất `--bootstrap-server` (và `--bootstrap-controller`). *(bẫy version)*
- Thấy "`ssl.client.auth=requested` cho an toàn hơn `none`" → dễ chọn đúng, nhưng docs gọi nó là **"false sense of security"**: client cấu hình sai **vẫn vào được** dưới danh nghĩa `ANONYMOUS`. Muốn mTLS thì phải **`required`**.
- Thấy "cert sắp hết hạn, xoay thế nào" → dễ chọn "rolling restart thay keystore rồi phát CA mới cho client", nhưng đúng là **phát CA mới vào truststore TRƯỚC**, đổi keystore SAU; ngược thứ tự là đứt client hoặc đứt replication. Và dễ chọn tiếp "không restart thì không xoay được" — thực ra keystore/truststore của listener **đã tồn tại** là **per-broker dynamic config**; cái **không** đổi động được là **thêm listener mới** hay đổi protocol.
- Thấy "thêm 50 service mới, chọn mechanism nào" → dễ chọn `PLAIN` vì đơn giản, nhưng PLAIN lưu credential **tĩnh trong JAAS** → mỗi user mới là một lần **rolling restart**. Đáp án là **SCRAM** (hoặc OAUTHBEARER nếu đã có IdP).
- Thấy "đã xoá credential của user, họ không vào được nữa" → dễ chọn đúng, nhưng với `connections.max.reauth.ms=0` (**mặc định**) kết nối **đang mở vẫn sống**. Muốn thu hồi tức thì phải bật re-authentication hoặc thêm **Deny ACL**.
- Thấy "topic chưa có ACL nào, bật `allow.everyone.if.no.acl.found=true`" → dễ nghĩ nó nới cho **mọi** topic, nhưng nó **chỉ** nới cho resource **chưa có bất kỳ ACL nào**; thêm một ACL cho một team là cả công ty mất quyền vào topic đó.
- Thấy "producer idempotent cần quyền gì" → dễ chọn `IdempotentWrite` trên **Cluster**; với broker **≥2.8** chỉ cần **`Write` trên Topic**. `IdempotentWrite` là yêu cầu của broker cũ. *(giá trị cũ)*
- Thấy "service produce được nhưng không consume được" → dễ đi thêm quyền trên Topic, nhưng thiếu là **`Read` trên Group**; tên ngoại lệ đã nói thẳng: `GroupAuthorizationException`.
- Thấy "ACL prefixed đã cấp Write cho cả `payments.`, vì sao vẫn bị chặn ở `payments.orders`" → dễ nghĩ prefixed không hoạt động, nhưng gần như luôn là có một **Deny ACL** hẹp hơn: **Deny thắng Allow** bất kể pattern rộng hay hẹp.
- Thấy "bật bảo mật cho cluster đang chạy" mà phương án nào **đóng cổng PLAINTEXT ở bước 1 hoặc 2** → sai; PLAINTEXT phải mở **xuyên suốt** và chỉ đóng ở **lần bounce cuối cùng**.
- Thấy "đặt `ssl.endpoint.identification.algorithm=` để sửa lỗi SAN" → chạy được nên rất dễ chọn, nhưng đó là **workaround**; cách đúng là **cấp lại cert có SAN**. Cùng loại bẫy "config nghe có lý": **Kafka không có config nào** cho encryption at rest — đáp án là volume encryption hoặc mã hoá payload phía client.

## 🧪 Lab checklist

- [ ] Lab 5.1 ⭐ — Dựng 3 listener (`INTERNAL` PLAINTEXT / `EXTERNAL` SASL_SSL / `CONTROLLER`) trên cluster 3 broker; chứng minh cả đường nội bộ lẫn đường ngoài cùng chạy.
- [ ] Lab 5.2 ⭐ — Xoay chứng chỉ: CA mới → truststore → đổi keystore từng broker; client chạy liên tục **không mất một message nào**.
- [ ] Lab 5.3 — Tạo 3 user SCRAM, xoay mật khẩu 1 user, thu hồi 1 user; quan sát ảnh hưởng của `connections.max.reauth.ms`.
- [ ] Lab 5.4 ⭐ — `StandardAuthorizer` + ACL `PREFIXED` theo tenant; tái hiện `TopicAuthorizationException` → `GroupAuthorizationException`; chứng minh Deny thắng Allow; dùng `--list --principal` và `--resource-pattern-type match`.
- [ ] Lab 5.5 — 💥 Thu hồi nhầm ACL → chẩn đoán bằng `kafka-authorizer.log` → cấp lại quyền tối thiểu.
- [ ] Lab 5.6 — 💥 Khai `AclAuthorizer` → broker không start → đọc `ConfigException` → sửa sang `StandardAuthorizer`.
- [ ] Lab 5.7 — mTLS: so sánh principal trước/sau `ssl.principal.mapping.rules`.

## 🚪 Cổng tự kiểm tra (phải trả lời trôi chảy mới sang tuần sau)

- **Một cluster KRaft có broker-only node. Node đó cần khai những config listener nào, và cái nào KHÔNG được xuất hiện trong `listeners`?**
  **Đáp án gọn:** khai `listeners` (listener client + inter-broker), `advertised.listeners`, `listener.security.protocol.map` (gồm **cả** entry cho CONTROLLER), `inter.broker.listener.name`, `controller.listener.names`, cùng chuỗi quorum (`controller.quorum.bootstrap.servers` với dynamic quorum, hoặc `controller.quorum.voters` với static quorum như compose của lab). **Listener CONTROLLER không nằm trong `listeners`** của broker-only node, và tên của nó **không được trùng** inter-broker.
- **Cert của 12 broker hết hạn sau 3 tuần. Nêu đúng thứ tự các bước để thay mà không downtime.**
  **Đáp án gọn:** (1) ký cert mới bằng CA mới; (2) nạp **CA mới vào truststore** của **mọi broker và mọi client** (truststore chứa cả 2 CA); (3) chờ client phủ hết; (4) đổi **keystore từng broker một** bằng `kafka-configs.sh --entity-type brokers --entity-name <id> --add-config listener.name.<l>.ssl.keystore.location=...` (hoặc rolling restart, chờ URP về 0 giữa các node); (5) gỡ CA cũ khỏi truststore.
- **Vì sao "đổi keystore trước rồi mới phát CA mới" lại hỏng, và hỏng khác nhau thế nào giữa listener inter-broker và listener client?**
  **Đáp án gọn:** inter-broker listener **bị broker chặn** — đổi keystore chỉ được phép nếu keystore mới đã được truststore hiện tại tin. Listener client **không được kiểm tra gì cả** → lệnh chạy thành công và **toàn bộ client rớt ngay lập tức** vì không tin CA mới.
- **Thu hồi credential SCRAM của một service lúc 10:00. Đến 10:05 nó vẫn ghi được. Giải thích và nêu 2 cách xử lý.**
  **Đáp án gọn:** `connections.max.reauth.ms` mặc định **0** = không re-authentication, nên kết nối đã xác thực trước đó vẫn sống. Cách xử lý: (a) thêm **Deny ACL** cho principal đó — có hiệu lực ngay ở tầng authorization; (b) đặt `connections.max.reauth.ms` (ví dụ 3600000) để ép xác thực lại định kỳ, áp dụng cho lần sau.
- **300 topic, 80 service. Viết ACL kiểu gì để không phải sửa mỗi lần thêm topic?**
  **Đáp án gọn:** đặt quy ước tên `<tenant>.<domain>.<dataset>.<version>` rồi dùng **`--resource-pattern-type prefixed`** theo tenant, áp dụng cùng quy ước cho `group.id` và `transactional.id`. Một principal cho một ứng dụng. Nhớ operation ngầm (Read/Write/Delete ⟹ Describe) để không cấp thừa.
- **`kafka-acls.sh --list --topic payments.orders` không thấy ACL nào, nhưng service vẫn produce được. Vì sao?**
  **Đáp án gọn:** `--list` mặc định chỉ khớp pattern **LITERAL** đúng tên. ACL đang có hiệu lực là **PREFIXED** (`payments.`) hoặc wildcard `*`. Dùng **`--resource-pattern-type match`** để thấy **mọi** ACL ảnh hưởng tới topic đó.
- **Ba họ lỗi bảo mật và log tương ứng?**
  **Đáp án gọn:** (1) **protocol/TLS** → `server.log` phía broker (`SSL handshake failed`, `PKIX path building failed`, `No subject alternative names`); (2) **authentication** → `SaslAuthenticationException` / `UnsupportedSaslMechanismException`, kiểm `sasl.enabled.mechanisms` của đúng listener; (3) **authorization** → `kafka-authorizer.log` dòng DENY, cho biết chính xác principal + operation + resource.
- **⭐ CHECKPOINT:** đã đạt **≥70%** ở MINI-MOCK SEC (30 câu / 45 phút) chưa? Nếu chưa → **KHÔNG** sang Tuần 6; làm lại Lab 5.1, 5.2, 5.4, 5.5 rồi thi lại.

## 📎 Tài nguyên tuần này

> 📂 **Đã crawl sẵn tài liệu chính thức vào** [`resources/`](resources/INDEX.md) — đọc offline được, có gợi ý thứ tự đọc.

- Apache Kafka Docs 4.3 — *Security*: [Security Overview](https://kafka.apache.org/43/security/security-overview/) · [Listener Configuration](https://kafka.apache.org/43/security/listener-configuration/) · [Encryption and Authentication using SSL](https://kafka.apache.org/43/security/encryption-and-authentication-using-ssl/) · [Authentication using SASL](https://kafka.apache.org/43/security/authentication-using-sasl/) · [Authorization and ACLs](https://kafka.apache.org/43/security/authorization-and-acls/) · [Incorporating Security Features in a Running Cluster](https://kafka.apache.org/43/security/incorporating-security-features-in-a-running-cluster/).
- Apache Kafka Docs 4.3 — [Broker Configs](https://kafka.apache.org/43/generated/kafka_config.html): nhóm `ssl.*`, `sasl.*`, `authorizer.class.name`, `super.users`, `allow.everyone.if.no.acl.found`, `connections.max.reauth.ms`, `delegation.token.*`.
- Confluent Platform Docs — [ACLs overview](https://docs.confluent.io/platform/current/security/authorization/acls/overview.html) · [Dynamic configurations](https://docs.confluent.io/platform/current/kafka/dynamic-config.html) (xoay keystore/truststore không restart) · [Security overview](https://docs.confluent.io/platform/current/security/general-overview.html).
- KIP: **KIP-801** (`StandardAuthorizer` lưu ACL trong `__cluster_metadata`, từ 3.2.0) · **KIP-554** (API broker-side cho SCRAM, bỏ phụ thuộc ZooKeeper) · KIP-11 (mô hình ACL) · KIP-290 (prefixed ACL) · KIP-684 (`ssl.principal.mapping.rules`).
- Sách: *Kafka: The Definitive Guide* 2nd ed. — Chương 11 *Securing Kafka* (bản đồ chương: [`kafka-definitive-guide-chapter-map.md`](../../../CCDAK/study-plan/week-10/resources/kafka-definitive-guide-chapter-map.md)).
- Khoá học: Confluent Developer — *Apache Kafka Security*; Stephane Maarek — *Kafka Security (SSL, SASL, ACL)*.

## ✅ Checklist hoàn thành Tuần 5

- [ ] Hoàn thành 4 buổi A/B/C/D
- [ ] Vẽ lại được từ trí nhớ **sơ đồ 4 listener** của một cluster production và 5 config đi kèm
- [ ] Thuộc bảng "PHẢI NHỚ" (4096 iterations · 1 ngày/7 ngày token · `connections.max.reauth.ms`=0 · 3 giá trị `ssl.client.auth` · 3 mức JAAS · 4 pha bật bảo mật · 6 resource × 13 operation)
- [ ] Đọc trôi **Playbook triệu chứng → hành động** mà không cần tra
- [ ] Hoàn thành **cả 7 lab**, trong đó **bắt buộc** 2 lab "gây hỏng rồi sửa" (5.5, 5.6)
- [ ] Làm xong 30 câu [questions.md](questions.md), ghi sổ câu sai theo 5 nhóm
- [ ] **Đạt ≥70% MINI-MOCK SEC (30 câu, 45 phút)** — ⭐ CHECKPOINT
- [ ] Vượt Cổng tự kiểm tra
