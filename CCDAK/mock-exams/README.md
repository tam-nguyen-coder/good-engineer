# 🎯 Mock Exams — CCDAK (60 câu · 90 phút)

> Ba bộ đề **full-length, canh giờ, trộn domain**, mô phỏng đúng định dạng kỳ thi thật.
> Khác với 291 câu theo chủ đề trong [`../study-plan/`](../study-plan/): ở đó bạn luyện **từng mảng kiến thức**, ở đây bạn luyện **phản xạ dưới áp lực 90 giây/câu**.
> Về [Kế hoạch tổng](../CCDAK-STUDY-PLAN.md) · [Tuần 10 — tuần chốt](../study-plan/week-10/README.md) · [Sổ câu sai](../questions/README.md)

---

## Ba bộ đề

| Mock | Sắc thái | Dùng khi nào |
|---|---|---|
| [**Mock 01**](mock-01/questions.md) — *Nền tảng & bẫy version* | Phủ đều 6 domain, nhấn vào các **mặc định đã đổi** theo phiên bản. Mỗi câu loại này có một phương án nhiễu là **giá trị cũ** | Ngay sau khi học xong Tuần 9. Đây là bài đo đường cơ sở |
| [**Mock 02**](mock-02/questions.md) — *Chẩn đoán sự cố* | Bắt đầu từ **triệu chứng** rồi suy ngược: log lỗi nguyên văn, output CLI, metric bất thường | Sau khi đã vá xong vùng yếu lộ ra từ Mock 01 |
| [**Mock 03**](mock-03/questions.md) — *Thiết kế & đánh đổi* | Cả bốn phương án đều chạy được; **qualifier trong đề** mới quyết định đáp án | Bài cuối trước khi đặt lịch thi. Khó nhất trong ba bộ |

Mỗi bộ có `questions.md` và `answers.md` riêng. Lời giải kèm bảng chấm điểm theo domain và bản đồ câu sai trỏ về tuần cần học lại.

---

## Định dạng — giống đề thật

| Hạng mục | Mock này | Đề thật |
|---|---|---|
| Số câu | 60 | 60 |
| Thời gian | 90 phút | 90 phút |
| Nhịp | ~90 giây/câu | ~90 giây/câu |
| Dạng câu | Single · Multi · **Matching** · **Ordering** | Multiple-choice · multiple-select · **matching** · **list order** |
| Tỉ trọng domain | 17 / 14 / 9 / 8 / 7 / 5 | 28% / 23% / 15% / 13% / 12% / 8% |

> 💡 **Matching và Ordering** là hai dạng câu có trên đề thật mà **không một practice test bên thứ ba nào cung cấp**. Mỗi mock ở đây có 4 câu mỗi dạng. Đừng bỏ qua chúng — dạng lạ làm mất thời gian nhiều hơn dạng khó.

Phân bổ dạng câu trong mỗi mock: **38 Single · 14 Multi · 4 Matching · 4 Ordering**.

---

## Cách chạy một bài mock

1. **Hẹn giờ 90 phút.** Không tra tài liệu, không tạm dừng, điện thoại để phòng khác. Nếu không canh giờ thì bài mock chỉ còn là bài đọc hiểu.
2. **Giữ nhịp 90 giây/câu.** Câu nào quá 2 phút thì đánh dấu, đoán một phương án rồi đi tiếp. Không bỏ trống câu nào — sai không bị trừ điểm.
3. **Ghi lại câu đánh dấu** và câu **đúng nhờ đoán may**. Hai nhóm này tính như câu sai khi đánh giá.
4. **Chấm và điền bảng domain** trong `answers.md` ngay sau khi nộp.
5. **Review 100% câu sai trong cùng ngày**, mỗi câu đáng nhớ viết một file phân tích 6 mục trong [`../questions/`](../questions/README.md).
6. **Nghỉ ít nhất 1 ngày** trước bài mock kế tiếp; ngày xen giữa dành cho vùng yếu.

---

## Ngưỡng và cách đọc kết quả

Confluent **không công bố ngưỡng đậu**. Con số ~75% lưu hành trên mạng chỉ là phỏng đoán của cộng đồng, chính tác giả nguồn đó cũng ghi rõ là suy đoán. Vì vậy ngưỡng cá nhân đặt cao hơn để có biên an toàn:

| Kết quả | Nghĩa là | Làm gì tiếp |
|---|---|---|
| **≥ 80%** (48/60) trên **cả 3 mock** | Đủ điều kiện đặt lịch thi | Review 100% câu sai, rồi đặt lịch |
| **70–79%** | Gần đạt, còn lỗ hổng cục bộ | Học lại domain thấp nhất 2 ngày, mock lại. **Chưa đặt lịch** |
| **< 70%** | Chưa sẵn sàng | **Lùi lịch 1 tuần.** Quay lại 2 domain thấp nhất, học lại Buổi A và B của tuần tương ứng |

Ngưỡng theo từng domain (ghi trong mỗi `answers.md`): DEV ≥ 13/17 · FUND ≥ 10/14 · CONNECT ≥ 7/9 · OBS ≥ 6/8 · STREAMS ≥ 5/7 · TEST ≥ 3/5.

> ⚠️ Một domain dưới ngưỡng **hai bài liên tiếp** là tín hiệu quay lại học, không phải tín hiệu làm thêm mock.

---

## Nguồn và tính cập nhật

Toàn bộ 180 câu ở đây **tự viết**, neo theo **Apache Kafka 4.3**, không sao chép từ practice test hay dump nào.

Lý do không chép: kho câu hỏi CCDAK công khai lớn nhất hiện có 356 câu, và **không câu nào** chạm tới cooperative rebalancing, KIP-848, share groups, tiered storage hay ELR. Chi tiết khảo sát, số liệu đo được và danh sách nguồn nằm ở [**SOURCES-AND-VALIDATION.md**](SOURCES-AND-VALIDATION.md).

Mỗi lời giải có dòng `📎 Source` trỏ về một file tài nguyên có thật trong `../study-plan/week-NN/resources/`, tức là trỏ ngược về tài liệu gốc đã crawl từ Apache Kafka, Confluent và AWS.
