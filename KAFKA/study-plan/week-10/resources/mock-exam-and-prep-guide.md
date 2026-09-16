# Hướng dẫn chạy mock & theo dõi điểm — CCDAK

> **Nguồn:** **tổng hợp** từ kinh nghiệm luyện thi và cấu trúc plan này — **không crawl từ tài liệu chính thức**. Thông số kỳ thi lấy từ [`ccdak-official-exam-page.md`](ccdak-official-exam-page.md).
> **Tuần:** 10 — Tuần chốt · **Loại:** Tổng hợp
> Về [file học Tuần 10](../README.md) · [Kế hoạch tổng](../../../KAFKA-STUDY-PLAN.md)

## 🎯 Điểm thi quan trọng (tóm tắt)

- Mục tiêu tuần 10 không phải học thêm, mà là **chuyển từ "biết" sang "phản xạ dưới áp lực 90 giây/câu"**.
- Điều kiện đặt lịch thi: **≥ 3 bộ practice KHÁC NHAU đạt ≥ 80%**, ổn định chứ không phải may mắn một lần.
- Van an toàn: một bài full mock **< 70%** → **lùi lịch thi 1 tuần**.
- Câu **đúng nhờ đoán may** tính như câu sai. Nếu không giải thích được vì sao ba phương án kia sai thì chưa nắm.

## Nguồn đề luyện tập

| Nguồn | Số câu | Ghi chú |
|---|---|---|
| **Bộ đề trong repo này** (`week-01` → `week-10`) | **291 câu** | Bám sát nội dung từng tuần; `week-10/questions.md` là mock cross-domain 30 câu theo đúng tỉ trọng đề |
| **Confluent sample questions** | ít | Miễn phí trên trang certification — **nguồn duy nhất phản ánh đúng văn phong đề thật**, kể cả dạng `matching` / `list order` |
| **Stephane Maarek — CCDAK Practice Exams** (Udemy) | 3 bộ | Phổ biến nhất; giải thích chi tiết; chú ý vài câu còn dùng số liệu **trước Kafka 3.0/4.0** |
| **Whizlabs / các bộ khác** | tuỳ | Chất lượng dao động — khi nghi ngờ, **đối chiếu docs** thay vì tin đáp án |

> ⚠️ Mọi bộ đề bên thứ ba đều có nguy cơ dùng mặc định cũ (`acks=1`, `linger.ms=0`, `session.timeout.ms=10000`, "ZooKeeper"). Gặp mâu thuẫn thì tin [`../../VALIDATION.md`](../../VALIDATION.md) và docs chính thức, không tin đáp án của bộ đề.

## Quy trình chạy một bài full mock

1. **Chuẩn bị như thi thật:** 60 câu, hẹn giờ **90 phút**, không tra tài liệu, không tạm dừng, điện thoại để phòng khác.
2. **Giữ nhịp 90 giây/câu.** Câu nào quá 2 phút → đánh dấu, đoán một phương án, đi tiếp. Không bỏ trống câu nào vì không bị trừ điểm khi sai.
3. **Chấm điểm và tách theo domain** ngay sau khi nộp, dùng bảng dưới.
4. **Review 100% câu sai** trong cùng ngày, mỗi câu đáng nhớ viết một file phân tích 6 mục trong [`KAFKA/questions/`](../../../questions/README.md).
5. **Nghỉ ít nhất 1 ngày** giữa hai bài full mock; ngày xen giữa dành cho vùng yếu.

## Bảng theo dõi 4 lần mock

Điền sau mỗi bài. Cột nào đỏ hai lần liên tiếp thì quay lại học tuần tương ứng, không mock tiếp.

| Domain | Tỉ trọng | Tuần tương ứng | Mock #1 | #2 | #3 | #4 | Ngưỡng |
|---|---|---|---|---|---|---|---|
| Application Development | 28% | 3, 4 | | | | | ≥ 80% |
| Fundamentals | 23% | 1, 2 | | | | | ≥ 78% |
| Kafka Connect | 15% | 5 | | | | | ≥ 75% |
| Observability | 13% | 8 | | | | | ≥ 75% |
| Kafka Streams | 12% | 6 | | | | | ≥ 75% |
| Testing | 8% | 7 | | | | | ≥ 70% |
| **Tổng** | 100% | — | | | | | **≥ 80%** |

| | Mock #1 | #2 | #3 | #4 |
|---|---|---|---|---|
| Ngày làm | | | | |
| Nguồn đề | | | | |
| Thời gian dùng / 90 phút | | | | |
| Số câu đánh dấu chưa chắc | | | | |
| Số câu **đúng nhờ đoán** | | | | |

## Phân loại lý do sai

Ghi nhãn cho từng câu sai. Tỉ lệ giữa bốn nhóm quyết định bạn nên sửa **cách học** hay sửa **cách làm bài**.

| Nhãn | Ý nghĩa | Cách sửa |
|---|---|---|
| **Thiếu kiến thức** | Không biết config/cơ chế đó | Đọc lại Buổi A của tuần tương ứng, làm lại lab |
| **Đọc sót qualifier** | Bỏ qua "guarantee", "without changing producer code", "minimize latency" | Luyện gạch chân qualifier **trước** khi đọc phương án |
| **Dính bẫy** | Chọn phương án đúng kỹ thuật nhưng sai yêu cầu, hoặc đặt config nhầm thành phần | Đọc lại mục "⚠️ Bẫy đề" của tuần đó |
| **Hết giờ** | Biết làm nhưng không kịp | Luyện nhịp 90 giây, đánh dấu và bỏ qua dứt khoát hơn |

> 📌 Nếu **"đọc sót qualifier" + "hết giờ" chiếm quá nửa** số câu sai, vấn đề của bạn là **kỹ thuật làm bài**, không phải kiến thức. Khi đó mock thêm sẽ hiệu quả hơn học thêm.

## Lịch 7 ngày cuối (gợi ý)

| Ngày | Việc chính |
|---|---|
| 1 | Full mock #2 (90 phút) → review 100% câu sai + viết file phân tích |
| 2 | Cày domain thấp điểm nhất + đọc lại bảng số §6 của kế hoạch tổng |
| 3 | Full mock #3 → review |
| 4 | Cày vùng yếu còn lại + đọc bảng phản xạ §7 và danh sách 15 bẫy |
| 5 | Full mock #4 **nếu chưa đủ 3 bài ≥ 80%**; đủ rồi thì rà hands-on còn thiếu |
| 6 | Cram: cram sheet 60 fact; **chạy Honorlock System Check**; chuẩn bị giấy tờ |
| 7 | Nghỉ nhẹ, đọc lướt cram sheet, ngủ đủ — **không học kiến thức mới** |
