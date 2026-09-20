# KIP-500 (bỏ ZooKeeper) & KIP-853 (dynamic controller quorum)

> **Nguồn (official):** https://cwiki.apache.org/confluence/display/KAFKA/KIP-500 · https://cwiki.apache.org/confluence/display/KAFKA/KIP-853
> **Nguồn crawl được:** https://www.confluent.io/blog/why-replace-zookeeper-with-kafka-raft-the-log-of-all-logs/ · https://developer.confluent.io/learn/kraft/ · https://kafka.apache.org/43/operations/kraft/
> **Tuần:** 1 — Nền tảng vận hành + `KRaft` in production · **Loại:** KIP + blog kỹ thuật
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.
> ⚠️ **Hai trang `cwiki.apache.org` không crawl được** (WebFetch trả về rỗng ở cả hai lần thử). Phần KIP-853 bên dưới **tổng hợp từ docs Apache 4.3 + Confluent Platform docs**, không phải trích nguyên văn KIP.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- **Vấn đề gốc của ZooKeeper không phải là "chậm", mà là "hai hệ thống".** Metadata là source of truth trong ZooKeeper, nhưng controller lại giữ một bản cache, và **broker khác cũng nói chuyện trực tiếp với ZooKeeper** → **metadata phân kỳ** (divergence). Vận hành phải biết tune, backup, bảo mật **hai** hệ thống với hai mô hình khác nhau.
- **Ba nút thắt scale** mà đề hay hỏi ở dạng "vì sao KRaft nhanh hơn":
  1. **Broker shutdown**: controller phải ghi metadata mới vào ZooKeeper cho **từng partition** broker đó giữ, rồi phát tán → hàng nghìn partition thì mất "seconds or even more".
  2. **Controller failover**: controller mới phải **nạp toàn bộ** metadata partition từ ZooKeeper — **tuyến tính theo số partition** → "a long unavailability window".
  3. **Metadata propagation**: mọi thay đổi giữa controller và broker đều tuyến tính theo số partition liên quan.
- **Ý tưởng cốt lõi của KRaft**: sau lưng API của ZooKeeper thì dữ liệu ghi vẫn được lưu dưới dạng **transaction log**. Vậy thì lưu thẳng **metadata log** trong Kafka — thứ Kafka vốn giỏi nhất. Thao tác tự nhiên có **thứ tự theo offset** và **gom lô** được.
- **Event-sourced**: broker **replicate changelog** thay vì nhận RPC cập nhật → "each broker's locally materialized view of the metadata would be eventually consistent as they are from the same log, and also versioned at a given time by the offset of the metadata log". Đây là lý do mỗi broker có thể trả lời "tôi đang ở metadata offset bao nhiêu".
- **Quorum controller**: một nhóm nhỏ node dùng Raft giữ metadata log. Leader chết → thành viên khác lên leader với "only a very short bootstrap time" vì **đã có sẵn** toàn bộ record đã committed. Không còn màn nạp lại từ đầu.
- Thử nghiệm với **2 triệu partition**: controlled shutdown và uncontrolled failover đều giảm độ trễ rất mạnh so với ZooKeeper.
- **KIP-853 giải bài toán vận hành còn sót lại**: với static quorum, danh sách voter nằm cứng trong `controller.quorum.voters` của **mọi** node → thay một controller hỏng = sửa config khắp nơi + **restart cả cluster**. KIP-853 đưa thành viên quorum vào **chính metadata log**, thêm `directory.id` vào `meta.properties`, và mở feature **`kraft.version`** (0 = static, 1 = dynamic).
- Với `kraft.version=1`: node chỉ cần `controller.quorum.bootstrap.servers` để **khám phá** quorum, còn thành viên thật được đọc từ log; thêm/bớt controller **lúc đang chạy** bằng `kafka-metadata-quorum.sh add-controller` / `remove-controller`.
- Mốc timeline cần nhớ: KRaft **production ready cho cluster mới từ 3.3**; **3.9 là bridge release cuối cùng** để migrate từ ZooKeeper; **4.0 là KRaft-only**.

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Why ZooKeeper Was Replaced with KRaft

*(Confluent engineering blog — "Why ZooKeeper Was Replaced with KRaft: The Log of All Logs")*

#### Metadata management issues

ZooKeeper stored cluster metadata (broker IDs, topic partitions, leader/ISR info) as the source of truth. The controller maintained this data, but "non-controller brokers also talk to ZooKeeper directly from time to time", creating complexity. Clients could write directly to ZooKeeper, introducing potential divergence.

#### Scalability bottlenecks

1. **Broker shutdown** — when a broker shut down, the controller had to write updated metadata to ZooKeeper for each partition it hosted, then propagate changes to remaining brokers. With thousands of partitions, this took "seconds or even more".
2. **Controller failover** — when the controller crashed, the new controller needed to fetch all topic-partition metadata from ZooKeeper, a process linear in partition count. This created "a long unavailability window" before it could handle admin requests.
3. **Metadata propagation** — all changes between controller and brokers were "linear with the number of topic partitions involved".
4. **Additional constraints** — ZooKeeper had size limits on znodes and watcher limits, and required extra validation since "each broker maintains its own metadata view, which can be divergent".

#### The KRaft solution

Instead of ZooKeeper, Kafka stores metadata as an internal log. The insight: "behind the ZooKeeper APIs, all written data is maintained as a transaction log." By maintaining this "metadata log directly", operations become naturally ordered by log offsets and can be batched efficiently.

**Event-sourced architecture** — brokers replicate the metadata changelog rather than receiving RPC updates. This ensures "each broker's locally materialized view of the metadata would be eventually consistent as they are from the same log, and also versioned at a given time by the offset of the metadata log".

**Quorum controller** — a small quorum of servers uses the Raft consensus protocol (KRaft) to manage the metadata log. When the leader controller fails, another quorum member becomes leader with "only a very short bootstrap time", since it already has the replicated metadata log.

#### Performance improvements

Testing with two million partitions showed dramatic reductions:

- **Controlled shutdown**: latency drastically reduced
- **Uncontrolled failover**: latency largely reduced

New controllers avoid bootstrap delays because elected leaders "would already have replicated all of the committed records up to the new epoch".

### KRaft in one sentence

*(developer.confluent.io/learn/kraft)*

KRaft "greatly simplifies Kafka's architecture by consolidating responsibility for metadata into Kafka itself, rather than splitting it between two different systems: ZooKeeper and Kafka." The quorum controller uses "an event-sourced storage model, which ensures that the internal state machines can always be accurately recreated", operating via "an event-based variant of the Raft consensus protocol". "KRaft mode is production ready for new clusters as of Apache Kafka 3.3."

### KIP-853 — dynamic controller quorum *(không crawl được, tổng hợp từ docs)*

**Problem.** With a static quorum, every node in the cluster — brokers included — must list the complete voter set in `controller.quorum.voters` as `id@host:port`. Replacing a failed controller, or growing the quorum from 3 to 5, therefore means editing configuration on every node and restarting them. There is no online membership change.

**Solution.** KIP-853 moves quorum membership **into the metadata log itself**, where it is replicated like any other record, and gates the new behaviour behind a feature flag:

- `kraft.version=0` — static quorum, membership comes from `controller.quorum.voters`.
- `kraft.version=1` — dynamic quorum, membership is stored in the log; nodes use `controller.quorum.bootstrap.servers` purely to *discover* the quorum.

Each voter is identified not only by `node.id` but also by a **`directory.id`**, a UUID written into `meta.properties` when `kafka-storage.sh format` runs. The pair `(node.id, directory.id)` distinguishes "the same controller restarted" from "a new controller reusing an id after its disk was wiped", which is what makes safe online membership change possible.

**Operational surface exposed by the KIP:**

```bash
# format the very first controller as the only voter
bin/kafka-storage.sh format --cluster-id <ID> --standalone --config config/controller.properties

# format a whole quorum at once, with explicit directory ids
bin/kafka-storage.sh format --cluster-id <ID> \
  --initial-controllers "0@controller-0:9093:<dirUUID0>,1@controller-1:9093:<dirUUID1>,2@controller-2:9093:<dirUUID2>" \
  --config config/controller.properties

# format a node that will JOIN an existing quorum (all brokers, and later controllers)
bin/kafka-storage.sh format --cluster-id <ID> --config config/server.properties --no-initial-controllers

# add a controller once it has caught up
bin/kafka-metadata-quorum.sh --bootstrap-server localhost:9092 add-controller

# remove a controller BEFORE shutting the machine down
bin/kafka-metadata-quorum.sh --bootstrap-controller localhost:9093 remove-controller \
  --controller-id 3 --controller-directory-id <dirUUID>

# which mode am I in?
bin/kafka-features.sh --bootstrap-controller localhost:9093 describe   # look at kraft.version
```

**Checking the migration state.** `kafka-features.sh describe` reports `kraft.version` with `FinalizedVersionLevel: 0` for a static quorum and `1` for a dynamic one. A cluster formatted with `--standalone` or `--initial-controllers` on Kafka 4.x starts at `kraft.version=1`; a cluster carried over from an older static configuration stays at `0` until the feature is upgraded.
