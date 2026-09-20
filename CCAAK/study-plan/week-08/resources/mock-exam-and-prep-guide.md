# Hướng dẫn chạy mock & theo dõi điểm — CCAAK

> **Nguồn:** **tổng hợp** của người viết từ cấu trúc bộ tài liệu này và kinh nghiệm luyện thi — **KHÔNG crawl từ tài liệu chính thức**. Mọi thông số kỳ thi (90 phút, dạng câu, retake, đổi lịch) lấy từ [`ccaak-official-exam-page.md`](ccaak-official-exam-page.md); tỉ trọng 7 domain lấy từ [`../../VALIDATION.md`](../../VALIDATION.md).
> **Tuần:** 8 — Tuần chốt · **Loại:** Tổng hợp (không crawl)
> Về [file học Tuần 8](../README.md) · [Kế hoạch tổng](../../../CCAAK-STUDY-PLAN.md)

## 🎯 Điểm thi quan trọng (tóm tắt)

- Tuần 8 không học thêm kiến thức, mà **chuyển từ "biết" sang "phản xạ dưới áp lực 90 giây/câu"**.
- Điều kiện đặt lịch: **≥3 bộ mock KHÁC NHAU đạt ≥80%**, ổn định chứ không phải may mắn một lần.
- **Van an toàn:** một bài full mock **<70%** → **lùi lịch thi 1 tuần**. Quyết định lùi phải ra **sớm hơn 5 ngày** so với giờ thi thì mới đổi lịch miễn phí.
- Câu **đúng nhờ đoán may** tính như câu sai. Không giải thích được vì sao ba phương án kia sai thì chưa nắm.
- **Riêng CCAAK:** đề hỏi *hành động của người vận hành*. Vì vậy sau mỗi bài mock, ngoài "đúng/sai" còn phải trả lời được: *câu này hỏi trục nào (durability / availability / throughput / chi phí)* và *hành động rẻ hơn mà mình đã bỏ qua là gì*.

## Nguồn đề luyện tập

| Nguồn | Số câu | Ghi chú |
|---|---|---|
| **Bộ đề trong repo này** (`week-01` → `week-08`) | ~26–30 câu/tuần | Bám sát nội dung từng tuần; `week-08/questions.md` là **mock cross-domain 30 câu** đúng tỉ trọng 7 domain |
| **3 bộ mock full-length của repo** ([`mock-01`](../../../mock-exams/mock-01/questions.md) · [`mock-02`](../../../mock-exams/mock-02/questions.md) · [`mock-03`](../../../mock-exams/mock-03/questions.md)) | 60 câu × 3 | Đúng format thi thật: 60 câu / 90 phút / 7 domain. Đây là ba bài chính để đạt tiêu chí "≥3 bộ ≥80%" |
| **Confluent sample questions** (trên trang certification) | ít | Miễn phí — **nguồn duy nhất phản ánh đúng văn phong đề thật**, kể cả dạng `matching` và `list order` |
| **Confluent exam guide** (link trên trang certification) | 0 | Không phải đề, nhưng là danh sách chủ đề chính thức — dùng để soát xem còn domain nào chưa chạm |
| **Khoá/đề bên thứ ba** (Udemy, Whizlabs, repo GitHub) | tuỳ | ⚠️ **Nguy hiểm với CCAAK** — xem cảnh báo dưới |

> 🔴 **Cảnh báo lớn nhất của CCAAK.** Hai kho câu hỏi CCAAK lớn nhất trên GitHub có tỉ lệ nhắc **ZooKeeper : KRaft = 118 : 3**, và **ZooKeeper thường là đáp án được đánh dấu ĐÚNG**, không phải phương án nhiễu (ví dụ: *"broker nào thành controller mới?"* → đáp án ghi là *"broker đầu tiên tạo lại được ephemeral node trên ZooKeeper"*). Với Kafka 4.x điều đó **sai hoàn toàn**. Gặp mâu thuẫn thì tin [`../../VALIDATION.md`](../../VALIDATION.md) và docs chính thức, **không tin đáp án của bộ đề**. Chi tiết đo đạc: [`../../../mock-exams/SOURCES-AND-VALIDATION.md`](../../../mock-exams/SOURCES-AND-VALIDATION.md).

> 🔄 **Mẹo nhận diện tài liệu cũ trong 5 giây:** nếu tài liệu chia CCAAK thành **4 domain** (Fundamentals 15% · Managing/Configuring/Optimizing 30% · Security 15% · Designing/Troubleshooting/Integrating 40%) thì nó thuộc **thế hệ trước**. Syllabus hiện hành có **7 domain**.

## Quy trình chạy một bài full mock (5 bước)

1. **Chuẩn bị như thi thật:** 60 câu, hẹn giờ **90 phút**, không tra tài liệu, không tạm dừng, điện thoại để phòng khác. Không mở bảng số §6 — nếu phải mở thì bài đó **không tính**.
2. **Giữ nhịp 90 giây/câu.** Quá 2 phút → đánh dấu, đoán một phương án, đi tiếp. Không bỏ trống câu nào.
3. **Chấm điểm và tách theo 7 domain** ngay sau khi nộp (bảng dưới). Điểm tổng che giấu vùng yếu; % theo domain thì không.
4. **Review 100% câu sai trong cùng ngày**, mỗi câu đáng nhớ viết một file phân tích trong [`CCAAK/questions/`](../../../questions/README.md) theo **6 mục + 3 mục bổ sung** (*Trục đánh đổi*, *Hành động rẻ hơn đã bị bỏ qua*, *Lý do mình sai*).
5. **Nghỉ ít nhất 1 ngày giữa hai bài full mock.** Ngày xen giữa dành cho vùng yếu và cho capstone — não cần thời gian hợp nhất, và mock liên tiếp chỉ đo được trí nhớ ngắn hạn.

## Bảng theo dõi 3–4 lần mock theo 7 domain

Điền sau mỗi bài. Domain nào **đỏ hai lần liên tiếp** thì quay lại học tuần tương ứng, **không mock tiếp**.

| Domain | Tỉ trọng | ~Câu/60 | Tuần tương ứng | Mock #1 | #2 | #3 | #4 | Ngưỡng |
|---|---|---|---|---|---|---|---|---|
| Cluster Configuration | 22% | 13 | Tuần 2–3 | | | | | ≥ 80% |
| Fundamentals | 15% | 9 | Tuần 1 | | | | | ≥ 80% |
| Security | 15% | 9 | Tuần 5 | | | | | ≥ 78% |
| Troubleshooting | 15% | 9 | Tuần 7 | | | | | ≥ 78% |
| Deployment Architecture | 12% | 7 | Tuần 4 | | | | | ≥ 75% |
| Kafka Connect | 12% | 7 | Tuần 6 | | | | | ≥ 75% |
| Observability | 10% | 6 | Tuần 7 | | | | | ≥ 75% |
| **Tổng** | 101%* | 60 | — | | | | | **≥ 80%** |

\* Tổng 101% do Confluent làm tròn từng domain — không phải lỗi chép.

| | Mock #1 | #2 | #3 | #4 |
|---|---|---|---|---|
| Ngày làm | | | | |
| Nguồn đề | | | | |
| Thời gian dùng / 90 phút | | | | |
| Số câu đánh dấu chưa chắc | | | | |
| Số câu **đúng nhờ đoán** | | | | |
| Số câu dạng matching / list order | | | | |

## Phân loại lý do sai (5 nhóm — CCAAK thêm 1 nhóm so với CCDAK)

Ghi nhãn cho **từng** câu sai. Tỉ lệ giữa các nhóm quyết định bạn nên sửa **cách học** hay sửa **cách làm bài**.

| Nhãn | Ý nghĩa | Cách sửa |
|---|---|---|
| **Thiếu kiến thức** | Không biết config/metric/cơ chế đó | Đọc lại Buổi A của tuần tương ứng và **làm lại lab** — với CCAAK, lab vá lỗ hổng nhanh hơn đọc |
| **Đọc sót qualifier** | Bỏ qua *without data loss*, *with minimal downtime*, *fewest changes*, *survive the loss of one rack*, *without restarting brokers* | Gạch chân qualifier **trước** khi đọc phương án |
| **Quá tay** | Chọn phương án đúng kỹ thuật nhưng **đắt / một chiều / không đảo ngược được** (tăng partition, bật `unclean.leader.election.enable`, hạ `min.insync.replicas`, restart cả cluster) | Trước khi chọn, hỏi: *"có hành động nào rẻ hơn và đảo ngược được không?"* |
| **🔴 Bẫy version** | Chọn phương án thuộc thế giới ZooKeeper (`--zookeeper`, znode, `zookeeper.connect`, `AclAuthorizer`, MirrorMaker 1) hoặc giá trị mặc định cũ | Đọc lại [`kafka-4x-operational-changes.md`](kafka-4x-operational-changes.md) + bảng "mặc định đã đổi" ở `VALIDATION.md` |
| **Hết giờ** | Biết làm nhưng không kịp | Luyện nhịp 90 giây; đánh dấu và bỏ qua dứt khoát hơn |

> 📌 Cách đọc kết quả phân loại:
> - **"Thiếu kiến thức" chiếm quá nửa** → vấn đề là **nội dung**: quay lại tuần yếu nhất, làm lại lab, chưa mock tiếp.
> - **"Đọc sót qualifier" + "Hết giờ" chiếm quá nửa** → vấn đề là **kỹ thuật làm bài**: mock thêm hiệu quả hơn học thêm.
> - **"Quá tay" chiếm quá nửa** → vấn đề là **tư duy vận hành**: đọc lại bảng phản xạ §7 và cột *Hành động đầu tiên*; mọi hành động ở cột đó đều là hành động rẻ nhất có thể.
> - **Còn bất kỳ câu nào nhãn "bẫy version"** → đọc lại toàn bộ file thay đổi 4.x trước khi thi. Nhóm này **phải về 0**, vì nó là nhóm dễ diệt nhất.

## Lịch 7 ngày cuối (gợi ý — khớp bảng lịch trong README Tuần 8)

| Ngày | Việc chính |
|---|---|
| 1 | **Full mock #2** (60 câu / 90 phút) → review 100% câu sai + viết file phân tích |
| 2 | Cày domain thấp điểm nhất + đọc lại **bảng số §6** + **Capstone bước 1–3** |
| 3 | **Full mock #3** → review 100% câu sai |
| 4 | **Capstone bước 4–7** (3 bài phá còn lại + diễn tập DR) + đọc **bảng phản xạ §7** |
| 5 | **Full mock #4 nếu chưa đủ 3 bài ≥80%**; đủ rồi thì rà hands-on còn thiếu + tự viết lại cram sheet từ trí nhớ |
| 6 | Cram: 60 fact + playbook tổng hợp + 15 bẫy; **chạy Honorlock System Check**; chuẩn bị giấy tờ và phòng |
| 7 | Nghỉ nhẹ, đọc lướt cram sheet + 15 bẫy; `docker compose down -v` mọi thứ; **không học kiến thức mới**; ngủ đủ |
