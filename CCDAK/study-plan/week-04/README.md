# 🟦 Tuần 4 — Consumer chuyên sâu: poll loop, consumer group, rebalance (classic vs `KIP-848`), offset commit, lag, share group

> **Domain CCDAK:** Application Development (28%) · **Thời lượng:** ~11h (4 buổi) · **Vị trí:** Tuần 4/10 — có 🎯 CHECKPOINT mini-mock FUND + DEV ≥70% (trộn Tuần 1→4)
>
> **Điều hướng:** [⬅️ Tuần 3](../week-03/README.md) · [🏠 Kế hoạch tổng](../../CCDAK-STUDY-PLAN.md) · [Tuần 5 ➡️](../week-05/README.md)

## 🎯 Mục tiêu tuần này

- **Phân biệt được** 2 "đồng hồ sống" của consumer: `session.timeout.ms`/`heartbeat.interval.ms` (heartbeat thread) và `max.poll.interval.ms` (processing thread) — và giải thích vì sao consumer bị kick dù heartbeat vẫn OK.
- **Giải thích được** quy trình rebalance classic (`FindCoordinator` → `JoinGroup` → `SyncGroup` → `Heartbeat`, group leader assign) và quy trình mới `KIP-848` (`ConsumerGroupHeartbeat`, broker assign, epoch).
- **Chọn đúng assignor** cho tình huống: `Range` (bẫy mất cân bằng nhiều topic), `RoundRobin`, `Sticky`, `CooperativeSticky`; phân biệt eager (stop-the-world) vs cooperative (incremental).
- **Cấu hình được** offset commit theo semantics mong muốn: auto commit (at-least-once), commit trước xử lý (at-most-once), `commitSync`/`commitAsync`, commit offset cụ thể (`offset + 1`).
- **Tự tay** scale consumer group 1→2→3→7 instance, gây rebalance, tạo duplicate/loss, reset offset bằng `kafka-consumer-groups.sh` và đọc lại theo timestamp.
- **Nhận diện** share group (`KafkaShareConsumer`, ack ACCEPT/RELEASE/REJECT, lock 30s) so với consumer group truyền thống.
- **Chốt checkpoint:** đạt **≥70%** ở MINI-MOCK FUND + DEV (~30 câu trộn Tuần 1→4) trước khi sang Tuần 5.

## 📚 Nội dung học chi tiết

### 🅰️ Buổi A — Lý thuyết (~3h)

**1. Poll loop & fetch request — consumer làm gì khi gọi `poll()`**

- Consumer Java là **pull model**: `poll(Duration timeout)` là trung tâm của mọi thứ — vừa lấy record, vừa gửi heartbeat (thread nền), vừa auto-commit, vừa tham gia rebalance. **Không gọi `poll()` đủ nhanh = consumer "chết" trong mắt group.**
- Bên dưới `poll()`, consumer gửi **Fetch request** tới **leader** của từng partition được assign (prefetch nền, có buffer). Các config điều khiển fetch:

| Config | Mặc định | Ý nghĩa |
|---|---|---|
| `fetch.min.bytes` | **1** byte | Broker chờ gom đủ bấy nhiêu byte mới trả lời → tăng lên (vd 1 MB) để giảm số request/CPU khi topic thưa |
| `fetch.max.wait.ms` | **500** ms | Broker chờ tối đa bấy nhiêu nếu chưa đủ `fetch.min.bytes` → cặp đôi với `fetch.min.bytes` (đến sớm cái nào thì trả cái đó) |
| `fetch.max.bytes` | **52428800** (50 MB) | Tối đa mỗi fetch response (không phải hard limit: batch đầu lớn hơn vẫn được trả để không kẹt) |
| `max.partition.fetch.bytes` | **1048576** (1 MB) | Tối đa mỗi partition trong 1 response; record lớn hơn vẫn trả về để consumer tiến được |
| `max.poll.records` | **500** | Số record tối đa **1 lần `poll()` trả về** cho ứng dụng — chỉ giới hạn tầng API, KHÔNG ảnh hưởng fetch bên dưới |

- ⚠️ `max.poll.records` là "van" chỉnh thời gian xử lý mỗi vòng lặp → liên quan trực tiếp tới `max.poll.interval.ms` (mục 5).
- `client.rack` (KIP-392 **follower fetching**): đặt rack của consumer trùng `broker.rack` + broker cấu hình `replica.selector.class=org.apache.kafka.common.replica.RackAwareReplicaSelector` → consumer đọc từ **replica gần nhất** (follower) thay vì leader → tiết kiệm băng thông liên AZ. Mặc định vẫn đọc từ leader.

**2. Consumer group & group coordinator**

- **Consumer group** = tập consumer cùng `group.id`; mỗi partition được giao cho **đúng 1** consumer trong group (nhưng 1 consumer có thể giữ nhiều partition). Số consumer > số partition → consumer dư **idle**.
- **Group coordinator** là 1 broker: client gửi `FindCoordinator`; broker tính `hash(group.id) % số partition của __consumer_offsets` (**50**) → broker đang là **leader** của partition đó làm coordinator cho group. Coordinator lưu offset & metadata group vào `__consumer_offsets` (compacted, RF theo `offsets.topic.replication.factor` = 3). Coordinator chết → leader mới của partition đó tiếp quản.
- `group.initial.rebalance.delay.ms` = **3000** ms: coordinator chờ 3s cho các member join cùng lúc để tránh rebalance liên tiếp khi group vừa tạo.
- Console consumer không đặt `--group` → tự sinh group ngẫu nhiên `console-consumer-<số>` → **mỗi lần chạy là group mới**, không nhớ offset.

**3. Rebalance protocol classic (`group.protocol=classic`, mặc định tới 4.x)**

1. Member gửi `JoinGroup` (kèm subscription + danh sách assignor hỗ trợ). Coordinator chọn **group leader** (thường member join đầu) và chỉ gửi **toàn bộ** subscription của group cho leader.
2. **Leader (client-side)** chạy `partition.assignment.strategy` để tính assignment → gửi `SyncGroup`. Các member khác gửi `SyncGroup` rỗng và nhận assignment từ coordinator.
3. Member gửi `Heartbeat` định kỳ; coordinator dùng heartbeat response để báo "rebalance đang diễn ra → rejoin".
- Rebalance kích hoạt khi: member join/leave/crash (hết `session.timeout.ms`), member vượt `max.poll.interval.ms`, topic subscribe thêm partition, subscription regex khớp topic mới, subscription thay đổi.
- **Assignor (client-side, classic):**

| Assignor | Cách chia | Eager / Cooperative | Bẫy đề |
|---|---|---|---|
| `RangeAssignor` (**mặc định đầu list**) | **Theo từng topic**: sort partition + consumer, chia đều, phần dư dồn cho consumer đầu | Eager | Nhiều topic → consumer đầu **luôn** nhận phần dư của mọi topic → **mất cân bằng**. Ưu điểm: co-partition (cùng partition số của nhiều topic về cùng consumer → join theo key) |
| `RoundRobinAssignor` | Gom **tất cả partition của tất cả topic** rồi chia vòng | Eager | Cân bằng hơn Range; nếu subscription các member **khác nhau** thì vẫn lệch |
| `StickyAssignor` | Cân bằng tối đa + **giữ nguyên assignment cũ** nhiều nhất có thể | Eager (vẫn revoke all) | Giảm state di chuyển nhưng vẫn stop-the-world |
| `CooperativeStickyAssignor` | Như Sticky nhưng theo protocol **cooperative** (KIP-429) | **Cooperative** | Cần **2 rolling bounce** khi chuyển từ eager assignor |

- Mặc định Kafka 4.3: `partition.assignment.strategy = [RangeAssignor, CooperativeStickyAssignor]` — group chọn assignor **đầu tiên mà mọi member đều hỗ trợ** → thực tế vẫn là **Range (eager)**. Muốn cooperative phải đặt **chỉ** `CooperativeStickyAssignor`.

**4. Eager vs cooperative (incremental) rebalance — KIP-429**

| Tiêu chí | Eager (stop-the-world) | Cooperative incremental (KIP-429) |
|---|---|---|
| Khi rebalance bắt đầu | Mọi member **revoke TẤT CẢ** partition → `onPartitionsRevoked(all)` | Member **giữ** partition, chỉ revoke phần **bị chuyển đi** |
| Số vòng rebalance | 1 | **2** (vòng 1: xác định & revoke partition cần chuyển; vòng 2: assign cho chủ mới) |
| Xử lý trong lúc rebalance | **Dừng toàn bộ** | Partition không bị chuyển **tiếp tục** xử lý |
| Assignor | Range / RoundRobin / Sticky | `CooperativeStickyAssignor` (hoặc protocol `consumer` KIP-848 — luôn incremental) |
| `ConsumerRebalanceListener` | `onPartitionsRevoked` nhận tất cả | `onPartitionsRevoked` chỉ nhận partition mất; `onPartitionsLost` khi mất không qua revoke (session timeout, fenced) |
| Nâng cấp từ eager | — | 2 rolling bounce: (1) thêm `CooperativeSticky` **bên cạnh** assignor cũ; (2) **bỏ** assignor cũ |

**5. `KIP-848` — Next Generation Consumer Rebalance Protocol (`group.protocol=consumer`)**

- Early access 3.7 → **GA 4.0**. Broker-side hoàn toàn: **không còn `JoinGroup`/`SyncGroup`**, chỉ 1 API `ConsumerGroupHeartbeat`. **Coordinator tính assignment** (không còn group leader phía client), phát tán **incremental** qua heartbeat, theo **epoch** (group epoch tăng mỗi lần group thay đổi; member epoch dùng để fence commit của member đã mất partition).
- Client config: `group.protocol=consumer` (mặc định `classic`), `group.remote.assignor` = `uniform` (mặc định, cân bằng + sticky) hoặc `range` (co-partition). Server config `group.consumer.assignors` liệt kê assignor broker hỗ trợ.
- **Bị bỏ qua / không hỗ trợ khi dùng `consumer`:** `partition.assignment.strategy`, `session.timeout.ms`, `heartbeat.interval.ms`, `enforceRebalance()`, client-side custom assignor. Thay bằng **group config phía broker** (`kafka-configs.sh --entity-type groups`): `consumer.session.timeout.ms` **45000**, `consumer.heartbeat.interval.ms` **5000**; giới hạn bởi `group.consumer.min/max.session.timeout.ms`, `group.consumer.min/max.heartbeat.interval.ms`.
- `max.poll.interval.ms` **vẫn là client config** và vẫn áp dụng.
- Migration: **offline** (dừng hết consumer, group rỗng → start lại với `consumer`, group tự đổi type) hoặc **online** (rolling: member `consumer` join → group chuyển type, member classic vẫn hoạt động nhờ lớp tương thích, miễn assignor classic không nhúng metadata tùy biến). Group type quyết định bởi **member đầu tiên** join.
- Kiểm tra: `kafka-groups.sh --list` (KIP-1043, cột `TYPE`/`PROTOCOL`), `kafka-consumer-groups.sh --list --type consumer|classic`, `--describe --state` hiện `ASSIGNMENT-STRATEGY` = `uniform`/`range`.
- Lộ trình: 4.3 (KIP-1274 phase 1) **log warning khuyến nghị bỏ classic**; **5.0** `consumer` thành mặc định; **6.0** client không còn classic. Đề mới sẽ hỏi "protocol nào loại bỏ group leader phía client?".

| Tiêu chí | Classic (`group.protocol=classic`) | Consumer / `KIP-848` (`group.protocol=consumer`) |
|---|---|---|
| Ai tính assignment | **Group leader** (1 consumer) | **Group coordinator** (broker) |
| API | `JoinGroup` + `SyncGroup` + `Heartbeat` | Chỉ `ConsumerGroupHeartbeat` |
| Kiểu rebalance | Eager (mặc định) hoặc cooperative nếu `CooperativeSticky` | **Luôn incremental**, không có synchronization barrier |
| Assignor config | `partition.assignment.strategy` (client) | `group.remote.assignor` = `uniform` / `range` (server) |
| Session/heartbeat | Client: `session.timeout.ms` 45s / `heartbeat.interval.ms` 3s | Broker group config: `consumer.session.timeout.ms` 45s / `consumer.heartbeat.interval.ms` 5s |
| Static membership | `group.instance.id` | `group.instance.id` (vẫn hỗ trợ) |
| Trạng thái | Deprecated dần (4.3 warn, 5.0 không mặc định, 6.0 gỡ) | GA từ 4.0, khuyến nghị |

**6. Static membership — KIP-345 (`group.instance.id`)**

- Mặc định member là **dynamic**: mỗi lần start được cấp `member.id` mới, `close()` gửi `LeaveGroup` → **restart = 2 rebalance** (rời + vào lại).
- Đặt `group.instance.id` duy nhất cho mỗi instance → **static member**: không gửi `LeaveGroup` khi tắt; nếu quay lại **trong `session.timeout.ms`** thì nhận lại **y nguyên** assignment cũ, **không rebalance**. Thường tăng `session.timeout.ms` (vd 5 phút) để đủ thời gian rolling restart — đổi lại phát hiện crash **chậm hơn**.
- 2 instance cùng `group.instance.id` → instance cũ bị **fence** (`FencedInstanceIdException`). Xóa static member thủ công: Admin `removeMembersFromConsumerGroup` / `kafka-consumer-groups.sh --delete` (group phải rỗng). Yêu cầu broker ≥ 2.3. Rất hợp cho Kafka Streams (state store lớn) và Kubernetes StatefulSet.

**7. Liveness: hai đồng hồ, hai thread (bẫy số 1 của tuần)**

| Cơ chế | Config | Mặc định | Thread nào | Vượt thì sao |
|---|---|---|---|---|
| Heartbeat | `heartbeat.interval.ms` | **3000** ms (nên ≤ 1/3 session) | **Heartbeat thread** nền (từ 0.10.1) | — |
| Session | `session.timeout.ms` | **45000** ms (từ 3.0; đề cũ ghi 10s); broker chặn trong `group.min.session.timeout.ms` 6000 – `group.max.session.timeout.ms` 1800000 | Coordinator đếm | Không nhận heartbeat 45s → member **chết** → rebalance |
| Poll interval | `max.poll.interval.ms` | **300000** ms (5 phút) | **Processing thread** (giữa 2 lần `poll()`) | Consumer **tự gửi `LeaveGroup`** → rebalance; commit sau đó ném `CommitFailedException` |

- ⚠️ Xử lý 1 batch quá 5 phút → heartbeat vẫn đều nhưng **vẫn bị kick** vì vượt `max.poll.interval.ms`. Sửa: **giảm `max.poll.records`**, tăng `max.poll.interval.ms`, hoặc đưa xử lý sang worker pool + `pause()`/`resume()`.
- `CommitFailedException` = "commit không thể hoàn tất vì group đã rebalance và partition đã giao cho member khác" — nguyên nhân gốc thường là vượt `max.poll.interval.ms`.

**8. Offset management**

- **Committed offset = offset của record TIẾP THEO cần đọc** = `offset cuối đã xử lý + 1`. Commit `offset` (không +1) → record cuối được xử lý **lại** khi restart.
- `enable.auto.commit=true` (mặc định) + `auto.commit.interval.ms` **5000**: commit **trong lần `poll()` kế tiếp** (và khi `close()`) offset của những record đã trả về ở poll trước → **at-least-once**: crash giữa xử lý → restart đọc lại → **duplicate**. Nếu bạn xử lý bất đồng bộ (đẩy vào thread khác rồi poll tiếp) thì auto commit có thể commit record chưa xử lý xong → **mất message**.
- Manual (`enable.auto.commit=false`):

| Cách commit | Hành vi | Khi nào dùng | Bẫy |
|---|---|---|---|
| Auto commit | Commit định kỳ trong `poll()` | Chấp nhận duplicate, code đơn giản | Không kiểm soát được; at-least-once (dup) |
| `commitSync()` | **Block** tới khi broker xác nhận; **retry** lỗi retriable | Cần chắc chắn (trước khi mất partition, khi tắt) | Chậm throughput |
| `commitAsync()` (+ callback) | Không block, **không retry** (retry có thể commit offset cũ đè offset mới → sai thứ tự) | Trong vòng lặp nóng | Kết hợp: `commitAsync` trong loop + `commitSync` trong `finally`/`onPartitionsRevoked` |
| `commitSync(Map<TP, OffsetAndMetadata>)` | Commit offset **cụ thể** theo partition | Commit giữa batch, theo record | Phải +1 |

- Semantics theo **vị trí commit**: commit **sau** xử lý → at-least-once; commit **trước** xử lý → at-most-once; exactly-once → transaction (Tuần 3) hoặc lưu offset cùng kết quả trong DB (atomic) + `seek()` lúc start.
- `auto.offset.reset` (**`latest`** mặc định / `earliest` / `none` / `by_duration:PT..`): chỉ dùng khi **không có committed offset** hoặc offset **out of range** (đã bị retention xóa). `none` → ném `NoOffsetForPartitionException`/`OffsetOutOfRangeException` cho ứng dụng tự xử lý.
- `offsets.retention.minutes` = **10080** (7 ngày): group **rỗng** quá 7 ngày → offset bị xóa → lần start sau rơi vào `auto.offset.reset`. Group đang active không bị xóa offset.
- `seek(tp, offset)`, `seekToBeginning(tps)`, `seekToEnd(tps)`, `offsetsForTimes(Map<TP, timestamp>)` → `OffsetAndTimestamp` rồi `seek` → **đọc lại theo thời gian** mà không đụng committed offset. `seek` chỉ có hiệu lực với partition **đã được assign** (gọi trong `onPartitionsAssigned` hoặc sau `poll()` đầu).
- `assign(Collection<TP>)` vs `subscribe(topics|pattern)`:

| | `subscribe()` | `assign()` |
|---|---|---|
| Group management | Có (rebalance, coordinator) | **Không** — standalone, tự chọn partition |
| Nhận partition mới tự động | Có | **Không** (tự gọi `partitionsFor()` kiểm tra) |
| Commit offset | Có (`group.id` bắt buộc) | Vẫn được nếu có `group.id`, nhưng không ai điều phối |
| Trộn lẫn | `IllegalStateException` nếu vừa subscribe vừa assign trên cùng consumer | |

- `ConsumerRebalanceListener`: `onPartitionsRevoked(tps)` → **commit offset đang giữ** trước khi mất partition (tránh dup); `onPartitionsAssigned(tps)` → `seek` nếu lưu offset ngoài Kafka; `onPartitionsLost(tps)` → đừng commit (đã bị fence).
- `isolation.level`: `read_uncommitted` (mặc định) đọc tới HW; `read_committed` chỉ đọc tới **LSO** (Last Stable Offset), bỏ record của transaction abort → lag đo với `read_committed` có thể không về 0 khi có transaction đang mở.

**9. Consumer lag & CLI**

- **Lag (per partition) = LOG-END-OFFSET − CURRENT-OFFSET (committed)**. Lag tăng đều = consumer chậm hơn producer; lag giữ nguyên = consumer chết/không commit.
- `kafka-consumer-groups.sh --describe --group g` → cột `TOPIC PARTITION CURRENT-OFFSET LOG-END-OFFSET LAG CONSUMER-ID HOST CLIENT-ID`; `--members [--verbose]`, `--state`, `--list [--type consumer|classic]`, `--delete`, `--delete-offsets`.
- `--reset-offsets` với 1 scenario: `--to-earliest` / `--to-latest` / `--to-current` / `--to-offset N` / `--shift-by ±N` / `--to-datetime YYYY-MM-DDThh:mm:ss.sss` / `--by-duration PnDTnHnMnS` / `--from-file csv`; scope `--topic t[:0,1]` hoặc `--all-topics`; chế độ mặc định là **dry-run (chỉ in)**, thêm `--execute` để áp dụng, `--export` xuất CSV. ⚠️ **Group phải INACTIVE** (không member nào) — nếu không lỗi "Assignments can only be reset if the group ... is inactive".

**10. Consumer không thread-safe → pattern đa luồng**

- `KafkaConsumer` **không thread-safe** (`ConcurrentModificationException`); phương thức duy nhất gọi được từ thread khác là **`wakeup()`** → `poll()` ném `WakeupException` để thoát vòng lặp sạch (rồi `close()` trong `finally`).
- Pattern 1 — **1 consumer / 1 thread** (đơn giản, giữ thứ tự per partition, nhưng số thread ≤ số partition; nhiều TCP connection).
- Pattern 2 — **1 consumer + worker pool**: `poll()` → giao record cho pool → **`pause(partitions)`** để `poll()` tiếp (giữ heartbeat, không lấy thêm data) → xong thì **`resume()`** và commit thủ công theo offset đã xử lý. Khó giữ thứ tự + commit phức tạp.
- Vượt số partition (cần > N consumer song song với N partition) → tăng partition hoặc dùng **share group**.

**11. Share group (Queues for Kafka, KIP-932) — GA 4.2**

| Tiêu chí | Consumer group | Share group |
|---|---|---|
| Ai đọc partition | Mỗi partition **đúng 1** consumer | **Nhiều** consumer cùng đọc 1 partition; số consumer > số partition **được phép** |
| Đơn vị giao việc | Partition (assign) | **Record** (acquire, có lock) |
| Theo dõi tiến độ | Committed offset (1 số/partition) | Trạng thái từng record: Available → **Acquired** → Acknowledged / Archived; SPSO/SPEO |
| Ack | Commit offset | `acknowledge(record, ACCEPT / RELEASE / REJECT)` (+ `RENEW` từ 4.2, KIP-1222); `share.acknowledgement.mode` = `implicit` (mặc định) / `explicit` |
| Lock | — | `group.share.record.lock.duration.ms` (group config `share.record.lock.duration.ms`) **30000** ms; hết lock → record lại Available |
| Retry | Đọc lại từ offset | `share.delivery.count.limit` **5** lần → quá thì Archived (không giao nữa) |
| Reset | `auto.offset.reset` `latest` | `share.auto.offset.reset` `latest` (earliest / by_duration) |
| Thứ tự | Giữ trong partition | **Không đảm bảo** |
| Client / CLI | `KafkaConsumer`, `kafka-consumer-groups.sh` | `KafkaShareConsumer`, `kafka-console-share-consumer.sh`, `kafka-share-groups.sh` (`--describe` cột `START-OFFSET`, `LAG`) |
| Isolation | `isolation.level` client | group config `share.isolation.level` (mặc định `read_uncommitted`) |

- Timeline nhớ: **4.0 early access → 4.1 preview → 4.2 GA**. Lệnh cũ `kafka-console-consumer.sh` **không** đọc được theo share group.

### 🅱️ Buổi B — Hands-on (~3.5h)

> 🧪 **Lab cầm tay chỉ việc (từng bước + lệnh + code):** [labs.md](labs.md). Dùng lại cluster 3 broker của Tuần 1 (`docker-compose.cluster.yml`) và alias `kt`/`kcp`/`kcc`/`kcg`.

- **Lab 4.1 ⭐ — Consumer group scaling:** topic 6 partition, chạy 1 → 2 → 3 → 7 consumer `kafkajs`; xem `kcg --describe --members --verbose` thấy 7 = 1 idle; quan sát event `GROUP_JOIN`.
- **Lab 4.2 — Eager vs cooperative vs KIP-848:** console consumer Java với `partition.assignment.strategy=CooperativeStickyAssignor` rồi `group.protocol=consumer`; đối chiếu `kafka-groups.sh --list` / `kcg --describe --state`.
- **Lab 4.3 — Commit thủ công, duplicate vs loss:** `autoCommit:false`, `eachBatch` + `resolveOffset`/`commitOffsetsIfNecessary`; crash giữa batch → duplicate; commit trước xử lý → mất message.
- **Lab 4.4 — Bẫy `max.poll.interval.ms`:** `rebalanceTimeout: 10000` + xử lý 15s → `The group is rebalancing`.
- **Lab 4.5 ⭐ — Reset offsets:** `kcg --reset-offsets --to-earliest / --shift-by -5 / --to-datetime` với `--dry-run` rồi `--execute`; thử khi group còn active để thấy lỗi.
- **Lab 4.6 — `seek` + đọc theo timestamp:** `consumer.seek`, `admin.fetchTopicOffsetsByTimestamp`; console consumer `--partition/--offset` (assign mode).
- **Lab 4.7 (tuỳ chọn) — Share group + đo lag:** `kafka-console-share-consumer.sh`, `kafka-share-groups.sh --describe`, `kcg --describe` cột LAG trong khi `kafka-producer-perf-test.sh` chạy.

### 🅲️ Buổi C — Bổ sung (~2.5h)

**Bảng quyết định 1 — "Tôi thấy triệu chứng X, config nào?"**

| Triệu chứng | Nguyên nhân | Chỉnh |
|---|---|---|
| Consumer bị kick dù log heartbeat đều | Xử lý 1 vòng poll > `max.poll.interval.ms` (5 phút) | Giảm `max.poll.records`, tăng `max.poll.interval.ms`, worker pool + `pause()` |
| Rebalance liên tục khi rolling restart | Dynamic membership: mỗi restart = leave + join | `group.instance.id` (static) + `session.timeout.ms` đủ dài; hoặc `group.protocol=consumer` |
| Rebalance làm dừng toàn bộ group vài giây | Eager assignor (Range/RoundRobin/Sticky) | `CooperativeStickyAssignor` (2 bounce) hoặc `KIP-848` |
| Consumer đầu tiên luôn nặng hơn khi subscribe 5 topic | `RangeAssignor` chia phần dư theo từng topic | `RoundRobin`/`CooperativeSticky` hoặc `group.remote.assignor=uniform` |
| Duplicate sau crash | At-least-once (commit sau xử lý / auto commit) | Idempotent consumer (Tuần 9) hoặc EOS transaction |
| Mất message sau crash | Commit trước xử lý / auto commit + xử lý async | Commit sau khi xử lý xong, `commitSync` trong `onPartitionsRevoked` |
| `CommitFailedException` | Group đã rebalance, partition không còn của mình | Xem dòng 1; commit trong `onPartitionsRevoked` |
| Quá nhiều fetch request nhỏ, CPU broker cao | `fetch.min.bytes=1` | Tăng `fetch.min.bytes` + `fetch.max.wait.ms` |
| Record 3 MB không đọc được | `max.partition.fetch.bytes` 1 MB (nhưng record lớn vẫn được trả để tiến) → thường do `message.max.bytes`/`fetch.max.bytes` phía khác | Kiểm tra `message.max.bytes` broker, `max.request.size` producer (Tuần 3) |
| Offset "biến mất" sau kỳ nghỉ 2 tuần | Group rỗng > `offsets.retention.minutes` 7 ngày | Chấp nhận `auto.offset.reset`, hoặc tăng retention, hoặc giữ group active |
| Cần đọc lại 2 giờ dữ liệu | — | `--reset-offsets --by-duration PT2H --execute` (dừng consumer) hoặc `offsetsForTimes` + `seek` |
| Cần > N consumer với N partition | Consumer group giới hạn bởi partition | Tăng partition (ảnh hưởng ordering theo key) hoặc **share group** |

**Bảng quyết định 2 — chọn cách commit**

| Yêu cầu | Chọn |
|---|---|
| Đơn giản, chịu được duplicate | Auto commit (mặc định 5s) |
| Không mất message, chấp nhận dup, throughput cao | `commitAsync` trong loop + `commitSync` khi tắt/revoke |
| Không mất message, cần chắc chắn từng batch | `commitSync` sau mỗi batch |
| Không xử lý 2 lần, chấp nhận mất | Commit trước xử lý (at-most-once) |
| Không mất, không dup | Transaction consume-process-produce (Tuần 3) hoặc offset lưu cùng kết quả trong DB + `seek` |

**Đọc thêm:** phần **Multi-threaded Processing** & **Storing Offsets Outside Kafka** trong `KafkaConsumer` javadoc; trang **Consumer Rebalance Protocol** (kafka.apache.org/43/operations); chương 4 *Kafka: The Definitive Guide* 2nd ed. (Consumers); Confluent Developer course *Consumer Group Protocol*.

### 🅳 Buổi D — Practice + Review (~2h)

> 📝 **Bộ câu hỏi luyện tập của tuần:** [questions.md](questions.md) — đáp án & giải thích: [answers.md](answers.md). *(tiếng Anh, văn phong CCDAK.)*

- Làm 28 câu của tuần; ghi sổ câu sai, phân loại: liveness / rebalance / commit / CLI / share group.
- **⭐ MINI-MOCK FUND + DEV (~30 câu, 45 phút)**: tự trộn ~8 câu Tuần 1, ~8 câu Tuần 2, ~7 câu Tuần 3, ~7 câu Tuần 4 (chọn ngẫu nhiên từ 4 file questions.md). Mục tiêu **≥70%**. Dưới 70% → ôn lại PHẢI NHỚ của tuần yếu nhất rồi làm lại bộ khác.
- **Spaced repetition:** flashcard số liệu consumer theo mốc **1 / 3 / 7 ngày** (45s / 3s / 5 phút / 500 / 5s / 7 ngày / 50 partition / 30s lock / 5 attempts).
- Chỉ sang Tuần 5 khi mini-mock **≥70%**.

## 🧠 PHẢI NHỚ tuần này

| Fact | Con số / Ghi nhớ |
|---|---|
| `session.timeout.ms` / `heartbeat.interval.ms` | **45000** ms / **3000** ms (heartbeat ≤ 1/3 session); đề cũ ghi session 10s; broker chặn 6s – 30 phút |
| `max.poll.interval.ms` | **300000** ms (5 phút) — đồng hồ của **processing thread**; vượt → tự `LeaveGroup` + `CommitFailedException` |
| `max.poll.records` | **500** record / `poll()`; giảm để rút ngắn thời gian mỗi vòng lặp |
| Fetch | `fetch.min.bytes` **1** · `fetch.max.wait.ms` **500** · `fetch.max.bytes` **50 MB** · `max.partition.fetch.bytes` **1 MB** |
| Auto commit | `enable.auto.commit` **true**, `auto.commit.interval.ms` **5000**; commit xảy ra trong lần `poll()` kế → at-least-once |
| Offset cần commit | **offset cuối đã xử lý + 1** (= vị trí record tiếp theo) |
| `commitSync` vs `commitAsync` | Sync: block + retry · Async: không block, **không retry**, có callback; kết hợp async-in-loop + sync-on-close |
| `auto.offset.reset` | **`latest`** mặc định; `earliest`; `none` → exception; `by_duration:PT..` (mới); chỉ áp dụng khi không có committed offset / out of range |
| `offsets.retention.minutes` | **10080** (7 ngày) cho group **rỗng** |
| `__consumer_offsets` | **50** partition, compacted; coordinator = leader của partition `hash(group.id) % 50` |
| `group.initial.rebalance.delay.ms` | **3000** ms |
| Assignor mặc định (classic) | `[RangeAssignor, CooperativeStickyAssignor]` → thực tế Range (eager); Range lệch khi nhiều topic |
| Cooperative rebalance | KIP-429, `CooperativeStickyAssignor`, **2 vòng**, chỉ revoke partition đổi chủ, nâng cấp = **2 rolling bounce** |
| `KIP-848` | `group.protocol=consumer`, `group.remote.assignor=uniform|range`, broker assign, `ConsumerGroupHeartbeat`, GA **4.0**; bỏ qua `session.timeout.ms`/`heartbeat.interval.ms`/`partition.assignment.strategy`; group config `consumer.session.timeout.ms` 45s / `consumer.heartbeat.interval.ms` 5s; 4.3 warn, 5.0 mặc định, 6.0 gỡ classic |
| Static membership | KIP-345 `group.instance.id`; restart trong `session.timeout.ms` → không rebalance; trùng id → `FencedInstanceIdException` |
| `assign()` vs `subscribe()` | assign = standalone, không rebalance, không tự thấy partition mới; không trộn 2 cái |
| Thread-safety | `KafkaConsumer` **không** thread-safe; chỉ `wakeup()` gọi được từ thread khác → `WakeupException` |
| `isolation.level` | `read_uncommitted` (mặc định, đọc tới HW) / `read_committed` (đọc tới LSO, lọc abort) |
| Consumer lag | **LOG-END-OFFSET − CURRENT-OFFSET**; `kcg --describe`; reset offset cần group **inactive**, mặc định dry-run, thêm `--execute` |
| Share group | GA **4.2**; `KafkaShareConsumer`; lock **30000** ms; `share.delivery.count.limit` **5**; ack ACCEPT/RELEASE/REJECT(/RENEW); nhiều consumer / partition; không giữ thứ tự |
| Follower fetching | KIP-392: `client.rack` + broker `replica.selector.class=RackAwareReplicaSelector` |
| Console consumer không `--group` | Group ngẫu nhiên `console-consumer-N`, mỗi lần chạy là group mới |

## ⚠️ Bẫy đề hay gặp

- Thấy "consumer bị loại khỏi group dù vẫn gửi heartbeat" → dễ chọn tăng `session.timeout.ms`, nhưng đúng là **vượt `max.poll.interval.ms`** → giảm `max.poll.records` / tăng `max.poll.interval.ms`.
- Thấy "xử lý xong record offset 42 thì commit gì?" → dễ chọn 42, nhưng đúng là **commit 43** (offset tiếp theo cần đọc).
- Thấy "auto commit → mất message hay duplicate?" → dễ chọn mất, nhưng mặc định (xử lý đồng bộ trong vòng poll) là **duplicate (at-least-once)**; chỉ mất khi xử lý **bất đồng bộ** hoặc commit trước xử lý.
- Thấy "`commitAsync` thất bại thì retry" → dễ chọn có, nhưng `commitAsync` **không retry** (tránh commit offset cũ đè offset mới); muốn chắc dùng `commitSync`.
- Thấy "8 consumer, topic 6 partition → throughput tăng?" → dễ chọn có, nhưng **2 consumer idle**; muốn thêm song song phải tăng partition hoặc dùng share group.
- Thấy "subscribe 3 topic × 4 partition, 3 consumer, consumer đầu luôn nhận nhiều hơn" → dễ đổ lỗi broker, nhưng đúng là **`RangeAssignor`** chia dư theo từng topic → chuyển `RoundRobin`/`CooperativeSticky`/`uniform`.
- Thấy "`CooperativeStickyAssignor` chỉ cần đổi config 1 lần rồi restart hết" → sai, cần **2 rolling bounce** (thêm bên cạnh assignor cũ → gỡ assignor cũ) nếu group đang chạy eager.
- Thấy "`group.protocol=consumer` mà vẫn đặt `partition.assignment.strategy`/`session.timeout.ms`" → tưởng có hiệu lực, nhưng **bị bỏ qua**; assignor chọn qua `group.remote.assignor`, session/heartbeat là **group config phía broker**.
- Thấy "`auto.offset.reset=earliest` nên consumer luôn đọc từ đầu" → sai, chỉ áp dụng khi **không có committed offset** (group mới / offset hết hạn / out of range).
- Thấy "reset offset bằng `kafka-consumer-groups.sh --reset-offsets --to-earliest`" mà không thấy đổi → thiếu **`--execute`** (mặc định dry-run) hoặc group **còn active**.
- Thấy "consumer 2 tuần không chạy, start lại đọc từ latest" → đúng là do **`offsets.retention.minutes` 7 ngày** xóa offset của group rỗng.
- Thấy "dùng `assign()` rồi thêm partition cho topic" → tưởng consumer tự nhận, nhưng **không**: chỉ `subscribe()` mới nhận metadata thay đổi.
- Thấy "gọi `consumer.commitSync()` từ thread khác để dừng" → sai, chỉ **`wakeup()`** thread-safe.
- Thấy "cần nhiều consumer hơn số partition, không cần thứ tự" → dễ chọn tăng partition, nhưng đáp án mới là **share group** (`KafkaShareConsumer`, GA 4.2).

## 🔁 Phản xạ nhanh (keyword → đáp án)

| Thấy từ khoá | Bật ngay |
|---|---|
| xử lý lâu, bị kick dù heartbeat OK | **`max.poll.interval.ms`** (5 phút) / giảm `max.poll.records` |
| không nhận heartbeat → coordinator loại member | **`session.timeout.ms`** 45s (heartbeat 3s) |
| `CommitFailedException` | group đã rebalance / vượt `max.poll.interval.ms` |
| stop-the-world rebalance | **eager** (Range/RoundRobin/Sticky) → chuyển **`CooperativeStickyAssignor`** / `KIP-848` |
| rebalance 2 vòng, chỉ revoke partition đổi chủ | **cooperative incremental (KIP-429)** |
| broker tính assignment, không JoinGroup/SyncGroup | **`KIP-848` `group.protocol=consumer`**, `ConsumerGroupHeartbeat` |
| `group.remote.assignor` | `uniform` (mặc định) / `range` — chỉ với protocol `consumer` |
| restart không gây rebalance | **static membership `group.instance.id`** (KIP-345) |
| consumer đầu nhận dư ở mọi topic | **`RangeAssignor`** |
| co-partition nhiều topic cùng consumer (join theo key) | `RangeAssignor` / `group.remote.assignor=range` |
| commit không block, không retry | **`commitAsync`** (+ `commitSync` khi close) |
| commit trước xử lý | **at-most-once** |
| commit sau xử lý / auto commit | **at-least-once** (duplicate) |
| offset không tồn tại / hết hạn | **`auto.offset.reset`** (`latest` mặc định) |
| đọc lại từ 1 mốc thời gian | `offsetsForTimes` + `seek` hoặc `--reset-offsets --to-datetime` |
| standalone, tự chọn partition, không group | **`assign()`** |
| lag | **LEO − committed offset**, `kafka-consumer-groups.sh --describe` |
| reset offset lỗi "inactive" | dừng hết consumer trước, nhớ `--execute` |
| chỉ đọc record đã commit transaction | **`isolation.level=read_committed`** (tới LSO) |
| đọc từ replica gần nhất | **`client.rack`** + `RackAwareReplicaSelector` (KIP-392) |
| nhiều consumer / partition, ack từng record, lock 30s | **share group / `KafkaShareConsumer`** (KIP-932) |
| dừng consumer an toàn từ thread khác | **`wakeup()`** → `WakeupException` |

## 🧪 Lab checklist

- [ ] Lab 4.1 ⭐ — Scale 1→2→3→7 consumer trên topic 6 partition, thấy 1 consumer idle qua `kcg --describe --members --verbose`.
- [ ] Lab 4.2 — Chạy console consumer với `CooperativeStickyAssignor`, rồi với `group.protocol=consumer`; xác nhận type/protocol của group qua `kafka-groups.sh --list` / `kcg --describe --state`.
- [ ] Lab 4.3 — Tạo duplicate (crash giữa batch, commit sau) và mất message (commit trước xử lý) với `autoCommit:false`.
- [ ] Lab 4.4 — Ép `rebalanceTimeout` 10s + xử lý 15s → thấy `The group is rebalancing`; sửa bằng giảm batch / tăng timeout.
- [ ] Lab 4.5 ⭐ — Reset offset `--to-earliest`, `--shift-by -5`, `--to-datetime` với `--dry-run` rồi `--execute`; thấy lỗi khi group active.
- [ ] Lab 4.6 — `consumer.seek` + `fetchTopicOffsetsByTimestamp`; console consumer `--partition 0 --offset 3` (assign mode).
- [ ] Lab 4.7 (tuỳ chọn) — Share group: 2 share consumer cùng đọc 1 partition; đo LAG khi producer perf test chạy.

## 🚪 Cổng tự kiểm tra (phải trả lời trôi chảy mới sang tuần sau)

- **Hai lý do khiến consumer bị coi là chết và config tương ứng?**
  **Đáp án gọn:** không heartbeat trong `session.timeout.ms` (45s, heartbeat thread) hoặc không `poll()` trong `max.poll.interval.ms` (5 phút, processing thread).
- **Xử lý xong record offset 99 của partition 2, commit gì để không đọc lại?**
  **Đáp án gọn:** commit `OffsetAndMetadata(100)` cho partition 2 — offset tiếp theo cần đọc.
- **Eager vs cooperative rebalance khác nhau ở đâu? Nâng cấp cần gì?**
  **Đáp án gọn:** eager revoke tất cả partition, 1 vòng, dừng toàn bộ; cooperative chỉ revoke partition đổi chủ, 2 vòng, phần còn lại tiếp tục xử lý; nâng cấp 2 rolling bounce với `CooperativeStickyAssignor`.
- **`KIP-848` thay đổi gì so với classic và bật bằng config nào?**
  **Đáp án gọn:** broker (coordinator) tính assignment qua `ConsumerGroupHeartbeat`, incremental, không group leader/JoinGroup/SyncGroup; `group.protocol=consumer` + `group.remote.assignor=uniform|range`; `session.timeout.ms`/`heartbeat.interval.ms`/`partition.assignment.strategy` bị bỏ qua.
- **Auto commit cho semantics gì, và khi nào nó gây mất message?**
  **Đáp án gọn:** at-least-once (duplicate khi crash) vì commit ở lần `poll()` kế; mất message khi xử lý bất đồng bộ (record chưa xong đã bị commit) hoặc commit trước xử lý.
- **Muốn consumer group đọc lại từ 2 giờ trước bằng CLI thì làm gì?**
  **Đáp án gọn:** dừng toàn bộ consumer (group inactive) → `kafka-consumer-groups.sh --reset-offsets --group g --topic t --by-duration PT2H --execute` (hoặc `--to-datetime`).
- **Khi nào chọn share group thay consumer group?**
  **Đáp án gọn:** cần nhiều consumer hơn số partition, xử lý từng record kiểu queue có ack/retry, không cần thứ tự; `KafkaShareConsumer`, lock 30s, tối đa 5 lần giao.
- **⭐ CHECKPOINT:** đã đạt **≥70%** ở MINI-MOCK FUND + DEV (~30 câu trộn Tuần 1→4) chưa? Nếu chưa → **KHÔNG** sang Tuần 5, ôn lại câu sai trước.

## 📎 Tài nguyên tuần này

> 📂 **Đã crawl sẵn tài liệu chính thức vào** [`resources/`](resources/INDEX.md) — đọc offline được.

- Apache Kafka Docs 4.3: *Consumer Configs* (`kafka.apache.org/43/generated/consumer_config.html`), *Group Configs* (`consumer.session.timeout.ms`, `share.*`), *Operations → Consumer Rebalance Protocol* (KIP-848), *Basic Kafka Operations → Managing Consumer Groups / Managing Share Groups*.
- Apache Kafka Javadoc 4.3: `KafkaConsumer` (Offsets and Consumer Position, Detecting Consumer Failures, Manual Offset Control, Multi-threaded Processing), `KafkaShareConsumer`, `ConsumerRebalanceListener`.
- KIP: **KIP-848** (Next Generation Consumer Rebalance Protocol), **KIP-429** (Incremental Cooperative Rebalancing), **KIP-345** (Static Membership), **KIP-392** (Follower Fetching), **KIP-932** (Queues for Kafka), KIP-1274 (deprecate classic protocol, phase 1 ở 4.3).
- Confluent Docs: *Kafka Consumer* (`docs.confluent.io/platform/current/clients/consumer.html`) — consumer group protocol, migration classic → consumer.
- Confluent Developer (free): course *Apache Kafka Architecture* → module **Consumer Group Protocol**; course *Apache Kafka 101* → Consumers.
- Khoá học: Stephane Maarek — *Apache Kafka Series: Learn Apache Kafka for Beginners* (mục Consumer Groups, Offsets, Delivery Semantics) + *Kafka Streams/Confluent Certified Developer practice exams*.
- Sách: *Kafka: The Definitive Guide* 2nd ed. — Chương 4 *Kafka Consumers: Reading Data from Kafka* (poll loop, commit, rebalance listener, seek, standalone consumer).

## ✅ Checklist hoàn thành Tuần 4

- [ ] Hoàn thành 4 buổi A/B/C/D
- [ ] Thuộc lòng bảng "PHẢI NHỚ" (45s / 3s / 5 phút / 500 / 5s / 7 ngày / 50 / 30s / 5)
- [ ] Vẽ lại được từ trí nhớ 2 sơ đồ: classic (`JoinGroup`/`SyncGroup`) và `KIP-848` (`ConsumerGroupHeartbeat`)
- [ ] Hoàn thành ≥6 lab (4.1–4.6; 4.7 tuỳ chọn)
- [ ] Làm xong 28 câu questions.md, ghi sổ câu sai
- [ ] **Đạt ≥70% MINI-MOCK FUND + DEV (~30 câu, Tuần 1→4)** — CHECKPOINT
- [ ] Vượt Cổng tự kiểm tra
