# 🛠️ Tuần 6 — Kafka Connect operations

> **Domain CCAAK:** Kafka Connect (12%) · **Thời lượng:** ~11h (4 buổi) · **Vị trí:** Tuần 6/8
>
> **Điều hướng:** [⬅️ Tuần 5](../week-05/README.md) · [🏠 Kế hoạch tổng](../../CCAAK-STUDY-PLAN.md) · [Tuần 7 ➡️](../week-07/README.md)

## 🔁 Ôn nhanh từ CCDAK (~20 phút)

CCDAK Tuần 5 đã phủ Connect ở **góc developer**: chọn converter nào, viết SMT ra sao, DLQ để bắt record hỏng, exactly-once cho source. Tuần này là **góc administrator**: dựng cluster worker, scale nó, giữ nó sống khi một worker chết, khôi phục task chết, quản lý offset và nâng cấp plugin. **Đọc lại đúng 4 mục dưới đây rồi sang phần mới — đừng học lại converter/SMT.**

| Khái niệm | File CCDAK cần đọc lại | Vì sao cần cho tuần này |
|---|---|---|
| Worker / connector / task, converter vs serializer | [`../../../CCDAK/study-plan/week-05/README.md`](../../../CCDAK/study-plan/week-05/README.md) (Buổi A mục Connect) | Tuần này giả định bạn đã biết task là thứ copy data; ta chỉ hỏi **task chạy ở đâu và chuyển đi đâu khi worker chết** |
| 3 internal topic + REST cơ bản | [`../../../CCDAK/study-plan/week-05/resources/connect-user-guide-configs-rest.md`](../../../CCDAK/study-plan/week-05/resources/connect-user-guide-configs-rest.md) | Tuần này đi sâu **partition/RF/cleanup policy** của từng topic và điều gì hỏng khi đặt sai |
| `errors.tolerance`, DLQ, header `__connect.errors.*` | [`../../../CCDAK/study-plan/week-05/resources/connect-error-handling-dlq-kip298.md`](../../../CCDAK/study-plan/week-05/resources/connect-error-handling-dlq-kip298.md) | Góc admin: **giám sát** DLQ bằng metric và quyết định ngưỡng alert, không chỉ bật config |
| Offset source vs sink | [`../../../CCDAK/study-plan/week-05/resources/connect-exactly-once-source-kip618.md`](../../../CCDAK/study-plan/week-05/resources/connect-exactly-once-source-kip618.md) | Tuần này là **thao tác reset offset thật** bằng REST và bằng `kafka-consumer-groups.sh` |
| Consumer group, rebalance, lag (nền cho Connect group) | [`../../../CCDAK/study-plan/week-04/README.md`](../../../CCDAK/study-plan/week-04/README.md) | Sink task **là** consumer trong group `connect-<name>`; mọi kiến thức lag/reset offset áp dụng nguyên si |

> ⚠️ Một điểm phải **bỏ khỏi trí nhớ** ngay: số của consumer group **không** dùng cho Connect worker group. `session.timeout.ms` của worker là **10000**, không phải 45000.

## 🎯 Mục tiêu tuần này

- **Dựng được** một Connect cluster distributed nhiều worker từ số 0, kiểm chứng 3 internal topic đúng partition / cleanup policy / replication factor trước khi cho connector đầu tiên chạy.
- **Chẩn đoán được** bằng `GET /connectors/{n}/status` và metric JMX: connector RUNNING nhưng task FAILED, task UNASSIGNED, cluster kẹt trong rebalance — và biết endpoint nào chữa từng cái.
- **Tự tay khôi phục** một worker chết và một task chết, phân biệt rõ hai tình huống này (một cái Connect tự xử, một cái **bắt buộc** người vận hành can thiệp).
- **Tính được** số task thật một connector sẽ tạo, và giải thích được vì sao `tasks.max=6` trên topic 3 partition cho ra **6 task RUNNING trong đó 3 task không có việc**.
- **Thao tác được** trên offset của cả source lẫn sink: đọc, sửa, reset — và biết vì sao xoá connector không đủ để "chạy lại từ đầu".
- **Cấu hình được** một connector chạy bằng credential riêng và siết REST API, thay vì để mọi connector dùng chung principal của worker.
- **Lên được kế hoạch** nâng cấp plugin và rolling restart worker mà không mất dữ liệu và không dừng pipeline.

## 📚 Nội dung học chi tiết

### 🅰️ Buổi A — Lý thuyết (~3h)

**1. Standalone vs distributed — quyết định đầu tiên và không có đường lùi**

| Tiêu chí | Standalone | Distributed |
|---|---|---|
| Lệnh khởi động | `connect-standalone.sh worker.properties conn1.properties [conn2.properties …]` | `connect-distributed.sh worker.properties` (**không** truyền file connector) |
| Cách khai connector | File `.properties` **trên dòng lệnh**, đọc lúc khởi động | **Chỉ qua REST 8083** |
| Offset của source | File local `offset.storage.file.filename` | Internal topic `offset.storage.topic` |
| Config & status | Trong bộ nhớ process | Internal topic `config.storage.topic` / `status.storage.topic` |
| Chịu lỗi | **Không** — process chết là dừng hết | Có — task chuyển sang worker còn sống |
| Scale | Không (1 process) | Thêm worker cùng `group.id` |
| Khi nào dùng | Dev, demo, **agent thu log ngay trên máy sinh dữ liệu** (edge) | **Mặc định cho mọi production** |
| Bẫy | Đổi connector phải sửa file + restart process | Sửa file `.properties` của connector **không có tác dụng gì** |

> 🧠 Câu hỏi đề hay ra: *"Chúng tôi chạy 1 worker duy nhất, có nên dùng standalone cho gọn?"* → **Không.** Distributed với 1 worker vẫn cho bạn REST API, state bền trong Kafka, và đường nâng lên 2 worker mà không phải viết lại gì. Standalone chỉ hợp lý khi **bản chất bài toán là một agent gắn với một máy**.

**2. Worker config — những key làm hỏng cluster nếu sai**

- `group.id` — định danh Connect cluster. **Không được trùng với bất kỳ consumer group id nào** đang có (tài liệu Kafka nói thẳng điều này). Hai worker khác `group.id` = **hai cluster khác nhau** dù chung Kafka; chúng sẽ không thấy nhau và bạn sẽ tưởng rebalance hỏng.
- `config.storage.topic` / `offset.storage.topic` / `status.storage.topic` — 3 topic trạng thái. Hai Connect cluster **bắt buộc** dùng 3 tên topic khác nhau; dùng chung = hai cluster ghi đè config của nhau.
- `bootstrap.servers`, `key.converter`, `value.converter` — bắt buộc ở **cả hai** chế độ.
- `plugin.path` — danh sách thư mục plugin. Mỗi plugin được nạp bằng **classloader riêng** → hai connector dùng hai version của cùng một thư viện (vd `jackson`) vẫn sống chung. Plugin để ngoài `plugin.path` sẽ rơi vào classpath chung và **mất isolation** — nguyên nhân kinh điển của `NoSuchMethodError` chỉ xuất hiện khi cài thêm connector thứ hai.
- `plugin.discovery` = `hybrid_warn` (mặc định) / `only_scan` / `hybrid_fail` / `service_load`. `service_load` khởi động nhanh nhất nhưng đòi mọi plugin đã migrate.
- `offset.flush.interval.ms` **60000**, `offset.flush.timeout.ms` **5000** — nhịp commit offset của **source** task. Flush lâu hơn timeout → log `Failed to flush, timed out while waiting for producer to flush outstanding messages` và offset **không tiến**.
- `rest.port` 8083 / `listeners=http://:8083`; `rest.advertised.host.name` và `rest.advertised.port` là **địa chỉ worker khác dùng để forward request tới leader**. Sai giá trị này thì `POST /connectors` gửi vào worker follower sẽ treo — triệu chứng "tạo connector lúc được lúc không tuỳ worker nào nhận request".
- `key.converter` / `value.converter` ở **mức worker** là mặc định cho mọi connector; connector khai lại thì **thay thế toàn bộ** khối converter đó (kể cả các thuộc tính con như `value.converter.schemas.enable`) — không phải merge.

**3. Ba internal topic — bảng phải thuộc nguyên văn**

| Topic (config) | Partition | `cleanup.policy` | RF khuyến nghị | Chứa gì | Hỏng thì sao |
|---|---|---|---|---|---|
| `config.storage.topic` (`connect-configs`) | **bắt buộc 1** | `compact` | **3** | Config của mọi connector + assignment do leader ghi | Mất toàn bộ định nghĩa connector; nhiều hơn 1 partition → **thứ tự config không đảm bảo**, cluster hành xử phi xác định |
| `offset.storage.topic` (`connect-offsets`) | **25** (`offset.storage.partitions`) | `compact` | **3** | Offset của **source** connector (key/value do connector định nghĩa) | Source connector đọc lại từ đầu → **duplicate hàng loạt** |
| `status.storage.topic` (`connect-statuses`) | **5** (`status.storage.partitions`) | `compact` | **3** | Trạng thái connector/task, `trace` khi FAILED | `/status` trả sai hoặc rỗng; **không mất dữ liệu**, nhưng mù hoàn toàn |

- Cả 3 đều **compacted** (không phải `delete`) — vì chúng là **bảng trạng thái hiện tại**, không phải luồng sự kiện.
- `*.replication.factor` mặc định đã là **3** trong Kafka 4.3; trên cluster lab 1 broker phải hạ xuống **1** nếu không worker chết lúc khởi tạo topic.
- **Nên tạo tay 3 topic trước** khi khởi động worker lần đầu: topic auto-create có thể lấy `num.partitions` của broker (ví dụ 3) và làm config topic sai ngay từ đầu.

**4. Kiến trúc cluster Connect — ai quyết định cái gì**

- Worker cùng `group.id` **join nhóm qua chính giao thức group của Kafka** (giống consumer group, nhưng là nhóm riêng của Connect). Một worker được bầu làm **leader**: leader tính assignment (connector nào, task nào, chạy ở worker nào) và **ghi assignment vào config topic**.
- Gọi REST vào **worker bất kỳ** đều được: worker không phải leader sẽ **forward** request tới leader bằng địa chỉ `rest.advertised.*`.
- **Rebalance của Connect là incremental cooperative từ Kafka 2.3 (KIP-415).** `connect.protocol` mặc định **`sessioned`** (giá trị `eager` / `compatible` / `sessioned`). Trước 2.3, mọi thay đổi nhỏ (thêm 1 connector) làm **dừng toàn bộ task** của cả cluster; nay chỉ task **cần đổi chủ** mới dừng.
- **Thêm worker** → rebalance, một phần task chuyển sang worker mới, task còn lại chạy tiếp.
- **Bớt worker (graceful)** → worker gửi tín hiệu rời nhóm, task của nó được chia lại ngay.
- **Worker chết đột ngột** → phát hiện sau `session.timeout.ms` (**10000**), rồi leader **hoãn** tối đa `scheduled.rebalance.max.delay.ms` (**300000** = 5 phút) trước khi giao lại task, để chờ worker quay về. Đây là lý do "tôi kill worker mà task không chuyển ngay" — **không phải lỗi**.
- **Task chết** → **không có rebalance nào cả**. Docs Confluent nói thẳng: *"When a worker fails, tasks are rebalanced across the active workers. When a task fails, no rebalance is triggered, as a task failure is considered an exceptional case."* Người vận hành phải gọi REST restart.

**5. `tasks.max` là TRẦN — mục hay bị dạy sai nhất**

- Định nghĩa chính thức: *"Maximum number of tasks to use for this connector."* Runtime gọi `connector.taskConfigs(maxTasks)`; **connector tự quyết** trả về bao nhiêu cấu hình task.
- Vì vậy số task thật có thể **nhỏ hơn** `tasks.max`: `FileStreamSourceConnector` luôn trả đúng **1** task; JDBC source thường 1 task cho mỗi bảng.
- Nhưng **hầu hết sink connector trả về đủ `maxTasks`**. Task sink là consumer trong group `connect-<name>` → khi số task > số partition, các task dư **RUNNING nhưng `partition-count = 0`**: chúng tồn tại, tiêu tốn thread và connection, **không xử lý gì**.
- ⚠️ **Công thức `số task = min(tasks.max, số partition)` lan truyền trong tài liệu và đề dump bên thứ ba là SAI.** Nó mô tả số task *có việc*, không phải số task *được tạo*. `GET /connectors/{n}/tasks` sẽ trả về 6, `kcg --describe --members` sẽ liệt kê 6 member, và 3 trong số đó có `ASSIGNMENT` rỗng.
- `tasks.max.enforce` (deprecated, mặc định `true`) chỉ chặn connector **vượt** trần, không ép nó đạt trần.
- Hệ quả vận hành: muốn tăng song song cho sink thì **tăng partition trước**, rồi mới tăng `tasks.max`. Tăng `tasks.max` một mình = thêm task rỗng.

**6. REST API vận hành — bàn phím của người quản trị**

| Việc cần làm | Gọi gì |
|---|---|
| Liệt kê connector | `GET /connectors` · dashboard: `GET /connectors?expand=status&expand=info` |
| Tạo mới | `POST /connectors` với body **bọc** `{"name":…,"config":{…}}` |
| Tạo **hoặc** sửa | `PUT /connectors/{n}/config` với body **phẳng** (chỉ map config) — 201 tạo mới, 200 cập nhật |
| Chẩn đoán | `GET /connectors/{n}/status` → `connector.state`, `worker_id`, `tasks[].state`, **`tasks[].trace`** |
| Cứu task chết | `POST /connectors/{n}/restart?includeTasks=true&onlyFailed=true` |
| Cứu đúng 1 task | `POST /connectors/{n}/tasks/{id}/restart` |
| Tạm ngừng / chạy lại | `PUT /connectors/{n}/pause` · `PUT /connectors/{n}/resume` |
| Dừng hẳn (huỷ task, giữ config) | `PUT /connectors/{n}/stop` |
| Xem plugin đã cài | `GET /connector-plugins` (`?connectorsOnly=false` để thấy converter/SMT) |
| Kiểm config trước khi tạo | `PUT /connector-plugins/{class}/config/validate` |
| Offset | `GET` / `PATCH` / `DELETE /connectors/{n}/offsets` |
| Topic connector đang đụng | `GET /connectors/{n}/topics` · reset danh sách: `PUT /connectors/{n}/topics/reset` |
| Xoá | `DELETE /connectors/{n}` → 204 |

- Mã trả về của `restart`: **200** (chỉ connector) · **202** (có task được restart) · **204** · **404** không tồn tại · **409** đang rebalance.
- **409 Conflict** xuất hiện ở nhiều endpoint khi group đang rebalance — hành vi đúng là **đợi vài giây rồi thử lại**, không phải sửa config.
- Mọi field kiểu password bị **che bằng dấu `*`** trong response.

**7. Trạng thái của connector và task — và hành động tương ứng**

| State | Xuất hiện ở | Nghĩa | Hành động của người vận hành |
|---|---|---|---|
| `RUNNING` | connector & task | Đang chạy | Không làm gì. Nhưng **connector RUNNING không đảm bảo task RUNNING** — luôn đọc cả mảng `tasks[]` |
| `UNASSIGNED` | connector & task | Chưa được giao cho worker nào | Bình thường trong vài giây sau rebalance. Kéo dài → thiếu worker, hoặc cluster kẹt rebalance |
| `PAUSED` | connector & task | Người dùng pause; task **vẫn tồn tại**, không poll/put | `PUT /resume`. Chuyển trạng thái là **bất đồng bộ**, các task không đổi cùng lúc |
| `STOPPED` | **chỉ connector** (3.5+) | Task bị **huỷ hoàn toàn**, config và offset giữ nguyên | Bắt buộc trước khi `PATCH`/`DELETE` offset. `PUT /resume` để chạy lại |
| `FAILED` | connector & task | Có exception; đọc `trace` | **Không tự hồi phục, không gây rebalance.** Sửa nguyên nhân rồi `restart?includeTasks=true&onlyFailed=true` |
| `RESTARTING` | connector & task | Đang trong quá trình restart | Đợi; nếu kẹt lâu thì xem log worker |

> 🧠 `connector-metrics.status` có giá trị `stopped`; `connector-task-metrics.status` **không có** — vì `STOPPED` huỷ task nên không còn task để báo trạng thái. Đây là chi tiết phân biệt hai mức mà đề thích khai thác.

**8. Quản lý offset — source và sink là hai thế giới**

| | Source connector | Sink connector |
|---|---|---|
| Offset nằm ở đâu | Internal topic **`connect-offsets`** | Consumer group **`connect-<connector-name>`** trong `__consumer_offsets` |
| Hình dạng offset | Cặp key/value **do connector tự định nghĩa** (vd `{"filename":"/data/in.txt"}` → `{"position":1024}`) | `{"kafka_topic":…,"kafka_partition":…}` → `{"kafka_offset":…}` |
| Ai commit | Framework theo `offset.flush.interval.ms` (**60000**) | Consumer commit theo nhịp của sink task |
| Có DLQ không | **KHÔNG** — `errors.deadletterqueue.*` không tồn tại trong config source | **CÓ** |
| Reset bằng CLI | Không có CLI riêng | `kafka-consumer-groups.sh --group connect-<n> --reset-offsets … --execute` (group phải **inactive**) |
| Reset bằng REST | `PUT /stop` → `DELETE /connectors/{n}/offsets` → `PUT /resume` | Y hệt (REST xoá luôn consumer group ở phía broker) |
| Xoá connector có xoá offset không | **Không** | **Không** |

- **`DELETE /connectors/<name>` không xoá offset.** Tạo lại cùng tên → tiếp tục từ chỗ cũ. Đây là bẫy vận hành gây "vì sao connector mới không đọc lại dữ liệu cũ".
- `PATCH` / `DELETE` offset **bắt buộc trạng thái `STOPPED`**. `PAUSED` là **không đủ**: pause giữ task sống, consumer group vẫn có member, nên broker từ chối xoá group → **500**.
- `PATCH` với `"offset": null` cho một partition = **xoá** offset của partition đó, không phải đặt về 0.
- Source có thể dùng offset topic riêng: `offsets.storage.topic` ở **mức connector** (mặc định `null` → dùng chung của worker).

**9. Error handling ở góc admin**

- `errors.tolerance` = `none` (**mặc định**, task FAILED ngay) hoặc `all` (bỏ qua record hỏng).
- `errors.log.enable` **false** và `errors.log.include.messages` **false** là mặc định → log **không** chứa nội dung record. Bật `include.messages` là quyết định có yếu tố **PII**.
- `errors.retry.timeout` **0** (không retry), `-1` = vô hạn; `errors.retry.delay.max.ms` **60000** là trần backoff. Retry chỉ cứu lỗi **tạm thời** (hệ đích timeout), không cứu record sai format.
- **DLQ chỉ có ở sink**: `errors.deadletterqueue.topic.name` (mặc định rỗng = tắt), `errors.deadletterqueue.topic.replication.factor` (**3** — phải hạ xuống 1 trên cluster nhỏ), `errors.deadletterqueue.context.headers.enable` (**false** — không bật thì DLQ không có lý do lỗi, gần như vô dụng).
- **`errors.tolerance=all` mà không có DLQ = mất dữ liệu im lặng.** Đây là phương án "sai nhưng hấp dẫn" của đề.
- Giám sát DLQ bằng `task-error-metrics`: `deadletterqueue-produce-requests` (thử ghi), `deadletterqueue-produce-failures` (ghi hỏng), `total-records-skipped`, `total-record-errors`, `total-record-failures`.
- **DLQ không có người đọc là mất dữ liệu có thủ tục.** Luôn kèm một alert trên sản lượng DLQ và một quy trình reprocess.

**10. Client override — cho một connector chạy bằng credential riêng**

- `connector.client.config.override.policy` ở **mức worker**: `None` (cấm hết) · `Principal` (chỉ `security.protocol`, `sasl.jaas.config`, `sasl.mechanism`) · `All` · **`Allowlist`** (từ 4.2, liệt kê tường minh).
- **Mặc định trong Apache Kafka 4.3 là `All`** (đổi từ `None` ở Kafka 3.0, KIP-722). Docs 4.3 khuyến nghị đặt `Allowlist`, và **`Allowlist` sẽ thành mặc định từ 5.0**.
- Connector override bằng prefix `consumer.override.*` / `producer.override.*` / `admin.override.*`. Ví dụ cho một sink connector dùng user SCRAM riêng: `consumer.override.sasl.jaas.config=…`.
- Vì sao quan trọng: mặc định **mọi connector dùng chung principal của worker**. Một connector bị cấu hình sai có thể đọc mọi topic mà worker có quyền. Tách credential = tách bán kính thiệt hại.
- Ba prefix, ba mục đích: `producer.` (source ghi Kafka + **ghi DLQ**), `consumer.` (sink đọc Kafka), `admin.` (tạo internal topic, **tạo DLQ topic**). Quên `admin.` → sink chạy ngon cho tới record hỏng đầu tiên rồi chết vì không tạo được DLQ.

**11. Nâng cấp plugin và worker**

- **KIP-891 (Kafka 4.1)** — nhiều version của cùng một plugin sống song song trên một cluster, chọn bằng `connector.plugin.version`, `key/value/header.converter.plugin.version`, `transforms.<alias>.plugin.version`. Cho phép nâng cấp **hai pha** và rollback từng connector. Trước 4.1 phải dựng **hai Connect cluster** để chạy hai version.
- Cài JAR version mới **vẫn cần restart worker** (để nạp plugin), nhưng **migrate từng connector** sang version mới thì không cần restart cluster.
- **Rolling restart worker** an toàn: tắt êm từng worker (không `kill -9`) → chờ rebalance xong (`rebalancing = false`, `/status` của mọi connector về RUNNING) → worker tiếp theo. Restart trong vòng `scheduled.rebalance.max.delay.ms` (5 phút) thì task trở về đúng worker cũ, gần như không xáo trộn.
- Không mất dữ liệu vì: sink commit offset qua consumer group, source flush offset vào `connect-offsets`; worker mới đọc lại đúng chỗ. Chỉ có thể **duplicate** ở ranh giới commit — đúng semantics at-least-once.

**12. Metric Connect — đèn báo của cluster**

| MBean | Attribute cần nhớ | Đọc để làm gì |
|---|---|---|
| `connect-worker-metrics` | `connector-count`, `task-count` | Số connector/task **trên chính worker này**; sau khi kill 1 worker, số của worker còn lại **tăng** = rebalance đã xảy ra |
| `connect-worker-rebalance-metrics` | `rebalancing`, `time-since-last-rebalance-ms`, `leader-name`, `epoch`, `rebalance-avg-time-ms` | `rebalancing=true` kéo dài hoặc `time-since-last-rebalance-ms` răng cưa = **rebalance loop** |
| `connector-metrics` | `status` (`unassigned`/`running`/`paused`/`stopped`/`failed`/`restarting`) | Alert trên `failed` |
| `connector-task-metrics` | `status`, `offset-commit-failure-percentage`, `running-ratio`, `pause-ratio` | `offset-commit-failure-percentage` > 0 = offset **không tiến**, sắp duplicate hàng loạt |
| `sink-task-metrics` | `partition-count`, `sink-record-read-rate`, `sink-record-send-rate`, `sink-record-active-count`, `sink-record-lag-max` | `partition-count=0` = task dư; `read` cao mà `send`=0 = SMT `Filter` loại hết |
| `source-task-metrics` | `source-record-poll-rate`, `source-record-write-rate`, `source-record-active-count` | `poll` cao mà `write`=0 = nghẽn ở producer/transform |
| `task-error-metrics` | `deadletterqueue-produce-requests`, `deadletterqueue-produce-failures`, `total-records-skipped` | Sản lượng DLQ; `produce-failures` > 0 = **DLQ đang mất record** |

**13. Bảo mật Connect**

- REST mặc định là **HTTP mở, không auth** (`listeners=http://:8083`, `rest.extension.classes=""`). Ai gọi được REST thì có quyền tương đương admin pipeline.
- HTTPS: `listeners=https://…` + prefix riêng **`listeners.https.ssl.*`** (không phải `ssl.*`, vì `ssl.*` là cho kết nối tới broker) + `rest.advertised.listener=https`.
- Basic auth: `rest.extension.classes=org.apache.kafka.connect.rest.basic.auth.extension.BasicAuthSecurityRestExtension`.
- ACL của **worker**: `Create` trên Cluster, `Read`+`Write` trên 3 internal topic, `Read` trên Group = `group.id`.
- ACL của **connector**: source cần `Write` topic đích; sink cần `Read` topic nguồn **và** `Read` trên Group `connect-<name>`.
- Secret: `FileConfigProvider` (`${file:/path:key}`) hoặc `EnvVarConfigProvider` (`${env:VAR}`). **Mọi worker phải giải được mọi biến** — thiếu file trên một worker thì task FAILED đúng trên worker đó.

### 🅱️ Buổi B — Hands-on (~3.5h)

> 🧪 **Lab cầm tay chỉ việc (từng bước + lệnh):** [labs.md](labs.md). Dùng lại cluster 3 broker (`docker-compose.cluster.yml`) từ [CCDAK Tuần 1](../../../CCDAK/study-plan/week-01/labs.md) và alias `kt`/`kcg`/`kcfg`.

- **Lab 6.1 ⭐ — Dựng Connect distributed 2 worker:** file override riêng, hai worker cùng `group.id` khác REST port (8083/8084); kiểm 3 internal topic bằng `kt --describe`; `GET /connector-plugins`.
- **Lab 6.2 ⭐ — Kill 1 worker (gây hỏng rồi sửa):** quan sát task chuyển qua `/status` và `connector-count`/`task-count`; đo độ trễ do `scheduled.rebalance.max.delay.ms`; bật lại worker → rebalance ngược.
- **Lab 6.3 — `tasks.max` thực nghiệm:** sink `tasks.max=6` trên topic 3 partition → chứng minh **6 task RUNNING, 3 task không sở hữu partition nào** bằng `kcg --describe --group connect-<name> --members --verbose`.
- **Lab 6.4 ⭐ — Task FAILED → DLQ (gây hỏng rồi sửa):** đẩy record hỏng → sink task chết → đọc `trace` trong `/status` → bật `errors.tolerance=all` + DLQ → `restart?includeTasks=true` → xác nhận record vào DLQ kèm header `__connect.errors.*`.
- **Lab 6.5 — Quản lý offset:** `GET /offsets` cho cả source và sink; reset sink bằng `kafka-consumer-groups.sh`; reset source bằng `PUT /stop` → `DELETE /offsets` → `PUT /resume`.
- **Lab 6.6 — Client override:** bật `connector.client.config.override.policy` trên worker, cho một connector dùng credential SCRAM riêng bằng `consumer.override.sasl.jaas.config`.
- **Lab 6.7 — Pause/resume và rolling restart worker:** dừng êm từng worker, chứng minh không mất record.

### 🅲️ Buổi C — Bổ sung (~2.5h)

**Bảng quyết định 1 — "Connect không chạy, tôi nhìn cái gì trước?"**

| Quan sát đầu tiên | Kết luận | Bước tiếp theo |
|---|---|---|
| `GET /connectors` trả `[]` dù vừa tạo | Request đã vào worker khác cluster (`group.id` khác) hoặc internal topic khác tên | So `group.id` và 3 tên topic giữa các worker |
| `connector.state=RUNNING`, `tasks: []` | Connector chưa sinh task nào, hoặc task đang UNASSIGNED | `GET /connectors/{n}/tasks`; kiểm số worker sống |
| `connector.state=RUNNING`, một task `FAILED` | Lỗi dữ liệu hoặc lỗi hệ đích | Đọc `trace` → sửa gốc → `restart?includeTasks=true&onlyFailed=true` |
| Mọi task `UNASSIGNED` kéo dài | Không còn worker nào, hoặc kẹt rebalance | `rebalancing`, `leader-name`; kiểm worker còn sống |
| REST trả **409** liên tục | Group đang rebalance | Đợi; nếu không dứt thì xem worker nào đang restart lặp |
| Task RUNNING nhưng `sink-record-send-rate = 0` | Không có dữ liệu, hoặc SMT lọc hết, hoặc task không giữ partition nào | So `sink-record-read-rate` và `partition-count` |

**Bảng quyết định 2 — "Tôi muốn thay đổi X, dùng lệnh nào"**

| Mục tiêu | Cách đúng | Cách sai hay gặp |
|---|---|---|
| Sửa config connector đang chạy | `PUT /connectors/{n}/config` (upsert) | `DELETE` rồi `POST` lại — mất thời gian, và **offset vẫn giữ** nên cũng không "làm mới" được gì |
| Cho connector nghỉ vài phút rồi chạy tiếp | `PUT /pause` → `PUT /resume` | `DELETE` connector |
| Chuẩn bị sửa offset | `PUT /stop` | `PUT /pause` (PAUSED **không đủ** để `PATCH`/`DELETE` offset) |
| Cho sink đọc lại từ đầu | `PUT /stop` → `DELETE /offsets` → `PUT /resume`, hoặc `kafka-consumer-groups.sh --reset-offsets --to-earliest --execute` | `DELETE` connector rồi tạo lại cùng tên (offset vẫn còn) |
| Tăng song song cho sink | Tăng **partition** trước, rồi tăng `tasks.max` | Chỉ tăng `tasks.max` → thêm task rỗng |
| Cứu task chết | `restart?includeTasks=true&onlyFailed=true` | `restart` trơn (chỉ restart connector, task vẫn FAILED) |
| Nâng version connector | Cài JAR mới + `connector.plugin.version` (4.1+), migrate từng connector | Restart cả cluster và cutover đồng loạt |
| Đổi credential cho 1 connector | `consumer.override.*` / `producer.override.*` + policy cho phép | Đổi credential ở worker (ảnh hưởng **mọi** connector) |

**Đọc thêm:** [`resources/INDEX.md`](resources/INDEX.md) theo đúng thứ tự gợi ý; chương 12 *Administering Kafka* trong *Kafka: The Definitive Guide* 2nd ed.; KIP-415, KIP-875, KIP-891, KIP-298.

### 🅳 Buổi D — Practice + Review (~2h)

> 📝 **Bộ câu hỏi luyện tập của tuần:** [questions.md](questions.md) — đáp án & giải thích: [answers.md](answers.md). *(tiếng Anh, văn phong CCAAK.)*

- Làm **28 câu** của tuần; ghi sổ câu sai, phân loại: kiến trúc worker / REST & state / tasks & scaling / offset / error & DLQ / bảo mật & metric.
- Vẽ lại **từ trí nhớ** bảng 3 internal topic (partition / cleanup policy / RF / chứa gì) và bảng trạng thái → hành động. Đây là hai bảng dễ ra câu Matching nhất.
- Tự đặt 5 tình huống và trả lời bằng **đúng một câu lệnh REST**: task 2 chết · muốn sink đọc lại từ đầu · muốn biết connector đụng topic nào · muốn kiểm config trước khi tạo · muốn xem mọi connector đang FAILED trong một lần gọi.
- **Spaced repetition** mốc **1 / 3 / 7 ngày** cho bộ số: **1 / 25 / 5 / RF 3 / 8083 / 60000 / 300000 / 10000 / 3**.

## 🧠 PHẢI NHỚ tuần này

| Fact | Con số / Ghi nhớ |
|---|---|
| 3 internal topic | `connect-configs` **1** partition (bắt buộc) · `connect-offsets` **25** · `connect-statuses` **5** — **cả 3 đều `cleanup.policy=compact`**; `*.storage.replication.factor` mặc định **3** (`-1` = theo default broker; cluster 1 broker phải đặt **1**) |
| Cổng REST | **8083** (`listeners=http://:8083`) |
| Đồng hồ của worker group | `session.timeout.ms` **10000** · `heartbeat.interval.ms` **3000** · `rebalance.timeout.ms` **60000** — **khác** consumer group (45000/3000) |
| Hoãn rebalance khi worker chết | `scheduled.rebalance.max.delay.ms` **300000** ms (5 phút) |
| Giao thức rebalance | `connect.protocol` **`sessioned`** (`eager`/`compatible`/`sessioned`); incremental cooperative từ Kafka **2.3** (KIP-415) |
| Flush offset của source | `offset.flush.interval.ms` **60000** · `offset.flush.timeout.ms` **5000** |
| `tasks.max` | Mặc định **1**, là **TRẦN**. Connector tự quyết qua `taskConfigs(maxTasks)`. **`min(tasks.max, partitions)` là công thức SAI** |
| Task sink dư | Task > partition → task dư **RUNNING** nhưng `partition-count = 0`; sink task là consumer trong group **`connect-<connector-name>`** |
| Worker chết vs task chết | Worker chết → **rebalance tự động**. Task chết → **không rebalance, không tự restart** → `POST /connectors/{n}/restart?includeTasks=true&onlyFailed=true` |
| Mã HTTP của restart | **200** chỉ connector · **202** có task · **204** · **404** không tồn tại · **409** đang rebalance |
| `pause` vs `stop` | `pause`: task **còn sống**, ngừng poll/put (bất đồng bộ) · `stop` (3.5+): **huỷ task**, giữ config + offset. Vì thế `stopped` có ở `connector-metrics.status` nhưng **không có** ở `connector-task-metrics.status` |
| Sửa offset | `PATCH`/`DELETE /connectors/{n}/offsets` **bắt buộc `STOPPED`** (PAUSED không đủ); `"offset": null` = xoá offset partition đó |
| Xoá connector | `DELETE /connectors/{n}` **KHÔNG xoá offset** — tạo lại cùng tên là chạy tiếp từ chỗ cũ |
| Offset ở đâu | Source → `connect-offsets` (key/value do connector định nghĩa) · Sink → `__consumer_offsets` qua group `connect-<name>` |
| DLQ | **Chỉ sink.** `errors.deadletterqueue.topic.name` (rỗng = tắt) · `.topic.replication.factor` **3** · `.context.headers.enable` **false** |
| `errors.tolerance` | **`none`** mặc định (task FAILED ngay) · `all` bỏ qua — **`all` không kèm DLQ = mất dữ liệu im lặng** |
| `errors.retry.timeout` | **0** = không retry; **-1** = vô hạn; `errors.retry.delay.max.ms` **60000** |
| Client override | `connector.client.config.override.policy` mặc định **`All`** (đổi từ `None` ở 3.0, KIP-722); giá trị `None`/`Principal`/`All`/**`Allowlist`** (4.2+, mặc định từ **5.0**) |
| Nhiều version plugin | **KIP-891, Kafka 4.1**: `connector.plugin.version`, `*.converter.plugin.version` |
| Metric đèn đỏ | `connector-count` / `task-count` (**theo worker**), `rebalancing`, `offset-commit-failure-percentage`, `deadletterqueue-produce-requests`, `partition-count = 0` |
| ACL của sink connector | `Read` topic nguồn **+ `Read` trên Group `connect-<name>`**; worker cần `Create` Cluster + RW 3 internal topic + `Read` Group = `group.id` |

## 🚨 Playbook: triệu chứng → hành động

| Triệu chứng | Nguyên nhân khả dĩ | Hành động đầu tiên |
|---|---|---|
| `/status` báo `connector: RUNNING` nhưng một `task: FAILED` | Record hỏng, hệ đích từ chối, hoặc thiếu quyền | Đọc `tasks[].trace` → sửa gốc → `POST /connectors/{n}/restart?includeTasks=true&onlyFailed=true` |
| Kill 1 worker, 3–4 phút sau task vẫn chưa chuyển | `scheduled.rebalance.max.delay.ms` mặc định **5 phút** đang hoãn có chủ đích | Chờ hết delay, **hoặc** hạ config nếu SLA đòi failover nhanh hơn — không phải bug |
| Mọi task `UNASSIGNED`, `rebalancing=true` không dứt | Một worker đang restart lặp (OOM), hoặc `session.timeout.ms` 10 s quá ngắn cho mạng hiện tại | Xem log worker + `time-since-last-rebalance-ms`; dừng hẳn worker bệnh trước khi chỉnh config |
| `POST /connectors` lúc được lúc không, tuỳ worker nhận request | `rest.advertised.host.name`/`.port` sai → follower không forward được tới leader | Sửa advertised cho địa chỉ các worker **gọi tới nhau được**, rồi restart |
| REST liên tục trả `409 Conflict` | Group đang rebalance | Đợi vài giây và thử lại; chỉ điều tra nếu rebalance không kết thúc |
| Tăng `tasks.max` mà throughput không đổi | Task dư không sở hữu partition nào | `kcg --describe --group connect-<n> --members --verbose`; **tăng partition trước**, rồi mới tăng `tasks.max` |
| Sink im lặng, không lỗi, dữ liệu vẫn thiếu | `errors.tolerance=all` **không có DLQ** | Thêm `errors.deadletterqueue.topic.name` + `context.headers.enable=true`, bật `errors.log.enable` |
| Xoá connector rồi tạo lại cùng tên, không đọc lại dữ liệu cũ | `DELETE` không xoá offset | `PUT /stop` → `DELETE /connectors/{n}/offsets` → `PUT /resume` |
| `DELETE /offsets` trả **500** | Connector đang `RUNNING`/`PAUSED`, consumer group còn member | `PUT /connectors/{n}/stop` trước, xác nhận `STOPPED`, rồi gọi lại |
| Source connector đọc lại toàn bộ từ đầu sau khi restart worker | `connect-offsets` bị xoá/mất, hoặc worker đổi `offset.storage.topic`, hoặc flush timeout | So tên 3 internal topic giữa các worker; kiểm log `Failed to flush` và `offset.flush.timeout.ms` |
| Worker thứ hai khởi động nhưng không nhận task nào | Khác `group.id`, hoặc khác tên internal topic → **hai cluster riêng biệt** | So `group.id` + 3 tên topic; `GET /connectors` trên từng worker sẽ cho danh sách khác nhau |
| Sink chết ngay khi gặp record hỏng đầu tiên dù đã bật DLQ | DLQ topic chưa tạo được: `errors.deadletterqueue.topic.replication.factor=3` trên cluster nhỏ, hoặc thiếu ACL cho `admin.` | Hạ RF về số broker thực tế; cấp `Create`/`Write` cho principal của worker trên topic DLQ |

## ⚠️ Bẫy đề hay gặp

- Thấy "task FAILED" → dễ chọn *"đợi Connect tự khởi động lại"*, nhưng đúng là **task không bao giờ tự restart và không gây rebalance** — phải gọi `restart?includeTasks=true`.
- Thấy "worker chết" → dễ chọn *"phải restart thủ công như task"*, nhưng **worker chết thì Connect tự rebalance**. Hai tình huống này ngược nhau và đề luôn thử trộn lẫn. Đi kèm hai biến thể: *"kill worker 3 phút rồi mà task chưa chuyển → cluster hỏng"* (sai, đó là `scheduled.rebalance.max.delay.ms` **5 phút** đang làm đúng việc) và *"`session.timeout.ms` của worker là 45000"* (sai, đó là số của **consumer**; worker là **10000**).
- Thấy `tasks.max=10` trên topic 4 partition → dễ chọn *"tạo 4 task"* theo công thức `min(tasks.max, partitions)`, nhưng **hầu hết sink connector tạo đủ 10**, trong đó **6 task không giữ partition nào**.
- Thấy "muốn sửa offset của connector" → dễ chọn `PUT /pause`, nhưng `PATCH`/`DELETE /offsets` đòi trạng thái **`STOPPED`**; `PAUSED` bị từ chối.
- Thấy "xoá connector rồi tạo lại để chạy từ đầu" → sai: **`DELETE` không xoá offset**, connector mới cùng tên đọc tiếp từ chỗ cũ.
- Thấy "bật `errors.tolerance=all` là xử lý lỗi xong" → sai, không có DLQ thì record **biến mất im lặng**; và không bật `context.headers.enable` thì DLQ không nói được vì sao lỗi. Biến thể khác: *"source connector cần DLQ"* → sai, **DLQ chỉ tồn tại cho sink**, bảng config source không có key nào `errors.deadletterqueue.*`.
- 🕰️ **Bẫy version:** thấy phương án *"Connect lưu config/offset/status trong znode của ZooKeeper"* hoặc *"worker đăng ký với ZooKeeper để tìm nhau"* → **luôn sai**. Connect **chưa bao giờ** dùng ZooKeeper cho việc này; distributed mode lưu tất cả trong 3 Kafka topic và join nhóm qua giao thức group của Kafka. Kafka 4.x còn không có ZooKeeper.
- 🕰️ **Bẫy version:** thấy *"mọi thay đổi connector làm dừng toàn bộ task trong cluster"* → đó là hành vi **trước Kafka 2.3**. Từ 2.3 (KIP-415) rebalance là **incremental cooperative**, `connect.protocol` mặc định `sessioned`.
- 🕰️ **Bẫy version:** thấy *"`connector.client.config.override.policy` mặc định là `None` nên không cần lo"* → mặc định **là `All` từ Kafka 3.0** (KIP-722). Muốn an toàn phải **chủ động** đặt `Allowlist` (4.2+).
- 🕰️ **Bẫy version:** thấy *"muốn chạy hai version của một connector thì phải dựng hai Connect cluster"* → đúng **trước 4.1**; từ **Kafka 4.1 (KIP-891)** đặt `connector.plugin.version` là đủ.
- Thấy "chỉ worker leader mới nhận được `POST /connectors`" → sai, gọi vào **worker nào cũng được**; follower forward tới leader (vì vậy `rest.advertised.*` phải đúng).
- Thấy "standalone mode vẫn dùng REST để tạo connector" → sai, standalone nhận connector qua **file `.properties` trên dòng lệnh**; REST của standalone chỉ để xem/điều khiển hạn chế.

## 🧪 Lab checklist

- [ ] Lab 6.1 ⭐ — Dựng Connect distributed **2 worker** (8083/8084) trên cluster 3 broker; `kt --describe` xác nhận `connect-configs` 1 partition / `connect-offsets` 25 / `connect-statuses` 5, cả 3 `cleanup.policy=compact`; `GET /connector-plugins` trên **cả hai** worker cho kết quả giống nhau.
- [ ] Lab 6.2 ⭐ — Kill 1 worker, quan sát task chuyển qua `/status` và `task-count`; đo đúng độ trễ `scheduled.rebalance.max.delay.ms`; bật lại worker → rebalance ngược.
- [ ] Lab 6.3 — Sink `tasks.max=6` trên topic 3 partition: `GET /connectors/{n}/tasks` trả **6**, `kcg --describe --members --verbose` cho thấy **3 member không có partition nào**.
- [ ] Lab 6.4 ⭐ — Đẩy record hỏng → task FAILED → đọc `trace` → bật `errors.tolerance=all` + DLQ (`replication.factor` hợp lệ + `context.headers.enable=true`) → `restart?includeTasks=true` → đọc được header `__connect.errors.*` trong DLQ.
- [ ] Lab 6.5 — `GET /offsets` cho cả source và sink; reset sink bằng `kafka-consumer-groups.sh`; reset source bằng `stop → DELETE /offsets → resume`; thử `DELETE /offsets` khi chưa STOPPED để thấy lỗi.
- [ ] Lab 6.6 — Bật policy override trên worker, cho một connector dùng `consumer.override.sasl.jaas.config` riêng; thu hồi quyền của user đó để thấy connector đó chết còn connector khác vẫn chạy.
- [ ] Lab 6.7 — `pause`/`resume` và **rolling restart** 2 worker; đếm record đầu vào và đầu ra để chứng minh không mất dữ liệu.

## 🚪 Cổng tự kiểm tra (phải trả lời trôi chảy mới sang tuần sau)

- **Ba internal topic của Connect: tên config, số partition mặc định, cleanup policy, RF mặc định?**
  **Đáp án gọn:** `config.storage.topic` **1** partition (bắt buộc, không phải mặc định chỉnh được) · `offset.storage.topic` **25** · `status.storage.topic` **5**; cả 3 **compact**; `*.storage.replication.factor` mặc định **3**.
- **Worker chết và task chết — Connect xử lý khác nhau thế nào?**
  **Đáp án gọn:** worker chết → rebalance tự động (sau `session.timeout.ms` 10 s, hoãn tới `scheduled.rebalance.max.delay.ms` 5 phút). Task chết → **không rebalance, không tự restart**; người vận hành gọi `POST /connectors/{n}/restart?includeTasks=true&onlyFailed=true`.
- **`tasks.max=8` cho một sink connector trên topic 3 partition thì có bao nhiêu task, và bao nhiêu task có việc?**
  **Đáp án gọn:** hầu hết sink connector tạo đủ **8** task RUNNING; chỉ **3** task giữ partition, **5** task có `partition-count = 0`. `tasks.max` là trần, không phải `min(tasks.max, partitions)`.
- **Muốn cho một sink connector đọc lại toàn bộ topic từ đầu, làm gì?**
  **Đáp án gọn:** `PUT /connectors/{n}/stop` → `DELETE /connectors/{n}/offsets` → `PUT /connectors/{n}/resume`; hoặc dừng connector rồi `kafka-consumer-groups.sh --group connect-<n> --reset-offsets --to-earliest --topic <t> --execute`. **Xoá connector không xoá offset.**
- **DLQ áp dụng cho loại connector nào, và ba config nào phải khai?**
  **Đáp án gọn:** **chỉ sink**. `errors.tolerance=all` + `errors.deadletterqueue.topic.name` + `errors.deadletterqueue.context.headers.enable=true` (và nhớ hạ `errors.deadletterqueue.topic.replication.factor` trên cluster nhỏ).
- **Làm sao cho một connector dùng credential khác với worker, và mặc định của chính sách đó là gì?**
  **Đáp án gọn:** `consumer.override.*` / `producer.override.*` / `admin.override.*` ở mức connector, bật bằng `connector.client.config.override.policy` ở mức worker. Mặc định Kafka 4.3 là **`All`**; khuyến nghị đặt **`Allowlist`** (4.2+, thành mặc định ở 5.0).
- **Ba metric nào bạn đặt alert đầu tiên cho một Connect cluster production?**
  **Đáp án gọn:** trạng thái `failed` ở `connector-metrics`/`connector-task-metrics`; `offset-commit-failure-percentage` > 0; `deadletterqueue-produce-requests` tăng bất thường (và `deadletterqueue-produce-failures` > 0). Thêm `rebalancing=true` kéo dài nếu muốn cái thứ tư.
- **Vì sao gọi `POST /connectors` vào worker follower vẫn tạo được connector, và cái gì làm nó hỏng?**
  **Đáp án gọn:** follower **forward** request tới leader bằng địa chỉ trong `rest.advertised.host.name`/`.port`/`.listener`. Sai giá trị này thì request treo hoặc lỗi tuỳ worker nào nhận.

## 📎 Tài nguyên tuần này

> 📂 **Đã crawl sẵn tài liệu chính thức vào** [`resources/`](resources/INDEX.md) — 9 file, đọc offline được, có **Gợi ý thứ tự đọc**.

- Apache Kafka Docs 4.3: *Kafka Connect User Guide* (`kafka.apache.org/43/kafka-connect/user-guide/`), *Connect Configs* (`43/generated/connect_config.html`), *Sink/Source Connector Configs* (`43/generated/sink_connector_config.html`, `source_connector_config.html`), *Operations → Monitoring → Connect Monitoring* (`43/operations/monitoring/`), đặc tả REST (`43/generated/connect_rest.yaml`).
- Confluent Docs: *Connect REST Interface* (`docs.confluent.io/platform/current/connect/references/restapi.html`), *Connect Concepts* (`/connect/concepts.html`), *Connect User Guide* (`/connect/userguide.html`), *Connect Security* (`/connect/security.html`).
- Confluent Developer (free): course **Kafka Connect 101** — module *Running Kafka Connect*, *Kafka Connect's REST API*, *Monitoring Kafka Connect*, *Errors and Dead Letter Queues* (`developer.confluent.io/courses/kafka-connect/`).
- KIP: **KIP-415** (incremental cooperative rebalancing cho Connect, 2.3), **KIP-298** (error handling & DLQ, 2.0), **KIP-875** (offset REST + `STOPPED`, 3.5/3.6), **KIP-891** (nhiều version plugin, 4.1), KIP-722 (đổi default override policy sang `All`, 3.0), KIP-618 (exactly-once source, 3.3).
- Sách: *Kafka: The Definitive Guide* 2nd ed. — Chương 7 *Building Data Pipelines* (Connect deep dive) và Chương 12 *Administering Kafka*.
- Ôn lại CCDAK: [Tuần 5 — Connect góc developer](../../../CCDAK/study-plan/week-05/README.md) và [labs Tuần 5](../../../CCDAK/study-plan/week-05/labs.md).

## ✅ Checklist hoàn thành Tuần 6

- [ ] Hoàn thành 4 buổi A/B/C/D
- [ ] Thuộc lòng bảng "PHẢI NHỚ" (**1 / 25 / 5 / RF 3 / 8083 / 60000 / 300000 / 10000**)
- [ ] Vẽ lại được từ trí nhớ **2 bảng**: 3 internal topic (partition · cleanup policy · RF · chứa gì) và trạng thái connector/task → hành động
- [ ] Giải thích được **không cần tra** khác biệt "worker chết" vs "task chết" và vì sao `min(tasks.max, partitions)` là công thức sai
- [ ] Hoàn thành **7/7 lab** (6.1 → 6.7), trong đó 2 lab "gây hỏng rồi sửa" (6.2, 6.4) làm **không nhìn hướng dẫn** ở lần thứ hai
- [ ] Làm xong **28 câu** [questions.md](questions.md), ghi sổ câu sai kèm lý do sai
- [ ] Vượt **Cổng tự kiểm tra** (8 câu) — trả lời miệng, không đọc lại README
- [ ] Đọc hết **🎯 Điểm thi quan trọng** của 9 file trong [`resources/`](resources/INDEX.md)
