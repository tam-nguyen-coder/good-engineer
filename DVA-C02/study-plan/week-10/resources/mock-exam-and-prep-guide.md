# Hướng dẫn Mock Exam & Sẵn sàng thi (DVA-C02)

> **Loại:** Tài liệu tự soạn (KHÔNG crawl) · **Tuần:** 10 — Kỳ thi & Mock (tuần chốt)
> Mục đích: gom quy tắc dùng mock, tiêu chí sẵn sàng đăng ký thi và checklist ngày thi vào một chỗ để duyệt nhanh trước khi đặt lịch.
> ⚠️ Các nhà cung cấp bên dưới là gợi ý phổ biến trong cộng đồng luyện thi AWS — **không phải endorsement chính thức của AWS**. Tự kiểm tra URL/tính cập nhật trước khi mua.

---

## 1. 📦 Nhà cung cấp practice exam uy tín cho DVA-C02

> KHÔNG dùng link lậu / bộ đề "brain dump" (vi phạm chính sách AWS, có thể bị huỷ chứng chỉ). Chỉ mua từ nguồn hợp pháp.

| Nhà cung cấp | Mô tả ngắn | Ghi chú |
|---|---|---|
| **AWS Official Practice Question Set / Official Practice Exam** (trên **AWS Skill Builder**) | Bộ câu hỏi & bài thi thử **chính thức của AWS**, sát định dạng và độ khó thật nhất; là "bước 4 – đo mức sẵn sàng" trong lộ trình ôn của AWS. | Ưu tiên số 1 để đối chiếu độ khó thật. Truy cập qua tài khoản AWS Skill Builder. |
| **Tutorials Dojo (Jon Bonso)** — DVA-C02 Practice Exams | Bộ mock nổi tiếng, giải thích (explanation) rất chi tiết cho từng đáp án đúng/sai, có chế độ **timed** (canh giờ) và **review**. | Rất tốt để luyện review câu sai vì phần giải thích dày. |
| **Stephane Maarek** — DVA-C02 Practice Tests | Bộ practice test đi kèm/độc lập với khoá học của Stephane; câu hỏi bám domain, giải thích gọn, sát style thi. | Thường bán trên nền tảng khoá học; hợp để lấy bộ đề "khác góc nhìn" với Tutorials Dojo. |

**Nguyên tắc chọn bộ đề:** dùng **≥ 3 bộ KHÁC NHAU** (khác tác giả) để tránh học vẹt theo văn phong 1 người. Ưu tiên có: (a) chế độ canh giờ, (b) chấm theo domain, (c) giải thích từng đáp án.

> Không chắc URL chính xác? → tra thẳng trong AWS Skill Builder (cho bộ AWS official) hoặc trang chính thức của từng nhà cung cấp; **đừng dùng URL bịa**.

---

## 2. ⏱️ Quy tắc dùng mock (bắt buộc)

1. **≥ 3 bộ mock KHÁC NHAU** — mỗi bộ là một full-length **65 câu**.
2. **Canh giờ nghiêm ngặt 130 phút** cho mỗi bài, không dừng, không tra tài liệu — mô phỏng đúng phòng thi (~2 phút/câu).
3. **Mỗi mock cách nhau ≥ 1 ngày** — ngày xen giữa dành để cày vùng yếu + review.
4. **Review 100% câu sai** (và cả câu *đúng nhưng đoán may*): xác định lý do sai (thiếu kiến thức / đọc sót qualifier / dính bẫy / quản lý giờ).
5. Với câu đáng nhớ → **viết file phân tích 6 mục** trong `questions/DVA-C02/` (giống workflow SAA-C03).
6. **Ghi lại % tổng + % theo từng domain** mỗi mock để lộ ra domain điểm thấp nhất → ưu tiên cày.
7. Ôn lại câu sai theo **spaced repetition 1 / 3 / 7 ngày**.

---

## 3. ✅ Tiêu chí SẴN SÀNG đăng ký thi — chỉ đặt lịch khi ĐỦ CẢ 4

| # | Tiêu chí |
|---|---|
| 1 | **≥ 3 full mock KHÁC NHAU đạt ≥ 85% ổn định** (không phải may mắn 1 lần) |
| 2 | Đã **review hết 100% câu sai** và hiểu vì sao sai |
| 3 | Đọc **trôi chảy** toàn bộ **bảng số §6** và **bảng phản xạ §7** (không cần tra cứu) |
| 4 | Hoàn thành **toàn bộ hands-on nhóm Serverless & CI/CD** |

**Bối cảnh mốc điểm:** điểm đậu chính thức là **720/1000 (~72%)**. Bar cá nhân **≥ 85%** tạo biên an toàn ~13% để hấp thụ độ khó dao động + áp lực phòng thi.

> 🚨 **VAN AN TOÀN:** Bất kỳ full mock nào **< 75%** → **lùi lịch thi 1 tuần**, tập trung 100% vào vùng yếu (domain điểm thấp nhất) rồi mới mock lại. Không "gồng" đặt lịch khi chưa đủ tiêu chí.

---

## 4. 🧪 Checklist NGÀY THI

**Nếu thi ONLINE PROCTORED:**
- [ ] **Chạy System Test** của Pearson VUE trước (webcam, micro, tốc độ mạng, trình duyệt) — làm sớm, không để sát giờ.
- [ ] **Dọn phòng riêng:** bàn trống hoàn toàn, không giấy tờ/sách/thiết bị điện tử lạ, đủ sáng, **một mình trong phòng**, cửa đóng.
- [ ] Chuẩn bị **quét phòng (room scan)** qua webcam theo yêu cầu giám thị.
- [ ] Nhớ quy tắc: **không rời khỏi khung hình camera** suốt bài (kể cả đi vệ sinh) → đi vệ sinh trước khi bắt đầu.
- [ ] Sẵn sàng **giao tiếp với giám thị** (bắt buộc để hoàn tất phiên thi).

**Nếu thi tại TEST CENTER (Pearson VUE):**
- [ ] Biết trước **địa chỉ + giờ hẹn**, đến **sớm ~30 phút**.
- [ ] Không mang đồ cá nhân vào phòng thi (có tủ khoá).

**Chung cho mọi hình thức:**
- [ ] **Giấy tờ tuỳ thân hợp lệ**, tên **khớp chính xác** với đăng ký (kiểm tra yêu cầu ID cho online vs in-person — có thể cần 2 loại ID / hộ chiếu).
- [ ] Nếu đã xin **ESL +30** → xác nhận accommodation đã áp vào lịch thi.
- [ ] **Ngủ đủ** đêm trước; ăn nhẹ; **KHÔNG nhồi kiến thức mới** phút chót.
- [ ] **Ôn nhanh** trước giờ: **bảng số §6** + **bảng phản xạ §7** + **danh sách bẫy**.
- [ ] Nhắc lại chiến lược làm bài: **~2 phút/câu**, **flag câu khó + quay lại**, **đọc câu hỏi trước đáp án**, **không đổi đáp án tuỳ tiện**.

---

## 5. 🔗 Liên kết nhanh trong kho tài liệu này
- Số liệu & lộ trình kỳ thi chính thức → [`dva-c02-official-cert-page.md`](dva-c02-official-cert-page.md)
- Domain + trọng số + phạm vi dịch vụ → [`dva-c02-exam-guide.md`](dva-c02-exam-guide.md)
- Chính sách đặt lịch / reschedule / online proctored / accommodation → [`aws-certification-exam-policies.md`](aws-certification-exam-policies.md)
- Bảng số §6 & bảng phản xạ §7 → [Kế hoạch tổng](../../../DVA-C02-STUDY-PLAN.md)
