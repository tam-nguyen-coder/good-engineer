# Confluent Certification — Trang chính thức, phần CCAAK

> **Nguồn (official):** https://www.confluent.io/certification/ · đăng ký tại https://training.confluent.io/
> **Tuần:** 8 — Tuần chốt · **Loại:** Confluent Official
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch ngày 2026-09-20, có thể rút gọn nhẹ) — **luôn đối chiếu link gốc trước khi đặt lịch thi**, vì lệ phí và nhà cung cấp proctor có thể đổi.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- **CCAAK dành cho "professionals who manage and maintain Kafka cluster environments"** — người vận hành, không phải người viết ứng dụng. Đây là lý do mọi câu hỏi đều hỏi *hành động của admin*, không hỏi định nghĩa.
- **Năng lực được xác nhận:** *"configure, deploy, monitor, and support Apache Kafka® clusters — ensuring reliable performance and operational excellence."* Bốn động từ này ánh xạ gần như 1-1 với 7 domain: configure → CFG 22%, deploy → ARCH 12%, monitor → OBS 10%, support → TROUBLE 15%.
- **Thời lượng 90 phút.** Trang chính thức **không** in số câu; con số **60 câu** đến từ syllabus bên thứ ba (xem [`../../VALIDATION.md`](../../VALIDATION.md)). Với 60 câu thì nhịp là **90 giây/câu**.
- **Dạng câu (nguyên văn trang chính thức):** `multiple-choice`, `matching`, `list order`. Practice test bên thứ ba gần như chỉ có multiple-choice → **hai dạng còn lại phải tự luyện**: vẽ lại thứ tự rolling upgrade, thứ tự chẩn đoán URP, các bước reassignment, ghép metric ↔ ngưỡng.
- **Kết quả hiện ngay trên màn hình** sau khi nộp: *"After completing your exam, you will receive results immediately on the testing screen."* Không có điểm số theo domain, chỉ **pass/fail** → đó là lý do đặt ngưỡng cá nhân **≥80%** trên mock.
- **Hiệu lực 2 năm** — *"The Certification expires after two years."*
- **Retake: chờ 7 ngày** — *"Candidates must wait 7 days before purchasing and taking another exam."* Trượt là mất trọn một tuần, thêm một lý do nữa để không "thử vận may".
- **Proctor Honorlock**, thi từ xa: cần **webcam**, **micro**, **Google Chrome + Honorlock extension**, **giấy tờ tuỳ thân do chính phủ cấp**, và đường truyền đủ mạnh. Phải chạy **System Check** trước.
- **Đổi/huỷ lịch miễn phí** nếu thao tác **trước 5 ngày trở lên**; trong vòng 5 ngày thì lệ phí **không hoàn**.
- **Sau khi đậu:** nhận **digital badge** qua email + quyền dùng danh hiệu và logo chứng chỉ trên tài liệu nghề nghiệp.

> 💡 **Việc phải làm ít nhất 1 ngày trước thi:** cài Honorlock Chrome Extension và chạy System Check. Đây là nguyên nhân hoãn thi phổ biến nhất và hoàn toàn tránh được.

> 🔎 **Điều trang chính thức KHÔNG nói:** số câu, lệ phí, ngưỡng đậu, và tỉ trọng 7 domain. Tỉ trọng dùng trong bộ tài liệu này (CFG 22 · FUND 15 · SEC 15 · TROUBLE 15 · ARCH 12 · CONNECT 12 · OBS 10) đến từ **hai nguồn bên thứ ba độc lập khớp nhau** — chi tiết ở [`../../VALIDATION.md`](../../VALIDATION.md).

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Available Certifications

**Confluent Certified Administrator for Apache Kafka® (CCAAK)** — *"designed for professionals who manage and maintain Kafka cluster environments."* The certification validates competency to *"configure, deploy, monitor, and support Apache Kafka® clusters—ensuring reliable performance and operational excellence."*

The same page lists three sibling programs, useful for knowing which exam a third-party study guide was written for:

- **Confluent Certified Developer for Apache Kafka® (CCDAK)** — developers and solution architects building applications with the Kafka APIs.
- **Confluent Certified Cloud Operator (CCAC)** — Confluent Cloud, multi-cloud and global architectures using Cluster Linking, Stream Governance, connectors and stream processing.
- **Fundamentals Accreditation (free)** — an entry option that awards a digital badge; a stepping stone if you are not ready for a full certification.

### Exam Format & Duration

- Duration: **90 minutes**, proctored.
- Question types: *"multiple-choice, matching, list order"*.
- Delivery: remote proctored exams, available in most countries.

### Proctoring Requirements

Exams are proctored remotely by **Honorlock**. Candidates must have:

- a **webcam** and a **microphone**;
- the **Google Chrome** browser with the **Honorlock extension** installed;
- a **government-issued ID** for identity verification;
- a strong internet connection meeting the stated requirements.

A **System Check** must be completed before the exam is launched.

### Scoring & Results

*"After completing your exam, you will receive results immediately on the testing screen."*

The page does not publish a passing score; results are reported as pass/fail.

### Certification Validity

*"The Certification expires after two years."* Re-certification is required to keep the credential current.

### Retake Policy

*"Candidates must wait 7 days before purchasing and taking another exam."*

### Cancellation / Rescheduling

*"Candidates may reschedule or cancel an appointment five (5) or more calendar days prior"* without penalty. Within 5 days of the appointment, fees become **nonrefundable**.

### After Passing

Candidates receive a **digital badge** by email and are authorized to use the certification **title and logo** on professional materials.

### Registration & Study Resources

Exams are purchased and scheduled through **[training.confluent.io](https://training.confluent.io/)**. The certification page also links the official **exam guide** and instructor-led training courses on the Confluent training platform.
