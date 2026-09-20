# 🎯 Mock Exams — CCAAK (60 câu · 90 phút)

> Ba bộ đề **full-length, canh giờ, trộn domain**, mô phỏng đúng định dạng kỳ thi CCAAK.
> Khác với các câu theo chủ đề trong [`../study-plan/`](../study-plan/): ở đó bạn luyện **từng mảng vận hành**, ở đây bạn luyện **phản xạ của người trực ca dưới áp lực 90 giây/câu**.
> Về [Kế hoạch tổng](../CCAAK-STUDY-PLAN.md) · [Tuần 8 — tuần chốt](../study-plan/week-08/README.md) · [Sổ câu sai](../questions/README.md)

---

## Ba bộ đề

| Mock | Sắc thái | Dùng khi nào |
|---|---|---|
| [**Mock 01**](mock-01/questions.md) — *Cấu hình & nền tảng* | Nặng về Cluster Configuration và Fundamentals, nhấn vào **bẫy version** ZooKeeper và các mặc định đã đổi | Ngay sau Tuần 7. Bài đo đường cơ sở |
| [**Mock 02**](mock-02/questions.md) — *Trực ca và chẩn đoán* | Gần như mọi câu bắt đầu từ **triệu chứng**: log nguyên văn, output CLI, metric bất thường | Sau khi vá xong vùng yếu từ Mock 01 |
| [**Mock 03**](mock-03/questions.md) — *Kiến trúc & đánh đổi* | Cả bốn phương án đều chạy được; **qualifier trong đề** quyết định. Khó nhất | Bài cuối trước khi đặt lịch thi |

Mỗi bộ có `questions.md` và `answers.md`. Lời giải kèm bảng chấm điểm theo 7 domain và bản đồ câu sai trỏ về tuần cần học lại.

---

## Định dạng — giống đề thật

| Hạng mục | Mock này | Đề thật |
|---|---|---|
| Số câu | 60 | 60 |
| Thời gian | 90 phút | 90 phút |
| Dạng câu | Single · Multi · **Matching** · **Ordering** | multiple-choice · multiple-select · **matching** · **list order** |
| Tỉ trọng | 13 / 9 / 9 / 9 / 7 / 7 / 6 | 22% / 15% / 15% / 15% / 12% / 12% / 10% |

Phân bổ domain mỗi mock: **CFG 13 · FUND 9 · SEC 9 · TROUBLE 9 · ARCH 7 · CONNECT 7 · OBS 6**.
Phân bổ dạng câu: **38 Single · 14 Multi · 4 Matching · 4 Ordering**.

> 💡 **Matching và Ordering** có trên đề thật nhưng **không practice test bên thứ ba nào cung cấp**. Mỗi mock ở đây có 4 câu mỗi dạng. Dạng lạ ngốn thời gian hơn dạng khó, nên đừng bỏ qua chúng.

---

## Đặc thù của đề CCAAK

Trang phân tích đề mô tả: *"The exam rarely asks you to define a term in isolation. Instead, it presents a scenario and asks which action a competent administrator would take."*

Ba hệ quả khi luyện:

1. **Đọc triệu chứng trước, phương án sau.** Xác định câu hỏi đang nằm trên trục nào: *durability · availability · throughput · chi phí vận hành*. Gần như mọi câu CCAAK quy về một trong bốn trục đó.
2. **Ưu tiên hành động rẻ và đảo ngược được.** Đề hay cài một phương án "đúng nhưng quá tay" — tăng partition (một chiều, phá ordering), bật `unclean.leader.election.enable` (mất dữ liệu), hạ `min.insync.replicas` khi đang sự cố. Phương án đúng thường là cái rẻ hơn và lùi lại được.
3. **Nghi ngờ mọi phương án nhắc ZooKeeper.** Với Kafka 4.x, znode, `--zookeeper`, `zookeeper.connect` và `AclAuthorizer` gần như chắc chắn là bẫy.

---

## Cách chạy một bài mock

1. **Hẹn giờ 90 phút.** Không tra tài liệu, không tạm dừng. Không canh giờ thì bài mock chỉ còn là bài đọc hiểu.
2. **Giữ nhịp 90 giây/câu.** Quá 2 phút thì đánh dấu, đoán một phương án, đi tiếp. Không bỏ trống câu nào.
3. **Ghi lại câu đánh dấu** và câu **đúng nhờ đoán may** — hai nhóm này tính như câu sai.
4. **Chấm và điền bảng 7 domain** trong `answers.md` ngay sau khi nộp.
5. **Review 100% câu sai trong cùng ngày**, mỗi câu đáng nhớ viết một file phân tích trong [`../questions/`](../questions/README.md), nhớ điền ba mục riêng của CCAAK: *Trục đánh đổi*, *Hành động rẻ hơn đã bị bỏ qua*, *Lý do mình sai*.
6. **Nghỉ ít nhất 1 ngày** trước bài kế tiếp; ngày xen giữa dành cho **lab**, không phải đọc thêm.

---

## Ngưỡng và cách đọc kết quả

Confluent **không công bố ngưỡng đậu**. Con số ~75% trên mạng chỉ là phỏng đoán cộng đồng. Ngưỡng cá nhân đặt cao hơn để có biên an toàn:

| Kết quả | Nghĩa là | Làm gì tiếp |
|---|---|---|
| **≥ 80%** (48/60) trên **cả 3 mock** | Đủ điều kiện đặt lịch | Review 100% câu sai rồi đặt lịch |
| **70–79%** | Còn lỗ hổng cục bộ | Học lại domain thấp nhất 2 ngày **và làm lại lab của tuần đó**. Chưa đặt lịch |
| **< 70%** | Chưa sẵn sàng | **Lùi lịch 1 tuần.** Quay lại 2 domain thấp nhất, làm lại Buổi A và B |

Ngưỡng từng domain: CFG ≥ 10/13 · FUND ≥ 7/9 · SEC ≥ 7/9 · TROUBLE ≥ 7/9 · ARCH ≥ 5/7 · CONNECT ≥ 5/7 · OBS ≥ 4/6.

> ⚠️ Một domain dưới ngưỡng **hai bài liên tiếp** là tín hiệu quay lại **lab**, không phải tín hiệu làm thêm mock. Với CCAAK, gần như mọi lỗ hổng đều vá được bằng tay chứ không bằng đọc.

---

## Nguồn và tính cập nhật

Toàn bộ 180 câu ở đây **tự viết**, neo theo **Apache Kafka 4.3**, không sao chép từ practice test hay dump nào.

Lý do không chép: hai kho câu hỏi CCAAK công khai lớn nhất có tỉ lệ nhắc ZooKeeper so với KRaft là **118 trên 3**, và ở nhiều chỗ ZooKeeper còn là **đáp án đúng** cho câu hỏi về bầu controller. Số liệu đo được, ví dụ cụ thể và danh sách nguồn nằm ở [**SOURCES-AND-VALIDATION.md**](SOURCES-AND-VALIDATION.md).

Mỗi lời giải có dòng `📎 Source` trỏ về một file tài nguyên có thật trong `../study-plan/week-NN/resources/`, tức là trỏ ngược về tài liệu gốc đã crawl từ Apache Kafka và Confluent.
