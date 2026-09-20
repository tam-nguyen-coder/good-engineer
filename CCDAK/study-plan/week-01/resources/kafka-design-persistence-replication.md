# Apache Kafka — Design: Persistence, Efficiency, Producer/Consumer, Replication

> **Nguồn (official):** https://kafka.apache.org/43/design/design/
> **Tuần:** 1 — Kiến trúc Kafka & `KRaft` + Dựng cluster + CLI · **Loại:** Apache Kafka Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- **Persistence:** Kafka ghi **tuần tự** xuống đĩa và tin vào **OS pagecache** thay vì cache trong JVM heap → tránh GC, cache "ít nhất gấp đôi". Ghi tuần tự trên RAID-5 ~**600 MB/s** vs ghi ngẫu nhiên ~**100 kB/s** (chênh ~6000×).
- **O(1):** không dùng BTree (O(log N)); chỉ **append + sequential read** → hiệu năng **không phụ thuộc kích cỡ dữ liệu** → lưu lâu, dùng đĩa SATA rẻ vẫn ổn.
- **Efficiency:** (1) **batching** — gom record thành batch để giảm số round-trip; (2) **zero-copy** qua `sendfile` — dữ liệu đi từ pagecache thẳng ra NIC, copy vào pagecache **đúng 1 lần** cho mọi consumer; (3) **end-to-end batch compression** — nén **cả batch**, giữ nguyên dạng nén trong log và khi gửi tới consumer (GZIP, Snappy, LZ4, ZStandard).
- **Producer** gửi **thẳng tới leader** của partition (không qua router). Có key → semantic partitioning (cùng user → cùng partition). Gửi bất đồng bộ, gom batch theo kích cỡ **hoặc** thời gian chờ (ví dụ 64 kB hay 10 ms → thực tế `batch.size` / `linger.ms`).
- **Consumer dùng PULL** (không push): consumer tự quyết định tốc độ, chậm thì "fall behind and catch up"; tránh tight-loop bằng **long poll** (`fetch.min.bytes` / `fetch.max.wait.ms`). Vị trí đọc = **1 số nguyên offset** → có thể **rewind** đọc lại.
- **ISR** = replica đang có session với controller **và** không tụt quá xa leader; tụt quá `replica.lag.time.max.ms` → leader loại khỏi ISR. Record **committed** khi **mọi replica trong ISR** đã ghi; consumer chỉ đọc được message committed.
- Kafka chịu **f lỗi với f+1 replica** (khác majority-vote cần **2f+1**) → ít replica hơn cho cùng độ bền, throughput cao hơn.
- Khi **toàn bộ ISR chết**: mặc định **chờ ISR hồi** (ưu tiên consistency); `unclean.leader.election.enable=true` cho phép replica ngoài ISR làm leader (ưu tiên availability, **có thể mất dữ liệu**).
- `min.insync.replicas` + `acks=all`: broker chỉ nhận ghi khi ISR ≥ min.isr; nếu không → `NotEnoughReplicas`. Bộ chuẩn production: **RF=3, min.isr=2, acks=all**.
- Controller quản đăng ký broker + bầu leader và **gom (batch) nhiều thông báo đổi leader** → failover nhanh ngay cả với rất nhiều partition.

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Motivation

We designed Kafka to be able to act as a unified platform for handling all the real-time data feeds a large company might have. To do this we had to think through a fairly broad set of use cases. It would have to have high-throughput to support high volume event streams such as real-time log aggregation. It would need to deal gracefully with large data backlogs to be able to support periodic data loads from offline systems. It also meant the system would have to handle low-latency delivery to handle more traditional messaging use-cases. We wanted to support partitioned, distributed, real-time processing of these feeds to create new, derived feeds. Finally in cases where the stream is fed into other data systems for serving, we knew the system would have to be able to guarantee fault-tolerance in the presence of machine failures.

### Persistence

#### Don't fear the filesystem!

Kafka relies heavily on the filesystem for storing and caching messages. There is a general perception that "disks are slow" which makes people skeptical that a persistent structure can offer competitive performance. In fact disks are both much slower and much faster than people expect depending on how they are used; and a properly designed disk structure can often be as fast as the network.

The key fact about disk performance is that the throughput of hard drives has been diverging from the latency of a disk seek for the last decade. As a result the performance of linear writes on a JBOD configuration with six 7200rpm SATA RAID-5 array is about **600MB/sec** but the performance of random writes is only about **100k/sec** — a difference of over **6000X**. These linear reads and writes are the most predictable of all usage patterns, and are heavily optimized by the operating system.

To compensate for this performance divergence, modern operating systems have become increasingly aggressive in their use of main memory for disk caching. A modern OS will happily divert all free memory to disk caching with little performance penalty when the memory is reclaimed. All disk reads and writes will go through this unified cache.

Furthermore, we are building on top of the JVM, and anyone who has spent any time with Java memory usage knows two things: the memory overhead of objects is very high, often doubling the size of the data stored; Java garbage collection becomes increasingly fiddly and slow as the in-heap data increases.

As a result of these factors using the filesystem and relying on **pagecache** is superior to maintaining an in-memory cache or other structure — we at least double the available cache by having automatic access to all free memory. This suggests a design which is very simple: rather than maintain as much as possible in-memory and flush it all out to the filesystem in a panic when we run out of space, we invert that. **All data is immediately written to a persistent log on the filesystem without necessarily flushing to disk.** In effect this just means that it is transferred into the kernel's pagecache.

#### Constant Time Suffices

The persistent data structure used in messaging systems are often a per-consumer queue with an associated BTree or other general-purpose random access data structures. BTree operations are O(log N). Disk seeks come at 10 ms a pop, and each disk can do only one seek at a time so parallelism is limited.

Intuitively a persistent queue could be built on **simple reads and appends to files** as is commonly the case with logging solutions. This structure has the advantage that all operations are **O(1)** and reads do not block writes or each other. This has obvious performance advantages since the performance is **completely decoupled from the data size** — one server can now take full advantage of a number of cheap, low-rotational speed 1+TB SATA drives. Having access to virtually unlimited disk space without any performance penalty means that we can provide some features not usually found in a messaging system. For example, in Kafka, instead of attempting to delete messages as soon as they are consumed, we can retain messages for a relatively long period (say a week).

### Efficiency

There are two common causes of inefficiency: too many small I/O operations, and excessive byte copying.

The small I/O problem happens both between the client and the server and in the server's own persistent operations. To avoid this, our protocol is built around a **"message set" abstraction that naturally groups messages together**. This allows network requests to group messages together and amortize the overhead of the network roundtrip rather than sending a single message at a time. The server in turn appends chunks of messages to its log in one go, and the consumer fetches large linear chunks at a time. This simple optimization produces orders of magnitude speed up.

The other inefficiency is in byte copying. We avoid this by employing a standardized binary message format that is shared by the producer, the broker, and the consumer (so data chunks can be transferred without modification between them).

Modern unix operating systems offer a highly optimized code path for transferring data out of pagecache to a socket; in Linux this is done with the **`sendfile` system call**. Using `sendfile`, this re-copying is avoided by allowing the OS to send the data from pagecache to the network directly. We expect a common use case to be multiple consumers on a topic. Using the zero-copy optimization above, **data is copied into pagecache exactly once and reused on each consumption** instead of being stored in memory and copied out to user-space every time it is read. This allows messages to be consumed at a rate that approaches the limit of the network connection.

#### End-to-end Batch Compression

Efficient compression requires compressing multiple messages together rather than compressing each message individually. Kafka supports this with an efficient batching format. **A batch of messages can be grouped together, compressed, and sent to the server in this form. The batch of messages will be written in compressed form and will remain compressed in the log and will only be decompressed by the consumer.** Kafka supports GZIP, Snappy, LZ4 and ZStandard compression protocols.

### The Producer

#### Load balancing

The producer **sends data directly to the broker that is the leader for the partition** without any intervening routing tier. To help the producer do this all Kafka nodes can answer a request for **metadata** about which servers are alive and where the leaders for the partitions of a topic are at any given time.

The client controls which partition it publishes messages to. This can be done at random, implementing a kind of random load balancing, or it can be done by some semantic partitioning function. We expose the interface for semantic partitioning by allowing the user to specify a **key** to partition by and using this to hash to a partition. For example if the key chosen was a user id then **all data for a given user would be sent to the same partition**.

#### Asynchronous send

Batching is one of the big drivers of efficiency, and to enable batching the Kafka producer will attempt to accumulate data in memory and to send out larger batches in a single request. The batching can be configured to accumulate no more than a fixed number of messages and to wait no longer than some fixed latency bound (say 64k or 10 ms). This allows the accumulation of more bytes to send, and few larger I/O operations on the servers.

### The Consumer

The Kafka consumer works by issuing "fetch" requests to the brokers leading the partitions it wants to consume. The consumer specifies its **offset** in the log with each request and receives back a chunk of log beginning from that position. The consumer thus has significant control over this position and can rewind it to re-consume data if need be.

#### Push vs. pull

Kafka follows a more traditional design, where **data is pushed to the broker from the producer and pulled from the broker by the consumer**. A push-based system has difficulty dealing with diverse consumers as the broker controls the rate at which data is transferred; a consumer can be overwhelmed when its rate of consumption falls below the rate of production (a denial of service attack, in essence). A pull-based system has the nicer property that the consumer simply falls behind and catches up when it can.

The deficiency of a naive pull-based system is that if the broker has no data the consumer may end up polling in a tight loop. To avoid this we have parameters in our pull request that allow the consumer request to block in a **"long poll"** waiting until data arrives (and optionally waiting until a given number of bytes is available to ensure large transfer sizes).

#### Consumer Position

Kafka's topic is divided into a set of totally ordered partitions, each of which is consumed by exactly one consumer within each subscribing consumer group at any given time. This means that the position of a consumer in each partition is **just a single integer, the offset of the next message to consume**. This makes the state about what has been consumed very small, just one number for each partition. This state can be periodically checkpointed.

There is a side benefit of this decision. A consumer can deliberately **rewind back to an old offset and re-consume data**. This violates the common contract of a queue, but turns out to be an essential feature for many consumers.

### Replication

Kafka replicates the log for each topic's partitions across a configurable number of servers (you can set this replication factor on a topic-by-topic basis). This allows automatic failover to these replicas when a server in the cluster fails so messages remain available in the presence of failures.

The unit of replication is the **topic partition**. Under non-failure conditions, each partition in Kafka has a single **leader** and zero or more **followers**. The total number of replicas including the leader constitute the **replication factor**. All writes go to the leader of the partition, and reads can go to the leader or the followers of the partition. Followers consume messages from the leader just as a normal Kafka consumer would and apply them to their own log.

As with most distributed systems, automatically handling failures requires a precise definition of what it means for a node to be "alive." In Kafka, a special node known as the "controller" is responsible for managing the registration of brokers in the cluster. Broker liveness has two conditions:

1. Brokers must maintain an active session with the controller in order to receive regular metadata updates.
2. Brokers acting as followers must replicate the writes from the leader and **not fall "too far" behind**.

We refer to nodes satisfying these two conditions as being **"in sync"** to avoid the vagueness of "alive" or "failed". The leader keeps track of the set of "in sync" replicas, which is known as the **ISR**. If either of these conditions fail to be satisfied, then the broker will be removed from the ISR. For example, if a follower dies, then the controller will notice the failure through the loss of its session, and will remove the broker from the ISR. On the other hand, if the follower lags too far behind the leader but still has an active session, then the leader can also remove it from the ISR. The determination of lagging replicas is controlled through the **`replica.lag.time.max.ms`** configuration. Replicas that cannot catch up to the end of the leader's log within the max time set by this config are removed from the ISR.

A message is considered **committed when all replicas in the ISR for that partition have applied it to their log. Only committed messages are ever given out to the consumer.** This means that the consumer need not worry about potentially seeing a message that could be lost if the leader fails. Producers, on the other hand, have the option of either waiting for the message to be committed or not, depending on their preference for tradeoff between latency and durability. This preference is controlled by the `acks` setting that the producer uses.

The guarantee that Kafka offers is that a committed message will not be lost, as long as there is at least one in sync replica alive, at all times.

#### Replicated Logs: Quorums, ISRs, and State Machines

A majority vote approach requires **2f+1** replicas to tolerate f failures. Kafka takes a slightly different approach to choosing its quorum set. Instead of majority vote, Kafka dynamically maintains a set of in-sync replicas (ISR) that are caught-up to the leader. Only members of this set are eligible for election as leader. A write to a Kafka partition is not considered committed until all in-sync replicas have received the write. This ISR set is persisted in the cluster metadata whenever it changes. Because of this, any replica in the ISR is eligible to be elected leader. With this ISR model and **f+1 replicas, a Kafka topic can tolerate f failures without losing committed messages.**

#### Unclean leader election: What if they all die?

If you are unlucky enough to have all replicas die, there are two behaviors that could be implemented:

1. Wait for a replica in the ISR to come back to life and choose this replica as the leader (hopefully it still has all its data).
2. Choose the first replica (not necessarily in the ISR) that comes back to life as the leader.

This is a simple tradeoff between **availability and consistency**. If we wait for replicas in the ISR, then we will remain unavailable as long as those replicas are down. If such replicas were destroyed or their data was lost, then we are permanently down. If, on the other hand, a non-in-sync replica comes back to life and we allow it to become leader, then its log becomes the source of truth even though it is not guaranteed to have every committed message. **By default, Kafka chooses the first strategy** and favors waiting for a consistent replica. This behavior can be changed using configuration property **`unclean.leader.election.enable`**, to support use cases where uptime is preferable to consistency.

#### Availability and Durability Guarantees

When writing to Kafka, producers can choose whether they wait for the message to be acknowledged by 0, 1 or all (-1) replicas. Note that "acknowledgement by all replicas" does not guarantee that the full set of assigned replicas have received the message. By default, when `acks=all`, acknowledgement happens as soon as all the current in-sync replicas have received the message. Kafka offers two topic-level configurations that can be used to prefer message durability over availability:

1. Disable unclean leader election — if all replicas become unavailable, then the partition will remain unavailable until the most recent leader becomes available again.
2. Specify a **minimum ISR size** — the partition will only accept writes if the size of the ISR is above a certain minimum, in order to prevent the loss of messages that were written to just a single replica. This setting only takes effect if the producer uses `acks=all` and guarantees that the message will be acknowledged by at least this many in-sync replicas. This setting offers a trade-off between consistency and availability. A higher setting for minimum ISR size guarantees better consistency since the message is guaranteed to be written to more replicas which reduces the probability that it will be lost. However, it reduces availability since the partition will be unavailable for writes if the number of in-sync replicas drops below the minimum threshold.

#### Replica Management

It is also important to optimize the leadership election process as that is the critical window of unavailability. A naive implementation of leader election would end up running an election per partition for all partitions a node hosted when that node failed. As discussed above in the section on replication, Kafka clusters have a special role known as the "controller" which is responsible for managing the registration of brokers. If the controller detects the failure of a broker, it is responsible for electing one of the remaining members of the ISR to serve as the new leader. The result is that we are able to **batch together many of the required leadership change notifications** which makes the election process far cheaper and faster for a large number of partitions. If the controller itself fails, then another controller will be elected.
