# ✅ Nhật ký Validate kiến thức — CCAAK Study Plan

> **Ngày lập:** 2026-09-20 · **Phiên bản neo:** Apache Kafka **4.3.x** (KRaft-only).
> **Phương pháp:** đối chiếu số liệu với `kafka.apache.org/43/generated/kafka_config.html` và `topic_config.html`, trang Operations/Monitoring/Security của Kafka 4.3, docs Confluent, và các file đã crawl trong `week-NN/resources/`.
> Mục tiêu: **tránh học số cũ** và **ghi rõ chỗ nào cần đối chiếu lại trước ngày thi**.
> Xem thêm: [nhật ký validate của bộ CCDAK](../../CCDAK/study-plan/VALIDATION.md) — phần lớn mặc định client dùng chung.

---

## 🔴 Vì sao tài liệu CCAAK công khai nguy hiểm hơn CCDAK

Đây là phát hiện quan trọng nhất của đợt khảo sát. Số liệu đo trực tiếp trên hai kho câu hỏi CCAAK lớn nhất tìm được trên GitHub:

| Chỉ số | Kết quả |
|---|---|
| Số lần nhắc **ZooKeeper** | **118** |
| Số lần nhắc **KRaft** | **3** |
| KIP-848 · share groups · ELR · Cluster Linking · cooperative rebalance | **0** mỗi loại |
| Tiered storage | 1 |
| Commit cuối cùng | 2025-03 và 2024-10 |

Tỉ lệ ZooKeeper trên KRaft là **118 : 3** — đảo ngược hoàn toàn so với Kafka hiện tại, nơi ZooKeeper **đã bị gỡ khỏi 4.0**.

Nghiêm trọng hơn CCDAK ở một điểm: trong kho CCAAK, ZooKeeper thường là **đáp án đúng**, không phải phương án nhiễu. Ví dụ có thật:

- *"When the broker running the controller thread fails, which broker becomes the new controller?"* → đáp án được ghi là **"The next broker to successfully recreate the ZooKeeper ephemeral node"**. Với KRaft, controller được bầu bằng **Raft** trong controller quorum; không có ephemeral node nào.
- *"Which of the following are components of Kafka?"* → đáp án đúng gồm **ZooKeeper**.

Với một kỳ thi **administrator**, chuyển đổi ZooKeeper sang KRaft chính là thay đổi vận hành trung tâm. Học theo tài liệu này không chỉ thiếu sót mà còn **dẫn tới đáp án sai**.

Chi tiết nguồn và phương pháp đo: [`../mock-exams/SOURCES-AND-VALIDATION.md`](../mock-exams/SOURCES-AND-VALIDATION.md).

---

## 🟢 Thông số kỳ thi — đã xác minh chéo

| Hạng mục | Giá trị | Nguồn |
|---|---|---|
| Số câu | **60** | Syllabus VMExam · bigdataprep |
| Thời gian | **90 phút** | Trang Confluent chính thức |
| Giá | **150 USD** | VMExam · bigdataprep |
| Chấm | **Pass/Fail**, không công bố ngưỡng | Trang Confluent chính thức |
| Dạng câu | multiple-choice · multiple-select · matching · list order | Trang Confluent chính thức |
| Hiệu lực / retake | 2 năm · chờ 7 ngày | Trang Confluent chính thức |
| Proctor | Honorlock (Chrome, webcam, micro, government ID) | Trang Confluent chính thức |

**Tỉ trọng 7 domain — xác nhận bởi 2 nguồn độc lập** (syllabus VMExam và bài phân tích bigdataprep 07/2026, hai bên khớp nhau hoàn toàn):

| Domain | Tỉ trọng |
|---|---|
| Apache Kafka Cluster Configuration | 22% |
| Apache Kafka Fundamentals | 15% |
| Apache Kafka Security | 15% |
| Troubleshooting | 15% |
| Deployment Architecture | 12% |
| Kafka Connect | 12% |
| Observability | 10% |

> ⚠️ Tổng là **101%** do Confluent làm tròn từng domain. Đây là con số công bố, không phải lỗi chép.

> 🔄 **Syllabus đã được cấu trúc lại.** Tài liệu CCAAK cũ (ví dụ repo `isaac88`, cập nhật 10/2024) chia đề thành **4 domain**: Kafka Fundamentals 15% · Managing, Configuring and Optimizing a Cluster for Performance **30%** · Kafka Security 15% · Designing, Troubleshooting and Integrating Systems **40%**. Cấu trúc 7 domain ở bảng trên mới là bản hiện hành. Gặp tài liệu chia 4 domain thì biết ngay nó thuộc thế hệ trước — đây là cách nhanh nhất để nhận diện đề cũ.

---

## 🟢 Số liệu broker — đã đối chiếu trực tiếp

Đối chiếu https://kafka.apache.org/43/generated/kafka_config.html ngày 2026-09-20:

| Config | Default | Config | Default |
|---|---|---|---|
| `num.network.threads` | 3 | `queued.max.requests` | 500 |
| `num.io.threads` | 8 | `socket.send.buffer.bytes` | 102400 |
| `num.replica.fetchers` | 1 | `socket.receive.buffer.bytes` | 102400 |
| `background.threads` | 10 | `socket.request.max.bytes` | 104857600 |
| `controlled.shutdown.enable` | true | `replica.socket.timeout.ms` | 30000 |
| `auto.create.topics.enable` | true | `log.cleaner.threads` | 1 |
| `auto.leader.rebalance.enable` | true | `offsets.topic.replication.factor` | 3 |
| `leader.imbalance.check.interval.seconds` | 300 | `transaction.state.log.replication.factor` | 3 |
| `controller.quorum.election.timeout.ms` | 1000 | `transaction.state.log.min.isr` | 2 |

---

## 🟡 Chỗ cần ĐỐI CHIẾU LẠI trước ngày thi

**Kỳ thi**
- **Ngưỡng đậu** không được công bố. Con số ~75% lưu hành trên mạng là phỏng đoán của cộng đồng. Giữ ngưỡng cá nhân **≥80%**.
- **Giá 150 USD** và **số câu 60** không in trên trang Confluent chính thức (trang chỉ nêu 90 phút và các dạng câu) — hai con số đến từ syllabus bên thứ ba. Kiểm trên trang đăng ký trước khi thanh toán.

**Số liệu chưa xác minh được từ trang generated config**
- `controlled.shutdown.max.retries` (thường ghi là **3**) và `leader.imbalance.per.broker.percentage` (thường ghi là **10**) không xuất hiện trong phần trích xuất được. Nếu một câu hỏi xoay quanh hai con số này, hãy tra lại trước khi tin.

**Khuyến nghị vận hành, không phải giá trị mặc định**
- Heap broker **6 GB**, **G1GC**, file descriptor **100.000+**, `vm.swappiness` **1**, filesystem **XFS**. Đây là *khuyến nghị* phổ biến trong tài liệu vận hành, không phải config có default trong Kafka. Đề có thể hỏi theo hướng "thực hành tốt", nhưng đừng trình bày chúng như default.

**Confluent Platform, không phải Apache Kafka**
- **Cluster Linking**, RBAC, Self-Balancing Clusters, Control Center chỉ có ở **Confluent Platform**. Lab local trên `apache/kafka` không chạy được. Đề CCAAK là chứng chỉ của Confluent nên vẫn có thể hỏi — học ở mức nhận diện và so sánh với MirrorMaker 2.

**Mẹo crawl: WebFetch trả về bản tóm tắt, không phải nguyên văn**

Nhiều lần "trang bị cắt" thực ra là do WebFetch **tóm tắt** nội dung thay vì trả nguyên văn, đặc biệt với trang lớn như `generated/kafka_config.html` (~1 MB). Agent Tuần 3 xử lý bằng **`curl` + `textutil`** và lấy được nguyên văn ở 12 trang. Nếu cần trích chính xác một bảng config, hãy dùng cách đó thay vì WebFetch.

**Docs Apache tự mâu thuẫn ở một chỗ**
- Quota window: trang **generated config** ghi `quota.window.num` **11** × `quota.window.size.seconds` **1**, nhưng trang **Design** nêu ví dụ *"30 windows of 1 second"*. Tài liệu trong repo theo **generated config** và ghi chú chỗ lệch.
- `vm.swappiness=1` chỉ xuất hiện trong **docs Confluent**, không có trong docs Apache — trình bày như khuyến nghị của Confluent, không phải chuẩn Apache.

**Nguồn không crawl được — vấn đề hệ thống**
- **`cwiki.apache.org` (trang KIP) trả về rỗng với WebFetch** ở mọi dạng URL đã thử, lặp lại ở nhiều tuần (KIP-500, KIP-853, KIP-1066, KIP-113/849/928). Nội dung KIP trong `resources/` được dựng lại từ kết quả tìm kiếm trên chính cwiki cộng docs Apache và Confluent, và **luôn có cảnh báo ở đầu file**. Khi cần trích dẫn chính xác một KIP, hãy mở thẳng trang cwiki bằng trình duyệt.
- Mục *Updating Broker Configs* của `/43/configuration/broker-configs/` bị **cắt ngắn** trong mọi lần fetch → bảng 5 mức ưu tiên config phải ghép từ trang Confluent (nêu 3 mức broker) cộng KIP-226. Đã ghi rõ trong resource của Tuần 2.

**Mặc định bảo mật — trang config bị cắt, mức xác minh không đồng đều**

`kafka.apache.org/43/generated/kafka_config.html` **bị cắt trước phần security** ở mọi lần fetch (trang ~1 MB). Mức xác minh từng giá trị:

| Config | Giá trị | Mức xác minh |
|---|---|---|
| `allow.everyone.if.no.acl.found` | `false` | ✅ **Xác nhận hành vi nguyên văn**: *"If a resource (R) does not have any ACLs defined… Kafka will restrict access to that resource. In this situation, only super users are allowed to access it."* |
| `ssl.client.auth` | `none` | ✅ Xác nhận trên trang SSL |
| `ssl.endpoint.identification.algorithm` | `https` | ✅ Xác nhận hành vi: hostname verification **bật mặc định từ 2.0.0**, tắt bằng cách đặt chuỗi rỗng |
| `authorizer.class.name` · `super.users` | rỗng | ⚠️ Chưa trích được giá trị; hành vi "không có ACL thì chỉ super user vào được" thì đã xác nhận |
| `ssl.keystore.type` · `ssl.truststore.type` | `JKS` | ⚠️ Docs **liệt kê** `JKS` nhưng không tuyên bố là default |
| `ssl.enabled.protocols` · `ssl.principal.mapping.rules` · `sasl.enabled.mechanisms` | TLSv1.2,TLSv1.3 · DEFAULT · GSSAPI | ⚠️ Lấy từ kiến thức, **chưa crawl xác minh** |

> ⚠️ **Bẫy dễ nhầm:** **Java 9 trở lên mặc định định dạng PKCS12**, nhưng **config `ssl.keystore.type` của Kafka vẫn là `JKS`**. Docs Apache nói rõ mọi lệnh `keytool` trong hướng dẫn **chỉ định PKCS12 tường minh** để không phụ thuộc phiên bản Java. Hai chuyện khác nhau, đừng gộp.

**Chưa trích được nguyên văn (đúng theo cơ chế, chưa có câu dẫn)**
- Giá trị mặc định của **`replica.selector.class`** (`null`, hành xử như `LeaderSelector`) — trang broker-configs bị cắt khi fetch. Sự tồn tại của config đã xác nhận qua hai nguồn.
- **`BytesOutPerSec` không tính traffic replication** (Kafka có metric riêng `ReplicationBytesOutPerSec`). Dùng làm phép kiểm chứng follower fetching ở Lab 4.3; đúng theo kiến trúc nhưng không trích được câu nguyên văn.
- Mốc **2000–4000 partition mỗi broker** đến từ tài liệu thời ZooKeeper. KRaft bầu leader nhanh hơn nên đây là mốc **thận trọng**, không phải giới hạn cứng của 4.x.

**ELR và `min.insync.replicas` — đã xác minh nguyên văn (2026-09-20)**
> *"After the ELR feature enabled, the previously set `min.insync.replicas` value at the broker-level config will be removed."* — https://kafka.apache.org/43/getting-started/upgrade/

ELR bật mặc định cho **cluster mới từ 4.1.0**. Khi bật, `min.insync.replicas` ở **mức broker bị gỡ**, phải đặt lại ở **mức cluster hoặc topic**. Đây là bẫy nâng cấp: một cấu hình durability tưởng còn hiệu lực thì thực ra đã biến mất. Mock 02 Q16 dựa trên điểm này.

**Chuỗi thông báo lỗi được dựng lại, không phải trích nguyên văn**
- Mock 02 Q30 dùng `Value must be at least 1048576` cho validator của `segment.bytes`. **Giới hạn 1 MiB là có thật** (ghi trong notable changes 4.3), nhưng **câu chữ của thông báo là dựng lại**.
- Mock 02 Q44 dùng `InvalidTimestampException` cho `message.timestamp.after.max.ms`. **Mốc 1 giờ là có thật**, tên ngoại lệ hợp lý nhưng chưa trích được nguyên văn.
- Tuần 5 Lab 5.5 dùng một dòng DENY mẫu của `StandardAuthorizer` — các **trường** là đúng, **thứ tự và từ ngữ** có thể lệch.

> 📌 Nguyên tắc chung khi gặp các mục này: câu hỏi neo vào **cơ chế và con số**, không neo vào câu chữ của thông báo. Nếu output thật khác, kiến thức vẫn đúng.

**Chi tiết dễ sai — đã xác minh**
- **MBean type của metric controller không đồng nhất.** `ActiveControllerCount` và `OfflinePartitionsCount` nằm ở `kafka.controller:type=**KafkaController**`, nhưng `UncleanLeaderElectionsPerSec` và `LeaderElectionRateAndTimeMs` nằm ở `kafka.controller:type=**ControllerStats**`. Còn `UnderReplicatedPartitions` thì ở `kafka.server:type=ReplicaManager`. Rule JMX exporter chỉ khớp `KafkaController` sẽ **âm thầm bỏ sót** hai metric kia. Đã đối chiếu https://kafka.apache.org/43/operations/monitoring/ ngày 2026-09-20. *(Lỗi này từng có trong `CCDAK/study-plan/week-08/README.md` và đã được sửa.)*
- **Exporter không gắn lên node `controller`** trong `docker-compose.monitoring.yml` của CCDAK Tuần 8 → `ActiveControllerCount` và `OfflinePartitionsCount` **không tồn tại** trong Prometheus khi cluster tách vai trò. Lab 7.1 của CCAAK thêm file override riêng để vá, không sửa file gốc.

**Hai nguồn chính thức lệch nhau**
- **Update mode của `auto.create.topics.enable` và `socket.send.buffer.bytes`**: Apache 4.3 generated config ghi là `read-only`, Confluent Broker Config Reference ghi là `cluster-wide`. Tài liệu trong repo **theo Apache** (bản neo) và ghi chú chỗ lệch. Không câu hỏi nào phụ thuộc riêng vào điểm này.
- **`connector.client.config.override.policy`**: Apache Kafka 4.3 ghi mặc định là **`All`** (đổi từ `None` ở 3.0, KIP-722), nhưng trang *Connect Security* của Confluent **vẫn in "None (default)"**. Tài liệu trong repo theo **Apache**, và biến chính chỗ lệch này thành phương án nhiễu ở Tuần 6 Q19. Từ 4.2 Confluent khuyến nghị `Allowlist`, và nó sẽ là mặc định từ 5.0.
- **KIP-875 chia làm hai bản**: **3.5** có `GET /offsets`, trạng thái `STOPPED` và `PUT /stop`; **3.6** mới có `PATCH` và `DELETE /offsets`. Tài liệu ghi "3.5+" cho cả ba là **không chính xác**.
- **Metric của log cleaner** (`max-dirty-percent`, `cleaner-recopy-percent`, `uncleanable-partitions-count`) **không xác minh được** trên trang monitoring 4.3 → cố ý **không đưa vào** tài liệu. Lab dùng bằng chứng trên đĩa (`cleaner-offset-checkpoint`, `kafka-dump-log.sh`) thay thế.

**Hành vi chưa có nguồn chính thức nói thẳng**
- **Mất đa số controller quorum thì data plane ra sao?** Kế hoạch dạy: *control plane đóng băng (không bầu leader mới, không tạo/xoá topic), data plane vẫn phục vụ partition không đổi leader*. Đây là suy luận đúng theo kiến trúc, nhưng **không trích dẫn nguyên văn được**: Apache chỉ nói *"A majority of the controllers must be alive in order to maintain availability"*, Confluent nói gọn *"the cluster becomes unavailable"*. Lab 1.3 tồn tại để bạn **tự chứng minh**. Trùng với dòng ⚠️ tương ứng trong [`../../CCDAK/study-plan/VALIDATION.md`](../../CCDAK/study-plan/VALIDATION.md).
- **Câu chữ của `InconsistentClusterIdException`** khác nhau tuỳ đường đi (storage tool chặn lúc format, hay Raft client bị controller từ chối khi fetch). Tài liệu neo vào **tên ngoại lệ**, không neo vào câu chữ.

**Thay đổi nhanh**
- Kiểm bản Kafka mới nhất; nếu **4.4+** ra mắt thì đọc mục *Notable changes*, đặc biệt các mặc định liên quan KRaft và share groups.
- KIP-1066 (cordoned log dirs) là tính năng 4.3 — cú pháp `kafka-configs.sh --alter --add-config cordoned.log.dirs` nên kiểm lại khi thực hành.

---

## 🔵 Mặc định đã đổi theo version — dùng chung với CCDAK

Bảng đầy đủ 13 mặc định đã đổi nằm ở [`../../CCDAK/study-plan/VALIDATION.md`](../../CCDAK/study-plan/VALIDATION.md). Những mục ảnh hưởng trực tiếp tới câu hỏi **administrator**:

| Mục | Cũ | Hiện hành (4.3) | Đổi từ |
|---|---|---|---|
| Broker metadata | ZooKeeper | **KRaft-only** | 4.0 |
| CLI | `--zookeeper` | **`--bootstrap-server`** (KIP-1147) | 4.2 |
| Authorizer | `AclAuthorizer` (ZooKeeper) | **`StandardAuthorizer`** (KRaft) | 4.0 |
| Java cho broker/Connect/tools | 8/11 | **17** | 4.0 |
| `num.recovery.threads.per.data.dir` | 1 | **2** | 4.0 |
| Logging | log4j 1.x | **log4j2** (`log4j2.yaml`) | 4.0 |
| ELR | không có | opt-in 4.0, **mặc định cho cluster mới từ 4.1** | 4.0 → 4.1 |
| MirrorMaker 1 | còn | **đã xoá** | 4.0 |

> 📌 Với CCAAK, **mọi phương án nhắc ZooKeeper, znode, `--zookeeper` hay `zookeeper.connect` gần như chắc chắn sai**. Đây vừa là mẹo làm bài, vừa là lý do không dùng đề dump công khai.

---

## 🧪 LAB — chưa chạy thật, cần đối chiếu khi thực hành

*(Mục này được các tuần bổ sung dần khi viết lab. Ghi lại mọi lệnh hoặc hành vi chưa kiểm chứng trên Docker thật, kèm cách tự xác minh.)*

| Tuần · Lab | Điểm chưa kiểm chứng | Cách xác minh nhanh |
|---|---|---|
| 1.2 | Image `apache/kafka:4.3.1` xử lý `meta.properties` sai `cluster.id` ở entrypoint (`--ignore-formatted`) như thế nào | Chạy Lab 1.2; lab đã có phương án dự phòng `rm -rf` log dir rồi `up -d` |
| 1.3 | `kafka-metadata-quorum.sh describe --status` khi controller chết: timeout hay trả `LeaderId: -1` | Chạy Lab 1.3; lab ghi nhận **cả hai** đều hợp lệ |
| 1.3 | `kafka-topics.sh --bootstrap-server controller:9093` treo bao lâu trước khi báo lỗi | Đo bằng `time` khi làm lab |
| 1.x | Lab Tuần 1 mới kiểm logic và cú pháp, **chưa chạy thật trên Docker** | Chạy tuần tự 1.1 → 1.6 và ghi lại chỗ lệch |
| 2.2 · 2.6 | Thêm `log.dirs` mới vào broker KRaft **đã format**: entrypoint image có tự chạy `kafka-storage.sh format --ignore-formatted` không | Chạy Lab 2.2; lab có sẵn bước chữa thủ công nếu broker không lên. Lab 2.6 dùng tmpfs 32 MiB nên an toàn cho đĩa host |
| 2.7 | **Tiered storage không chạy được đủ vòng** với `apache/kafka:4.3.1` — `LocalTieredStorage` nằm trong test jar, không có trong `libs/` | Lab đã nói thẳng giới hạn và chuyển sang 3 "cổng cấu hình" chạy được thật. Câu chữ của 3 thông báo lỗi có thể khác giữa bản vá — đọc output thật |
| 7.6 | Image `apache/kafka:4.3.1` có thực sự ghi `state-change.log` ra file hay gộp vào stdout | Chạy Lab 7.6 và `docker exec kafka-1 ls /opt/kafka/logs/` |
| 7.x | Lab Tuần 7 chưa chạy thật trên Docker; riêng Lab 7.1 cần override để gắn exporter lên node `controller` | Chạy 7.1 trước, xác nhận `curl :7071/metrics \| grep activecontroller` có kết quả trên node controller |
| 8.x | Mapping biến môi trường dạng `KAFKA_LISTENER_NAME_<TÊN>_<MECHANISM>_SASL_JAAS_CONFIG` (dấu gạch dưới ba lần cho `-`) | Lab có fallback dùng file JAAS; nhớ gộp `KAFKA_OPTS` với `-javaagent` của phần giám sát |
| 8.x | `tmpfs` làm `log.dirs` thứ hai: image có tự `kafka-storage.sh format --ignore-formatted` cho dir mới không | Lab bắt buộc bắt đầu bằng `docker compose down -v` để tránh trạng thái cũ |
| 8.x | Bơm dữ liệu làm đầy ổ 32 MB bằng console producer **không ghim được partition** | Lab có phương án chắc chắn hơn; nếu không đầy đúng ổ mong muốn thì dùng topic 1 partition |
| — | `cordoned.log.dirs` (KIP-1066): trang upgrade xác nhận 4.3 **có** cordoning log dir nhưng **không in cú pháp config** | Lab dùng `|| echo "không khả dụng"` để không chặn bài; tra `kafka-configs.sh --describe --all` trên broker thật |
| 5.5 | Định dạng dòng DENY của `StandardAuthorizer` trong `kafka-authorizer.log` (khác `AclAuthorizer` cũ); và file có tồn tại trong image không hay log4j2 chỉ ghi ra console | Lab có nhánh dự phòng `docker logs … \| grep denied` |
| 5.2 | Xoay keystore bằng dynamic config mà **chỉ đổi `location`**, để password rơi về config chung — đúng theo docs ("falls back to the generic config") nhưng chưa chạy thật | Lab 5.2 bước 6 có phương án dự phòng rolling restart; chú ý `password.encoder.secret` |
| 5.5 | `kafka-acls.sh` có nhận **hai `--resource-pattern-type` trong một lệnh** không | Lab đã viết sẵn cách tách thành 2 lệnh |
| 5.3 | `kafkajs` **không hỗ trợ SASL re-authentication** → bật `connections.max.reauth.ms` sẽ làm client bị ngắt thay vì tự xác thực lại | Đã ghi thẳng trong Lab 5.3 bước 6; dùng client Java nếu cần kiểm chứng đúng |
| 3.3 | Cột `Elr:` / `LastKnownElr:` có thực sự hiện trong output `kafka-topics.sh --describe` của 4.3 hay chỉ đọc được qua API khác | Bật `eligible.leader.replicas.version=1` rồi chạy `kt --describe` và xem output thật |
