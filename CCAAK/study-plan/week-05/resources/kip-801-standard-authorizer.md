# KIP-801 — Implement an Authorizer that stores metadata in `__cluster_metadata` (`StandardAuthorizer`)

> **Nguồn (official):** https://cwiki.apache.org/confluence/display/KAFKA/KIP-801%3A+Implement+an+Authorizer+that+stores+metadata+in+__cluster_metadata
> **Nguồn phụ đã crawl được:** https://issues.apache.org/jira/browse/KAFKA-13646 (KAFKA-13646 *"Implement KIP-801: KRaft authorizer"*, Colin McCabe, tạo 2022-02-04, resolve 2022-02-09, **Fix Version 3.2.0**, PR #11649)
> **Tuần:** 5 — Security administration · **Loại:** Apache Kafka Improvement Proposal
> ⚠️ **Trang cwiki KHÔNG crawl được** (WebFetch trả về rỗng ở cả hai dạng URL). Phần "Nội dung" bên dưới **(không crawl được, tổng hợp từ docs)** — dựa trên trang JIRA đã crawl, trang [Authorization and ACLs 4.3](https://kafka.apache.org/43/security/authorization-and-acls/) đã crawl, và [Confluent ACL overview](https://docs.confluent.io/platform/current/security/authorization/acls/overview.html) đã crawl. Đối chiếu lại link gốc trước ngày thi.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- **Tại sao cần KIP-801:** `AclAuthorizer` (tên đầy đủ `kafka.security.authorizer.AclAuthorizer`) lưu ACL trong **znode ZooKeeper** và theo dõi thay đổi bằng **ZooKeeper watch**. Cluster KRaft **không có ZooKeeper** → class đó không thể hoạt động. KIP-801 tạo authorizer đầu tiên **không phụ thuộc ZooKeeper**.
- **Tên class phải thuộc**: `org.apache.kafka.metadata.authorizer.StandardAuthorizer` — chú ý package là **`org.apache.kafka.metadata.authorizer`**, không phải `kafka.security.authorizer`.
- **Có từ Apache Kafka 3.2.0** (KAFKA-13646). Từ **4.0 ZooKeeper bị gỡ hoàn toàn** → `AclAuthorizer` **không còn trong binary**. Khai nó vào `authorizer.class.name` ở 4.x thì **node không khởi động được**, lỗi dạng:
  `org.apache.kafka.common.config.ConfigException: Invalid value kafka.security.authorizer.AclAuthorizer for configuration authorizer.class.name: Class kafka.security.authorizer.AclAuthorizer could not be found.`
- **ACL được lưu ngay trong metadata log `__cluster_metadata`** như một loại record metadata. Hệ quả vận hành: ACL **được replicate bằng Raft**, có cùng bảo đảm bền vững như metadata topic/partition, và **được khôi phục tự động** khi node restart (không cần backup riêng như thời ZooKeeper).
- **Ai ghi, ai đọc:** thay đổi ACL (`CreateAcls` / `DeleteAcls`) đi tới **active controller**, controller ghi record vào metadata log; **broker và standby controller đọc log liên tục** tới last stable offset rồi cập nhật bản đồ ACL trong bộ nhớ.
- **Hệ quả quan trọng nhất cho người vận hành:** việc áp dụng ACL là **bất đồng bộ, eventually consistent**. `kafka-acls.sh --add` trả về thành công khi **controller** đã ghi record, không có nghĩa **mọi broker** đã thấy. Trong vài trăm mili-giây tiếp theo client vẫn có thể nhận `TopicAuthorizationException` — **đừng vội kết luận ACL sai**, hãy thử lại rồi mới điều tra.
- Phải khai `authorizer.class.name` trên **mọi node broker VÀ mọi node controller**. Controller cần authorizer vì nó là nơi ủy quyền các request được broker **chuyển tiếp qua Envelope**.
- **Early start listeners / thứ tự khởi động:** node phải phục vụ được lưu lượng controller ngay cả khi chưa nạp xong toàn bộ ACL từ metadata log. Kafka xử lý bằng cách cho listener của controller (và inter-broker) khởi động sớm, còn listener của client chỉ mở khi authorizer đã sẵn sàng — nhờ vậy không có khe thời gian nào client được vào mà ACL chưa nạp.
- `super.users` và `allow.everyone.if.no.acl.found` hoạt động **y hệt** `AclAuthorizer`, nên tài liệu ACL cũ vẫn đúng về mặt ngữ nghĩa — **chỉ tên class và nơi lưu là đổi**.
- ⚠️ Nhiều tài liệu bên thứ ba viết "*StandardAuthorizer is the default authorizer in KRaft clusters*". Hiểu cho đúng: nó là **authorizer mặc định được chọn khi bạn bật authorization**, còn `authorizer.class.name` bản thân nó **mặc định rỗng** → cluster mới dựng **không có authorization nào cả**. Đề hỏi "cluster mới dựng, chưa đặt `authorizer.class.name`, ai được làm gì?" → **mọi người làm được mọi thứ**.

---

## 📄 Nội dung (không crawl được, tổng hợp từ docs)

### Motivation

Prior to KIP-500, Kafka stored its ACLs in ZooKeeper. The built-in authorizer, `kafka.security.authorizer.AclAuthorizer`, read ACLs from ZooKeeper znodes at startup and installed ZooKeeper watches so that later changes were propagated to every broker. Because KRaft clusters do not run ZooKeeper at all, that authorizer cannot be used: there is no znode to read and no watch to install. A secure KRaft cluster therefore needs a new built-in authorizer that keeps its ACLs in the cluster metadata log.

### Proposed changes

KIP-801 adds `org.apache.kafka.metadata.authorizer.StandardAuthorizer`, which provides the same behaviour as `AclAuthorizer` but stores ACLs as records in the `__cluster_metadata` topic:

- `CreateAcls` and `DeleteAcls` requests are handled by the **active controller**, which appends `AccessControlEntryRecord` / `RemoveAccessControlEntryRecord` entries to the metadata log.
- Brokers and standby controllers **replay the metadata log** up to its last stable offset and maintain an in-memory index of ACLs, which is what the authorizer consults on every request.
- Because replication of the metadata log is asynchronous, an ACL change is visible on the controller before it is visible on every broker. Propagation is fast but **not instantaneous**; authorization is eventually consistent.

Configuration on every broker and controller node:

```
authorizer.class.name=org.apache.kafka.metadata.authorizer.StandardAuthorizer
```

The existing configurations keep their meaning:

```
super.users=User:admin;User:kafka
allow.everyone.if.no.acl.found=false
```

### Startup ordering and early start listeners

An authorizer that reads its data from the metadata log faces a bootstrap problem: the node has to accept connections in order to participate in the quorum and catch up on the log, but it must not serve client traffic before it knows the ACLs. Kafka resolves this by distinguishing **early start listeners** — the controller listener and the inter-broker listener — from client listeners. Early start listeners accept connections while the authorizer is still loading; client listeners are only opened once the authorizer reports that it has completed its initial load. The practical consequence is that there is never a window in which a client is authorized against an empty ACL set.

### Compatibility

- The change applies to **KRaft-based clusters only**. It has no impact on legacy ZooKeeper-based clusters.
- Configuring `StandardAuthorizer` on a ZooKeeper-based cluster (Kafka 3.x) throws a fatal exception at startup.
- Conversely, configuring `AclAuthorizer` on a KRaft cluster is not supported; from Kafka 4.0 the class no longer exists in the distribution, so the node fails to start with a `ConfigException` reporting that the class could not be found.
- ACL semantics — deny over allow, default deny, prefixed and literal patterns, super users — are unchanged, so existing ACL definitions and `kafka-acls.sh` commands migrate as-is.

### Operational notes

- ACLs live in the metadata log, so they are covered by the same durability and disaster-recovery story as the rest of cluster metadata. There is no separate ACL store to back up, but also no way to restore ACLs independently of the metadata log.
- `kafka-acls.sh` can talk either to a broker (`--bootstrap-server`) or directly to the controller quorum (`--bootstrap-controller`). The latter is useful when brokers are unhealthy but the controllers are up.
- Denied requests are recorded by the authorizer logger, which writes to `kafka-authorizer.log`. This is the audit trail for "which permission was actually missing".
