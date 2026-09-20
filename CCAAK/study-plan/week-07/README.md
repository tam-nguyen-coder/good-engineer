# 🛠️ Tuần 7 — Observability + Troubleshooting playbook

> **Domain CCAAK:** Observability **10%** + Troubleshooting **15%** = **25% — cụm lớn nhất của đề** · **Thời lượng:** ~11h (4 buổi) · **Vị trí:** Tuần 7/8 — có 🎯 **FULL MOCK #1** (60 câu / 90 phút) ở Buổi D
>
> **Điều hướng:** [⬅️ Tuần 6](../week-06/README.md) · [🏠 Kế hoạch tổng](../../CCAAK-STUDY-PLAN.md) · [Tuần 8 ➡️](../week-08/README.md)

## 🔁 Ôn nhanh từ CCDAK (~20 phút)

Tuần này **dựa hẳn** lên CCDAK Tuần 8. Đọc lại 4 chỗ dưới đây trước khi vào Buổi A — tuần này **không in lại bảng metric**, mà biến chúng thành **playbook chẩn đoán có phương pháp**.

| Khái niệm | File CCDAK cần đọc lại | Vì sao cần cho tuần này |
|---|---|---|
| JMX, MBean naming, JMX Exporter → Prometheus → Grafana | [`week-08/README.md`](../../../CCDAK/study-plan/week-08/README.md) mục A.1 | Tuần này **không dạy lại** cách lấy metric — chỉ dùng nó để dựng **alert rule** và kiểm chứng alert thực sự kêu (Lab 7.1) |
| Bảng metric broker (URP, OfflinePartitions, idle percent, `TotalTimeMs`) | [`week-08/README.md`](../../../CCDAK/study-plan/week-08/README.md) mục A.2–A.3 | Tuần này chuyển từ *"metric này nghĩa là gì"* sang *"thấy metric này thì bấm lệnh nào trước"* |
| Metric client + bảng nguyên nhân lag | [`week-08/README.md`](../../../CCDAK/study-plan/week-08/README.md) mục A.4–A.6 | Thành **cây quyết định lag** (skew → thiếu consumer → rebalance lặp → xử lý chậm) ở Lab 7.4 |
| `docker-compose.monitoring.yml` + rules YAML + Prometheus/Grafana | [`week-08/labs.md`](../../../CCDAK/study-plan/week-08/labs.md) Lab 8.1 | **Dùng lại nguyên file compose đó**; tuần này chỉ thêm 1 file rule alert. Không dựng lại từ đầu |
| Reassignment + rolling restart có throttle | [`week-08/labs.md`](../../../CCDAK/study-plan/week-08/labs.md) Lab 8.4 | Là **hành động sửa** ở cuối nhiều playbook (URP kéo dài, disk lệch) |

> 🧠 Câu chốt của tuần: CCDAK dạy bạn **đọc** metric. CCAAK hỏi bạn **làm gì tiếp theo** khi metric đó lệch — và đề luôn cài sẵn một phương án "đúng nhưng quá tay".

## 🎯 Mục tiêu tuần này

- **Thiết kế được** chiến lược giám sát 3 tầng (cluster health → broker resource → client experience) và nói được mỗi tầng trả lời câu hỏi gì.
- **Thuộc ngưỡng** 4 metric đèn đỏ (`OfflinePartitionsCount`, `ActiveControllerCount`, `UnderReplicatedPartitions`, `UnderMinIsrPartitionCount`) và phân biệt được cái nào **mất độ bền** với cái nào **mất khả năng ghi**.
- **Phân loại được** alert nào đáng gọi dậy lúc 3 giờ sáng và alert nào chỉ cần ticket — rồi **viết đúng `for:`** để chứng minh điều đó bằng cấu hình chứ không bằng lời nói.
- **Chẩn đoán được** 12 kịch bản sự cố theo đúng quy trình **metric → log → config → hành động**, luôn ưu tiên hành động **rẻ và đảo ngược được** trước.
- **Tự tay gây hỏng rồi khôi phục**: URP, OfflinePartition, lag, `advertised.listeners` sai — và đo được thời gian hồi phục.
- **Đọc được** `server.log` / `controller.log` / `state-change.log` / `kafka-authorizer.log`, và chỉnh log level **lúc chạy** không restart.
- **Chốt mốc:** đạt **≥75%** ở **FULL MOCK #1** (60 câu / 90 phút) trước khi sang Tuần 8.

## 📚 Nội dung học chi tiết

### 🅰️ Buổi A — Lý thuyết (~3h)

#### PHẦN I — OBSERVABILITY (10%)

**1. Chiến lược giám sát 3 tầng — khung để không bị chết đuối trong metric**

Một cluster Kafka phát ra hàng nghìn MBean. Người vận hành giỏi không nhìn tất cả; họ chia thành **3 tầng**, mỗi tầng trả lời **đúng một câu hỏi**, và chỉ đi xuống tầng dưới khi tầng trên đã sạch.

| Tầng | Câu hỏi nó trả lời | Metric đại diện | Ai quan tâm |
|---|---|---|---|
| **1 — Cluster health** | *Cluster còn phục vụ được không?* | `OfflinePartitionsCount`, `ActiveControllerCount`, `UnderMinIsrPartitionCount`, `UnderReplicatedPartitions`, `UncleanLeaderElectionsPerSec` | On-call — đây là tầng **duy nhất** được phép gọi dậy lúc 3h sáng |
| **2 — Broker resource** | *Broker có đủ sức không, nghẽn ở đâu?* | `RequestHandlerAvgIdlePercent`, `NetworkProcessorAvgIdlePercent`, `TotalTimeMs` 5 pha, disk free, GC pause, page cache | Người tuning — sinh ticket, không gọi dậy |
| **3 — Client experience** | *Ứng dụng có thấy đau không?* | consumer lag, `records-lead-min`, `produce-throttle-time-avg`, `record-error-rate`, `rebalance-rate-per-hour` | Chủ ứng dụng — thường là nơi **triệu chứng xuất hiện trước tiên** |

- **Nghịch lý phải nhớ:** tầng 3 thường **kêu trước** (ứng dụng báo chậm), nhưng phải chẩn đoán từ **tầng 1 xuống**. Nhảy thẳng vào tối ưu code consumer khi `OfflinePartitionsCount` = 7 là chẩn đoán sai hoàn toàn.
- Ngược lại, tầng 1 sạch trơn mà ứng dụng vẫn kêu → nguyên nhân gần như chắc chắn nằm ở **tầng 3 hoặc phía client**, không phải ở broker.

**2. JMX, MBean naming và KIP-1100 — vì sao dashboard cũ im lặng sau nâng cấp**

- Broker dùng **Yammer Metrics**, client Java dùng **Kafka Metrics**; cả hai expose qua **JMX**. Remote JMX **tắt mặc định** — bật bằng `JMX_PORT`, và production **bắt buộc** đặt auth qua `KAFKA_JMX_OPTS` vì JMX mặc định **không xác thực**.
- Tên MBean: `<domain>:type=<Type>,name=<Name>[,request=…|topic=…|client-id=…]`. Domain theo thành phần: `kafka.server`, `kafka.network`, `kafka.controller`, `kafka.log`, `kafka.producer`, `kafka.consumer`, `kafka.connect`.
- **KIP-1100 (Kafka 4.2)** chuẩn hoá mọi tên về dạng `kafka.COMPONENT:type=…` — ví dụ `org.apache.kafka.server:type=AssignmentsManager,…` đổi thành `kafka.server:type=AssignmentsManager,…`. **Hệ quả vận hành:** sau khi nâng lên 4.2+, panel Grafana viết theo tên legacy sẽ **không có dữ liệu**, và người trực rất dễ chẩn đoán nhầm thành "broker chết". Kiểm chứng bằng `curl :7071/metrics | grep <tên>` chứ không bằng dashboard.
- Production dùng **JMX Exporter chạy dạng Java agent** (`KAFKA_OPTS=-javaagent:<jar>=<port>:<rules.yml>`) thay vì mở remote JMX: docs khuyến nghị agent vì nó *"avoids remote JMX/RMI setup"*. Chỉ MBean **khớp rule** mới được export.

**3. Bốn metric đèn đỏ — BẢNG BẮT BUỘC THUỘC (metric → ngưỡng → nghĩa là gì → hành động đầu tiên)**

| Metric | Ngưỡng docs ghi thẳng | Nghĩa thật sự | Hành động đầu tiên |
|---|---|---|---|
| `kafka.controller:type=KafkaController,name=OfflinePartitionsCount` | **0** — Confluent: *"Alert if value is greater than 0"* | Partition **không có leader** → **không đọc được và không ghi được**. Đây là mất availability toàn phần | Bật lại broker giữ replica của partition đó. Unclean election là **lựa chọn cuối**, đánh đổi bằng mất dữ liệu |
| `kafka.controller:type=KafkaController,name=ActiveControllerCount` | Mỗi node **0 hoặc 1**; **tổng toàn cluster = 1** | Tổng = 0 → không ai điều khiển cluster (mọi thao tác admin treo). Tổng ≥ 2 → split-brain | `kafka-metadata-quorum.sh describe --status`, đọc `LeaderId` và `CurrentVoters` |
| `kafka.server:type=ReplicaManager,name=UnderReplicatedPartitions` | **0** | \|ISR\| < \|replicas\| → **giảm độ bền**, nhưng client **vẫn chạy bình thường** | Kiểm broker còn sống không → nếu follower chỉ đang tụt thì tăng `num.replica.fetchers` (mặc định **1**) |
| `kafka.server:type=ReplicaManager,name=UnderMinIsrPartitionCount` | **0** | \|ISR\| < `min.insync.replicas` → producer `acks=all` **ĐANG BỊ CHẶN** (`NotEnoughReplicasException`) | Khôi phục replica **gấp**. **Không** hạ `min.insync.replicas` trong lúc hoảng loạn — đó là đổi mất dữ liệu lấy availability |

- **Cặp dễ nhầm nhất của đề:** `UnderReplicatedPartitions` > 0 = *"độ bền giảm, dịch vụ vẫn chạy"*; `UnderMinIsrPartitionCount` > 0 = *"ghi đã dừng"*. RF=3 + min.isr=2: mất 1 broker → URP > 0 nhưng UnderMinIsr = **0** (vẫn ghi được); mất 2 broker → **cả hai** > 0.
- `AtMinIsrPartitionCount` > 0 là **cảnh báo sớm**: \|ISR\| = min.isr, chỉ cần thêm **một** sự cố nữa là chặn ghi.
- `UncleanLeaderElectionsPerSec` phải **= 0 tuyệt đối**. Khác 0 nghĩa là cluster đã bầu leader **ngoài ISR** và **đã chấp nhận mất dữ liệu đã ack**.

**4. Metric tài nguyên và `TotalTimeMs` 5 pha — BẢNG: pha nào cao → nút thắt nào**

`RequestHandlerAvgIdlePercent` (io thread) và `NetworkProcessorAvgIdlePercent` (network thread) đều nằm trong khoảng 0–1, docs ghi **"ideally > 0.3"**. Nhưng hai con số này chỉ nói *"đang bận"*; muốn biết **bận ở đâu** thì phải tách `TotalTimeMs`:

```
TotalTimeMs = RequestQueueTimeMs + LocalTimeMs + RemoteTimeMs + ResponseQueueTimeMs + ResponseSendTimeMs
```

| Pha cao bất thường | Nút thắt tương ứng | Hành động | Bẫy |
|---|---|---|---|
| `RequestQueueTimeMs` | Request **xếp hàng chờ io thread** → đi kèm `RequestHandlerAvgIdlePercent` thấp | Tăng `num.io.threads` (mặc định **8**); kiểm `queued.max.requests` (**500**) | Tăng thread khi CPU đã 100% thì **không** giúp — lúc đó phải thêm broker |
| `LocalTimeMs` | **Leader tự xử lý chậm**: ghi log, fsync, disk chậm | Đối chiếu `LogFlushRateAndTimeMs`, disk latency, page cache | Đây là pha duy nhất trỏ thẳng vào **đĩa**, không phải mạng |
| `RemoteTimeMs` với `request=Produce` | Leader **chờ follower ack** khi `acks=all` | Kiểm follower (URP, `num.replica.fetchers`, network liên broker) | **Với `acks=all` thì khác 0 là BÌNH THƯỜNG** — chỉ bất thường khi tăng đột biến |
| `RemoteTimeMs` với `request=FetchConsumer` | Broker **cố ý chờ** đủ `fetch.min.bytes` tới `fetch.max.wait.ms` | **Không làm gì** | Đây là bẫy kinh điển: nhìn thấy số to rồi tưởng broker chậm |
| `ResponseQueueTimeMs` / `ResponseSendTimeMs` | Thiếu **network thread** hoặc mạng tới client chậm | Tăng `num.network.threads` (mặc định **3**); kiểm băng thông | `ResponseSendTimeMs` cao mà `ResponseQueueTimeMs` thấp → lỗi ở **mạng phía client**, không phải broker |

**5. ISR flapping, JVM GC và page cache**

- `IsrShrinksPerSec` / `IsrExpandsPerSec` bình thường **= 0**, trừ lúc broker up/down. Dao động liên tục và **gần bằng nhau** = **ISR flapping**: một follower cứ rớt ra rồi vào lại.
- Ba nguyên nhân thật của flapping, theo thứ tự hay gặp: **GC pause dài** → **disk bão hoà** → **network liên broker**. Ngưỡng rớt ISR là `replica.lag.time.max.ms` = **30000** ms.
- ⚠️ **Hành động SAI mà đề hay cài:** tăng `replica.lag.time.max.ms` để "hết flapping". Đó là **giấu triệu chứng** — follower vẫn chậm, chỉ là bây giờ nó ở trong ISR lâu hơn trước khi bị loại, làm `min.insync.replicas` mất ý nghĩa bảo vệ.
- **JVM:** heap broker **~6 GB** là đủ, dùng **G1GC**. Heap to hơn **không** tốt hơn, vì Kafka đọc/ghi qua **page cache của OS** chứ không qua heap — RAM còn lại để OS làm page cache mới là thứ quyết định throughput đọc. Một broker 64 GB RAM với heap 48 GB sẽ **chậm hơn** chính nó với heap 6 GB.
- Hệ quả chẩn đoán: `LocalTimeMs` tăng dần theo thời gian trong khi disk vẫn nhàn → nghi **page cache bị co lại** (heap quá lớn, hoặc process khác chiếm RAM), không phải nghi đĩa.

**6. Consumer lag — hai con số đều đúng, và một trường hợp không đo được**

| | Lag theo **committed offset** | Lag theo **fetch position** |
|---|---|---|
| Lấy ở đâu | `kafka-consumer-groups.sh --describe` (cột `LAG`), broker-side emitter | Client metric `records-lag-max` (`kafka.consumer:type=consumer-fetch-manager-metrics`) |
| Công thức | `LOG-END-OFFSET − CURRENT-OFFSET` | `LOG-END-OFFSET − position đã fetch` |
| Cập nhật khi nào | Mỗi lần **commit** (auto commit mặc định **5000** ms) | Mỗi lần **fetch** |
| Quan hệ | **Luôn ≥** con số client | Luôn ≤ con số CLI |
| Dùng để | Alert vận hành, báo cáo | Chẩn đoán "consumer đang fetch kịp không" |

- Chênh lệch giữa hai số **không phải lỗi** — nó chính bằng lượng record đã fetch nhưng chưa commit. Đề dùng chi tiết này để bẫy.
- **Không đo được lag cho consumer dùng `assign()`** — docs Confluent nói thẳng: coordinator không quản lý assignment cho consumer standalone, nên chúng **không xuất hiện** trong `kafka-consumer-groups.sh`. Ứng dụng kiểu này phải tự đẩy metric ra.
- Broker-side emitter của Confluent Platform mặc định tính lại mỗi **60000** ms → alert lag đặt `for:` ngắn hơn 2 chu kỳ là alert trên dữ liệu cũ.
- **`records-lead-min` → 0** là cảnh báo sớm khác hẳn lag: nó nói *"retention sắp xoá record trước khi consumer kịp đọc"*. `records-lag-max` không cho biết điều này, vì lag lớn mà retention dài thì vẫn an toàn.
- `CONSUMER-ID` = `-` trong output `--describe` nghĩa là **không member nào đang giữ partition đó** (group rỗng hoặc đang rebalance), chứ không phải lag = 0.

**7. Thiết kế alert — BẢNG: cái gì gọi dậy lúc 3 giờ sáng, cái gì chỉ cần ticket**

Triết lý Prometheus: *"keep alerting simple, alert on symptoms… avoid having pages where there is nothing to do."* Với Kafka, ranh giới rất rõ: **gọi dậy khi mất đọc/ghi hoặc khi không kịp cứu**; **tạo ticket khi chỉ giảm biên an toàn**.

| Điều kiện | Mức | `for:` gợi ý | Vì sao |
|---|---|---|---|
| `sum(OfflinePartitionsCount) > 0` | 🔴 **PAGE** | `1m` | Mất cả đọc lẫn ghi. Không có cách nào "tự khỏi" |
| `sum(ActiveControllerCount) != 1` | 🔴 **PAGE** | `2m` | 0 = control plane chết; ≥2 = split-brain. `for: 2m` để bỏ qua failover bình thường |
| `UnderMinIsrPartitionCount > 0` | 🔴 **PAGE** | `2m` | Producer `acks=all` đang bị chặn — ứng dụng **đang** lỗi |
| Disk free < 15% trên bất kỳ `log.dirs` | 🔴 **PAGE** | `5m` | Docs Prometheus: capacity *"often requires human intervention to avoid an outage"*. Disk đầy → broker chết, và sửa **không** nhanh |
| `UncleanLeaderElectionsPerSec > 0` | 🔴 **PAGE** | `0s` | Đã mất dữ liệu rồi. Cần điều tra ngay, không chờ |
| `UnderReplicatedPartitions > 0` | 🟡 **TICKET** | **`10m`** | URP vài phút lúc rolling restart là **bình thường**. `for: 10m` chính là ranh giới giữa "đang bảo trì" và "hỏng thật" |
| `RequestHandlerAvgIdlePercent < 0.3` | 🟡 **TICKET** | `15m` | Vấn đề capacity, không phải outage |
| `IsrShrinksPerSec > 0` liên tục | 🟡 **TICKET** | `15m` + `keep_firing_for: 5m` | Flapping cần `keep_firing_for` để alert không tự tắt giữa hai nhịp dao động |
| Consumer lag > N | 🟡 **TICKET** | `≥ 5m` | Ngưỡng phải rộng hơn **2 chu kỳ** tính lag (emitter 60 s) |
| Prometheus/JMX exporter target `up == 0` | 🔴 **PAGE** | `5m` | **Metamonitoring**: hệ giám sát chết thì mọi alert Kafka đều im — đó là **im lặng giả** |

- **Ba nguyên tắc chống alert fatigue:** (1) alert vào **triệu chứng** (`OfflinePartitions`) chứ không vào mọi nguyên nhân; (2) mọi alert phải có **runbook_url** trong annotation trỏ tới playbook — alert không có hành động kèm theo thì phải xoá; (3) dùng `for:` chứ **không** nâng ngưỡng: nâng ngưỡng làm mất sự cố thật, `for:` chỉ lọc nhiễu thời gian.
- Trạng thái Prometheus: điều kiện đúng nhưng chưa đủ `for:` → **`pending`**; đủ rồi → **`firing`**. Alert không có `for:` thì firing ngay lần đánh giá đầu tiên.

**8. Log của broker — đọc cái nào, khi nào**

| File | Chứa gì | Đọc khi nào | Ghi chú |
|---|---|---|---|
| `server.log` | Hoạt động chung của broker, startup, lỗi listener, lỗi disk | **Mặc định bắt đầu ở đây** | Level mặc định `INFO` |
| `controller.log` | Quorum, bầu leader, đăng ký/fence broker | Controller bất thường, broker không join | *"Any ERROR, FATAL or WARN in this log indicates an important event"* |
| `state-change.log` | **Mọi** thay đổi leader/ISR/partition do controller ra lệnh | Truy vết **chính xác** khi nào partition đổi leader | Level mặc định **TRACE** — rất chi tiết |
| `kafka-authorizer.log` | Quyết định ACL | `TopicAuthorizationException` / `GroupAuthorizationException` | DENIED ở INFO; **ALLOWED phải bật DEBUG** mới thấy |
| `kafka-request.log` | Mọi request, kèm latency (DEBUG) và nội dung (TRACE) | Chỉ khi đã khoanh vùng | **Cực nặng** — bật vài chục giây rồi tắt |

- Kafka 4.0 chuyển sang **Log4j2** (`config/log4j2.yaml`, thay log4j 1.x). `KafkaLog4jAppender` đã bị gỡ.
- **Đổi log level lúc chạy, không restart:**
  ```bash
  kafka-configs.sh --bootstrap-server … --describe --entity-type broker-loggers --entity-name 2
  kafka-configs.sh --bootstrap-server … --alter  --entity-type broker-loggers --entity-name 2 \
      --add-config kafka.request.logger=DEBUG
  kafka-configs.sh --bootstrap-server … --alter  --entity-type broker-loggers --entity-name 2 \
      --delete-config kafka.request.logger
  ```
  `--entity-name` là **node id**, và thay đổi **không bền qua restart** (broker quay về level trong `log4j2.yaml`) — đó lại là tính năng tốt: quên tắt DEBUG thì lần restart sau tự sạch.
- ⚠️ **Bẫy chữ nghĩa:** `log.dirs` là nơi chứa **dữ liệu partition**; thư mục log ứng dụng là `/var/log/kafka` (RPM/Deb) hoặc `$base_dir/logs` (tar). Đề hỏi "đổi chỗ ghi `server.log`" mà chọn `log.dirs` là sai.

#### PHẦN II — TROUBLESHOOTING (15%): PLAYBOOK

**9. Quy trình 4 bước — áp cho MỌI sự cố**

```
① METRIC  → tầng 1 trước (còn leader không? controller còn không?), rồi tầng 2, rồi tầng 3
② LOG     → server.log → controller.log / state-change.log → kafka-authorizer.log (nếu là lỗi quyền)
③ CONFIG  → kafka-configs.sh --describe --all, đọc cột synonyms để biết giá trị đến TỪ ĐÂU
④ HÀNH ĐỘNG → rẻ & đảo ngược được TRƯỚC; một chiều & mất mát SAU CÙNG
```

**Thang "rẻ và đảo ngược được"** — đề CCAAK gần như luôn hỏi bước nào làm **trước**:

| Bậc | Ví dụ hành động | Đảo ngược được? |
|---|---|---|
| 1 — Miễn phí | Đọc metric, đọc log, `--describe`, `describe --status` | ✔️ Không đổi gì |
| 2 — Rẻ | Bật lại broker đã tắt, preferred leader election, thêm consumer instance | ✔️ |
| 3 — Có chi phí | Tăng `num.replica.fetchers` / `num.io.threads` (restart broker), reassignment có throttle | ✔️ nhưng tốn thời gian |
| 4 — **Một chiều** | **Tăng partition** (không giảm được, phá ordering theo key) | ❌ |
| 5 — **Mất mát** | `unclean.leader.election.enable=true`, hạ `min.insync.replicas`, xoá log dir | ❌ Mất dữ liệu |

> 📌 Mọi câu hỏi dạng *"what should the administrator do FIRST?"* đều đang kiểm tra bạn có nhảy cóc xuống bậc 4–5 hay không.

**10. Playbook 12 kịch bản**

**① `UnderReplicatedPartitions` > 0 kéo dài**
Metric: URP > 0 nhưng `OfflinePartitionsCount` = 0 → vẫn còn leader, chỉ giảm độ bền. Kiểm `ActiveBrokerCount` xem có broker nào biến mất. → Log: `server.log` của broker tụt, tìm GC pause / `KafkaStorageException`. → Config: `num.replica.fetchers` (**1**), `replica.lag.time.max.ms` (**30000**). → Hành động: broker chết thì **bật lại** (bậc 2); broker sống mà follower không đuổi kịp thì **tăng `num.replica.fetchers`** (bậc 3). **Không** tăng `replica.lag.time.max.ms` — đó là giấu triệu chứng.

**② `OfflinePartitionsCount` > 0**
Metric: partition **không có leader**. → `kafka-topics.sh --describe --under-min-isr-partitions` và `--unavailable-partitions` để biết chính xác partition nào. → Log: `state-change.log` cho biết leader cuối cùng là ai. → Hành động: **bật lại broker giữ replica** đó (bậc 2). Nếu broker đó mất vĩnh viễn: cân nhắc **ELR** (KIP-966, bật mặc định cho cluster mới từ 4.1) trước; `kafka-leader-election.sh --election-type unclean` là **bậc 5**, chỉ dùng khi chấp nhận mất dữ liệu và đã ghi vào sự cố.

**③ ISR flapping**
Metric: `IsrShrinksPerSec` và `IsrExpandsPerSec` dao động, **gần bằng nhau**, URP nhấp nháy quanh 0. → Log: GC log của broker (pause > vài trăm ms), `LogFlushRateAndTimeMs`. → Hành động: sửa **nguyên nhân** — giảm heap nếu GC dài, đổi đĩa nếu fsync chậm, kiểm mạng liên broker. Tăng `replica.lag.time.max.ms` là **đáp án sai được cài sẵn**.

**④ Controller không bầu được / `ActiveControllerCount` = 0**
Metric: tổng `ActiveControllerCount` = 0, `LastAppliedRecordLagMs` trên broker tăng không ngừng. → `kafka-metadata-quorum.sh describe --status`: `LeaderId` = **-1** hoặc `LeaderEpoch` nhảy liên tục. → Kiểm số controller còn sống so với **quy tắc đa số**: quorum 3 chịu mất **1**, quorum 5 chịu mất **2**. Mất đa số → **control plane đóng băng** nhưng **data plane vẫn phục vụ** produce/fetch cho partition không cần đổi leader. → Log: `controller.log`. → Hành động: **khôi phục đủ số controller** cho lại đa số. Đây là lý do quorum phải **lẻ** (3 hoặc 5) và controller nên **tách riêng** khỏi broker.

**⑤ Broker không join được cluster**
Ba nguyên nhân, phân biệt bằng **đúng dòng log**:

| Log/triệu chứng | Nguyên nhân gốc | Sửa |
|---|---|---|
| `InconsistentClusterIdException: The Cluster ID X doesn't match stored clusterId Y` | `meta.properties` có cluster id khác cluster | Format lại storage với **đúng** `cluster.id` (`kafka-storage.sh format --cluster-id …`); **không** xoá bừa `log.dirs` của broker đang có dữ liệu |
| Broker start rồi treo, `controller.log` không thấy `Registered broker` | Listener/`controller.quorum.voters` sai, không tới được controller | Đối chiếu `controller.listener.names`, `controller.quorum.voters`, firewall cổng **9093** |
| `java.net.BindException: Address already in use` | Port trùng (rất hay gặp khi bật thêm listener hoặc JMX/exporter) | Đổi port; nhớ `KAFKA_OPTS` javaagent áp cho **mọi** script trong `bin/` |

**⑥ Disk đầy / `KafkaStorageException` / log dir offline**
Metric: disk free giảm dần; broker log `KafkaStorageException`; partition trên đĩa đó **offline** (JBOD: chỉ đĩa hỏng bị ảnh hưởng, các đĩa còn lại vẫn chạy). → Chẩn đoán: `kafka-log-dirs.sh --describe --bootstrap-server …` xem phân bố dung lượng theo từng log dir. → Hành động theo thứ tự: (1) **hạ `retention.ms` tạm thời** cho topic to nhất — nhanh và đảo ngược được; (2) reassignment **có throttle** sang broker khác; (3) `cordoned.log.dirs` để chặn partition mới rơi vào đĩa sắp rút, rồi mới sửa `log.dirs` + restart. Nhớ rằng **segment active không bao giờ bị xoá** — retention 1 giờ mà data vẫn còn thì hạ `segment.ms`/`segment.bytes`.

**⑦ Consumer lag tăng — CÂY QUYẾT ĐỊNH (thứ tự này chính là câu hỏi đề)**
```
Lag tăng?
├─ Lag chỉ ở 1–2 partition, các partition khác = 0
│     → KEY SKEW / hot partition. Thêm consumer KHÔNG giúp. Sửa key / partitioner
├─ Lag đều, mọi consumer đều có partition, assigned-partitions lệch nhau
│     → THIẾU CONSUMER. Thêm instance (tối đa = số partition) ← rẻ, đảo ngược được
├─ Lag răng cưa, rebalance-rate-per-hour cao, log "group is rebalancing"
│     → REBALANCE LẶP. Xem ⑧
└─ Lag đều, đủ consumer, poll-idle-ratio-avg ≈ 0
      → XỬ LÝ CHẬM. Tối ưu code / giảm max.poll.records; tăng partition là BẬC 4
```
Kiểm tra bắt buộc trước khi kết luận: `kcg --describe --members --verbose` (xem có consumer nào `assigned-partitions = 0` không → dư consumer) và `records-lead-min` (→ 0 nghĩa là **sắp mất dữ liệu**, phải tăng retention tạm thời **ngay**, song song với việc scale).

**⑧ Rebalance liên tục**
Triệu chứng: log client `Attempt to heartbeat failed since group is rebalancing`, `CommitFailedException`, hoặc `Member … sending LeaveGroup request … due to consumer poll timeout has expired`. → Nguyên nhân số một: xử lý một vòng `poll()` vượt **`max.poll.interval.ms`** (**300000** ms) — **heartbeat vẫn đều** nên `session.timeout.ms` không phải thủ phạm. → Hành động: giảm `max.poll.records` (**500**) trước (rẻ nhất), rồi mới tăng `max.poll.interval.ms`; rolling restart gây rebalance thì dùng **static membership** (`group.instance.id`) hoặc `group.protocol=consumer` (KIP-848).

**⑨ Produce timeout / `NotEnoughReplicas` / `TimeoutException`**
Phân biệt bằng **nội dung exception**, không đoán:

| Exception client | Nguyên nhân gốc | Hành động của admin |
|---|---|---|
| `NotEnoughReplicasException` | \|ISR\| < `min.insync.replicas` với `acks=all` | Khôi phục replica. Đây là **đúng thiết kế** — thà chặn ghi còn hơn mất dữ liệu |
| `TimeoutException: Expiring N record(s) … since batch creation` | Hết `delivery.timeout.ms`; broker chậm/unreachable | Kiểm URP, `TotalTimeMs`, `advertised.listeners` |
| `TimeoutException: Topic … not present in metadata after … ms` | Client không lấy được metadata | Bootstrap sai, topic chưa tồn tại, hoặc ACL thiếu `Describe` |
| `NotLeaderOrFollowerException` | Leader vừa đổi, metadata client cũ | **Không làm gì** — client tự refresh và retry |

**⑩ Throughput bị chặn trần, log hoàn toàn sạch**
Không có exception, không có lỗi, throughput cứ đụng một con số rồi đứng → gần như chắc chắn là **quota**. → Metric: `produce-throttle-time-avg` / `fetch-throttle-time-avg` > 0 phía client; broker có `byte-rate` và `throttle-time` theo quota. → Config: `kafka-configs.sh --describe --entity-type clients|users` xem `producer_byte_rate`, `consumer_byte_rate`, `request_percentage`. → Hành động: nâng quota cho principal đó, hoặc giải thích cho chủ ứng dụng — **không** đi tune `num.io.threads`.

**⑪ Client nối bootstrap được nhưng produce timeout**
Đây là triệu chứng **rất đặc trưng**: `bootstrap.servers` kết nối OK, `kafka-topics.sh --list` chạy được, nhưng produce/consume timeout. → Nguyên nhân: **`advertised.listeners` trả về địa chỉ client không tới được**. Client lấy metadata từ bootstrap, rồi kết nối **thẳng tới leader** bằng địa chỉ broker **tự khai** — nếu đó là hostname nội bộ Docker/Kubernetes thì client bên ngoài chết ở bước hai. → Log: client báo timeout tới một host lạ hoắc; broker `server.log` không thấy produce request nào. → Hành động: sửa `advertised.listeners` cho từng listener sao cho **địa chỉ client gõ được**; nhớ `listener.security.protocol.map` phải phủ đủ tên listener.

**⑫ "Topic xoá rồi mà vẫn còn" / offset ngoài vùng**
Hai trường hợp hay bị gộp nhầm:
- *Xoá topic nhưng consumer vẫn lỗi:* offset đã commit trong `__consumer_offsets` **không bị xoá ngay** theo topic; group khởi động lại có thể trỏ vào offset không còn tồn tại → `OffsetOutOfRangeException`, rồi rơi vào `auto.offset.reset`. Sửa: `kafka-consumer-groups.sh --delete-offsets` hoặc reset có chủ đích.
- *Xoá topic nhưng thư mục vẫn còn:* `delete.topic.enable` (mặc định **true** ở 4.x) và việc xoá là **bất đồng bộ** — thư mục đổi tên thành `<topic>-<partition>.<uuid>-delete` trước khi biến mất.

**11. Exception cheat-sheet góc admin — BẢNG: exception → nguyên nhân gốc → hành động**

| Exception | Nhìn thấy ở đâu | Nguyên nhân gốc | Hành động của admin |
|---|---|---|---|
| `NotEnoughReplicasException` | Producer | \|ISR\| < `min.insync.replicas`, `acks=all` | Khôi phục broker/replica. **Không** hạ min.isr |
| `NotLeaderOrFollowerException` | Producer/Consumer | Leader vừa đổi (retriable) | Không làm gì; client tự retry |
| `LeaderNotAvailableException` | Cả hai | Đang bầu leader (topic mới, broker vừa chết) | Chờ; nếu kéo dài → xem ② |
| `KafkaStorageException` | Broker `server.log` | Log dir lỗi/đầy → đĩa bị đánh dấu offline | Thay/giải phóng đĩa; JBOD thì chỉ partition trên đĩa đó offline |
| `InconsistentClusterIdException` | Broker khi start | `meta.properties` sai cluster id | Format lại đúng `cluster.id`; xem ⑤ |
| `BindException: Address already in use` | Broker khi start | Trùng port (listener hoặc JMX/exporter) | Đổi port; kiểm `KAFKA_OPTS`/`JMX_PORT` đang export trong shell |
| `OffsetOutOfRangeException` | Consumer | Offset đã bị retention xoá hoặc topic tạo lại | `auto.offset.reset`, hoặc reset offset có chủ đích |
| `UnknownTopicOrPartitionException` | Cả hai | Topic chưa tồn tại / metadata cũ / `auto.create.topics.enable=false` | Tạo topic; kiểm tên và ACL `Describe` |
| `TopicAuthorizationException` | Client | Thiếu ACL trên **topic** | `kafka-acls.sh --add --producer/--consumer`; bật `kafka-authorizer.log` |
| `GroupAuthorizationException` | Client | Thiếu ACL `Read` trên resource **Group** | Cấp ACL Group — lỗi rất hay bị sửa nhầm sang topic |
| `TimeoutException` (batch expiring) | Producer | Broker chậm/unreachable, ISR thiếu | Xem ⑨ |
| `CommitFailedException` | Consumer | Group đã rebalance, partition đổi chủ | Xem ⑧ |
| `RecordTooLargeException` | Producer | Vượt `message.max.bytes` (**1048588**) / `max.request.size` | Nâng cả broker + topic + client, hoặc nén |
| `InvalidReplicationFactorException` | Admin/CLI | RF > số broker sống | Sửa lệnh; cluster 1 broker phải hạ RF internal topic xuống 1 |

### 🅱️ Buổi B — Hands-on (~3.5h)

> 🧪 **Lab cầm tay chỉ việc (từng bước + lệnh):** [labs.md](labs.md). Dùng lại cluster 3 broker + 1 controller của [CCDAK Tuần 1](../../../CCDAK/study-plan/week-01/labs.md) và `docker-compose.monitoring.yml` của [CCDAK Tuần 8](../../../CCDAK/study-plan/week-08/labs.md). Tuần này là **tuần chẩn đoán**: 5 trong 7 lab là dạng **"gây hỏng rồi sửa"**.

- **Lab 7.1 ⭐ — Alert rule cho 4 metric đèn đỏ:** thêm `prometheus/alerts.yml` vào stack có sẵn, kiểm chứng alert **thực sự chuyển pending → firing**, không chỉ "viết ra cho đẹp".
- **Lab 7.2 ⭐ — Gây URP:** tắt 1 broker, xem alert kêu, **đo thời gian URP về 0**, tăng `num.replica.fetchers` rồi đo lại để thấy con số thay đổi.
- **Lab 7.3 ⭐ — Gây OfflinePartition:** topic RF=1 rồi tắt đúng broker giữ partition đó → `OfflinePartitionsCount` > 0 → khôi phục và so sánh với trường hợp RF=3.
- **Lab 7.4 ⭐ — Gây lag rồi chạy đúng cây quyết định:** dựng cả 3 tình huống (skew / thiếu consumer / rebalance lặp) và phân biệt chúng **chỉ bằng dữ liệu quan sát được**.
- **Lab 7.5 — `advertised.listeners` sai:** bootstrap OK nhưng produce timeout → đọc log tìm ra → sửa.
- **Lab 7.6 — Đọc log có phương pháp:** đổi log level lúc chạy bằng `--entity-type broker-loggers`, theo dõi `state-change.log` trong lúc leader election.
- **Lab 7.7 — Bài tập tổng hợp:** script phá cluster ngẫu nhiên 1 trong 4 cách, bạn chẩn đoán bằng playbook rồi sửa (đáp án in ở cuối lab).

### 🅲️ Buổi C — Bổ sung (~2.5h)

**Bảng quyết định 1 — "Tôi có 60 giây, nhìn gì trước?"**

| Thứ tự | Lệnh / panel | Loại trừ được gì |
|---|---|---|
| 1 | `sum(OfflinePartitionsCount)` và `sum(ActiveControllerCount)` | Sự cố tầng 1. Nếu ≠ 0 / ≠ 1 thì **dừng mọi việc khác** |
| 2 | `kafka-metadata-quorum.sh describe --status` | Control plane còn sống không (`LeaderId` ≠ -1) |
| 3 | `kafka-topics.sh --describe --under-replicated-partitions` | Partition nào đang thiếu replica, trên broker nào |
| 4 | `RequestHandlerAvgIdlePercent` + `TotalTimeMs` 5 pha | Nghẽn tài nguyên và nghẽn **ở pha nào** |
| 5 | `kafka-consumer-groups.sh --describe --all-groups` | Phía client có ai đang đau không |
| 6 | `kafka-log-dirs.sh --describe` | Disk lệch hay sắp đầy |

**Bảng quyết định 2 — "Metric này lệch thì SỬA CÁI GÌ, và KHÔNG sửa cái gì"**

| Quan sát | ✅ Làm | ❌ Đừng làm (đáp án bẫy) |
|---|---|---|
| URP > 0 sau khi 1 broker chết | Bật lại broker; nếu cần thì tăng `num.replica.fetchers` | Tăng `replica.lag.time.max.ms`; hạ RF |
| `UnderMinIsrPartitionCount` > 0 | Khôi phục replica | **Hạ `min.insync.replicas` xuống 1** — mất bảo vệ đúng lúc cần nhất |
| `OfflinePartitionsCount` > 0 | Bật lại broker giữ replica; cân nhắc ELR | Bật `unclean.leader.election.enable` ngay lập tức |
| ISR flapping | Sửa GC / disk / network | Nới `replica.lag.time.max.ms` |
| Lag tăng ở **1** partition | Sửa key/partitioner | Thêm consumer (không giúp), tăng partition (một chiều) |
| `RemoteTimeMs` cao ở `FetchConsumer` | Không làm gì | Tăng `num.io.threads` |
| Throughput trần, log sạch | Kiểm quota | Tune thread, thêm broker |
| Client bootstrap OK nhưng produce timeout | Sửa `advertised.listeners` | Tăng `request.timeout.ms` |

**So sánh nhanh — 3 công cụ trả lời "partition đang ở đâu"**

| Công cụ | Trả lời | Khi nào dùng |
|---|---|---|
| `kafka-topics.sh --describe --under-replicated-partitions / --unavailable-partitions / --under-min-isr-partitions` | Partition nào đang lệch, theo góc nhìn **metadata hiện tại** | Bước chẩn đoán đầu tiên, luôn dùng |
| `kafka-log-dirs.sh --describe` | Partition nằm trên **log dir nào**, chiếm bao nhiêu byte | Disk lệch, disk đầy, JBOD |
| `kafka-dump-log.sh --cluster-metadata-decoder` / `kafka-metadata-shell.sh` | Controller **nghĩ** partition đang ở đâu | Khi metadata và thực tế mâu thuẫn — bậc cuối |

**Đọc thêm (30–40 phút):** *Kafka: The Definitive Guide* 2nd ed. chương **13 — Monitoring Kafka** (bảng metric, request latency) và chương **12 — Administering Kafka**; trang [Prometheus Alerting best practices](https://prometheus.io/docs/practices/alerting/); [`resources/prometheus-alerting-rules.md`](resources/prometheus-alerting-rules.md) phần `for:` / `keep_firing_for:`.

### 🅳 Buổi D — Practice + Review (~2h) — 🎯 FULL MOCK #1

> 📝 **Bộ câu hỏi của tuần:** [questions.md](questions.md) — đáp án & giải thích: [answers.md](answers.md). *(tiếng Anh, văn phong CCAAK.)*

1. Làm **30 câu** của tuần (~45 phút), ghi sổ câu sai, phân loại: metric/ngưỡng · alert design · playbook · log · exception.
2. **🎯 FULL MOCK #1 — 60 câu / 90 phút, bấm giờ, không tra tài liệu.** Lấy từ [`CCAAK/mock-exams/`](../../mock-exams/README.md). Đây là lần đầu bạn chạy đúng format thi thật: **90 giây/câu**.
3. **Chấm theo 7 domain**, không chỉ chấm điểm tổng:

   | Domain | Tỉ trọng | Số câu ~/60 | Đúng | % |
   |---|---|---|---|---|
   | CFG — Cluster Configuration | 22% | 13 | ___ | ___ |
   | FUND — Fundamentals | 15% | 9 | ___ | ___ |
   | SEC — Security | 15% | 9 | ___ | ___ |
   | TROUBLE — Troubleshooting | 15% | 9 | ___ | ___ |
   | ARCH — Deployment Architecture | 12% | 7 | ___ | ___ |
   | CONNECT — Kafka Connect | 12% | 7 | ___ | ___ |
   | OBS — Observability | 10% | 6 | ___ | ___ |

4. **Đọc kết quả:**

   | Điểm | Ý nghĩa | Việc làm ngay |
   |---|---|---|
   | **≥80%** | Đã chạm ngưỡng đăng ký thi | Review 100% câu sai; cần **≥3 bộ mock khác nhau ≥80%** mới đặt lịch |
   | **75–79%** | **Đủ an toàn để sang Tuần 8** | Xác định 2 domain thấp nhất, ôn lại đúng tuần đó trong Tuần 8 |
   | **70–74%** | Còn lỗ hổng rõ | Vẫn sang Tuần 8 nhưng dành thêm 1 buổi cho domain yếu nhất |
   | **<70%** | **Van an toàn: lùi lịch thi 1 tuần** | Học lại Buổi A + B của 2 domain điểm thấp nhất trước khi mock lại |

5. **Spaced repetition:** flashcard các con số của tuần (0 / 0 / 1 / 0.3 / 5 pha / 30 s / 60 s / 300 s) theo mốc **1 / 3 / 7 ngày**.

## 🧠 PHẢI NHỚ tuần này

| Fact | Con số / Ghi nhớ |
|---|---|
| 4 metric đèn đỏ | `OfflinePartitionsCount` **0** · `UnderMinIsrPartitionCount` **0** · `UnderReplicatedPartitions` **0** · `ActiveControllerCount` tổng cụm **= 1** (mỗi node 0 **hoặc** 1) |
| URP vs UnderMinIsr | URP > 0 = **giảm độ bền, vẫn chạy**; UnderMinIsr > 0 = producer `acks=all` **đang bị chặn**. RF 3 / min.isr 2: mất **1** broker → URP > 0 nhưng UnderMinIsr **= 0**; mất **2** broker → cả hai > 0 |
| 3 alert Confluent nêu là tối thiểu | `ActiveControllerCount` ≠ 1 (**tổng**) · `OfflinePartitionsCount` > 0 · `UncleanLeaderElectionsPerSec` ≠ 0 |
| Idle percent | `RequestHandlerAvgIdlePercent` / `NetworkProcessorAvgIdlePercent` **ideally > 0.3**; io thread mặc định **8**, network thread **3** |
| `TotalTimeMs` = 5 pha | `RequestQueue` (io thread) + `Local` (đĩa) + `Remote` (follower ack / fetch wait) + `ResponseQueue` (network thread) + `ResponseSend` (mạng client) |
| `RemoteTimeMs` | Cao với `Produce` + `acks=all` = **bình thường**; cao với `FetchConsumer` = **bình thường** (chờ `fetch.min.bytes`) |
| ISR & JVM | `replica.lag.time.max.ms` **30000** ms; flapping = sửa GC/disk/network, **không** nới ngưỡng. Heap broker **~6 GB** + **G1GC**; **page cache quan trọng hơn heap** |
| Lag: 2 con số | CLI theo **committed** (auto commit **5000** ms) ≥ client `records-lag-max` theo **position**. Chênh lệch **không phải lỗi** |
| Lag không đo được | Consumer dùng **`assign()`** — coordinator không quản lý assignment |
| `records-lead-min` → 0 | **Sắp mất dữ liệu** vì retention xoá trước khi đọc kịp. Emitter lag Confluent tính lại mỗi **60000** ms → `for:` phải ≥ 2 chu kỳ |
| Alert PAGE | OfflinePartitions · ActiveControllerCount ≠ 1 · UnderMinIsr · disk sắp đầy · unclean election · monitoring chết |
| Alert TICKET | URP (`for: 10m`) · idle % thấp · ISR flapping (`keep_firing_for`) · lag tăng nhẹ |
| `for:` vs ngưỡng | `for:` lọc **nhiễu thời gian** và giữ alert ở trạng thái **pending**; nâng ngưỡng làm **mất sự cố thật** |
| 4 file log | `server.log` · `controller.log` (mọi WARN/ERROR đáng xem) · `state-change.log` (mặc định **TRACE**) · `kafka-authorizer.log` (DENIED ở INFO) |
| Log level lúc chạy | `kafka-configs.sh --alter --entity-type broker-loggers --entity-name <node.id>`; **không bền qua restart**; Kafka 4.0 dùng **log4j2** |
| Quy trình chẩn đoán | **metric → log → config → hành động**, và **rẻ + đảo ngược được TRƯỚC**. Bậc 4–5 phải tránh: tăng partition (**một chiều**) · unclean election · hạ `min.insync.replicas` |
| Quorum | 3 controller chịu mất **1**, 5 chịu mất **2** (**2N+1**); mất đa số → control plane **đóng băng**, data plane **vẫn chạy** |
| Cây quyết định lag | skew (1 partition) → thiếu consumer → rebalance lặp → xử lý chậm. Rebalance lặp: thủ phạm số 1 là vượt `max.poll.interval.ms` (**300000** ms) → giảm `max.poll.records` (**500**) trước |
| KIP-1100 (4.2) | Tên MBean chuẩn hoá về `kafka.COMPONENT:type=…` → **dashboard cũ mất dữ liệu** sau nâng cấp |
| Graceful shutdown | `controlled.shutdown.enable` **true**; chỉ thành công khi mọi partition còn **≥1 replica sống** → rolling restart phải chờ URP về 0 |

## 🚨 Playbook: triệu chứng → hành động

| Triệu chứng quan sát được | Nguyên nhân khả dĩ | Hành động đầu tiên |
|---|---|---|
| `OfflinePartitionsCount` > 0 | Mất **mọi** replica có thể làm leader | Bật lại broker giữ replica; ELR trước, unclean election là **cuối cùng** |
| Tổng `ActiveControllerCount` = 0, thao tác admin treo nhưng produce/fetch vẫn chạy | Mất đa số quorum → control plane đóng băng | `kafka-metadata-quorum.sh describe --status`, khôi phục đủ controller cho lại đa số |
| `UnderMinIsrPartitionCount` > 0, producer báo `NotEnoughReplicas` | \|ISR\| < `min.insync.replicas` | Khôi phục replica. **Không** hạ min.isr |
| URP > 0 suốt 30 phút, mọi broker đều sống | Follower không đuổi kịp | Tăng `num.replica.fetchers` (mặc định **1**); kiểm GC/disk của follower |
| `IsrShrinksPerSec` ≈ `IsrExpandsPerSec` > 0 liên tục | GC pause / disk chậm / network | Đọc GC log + `LogFlushRateAndTimeMs`; **không** nới `replica.lag.time.max.ms` |
| Broker start rồi tắt ngay: `InconsistentClusterIdException` / `BindException` / không thấy `Registered broker` | Sai `cluster.id` · trùng port · listener hoặc `controller.quorum.voters` sai | Đọc **đúng dòng log** rồi mới sửa: format lại đúng `cluster.id` / đổi port / sửa listener |
| `server.log` báo `KafkaStorageException`, một số partition offline | Log dir hỏng/đầy | `kafka-log-dirs.sh --describe`; hạ retention tạm thời; `cordoned.log.dirs` trước khi rút đĩa |
| `RequestQueueTimeMs` cao + `RequestHandlerAvgIdlePercent` < 0.3 | Thiếu io thread | Tăng `num.io.threads` (**8**) — nếu CPU đã bão hoà thì thêm broker. *(Nhưng `RemoteTimeMs` cao với `FetchConsumer` là **bình thường** — không làm gì)* |
| Lag chỉ tăng ở 1 partition, các partition khác bằng 0 | Key skew / hot partition | Sửa key hoặc partitioner; thêm consumer **không** giúp |
| Lag răng cưa + log `group is rebalancing`; hoặc `records-lead-min` tiến về 0 | Vượt `max.poll.interval.ms` (**300000** ms); hoặc retention sắp xoá record chưa đọc | Giảm `max.poll.records` trước (static membership cho rolling restart); nếu lead → 0 thì tăng `retention.ms` **tạm thời** NGAY rồi mới scale |
| Throughput đụng trần, không lỗi, log sạch | Quota | Xem `produce-throttle-time-avg`; `kafka-configs.sh --describe --entity-type clients` |
| Client `--list` topic được nhưng produce timeout | `advertised.listeners` trả địa chỉ client không tới được | Sửa `advertised.listeners` theo từng listener |
| Dashboard trống trơn sau khi nâng cấp cluster | **KIP-1100** đổi tên MBean ở 4.2 | `curl :7071/metrics \| grep` để lấy tên mới; sửa PromQL |

## ⚠️ Bẫy đề hay gặp

- Thấy "`UnderReplicatedPartitions` = 140, `OfflinePartitionsCount` = 0" → dễ chọn "mất dữ liệu / dịch vụ dừng", nhưng đúng là **client vẫn chạy bình thường, chỉ giảm độ bền** — đây là ticket, không phải page.
- Thấy "`UnderMinIsrPartitionCount` = 3, cần khôi phục ghi ngay" → dễ chọn **hạ `min.insync.replicas` xuống 1**, nhưng đúng là **khôi phục replica**; hạ min.isr là bỏ đúng lớp bảo vệ vào đúng lúc cần nó nhất.
- Thấy "ISR flapping liên tục" → dễ chọn **tăng `replica.lag.time.max.ms`**, nhưng đúng là sửa **GC / disk / network**; nới ngưỡng chỉ làm metric đẹp lên mà rủi ro tăng.
- Thấy "`ActiveControllerCount` = 0 trên broker A" → dễ kết luận sự cố, nhưng KRaft cho phép mỗi node có **0 hoặc 1**; chỉ **tổng toàn cluster** ≠ 1 mới là sự cố. Broker thường không phải controller nên 0 là bình thường.
- Thấy "`RemoteTimeMs` của Produce cao với `acks=all`" → dễ chọn "broker nghẽn", nhưng đúng là **chờ follower ack — hành vi thiết kế**; chỉ bất thường khi tăng đột biến so với baseline.
- Thấy "consumer lag từ CLI là 12.000 nhưng `records-lag-max` là 3.500" → dễ kết luận "một trong hai sai", nhưng **cả hai đều đúng**: một tính theo committed, một theo fetch position.
- Thấy "ứng dụng dùng `assign()` và cần alert lag" → dễ chọn `kafka-consumer-groups.sh`, nhưng đúng là **không đo được lag từ phía broker** cho consumer standalone.
- Thấy "alert URP kêu suốt mỗi lần deploy" → dễ chọn **nâng ngưỡng lên > 5**, nhưng đúng là thêm **`for: 10m`**: nâng ngưỡng làm mất sự cố thật, `for:` chỉ lọc nhiễu thời gian.
- Thấy "throughput đụng trần mà log sạch" → dễ chọn tăng `num.io.threads`, nhưng đúng là **quota** (`produce-throttle-time-avg` > 0). Tương tự, "đổi nơi ghi `server.log`" → dễ chọn `log.dirs`, nhưng `log.dirs` chứa **dữ liệu partition**; log ứng dụng ở `/var/log/kafka` hoặc `$base_dir/logs`.
- 🕰️ **Bẫy version:** đáp án nào bảo "xem znode trong ZooKeeper để biết controller nào đang active", "dùng `--zookeeper` với `kafka-topics.sh`", hay "`zookeeper.connect` trỏ sai" đều **sai với Kafka 4.x** — ZooKeeper bị gỡ từ 4.0, thay bằng `kafka-metadata-quorum.sh describe --status`.
- 🕰️ **Bẫy version:** đáp án nào bảo "đặt `inter.broker.protocol.version` sau khi nâng cấp" là của thế hệ trước; từ 4.0 dùng **`kafka-features.sh upgrade --release-version 4.3`** và `metadata.version`.
- 🕰️ **Bẫy version:** tài liệu cũ ghi `num.recovery.threads.per.data.dir` mặc định **1** và `linger.ms` **0** — từ 4.0 là **2** và **5**. Cũng đừng dùng tên MBean legacy kiểu `org.apache.kafka.server:type=…`: KIP-1100 đã đổi ở **4.2**.

## 🧪 Lab checklist

- [ ] Lab 7.1 ⭐ — Dựng `alerts.yml` cho 4 metric đèn đỏ trên stack Prometheus/Grafana có sẵn; xác nhận alert đi từ **pending → firing** trong UI Prometheus.
- [ ] Lab 7.2 ⭐ — Tắt `kafka-3`, thấy alert URP kêu, **đo giây** URP về 0; tăng `num.replica.fetchers` và đo lại.
- [ ] Lab 7.3 ⭐ — Tạo topic RF=1, tắt đúng broker giữ nó → `OfflinePartitionsCount` > 0; đối chiếu với topic RF=3 trên cùng broker.
- [ ] Lab 7.4 ⭐ — Gây 3 kiểu lag (skew / thiếu consumer / rebalance lặp) và phân biệt bằng `--members --verbose` + metric.
- [ ] Lab 7.5 — Làm sai `advertised.listeners` → bootstrap OK nhưng produce timeout → đọc log tìm ra → sửa.
- [ ] Lab 7.6 — `--entity-type broker-loggers` nâng `state-change.logger` lên TRACE, quan sát leader election, rồi hạ xuống.
- [ ] Lab 7.7 — Chạy script phá ngẫu nhiên, chẩn đoán bằng playbook, ghi lại **thứ tự** các lệnh đã dùng rồi đối chiếu đáp án.

## 🚪 Cổng tự kiểm tra (phải trả lời trôi chảy mới sang tuần sau)

- **`UnderReplicatedPartitions` = 50 và `UnderMinIsrPartitionCount` = 0 — client đang bị ảnh hưởng gì?**
  **Đáp án gọn:** không bị gì. Vẫn đọc/ghi bình thường, chỉ **giảm độ bền**. Đây là ticket, không phải page. Nếu UnderMinIsr > 0 thì producer `acks=all` mới bị chặn.
- **`ActiveControllerCount` trên cả 3 broker đều bằng 0 — bình thường hay sự cố?**
  **Đáp án gọn:** với controller **tách riêng** thì broker bằng 0 là bình thường. Chỉ sai khi **tổng toàn cluster** ≠ 1. Kiểm bằng `kafka-metadata-quorum.sh describe --status`.
- **Produce latency p99 tăng gấp 3; pha nào của `TotalTimeMs` cho biết thủ phạm là thiếu io thread, pha nào cho biết là follower chậm?**
  **Đáp án gọn:** `RequestQueueTimeMs` cao (kèm `RequestHandlerAvgIdlePercent` < 0.3) = thiếu io thread → `num.io.threads`. `RemoteTimeMs` cao = chờ follower ack với `acks=all` → kiểm follower, `num.replica.fetchers`.
- **Alert nào được phép gọi dậy lúc 3 giờ sáng, alert nào chỉ tạo ticket, và dùng gì để tách hai loại?**
  **Đáp án gọn:** PAGE = OfflinePartitions, ActiveControllerCount ≠ 1, UnderMinIsr, disk sắp đầy, unclean election, monitoring chết. TICKET = URP, idle % thấp, ISR flapping, lag tăng nhẹ. Tách bằng **`for:`** (URP `for: 10m`), không bằng cách nâng ngưỡng.
- **Lag CLI 12.000 còn `records-lag-max` 3.500 — số nào sai?**
  **Đáp án gọn:** **không số nào sai**. CLI tính theo committed offset (auto commit 5 s), client tính theo fetch position. Chênh lệch = lượng đã fetch chưa commit.
- **Lag tăng chỉ ở partition 3, các partition khác bằng 0. Thêm consumer có giúp không?**
  **Đáp án gọn:** **không**. Đây là key skew — partition 3 đã có chủ, consumer mới sẽ idle. Phải sửa key/partitioner (hoặc tăng partition, nhưng đó là hành động **một chiều**).
- **Client `kafka-topics.sh --list` chạy được nhưng produce timeout. Nghi gì đầu tiên?**
  **Đáp án gọn:** **`advertised.listeners`** trả về địa chỉ client không tới được. Client lấy metadata từ bootstrap rồi kết nối **thẳng tới leader** bằng địa chỉ broker tự khai.
- **Cần bật DEBUG cho request logger trên broker `node.id=2` mà không được restart. Lệnh gì?**
  **Đáp án gọn:** `kafka-configs.sh --alter --entity-type broker-loggers --entity-name 2 --add-config kafka.request.logger=DEBUG`; nhớ `--delete-config` sau khi xong (thay đổi không bền qua restart).
- **⭐ CHECKPOINT:** đã đạt **≥75%** ở **FULL MOCK #1** (60 câu / 90 phút) chưa? Dưới **70%** → **van an toàn: lùi lịch thi 1 tuần** và học lại 2 domain điểm thấp nhất.

## 📎 Tài nguyên tuần này

> 📂 **Đã crawl sẵn tài liệu chính thức vào** [`resources/`](resources/INDEX.md) — đọc offline được.

- Apache Kafka Docs 4.3: [*Monitoring*](https://kafka.apache.org/43/operations/monitoring/) (bảng metric + ngưỡng gốc, KRaft metrics), [*Basic Kafka Operations*](https://kafka.apache.org/43/operations/basic-kafka-operations/) (leader election, reassignment, graceful shutdown, `cordoned.log.dirs`), [*KRaft*](https://kafka.apache.org/43/operations/kraft/) (`kafka-metadata-quorum.sh`, debugging metadata), [*Upgrading*](https://kafka.apache.org/43/getting-started/upgrade/) (KIP-1100, `kafka-features.sh`).
- Confluent Platform Docs: [*Broker and Controller Metrics*](https://docs.confluent.io/platform/current/kafka/broker-metrics.html) (3 alert tối thiểu), [*Monitor Consumer Lag*](https://docs.confluent.io/platform/current/monitor/monitor-consumer-lag.html) (giới hạn `assign()`), [*Post-Deployment*](https://docs.confluent.io/platform/current/kafka/post-deployment.html) (file log, rolling restart).
- Prometheus: [*Alerting rules*](https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/) (`for:`, `keep_firing_for:`, pending vs firing), [*Alerting best practices*](https://prometheus.io/docs/practices/alerting/) (symptom-based, metamonitoring).
- Prometheus JMX Exporter: [README](https://github.com/prometheus/jmx_exporter) + [rules configuration](https://prometheus.github.io/jmx_exporter/1.4.0/configuration/rules/).
- KIP: **KIP-1100** (chuẩn hoá tên metric, 4.2), **KIP-966** (ELR), **KIP-412** (dynamic log level), **KIP-853** (dynamic KRaft quorum).
- Sách: *Kafka: The Definitive Guide* 2nd ed. — chương **13 Monitoring Kafka**, chương **12 Administering Kafka**. Bản đồ chương: [`CCDAK/.../kafka-definitive-guide-chapter-map.md`](../../../CCDAK/study-plan/week-10/resources/kafka-definitive-guide-chapter-map.md).
- Ôn lại CCDAK: [Tuần 8 — Observability & Operations](../../../CCDAK/study-plan/week-08/README.md) và [labs Tuần 8](../../../CCDAK/study-plan/week-08/labs.md).

## ✅ Checklist hoàn thành Tuần 7

- [ ] Hoàn thành 4 buổi A/B/C/D
- [ ] Thuộc bảng "PHẢI NHỚ" — đặc biệt 4 ngưỡng đèn đỏ, 5 pha `TotalTimeMs`, và ranh giới PAGE vs TICKET
- [ ] Đọc trôi **12 playbook** và nói được **hành động đầu tiên** của từng kịch bản mà không tra
- [ ] Vẽ lại từ trí nhớ **cây quyết định lag** (skew → thiếu consumer → rebalance lặp → xử lý chậm)
- [ ] Hoàn thành ≥6 lab (7.1–7.7, trong đó 4 lab ⭐ là bắt buộc)
- [ ] Làm xong 30 câu [questions.md](questions.md), ghi sổ câu sai
- [ ] **🎯 FULL MOCK #1: đạt ≥75%** (60 câu / 90 phút) — điền đủ **bảng chấm theo 7 domain**
- [ ] Vượt Cổng tự kiểm tra
