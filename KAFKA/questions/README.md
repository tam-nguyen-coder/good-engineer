# 📒 Sổ câu sai — Kafka / CCDAK

> Mỗi câu practice hoặc mock **làm sai** (và cả câu **đúng nhờ đoán may**) → viết 1 file phân tích ở đây.
> Về [Kế hoạch tổng](../KAFKA-STUDY-PLAN.md) · [Tuần 10 — tuần chốt](../study-plan/week-10/README.md)

## Quy ước đặt tên

`KAFKA-NNNN.md` với hậu tố 4 chữ số, đánh số tăng dần theo thứ tự bạn viết: `KAFKA-0001.md`, `KAFKA-0002.md`…
Giống quy ước đã dùng cho [`SAA-C03/`](../../SAA-C03/) và `CLF-C02/` trong repo này.

## Format 6 mục (bắt buộc)

Theo đúng [`aws-saa-c03-analysis-format.md`](../../aws-saa-c03-analysis-format.md) ở gốc repo — **đọc file đó trước khi viết file đầu tiên**. Sáu mục, không đổi thứ tự:

1. **CONTEXT & ĐỀ BÀI** — tình huống, tài nguyên sẵn có, mục tiêu hoặc sự cố.
2. **KEYWORDS QUAN TRỌNG** — bảng Markdown đúng 2 cột: `Keyword` và `Ý nghĩa / Gợi ý`.
3. **YÊU CẦU CỦA ĐỀ** — dạng câu hỏi (*guarantee ordering*, *no data loss*, *minimize latency*, *exactly-once*, *without changing producer code*…) và ràng buộc.
4. **ĐÁP ÁN ĐÚNG** — nguyên văn lựa chọn đúng + giải thích vì sao khớp tình huống.
5. **CÁC ĐÁP ÁN SAI** — từng lựa chọn sai, sai ở đâu, và **khi nào nó sẽ đúng**.
6. **MẸO GHI NHỚ (Memory Hook)** — mẹo ngắn, mở đầu bằng 🧠.

## Khác biệt so với bộ AWS

- Tên config, tên class và tên công cụ giữ nguyên tiếng Anh trong backtick: `` `min.insync.replicas` ``, `` `CooperativeStickyAssignor` ``, `` `kafka-consumer-groups.sh` ``.
- Văn phân tích viết **tiếng Việt**, giống bộ `SAA-C03` và `DVA-C02`.
- Thêm một dòng cuối mỗi file: **`Lý do mình sai:`** — chọn một trong bốn nhóm *thiếu kiến thức · đọc sót qualifier · dính bẫy · hết giờ*. Đây là dữ liệu để bạn biết nên sửa cách học hay sửa cách làm bài.
- Ghi kèm **nguồn đề** (tuần mấy trong plan, hoặc tên bộ practice test) và **ngày làm**, phục vụ ôn lại theo mốc **1 ngày → 3 ngày → 7 ngày**.

## Gợi ý theo dõi

Khi số file tăng, nhóm chúng theo domain để thấy vùng yếu thật sự:

| Domain | Tỉ trọng CCDAK | Số file đã viết |
|---|---|---|
| Application Development | 28% | |
| Fundamentals | 23% | |
| Kafka Connect | 15% | |
| Observability | 13% | |
| Kafka Streams | 12% | |
| Testing | 8% | |

> 📌 Domain nào chiếm nhiều file nhất chính là nơi cần quay lại đọc Buổi A và làm lại lab, **trước** khi thử full mock tiếp theo.
