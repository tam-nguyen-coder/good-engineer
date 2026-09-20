# Apache Kafka — KRaft Operations: `process.roles`, quorum sizing, storage format, membership changes

> **Nguồn (official):** https://kafka.apache.org/43/operations/kraft/ · https://docs.confluent.io/platform/current/kafka-metadata/config-kraft.html
> **Tuần:** 1 — Nền tảng vận hành + `KRaft` in production · **Loại:** Apache Kafka Docs + Confluent Platform Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- `process.roles` nhận **3 giá trị**: `broker`, `controller`, `broker,controller`. Cái thứ ba là **combined mode** — docs Apache nói "simpler to operate for small use cases like a development environment" nhưng **"not recommended in critical deployment environments"**; Confluent nói thẳng hơn: *"Combined mode is for local experimentation only and is not supported by Confluent"*. **Đề CCAAK luôn chọn tách riêng cho production.**
- Lý do kỹ thuật của việc tách: combined mode **không thể roll hoặc scale controller độc lập với broker**, và controller **kém cách ly** khỏi tải data plane (page cache, GC, disk I/O của broker ảnh hưởng trực tiếp tới metadata).
- Quorum **3 hoặc 5** controller. Công thức: **2N+1 controller chịu được N lỗi đồng thời** → 3 chịu **1**, 5 chịu **2**. **Phải còn đa số (majority) sống** thì quorum mới hoạt động. Số chẵn (4) không cho thêm khả năng chịu lỗi so với 3 — chỉ tốn máy.
- **Static quorum** = `controller.quorum.voters=id@host:port,...` — mọi node (kể cả broker-only) liệt kê **đầy đủ** danh sách; đổi thành viên phải sửa config và **restart toàn bộ**.
- **Dynamic quorum** (KIP-853, feature `kraft.version=1`) = `controller.quorum.bootstrap.servers=host:port,...` — chỉ cần **địa chỉ đủ để khám phá**, thêm/bớt controller **lúc đang chạy**. Kiểm tra đang dùng loại nào: `kafka-features.sh --bootstrap-controller localhost:9093 describe` → `kraft.version` có `FinalizedVersionLevel: 0` nghĩa là **static**, `1` là **dynamic**.
- **Format storage là bắt buộc trước khi start**: `kafka-storage.sh random-uuid` sinh `cluster.id`; `format --cluster-id <ID> --config <file>` kèm **đúng một** trong ba cờ: `--standalone` (controller đầu tiên, voter duy nhất), `--initial-controllers "id@host:port:dirUUID,..."` (format đồng loạt cả quorum), `--no-initial-controllers` (broker và controller **gia nhập sau** vào quorum sẵn có).
- **Mọi node trong cùng cluster phải format bằng CÙNG `cluster.id`.** Sai → node không join được, ném `InconsistentClusterIdException`. `format` ghi `meta.properties` (chứa `cluster.id`, `node.id`, `directory.id` ngẫu nhiên).
- Thêm/bớt controller khi dùng dynamic quorum: `kafka-metadata-quorum.sh --bootstrap-server ... add-controller` (**sau khi** controller mới đã bắt kịp log) và `kafka-metadata-quorum.sh --bootstrap-controller ... remove-controller --controller-id <id> --controller-directory-id <uuid>` (**trước khi** tắt máy).
- 3 công cụ soi metadata: `kafka-metadata-quorum.sh describe --status` (ClusterId / LeaderId / LeaderEpoch / HighWatermark / MaxFollowerLag / CurrentVoters / CurrentObservers), `describe --replication` (từng node: LogEndOffset, Lag, Status = Leader/Follower/Observer), và `kafka-dump-log.sh --cluster-metadata-decoder --files .../__cluster_metadata-0/*.log` để đọc từng metadata record.
- `kafka-metadata-shell.sh --snapshot .../__cluster_metadata-0/<offset>-<epoch>.checkpoint` duyệt snapshot như một filesystem. **Không** dùng file `00000000000000000000-0000000000.checkpoint` (không phải snapshot hợp lệ).
- Tài nguyên khuyến nghị cho controller: **~5 GB RAM và ~5 GB đĩa** cho metadata log directory ở một cluster Kafka điển hình — controller **rất nhẹ**, đó là lý do tách riêng không tốn kém như người ta tưởng.
- Migration ZooKeeper → KRaft **phải qua bridge release**; "the last bridge release is **Kafka 3.9**". Từ **4.0** không còn ZooKeeper mode — mọi đáp án nhắc `zookeeper.connect` đều sai với cluster 4.x.

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Process Roles

The `process.roles` property defines each server's function:

- **`broker`**: Server acts as a broker only
- **`controller`**: Server acts as a controller only
- **`broker,controller`**: Server acts as both (combined mode)

"Combined servers are simpler to operate for small use cases like a development environment. The key disadvantage is that the controller will be less isolated from the rest of the system." Controllers cannot be rolled or scaled separately from brokers in combined mode, making it unsuitable for critical production deployments.

Confluent Platform documentation states: "Combined mode is for local experimentation only and is not supported by Confluent."

### Controller Quorum Sizing

"A Kafka admin will typically select 3 or 5 servers for this role, depending on factors like cost and the number of concurrent failures your system should withstand without availability impact."

- **3 controllers**: tolerates 1 concurrent failure
- **5 controllers**: tolerates 2 concurrent failures

"A majority of the controllers must be alive in order to maintain availability."

Confluent adds: a production deployment requires "at least three (3) KRaft controllers in production". The quorum follows a `2n + 1` structure, allowing the cluster to tolerate up to `n` simultaneous controller failures. If the controller majority is lost, the cluster can no longer perform metadata operations.

### Static vs. Dynamic Quorum Configuration

**Dynamic quorum** (recommended for new clusters) uses `controller.quorum.bootstrap.servers`:

```
controller.quorum.bootstrap.servers=controller1.example.com:9093,controller2.example.com:9093,controller3.example.com:9093
```

- Lists enough controllers for discovery without requiring complete enumeration
- Supports runtime controller modifications
- Managed through the KRaft version feature level (`kraft.version`)

**Static quorum** uses `controller.quorum.voters`:

- Explicitly lists all controller IDs, hosts, and ports in the form `id@host:port`
- Requires updating and restarting all nodes to modify the controller set

Determine the current configuration via:

```bash
bin/kafka-features.sh --bootstrap-controller localhost:9093 describe
```

If `kraft.version` shows `FinalizedVersionLevel: 0`, the cluster is using a static quorum.

### Node Provisioning

Generate the cluster ID:

```bash
bin/kafka-storage.sh random-uuid
```

Bootstrap a standalone controller:

```bash
bin/kafka-storage.sh format --cluster-id <CLUSTER_ID> --standalone --config config/controller.properties
```

This creates `meta.properties` with a random `directory.id`, plus control records in the bootstrap snapshot file.

Bootstrap multiple controllers at once:

```bash
CLUSTER_ID="$(bin/kafka-storage.sh random-uuid)"
CONTROLLER_0_UUID="$(bin/kafka-storage.sh random-uuid)"

bin/kafka-storage.sh format --cluster-id ${CLUSTER_ID} \
  --initial-controllers "0@controller-0:1234:${CONTROLLER_0_UUID},..." \
  --config config/controller.properties
```

Format brokers (and controllers joining an existing cluster):

```bash
bin/kafka-storage.sh format --cluster-id <CLUSTER_ID> --config config/server.properties --no-initial-controllers
```

### Controller Membership Changes

Add a new controller (dynamic quorum only):

```bash
bin/kafka-metadata-quorum.sh --bootstrap-server localhost:9092 add-controller
```

Monitor replication progress:

```bash
bin/kafka-metadata-quorum.sh describe --replication
```

Remove a controller:

```bash
bin/kafka-metadata-quorum.sh --bootstrap-controller localhost:9093 remove-controller \
  --controller-id <id> --controller-directory-id <directory-id>
```

### Debugging Tools

Metadata quorum status:

```bash
bin/kafka-metadata-quorum.sh --bootstrap-server localhost:9092 describe --status
```

Sample output shows `ClusterId`, `LeaderId`, `LeaderEpoch`, `HighWatermark`, `MaxFollowerLag`, `MaxFollowerLagTimeMs`, `CurrentVoters` and `CurrentObservers`.

Dump metadata log segments:

```bash
bin/kafka-dump-log.sh --cluster-metadata-decoder \
  --files metadata_log_dir/__cluster_metadata-0/00000000000000000000.log
```

Dump metadata snapshots:

```bash
bin/kafka-dump-log.sh --cluster-metadata-decoder \
  --files metadata_log_dir/__cluster_metadata-0/00000000000000000100-0000000001.checkpoint
```

Metadata shell (interactive inspection):

```bash
bin/kafka-metadata-shell.sh \
  --snapshot metadata_log_dir/__cluster_metadata-0/00000000000000007228-0000000001.checkpoint
```

**Note**: do not use `00000000000000000000-0000000000.checkpoint` with the metadata shell — use valid snapshot files.

### Deployment Recommendations

- **Role separation**: set `process.roles` to either `broker` or `controller`, not both, in production
- **Controller count**: use 3+ controllers for redundancy; to tolerate N concurrent failures, deploy 2N+1 controllers
- **Resource allocation**: "For a typical Kafka cluster 5GB of main memory and 5GB of disk space on the metadata log directory is sufficient"

### Upgrade Path

For ZooKeeper to KRaft migration, "the last bridge release is Kafka 3.9", with detailed steps available in the 3.9 documentation. Kafka 4.x no longer supports ZooKeeper mode at all.
