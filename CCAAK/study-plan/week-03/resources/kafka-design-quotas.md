# Apache Kafka Design — Quotas: 2 loại quota, 8 mức ưu tiên, cơ chế throttle

> **Nguồn (official):** https://kafka.apache.org/43/design/design/#quotas · https://kafka.apache.org/43/operations/multi-tenancy/
> **Tuần:** 3 — Cluster Config II: quotas · **Loại:** Apache Kafka 4.3 Documentation (Design + Operations)
> ⚠️ Nội dung dưới đây được crawl tự động từ trang gốc (có cắt bớt phần ngoài chủ đề) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- Kafka có **2 nhóm client quota** ở tầng design: **network bandwidth quota** (byte/s, từ 0.9) và **request rate quota** (% thời gian CPU của thread, từ 0.11). Cộng thêm **`controller_mutation_rate`** (KIP-599) giới hạn tốc độ **tạo/xoá/thêm partition** → tổng cộng **4 tên config quota** admin phải thuộc: `producer_byte_rate`, `consumer_byte_rate`, `request_percentage`, `controller_mutation_rate`.
- Danh tính client = cặp **(user principal, client-id)**. Cluster **không xác thực** thì principal là `ANONYMOUS` (do `PrincipalBuilder` quyết định). Quota áp cho **cả nhóm**: mọi instance cùng (user, client-id) **chia nhau** một quota.
- **8 mức ưu tiên** (khớp nguyên văn docs), lấy mức **khớp cụ thể nhất**: (1) user + client-id → (2) user + default client-id → (3) user → (4) default user + client-id → (5) default user + default client-id → (6) default user → (7) client-id → (8) default client-id.
- Quota **ghi vào metadata log**, mọi broker đọc và **có hiệu lực ngay**, **không cần rolling restart**. (Thế giới ZooKeeper cũ ghi vào znode `/config/users` — nhắc tới znode là dấu hiệu tài liệu lỗi thời.)
- Quota là **per-broker**, KHÔNG phải per-cluster. Đặt `producer_byte_rate=10485760` trên cluster 6 broker → client có thể ghi tới **10 MB/s × 6 = 60 MB/s** toàn cluster. Docs nói thẳng lý do: quota cluster-wide đòi cơ chế chia sẻ mức dùng giữa các broker, khó hơn cả việc cài đặt quota.
- **Cơ chế throttle = trì hoãn response, KHÔNG ném lỗi.** Broker tính độ trễ cần thiết, trả response **ngay** kèm `throttle_time_ms`, rồi **mute socket channel** của client cho tới hết thời gian đó. Client mới cũng tự ngừng gửi. ⇒ Triệu chứng kinh điển: **throughput bị chặn trần mà log hoàn toàn sạch, không exception nào**.
- Metric để xác nhận: phía **broker** `kafka.server:type={Produce|Fetch},user=...,client-id=...` với thuộc tính **`throttle-time`** (ms, lý tưởng = 0) và `byte-rate`; `kafka.server:type=Request,...` với `throttle-time` + `request-time`. Phía **client** là `produce-throttle-time-avg` / `produce-throttle-time-max` (producer) và `fetch-throttle-time-avg` / `fetch-throttle-time-max` (consumer).
- `request_percentage` tính theo **% của một thread**: quota `n%` là n% của **một** thread, trên tổng công suất **`(num.io.threads + num.network.threads) × 100`%**. Mặc định 8 + 3 = 11 thread → trần 1100%. Đặt `request_percentage=200` nghĩa là client được dùng **2 thread**.
- Cửa sổ đo: `quota.window.num` **11** mẫu × `quota.window.size.seconds` **1** giây (tương tự `controller.quota.window.num` 11 / 1s và `replication.quota.window.num` 11 / 1s). Docs giải thích vì sao dùng **nhiều cửa sổ nhỏ**: cửa sổ lớn gây "bùng nổ traffic rồi đứng im" — trải nghiệm tệ.
- Trong cluster multi-tenant, docs khuyên **request rate quota thường hiệu quả hơn bandwidth quota**, vì CPU broker bị chiếm mới là thứ làm giảm băng thông thực tế mà broker phục vụ được.

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Quotas

Kafka cluster has the ability to enforce quotas on requests to control the broker resources used by clients. Two types of client quotas can be enforced by Kafka brokers for each group of clients sharing a quota:

1. Network bandwidth quotas define byte-rate thresholds (since 0.9)
2. Request rate quotas define CPU utilization thresholds as a percentage of network and I/O threads (since 0.11)

### Why are quotas necessary?

It is possible for producers and consumers to produce/consume very high volumes of data or generate requests at a very high rate and thus monopolize broker resources, cause network saturation and generally DOS other clients and the brokers themselves. Having quotas protects against these issues and is all the more important in large multi-tenant clusters where a small set of badly behaved clients can degrade user experience for the well behaved ones. In fact, when running Kafka as a service this even makes it possible to enforce API limits according to an agreed upon contract.

### Client groups

The identity of Kafka clients is the user principal which represents an authenticated user in a secure cluster. In a cluster that supports unauthenticated clients, user principal is a grouping of unauthenticated users chosen by the broker using a configurable `PrincipalBuilder`. Client-id is a logical grouping of clients with a meaningful name chosen by the client application. The tuple (user, client-id) defines a secure logical group of clients that share both user principal and client-id.

Quotas can be applied to (user, client-id), user or client-id groups. For a given connection, the most specific quota matching the connection is applied. All connections of a quota group share the quota configured for the group. For example, if (user="test-user", client-id="test-client") has a produce quota of 10MB/sec, this is shared across all producer instances of user "test-user" with the client-id "test-client".

### Quota Configuration

Quota configuration may be defined for (user, client-id), user and client-id groups. It is possible to override the default quota at any of the quota levels that needs a higher (or even lower) quota. The mechanism is similar to the per-topic log config overrides. **User and (user, client-id) quota overrides are written to the metadata log. These overrides are read by all brokers and are effective immediately. This lets us change quotas without having to do a rolling restart of the entire cluster.** Default quotas for each group may also be updated dynamically using the same mechanism.

**The order of precedence for quota configuration is:**

1. matching user and client-id quotas
2. matching user and default client-id quotas
3. matching user quota
4. default user and matching client-id quotas
5. default user and default client-id quotas
6. default user quota
7. matching client-id quota
8. default client-id quota

### Network Bandwidth Quotas

Network bandwidth quotas are defined as the byte rate threshold for each group of clients sharing a quota. By default, each unique client group receives a fixed quota in bytes/sec as configured by the cluster. **This quota is defined on a per-broker basis.** Each group of clients can publish/fetch a maximum of X bytes/sec per broker before clients are throttled.

### Request Rate Quotas

Request rate quotas are defined as the percentage of time a client can utilize on request handler I/O threads and network threads of each broker within a quota window. **A quota of n% represents n% of one thread, so the quota is out of a total capacity of ((num.io.threads + num.network.threads) * 100)%.** Each group of clients may use a total percentage of upto n% across all I/O and network threads in a quota window before being throttled. Since the number of threads allocated for I/O and network threads are typically based on the number of cores available on the broker host, request rate quotas represent the total percentage of CPU that may be used by each group of clients sharing the quota.

### Enforcement

By default, each unique client group receives a fixed quota as configured by the cluster. This quota is defined on a per-broker basis. Each client can utilize this quota per broker before it gets throttled. **We decided that defining these quotas per broker is much better than having a fixed cluster wide bandwidth per client because that would require a mechanism to share client quota usage among all the brokers. This can be harder to get right than the quota implementation itself!**

**How does a broker react when it detects a quota violation?** In our solution, the broker first computes the amount of delay needed to bring the violating client under its quota and returns a response with the delay immediately. In case of a fetch request, the response will not contain any data. Then, the broker mutes the channel to the client, not to process requests from the client anymore, until the delay is over. Upon receiving a response with a non-zero delay duration, the Kafka client will also refrain from sending further requests to the broker during the delay. Therefore, requests from a throttled client are effectively blocked from both sides. Even with older client implementations that do not respect the delay response from the broker, the back pressure applied by the broker via muting its socket channel can still handle the throttling of badly behaving clients. Those clients who sent further requests to the throttled channel will receive responses only after the delay is over.

Byte-rate and thread utilization are measured over multiple small windows (e.g. 30 windows of 1 second each) in order to detect and correct quota violations quickly. Typically, having large measurement windows (for e.g. 10 windows of 30 seconds each) leads to large bursts of traffic followed by long delays which is not great in terms of user experience.

> 📌 **Ghi chú đối chiếu:** đoạn trên là ví dụ minh hoạ trong trang Design. Giá trị **mặc định thật** trong Broker Configs 4.3 là `quota.window.num` = **11** (10 cửa sổ trọn vẹn + 1 cửa sổ hiện tại) và `quota.window.size.seconds` = **1**.

### Bổ sung — Isolating tenants with quotas and rate limits (Operations → Multi-Tenancy)

Multi-tenant clusters should generally be configured with quotas, which protect against users (tenants) eating up too many cluster resources, such as when they attempt to write or read very high volumes of data, or create requests to brokers at an excessively high rate. This may cause network saturation, monopolize broker resources, and impact other clients—all of which you want to avoid in a shared environment.

**Client quotas:** Kafka supports different types of (per-user principal) client quotas. Because a client's quotas apply irrespective of which topics the client is writing to or reading from, they are a convenient and effective tool to allocate resources in a multi-tenant cluster. **Request rate quotas, for example, help to limit a user's impact on broker CPU usage by limiting the time a broker spends on the request handling path for that user, after which throttling kicks in. In many situations, isolating users with request rate quotas has a bigger impact in multi-tenant clusters than setting incoming/outgoing network bandwidth quotas, because excessive broker CPU usage for processing requests reduces the effective bandwidth the broker can serve.** Furthermore, administrators can also define quotas on topic operations—such as create, delete, and alter—to prevent Kafka clusters from being overwhelmed by highly concurrent topic operations (see **KIP-599 and the quota type `controller_mutation_rate`**).

**Server quotas:** Kafka also supports different types of broker-side quotas. For example, administrators can set a limit on the rate with which the broker accepts new connections, set the maximum number of connections per broker, or set the maximum number of connections allowed from a specific IP address.

### Bổ sung — quota metrics (Operations → Monitoring)

| Metric | MBean | Ghi chú của docs |
|---|---|---|
| Bandwidth quota metrics per (user, client-id), user or client-id | `kafka.server:type={Produce\|Fetch},user=([-.\w]+),client-id=([-.\w]+)` | Two attributes. `throttle-time` indicates the amount of time in ms the client was throttled. **Ideally = 0.** `byte-rate` indicates the data produce/consume rate of the client in bytes/sec. For (user, client-id) quotas, both user and client-id are specified. If per-client-id quota is applied to the client, user is not specified. If per-user quota is applied, client-id is not specified. |
| Request quota metrics per (user, client-id), user or client-id | `kafka.server:type=Request,user=([-.\w]+),client-id=([-.\w]+)` | Two attributes. `throttle-time` indicates the amount of time in ms the client was throttled. Ideally = 0. `request-time` indicates the percentage of time spent in broker network and I/O threads to process requests from client group. |
| Requests exempt from throttling | `kafka.server:type=Request` | `exempt-throttle-time` indicates the percentage of time spent in broker network and I/O threads to process requests that are exempt from throttling. |
| Producer client metric | `produce-throttle-time-avg` / `produce-throttle-time-max` | "The average / maximum time in ms a request was throttled by a broker" |
| Consumer client metric | `fetch-throttle-time-avg` / `fetch-throttle-time-max` | "The average / maximum throttle time in ms" |
