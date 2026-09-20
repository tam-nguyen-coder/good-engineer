# Confluent Platform — Log của broker, đổi log level lúc chạy, và rolling restart

> **Nguồn (official):** https://docs.confluent.io/platform/current/kafka/post-deployment.html
> **Tuần:** 7 — Observability + Troubleshooting playbook · **Loại:** Confluent Platform Docs (Post-Deployment / Kafka Operations)
> ⚠️ Nội dung dưới đây được crawl tự động (HTTP → Markdown, có rút gọn) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất. Phần `broker-loggers` bổ sung từ Apache Kafka docs (đã đánh dấu).

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- **Vị trí log phụ thuộc cách cài:** RPM/Debian → `/var/log/kafka`; ZIP/TAR → `$base_dir/logs`. **Đừng nhầm với `log.dirs`** — `log.dirs` là nơi chứa **dữ liệu partition**, không phải log ứng dụng. Đây là bẫy chữ nghĩa xuất hiện trong đề.
- **Log level mặc định là `INFO`** — *"designed to be light so that your logs do not grow too big"*. Muốn debug thì **nâng level tạm thời**, không để vĩnh viễn.
- **4 file log cần biết:**
  - `server.log` — hoạt động chung của broker.
  - `controller.log` — hoạt động của controller. *"Any `ERROR`, `FATAL` or `WARN` in this log indicates an important event that should be looked at by the administrator."*
  - `state-change.log` — *"When the state of any resource is changed by the controller, it logs the action to a special state change log"*; mặc định level **TRACE**. Đây là file đọc khi truy vết **leader election / ISR thay đổi**.
  - `kafka-authorizer.log` — quyết định ACL (DENIED ở INFO, ALLOWED phải bật DEBUG).
- **Request logger** ghi **mọi** request broker phục vụ, kèm latency và nội dung request ở DEBUG/TRACE — cực nặng, chỉ bật vài chục giây.
- **Rolling restart đúng thứ tự** (docs liệt kê 7 bước): kiểm tra cluster khoẻ & **không còn URP** → xác định broker nào đang là active controller → **tắt mềm** (không `kill -9`) → cập nhật → khởi động → **chờ broker bắt kịp** → mới sang broker kế tiếp; **restart active controller sau cùng**.
- **Broker mới không tự nhận partition:** *"these new servers will not automatically be assigned any data partitions"* → phải dùng `kafka-reassign-partitions.sh` (hoặc confluent-rebalancer).

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Logging

The location the logs are written depends on the packaging format. For example, `kafka_logs_dir` will be in `/var/log/kafka` in a RPM/Debian installation and `$base_dir/logs` for a ZIP/TAR installation.

The default logging level is `INFO`. It provides a moderate amount of information, but is designed to be light so that your logs do not grow too big.

When debugging problems, particularly problems with replicas, it can be helpful to raise the logging level to `DEBUG`.

#### Controller log

The controller in a Kafka cluster is responsible for managing partition leaders and replication. The controller logs its activity to `logs/controller.log`. Any `ERROR`, `FATAL` or `WARN` in this log indicates an important event that should be looked at by the administrator.

#### State change log

When the state of any resource is changed by the controller, it logs the action to a special state change log located at `logs/state-change.log`. The default log level of this log is TRACE. This log is useful when tracing which replica became the leader for a partition and when.

#### Request logger

Kafka has the facility to log every request served by the broker. This is turned off by default. At the `DEBUG` level it shows the latency information of each request, and at `TRACE` level it also shows the contents of the request. Because this logger is very verbose it should only be enabled for short periods.

### Rolling restart

To perform a rolling restart with no downtime for end users:

1. Verify that the cluster is healthy and there are no under-replicated partitions.
2. Determine which broker is the active controller.
3. Stop one broker gracefully — do not use `kill -9`, because a controlled shutdown syncs the logs and moves leadership away first.
4. Apply the configuration change or software update.
5. Restart the broker.
6. Wait for the broker to catch up — the under-replicated partition count must return to zero — before touching the next broker.
7. Restart the active controller last.

This approach provides high availability by avoiding downtime for end users.

### Adding and removing brokers

Adding brokers to a cluster is straightforward, but these new servers will not automatically be assigned any data partitions. Use a rebalancing tool such as `confluent-rebalancer` or `kafka-reassign-partitions` to move existing partitions onto the new brokers.

When removing a broker, first move all of its partitions to other brokers with a reassignment, verify the reassignment completed, and only then shut the broker down.

---

### Bổ sung — đổi log level lúc chạy không restart

> 📌 *(Không crawl được nguyên văn — tổng hợp từ mục **Dynamic Broker Configs → Updating Log Level Configs** của https://kafka.apache.org/43/configuration/broker-configs/ và **KIP-412**. Kiểm chứng bằng chính lệnh `--describe` bên dưới trên cluster lab.)*

Kafka exposes each broker's loggers as a dynamic config entity, so levels can be changed at runtime:

```bash
# Xem toàn bộ logger và level hiện tại của broker id 2
$ bin/kafka-configs.sh --bootstrap-server localhost:9092 \
    --describe --entity-type broker-loggers --entity-name 2

# Nâng một logger lên DEBUG (có hiệu lực ngay, KHÔNG restart)
$ bin/kafka-configs.sh --bootstrap-server localhost:9092 \
    --alter --entity-type broker-loggers --entity-name 2 \
    --add-config kafka.request.logger=DEBUG

# Trả về mặc định khi xong
$ bin/kafka-configs.sh --bootstrap-server localhost:9092 \
    --alter --entity-type broker-loggers --entity-name 2 \
    --delete-config kafka.request.logger
```

Note: `broker-loggers` changes are **not persisted** across a broker restart — the broker falls back to the level in `log4j2.yaml`. Kafka 4.0 replaced log4j 1.x with **Log4j2** (`config/log4j2.yaml`).
