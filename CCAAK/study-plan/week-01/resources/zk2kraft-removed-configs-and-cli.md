# Apache Kafka — ZooKeeper → KRaft: config bị gỡ, CLI đổi, metric biến mất

> **Nguồn (official):** https://kafka.apache.org/43/getting-started/zk2kraft/
> **Tuần:** 1 — Nền tảng vận hành + `KRaft` in production · **Loại:** Apache Kafka Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- **Đây là trang chống-lỗi-thời quan trọng nhất của Tuần 1.** Hai kho câu hỏi CCAAK công khai lớn nhất còn nhắc ZooKeeper nhiều gấp ~40 lần KRaft. Học thuộc bảng ánh xạ ở dưới là cách rẻ nhất để không mất điểm.
- **Toàn bộ `zookeeper.*` bị gỡ** — `zookeeper.connect`, `zookeeper.session.timeout.ms`, `zookeeper.connection.timeout.ms`, cùng mọi config SSL/TLS của ZooKeeper. Phương án nào nhắc tới chúng với cluster 4.x đều sai.
- `broker.id.generation.enable` và `reserved.broker.max.id` bị gỡ → định danh node giờ là **`node.id`**, do người vận hành đặt tay, **không** tự sinh.
- `inter.broker.protocol.version` bị gỡ → thay bằng **`metadata.version`**, và nó được nâng bằng **`kafka-features.sh`** chứ không phải bằng cách sửa file config rồi restart. Đây là thay đổi lớn nhất với quy trình **rolling upgrade**.
- `control.plane.listener.name` bị gỡ → thay bằng **`controller.listener.names`** cùng `listeners` và `listener.security.protocol.map`.
- `controlled.shutdown.max.retries` và `controlled.shutdown.retry.backoff.ms` bị gỡ (quorum controller lo việc này). **`controlled.shutdown.enable` thì VẪN CÒN** và vẫn mặc định `true` — đừng nhầm cả cụm.
- Mọi `password.encoder.*` bị gỡ: KRaft không mã hoá secret trong config theo kiểu cũ nữa.
- **`advertised.listeners` không còn cập nhật động được** trong KRaft → đổi nó là phải **restart broker**. Bẫy đề: "sửa advertised listener mà không restart broker" → không có cách nào.
- Muốn chỉnh log level (hoặc bất kỳ config nào) **của controller**, phải gõ `--bootstrap-controller localhost:9093`, không phải `--bootstrap-server`. `entity-type` vẫn là `broker-loggers`.
- Plugin policy (`CreateTopicPolicy`, `AlterConfigPolicy`) giờ chạy **trên controller** → JAR phải được nạp ở controller, không phải broker. Bẫy vận hành thật sự: deploy policy lên broker rồi ngạc nhiên vì nó không có tác dụng.
- `KafkaPrincipalBuilder` tự viết bắt buộc phải implement thêm **`KafkaPrincipalSerde`** (vì principal phải được tuần tự hoá để gửi qua metadata/forwarding).

### 🗺️ Bảng ánh xạ ZooKeeper → KRaft (học thuộc)

| Thế giới ZooKeeper (≤ 3.9) | Thế giới KRaft (4.x) |
|---|---|
| znode trong ZooKeeper | **metadata record** trong `__cluster_metadata` |
| Ephemeral node `/controller` bầu controller | **Bầu leader bằng Raft** trong controller quorum |
| Controller đọc toàn bộ state từ ZooKeeper khi failover | Controller mới **đã có sẵn** log đã replicate → failover gần như tức thời |
| Broker đăng ký bằng ephemeral node `/brokers/ids/<id>` | Broker **đăng ký + heartbeat** với controller; controller có thể **fence** broker |
| `--zookeeper` trên CLI | **`--bootstrap-server`** (hoặc `--bootstrap-controller` cho controller) |
| ACL lưu trong znode, ZK authorizer | ACL lưu trong **metadata log**, `StandardAuthorizer` |
| `zookeeper.connect` | `controller.quorum.bootstrap.servers` / `controller.quorum.voters` |
| `broker.id` (+ tự sinh) | `node.id` (đặt tay, bắt buộc) |
| `inter.broker.protocol.version` trong file config | `metadata.version` nâng bằng `kafka-features.sh` |
| `control.plane.listener.name` | `controller.listener.names` |
| Giới hạn kích thước znode, số watcher | Giới hạn theo **log + snapshot**, scale tốt hơn nhiều |

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Configuration Removals

**Password encryption** — "Removed password encoder-related configurations", including `password.encoder.secret`, `password.encoder.old.secret` and related algorithm/key parameters. KRaft stores sensitive data differently, without encrypting it inside Kafka itself.

**Control plane** — the `control.plane.listener.name` configuration was removed. Instead, use `controller.listener.names`, `listeners` and `listener.security.protocol.map` to configure controller communication over the integrated Raft protocol.

**Broker management** — graceful-shutdown retry configs (`controlled.shutdown.max.retries`, `controlled.shutdown.retry.backoff.ms`) were eliminated. KRaft's quorum-based controller handles shutdowns.

**Broker identification** — `reserved.broker.max.id` and `broker.id.generation.enable` were removed; KRaft uses `node.id` instead.

**Protocol versioning** — `inter.broker.protocol.version` was replaced by `metadata.version`, managed via `kafka-features.sh`.

**Dynamic configuration removal** — `advertised.listeners` no longer supports dynamic updates in KRaft mode.

**ZooKeeper specifics** — all `zookeeper.*` configurations were removed, including connection settings, SSL/TLS parameters and session management.

### CLI Tool Changes

Dynamic log levels use a different syntax for controllers: use `--bootstrap-controller localhost:9093` instead of `--bootstrap-server` when targeting controllers, though the entity type remains `broker-loggers`.

### Metrics Removed

Numerous controller and ZooKeeper-specific metrics were eliminated, including `ControlPlaneNetworkProcessorAvgIdlePercent`, `ControlPlaneExpiredConnectionsKilledCount`, and extensive controller statistics tracking leader elections, ISR changes and ZooKeeper migration state.

### Behavioral Changes

- Configuration values are limited to `Short.MAX_VALUE` in KRaft
- Policy plugins (`CreateTopicPolicy`, `AlterConfigPolicy`) now run on controllers, requiring the JAR to be deployed there
- Custom `KafkaPrincipalBuilder` implementations must also implement `KafkaPrincipalSerde`

> 📌 Bảng ánh xạ ở phần *Điểm thi quan trọng* là tổng hợp từ trang này cộng với https://kafka.apache.org/43/operations/kraft/ và blog KIP-500 — không phải một bảng nguyên văn trong tài liệu gốc.
