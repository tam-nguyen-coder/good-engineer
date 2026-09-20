# Apache Kafka Operations — Hardware and OS + Java Version (heap 6 GB, G1GC, file descriptor, XFS)

> **Nguồn (official):** https://kafka.apache.org/43/operations/hardware-and-os/ · https://kafka.apache.org/43/operations/java-version/
> **Tuần:** 3 — Cluster Config II: JVM & OS tuning · **Loại:** Apache Kafka 4.3 Documentation (Operations)
> ⚠️ Nội dung dưới đây được crawl tự động từ hai trang gốc (có cắt bớt phần ngoài chủ đề) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- **Tham số JVM khuyến nghị chính thức** (nguyên văn trong docs): `-Xmx6g -Xms6g -XX:MetaspaceSize=96m -XX:+UseG1GC -XX:MaxGCPauseMillis=20 -XX:InitiatingHeapOccupancyPercent=35 -XX:G1HeapRegionSize=16M -XX:MinMetaspaceFreeRatio=50 -XX:MaxMetaspaceFreeRatio=80`. Thuộc **6 GB heap** và **G1GC**.
- `-Xms` **bằng** `-Xmx` (cả hai 6g) → heap cố định, tránh JVM co giãn heap giữa lúc chạy.
- Kafka **không dựa vào heap** để chứa dữ liệu — nó dựa vào **page cache của OS**. Heap to hơn = page cache nhỏ hơn + GC pause dài hơn ⇒ ISR flapping. Đây là lý do "tăng heap cho broker chậm" gần như luôn là **đáp án sai** trong đề.
- Tham chiếu của LinkedIn với đúng bộ flag trên: **60 broker, 50k partition (RF 2), 800k message/s, 300 MB/s vào — 1 GB/s+ ra**, GC pause p90 ≈ **21 ms**, **dưới 1 young GC mỗi giây**.
- Java: Kafka 4.3 hỗ trợ đầy đủ **Java 17, 21, 25**; **Java 11 chỉ cho một phần module** (clients, streams và liên quan). Khuyến nghị dùng bản LTS mới nhất.
- Bộ nhớ: ước lượng nhanh **`write_throughput × 30`** (đệm 30 giây). Máy tham chiếu trong docs: dual quad-core Xeon, **24 GB RAM**, **8 ổ SATA 7200 rpm**. "Disk throughput is the performance bottleneck, and more disks is better."
- **File descriptor: tối thiểu 100000** cho tiến trình broker ("We recommend at least 100000 allowed file descriptors for the broker processes as a starting point"). Mỗi log segment, mỗi connection đều tốn fd.
- **`vm.max_map_count`** (mặc định ~65535 trên nhiều distro) giới hạn số partition: mỗi log segment cần **2 map area** (index + timeindex) → **50000 partition ⇒ 100000 map area ⇒ broker crash `OutOfMemoryError (Map failed)`**. Đây là con số rất hay bị bỏ qua.
- Filesystem: hai lựa chọn phổ biến là **EXT4 và XFS**; kiểm thử cho thấy **XFS tốt hơn rõ rệt** — "Request Local Time" **160 ms so với 250 ms+** của cấu hình EXT4 tốt nhất. Mount với **`noatime`**. XFS gần như không cần tinh chỉnh thêm.
- Ổ đĩa: **dùng nhiều ổ**, và **không dùng chung ổ Kafka với application log / hoạt động filesystem của OS**. Nhiều `log.dirs` → partition được gán **round-robin theo thư mục**, mỗi partition nằm trọn trong một thư mục → dữ liệu lệch giữa partition sẽ làm **lệch tải giữa các ổ**.
- RAID: Kafka đã có replication nên RAID **không thêm nhiều giá trị**; docs nói rebuild RAID array tốn I/O tới mức "effectively disables the server".
- Flush: **giữ mặc định — tắt hẳn application fsync**, để OS flush nền. "Durability in Kafka does not require syncing data to disk, as a failed node will always recover from its replicas."

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Java Version

Java 17, Java 21, and Java 25 are fully supported while Java 11 is supported for a subset of modules (clients, streams and related). Support for versions newer than the most recent LTS version are best-effort and the project typically only tests with the most recent non LTS version.

We generally recommend running Apache Kafka with the most recent LTS release (Java 25 at the time of writing) for performance, efficiency and support reasons. From a security perspective, we recommend the latest released patch version as older versions typically have disclosed security vulnerabilities.

Typical arguments for running Kafka with OpenJDK-based Java implementations (including Oracle JDK) are:

```
-Xmx6g -Xms6g -XX:MetaspaceSize=96m -XX:+UseG1GC
-XX:MaxGCPauseMillis=20 -XX:InitiatingHeapOccupancyPercent=35 -XX:G1HeapRegionSize=16M
-XX:MinMetaspaceFreeRatio=50 -XX:MaxMetaspaceFreeRatio=80 -XX:+ExplicitGCInvokesConcurrent
```

For reference, here are the stats for one of LinkedIn's busiest clusters (at peak) that uses said Java arguments:

- 60 brokers
- 50k partitions (replication factor 2)
- 800k messages/sec in
- 300 MB/sec inbound, 1 GB/sec+ outbound

All of the brokers in that cluster have a 90% GC pause time of about 21ms with less than 1 young GC per second.

### Hardware and OS

We are using dual quad-core Intel Xeon machines with 24GB of memory.

You need sufficient memory to buffer active readers and writers. You can do a back-of-the-envelope estimate of memory needs by assuming you want to be able to buffer for 30 seconds and compute your memory need as `write_throughput*30`.

The disk throughput is important. We have 8x7200 rpm SATA drives. In general disk throughput is the performance bottleneck, and more disks is better. Depending on how you configure flush behavior you may or may not benefit from more expensive disks (if you force flush often then higher RPM SAS drives may be better).

#### OS

Kafka should run well on any unix system and has been tested on Linux and Solaris. We have seen a few issues running on Windows and Windows is not currently a well supported platform though we would be happy to change that.

It is unlikely to require much OS-level tuning, but there are three potentially important OS-level configurations:

- **File descriptor limits**: Kafka uses file descriptors for log segments and open connections. If a broker hosts many partitions, consider that the broker needs at least `(number_of_partitions)*(partition_size/segment_size)` to track all log segments in addition to the number of connections the broker makes. **We recommend at least 100000 allowed file descriptors for the broker processes as a starting point.** Note: The `mmap()` function adds an extra reference to the file associated with the file descriptor fildes which is not removed by a subsequent `close()` on that file descriptor. This reference is removed when there are no more mappings to the file.
- **Max socket buffer size**: can be increased to enable high-performance data transfer between data centers as described here.
- **Maximum number of memory map areas a process may have (aka `vm.max_map_count`)**. See the Linux kernel documentation. You should keep an eye at this OS-level property when considering the maximum number of partitions a broker may have. By default, on a number of Linux systems, the value of `vm.max_map_count` is somewhere around 65535. Each log segment, allocated per partition, requires a pair of index/timeindex files, and each of these files consumes 1 map area. In other words, each log segment uses 2 map areas. Thus, each partition requires minimum 2 map areas, as long as it hosts a single log segment. **That is to say, creating 50000 partitions on a broker will result allocation of 100000 map areas and likely cause broker crash with `OutOfMemoryError (Map failed)` on a system with default `vm.max_map_count`.** Keep in mind that the number of log segments per partition varies depending on the segment size, load intensity, retention policy and, generally, tends to be more than one.

#### Disks and Filesystem

We recommend using multiple drives to get good throughput and **not sharing the same drives used for Kafka data with application logs or other OS filesystem activity** to ensure good latency. You can either RAID these drives together into a single volume or format and mount each drive as its own directory. Since Kafka has replication the redundancy provided by RAID can also be provided at the application level. This choice has several tradeoffs.

**If you configure multiple data directories partitions will be assigned round-robin to data directories. Each partition will be entirely in one of the data directories. If data is not well balanced among partitions this can lead to load imbalance between disks.**

RAID can potentially do better at balancing load between disks (although it doesn't always seem to) because it balances load at a lower level. The primary downside of RAID is that it is usually a big performance hit for write throughput and reduces the available disk space.

Another potential benefit of RAID is the ability to tolerate disk failures. However our experience has been that rebuilding the RAID array is so I/O intensive that it effectively disables the server, so this does not provide much real availability improvement.

#### Application vs. OS Flush Management

Kafka always immediately writes all data to the filesystem and supports the ability to configure the flush policy that controls when data is forced out of the OS cache and onto disk using the flush. This flush policy can be controlled to force data to disk after a period of time or after a certain number of messages has been written.

Kafka must eventually call `fsync` to know that data was flushed. When recovering from a crash for any log segment not known to be `fsync`'d Kafka will check the integrity of each message by checking its CRC and also rebuild the accompanying offset index file as part of the recovery process executed on startup.

**Note that durability in Kafka does not require syncing data to disk, as a failed node will always recover from its replicas.**

**We recommend using the default flush settings which disable application fsync entirely.** This means relying on the background flush done by the OS and Kafka's own background flush. This provides the best of all worlds for most uses: no knobs to tune, great throughput and latency, and full recovery guarantees. We generally feel that the guarantees provided by replication are stronger than sync to local disk, however the paranoid still may prefer having both and application level fsync policies are still supported.

The drawback of using application level flush settings is that it is less efficient in its disk usage pattern (it gives the OS less leeway to re-order writes) and it can introduce latency as `fsync` in most Linux filesystems blocks writes to the file whereas the background flushing does much more granular page-level locking.

#### Understanding Linux OS Flush Behavior

In Linux, data written to the filesystem is maintained in pagecache until it must be written out to disk (due to an application-level `fsync` or the OS's own flush policy). […] You can see the current state of OS memory usage by doing `cat /proc/meminfo`.

Using pagecache has several advantages over an in-process cache for storing data that will be written out to disk:

- The I/O scheduler will batch together consecutive small writes into bigger physical writes which improves throughput.
- The I/O scheduler will attempt to re-sequence writes to minimize movement of the disk head which improves throughput.
- **It automatically uses all the free memory on the machine.**

#### Filesystem Selection

Kafka uses regular files on disk, and as such it has no hard dependency on a specific filesystem. **The two filesystems which have the most usage, however, are EXT4 and XFS.** Historically, EXT4 has had more usage, but recent improvements to the XFS filesystem have shown it to have better performance characteristics for Kafka's workload with no compromise in stability.

Comparison testing was performed on a cluster with significant message loads, using a variety of filesystem creation and mount options. The primary metric in Kafka that was monitored was the "Request Local Time", indicating the amount of time append operations were taking. **XFS resulted in much better local times (160ms vs. 250ms+ for the best EXT4 configuration)**, as well as lower average wait times. The XFS performance also showed less variability in disk performance.

#### General Filesystem Notes

For any filesystem used for data directories, on Linux systems, the following options are recommended to be used at mount time:

- **`noatime`**: This option disables updating of a file's atime (last access time) attribute when the file is read. This can eliminate a significant number of filesystem writes, especially in the case of bootstrapping consumers. Kafka does not rely on the atime attributes at all, so it is safe to disable this.

#### XFS Notes

The XFS filesystem has a significant amount of auto-tuning in place, so it does not require any change in the default settings, either at filesystem creation time or at mount. The only tuning parameters worth considering are `largeio` and `nobarrier`.

#### EXT4 Notes

EXT4 is a serviceable choice of filesystem for the Kafka data directories, however getting the most performance out of it will require adjusting several mount options (`data=writeback`, disabling journaling, `commit=num_secs`, `nobh`, `delalloc`, `fast_commit`). **In addition, these options are generally unsafe in a failure scenario, and will result in much more data loss and corruption.**

#### Replace KRaft Controller Disk

When Kafka is configured to use KRaft, the controllers store the cluster metadata in the directory specified in `metadata.log.dir` — or the first log directory, if `metadata.log.dir` is not configured.

If the data in the cluster metadata directory is lost either because of hardware failure or the hardware needs to be replaced, care should be taken when provisioning the new controller node. **The new controller node should not be formatted and started until the majority of the controllers have all of the committed data.** To determine if the majority of the controllers have the committed data, run the `kafka-metadata-quorum.sh` tool to describe the replication status:

```
$ bin/kafka-metadata-quorum.sh --bootstrap-server localhost:9092 describe --replication
NodeId  DirectoryId             LogEndOffset  Lag  LastFetchTimestamp  LastCaughtUpTimestamp  Status
1       dDo1k_pRSD-VmReEpu383g  966           0    1732367153528       1732367153528          Leader
2       wQWaQMJYpcifUPMBGeRHqg  966           0    1732367153304       1732367153304          Observer
```

Check and wait until the Lag is small for a majority of the controllers. […] At this point it is safer to format the controller's metadata log directory with `kafka-storage.sh format`.
