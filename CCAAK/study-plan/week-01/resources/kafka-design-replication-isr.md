# Apache Kafka — Design: Replication, ISR, committed, leader election (góc nhìn vận hành)

> **Nguồn (official):** https://kafka.apache.org/43/design/design/ (mục *Replication*)
> **Tuần:** 1 — Nền tảng vận hành + `KRaft` in production · **Loại:** Apache Kafka Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- Mỗi partition có **1 leader và 0..n follower**. **Mọi ghi đi qua leader**; đọc có thể từ leader hoặc (nếu bật follower fetching, KIP-392) từ replica gần nhất. Follower kéo dữ liệu từ leader **y như một consumer**.
- **ISR = tập replica đang bắt kịp.** Một replica ở trong ISR khi thoả **cả hai**: (1) còn phiên hoạt động với controller qua heartbeat, (2) không tụt quá `replica.lag.time.max.ms` (**30000 ms**) so với leader. Hỏng một trong hai → bị **đẩy khỏi ISR**.
- **"Committed" = mọi replica trong ISR đã nhận record.** Chỉ record đã committed mới được consumer nhìn thấy → **high watermark** chính là ranh giới này. Đây là lý do consumer **không bao giờ** đọc được dữ liệu có nguy cơ biến mất.
- **f+1 replica chịu được f lỗi** mà không mất dữ liệu đã committed. Kafka dùng **cách tiếp cận ISR**, không phải bỏ phiếu đa số: **bất kỳ** thành viên ISR nào cũng đủ điều kiện làm leader. Đổi lại ít overhead hơn quorum-vote. *(Trái ngược với `__cluster_metadata`, vốn dùng Raft — tức là đa số. Hai mặt phẳng, hai luật khác nhau: nhớ kỹ chỗ này.)*
- **Mất toàn bộ replica** thì Kafka đứng trước hai lựa chọn: chờ một replica trong ISR quay lại (mất availability) hay bầu một replica **ngoài ISR** (mất dữ liệu). Mặc định `unclean.leader.election.enable=false` → **chờ**, ưu tiên nhất quán. Bật unclean election là **hành động cuối cùng**, phải được người có thẩm quyền quyết định, không phải phản xạ khi thấy partition offline.
- `acks` = `0` / `1` / `all` (`-1`). Với `acks=all`, broker chỉ ack khi **mọi thành viên ISR hiện tại** đã nhận. `min.insync.replicas` là **sàn** cho kích thước ISR: ISR tụt dưới sàn → ghi `acks=all` bị từ chối bằng `NotEnoughReplicasException`.
- Bộ ba production: **RF 3 + `min.insync.replicas` 2 + `acks=all`** → chịu mất **1 broker** mà vẫn ghi được và không mất dữ liệu. Đặt `min.insync.replicas=3` với RF 3 là **over-correction**: mất 1 broker là ngừng ghi ngay.
- Điểm dễ nhầm ở góc admin: `min.insync.replicas` **chỉ có răng** khi producer dùng `acks=all`. Producer `acks=1` vẫn ghi được khi ISR = 1 — nghĩa là đổi `min.insync.replicas` không "bảo vệ" được ứng dụng đang dùng `acks=1`.

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Core Replication Model

Kafka replicates topic partitions across multiple servers with a configurable replication factor. Each partition has one leader and zero or more followers. The leader handles all writes; reads can come from either. Followers pull messages from the leader like regular consumers and apply them to their own logs.

### In-Sync Replicas (ISR)

The system maintains a dynamic set called the "in-sync replicas" (ISR) containing replicas caught up to the leader. A replica remains in the ISR if it:

1. Maintains an active session with the controller via periodic heartbeats
2. Doesn't fall too far behind the leader (controlled by `replica.lag.time.max.ms`)

If either condition fails, the broker is removed from the ISR.

### Message Commitment

A write is "committed" only when all in-sync replicas have received it. Once committed, the message won't be lost provided at least one ISR member survives. Consumers only receive committed messages.

### Leader Election and Quorum

Kafka uses an ISR-based approach rather than majority voting. With `f+1` replicas, the system tolerates `f` failures without losing committed data. Any ISR member is eligible for leader election — this differs from majority quorum approaches where election requires consensus from a majority.

The ISR approach trades slightly lower latency consistency (compared to majority vote) for better throughput and lower replication overhead.

### Unclean Leader Election

If all replicas die, Kafka must choose between:

- Waiting for an ISR replica (risking permanent unavailability)
- Electing a non-ISR replica (risking data loss)

By default, Kafka waits for consistency. The `unclean.leader.election.enable` configuration allows changing this behavior when uptime matters more than consistency.

### Durability Guarantees

Producers can request acknowledgment from 0, 1, or all (−1) replicas via the `acks` setting. When `acks=all`, acknowledgment requires all current ISR members to receive the message.

The `min.insync.replicas` setting ensures messages are written to a minimum number of replicas before acknowledgment, preventing loss if the remaining replica fails.

---

### 🔗 Đối chiếu nhanh: hai mặt phẳng, hai cơ chế nhất quán

| | Data plane (`orders-0`, `__consumer_offsets-17`…) | Control plane (`__cluster_metadata-0`) |
|---|---|---|
| Giao thức | **ISR replication** | **Raft** (KRaft) |
| Ai được làm leader | Bất kỳ replica nào **trong ISR** | Ứng viên có log **≥** log của người bỏ phiếu, và phải thắng **đa số** |
| Chịu lỗi | RF `f+1` chịu `f` lỗi | `2N+1` voter chịu `N` lỗi |
| Đồng hồ phát hiện lỗi | `replica.lag.time.max.ms` **30000** | `controller.quorum.fetch.timeout.ms` **2000** |
| Ranh giới "đã an toàn" | **High watermark** | **HighWatermark** của metadata log |
| Hậu quả khi mất đa số | Không có khái niệm đa số ở đây | Mất **control plane**: không bầu được leader mới, không đổi được metadata |

> 📌 Bảng trên là tổng hợp từ hai trang docs (Design → Replication và Operations → KRaft), không phải một đoạn nguyên văn trong tài liệu gốc.
