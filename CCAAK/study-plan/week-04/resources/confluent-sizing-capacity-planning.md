# Confluent — Sizing & Capacity Planning: broker, partition, disk, RAM, network

> **Nguồn (official):** https://docs.confluent.io/platform/current/kafka/deployment.html (Running Kafka in Production) · https://www.confluent.io/blog/how-choose-number-topics-partitions-kafka-cluster/ (công thức partition)
> **Tuần:** 4 — Deployment Architecture · **Loại:** Confluent Docs + Confluent Engineering Blog
> ⚠️ Nội dung dưới đây được crawl tự động (HTTP → Markdown, có rút gọn) — luôn đối chiếu link gốc để đầy đủ và cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- **Công thức partition:** *"you need to have at least `max(t/p, t/c)` partitions"* — `t` = throughput cần, `p` = throughput **một partition** producer đạt được, `c` = throughput **một partition** consumer xử lý được. Cộng thêm **biên tăng trưởng** vì **không giảm được partition**.
- Thực tế `p` rất cao (*"one can produce at 10s of MB/sec on just a single partition"*) nên **`c` mới là cái chặn** — số partition gần như luôn bị quyết định bởi tốc độ **xử lý** của consumer.
- **Chi phí over-partition, 4 khoản, phải thuộc:**
  1. **File descriptor** — mỗi partition, mỗi segment, mỗi connection đều tốn; blog nêu cluster production chạy *"more than 30 thousand open file handles per broker"*; khuyến nghị FD **≥ 100.000**.
  2. **Thời gian leader election khi broker chết bẩn** — *"1000 partitions ... 5 ms each ... up to 5 seconds"* unavailability.
  3. **Latency end-to-end** — *"replicating 1000 partitions from one broker to another can add about 20 ms latency"*.
  4. **Bộ nhớ client** — *"at least a few tens of KB per partition being produced"*.
- **Trần thực tế:** *"limit the number of partitions per broker to two to four thousand and the total number of partitions in the cluster to low tens of thousand"*. Ứng dụng nhạy latency thì chặt hơn: **`100 × b × r`** partition mỗi broker (`b` = số broker, `r` = RF).
- **Công thức disk:** `throughput ghi (byte/s) × retention (s) × RF × hệ số dự phòng (~1.2)`. Bật **tiered storage** thì phần **local** chỉ còn `log.local.retention.ms` (mặc định **-2** = dùng `retention.ms`), phần dài hạn nằm ở remote tier → disk broker nhỏ đi rất nhiều.
- **RAM: heap ≤ 6 GB, phần còn lại để page cache.** Docs: *"Kafka uses heap space very carefully and does not require setting heap sizes more than 6 GB"*, `-Xms6g -Xmx6g`, *"This will result in a file system cache of up to 28-30 GB on a 32 GB machine"*. Máy **64 GB** là lựa chọn tốt, 32 GB vẫn phổ biến.
- **CPU · Disk · Network:** mốc **24 core**, ưu tiên nhiều core hơn core nhanh, **TLS làm CPU tăng đáng kể**; **12 × 1 TB** disk (RAID 10 tuỳ chọn), **tách ổ OS khỏi ổ Kafka**, ưu tiên SSD, **tránh NAS**, filesystem **XFS hoặc ext4**; mạng **1 GbE / 10 GbE** là đủ với **latency < 30 ms** giữa các node.
- **Sizing broker theo N-1:** cluster phải còn đủ công suất khi **mất 1 broker** (hoặc 1 rack). Chạy 3 broker ở 90% CPU = mất 1 broker là sập; đó là lỗi sizing kinh điển.
- **Controller nhẹ hơn broker rất nhiều:** production tối thiểu *"three brokers and three controllers"*; controller KRaft *"3-5"* node với **64 GB SSD** và **4 GB RAM**.
- **File descriptor ≥ 100.000**; `vm.max_map_count=262144`; buffer ước lượng `write_throughput × 30` giây.
- `default.replication.factor` *"should be set to at least 2"* — thực tế production là **3**, đi cùng `min.insync.replicas=2`.

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Choosing the number of partitions (Confluent blog)

> **More partitions lead to higher throughput.** The more partitions there are in a Kafka cluster, the higher the throughput one can achieve. Roughly, if one thinks of a single partition as the unit of parallelism...

> A rough formula for picking the number of partitions is based on throughput. You measure the throughput that you can achieve on a single partition for production (call it `p`) and consumption (call it `c`). Let's say your target throughput is `t`. Then **you need to have at least `max(t/p, t/c)` partitions**. The per-partition throughput that one can achieve on the producer depends on configurations such as the batching size, compression codec, type of acknowledgement, replication factor, etc. However, in general, one can produce at 10s of MB/sec on just a single partition. The consumer throughput is often application dependent since it corresponds to how fast the consumer logic can process each message.

> A rule of thumb: if you care about latency, it's probably a good idea to **limit the number of partitions per broker to `100 × b × r`**, where `b` is the number of brokers in a Kafka cluster and `r` is the replication factor.

#### More partitions requires more open file handles

> Each partition maps to a directory in the file system in the broker. Within that log directory, there will be two files (one for the index and another for the actual data) per log segment. Currently, in Kafka, each broker opens a file handle of both the index and the data file of every log segment. So, the more partitions, the higher that one needs to configure the open file handle limit in the underlying operating system. This is mostly just a configuration issue. We have seen production Kafka clusters running with **more than 30 thousand open file handles per broker**.

#### More partitions may increase unavailability

> In the rare cases when a broker is stopped uncleanly (for example, it is killed), the observed unavailability could be proportional to the number of partitions. Suppose that a broker has a total of 2000 partitions, each with 2 replicas. Roughly, this broker will be the leader for about 1000 partitions. When this broker fails uncleanly, all those 1000 partitions become unavailable at exactly the same time. Suppose that it takes **5 ms** to elect a new leader for a single partition. It will take up to **5 seconds** to elect the new leader for all **1000 partitions**.

> As a rule of thumb, if you care about availability, it's probably better to **limit the number of partitions per broker to two to four thousand and the total number of partitions in the cluster to low tens of thousand**.

#### More partitions may increase end-to-end latency

> ... in general, **replicating 1000 partitions from one broker to another can add about 20 ms latency**, which implies an end-to-end latency of at least 20 ms.

#### More partitions may require more memory in the client

> In the producer, we do batching per partition. The amount of memory used for batching is per partition. In the consumer, we fetch a batch of messages per partition. The more partitions that a consumer subscribes to, the more memory it needs. As a rule of thumb, allocate **at least a few tens of KB per partition being produced** in the producer and adjust the total memory if the number of partitions increases significantly.

> ⚠️ **Lưu ý version:** bài blog này viết ở thời ZooKeeper. **KRaft rút ngắn đáng kể thời gian bầu leader hàng loạt** (controller giữ metadata trong bộ nhớ và phát thay đổi qua metadata log thay vì đọc/ghi znode), nên trần "2000–4000 partition/broker" là mốc **thận trọng**, không phải giới hạn cứng của 4.x. Cơ chế và 4 khoản chi phí thì không đổi.

### Running Kafka in production — hardware (Confluent Docs)

**Memory**

> Kafka uses heap space very carefully and does not require setting heap sizes more than **6 GB**. This will result in a file system cache of up to **28-30 GB** on a 32 GB machine.
>
> **64 GB RAM is a decent choice, but 32 GB machines are not uncommon.**
>
> Recommended JVM settings: `-Xms6g -Xmx6g`

**CPUs**

> Most Kafka deployments tend to be rather light on CPU requirements... You should **choose more cores** over faster processors for better concurrency. A baseline of **24 cores** is reasonable.
>
> If you need SSL/TLS enabled, CPU requirements can be significantly higher.

**Disks**

> **12 × 1 TB disk**, RAID 10 is optional.
>
> **Separate OS disks from Apache Kafka storage.** Use SSDs where possible and avoid network-attached storage (NAS).
>
> On Azure, use `cachingMode: None` for managed disks.

**Network**

> Modern data-center networking (**1 GbE, 10 GbE**) is sufficient for the vast majority of clusters. **Latency less than 30 milliseconds is generally recommended** between nodes of the same cluster.

### Cluster configuration

> A production cluster should have a minimum of **three brokers and three controllers**.
>
> KRaft controllers: **3-5** nodes, with **64 GB SSD** and **4 GB RAM** each.
>
> `default.replication.factor` should be set to **at least 2**; `min.insync.replicas` is critical for durability.

### JVM and OS tuning

> **Increase your file descriptor count to at least 100,000.**
>
> Set `vm.max_map_count=262144` — this value must exceed the number of `.index` files.
>
> Buffer estimate: `write_throughput * 30` seconds of data.
>
> Use **XFS or ext4** as the filesystem.
