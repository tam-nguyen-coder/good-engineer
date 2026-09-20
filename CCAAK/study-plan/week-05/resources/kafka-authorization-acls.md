# Apache Kafka 4.3 Docs — Authorization and ACLs

> **Nguồn (official):** https://kafka.apache.org/43/security/authorization-and-acls/
> **Tuần:** 5 — Security administration · **Loại:** Apache Kafka Docs (Security → Authorization and ACLs)
> ⚠️ Nội dung dưới đây được crawl tự động (WebFetch, có rút gọn) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- Bật authorization trên **mọi node broker VÀ controller**: `authorizer.class.name=org.apache.kafka.metadata.authorizer.StandardAuthorizer`. Mặc định config này **rỗng** → cluster **không kiểm tra quyền gì cả**. Đặt trên broker mà quên controller thì các thao tác quản trị được chuyển tiếp lên controller sẽ không bị kiểm soát.
- **Câu định nghĩa ACL chuẩn** (học thuộc nguyên văn, đề hay trích): "*Principal {P} is [Allowed|Denied] Operation {O} From Host {H} on any Resource {R} matching ResourcePattern {RP}*".
- **Mặc định từ chối**: "*If a resource (R) does not have any ACLs defined, meaning that no ACL matches the resource, Kafka will restrict access to that resource*" — chỉ super user vào được. `allow.everyone.if.no.acl.found=true` đảo ngược điều đó, và **chỉ nới cho resource CHƯA có ACL nào**; resource đã có dù chỉ 1 ACL thì quay lại luật thường.
- **`super.users` ngăn cách bằng dấu chấm phẩy**, không phải dấu phẩy: `super.users=User:Bob;User:Alice`. Chữ `User` **phân biệt hoa thường**. Super user **bỏ qua toàn bộ** ACL và **không hỗ trợ wildcard**.
- **Deny thắng Allow** trong mọi trường hợp, kể cả khi Allow khớp rộng hơn (PREFIXED) còn Deny khớp hẹp (LITERAL).
- **6 resource type**: `Topic`, `Group`, `Cluster`, `TransactionalId`, `DelegationToken`, `User`.
- **13 operation**: `Read`, `Write`, `Create`, `Delete`, `Alter`, `Describe`, `ClusterAction`, `DescribeConfigs`, `AlterConfigs`, `IdempotentWrite`, `CreateTokens`, `DescribeTokens`, `All`.
- **4 pattern type** cho `--resource-pattern-type`: `literal` (mặc định), `prefixed`, `any`, `match`. ⚠️ `any` và `match` **chỉ dùng để liệt kê/xoá** (filter khi truy vấn), **không tạo được ACL** kiểu đó. `match` trả về mọi ACL ảnh hưởng tới tên resource đã cho (literal khớp + prefixed khớp + wildcard).
- Cờ tiện lợi: `--producer` = **Write + Describe + Create** trên Topic; `--consumer --group g` = **Read + Describe** trên Topic **cộng Read** trên Group; `--idempotent` thêm `IdempotentWrite` trên Cluster (chỉ cần cho broker cũ hơn 2.8).
- **Principal mapping**: cert TLS → `ssl.principal.mapping.rules` với mẫu `RULE:^CN=(.*?),OU=.*$/$1/` (thêm `/L` hoặc `/U` để ép chữ thường/hoa); Kerberos → `sasl.kerberos.principal.to.local.rules` dạng auth_to_local, ví dụ `RULE:[1:$1@$0](.*@MYDOMAIN.COM)s/@.*//,DEFAULT`.
- **KRaft**: broker **chuyển tiếp** request quản trị lên controller bằng **Envelope**. Controller ủy quyền **hai lần**: Envelope theo principal của **broker**, request bên trong theo principal của **client** được chuyển tiếp. `principal.builder.class` tùy biến phải implement `KafkaPrincipalSerde`, nếu không request sẽ không chuyển tiếp được.
- Có thể nối `--bootstrap-controller` thay `--bootstrap-server` khi quản ACL trực tiếp trên controller (hữu ích khi broker đang không lên).

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Enabling the authorizer

Kafka ships with a pluggable authorization framework, which is configured with the `authorizer.class.name` property in the server configuration. Configured implementations must extend `org.apache.kafka.server.authorizer.Authorizer`. Kafka provides a default implementation which stores ACLs in the cluster metadata (either ZooKeeper or the KRaft metadata log).

For KRaft clusters, use the following configuration on all nodes (brokers, controllers, or combined broker/controller nodes):

```
authorizer.class.name=org.apache.kafka.metadata.authorizer.StandardAuthorizer
```

Kafka ACLs are defined in the general format of "Principal {P} is [Allowed|Denied] Operation {O} From Host {H} on any Resource {R} matching ResourcePattern {RP}". You can read more about the ACL structure in KIP-11 and resource patterns in KIP-290.

In order to add, remove, or list ACLs, you can use the Kafka ACL CLI `kafka-acls.sh`. By default, if no ResourcePatterns match a specific Resource R, then R has no associated ACLs, and therefore no one other than super users is allowed to access R. If you want to change that behavior, you can include the following in the server configuration:

```
allow.everyone.if.no.acl.found=true
```

One can also add super users in server configuration like the following (note that the delimiter is semicolon since SSL user names may contain comma). Default `PrincipalType` string `User` is case sensitive.

```
super.users=User:Bob;User:Alice
```

### Customizing SSL user name

By default, the SSL user name will be of the form `CN=writeuser,OU=Unknown,O=Unknown,L=Unknown,ST=Unknown,C=Unknown`. One can change that by setting `ssl.principal.mapping.rules` to a customized rule in the server configuration. This config allows a list of rules for mapping X.500 distinguished name to short name. The rules are evaluated in order and the first rule that matches a distinguished name is used to map it to a short name. Any later rules in the list are ignored.

The format of `ssl.principal.mapping.rules` is a list where each rule starts with "RULE:" and contains an expression as the following formats. Default rule will return string representation of the X.500 certificate distinguished name. If the distinguished name matches the pattern, then the replacement command will be run over the name. This also supports lowercase/uppercase options, to force the translated result to be all lower/uppercase case. This is done by adding a "/L" or "/U" to the end of the rule.

```
RULE:pattern/replacement/
RULE:pattern/replacement/[LU]
```

Example `ssl.principal.mapping.rules` values are:

```
RULE:^CN=(.*?),OU=ServiceUsers.*$/$1/,
RULE:^CN=(.*?),OU=(.*?),O=(.*?),L=(.*?),ST=(.*?),C=(.*?)$/$1@$2/L,
RULE:^.*[Cc][Nn]=([a-zA-Z0-9.]*).*$/$1/L,
DEFAULT
```

Above rules translate distinguished name `CN=serviceuser,OU=ServiceUsers,O=Unknown,L=Unknown,ST=Unknown,C=Unknown` to `serviceuser` and `CN=adminUser,OU=Admin,O=Unknown,L=Unknown,ST=Unknown,C=Unknown` to `adminuser@admin`.

### Customizing SASL user name

By default, the SASL user name will be the primary part of the Kerberos principal. One can change that by setting `sasl.kerberos.principal.to.local.rules` to a customized rule in the server configuration. The format of `sasl.kerberos.principal.to.local.rules` is a list where each rule works in the same way as the auth_to_local in Kerberos configuration file (krb5.conf).

```
sasl.kerberos.principal.to.local.rules=RULE:[1:$1@$0](.*@MYDOMAIN.COM)s/@.*//,DEFAULT
```

### Command Line Interface

Kafka Authorization management CLI can be found under bin directory with all the other CLIs. The CLI script is called `kafka-acls.sh`. The following lists all the options that the script supports:

| Option | Description |
| --- | --- |
| `--add` | Indicates to the script that user is trying to add an ACL. |
| `--remove` | Indicates to the script that user is trying to remove an ACL. |
| `--list` | Indicates to the script that user is trying to list ACLs. |
| `--bootstrap-server` | A list of host/port pairs to use for establishing the connection to the Kafka cluster. |
| `--bootstrap-controller` | A list of host/port pairs to use for establishing the connection to the KRaft controller quorum. Only one of `--bootstrap-server` or `--bootstrap-controller` must be specified. |
| `--command-config` | A property file containing configs to be passed to Admin Client. |
| `--cluster` | Indicates to the script that the user is trying to interact with ACLs on the singular cluster resource. |
| `--topic [topic-name]` | Indicates to the script that the user is trying to interact with ACLs on topic resource pattern(s). |
| `--group [group-name]` | Indicates to the script that the user is trying to interact with ACLs on consumer-group resource pattern(s). |
| `--transactional-id [transactional-id]` | The transactionalId to which ACLs should be added or removed. |
| `--delegation-token [delegation-token]` | Delegation token to which ACLs should be added or removed. |
| `--resource-pattern-type [pattern-type]` | Indicates to the script the type of resource pattern (for `--add`) or resource pattern filter (for `--list` and `--remove`) the user wishes to use. When adding ACLs, this should be a specific pattern type, e.g. `literal` or `prefixed`. When listing or removing ACLs, a specific pattern type filter can be used to list or remove ACLs from a specific type of resource pattern, or the filter values of `any` or `match` can be used, where `any` will match any pattern type, but will match the resource name exactly, and `match` will perform pattern matching to list or remove all ACLs that affect the supplied resource(s). Default: `literal`. |
| `--allow-principal` | Principal is in `PrincipalType:name` format that will be added to ACL with Allow permission. Default `PrincipalType` string `User` is case sensitive. You can specify multiple `--allow-principal` in a single command. |
| `--deny-principal` | Principal is in `PrincipalType:name` format that will be added to ACL with Deny permission. |
| `--allow-host` | IP address from which principals listed in `--allow-principal` will have access. Default: if `--allow-principal` is specified defaults to `*` which translates to "all hosts". |
| `--deny-host` | IP address from which principals listed in `--deny-principal` will be denied access. |
| `--operation` | Operation that will be allowed or denied. Valid values are: Read, Write, Create, Delete, Alter, Describe, ClusterAction, DescribeConfigs, AlterConfigs, IdempotentWrite, CreateTokens, DescribeTokens, All. Default: All. |
| `--producer` | Convenience option to add/remove ACLs for producer role. This will generate ACLs that allows WRITE, DESCRIBE and CREATE on topic. |
| `--consumer` | Convenience option to add/remove ACLs for consumer role. This will generate ACLs that allows READ, DESCRIBE on topic and READ on consumer-group. |
| `--idempotent` | Enable idempotence for the producer. This should be used in combination with the `--producer` option. |
| `--force` | Convenience option to assume yes to all queries and do not prompt. |

### Examples

**Adding Acls**: Suppose you want to add an acl "Principals User:Bob and User:Alice are allowed to perform Operation Read and Write on Topic Test-Topic from IP 198.51.100.0 and IP 198.51.100.1". You can do that by executing the CLI with following options:

```
bin/kafka-acls.sh --bootstrap-server localhost:9092 --add --allow-principal User:Bob --allow-principal User:Alice --allow-host 198.51.100.0 --allow-host 198.51.100.1 --operation Read --operation Write --topic Test-topic
```

By default, all principals that don't have an explicit acl that allows access for an operation to a resource are denied. In rare cases where an allow acl is defined that allows access to all but some principal we will have to use the `--deny-principal` and `--deny-host` option. For example, if we want to allow all users to Read from Test-topic but only deny User:BadBob from IP 198.51.100.3 we can do so using following commands:

```
bin/kafka-acls.sh --bootstrap-server localhost:9092 --add --allow-principal User:* --allow-host '*' --deny-principal User:BadBob --deny-host 198.51.100.3 --operation Read --topic Test-topic
```

Note that `--allow-host` and `--deny-host` only support IP addresses (hostnames are not supported).

Above examples add acls to a topic by specifying `--topic [topic-name]` as the resource pattern option. Similarly user can add acls to cluster by specifying `--cluster` and to a consumer group by specifying `--group [group-name]`.

You can add acls on any resource of a certain type, e.g. suppose you wanted to add an acl "Principal User:Peter is allowed to produce to any Topic from IP 198.51.200.0". You can do that by using the wildcard resource `*`:

```
bin/kafka-acls.sh --bootstrap-server localhost:9092 --add --allow-principal User:Peter --allow-host 198.51.200.1 --producer --topic '*'
```

You can add acls on prefixed resource patterns, e.g. suppose you want to add an acl "Principal User:Jane is allowed to produce to any Topic whose name starts with Test- from any host". You can do that by executing the CLI with following options:

```
bin/kafka-acls.sh --bootstrap-server localhost:9092 --add --allow-principal User:Jane --producer --topic Test- --resource-pattern-type prefixed
```

Note, `--resource-pattern-type` defaults to `literal`, which only affects resources with the exact same name or, in the case of the wildcard resource name `*`, a resource with any name.

**Removing Acls**: Removing acls is pretty much the same. The only difference is instead of `--add` option users will have to specify `--remove` option.

**List Acls**: We can list acls for any resource by specifying the `--list` option with the resource. To list all acls on the literal resource pattern Test-topic, we can execute the CLI with following options:

```
bin/kafka-acls.sh --bootstrap-server localhost:9092 --list --topic Test-topic
```

However, this will only return the acls that have been added to this exact resource pattern. Other acls can exist that affect access to the topic, e.g. any acls on the topic wildcard `*`, or any acls on prefixed resource patterns. Acls on the wildcard resource pattern can be queried explicitly, but it is not possible to explicitly query all prefixed resource patterns that match Test-topic. However, we can use `--resource-pattern-type match` to list all acls affecting Test-topic:

```
bin/kafka-acls.sh --bootstrap-server localhost:9092 --list --topic Test-topic --resource-pattern-type match
```

This will list acls on all matching literal, wildcard and prefixed resource patterns.

**Adding or removing a principal as producer or consumer**: The most common use case for acl management are adding/removing a principal as producer or consumer so we added convenience options to handle these cases. In order to add User:Bob as a producer of Test-topic we can execute the following command:

```
bin/kafka-acls.sh --bootstrap-server localhost:9092 --add --allow-principal User:Bob --producer --topic Test-topic
```

Similarly to add Alice as a consumer of Test-topic with consumer group Group-1 we just have to pass `--consumer` option:

```
bin/kafka-acls.sh --bootstrap-server localhost:9092 --add --allow-principal User:Bob --consumer --topic Test-topic --group Group-1
```

Note that for consumer option we must also specify the consumer group.

### Authorization Primitives

Protocol calls are usually performing some operations on certain resources in Kafka. It is required to know the operations and resources to set up effective protection. In this section we'll list these operations and resources, then list the combination of these with the protocols to see the valid scenarios.

**Operations in Kafka**: `Read`, `Write`, `Create`, `Delete`, `Alter`, `Describe`, `ClusterAction`, `DescribeConfigs`, `AlterConfigs`, `IdempotentWrite`, `CreateTokens`, `DescribeTokens`, `All`.

**Resources in Kafka**:

- **Topic**: this simply represents a Topic. All protocol calls that are acting on topics (such as reading, writing them) require the corresponding privilege to be added.
- **Group**: this represents the consumer groups in the brokers. All protocol calls that are working with consumer groups, like joining a group must have privileges with the group in subject.
- **Cluster**: this resource represents the cluster. Operations that are affecting the whole cluster, like controlled shutdown are protected by privileges on the Cluster resource.
- **TransactionalId**: this resource represents actions related to transactions, such as committing. Essentially any producer that acts on behalf of a given transactional id must be authorized on that id.
- **DelegationToken**: this represents the delegation tokens in the cluster. Actions, such as describing delegation tokens could be protected by a privilege on the DelegationToken resource.
- **User**: `CreateToken` and `DescribeToken` operations can be granted to `User` resources to allow creating and describing tokens for other users.

### Operations and Resources on Protocols (selected rows)

| Protocol (API key) | Operation | Resource | Note |
| --- | --- | --- | --- |
| PRODUCE | Write | TransactionalId | An transactional producer which has its transactional.id set requires this privilege. |
| PRODUCE | IdempotentWrite | Cluster | An idempotent produce action requires this privilege (only on brokers older than 2.8). |
| PRODUCE | Write | Topic | This applies to a normal produce action. |
| FETCH | ClusterAction | Cluster | This applies to follower fetch. |
| FETCH | Read | Topic | Regular Kafka consumers need READ permission on each partition they are fetching. |
| LIST_OFFSETS | Describe | Topic | |
| METADATA | Describe | Topic | |
| METADATA | Create | Cluster | If topic auto-creation is enabled, then the broker-side API will check for the existence of a Cluster level privilege. |
| METADATA | Create | Topic | Applies if automatic topic creation is enabled and the given user has a Topic level permission. |
| OFFSET_COMMIT | Read | Group | An offset can only be committed if it's authorized to the given group and the topic too. |
| OFFSET_COMMIT | Read | Topic | |
| OFFSET_FETCH | Describe | Group | Similar to OFFSET_COMMIT, the application must be authorized on the group and the topic. |
| OFFSET_FETCH | Describe | Topic | |
| FIND_COORDINATOR | Describe | Group | The FIND_COORDINATOR request can be of "Group" type in which case it is looking for consumer group coordinators. |
| FIND_COORDINATOR | Describe | TransactionalId | This applies only to transactional producers. |
| JOIN_GROUP / SYNC_GROUP / HEARTBEAT / LEAVE_GROUP | Read | Group | |
| DESCRIBE_GROUPS | Describe | Group | |
| LIST_GROUPS | Describe | Cluster | |
| CREATE_TOPICS | Create | Cluster | If there is no Cluster level authorization then it won't return CLUSTER_AUTHORIZATION_FAILED but fall back to use topic level. |
| CREATE_TOPICS | Create | Topic | |
| DELETE_TOPICS | Delete | Topic | |
| DELETE_RECORDS | Delete | Topic | |
| INIT_PRODUCER_ID | Write | TransactionalId | |
| INIT_PRODUCER_ID | IdempotentWrite | Cluster | |
| ADD_PARTITIONS_TO_TXN | Write | TransactionalId / Topic | |
| ADD_OFFSETS_TO_TXN | Write | TransactionalId; Read | Group | |
| END_TXN | Write | TransactionalId | |
| TXN_OFFSET_COMMIT | Write | TransactionalId; Read | Group; Read | Topic | |
| DESCRIBE_CONFIGS | DescribeConfigs | Cluster / Topic | |
| ALTER_CONFIGS | AlterConfigs | Cluster / Topic | |
| ALTER_PARTITION_REASSIGNMENTS | Alter | Cluster | |
| CREATE_PARTITIONS | Alter | Topic | |
| DELETE_GROUPS | Delete | Group | |
| ELECT_LEADERS | Alter | Cluster | |
| CREATE_ACLS / DELETE_ACLS | Alter | Cluster | |
| DESCRIBE_ACLS | Describe | Cluster | |
| CREATE_DELEGATION_TOKEN | CreateTokens | User | |
| DESCRIBE_DELEGATION_TOKEN | DescribeTokens | User | |

### KRaft principal forwarding

In KRaft clusters, admin requests such as `CreateTopics` and `DeleteTopics` are sent to the broker listeners from the client. The broker then forwards the request to the active controller through the first listener configured in `controller.listener.names`. Authorization of these requests is done on the controller node. This is achieved by way of an `Envelope` request which packages both the underlying request from the client as well as the client principal. When the controller receives the forwarded `Envelope` request from the broker, it first authorizes the `Envelope` request using the authenticated broker principal. Then it authorizes the underlying request using the forwarded principal.

All of this implies that Kafka must understand how to serialize and deserialize the client principal. The authentication framework allows for customized principals by overriding the `principal.builder.class` configuration. In order for customized principals to work with KRaft, the configured class must implement `org.apache.kafka.common.security.auth.KafkaPrincipalSerde` so that Kafka knows how to serialize and deserialize the principals. The default implementation `org.apache.kafka.common.security.authenticator.DefaultKafkaPrincipalBuilder` uses the Kafka RPC format defined in the source code: `clients/src/main/resources/common/message/DefaultPrincipalData.json`.
