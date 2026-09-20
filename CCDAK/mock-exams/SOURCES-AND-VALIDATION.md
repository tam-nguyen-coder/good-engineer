# 🔍 Nguồn đã khảo sát & Kết quả validate — Mock CCDAK

> **Ngày khảo sát:** 2026-09-20 · **Phiên bản neo:** Apache Kafka **4.3.1**
> Tài liệu này trả lời hai câu hỏi: *(1) ngoài kia có gì*, và *(2) vì sao bộ mock trong thư mục này được viết mới thay vì chép lại*.
> Về [mục lục mock](README.md) · [Kế hoạch tổng](../CCDAK-STUDY-PLAN.md) · [Nhật ký validate chung](../study-plan/VALIDATION.md)

---

## 1. Thông số kỳ thi — ĐÃ XÁC MINH CHÉO

Trước khảo sát này, bốn con số dưới đây chỉ là "tổng hợp cộng đồng" và bị đánh dấu nghi vấn trong [`../study-plan/VALIDATION.md`](../study-plan/VALIDATION.md). Nay đã được **hai nguồn độc lập** xác nhận khớp nhau.

| Hạng mục | Giá trị | Xác nhận bởi |
|---|---|---|
| Số câu | **60** | Syllabus VMExam · README repo `danielsobrado` |
| Thời gian | **90 phút** | Trang Confluent chính thức · VMExam |
| Giá | **150 USD** | VMExam |
| Chấm điểm | **Pass/Fail**, Confluent **không công bố ngưỡng** | Trang Confluent chính thức |
| Hiệu lực | **2 năm** | Trang Confluent chính thức |
| Retake | chờ **7 ngày** | Trang Confluent chính thức |
| Dạng câu | **multiple-choice · multiple-select · matching · list order** | Trang Confluent chính thức |
| Proctor | **Honorlock** (Chrome, webcam, micro, government ID) | Trang Confluent chính thức |

### Tỉ trọng 6 domain — ĐÃ XÁC NHẬN

| Domain | Tỉ trọng | Số câu trong mock 60 |
|---|---|---|
| Apache Kafka Application Development | **28%** | 17 |
| Apache Kafka Fundamentals | **23%** | 14 |
| Kafka Connect | **15%** | 9 |
| Application Observability | **13%** | 8 |
| Apache Kafka Streams | **12%** | 7 |
| Application Testing | **8%** | 5 |

Trước đây plan ghi chú tỉ trọng này là "tổng hợp cộng đồng, không phải tài liệu Confluent công bố". Syllabus của VMExam nay liệt kê **đúng 6 domain với đúng 6 con số** này, khớp hoàn toàn với con số đang dùng trong repo. Đây là mức xác nhận cao nhất có thể đạt được khi Confluent không phát hành exam guide dạng PDF như AWS.

> ⚠️ **Vẫn là phỏng đoán:** ngưỡng đậu **~75%**. Nguồn duy nhất nói con số này là README của repo `danielsobrado`, và chính tác giả ghi kèm *"(My own guess)"*. Confluent không công bố. Giữ ngưỡng cá nhân **≥ 80%** để có biên an toàn.

---

## 2. Các nguồn đã khảo sát

### 2.1 Nguồn chính thức

| Nguồn | Dùng để làm gì |
|---|---|
| [confluent.io/certification](https://www.confluent.io/certification/) | Thông số kỳ thi, dạng câu hỏi, chính sách proctor/retake/hiệu lực |
| [docs.confluent.io](https://docs.confluent.io/platform/current/) | Đối chiếu Schema Registry, Connect, security |
| [kafka.apache.org/43/](https://kafka.apache.org/43/) | Nguồn chân lý cho mọi giá trị mặc định |
| Apache cwiki — các KIP | KIP-98, 345, 429, 480, 618, 848, 932, 966, 1030, 1147 |

### 2.2 Nguồn cộng đồng đã crawl

| Nguồn | Quy mô | Cập nhật lần cuối | Đánh giá |
|---|---|---|---|
| [`danielsobrado/CCDAK-Exam-Questions`](https://github.com/danielsobrado/CCDAK-Exam-Questions) | **356 câu**, 14 chủ đề, 55 file | 2026-07-20 | Kho cộng đồng tốt nhất tìm được. Tác giả nói rõ **không phải đề thật**. Xem phần 3 để biết lỗ hổng |
| [`YovoManolov/kafka-certification-study-guide`](https://github.com/YovoManolov/kafka-certification-study-guide) | 22 chương + trình chạy mock trên trình duyệt | 2026 | Sạch phần ZooKeeper, nhưng **không** phủ KIP-848 / share group |
| [`ayushdixit487/CCDAK-Exam-Practice-Test1` và `-2`](https://github.com/ayushdixit487/CCDAK-Exam-Practice-Test1) | 2 × 50 câu | — | Mô tả phủ *"Brokers, Topics, **Zookeeper**, …"* — đề cương từ thời Kafka 2.x |
| [Stéphane Maarek — bài hướng dẫn ôn CCDAK](https://medium.com/@stephane.maarek/how-to-prepare-for-the-confluent-certified-developer-for-apache-kafka-ccdak-exam-ab081994da78) | bài viết | — | Trả HTTP 403, không crawl được |
| [VMExam — syllabus CCDAK](https://www.vmexam.com/confluent/confluent-apache-kafka-developer-certification-exam-syllabus) | syllabus + đề mẫu | — | **Nguồn xác nhận tỉ trọng 6 domain** |

### 2.3 Nguồn KHÔNG dùng, và lý do

Một nhóm lớn kết quả tìm kiếm là **braindump thương mại**: ExamCollection, ValidExamDumps, DumpsBoss, CertsHero, SkillCertPro, Pass4Future, CertsProvider, Study4Exam. Các trang này quảng cáo *"actual exam questions"*.

Không dùng chúng, vì ba lý do độc lập:

1. **Vi phạm thoả thuận ứng viên.** Nội dung đề thi thật là tài sản của Confluent; sao chép lại vào repo của bạn tạo rủi ro không cần thiết cho chính chứng chỉ bạn sắp thi.
2. **Chất lượng không kiểm chứng được.** Không có nguồn, không có cách đối chiếu; nhiều trang bán cùng một tệp câu hỏi luân chuyển nhiều năm.
3. **Lỗi thời là mặc định, không phải ngoại lệ.** Mọi bộ dump lưu hành đều sinh ra trước Kafka 4.0. Xem phần 3.

---

## 3. Kết quả validate: kho câu hỏi công khai lỗi thời ở đâu

Đây là phần quan trọng nhất của khảo sát. Số liệu dưới đây đo trực tiếp trên **356 câu** của repo cộng đồng tốt nhất (`danielsobrado`, cập nhật 2026-07).

### 3.1 Lỗ hổng tính năng — nghiêm trọng nhất

Đếm số lần xuất hiện trên toàn bộ file câu hỏi:

| Tính năng | Có từ | Số lần xuất hiện |
|---|---|---|
| **Cooperative rebalancing** (`CooperativeStickyAssignor`, KIP-429) | Kafka **2.4** | **0** |
| **KIP-848** — consumer protocol mới (`group.protocol=consumer`) | GA **4.0** | **0** |
| **Share groups / Queues for Kafka** (KIP-932) | GA **4.2** | **0** |
| **Tiered storage** (KIP-405) | 3.6 → GA 3.9 | **0** |
| **ELR** — Eligible Leader Replicas (KIP-966) | 4.0 → mặc định 4.1 | **0** |
| **Streams rebalance protocol** (KIP-1071) | GA 4.2 | **0** |

Sáu con số 0. Nghĩa là một người luyện hết 356 câu vẫn **chưa từng gặp** bất kỳ câu nào về cơ chế rebalance đã tồn tại từ Kafka 2.4, chứ chưa nói tới các tính năng 4.x. Trong khi đó, `session.timeout.ms`, assignor và giao thức consumer đều nằm trong domain Application Development — **28% đề thi**.

### 3.2 Nội dung dạy sai vì đã bị gỡ khỏi sản phẩm

Tài liệu "ôn phút chót" của cùng repo vẫn liệt kê các sự kiện sau như kiến thức cần thuộc:

- ZooKeeper znode, znode tạm thời và znode bền vững
- Ensemble 5 node chịu được 2 node hỏng
- Cổng ZooKeeper 2181 / 2888 / 3888
- `tickTime=2000`, `initLimit=20`, `syncLimit=5` → timeout 40 giây

**ZooKeeper đã bị gỡ hoàn toàn khỏi Kafka 4.0.** Toàn bộ nhóm kiến thức trên hiện không còn giá trị thi.

Ngoài ra còn các phương án và câu hỏi dựng trên thế giới ZooKeeper:

| File | Nội dung |
|---|---|
| `CLI/Questions1.md` | Phương án dùng `kafka-topics.sh --create --zookeeper localhost:2181` |
| `CLI/Questions1.md` | Phương án dùng `zookeeper-shell.sh` để sửa config topic |
| `Broker/Questions1.md` | Mô tả bầu controller qua thứ tự tạo znode tạm thời |
| `Security/Questions1.md` | ACL lưu tại znode `/kafka-acl/` |
| `Kafka-Streams/Questions2.md` | Trạng thái Streams lưu tại znode `/kafka-streams` |

Một phần trong số này nằm ở vị trí **phương án sai**, nên vẫn chấp nhận được. Nhưng người học không có cách phân biệt đâu là "sai vì lỗi thời" và đâu là "sai theo thiết kế của câu hỏi".

### 3.3 Điểm tích cực, ghi nhận công bằng

- Thư mục mang tên `Zookeeper` của repo `danielsobrado` thực chất **đã được viết lại cho KRaft**: cả 30 câu hỏi về `process.roles`, `controller.quorum.voters`, số controller tối thiểu. Chỉ tên thư mục là di sản cũ.
- File `LAST_MINUTE_REVIEW.md` neo theo **Kafka 4.2** và ghi đúng nhiều điểm: `linger.ms` đổi 0 → 5 ở 4.0, Java 17 cho broker từ 4.0, ZooKeeper đã gỡ, KIP-848 GA nhưng classic vẫn là mặc định, share group production-ready ở 4.2.
- Repo `YovoManolov` không còn nội dung ZooKeeper.

Nói cách khác: **phần tài liệu ôn thì đã cập nhật, nhưng phần ngân hàng câu hỏi thì chưa theo kịp**. Đây là lý do bộ mock trong thư mục này được viết mới.

---

## 4. Phương pháp xây mock trong thư mục này

1. **Tự viết 100%.** Không câu nào sao chép nguyên văn từ bất kỳ practice test, dump hay repo nào. Nguồn cộng đồng chỉ dùng để trả lời câu hỏi *"chủ đề nào hay được hỏi"*.
2. **Neo theo Apache Kafka 4.3.** Mọi giá trị mặc định tra chéo với [`../CCDAK-STUDY-PLAN.md`](../CCDAK-STUDY-PLAN.md) §6 và [`../study-plan/VALIDATION.md`](../study-plan/VALIDATION.md).
3. **Biến chỗ lỗi thời thành bẫy có chủ đích.** Mỗi mock có tối thiểu 5 câu mà **một phương án nhiễu chính là giá trị mặc định cũ** (`acks=1`, `linger.ms=0`, `session.timeout.ms=10000`, ZooKeeper). Ai luyện bằng dump cũ sẽ chọn đúng phương án đó và sai.
4. **Phủ đủ 6 lỗ hổng ở mục 3.1.** Cooperative rebalancing, KIP-848, share groups, tiered storage, ELR và Streams rebalance protocol đều xuất hiện trong bộ mock.
5. **Có đủ 4 dạng câu của đề thật**, gồm **matching** và **list order** — hai dạng mà không một practice test bên thứ ba nào cung cấp.
6. **Truy nguồn được.** Mỗi lời giải có dòng `📎 Source` trỏ tới một file tài nguyên có thật trong `study-plan/week-NN/resources/`, tức là trỏ về tài liệu gốc đã crawl.

---

## 5. Việc cần làm lại trước ngày thi

| Việc | Vì sao |
|---|---|
| Mở lại [confluent.io/certification](https://www.confluent.io/certification/) xác nhận **giá và số câu** | Trang chính thức nêu 90 phút và các dạng câu, nhưng **không** in số câu và giá; hai con số đó đến từ syllabus bên thứ ba |
| Kiểm tra Kafka đã lên **4.4+** chưa | Nếu có, đọc mục *Notable changes* — đặc biệt `group.protocol` đã đổi mặc định sang `consumer` chưa |
| Làm **sample questions chính thức** của Confluent | Nguồn duy nhất phản ánh đúng văn phong đề thật, kể cả dạng matching và list order |

---

> 📌 **Kết luận ngắn gọn:** ngoài kia không thiếu câu hỏi CCDAK, nhưng thiếu câu hỏi **đúng với Kafka hiện tại**. Kho cộng đồng lớn nhất có 356 câu và **không câu nào** chạm tới cooperative rebalancing, KIP-848, share groups, tiered storage hay ELR. Bộ mock trong thư mục này được viết để lấp đúng khoảng trống đó.
