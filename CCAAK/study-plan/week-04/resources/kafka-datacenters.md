# Apache Kafka — Datacenters: một cluster trải nhiều DC hay nhiều cluster + mirroring?

> **Nguồn (official):** https://kafka.apache.org/43/operations/datacenters/ (§6.2 Datacenters)
> **Tuần:** 4 — Deployment Architecture · **Loại:** Apache Kafka 4.3 Docs
> ⚠️ Nội dung dưới đây được crawl tự động (HTTP → Markdown, có rút gọn) — luôn đối chiếu link gốc để đầy đủ và cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- **Khuyến nghị mặc định của Apache Kafka: MỖI DC một cluster riêng**, ứng dụng trong DC chỉ nói chuyện với cluster **local** của nó, rồi **mirror** dữ liệu giữa các cluster. Đây là câu trả lời "an toàn" khi đề không nói rõ độ trễ giữa các DC.
- **Docs cảnh báo thẳng chống lại stretch cluster qua link chậm**: *"we do not recommend ... a single Kafka cluster that spans multiple datacenters over a high-latency link"* vì **replication latency** cao và **mất khả dụng** khi đứt mạng. Đối chiếu với Confluent: stretch cluster **chỉ** chấp nhận được khi mạng ổn định và **dưới 100 ms**.
- **3 lợi ích của mô hình cluster-per-DC** mà đề hay hỏi: mỗi DC **tự chủ** (chạy được cả khi link liên DC chết) · khi link trở lại, mirroring **tự đuổi kịp** phần tồn đọng · điều chỉnh và quản lý replication liên DC **ở một chỗ**.
- Cần dữ liệu toàn cục → dựng **aggregate cluster** mirror từ tất cả cluster local; ứng dụng phân tích đọc từ aggregate cluster (đây chính là topology **hub-and-spoke / aggregation** `A->K, B->K, C->K` của MM2).
- Nếu **bắt buộc** phải đọc/ghi xuyên DC: tăng **`socket.send.buffer.bytes`** và **`socket.receive.buffer.bytes`** (mặc định **102400** = 100 KiB) để bù bandwidth-delay product, nếu không throughput sẽ bị chặn dù đường truyền rộng. Đây là chi tiết rất "admin" và hay xuất hiện trong đề.
- Đọc chéo: Kafka docs bảo "đừng stretch qua link chậm"; Confluent docs bảo "stretch được nếu **dưới 100 ms** và ổn định, và 2 DC thì phải thêm DC thứ ba chỉ chạy controller (2.5 DC)". **Hai tài liệu không mâu thuẫn** — điều kiện độ trễ là thứ phân định.

---

## 📄 Nội dung (trích từ tài liệu gốc)

### 6.2 Datacenters

Some deployments will need to manage a data pipeline that spans multiple datacenters. Our recommended approach to this is to deploy a local Kafka cluster in each datacenter, with application instances in each datacenter interacting only with their local cluster and mirroring data between clusters (see the documentation on Geo-Replication for how to do this).

This deployment pattern allows datacenters to act as independent entities and allows us to manage and tune inter-datacenter replication centrally. This allows each facility to stand alone and operate even if the inter-datacenter links are unavailable: when this occurs the mirroring falls behind until the link is restored at which time it catches up.

For applications that need a global view of all data you can use mirroring to provide clusters which have aggregate data mirrored from the local clusters in *all* datacenters. These aggregate clusters are used for reads by applications that require the full data set.

This is not the only possible deployment pattern. It is possible to read from or write to a remote Kafka cluster over the WAN, though obviously this will add whatever latency is required to get the cluster.

Kafka naturally batches data in both the producer and consumer so it can achieve high-throughput even over a high-latency connection. To allow this though it may be necessary to increase the TCP socket buffer sizes for the producer, consumer, and broker using the `socket.send.buffer.bytes` and `socket.receive.buffer.bytes` configurations. The appropriate way to set this is documented here.

It is generally **not** advisable to run a *single* Kafka cluster that spans multiple datacenters over a high-latency link. This will incur very high replication latency both for Kafka writes and ZooKeeper writes, and neither Kafka nor ZooKeeper will remain available in all locations if the network between locations is unavailable.

> 📌 *Ghi chú version:* câu cuối còn giữ chữ "ZooKeeper" từ các bản docs cũ. Với **Kafka 4.x (KRaft-only)** hãy đọc là **controller quorum**: một quorum trải nhiều DC qua link chậm sẽ chậm khi ghi metadata, và mất đa số khi đứt mạng thì **control plane đóng băng**. Bản chất lập luận không đổi.

### The socket buffer configurations referenced above

> Trích https://kafka.apache.org/43/configuration/broker-configs/ — đây là hai config mà trang Datacenters bảo phải tăng khi đi xuyên WAN.

**`socket.send.buffer.bytes`**

> The SO_SNDBUF buffer of the socket server sockets. If the value is -1, the OS default will be used.
>
> Type: int · Default: **102400** (100 kibibytes) · Importance: high · Update Mode: **read-only**

**`socket.receive.buffer.bytes`**

> The SO_RCVBUF buffer of the socket server sockets. If the value is -1, the OS default will be used.
>
> Type: int · Default: **102400** (100 kibibytes) · Importance: high · Update Mode: **read-only**

**`socket.request.max.bytes`**

> The maximum number of bytes in a socket request
>
> Type: int · Default: **104857600** (100 mebibytes) · Importance: high · Update Mode: read-only

Two neighbouring configurations that matter when a broker suddenly has to serve many more, and much slower, connections:

**`num.network.threads`**

> The number of threads that the server uses for receiving requests from the network and sending responses to the network. Noted: each listener (except for controller listener) creates its own thread pool.
>
> Type: int · Default: **3** · Importance: high · Update Mode: **cluster-wide**

**`num.io.threads`**

> The number of threads that the server uses for processing requests, which may include disk I/O
>
> Type: int · Default: **8** · Importance: high · Update Mode: **cluster-wide**

**`queued.max.requests`**

> The number of queued requests allowed for data-plane, before blocking the network threads
>
> Type: int · Default: **500** · Importance: high · Update Mode: read-only

> 🧠 **Vì sao 102400 là quá nhỏ cho WAN.** Throughput tối đa của một kết nối TCP xấp xỉ `buffer / RTT`. Với buffer 100 KiB và RTT 80 ms giữa hai DC: `102400 / 0.08 ≈ 1,28 MB/s` cho **mỗi** kết nối, bất kể đường truyền rộng 10 Gb/s. Đó chính là *bandwidth-delay product*, và là lý do docs bảo tăng hai config này — chứ không phải "mua thêm băng thông". Lưu ý cả hai đều **read-only** → phải restart broker, nên đây là quyết định lúc thiết kế, không phải lúc sự cố.

---

## 📎 Đọc chéo trong tuần

| Câu hỏi của đề | Trả lời | Nguồn |
|---|---|---|
| DC cách xa, độ trễ cao hoặc không đoán được | **Cluster tách rời + replication** (MM2 hoặc Cluster Linking), RPO > 0 | trang này + [`confluent-multi-dc-architectures.md`](confluent-multi-dc-architectures.md) |
| 3 DC gần nhau, mạng ổn định < 100 ms, cần **RPO = 0** | **Stretch cluster** 3 DC, quorum trải cả 3 | [`confluent-multi-dc-architectures.md`](confluent-multi-dc-architectures.md) |
| Chỉ có **2 DC** nhưng vẫn muốn stretch | **2.5 DC**: DC thứ ba **chỉ chạy controller** để giữ quorum lẻ | [`confluent-multi-dc-architectures.md`](confluent-multi-dc-architectures.md) |
| Cần dữ liệu toàn cục để phân tích | **Aggregate cluster** (`A->K, B->K, C->K`) | trang này + [`kafka-geo-replication-mm2.md`](kafka-geo-replication-mm2.md) |
| Bắt buộc ghi xuyên WAN, throughput thấp dù băng thông rộng | Tăng `socket.send.buffer.bytes` / `socket.receive.buffer.bytes` (mặc định 102400) | trang này |
