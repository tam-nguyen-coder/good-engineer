# Confluent Certification — Chính sách thi & chuẩn bị phòng thi (CCAAK)

> **Nguồn (official):** https://www.confluent.io/certification/ (mục policies · proctoring) · https://training.confluent.io/ · hỗ trợ Honorlock: https://honorlock.com/support/
> **Tuần:** 8 — Tuần chốt · **Loại:** Confluent Official + tổng hợp
> ⚠️ **Phần "Nội dung (trích từ tài liệu gốc)" ở cuối file là crawl từ trang certification của Confluent.** Phần **"✅ Checklist phòng thi"** và phần **"🚨 Sự cố hay gặp"** là **tổng hợp của người viết** từ yêu cầu Honorlock nêu trên trang đó — **không phải trích nguyên văn**, và tốc độ mạng gợi ý là con số kinh nghiệm chứ không phải yêu cầu chính thức. Đối chiếu lại khi đặt lịch, vì nhà cung cấp proctor và lệ phí có thể đổi.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- **Hiệu lực 2 năm.** Đặt nhắc tái chứng nhận ngay khi đậu, đừng đợi email.
- **Retake: chờ đủ 7 ngày.** Trượt lần một là mất trọn một tuần → giữ ngưỡng cá nhân **≥80%** trên **≥3 bộ mock khác nhau** trước khi mua bài thi.
- **Đổi/huỷ lịch miễn phí nếu thao tác trước 5 ngày trở lên**; trong vòng 5 ngày thì lệ phí **không hoàn**. Con số 5 ngày này chính là thứ khiến **van an toàn "<70% → lùi lịch 1 tuần"** khả thi: quyết định lùi phải ra **sớm hơn 5 ngày** so với giờ thi.
- **Kết quả pass/fail hiện ngay trên màn hình** khi nộp bài — không có bảng điểm theo domain, nên mọi phân tích vùng yếu phải làm **trước** ngày thi bằng bảng chấm theo 7 domain của repo.
- **Proctor Honorlock** chạy trong **Google Chrome** qua extension; bắt buộc **System Check trước ngày thi**.
- **Giấy tờ tuỳ thân do chính phủ cấp**, còn hạn, **tên khớp** tài khoản `training.confluent.io`. Sai tên là bị từ chối vào phòng thi.
- **Cấm tuyệt đối:** tài liệu tham khảo, điện thoại di động, người khác trong phòng. Với CCAAK điều này đau hơn CCDAK: **không được mở bảng số §6** — đó là lý do phải thuộc, không phải tra.
- Proctor thường yêu cầu **quay camera 360°** quanh phòng trước khi bắt đầu.
- **Thi bằng tiếng Anh.** Cần hỗ trợ đặc biệt thì liên hệ bộ phận certification của Confluent **trước nhiều tuần**, không phải sát ngày.

## ✅ Checklist phòng thi (tổng hợp — làm theo thứ tự)

**Trước 1 tuần**

- [ ] Đăng nhập `training.confluent.io`, kiểm tra **tên hiển thị khớp giấy tờ tuỳ thân** (họ/tên, thứ tự, dấu).
- [ ] Đặt lịch — **chỉ khi đã đủ 4 điều kiện** ở [Cổng cuối Tuần 8](../README.md#-cổng-tự-kiểm-tra--cổng-cuối--điều-kiện-đăng-ký-thi).
- [ ] Kiểm tra giấy tờ tuỳ thân **còn hạn** vào đúng ngày thi.
- [ ] Chọn khung giờ **tỉnh táo nhất trong ngày** — 90 phút chẩn đoán liên tục mệt hơn thi lý thuyết.

**Trước 1 ngày**

- [ ] Cài **Honorlock Chrome Extension**, chạy **System Check** đầy đủ (webcam, micro, chia sẻ màn hình).
- [ ] Cập nhật Chrome; **tắt mọi extension khác** (chặn quảng cáo, VPN, quản lý mật khẩu) — đây là nguyên nhân hỏng System Check phổ biến nhất.
- [ ] Mạng ổn định, tắt VPN công ty. *(Kinh nghiệm: ≥1 Mbps xuống / ≥2,5 Mbps lên là đủ; con số này là tổng hợp, không phải yêu cầu chính thức.)*
- [ ] **Không dùng máy công ty bị chặn cài extension** hoặc bị MDM khoá chia sẻ màn hình.
- [ ] Dọn bàn trống hoàn toàn; phòng riêng, khoá cửa, báo người nhà.
- [ ] Sạc đầy + cắm điện; tắt thông báo hệ điều hành, Slack, mail, lịch.
- [ ] **`docker compose down -v`** toàn bộ lab (capstone Tuần 8) — máy nhẹ thì webcam và chia sẻ màn hình mới mượt.

**Ngày thi**

- [ ] Ăn nhẹ, vào phòng sớm **15 phút**.
- [ ] Chỉ đọc **cram sheet 60 fact** và **15 bẫy** trong [README Tuần 8](../README.md) — không học kiến thức mới.
- [ ] Nhắc lại nhịp **90 giây/câu**; câu quá 2 phút → đánh dấu, đoán, đi tiếp. Không bỏ trống câu nào.
- [ ] Nhắc lại hai phản xạ CCAAK: **ưu tiên hành động rẻ và đảo ngược được**; **phương án nhắc ZooKeeper/znode/`--zookeeper` gần như chắc chắn sai**.
- [ ] Với câu hỏi "default": trả lời theo **Kafka 4.3** trừ khi đề nêu version.

## 🚨 Sự cố hay gặp trong phòng thi (tổng hợp)

| Sự cố | Phòng ngừa |
|---|---|
| System Check pass hôm trước nhưng fail lúc thi | Chạy lại System Check **sáng ngày thi**, sau khi khởi động lại máy |
| Extension VPN/ad-block làm treo Honorlock | Tắt hết từ hôm trước; dùng **profile Chrome sạch** riêng cho bài thi |
| Tên trên ID không khớp tài khoản | Sửa tên tài khoản **trước ≥1 tuần** (đổi tên có thể cần hỗ trợ) |
| Ai đó bước vào phòng giữa giờ | Khoá cửa + dán giấy; proctor có thể **huỷ bài** khi thấy người thứ hai |
| Mất mạng giữa bài | Chuẩn bị sẵn **hotspot điện thoại** (điện thoại phải ngoài tầm tay khi thi — chỉ dùng nếu proctor cho phép) |
| Máy nóng, quạt kêu, tab đóng đột ngột | Đóng Docker/IDE; chạy máy cắm điện, không chạy pin |

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Certification Validity

*"The Certification expires after two years."* Re-certification is required every two years.

### Retake Policy

*"Candidates must wait 7 days before purchasing and taking another exam."*

### Results

*"After completing your exam, you will receive results immediately on the testing screen."*

### Proctoring

Exams are proctored remotely by **Honorlock**. Candidates need a **webcam**, a **microphone**, the **Google Chrome** browser with the Honorlock extension, a **government-issued ID** for identity verification, and a strong internet connection meeting the stated requirements. A **System Check** must be completed before the exam is launched. The use of reference materials and mobile phones is prohibited.

### Cancellation and Rescheduling

*"Candidates may reschedule or cancel an appointment five (5) or more calendar days prior"* free of charge. Within 5 days of the exam, fees are **nonrefundable**.

### After Passing

Candidates receive a **digital badge** by email and are authorized to use the certification **title and logo** on professional materials.

### Registration

Exams are purchased and scheduled at **[training.confluent.io](https://training.confluent.io/)**.

---

> 📌 **Chưa xác nhận được từ nguồn chính thức:** **số câu 60**, **lệ phí 150 USD** và **ngưỡng đậu** đều **không** xuất hiện trên trang certification (trang chỉ nêu 90 phút, các dạng câu và các chính sách trên). Ba con số này đến từ tổng hợp bên thứ ba — **kiểm tra lại giá và số câu trên trang đăng ký trước khi thanh toán**. Xem [`../../VALIDATION.md`](../../VALIDATION.md) mục *"Chỗ cần đối chiếu lại trước ngày thi"*.
