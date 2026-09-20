# 🛠️ Tuần 2 — Cluster Config I: broker config, storage & `log.dirs`, retention, compaction

> **Domain CCAAK:** Apache Kafka Cluster Configuration (22%) — phần 1 của 2 · **Thời lượng:** ~11h (4 buổi) · **Vị trí:** Tuần 2/8
>
> **Điều hướng:** [⬅️ Tuần 1](../week-01/README.md) · [🏠 Kế hoạch tổng](../../CCAAK-STUDY-PLAN.md) · [Tuần 3 ➡️](../week-03/README.md)

## 🔁 Ôn nhanh từ CCDAK (~20 phút)

| Khái niệm | File CCDAK cần đọc lại | Vì sao cần cho tuần này |
|---|---|---|
| Segment, retention, bẫy "active segment không bị xoá" | [`week-02/README.md`](../../../CCDAK/study-plan/week-02/README.md) mục 4 | Tuần này lặp lại cùng cơ chế nhưng hỏi từ góc **người vận hành**: chỉnh config nào, ở tầng nào, có cần restart không |
| Log compaction, tombstone, head vs tail | [`week-02/resources/kafka-log-compaction.md`](../../../CCDAK/study-plan/week-02/resources/kafka-log-compaction.md) | Lab 2.4 sẽ ép cleaner chạy thật và đọc kết quả bằng `kafka-dump-log.sh` — cần nhớ trước 4 đảm bảo |
| Chuỗi 4 giới hạn kích cỡ message | [`week-02/README.md`](../../../CCDAK/study-plan/week-02/README.md) mục 8 | Lab 2.5 gây `RecordTooLargeException` ở **2 tầng khác nhau**; phải phân biệt `max.request.size` 1048576 vs `message.max.bytes` 1048588 |
| Broker config & listener cơ bản | [`week-01/resources/kafka-broker-configs-listeners.md`](../../../CCDAK/study-plan/week-01/resources/kafka-broker-configs-listeners.md) | Nền để mở rộng sang nhóm thread / socket / storage mà CCDAK không đụng tới |
| Tiered storage (nhận diện) | [`week-08/resources/kafka-tiered-storage.md`](../../../CCDAK/study-plan/week-08/resources/kafka-tiered-storage.md) | Tuần này chỉ học **góc cấu hình**: hai công tắc, `local.retention.ms`, và điều kiện loại trừ |
| Cluster Docker 3 broker + alias | [`week-01/labs.md`](../../../CCDAK/study-plan/week-01/labs.md) Lab 1.2 | Toàn bộ 7 lab tuần này chạy trên đúng cluster đó; không dựng lại |

## 🎯 Mục tiêu tuần này

- **Đọc được** một bảng broker config lạ và phân loại ngay nó thuộc nhóm nào (thread / socket / storage / log) và có **đổi nóng được không** — mà không cần tra docs.
- **Chứng minh được** trên cluster thật thứ tự ưu tiên 5 mức của config, và **chỉ đúng nguồn** đang thắng bằng cách đọc cột `synonyms` trong `kafka-configs.sh --describe --all`.
- **Tự tay khôi phục** một broker có log dir hỏng: nhận ra partition offline, xác định đúng ổ, sửa, và xác nhận ISR trở lại đầy đủ.
- **Chẩn đoán được** hai triệu chứng đối lập mà học viên hay nhầm: *"đặt retention 1 giờ mà data vẫn còn"* và *"đĩa đầy dù retention đã ngắn"* — nói được nguyên nhân và hành động đầu tiên cho từng cái.
- **Cấu hình được** một compacted topic chạy thật: ép cleaner làm việc, quan sát tombstone biến mất, và giải thích vì sao head vẫn còn key trùng.
- **Sửa đúng chỗ** khi gặp `RecordTooLargeException`, phân biệt lỗi phát sinh ở client với lỗi broker trả về.
- **Tính được** khi nào nên bật tiered storage thay vì mua thêm đĩa, và nêu được điều kiện khiến một topic **không** dùng được nó.

## 📚 Nội dung học chi tiết

### 🅰️ Buổi A — Lý thuyết (~3h)

**1. Bản đồ broker config theo nhóm — học theo nhóm, đừng học theo danh sách**

Kafka 4.3 có hơn 200 broker config. CCAAK không hỏi hết; nó hỏi **4 nhóm** dưới đây, và luôn hỏi kèm một triệu chứng. Bảng này là bảng **bắt buộc thuộc** của tuần:

| Nhóm | Config & mặc định | Tác dụng | Metric quan sát để biết phải chỉnh |
|---|---|---|---|
| **Network thread** | `num.network.threads` **3** | Nhận byte từ socket, trả response. Không đụng vào đĩa | `kafka.network:type=SocketServer,name=NetworkProcessorAvgIdlePercent` — dưới **0.3** là thiếu |
| **I/O (request handler) thread** | `num.io.threads` **8** | Xử lý request, bao gồm đọc/ghi đĩa | `kafka.server:type=KafkaRequestHandlerPool,name=RequestHandlerAvgIdlePercent` — dưới **0.3** là thiếu |
| **Replica fetcher** | `num.replica.fetchers` **1** | Số thread follower kéo dữ liệu từ **mỗi** broker nguồn | `UnderReplicatedPartitions` lâu không về 0 sau khi broker đã sống lại |
| **Background** | `background.threads` **10** | Việc nền linh tinh (xoá segment, checkpoint…) | Hiếm khi phải chỉnh; xem `LogFlushRateAndTimeMs` nếu nghi ngờ |
| **Recovery** | `num.recovery.threads.per.data.dir` **2** | Dựng lại index sau khi broker tắt không sạch; song song **theo từng thư mục** | Thời gian broker từ start tới `Kafka Server started` (trong `server.log`) |
| **Socket buffer** | `socket.send.buffer.bytes` / `socket.receive.buffer.bytes` **102400** (100 KiB) | SO_SNDBUF / SO_RCVBUF; tăng khi băng thông × RTT lớn (liên DC) | Throughput trần thấp dù CPU và đĩa rảnh |
| **Request queue** | `queued.max.requests` **500** | Số request chờ trước khi network thread bị chặn | `kafka.network:type=RequestChannel,name=RequestQueueSize` sát 500 |
| **Request size** | `socket.request.max.bytes` **104857600** (100 MiB) | Trần tuyệt đối một request | Client bị ngắt kết nối khi gửi batch rất lớn |
| **Storage** | `log.dirs` (null → `log.dir` = `/tmp/kafka-logs`) | Danh sách thư mục dữ liệu (JBOD) | `kafka.log:type=LogManager,name=OfflineLogDirectoryCount` > 0 |
| **Log/segment** | `log.segment.bytes` **1 GiB**, `log.roll.hours` **168** | Khi nào đóng segment hiện tại | `kafka.log:type=Log,name=Size,...` không giảm dù quá retention |
| **Retention** | `log.retention.hours` **168**, `log.retention.bytes` **-1**, `log.retention.check.interval.ms` **300000** | Khi nào xoá segment đã đóng | `kafka.log:type=Log,name=LogStartOffset,...` — **tăng = retention vừa xoá được cái gì đó** |
| **Cleaner** | `log.cleaner.threads` **1**, `min.cleanable.dirty.ratio` **0.5**, `log.cleaner.delete.retention.ms` **86400000** | Compaction | Kích thước partition của compacted topic cứ tăng đều |

> 🧠 Mẹo ghi nhớ nhóm thread: **3 – 8 – 1 – 10 – 2**. Đọc thành "ba network, tám io, một fetcher, mười background, hai recovery".

**2. Thứ tự ưu tiên config — 5 mức, và cách chứng minh**

Khi cùng một config được định nghĩa ở nhiều nơi, Kafka chọn theo thứ tự **từ mạnh xuống yếu**:

1. `DYNAMIC_TOPIC_CONFIG` — override trên chính topic
2. `DYNAMIC_BROKER_CONFIG` — dynamic cho **một** broker (`--entity-name <id>`)
3. `DYNAMIC_DEFAULT_BROKER_CONFIG` — dynamic **cluster-wide** (`--entity-default`)
4. `STATIC_BROKER_CONFIG` — `server.properties` lúc khởi động
5. `DEFAULT_CONFIG` — mặc định dựng sẵn

Công cụ chứng minh là `--describe --all`, và thứ bạn phải đọc là cột **`synonyms`**:

```
retention.ms=60000 sensitive=false synonyms={DYNAMIC_TOPIC_CONFIG:retention.ms=60000,
  STATIC_BROKER_CONFIG:log.retention.ms=604800000, DEFAULT_CONFIG:log.retention.hours=168}
```

Phần tử **đầu tiên** trong `synonyms` là nguồn đang thắng. Những phần tử sau cho biết *nếu gỡ override thì rơi xuống đâu* — nên `--delete-config` **không** đưa về mặc định in trong docs, mà về mức kế tiếp còn tồn tại.

Hệ quả vận hành quan trọng nhất, và cũng là câu hỏi lặp lại trong đề: **đặt cluster-wide default không đè được override đã có trên topic.** Sửa `min.insync.replicas` hay `retention.ms` ở mức broker rồi tuyên bố xong việc là sai; phải quét từng topic.

**3. Config động vs config cần restart — bảng quyết định thứ hai của tuần**

| Update mode | Nghĩa | Lệnh | Ví dụ tiêu biểu của Tuần 2 |
|---|---|---|---|
| `cluster-wide` | Đổi nóng cho cả cluster; cũng đặt per-broker được để thử nghiệm | `kafka-configs.sh --alter --entity-type brokers --entity-default --add-config k=v` | **Toàn bộ nhóm thread** (`num.network.threads`, `num.io.threads`, `num.replica.fetchers`, `background.threads`, `num.recovery.threads.per.data.dir`), **toàn bộ nhóm cleaner**, `log.retention.ms`, `log.retention.bytes`, `log.segment.bytes`, `log.roll.ms`, `message.max.bytes`, `compression.type` |
| `per-broker` | Đổi nóng nhưng chỉ cho một broker | `... --entity-type brokers --entity-name 2 --add-config k=v` | `cordoned.log.dirs` |
| `read-only` | **Bắt buộc restart** | Sửa `server.properties` → rolling restart | `log.dirs`, `log.dir`, `queued.max.requests`, cả hai socket buffer, `socket.request.max.bytes`, `log.retention.hours`, `log.roll.hours`, `log.retention.check.interval.ms`, `auto.create.topics.enable`, `delete.topic.enable`, `num.partitions`, `controlled.shutdown.enable`, `remote.log.storage.system.enable` |

> ⚠️ Chú ý cặp trớ trêu: `log.retention.hours` là **read-only** nhưng `log.retention.ms` là **cluster-wide**. Muốn đổi retention toàn cluster lúc chạy thì phải dùng `log.retention.ms`, không phải `log.retention.hours`. Tương tự `log.roll.hours` (read-only) vs `log.roll.ms` (cluster-wide).

`--entity-type` nhận `topics` · `brokers` · `users` · `clients` · `groups` · `ips`. `--entity-default` = "áp cho mọi entity chưa có override riêng". Trong Kafka 4.x các override này nằm trong **metadata log**, **không còn znode ZooKeeper** — mọi phương án nhắc `/config/brokers/<id>` hay cờ `--zookeeper` đều thuộc thế hệ Kafka ≤ 3.x.

**4. `log.dirs` nhiều ổ đĩa — JBOD**

- Docs Kafka khuyên **JBOD hơn RAID**: RAID "is usually a big performance hit for write throughput and reduces the available disk space", và rebuild RAID "effectively disables the server". Dư thừa đã có ở tầng ứng dụng nhờ replication.
- **Cách rải partition:** *"partitions will be assigned round-robin to data directories. Each partition will be entirely in one of the data directories."* Cụ thể, partition mới rơi vào thư mục **đang có ít partition nhất** — **theo SỐ PARTITION, không theo dung lượng còn trống**. Một ổ đã đầy 95% nhưng chỉ giữ 3 partition vẫn có thể nhận partition mới trước một ổ trống giữ 10 partition.
- **Một partition nằm trọn trong một thư mục.** Vì thế vài partition rất lớn vẫn làm lệch đĩa dù số lượng đã đều.
- **Một ổ hỏng ≠ broker chết.** Chỉ partition trên ổ đó về offline; broker tiếp tục phục vụ những partition ở ổ khác. Dấu hiệu: `OfflineLogDirectoryCount` > 0, và trong output `kafka-log-dirs.sh` thì trường `error` của log dir đó khác `null`.
- **Đọc phân bố:** `kafka-log-dirs.sh --bootstrap-server ... --describe --broker-list 2,3,4`. JSON gồm `brokers[] → logDirs[] → partitions[]`, mỗi partition có `size`, `offsetLag`, `isFuture`; mỗi log dir (từ KIP-849) có thêm `totalBytes` / `usableBytes`.
- **Di chuyển giữa các ổ:** `kafka-reassign-partitions.sh` với JSON có trường `log_dirs` song song `replicas` (KIP-113); `"any"` = để broker tự chọn.
- **Cordoning (KIP-1066):** `cordoned.log.dirs=/data/dir1` khiến ổ đó **vẫn chạy bình thường** nhưng **không nhận partition mới**; `cordoned.log.dirs="*"` cordon cả broker. Reassign lên broker không còn ổ nào chưa cordon → lỗi `INELIGIBLE_REPLICA`. Thứ tự rút broker: **cordon → reassign đi hết → `kafka-cluster.sh unregister`**.

**5. Cấu trúc segment**

Partition = một thư mục `<topic>-<partition>`. Trong đó mỗi segment là bộ 3 file cùng tên, đặt tên theo **offset đầu tiên** của segment: `.log` (dữ liệu), `.index` (offset → vị trí byte), `.timeindex` (timestamp → offset). Segment đầu tiên luôn là `00000000000000000000.log`.

- Segment **đang ghi** là **active segment**. Nó **không bao giờ** bị retention xoá, cũng **không bao giờ** bị compaction đụng vào, cũng **không** được đẩy lên tiered storage.
- Đóng (roll) segment khi đạt **`segment.bytes` = 1 GiB** hoặc quá **`segment.ms` = 7 ngày** (broker: `log.segment.bytes` / `log.roll.ms`, `log.roll.hours` 168) — cái nào đến trước.
- `.index` là **sparse index**: cứ mỗi `index.interval.bytes` = **4096** byte dữ liệu mới ghi một entry. Trần kích thước index là `segment.index.bytes` = **10 MiB**.
- Xoá thật: file bị đổi đuôi `.deleted` trước, rồi mới xoá sau `file.delete.delay.ms` = **1 phút** (broker: `log.segment.delete.delay.ms` = 60000).

**6. Retention — thời gian vs kích cỡ, và cái bẫy kinh điển**

- Thời gian: `retention.ms` = **7 ngày**. Ở broker, thứ tự ưu tiên trong nhóm là `log.retention.ms` > `log.retention.minutes` > `log.retention.hours` (168).
- Kích cỡ: `retention.bytes` = **-1** (không giới hạn), tính **trên từng partition** — topic 6 partition × 1 GiB = 6 GiB mỗi bản replica.
- Đặt cả hai → **cái nào chạm trước xoá trước**.
- Broker chỉ **quét** mỗi `log.retention.check.interval.ms` = **300000** (5 phút).
- 🚨 **Bẫy:** *"Data is deleted one log segment at a time."* Retention chỉ xoá **segment đã đóng**, và chỉ khi record **mới nhất** trong segment đã quá hạn. Đặt `retention.ms=3600000` trên một topic thưa dữ liệu với `segment.bytes` mặc định 1 GiB → segment không bao giờ đóng → **không có gì bị xoá**, dữ liệu sống nhiều ngày. Cách sửa: hạ **`segment.ms`** (hoặc `segment.bytes`) trước, rồi mới nói chuyện retention.

**7. Compaction — `cleanup.policy` và ba chế độ**

Bảng bắt buộc thứ ba của tuần:

| Tiêu chí | `delete` (mặc định) | `compact` | `compact,delete` |
|---|---|---|---|
| Xoá cái gì | **Cả segment** quá `retention.ms` / `retention.bytes` | Bản cũ của key trùng; tombstone xoá key | Cả hai cơ chế cùng chạy |
| Cần key? | Không | **Bắt buộc** (record key `null` bị từ chối) | Bắt buộc |
| Kích cỡ log hội tụ về | Bị chặn bởi retention | Số **key distinct** | Bị chặn bởi cả hai |
| Đọc từ offset 0 thấy gì | Mọi record còn trong retention | **Ít nhất** giá trị cuối của mọi key (+ tombstone chưa quá `delete.retention.ms`) | Giá trị cuối của key còn trong retention |
| Dùng cho | Event stream, log, metric | `__consumer_offsets`, changelog Streams, CDC snapshot, KV state | State có TTL (session, cache) |
| Tiered storage | ✅ hỗ trợ | ❌ **không** | ❌ **không** |

- Cleaner là thread nền (`log.cleaner.threads` = **1**). Nó chọn log có **tỉ lệ head/tail cao nhất**, dựng bản đồ offset cuối theo key, copy lại segment sạch rồi hoán đổi.
- Điều kiện để một log được dọn: bẩn ≥ **`min.cleanable.dirty.ratio` = 0.5**; record phải già hơn `min.compaction.lag.ms` = **0**; và `max.compaction.lag.ms` = **Long.MAX** là deadline ép dọn cho topic ghi chậm.
- **Cleaner cũng chỉ làm việc trên segment đã đóng** — hệt như retention. Lab compaction bắt buộc phải hạ `segment.ms`.
- **Tombstone** = record value `null`. Nó xoá key, rồi **chính nó** bị dọn sau `delete.retention.ms` = **86400000** (24 h). Hệ quả: consumer bootstrap từ offset 0 phải bắt kịp head **trong 24 h**, không thì bỏ lỡ tombstone và dựng state sai.
- **4 đảm bảo** của compaction: consumer bám head thấy mọi message · thứ tự không đổi · **offset không đổi** (đọc offset đã bị dọn → nhận offset kế tiếp còn tồn tại) · đọc từ đầu thấy **ít nhất** trạng thái cuối mọi key. Cái **không** được đảm bảo: "mỗi key chỉ còn đúng 1 bản" — **head chưa compact vẫn còn trùng**.

**8. Ba tầng kích cỡ message**

| Tầng | Config | Mặc định | Lỗi khi vượt |
|---|---|---|---|
| Producer | `max.request.size` | **1048576** | `RecordTooLargeException` **ném ngay ở client**, chưa gửi đi byte nào |
| Broker / topic | `message.max.bytes` / topic `max.message.bytes` | **1048588** | Broker trả `MESSAGE_TOO_LARGE`; client nhận `RecordTooLargeException` **sau một vòng mạng** |
| Follower | `replica.fetch.max.bytes` | **1048576** | Không ném lỗi — batch đầu vẫn được trả để replication không kẹt, nhưng nên đặt ≥ `message.max.bytes` |

Nhớ **1048588 ≠ 1048576**: 12 byte chênh là phần overhead của record batch header. Sửa `RecordTooLargeException` đúng thứ tự: tăng `max.request.size` phía producer **và** `max.message.bytes` phía topic; cân nhắc `replica.fetch.max.bytes`. Cách tốt hơn cả hai: **nén** hoặc **claim-check** (đẩy payload lên object storage, chỉ gửi URL).

**9. Hai công tắc vận hành hay bị hỏi**

- `auto.create.topics.enable` = **true** (read-only). Production **nên tắt**: một consumer gõ nhầm tên topic sẽ tạo ra topic mới với `num.partitions` = 1 và `default.replication.factor` = 1 — tức một topic không có dự phòng nào, lặng lẽ nằm trong cluster.
- `delete.topic.enable` = **true** (read-only). Từ Kafka 1.0 mặc định đã là `true`; tài liệu cũ ghi `false` là kiến thức ≤ 0.11.

**10. Tiered storage — nhìn từ góc cấu hình**

Hai công tắc, hai tầng: broker `remote.log.storage.system.enable=true` (**read-only** → restart) và topic `remote.storage.enable=true`. Khi bật, retention tách đôi: `local.retention.ms` / `local.retention.bytes` giữ trên đĩa broker, `retention.ms` / `retention.bytes` giữ tổng cộng. Mặc định local là **-2** = "kế thừa retention tổng" → bật tiered storage mà quên hạ local retention thì **không tiết kiệm được byte nào**. Điều kiện loại trừ phải thuộc: **không dùng được với compacted topic**.

### 🅱️ Buổi B — Hands-on (~3.5h)

> 🧪 **Lab cầm tay chỉ việc (từng bước + lệnh):** [labs.md](labs.md). Dùng lại cluster 3 broker + 1 controller của [CCDAK Tuần 1 Lab 1.2](../../../CCDAK/study-plan/week-01/labs.md) và alias `kt`/`kcp`/`kcc`/`kcg`/`kcfg`.

- **Lab 2.1 ⭐ — Ba mức config + synonyms:** đặt cùng một config ở topic / broker / cluster-default rồi dùng `kcfg --describe --all` chứng minh từng mức thắng theo đúng thứ tự; gỡ dần từng mức để thấy giá trị "rơi" xuống mức kế tiếp.
- **Lab 2.2 ⭐ — JBOD, gây hỏng rồi sửa:** thêm `log.dirs` hai thư mục, tạo topic nhiều partition, đọc phân bố bằng `kafka-log-dirs.sh`, **làm hỏng một log dir** → quan sát partition offline → khôi phục.
- **Lab 2.3 — Retention nhanh:** `retention.ms=60000` + `segment.ms=10000`, và đối chứng cho thấy vì sao để mặc định `segment.bytes` thì chẳng có gì bị xoá.
- **Lab 2.4 ⭐ — Compaction thật:** `min.cleanable.dirty.ratio=0.01`, `segment.ms=5000`, `delete.retention.ms=10000`; ghi cùng key nhiều lần + tombstone; đọc kết quả bằng `kafka-dump-log.sh`.
- **Lab 2.5 — Message size 3 tầng:** gây `RecordTooLargeException` ở client, rồi ở broker, rồi sửa đúng chỗ.
- **Lab 2.6 ⭐ — Làm đầy disk, gây hỏng rồi sửa:** ép log dir hết chỗ → quan sát `KafkaStorageException` / log dir offline → khôi phục theo playbook.
- **Lab 2.7 — Tiered storage:** bật trên một topic thử nghiệm với `local.retention.ms` nhỏ và `segment.bytes` nhỏ.

### 🅲️ Buổi C — Bổ sung (~2.5h)

**Bảng quyết định — "tôi muốn đổi X, đi đường nào?"**

| Tôi muốn | Đường đúng | Đường sai hay gặp |
|---|---|---|
| Đổi retention cho **một** topic | `kcfg --alter --entity-type topics --entity-name t --add-config retention.ms=...` | Đổi `log.retention.hours` ở broker (read-only, và không đè được topic override) |
| Đổi retention **mặc định** cho topic **tạo mới sau này** | `--entity-type brokers --entity-default --add-config log.retention.ms=...` | Tưởng nó áp ngược cho topic đã tồn tại có override |
| Tăng `num.io.threads` vì `RequestHandlerAvgIdlePercent` = 0.05 | `--entity-type brokers --entity-default --add-config num.io.threads=16` (nóng) | Rolling restart cả cluster (không cần) |
| Tăng `queued.max.requests` | Sửa `server.properties` + rolling restart | `kafka-configs.sh` (read-only, sẽ bị từ chối) |
| Thêm một ổ đĩa vào broker | Sửa `log.dirs` + restart **broker đó** | Tìm cách `--alter` động (không có) |
| Rút một ổ đĩa ra | `cordoned.log.dirs=/data/dir1` → reassign đi hết → tháo | Xoá thẳng thư mục khi broker đang chạy |
| Rút một broker ra | `cordoned.log.dirs="*"` → reassign → `kafka-cluster.sh unregister --id N` | `kill -9` rồi gỡ khỏi compose |
| Gỡ một override topic | `--alter --delete-config k` rồi **kiểm lại bằng `--describe --all`** | Giả định nó về đúng mặc định trong docs |
| Giảm số partition từ 12 xuống 6 | **Không làm được.** Tạo topic mới + mirror dữ liệu sang | `kafka-topics.sh --alter --partitions 6` (bị từ chối) |

**Bảng quyết định — "đĩa đang có vấn đề, hành động nào trước?"**

| Tình huống | Hành động đầu tiên (rẻ, đảo ngược được) | Hành động sau nếu chưa đủ |
|---|---|---|
| Một broker đầy đĩa, các broker khác rảnh | `kafka-log-dirs.sh --describe` tìm partition to nhất | Reassign có `--throttle`; cordon ổ trong lúc dọn |
| Một ổ trong JBOD đầy, ổ khác trống | `kafka-log-dirs.sh` xem `usableBytes` từng ổ | Reassign **giữa các log dir** bằng JSON có `log_dirs` |
| Cả cluster đầy đĩa | Hạ `retention.ms` (và **`segment.ms`**!) trên topic to nhất | Bật tiered storage với `local.retention.ms` nhỏ |
| Compacted topic phình mãi | Kiểm `min.cleanable.dirty.ratio` và `segment.ms` — có thể active segment đang giữ hết | Hạ `segment.ms`, tăng `log.cleaner.threads` |
| Log dir offline sau khi ổ hỏng | Đọc `server.log` tìm `KafkaStorageException`, xác nhận `OfflineLogDirectoryCount` | Sửa/thay ổ → restart broker → chờ URP về 0 |

**Đọc thêm:** mục *Updating Broker Configs* trên trang [Broker Configs](https://kafka.apache.org/43/configuration/broker-configs/) (đặc biệt hai tiểu mục *Updating Log Cleaner Configs* và *Updating Thread Configs*); mục *Log Compaction* trong [Design](https://kafka.apache.org/43/design/design/#log-compaction); [KIP-1066](resources/kip-1066-cordoned-log-dirs.md); chương 2 và 12 *Kafka: The Definitive Guide* 2nd ed.

### 🅳 Buổi D — Practice + Review (~2h)

> 📝 **Bộ câu hỏi luyện tập của tuần:** [questions.md](questions.md) — đáp án & giải thích: [answers.md](answers.md). *(tiếng Anh, văn phong CCAAK.)*

- Làm 30 câu của tuần. Ghi sổ câu sai, phân loại thành 5 nhóm: **ưu tiên config / update mode / log.dirs & JBOD / retention & segment / compaction**.
- Với **mỗi câu sai**, viết lại bằng một câu: *"triệu chứng là gì → metric nào xác nhận → lệnh nào là hành động đầu tiên"*. Đề CCAAK hỏi hành động, không hỏi định nghĩa.
- **Spaced repetition** mốc 1 / 3 / 7 ngày cho bộ số: **3 / 8 / 1 / 10 / 2** (thread) · **500 / 102400 / 104857600** (socket) · **1 GiB / 168 / 300000** (segment & retention) · **0.5 / 86400000 / 1** (cleaner) · **1048588 vs 1048576** (message size).
- Vẽ lại từ trí nhớ **thang 5 mức ưu tiên config** và nói to lệnh tương ứng của từng mức.

## 🧠 PHẢI NHỚ tuần này

| Fact | Con số / Ghi nhớ |
|---|---|
| Nhóm thread | `num.network.threads` **3** · `num.io.threads` **8** · `num.replica.fetchers` **1** · `background.threads` **10** · `num.recovery.threads.per.data.dir` **2** (đổi từ 1 ở 4.0) — **tất cả cluster-wide, đổi nóng được** |
| Nhóm socket | `queued.max.requests` **500** · socket send/receive buffer **102400** (100 KiB) · `socket.request.max.bytes` **104857600** (100 MiB) — **tất cả read-only, phải restart** |
| 5 mức ưu tiên | `DYNAMIC_TOPIC_CONFIG` > `DYNAMIC_BROKER_CONFIG` > `DYNAMIC_DEFAULT_BROKER_CONFIG` > `STATIC_BROKER_CONFIG` > `DEFAULT_CONFIG` |
| Đọc nguồn đang thắng | `kafka-configs.sh --describe --all` → phần tử **đầu tiên** trong `synonyms={...}` |
| `log.dirs` | **read-only** (null → `log.dir` = `/tmp/kafka-logs`); thêm ổ = **restart broker** |
| Rải partition trên JBOD | Theo **số partition ít nhất**, **KHÔNG theo dung lượng trống**; một partition nằm trọn một thư mục |
| Một ổ hỏng | Chỉ partition trên ổ đó offline, broker vẫn sống; `OfflineLogDirectoryCount` > 0, `error != null` trong `kafka-log-dirs.sh` |
| Cordon (KIP-1066) | `cordoned.log.dirs` (list, `""`, **per-broker**); `"*"` = cả broker; reassign vào → `INELIGIBLE_REPLICA`; cordon **không** di chuyển gì |
| Segment | `.log` + `.index` + `.timeindex`, tên = offset đầu tiên; `segment.bytes` **1 GiB**, `segment.ms` **7 ngày**, `index.interval.bytes` **4096**, `segment.index.bytes` **10 MiB** |
| Active segment | **Không bị** retention xoá, **không bị** compaction đụng, **không** lên tiered storage |
| Retention | `log.retention.hours` **168** · `log.retention.bytes` **-1** (per partition) · quét mỗi `log.retention.check.interval.ms` **300000** · xoá thật sau `file.delete.delay.ms` **60000** |
| Ưu tiên retention thời gian | `log.retention.ms` > `log.retention.minutes` > `log.retention.hours`; **`.ms` là cluster-wide, `.hours` là read-only** |
| Bẫy retention | "Retention 1 giờ mà data vẫn còn" = segment chưa đóng → **hạ `segment.ms`** |
| Compaction | `cleanup.policy` `delete` / `compact` / `compact,delete`; `min.cleanable.dirty.ratio` **0.5**; `log.cleaner.threads` **1**; `min.compaction.lag.ms` **0**; `max.compaction.lag.ms` Long.MAX |
| Tombstone | value `null`; giữ `delete.retention.ms` **86400000** (24 h) → consumer bootstrap phải bắt kịp head trong 24 h |
| 4 đảm bảo compaction | Bám head thấy mọi message · thứ tự không đổi · **offset không đổi** · từ đầu thấy **ít nhất** trạng thái cuối mỗi key. **Không** đảm bảo "1 record/key" |
| Ba tầng message size | producer `max.request.size` **1048576** · broker `message.max.bytes` **1048588** (topic `max.message.bytes`) · follower `replica.fetch.max.bytes` **1048576** |
| Tên lệch giữa 2 tầng | topic `segment.ms` ↔ broker **`log.roll.ms`** · topic `min.cleanable.dirty.ratio` ↔ **`log.cleaner.min.cleanable.ratio`** · topic `file.delete.delay.ms` ↔ **`log.segment.delete.delay.ms`** |
| Công tắc vận hành | `auto.create.topics.enable` **true** (read-only, production nên tắt) · `delete.topic.enable` **true** (read-only) · `num.partitions` **1** |
| Tiered storage | Broker `remote.log.storage.system.enable` (read-only) + topic `remote.storage.enable`; `local.retention.ms/bytes` mặc định **-2** = kế thừa; **không hỗ trợ compacted topic** |

## 🚨 Playbook: triệu chứng → hành động

| Triệu chứng | Nguyên nhân khả dĩ | Hành động đầu tiên |
|---|---|---|
| Đặt `retention.ms=3600000` nhưng dữ liệu 3 ngày trước vẫn đọc được | Active segment chưa đóng (`segment.bytes` 1 GiB mặc định) | Đặt `segment.ms` nhỏ (vd 600000) trên topic đó, rồi chờ qua một chu kỳ `log.retention.check.interval.ms` (5 phút) |
| Đĩa broker đầy dù `retention.bytes` đã đặt | `retention.bytes` tính **per partition**, nhân với số partition × RF; hoặc segment chưa đóng | `kafka-log-dirs.sh --describe` xem partition nào to nhất, rồi hạ cả `segment.ms` lẫn `retention.bytes` |
| `server.log` in `KafkaStorageException`, một số partition biến mất khỏi ISR | Log dir hỏng hoặc hết chỗ | Kiểm `OfflineLogDirectoryCount` và `error` trong `kafka-log-dirs.sh`; giải phóng chỗ hoặc sửa ổ → **restart broker** (log dir offline chỉ hồi phục khi restart) |
| Một ổ trong JBOD gần đầy, ổ kia trống | Kafka rải theo **số partition**, không theo dung lượng | `cordoned.log.dirs=<ổ đầy>` để chặn partition mới, rồi reassign giữa log dir bằng JSON có `log_dirs` |
| `RequestHandlerAvgIdlePercent` = 0.08, CPU 40%, produce latency gấp 3 | Thiếu I/O thread | `kcfg --alter --entity-type brokers --entity-default --add-config num.io.threads=16` — **nóng, không restart** |
| `NetworkProcessorAvgIdlePercent` thấp trong khi `RequestHandlerAvgIdlePercent` vẫn cao | Thiếu network thread, không phải thiếu I/O thread | Tăng `num.network.threads` (cluster-wide) |
| Compacted topic phình liên tục, số key distinct không đổi | Dirty ratio chưa chạm **0.5**, hoặc dữ liệu còn nằm trong active segment | Hạ `min.cleanable.dirty.ratio` và `segment.ms` trên topic; cân nhắc tăng `log.cleaner.threads` |
| Consumer dựng lại state từ offset 0 nhưng một key đã xoá lại "sống dậy" | Bỏ lỡ tombstone vì bootstrap lâu hơn `delete.retention.ms` (24 h) | Tăng `delete.retention.ms` trên topic changelog, hoặc rút ngắn thời gian bootstrap |
| Producer ném `RecordTooLargeException` **trước khi** có request nào ra mạng | Vượt `max.request.size` (1048576) ở client | Tăng `max.request.size` phía producer; đồng thời tăng `max.message.bytes` của topic nếu không muốn lỗi lần hai |
| Producer nhận `RecordTooLargeException` **sau một vòng mạng** | Broker trả `MESSAGE_TOO_LARGE` vì vượt `message.max.bytes` (1048588) | `kcfg --alter --entity-type topics --add-config max.message.bytes=...`; kiểm `replica.fetch.max.bytes` ≥ giá trị mới |
| Đổi `min.insync.replicas` ở cluster default nhưng vài topic không đổi theo | Những topic đó có `DYNAMIC_TOPIC_CONFIG` override | `--describe --all` từng topic, đọc `synonyms`, rồi `--delete-config` hoặc đặt lại trực tiếp trên topic |
| Broker khởi động lại rất lâu sau `kill -9` | Log recovery phải dựng lại index cho mọi segment | Tăng `num.recovery.threads.per.data.dir` (mặc định 2, cluster-wide); lần sau dùng shutdown có kiểm soát (`controlled.shutdown.enable=true`) |

## ⚠️ Bẫy đề hay gặp

- Thấy "tăng `num.io.threads` trên cluster production" → dễ chọn *rolling restart*, nhưng đúng là **`kafka-configs.sh` đổi nóng** (cluster-wide). Ngược lại, thấy "tăng `queued.max.requests`" → dễ chọn `kafka-configs.sh`, nhưng nó **read-only, phải restart**.
- Thấy "đặt `log.retention.hours=1` bằng `kafka-configs.sh`" → tưởng chạy được, nhưng `log.retention.hours` là **read-only**; muốn đổi nóng phải dùng **`log.retention.ms`**.
- Thấy "retention đã 1 giờ mà dữ liệu vẫn còn" → dễ chọn *tăng `log.retention.check.interval.ms`* hoặc *restart broker*, nhưng đúng là **segment active chưa đóng** → hạ `segment.ms`.
- Thấy "Kafka rải partition lên ổ nhiều chỗ trống nhất" → sai; nó rải theo **số partition ít nhất**. Đây là câu trả lời cho "vì sao một ổ đầy mà ổ kia trống".
- Thấy "một ổ đĩa hỏng → broker chết, phải thay cả broker" → sai; chỉ **partition trên ổ đó** offline, broker vẫn phục vụ ổ còn lại.
- Thấy "cordon một log dir" → tưởng nó chuyển partition đi, nhưng cordon **chỉ chặn partition mới**; muốn rỗng ổ vẫn phải reassign.
- Thấy "compacted topic đảm bảo mỗi key chỉ còn một record" → sai; **head chưa compact vẫn còn bản trùng**. Đảm bảo đúng là "đọc từ đầu thấy **ít nhất** trạng thái cuối của mọi key".
- Thấy tiered storage → hai bẫy đi cặp: "bật cho `__consumer_offsets` để tiết kiệm đĩa" là **sai** (compacted topic không được hỗ trợ), và "bật `remote.storage.enable=true` là xong" là **thiếu** (phải bật `remote.log.storage.system.enable` ở broker **và** hạ `local.retention.ms`, mặc định `-2` = kế thừa retention tổng).
- **Bẫy version 1:** phương án nào nhắc `--zookeeper`, znode `/config/brokers/<id>`, hoặc `zookeeper.connect` để đổi config động → **sai với Kafka 4.x** (KRaft-only từ 4.0); override nằm trong metadata log, thao tác bằng `--bootstrap-server` (hoặc `--bootstrap-controller` khi broker offline).
- **Bẫy version 2:** phương án ghi `num.recovery.threads.per.data.dir` mặc định **1**, `delete.topic.enable` mặc định **false**, hoặc `message.max.bytes` = **1048576** → cả ba là số cũ/số nhầm. Từ **4.0** recovery threads là **2**; `delete.topic.enable` đã là `true` từ Kafka 1.0; `message.max.bytes` là **1048588** (1048576 là `max.request.size` của producer).
- **Bẫy version 3:** phương án đề xuất đặt `log.cleaner.enable=false` để tắt compaction → config này **đã deprecated và sẽ bị gỡ ở Kafka 5.0**; muốn tắt compaction thì đổi `cleanup.policy` của topic.
- Thấy "giảm số partition của topic từ 12 xuống 6 để tiết kiệm đĩa" → **không làm được**; Kafka không hỗ trợ giảm partition.

## 🧪 Lab checklist

- [ ] Lab 2.1 ⭐ — Đặt cùng một config ở 3 mức (topic / broker / cluster-default), dùng `kcfg --describe --all` đọc `synonyms` chứng minh đúng thứ tự ưu tiên, rồi gỡ dần từng mức.
- [ ] Lab 2.2 ⭐ — JBOD 2 log dir, `kafka-log-dirs.sh` xem phân bố, **làm hỏng một log dir** → partition offline → khôi phục (gây hỏng rồi sửa).
- [ ] Lab 2.3 — `retention.ms=60000` + `segment.ms=10000` xoá được dữ liệu; đối chứng với `segment.bytes` mặc định thì không.
- [ ] Lab 2.4 ⭐ — Compaction thật với `min.cleanable.dirty.ratio=0.01`, tombstone, và `kafka-dump-log.sh` để nhìn kết quả.
- [ ] Lab 2.5 — `RecordTooLargeException` ở client rồi ở broker; sửa đúng tầng.
- [ ] Lab 2.6 ⭐ — Làm đầy log dir → `KafkaStorageException` / log dir offline → khôi phục (gây hỏng rồi sửa).
- [ ] Lab 2.7 — Tiered storage trên 1 topic với `local.retention.ms` nhỏ; xác nhận điều kiện loại trừ với compacted topic.

## 🚪 Cổng tự kiểm tra (phải trả lời trôi chảy mới sang tuần sau)

- **Đọc đúng thứ tự 5 mức ưu tiên config, và nói lệnh tương ứng của từng mức?**
  **Đáp án gọn:** `DYNAMIC_TOPIC_CONFIG` (`--entity-type topics --entity-name t`) > `DYNAMIC_BROKER_CONFIG` (`--entity-type brokers --entity-name id`) > `DYNAMIC_DEFAULT_BROKER_CONFIG` (`--entity-type brokers --entity-default`) > `STATIC_BROKER_CONFIG` (`server.properties`) > `DEFAULT_CONFIG`.
- **Config nào trong nhóm thread/socket đổi nóng được, config nào không?**
  **Đáp án gọn:** cả 5 config thread (`num.network.threads` 3, `num.io.threads` 8, `num.replica.fetchers` 1, `background.threads` 10, `num.recovery.threads.per.data.dir` 2) là cluster-wide → đổi nóng. Cả nhóm socket (`queued.max.requests` 500, buffer 102400, `socket.request.max.bytes` 104857600) là read-only → restart.
- **Kafka chọn log dir nào cho một partition mới, và tại sao một ổ vẫn đầy trước ổ kia?**
  **Đáp án gọn:** chọn thư mục đang có **ít partition nhất**, không nhìn dung lượng trống; partition to nhỏ khác nhau nên đều về số lượng không có nghĩa đều về byte.
- **Một log dir hỏng thì chuyện gì xảy ra, và khôi phục thế nào?**
  **Đáp án gọn:** chỉ partition trên ổ đó offline (`OfflineLogDirectoryCount` > 0, `KafkaStorageException` trong `server.log`), broker vẫn phục vụ ổ khác; sửa/thay ổ rồi **restart broker**, chờ URP về 0.
- **"Đặt retention 1 giờ nhưng data 3 ngày vẫn còn" — nguyên nhân và hành động đầu tiên?**
  **Đáp án gọn:** retention chỉ xoá **segment đã đóng**; `segment.bytes` mặc định 1 GiB khiến active segment không bao giờ đóng. Hành động: đặt `segment.ms` nhỏ trên topic đó.
- **Compaction đảm bảo gì và KHÔNG đảm bảo gì?**
  **Đáp án gọn:** đảm bảo bám head thấy mọi message, thứ tự không đổi, offset không đổi, đọc từ đầu thấy **ít nhất** trạng thái cuối mọi key. **Không** đảm bảo mỗi key chỉ còn một record (head còn trùng).
- **Tombstone tồn tại bao lâu, và điều đó ràng buộc gì với consumer?**
  **Đáp án gọn:** `delete.retention.ms` = 86400000 (24 h). Consumer dựng lại state từ offset 0 phải bắt kịp head trong 24 h, nếu không sẽ bỏ lỡ tombstone và giữ lại key lẽ ra đã xoá.
- **Cần giữ dữ liệu 1 năm nhưng đĩa broker đắt — cấu hình gì, và ngoại lệ nào?**
  **Đáp án gọn:** bật `remote.log.storage.system.enable` ở broker (restart) + `remote.storage.enable=true` trên topic, đặt `local.retention.ms` nhỏ và `retention.ms` = 1 năm. Ngoại lệ: **không dùng được với compacted topic**.

## 📎 Tài nguyên tuần này

> 📂 **Đã crawl sẵn tài liệu chính thức vào** [`resources/`](resources/INDEX.md) — đọc offline được (9 file).

- Apache Kafka Docs 4.3: [Broker Configs](https://kafka.apache.org/43/generated/kafka_config.html) · [Topic Configs](https://kafka.apache.org/43/generated/topic_config.html) · [Basic Kafka Operations](https://kafka.apache.org/43/operations/basic-kafka-operations/) · [Hardware and OS](https://kafka.apache.org/43/operations/hardware-and-os/) · [Design → Log Compaction](https://kafka.apache.org/43/design/design/#log-compaction) · [Tiered Storage](https://kafka.apache.org/43/operations/tiered-storage/) · [Monitoring](https://kafka.apache.org/43/operations/monitoring/).
- Confluent Docs: [Change Kafka Configurations Without Restart](https://docs.confluent.io/platform/current/kafka/dynamic-config.html) · [Kafka Broker and Controller Configuration Reference](https://docs.confluent.io/platform/current/installation/configuration/broker-configs.html) · [Kafka CLI Tools](https://docs.confluent.io/kafka/operations-tools/kafka-tools.html).
- KIP cho admin: **KIP-1066** (cordoned log dirs), KIP-112 (disk failure for JBOD), KIP-113 (replica movement between log dirs), KIP-849 (`totalBytes`/`usableBytes` trong `kafka-log-dirs.sh`), KIP-928 (log dir đầy), KIP-405 (tiered storage), KIP-226 (dynamic broker configuration).
- Sách: *Kafka: The Definitive Guide* 2nd ed. — chương 2 (Installing Kafka: broker config, disk, filesystem) và chương 12 (Administering Kafka: dynamic config, topic override).
- Confluent Developer (miễn phí): course *Kafka Internals* — module về log, segment và storage.

## ✅ Checklist hoàn thành Tuần 2

- [ ] Hoàn thành 4 buổi A/B/C/D
- [ ] Thuộc lòng bảng "PHẢI NHỚ" — đọc trôi bộ số **3 / 8 / 1 / 10 / 2** · **500 / 102400 / 104857600** · **1 GiB / 168 / 300000** · **0.5 / 86400000 / 1** · **1048588 vs 1048576**
- [ ] Đọc được thang 5 mức ưu tiên config từ trí nhớ, kèm lệnh của từng mức
- [ ] Hoàn thành **cả 7 lab**, trong đó **bắt buộc** Lab 2.2 và Lab 2.6 (hai bài "gây hỏng rồi sửa")
- [ ] Làm xong 30 câu [questions.md](questions.md), ghi sổ câu sai và phân loại theo 5 nhóm
- [ ] Viết lại được playbook 12 dòng của tuần mà không nhìn tài liệu
- [ ] Vượt Cổng tự kiểm tra (8 câu)
- [ ] Sẵn sàng sang [Tuần 3](../week-03/README.md) — nửa còn lại của domain CFG: replication & durability, quota, throughput, JVM/OS tuning
