# 🛠️ Tuần 3 — Cluster Config II: replication & durability, quotas, throughput + JVM/OS tuning

> **Domain CCAAK:** Apache Kafka Cluster Configuration (22%) · **Thời lượng:** ~11h (4 buổi) · **Vị trí:** Tuần 3/8 — có 🎯 **CHECKPOINT mini-mock CFG ≥70%** (trộn Tuần 2 + Tuần 3)
>
> **Điều hướng:** [⬅️ Tuần 2](../week-02/README.md) · [🏠 Kế hoạch tổng](../../CCAAK-STUDY-PLAN.md) · [Tuần 4 ➡️](../week-04/README.md)

## 🔁 Ôn nhanh từ CCDAK (~20 phút)

| Khái niệm | File CCDAK cần đọc lại | Vì sao cần cho tuần này |
|---|---|---|
| ISR, high watermark, `acks` × `min.insync.replicas` | [`week-02/resources/kafka-replication-isr.md`](../../../CCDAK/study-plan/week-02/resources/kafka-replication-isr.md) | Tuần này **không** học lại định nghĩa ISR mà lập **ma trận quyết định** RF × min.isr × acks và tự tay gây `NotEnoughReplicasException`. Vào lab mà chưa thuộc "committed = mọi replica trong ISR đã nhận" thì đọc bảng nào cũng vô nghĩa. |
| ELR (Eligible Leader Replicas) | [`week-02/resources/kafka-eligible-leader-replicas.md`](../../../CCDAK/study-plan/week-02/resources/kafka-eligible-leader-replicas.md) | CCDAK chỉ giới thiệu khái niệm. Tuần này **bật thật** `eligible.leader.replicas.version=1`, đọc cột `Elr:` và học **thứ tự bầu leader** — dạng câu list-order của CCAAK. |
| `acks`, idempotence phía producer | [`week-03/README.md`](../../../CCDAK/study-plan/week-03/README.md) (mục producer configs) | Admin phải giải thích được vì sao `acks=1` **vô hiệu hoá** `min.insync.replicas`, và vì sao batch/linger của client lại đổi tải trên broker. |
| Metric broker & JMX | [`week-08/resources/kafka-monitoring-broker-metrics.md`](../../../CCDAK/study-plan/week-08/resources/kafka-monitoring-broker-metrics.md) | Tuần này dùng metric làm **tín hiệu tuning** (`RequestHandlerAvgIdlePercent`, `UnderMinIsrPartitionCount`, `throttle-time`), chưa phải dựng alerting — việc đó để Tuần 7. |
| Reassignment & throttle | [`week-08/resources/kafka-basic-ops-reassignment.md`](../../../CCDAK/study-plan/week-08/resources/kafka-basic-ops-reassignment.md) | Nền cho phần `num.replica.fetchers` và 4 config `*.replication.throttled.*` — Tuần 3 chỉ dùng ở mức "làm URP về 0 nhanh hơn". |
| Cluster Docker 3 broker | [`week-01/labs.md`](../../../CCDAK/study-plan/week-01/labs.md) (Lab 1.2) | Toàn bộ 7 lab tuần này chạy trên đúng cluster đó: `controller` + `kafka-1/2/3`, host port 9092/9094/9096. |

## 🎯 Mục tiêu tuần này

- **Lập được từ trí nhớ** ma trận `acks` × `min.insync.replicas` × RF và trả lời tức thì: mất 0 / 1 / 2 broker thì **còn ghi được không** và **có mất dữ liệu không**.
- **Chẩn đoán và khôi phục được** sự cố min-ISR: phân biệt `NotEnoughReplicasException` với `NotEnoughReplicasAfterAppendException`, biết hành động đúng là **khôi phục replica** chứ không phải hạ `min.insync.replicas`, và tự tay sửa một cluster bị đặt `min.insync.replicas=3` (over-correction) về **2** mà không restart broker nào.
- **Bật và đọc được ELR**: `eligible.leader.replicas.version=1`, cột `Elr:` / `LastKnownElr:`, và giải thích thứ tự bầu **ISR → ELR → last known leader** so với `unclean.leader.election.enable`.
- **Thiết kế được quota** cho một tenant: chọn đúng 1 trong 4 loại quota, đặt đúng 1 trong **8 mức ưu tiên**, và **chứng minh bằng metric** rằng throttle đang xảy ra dù log hoàn toàn sạch.
- **Tính được** ảnh hưởng của `num.replica.fetchers`, `replica.fetch.max.bytes`, `compression.type=producer` lên thời gian URP về 0 và lên CPU broker.
- **Quyết định được** heap broker và tham số OS: vì sao **6 GB + G1GC** chứ không phải "heap càng to càng tốt", và 4 con số OS phải chỉnh (fd **100000**, `vm.swappiness` **1**, `vm.max_map_count`, XFS).
- **Chốt checkpoint:** đạt **≥70%** ở MINI-MOCK CFG (~30 câu trộn Tuần 2 + Tuần 3) trước khi sang Tuần 4.

## 📚 Nội dung học chi tiết

### 🅰️ Buổi A — Lý thuyết (~3h)

**1. Durability: ba núm vặn và một ma trận**

Ba thứ quyết định "cluster này chịu mất mấy broker mà không mất dữ liệu": **replication factor** (bao nhiêu bản sao), **`min.insync.replicas`** (tối thiểu bao nhiêu bản sao phải xác nhận), **`acks`** phía producer (client có chờ hay không). Thiếu một trong ba thì hai cái kia vô nghĩa.

Quy tắc gốc từ docs: *committed message* = message đã tới **tất cả replica đang trong ISR**. `acks=all` nghĩa là chờ **mọi replica ĐANG trong ISR** — **không** phải mọi replica được gán. Vì thế topic RF=2 mất 1 broker thì `acks=all` **vẫn thành công** (ISR còn 1), và ghi đó sẽ mất nếu replica cuối cũng chết. `min.insync.replicas` sinh ra chính để chặn tình huống đó — và nó **chỉ có tác dụng khi `acks=all`**.

> 📊 **Bảng 1 — Ma trận `acks` × `min.insync.replicas` × RF** (cluster 3 broker, mỗi partition 3 replica trừ dòng cuối)

| RF | `min.isr` | `acks` | Mất **0** broker | Mất **1** broker | Mất **2** broker | Có mất dữ liệu đã ack? |
|---|---|---|---|---|---|---|
| 3 | 1 | `all` | ✅ ghi được | ✅ ghi được | ✅ ghi được (ISR = 1) | **Có** — ack khi chỉ còn 1 bản, bản đó chết là mất |
| **3** | **2** | **`all`** | ✅ ghi được | ✅ **ghi được** | ❌ `NotEnoughReplicas` | **Không** — luôn ≥ 2 bản. ⭐ **Bộ ba production** |
| 3 | 3 | `all` | ✅ ghi được | ❌ `NotEnoughReplicas` | ❌ `NotEnoughReplicas` | Không, nhưng **over-correction**: mất 1 broker là ngừng ghi |
| 3 | 2 | `1` | ✅ ghi được | ✅ ghi được | ✅ ghi được | **Có** — `min.isr` **bị bỏ qua hoàn toàn** khi `acks≠all` |
| 3 | 2 | `0` | ✅ ghi được | ✅ ghi được | ✅ ghi được | **Có** — không chờ ack nào, mất cả khi leader bận |
| 2 | 2 | `all` | ✅ ghi được | ❌ `NotEnoughReplicas` | — | Không, nhưng availability chỉ bằng RF=3/min.isr=3 |
| 1 | 1 | `all` | ✅ ghi được | ❌ partition **offline** | — | **Có** — không có bản sao nào |

- Đọc bảng theo chiều dọc: **`min.insync.replicas` mua durability bằng availability.** `RF − min.isr` = số broker được phép chết mà **vẫn ghi được**. RF 3 / min.isr 2 → `3 − 2 = 1`.
- Đây là câu hỏi **lặp lại nhiều lần** trong đề dưới nhiều lớp vỏ: "cần chịu được mất 1 broker mà không mất dữ liệu", "cần vừa durable vừa còn ghi được", "min.isr nên là bao nhiêu với RF=3". Đáp án luôn là **2**.
- ⚠️ Tăng `min.insync.replicas` **không** cứu được cluster đang có sự cố — nó chỉ làm cluster **ngừng ghi sớm hơn**. Hành động cứu là khôi phục replica.

**2. Hai exception dễ nhầm**

| Exception | Xảy ra khi nào | Ý nghĩa với dữ liệu |
|---|---|---|
| `NotEnoughReplicasException` | Leader kiểm tra **TRƯỚC khi append**: `\|ISR\| < min.insync.replicas` | Record **chưa được ghi** vào log. Producer retry an toàn. |
| `NotEnoughReplicasAfterAppendException` | Leader **đã append vào log của mình** rồi ISR mới co xuống dưới ngưỡng | Record **đã nằm trong log leader** nhưng chưa committed. Producer retry → **có thể sinh bản ghi trùng** nếu không bật idempotence. |

Cả hai đều là **retriable**; producer mặc định (`enable.idempotence=true`, `acks=all`) sẽ tự retry. Điều đề muốn nghe không phải "sửa producer" mà **"khôi phục replica để ISR về đủ"**.

**3. ISR, `replica.lag.time.max.ms` và high watermark**

- Broker rời ISR khi (a) mất session với controller (`broker.session.timeout.ms` **9000** ms) hoặc (b) không fetch kịp trong **`replica.lag.time.max.ms` = 30000** ms. Đây là ngưỡng **theo thời gian**, và nó là **`read-only`** → đổi phải restart broker.
- `replica.fetch.wait.max.ms` (**500**) phải **luôn nhỏ hơn** `replica.lag.time.max.ms`, nếu không topic ít traffic sẽ ISR co giãn liên tục.
- **High watermark** = offset cao nhất mà **mọi replica trong ISR** đã có. Consumer chỉ đọc tới HW. Với quy tắc **strict min ISR**, HW **không tiến** khi `|ISR| < min.insync.replicas` → đây chính là nền tảng để ELR hoạt động.
- ISR flapping (`IsrShrinksPerSec`/`IsrExpandsPerSec` dao động) → nghi **GC pause** và **disk latency** trước. Docs Confluent hướng dẫn chọn `replica.lag.time.max.ms` theo `MinFetchRate`: nếu tốc độ là `n` thì đặt lớn hơn `1/n × 1000` — tức là **đo trước, chỉnh sau**.

**4. `unclean.leader.election.enable` — lựa chọn cuối cùng**

- Mặc định **`false`** từ 0.11.0.0. Bật = cho replica **ngoài ISR** lên làm leader → partition sống lại nhưng **log của nó thành nguồn sự thật** → **mất mọi message nó chưa kịp nhận**.
- Trong KRaft, bật động (`cluster-wide`) thì phải chờ **unclean leader election thread chạy định kỳ (mặc định 5 phút)**; muốn ngay thì chạy `kafka-leader-election.sh` với option unclean.
- Phạm vi: đặt cluster-wide bằng `kafka-configs.sh --entity-type brokers --entity-default`, hoặc **chỉ cho một topic** bằng `--entity-type topics --entity-name <t>`. Trong đề, "chỉ một topic phi quan trọng cần sống lại" → **topic-level**, không bật toàn cluster.
- Metric xác nhận thiệt hại: `UncleanLeaderElectionsPerSec` — khác 0 nghĩa là **đã mất dữ liệu**.

**5. ELR — KIP-966, cách giảm số lần phải dùng unclean election**

> 📊 **Bảng 2 — ELR vs unclean leader election**

| Tiêu chí | **ELR** (KIP-966) | **Unclean leader election** |
|---|---|---|
| Replica được bầu | Ngoài ISR **nhưng chắc chắn có đủ message đã commit** (nhờ strict min ISR) | Bất kỳ replica nào sống lại, **không đảm bảo gì** |
| Mất dữ liệu | **Không** | **Có** |
| Bật bằng | `eligible.leader.replicas.version=1` (mặc định cho cluster **mới** từ **4.1**) | `unclean.leader.election.enable=true` (mặc định **false**) |
| Nhìn thấy ở đâu | Cột **`Elr:`** / **`LastKnownElr:`** trong `kafka-topics.sh --describe` | Metric `UncleanLeaderElectionsPerSec` > 0 |
| Metric riêng | `ElectionFromEligibleLeaderReplicasPerSec` (kỳ vọng 0) | `UncleanLeaderElectionsPerSec` (kỳ vọng 0) |
| Khi nào vô dụng | ISR **và** ELR đều rỗng, last known leader cũng offline | — (đây là lúc buộc phải dùng unclean) |

- **Thứ tự bầu leader khi ELR bật** (thuộc lòng — dạng list-order): **① ISR nếu không rỗng → ② ELR (chọn replica chưa fenced) → ③ last known leader nếu unfenced.**
- Khi bật ELR, `min.insync.replicas` **chuyển hẳn về cluster level**: broker-level bị gỡ và **không được sửa**; sửa cluster-level (kể cả đặt lại đúng giá trị cũ) → **toàn bộ ELR state bị xoá**.

**6. Durability của internal topic — chỗ hay quên**

| Config | Mặc định | Ý nghĩa | Bẫy |
|---|---|---|---|
| `offsets.topic.replication.factor` | **3** | RF của `__consumer_offsets` (50 partition) | Cluster **1 broker** phải hạ về **1**, nếu không topic không tạo được |
| `transaction.state.log.replication.factor` | **3** | RF của `__transaction_state` (50 partition) | Như trên |
| `transaction.state.log.min.isr` | **2** | `min.insync.replicas` riêng cho `__transaction_state` | Cluster 1–2 broker phải hạ về **1** |
| `share.coordinator.state.topic.replication.factor` | 3 | RF cho state topic của share group | Như trên |

Cả bốn đều **`read-only`** → **phải restart broker** để đổi, và chúng **chỉ áp dụng lúc topic internal được tạo lần đầu**. Đây là lý do lỗi kinh điển khi dựng cluster lab 1 broker: broker start OK nhưng consumer đầu tiên chết vì không tạo được `__consumer_offsets`.

**7. Quotas — 4 loại, 8 mức, một cơ chế**

| Loại quota | Config | Giới hạn cái gì | Đơn vị |
|---|---|---|---|
| Network bandwidth (produce) | `producer_byte_rate` | Byte/s ghi vào **mỗi broker** | bytes/sec/broker |
| Network bandwidth (consume) | `consumer_byte_rate` | Byte/s đọc ra từ **mỗi broker** | bytes/sec/broker |
| Request rate | `request_percentage` | % thời gian của **một** thread; trần = `(num.io.threads + num.network.threads) × 100`% | % (200 = 2 thread) |
| Controller mutation (KIP-599) | `controller_mutation_rate` | Tốc độ **tạo/xoá topic, thêm partition** | mutation/sec |

> 📊 **Bảng 3 — 8 mức ưu tiên quota** (nguyên văn docs, lấy mức khớp **cụ thể nhất**)

| # | Mức | Lệnh `kafka-configs.sh` tương ứng |
|---|---|---|
| 1 | matching user **and** client-id | `--entity-type users --entity-name u --entity-type clients --entity-name c` |
| 2 | matching user **and default** client-id | `--entity-type users --entity-name u --entity-type clients --entity-default` |
| 3 | matching user | `--entity-type users --entity-name u` |
| 4 | **default user** and matching client-id | `--entity-type users --entity-default --entity-type clients --entity-name c` |
| 5 | **default user** and **default** client-id | `--entity-type users --entity-default --entity-type clients --entity-default` |
| 6 | **default user** | `--entity-type users --entity-default` |
| 7 | matching client-id | `--entity-type clients --entity-name c` |
| 8 | **default** client-id | `--entity-type clients --entity-default` |

- Mẹo nhớ: **user thắng client-id ở mọi cấp**; trong cùng cấp, **`--entity-name` thắng `--entity-default`**. Bốn mức đầu có user cụ thể hoặc default user, ba mức cuối là client-id "trơ trọi".
- **Cơ chế throttle:** broker tính độ trễ cần thiết, **trả response ngay kèm `throttle_time_ms`** rồi **mute socket channel** cho tới hết thời gian đó. **KHÔNG có exception nào được ném ra.** Với fetch request, response trả về **rỗng data**.
- ⇒ Triệu chứng kinh điển trong đề: **"throughput bị chặn trần, log broker và log client đều sạch"** → nghĩ ngay tới quota, kiểm `produce-throttle-time-avg` (client) hoặc MBean `kafka.server:type=Produce,user=...,client-id=...` thuộc tính `throttle-time` (broker).
- **Quota là per-broker.** `producer_byte_rate=10485760` trên cluster 6 broker ⇒ client có thể đạt **60 MB/s** toàn cluster. Đề rất hay hỏi phép nhân này.
- Quota ghi vào **metadata log**, **hiệu lực ngay, không cần restart**. Mặc định **client không có quota** (unlimited) — quota chỉ tồn tại khi admin tạo.
- Cửa sổ đo: `quota.window.num` **11** mẫu × `quota.window.size.seconds` **1** giây.

**8. Throughput tuning nhìn từ broker**

> 📊 **Bảng 4 — Triệu chứng hiệu năng → config cần chỉnh**

| Triệu chứng đo được | Nguyên nhân | Config chỉnh | Restart? |
|---|---|---|---|
| `RequestHandlerAvgIdlePercent` < 0.3, CPU chưa bão hoà | Thiếu I/O thread | `num.io.threads` (8) | ❌ `cluster-wide` |
| `NetworkProcessorAvgIdlePercent` < 0.3 | Thiếu network thread | `num.network.threads` (3) | ❌ `cluster-wide` |
| URP > 0 lâu sau khi broker đã sống lại | 1 fetcher thread không đủ | **`num.replica.fetchers`** (1 → 4) | ❌ `cluster-wide` |
| Follower fetch nhiều vòng nhỏ với message lớn | `replica.fetch.max.bytes` 1 MiB quá nhỏ | `replica.fetch.max.bytes` / `replica.fetch.response.max.bytes` (10 MiB) | ✅ `read-only` |
| CPU broker cao bất thường, `BytesInPerSec` không tăng | Broker đang **recompress** | `compression.type=producer` (mặc định) | ❌ `cluster-wide` |
| `RemoteTimeMs` (Produce) cao, các pha khác thấp | Chờ follower ack | **Bình thường với `acks=all`** — kiểm follower, không chỉnh thread | — |
| Nhiều request rất nhỏ, broker tốn CPU | Client không batch | Phía client: `batch.size`, `linger.ms` (mặc định 5 ms ở 4.x) | — |
| `throttle-time` > 0 | Quota | Nâng quota hoặc giảm tốc client | ❌ hiệu lực ngay |
| GC pause dài, ISR flapping | Heap quá to | `KAFKA_HEAP_OPTS` về **6 GB** + G1GC | ✅ restart broker |

- `num.replica.fetchers` là **cách rẻ nhất, đảo ngược được** để kéo URP về 0 nhanh. Docs ghi rõ: tổng fetcher trên mỗi broker = `num.replica.fetchers × số broker`; tăng thì tăng song song I/O nhưng **tốn CPU và bộ nhớ**.
- `compression.type=producer` ở broker = **giữ nguyên codec của producer**. Đặt giá trị khác buộc broker **giải nén rồi nén lại** từng batch → tốn CPU và **phá zero-copy** khi gửi cho consumer.
- Batch/linger nằm phía client nhưng **tải rơi vào broker**: batch nhỏ ⇒ nhiều request ⇒ `RequestHandlerAvgIdlePercent` tụt. Admin không sửa được code client thì dùng **`request_percentage` quota** để bảo vệ cluster.

**9. JVM & OS tuning**

- **Heap 6 GB, G1GC.** Bộ flag chính thức trong docs: `-Xmx6g -Xms6g -XX:MetaspaceSize=96m -XX:+UseG1GC -XX:MaxGCPauseMillis=20 -XX:InitiatingHeapOccupancyPercent=35 -XX:G1HeapRegionSize=16M -XX:MinMetaspaceFreeRatio=50 -XX:MaxMetaspaceFreeRatio=80`. `-Xms` = `-Xmx` để heap cố định.
- **Vì sao heap lớn có hại:** Kafka **không giữ dữ liệu trong heap** — nó ghi vào **page cache của OS** rồi để OS flush. Heap to = page cache nhỏ = đọc phải chạm đĩa; đồng thời GC pause dài = follower trễ = **ISR flapping**. Confluent nói thẳng: heap **không cần quá 6 GB**, máy 32 GB sẽ có **28–30 GB page cache**.
- Số tham chiếu LinkedIn với đúng bộ flag đó: **60 broker, 50k partition (RF 2), 800k msg/s, 300 MB/s vào — 1 GB/s+ ra**, GC pause **p90 ≈ 21 ms**, **< 1 young GC/giây**.
- **OS — 4 con số phải nhớ:**
  - **File descriptor ≥ 100000** (distro thường mặc định 1024 — quá thấp).
  - **`vm.swappiness = 1`** — rất thấp nhưng **khác 0**, vì 0 là bỏ luôn lưới an toàn OOM.
  - **`vm.max_map_count`** ~65535 mặc định; mỗi log segment tốn **2 map area** → **50000 partition ⇒ 100000 map area ⇒ broker crash `OutOfMemoryError (Map failed)`**. Confluent khuyên đặt **262144**.
  - **Filesystem XFS** (Request Local Time **160 ms** vs **250 ms+** của EXT4 tốt nhất), mount `noatime`.
- **Tách ổ đĩa**: không dùng chung ổ Kafka với application log hay hoạt động filesystem của OS. Nhiều `log.dirs` → partition gán **round-robin theo thư mục**, mỗi partition nằm trọn trong một thư mục.
- Giữ **mặc định tắt application fsync** — "durability in Kafka does not require syncing data to disk, as a failed node will always recover from its replicas".

### 🅱️ Buổi B — Hands-on (~3.5h)

> 🧪 **Lab cầm tay chỉ việc (từng bước + lệnh + kết quả mong đợi):** [labs.md](labs.md). Dùng lại cluster 3 broker của [CCDAK Tuần 1 — Lab 1.2](../../../CCDAK/study-plan/week-01/labs.md) (`docker-compose.cluster.yml`) và alias `kt`/`kcp`/`kcc`/`kcg`/`kcfg`.

- **Lab 3.1 ⭐ — Ma trận durability (gây hỏng rồi sửa):** topic RF=3 / `min.isr=2`, tắt lần lượt 1 rồi 2 broker, thử `acks=all` và `acks=1`, **lập bảng kết quả thực nghiệm** rồi đối chiếu Bảng 1.
- **Lab 3.2 — Over-correction `min.isr=3` (gây hỏng rồi sửa):** đặt `min.insync.replicas=3`, tắt 1 broker → ngừng ghi ngay, đọc `NotEnoughReplicasException`, rồi sửa về 2 **không restart broker nào**.
- **Lab 3.3 — ELR:** bật `eligible.leader.replicas.version=1`, đọc cột `Elr:` / `LastKnownElr:`, mô phỏng ISR co về 1 và quan sát ELR được điền.
- **Lab 3.4 ⭐ — Quota bandwidth + mức ưu tiên:** đặt `producer_byte_rate` cho user, chạy `kafka-producer-perf-test.sh` thấy throughput bị kìm **mà không có lỗi**, đọc `throttle-time` / `produce-throttle-time-avg`; thêm quota `(user, client-id)` để **chứng minh mức 1 thắng mức 3**.
- **Lab 3.5 — `num.replica.fetchers`:** tắt 1 broker đủ lâu, bật lại, **đo thời gian URP về 0** với 1 fetcher rồi với 4 fetcher.
- **Lab 3.6 — JVM & page cache:** xem heap và GC của broker qua `/proc`/`jcmd`, đổi `KAFKA_HEAP_OPTS`, quan sát page cache bằng `/proc/meminfo` trong container.
- **Lab 3.7 — `request_percentage` quota:** đặt quota CPU cho một client, đọc MBean `kafka.server:type=Request,...` với `throttle-time` + `request-time`.

### 🅲️ Buổi C — Bổ sung (~2.5h)

**Bảng quyết định — "Yêu cầu nghiệp vụ nói thế này, tôi đặt config gì?"**

| Yêu cầu nghe được từ đề | Cấu hình đúng |
|---|---|
| "Không mất dữ liệu **và** vẫn ghi được khi mất 1 broker" | RF **3** + `min.insync.replicas` **2** + `acks=all` |
| "Không mất dữ liệu, chấp nhận ngừng ghi khi mất 1 broker" | RF 3 + `min.isr` **3** (hiếm; thường là bẫy) |
| "Ưu tiên uptime, chấp nhận mất dữ liệu" | `unclean.leader.election.enable=true` **ở topic đó**, không toàn cluster |
| "Giảm khả năng phải bật unclean election" | Bật **ELR** (`eligible.leader.replicas.version=1`) |
| "Một tenant đang bóp nghẹt cluster bằng băng thông" | `producer_byte_rate` / `consumer_byte_rate` ở mức **user** |
| "Một tenant tạo/xoá topic liên tục làm controller nghẽn" | **`controller_mutation_rate`** (KIP-599) |
| "Một client gửi hàng vạn request bé, CPU broker cháy" | **`request_percentage`** — hiệu quả hơn bandwidth quota |
| "Áp trần cho **mọi** client chưa khai báo" | `--entity-type clients --entity-default` (mức **8**) |
| "Broker mới vừa join, URP mãi không về 0" | Tăng **`num.replica.fetchers`** (không cần restart) |
| "Produce latency tăng gấp 3, `RequestHandlerAvgIdlePercent` 0.08" | Tăng **`num.io.threads`** (không cần restart) |
| "Broker GC pause 2 giây, ISR flapping" | Heap về **6 GB** + G1GC, **restart** broker |
| "Broker crash `OutOfMemoryError (Map failed)` khi lên 40k partition" | **`vm.max_map_count`** (lên 262144), không phải heap |
| "Too many open files" trong `server.log` | **`ulimit -n` ≥ 100000** |

**Bảng quyết định — đổi nóng hay phải restart?**

| Config | Update Mode | Cách đổi |
|---|---|---|
| `min.insync.replicas` | **cluster-wide** (và override ở topic) | `kafka-configs.sh --entity-type brokers --entity-default` hoặc `--entity-type topics` |
| `unclean.leader.election.enable` | **cluster-wide** | Đổi nóng, nhưng phải chờ thread định kỳ **5 phút** hoặc chạy `kafka-leader-election.sh` |
| `num.replica.fetchers`, `num.io.threads`, `num.network.threads`, `background.threads`, `compression.type`, `message.max.bytes` | **cluster-wide** | `kafka-configs.sh --alter --entity-type brokers --entity-default` |
| Quota (`producer_byte_rate`, …) | Ghi vào **metadata log** | `kafka-configs.sh --entity-type users/clients`, hiệu lực **ngay** |
| `replica.lag.time.max.ms`, `auto.leader.rebalance.enable`, `leader.imbalance.check.interval.seconds`, `replica.fetch.*.bytes`, `queued.max.requests`, `offsets.topic.replication.factor`, `transaction.state.log.*` | **read-only** | **Phải restart broker** (rolling restart) |
| `KAFKA_HEAP_OPTS`, `ulimit`, `vm.swappiness`, filesystem | Ngoài Kafka | Restart broker / sysctl / mount lại |

**Đọc thêm:** trang [*Eligible Leader Replicas*](resources/kafka-eligible-leader-replicas.md) đọc cùng phần **Availability and Durability Guarantees** trong [*Design → Replication*](resources/kafka-design-replication.md); phần **Enforcement** trong [*Design → Quotas*](resources/kafka-design-quotas.md) để hiểu vì sao không có exception; chương 6 (*Reliable Data Delivery*) và 12 (*Administering Kafka*) — *Kafka: The Definitive Guide* 2nd ed.

### 🅳 Buổi D — Practice + Review (~2h)

> 📝 **Bộ câu hỏi luyện tập của tuần:** [questions.md](questions.md) — đáp án & giải thích: [answers.md](answers.md). *(tiếng Anh, văn phong CCAAK.)*

- Làm **30 câu** của tuần; ghi sổ câu sai, phân loại theo 5 nhóm: **durability / ELR & leader election / quota / throughput tuning / JVM-OS**.
- **⭐ CHECKPOINT — MINI-MOCK CFG (~30 câu, 45 phút):** tự trộn **~15 câu Tuần 2** (broker config theo nhóm, `log.dirs`/JBOD, segment, retention, compaction, message size) + **~15 câu Tuần 3** (durability, quota, tuning, JVM/OS), chọn ngẫu nhiên từ hai file `questions.md`. Chấm theo đúng thang CCAAK: **mục tiêu ≥70%**.
  - **≥70%** → đủ điều kiện sang Tuần 4.
  - **60–69%** → ôn lại **PHẢI NHỚ** của tuần yếu hơn + làm lại lab tương ứng, mock lại bằng bộ trộn khác.
  - **<60%** → học lại Buổi A của cả Tuần 2 và Tuần 3, **không** sang Tuần 4.
- **Spaced repetition:** flashcard con số theo mốc **1 / 3 / 7 ngày** — `30000` · `2` · `3` · `8` / `3` · `0.3` · `300` · `11 × 1s` · `6 GB` · `100000` · `1`.
- Vẽ lại từ trí nhớ **Bảng 1 (ma trận durability)** và **Bảng 3 (8 mức quota)** trên giấy trắng. Không vẽ được = chưa qua cổng.

## 🧠 PHẢI NHỚ tuần này

| Fact | Con số / Ghi nhớ |
|---|---|
| Bộ ba production | **RF 3 + `min.insync.replicas` 2 + `acks=all`** → chịu mất **đúng 1** broker, không mất dữ liệu. Công thức: số broker được phép chết mà vẫn ghi được = **`RF − min.insync.replicas`** |
| Mặc định durability | `min.insync.replicas` **1** (`cluster-wide`) · `default.replication.factor` **1** — mặc định của Kafka **KHÔNG** an toàn; min.isr chỉ có tác dụng khi **`acks=all`** |
| 2 exception min.isr | `NotEnoughReplicas` (**trước** append) · `NotEnoughReplicasAfterAppend` (**sau** append, có thể sinh trùng) |
| Đồng hồ ISR | `replica.lag.time.max.ms` **30000** ms (ngưỡng duy nhất loại follower khỏi ISR, **`read-only`**) · `broker.session.timeout.ms` **9000** ms (KRaft coi broker offline) · `replica.fetch.wait.max.ms` **500** ms phải **luôn nhỏ hơn** 30000 |
| `unclean.leader.election.enable` | **false**; bật động phải chờ thread **5 phút** hoặc chạy `kafka-leader-election.sh` |
| ELR | KIP-966; bật `eligible.leader.replicas.version=1`; mặc định cho cluster **mới** từ **4.1**; cột `Elr:` / `LastKnownElr:` |
| Thứ tự bầu leader (ELR bật) | **ISR → ELR (unfenced) → last known leader (unfenced)** |
| Preferred leader | `auto.leader.rebalance.enable` **true** · `leader.imbalance.check.interval.seconds` **300** — cả hai **`read-only`** |
| Internal topic | `offsets.topic.replication.factor` **3** · `transaction.state.log.replication.factor` **3** · `transaction.state.log.min.isr` **2** — cluster nhỏ phải hạ về **1** |
| 4 loại quota | `producer_byte_rate` · `consumer_byte_rate` · `request_percentage` · `controller_mutation_rate` |
| Mức ưu tiên quota | **8 mức**, user thắng client-id, `--entity-name` thắng `--entity-default` |
| Cơ chế throttle | **Trì hoãn response + mute channel — KHÔNG ném exception**; quota là **per-broker** |
| `request_percentage` | `n%` = n% của **một** thread; trần `(num.io.threads + num.network.threads) × 100`% = **1100%** với mặc định 8+3 |
| Cửa sổ quota | `quota.window.num` **11** × `quota.window.size.seconds` **1** giây |
| Thread & idle | `num.network.threads` **3** · `num.io.threads` **8** · `background.threads` **10** · `queued.max.requests` **500**; idle percent **> 0.3** |
| Replication fetch | `num.replica.fetchers` **1** · `replica.fetch.max.bytes` **1 MiB** · `replica.fetch.response.max.bytes` **10 MiB** · `replica.socket.receive.buffer.bytes` **64 KiB** |
| Nén ở broker | `compression.type` = **`producer`** (giữ nguyên codec, **không** recompress) |
| JVM | Heap **6 GB** (`-Xms6g -Xmx6g`), **G1GC**, `MaxGCPauseMillis=20`, `InitiatingHeapOccupancyPercent=35`, `G1HeapRegionSize=16M` |
| OS | File descriptor **≥ 100000** · `vm.swappiness` **1** (không phải 0) · `vm.max_map_count` **262144** · filesystem **XFS**, mount `noatime` |
| 3 metric ISR | `UnderReplicatedPartitions` (ISR < replicas) · **`UnderMinIsrPartitionCount`** (ISR < min.isr → **acks=all bị chặn**) · `AtMinIsrPartitionCount` (ISR = min.isr → cảnh báo sớm) |

## 🚨 Playbook: triệu chứng → hành động

| Triệu chứng | Nguyên nhân khả dĩ | Hành động đầu tiên |
|---|---|---|
| Producer nhận `NotEnoughReplicasException` hàng loạt | ISR < `min.insync.replicas` vì broker chết hoặc follower tụt | `kt --describe --under-min-isr-partitions` → **khôi phục broker**. **Tuyệt đối không** hạ `min.insync.replicas` trong lúc hoảng loạn |
| Ghi ngừng ngay khi mất **1** broker trong cluster RF=3 (hoặc `UnderMinIsrPartitionCount` > 0 mà `UnderReplicatedPartitions` = 0) | `min.insync.replicas=3` — **over-correction**, hoặc min.isr đặt **> RF** | So `min.insync.replicas` với RF thật, rồi `kcfg --alter --entity-type topics --entity-name <t> --add-config min.insync.replicas=2` (đổi nóng) |
| `IsrShrinksPerSec`/`IsrExpandsPerSec` dao động liên tục | GC pause dài, disk chậm, mạng | Xem **GC log** và disk latency trước; **chưa** đụng `replica.lag.time.max.ms` (mà nó cũng `read-only`) |
| `OfflinePartitionsCount` > 0, vài broker vẫn sống | ISR rỗng cho partition đó | `kt --describe --unavailable-partitions`; kiểm cột `Elr:`; unclean election là **lựa chọn cuối** |
| URP > 0 kéo dài sau khi broker đã lên lại | 1 fetcher thread không kịp bắt kịp | `kcfg --alter --entity-type brokers --entity-default --add-config num.replica.fetchers=4` (không restart) |
| Broker vừa restart nhưng không nhận traffic ghi/đọc | Nó chỉ là **follower** cho mọi partition | Chờ `leader.imbalance.check.interval.seconds` **300** s, hoặc chạy `kafka-leader-election.sh --election-type preferred --all-topic-partitions` |
| Throughput client bị chặn trần, **log hoàn toàn sạch** | **Quota** đang throttle | Đọc `produce-throttle-time-avg` / MBean `kafka.server:type=Produce,user=…` `throttle-time`; rồi `kcfg --describe --entity-type users` |
| Produce latency ×3, CPU broker mới 40% | Thiếu I/O thread | `RequestHandlerAvgIdlePercent` < 0.3 → tăng `num.io.threads` |
| Controller nghẽn, tạo topic chậm bất thường | Một tenant spam create/delete topic | Đặt **`controller_mutation_rate`** cho user đó |
| `server.log`: `Too many open files` | ulimit của tiến trình broker quá thấp | Nâng file descriptor lên **≥ 100000**, restart broker |
| Broker crash `OutOfMemoryError (Map failed)` khi tăng partition | `vm.max_map_count` cạn (2 map area / segment) | `sysctl -w vm.max_map_count=262144` và ghi vào `/etc/sysctl.conf` |
| GC pause 1–2 s, throughput sụt, page cache nhỏ | Heap đặt quá to (16–32 GB) | Đưa `KAFKA_HEAP_OPTS` về **`-Xms6g -Xmx6g -XX:+UseG1GC`**, rolling restart |

## ⚠️ Bẫy đề hay gặp

- Thấy "cần durability cao hơn nữa cho RF=3" → dễ chọn `min.insync.replicas=3`, nhưng đúng là **2**: min.isr=3 khiến **mất 1 broker là ngừng ghi**, và đó là bẫy lặp lại nhiều nhất của domain này.
- Thấy "producer báo `NotEnoughReplicas`, làm gì trước?" → dễ chọn hạ `min.insync.replicas` xuống 1, nhưng đúng là **khôi phục replica**; hạ min.isr chỉ để lại dữ liệu chỉ có 1 bản.
- Thấy "`min.insync.replicas=2` đã đặt, sao vẫn mất dữ liệu?" → dễ đổ lỗi broker, nhưng đúng là producer đang dùng **`acks=1`** — `min.isr` **hoàn toàn vô hiệu** khi `acks≠all`.
- Thấy "ISR flapping" → dễ chọn tăng `replica.lag.time.max.ms`, nhưng đúng là **kiểm GC log và disk latency trước** (và config này `read-only`, đổi phải restart).
- Thấy "partition offline, cần sống lại ngay" → dễ chọn bật `unclean.leader.election.enable` toàn cluster, nhưng đúng là kiểm **ELR** trước, và nếu buộc phải unclean thì bật **ở đúng topic đó** thôi.
- Thấy "bật `unclean.leader.election.enable=true` xong mà partition vẫn offline" → tưởng lệnh không ăn, nhưng KRaft cần chờ **thread định kỳ 5 phút** hoặc chạy `kafka-leader-election.sh` với option unclean.
- Thấy "client bị chặn throughput" → dễ tìm exception trong log, nhưng quota **không ném lỗi**: nó **trì hoãn response**. Bằng chứng duy nhất là **`throttle-time` / `produce-throttle-time-avg`**.
- Thấy "`producer_byte_rate=10 MB/s` trên cluster 6 broker, client đo được 55 MB/s" hoặc "đặt quota cho user rồi mà client vẫn vượt" → không phải quota hỏng: quota là **per-broker** (trần thực tế **60 MB/s**), và một quota `(user, client-id)` cụ thể hơn luôn **thắng** quota mức user.
- Thấy "broker chậm, thêm RAM cho heap" → sai: Kafka dựa **page cache**, heap **6 GB** là đủ; heap to làm **GC pause dài** và **page cache nhỏ**.
- 🕰️ **Bẫy version:** đáp án nhắc `zookeeper.connect`, `--zookeeper`, hay "quota lưu trong znode `/config/users`" → **sai với Kafka 4.x**: ZooKeeper đã bị gỡ từ **4.0**, quota nằm trong **metadata log**.
- 🕰️ **Bẫy version:** đáp án đề nghị chạy **`kafka-preferred-replica-election.sh`** → công cụ này **đã bị gỡ**; đúng là **`kafka-leader-election.sh --election-type preferred`**.
- 🕰️ **Bẫy giá trị cũ:** "ISR dựa trên `replica.lag.max.messages`" → config này **đã bỏ từ 0.9**, chỉ còn **`replica.lag.time.max.ms` = 30000**; "`num.recovery.threads.per.data.dir` mặc định 1" → đã đổi thành **2** từ **4.0**; "`replica.fetch.response.max.bytes` mặc định 1 MiB" → thật ra là **10 MiB**.

## 🧪 Lab checklist

- [ ] Lab 3.1 ⭐ — Lập bảng thực nghiệm RF=3/`min.isr=2`: tắt 1 rồi 2 broker × thử `acks=all` và `acks=1`, đối chiếu Bảng 1.
- [ ] Lab 3.2 — Đặt `min.insync.replicas=3`, tắt 1 broker → thấy `NotEnoughReplicasException`; sửa về 2 **không restart broker**.
- [ ] Lab 3.3 — Bật `eligible.leader.replicas.version=1`, đọc cột `Elr:` / `LastKnownElr:`, ép ISR co về 1 và quan sát ELR.
- [ ] Lab 3.4 ⭐ — `producer_byte_rate` cho user: `kafka-producer-perf-test.sh` bị kìm **không lỗi**; thêm quota `(user, client-id)` để chứng minh mức ưu tiên 1 > 3.
- [ ] Lab 3.5 — Đo thời gian URP về 0 với `num.replica.fetchers` = 1 so với = 4.
- [ ] Lab 3.6 — Đọc heap/GC của broker, đổi `KAFKA_HEAP_OPTS`, xem page cache qua `/proc/meminfo`.
- [ ] Lab 3.7 — `request_percentage` quota + MBean `kafka.server:type=Request,...` (`throttle-time`, `request-time`).

## 🚪 Cổng tự kiểm tra (phải trả lời trôi chảy mới sang tuần sau)

- **Cluster RF=3. Muốn chịu mất 1 broker mà vẫn ghi được và không mất dữ liệu thì đặt gì? Vì sao không đặt `min.isr=3`?**
  **Đáp án gọn:** `min.insync.replicas=2` + producer `acks=all`. `min.isr=3` là over-correction: `RF − min.isr = 0` → **mất 1 broker là ngừng ghi**.
- **`min.insync.replicas=2` nhưng producer dùng `acks=1` thì điều gì xảy ra?**
  **Đáp án gọn:** `min.insync.replicas` **bị bỏ qua hoàn toàn**; ghi thành công chỉ với leader và **có thể mất** nếu leader chết trước khi follower kịp sao.
- **Nêu thứ tự bầu leader khi ELR đã bật, và ELR khác unclean leader election ở điểm nào?**
  **Đáp án gọn:** ISR → ELR (replica unfenced) → last known leader (unfenced). ELR **không mất dữ liệu** (nhờ strict min ISR); unclean election **chấp nhận mất dữ liệu**.
- **Kể 4 loại quota và cho biết loại nào chặn một tenant spam tạo/xoá topic.**
  **Đáp án gọn:** `producer_byte_rate`, `consumer_byte_rate`, `request_percentage`, `controller_mutation_rate` — loại cuối (KIP-599) chặn create/delete/alter topic.
- **Client báo throughput bị chặn trần nhưng không có exception nào. Bạn kiểm tra gì đầu tiên?**
  **Đáp án gọn:** quota — throttle là **trì hoãn response + mute channel**, không ném lỗi. Kiểm `produce-throttle-time-avg` phía client, MBean `kafka.server:type=Produce,user=…,client-id=…` `throttle-time` phía broker, rồi `kafka-configs.sh --describe --entity-type users`.
- **Broker vừa restart xong, URP mãi không về 0. Hành động rẻ nhất và đảo ngược được là gì?**
  **Đáp án gọn:** tăng `num.replica.fetchers` (1 → 4) bằng `kafka-configs.sh`, **cluster-wide, không cần restart**.
- **Broker 64 GB RAM đang chạy heap 32 GB, GC pause 2 giây, ISR flapping. Sửa thế nào và vì sao?**
  **Đáp án gọn:** đưa heap về **6 GB** với **G1GC** rồi rolling restart. Kafka dựa vào **page cache của OS**, không dựa heap; heap to chỉ làm GC pause dài và page cache nhỏ.
- **Ba con số OS phải chỉnh cho broker production là gì?**
  **Đáp án gọn:** file descriptor **≥ 100000**, `vm.swappiness` **= 1** (không phải 0), `vm.max_map_count` (ví dụ **262144**) — cộng thêm filesystem **XFS** mount `noatime` và tách ổ log khỏi ổ OS.
- **⭐ CHECKPOINT:** đã đạt **≥70%** ở MINI-MOCK CFG (~30 câu trộn Tuần 2 + Tuần 3) chưa? Nếu chưa → **KHÔNG** sang Tuần 4, ôn lại câu sai trước.

## 📎 Tài nguyên tuần này

> 📂 **Đã crawl sẵn tài liệu chính thức vào** [`resources/`](resources/INDEX.md) — đọc offline được.

- Apache Kafka Docs 4.3 — **Design → Replication** (`kafka.apache.org/43/design/design/#replication`) và **Design → Quotas** (`#quotas`).
- Apache Kafka Docs 4.3 — **Operations → Basic Kafka Operations**: *Setting quotas*, *Balancing leadership*, *Graceful shutdown* (`kafka.apache.org/43/operations/basic-kafka-operations/`).
- Apache Kafka Docs 4.3 — **Operations → Eligible Leader Replicas** (`kafka.apache.org/43/operations/eligible-leader-replicas/`).
- Apache Kafka Docs 4.3 — **Operations → Hardware and OS** + **Java Version** (`/43/operations/hardware-and-os/`, `/43/operations/java-version/`).
- Apache Kafka Docs 4.3 — **Configuration → Broker Configs** (`kafka.apache.org/43/generated/kafka_config.html`) — đọc kỹ cột **Update Mode**.
- Apache Kafka Docs 4.3 — **Operations → Monitoring** (`kafka.apache.org/43/operations/monitoring/`) — phần replication, request pipeline và quota metrics.
- Confluent Docs — *Running Kafka in Production* (`docs.confluent.io/platform/current/kafka/deployment.html`) và *Best Practices for Kafka Production Deployments* (`.../post-deployment.html`).
- **KIP:** KIP-966 (Eligible Leader Replicas), KIP-599 (`controller_mutation_rate`), KIP-392 (follower fetching, `replica.selector.class`).
- Sách: *Kafka: The Definitive Guide* 2nd ed. — Chương **6** *Reliable Data Delivery* (acks × min.isr × RF) và Chương **12** *Administering Kafka* (quota, dynamic config).

## ✅ Checklist hoàn thành Tuần 3

- [ ] Hoàn thành 4 buổi A/B/C/D
- [ ] Vẽ lại được từ trí nhớ **Bảng 1** (ma trận durability) và **Bảng 3** (8 mức ưu tiên quota)
- [ ] Thuộc lòng bảng "PHẢI NHỚ" (30000 / 2 / 3 / 8 / 3 / 0.3 / 300 / 11×1s / 6 GB / 100000 / 1)
- [ ] Hoàn thành **7 lab** (3.1 → 3.7), trong đó 2 lab "gây hỏng rồi sửa" (3.1, 3.2) làm **không nhìn hướng dẫn** ở lần thứ hai
- [ ] Làm xong 30 câu [questions.md](questions.md), ghi sổ câu sai theo 5 nhóm
- [ ] **Đạt ≥70% MINI-MOCK CFG (~30 câu, Tuần 2 + Tuần 3)** — ⭐ CHECKPOINT
- [ ] Vượt Cổng tự kiểm tra
