# 📒 Sổ câu sai — CCAAK (Kafka Administrator)

> Mỗi câu practice hoặc mock **làm sai** (và cả câu **đúng nhờ đoán may**) → viết 1 file phân tích ở đây.
> Về [Kế hoạch tổng](../CCAAK-STUDY-PLAN.md) · [Tuần 8 — tuần chốt](../study-plan/week-08/README.md) · [Mock exams](../mock-exams/README.md)

## Quy ước đặt tên

`CCAAK-NNNN.md` với hậu tố 4 chữ số, tăng dần theo thứ tự bạn viết: `CCAAK-0001.md`, `CCAAK-0002.md`…
Giống quy ước đã dùng cho [`SAA-C03/`](../../SAA-C03/), `CLF-C02/` và [`CCDAK/questions/`](../../CCDAK/questions/README.md).

## Format 6 mục (bắt buộc)

Theo đúng [`aws-saa-c03-analysis-format.md`](../../aws-saa-c03-analysis-format.md) ở gốc repo. Sáu mục, không đổi thứ tự:

1. **CONTEXT & ĐỀ BÀI** — tình huống, trạng thái cluster, triệu chứng quan sát được.
2. **KEYWORDS QUAN TRỌNG** — bảng Markdown đúng 2 cột: `Keyword` và `Ý nghĩa / Gợi ý`.
3. **YÊU CẦU CỦA ĐỀ** — qualifier quyết định đáp án (*without data loss*, *with minimal downtime*, *fewest changes*, *survive the loss of one rack*, *without restarting brokers*).
4. **ĐÁP ÁN ĐÚNG** — nguyên văn lựa chọn đúng + vì sao nó khớp tình huống.
5. **CÁC ĐÁP ÁN SAI** — từng lựa chọn sai, sai ở đâu, và **khi nào nó sẽ đúng**.
6. **MẸO GHI NHỚ (Memory Hook)** — mẹo ngắn, mở đầu bằng 🧠.

## Ba mục bổ sung riêng cho CCAAK

Vì đề CCAAK hỏi **hành động của người vận hành** chứ không hỏi định nghĩa, thêm ba dòng vào cuối mỗi file:

- **`Trục đánh đổi:`** — câu này thực chất hỏi về trục nào: *durability · availability · throughput · chi phí vận hành*. Gần như mọi câu CCAAK quy về một trong bốn trục.
- **`Hành động rẻ hơn đã bị bỏ qua:`** — đề thường cài một phương án "đúng nhưng quá tay" (tăng partition, bật unclean election, hạ `min.insync.replicas`). Ghi lại phương án rẻ và đảo ngược được mà lẽ ra phải thử trước.
- **`Lý do mình sai:`** — chọn một trong bốn nhóm: *thiếu kiến thức · đọc sót qualifier · dính bẫy version · hết giờ*.

Ghi kèm **nguồn đề** (tuần mấy, hay mock số mấy) và **ngày làm**, phục vụ ôn lại theo mốc **1 ngày → 3 ngày → 7 ngày**.

## Khác biệt so với bộ CCDAK

- Tên config, metric và công cụ giữ nguyên tiếng Anh trong backtick: `` `min.insync.replicas` ``, `` `UnderReplicatedPartitions` ``, `` `kafka-reassign-partitions.sh` ``.
- Văn phân tích viết **tiếng Việt**.
- Nếu câu sai vì chọn phải phương án thuộc **thế giới ZooKeeper** (znode, `--zookeeper`, `zookeeper.connect`, `AclAuthorizer`), đánh dấu nhãn `bẫy version` và ghi rõ — đây là nhóm bẫy phổ biến nhất của CCAAK vì tài liệu ôn công khai vẫn đầy nội dung tiền Kafka 4.0.

## Gợi ý theo dõi

Khi số file tăng, nhóm theo domain để thấy vùng yếu thật sự:

| Domain | Tỉ trọng | Số file đã viết |
|---|---|---|
| Cluster Configuration | 22% | |
| Fundamentals | 15% | |
| Security | 15% | |
| Troubleshooting | 15% | |
| Deployment Architecture | 12% | |
| Kafka Connect | 12% | |
| Observability | 10% | |

> 📌 Domain nào chiếm nhiều file nhất chính là nơi cần quay lại đọc Buổi A và **làm lại lab**, trước khi thử mock tiếp theo. Với CCAAK, gần như mọi lỗ hổng đều vá được bằng lab chứ không bằng đọc thêm.
