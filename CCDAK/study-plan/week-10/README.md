# 🏁 Tuần 10 — Tuần chốt — Mock dồn + Review + Cram + Capstone + Thi

> **Domain CCDAK:** Tất cả (tổng ôn 6 domain) · **Thời lượng:** ~11h+ (mock dồn + review + capstone + cram) · **Vị trí:** Tuần 10/10 — vùng đệm đảm bảo đậu 🏁 Full mock #2–4 → Thi
>
> **Điều hướng:** [⬅️ Tuần 9](../week-09/README.md) · [🏠 Kế hoạch tổng](../../CCDAK-STUDY-PLAN.md) · 🎓 Đăng ký & thi

## 🎯 Mục tiêu tuần này

Tuần này **KHÔNG học kiến thức mới**. Toàn bộ trọng tâm là chuyển hoá: từ *"biết Kafka"* sang *"phản xạ đúng dưới áp lực 90 giây/câu + đủ điều kiện đăng ký thi"*.

- **Hoàn tất ≥ 3 bộ practice CCDAK KHÁC NHAU đạt ≥ 80% ổn định** (không phải may mắn 1 lần). CCDAK **không công bố điểm đậu** (chỉ pass/fail), cộng đồng ước ~65–70% → bar cá nhân **80%** cho biên an toàn ≥ 10%.
- **Review 100% câu sai** của mọi mock và **viết file phân tích** trong `CCDAK/questions/` theo đúng format 6 mục của repo (`aws-saa-c03-analysis-format.md`).
- **Làm bài đúng nhịp thi thật:** **60 câu / 90 phút ≈ 90 giây/câu**, biết đánh dấu + bỏ qua + quay lại; xử lý được 3 dạng câu ngoài multiple-choice: **multiple-select, matching, list-order**.
- **Đọc trôi chảy** toàn bộ **bảng số [§6](../../CCDAK-STUDY-PLAN.md#6-những-con-số-phải-thuộc-lòng)** và **bảng phản xạ [§7](../../CCDAK-STUDY-PLAN.md#7-bảng-phản-xạ-keyword--đáp-án)** của Kế hoạch tổng — không cần tra cứu.
- **Tự tay ghép toàn bộ stack 9 tuần** thành 1 pipeline end-to-end (**Capstone "Order Pipeline"** trong [labs.md](labs.md)) và chứng minh được **không mất data khi kill broker**, **replay không xử lý trùng**.
- **Sẵn sàng thi online proctored Confluent:** hiểu điều kiện phòng/webcam/ID/trình duyệt, đã chạy system check, đã đặt lịch. *(Confluent hiện dùng nền tảng proctor **Honorlock** qua Chrome extension theo trang FAQ chính thức — luôn **đối chiếu trang chính thức** trước ngày thi vì nhà cung cấp có thể đổi.)*

## 📚 Nội dung học chi tiết

Bốn "buổi" tuần này quy đổi thành **lịch mock dồn + capstone**. Nguyên tắc: **mỗi full mock cách nhau ≥ 1 ngày** (ngày xen giữa để cày vùng yếu + review + capstone), và **luôn canh giờ 90 phút nghiêm ngặt** như thi thật.

**Gợi ý lịch 7 ngày cuối:**

| Ngày                       | Việc chính                                                                                                                                                  |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Ngày 1**           | 🎯**FULL MOCK #2** = [**Mock 01**](../../mock-exams/mock-01/questions.md) *(nền tảng & bẫy version)*, 60 câu canh giờ 90' → **Review 100% câu sai** + viết file phân tích 6 mục                                                 |
| **Ngày 2**           | Cày**vùng yếu** (domain điểm thấp nhất ở mock #2) + đọc lại **bảng số §6** + **Capstone bước 1–3** (topics/ACL, producer Avro, consumer dedup) |
| **Ngày 3**           | 🎯**FULL MOCK #3** = [**Mock 02**](../../mock-exams/mock-02/questions.md) *(chẩn đoán sự cố)*, canh giờ 90' → Review 100% câu sai + viết file phân tích                                                                            |
| **Ngày 4**           | **Capstone bước 4–7** (Streams join+window EOS, Connect sink+DLQ, kill broker/instance, replay) + đọc lại **bảng phản xạ §7**                       |
| **Ngày 5**           | 🎯**FULL MOCK #4** = [**Mock 03**](../../mock-exams/mock-03/questions.md) *(thiết kế & đánh đổi — khó nhất)* → Review. Xong 3 mock thì tự viết lại **cram sheet 1 trang** từ trí nhớ                            |
| **Ngày 6**           | **Cram:** cram sheet + 60 fact + bảng số §6 + bảng phản xạ §7 + 15 bẫy; chạy **system check Honorlock**, chuẩn bị **ID + phòng**                    |
| **Ngày trước thi** | **Nghỉ nhẹ** — chỉ đọc lướt cram sheet + danh sách bẫy; **ngủ đủ**; `docker compose down -v` mọi thứ; KHÔNG học kiến thức mới                |

### 🅰️ Buổi A — FULL MOCK #2 + chiến lược làm bài CCDAK (~2.5h)

> 📝 **Mock cross-domain 30 câu của repo (phủ 6 domain đúng tỉ trọng CCDAK):** [questions.md](questions.md) — canh giờ **45 phút** (90 giây/câu), tự chấm + **phân tích điểm theo domain** ở [answers.md](answers.md). *(Câu hỏi & giải thích bằng tiếng Anh — văn phong đề thật.)* Dùng làm bài "khởi động" trước khi vào full mock 60 câu/90'.

**Quy trình chạy mock (giống thi thật):**

1. Chọn một bộ practice **60 câu**, đặt đồng hồ **90 phút**, không dừng giữa chừng, không tra tài liệu (thi thật **cấm tài liệu tham khảo & điện thoại**).
2. Áp dụng **chiến lược làm bài** dưới đây trong suốt bài.
3. Chấm điểm, ghi lại **% tổng** và **% theo 6 domain** (bảng chấm ở [answers.md](answers.md)) để biết vùng yếu.

**4 dạng câu CCDAK (theo trang Confluent Certification):**

| Dạng câu                       | Cách nhận diện                                                | Chiến thuật                                                                                                                                              |
| -------------------------------- | -------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Multiple-choice**        | 1 đáp án đúng, 4 lựa chọn                                | Loại 2 đáp án sai rõ → so 2 còn lại theo qualifier                                                                                              |
| **Multiple-select**        | "Select **TWO**/**THREE**"                         | Chọn **đúng số**; mỗi lựa chọn tự đánh giá đúng/sai độc lập; không có điểm một phần                                            |
| **Matching**               | Kéo config/khái niệm ↔ hành vi/mô tả                     | Ghép cặp **chắc chắn nhất trước**, cặp còn lại tự khớp bằng loại trừ; nhớ bảng defaults (linger 5 ms, session 45 s, poll interval 5 phút…) |
| **List-order**             | Sắp xếp thứ tự bước (vd: send flow, rebalance, EOS commit) | Xác định **bước đầu & bước cuối** trước, rồi điền giữa (vd: `beginTransaction` → `send` → `sendOffsetsToTransaction` → `commitTransaction`) |

**Chiến lược làm bài (luyện đến mức tự động):**

- **Nhịp 90 giây/câu.** 60 câu / 90 phút. Một câu quá **2 phút** → **đánh dấu + bỏ qua**, quay lại cuối giờ (không có điểm trừ khi đoán).
- **Đọc CÂU HỎI trước, đáp án sau.** Xác định *đề đang hỏi gì* (hành vi? config? nguyên nhân lỗi?) trước khi bị 4 lựa chọn dẫn dắt.
- **Gạch chân qualifier Kafka:** "**guarantee ordering**", "**no data loss**", "**minimize latency**", "**exactly-once**", "**without changing producer code**", "**minimal rebalance**", "**highest throughput**" — qualifier quyết định đáp án.
- **Bẫy số liệu đổi theo version:** đề cũ/khoá học cũ hay ghi số cũ. Kafka **4.0**: `linger.ms` = **5** (cũ 0); **3.0**: `acks` = **all** & `enable.idempotence` = **true** (cũ `acks=1`/false), `session.timeout.ms` = **45 s** (cũ 10 s). Nếu đề nói "default" → trả lời theo **bản mới nhất**, trừ khi đề nêu version.
- **Bẫy "đúng kỹ thuật nhưng không đáp ứng qualifier":** vd đề đòi "without changing producer code" mà đáp án là bật `enable.idempotence` phía producer → **loại**; đáp án đúng nằm ở broker/topic config hoặc consumer.
- **Multiple-select:** đọc rõ số cần chọn; đánh giá **từng** lựa chọn như câu true/false độc lập.
- **Hạn chế đổi đáp án:** chỉ đổi khi phát hiện **đã đọc sót** một chi tiết rõ ràng.

### 🅱️ Buổi B — Review 100% câu sai + viết file phân tích (~3h)

1. **Rà từng câu sai** (và cả câu *đúng nhưng đoán may*): xác định **lý do sai** — thiếu kiến thức / đọc sót qualifier / dính bẫy số liệu version / quản lý giờ.
2. Với mỗi câu đáng nhớ, **viết một file phân tích** trong `CCDAK/questions/` (đặt tên `CCDAK-NNNN.md`) theo **format 6 mục** của `aws-saa-c03-analysis-format.md`:
   1. **CONTEXT & ĐỀ BÀI** — Scenario / Existing Resources / Current Issue-Goal
   2. **KEYWORDS QUAN TRỌNG** — bảng 2 cột `Keyword` | `Ý nghĩa / Gợi ý`
   3. **YÊU CẦU CỦA ĐỀ** — Question type (no data loss / ordering / exactly-once / minimal latency…) + Constraints
   4. **ĐÁP ÁN ĐÚNG** — `✅ Đáp án: X` + giải thích
   5. **CÁC ĐÁP ÁN SAI** — `❌` từng đáp án: vì sao sai + khi nào thì nó ĐÚNG
   6. **MẸO GHI NHỚ (Memory Hook)** — mở đầu bằng `🧠`
3. **Ví dụ rút gọn** 1 file phân tích câu Kafka:

   ```markdown
   # KAFKA-0001 — Producer mất message khi broker leader crash

   ## 1. CONTEXT & ĐỀ BÀI
   - **Scenario:** Producer ghi vào topic RF=3, thấy mất record sau khi 1 broker leader crash.
   - **Existing Resources:** Topic `payments`, `acks=1`, `min.insync.replicas=1`.
   - **Current Issue/Goal:** Không mất data khi leader fail, không giảm nhiều throughput.

   ## 2. KEYWORDS QUAN TRỌNG
   | Keyword | Ý nghĩa / Gợi ý |
   |---------|-----------------|
   | `acks=1` | leader ack xong là trả về → follower chưa kịp copy → mất khi leader chết |
   | `min.insync.replicas` | số replica tối thiểu trong ISR để ghi `acks=all` thành công |
   | "no data loss" | qualifier → cần `acks=all` + `min.insync.replicas=2` + RF=3 |

   ## 3. YÊU CẦU CỦA ĐỀ
   - **Question type:** No data loss (durability).
   - **Constraints:** RF=3 đã có; không muốn đổi RF; chấp nhận latency tăng nhẹ.

   ## 4. ĐÁP ÁN ĐÚNG
   **✅ Đáp án: B** — `acks=all` + topic `min.insync.replicas=2`.
   - `acks=all` chờ mọi replica trong ISR ack; `min.isr=2` đảm bảo ít nhất 2 bản trước khi ack.
   - Mất 1 broker vẫn ghi được (ISR còn 2); mất 2 → `NotEnoughReplicasException` thay vì âm thầm mất data.

   ## 5. CÁC ĐÁP ÁN SAI
   **❌ Đáp án A (`acks=0`):** nhanh nhất nhưng fire-and-forget → mất nhiều hơn. Đúng khi: metrics/log chấp nhận mất.
   **❌ Đáp án C (`min.insync.replicas=3`):** mất 1 broker là không ghi được → giảm availability. Đúng khi: đề đòi durability tuyệt đối, chấp nhận downtime.
   **❌ Đáp án D (`unclean.leader.election.enable=true`):** tăng availability nhưng CHO PHÉP mất data. Đúng khi: đề ưu tiên availability hơn durability.

   ## 6. MẸO GHI NHỚ (Memory Hook)
   🧠 *"RF 3 – ISR 2 – acks all: mất 1 vẫn chạy, mất 2 thì báo lỗi, không bao giờ âm thầm mất."*
   ```
4. **Ghi sổ câu sai** và ôn theo **spaced repetition 1 / 3 / 7 ngày**.
5. **Cày lại bảng số §6** cho các con số dính sai trong mock (vd `delivery.timeout.ms` 120 s, `offsets.retention.minutes` 7 ngày, `connect-offsets` 25 partition…).

### 🅲️ Buổi C — Capstone end-to-end + Cram sheet 1 trang (~3.5h)

> 🏗️ **Capstone "Order Pipeline" ⭐ (7 bước, ghép toàn bộ stack 9 tuần):** [labs.md](labs.md). Tóm tắt:
>
> 1. **Topics + ACL** — `orders` (12 partition, RF3, `min.insync.replicas=2`), `customers` (compacted), `order-stats`, `orders-dlq`; ACL cho user `order-svc` (write) và `analytics` (read + group). *(Tuần 1, 2, 7)*
> 2. **Producer Node Avro** — `Schema Registry` + idempotent, key = `customerId`, 1.000 order + 5% record hỏng cố ý. *(Tuần 3, 5)*
> 3. **Consumer group `fulfillment`** — manual commit, dedup idempotent, retry → DLQ. *(Tuần 4, 9)*
> 4. **Kafka Streams Java** — join `orders` × `customers` (KTable) → tumbling 1 phút tổng tiền theo country → `order-stats`, `exactly_once_v2`. *(Tuần 6)*
> 5. **Connect FileStreamSink** từ `order-stats` với SMT + DLQ. *(Tuần 5)*
> 6. **Grafana**: lag, URP; **kill 1 broker** → chứng minh không mất data; **kill 1 Streams instance** → task chuyển. *(Tuần 8)*
> 7. **Reset offsets `fulfillment` về đầu** → replay không xử lý trùng nhờ dedup. *(Tuần 4, 9)*

**Cram sheet 1 trang — TỰ VIẾT LẠI từ trí nhớ** (không copy), gồm 7 khối; đối chiếu với `## 🧠 Cram sheet — 60 fact` bên dưới sau khi viết xong:

| Khối                             | Nội dung phải có                                                                                                                                                  |
| --------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **1. Defaults producer**    | `acks`, `enable.idempotence`, `retries`, `delivery.timeout.ms`, `linger.ms`, `batch.size`, `buffer.memory`, `max.in.flight`, `compression.type`, `max.request.size` |
| **2. Defaults consumer**    | `max.poll.records`, `max.poll.interval.ms`, `session.timeout.ms`, `heartbeat.interval.ms`, `fetch.min.bytes`, `fetch.max.wait.ms`, `enable.auto.commit`, `auto.offset.reset`, `isolation.level` |
| **3. Defaults broker/topic** | `num.partitions`, RF, `min.insync.replicas`, `message.max.bytes`, retention (168 h), segment (1 GB), `replica.lag.time.max.ms`, `unclean.leader.election.enable`, ports |
| **4. Delivery semantics matrix** | at-most-once / at-least-once / exactly-once × (producer config, consumer commit vị trí, isolation.level)                                                        |
| **5. Rebalance protocols**  | classic eager vs cooperative (`CooperativeStickyAssignor`) vs KIP-848 `group.protocol=consumer` (server-side, GA 4.0); static membership; Streams KIP-1071        |
| **6. Compatibility & Streams** | 7 mode SR (`BACKWARD` default…), 3 subject strategy, wire format 5 byte; tumbling/hopping/sliding/session; 4 loại join & co-partition; EOS v2 commit 100 ms           |
| **7. Exception → fix / Metric → ngưỡng** | `NotEnoughReplicas`, `RecordTooLarge`, `CommitFailed`, `OffsetOutOfRange`, `SerializationException`, `ProducerFenced`; URP > 0, `records-lag-max` tăng, `ActiveControllerCount` ≠ 1, `request-latency-avg`, `rebalance-rate` |

### 🅳 Buổi D — FULL MOCK #3 (và #4 nếu cần) + van an toàn (~2h)

1. **≥ 1 ngày sau mock #2**, chạy **FULL MOCK #3** (bộ đề KHÁC), lặp lại đúng quy trình canh giờ 90' + chiến lược.
2. Review 100% câu sai + viết file phân tích như Buổi B.
3. Nếu **chưa đủ 3 bài ≥ 80%** → xếp thêm **FULL MOCK #4** (cách ≥ 1 ngày, bộ đề thứ 4).
4. **🚨 VAN AN TOÀN:** bất kỳ full mock nào **< 70%** → **lùi lịch thi 1 tuần** (Confluent cho đổi lịch miễn phí nếu ≥ 5 ngày trước giờ thi — đối chiếu FAQ), tập trung 100% vào domain điểm thấp nhất rồi mới mock lại.
5. **Spaced repetition** lần cuối cho cụm hay quên: EOS end-to-end (producer transaction + `read_committed` + Streams EOS v2), rebalance protocol, compatibility mode, Connect DLQ chỉ sink.

## 🧠 PHẢI NHỚ tuần này

**Thông tin kỳ thi (bám đúng để phân bổ giờ):**

| Fact                        | Con số / Ghi nhớ                                                                                                                      |
| --------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| Số câu                    | **60 câu** (tổng hợp từ cộng đồng; trang Confluent không công bố — đối chiếu)                                             |
| Thời gian                  | **90 phút** ("90 minute proctored exams" — trang Confluent) → **90 giây/câu**                                                    |
| Dạng câu                   | **multiple-choice, multiple-select, matching, list order**                                                                           |
| Điểm đậu                | **Không công bố**, chỉ **pass/fail**, kết quả **hiện ngay trên màn hình** sau khi nộp; ước ~65–70%                          |
| **Bar cá nhân**       | **≥ 80% ổn định** trên ≥ 3 bộ → biên an toàn ≥ 10% so với ngưỡng ước tính                                             |
| Lệ phí                    | **150 USD** (kiểm chứng lại lúc mua trên training.confluent.io)                                                                   |
| Hiệu lực chứng chỉ     | **2 năm**, phải **tái chứng nhận mỗi 2 năm**                                                                                    |
| Thi lại                    | Chờ **7 ngày** mới được mua & thi lại                                                                                             |
| Đổi/huỷ lịch             | Miễn phí nếu **≥ 5 ngày** trước; trong 5 ngày → **không hoàn phí**                                                            |
| Hình thức thi              | **Online proctored** qua **Honorlock** (Chrome extension + System Check), webcam + micro + Chrome; **government ID**                 |
| Ngôn ngữ                   | Chỉ **tiếng Anh**; cần hỗ trợ đặc biệt → email `certification@confluent.io` trước **21 ngày**                              |
| Version neo                 | **Apache Kafka 4.3** (KRaft-only từ 4.0); đề có thể còn nội dung 3.x → luôn trả lời theo default **mới nhất** trừ khi đề nêu version |
| Tài liệu tham khảo        | **Cấm** — không tài liệu, không điện thoại trong lúc thi                                                                          |

**Tiêu chí SẴN SÀNG đăng ký thi — CHỈ đặt lịch khi ĐỦ CẢ 4:**

| # | Tiêu chí                                                                                                              |
| - | ----------------------------------------------------------------------------------------------------------------------- |
| 1 | ✅**≥ 3 bộ practice KHÁC NHAU đạt ≥ 80%** (ổn định, canh giờ 90', không tra tài liệu)                       |
| 2 | ✅ Đã**review hết 100% câu sai** và viết file phân tích 6 mục cho câu đáng nhớ trong `CCDAK/questions/`       |
| 3 | ✅ Đọc**trôi chảy** toàn bộ **bảng số §6** + **bảng phản xạ §7** + tự viết lại được cram sheet 1 trang |
| 4 | ✅ Hoàn thành**Capstone "Order Pipeline" 7 bước** với đủ ✅ Kiểm chứng (kill broker không mất data, replay không trùng) |

> 🚨 **VAN AN TOÀN:** Bất kỳ full mock nào **< 70%** → **lùi lịch thi 1 tuần**, tập trung 100% vào vùng yếu rồi mới mock lại.

## 🧠 Cram sheet — 60 fact trong 1 trang

**Producer (1–12)**

1. `acks=all` mặc định (từ 3.0); `acks=0` fire-and-forget, `acks=1` leader-only.
2. `enable.idempotence=true` mặc định (3.0); yêu cầu `acks=all`, `retries>0`, `max.in.flight ≤ 5`. Từ 4.0 không tự fallback khi `max.in.flight > 5` → lỗi config.
3. `retries=Integer.MAX_VALUE`; giới hạn thực tế bởi `delivery.timeout.ms=120000` (≥ `linger.ms` + `request.timeout.ms=30000`).
4. `linger.ms=5` (4.0, KIP-1030; cũ 0); `batch.size=16384`; batch gửi khi đầy HOẶC hết linger.
5. `buffer.memory=32 MB`; đầy → block `max.block.ms=60000` → `TimeoutException`.
6. `max.request.size=1 MB` (producer) vs `message.max.bytes≈1 MB` (broker) vs `max.partition.fetch.bytes=1 MB` (consumer) — phải nâng cả 3 cho message lớn.
7. `compression.type=none`; none/gzip/snappy/lz4/zstd; nén theo batch, batch lớn nén tốt hơn.
8. Partitioner: có key → murmur2 % partitions; không key → sticky partitioner (KIP-480/794). Tăng partition → phá mapping key→partition.
9. Retriable: `NotLeaderOrFollower`, `NotEnoughReplicas`, `NetworkException`; Fatal: `RecordTooLarge`, `SerializationException`, `Authorization`, `InvalidTopic`.
10. Transactions: `transactional.id` bắt buộc → `initTransactions` → `beginTransaction` → `send` → `sendOffsetsToTransaction` → `commitTransaction`/`abortTransaction`.
11. `transaction.timeout.ms=60000` (broker cap `transaction.max.timeout.ms=900000`); `transactional.id.expiration.ms` 7 ngày; `__transaction_state` 50 partition.
12. Producer khác cùng `transactional.id` → epoch bump → producer cũ nhận `ProducerFencedException` (fatal, phải đóng).

**Consumer (13–26)**

13. `max.poll.records=500`; `max.poll.interval.ms=300000` (5 phút) — vượt → rời group dù heartbeat vẫn sống.
14. `session.timeout.ms=45000` (3.0; cũ 10 s); `heartbeat.interval.ms=3000` (≤ 1/3 session). Heartbeat chạy thread riêng.
15. `fetch.min.bytes=1`, `fetch.max.wait.ms=500`, `fetch.max.bytes=50 MB`, `max.partition.fetch.bytes=1 MB`.
16. `enable.auto.commit=true`, `auto.commit.interval.ms=5000` — commit ở lần `poll()` kế → at-least-once (trùng khi crash).
17. `auto.offset.reset=latest` mặc định; `earliest`; `none` → `NoOffsetForPartitionException`. Chỉ áp dụng khi **không có committed offset** hoặc offset out of range.
18. at-most-once = commit **trước** xử lý; at-least-once = commit **sau** xử lý; exactly-once = transactions + `isolation.level=read_committed`.
19. `commitSync` chặn + retry; `commitAsync` không chặn, không retry (thứ tự commit có thể lệch) → pattern: async trong loop, sync khi đóng.
20. Assignors classic: `RangeAssignor` (default cùng `CooperativeStickyAssignor`), `RoundRobin`, `Sticky`, `CooperativeSticky` (incremental, không stop-the-world).
21. KIP-848: `group.protocol=consumer` (GA 4.0), assignor **server-side** `uniform`/`range`, không dùng `partition.assignment.strategy`, không `session.timeout` phía client; 4.3 bắt đầu cảnh báo deprecate `classic` (KIP-1274).
22. Static membership: `group.instance.id` → restart trong `session.timeout.ms` không rebalance.
23. `__consumer_offsets` 50 partition compacted; `offsets.retention.minutes=10080` (7 ngày) cho group rỗng.
24. `isolation.level=read_uncommitted` mặc định; `read_committed` chỉ đọc tới LSO (Last Stable Offset).
25. `CommitFailedException` = group đã rebalance (xử lý quá `max.poll.interval.ms`) → giảm `max.poll.records` hoặc tăng interval.
26. Share groups (Queues for Kafka, KIP-932): GA **4.2**, per-record ack (ACCEPT/RELEASE/REJECT/RENEW), nhiều consumer cùng partition, **không đảm bảo thứ tự**, `share.version=1`.

**Broker / Topic / KRaft (27–38)**

27. `num.partitions=1`, `default.replication.factor=1`, `min.insync.replicas=1` mặc định → production: RF3 + min.isr 2 + acks=all.
28. ISR: follower tụt > `replica.lag.time.max.ms=30000` → rời ISR. `acks=all` chỉ chờ ISR, không chờ mọi replica.
29. `unclean.leader.election.enable=false` → không có ISR → partition offline (ưu tiên durability). `true` → mất data có thể.
30. ELR (KIP-966, GA 4.0/bật mặc định cluster mới 4.1): replica ngoài ISR nhưng an toàn để làm leader không mất data.
31. Retention: `log.retention.hours=168`, `log.retention.bytes=-1` (per partition), `log.segment.bytes=1 GB`, chỉ xoá **segment đã đóng**; check mỗi `300000` ms.
32. Compaction: `cleanup.policy=compact`; giữ value mới nhất theo key; tombstone (value null) giữ `delete.retention.ms=24 h`; `min.cleanable.dirty.ratio=0.5`; active segment không compact.
33. `message.max.bytes=1048588`; `replica.fetch.max.bytes=1048576`.
34. High watermark = offset đã replicate tới toàn ISR; consumer chỉ đọc tới HW.
35. KRaft: `process.roles=broker|controller|broker,controller` (combined chỉ dev); quorum **3 hoặc 5** controller; `__cluster_metadata`; `controller.quorum.voters` (static) / `controller.quorum.bootstrap.servers` (dynamic, KIP-853); `kafka-storage.sh format`.
36. Kafka 4.0: gỡ ZooKeeper; broker/Connect/tools **Java 17+**, clients/Streams **Java 11+**; baseline client protocol **2.1**; `num.recovery.threads.per.data.dir` 1→2.
37. Ports: broker 9092, controller 9093, Schema Registry 8081, Connect 8083, ksqlDB 8088, JMX 9999/9101.
38. Quotas: `producer_byte_rate`, `consumer_byte_rate`, `request_percentage` theo user/client-id → broker **throttle** (delay response), không lỗi.

**Schema Registry / Connect (39–47)**

39. Wire format: 1 byte magic (0) + 4 byte schema ID + payload = **5 byte** overhead.
40. `BACKWARD` (default): consumer schema mới đọc data cũ → được **xoá field**, **thêm field có default**; nâng **consumer trước**.
41. `FORWARD`: producer nâng trước → được **thêm field**, **xoá field có default**. `FULL` = cả hai → chỉ thêm/xoá field **có default**. `*_TRANSITIVE` so với mọi version; `NONE` tắt kiểm.
42. Subject: `TopicNameStrategy` (default `<topic>-value`), `RecordNameStrategy` (nhiều kiểu/topic), `TopicRecordNameStrategy`.
43. Connect: worker standalone (1 process, offset file) vs distributed (REST 8083, group.id, internal topics); `tasks.max`.
44. Internal topics: `connect-configs` 1 partition, `connect-offsets` **25**, `connect-status` **5** — đều compacted.
45. Converter (`key.converter`/`value.converter`, đổi format bytes) ≠ SMT (`transforms`, sửa từng record); `schemas.enable` cho JsonConverter.
46. `errors.tolerance=all` + `errors.deadletterqueue.topic.name` — DLQ **chỉ sink connector**; `errors.deadletterqueue.context.headers.enable=true` ghi lý do vào header; `errors.log.enable`.
47. Exactly-once source: worker `exactly.once.source.support=enabled` + connector `exactly.once.support=required` (3.3+). Debezium = CDC source đọc WAL/binlog.

**Kafka Streams (48–54)**

48. `processing.guarantee=at_least_once` mặc định; `exactly_once_v2` (2.6+, broker ≥ 2.5) → `commit.interval.ms` 30000 → **100**.
49. Số task = số partition lớn nhất của input topics trong sub-topology; `num.stream.threads=1`; task là đơn vị song song, thread chạy nhiều task.
50. State store + changelog `<app.id>-<store>-changelog` (compacted); `num.standby.replicas=0` mặc định → set 1 để failover nhanh; repartition topic khi đổi key trước aggregation.
51. KStream (event, insert) vs KTable (changelog, upsert, key mới nhất) vs GlobalKTable (bản đầy đủ mọi instance, không co-partition).
52. Windows: tumbling (size=advance, không chồng), hopping (advance<size, chồng), sliding (theo khoảng cách record), session (inactivity gap); grace period bắt buộc khai báo (`ofSizeAndGrace` / `ofSizeWithNoGrace`).
53. Joins: KStream-KStream **windowed** + co-partition; KStream-KTable không window + co-partition; KTable-KTable không window; KStream-GlobalKTable không cần co-partition.
54. `TopologyTestDriver` test topology không cần broker; KIP-1071 Streams rebalance protocol GA 4.2 (`group.protocol=streams`); `kafka-streams-scala` deprecated 4.3.

**Security / Testing / Observability (55–60)**

55. `security.protocol`: PLAINTEXT / SSL / SASL_PLAINTEXT / SASL_SSL; SASL mechanism: PLAIN, SCRAM-SHA-256/512 (credential trong metadata KRaft), GSSAPI (Kerberos), OAUTHBEARER; mTLS = SSL + `ssl.client.auth=required`.
56. ACL KRaft: `StandardAuthorizer`; mặc định **deny** khi có authorizer (`allow.everyone.if.no.acl.found=false`); `super.users`; consumer cần `Read` topic + `Read` group; producer cần `Write` topic (+ `IdempotentWrite` cluster cho idempotence cũ, `Describe`).
57. Test: `MockProducer`/`MockConsumer` (unit, không broker), `TopologyTestDriver` (Streams), Testcontainers/EmbeddedKafka (integration, broker thật), contract test với Schema Registry (kiểm compat trước deploy).
58. Lag = log-end-offset − committed offset; `records-lag-max` (consumer JMX) ; lag tăng liên tục = consumer chậm/đứng → scale consumer ≤ số partition.
59. Broker metrics: `UnderReplicatedPartitions` > 0, `OfflinePartitionsCount` > 0, `ActiveControllerCount` ≠ 1 (tổng cluster), `RequestHandlerAvgIdlePercent` < 0.3, `IsrShrinksPerSec`.
60. MirrorMaker 2 = Connect-based (MM1 gỡ ở 4.0), offset translation `RemoteClusterUtils`; Cruise Control cân bằng; tiered storage tách local/remote (`remote.storage.enable`, `local.retention.ms`).

## ⚠️ Bẫy đề tổng hợp 15 bẫy xuyên tuần

1. Thấy "default `acks`" → dễ chọn `1` (đề cũ), nhưng đúng là **`all`** (từ 3.0); tương tự `enable.idempotence` mặc định **true**.
2. Thấy "default `linger.ms`" → dễ chọn `0`, nhưng đúng là **5 ms** từ Kafka 4.0 (KIP-1030).
3. Thấy "default `session.timeout.ms`" → dễ chọn 10 s, nhưng đúng là **45 s** (3.0). Consumer xử lý 6 phút bị kick là do **`max.poll.interval.ms`** (5 phút), không phải session timeout.
4. Thấy `acks=all` → tưởng "mọi replica phải ack", nhưng đúng là **mọi replica trong ISR**; độ bền thực sự do **`min.insync.replicas`** quyết định.
5. Thấy `min.insync.replicas=2` với RF=3 và 2 broker chết → dễ nghĩ "vẫn ghi được với acks=1", đúng là **`acks=1` vẫn ghi được** (chỉ leader), **`acks=all` → `NotEnoughReplicasException`**. Đọc kỹ acks trong đề.
6. Thấy "idempotent producer" → tưởng exactly-once end-to-end, nhưng idempotence chỉ chống trùng **trong 1 partition, 1 producer session**; end-to-end cần **transactions + `read_committed`**.
7. Thấy "giữ thứ tự với retries" → dễ chọn `max.in.flight=1`, nhưng với idempotence bật thì **`max.in.flight ≤ 5` vẫn giữ thứ tự**; `=1` chỉ cần khi idempotence tắt.
8. Thấy `auto.offset.reset=earliest` → tưởng lúc nào cũng đọc từ đầu, nhưng chỉ khi **không có committed offset** cho group; group cũ đã commit thì đọc tiếp từ offset đó.
9. Thấy "consumer nhiều hơn partition" → dễ nghĩ tăng throughput, nhưng consumer dư **idle**; muốn scale hơn phải **tăng partition** (và chấp nhận phá key mapping) hoặc dùng **share group**.
10. Thấy "xoá field khỏi schema, consumer nâng trước" → dễ chọn `FORWARD`, nhưng đúng là **`BACKWARD`** (default). Ngược lại producer nâng trước = `FORWARD`.
11. Thấy "DLQ cho connector" → dễ áp cho cả source, nhưng **DLQ chỉ có ở sink connector**; source lỗi thì `errors.tolerance` + log.
12. Thấy "đổi format JSON → Avro" → dễ chọn SMT, nhưng đó là việc của **Converter**; SMT chỉ sửa record (rename/mask/route).
13. Thấy "join 2 KStream" → quên **window** và **co-partitioning**; join KStream với dữ liệu tham chiếu nhỏ không cùng key → **GlobalKTable**.
14. Thấy "exactly_once_v2" → tưởng chỉ là config Streams, nhưng cần **broker ≥ 2.5** và **`commit.interval.ms` tự xuống 100 ms** → throughput giảm; đề hỏi "why slower after EOS" → đây.
15. Thấy "Java client" → nghĩ CCDAK chỉ hỏi API; thực tế đề nặng **config + hành vi** (defaults, exception nào retriable, metric nào báo gì). Kafka 4.x **không còn ZooKeeper** → đáp án có `zookeeper.connect`/`--zookeeper` là **sai**.

## 🔁 Phản xạ nhanh (keyword → đáp án)

| Thấy qualifier / từ khoá                                       | Bật ngay                                                                                                  |
| ---------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| "no data loss" / "durability"                                    | `acks=all` + `min.insync.replicas=2` + RF≥3 + `unclean.leader.election.enable=false` + idempotence     |
| "guarantee ordering" (per key)                                   | cùng key → cùng partition; idempotence + `max.in.flight ≤ 5`; không tăng partition                    |
| "exactly-once" producer→consumer                                 | `transactional.id` + `sendOffsetsToTransaction` + consumer `isolation.level=read_committed`             |
| "exactly-once" Kafka Streams                                     | `processing.guarantee=exactly_once_v2`                                                                   |
| "minimize latency" producer                                      | `linger.ms=0`, `batch.size` nhỏ, `acks=1` (nếu chấp nhận rủi ro), `compression.type=none`             |
| "maximize throughput" producer                                   | tăng `linger.ms` + `batch.size`, `compression.type=lz4/zstd`, nhiều partition                        |
| "without changing producer code"                                 | sửa **topic/broker config** (`min.insync.replicas`, `retention`, `max.message.bytes`) hoặc phía consumer |
| "consumer kicked out while processing"                           | `max.poll.interval.ms` (5 phút) → giảm `max.poll.records` / xử lý async                               |
| "no rebalance on restart / rolling deploy"                       | static membership `group.instance.id` (+ `CooperativeStickyAssignor` hoặc KIP-848)                     |
| "stop-the-world rebalance"                                       | eager → chuyển `CooperativeStickyAssignor` hoặc `group.protocol=consumer`                               |
| "queue semantics / nhiều consumer hơn partition / per-record ack" | **share group** (Queues for Kafka, GA 4.2)                                                              |
| "keep latest value per key" / "changelog"                        | `cleanup.policy=compact` (+ KTable)                                                                      |
| "add field with default, consumers upgraded first"               | `BACKWARD` compatibility                                                                                 |
| "route bad records instead of failing connector"                 | `errors.tolerance=all` + `errors.deadletterqueue.topic.name` (sink)                                      |
| "enrich stream with small reference table on different key"      | `GlobalKTable` join                                                                                       |
| "count per 5 minutes non-overlapping"                            | tumbling window                                                                                            |
| "overlapping windows every 1 min size 5 min"                     | hopping window                                                                                             |
| "user session ends after 30 min inactivity"                      | session window                                                                                             |
| "test topology without broker"                                   | `TopologyTestDriver`; producer/consumer logic → `MockProducer`/`MockConsumer`                            |
| "`UnderReplicatedPartitions` > 0"                                | follower tụt/broker down → check broker health, `replica.lag.time.max.ms`, disk/network                 |

## 🧪 Lab checklist

- [ ] **Capstone bước 1** — Topics `orders`/`customers`/`order-stats`/`orders-dlq` + ACL `order-svc`/`analytics` (✅ describe đúng 12 partition, RF3, min.isr 2; user không quyền bị `TopicAuthorizationException`)
- [ ] **Capstone bước 2** — Producer Node Avro idempotent, 1.000 order + 50 record hỏng vào `orders-raw-bad` (✅ schema `orders-value` v1 trên SR; end offset tổng = 1.000)
- [ ] **Capstone bước 3** — Consumer group `fulfillment` manual commit + dedup + retry/DLQ (✅ processed = 1.000, duplicates skipped ≥ 0, DLQ nhận record hỏng)
- [ ] **Capstone bước 4** — Streams Java join + tumbling 1 phút EOS v2 → `order-stats` (✅ tổng tiền theo country khớp với tính tay từ dữ liệu producer)
- [ ] **Capstone bước 5** — Connect FileStreamSink + SMT + DLQ từ `order-stats` (✅ file có dòng JSON, connector `RUNNING`)
- [ ] **Capstone bước 6** — Grafana lag/URP; kill broker → không mất data; kill Streams instance → task chuyển (✅ end offset không đổi, URP về 0 sau restart)
- [ ] **Capstone bước 7** — Reset offsets `fulfillment` về đầu → replay 1.000 record, dedup bỏ 100% (✅ processed mới = 0, skipped = 1.000)
- [ ] **🧹 Dọn dẹp toàn bộ** — `docker compose down -v` mọi compose, xoá volumes/images (tuỳ chọn)

## 🚪 Cổng tự kiểm tra (⭐ CỔNG CUỐI — điều kiện đăng ký thi)

- **Nhịp thời gian bao nhiêu, làm gì khi gặp câu khó?**
  **Đáp án gọn:** **90 giây/câu** (60 câu / 90 phút); câu quá 2 phút → **đánh dấu + bỏ qua + quay lại cuối giờ**, không sa đà.
- **Đề hỏi "default" mà không nêu version thì trả lời theo gì?**
  **Đáp án gọn:** theo **bản mới nhất** (4.3): `acks=all`, `enable.idempotence=true`, `linger.ms=5`, `session.timeout.ms=45 s`, `max.poll.interval.ms=5 phút`, `auto.offset.reset=latest`.
- **Thấy "no data loss" thì phản xạ chuỗi config nào?**
  **Đáp án gọn:** `acks=all` + `min.insync.replicas=2` + RF≥3 + `unclean.leader.election.enable=false` + idempotence (+ consumer commit **sau** xử lý).
- **Exactly-once end-to-end cần đúng 3 mảnh nào?**
  **Đáp án gọn:** producer **transactional** (`transactional.id`, `sendOffsetsToTransaction`) + consumer **`read_committed`** + (nếu Streams) **`exactly_once_v2`**. Idempotence một mình **không** đủ.
- **Dạng matching/list-order xử lý thế nào?**
  **Đáp án gọn:** ghép cặp **chắc nhất trước**, còn lại bằng loại trừ; list-order xác định **bước đầu & cuối** trước (vd `initTransactions` đầu, `commitTransaction` cuối).
- **Multiple-select nên chọn thế nào?**
  **Đáp án gọn:** đánh giá **từng lựa chọn** như true/false độc lập; chọn **đúng số** đề yêu cầu — không thừa, không thiếu.
- **Mock < 70% thì làm gì?**
  **Đáp án gọn:** **lùi lịch thi 1 tuần** (đổi lịch ≥ 5 ngày trước để miễn phí), cày domain thấp nhất, mock lại bằng bộ đề khác.
- **🎯 (CÂU CUỐI CÙNG) Đã đủ CẢ 4 tiêu chí sẵn sàng chưa?**
  **Đáp án gọn:** (1) ≥3 bộ practice khác nhau ≥80% ổn định; (2) review 100% câu sai + file phân tích 6 mục; (3) đọc trôi bảng số §6 + bảng phản xạ §7 + tự viết lại cram sheet; (4) xong Capstone 7 bước với đủ kiểm chứng. **Chưa đủ CẢ 4 → CHƯA đặt lịch thi.**

## 🧪 Checklist ngày thi

- [ ] **Đối chiếu trang chính thức** [confluent.io/certification](https://www.confluent.io/certification/) về nhà cung cấp proctor, số câu, lệ phí (thông tin có thể đổi).
- [ ] Cài **Honorlock Chrome Extension**, chạy **System Check** (webcam, micro, tốc độ mạng) ít nhất 1 ngày trước; đường truyền yếu có thể bị **tính là mất lượt**.
- [ ] Dùng **Google Chrome**, tắt VPN/extension khác, đóng mọi ứng dụng; **không** dùng máy công ty bị chặn cài extension.
- [ ] **Government ID** còn hạn, tên **khớp** với tài khoản đăng ký.
- [ ] **Dọn phòng**: bàn trống, không giấy tờ/thiết bị/điện thoại, đủ sáng, **một mình** trong phòng; sẵn sàng quay 360° phòng theo yêu cầu proctor.
- [ ] Đăng nhập sớm **15 phút**; kết quả **pass/fail hiện ngay** sau khi nộp — đọc kỹ rồi mới đóng.
- [ ] **Ngủ đủ** đêm trước; ăn nhẹ; **ôn nhanh** trước giờ: **cram sheet 60 fact** + **bảng số §6** + **15 bẫy**.
- [ ] Nhắc lại chiến lược: **90 giây/câu**, **đánh dấu câu khó**, **đọc câu hỏi trước**, **default theo version mới nhất**, **không đổi đáp án tuỳ tiện**.

## 📎 Tài nguyên tuần này

> 📂 **Đã crawl sẵn tài liệu vào** [`resources/`](resources/INDEX.md) — đọc offline được.

- **Confluent Certification (chính thức):** [confluent.io/certification](https://www.confluent.io/certification/) — mô tả CCDAK, "90 minute proctored exams", dạng câu, FAQ (Honorlock, retake 7 ngày, hiệu lực 2 năm, đổi lịch 5 ngày). Trang chi tiết `/certification/developer/` hiện trả **404** → dùng trang tổng + portal đăng ký [training.confluent.io](https://training.confluent.io/) (catalog view 108).
- **Apache Kafka Upgrade notes (4.0 → 4.3):** [kafka.apache.org/43/getting-started/upgrade](https://kafka.apache.org/43/getting-started/upgrade) — bảng default đổi (`linger.ms`, `num.recovery.threads.per.data.dir`, `message.timestamp.after.max.ms`), API/tool bị gỡ, KIP-848/932/1071/966.
- **Bộ đề practice (chọn ≥ 3 bộ KHÁC NHAU, canh giờ 90'):** Confluent sample questions (trong prep guide), **Udemy — Stephane Maarek "CCDAK Practice Exams"**, **Whizlabs CCDAK**, free sample trên GitHub/blog cộng đồng — xem cách chấm theo domain trong [resources/mock-exam-and-prep-guide.md](resources/mock-exam-and-prep-guide.md).
- **Sách:** *Kafka: The Definitive Guide* 2nd ed. — đọc lại chương theo domain yếu, map chương → tuần ở [resources/kafka-definitive-guide-chapter-map.md](resources/kafka-definitive-guide-chapter-map.md).
- **Khoá học ôn nhanh:** Confluent Developer free courses (Kafka 101, Schema Registry 101, Kafka Connect 101, Kafka Streams 101) — xem lại phần "Hands-on" của module yếu; Stephane Maarek *Apache Kafka Series* (Beginners → Streams → Connect → Schema Registry).
- **Ôn tổng:** cram sheet 60 fact ở trên + **bảng số [§6](../../CCDAK-STUDY-PLAN.md#6-những-con-số-phải-thuộc-lòng)** + **bảng phản xạ [§7](../../CCDAK-STUDY-PLAN.md#7-bảng-phản-xạ-keyword--đáp-án)** của Kế hoạch tổng.
- **Sổ câu sai:** file phân tích 6 mục trong `CCDAK/questions/` (workflow giống SAA-C03).

## ✅ Checklist hoàn thành Tuần 10

- [ ] Hoàn thành **≥ 3 bộ practice CCDAK KHÁC NHAU**, mỗi bài canh giờ 90', cách nhau ≥ 1 ngày
- [ ] Đạt **≥ 80% ổn định** trên ≥ 3 bộ (không bài nào < 70%; nếu có → đã lùi lịch 1 tuần)
- [ ] Làm **mock cross-domain 30 câu** của repo trong 45' và chấm theo 6 domain ([answers.md](answers.md))
- [ ] **Review 100% câu sai** + viết file phân tích 6 mục trong `CCDAK/questions/`
- [ ] Đọc trôi chảy **bảng số §6** + **bảng phản xạ §7**; tự viết lại **cram sheet 1 trang** và đối chiếu 60 fact
- [ ] Hoàn thành **Capstone "Order Pipeline" 7 bước** với đủ ✅ Kiểm chứng + 🧹 Dọn dẹp toàn bộ
- [ ] Hoàn tất **Checklist ngày thi** (Honorlock system check, Chrome, ID, phòng, ngủ đủ)
- [ ] Vượt **Cổng tự kiểm tra** — trả lời được **CÂU CUỐI: đủ CẢ 4 tiêu chí sẵn sàng** → đặt lịch thi 🎓
