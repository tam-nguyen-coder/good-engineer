# Confluent Platform — Production tuning: sizing, page cache vs heap, JVM, file descriptor, `vm.swappiness`, lagging replicas

> **Nguồn (official):** https://docs.confluent.io/platform/current/kafka/deployment.html (Phần A) · https://docs.confluent.io/platform/current/kafka/post-deployment.html (Phần B)
> **Tuần:** 3 — Cluster Config II: JVM & OS tuning, ISR & throughput replication · **Loại:** Confluent Platform Documentation
> ⚠️ Nội dung dưới đây được crawl tự động từ hai trang gốc (có cắt bớt phần ngoài chủ đề) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

### Phần A — Running Kafka in Production (sizing, heap, JVM, file descriptor)

- Câu chốt của Confluent về heap: **"Kafka uses heap space very carefully and does not require setting heap sizes more than 6 GB. This will result in a file system cache of up to 28-30 GB on a 32 GB machine."** → heap **6 GB**, phần RAM còn lại **để OS làm page cache**. Đây là lý do "tăng heap lên 32 GB cho chắc" luôn sai. Kafka ghi vào **page cache trước**, không bắt buộc flush xuống đĩa.
- RAM: **64 GB là lựa chọn tốt**, 32 GB vẫn phổ biến, **dưới 32 GB phản tác dụng**; ước lượng đệm `write_throughput × 30` giây. CPU: nhẹ **trừ khi bật TLS**, và chọn **nhiều core** hơn core nhanh (cụm phổ biến 24 core).
- Cấu hình tham chiếu: **3 broker** (12 × 1 TB đĩa, **tách ổ OS khỏi ổ dữ liệu Kafka**, 64 GB RAM, 24 core) + **3–5 KRaft controller** (64 GB SSD, 4 GB RAM, 4 core).
- Filesystem **XFS hoặc ext4**; RAID ưu tiên **RAID 1 / RAID 10**, sau đó RAID 0, **không khuyến nghị RAID 5**; tránh NAS, chấp nhận SAN/EBS nếu đo đạt yêu cầu; latency giữa broker nên **dưới 30 ms**. ⚠️ **Tiered Storage của Confluent Platform yêu cầu một mount point duy nhất → KHÔNG hỗ trợ JBOD.**
- Bộ flag GC **trùng khớp Apache docs**: `-Xms6g -Xmx6g -XX:MetaspaceSize=96m -XX:+UseG1GC -XX:MaxGCPauseMillis=20 -XX:InitiatingHeapOccupancyPercent=35 -XX:G1HeapRegionSize=16M -XX:MinMetaspaceFreeRatio=50 -XX:MaxMetaspaceFreeRatio=80`.
- **File descriptor: distro Linux thường mặc định 1.024 — quá thấp. Nâng lên ít nhất 100.000**, "and possibly much more". `vm.max_map_count`: đếm file `.index` rồi đặt ví dụ **`sysctl -w vm.max_map_count=262144`** và ghi vào `/etc/sysctl.conf`.

### Phần B — Best Practices (`vm.swappiness`, lagging replicas, throttle, rolling restart)

- **`vm.swappiness = 1`, KHÔNG phải 0.** Swap cướp RAM của page cache nên phải rất thấp, nhưng **0 là bỏ luôn lưới an toàn** — hết RAM thì OS giết tiến trình thay vì swap. Giá trị là **phần trăm mức "hăng hái" chọn swap thay vì bỏ page cache**.
- **Replica tụt khỏi ISR** vì replica **hỏng** (failed) hoặc **chậm** (slow); ngưỡng duy nhất là `replica.lag.time.max.ms`. Cách chọn theo docs: quan sát `kafka.server:type=ReplicaFetcherManager,name=MinFetchRate,clientId=Replica`, nếu tốc độ là `n` thì đặt **lớn hơn `1/n × 1000`** ⇒ **đo trước, chỉnh sau**; `MinFetchRate` gần 0 nghĩa là replica/consumer đã **dừng hẳn**, khác 0 mà lag tăng nghĩa là **chậm hơn producer**.
- Throttle khi reassign dùng **4 config** tự động gán bởi `kafka-reassign-partitions`: broker-level dynamic **`leader.replication.throttled.rate`** / **`follower.replication.throttled.rate`**, topic-level **`leader.replication.throttled.replicas`** / **`follower.replication.throttled.replicas`**; theo dõi bằng `kafka.server:type=LeaderReplication,name=byte-rate` và `…FollowerReplication…`.
- Rolling restart: **`controlled.shutdown.enable=true`**, tắt **từng broker một**, **không `kill -9`**, **restart active controller CUỐI CÙNG**, **chờ URP về 0** rồi mới sang broker kế. Client không downtime nếu số ISR còn lại **lớn hơn** `min.insync.replicas`. Trước khi bắt đầu: xác nhận **URP = 0** và tìm active controller bằng `ActiveControllerCount` = **1**.
- Message lớn: **giữ mức 1 MB mặc định**. Muốn tăng thì chỉnh đồng bộ topic `max.message.bytes` (**khuyến nghị đặt ở topic, không ở broker**) + producer `max.request.size`/`batch.size`/`buffer.memory` + consumer `fetch.max.bytes`/`max.partition.fetch.bytes`. Tác hại: **heap fragmentation** và **page cache bẩn**.
- Backup Kafka = **dựng cluster thứ hai và replicate**, không có "dump file rồi restore" (chi tiết ở Tuần 4).

---

## 📄 Nội dung (trích từ tài liệu gốc)

## Phần A — Running Kafka in Production


### Hardware recommendations (bảng tóm tắt)

| Component | Nodes | Storage | Memory | CPU |
|---|---|---|---|---|
| **Broker** | 3 | 12 × 1 TB disk. RAID 10 is optional. **Separate OS disks from Apache Kafka® storage** | 64 GB RAM | 24 cores |
| **KRaft controller** | 3–5 | 64 GB SSD | 4 GB RAM | 4 cores |
| Connect | 2 | Storage is only required at installation time | 0.5 – 4 GB heap size depending on connectors | Typically not CPU-bound. More cores is better than faster cores |

> If you want to use RAID disks, the recommendation is: **RAID 1 and RAID 10: Preferred · RAID 0: 2nd preferred · RAID 5: Not recommended.**

### Memory

Kafka relies heavily on the filesystem for storing and caching messages. All data is immediately written to a persistent log on the filesystem without necessarily flushing to disk. In effect this just means that it is transferred into the kernel's pagecache. A modern OS will happily divert all free memory to disk caching with little performance penalty when the memory is reclaimed. **Furthermore, Kafka uses heap space very carefully and does not require setting heap sizes more than 6 GB. This will result in a file system cache of up to 28-30 GB on a 32 GB machine.**

You need sufficient memory to buffer active readers and writers. You can do a back-of-the-envelope estimate of memory needs by assuming you want to be able to buffer for 30 seconds and compute your memory need as `write_throughput * 30`.

**A machine with 64 GB of RAM is a decent choice, but 32 GB machines are not uncommon. Less than 32 GB tends to be counterproductive** (you end up needing many, many small machines).

### CPUs

Most Kafka deployments tend to be rather light on CPU requirements. As such, the exact processor setup matters less than the other resources. **Note that if TLS is enabled, the CPU requirements can be significantly higher** (the exact details depend on the CPU type and JVM implementation).

You should choose a modern processor with multiple cores. Common clusters utilize 24 core machines. **If you need to choose between faster CPUs or more cores, choose more cores.** The extra concurrency that multiple cores offers will far outweigh a slightly faster clock speed.

### Disks

> **Note**
> - Tiered Storage in Confluent Platform requires a single mount point and therefore **does not support Just a Bunch of Disks (JBOD)**. If you want to use Tiered Storage, do not use JBOD.
> - Self-Balancing balances data across the disks within a broker in a JBOD setup.

You should use multiple drives to maximize throughput. **Do not share the same drives used for Kafka data with application logs or other OS filesystem activity to ensure good latency.** You can either combine these drives together into a single volume as a Redundant Array of Independent Disks (RAID) or format and mount each drive as its own directory. Because Kafka has replication the redundancy provided by RAID can also be provided at the application level.

**If you configure multiple data directories, the broker places a new partition in the path with the least number of partitions currently stored.** Each partition will be entirely in one of the data directories. If data is not well balanced among partitions, this can lead to load imbalance among disks.

RAID 10 is recommended as the best "sleep at night" option for most use cases. It provides improved read and write performance, data protection (ability to tolerate disk failures), and fast rebuild times. The primary downside of RAID is that it reduces the available disk space. Another downside is the I/O cost of rebuilding the array when a disk fails.

Finally, you should avoid file-based network-attached storage (NAS). NAS is often slower, displays larger latencies with a wider deviation in average latency, and is a single point of failure. However, block-based storage area networks (SANs) can be used for Kafka deployments, provided that you validate the performance meets your requirements. Cloud-based block storage solutions, such as Amazon EBS, are examples of SAN storage that are commonly used with Kafka.

### Network and general sizing

A fast and reliable network is an essential performance component in a distributed system. Modern data-center networking (1 GbE, 10 GbE) is sufficient for the vast majority of clusters and **latency less than 30 milliseconds is generally recommended for Kafka**. In general, medium-to-large machines are preferred: avoid small machines (you do not want a thousand-node cluster) and avoid very large ones, which "often lead to imbalanced resource usage. For example, all the memory is being used, but none of the CPU."

### Filesystem

**You should run Kafka on XFS or ext4.**

### JVM

The recommended GC tuning (tested on a large deployment with JDK 1.8 u5) looks like this:

```
-Xms6g -Xmx6g -XX:MetaspaceSize=96m -XX:+UseG1GC -XX:MaxGCPauseMillis=20
       -XX:InitiatingHeapOccupancyPercent=35 -XX:G1HeapRegionSize=16M
       -XX:MinMetaspaceFreeRatio=50 -XX:MaxMetaspaceFreeRatio=80
```

For reference, here are the stats on one of LinkedIn's busiest clusters (at peak):

- 60 brokers
- 50k partitions (replication factor 2)
- 800k messages/sec in
- 300 MBps inbound, 1 GBps + outbound

The tuning looks fairly aggressive, but all of the brokers in that cluster have a 90% GC pause time of about 21ms, and they're doing less than 1 young GC per second.

Java support in Confluent Platform: **8.3.x recommends Java 21** and supports 25 / 21 / 17. Confluent Platform 8.0.x and later support Java 11 **only** for Kafka Streams and Kafka clients.

### File Descriptors and mmap

Kafka uses a very large number of files and a large number of sockets to communicate with the clients. All of this requires a relatively high number of available file descriptors.

**Many modern Linux distributions ship with only 1,024 file descriptors allowed per process. This is too low for Kafka. You should increase your file descriptor count to at least 100,000, and possibly much more.** This process can be difficult and is highly dependent on your particular OS and distribution.

To calculate the current mmap number, you can count the `.index` files in the Kafka data directory. The `.index` files represent the majority of the memory mapped files. Here is the procedure:

1. Count the `.index` files using this command:
   ```
   find . -name '*index' | wc -l
   ```
2. Set the `vm.max_map_count` for the session. The minimum value for mmap limit (`vm.max_map_count`) is the number of open files ulimit.
   ```
   sysctl -w vm.max_map_count=262144
   ```
3. Set the `vm.max_map_count` so that it will survive a reboot:
   ```
   echo 'vm.max_map_count=262144' >> /etc/sysctl.conf
   sysctl -p
   ```

> **Important:** You should set `vm.max_map_count` sufficiently higher than the number of `.index` files to account for broker segment growth.

> ⚠️ Cảnh báo VMware: **Disable vMotion and disk snapshotting for Confluent Platform** — chúng có thể gây mất cả cluster khi dùng với Kafka hoặc KRaft.

---

## Phần B — Best Practices for Kafka Production Deployments


### Tuning virtual memory

Linux virtual memory automatically adjusts to accommodate the workload of a system. Because Kafka relies heavily on the system page cache, when a virtual memory system swaps to disk it is possible that insufficient memory is allocated to the page cache. **Generally speaking, swapping has a noticeable negative impact on all aspects of Kafka performance, and should be avoided.**

If you do not configure swap space, then you can avoid altogether swapping-related performance issues. However, swap provides an important safety mechanism in case of a catastrophic system issue. For example, swap prevents the OS from abruptly killing a process when faced with an out-of-memory condition.

**To avoid swap performance issues and simultaneously have the assurance of a safety net, set the `vm.swappiness` parameter to a very low value, such as 1.** The `vm.swappiness` value is a percentage of how likely the virtual memory subsystem is to use swap space rather than drop pages from the page cache. The higher the value of the parameter, the more aggressively the kernel will swap. Reducing the page cache size is preferable to adjusting swap. **However, it is not recommended to use a value of 0, because it would never allow a swap under any circumstances, thus forfeiting the safety net afforded when using this parameter.**

### Lagging replicas

ISR is the set of replicas that are fully sync-ed up with the leader. In other words, every replica in the ISR has written all committed messages to its local log. **In steady state, ISR should always include all replicas of the partition.** Occasionally, some replicas fall out of the in-sync replica list. This could either be due to failed replicas or slow replicas.

A replica can be dropped out of the ISR if it diverges from the leader beyond a certain threshold. This is controlled by the following parameter:

- **`replica.lag.time.max.ms`** — This is typically set to a value that reliably detects the failure of a broker. You can set this value appropriately by observing the value of the replica's minimum fetch rate that measures the rate of fetching messages from the leader (`kafka.server:type=ReplicaFetcherManager,name=MinFetchRate,clientId=Replica`). **If that rate is n, set the value for this parameter to larger than `1/n * 1000`.**

### Increasing consumer throughput

First, try to figure out if the consumer is just slow or has stopped. To do so, you can monitor the maximum lag metric `kafka.consumer:type=ConsumerFetcherManager,name=MaxLag,clientId=([-.\w]+)` that indicates the number of messages the consumer lags behind the producer. Another metric to monitor is the minimum fetch rate `kafka.consumer:type=ConsumerFetcherManager,name=MinFetchRate,clientId=([-.\w]+)` of the consumer. **If the `MinFetchRate` of the consumer drops to almost 0, the consumer is likely to have stopped. If the `MinFetchRate` is non-zero and relatively constant, but the consumer lag is increasing, it indicates that the consumer is slower than the producer.**

### Handling large message sizes

**We strongly recommend that you adhere to the default maximum size of 1 MB for messages.** When it is absolutely necessary to increase the maximum message size, the following are a few of the many implications you should consider. Also consider alternative options such as using compression and/or splitting up messages.

- **Heap fragmentation** — Consistently large messages likely cause heap fragmentation on the broker side, requiring significant JVM tuning to maintain consistent performance.
- **Dirty page cache** — Accessing messages that are no longer available in the page cache is slow. With larger messages, fewer messages can fit in the page cache, causing degraded performance.
- **Kafka client buffer sizes** — Default buffer sizes on the client side are tuned for small messages (<1MB). You will have to tune client side buffers on both the producer and consumer.

| Scope | Config Parameter | Notes |
|---|---|---|
| Topic | `max.message.bytes` | **Recommended** to set the maximum message size at the topic level |
| Broker | `message.max.bytes` | Setting the maximum message size at the broker level is **not recommended** |
| Producer | `max.request.size` | Required for the producer level change of the maximum message size |
| Producer | `batch.size`, `buffer.memory` | Use these parameters for performance tuning |
| Consumer | `fetch.max.bytes`, `max.partition.fetch.bytes` | Use these to set the maximum message size at the consumer level |

### Rolling restart

If you need to do software upgrades, broker configuration updates, or cluster maintenance, then you will need to restart all the brokers in your Kafka cluster. To do this, you can do a rolling restart by restarting one broker at a time.

Some considerations to avoid downtime include:

- **Because one replica is unavailable while a broker is restarting, clients will not experience downtime if the number of remaining in-sync replicas is greater than the configured `min.insync.replicas`.**
- Run brokers with **`controlled.shutdown.enable=true`** to migrate topic partition leadership before the broker is stopped.
- **The active controller should be the last broker you restart.** This is to ensure that the active controller is not moved on each broker restart, which would slow down the restart.

Before starting a rolling restart:

1. Verify your cluster is healthy and **there are no under replicated partitions**. If there are under replicated partitions, investigate why before doing a rolling restart.
2. Identify which Kafka broker in the cluster is the active controller. The active controller will report **1** for the metric `kafka.controller:type=KafkaController,name=ActiveControllerCount` and the remaining brokers will report 0.

Workflow:

1. Connect to one broker, being sure to leave the active controller for last, and **stop the broker process gracefully. Do not send a `kill -9` command.** Wait until the broker has completely shut down.
2. Perform the software upgrade / configuration change on this broker.
3. Start the broker back up.
4. **Wait until that broker completely restarts and is caught up before proceeding to restart the next broker.** During broker restart, the under-replicated partitions number increases because data will not be replicated to topic partitions that reside on the restarting broker. After a broker restarts and is caught up, this number goes back to **0** in a healthy cluster.
5. Repeat on each broker until you have restarted all brokers but the active controller. Now you can restart the active controller.

### Replication throttle (dùng khi reassign partition)

There are two pairs of throttle configuration used to manage the throttling process. The throttle value itself is configured, at a broker level, using the dynamic properties:

```
leader.replication.throttled.rate
follower.replication.throttled.rate
```

There is also an enumerated set of throttled replicas, configured per topic:

```
leader.replication.throttled.replicas
follower.replication.throttled.replicas
```

**All four config values are automatically assigned by `kafka-reassign-partitions`.**

The throttle mechanism works by measuring the received and transmitted rates, for partitions in the `replication.throttled.replicas` lists, on each broker. These rates are compared to the `replication.throttled.rate` config to determine if a throttle should be applied. The rate of throttled replication is recorded in the below JMX metrics:

```
MBean: kafka.server:type=LeaderReplication,name=byte-rate
MBean: kafka.server:type=FollowerReplication,name=byte-rate
```

To view the throttle limit configuration:

```
bin/kafka-configs --describe --bootstrap-server localhost:9092 --entity-type brokers
Configs for brokers '2' are leader.replication.throttled.rate=1000000,follower.replication.throttled.rate=1000000
Configs for brokers '1' are leader.replication.throttled.rate=1000000,follower.replication.throttled.rate=1000000
```

### Logging (bối cảnh chẩn đoán ISR)

Apache Kafka® emits a number of logs. The default logging level is INFO. **When debugging problems, particularly problems with replicas falling out of ISR, it can be helpful to bump up the logging level to DEBUG.** You can edit the `log4j2.yaml` file and restart your nodes, but that leads to unnecessary downtime — Kafka supports changing log levels dynamically instead.

- `logs/controller.log` — "Any ERROR, FATAL or WARN in this log indicates an important event that should be looked at by the administrator."
- `logs/state-change.log` — "if some partition is offline for a while, this log can provide useful information as to whether the partition is offline due to a failed leader election operation." Default log level for this log is **TRACE**.
