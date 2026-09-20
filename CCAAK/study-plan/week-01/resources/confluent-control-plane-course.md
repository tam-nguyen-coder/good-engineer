# Confluent Developer — Apache Kafka Architecture: The Control Plane (`KRaft`)

> **Nguồn (official):** https://developer.confluent.io/courses/architecture/control-plane/
> **Tuần:** 1 — Nền tảng vận hành + `KRaft` in production · **Loại:** Confluent Developer course (free)
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- **Ba vai trong control plane**: **active controller** (leader của partition duy nhất của `__cluster_metadata`), **standby controller** (replica **follower**, có quyền bỏ phiếu), **broker** (replica **observer** — fetch metadata nhưng **không bỏ phiếu**). Ba từ Leader / Follower / Observer chính là cột `Status` trong `kafka-metadata-quorum.sh describe --replication`.
- `__cluster_metadata` là **topic nội bộ 1 partition**. Đề hay bẫy bằng "bao nhiêu partition" — đáp án là **1**, khác hẳn `__consumer_offsets` (**50**) và `__transaction_state` (**50**).
- **Mọi controller giữ metadata cache trong bộ nhớ và luôn được cập nhật** → failover gần như tức thời, không phải nạp lại state như thời ZooKeeper. Đây là câu trả lời cho "vì sao KRaft failover nhanh".
- **Broker chủ động kéo (fetch) metadata**, controller **không** broadcast. Cách này "very efficient to keep all the controllers and brokers in sync, and also shortens restart times".
- **Bầu cử trong quorum không dùng ISR** mà dùng Raft: ứng viên tăng **epoch** và gửi `VoteRequest` kèm **offset cuối cùng + epoch của offset đó**; follower chỉ bỏ phiếu nếu log của ứng viên **bằng hoặc mới hơn** log của mình; thắng rồi thì gửi `BeginQuorumEpoch`. → **Không bao giờ bầu được một controller có log cũ hơn** — đó là điều bảo đảm metadata không bị lùi.
- **Snapshot**: controller và broker định kỳ "take a snapshot of their in-memory metadata cache" → cắt bớt log mà vẫn khôi phục được đầy đủ state bằng **snapshot + phần log còn lại**. Đây là lý do `metadata.max.retention.bytes` chỉ 100 MiB mà không mất dữ liệu.
- KRaft đạt production-ready từ **Kafka 3.3.1 (10/2022)**; Confluent nêu mức cải thiện scale khoảng **10×** và "more efficient metadata propagation".
- ⚠️ **Trang này KHÔNG nói gì về việc mất quorum thì data plane ra sao.** Xem ghi chú ở cuối file — đây là điểm phải tự chứng minh bằng Lab 1.3.

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Overview

KRaft (released October 2022 with Kafka 3.3.1) eliminates the ZooKeeper dependency by embedding consensus mechanisms directly into Kafka. The system "stores all cluster metadata in Kafka topics and manages" them internally.

### Active controller vs. standby controllers

One controller becomes the active leader handling metadata changes. "All of the controller brokers maintain an in-memory metadata cache that is kept up to date", enabling rapid failover without metadata refresh delays — a significant efficiency gain over ZooKeeper's architecture.

### The `__cluster_metadata` topic

This internal single-partition topic persists all cluster state. "The active controller is the leader of this internal metadata topic's single partition. Other controllers are replica followers. Brokers are replica observers."

### Broker metadata observation

Rather than controllers broadcasting changes, brokers proactively fetch metadata updates from the topic, making "it very efficient to keep all the controllers and brokers in sync, and also shortens restart times."

### Leader election process

Controllers use quorum-based election without ISR concepts:

- **VoteRequest** — candidates increment the epoch and send requests including "the candidate's last offset and the epoch associated with that offset"
- **Vote response** — followers grant votes if the candidate's log is "the same or higher than its own"
- **Completion** — the new leader sends a `BeginQuorumEpoch` notification

### Snapshots

Periodically, controllers and brokers "take a snapshot of their in-memory metadata cache", enabling log truncation while preserving complete cluster state through the snapshot plus the remainder of the log.

### Differences from ZooKeeper

KRaft provides "simpler deployment and administration", improved scalability (10x gains), and "more efficient metadata propagation" through log-based, event-driven mechanisms.

---

### ⚖️ Ghi chú kiểm chứng — "mất quorum thì chuyện gì xảy ra?"

Trang course này **không** trả lời câu hỏi đó. Các nguồn chính thức nói như sau:

| Nguồn | Câu chữ | Suy ra được gì |
|---|---|---|
| kafka.apache.org/43/operations/kraft/ | "A majority of the controllers must be alive in order to maintain availability." | Mất đa số → quorum **không** hoạt động |
| docs.confluent.io … config-kraft | "If the controller majority is lost, the cluster becomes unavailable." | Câu này nói ở mức **quản trị cluster** |
| developer.confluent.io … control-plane | Broker giữ **metadata cache trong bộ nhớ**, tự fetch từ log | Broker **không cần** controller để phục vụ một partition mà leader không đổi |

**Kết luận dùng cho đề (và cho Lab 1.3):** mất đa số quorum thì **control plane đóng băng** — không bầu được leader mới, không tạo/xoá topic, không đổi config, không đăng ký broker mới. **Data plane vẫn phục vụ produce/consume** cho những partition mà leader **không thay đổi**, vì broker đọc từ metadata đã cache. Nhưng đây là **trạng thái vá víu, không phải trạng thái ổn định**: chỉ cần thêm một broker chết là partition của nó **không có ai bầu leader mới** → offline thật sự. Không có câu docs nào nói nguyên văn điều này, nên Lab 1.3 tồn tại để bạn **tự nhìn thấy** nó.
