# 🏁 Tuần 10 — Tuần chốt — Mock dồn + Review + Cram + Thi

> **Domain:** Tất cả (tổng ôn) · **Thời lượng:** ~11h+ (mock dồn + review + cram) · **Vị trí:** Tuần cuối — vùng đệm đảm bảo đậu
>
> **Điều hướng:** [⬅️ Tuần 9](../week-09/README.md) · [🏠 Kế hoạch tổng](../../DVA-C02-STUDY-PLAN.md) · 🎓 Đăng ký & thi

## 🎯 Mục tiêu tuần này

Tuần này **KHÔNG học kiến thức mới**. Toàn bộ trọng tâm là chuyển hoá: từ *"biết kiến thức"* sang *"phản xạ đúng dưới áp lực + đủ điều kiện đăng ký thi"*.

- **Hoàn tất ≥ 3 full mock KHÁC NHAU đạt ≥ 85% ổn định** (không phải may mắn 1 lần) — điều kiện cứng để đặt lịch thi.
- **Review 100% câu sai** của mọi mock và **viết file phân tích** trong `questions/DVA-C02/` theo đúng format 6 mục như SAA-C03.
- **Làm bài dưới áp lực đúng giờ:** tự canh **130 phút** nghiêm ngặt, giữ nhịp **~2 phút/câu**, biết flag + bỏ qua + quay lại.
- **Đọc trôi chảy** toàn bộ **bảng số [§6](../../DVA-C02-STUDY-PLAN.md#6-những-con-số-phải-thuộc-lòng)** và **bảng phản xạ [§7](../../DVA-C02-STUDY-PLAN.md#7-bảng-phản-xạ-keyword--dịch-vụ)** — không cần tra cứu.
- **Nhận diện qualifier trong 1 lần đọc** ("most cost-effective", "least operational overhead", "fully managed", "real-time", "ordered") và loại được bẫy "đúng kỹ thuật nhưng không đáp ứng yêu cầu".
- **Sẵn sàng phòng thi:** thiết bị/phòng đạt yêu cầu (nếu thi online proctored), giấy tờ, tâm lý, lịch thi đã đặt.

## 📚 Nội dung học chi tiết

Bốn "buổi" tuần này quy đổi thành **lịch mock dồn**. Nguyên tắc: **mỗi full mock cách nhau ≥ 1 ngày** (ngày xen giữa dành để cày vùng yếu + review), và **luôn canh giờ 130 phút nghiêm ngặt** như thi thật.

**Gợi ý lịch 7 ngày cuối:**

| Ngày | Việc chính |
|---|---|
| **Ngày 1** | 🎯 **FULL MOCK #2** (canh giờ 130') → **Review 100% câu sai** + viết file phân tích 6 mục |
| **Ngày 2** | Cày **vùng yếu** (domain điểm thấp nhất ở mock #2) + đọc lại **bảng số §6** |
| **Ngày 3** | 🎯 **FULL MOCK #3** (canh giờ 130') → Review 100% câu sai + viết file phân tích |
| **Ngày 4** | Cày vùng yếu còn lại + đọc lại **bảng phản xạ §7** + danh sách bẫy |
| **Ngày 5** | 🎯 **FULL MOCK #4** *(nếu chưa đủ 3 bài ≥85%)* → Review. Nếu đã đủ → flashcard nhẹ + rà hands-on còn thiếu |
| **Ngày 6** | **Cram:** cheat sheet + bảng số §6 + bảng phản xạ §7; chuẩn bị **giấy tờ + thiết bị/phòng** |
| **Ngày trước thi** | **Nghỉ nhẹ** — chỉ đọc lướt cheat sheet + danh sách bẫy; **ngủ đủ**; KHÔNG học kiến thức mới |

### 🅰️ Buổi A — FULL MOCK #2 + chiến lược làm bài (~2.5h)

**Quy trình chạy mock (giống thi thật):**
1. Chọn một bộ full-length **65 câu**, đặt đồng hồ **130 phút**, không dừng giữa chừng, không tra tài liệu.
2. Áp dụng **chiến lược làm bài** dưới đây trong suốt bài.
3. Chấm điểm, ghi lại **% tổng** và **% theo từng domain** để biết vùng yếu.

**Chiến lược làm bài (luyện đến mức tự động):**
- **Nhịp ~2 phút/câu.** ~65 câu / 130 phút → giữ đều nhịp. Một câu quá **2–3 phút** → **flag + bỏ qua**, quay lại cuối giờ (không có điểm trừ khi đoán).
- **Đọc CÂU HỎI trước, đáp án sau.** Xác định *đề đang hỏi gì* trước khi bị 4 lựa chọn dẫn dắt.
- **Gạch chân qualifier:** "most cost-effective", "least operational overhead", "fully managed", "real-time", "ordered", "highly available"… — qualifier quyết định đáp án đúng.
- **Loại trừ (elimination):** gạch 2 phương án sai rõ ràng trước, rồi so 2 phương án còn lại theo qualifier.
- **Bẫy "đúng kỹ thuật nhưng không đáp ứng yêu cầu":** một phương án chạy được về mặt kỹ thuật nhưng **không tối ưu theo tiêu chí đề** (vd đề đòi "fully managed" mà phương án là tự dựng trên EC2) → **loại**.
- **Multiple response:** đọc rõ "Choose **TWO/THREE**" → chọn **đúng số**, không thừa không thiếu.
- **Hạn chế đổi đáp án:** chỉ đổi khi phát hiện **đã đọc sót** một chi tiết rõ ràng — cảm giác mơ hồ thường khiến đổi từ đúng sang sai.

### 🅱️ Buổi B — Review 100% câu sai + viết file phân tích (~3h)

1. **Rà từng câu sai** (và cả câu *đúng nhưng đoán may*): xác định **lý do sai** — thiếu kiến thức / đọc sót qualifier / dính bẫy / quản lý giờ.
2. Với mỗi câu đáng nhớ, **viết một file phân tích** trong `questions/DVA-C02/` theo **format 6 mục như SAA-C03**:
   1. **CONTEXT & ĐỀ BÀI**
   2. **KEYWORDS QUAN TRỌNG** (bảng 2 cột)
   3. **YÊU CẦU CỦA ĐỀ**
   4. **ĐÁP ÁN ĐÚNG**
   5. **CÁC ĐÁP ÁN SAI**
   6. **MẸO GHI NHỚ (Memory Hook)** — mở đầu bằng `🧠`
3. **Ghi sổ câu sai** và ôn theo **spaced repetition 1 / 3 / 7 ngày**.
4. **Cày lại bảng số §6** cho các con số dính sai trong mock (vd giới hạn `Lambda`, TTL cache, v.v.).

### 🅲️ Buổi C — FULL MOCK #3 (và #4 nếu cần) + cày bảng phản xạ (~3h)

1. **≥ 1 ngày sau mock #2**, chạy **FULL MOCK #3** (bộ đề KHÁC), lặp lại đúng quy trình canh giờ + chiến lược.
2. Review 100% câu sai + viết file phân tích như Buổi B.
3. Nếu **chưa đủ 3 bài ≥ 85%** → xếp thêm **FULL MOCK #4** (cách ≥ 1 ngày).
4. **Xen kẽ cày lại bảng phản xạ §7** (keyword → dịch vụ) đến mức bật ngay không cần suy nghĩ.

### 🅳 Buổi D — Cram cuối + tổng duyệt (~2h)

- **Đọc lướt cheat sheet + bảng số §6 + bảng phản xạ §7 + danh sách bẫy** — chỉ ôn lại, không nhồi cái mới.
- **Rà hands-on còn thiếu:** đảm bảo đã hoàn tất **toàn bộ hands-on nhóm Serverless & CI/CD** (điều kiện đăng ký thi).
- **Spaced repetition** lần cuối cho các nhóm hay quên (STS API, `SQS` FIFO vs Standard, cache invalidation…).
- **Duyệt lại "Checklist ngày thi"** và **4 tiêu chí sẵn sàng** → chỉ khi ĐỦ CẢ mới đặt lịch thi.

## 🧠 PHẢI NHỚ tuần này

**Thông tin kỳ thi (bám đúng để phân bổ giờ):**

| Fact | Con số |
|---|---|
| Số câu | **~65 câu** |
| Thời gian | **130 phút** (~2 phút/câu) |
| Điểm đậu | **720 / 1000** (~**72%**) |
| **Bar cá nhân** | **≥ 85% ổn định** → biên an toàn ~13% so với ngưỡng đậu, đủ hấp thụ độ khó dao động + áp lực phòng thi |

**Tiêu chí SẴN SÀNG đăng ký thi — CHỈ đặt lịch khi ĐỦ CẢ 4** (nhắc lại từ *Cơ chế đảm bảo đậu*):

| # | Tiêu chí |
|---|---|
| 1 | ✅ **≥ 3 full mock KHÁC NHAU đạt ≥ 85%** (ổn định, không may mắn) |
| 2 | ✅ Đã **review hết 100% câu sai** và hiểu vì sao sai |
| 3 | ✅ Đọc **trôi chảy** toàn bộ **bảng số §6** và **bảng phản xạ §7** |
| 4 | ✅ Hoàn thành **toàn bộ hands-on nhóm Serverless & CI/CD** |

> 🚨 **VAN AN TOÀN:** Bất kỳ full mock nào **< 75%** → **lùi lịch thi 1 tuần**, tập trung 100% vào vùng yếu (domain điểm thấp nhất) rồi mới mock lại.

## ⚠️ Bẫy phòng thi hay gặp

- Thấy một câu khó → **sa đà** cố giải cho bằng được → **cháy giờ** cho các câu dễ phía sau. Đúng là: **flag + bỏ qua + quay lại cuối giờ**.
- Đọc **đáp án trước câu hỏi** → bị 4 lựa chọn dẫn dắt. Đúng là: đọc **câu hỏi + qualifier** trước.
- Bỏ qua qualifier "**MOST** cost-effective" / "**LEAST** operational overhead" → chọn phương án đúng kỹ thuật nhưng không tối ưu theo tiêu chí → **sai**. Đúng là: gạch chân qualifier, chọn theo nó.
- Multiple response chọn **thiếu hoặc thừa** đáp án → **sai** (không có điểm một phần). Đúng là: chọn **đúng số** đề yêu cầu.
- Gặp phương án **"đúng kỹ thuật nhưng không đáp ứng yêu cầu"** (vd đề đòi *fully managed* mà chọn tự dựng EC2) → dễ chọn nhầm → **loại**, bám sát yêu cầu chính.
- **Đổi đáp án phút chót vì "cảm giác"** → thường đổi từ đúng sang sai. Đúng là: chỉ đổi khi phát hiện **đọc sót** rõ ràng.
- Gặp **dịch vụ/feature lạ** → **panic**. Đúng là: dùng **loại trừ**, đoán có cơ sở, flag, đi tiếp — không có điểm trừ.
- Không canh giờ khi luyện → vào phòng thi mất kiểm soát nhịp. Đúng là: **mọi mock đều canh 130 phút** như thật.

## 🔁 Chiến lược đọc qualifier (keyword → phản xạ)

| Thấy qualifier / từ khoá | Bật ngay |
|---|---|
| "most cost-effective" | Phương án **rẻ nhất VẪN đáp ứng đủ yêu cầu** (không phải rẻ nhất tuyệt đối) |
| "least operational overhead" / "fully managed" / "serverless" | Ưu tiên **managed/serverless** (`Lambda`, `Fargate`, `DynamoDB`) hơn tự quản EC2 |
| "real-time" streaming / analytics | Nghĩ tới `Kinesis Data Streams` (không phải `SQS`) |
| "ordered" + "no duplicates" (exactly-once) | `SQS FIFO` |
| "decouple" / "buffer" / "smooth spikes" | `SQS` |
| "fan-out" / một message → nhiều consumer | `SNS` (+ `SQS`) |
| "microsecond" / cache trước `DynamoDB` | `DAX` |
| "minimize latency toàn cầu" / static content | `CloudFront` |
| "đúng kỹ thuật nhưng lệch yêu cầu chính của đề" | **Loại** — bám sát YÊU CẦU + qualifier |

## 🧪 Checklist ngày thi

- [ ] (Online proctored) **Kiểm tra thiết bị**: webcam, micro, đường truyền, chạy **system test** của nhà cung cấp trước.
- [ ] (Online proctored) **Dọn phòng**: bàn trống, không giấy tờ/thiết bị lạ, đủ sáng, một mình trong phòng.
- [ ] Chuẩn bị **giấy tờ tuỳ thân** hợp lệ (tên khớp với đăng ký).
- [ ] (Test center) Biết trước **địa điểm + thời gian**, đến sớm.
- [ ] **Ngủ đủ** đêm trước; ăn nhẹ, tránh nhồi kiến thức phút chót.
- [ ] **Ôn nhanh** trước giờ: **bảng số §6** + **bảng phản xạ §7** + **danh sách bẫy**.
- [ ] Nhắc lại chiến lược: **~2 phút/câu**, **flag câu khó**, **đọc câu hỏi trước**, **không đổi đáp án tuỳ tiện**.

## 🚪 Cổng tự kiểm tra (phải trả lời trôi chảy mới đặt lịch thi)

- **Nhịp thời gian bao nhiêu, làm gì khi gặp câu khó?**
  **Đáp án gọn:** ~**2 phút/câu** (~65 câu / 130 phút); câu khó quá 2–3 phút → **flag + bỏ qua + quay lại cuối giờ**, không sa đà.
- **Thấy "least operational overhead" thì phản xạ gì?**
  **Đáp án gọn:** ưu tiên **managed/serverless** (`Lambda`, `Fargate`, `DynamoDB`), tránh giải pháp tự quản.
- **Multiple response nên chọn thế nào?**
  **Đáp án gọn:** chọn **đúng số** đề yêu cầu ("Choose TWO/THREE") — không thừa, không thiếu (không có điểm một phần).
- **Có nên đổi đáp án ở phút chót không?**
  **Đáp án gọn:** **Hạn chế.** Chỉ đổi khi phát hiện đã **đọc sót** một chi tiết rõ ràng; đổi theo "cảm giác" thường sai.
- **🎯 (CÂU CUỐI CÙNG) Đã đủ CẢ 4 tiêu chí sẵn sàng chưa?**
  **Đáp án gọn:** (1) ≥3 mock khác nhau ≥85% ổn định; (2) review 100% câu sai; (3) đọc trôi chảy bảng số §6 + bảng phản xạ §7; (4) xong toàn bộ hands-on Serverless & CI/CD. **Chưa đủ CẢ 4 → CHƯA đặt lịch thi.** Có mock **<75% → lùi 1 tuần**, cày vùng yếu.

## 📎 Tài nguyên tuần này

> 📂 **Đã crawl sẵn tài liệu AWS vào** [`resources/`](resources/INDEX.md) — đọc offline được.

- **AWS Certification:** trang chi tiết kỳ thi **AWS Certified Developer – Associate (DVA-C02)** — exam guide, số câu, thời gian, điểm đậu.
- **Đăng ký & lịch thi:** AWS Certification account → Pearson VUE / PSI (chọn **online proctored** hoặc **test center**); đọc kỹ **hướng dẫn thiết bị/phòng** nếu thi online.
- **Bộ đề mock:** các nhà cung cấp practice exam uy tín (vd Tutorials Dojo / Stephane Maarek practice tests) — chọn **≥ 3 bộ KHÁC NHAU**, luôn **canh giờ 130'**.
- **Ôn tổng:** cheat sheet + **bảng số [§6](../../DVA-C02-STUDY-PLAN.md#6-những-con-số-phải-thuộc-lòng)** + **bảng phản xạ [§7](../../DVA-C02-STUDY-PLAN.md#7-bảng-phản-xạ-keyword--dịch-vụ)** của Kế hoạch tổng.
- **Sổ câu sai:** file phân tích 6 mục trong `questions/DVA-C02/` (workflow giống SAA-C03).

## ✅ Checklist hoàn thành Tuần 10

- [ ] Hoàn thành **≥ 3 full mock KHÁC NHAU**, mỗi bài canh giờ 130', cách nhau ≥ 1 ngày
- [ ] Đạt **≥ 85% ổn định** trên ≥ 3 bộ mock
- [ ] **Review 100% câu sai** + viết file phân tích 6 mục trong `questions/DVA-C02/`
- [ ] Đọc trôi chảy **bảng số §6** + **bảng phản xạ §7**
- [ ] Hoàn thành **toàn bộ hands-on nhóm Serverless & CI/CD**
- [ ] Hoàn tất **Checklist ngày thi** (thiết bị/phòng, giấy tờ, ngủ đủ)
- [ ] Vượt **Cổng tự kiểm tra** — trả lời được **CÂU CUỐI: đủ CẢ 4 tiêu chí sẵn sàng** → đặt lịch thi 🎓
