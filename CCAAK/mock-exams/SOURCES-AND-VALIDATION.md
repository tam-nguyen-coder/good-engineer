# 🔍 Nguồn đã khảo sát & Kết quả validate — Mock CCAAK

> **Ngày khảo sát:** 2026-09-20 · **Phiên bản neo:** Apache Kafka **4.3.x**
> Tài liệu này trả lời hai câu hỏi: *(1) ngoài kia có gì*, và *(2) vì sao bộ mock trong thư mục này được viết mới thay vì chép lại*.
> Về [mục lục mock](README.md) · [Kế hoạch tổng](../CCAAK-STUDY-PLAN.md) · [Nhật ký validate](../study-plan/VALIDATION.md)

---

## 1. Thông số kỳ thi — đã xác minh chéo

| Hạng mục | Giá trị | Xác nhận bởi |
|---|---|---|
| Số câu | **60** | Syllabus VMExam · phân tích bigdataprep 07/2026 |
| Thời gian | **90 phút** | Trang Confluent chính thức |
| Giá | **150 USD** | VMExam · bigdataprep |
| Chấm điểm | **Pass/Fail**, không công bố ngưỡng | Trang Confluent chính thức |
| Dạng câu | multiple-choice · multiple-select · **matching** · **list order** | Trang Confluent chính thức |
| Hiệu lực / retake | 2 năm · chờ 7 ngày | Trang Confluent chính thức |
| Proctor | Honorlock | Trang Confluent chính thức |
| Đối tượng | *"Professionals who manage and maintain Kafka cluster environments"* | Trang Confluent chính thức |

### Tỉ trọng 7 domain — và một phát hiện về syllabus

| Domain | Tỉ trọng | Câu trong mock 60 |
|---|---|---|
| Apache Kafka Cluster Configuration | **22%** | 13 |
| Apache Kafka Fundamentals | **15%** | 9 |
| Apache Kafka Security | **15%** | 9 |
| Troubleshooting | **15%** | 9 |
| Deployment Architecture | **12%** | 7 |
| Kafka Connect | **12%** | 7 |
| Observability | **10%** | 6 |

Tổng là **101%** do Confluent làm tròn từng domain. Hai nguồn độc lập (syllabus VMExam và bài phân tích bigdataprep tháng 7/2026) đưa ra **đúng cùng bảy con số này**.

> 🔄 **Syllabus đã được cấu trúc lại, và đây là cách nhanh nhất để nhận diện tài liệu cũ.**
> Bản trước chia đề thành **4 domain**: Kafka Fundamentals 15% · Managing, Configuring and Optimizing a Cluster for Performance **30%** · Kafka Security 15% · Designing, Troubleshooting and Integrating Systems **40%**.
> Repo `isaac88` (cập nhật 10/2024) vẫn tổ chức câu hỏi theo bốn mục đó. Bất kỳ tài liệu ôn nào chia theo 4 domain đều thuộc thế hệ trước.

> ⚠️ **Vẫn là phỏng đoán:** ngưỡng đậu **~75%** lưu hành trên mạng. Confluent không công bố. Giữ ngưỡng cá nhân **≥80%**.

---

## 2. Các nguồn đã khảo sát

### 2.1 Nguồn chính thức

| Nguồn | Dùng để làm gì |
|---|---|
| [confluent.io/certification](https://www.confluent.io/certification/) | Thông số kỳ thi, dạng câu, chính sách, mô tả đối tượng CCAAK |
| [kafka.apache.org/43/](https://kafka.apache.org/43/) | Nguồn chân lý cho mọi giá trị mặc định broker và topic |
| [kafka.apache.org/43/generated/kafka_config.html](https://kafka.apache.org/43/generated/kafka_config.html) | Đối chiếu trực tiếp 18 default broker dùng trong plan |
| [docs.confluent.io](https://docs.confluent.io/platform/current/) | Cluster Linking, security, monitoring của Confluent Platform |
| Apache cwiki — các KIP | KIP-500, 392, 405, 853, 966, 1066, 1147 |

### 2.2 Nguồn cộng đồng đã crawl

| Nguồn | Quy mô | Cập nhật cuối | Đánh giá |
|---|---|---|---|
| [`osodevops/CCAAK-Exam-Questions`](https://github.com/osodevops/CCAAK-Exam-Questions) | ~60 câu, 7 chủ đề | **2025-03** | 19 lần nhắc ZooKeeper / 3 lần KRaft. Có câu đặt ZooKeeper làm **đáp án đúng** |
| [`isaac88/confluent-certified-administrator-for-apache-kafka-CCAAK`](https://github.com/isaac88/confluent-certified-administrator-for-apache-kafka-CCAAK) | 6 bộ sample, ~222 mục | **2024-10** | **99 lần nhắc ZooKeeper / 0 lần KRaft**. Tổ chức theo **syllabus 4 domain cũ** |
| [`YovoManolov/kafka-certification-study-guide`](https://github.com/YovoManolov/kafka-certification-study-guide) | 22 chương + trình chạy mock | 2026 | Sạch ZooKeeper nhưng không phủ tính năng 4.x |
| [VMExam — syllabus CCAAK](https://www.vmexam.com/confluent/confluent-apache-kafka-administrator-certification-exam-syllabus) | syllabus | — | **Nguồn xác nhận tỉ trọng 7 domain** |
| [bigdataprep — phân tích CCAAK](https://www.bigdataprep.com/2026/07/29/apache-kafka-administrator-ccaak/) | bài viết 07/2026 | — | Xác nhận tỉ trọng + mô tả **văn phong đề** |

### 2.3 Nguồn KHÔNG dùng

ExamTopics, ValidExamDumps, Marks4sure, CertificationBox, CliffsNotes và các trang bán dump tương tự quảng cáo *"actual exam questions"*. Không dùng vì ba lý do độc lập: vi phạm thoả thuận ứng viên, không kiểm chứng được nguồn, và toàn bộ đều sinh ra trước khi syllabus được cấu trúc lại.

---

## 3. Kết quả validate: tài liệu CCAAK công khai lỗi thời tới mức nào

Đây là phần quan trọng nhất. Số liệu đo trực tiếp trên hai kho CCAAK lớn nhất tìm được.

### 3.1 Tỉ lệ ZooKeeper trên KRaft: 118 : 3

| Repo | Nhắc ZooKeeper | Nhắc KRaft |
|---|---|---|
| `osodevops` (2025-03) | 19 | 3 |
| `isaac88` (2024-10) | **99** | **0** |
| **Tổng** | **118** | **3** |

**ZooKeeper đã bị gỡ hoàn toàn khỏi Kafka 4.0.** Với một kỳ thi **administrator**, chuyển đổi ZooKeeper sang KRaft chính là thay đổi vận hành trung tâm — nó đổi cách bầu controller, cách lưu metadata, cách lưu ACL, và toàn bộ bộ công cụ dòng lệnh.

### 3.2 Nghiêm trọng hơn CCDAK: ZooKeeper là ĐÁP ÁN ĐÚNG

Ở bộ CCDAK, ZooKeeper chủ yếu xuất hiện trong **phương án nhiễu**, nên vẫn còn chấp nhận được. Ở bộ CCAAK thì khác — nó là **đáp án được đánh dấu đúng**:

- *"When the broker running the controller thread fails, which broker becomes the new controller?"*
  → Đáp án ghi: **"The next broker to successfully recreate the ZooKeeper ephemeral node."**
  → Thực tế Kafka 4.x: controller được bầu bằng **Raft** trong controller quorum. Không có ephemeral node nào tồn tại.
- *"Which of the following are components of Kafka?"*
  → Đáp án đúng gồm: Producer, Consumer, **ZooKeeper**.

Người học theo tài liệu này không chỉ **thiếu** kiến thức mới, mà còn **học thuộc đáp án sai**.

### 3.3 Lỗ hổng tính năng

Đếm trên toàn bộ file của cả hai repo:

| Tính năng | Có từ | Số lần xuất hiện |
|---|---|---|
| **KRaft** (vận hành: quorum, `process.roles`, metadata log) | GA 3.3, bắt buộc từ **4.0** | **3** |
| **ELR** — Eligible Leader Replicas | 4.0 → mặc định 4.1 | **0** |
| **Tiered storage** | GA 3.9 | **1** |
| **Cluster Linking** (Confluent) | — | **0** |
| **Cooperative rebalancing** | 2.4 | **0** |
| **KIP-848** consumer protocol | GA 4.0 | **0** |
| **Share groups** | GA 4.2 | **0** |

Năm con số 0 và hai con số gần 0. Một người luyện hết cả hai kho vẫn **chưa từng gặp** ELR, tiered storage hay Cluster Linking — ba chủ đề nằm thẳng trong domain *Cluster Configuration* và *Deployment Architecture*, cộng lại **34%** của đề.

---

## 4. Phương pháp xây mock trong thư mục này

1. **Tự viết 100%.** Không câu nào sao chép từ practice test, dump hay repo nào. Nguồn cộng đồng chỉ dùng để biết *chủ đề nào hay được hỏi* và *đề cũ sai ở đâu*.
2. **Neo theo Apache Kafka 4.3.** Mọi giá trị mặc định tra chéo với [`../CCAAK-STUDY-PLAN.md`](../CCAAK-STUDY-PLAN.md) §6 và [`../study-plan/VALIDATION.md`](../study-plan/VALIDATION.md); 18 default broker đã đối chiếu trực tiếp với trang generated config.
3. **Biến chỗ lỗi thời thành bẫy có chủ đích.** Mỗi mock có tối thiểu 5 câu mà **một phương án nhiễu thuộc thế giới ZooKeeper** (znode, `--zookeeper`, `zookeeper.connect`, `AclAuthorizer`) hoặc là **giá trị mặc định cũ**. Ai luyện bằng đề cũ sẽ chọn trúng và sai.
4. **Phủ đủ các lỗ hổng ở mục 3.3.** ELR, tiered storage, Cluster Linking, KRaft vận hành đều xuất hiện trong bộ mock.
5. **Bám văn phong đề thật.** Trang phân tích mô tả đề CCAAK *"rarely asks you to define a term in isolation; it presents a scenario and asks which action a competent administrator would take"*. Vì vậy **≥60% số câu** bắt đầu từ **triệu chứng, log, output CLI hoặc metric**, và qualifier trong đề quyết định đáp án.
6. **Có đủ 4 dạng câu của đề thật**, gồm **matching** và **list order** — hai dạng không practice test bên thứ ba nào cung cấp.
7. **Truy nguồn được.** Mỗi lời giải có dòng `📎 Source` trỏ tới một file tài nguyên có thật trong `../study-plan/week-NN/resources/`.

---

## 5. Việc cần làm lại trước ngày thi

| Việc | Vì sao |
|---|---|
| Mở lại [confluent.io/certification](https://www.confluent.io/certification/) xác nhận **giá và số câu** | Trang chính thức nêu 90 phút và các dạng câu nhưng **không** in số câu và giá |
| Kiểm Kafka đã lên **4.4+** chưa | Nếu có, đọc *Notable changes* cho mặc định mới |
| Làm **sample questions chính thức** của Confluent | Nguồn duy nhất phản ánh đúng văn phong, kể cả matching và list order |
| Xác nhận lại **tỉ trọng 7 domain** trên trang đăng ký | Syllabus vừa được cấu trúc lại một lần; có thể đổi tiếp |

---

> 📌 **Kết luận ngắn gọn:** với CCAAK, tài liệu công khai không chỉ thiếu mà **sai**. Tỉ lệ ZooKeeper trên KRaft là 118 trên 3, và ZooKeeper còn được đánh dấu là đáp án đúng cho câu hỏi về bầu controller. Bộ mock trong thư mục này được viết để dạy đúng Kafka 4.3, và để biến chính những chỗ sai đó thành bẫy bạn nhận ra được trong phòng thi.
