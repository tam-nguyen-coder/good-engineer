# 🛠️ Tuần 4 — Deployment Architecture: sizing, rack awareness, multi-DC, DR

> **Domain CCAAK:** Deployment Architecture (12%) · **Thời lượng:** ~11h (4 buổi) · **Vị trí:** Tuần 4/8
>
> **Điều hướng:** [⬅️ Tuần 3](../week-03/README.md) · [🏠 Kế hoạch tổng](../../CCAAK-STUDY-PLAN.md) · [Tuần 5 ➡️](../week-05/README.md)

## 🔁 Ôn nhanh từ CCDAK (~20 phút)

| Khái niệm | File CCDAK cần đọc lại | Vì sao cần cho tuần này |
|---|---|---|
| `KRaft` cơ bản: `process.roles`, quorum, `__cluster_metadata`, `kafka-storage.sh format` | [`week-01/README.md`](../../../CCDAK/study-plan/week-01/README.md) mục KRaft + [`week-01/resources/kafka-operations-kraft.md`](../../../CCDAK/study-plan/week-01/resources/kafka-operations-kraft.md) | Tuần này quyết định **đặt controller ở đâu, bao nhiêu cái** — phải chắc nền quorum trước |
| RF · ISR · `min.insync.replicas` · rack awareness ở mức khái niệm | [`week-02/README.md`](../../../CCDAK/study-plan/week-02/README.md) + [`week-02/resources/kafka-replication-isr.md`](../../../CCDAK/study-plan/week-02/resources/kafka-replication-isr.md) | Sizing disk nhân với RF; rack awareness là replica placement; "mất 1 rack" quy về ISR còn bao nhiêu |
| `client.rack` + `replica.selector.class` (follower fetching) nhìn từ phía **client** | [`week-04/README.md`](../../../CCDAK/study-plan/week-04/README.md) mục 1 (poll loop) | Tuần này nhìn **phía broker**: ai bật, bật thế nào, tiết kiệm được gì |
| MirrorMaker 2 lần đầu + reassignment + rolling restart | [`week-08/README.md`](../../../CCDAK/study-plan/week-08/README.md) và [`week-08/labs.md`](../../../CCDAK/study-plan/week-08/labs.md) (Lab 8.4, 8.6, 8.7) | Tuần này đi sâu **góc vận hành**: offset translation, throttle, thứ tự nâng cấp, finalize feature |
| Tiered storage: `remote.log.storage.system.enable`, `local.retention.ms` | [`week-08/resources/kafka-tiered-storage.md`](../../../CCDAK/study-plan/week-08/resources/kafka-tiered-storage.md) | Bật tiered storage làm **đổi hẳn công thức disk** — local retention nhỏ hơn retention tổng rất nhiều |

## 🎯 Mục tiêu tuần này

- **Tính được trên giấy** số partition (`max(t/p, t/c)` + biên tăng trưởng), dung lượng disk (`throughput × retention × RF × 1.2`) và số broker cho một đề bài throughput/retention cho trước — rồi kiểm lại bằng thực nghiệm nhỏ.
- **Liệt kê được 4 chi phí của over-partition** (file descriptor, thời gian leader election, latency end-to-end, bộ nhớ metadata/client) và giải thích vì sao **không giảm được partition** khiến đây là quyết định một chiều.
- **Thiết kế được controller topology**: combined chỉ dev, production tách riêng, quorum 3 hay 5, rải qua AZ nào, và sizing máy controller nhẹ hơn broker ra sao.
- **Tự tay bật `broker.rack`**, xác nhận replica rải đều rack, rồi **tắt cả một rack** và đọc đúng triệu chứng (URP, `UnderMinIsr`, offline partition) trước khi khôi phục.
- **Cấu hình được follower fetching** đủ 3 mảnh (`broker.rack` + `replica.selector.class` + `client.rack`) và giải thích nó tiết kiệm **chi phí đọc**, không phải latency ghi.
- **Chọn đúng giữa MM2, Cluster Linking và stretch cluster** cho một yêu cầu RPO/RTO cụ thể, và dựng được MM2 thật giữa 2 cluster local kèm dịch offset consumer group.
- **Thực hiện được rolling upgrade và thay đổi cluster** an toàn: chờ URP = 0 từng broker, finalize bằng `kafka-features.sh`, reassign có throttle và **gỡ throttle**, cordon rồi unregister broker.

## 📚 Nội dung học chi tiết

### 🅰️ Buổi A — Lý thuyết (~3h)

**1. Capacity planning — partition**

- Công thức gốc (Confluent): cần **`max(t/p, t/c)`** partition, với `t` = throughput mục tiêu, `p` = throughput **một partition** phía producer, `c` = throughput **một partition** phía consumer. Vì `p` thường rất cao (*"one can produce at 10s of MB/sec on just a single partition"*), thực tế **`c` mới là cái chặn** — số partition bị quyết định bởi tốc độ **xử lý** của consumer.
- Cộng **biên tăng trưởng** (thường ×1.5–2 cho 12–24 tháng) vì **`--alter --partitions` chỉ tăng được, không giảm được**. Tăng partition còn **phá phân bố key → partition** (cùng key có thể rơi partition khác) nên phá thứ tự theo key với dữ liệu cũ.
- **Chi phí của over-partition — bảng bắt buộc thuộc:**

| Chi phí | Cơ chế | Con số docs nêu |
|---|---|---|
| **File descriptor** | Mỗi partition là một thư mục; mỗi segment mở **2 file** (`.log` + `.index`), cộng mọi connection | Cluster production chạy *"more than 30 thousand open file handles per broker"*; khuyến nghị FD **≥ 100.000** |
| **Thời gian mất khả dụng khi broker chết bẩn** | Controller phải bầu leader cho **từng** partition | *"5 ms"* mỗi partition × **1000 partition** = **tới 5 giây** không phục vụ |
| **Latency end-to-end** | Replication thêm một vòng cho mỗi partition | *"replicating 1000 partitions from one broker to another can add about 20 ms latency"* |
| **Bộ nhớ client + metadata** | Producer batch **theo partition**, consumer fetch buffer **theo partition**; metadata mỗi partition nằm trong `__cluster_metadata` và trong bộ nhớ controller | *"at least a few tens of KB per partition being produced"* |

- **Trần thực tế:** *"limit the number of partitions per broker to two to four thousand and the total number of partitions in the cluster to low tens of thousand"*. Nhạy latency thì chặt hơn: **`100 × b × r`** partition/broker (`b` = số broker, `r` = RF). KRaft bầu leader nhanh hơn ZooKeeper cũ nên đây là mốc **thận trọng**, không phải giới hạn cứng của 4.x.

**2. Capacity planning — disk, broker, RAM, network**

- **Disk mỗi cluster** = `throughput ghi (byte/s) × retention (giây) × RF × hệ số dự phòng (~1.2)`. Ví dụ 50 MB/s ghi, retention 7 ngày (604.800 s), RF 3 → `50 × 604800 × 3 × 1.2 ≈ 109 TB` → chia cho số broker ra disk mỗi broker. Nhớ cộng phần **compaction** cần chỗ trống để ghi segment mới, và `log.retention.bytes` là **per partition**, không phải per topic.
- **Tiered storage đổi hẳn phép tính:** bật `remote.log.storage.system.enable` + topic `remote.storage.enable=true` thì disk broker chỉ phải chứa **`local.retention.ms`/`local.retention.bytes`** (mặc định **-2** = dùng `retention.ms`), còn `retention.ms` tổng áp cho tier remote. Retention 1 năm với local 1 ngày → disk broker nhỏ đi ~365 lần. Đổi lại đọc dữ liệu cũ đi qua remote fetch, chậm hơn.
- **Số broker**: phải còn **đủ công suất khi mất 1 broker** (hoặc cả 1 rack nếu rack awareness). Chạy 3 broker ở 90% CPU = mất 1 broker là sập. Cũng phải ≥ RF (RF 3 cần tối thiểu 3 broker) và ≥ số rack muốn trải.
- **RAM**: heap *"does not require setting heap sizes more than 6 GB"* (`-Xms6g -Xmx6g`), phần còn lại **để OS làm page cache** — *"file system cache of up to 28-30 GB on a 32 GB machine"*. Heap to hơn **không** nhanh hơn; chỉ làm GC pause dài → ISR flapping. Máy 64 GB là lựa chọn tốt.
- **CPU**: mốc **24 core**, ưu tiên nhiều core hơn core nhanh; **TLS làm CPU tăng đáng kể**. **Disk**: 12 × 1 TB, tách ổ OS khỏi ổ Kafka, SSD, tránh NAS, filesystem **XFS/ext4**. **Network**: 1–10 GbE, **latency < 30 ms** giữa node cùng cluster. Ước lượng network in = `throughput ghi × RF`, network out = `throughput ghi × (số consumer group + RF − 1)`.

**3. Controller topology**

| Tiêu chí | Combined (`process.roles=broker,controller`) | Tách riêng (`controller` và `broker`) |
|---|---|---|
| Docs nói gì | *"simpler to operate for small use cases like a development environment"*; **"Combined mode is not recommended in critical deployment environments"** | Khuyến nghị cho production |
| Cách ly lỗi | *"the controller will be less isolated from the rest of the system"* — GC pause hay disk đầy vì log topic kéo luôn controller xuống | Controller không nhận produce/fetch → tải ổn định, dễ đoán |
| Nâng cấp | **Không thể** roll hoặc scale controller tách khỏi broker | Nâng controller và broker độc lập |
| Sizing | Dùng chung tài nguyên broker | Nhẹ: docs Kafka ~**5 GB RAM / 5 GB disk**; Confluent gợi ý **4 GB RAM / 64 GB SSD** |
| Số node tối thiểu | 3 node combined | **3 broker + 3 controller** (Confluent: *"a production cluster should have a minimum of three brokers and three controllers"*) |
| Khi nào dùng | Lab, dev, CI | Mọi thứ còn lại |

- **Quorum 3 hay 5**: *"A majority of the controllers must be alive"*. 3 → chịu mất **1**; 5 → chịu mất **2**; công thức docs: chịu `N` lỗi cần **`2N + 1`** controller. Số **chẵn vô nghĩa** (4 controller vẫn chỉ chịu 1 lỗi, tốn thêm 1 máy).
- **Đặt ở đâu**: rải qua **AZ/rack khác nhau**, tuyệt đối không dồn 2 trong 3 controller vào cùng một AZ — mất AZ đó là mất đa số. 5 controller trên 3 AZ thì chia 2-2-1.
- **Mất đa số quorum**: **control plane đóng băng** (không tạo/xoá topic, không bầu leader mới, không đăng ký broker mới) nhưng **data plane vẫn phục vụ** produce/fetch cho partition không đổi leader, vì broker dùng metadata đã cache. Đây là phân biệt hay bị hỏi.
- **Static vs dynamic quorum**: `controller.quorum.voters` (mọi id/host/port cố định, đổi phải restart cả cụm) vs `controller.quorum.bootstrap.servers` + KIP-853 (thêm/bớt controller lúc chạy bằng `kafka-metadata-quorum.sh add-controller` / `remove-controller`). Nhận biết: `kafka-features.sh describe` → **`kraft.version` ≥ 1 = dynamic**, `0` = static.

**4. Rack awareness — replica placement**

- `broker.rack=<id>` (kiểu string, mặc định `null`, **read-only** → đổi phải restart). Khi tạo topic hoặc reassign, controller bảo đảm replica của một partition trải **`min(#racks, replication-factor)`** rack khác nhau.
- Thuật toán còn giữ **số leader mỗi broker gần như bằng nhau** bất kể phân bố rack, để throughput không lệch.
- ⚠️ **Rack lệch nhau là bẫy:** docs ghi *"if brokers are assigned different numbers of racks, the assignment of replicas will not be even. Racks with fewer brokers will get more replicas"* → rack ít broker gánh nhiều replica hơn, tốn disk và băng thông replication hơn. Khuyến nghị **số broker mỗi rack bằng nhau**.
- **RF phải ≥ số rack muốn sống sót.** RF 3 trên 3 rack → mất 1 rack còn 2 replica, vẫn ≥ `min.insync.replicas=2`, vẫn ghi được. RF 3 trên **2** rack → một rack chứa 2 replica, mất rack đó còn 1 → dưới min.isr, **ngừng ghi**. RF 4 trên 3 rack **không** tốt hơn RF 3: vẫn có một rack chứa 2 replica, tốn thêm 33% disk.
- Broker **không có** `broker.rack` sẽ bị coi là không có thông tin rack → `kafka-topics.sh --create` với `--replica-assignment` thủ công bỏ qua rack; còn tạo topic bình thường trên cluster **trộn** broker có và không có rack sẽ báo lỗi hoặc bỏ qua ràng buộc rack tuỳ phiên bản. Nguyên tắc: **hoặc tất cả broker khai rack, hoặc không broker nào khai**.

**5. Follower fetching (KIP-392) — cắt chi phí đọc xuyên AZ**

- Cần **đủ 3 mảnh, thiếu 1 là vô hiệu**: broker `broker.rack=<az>` · broker `replica.selector.class=org.apache.kafka.common.replica.RackAwareReplicaSelector` (mặc định là `LeaderSelector` = luôn leader) · consumer `client.rack=<az>` (mặc định `""`).
- Cơ chế: consumer fetch tới **leader** kèm rack id → leader chạy selector và trả **`PreferredReadReplica`** trong `FetchResponse` → consumer fetch thẳng replica đó. Quay lại leader khi cache hết hạn theo `metadata.max.age.ms` (**300000** ms) hoặc replica trả lỗi.
- **Chỉ replica trong ISR** đủ điều kiện; follower chỉ trả tới **high watermark** nên không lộ dữ liệu chưa commit, nhưng có thể **chậm hơn leader** một nhịp fetch. Đây là đánh đổi **chi phí lấy độ trễ**.
- **Producer vẫn luôn ghi vào leader.** Follower fetching **không** giảm latency ghi và **không** tăng throughput — nó giảm **hoá đơn cross-AZ**.
- Phân biệt 3 thứ dễ lẫn: `broker.rack` = **đặt replica ở đâu** · `client.rack` + `replica.selector.class` = **đọc từ đâu** · rack-aware assignor (KIP-881) = **chia partition cho consumer nào**.

**6. Multi-DC: stretch cluster vs cluster tách rời**

- **Khuyến nghị gốc của Apache Kafka**: mỗi DC **một cluster riêng**, ứng dụng chỉ nói chuyện với cluster local, rồi mirror. Docs nói thẳng *"it is generally not advisable to run a single Kafka cluster that spans multiple datacenters over a high-latency link"*.
- **Stretch cluster** chỉ hợp lệ khi mạng **ổn định và < 100 ms** (Confluent gọi là "dark fiber"). Khi đó replication chính là ISR → **đồng bộ** → **RPO = 0, RTO ≈ 0**, không cần dịch offset vì chỉ có một cluster.
- **2 DC không stretch được** (quorum chẵn, mất 1 DC là mất đa số) → **"2.5 DC"**: 2 DC chạy broker + controller đầy đủ, **DC thứ ba chỉ chạy controller** để quorum luôn lẻ và luôn có đa số khi mất 1 DC đầy đủ.
- Bắt buộc đi xuyên WAN → tăng `socket.send.buffer.bytes` / `socket.receive.buffer.bytes` (mặc định **102400**) để bù bandwidth-delay product.

**7. DR — bảng quyết định bắt buộc thuộc**

| Tiêu chí | **MirrorMaker 2** | **Cluster Linking** | **Stretch cluster (2.5 / 3 DC)** |
|---|---|---|---|
| Có ở đâu | **Apache Kafka thuần** (và mọi bản phái sinh) | **Chỉ Confluent Server / Confluent Cloud** | Apache Kafka hoặc Confluent |
| Cơ chế | 3 connector chạy trên **Kafka Connect**, consume cluster nguồn → produce cluster đích | **Broker đích kéo trực tiếp** từ broker nguồn, *"does not require running Connect"* | Không có replication liên cluster — chính là **ISR** của một cluster |
| Tên topic đích | `DefaultReplicationPolicy` → **`{source}.{topic}`**; `IdentityReplicationPolicy` giữ tên | **Giữ nguyên tên** (mirror topic **read-only**) | Không đổi (cùng một topic) |
| Offset | **Đổi** → cần offset translation qua `{source}.checkpoints.internal` | **Giữ nguyên byte-for-byte**, không cần dịch | Không có khái niệm dịch |
| RPO / RTO | **> 0 / > 0** (bất đồng bộ) | **> 0 / > 0** (bất đồng bộ, nhưng RTO thấp hơn vì offset và ACL đã sẵn) | **RPO = 0 / RTO ≈ 0** |
| Hai chiều | `A->B, B->A` (active-active) | Cần **2 link đơn hướng** riêng | Không áp dụng |
| Bộ phận phải vận hành thêm | Connect worker, 3 connector, topic nội bộ ở cả 2 cluster | Không có — nằm trong broker | Không có, nhưng ràng buộc mạng rất chặt |
| Giới hạn đáng nhớ | Không copy được state của transaction; `groups.exclude` loại console consumer | **Không mirror được message transaction**; đích ≥ Confluent Server 7.8.0 | Cần **< 100 ms** và ≥ 3 vị trí (hoặc 2.5 DC) |
| Chọn khi đề nói | *"Apache Kafka thuần"*, *"active-active"*, *"aggregate nhiều cluster"* | *"giữ nguyên offset"*, *"ít bộ phận vận hành nhất"*, *"migration sang cloud"* | *"không được mất một message nào"* + *"các DC cách nhau vài chục km"* |

**8. MirrorMaker 2 ở góc vận hành**

- **3 connector**: `MirrorSourceConnector` (record + topic config + ACL, giữ partition, tự phát hiện topic mới) · `MirrorCheckpointConnector` (dịch offset group → `{source}.checkpoints.internal`) · `MirrorHeartbeatConnector` (topic `heartbeats`, đo liveness và `replication-latency-ms`).
- **Flow mặc định TẮT** — khai `clusters = A, B` thôi thì không có gì chạy, phải có **`A->B.enabled = true`**. Lỗi vận hành số 1.
- `DefaultReplicationPolicy` đổi tên thành `{source}.{topic}` để **chống loop** (bắt buộc cho active-active); `IdentityReplicationPolicy` giữ tên → **chỉ** active-passive và migration.
- Mặc định `topics = .*`, `groups = .*`, nhưng **`groups.exclude = console-consumer-.*, connect-.*, __.*`** → group của console consumer **không** được replicate. Rất hay làm người mới tưởng offset sync hỏng.
- `sync.group.offsets.enabled = true` ghi thẳng offset đã dịch vào `__consumer_offsets` của đích, **chỉ khi group ở đích inactive**. Dịch là **conservative** (không vượt) → consumer phải idempotent.
- **Exactly-once từ 3.5.0**: `{target}.exactly.once.source.support = enabled` (cluster cũ đi 2 bước `preparing` → `enabled`) + `dedicated.mode.enable.internal.rest = true` + `listeners`; nên đặt `{source}.consumer.isolation.level = read_committed`.
- **"Consume from remote, produce to local"**: chạy MM2 gần cluster **đích**, truyền `--clusters <target>`. `tasks.max` phải **≥ 2** (mặc định 1 = không scale). Đổi config phải **restart**; nhiều process cùng target mà config lệch → race.

**9. Rolling upgrade & thay đổi cluster**

- **Rolling upgrade KRaft chỉ 2 giai đoạn**: (1) nâng **từng** node — tắt, thay binary, khởi động, **chờ `UnderReplicatedPartitions` = 0** và `ActiveControllerCount` tổng = 1, rồi mới sang node kế; (2) khi mọi node đã chạy bản mới **và** đã xác minh, **finalize** bằng `kafka-features.sh --bootstrap-server ... upgrade --release-version 4.3`.
- **`metadata.version` thay hoàn toàn `inter.broker.protocol.version`** — config cũ **không còn tồn tại** trong KRaft.
- **Downgrade**: chỉ được khi **không có metadata change** giữa hai version. 4.3.0 và 4.0.x **không downgrade được**; 4.2.0 thì được. Nâng lên 4.x cần software/metadata ≥ **3.3**; cũ hơn thì qua **3.9** trước; còn ZooKeeper thì migrate sang KRaft trước.
- `controlled.shutdown.enable=true` (mặc định) là thứ khiến rolling restart "zero-downtime": broker *"sync all its logs to disk"* và *"migrate any partitions the server is the leader for to other replicas prior to shutting down"*. `kill -9` thì không, và lần lên lại phải log recovery.
- **Thêm broker**: *"these new servers will not automatically be assigned any data partitions"* → phải `kafka-reassign-partitions.sh --generate` (cần `--topics-to-move-json-file` + `--broker-list`) → `--execute --throttle <B/s>` → `--verify`. **`--verify` mới là lệnh gỡ throttle** — quên nó thì replication bị bóp vĩnh viễn.
- **Tăng RF**: viết JSON thêm replica (`"replicas":[5,6,7]`) rồi `--execute`. Không có `--alter --replication-factor`.
- **Decommission**: `cordoned.log.dirs="*"` (controller thôi đặt partition mới) → reassign hết đi → tắt broker → `kafka-cluster.sh unregister --id <n>`.
- Sau mọi thứ: `kafka-leader-election.sh --election-type preferred --all-topic-partitions` để trả leader về preferred; hoặc chờ `auto.leader.rebalance.enable` mỗi `leader.imbalance.check.interval.seconds` (**300**). Lưu ý `leader.imbalance.per.broker.percentage` **không dùng trong KRaft**.
- **Cruise Control** (LinkedIn, ngoài Apache Kafka): tự theo dõi tải và sinh proposal theo **goal** (hard: `RackAwareGoal`, `ReplicaCapacityGoal`, `DiskCapacityGoal`; soft: `ReplicaDistributionGoal`…), có self-healing. Nó **vẫn thực thi bằng chính cơ chế reassignment** — chỉ khác là bạn nêu mục tiêu thay vì viết JSON tay.

### 🅱️ Buổi B — Hands-on (~3.5h)

> 🧪 **Lab cầm tay chỉ việc (từng bước + lệnh + output mẫu):** [labs.md](labs.md). Dùng lại `~/kafka-labs/` và 2 file compose chuẩn từ [CCDAK Tuần 1](../../../CCDAK/study-plan/week-01/labs.md) (`controller` node.id 1, `kafka-1/2/3` node.id 2/3/4, host port 9092/9094/9096) cùng alias `kt`/`kcp`/`kcc`/`kcg`/`kcfg`.

- **Lab 4.1 ⭐ — Sizing trên giấy rồi kiểm bằng thực nghiệm:** tính partition/disk/broker cho một đề bài cho trước, rồi đo throughput một partition thật bằng `kafka-producer-perf-test.sh` và đo dung lượng thật bằng `kafka-log-dirs.sh` để đối chiếu.
- **Lab 4.2 ⭐ — `broker.rack` và "tắt cả một rack" (gây hỏng rồi sửa):** gán rack cho 3 broker, tạo topic RF 3, xác nhận replica rải đều rack, rồi **tắt cả một rack** và đọc triệu chứng trước khi khôi phục.
- **Lab 4.3 — Follower fetching:** bật `replica.selector.class=RackAwareReplicaSelector`, chạy consumer với `client.rack` khớp và không khớp, xác nhận replica phục vụ đổi.
- **Lab 4.4 ⭐ — MirrorMaker 2 giữa 2 cluster local:** `mm2.properties` đầy đủ, kiểm chứng `A.orders` / `heartbeats` / `A.checkpoints.internal`, dịch offset consumer group, rồi đổi sang `IdentityReplicationPolicy`.
- **Lab 4.5 — Reassignment với broker thứ 4:** `--generate` → `--execute --throttle` → soi 4 config throttle → `--verify` để **gỡ throttle** → preferred election.
- **Lab 4.6 — Rolling upgrade mô phỏng (gây hỏng rồi sửa):** script tắt/bật từng broker chờ URP = 0, `kafka-features.sh describe` trước/sau, cộng đối chứng "tắt 2 broker cùng lúc" để thấy `NotEnoughReplicas`.
- **Lab 4.7 (concept) — Cluster Linking:** chứng minh vì sao không chạy được trên Apache Kafka thuần, in cấu hình mẫu Confluent Platform và đối chiếu từng dòng với MM2.

### 🅲️ Buổi C — Bổ sung (~2.5h)

**Bảng quyết định 1 — "Tôi cần gì cho DR?"**

| Yêu cầu trong đề | Đáp án | Vì sao không phải cái kia |
|---|---|---|
| "Không được mất một message nào" + DC cách nhau < 100 ms | **Stretch cluster** (3 DC hoặc 2.5 DC) | MM2/Cluster Linking đều bất đồng bộ → RPO > 0 |
| "Chỉ có 2 DC nhưng vẫn muốn RPO = 0" | **2.5 DC** — thêm DC thứ ba **chỉ chạy controller** | 2 DC là quorum chẵn, mất 1 DC là mất đa số |
| "Consumer phải tiếp tục đúng offset sau failover, ít vận hành nhất" | **Cluster Linking** | MM2 đổi offset, phải dịch qua checkpoint |
| "Apache Kafka thuần, không có Confluent Platform" | **MirrorMaker 2** | Cluster Linking không tồn tại trên Apache Kafka |
| "Ứng dụng chạy ở cả 2 vùng, cả 2 cùng nhận traffic" | **MM2 active-active** `A->B, B->A` + `DefaultReplicationPolicy` | `IdentityReplicationPolicy` không chống loop |
| "Gom 5 cluster vùng về một chỗ để phân tích" | **MM2 aggregation** `A->K, B->K, ...` | Cluster Linking mỗi link một chiều, tên topic trùng nhau ở đích |
| "Migrate ứng dụng sang cluster mới rồi tắt cluster cũ" | **Cluster Linking** (`--promote`) hoặc **MM2 + `IdentityReplicationPolicy`** | `DefaultReplicationPolicy` đổi tên topic → ứng dụng phải sửa cấu hình |
| "Đọc từ AZ khác tốn tiền quá" | **Follower fetching** (KIP-392) | Đây không phải bài toán DR — đừng nhảy sang MM2 |

**Bảng quyết định 2 — "Cluster cần thay đổi, dùng công cụ nào?"**

| Việc cần làm | Công cụ | Bẫy |
|---|---|---|
| Broker mới không có traffic | `kafka-reassign-partitions.sh --generate/--execute/--verify` | Kafka **không** tự chuyển partition sang broker mới |
| Reassignment làm nghẽn mạng | `--execute --throttle <B/s>`, sửa bằng `--additional` | **Phải `--verify`** mới gỡ throttle |
| Leader dồn về 1 broker sau restart | `kafka-leader-election.sh --election-type preferred` | Đây là **election**, không copy data — đừng reassign |
| Tăng RF từ 2 lên 3 | JSON reassignment thêm replica | Không có cờ `--replication-factor` khi alter |
| Bỏ hẳn một broker | `cordoned.log.dirs` → reassign → `kafka-cluster.sh unregister` | Tắt máy trước khi reassign = partition mất replica |
| Cân bằng tự động ở cluster hàng trăm broker | **Cruise Control** | Không thuộc Apache Kafka; vẫn dùng reassignment bên dưới |
| Chốt version sau khi nâng cấp | `kafka-features.sh upgrade --release-version 4.3` | **Không** phải `inter.broker.protocol.version` (đã bị gỡ) |
| Xem quorum kiểu gì, feature ở mức nào | `kafka-features.sh describe`, `kafka-metadata-quorum.sh describe --status` | `kraft.version` 0 = static, ≥ 1 = dynamic |

**Đọc thêm:** [`resources/INDEX.md`](resources/INDEX.md) theo đúng thứ tự gợi ý; chương 10 (*Cross-Cluster Data Mirroring*) và chương 12 (*Administering Kafka*) của *Kafka: The Definitive Guide* 2nd ed.; Confluent Developer course *Mastering Production Data Streaming Systems*.

### 🅳 Buổi D — Practice + Review (~2h)

> 📝 **Bộ câu hỏi luyện tập của tuần:** [questions.md](questions.md) — đáp án & giải thích: [answers.md](answers.md). *(tiếng Anh, văn phong CCAAK.)*

- Làm **28 câu** của tuần trong 42 phút (~90 giây/câu như đề thật); ghi sổ câu sai, phân loại: sizing / controller topology / rack / MM2 / Cluster Linking / upgrade & reassignment.
- **Bài tập giấy bắt buộc:** vẽ lại từ trí nhớ bảng *MM2 vs Cluster Linking vs stretch cluster* (8 dòng) và bảng *chi phí over-partition* (4 dòng). Không nhìn tài liệu.
- **Bài tập thứ tự (dạng list order của đề thật):** viết lại đúng thứ tự (a) rolling upgrade 1 cluster, (b) thêm broker và cân bằng lại, (c) decommission broker. Ba chuỗi này gần như chắc chắn xuất hiện ở dạng ordering.
- **Spaced repetition:** flashcard số liệu theo mốc **1 / 3 / 7 ngày** (3 hoặc 5 controller · 2N+1 · `min(#racks, RF)` · 6 GB heap · 100.000 FD · 2000–4000 partition/broker · 100 ms · 300000 ms · 300 s · 102400).

## 🧠 PHẢI NHỚ tuần này

| Fact | Con số / Ghi nhớ |
|---|---|
| Công thức partition | **`max(t/p, t/c)`** + biên tăng trưởng; `c` (consumer) thường là cái chặn; **không giảm được partition** |
| Trần partition | **2000–4000** partition/broker, cluster **vài chục nghìn**; nhạy latency: **`100 × b × r`** |
| Chi phí over-partition | FD (> **30.000**/broker thực tế, đặt **≥ 100.000**) · leader election **5 ms** × 1000 = **5 s** · **+20 ms** latency/1000 partition · **vài chục KB**/partition ở client |
| Công thức disk | `throughput ghi × retention × RF × 1.2`; tiered storage → chỉ tính **`local.retention.*`** (mặc định **-2**) |
| Heap vs page cache | Heap **≤ 6 GB** (`-Xms6g -Xmx6g`), phần còn lại page cache (**28–30 GB** trên máy 32 GB); RAM khuyến nghị **64 GB** |
| Phần cứng broker | **24 core** · **12 × 1 TB** · XFS/ext4 · tách ổ OS · **1–10 GbE**, latency **< 30 ms** trong cluster |
| Controller: combined vs tách + sizing | Combined *"not recommended in critical deployment environments"*, không roll/scale riêng được; production tối thiểu **3 broker + 3 controller**; máy controller nhẹ — Kafka docs ~**5 GB RAM / 5 GB disk**, Confluent **4 GB RAM / 64 GB SSD** |
| Quorum controller | **3 hoặc 5** (lẻ); 3 → chịu **1** lỗi, 5 → chịu **2**; chịu N lỗi cần **2N+1**; rải qua AZ, 5 controller/3 AZ chia **2-2-1** |
| Mất đa số quorum | **Control plane đóng băng**, **data plane vẫn phục vụ** partition không đổi leader |
| Static vs dynamic quorum | `controller.quorum.voters` vs `controller.quorum.bootstrap.servers` (KIP-853); nhận biết bằng **`kraft.version`** 0 / ≥ 1 |
| Rack awareness | `broker.rack` (read-only, restart); partition trải **`min(#racks, RF)`** rack; rack lệch → rack ít broker **gánh nhiều replica hơn**; nên **số broker mỗi rack bằng nhau** |
| Follower fetching | **3 mảnh**: `broker.rack` + `replica.selector.class=RackAwareReplicaSelector` + `client.rack`; quay lại leader sau `metadata.max.age.ms` **300000**; **producer vẫn ghi leader** |
| Stretch cluster | Cần **< 100 ms** và ổn định; **RPO = 0 / RTO ≈ 0**; 2 DC → phải thành **2.5 DC** (DC thứ ba chỉ controller) |
| RPO/RTO chính thức | Cluster Linking **> 0 / > 0** · MirrorMaker **> 0 / > 0** · MRC **= 0 hoặc > 0 / ≥ 0** (chỉ Confluent Platform) |
| MM2 | **3 connector**; flow **mặc định tắt** → `A->B.enabled=true`; `DefaultReplicationPolicy` → **`{source}.{topic}`**; `groups.exclude = console-consumer-.*, connect-.*, __.*`; EOS từ **3.5** |
| Cluster Linking | Chỉ **Confluent**; broker kéo trực tiếp, **không cần Connect**; **giữ nguyên offset byte-for-byte**; mirror topic **read-only**; hai chiều cần **2 link**; **không mirror transaction**; đích ≥ **7.8.0** |
| Rolling upgrade | 1 node/lần → **chờ URP = 0** → finalize `kafka-features.sh upgrade --release-version 4.3`; **`metadata.version` thay `inter.broker.protocol.version`** |
| Downgrade | Chỉ khi **không có metadata change**; **4.3.0 và 4.0.x không downgrade**, 4.2.0 thì được; lên 4.x cần ≥ **3.3** |
| Reassignment | `--generate` (cần `--topics-to-move-json-file` + `--broker-list`) → `--execute --throttle` → **`--verify` mới gỡ throttle**; tăng RF cũng bằng JSON |
| Config leader balance | `auto.leader.rebalance.enable` **true**, `leader.imbalance.check.interval.seconds` **300**; **`leader.imbalance.per.broker.percentage` không dùng trong KRaft** |
| Socket buffer xuyên WAN | `socket.send.buffer.bytes` / `socket.receive.buffer.bytes` **102400** (100 KiB) — tăng khi đi qua link độ trễ cao |

## 🚨 Playbook: triệu chứng → hành động

| Triệu chứng | Nguyên nhân khả dĩ | Hành động đầu tiên |
|---|---|---|
| Thêm broker thứ 4 nhưng `BytesInPerSec` của nó = 0, 3 broker cũ vẫn full disk | Kafka **không tự** chuyển partition sang broker mới | `kafka-reassign-partitions.sh --generate --broker-list "2,3,4,5"` rồi `--execute --throttle` |
| Reassignment "xong" nhưng URP cao dai dẳng nhiều ngày sau | **Throttle chưa được gỡ** (quên `--verify`) | `kcfg --describe --entity-type brokers` tìm `*.replication.throttled.rate`; chạy `--verify`, hoặc xoá config thủ công |
| Mất 1 AZ → nhiều partition offline dù RF = 3 | RF 3 trên **2 rack**, hoặc broker chưa khai `broker.rack`, hoặc số broker mỗi rack lệch | `kt --describe` xem replica có trải rack không; `kcfg --describe --entity-type brokers --all \| grep broker.rack` |
| `UnderMinIsrPartitionCount` > 0 ngay khi tắt **1** rack | RF/min.isr không chịu nổi mất 1 rack (ví dụ RF 3 / min.isr 3, hoặc 2 replica cùng rack) | Khôi phục rack trước; sau đó tính lại RF theo số rack, **không** hạ `min.insync.replicas` trong lúc sự cố |
| Hoá đơn cross-AZ tăng vọt trong khi throughput không đổi | Consumer đọc từ leader ở AZ khác | Bật đủ **3 mảnh** KIP-392; kiểm bằng metric `FetchFollower` / log fetch của follower |
| Cluster "đơ": không tạo được topic, nhưng produce/consume vẫn chạy | Mất **đa số** controller quorum → control plane đóng băng | `kafka-metadata-quorum.sh describe --status` xem `LeaderId` và `CurrentVoters`; khôi phục controller, **không** động vào broker |
| Broker mới không join, log in `InconsistentClusterId` | Format sai `cluster.id`, hoặc trỏ nhầm quorum | So `cluster.id` trong `meta.properties` với `kq describe --status`; format lại đúng id |
| Rolling upgrade: broker thứ hai vừa tắt thì producer báo `NotEnoughReplicas` | Không chờ URP về 0 trước khi sang broker kế; RF 3/min.isr 2 chỉ chịu **1** broker vắng | Bật lại broker vừa tắt ngay; sửa quy trình: `kt --describe --under-replicated-partitions` phải rỗng mới đi tiếp |
| Đã nâng hết broker lên 4.3 nhưng `kafka-features.sh describe` vẫn ghi `metadata.version` cũ | Chưa **finalize** | `kafka-features.sh upgrade --release-version 4.3` (thử `--dry-run` trước) |
| MM2 chạy, log sạch, nhưng cluster đích không có topic nào | Flow chưa bật (`A->B.enabled` thiếu) hoặc `A->B.topics` không khớp | Kiểm 2 dòng đó trong `mm2.properties`; nhớ regex mặc định là `.*` nhưng flow mặc định **tắt** |
| MM2 copy data OK nhưng consumer group không xuất hiện ở đích | Group bị **`groups.exclude`** loại (console consumer), hoặc `sync.group.offsets.enabled` chưa bật, hoặc group ở đích đang **active** | Đổi sang group có tên thật; bật `sync.group.offsets.enabled=true`; dừng consumer ở đích |
| Sau rolling restart, 1 broker giữ gần hết leader, CPU nó 90% | Leader chưa quay về preferred replica | `kafka-leader-election.sh --election-type preferred --all-topic-partitions` (không copy data, chạy vài giây) |

## ⚠️ Bẫy đề hay gặp

- Thấy "cần thêm throughput cho consumer" → dễ chọn **tăng partition**, nhưng đúng là kiểm **skew key** và số consumer trước; tăng partition là **một chiều**, phá phân bố key, và kéo theo 4 khoản chi phí.
- Thấy "broker mới đã join cluster, cluster tự cân bằng chưa?" → dễ chọn có, nhưng docs ghi rõ *"these new servers will not automatically be assigned any data partitions"* → phải **reassign tay** (hoặc Cruise Control).
- Thấy "reassignment đã `Reassignment ... is completed`, xong chưa?" → dễ chọn xong, nhưng **throttle vẫn còn** tới khi chạy **`--verify`**.
- Thấy "tăng RF của topic" → dễ chọn `kafka-topics.sh --alter --replication-factor 3`, nhưng cờ đó **không tồn tại**; phải viết **JSON reassignment** thêm replica.
- **(bẫy version)** Thấy "chốt protocol version sau khi nâng cấp toàn cluster" → dễ chọn `inter.broker.protocol.version`, nhưng trong KRaft config này **đã bị gỡ**; đúng là **`metadata.version`** qua `kafka-features.sh upgrade --release-version`.
- **(bẫy version)** Thấy "dùng `kafka-mirror-maker.sh --whitelist`", "chỉnh znode ZooKeeper để đổi replica", hay "điều chỉnh `leader.imbalance.per.broker.percentage` cho leader cân hơn" → đều sai với 4.x: **MM1 bị xoá ở 4.0**, **không còn ZooKeeper**, và `leader.imbalance.per.broker.percentage` **không dùng trong KRaft**; đúng là `connect-mirror-maker.sh`, `kafka-reassign-partitions.sh`, `kafka-leader-election.sh --election-type preferred`.
- Thấy "cần DR mà consumer giữ nguyên offset" → dễ chọn **MM2 + `IdentityReplicationPolicy`**, nhưng Identity chỉ giữ **tên topic**, **offset vẫn khác**; giữ nguyên offset là **Cluster Linking**.
- Thấy "active-active giữa 2 vùng bằng MM2" → dễ chọn `IdentityReplicationPolicy` cho gọn, nhưng nó **không chống loop** → phải dùng `DefaultReplicationPolicy` (`{source}.{topic}`).
- Thấy "2 datacenter, muốn RPO = 0 bằng stretch cluster" → dễ chọn được, nhưng quorum **chẵn**; phải có **DC thứ ba chạy controller** (2.5 DC).
- Thấy "đặt `client.rack` trên consumer là xong" → thiếu; phải đủ **3 mảnh** (`broker.rack` + `replica.selector.class` + `client.rack`), thiếu `replica.selector.class` thì broker vẫn trả leader. Và thấy "follower fetching giảm latency produce" cũng sai — **producer luôn ghi leader**, KIP-392 chỉ đụng tới **đọc**.
- Thấy "tăng heap broker lên 32 GB cho nhanh" → sai hướng; heap **6 GB** là đủ, phần RAM còn lại phải để **page cache**; heap to làm GC pause dài → ISR flapping.
- Thấy "RF 4 trên 3 rack an toàn hơn RF 3" → không: vẫn có một rack chứa 2 replica, mất rack đó còn 2 — bằng RF 3, mà tốn thêm 33% disk và băng thông.

## 🧪 Lab checklist

- [ ] Lab 4.1 ⭐ — Tính sizing trên giấy (partition / disk / broker) cho đề bài cho trước, rồi đo lại bằng `kafka-producer-perf-test.sh` và `kafka-log-dirs.sh`.
- [ ] Lab 4.2 ⭐ — Gán `broker.rack` cho 3 broker, tạo topic RF 3, xác nhận replica rải đều rack, **tắt cả một rack** rồi khôi phục.
- [ ] Lab 4.3 — Bật `RackAwareReplicaSelector`, chạy consumer với `client.rack` khớp và không khớp, xác nhận replica phục vụ đổi.
- [ ] Lab 4.4 ⭐ — MM2 giữa 2 cluster local: kiểm `A.orders`, `heartbeats`, `A.checkpoints.internal`, dịch offset group, rồi đổi sang `IdentityReplicationPolicy`.
- [ ] Lab 4.5 — Thêm broker thứ 4, `--generate/--execute --throttle/--verify`, **soi 4 config throttle và xác nhận nó được gỡ**, preferred election.
- [ ] Lab 4.6 — Script rolling restart chờ URP = 0 từng broker; `kafka-features.sh describe` trước/sau; đối chứng tắt 2 broker cùng lúc.
- [ ] Lab 4.7 — (concept) Chứng minh Cluster Linking không chạy trên Apache Kafka thuần; đối chiếu cấu hình mẫu Confluent với MM2.

## 🚪 Cổng tự kiểm tra (phải trả lời trôi chảy mới sang tuần sau)

- **Topic cần 300 MB/s, một consumer instance xử lý được 15 MB/s, producer đạt 50 MB/s mỗi partition. Cần bao nhiêu partition, và tại sao còn phải cộng thêm?**
  **Đáp án gọn:** `max(300/50, 300/15) = max(6, 20) = 20` partition; cộng biên tăng trưởng vì **không giảm được partition** và tăng partition phá phân bố key.
- **Kể 4 chi phí của việc đặt quá nhiều partition, kèm con số.**
  **Đáp án gọn:** file descriptor (thực tế > 30.000/broker, đặt ≥ 100.000) · thời gian bầu leader khi broker chết bẩn (~5 ms × số partition, 1000 partition ≈ 5 s) · latency end-to-end (+~20 ms cho 1000 partition) · bộ nhớ client (vài chục KB mỗi partition).
- **Cluster production 9 broker trên 3 AZ. Đặt bao nhiêu controller, ở đâu, và sizing thế nào?**
  **Đáp án gọn:** **3 controller tách riêng** (`process.roles=controller`), mỗi AZ một cái; chịu mất 1. Muốn chịu mất 2 thì 5 controller chia 2-2-1. Máy controller nhẹ: ~4–5 GB RAM, vài chục GB SSD — không sizing như broker.
- **Topic RF 3 trên cluster có `broker.rack` 3 rack. Tắt cả 1 rack thì chuyện gì xảy ra với `min.insync.replicas=2`?**
  **Đáp án gọn:** mỗi partition trải `min(3, 3) = 3` rack → mất 1 rack còn **2 replica** trong ISR → vẫn ≥ min.isr → **vẫn ghi được** với `acks=all`, chỉ có URP > 0. Nếu chỉ có 2 rack thì một rack giữ 2 replica → mất rack đó còn 1 → `NotEnoughReplicas`.
- **Cần cho consumer ở `az-b` đọc mà không trả tiền cross-AZ. Phải đặt những gì, ở đâu?**
  **Đáp án gọn:** broker: `broker.rack=<az>` + `replica.selector.class=org.apache.kafka.common.replica.RackAwareReplicaSelector`; consumer: `client.rack=az-b`. Thiếu bất kỳ mảnh nào là broker vẫn trả leader. Producer vẫn ghi leader.
- **MM2 và Cluster Linking khác nhau ở 3 điểm cốt lõi nào?**
  **Đáp án gọn:** (1) MM2 chạy trên **Connect**, Cluster Linking nằm **trong broker**; (2) MM2 **đổi offset** (cần translation), Cluster Linking **giữ nguyên byte-for-byte**; (3) MM2 có ở **Apache Kafka thuần** và làm được active-active, Cluster Linking **chỉ Confluent** và mirror topic **read-only**, hai chiều cần 2 link.
- **Viết đúng thứ tự các bước rolling upgrade một cluster KRaft 3 broker + 3 controller lên 4.3.**
  **Đáp án gọn:** với từng node một: tắt (controlled shutdown) → thay binary → khởi động → **chờ URP = 0 và `ActiveControllerCount` = 1** → node kế tiếp. Xong hết, xác minh hành vi, rồi **finalize** `kafka-features.sh upgrade --release-version 4.3`. Nhớ 4.3 **không downgrade được**.
- **Thêm broker mới xong rồi, làm gì tiếp, và bước nào hay bị quên nhất?**
  **Đáp án gọn:** `--generate` (JSON topics-to-move + `--broker-list` có broker mới) → lưu lại **current assignment** để rollback → `--execute --throttle` → `--verify` cho tới khi completed. Bước hay quên nhất: **`--verify` để gỡ throttle**, và preferred leader election sau đó.

## 📎 Tài nguyên tuần này

> 📂 **Đã crawl sẵn tài liệu chính thức vào** [`resources/`](resources/INDEX.md) — đọc offline được, có gợi ý thứ tự đọc.

- Apache Kafka Docs 4.3: *Geo-Replication (Cross-Cluster Data Mirroring)*, *Basic Kafka Operations* (expanding cluster, reassignment, throttling, rack awareness, graceful shutdown), *Datacenters*, *KRaft*, *Upgrading*.
- Confluent Platform Docs: *Cluster Linking overview*, *Multi-Datacenter Architectures* (RPO/RTO, stretch 2.5 DC), *Multi-Region Clusters* (follower fetching, observers), *Running Kafka in Production* (sizing).
- Confluent Engineering Blog: *How to Choose the Number of Topics/Partitions in a Kafka Cluster* — nguồn của công thức `max(t/p, t/c)` và 4 chi phí over-partition.
- KIP: **KIP-392** (follower fetching), **KIP-382** (MirrorMaker 2), **KIP-36** (rack-aware replica assignment), **KIP-853** (dynamic KRaft quorum), **KIP-405** (tiered storage), KIP-1066 (`cordoned.log.dirs`).
- LinkedIn **Cruise Control** README — nhận diện goal, self-healing, và quan hệ với reassignment.
- Sách: *Kafka: The Definitive Guide* 2nd ed. — chương **10** (*Cross-Cluster Data Mirroring*) và chương **12** (*Administering Kafka*).

## ✅ Checklist hoàn thành Tuần 4

- [ ] Hoàn thành 4 buổi A/B/C/D
- [ ] Thuộc lòng bảng "PHẢI NHỚ" (3/5 controller · 2N+1 · `min(#racks, RF)` · 6 GB heap · 100.000 FD · 2000–4000 partition/broker · 100 ms · 300000 ms · 300 s · 102400)
- [ ] Vẽ lại được **từ trí nhớ** bảng *MM2 vs Cluster Linking vs stretch cluster* (8 dòng) và bảng *chi phí over-partition* (4 dòng)
- [ ] Viết lại được **từ trí nhớ** 3 chuỗi thứ tự: rolling upgrade · thêm broker + cân bằng · decommission broker
- [ ] Hoàn thành ≥6 lab (4.1–4.6; 4.7 là concept, đọc là đủ)
- [ ] Làm xong 28 câu [questions.md](questions.md), ghi sổ câu sai theo 6 nhóm chủ đề
- [ ] Trả lời trôi chảy toàn bộ 8 câu ở Cổng tự kiểm tra
- [ ] Cập nhật playbook cá nhân: thêm 6 dòng mới của tuần này vào bảng phản xạ [§7 của kế hoạch tổng](../../CCAAK-STUDY-PLAN.md#7-bảng-phản-xạ-triệu-chứng--hành-động)
