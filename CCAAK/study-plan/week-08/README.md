# 🏁 Tuần 8 — Tuần chốt: mock dồn + capstone vận hành + cram + thi

> **Domain CCAAK:** Tất cả 7 domain (tổng ôn) · **Thời lượng:** ~11h+ (4 buổi: mock dồn + review + capstone + cram) · **Vị trí:** Tuần 8/8 — vùng đệm đảm bảo đậu 🏁 Full mock #2–3 → Thi
>
> **Điều hướng:** [⬅️ Tuần 7](../week-07/README.md) · [🏠 Kế hoạch tổng](../../CCAAK-STUDY-PLAN.md) · 🎓 Đăng ký & thi

## 🔁 Ôn nhanh từ CCDAK (~20 phút)

Tuần chốt **không** đọc lại CCDAK theo chủ đề nữa — chỉ dùng CCDAK như **kho lab và kho tra cứu** khi bảng chấm điểm chỉ ra một domain dưới ngưỡng.

| Khái niệm | File CCDAK cần đọc lại | Vì sao cần cho tuần này |
|---|---|---|
| Quy trình tuần chốt (mock dồn, van an toàn, cram sheet) | [`week-10/README.md`](../../../CCDAK/study-plan/week-10/README.md) | Bạn đã chạy đúng quy trình này một lần cho CCDAK — lặp lại nó, chỉ đổi nội dung sang góc vận hành |
| Ma trận `acks` × `min.insync.replicas` × RF | [`week-02/resources/kafka-replication-isr.md`](../../../CCDAK/study-plan/week-02/resources/kafka-replication-isr.md) | **Bài phá số 1** của capstone và ít nhất 3–4 câu trong mọi bộ mock đều xoay quanh ma trận này |
| Reassignment + throttle + preferred leader election | [`week-08/labs.md`](../../../CCDAK/study-plan/week-08/labs.md) (Lab 8.4) | **Bài phá số 4** của capstone dùng lại nguyên quy trình `--generate` → `--execute --throttle` → `--verify` |
| MirrorMaker 2 giữa 2 cluster local | [`week-08/labs.md`](../../../CCDAK/study-plan/week-08/labs.md) (Lab 8.6) | **Bước 7 — diễn tập DR** dựng lại cluster B và `mm2.properties` từ lab này |
| JMX → Prometheus → Grafana | [`week-08/labs.md`](../../../CCDAK/study-plan/week-08/labs.md) (Lab 8.1) | Capstone bước 1–2 cần dashboard sống để **nhìn thấy** từng bài phá, không chỉ đọc log |
| TLS/mTLS + SASL/SCRAM + ACL | [`week-07/labs.md`](../../../CCDAK/study-plan/week-07/labs.md) | **Bài phá số 3** thu hồi ACL rồi chẩn đoán qua `kafka-authorizer.log` |

> 🗺️ Cần biết **phần nào của một domain đã có sẵn từ CCDAK, phần nào thật sự mới**? Mở bảng ánh xạ [`resources/ccaak-vs-ccdak-map.md`](resources/ccaak-vs-ccdak-map.md) — có cả bảng **8 chỗ kiến thức CCDAK lệch với góc admin**, nhóm sai khó phát hiện nhất vì bạn "chắc chắn là mình biết".

## 🎯 Mục tiêu tuần này

Tuần này **KHÔNG học kiến thức mới**. Toàn bộ trọng tâm là chuyển hoá: từ *"biết vận hành Kafka"* sang *"phản xạ đúng dưới áp lực 90 giây/câu, và đủ điều kiện đăng ký thi"*.

- **Hoàn tất ≥3 bộ mock KHÁC NHAU đạt ≥80% ổn định** (không phải may mắn một lần). CCAAK chỉ chấm **pass/fail**, không công bố ngưỡng → bar cá nhân **80%** để có biên an toàn.
- **Review 100% câu sai** của mọi mock và **viết file phân tích** trong [`CCAAK/questions/`](../../questions/README.md) theo **6 mục + 3 mục bổ sung riêng CCAAK**.
- **Làm bài đúng nhịp thi thật: 60 câu / 90 phút ≈ 90 giây/câu**, biết đánh dấu + bỏ qua + quay lại; xử lý được hai dạng ngoài multiple-choice là **matching** và **list order**.
- **Đọc trôi chảy không cần tra** toàn bộ **bảng số [§6](../../CCAAK-STUDY-PLAN.md#6-những-con-số-phải-thuộc-lòng)** và **bảng phản xạ triệu chứng [§7](../../CCAAK-STUDY-PLAN.md#7-bảng-phản-xạ-triệu-chứng--hành-động)** của Kế hoạch tổng. Trong phòng thi **không được mở tài liệu** — đây là lý do phải thuộc.
- **Tự tay chẩn đoán và khôi phục một cluster bị phá** — **Capstone "Cluster Rescue"** trong [labs.md](labs.md): 4 bài phá (durability · storage · security · cân bằng) cộng một buổi diễn tập DR, mỗi bài có ✅ Kiểm chứng riêng.
- **Phản xạ được trục đánh đổi của mỗi câu hỏi**: durability · availability · throughput · chi phí vận hành — và luôn **ưu tiên hành động rẻ, đảo ngược được** trước hành động "đúng nhưng quá tay".
- **Sẵn sàng phòng thi Honorlock:** đã chạy System Check, đã chuẩn bị giấy tờ và phòng, đã đặt lịch.

## 📚 Nội dung học chi tiết

Bốn "buổi" tuần này quy đổi thành **lịch mock dồn xen capstone**. Hai nguyên tắc không đổi: **mỗi full mock cách nhau ≥1 ngày** (ngày xen giữa dành cho vùng yếu và capstone), và **luôn canh giờ 90 phút nghiêm ngặt** như thi thật.

### 🗓️ Lịch 7 ngày cuối

| Ngày | Việc chính | Đầu ra phải có |
|---|---|---|
| **Ngày 1** | 🎯 **FULL MOCK #2** = [**Mock 01**](../../mock-exams/mock-01/questions.md) — 60 câu, canh giờ 90' → chấm theo **7 domain** → **review 100% câu sai** | Bảng điểm 7 domain lần #2 + ≥3 file phân tích trong `CCAAK/questions/` |
| **Ngày 2** | Cày **domain thấp nhất** ở mock #2 + đọc lại **bảng số §6** + **Capstone bước 1–3** (dựng cluster production-like → baseline → **bài phá durability**) | Cluster 3 broker + controller tách riêng + TLS/SCRAM/ACL/quota/Grafana đang chạy; bài phá 1 đã khôi phục |
| **Ngày 3** | 🎯 **FULL MOCK #3** = [**Mock 02**](../../mock-exams/mock-02/questions.md) — canh giờ 90' → review 100% câu sai | Bảng điểm 7 domain lần #3; so xu hướng với lần #2 |
| **Ngày 4** | **Capstone bước 4–6** (**bài phá storage · security · cân bằng**) + đọc **bảng phản xạ §7** | 3 bài phá đã chẩn đoán đúng nguyên nhân **trước khi** xem gợi ý |
| **Ngày 5** | 🎯 **FULL MOCK #4 nếu chưa đủ 3 bài ≥80%** = [**Mock 03**](../../mock-exams/mock-03/questions.md); đủ rồi thì **Capstone bước 7 (diễn tập DR)** + tự viết lại **cram sheet 1 trang từ trí nhớ** | Đủ 3 bài ≥80%; cram sheet tự viết đã đối chiếu với 60 fact bên dưới |
| **Ngày 6** | **Cram:** 60 fact + **playbook tổng hợp** + 15 bẫy + bảng số §6; chạy **Honorlock System Check**; chuẩn bị **ID + phòng**; 🧹 `docker compose down -v` toàn bộ lab | System Check pass; giấy tờ và phòng sẵn sàng; máy sạch |
| **Ngày trước thi** | **Nghỉ nhẹ** — chỉ đọc lướt cram sheet + 15 bẫy + playbook; **ngủ đủ**; KHÔNG học kiến thức mới, KHÔNG mock thêm | Tinh thần, không phải kiến thức |

> 📌 Ba bộ mock full-length nằm ở [`mock-exams/`](../../mock-exams/README.md). **Mock #1 đã làm ở Tuần 7** — tuần này là **#2 và #3** (và #4 nếu cần). Bộ 30 câu của chính tuần này ([questions.md](questions.md), 45 phút) dùng làm bài **khởi động** trước mock #2, không tính vào "3 bộ ≥80%".

### 🅰️ Buổi A — FULL MOCK #2 + chiến lược làm bài CCAAK (~2.5h)

> 📝 **Khởi động trước khi vào mock 60 câu:** [questions.md](questions.md) — **mock cross-domain 30 câu** phủ đúng tỉ trọng 7 domain, canh giờ **45 phút** (90 giây/câu), tự chấm + **phân tích điểm theo 7 domain** ở [answers.md](answers.md).

**Quy trình chạy một bài full mock (giống thi thật):**

1. Chọn một bộ **60 câu**, đặt đồng hồ **90 phút**, không dừng giữa chừng, **không tra tài liệu** (thi thật cấm tài liệu tham khảo và điện thoại). Nếu phải mở bảng số §6 thì bài đó **không tính**.
2. Áp dụng chiến lược dưới đây trong suốt bài.
3. Chấm điểm, ghi **% tổng** và **% theo 7 domain** vào bảng theo dõi ở [`resources/mock-exam-and-prep-guide.md`](resources/mock-exam-and-prep-guide.md).

**Bốn dạng câu và cách xử lý:**

| Dạng câu | Cách nhận diện | Chiến thuật |
|---|---|---|
| **Multiple-choice** | 1 đáp án đúng, 4 lựa chọn | Loại 2 phương án sai rõ → so 2 phương án còn lại **theo qualifier**, không theo "cái nào nghe đúng hơn" |
| **Multiple-select** | "Select **TWO**/**THREE**" | Chọn **đúng số**; đánh giá từng lựa chọn như một câu true/false độc lập; không có điểm một phần |
| **Matching** | Ghép metric ↔ nguyên nhân, config ↔ hành vi, tool ↔ tình huống | Ghép cặp **chắc chắn nhất trước**, phần còn lại tự khớp bằng loại trừ; bám bảng số §6 (`num.io.threads` 8, `replica.lag.time.max.ms` 30 s, `connect-offsets` 25…) |
| **List order** | Sắp xếp thứ tự các bước vận hành | Xác định **bước đầu và bước cuối** trước rồi điền giữa. Ba chuỗi phải thuộc: **rolling upgrade** (controlled shutdown → thay binary → start → **chờ URP = 0** → broker kế tiếp → `kafka-features.sh upgrade`), **reassignment** (`--generate` → `--execute --throttle` → `--verify` → preferred leader election), **chẩn đoán** (metric → log → config → hành động) |

**Chiến lược làm bài CCAAK — luyện đến mức tự động:**

- **Nhịp 90 giây/câu.** Câu quá **2 phút** → đánh dấu, đoán một phương án, đi tiếp. Không bỏ trống câu nào (đoán sai không bị trừ điểm).
- **Đọc TRIỆU CHỨNG trước, đáp án sau.** Đề CCAAK mở đầu bằng một output CLI, một dòng log hay một metric. Tóm tắt nó thành một câu *"cluster đang bị gì"* **trước khi** liếc 4 phương án.
- **Xác định trục đang bị hỏi:** **durability · availability · throughput · chi phí vận hành**. Gần như mọi câu quy về đúng một trục; biết trục thì hai phương án lập tức rụng. Ví dụ: "*without data loss*" là trục durability → mọi phương án tăng availability bằng cách hy sinh dữ liệu (`unclean.leader.election.enable=true`, hạ `min.insync.replicas`) đều sai.
- **⭐ Ưu tiên hành động RẺ và ĐẢO NGƯỢC ĐƯỢC.** Đây là điểm khác biệt lớn nhất so với CCDAK: đề luôn cài một phương án "đúng kỹ thuật nhưng quá tay". Chọn **nấc thấp nhất** giải quyết được vấn đề:

| Nấc | Hành động | Chi phí | Đảo ngược được? | Khi nào là đáp án đúng |
|---|---|---|---|---|
| 1 | Đọc metric / log (`kafka-log-dirs.sh`, `kafka-metadata-quorum.sh`, `kafka-authorizer.log`) | miễn phí | — | Gần như **luôn** là bước đầu; đề hỏi *"what should the administrator do FIRST"* thường nhắm đúng nấc này |
| 2 | Đổi config **động** bằng `kafka-configs.sh` (`num.io.threads`, `num.replica.fetchers`, `min.insync.replicas`, quota) | thấp | ✅ | Khi nguyên nhân đã rõ và chỉ là một con số sai |
| 3 | Cấp/thu ACL, xoay credential SCRAM | thấp | ✅ | Khi log authorizer chỉ đúng resource thiếu quyền |
| 4 | Reassign partition **có `--throttle`** | tốn băng thông | ✅ | Thêm/bớt broker, sửa skew dung lượng, đổi log dir |
| 5 | Rolling restart (từng broker, chờ URP = 0) | downtime từng broker | ✅ | Đổi config **read-only**, nâng cấp, nạp plugin Connect |
| 6 | **Tăng số partition** | trung bình | ❌ **một chiều**, phá mapping key → partition | Chỉ khi đã loại trừ skew và consumer đã bằng số partition |
| 7 | Bật `unclean.leader.election.enable=true` | **mất dữ liệu đã ack** | ❌ | Chỉ khi đề nói rõ *availability quan trọng hơn dữ liệu* |
- **🔴 Nhận diện bẫy version.** Phương án nào nhắc **ZooKeeper, znode, `--zookeeper`, `zookeeper.connect`, `AclAuthorizer`, MirrorMaker 1** thì gần như chắc chắn **sai** với Kafka 4.x. Tương tự với giá trị mặc định cũ (`num.recovery.threads.per.data.dir=1`, `linger.ms=0`).
- **Gạch chân qualifier:** *without data loss* · *with minimal downtime* · *fewest changes* · *survive the loss of one rack* · *without restarting brokers* · *FIRST* · *MOST likely*. Qualifier quyết định đáp án nhiều hơn kiến thức.
- **Multiple-select:** đọc kỹ số lượng cần chọn trước khi đọc các lựa chọn.
- **Hạn chế đổi đáp án**: chỉ đổi khi phát hiện mình **đã đọc sót** một chi tiết rõ ràng trong đề, không đổi vì "cảm thấy".

### 🅱️ Buổi B — Review 100% câu sai + viết file phân tích (~3h)

1. **Rà từng câu sai** — và cả câu **đúng nhờ đoán may**. Với mỗi câu, gán **một** trong năm nhãn lý do sai: *thiếu kiến thức · đọc sót qualifier · **quá tay** · **bẫy version** · hết giờ*. Bảng phân loại và cách đọc kết quả ở [`resources/mock-exam-and-prep-guide.md`](resources/mock-exam-and-prep-guide.md).
2. Với mỗi câu đáng nhớ, **viết một file phân tích** trong [`CCAAK/questions/`](../../questions/README.md) (đặt tên `CCAAK-NNNN.md`) theo **6 mục** của [`aws-saa-c03-analysis-format.md`](../../../aws-saa-c03-analysis-format.md):
   1. **CONTEXT & ĐỀ BÀI** — tình huống, trạng thái cluster, triệu chứng quan sát được
   2. **KEYWORDS QUAN TRỌNG** — bảng 2 cột `Keyword` | `Ý nghĩa / Gợi ý`
   3. **YÊU CẦU CỦA ĐỀ** — qualifier quyết định đáp án
   4. **ĐÁP ÁN ĐÚNG** — `✅ Đáp án: X` + vì sao nó khớp tình huống
   5. **CÁC ĐÁP ÁN SAI** — `❌` từng phương án: sai ở đâu, và **khi nào nó sẽ đúng**
   6. **MẸO GHI NHỚ (Memory Hook)** — mở đầu bằng `🧠`
3. **Thêm ba dòng bổ sung riêng CCAAK** vào cuối mỗi file (đây là phần giá trị nhất, đừng bỏ):
   - **`Trục đánh đổi:`** — câu này thực chất hỏi *durability · availability · throughput · chi phí vận hành*?
   - **`Hành động rẻ hơn đã bị bỏ qua:`** — phương án rẻ và đảo ngược được lẽ ra phải thử trước là gì?
   - **`Lý do mình sai:`** — một trong năm nhãn ở bước 1. Nếu là **bẫy version**, ghi thêm nhãn `bẫy version` để đếm riêng.
4. **Ghi sổ câu sai** và ôn lại theo mốc **1 ngày → 3 ngày → 7 ngày**.
5. **Cày lại bảng số §6** cho đúng những con số mình sai trong mock — không đọc lại cả bảng, chỉ đọc dòng mình sai, rồi ngày hôm sau che đi và tự đọc lại.

> 🎯 **Chỉ tiêu cụ thể:** sau mock #3, số câu sai nhãn **"bẫy version" phải về 0**. Đây là nhóm dễ diệt nhất — nó chỉ là một danh sách hữu hạn ở [`resources/kafka-4x-operational-changes.md`](resources/kafka-4x-operational-changes.md). Còn sót một câu nhóm này nghĩa là bạn chưa đọc file đó nghiêm túc.

### 🅲️ Buổi C — Capstone vận hành "Cluster Rescue" + cram sheet (~3.5h)

> 🛠️ **Capstone "Cluster Rescue" ⭐ (7 bước) — chi tiết cầm tay ở [labs.md](labs.md).** Khác capstone của CCDAK ở bản chất: CCDAK bắt bạn **xây một pipeline**, CCAAK bắt bạn **giữ một cluster sống**. Tóm tắt 7 bước:
>
> 1. **Dựng cluster production-like** — 3 broker + **controller tách riêng**, `broker.rack`, TLS + SCRAM + ACL, quota, Prometheus/Grafana có alert. Dùng lại mọi thứ đã dựng ở Tuần 1–7. *(FUND, ARCH, SEC, OBS)*
> 2. **Thiết lập baseline** — tạo topic theo đúng sizing tự tính, ghi nhận metric "bình thường" vào một file để so sánh. Không có baseline thì không chẩn đoán được. *(CFG, ARCH, OBS)*
> 3. ⭐ **Bài phá số 1 — durability**: ai đó đặt `min.insync.replicas=3` trên topic RF3, rồi một broker chết → producer `acks=all` đứng. Chẩn đoán và khôi phục **đúng cách**. *(CFG, FUND, TROUBLE)*
> 4. ⭐ **Bài phá số 2 — storage**: một `log.dirs` đầy/hỏng → `KafkaStorageException`, partition offline. Chẩn đoán bằng `kafka-log-dirs.sh` và khôi phục. *(CFG, TROUBLE)*
> 5. ⭐ **Bài phá số 3 — security**: ACL bị thu hồi nhầm khiến một service chết im lặng. Tìm ra bằng `kafka-authorizer.log` và cấp lại **quyền tối thiểu**. *(SEC, TROUBLE)*
> 6. ⭐ **Bài phá số 4 — cân bằng**: thêm broker mới nhưng nó không nhận traffic. Reassign **có throttle**, gỡ throttle, preferred leader election. *(ARCH, CFG)*
> 7. **Diễn tập DR** — MirrorMaker 2 sang cluster thứ hai, dịch offset consumer group, kiểm chứng dữ liệu. *(ARCH, CONNECT)*

**Cram sheet 1 trang — TỰ VIẾT LẠI từ trí nhớ** (không copy), gồm 7 khối; đối chiếu với `## 🧠 Cram sheet — 60 fact` bên dưới **sau khi** viết xong:

| Khối | Nội dung phải có |
|---|---|
| **1. Broker defaults — threads & socket** | `num.network.threads` · `num.io.threads` · `num.replica.fetchers` · `background.threads` · `queued.max.requests` · socket buffer · `num.recovery.threads.per.data.dir` |
| **2. Ma trận durability** | RF × `min.insync.replicas` × `acks` → chịu mất mấy broker; RF internal topic; `unclean.leader.election.enable`; `replica.lag.time.max.ms` |
| **3. Retention, compaction, storage** | `log.retention.hours` · `log.segment.bytes` · `min.cleanable.dirty.ratio` · `delete.retention.ms` · segment active không bị xoá · JBOD rải theo **số partition** |
| **4. Thứ tự ưu tiên config (5 mức) + config động vs tĩnh** | `DYNAMIC_TOPIC_CONFIG` → … → `DEFAULT_CONFIG`; cái nào đổi được lúc chạy |
| **5. KRaft & kiến trúc triển khai** | Quorum 3/5 chịu mất `(N-1)/2`; `process.roles`; `__cluster_metadata`; cùng `cluster.id`; `broker.rack`; MM2 vs Cluster Linking vs stretch |
| **6. Security & quota** | 4 `security.protocol`; 4 SASL mechanism; `StandardAuthorizer`; Deny thắng Allow; PREFIXED; **4 loại quota + 8 mức ưu tiên** |
| **7. Metric → ngưỡng → hành động** | `UnderReplicatedPartitions` · `OfflinePartitionsCount` · `ActiveControllerCount` · `UnderMinIsrPartitionCount` · `RequestHandlerAvgIdlePercent` < 0.3 · lag committed vs position |

### 🅳 Buổi D — FULL MOCK #3 (và #4 nếu cần) + van an toàn (~2h)

1. **≥1 ngày sau mock #2**, chạy **FULL MOCK #3** (bộ đề KHÁC), lặp lại đúng quy trình canh giờ 90' + chiến lược Buổi A.
2. Review 100% câu sai + viết file phân tích như Buổi B.
3. Chưa đủ **3 bài ≥80%** → xếp thêm **FULL MOCK #4** (cách ≥1 ngày, bộ đề thứ tư).
4. **🚨 VAN AN TOÀN:** bất kỳ full mock nào **<70%** → **lùi lịch thi 1 tuần**, tập trung 100% vào hai domain điểm thấp nhất rồi mới mock lại. Quyết định lùi phải ra **sớm hơn 5 ngày** so với giờ thi thì mới đổi lịch miễn phí.
5. **Spaced repetition lần cuối** cho bốn cụm hay quên nhất của CCAAK: **ma trận durability** (RF/min.isr/acks), **thứ tự ưu tiên config 5 mức**, **8 mức quota**, **3 internal topic Connect 1/25/5**.

## 🧠 PHẢI NHỚ tuần này

**Thông tin kỳ thi — bám đúng để phân bổ giờ:**

| Fact | Con số / Ghi nhớ |
|---|---|
| Số câu | **60 câu** *(syllabus bên thứ ba; trang Confluent không công bố — đối chiếu khi mua)* |
| Thời gian | **90 phút** (trang Confluent chính thức) → **90 giây/câu** |
| Dạng câu | **multiple-choice · multiple-select · matching · list order** |
| Điểm đậu | **Không công bố**, chỉ **pass/fail**; kết quả **hiện ngay trên màn hình** |
| **Bar cá nhân** | **≥80% ổn định** trên **≥3 bộ khác nhau** |
| Lệ phí | **150 USD** *(chưa xác nhận trên trang chính thức — kiểm lúc thanh toán)* |
| Hiệu lực | **2 năm**, phải tái chứng nhận |
| Thi lại | Chờ **7 ngày** mới được mua và thi lại |
| Đổi/huỷ lịch | Miễn phí nếu **≥5 ngày** trước; trong 5 ngày → **không hoàn phí** |
| Hình thức | **Online proctored** qua **Honorlock**: Chrome + extension, webcam, micro, **government ID**, System Check |
| Tài liệu tham khảo | **Cấm** — không tài liệu, không điện thoại. Bảng số §6 **phải thuộc**, không tra |
| Tỉ trọng 7 domain | CFG **22** · FUND **15** · SEC **15** · TROUBLE **15** · ARCH **12** · CONNECT **12** · OBS **10** (tổng 101% do làm tròn) |
| Cụm nặng nhất | **CFG + TROUBLE + OBS = 47%** — gần nửa đề là *"cluster có triệu chứng X, sửa config nào"* |
| Version neo | **Apache Kafka 4.3** (KRaft-only từ 4.0); hỏi "default" không nêu version → trả lời theo **4.3** |
| Syllabus cũ | Tài liệu chia **4 domain** (Fundamentals 15 · Managing/Configuring/Optimizing 30 · Security 15 · Designing/Troubleshooting/Integrating 40) là **thế hệ trước** — bỏ qua |

**Tiêu chí SẴN SÀNG đăng ký thi — CHỈ đặt lịch khi ĐỦ CẢ 4:**

| # | Tiêu chí |
|---|---|
| 1 | ✅ **≥3 bộ mock KHÁC NHAU đạt ≥80%** (ổn định, canh giờ 90', không tra tài liệu) |
| 2 | ✅ Đã **review 100% câu sai** và viết file phân tích **6 mục + 3 mục bổ sung** trong `CCAAK/questions/` |
| 3 | ✅ Đọc **trôi chảy** toàn bộ **bảng số §6** + **bảng phản xạ §7** + tự viết lại được **cram sheet 1 trang** |
| 4 | ✅ Hoàn thành **Capstone "Cluster Rescue" 7 bước** với đủ ✅ Kiểm chứng (4 bài phá đã chẩn đoán và khôi phục, DR đã kiểm chứng dữ liệu) |

> 🚨 **VAN AN TOÀN:** bất kỳ full mock nào **<70%** → **lùi lịch thi 1 tuần**, cày hai domain thấp nhất, rồi mock lại bằng bộ đề khác.

## 🧠 Cram sheet — 60 fact trong 1 trang

> Mọi con số khớp [§6 Kế hoạch tổng](../../CCAAK-STUDY-PLAN.md#6-những-con-số-phải-thuộc-lòng). Đọc theo chiều dọc mỗi sáng của tuần chốt; ngày 6 thì che cột số và tự đọc lại.

**Broker — threads & socket (1–7)**

1. `num.network.threads` = **3** · xử lý socket; đo bằng `NetworkProcessorAvgIdlePercent`.
2. `num.io.threads` = **8** · xử lý request; đo bằng `RequestHandlerAvgIdlePercent`, lý tưởng **> 0.3**.
3. `num.replica.fetchers` = **1** · quyết định tốc độ follower bắt kịp → **tăng khi URP lâu về 0**.
4. `background.threads` = **10** · tác vụ nền của broker.
5. `queued.max.requests` = **500** · hàng đợi giữa network thread và I/O thread.
6. `socket.send.buffer.bytes` = `socket.receive.buffer.bytes` = **102400** (100 KiB); `socket.request.max.bytes` = **104857600** (100 MiB).
7. `num.recovery.threads.per.data.dir` = **2** (đổi từ 1 ở **4.0**) · dùng khi broker recovery log sau crash.

**Durability & replication (8–17)**

8. Mặc định "trần trụi": `default.replication.factor` **1** · `min.insync.replicas` **1** · `num.partitions` **1**. Production phải là **RF 3 / min.isr 2**.
9. **Bộ ba vàng:** RF **3** + `min.insync.replicas` **2** + producer `acks=all` = chịu mất **1 broker**, vẫn ghi được, không mất dữ liệu.
10. `min.insync.replicas=3` với RF 3 là **over-correction**: mất 1 broker là **ngừng ghi**. Câu này lặp lại nhiều lần trong đề.
11. `acks=all` nghĩa là "mọi replica **trong ISR**", không phải mọi replica. Độ bền thực sự do `min.insync.replicas` quyết định.
12. `unclean.leader.election.enable` = **false** · bật lên = đổi dữ liệu lấy availability, là **lựa chọn cuối cùng**.
13. `replica.lag.time.max.ms` = **30000** · follower tụt quá thì rời ISR. `replica.socket.timeout.ms` = **30000**.
14. `auto.leader.rebalance.enable` = **true** · `leader.imbalance.check.interval.seconds` = **300**.
15. `controlled.shutdown.enable` = **true** · đây là thứ khiến rolling restart không tạo offline partition.
16. Internal topic: `offsets.topic.replication.factor` **3** · `transaction.state.log.replication.factor` **3** · `transaction.state.log.min.isr` **2**. Cluster 1 broker phải hạ về **1** nếu không sẽ lỗi khi tạo.
17. `__consumer_offsets` **50** partition · `__transaction_state` **50** partition — đều compacted. **ELR** (KIP-966) bật mặc định cho cluster mới từ **4.1**; khi ELR bật, `min.insync.replicas` mức **broker** bị gỡ → đặt ở mức **cluster/topic**.

**Log, retention, compaction, storage (18–27)**

18. `log.retention.hours` = **168** (7 ngày) · `log.retention.bytes` = **-1** (không giới hạn, tính **theo partition**).
19. `log.segment.bytes` = **1 GiB** · `log.roll.hours` = **168** · từ 4.x **giá trị nhỏ nhất cho phép là 1 MiB** (trước là 14 byte).
20. **Retention chỉ áp cho segment ĐÃ ĐÓNG.** "Đặt retention 1 giờ mà data vẫn còn" → hạ `segment.ms`/`segment.bytes`, không phải sửa retention.
21. `log.retention.check.interval.ms` = **300000** (5 phút).
22. `log.cleaner.threads` = **1** · `min.cleanable.dirty.ratio` = **0.5** · `log.cleaner.delete.retention.ms` = **86400000** (24 giờ, thời gian sống của tombstone).
23. `message.max.bytes` = **1048588** (broker) · `replica.fetch.max.bytes` = **1048576**. `replica.fetch.max.bytes` nhỏ hơn `message.max.bytes` → replica **không kéo nổi** message lớn.
24. `auto.create.topics.enable` = **true** — production **nên tắt**.
25. **Thứ tự ưu tiên config, 5 mức:** `DYNAMIC_TOPIC_CONFIG` > `DYNAMIC_BROKER_CONFIG` > `DYNAMIC_DEFAULT_BROKER_CONFIG` > `STATIC_BROKER_CONFIG` > `DEFAULT_CONFIG`. Đọc cột **synonyms** của `kafka-configs.sh --describe --all` để biết giá trị hiệu lực đến từ đâu.
26. **JBOD `log.dirs` nhiều ổ:** Kafka rải partition theo **số partition mỗi thư mục**, **không theo dung lượng**. Một ổ hỏng → chỉ partition trên ổ đó offline. Xem phân bố bằng `kafka-log-dirs.sh`. Kafka **4.3** có **cordoned log dir** (KIP-1066) để ngừng đặt partition mới lên ổ sắp bỏ.
27. **Sizing:** partition = `max(throughput cần / throughput 1 producer, throughput cần / throughput 1 consumer)` + biên tăng trưởng; disk = `throughput ghi × retention × RF × 1.2`. **Không giảm được số partition.**

**KRaft & Deployment Architecture (28–38)**

28. Quorum **3 hoặc 5** controller (số lẻ), chịu mất **`(N-1)/2`**. `controller.quorum.election.timeout.ms` = **1000**.
29. `process.roles` = `broker` | `controller` | `broker,controller`. **Combined chỉ dùng cho dev**, production tách riêng.
30. Metadata nằm ở `__cluster_metadata`; format bằng `kafka-storage.sh format` với **cùng `cluster.id`** → sai thì broker báo **`InconsistentClusterId`**.
31. **4.3:** `controller.quorum.auto.join.enable` mặc định **`false`** — controller mới **không tự vào quorum**.
32. `kafka-metadata-quorum.sh describe --status` là lệnh đầu tiên khi `ActiveControllerCount` bất thường.
33. Java **17** cho broker/Connect/tools, Java **11** cho client; baseline client protocol **2.1** (Kafka 4.0).
34. **Rolling upgrade:** từng broker một — `controlled.shutdown` → thay binary → start → **chờ URP về 0** → broker kế tiếp; xong hết mới `kafka-features.sh upgrade --release-version 4.3`. `metadata.version` thay vai trò `inter.broker.protocol.version` cũ.
35. `broker.rack` → controller rải replica qua rack. Follower fetching (`client.rack`, **KIP-392**) cho consumer đọc từ replica cùng rack, tiết kiệm phí liên AZ.
36. **DR:** MM2 = 3 connector trên Connect, offset **đổi** → cần offset translation. **Cluster Linking** (Confluent Platform) giữ offset **byte-for-byte**. **Stretch cluster** cho RPO = 0 khi DC gần nhau.
37. **Thêm broker KHÔNG tự nhận partition** — topic cũ vẫn nằm nguyên chỗ cũ. Phải `kafka-reassign-partitions.sh --generate` → `--execute --throttle` → `--verify` (**chính `--verify` gỡ throttle**), rồi `kafka-leader-election.sh --election-type preferred`.
38. **JVM/OS (khuyến nghị, KHÔNG phải default):** heap broker **6 GB** + **G1GC**, phần RAM còn lại để **page cache**; file descriptor **100.000+**; `vm.swappiness` **1**; filesystem **XFS**; tách ổ log Kafka khỏi ổ hệ điều hành.

**Security & quota (39–46)**

39. Bốn giá trị `security.protocol`: **PLAINTEXT · SSL · SASL_PLAINTEXT · SASL_SSL**.
40. Bốn SASL mechanism: **PLAIN · SCRAM-SHA-256/512 · GSSAPI (Kerberos) · OAUTHBEARER**. mTLS = SSL + `ssl.client.auth=required`.
41. Listener: `listeners` / `advertised.listeners` / `listener.security.protocol.map` / `inter.broker.listener.name` / `controller.listener.names`. **Client nối được bootstrap nhưng produce timeout = `advertised.listeners` sai.**
42. **KRaft dùng `StandardAuthorizer`** (`AclAuthorizer` của ZooKeeper đã bị gỡ ở **4.0**). Có authorizer thì mặc định **deny**: `allow.everyone.if.no.acl.found` = **false**.
43. **Deny thắng Allow**; `super.users` bỏ qua mọi ACL; pattern **LITERAL** vs **PREFIXED**; producer cần `Write` + `Describe` trên Topic, consumer cần `Read` Topic **và** `Read` **Group**.
44. `TopicAuthorizationException` = thiếu ACL **Topic**; `GroupAuthorizationException` = thiếu ACL **Group**. Bằng chứng nằm ở **`kafka-authorizer.log`**.
45. SCRAM tạo/xoay/thu hồi **lúc chạy** bằng `kafka-configs.sh --entity-type users` (credential nằm trong metadata KRaft); lúc bootstrap dùng `kafka-storage.sh format --add-scram`.
46. **Quota: 4 loại** — `producer_byte_rate` · `consumer_byte_rate` · `request_percentage` · `controller_mutation_rate`; áp theo **user / client-id** với **8 mức ưu tiên** (user+client-id cụ thể → … → default chung). Broker **throttle bằng cách trì hoãn response**, **không trả lỗi** → triệu chứng là "throughput chạm trần, log sạch", kiểm bằng `produce-throttle-time-avg`. Kafka **không có** encryption at rest → dùng mã hoá đĩa/volume.

**Kafka Connect (47–52)**

47. Ba internal topic của Connect distributed: `connect-configs` **1** partition · `connect-offsets` **25** · `connect-status` **5** — **đều compacted**, RF nên cao.
48. `tasks.max` là **trần**, connector tự quyết số task thực tế; task **sink** dư sẽ **nằm không** (không có partition để nhận).
49. **DLQ chỉ có ở sink connector.** `errors.tolerance=all` **không kèm** `errors.deadletterqueue.topic.name` = **mất record âm thầm**.
50. REST ops: `GET /connectors/<n>/status` (đọc trace) · `POST /connectors/<n>/restart?includeTasks=true` · `PUT /pause` & `/resume` · `DELETE /connectors/<n>/offsets`.
51. **Converter** đổi format bytes ↔ record (`key.converter`/`value.converter`); **SMT** sửa từng record (`transforms`). Hai thứ khác nhau, đề hay đánh tráo.
52. Vận hành: `plugin.path` để nạp plugin; nâng plugin = rolling restart worker; `connector.client.config.override.policy` cho phép connector ghi đè config client.

**Observability & Troubleshooting (53–60)**

53. `UnderReplicatedPartitions` **> 0** = **redundancy suy giảm** (follower tụt/broker chết). Hành động: kiểm broker sống chưa, rồi tăng `num.replica.fetchers`.
54. `OfflinePartitionsCount` **> 0** = **mất availability** (không còn leader). Nghiêm trọng hơn URP. Kiểm ISR, cân nhắc ELR; unclean election là lựa chọn cuối.
55. `ActiveControllerCount` cộng toàn cluster phải **= 1**. Khác 1 → `kafka-metadata-quorum.sh describe --status`.
56. `UnderMinIsrPartitionCount` **> 0** = producer `acks=all` **đang bị chặn** → khôi phục replica gấp, **không** hạ `min.insync.replicas` trong hoảng loạn.
57. `IsrShrinksPerSec` / `IsrExpandsPerSec` dao động liên tục = GC, disk chậm hoặc mạng — **không vội** chỉnh `replica.lag.time.max.ms`.
58. `RequestHandlerAvgIdlePercent` **< 0.3** → thiếu I/O thread → tăng `num.io.threads`. `NetworkProcessorAvgIdlePercent` thấp → tăng `num.network.threads`.
59. `TotalTimeMs` tách **5 pha**: queue → local → remote → throttle → response. Produce với `acks=all` có `RemoteTimeMs` cao là **bình thường** (chờ follower).
60. **Lag đo hai kiểu:** `kafka-consumer-groups.sh` đo theo **committed offset**; metric client `records-lag-max` đo theo **position**. Hai số lệch nhau là bình thường — biết đang nhìn số nào mới chẩn đoán đúng. **Cổng:** broker **9092** · controller **9093** · JMX **9999** · Connect REST **8083** · Schema Registry **8081** · ksqlDB **8088**.

## 🚨 Playbook tổng hợp — triệu chứng → hành động (cả 7 tuần)

> **Đây là tài sản quan trọng nhất của tuần chốt.** Gộp bảng playbook của Tuần 1–7 thành một bảng. Đọc theo chiều **triệu chứng → hành động đầu tiên**; cột *Hành động đầu tiên* luôn là **nấc rẻ nhất, đảo ngược được**. Nếu bạn chỉ kịp thuộc một thứ trước khi thi, thuộc bảng này.

| # | Triệu chứng quan sát được | Nguyên nhân khả dĩ | Hành động ĐẦU TIÊN | Tuần |
|---|---|---|---|---|
| 1 | `UnderReplicatedPartitions` > 0 kéo dài | Broker chết · follower tụt · mạng | Kiểm broker sống chưa → rồi mới tăng `num.replica.fetchers` | 3, 7 |
| 2 | `OfflinePartitionsCount` > 0 | Không còn leader cho partition | Kiểm ISR bằng `kt --describe`; cân nhắc ELR; **unclean election là lựa chọn cuối** | 3, 7 |
| 3 | `ActiveControllerCount` tổng ≠ 1 | Controller lỗi hoặc đang failover | `kafka-metadata-quorum.sh describe --status` | 1, 7 |
| 4 | `UnderMinIsrPartitionCount` > 0, producer đứng | ISR < `min.insync.replicas` | Khôi phục replica; **không hạ `min.insync.replicas`** trong hoảng loạn | 3, 7 |
| 5 | Producer nhận `NotEnoughReplicasException` | ISR < min.isr (hoặc min.isr đặt = RF) | `kt --describe` xem ISR; kiểm `min.insync.replicas` **ở mức topic** (override thắng broker) | 2, 3 |
| 6 | `IsrShrinks/ExpandsPerSec` dao động liên tục | GC dài · disk chậm · mạng chập chờn | Đọc GC log và disk latency; **không vội** chỉnh `replica.lag.time.max.ms` | 3, 7 |
| 7 | Idle percent của một thread pool thấp: `RequestHandlerAvgIdlePercent` < 0.3 **hoặc** `NetworkProcessorAvgIdlePercent` thấp, CPU chưa cao | Thiếu thread ở đúng pool đó | Pool nào **idle thấp** thì tăng pool đó: `num.io.threads` (mặc định 8) hoặc `num.network.threads` (mặc định 3) — đều là config **động** | 2, 7 |
| 8 | `TotalTimeMs` cao, dồn ở `RemoteTimeMs` (Produce) | Chờ follower xác nhận | Bình thường với `acks=all`; kiểm sức khoẻ follower trước khi chỉnh gì | 7 |
| 9 | Disk gần đầy trên **một** broker, các broker khác rảnh | Phân bố partition lệch | `kafka-log-dirs.sh --describe` → reassign **có throttle** | 2, 4 |
| 10 | `KafkaStorageException`, một số partition offline, broker vẫn sống | Một `log.dirs` hỏng/đầy | `kafka-log-dirs.sh` tìm đúng dir; cordon dir (4.3) hoặc chuyển replica sang dir khác | 2, 7 |
| 11 | "Đặt retention 1 giờ mà data vẫn còn", hoặc topic compact nhưng key cũ chưa biến mất | Segment **active** chưa đóng (retention và compaction đều chỉ áp cho segment đã đóng); với compact thì `min.cleanable.dirty.ratio` 0.5 chưa đạt | Hạ `segment.ms` / `segment.bytes` — **không** sửa retention; với compact thì kiểm `LogCleaner` còn sống trước khi hạ dirty ratio | 2 |
| 12 | Broker mới lên nhưng **không nhận traffic** | Kafka không tự chuyển partition | `kafka-reassign-partitions.sh --generate` → `--execute --throttle` → `--verify` | 4 |
| 13 | Reassignment chạy mãi không xong | Throttle thấp hơn tốc độ ghi vào | Tăng throttle bằng `--additional --execute --throttle N` | 4 |
| 14 | Sau bảo trì, một broker gánh gần hết leader | Leader không trở về preferred replica | `kafka-leader-election.sh --election-type preferred` (**không** cần reassign) | 4 |
| 15 | Broker không khởi động, log báo `InconsistentClusterId` | Format sai `cluster.id` | Format lại đúng `cluster.id` của cluster | 1 |
| 16 | Client nối được bootstrap nhưng produce timeout | `advertised.listeners` sai địa chỉ | Sửa advertised listener sang địa chỉ client tới được | 1, 5 |
| 17 | Client báo `TopicAuthorizationException` | Thiếu ACL trên Topic | `kafka-authorizer.log` xác nhận → `kafka-acls.sh --add --producer/--consumer` **quyền tối thiểu** | 5 |
| 18 | Client báo `GroupAuthorizationException` | Thiếu ACL trên **Group** | Cấp `Read` trên resource **Group** (consumer cần cả Topic **và** Group) | 5 |
| 19 | Throughput chạm trần đều đặn, log sạch, không lỗi | **Quota** đang throttle (delay response, không báo lỗi) | Kiểm `produce-throttle-time-avg` / `fetch-throttle-time-avg`; xem quota theo 8 mức ưu tiên | 3, 5 |
| 20 | Consumer lag tăng, CPU thấp, rebalance lặp lại | Vượt `max.poll.interval.ms` | Giảm `max.poll.records` hoặc tăng interval — **không** tăng partition | 1, 7 |
| 21 | Lag tăng, thêm consumer **không** đỡ | Consumer ≥ số partition, hoặc key skew | Kiểm skew trước (miễn phí); tăng partition là **một chiều**, để sau cùng | 1, 7 |
| 22 | Connect task ở trạng thái `FAILED` | Lỗi trong connector/converter | `GET /connectors/<n>/status` đọc trace → `restart?includeTasks=true` | 6 |
| 23 | Sink connector bỏ record hỏng **im lặng** | `errors.tolerance=all` mà **không** có DLQ | Thêm `errors.deadletterqueue.topic.name` (+ `context.headers.enable=true`) | 6 |
| 24 | Cần DR nhưng offset phải giữ nguyên | MM2 **đổi** offset, cần translation | **Cluster Linking** (Confluent Platform) nếu được; nếu Apache thuần thì MM2 + `sync.group.offsets.enabled=true` | 4 |
| 25 | Cần retention rất dài mà disk broker đắt | Giữ hết trên disk local | **Tiered storage** (`remote.storage.enable`, `local.retention.ms`) | 4 |

## ⚠️ 15 bẫy xuyên suốt

> Năm bẫy đầu là **bẫy version** — nhóm chiếm nhiều câu sai nhất của CCAAK vì tài liệu ôn công khai vẫn đầy nội dung tiền 4.0. Diệt nhóm này trước, nó rẻ nhất.

1. 🔴 Thấy câu hỏi *"broker nào trở thành controller mới?"* → dễ chọn **"broker đầu tiên tạo lại được ephemeral node trên ZooKeeper"** (đáp án này có thật trong đề dump công khai), nhưng đúng là **controller được bầu bằng Raft trong controller quorum**; Kafka 4.x **không có znode nào**.
2. 🔴 Thấy lệnh CLI có `--zookeeper` hoặc config `zookeeper.connect` → dễ chọn vì quen mắt, nhưng đúng là **`--bootstrap-server`**; `--zookeeper` đã bị gỡ, và ở 4.2 KIP-1147 còn thống nhất luôn tên tuỳ chọn CLI (`--broker-list` cũng đã bị xoá).
3. 🔴 Thấy "bật ACL" → dễ chọn **`AclAuthorizer`**, nhưng đúng là **`StandardAuthorizer`** (KRaft). `AclAuthorizer` bị gỡ cùng ZooKeeper ở 4.0.
4. 🔴 Thấy "tài liệu ôn chia CCAAK thành 4 domain" hoặc đề nhắc **MirrorMaker 1** → đó là **thế hệ trước**: syllabus hiện hành có **7 domain**, và **MM1 đã bị xoá ở 4.0**; DR trên Apache Kafka thuần chỉ còn **MM2**.
5. 🔴 Thấy hỏi "default của `num.recovery.threads.per.data.dir`" → dễ chọn **1** (số cũ), nhưng đúng là **2** từ 4.0. Cùng nhóm: `linger.ms` **5** (không phải 0), `segment.bytes` nhỏ nhất **1 MiB** (không phải 14 byte), và **4.3** `controller.quorum.auto.join.enable` = **false**.
6. Thấy `acks=all` → tưởng "mọi replica phải ack", nhưng đúng là **mọi replica trong ISR**; độ bền thật sự do **`min.insync.replicas`** quyết định.
7. Thấy "cần độ bền tối đa" trên topic RF 3 → dễ chọn **`min.insync.replicas=3`**, nhưng đó là **over-correction**: mất 1 broker là ngừng ghi. Đáp án đúng gần như luôn là **2**.
8. Thấy "lag tăng" → dễ chọn **tăng partition**, nhưng đó là hành động **một chiều** phá key mapping. Thứ tự đúng: kiểm **skew** (miễn phí) → thêm consumer (rẻ, đảo ngược được) → mới tính tới partition.
9. Thấy "partition offline, cần khôi phục dịch vụ ngay" → dễ chọn **`unclean.leader.election.enable=true`**, nhưng nó **đổi dữ liệu lấy availability**. Chỉ đúng khi đề nói rõ *"availability quan trọng hơn dữ liệu"*.
10. Thấy "đổi `min.insync.replicas` ở mức broker" → tưởng áp cho mọi topic, nhưng **topic đã có override thì override thắng**. Luôn kiểm bằng `kafka-configs.sh --describe --all` và đọc cột **synonyms**. *(Thêm: khi **ELR** bật — mặc định cho cluster mới từ 4.1 — `min.insync.replicas` mức broker bị gỡ hẳn.)*
11. Thấy "thêm broker để tăng dung lượng" → tưởng cluster tự cân bằng, nhưng Kafka **không tự chuyển partition**; broker mới chỉ nhận topic **tạo sau**. Phải reassign.
12. Thấy "chạy `--execute --throttle` xong là hết việc" → quên **`--verify`**, và chính `--verify` mới là lệnh **gỡ throttle**. Quên nó = throttle nằm lại bóp cả replication bình thường.
13. Thấy "throughput chạm trần mà log không có lỗi gì" → dễ đi tìm bug, nhưng đó là dấu hiệu kinh điển của **quota**: broker **trì hoãn response**, **không trả lỗi**. Kiểm `produce-throttle-time-avg`.
14. Thấy "DLQ cho connector" → dễ áp cho cả source, nhưng **DLQ chỉ có ở sink**; source lỗi thì chỉ có `errors.tolerance` + log. Và `errors.tolerance=all` **không kèm DLQ** = mất record âm thầm.
15. Thấy "cần DR giữ nguyên offset" → dễ chọn **MirrorMaker 2**, nhưng MM2 **đổi offset** (cần offset translation qua checkpoint). Giữ nguyên byte-for-byte là **Cluster Linking** — và nhớ rằng đó là **Confluent Platform**, không phải Apache Kafka.

## 🧪 Lab checklist

- [ ] **Capstone bước 1** — Cluster production-like: 3 broker + **controller tách riêng**, `broker.rack`, TLS + SCRAM + ACL, quota, Prometheus/Grafana có alert (✅ `kafka-metadata-quorum.sh describe --status` đúng 1 leader; alert URP đã nạp)
- [ ] **Capstone bước 2** — Baseline: topic tạo theo sizing tự tính, ghi metric bình thường ra file (✅ có `baseline.txt` với URP = 0, `ActiveControllerCount` = 1, lag ≈ 0)
- [ ] **Capstone bước 3** ⭐ — **Bài phá durability**: `min.insync.replicas=3` trên RF3 + kill 1 broker → chẩn đoán `NotEnoughReplicas` và khôi phục (✅ producer ghi lại được **mà không** bật unclean election)
- [ ] **Capstone bước 4** ⭐ — **Bài phá storage**: một `log.dirs` hỏng → `kafka-log-dirs.sh` định vị → khôi phục (✅ offline partition về 0, replica nằm đúng dir còn sống)
- [ ] **Capstone bước 5** ⭐ — **Bài phá security**: thu hồi ACL nhầm → `kafka-authorizer.log` tìm ra → cấp lại **quyền tối thiểu** (✅ service chạy lại; `kafka-acls.sh --list` không có quyền thừa)
- [ ] **Capstone bước 6** ⭐ — **Bài phá cân bằng**: broker mới không nhận traffic → reassign có throttle → **gỡ throttle bằng `--verify`** → preferred leader election (✅ broker mới có replica và leader; config throttle đã biến mất)
- [ ] **Capstone bước 7** — **Diễn tập DR**: MM2 sang cluster B, offset consumer group được dịch, dữ liệu khớp (✅ `A.orders` đủ record; group tồn tại ở B dù chưa consumer nào nối B)
- [ ] **🧹 Dọn dẹp toàn bộ** — `docker compose down -v` mọi compose, volume trống

## 🚪 Cổng tự kiểm tra (⭐ CỔNG CUỐI — điều kiện đăng ký thi)

- **Nhịp thời gian bao nhiêu, gặp câu khó thì làm gì?**
  **Đáp án gọn:** **90 giây/câu** (60 câu / 90 phút); quá 2 phút → **đánh dấu + đoán + đi tiếp**, quay lại cuối giờ. Không bỏ trống câu nào.
- **Đọc một câu CCAAK thì việc đầu tiên là gì?**
  **Đáp án gọn:** đọc **triệu chứng** (log/metric/CLI) và tóm tắt thành một câu, rồi xác định **trục**: durability · availability · throughput · chi phí vận hành. Xong mới đọc phương án.
- **Hai phương án đều "đúng kỹ thuật" thì chọn cái nào?**
  **Đáp án gọn:** cái **rẻ hơn và đảo ngược được**. Thang: đọc metric → config động → reassign có throttle → rolling restart → tăng partition (một chiều) → unclean election (mất dữ liệu).
- **Thấy phương án nhắc ZooKeeper/znode/`--zookeeper`/`AclAuthorizer` thì sao?**
  **Đáp án gọn:** gần như chắc chắn **sai** với Kafka 4.x (KRaft-only từ 4.0). Loại ngay, tiết kiệm 30 giây.
- **RF 3, cần chịu mất 1 broker mà không mất dữ liệu và vẫn ghi được — đặt gì?**
  **Đáp án gọn:** `min.insync.replicas=2` + producer `acks=all` + `unclean.leader.election.enable=false`. Đặt **3** là over-correction.
- **Dạng matching và list order xử lý thế nào?**
  **Đáp án gọn:** matching → ghép cặp **chắc nhất trước**, còn lại bằng loại trừ. List order → xác định **bước đầu và bước cuối** rồi điền giữa; ba chuỗi phải thuộc là rolling upgrade, reassignment, và chẩn đoán (metric → log → config → hành động).
- **Một full mock dưới 70% thì làm gì?**
  **Đáp án gọn:** **lùi lịch thi 1 tuần** (đổi lịch ≥5 ngày trước để miễn phí), cày hai domain thấp nhất, mock lại bằng bộ đề khác.
- **🎯 (CÂU CUỐI CÙNG) Đã đủ CẢ 4 điều kiện đăng ký thi chưa?**
  **Đáp án gọn:** (1) **≥3 bộ mock khác nhau ≥80%** ổn định; (2) **review 100% câu sai** + file phân tích 6 mục **+ 3 mục bổ sung** trong `CCAAK/questions/`; (3) đọc trôi **bảng số §6** + **bảng phản xạ §7** + tự viết lại được cram sheet; (4) xong **Capstone "Cluster Rescue" 7 bước** với đủ ✅ Kiểm chứng. **Chưa đủ CẢ 4 → CHƯA đặt lịch thi.**

## 🧪 Checklist trước ngày thi

- [ ] **Đối chiếu trang chính thức** [confluent.io/certification](https://www.confluent.io/certification/) về nhà cung cấp proctor, số câu và lệ phí — ba thông tin này có thể đổi; xem [resources/ccaak-official-exam-page.md](resources/ccaak-official-exam-page.md).
- [ ] Cài **Honorlock Chrome Extension** và chạy **System Check** (webcam, micro, chia sẻ màn hình, mạng) **ít nhất 1 ngày trước** — và chạy lại một lần nữa **sáng ngày thi**.
- [ ] Dùng **Google Chrome** bản mới, tắt VPN và mọi extension khác; **không dùng máy công ty** bị chặn cài extension hoặc bị MDM khoá chia sẻ màn hình.
- [ ] **Government ID** còn hạn, tên **khớp** tài khoản `training.confluent.io` (sửa tên cần vài ngày — làm sớm).
- [ ] **Dọn phòng:** bàn trống, không giấy tờ/thiết bị/điện thoại, đủ sáng, **một mình** trong phòng, khoá cửa; sẵn sàng quay camera **360°** theo yêu cầu proctor.
- [ ] 🧹 **`docker compose down -v` toàn bộ lab capstone** — máy nhẹ thì webcam và chia sẻ màn hình mới mượt.
- [ ] Đăng nhập sớm **15 phút**; kết quả **pass/fail hiện ngay** sau khi nộp — đọc kỹ rồi mới đóng.
- [ ] **Ngủ đủ** đêm trước; ăn nhẹ; trước giờ thi chỉ đọc **cram sheet 60 fact** + **playbook tổng hợp** + **15 bẫy**.
- [ ] Nhắc lại bốn phản xạ: **90 giây/câu** · **đọc triệu chứng trước** · **chọn hành động rẻ và đảo ngược được** · **phương án có ZooKeeper là sai**.

## 📎 Tài nguyên tuần này

> 📂 **Đã crawl sẵn tài liệu vào** [`resources/`](resources/INDEX.md) — đọc offline được.

- **Trang chứng chỉ (chính thức):** [confluent.io/certification](https://www.confluent.io/certification/) — phần CCAAK, 90 phút, dạng câu, Honorlock, retake 7 ngày, hiệu lực 2 năm, đổi lịch 5 ngày → [resources/ccaak-official-exam-page.md](resources/ccaak-official-exam-page.md) và [resources/confluent-certification-policies.md](resources/confluent-certification-policies.md). Đăng ký tại [training.confluent.io](https://training.confluent.io/).
- **Apache Kafka Upgrade notes (4.0 → 4.3):** [kafka.apache.org/43/getting-started/upgrade](https://kafka.apache.org/43/getting-started/upgrade/) — thay đổi ảnh hưởng người vận hành, bảng default đã đổi, tool bị gỡ → [resources/kafka-4x-operational-changes.md](resources/kafka-4x-operational-changes.md).
- **Ba bộ mock full-length của repo:** [mock-01](../../mock-exams/mock-01/questions.md) · [mock-02](../../mock-exams/mock-02/questions.md) · [mock-03](../../mock-exams/mock-03/questions.md) — 60 câu / 90 phút, đúng tỉ trọng 7 domain. Quy trình chạy và bảng theo dõi ở [resources/mock-exam-and-prep-guide.md](resources/mock-exam-and-prep-guide.md).
- **Bản đồ tái sử dụng CCDAK:** [resources/ccaak-vs-ccdak-map.md](resources/ccaak-vs-ccdak-map.md) — domain nào đã có sẵn, domain nào phải làm lab, và 8 chỗ kiến thức CCDAK **lệch** với góc admin.
- **Sách:** *Kafka: The Definitive Guide* 2nd ed. — chương 2 (cài đặt), 6 (reliability), 10 (cross-cluster), 11 (security), 12 (administering), 13 (monitoring). Bản đồ chương ở [`../../../CCDAK/study-plan/week-10/resources/kafka-definitive-guide-chapter-map.md`](../../../CCDAK/study-plan/week-10/resources/kafka-definitive-guide-chapter-map.md).
- **Ôn tổng:** cram sheet 60 fact + playbook tổng hợp ở trên, cộng **bảng số [§6](../../CCAAK-STUDY-PLAN.md#6-những-con-số-phải-thuộc-lòng)** và **bảng phản xạ [§7](../../CCAAK-STUDY-PLAN.md#7-bảng-phản-xạ-triệu-chứng--hành-động)** của Kế hoạch tổng.
- **Sổ câu sai:** file phân tích 6 mục + 3 mục bổ sung trong [`CCAAK/questions/`](../../questions/README.md).
- **Nhật ký validate:** [`../VALIDATION.md`](../VALIDATION.md) — chỗ nào đã xác minh, chỗ nào phải đối chiếu lại trước ngày thi.

## ✅ Checklist hoàn thành Tuần 8

- [ ] Làm **mock cross-domain 30 câu** của tuần này trong **45 phút** và chấm theo 7 domain ([questions.md](questions.md) → [answers.md](answers.md))
- [ ] Hoàn thành **≥3 bộ mock KHÁC NHAU**, mỗi bài canh giờ **90 phút**, cách nhau ≥1 ngày
- [ ] Đạt **≥80% ổn định** trên ≥3 bộ; **không bài nào <70%** (nếu có → đã lùi lịch 1 tuần)
- [ ] **Review 100% câu sai** + viết file phân tích **6 mục + 3 mục bổ sung** trong `CCAAK/questions/`; số câu sai nhãn **"bẫy version" = 0**
- [ ] Đọc trôi chảy **bảng số §6** + **bảng phản xạ §7**; **tự viết lại cram sheet 1 trang** từ trí nhớ và đối chiếu với 60 fact
- [ ] Thuộc **playbook tổng hợp 25 dòng** và **15 bẫy** (đặc biệt 5 bẫy version)
- [ ] Hoàn thành **Capstone "Cluster Rescue" 7 bước** với đủ ✅ Kiểm chứng + **🧹 Dọn dẹp toàn bộ**
- [ ] Hoàn tất **Checklist trước ngày thi** (Honorlock System Check, Chrome, ID, phòng, ngủ đủ)
- [ ] Vượt **Cổng cuối** — trả lời được **CÂU CUỐI: đủ CẢ 4 điều kiện** → đặt lịch thi 🎓
