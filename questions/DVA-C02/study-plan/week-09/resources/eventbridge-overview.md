# What Is Amazon EventBridge? (event buses, pipes, Scheduler)

> **Nguồn (AWS official):** https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-what-is.html
> **Tuần:** 9 — Observability & Optimization · **Loại:** AWS Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)
- **`EventBridge` = serverless event bus** kết nối các thành phần bằng event (event-driven, loosely-coupled). Tiền thân là **CloudWatch Events**.
- **Event bus** = router nhận event và giao tới **0 hoặc nhiều target** (nhiều nguồn → nhiều target); hỗ trợ **transform** event trước khi giao. Dùng **rule** khớp theo **event pattern** HOẶC theo **lịch**.
- **Pipes** = tích hợp **point-to-point** (1 source → 1 target), kèm **enrichment & transformation** nâng cao. Ví dụ: source = **DynamoDB stream**, target = event bus.
- **EventBridge Scheduler** = serverless scheduler tạo/chạy/quản lý task tập trung; hỗ trợ **cron & rate expression** cho pattern lặp lại, hoặc **one-time invocation**; có flexible time window, retry limit, max retention cho invocation lỗi.
- 🧠 Câu bẫy kinh điển: **"chạy `Lambda`/task theo lịch định kỳ"** → `EventBridge` rule schedule (`cron`/`rate`) hoặc EventBridge Scheduler — KHÔNG tự viết cron trong Lambda.
- Kết hợp thường gặp: **pipe → event bus → nhiều target** (fan-out).

---

## 📄 Nội dung (trích từ tài liệu gốc)

# What Is Amazon EventBridge?

EventBridge is a serverless service that uses events to connect application components together, making it easier for you to build scalable event-driven applications. Event-driven architecture is a style of building loosely-coupled software systems that work together by emitting and responding to events. Event-driven architecture can help you boost agility and build reliable, scalable applications.

EventBridge provides simple and consistent ways to ingest, filter, transform, and deliver events so you can build applications quickly.

EventBridge includes two ways to process and deliver events: *event buses* and *pipes*.

+ **Event buses** are routers that receive events and delivers them to zero or more targets. Use EventBridge to route events from sources such as home-grown applications, AWS services, and third-party software to consumer applications across your organization. Event buses are well-suited for routing events from many sources to many targets, with optional transformation of events prior to delivery to a target.

+ **Pipes** – EventBridge Pipes is intended for point-to-point integrations; each pipe receives events from a single source for processing and delivery to a single target. Pipes also include support for advanced transformations and enrichment of events prior to delivery to a target.

  Pipes and event buses are often used together. A common use case is to create a pipe with an event bus as its target; the pipe sends events to the event bus, which then sends those events on to multiple targets. For example, you could create a pipe with a DynamoDB stream for a source, and an event bus as the target. The pipe receives events from the DynamoDB stream and sends them to the event bus, which then sends them on to multiple targets according to the rules you've specified on the event bus.

In addition, EventBridge provides **EventBridge Scheduler**, a serverless scheduler that allows you to create, run, and manage tasks from one central, managed service. With EventBridge Scheduler, you can create schedules using cron and rate expressions for recurring patterns, or configure one-time invocations. You can set up flexible time windows for delivery, define retry limits, and set the maximum retention time for failed API invocations.

*(EventBridge provides multiple ways to process and deliver events: buses, pipes, and schedules.)*

## Sign up for an AWS account

To get started with AWS, you need an AWS account. For information about creating an AWS account, see Getting started with an AWS account in the AWS Account Management Reference Guide.
