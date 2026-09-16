# Apache Kafka 4.3 Docs — Quotas (Design → Quotas + Operations → Setting quotas)

> **Nguồn (official):** https://kafka.apache.org/43/design/design/#quotas · https://kafka.apache.org/43/operations/basic-kafka-operations/#setting-quotas
> **Tuần:** 7 — Security & Testing · **Loại:** Apache Kafka Docs (Design + Basic Kafka Operations)
> ⚠️ Nội dung dưới đây được crawl tự động (qua curl + WebFetch, có rút gọn) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- 2 loại quota theo docs Design: **network bandwidth** (byte-rate, từ **0.9**) và **request rate** (% CPU của network + I/O thread, từ **0.11**). Thực tế còn `controller_mutation_rate` (KIP-599, số partition create/delete mỗi giây) — chỉ cần nhận diện.
- Mục đích: chống client "noisy" **DOS** broker và client khác trong cluster **multi-tenant**; cho phép "Kafka as a service" enforce hạn mức theo hợp đồng.
- Định danh client: **user principal** (authenticated; cluster không auth thì là nhóm user do `PrincipalBuilder` chọn) và **client-id** (chuỗi ứng dụng tự đặt). Quota áp cho `(user, client-id)`, `user`, hoặc `client-id`; **quota cụ thể nhất** thắng; **mọi connection trong nhóm chia sẻ chung** quota (ví dụ 10 MB/s chia cho mọi producer instance cùng user + client-id).
- **8 mức ưu tiên** (thuộc lòng thứ tự): (1) user + client-id khớp → (2) user khớp + default client-id → (3) user khớp → (4) default user + client-id khớp → (5) default user + default client-id → (6) default user → (7) client-id khớp → (8) default client-id.
- Override ghi vào **metadata log**, mọi broker đọc và **hiệu lực ngay**, **không cần rolling restart**; default quota cũng đổi động được. Mặc định client có quota **không giới hạn**.
- Byte-rate quota tính **per-broker**: mỗi nhóm được X bytes/s **trên mỗi broker** (docs giải thích: per-broker dễ đúng hơn cluster-wide vì không cần đồng bộ mức dùng giữa các broker). Trần cluster ≈ quota × số broker client ghi tới.
- Request quota: `n%` = n% của **1 thread**; tổng capacity = `(num.io.threads + num.network.threads) × 100`%; xấp xỉ **% CPU** broker mà nhóm client được dùng.
- **Cơ chế enforce**: broker tính **delay** đưa client về dưới quota → **trả response ngay kèm delay** (fetch response **không có data**) → **mute channel** không xử lý request của client tới hết delay; client hiện đại nhận delay ≠ 0 cũng **tự ngừng gửi**. Client cũ không tôn trọng delay vẫn bị back-pressure vì channel bị mute. → Client **không nhận exception**.
- Đo trong **nhiều window nhỏ** (ví dụ **30 window × 1 s**) để phát hiện/sửa vi phạm nhanh; window lớn (10 × 30 s) gây burst rồi delay dài, trải nghiệm xấu.
- CLI: `kafka-configs.sh --alter --add-config 'producer_byte_rate=1024,consumer_byte_rate=2048,request_percentage=200' --entity-type users --entity-name user1 [--entity-type clients --entity-name clientA]`; default bằng `--entity-default`; xem bằng `--describe` (bỏ `--entity-name` để liệt kê mọi entity của type đó).
- Metric phía client để nhận biết: `produce-throttle-time-avg/max` (producer), `fetch-throttle-time-avg/max` (consumer); phía broker: `kafka.server:type=Produce,user=…,client-id=…` với `throttle-time`, `byte-rate`.

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Quotas (Design)

Kafka cluster has the ability to enforce quotas on requests to control the broker resources used by clients. Two types of client quotas can be enforced by Kafka brokers for each group of clients sharing a quota:

- Network bandwidth quotas define byte-rate thresholds (since 0.9)
- Request rate quotas define CPU utilization thresholds as a percentage of network and I/O threads (since 0.11)

#### Why are quotas necessary?

It is possible for producers and consumers to produce/consume very high volumes of data or generate requests at a very high rate and thus monopolize broker resources, cause network saturation and generally DOS other clients and the brokers themselves. Having quotas protects against these issues and is all the more important in large multi-tenant clusters where a small set of badly behaved clients can degrade user experience for the well behaved ones. In fact, when running Kafka as a service this even makes it possible to enforce API limits according to an agreed upon contract.

#### Client groups

The identity of Kafka clients is the user principal which represents an authenticated user in a secure cluster. In a cluster that supports unauthenticated clients, user principal is a grouping of unauthenticated users chosen by the broker using a configurable `PrincipalBuilder`. Client-id is a logical grouping of clients with a meaningful name chosen by the client application. The tuple (user, client-id) defines a secure logical group of clients that share both user principal and client-id.

Quotas can be applied to (user, client-id), user or client-id groups. For a given connection, the most specific quota matching the connection is applied. All connections of a quota group share the quota configured for the group. For example, if (user="test-user", client-id="test-client") has a produce quota of 10MB/sec, this is shared across all producer instances of user "test-user" with the client-id "test-client".

#### Quota Configuration

Quota configuration may be defined for (user, client-id), user and client-id groups. It is possible to override the default quota at any of the quota levels that needs a higher (or even lower) quota. The mechanism is similar to the per-topic log config overrides. User and (user, client-id) quota overrides are written to the metadata log. These overrides are read by all brokers and are effective immediately. This lets us change quotas without having to do a rolling restart of the entire cluster. Default quotas for each group may also be updated dynamically using the same mechanism.

The order of precedence for quota configuration is:

1. matching user and client-id quotas
2. matching user and default client-id quotas
3. matching user quota
4. default user and matching client-id quotas
5. default user and default client-id quotas
6. default user quota
7. matching client-id quota
8. default client-id quota

#### Network Bandwidth Quotas

Network bandwidth quotas are defined as the byte rate threshold for each group of clients sharing a quota. By default, each unique client group receives a fixed quota in bytes/sec as configured by the cluster. This quota is defined on a per-broker basis. Each group of clients can publish/fetch a maximum of X bytes/sec per broker before clients are throttled.

#### Request Rate Quotas

Request rate quotas are defined as the percentage of time a client can utilize on request handler I/O threads and network threads of each broker within a quota window. A quota of n% represents n% of one thread, so the quota is out of a total capacity of ((num.io.threads + num.network.threads) * 100)%. Each group of clients may use a total percentage of upto n% across all I/O and network threads in a quota window before being throttled. Since the number of threads allocated for I/O and network threads are typically based on the number of cores available on the broker host, request rate quotas represent the total percentage of CPU that may be used by each group of clients sharing the quota.

#### Enforcement

By default, each unique client group receives a fixed quota as configured by the cluster. This quota is defined on a per-broker basis. Each client can utilize this quota per broker before it gets throttled. We decided that defining these quotas per broker is much better than having a fixed cluster wide bandwidth per client because that would require a mechanism to share client quota usage among all the brokers. This can be harder to get right than the quota implementation itself!

How does a broker react when it detects a quota violation? In our solution, the broker first computes the amount of delay needed to bring the violating client under its quota and returns a response with the delay immediately. In case of a fetch request, the response will not contain any data. Then, the broker mutes the channel to the client, not to process requests from the client anymore, until the delay is over. Upon receiving a response with a non-zero delay duration, the Kafka client will also refrain from sending further requests to the broker during the delay. Therefore, requests from a throttled client are effectively blocked from both sides. Even with older client implementations that do not respect the delay response from the broker, the back pressure applied by the broker via muting its socket channel can still handle the throttling of badly behaving clients. Those clients who sent further requests to the throttled channel will receive responses only after the delay is over.

Byte-rate and thread utilization are measured over multiple small windows (e.g. 30 windows of 1 second each) in order to detect and correct quota violations quickly. Typically, having large measurement windows (for e.g. 10 windows of 30 seconds each) leads to large bursts of traffic followed by long delays which is not great in terms of user experience.

### Setting quotas (Basic Kafka Operations)

Quotas overrides and defaults may be configured at (user, client-id), user or client-id levels as described here. By default, clients receive an unlimited quota. It is possible to set custom quotas for each (user, client-id), user or client-id group.

Configure custom quota for (user=user1, client-id=clientA):

```bash
$ bin/kafka-configs.sh --bootstrap-server localhost:9092 --alter --add-config 'producer_byte_rate=1024,consumer_byte_rate=2048,request_percentage=200' --entity-type users --entity-name user1 --entity-type clients --entity-name clientA
Updated config for entity: user-principal 'user1', client-id 'clientA'.
```

Configure custom quota for user=user1:

```bash
$ bin/kafka-configs.sh --bootstrap-server localhost:9092 --alter --add-config 'producer_byte_rate=1024,consumer_byte_rate=2048,request_percentage=200' --entity-type users --entity-name user1
Updated config for entity: user-principal 'user1'.
```

Configure custom quota for client-id=clientA:

```bash
$ bin/kafka-configs.sh --bootstrap-server localhost:9092 --alter --add-config 'producer_byte_rate=1024,consumer_byte_rate=2048,request_percentage=200' --entity-type clients --entity-name clientA
Updated config for entity: client-id 'clientA'.
```

It is possible to set default quotas for each (user, client-id), user or client-id group by specifying `--entity-default` option instead of `--entity-name`.

```bash
# default client-id quota for user=user1
$ bin/kafka-configs.sh --bootstrap-server localhost:9092 --alter --add-config 'producer_byte_rate=1024,consumer_byte_rate=2048,request_percentage=200' --entity-type users --entity-name user1 --entity-type clients --entity-default
Updated config for entity: user-principal 'user1', default client-id.

# default quota for user
$ bin/kafka-configs.sh --bootstrap-server localhost:9092 --alter --add-config 'producer_byte_rate=1024,consumer_byte_rate=2048,request_percentage=200' --entity-type users --entity-default
Updated config for entity: default user-principal.

# default quota for client-id
$ bin/kafka-configs.sh --bootstrap-server localhost:9092 --alter --add-config 'producer_byte_rate=1024,consumer_byte_rate=2048,request_percentage=200' --entity-type clients --entity-default
Updated config for entity: default client-id.
```

Here's how to describe the quota for a given (user, client-id):

```bash
$ bin/kafka-configs.sh --bootstrap-server localhost:9092 --describe --entity-type users --entity-name user1 --entity-type clients --entity-name clientA
Configs for user-principal 'user1', client-id 'clientA' are producer_byte_rate=1024,consumer_byte_rate=2048,request_percentage=200

$ bin/kafka-configs.sh --bootstrap-server localhost:9092 --describe --entity-type users --entity-name user1
Configs for user-principal 'user1' are producer_byte_rate=1024,consumer_byte_rate=2048,request_percentage=200

$ bin/kafka-configs.sh --bootstrap-server localhost:9092 --describe --entity-type clients --entity-name clientA
Configs for client-id 'clientA' are producer_byte_rate=1024,consumer_byte_rate=2048,request_percentage=200

$ bin/kafka-configs.sh --bootstrap-server localhost:9092 --describe --entity-type users --entity-default
Quota configs for the default user-principal are consumer_byte_rate=2048.0, request_percentage=200.0, producer_byte_rate=1024.0

$ bin/kafka-configs.sh --bootstrap-server localhost:9092 --describe --entity-type clients --entity-default
Quota configs for the default client-id are consumer_byte_rate=2048.0, request_percentage=200.0, producer_byte_rate=1024.0
```

If entity name is not specified, all entities of the specified type are described. For example, describe all users:

```bash
$ bin/kafka-configs.sh --bootstrap-server localhost:9092 --describe --entity-type users
Configs for user-principal 'user1' are producer_byte_rate=1024,consumer_byte_rate=2048,request_percentage=200
Configs for default user-principal are producer_byte_rate=1024,consumer_byte_rate=2048,request_percentage=200

$ bin/kafka-configs.sh --bootstrap-server localhost:9092 --describe --entity-type users --entity-type clients
Configs for user-principal 'user1', default client-id are producer_byte_rate=1024,consumer_byte_rate=2048,request_percentage=200
```

### Ghi chú thêm (tổng hợp từ Broker Configs / KIP-599, không nằm trong 2 trang trên)

- `controller_mutation_rate` (KIP-599, 2.7+): giới hạn số **partition mutation** (create topic / create partitions / delete topic) mỗi giây cho `(user, client-id)`/`user`/`client-id`, cùng cú pháp `kafka-configs.sh --add-config 'controller_mutation_rate=10'`. Khi vượt, controller trả `THROTTLING_QUOTA_EXCEEDED` (error code 89) kèm `throttle_time_ms` — khác byte-rate quota, đây là quota **có báo lỗi** cho client admin.
- Broker config liên quan: `quota.window.num` (mặc định **11** sample), `quota.window.size.seconds` (**1** s); `replication.quota.*` cho throttle replication (Tuần 8, `kafka-reassign-partitions.sh --throttle`).
- Producer Java expose `produce-throttle-time-avg` / `produce-throttle-time-max` (group `producer-metrics`); consumer expose `fetch-throttle-time-avg` / `fetch-throttle-time-max` (group `consumer-fetch-manager-metrics`). `kafka-producer-perf-test.sh --print-metrics` in các metric này.
