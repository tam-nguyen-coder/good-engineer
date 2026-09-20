# Confluent Platform — Cluster Linking (DR và migration giữ nguyên offset)

> **Nguồn (official):** https://docs.confluent.io/platform/current/multi-dc-deployments/cluster-linking/index.html
> **Tuần:** 4 — Deployment Architecture · **Loại:** Confluent Platform Docs
> ⚠️ Nội dung dưới đây được crawl tự động (HTTP → Markdown, có rút gọn) — luôn đối chiếu link gốc để đầy đủ và cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- **Cluster Linking là tính năng của Confluent Server / Confluent Cloud, KHÔNG có trong Apache Kafka thuần.** Lab trên `apache/kafka:4.3.1` **không chạy được** — đây chính là điểm phân biệt mà CCAAK hay hỏi.
- **Cơ chế:** broker của cluster đích **kéo (pull) trực tiếp** từ broker nguồn, giống như một follower liên cluster. *"Cluster Linking does not require running Connect to move messages between clusters"* → không có Connect worker, không có connector, không có task để vận hành.
- **Giữ nguyên offset byte-for-byte.** Docs: *"byte-for-byte replication"* với *"globally consistent offsets and identical content across partitions"*. Hệ quả: **không cần offset translation**, consumer failover sang đích và `seek` đúng offset cũ.
- **Mirror topic là read-only ở cluster đích.** Muốn ghi vào nó phải **promote/failover** trước (mirror topic chuyển thành topic bình thường). Đây là khác biệt vận hành lớn so với MM2 (topic đích của MM2 là topic ghi được bình thường).
- **Tên topic giữ nguyên** (không có tiền tố `{source}.`) — nên Cluster Linking **một chiều tại một thời điểm**; muốn hai chiều phải tạo **2 link đơn hướng** riêng.
- Tự **sync consumer offset** và **sync ACL** sang đích → đó là thứ khiến RTO thấp: ứng dụng bật lên ở đích là chạy tiếp, không phải dịch offset hay cấp lại ACL.
- **Use case chuẩn:** DR/failover (RTO và RPO thấp) · migration cluster/cloud · hybrid cloud bridge on-prem ↔ Confluent Cloud · chia sẻ dữ liệu giữa team/tổ chức.
- **Yêu cầu version:** đích **Confluent Server ≥ 7.8.0**; nguồn là Confluent Platform 7.8.x, Confluent Cloud, hoặc **Apache Kafka ≥ 3.8.x**; IBP ≥ 3.0 ở cả hai phía.
- **Giới hạn phải nhớ:** **không mirror được message transaction**; không hỗ trợ message format v0/v1; hai chiều cần 2 link.
- **So sánh nhanh với MM2:** cùng là replication **bất đồng bộ** (RPO > 0), nhưng MM2 cần Connect + đổi tên topic + dịch offset, còn Cluster Linking nằm trong broker + giữ tên + giữ offset. Nếu đề nói *"DR mà consumer phải tiếp tục đúng offset, ít bộ phận vận hành nhất"* → **Cluster Linking**; nếu đề nói *"Apache Kafka thuần / active-active"* → **MM2**.

---

## 📄 Nội dung (trích từ tài liệu gốc)

### What is Cluster Linking?

Cluster Linking enables direct connections between clusters to mirror topics with **byte-for-byte replication** while maintaining "globally consistent offsets and identical content across partitions." Unlike traditional replication tools, it requires no separate Connect infrastructure — the functionality is "built into Confluent Server and Confluent Cloud."

Cluster Linking makes it easy to build multi-datacenter, multi-region, and hybrid cloud deployments. Because it is a broker-native pull mechanism, it eliminates the dependency on external components and simplifies multi-datacenter deployments.

### Key differences from MirrorMaker 2

The primary distinction is architectural: "Cluster Linking does not require running Connect to move messages between clusters." Instead, it operates as a broker-native pull mechanism, eliminating dependency on external components and simplifying multi-datacenter deployments.

Cluster Linking also preserves offsets, so applications that fail over to the destination cluster do not require custom offset translation logic.

### Mirror topics

Mirror topics are created by and owned by a cluster link. They are **read-only** on the destination cluster: they get their messages from their source topic, and they are byte-for-byte identical to the source topic. Mirror topics replicate topic data and metadata, including consumer offsets.

Because mirror topics carry the same name as their source topics and are read-only, an application that is moved to the destination cluster reads exactly the same topic names it read before.

### Primary use cases

**Disaster recovery and failover.** Build recovery strategies achieving "low recovery time objectives (RTOs) and minimal data loss through low recovery point objectives (RPOs)."

**Cluster migration.** "Migrate from an older cluster to one in a newer environment, region, or cloud" with preserved offsets enabling seamless application failover.

**Hybrid cloud.** "Create a secure, scalable bridge to cloud by linking an on-premises Confluent Platform cluster in a private cloud to a Confluent Cloud cluster."

**Data sharing.** "Exchange data between different teams, lines of business, and organizations" while isolating resource consumption.

### Consumer offset synchronization

Cluster Linking automatically syncs consumer offsets when enabled, allowing consumers to resume processing from their previous position during failover scenarios without manual intervention. Offset sync is controlled by the link configuration (`consumer.offset.sync.enable`) and the set of groups to include or exclude (`consumer.offset.group.filters`).

### ACL synchronization

"Cluster Linking syncs access control lists (ACLs) between clusters," facilitating secure migration and failover by maintaining authorization rules across destinations.

### Platform and version requirements

- **Destination:** Confluent Server 7.8.0 or later.
- **Source:** Confluent Platform 7.8.x, Confluent Cloud, or Apache Kafka 3.8.x and later.
- **Protocol:** inter-broker protocol (IBP) 3.0 or later on both clusters.

### Notable limitations

- No support for messages in Kafka v0 or v1 message formats.
- **Transactional messages cannot be mirrored.**
- Mirror topics display incorrectly in Control Center without REST Proxy API v3 connectivity.
- **Bidirectional replication requires two separate unidirectional links.**

---

## 📄 Cấu hình mẫu (tham khảo — chạy trên Confluent Platform)

> Không chạy được trên `apache/kafka:4.3.1`. In ở đây để nhận diện cú pháp trong đề.

```properties
# ~/cluster-link.properties — cấu hình của một cluster link tại cluster ĐÍCH
bootstrap.servers=source-kafka-1:9092,source-kafka-2:9092
link.mode=DESTINATION
connection.mode=OUTBOUND

# Đồng bộ offset consumer group từ nguồn sang đích
consumer.offset.sync.enable=true
consumer.offset.sync.ms=30000
consumer.offset.group.filters={"groupFilters":[{"name":"*","patternType":"LITERAL","filterType":"INCLUDE"}]}

# Đồng bộ ACL
acl.sync.enable=true
acl.filters={"aclFilters":[{"resourceFilter":{"resourceType":"any","patternType":"any"},"accessFilter":{"operation":"any","permissionType":"any"}}]}

# Tự tạo mirror topic cho topic mới khớp prefix
auto.create.mirror.topics.enable=true
auto.create.mirror.topics.filters={"topicFilters":[{"name":"orders","patternType":"PREFIXED","filterType":"INCLUDE"}]}
```

```bash
# Tạo link ở cluster ĐÍCH
kafka-cluster-links --bootstrap-server dest-kafka:9092 \
  --create --link my-dr-link --config-file cluster-link.properties

# Tạo mirror topic (read-only) cho topic "orders" của nguồn
kafka-mirrors --create --mirror-topic orders --link my-dr-link --bootstrap-server dest-kafka:9092

# Theo dõi độ trễ mirror
kafka-mirrors --describe --link my-dr-link --bootstrap-server dest-kafka:9092

# FAILOVER: biến mirror topic thành topic ghi được
kafka-mirrors --failover --topics orders --bootstrap-server dest-kafka:9092
# hoặc dừng mirroring "sạch" khi nguồn còn sống (migration có kiểm soát):
kafka-mirrors --promote --topics orders --bootstrap-server dest-kafka:9092
```

> 📌 `--promote` dùng khi nguồn **còn sống** (chờ mirror đuổi kịp rồi mới cắt → không mất dữ liệu). `--failover` dùng khi nguồn **đã chết** (cắt ngay, chấp nhận RPO > 0).
