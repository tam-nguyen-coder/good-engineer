# Confluent Platform — ACLs for authorization (quản trị ở quy mô)

> **Nguồn (official):** https://docs.confluent.io/platform/current/security/authorization/acls/overview.html
> **Tuần:** 5 — Security administration · **Loại:** Confluent Platform Docs (Security → Authorization → ACLs overview)
> ⚠️ Nội dung dưới đây được crawl tự động (WebFetch, có rút gọn) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- Định nghĩa ngắn gọn Confluent dùng: "*An ACL grants or denies a principal (a user or service) permission to perform a specific operation on a resource*". Trên cluster KRaft, thực thi bởi **`StandardAuthorizer`** khai qua `authorizer.class.name`.
- **Hình dạng principal đổi theo cách xác thực** — đây là chỗ hay sai khi viết ACL:
  - **TLS/mTLS**: subject của cert, ví dụ `CN=quickstart.confluent.io,OU=TEST,O=Sales` (toàn bộ DN, trừ khi có mapping rule).
  - **SASL/Kerberos**: `kafka-client@hostname.com`.
  - **SASL/PLAIN hoặc SCRAM**: chuỗi đơn giản — `alice`, `admin`, `billing_etl_job_03`.
- Nguyên tắc vận hành ở quy mô: "*create one principal per application and give each principal only the ACLs required*". Một service = một principal, **không dùng chung tài khoản** — nếu không thì audit và thu hồi đều vô nghĩa.
- `User:*` áp cho mọi user, nhưng **wildcard không dùng được cho super user** — `super.users` phải liệt kê từng principal.
- **5 nhóm resource** Confluent liệt kê: Cluster · Topic · Group · Transactional ID · Delegation Token.
- **Implicitly-derived operations** (rất hay bị bỏ sót khi tính "quyền tối thiểu"): cấp **READ / WRITE / DELETE** thì **tự có DESCRIBE**; cấp **ALTER_CONFIGS** thì **tự có DESCRIBE_CONFIGS**. Vì vậy `--producer` in ra 3 dòng ACL nhưng thực tế quyền hiệu lực nhiều hơn.
- **2 pattern type**: `LITERAL` (khớp đúng tên, mặc định) và `PREFIXED` (khớp theo tiền tố) — PREFIXED là **công cụ chính** để quản hàng trăm topic bằng vài chục ACL.
- "*In contexts where you have both allow and deny ACLs, deny ACLs take precedence*" — **Deny luôn thắng**, không có ngoại lệ.
- Mặc định: resource không có ACL nào → **chỉ super user** vào được. `allow.everyone.if.no.acl.found=true` đổi hành vi này và Confluent xếp vào loại **không nên dùng ở production**.
- `super.users=User:Bob;User:Alice` — **dấu chấm phẩy**. Bản thân **broker cần quyền super user** để làm replication và thao tác cluster.
- Chiến lược mở rộng Confluent khuyến nghị: (1) **PREFIXED ACL cho họ topic cùng mẫu truy cập**; (2) **ACL theo nhóm** nếu authorizer hỗ trợ (Confluent Server Authorizer / RBAC); (3) **quy ước đặt tên** cho principal và resource để tra cứu và gỡ lỗi nhanh. Consumer group cần **READ**; Kafka Connect và Schema Registry dùng đúng mẫu ACL thông thường trên các resource tương ứng.

---

## 📄 Nội dung (trích từ tài liệu gốc)

### ACL concepts

Access control lists (ACLs) provide important authorization controls for your enterprise's Apache Kafka cluster data. An ACL grants or denies a principal (a user or service) permission to perform a specific operation on a resource, such as a topic, consumer group, or cluster.

Kafka ACLs are enforced by an authorizer. For KRaft-based clusters, `StandardAuthorizer` is configured with the `authorizer.class.name` property.

### Principals

A principal is an entity that can be authenticated by the broker. When you configure an ACL, you specify the principal that the ACL applies to. The form of the principal depends on the security protocol used to authenticate:

- **TLS/mTLS**: the principal is the subject of the client certificate, for example `CN=quickstart.confluent.io,OU=TEST,O=Sales`.
- **SASL/Kerberos**: the principal takes a form such as `kafka-client@hostname.com`.
- **SASL/PLAIN and SASL/SCRAM**: the principal is a simple string such as `alice`, `admin` or `billing_etl_job_03`.

To follow best practices, create one principal per application and give each principal only the ACLs required.

You can use the wildcard principal `User:*` to apply an ACL to all users. Note that wildcards are not supported for super users.

### Resources

ACLs can be defined on the following resource types:

- **Cluster**: operations that affect the whole cluster, such as broker-level operations.
- **Topic**: read and write access to topic data and topic metadata.
- **Group**: consumer group and group protocol operations.
- **Transactional ID**: identifies a producer instance for exactly-once semantics.
- **Delegation Token**: lightweight authentication tokens.

### Operations and pattern types

Operations map to specific Kafka APIs for each resource. Common operations include READ, WRITE, CREATE, DELETE, ALTER, DESCRIBE and DESCRIBE_CONFIGS.

Two resource pattern types are available:

- **LITERAL**: matches the exact resource name. This is the default.
- **PREFIXED**: matches resource names that begin with the supplied prefix. This is useful for managing families of related topics.

Some operations are **implicitly derived** from others: granting READ, WRITE or DELETE also grants DESCRIBE, and granting ALTER_CONFIGS also grants DESCRIBE_CONFIGS.

### How ACLs are evaluated

In contexts where you have both allow and deny ACLs, deny ACLs take precedence.

By default, if no ACLs are associated with a resource, then only super users are allowed to access that resource. You can change this behavior with `allow.everyone.if.no.acl.found=true`, but this is discouraged in production environments.

Super users are specified in `server.properties` with a semicolon-delimited list:

```
super.users=User:Bob;User:Alice
```

Brokers must be granted super user status (or the equivalent ACLs) in order to perform replication and cluster operations.

### Managing ACLs at scale

- Use **prefixed ACLs** to efficiently manage families of topics that share the same access pattern, rather than writing one ACL per topic.
- Use **group-based ACLs** where the authorizer supports them (such as the Confluent Server Authorizer) so that adding a new application means adding a principal to a group rather than writing new ACLs.
- Adopt **naming conventions** for principals and resources. Consistent names make ACLs readable, make prefixed patterns usable, and make debugging authorization failures much faster.
- Consumer groups require READ permission on the Group resource in addition to READ on the topics being consumed.
- Kafka Connect and Schema Registry follow the standard ACL patterns for the operations they perform on cluster, topic and group resources.
