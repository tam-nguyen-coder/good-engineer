# Amazon SNS — Message filtering (filter policy)

> **Nguồn (AWS official):** https://docs.aws.amazon.com/sns/latest/dg/sns-message-filtering.html
> **Tuần:** 5 — Messaging + Step Functions + Caching · **Loại:** AWS Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)
- **Mặc định:** subscriber nhận **MỌI** message publish lên topic. Muốn chỉ nhận **một tập con** → gắn **filter policy** cho subscription.
- **Filter policy** là một **JSON object** đặt trên subscription; `SNS` so khớp policy với từng message, chỉ gửi message **thỏa điều kiện** → subscriber khỏi tự lọc trong code (giảm code + giảm chi phí xử lý thừa).
- **Filter policy scope** — 2 chế độ:
  - `MessageAttributes` (mặc định): lọc theo **message attributes**.
  - `MessageBody`: lọc theo **nội dung body**; yêu cầu payload là **JSON hợp lệ**.
- Nếu subscription **không có** filter policy → nhận **tất cả** message của topic.
- Bẫy đề: "mỗi subscriber chỉ muốn nhận loại message nhất định trong fan-out" → dùng **SNS message filtering (filter policy)**, KHÔNG cần tạo nhiều topic hay lọc thủ công.

---

## 📄 Nội dung (trích từ tài liệu gốc)

By default, an Amazon SNS topic subscriber receives **every message** that's published to the topic. To receive only a subset of the messages, a subscriber must assign a **filter policy** to the topic subscription.

A filter policy is a **JSON object** containing properties that define which messages the subscriber receives. Amazon SNS supports policies that act on the **message attributes** or on the **message body**, according to the **filter policy scope** that you set for the subscription. Filter policies for the message body assume that the message payload is a **well-formed JSON object**.

If a subscription doesn't have a filter policy, the subscriber receives **every message** published to its topic. When you publish a message to a topic with a filter policy in place, Amazon SNS compares the message attributes or the message body to the properties in the filter policy for each of the topic's subscriptions. If **all** of the message attributes or message body properties satisfy the conditions specified in the filter policy, Amazon SNS sends the message to the subscriber. Otherwise, Amazon SNS doesn't send the message to that subscriber.

> Ghi chú: Trang gốc còn liên kết tới các mục con: *filter policy scope* (`MessageAttributes` vs `MessageBody`), *filter policy constraints* (giới hạn số key/giá trị), *matching operators* (exact match, anything-but, prefix, numeric range, IP address, `$or`, `AND`/`OR` logic) và ví dụ áp dụng filter policy bằng console/CLI/SDK. Xem link gốc để lấy đầy đủ cú pháp và ví dụ.
