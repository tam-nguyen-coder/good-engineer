# 📂 Tài nguyên Tuần 2 — Lambda nâng cao

> Crawl từ tài liệu AWS chính thức. Về [file học Tuần 2](../README.md) · [Kế hoạch tổng](../../../DVA-C02-STUDY-PLAN.md)

| # | Tài nguyên (file local) | Chủ đề | Nguồn AWS |
|---|---|---|---|
| 1 | [lambda-versions.md](lambda-versions.md) | Function versions — `$LATEST` mutable vs version bất biến, qualified/unqualified ARN | https://docs.aws.amazon.com/lambda/latest/dg/configuration-versions.html |
| 2 | [lambda-aliases.md](lambda-aliases.md) | Aliases — con trỏ tới version, weighted routing (canary) | https://docs.aws.amazon.com/lambda/latest/dg/configuration-aliases.html |
| 3 | [lambda-layers.md](lambda-layers.md) | Layers — chia sẻ dependency, tối đa 5/function, `/opt`, layer version immutable | https://docs.aws.amazon.com/lambda/latest/dg/chapter-layers.html |
| 4 | [lambda-concurrency.md](lambda-concurrency.md) | Reserved vs provisioned concurrency, quy tắc trừ 100 unit, throttle = 0 | https://docs.aws.amazon.com/lambda/latest/dg/configuration-concurrency.html |
| 5 | [lambda-async-invocation.md](lambda-async-invocation.md) | Async invoke (`Event`, HTTP 202), internal queue, destinations | https://docs.aws.amazon.com/lambda/latest/dg/invocation-async.html |
| 6 | [lambda-event-source-mapping.md](lambda-event-source-mapping.md) | Event source mapping (poll) — batching, at-least-once/idempotent, provisioned mode | https://docs.aws.amazon.com/lambda/latest/dg/invocation-eventsourcemapping.html |
| 7 | [lambda-quotas-limits.md](lambda-quotas-limits.md) | Lambda quotas — số liệu payload, package, memory, timeout, `/tmp`, concurrency | https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-limits.html |

## Gợi ý thứ tự đọc
1. **lambda-versions.md** — nắm nền tảng `$LATEST` vs version bất biến trước.
2. **lambda-aliases.md** — alias trỏ tới version + weighted routing (canary/blue-green).
3. **lambda-concurrency.md** — phân biệt reserved vs provisioned concurrency (điểm bẫy hay gặp).
4. **lambda-async-invocation.md** — mô hình async (`Event`, 202) và xử lý lỗi/destinations.
5. **lambda-event-source-mapping.md** — mô hình poll cho `SQS`/`Kinesis`/`DynamoDB Streams` + batching.
6. **lambda-layers.md** — layers & giới hạn (5 layer, `/opt`, immutable version).
7. **lambda-quotas-limits.md** — chốt lại toàn bộ con số cần thuộc lòng cho phòng thi.

> ⚠️ **Lưu ý số liệu payload async:** bảng *Lambda quotas* hiện hành của AWS ghi **1 MB** cho async (trước đây phổ biến là 256 KB). File tuần (`week-02.md`) vẫn ghi 256 KB theo tài liệu ôn thi cũ — khi làm đề, đối chiếu bảng quotas gốc để biết con số mới nhất.
