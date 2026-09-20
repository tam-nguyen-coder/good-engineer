# 🛠️ Tuần 1 — Nền tảng vận hành + `KRaft` in production

> **Domain CCAAK:** Apache Kafka Fundamentals (15%) · **Thời lượng:** ~11h (4 buổi) · **Vị trí:** Tuần 1/8 — không có checkpoint, nhưng **Cổng tự kiểm tra là bắt buộc**
>
> **Điều hướng:** [🏠 Kế hoạch tổng](../../CCAAK-STUDY-PLAN.md) · [Tuần 2 ➡️](../week-02/README.md)

## 🔁 Ôn nhanh từ CCDAK (~20 phút)

> Tuần này **dựa nhiều** vào CCDAK. Đọc lại đúng 4 chỗ dưới đây rồi mới vào Buổi A — đừng học lại từ đầu.

| Khái niệm | File CCDAK cần đọc lại | Vì sao cần cho tuần này |
|---|---|---|
| `process.roles`, controller quorum, `__cluster_metadata` | [`week-01/resources/kafka-operations-kraft.md`](../../../CCDAK/study-plan/week-01/resources/kafka-operations-kraft.md) | Tuần này **không** dạy lại KRaft là gì — mà hỏi *"quorum mấy node, đặt ở đâu, mất một node thì sao"* |
| Listener vs `advertised.listeners`, bẫy Docker | [`week-01/README.md`](../../../CCDAK/study-plan/week-01/README.md) mục 7 | Controller có listener riêng; cấu hình sai listener là lỗi #1 khi dựng cluster tách vai trò |
| ISR, high watermark, `acks` × `min.insync.replicas` | [`week-02/resources/kafka-replication-isr.md`](../../../CCDAK/study-plan/week-02/resources/kafka-replication-isr.md) | Buổi A đối chiếu **ISR (data plane)** với **Raft (control plane)** — phải nhớ ISR trước đã |
| Cluster Docker 3 broker + 1 controller | [`week-01/labs.md`](../../../CCDAK/study-plan/week-01/labs.md) Lab 1.2 | **Toàn bộ lab tuần này dùng lại file compose đó**, không dựng mới |

## 🎯 Mục tiêu tuần này

- **Chuyển được tư duy** từ developer sang administrator: mọi câu hỏi quy về 4 trục **durability · availability · throughput · chi phí vận hành**, và luôn chọn hành động **rẻ, đảo ngược được** trước.
- **Thiết kế được** một controller quorum cho production: mấy node, vì sao lẻ, chịu mất bao nhiêu, đặt cùng máy với broker hay tách riêng — và **bảo vệ được lựa chọn đó bằng con số**.
- **Tự tay dựng** một cluster có controller **tách riêng**, rồi đọc và **giải nghĩa từng dòng** output `kafka-metadata-quorum.sh describe --status` / `--replication`.
- **Tái hiện và khôi phục** sự cố `InconsistentClusterId` do format sai `cluster.id` — lỗi kinh điển của mọi script tự động hoá dựng cluster.
- **Chứng minh bằng thực nghiệm** điều gì chết và điều gì vẫn sống khi **mất quorum controller**: control plane đóng băng, data plane còn phục vụ partition không đổi leader.
- **Nhận diện tức thì** mọi dấu vết của thế giới ZooKeeper (`--zookeeper`, znode, `zookeeper.connect`, `broker.id` tự sinh) và chỉ ra được **cái gì trong KRaft thay thế cái gì**.
- **Gọi tên đúng công cụ** cho từng câu hỏi vận hành: quorum → `kafka-metadata-quorum.sh`, config hiệu lực → `kafka-configs.sh --all`, phân bố đĩa → `kafka-log-dirs.sh`, feature → `kafka-features.sh`, leader lệch → `kafka-leader-election.sh`.

## 📚 Nội dung học chi tiết

### 🅰️ Buổi A — Lý thuyết (~3h)

**1. Admin khác Dev ở chỗ nào (đọc 10 phút, quyết định cả kỳ thi)**

CCDAK hỏi *"ứng dụng của tôi nên gọi API nào"*. CCAAK hỏi **"cluster của tôi đang chịu tải gì, chịu được mất mát gì, và tôi phải chỉnh con số nào"**.

| | Developer (CCDAK) | Administrator (CCAAK) |
|---|---|---|
| Đơn vị tư duy | Một ứng dụng, một consumer group | **Cả cluster**, mọi tenant dùng chung |
| Câu hỏi điển hình | "Commit offset nào?" | "`UnderReplicatedPartitions` > 0 — làm gì **trước tiên**?" |
| Config quan tâm | `acks`, `max.poll.records`, `group.id` | `num.io.threads`, `log.dirs`, `process.roles`, `min.insync.replicas` |
| Sai lầm tốn kém | Duplicate / mất message của **một** app | **Mất dữ liệu cả cluster**, hoặc downtime toàn hệ thống |
| Công cụ | Client API, IDE | **CLI + metric + log**, và bàn tay trên máy đang cháy |
| Đáp án đúng thường là | Đúng về mặt ngữ nghĩa | **Rẻ nhất, đảo ngược được, ít thay đổi nhất** mà vẫn giải quyết triệu chứng |

> 🧠 Câu thần chú: đề CCAAK *"rarely asks you to define a term in isolation; it presents a scenario and asks which action a competent administrator would take"*. Khi đọc đề, **tìm triệu chứng trước, đọc phương án sau**.

**2. Kiến trúc cluster nhìn từ vận hành: hai mặt phẳng**

Đây là mô hình tư duy quan trọng nhất của tuần. Mọi sự cố Kafka đều rơi vào **một trong hai** mặt phẳng, và chúng **hỏng độc lập với nhau**.

| | **Control plane** | **Data plane** |
|---|---|---|
| Ai chạy | Controller quorum (`process.roles=controller`) | Broker (`process.roles=broker`) |
| Giữ cái gì | `__cluster_metadata` — **1 partition**: topic, partition, replica, ISR, ACL, config động, đăng ký broker | `orders-0`, `__consumer_offsets-17`, … — dữ liệu người dùng |
| Giao thức | **Raft** (đa số phiếu) | **ISR replication** (leader + follower fetch) |
| Cổng chuẩn | **9093** (`CONTROLLER` listener) | **9092** (client), listener nội bộ cho inter-broker |
| Hỏng thì mất gì | Không tạo/xoá topic, không đổi config, **không bầu leader mới**, broker mới không đăng ký được | Partition mất leader → produce/consume chết cho đúng partition đó |
| Metric canh | `ActiveControllerCount` (tổng toàn cluster = **1**) | `UnderReplicatedPartitions`, `OfflinePartitionsCount` |
| Công cụ soi | `kafka-metadata-quorum.sh` | `kafka-topics.sh --describe`, `kafka-log-dirs.sh` |

**3. `process.roles` — ba giá trị, một lựa chọn production duy nhất**

| Giá trị | Node làm gì | Dùng khi nào | Vì sao |
|---|---|---|---|
| `controller` | Chỉ tham gia quorum metadata. **Không** nhận produce/fetch của client | ✅ **Production** | Controller được cách ly khỏi GC, page cache và disk I/O của data plane |
| `broker` | Chỉ phục vụ data plane. Là **observer** của metadata log | ✅ **Production** | Roll/scale broker độc lập với controller |
| `broker,controller` | **Combined** — cả hai | ⚠️ **Chỉ dev/lab** | Docs Apache: *"not recommended in critical deployment environments"*; Confluent: *"for local experimentation only and is not supported by Confluent"* |

Lý do kỹ thuật, không phải khẩu hiệu: ở combined mode **không thể rolling-restart controller tách khỏi broker** — muốn nâng cấp broker là đồng thời nâng cấp cả quorum, và mọi cơn GC của broker đều có thể làm controller lỡ nhịp `controller.quorum.fetch.timeout.ms` (**2000 ms**).

**4. Sizing quorum: vì sao luôn là số lẻ**

Công thức duy nhất cần nhớ: **`2N+1` voter chịu được `N` lỗi đồng thời**; quorum sống khi còn **đa số**.

| Số controller | Đa số cần | Chịu mất | Nhận xét vận hành |
|---|---|---|---|
| 1 | 1 | **0** | Chỉ lab. Controller chết = control plane chết |
| **3** | 2 | **1** | ✅ Mặc định đúng cho hầu hết production |
| 4 | 3 | **1** | ❌ **Tốn thêm một máy mà không chịu lỗi tốt hơn 3** — bẫy đề kinh điển |
| **5** | 3 | **2** | ✅ Cluster lớn / trải 3 AZ / cần chịu mất 2 node cùng lúc |
| 7 | 4 | 3 | Hiếm — mỗi lần ghi metadata phải chờ nhiều voter hơn, độ trễ tăng |

Controller **rất nhẹ**: docs khuyến nghị ~**5 GB RAM** và ~**5 GB đĩa** cho metadata log directory ở một cluster điển hình. Đây là lý do "tách riêng tốn kém" là một hiểu lầm.

**5. Static quorum vs dynamic quorum (KIP-853)**

| | **Static** | **Dynamic** (KIP-853) |
|---|---|---|
| Config | `controller.quorum.voters=1@c1:9093,2@c2:9093,3@c3:9093` | `controller.quorum.bootstrap.servers=c1:9093,c2:9093,c3:9093` |
| Ai phải khai | **Mọi node**, kể cả broker-only, khai **đầy đủ** danh sách | Chỉ cần **đủ địa chỉ để khám phá** quorum |
| Thành viên quorum lưu ở đâu | Trong **file config** | Trong **chính metadata log** |
| Thay một controller hỏng | Sửa config **mọi node** + **restart cả cluster** | `remove-controller` rồi `add-controller`, **không downtime** |
| Feature flag | `kraft.version=0` | `kraft.version=1` |
| Định danh voter | `node.id` | `node.id` **+ `directory.id`** (UUID trong `meta.properties`) |
| Kiểm tra đang ở đâu | `kafka-features.sh --bootstrap-controller localhost:9093 describe` → đọc dòng `kraft.version` | |

**6. Format storage: bước bắt buộc mà thời ZooKeeper không có**

```bash
CLUSTER_ID=$(kafka-storage.sh random-uuid)          # SINH MỘT LẦN cho cả cluster
kafka-storage.sh format --cluster-id $CLUSTER_ID --standalone  -c controller.properties  # controller đầu tiên
kafka-storage.sh format --cluster-id $CLUSTER_ID --no-initial-controllers -c server.properties  # broker & controller vào sau
kafka-server-start.sh server.properties
```

- `format` ghi **`meta.properties`** vào mỗi thư mục của `log.dirs`: `cluster.id`, `node.id`, `directory.id`, `version`.
- **Cùng cluster ⇒ cùng `cluster.id`.** Sai → node ném **`InconsistentClusterIdException`** và không join được. Nguồn gốc thực tế: script dựng cluster gọi `random-uuid` **trên từng máy** thay vì một lần.
- Ba cờ loại trừ nhau: `--standalone` (controller đầu tiên, voter duy nhất) · `--initial-controllers "id@host:port:dirUUID,..."` (format cả quorum cùng lúc) · `--no-initial-controllers` (gia nhập quorum sẵn có).
- Xoá `log.dirs` = xoá `meta.properties` = phải format lại. Trên production, xoá nhầm log dir của controller là **mất một voter**.

**7. `__cluster_metadata` và các đồng hồ của quorum**

- `__cluster_metadata` là topic nội bộ **1 partition** (khác `__consumer_offsets` **50** và `__transaction_state` **50**). Active controller là **leader** của partition đó, standby controller là **follower**, **broker là observer** — fetch metadata nhưng **không bỏ phiếu**.
- `metadata.log.dir` mặc định **`null`** → metadata nằm ở **thư mục đầu tiên** trong `log.dirs`. Production nên trỏ sang **ổ riêng** để metadata không tranh I/O với data.
- Snapshot: controller và broker định kỳ chụp metadata cache trong bộ nhớ → log cắt bớt được (`metadata.max.retention.bytes` **100 MiB**, `metadata.max.retention.ms` **7 ngày**) mà state vẫn khôi phục đủ.
- Đồng hồ quorum nhỏ hơn đồng hồ data plane **một bậc độ lớn**:

| Đồng hồ | Giá trị | Đo cái gì |
|---|---|---|
| `controller.quorum.fetch.timeout.ms` | **2000** | Hai chiều: voter không fetch thành công từ leader trong bấy nhiêu → **tự ứng cử**; leader không nhận được fetch từ **đa số** trong bấy nhiêu → **tự từ chức** |
| `controller.quorum.election.timeout.ms` | **1000** | Đang trong một vòng bầu cử mà vẫn không fetch được từ leader trong bấy nhiêu → **mở vòng bầu cử mới** |
| `controller.quorum.election.backoff.max.ms` | **1000** | Trần của backoff luỹ thừa giữa các vòng bầu cử, tránh bầu cử giẫm chân nhau |
| `controller.quorum.request.timeout.ms` | **2000** | Timeout một RPC trong quorum |
| `controller.quorum.append.linger.ms` | **25** | Leader gom write metadata bấy nhiêu trước khi flush xuống đĩa |
| `replica.lag.time.max.ms` *(data plane)* | **30000** | Follower tụt bao lâu thì rơi khỏi ISR |

**8. ⚠️ Mất quorum thì chuyện gì xảy ra — câu hỏi đắt nhất tuần này**

Khi **không còn đa số** controller sống:

| Vẫn chạy được ✅ | Đóng băng ❌ |
|---|---|
| Produce / consume vào partition mà **leader không đổi** | Tạo / xoá topic, thêm partition |
| Consumer group commit offset (ghi vào `__consumer_offsets`, là data plane) | Đổi config động bằng `kafka-configs.sh` |
| Broker đang sống tiếp tục phục vụ từ **metadata đã cache** | **Bầu leader mới** cho bất kỳ partition nào |
| `kafka-topics.sh --describe` (đọc từ cache của broker) | Broker mới **đăng ký** vào cluster |
| | Thêm/bớt ACL, thay đổi quota |

**Nhưng đây là trạng thái vá víu, không phải trạng thái ổn định.** Chỉ cần **thêm một broker chết** là partition nó đang làm leader **không có ai bầu leader mới** → `OfflinePartitionsCount` tăng và partition đó chết thật. Ưu tiên tuyệt đối khi mất quorum: **khôi phục đa số controller**, không phải đi sửa từng partition.

> 📌 **Ghi chú trung thực:** docs Apache chỉ nói *"A majority of the controllers must be alive in order to maintain availability"*, và Confluent nói *"if the controller majority is lost, the cluster becomes unavailable"* — **không có câu nào nói thẳng về data plane**. Kết luận ở bảng trên suy ra từ kiến trúc (broker phục vụ bằng metadata cache) và **bạn sẽ tự chứng minh nó ở Lab 1.3**. Xem thêm ghi chú ở cuối [`resources/confluent-control-plane-course.md`](resources/confluent-control-plane-course.md).

**9. Vì sao bỏ ZooKeeper — và cái gì thay thế cái gì**

Ba nút thắt khiến ZooKeeper phải ra đi (KIP-500):

1. **Hai hệ thống**: metadata là source of truth trong ZooKeeper nhưng controller giữ cache riêng, và broker khác cũng nói chuyện trực tiếp với ZooKeeper → **metadata phân kỳ**; vận hành phải tune/backup/bảo mật hai hệ thống.
2. **Controller failover tuyến tính theo số partition**: controller mới phải nạp **toàn bộ** metadata từ ZooKeeper → "a long unavailability window". Với KRaft, controller mới **đã có sẵn** log → failover gần như tức thời.
3. **Mọi thay đổi propagate tuyến tính theo số partition**, cộng giới hạn kích thước znode và số watcher.

| Thế giới ZooKeeper (≤ 3.9) | Thế giới KRaft (4.x) |
|---|---|
| znode | **metadata record** trong `__cluster_metadata` |
| Ephemeral node `/controller` để bầu controller | **Bầu leader bằng Raft** (`VoteRequest` + epoch, log phải ≥ log người bỏ phiếu) |
| Broker đăng ký bằng ephemeral node `/brokers/ids/<id>` | Broker **đăng ký + heartbeat** với controller; controller **fence** broker chết |
| `--zookeeper` trên CLI | **`--bootstrap-server`** (hoặc `--bootstrap-controller`) |
| ACL lưu trong znode | ACL lưu trong **metadata log**, `StandardAuthorizer` |
| `zookeeper.connect` | `controller.quorum.bootstrap.servers` / `controller.quorum.voters` |
| `broker.id` (+ `broker.id.generation.enable`) | **`node.id`**, đặt tay, bắt buộc |
| `inter.broker.protocol.version` trong file config | **`metadata.version`**, nâng bằng `kafka-features.sh` |
| `control.plane.listener.name` | **`controller.listener.names`** |

**10. ISR, high watermark, leader election — ôn lại ở góc admin**

Bạn đã học ở CCDAK Tuần 2. Ở đây chỉ cần **ba điều admin phải nói được ngay**:

- **ISR có 2 điều kiện**: còn phiên heartbeat với controller **và** không tụt quá `replica.lag.time.max.ms` (**30000**). Hỏng một trong hai là rơi khỏi ISR.
- **"Committed" = mọi replica trong ISR đã nhận** → đó chính là **high watermark**, và consumer **chỉ đọc tới đó**. Vì vậy dữ liệu consumer đọc được là dữ liệu đã an toàn.
- **Data plane không dùng đa số phiếu.** RF `f+1` chịu `f` lỗi, và **bất kỳ** thành viên ISR nào cũng đủ điều kiện làm leader. Trái ngược hoàn toàn với control plane (Raft, cần đa số). **Cùng một cluster, hai luật bầu cử khác nhau** — đề rất hay trộn hai thứ này.
- Bộ ba production: **RF 3 + `min.insync.replicas` 2 + `acks=all`** = chịu mất **1 broker** vẫn ghi được, không mất dữ liệu. `min.insync.replicas=3` với RF 3 là **over-correction**.
- `__consumer_offsets`: **50 partition**, compacted, `offsets.topic.replication.factor` **3**. Group coordinator = broker đang làm **leader** của partition `hash(group.id) % 50`.

**11. Bộ đồ nghề CLI của admin — tool nào trả lời câu hỏi nào**

| Câu hỏi vận hành | Công cụ | Ghi chú |
|---|---|---|
| Quorum còn sống không? Leader là ai? | `kafka-metadata-quorum.sh describe --status` / `--replication` | `--replication` cho cột `Status` = Leader / Follower / Observer |
| Topic này replica ở đâu, ISR ra sao? | `kafka-topics.sh --describe` | Đọc `Leader / Replicas / Isr` — replica **đầu tiên** là preferred leader |
| Config đang **thực sự** có hiệu lực là gì, từ đâu? | `kafka-configs.sh --describe --all` | Đọc cột **synonyms** để biết giá trị đến từ mức nào |
| Partition nằm ở ổ nào, chiếm bao nhiêu byte? | `kafka-log-dirs.sh --describe` | Trả JSON; dùng khi một broker sắp đầy đĩa |
| Cluster đang ở metadata version nào, static hay dynamic quorum? | `kafka-features.sh describe` | Đọc `metadata.version` và `kraft.version` |
| Leader lệch sau bảo trì, trả về preferred? | `kafka-leader-election.sh --election-type preferred` | `unclean` là lựa chọn **cuối cùng**, có mất dữ liệu |
| Di chuyển partition sang broker khác | `kafka-reassign-partitions.sh` | `--generate` → `--execute` → **`--verify` (bước gỡ throttle)** |
| Trong segment này thực sự có gì? | `kafka-dump-log.sh` | `--cluster-metadata-decoder` để đọc `__cluster_metadata` |
| Broker này nói được API version nào? | `kafka-broker-api-versions.sh` | Dùng khi nghi ngờ client quá cũ |

- **KIP-1147** thống nhất CLI về **`--bootstrap-server`** (Kafka 4.2). Không tool nào còn nhận `--zookeeper`.
- **Java 17** cho broker / Connect / tools, **Java 11** cho client Java; **baseline giao thức client 2.1** — client cũ hơn 2.1 không nói chuyện được với broker 4.x.

### 🅱️ Buổi B — Hands-on (~3.5h)

> 🧪 **Lab cầm tay chỉ việc (từng bước + lệnh + output mong đợi):** [labs.md](labs.md). Dùng lại `~/kafka-labs/` và `docker-compose.cluster.yml` của [CCDAK Tuần 1 Lab 1.2](../../../CCDAK/study-plan/week-01/labs.md) — **không dựng compose mới**.

- **Lab 1.1 ⭐ — Cluster controller tách riêng + đọc quorum:** xác nhận `controller` (node.id **1**) là `process.roles=controller` thuần, 3 broker là node **2/3/4**; đọc `describe --status` và `--replication` **giải nghĩa từng dòng**.
- **Lab 1.2 💥 — Gây hỏng rồi sửa: `InconsistentClusterId`:** sửa `cluster.id` trong `meta.properties` của `kafka-3` → restart → đọc exception → chẩn đoán bằng cách so với `describe --status` → sửa.
- **Lab 1.3 ⭐💥 — Gây hỏng rồi sửa: tắt controller duy nhất:** chứng minh **produce/consume vẫn chạy** nhưng **tạo topic mới thì timeout**; bật lại và xác nhận control plane hồi phục.
- **Lab 1.4 — Tour CLI admin:** `kafka-broker-api-versions.sh`, `kafka-log-dirs.sh --describe`, `kafka-features.sh describe`, `kafka-dump-log.sh` soi segment data và segment metadata.
- **Lab 1.5 — `kafka-configs.sh` và synonyms ở 3 mức:** đọc giá trị **hiệu lực** và truy ngược nó đến từ topic override / broker / default.
- **Lab 1.6 — Leader election khi tắt 1 broker:** `kt --describe` trước/sau, xem ISR co lại và leader chuyển, rồi `kafka-leader-election.sh --election-type preferred` trả leader về.

### 🅲️ Buổi C — Bổ sung (~2.5h)

**Bảng quyết định 1 — "Thiết kế quorum cho tình huống này"**

| Tình huống | Quyết định | Vì sao |
|---|---|---|
| Lab trên laptop, 4 GB RAM | **1 controller**, hoặc combined | Chịu lỗi = 0, chấp nhận được vì là lab |
| Production 1 DC, 6–20 broker | **3 controller tách riêng** | Chịu mất 1 controller; rẻ (5 GB RAM/node) |
| Production trải **3 AZ** | **3 controller, mỗi AZ một cái** | Mất nguyên 1 AZ vẫn còn đa số 2/3 |
| Production trải **2 AZ** | ⚠️ Không có cấu hình an toàn | Mất AZ chứa 2 controller là mất đa số. Cần **AZ thứ 3** (dù chỉ để đặt 1 controller) |
| Cluster rất lớn, cần chịu mất 2 node | **5 controller** | `2N+1` với `N=2` |
| Ai đó đề xuất **4 controller** | ❌ Từ chối | Chịu lỗi vẫn là 1, y hệt 3 — chỉ tốn thêm máy và tăng độ trễ ghi metadata |

**Bảng quyết định 2 — "Node không join được cluster, đi từ đâu?"**

| Quan sát đầu tiên | Nghi ngờ | Lệnh tiếp theo |
|---|---|---|
| Log có `InconsistentClusterIdException` | Format sai `cluster.id` | `cat meta.properties` rồi so với `describe --status` |
| Log báo log dir chưa được format | Quên `kafka-storage.sh format` | Format lại với **đúng** `cluster.id` của cluster |
| Node start được nhưng không xuất hiện trong `CurrentObservers` | Sai `controller.quorum.*` hoặc không tới được cổng 9093 | `describe --status` từ node khác; kiểm mạng tới controller |
| Client nối bootstrap OK nhưng produce timeout | `advertised.listeners` sai | Sửa advertised listener — **và phải restart broker**, config này không dynamic trong KRaft |
| Controller không bầu được leader | Không đủ đa số voter | `describe --status` xem `CurrentVoters`; bật lại controller thiếu |

**Đọc thêm:** [`resources/kraft-operations-production.md`](resources/kraft-operations-production.md) (toàn bộ), phần *ZooKeeper to KRaft* trong [`resources/zk2kraft-removed-configs-and-cli.md`](resources/zk2kraft-removed-configs-and-cli.md), và chương 2 *Kafka: The Definitive Guide* 2nd ed. (Installing Kafka) — xem [bản đồ chương](../../../CCDAK/study-plan/week-10/resources/kafka-definitive-guide-chapter-map.md).

### 🅳 Buổi D — Practice + Review (~2h)

> 📝 **Bộ câu hỏi luyện tập của tuần:** [questions.md](questions.md) — đáp án & giải thích: [answers.md](answers.md). *(tiếng Anh, văn phong CCAAK.)*

- Làm **28 câu** của tuần trong **~42 phút** (~90 giây/câu, đúng nhịp đề thật). Không tra tài liệu.
- Ghi **sổ câu sai** và phân loại: *quorum sizing / format & cluster id / control vs data plane / di sản ZooKeeper / chọn công cụ CLI*. Ôn lại theo mốc **1 / 3 / 7 ngày**.
- Với mỗi câu sai, viết một dòng **"lý do sai"**: thiếu kiến thức · đọc sót qualifier · dính bẫy · hết giờ. Câu đúng nhờ đoán may **cũng tính là câu sai**.
- Tự vẽ lại từ trí nhớ: sơ đồ **hai mặt phẳng** (mục A.2) và **bảng ánh xạ ZooKeeper → KRaft** (mục A.9). Không nhìn được thì quay lại Buổi A.

## 🧠 PHẢI NHỚ tuần này

| Fact | Con số / Ghi nhớ |
|---|---|
| `process.roles` | `broker` \| `controller` \| `broker,controller`; **combined chỉ dev** — "not recommended in critical deployment environments" |
| Quorum size | **3 hoặc 5** (lẻ); `2N+1` chịu `N` lỗi; **4 controller chịu lỗi y hệt 3** |
| Tài nguyên controller | ~**5 GB RAM** + ~**5 GB đĩa** cho metadata log dir |
| `controller.quorum.election.timeout.ms` | **1000** ms · `fetch.timeout.ms` **2000** · `request.timeout.ms` **2000** · `append.linger.ms` **25** |
| `replica.lag.time.max.ms` (data plane) | **30000** ms — chậm hơn đồng hồ quorum **một bậc độ lớn** |
| Static vs dynamic quorum | `controller.quorum.voters` (`kraft.version=0`) vs `controller.quorum.bootstrap.servers` (**KIP-853**, `kraft.version=1`, có `directory.id`) |
| Format storage | `kafka-storage.sh random-uuid` → `format --cluster-id <ID>` với **1 trong 3 cờ**: `--standalone` / `--initial-controllers` / `--no-initial-controllers`; ghi `meta.properties` |
| Sai `cluster.id` | **`InconsistentClusterIdException`** — node không join được; sửa bằng format lại đúng id |
| `__cluster_metadata` | **1 partition**; active controller = **Leader**, standby = **Follower**, broker = **Observer** |
| `metadata.log.dir` | Mặc định **`null`** → dùng thư mục **đầu tiên** của `log.dirs`; production nên tách ổ riêng |
| Metadata retention | `metadata.max.retention.bytes` **100 MiB** · `metadata.max.retention.ms` **7 ngày** · snapshot mỗi **20 MiB** record |
| Mất đa số quorum | Control plane **đóng băng** (không bầu leader mới, không tạo/xoá topic); data plane **vẫn phục vụ** partition không đổi leader |
| Cổng | Broker **9092** · Controller **9093** · JMX **9999** · Connect REST **8083** |
| Internal topic | `__cluster_metadata` **1** · `__consumer_offsets` **50** · `__transaction_state` **50**; `offsets.topic.replication.factor` **3** |
| Durability production | **RF 3 + `min.insync.replicas` 2 + `acks=all`** = chịu mất **1** broker; min.isr **3** với RF 3 là over-correction |
| Bầu leader: hai luật | Data plane = **ISR** (bất kỳ thành viên ISR, `f+1` chịu `f`) · Control plane = **Raft** (cần **đa số**) |
| `auto.leader.rebalance.enable` | **true**, `leader.imbalance.check.interval.seconds` **300** → leader tự về preferred trong **5 phút** |
| Java & protocol | Broker/Connect/tools **Java 17**, client Java **11**, baseline giao thức client **2.1** |
| CLI | **KIP-1147**: mọi tool dùng `--bootstrap-server`; controller dùng `--bootstrap-controller`; **không còn `--zookeeper`** |
| Thread/socket mặc định | `num.network.threads` **3** · `num.io.threads` **8** · `num.replica.fetchers` **1** · `queued.max.requests` **500** |

## 🚨 Playbook: triệu chứng → hành động

| Triệu chứng | Nguyên nhân khả dĩ | Hành động đầu tiên |
|---|---|---|
| Broker log: `InconsistentClusterIdException` | `meta.properties` có `cluster.id` khác cluster | `cat meta.properties`, so với `kafka-metadata-quorum.sh describe --status`; format lại log dir với **đúng** id |
| Broker chết ngay lúc start, log báo log dir chưa format | Quên `kafka-storage.sh format` | Format với `--no-initial-controllers` và `cluster.id` của cluster |
| `kafka-topics.sh --create` timeout, còn produce/consume vẫn chạy | **Mất đa số controller quorum** | `describe --status` xem `CurrentVoters`/`LeaderId`; **khôi phục controller**, không đi sửa từng topic |
| Tổng `ActiveControllerCount` toàn cluster ≠ 1 | Controller lỗi hoặc đang failover | `kafka-metadata-quorum.sh describe --status`; `LeaderId` = -1 nghĩa là chưa bầu được |
| `describe --replication` cho thấy một voter có `Lag` tăng dần | Controller đó tụt log (đĩa chậm / mạng) | Kiểm I/O và mạng của node đó; **đừng** vội `remove-controller` |
| Node mới không xuất hiện trong `CurrentObservers` | Sai `controller.quorum.*` hoặc không tới được cổng 9093 | Kiểm cấu hình controller listener + kết nối mạng tới controller |
| Sau rolling restart, leader dồn hết về 1–2 broker | Leader chưa quay về preferred replica | Chờ tối đa **5 phút** (`leader.imbalance.check.interval.seconds` 300) hoặc chạy `kafka-leader-election.sh --election-type preferred --all-topic-partitions` |
| Đổi `advertised.listeners` bằng `kafka-configs.sh` nhưng không có tác dụng | KRaft **bỏ** khả năng cập nhật động config này | Sửa file config và **restart broker** |
| Chỉnh log level của controller bằng `--bootstrap-server` nhưng không ăn | Controller không nằm sau listener của broker | Dùng **`--bootstrap-controller localhost:9093`** |
| Tạo topic thất bại trên cluster 1 broker: không đủ replica cho `__consumer_offsets` | `offsets.topic.replication.factor` mặc định **3** | Hạ RF của internal topic xuống **1** cho cluster 1 node |
| `CreateTopicPolicy` tự viết không có tác dụng | KRaft chạy policy plugin ở **controller** | Nạp JAR vào **controller**, không phải broker |
| Một broker chết, partition của nó offline và **không** bầu leader mới | Quorum đã mất đa số từ trước | Khôi phục quorum trước; unclean election là **lựa chọn cuối cùng** |

## ⚠️ Bẫy đề hay gặp

- Thấy "cluster cần chịu được mất **2** controller" → dễ chọn **4**, nhưng đúng là **5** (`2N+1`, 4 chịu lỗi y hệt 3).
- Thấy "production nhỏ, chỉ 3 máy" → dễ chọn `process.roles=broker,controller` cho gọn, nhưng đúng là **tách riêng** — docs nói combined *"not recommended in critical deployment environments"*, Confluent thì không hỗ trợ.
- Thấy "mất đa số controller" → dễ chọn "cả cluster ngừng ngay lập tức, client mất kết nối", nhưng đúng là **control plane đóng băng, data plane vẫn phục vụ partition không đổi leader** — và đó là trạng thái **tạm thời nguy hiểm**, không phải "vẫn ổn".
- 🕰️ **Bẫy version:** thấy phương án "`kafka-topics.sh --zookeeper zk1:2181 --list`" hoặc "kiểm tra znode `/brokers/ids`" → **sai với Kafka 4.x**; ZooKeeper đã bị gỡ hoàn toàn từ **4.0**, bridge release cuối là **3.9**.
- 🕰️ **Bẫy version:** thấy "đặt `inter.broker.protocol.version` rồi rolling restart để hoàn tất nâng cấp" → sai; KRaft thay bằng **`metadata.version`** và nâng bằng **`kafka-features.sh`**.
- 🕰️ **Bẫy version:** thấy "để trống `broker.id` cho Kafka tự sinh" → sai; `broker.id.generation.enable` và `reserved.broker.max.id` **đã bị gỡ**, `node.id` phải đặt tay.
- Thấy câu hỏi về `__cluster_metadata` → hai chỗ dễ sai cùng lúc: nó có **1** partition (không phải 50 — đó là `__consumer_offsets`), và broker chỉ là **observer** của nó — fetch metadata, **không vote**. Chỉ node có `process.roles` chứa `controller` mới là voter.
- Thấy "bất kỳ replica nào cũng có thể được bầu làm leader partition" → sai: chỉ replica **trong ISR**, trừ khi bật `unclean.leader.election.enable`. Ngược lại, ở control plane thì **phải thắng đa số phiếu** — đừng trộn hai luật.
- Thấy "tăng `replica.lag.time.max.ms` để controller failover nhanh hơn" → sai đối tượng: đó là đồng hồ của **ISR/data plane**; đồng hồ quorum là `controller.quorum.fetch.timeout.ms` (**2000**).
- Thấy "sửa `advertised.listeners` bằng `kafka-configs.sh --alter` để không phải restart" → sai; KRaft đã **bỏ** dynamic update cho config này.
- Thấy "dùng `--bootstrap-server` để đổi config của controller" → sai; controller nghe ở listener riêng, phải dùng **`--bootstrap-controller`**.
- Thấy "thêm broker mới vào cluster thì nó tự nhận partition" → sai; phải chạy **`kafka-reassign-partitions.sh`**. Và **đừng quên `--verify`** — đó là bước gỡ throttle.

## 🧪 Lab checklist

- [ ] Lab 1.1 ⭐ — Dựng cluster controller **tách riêng** (node.id 1 = controller-only, 2/3/4 = broker) và giải nghĩa **từng dòng** `kafka-metadata-quorum.sh describe --status` + `--replication`.
- [ ] Lab 1.2 💥 — Sửa `cluster.id` trong `meta.properties` → tái hiện **`InconsistentClusterIdException`** → chẩn đoán → khôi phục.
- [ ] Lab 1.3 ⭐💥 — Tắt controller duy nhất: chứng minh **produce/consume vẫn chạy** nhưng **`--create` timeout**; bật lại và xác nhận hồi phục.
- [ ] Lab 1.4 — Tour CLI: `kafka-broker-api-versions.sh`, `kafka-log-dirs.sh --describe`, `kafka-features.sh describe`, `kafka-dump-log.sh` (segment data **và** segment metadata).
- [ ] Lab 1.5 — `kafka-configs.sh --describe --all`: đọc giá trị hiệu lực và **truy ngược synonyms** qua 3 mức (topic → broker → default).
- [ ] Lab 1.6 — Tắt 1 broker: `kt --describe` trước/sau, thấy ISR co và leader chuyển; `kafka-leader-election.sh --election-type preferred` trả leader về.

## 🚪 Cổng tự kiểm tra (phải trả lời trôi chảy mới sang tuần sau)

- **Vì sao quorum controller luôn là số lẻ, và 4 controller sai ở đâu?**
  **Đáp án gọn:** quorum sống khi còn **đa số**; `2N+1` chịu `N` lỗi. 4 controller cần đa số là 3 → vẫn chỉ chịu **1** lỗi, y hệt 3, mà tốn thêm một máy và tăng độ trễ ghi metadata.
- **Ba giá trị của `process.roles`, và vì sao production phải tách riêng?**
  **Đáp án gọn:** `broker` / `controller` / `broker,controller`. Combined *"not recommended in critical deployment environments"* vì controller kém cách ly khỏi GC và I/O của data plane, và **không roll/scale controller độc lập được**.
- **Một broker mới ném `InconsistentClusterIdException`. Chẩn đoán theo trình tự nào?**
  **Đáp án gọn:** `cat meta.properties` xem `cluster.id` của node → `kafka-metadata-quorum.sh describe --status` xem `ClusterId` của cluster → hai giá trị khác nhau → xoá/format lại log dir với **đúng** `cluster.id` (`--no-initial-controllers`).
- **Mất đa số controller quorum: cái gì còn chạy, cái gì đóng băng?**
  **Đáp án gọn:** còn chạy = produce/consume vào partition **leader không đổi**, commit offset, đọc metadata từ cache. Đóng băng = tạo/xoá topic, đổi config, đăng ký broker mới, và **bầu leader mới**. Rủi ro thật sự: thêm một broker chết là partition đó offline vĩnh viễn cho tới khi quorum trở lại.
- **Static quorum khác dynamic quorum ở đâu, và kiểm tra bằng lệnh nào?**
  **Đáp án gọn:** static = `controller.quorum.voters` khai đủ trên **mọi node**, đổi thành viên phải restart cả cluster; dynamic = `controller.quorum.bootstrap.servers` + thành viên nằm **trong metadata log**, thêm/bớt online bằng `add-controller`/`remove-controller`. Kiểm bằng `kafka-features.sh --bootstrap-controller localhost:9093 describe` → `kraft.version` 0 hay 1.
- **Cùng một cluster có hai cơ chế bầu leader. Kể tên và phân biệt.**
  **Đáp án gọn:** data plane dùng **ISR** — bất kỳ thành viên ISR nào cũng đủ điều kiện, `f+1` replica chịu `f` lỗi. Control plane dùng **Raft** — ứng viên phải có log ≥ và phải thắng **đa số** phiếu. Đề hay đổi chỗ hai luật này.
- **Kể 5 thứ trong thế giới ZooKeeper và thứ thay thế chúng trong KRaft.**
  **Đáp án gọn:** znode → metadata record; ephemeral `/controller` → bầu Raft; `--zookeeper` → `--bootstrap-server`; ACL trong znode → ACL trong metadata log; `inter.broker.protocol.version` → `metadata.version` (nâng bằng `kafka-features.sh`); `broker.id` tự sinh → `node.id` đặt tay.
- **Bạn cần biết "giá trị `min.insync.replicas` đang có hiệu lực cho topic `orders` đến từ đâu". Gõ lệnh nào?**
  **Đáp án gọn:** `kafka-configs.sh --describe --all --entity-type topics --entity-name orders` rồi đọc cột **synonyms** — nó liệt kê theo thứ tự ưu tiên từ `DYNAMIC_TOPIC_CONFIG` xuống `DEFAULT_CONFIG`.

## 📎 Tài nguyên tuần này

> 📂 **Đã crawl sẵn tài liệu chính thức vào** [`resources/`](resources/INDEX.md) — đọc offline được (8 file).

- Apache Kafka Docs 4.3: *Operations → KRaft* (`kafka.apache.org/43/operations/kraft/`), *Operations → Basic Kafka Operations*, *Getting Started → Quickstart*, *Getting Started → ZooKeeper to KRaft*, *Design → Replication*, *Configuration → Broker Configs* (`generated/kafka_config.html`).
- Confluent Platform Docs: *KRaft Configuration* (`docs.confluent.io/platform/current/kafka-metadata/config-kraft.html`) — câu chữ "combined mode ... is not supported by Confluent".
- Confluent Developer (free): course *Apache Kafka Architecture* → module **Control Plane**; trang *learn/kraft*.
- Blog kỹ thuật: *Why ZooKeeper Was Replaced with KRaft: The Log of All Logs* (confluent.io/blog) — nguồn cho ba nút thắt của ZooKeeper.
- KIP: **KIP-500** (bỏ ZooKeeper), **KIP-853** (dynamic controller quorum), **KIP-1147** (thống nhất `--bootstrap-server`), KIP-966 (ELR — học sâu ở Tuần 3).
- Sách: *Kafka: The Definitive Guide* 2nd ed. — Chương 2 *Installing Kafka* và Chương 12 *Administering Kafka*.
- Chống lỗi thời: [`CCDAK/study-plan/VALIDATION.md`](../../../CCDAK/study-plan/VALIDATION.md) — bảng "mặc định ĐÃ ĐỔI theo version".

## ✅ Checklist hoàn thành Tuần 1

- [ ] Hoàn thành 4 buổi A/B/C/D
- [ ] Thuộc lòng bảng "PHẢI NHỚ" (3 hoặc 5 / 2N+1 / 1000 / 2000 / 30000 / 1 / 50 / 5 GB / 9092 / 9093)
- [ ] Vẽ lại được từ trí nhớ **sơ đồ hai mặt phẳng** và **bảng ánh xạ ZooKeeper → KRaft**
- [ ] Hoàn thành **6/6 lab**, trong đó **2 lab "gây hỏng rồi sửa"** (1.2 và 1.3) làm được **không nhìn hướng dẫn** ở lần thứ hai
- [ ] Làm xong 28 câu [questions.md](questions.md) trong ~42 phút, ghi sổ câu sai kèm **lý do sai**
- [ ] Vượt toàn bộ **Cổng tự kiểm tra** (8 câu) mà không tra tài liệu
