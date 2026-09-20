# Apache Kafka 4.3 Docs — Authorization and ACLs (`StandardAuthorizer`, `kafka-acls.sh`)

> **Nguồn (official):** https://kafka.apache.org/43/security/authorization-and-acls/
> **Tuần:** 7 — Security & Testing · **Loại:** Apache Kafka Docs (Security → Authorization and ACLs)
> ⚠️ Nội dung dưới đây được crawl tự động (qua curl + WebFetch, có rút gọn) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- Authorizer pluggable qua `authorizer.class.name`, phải extend `org.apache.kafka.server.authorizer.Authorizer`. KRaft dùng **`org.apache.kafka.metadata.authorizer.StandardAuthorizer`** trên **mọi node** (broker, controller, combined); ACL lưu trong **metadata log** (`__cluster_metadata`). `AclAuthorizer` (ZooKeeper) không còn ở 4.x.
- Câu định nghĩa ACL phải thuộc: "**Principal P is [Allowed|Denied] Operation O From Host H on any Resource R matching ResourcePattern RP**" (KIP-11 + KIP-290).
- **Không có ACL khớp → từ chối**, chỉ super user vào được. Đổi bằng `allow.everyone.if.no.acl.found=true` (chỉ áp dụng resource **không có ACL nào**; resource đã có ACL vẫn enforce). `super.users=User:Bob;User:Alice` — ngăn cách **`;`** vì DN của SSL có dấu phẩy; `User` **phân biệt hoa thường**.
- **KRaft principal forwarding**: request admin (CreateTopics…) gửi tới broker, broker forward tới active controller qua **Envelope** trên listener đầu của `controller.listener.names`; controller authorize Envelope bằng principal broker rồi authorize request gốc bằng principal client. Custom `principal.builder.class` phải implement `KafkaPrincipalSerde`.
- Principal SSL mặc định = **DN đầy đủ** (`CN=writeuser,OU=Unknown,…`) → `ssl.principal.mapping.rules` (`RULE:pattern/replacement/[LU]`, rule đầu khớp thắng, kết thúc `DEFAULT`); Kerberos → `sasl.kerberos.principal.to.local.rules`.
- `kafka-acls.sh`: action `--add`/`--remove`/`--list`; kết nối `--bootstrap-server` **hoặc** `--bootstrap-controller`; resource `--topic`/`--group`/`--cluster`/`--transactional-id`/`--delegation-token`/`--user-principal`; `--allow-principal`/`--deny-principal` (`User:name`); `--allow-host`/`--deny-host` **chỉ nhận IP** (mặc định `*`); `--operation` mặc định **`All`**.
- **`--resource-pattern-type`** mặc định **`literal`**; khi `--add` chỉ được `literal`/`prefixed`; khi `--list`/`--remove` thêm `any` (khớp tên chính xác mọi loại pattern) và **`match`** (liệt kê mọi ACL literal + wildcard + prefixed **ảnh hưởng** resource; cẩn thận khi kèm `--remove`).
- Shortcut: **`--producer`** = WRITE + DESCRIBE + **CREATE** trên topic; **`--consumer --group`** = READ + DESCRIBE topic + READ group; `--idempotent` (đi cùng `--producer`) thêm IdempotentWrite Cluster — "idempotence is enabled automatically if the producer is authorized to a particular transactional-id".
- 13 operation: Read, Write, Create, Delete, Alter, Describe, ClusterAction, DescribeConfigs, AlterConfigs, IdempotentWrite, CreateTokens, DescribeTokens, All. 6 resource type + error code: **Topic (29)**, **Group (30)**, **Cluster (31)**, **TransactionalId (53)**, DelegationToken, User.
- Bảng protocol → quyền phải nhớ: PRODUCE = Write Topic (+ Write TransactionalId nếu transactional, + IdempotentWrite Cluster nếu idempotent) · FETCH = Read Topic (follower: ClusterAction Cluster) · METADATA = Describe Topic (+ Create Cluster/Topic nếu auto-create) · OFFSET_COMMIT = **Read Group** (check trước) + Read Topic · OFFSET_FETCH = Describe Group + Describe Topic · JOIN/HEARTBEAT/LEAVE/SYNC_GROUP = Read Group · FIND_COORDINATOR = Describe Group / Describe TransactionalId · CREATE_TOPICS = Create Cluster **hoặc** Create Topic (2.0+) · INIT_PRODUCER_ID = Write TransactionalId / IdempotentWrite Cluster · ADD_PARTITIONS_TO_TXN = Write TransactionalId + Write Topic · ADD_OFFSETS_TO_TXN / TXN_OFFSET_COMMIT = Write TransactionalId + Read Group (+ Read Topic) · DESCRIBE_ACLS = Describe Cluster · CREATE/DELETE_ACLS = **Alter Cluster** · DESCRIBE/ALTER_CONFIGS = DescribeConfigs/AlterConfigs trên Cluster (broker config) hoặc Topic · CREATE_PARTITIONS = Alter Topic · DELETE_GROUPS = Delete Group · ALTER_USER_SCRAM_CREDENTIALS = Alter Cluster · ALTER_CLIENT_QUOTAS = AlterConfigs Cluster.
- Deny thắng Allow: ví dụ trong docs cho phép `User:'*'` Read từ mọi host nhưng `--deny-principal User:BadBob --deny-host 198.51.100.3` → BadBob từ IP đó bị chặn dù khớp Allow.

---

## 📄 Nội dung (trích từ tài liệu gốc)

Kafka ships with a pluggable authorization framework, which is configured with the `authorizer.class.name` property in the server configuration. Configured implementations must extend `org.apache.kafka.server.authorizer.Authorizer`. Kafka provides a default implementation which store ACLs in the cluster metadata (KRaft metadata log). For KRaft clusters, use the following configuration on all nodes (brokers, controllers, or combined broker/controller nodes):

```properties
authorizer.class.name=org.apache.kafka.metadata.authorizer.StandardAuthorizer
```

Kafka ACLs are defined in the general format of "Principal {P} is [Allowed|Denied] Operation {O} From Host {H} on any Resource {R} matching ResourcePattern {RP}". You can read more about the ACL structure in KIP-11 and resource patterns in KIP-290. In order to add, remove, or list ACLs, you can use the Kafka ACL CLI `kafka-acls.sh`.

**Behavior Without ACLs:** If a resource (R) does not have any ACLs defined, meaning that no ACL matches the resource, Kafka will restrict access to that resource. In this situation, only super users are allowed to access it.

**Changing the Default Behavior:** If you prefer that resources without any ACLs be accessible by all users (instead of just super users), you can change the default behavior. To do this, add the following line to your server.properties file:

```properties
allow.everyone.if.no.acl.found=true
```

With this setting enabled, if a resource does not have any ACLs defined, Kafka will allow access to everyone. If a resource has one or more ACLs defined, those ACL rules will be enforced as usual, regardless of the setting. One can also add super users in server.properties like the following (note that the delimiter is semicolon since SSL user names may contain comma). Default PrincipalType string "User" is case sensitive.

```properties
super.users=User:Bob;User:Alice
```

### KRaft Principal Forwarding

In KRaft clusters, admin requests such as CreateTopics and DeleteTopics are sent to the broker listeners by the client. The broker then forwards the request to the active controller through the first listener configured in `controller.listener.names`. Authorization of these requests is done on the controller node. This is achieved by way of an Envelope request which packages both the underlying request from the client as well as the client principal. When the controller receives the forwarded Envelope request from the broker, it first authorizes the Envelope request using the authenticated broker principal. Then it authorizes the underlying request using the forwarded principal.

All of this implies that Kafka must understand how to serialize and deserialize the client principal. The authentication framework allows for customized principals by overriding the `principal.builder.class` configuration. In order for customized principals to work with KRaft, the configured class must implement `org.apache.kafka.common.security.auth.KafkaPrincipalSerde` so that Kafka knows how to serialize and deserialize the principals. The default implementation `org.apache.kafka.common.security.authenticator.DefaultKafkaPrincipalBuilder` uses the Kafka RPC format.

### Customizing SSL User Name

By default, the SSL user name will be of the form "CN=writeuser,OU=Unknown,O=Unknown,L=Unknown,ST=Unknown,C=Unknown". One can change that by setting `ssl.principal.mapping.rules` to a customized rule in server.properties. This config allows a list of rules for mapping X.500 distinguished name to short name. The rules are evaluated in order and the first rule that matches a distinguished name is used to map it to a short name. Any later rules in the list are ignored.

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

Above rules translate distinguished name "CN=serviceuser,OU=ServiceUsers,O=Unknown,L=Unknown,ST=Unknown,C=Unknown" to "serviceuser" and "CN=adminUser,OU=Admin,O=Unknown,L=Unknown,ST=Unknown,C=Unknown" to "adminuser@admin". For advanced use cases, one can customize the name by setting a customized PrincipalBuilder: `principal.builder.class=CustomizedPrincipalBuilderClass`.

### Customizing SASL User Name

By default, the SASL user name will be the primary part of the Kerberos principal. One can change that by setting `sasl.kerberos.principal.to.local.rules` to a customized rule in server.properties. Each rule works in the same way as the `auth_to_local` in Kerberos configuration file (krb5.conf). An example of adding a rule to properly translate `user@MYDOMAIN.COM` to `user` while also keeping the default rule in place is:

```properties
sasl.kerberos.principal.to.local.rules=RULE:[1:$1@$0](.*@MYDOMAIN.COM)s/@.*//,DEFAULT
```

### Command Line Interface

Kafka Authorization management CLI can be found under bin directory with all the other CLIs. The CLI script is called `kafka-acls.sh`. Following lists all the options that the script supports:

| Option | Description | Default | Option type |
| --- | --- | --- | --- |
| `--add` | Indicates to the script that user is trying to add an acl. | | Action |
| `--remove` | Indicates to the script that user is trying to remove an acl. | | Action |
| `--list` | Indicates to the script that user is trying to list acls. | | Action |
| `--bootstrap-server` | A list of host/port pairs to use for establishing the connection to the Kafka cluster broker. Only one of --bootstrap-server or --bootstrap-controller option must be specified. | | Configuration |
| `--bootstrap-controller` | A list of host/port pairs to use for establishing the connection to the Kafka cluster controller. Only one of --bootstrap-server or --bootstrap-controller option must be specified. | | Configuration |
| `--command-config` | A property file containing configs to be passed to Admin Client. This option can only be used with --bootstrap-server option. | | Configuration |
| `--cluster` | Indicates to the script that the user is trying to interact with acls on the singular cluster resource. | | ResourcePattern |
| `--topic [topic-name]` | Indicates to the script that the user is trying to interact with acls on topic resource pattern(s). | | ResourcePattern |
| `--group [group-name]` | Indicates to the script that the user is trying to interact with acls on consumer-group resource pattern(s) | | ResourcePattern |
| `--transactional-id [transactional-id]` | The transactionalId to which ACLs should be added or removed. A value of * indicates the ACLs should apply to all transactionalIds. | | ResourcePattern |
| `--delegation-token [delegation-token]` | Delegation token to which ACLs should be added or removed. A value of * indicates ACL should apply to all tokens. | | ResourcePattern |
| `--user-principal [user-principal]` | A user resource to which ACLs should be added or removed. This is currently supported in relation with delegation tokens. A value of * indicates ACL should apply to all users. | | ResourcePattern |
| `--resource-pattern-type [pattern-type]` | Indicates to the script the type of resource pattern, (for --add), or resource pattern filter, (for --list and --remove), the user wishes to use. When adding acls, this should be a specific pattern type, e.g. 'literal' or 'prefixed'. When listing or removing acls, a specific pattern type filter can be used to list or remove acls from a specific type of resource pattern, or the filter values of 'any' or 'match' can be used, where 'any' will match any pattern type, but will match the resource name exactly, and 'match' will perform pattern matching to list or remove all acls that affect the supplied resource(s). WARNING: 'match', when used in combination with the '--remove' switch, should be used with care. | literal | Configuration |
| `--allow-principal` | Principal is in PrincipalType:name format that will be added to ACL with Allow permission. Default PrincipalType string "User" is case sensitive. You can specify multiple --allow-principal in a single command. | | Principal |
| `--deny-principal` | Principal is in PrincipalType:name format that will be added to ACL with Deny permission. You can specify multiple --deny-principal in a single command. | | Principal |
| `--principal` | Principal is in PrincipalType:name format that will be used along with --list option. This will list the ACLs for the specified principal. | | Principal |
| `--allow-host` | IP address from which principals listed in --allow-principal will have access. | if --allow-principal is specified defaults to * which translates to "all hosts" | Host |
| `--deny-host` | IP address from which principals listed in --deny-principal will be denied access. | if --deny-principal is specified defaults to * | Host |
| `--operation` | Operation that will be allowed or denied. Valid values are: Read, Write, Create, Delete, Alter, Describe, ClusterAction, DescribeConfigs, AlterConfigs, IdempotentWrite, CreateTokens, DescribeTokens, All | All | Operation |
| `--producer` | Convenience option to add/remove acls for producer role. This will generate acls that allows WRITE, DESCRIBE and CREATE on topic. | | Convenience |
| `--consumer` | Convenience option to add/remove acls for consumer role. This will generate acls that allows READ, DESCRIBE on topic and READ on consumer-group. | | Convenience |
| `--idempotent` | Enable idempotence for the producer. This should be used in combination with the --producer option. Note that idempotence is enabled automatically if the producer is authorized to a particular transactional-id. | | Convenience |
| `--force` | Convenience option to assume yes to all queries and do not prompt. | | Convenience |

### Examples

**Adding Acls.** Suppose you want to add an acl "Principals User:Bob and User:Alice are allowed to perform Operation Read and Write on Topic Test-Topic from IP 198.51.100.0 and IP 198.51.100.1":

```bash
$ bin/kafka-acls.sh --bootstrap-server localhost:9092 --add --allow-principal User:Bob --allow-principal User:Alice --allow-host 198.51.100.0 --allow-host 198.51.100.1 --operation Read --operation Write --topic Test-topic
```

By default, all principals that don't have an explicit acl that allows access for an operation to a resource are denied. In rare cases where an allow acl is defined that allows access to all but some principal we will have to use the --deny-principal and --deny-host option. For example, if we want to allow all users to Read from Test-topic but only deny User:BadBob from IP 198.51.100.3:

```bash
$ bin/kafka-acls.sh --bootstrap-server localhost:9092 --add --allow-principal User:'*' --allow-host '*' --deny-principal User:BadBob --deny-host 198.51.100.3 --operation Read --topic Test-topic
```

Note that `--allow-host` and `--deny-host` only support IP addresses (hostnames are not supported). You can add acls on any resource of a certain type, e.g. "Principal User:Peter is allowed to produce to any Topic from IP 198.51.200.0" by using the wildcard resource '*':

```bash
$ bin/kafka-acls.sh --bootstrap-server localhost:9092 --add --allow-principal User:Peter --allow-host 198.51.200.1 --producer --topic '*'
```

You can add acls on prefixed resource patterns, e.g. "Principal User:Jane is allowed to produce to any Topic whose name starts with 'Test-' from any host":

```bash
$ bin/kafka-acls.sh --bootstrap-server localhost:9092 --add --allow-principal User:Jane --producer --topic Test- --resource-pattern-type prefixed
```

Note, --resource-pattern-type defaults to 'literal', which only affects resources with the exact same name or, in the case of the wildcard resource name '*', a resource with any name.

**Removing Acls.** Removing acls is pretty much the same. The only difference is instead of --add option users will have to specify --remove option:

```bash
$ bin/kafka-acls.sh --bootstrap-server localhost:9092 --remove --allow-principal User:Bob --allow-principal User:Alice --allow-host 198.51.100.0 --allow-host 198.51.100.1 --operation Read --operation Write --topic Test-topic
$ bin/kafka-acls.sh --bootstrap-server localhost:9092 --remove --allow-principal User:Jane --producer --topic Test- --resource-pattern-type Prefixed
```

**List Acls.** To list all acls on the literal resource pattern Test-topic:

```bash
$ bin/kafka-acls.sh --bootstrap-server localhost:9092 --list --topic Test-topic
```

However, this will only return the acls that have been added to this exact resource pattern. Other acls can exist that affect access to the topic, e.g. any acls on the topic wildcard '*', or any acls on prefixed resource patterns. We can list all acls affecting Test-topic by using '--resource-pattern-type match':

```bash
$ bin/kafka-acls.sh --bootstrap-server localhost:9092 --list --topic '*'
$ bin/kafka-acls.sh --bootstrap-server localhost:9092 --list --topic Test-topic --resource-pattern-type match
```

**Adding or removing a principal as producer or consumer.** In order to add User:Bob as a producer of Test-topic:

```bash
$ bin/kafka-acls.sh --bootstrap-server localhost:9092 --add --allow-principal User:Bob --producer --topic Test-topic
```

Similarly to add Alice as a consumer of Test-topic with consumer group Group-1 we just have to pass --consumer option:

```bash
$ bin/kafka-acls.sh --bootstrap-server localhost:9092 --add --allow-principal User:Bob --consumer --topic Test-topic --group Group-1
```

Note that for consumer option we must also specify the consumer group. In order to remove a principal from producer or consumer role we just need to pass --remove option.

### Authorization Primitives

**Operations in Kafka:** Read, Write, Create, Delete, Alter, Describe, ClusterAction, DescribeConfigs, AlterConfigs, IdempotentWrite, CreateTokens, DescribeTokens, All.

**Resources in Kafka:**

- **Topic**: this simply represents a Topic. All protocol calls that are acting on topics (such as reading, writing them) require the corresponding privilege to be added. If there is an authorization error with a topic resource, then a `TOPIC_AUTHORIZATION_FAILED` (error code: 29) will be returned.
- **Group**: this represents the consumer groups in the brokers. All protocol calls that are working with consumer groups, like joining a group must have privileges with the group in subject. If the privilege is not given then a `GROUP_AUTHORIZATION_FAILED` (error code: 30) will be returned in the protocol response.
- **Cluster**: this resource represents the cluster. Operations that are affecting the whole cluster, like controlled shutdown are protected by privileges on the Cluster resource. If there is an authorization problem on a cluster resource, then a `CLUSTER_AUTHORIZATION_FAILED` (error code: 31) will be returned.
- **TransactionalId**: this resource represents actions related to transactions, such as committing. If any error occurs, then a `TRANSACTIONAL_ID_AUTHORIZATION_FAILED` (error code: 53) will be returned by brokers.
- **DelegationToken**: this represents the delegation tokens in the cluster. Actions, such as describing delegation tokens could be protected by a privilege on the DelegationToken resource (KIP-48).
- **User**: CreateToken and DescribeToken operations can be granted to User resources to allow creating and describing tokens for other users (KIP-373).

### Operations and Resources on Protocols (trích các dòng quan trọng)

| Protocol (API key) | Operation | Resource | Note |
| --- | --- | --- | --- |
| PRODUCE (0) | Write | TransactionalId | A transactional producer which has its transactional.id set requires this privilege. |
| PRODUCE (0) | IdempotentWrite | Cluster | An idempotent produce action requires this privilege. |
| PRODUCE (0) | Write | Topic | This applies to a normal produce action. |
| FETCH (1) | ClusterAction | Cluster | A follower must have ClusterAction on the Cluster resource in order to fetch partition data. |
| FETCH (1) | Read | Topic | Regular Kafka consumers need READ permission on each partition they are fetching. |
| LIST_OFFSETS (2) | Describe | Topic | |
| METADATA (3) | Describe | Topic | |
| METADATA (3) | Create | Cluster | If topic auto-creation is enabled, then the broker-side API will check for the existence of a Cluster level privilege. If it's found then it'll allow creating the topic, otherwise it'll iterate through the Topic level privileges (see the next one). |
| METADATA (3) | Create | Topic | This authorizes auto topic creation if enabled but the given user doesn't have a cluster level permission (above). |
| OFFSET_COMMIT (8) | Read | Group | An offset can only be committed if it's authorized to the given group and the topic too (see below). Group access is checked first, then Topic access. |
| OFFSET_COMMIT (8) | Read | Topic | Since offset commit is part of the consuming process, it needs privileges for the read action. |
| OFFSET_FETCH (9) | Describe | Group | Similarly to OFFSET_COMMIT, the application must have privileges on group and topic level too to be able to fetch. However in this case it requires describe access instead of read. Group access is checked first, then Topic access. |
| OFFSET_FETCH (9) | Describe | Topic | |
| FIND_COORDINATOR (10) | Describe | Group | The FIND_COORDINATOR request can be of "Group" type in which case it is looking for consumergroup coordinators. |
| FIND_COORDINATOR (10) | Describe | TransactionalId | This applies only on transactional producers and checked when a producer tries to find the transaction coordinator. |
| JOIN_GROUP (11) / HEARTBEAT (12) / LEAVE_GROUP (13) / SYNC_GROUP (14) | Read | Group | |
| DESCRIBE_GROUPS (15) | Describe | Group | |
| LIST_GROUPS (16) | Describe | Cluster, then Group | If none of the groups are authorized, then just an empty response will be sent back instead of an error. |
| SASL_HANDSHAKE (17) / API_VERSIONS (18) / SASL_AUTHENTICATE (36) | — | — | Part of the authentication / protocol handshake, therefore it's not possible to apply any kind of authorization here. |
| CREATE_TOPICS (19) | Create | Cluster | If there is no cluster level authorization then it won't return CLUSTER_AUTHORIZATION_FAILED but fall back to use topic level. |
| CREATE_TOPICS (19) | Create | Topic | This is applicable from the 2.0 release. |
| DELETE_TOPICS (20) / DELETE_RECORDS (21) | Delete | Topic | |
| INIT_PRODUCER_ID (22) | Write | TransactionalId | |
| INIT_PRODUCER_ID (22) | IdempotentWrite | Cluster | |
| ADD_PARTITIONS_TO_TXN (24) | Write | TransactionalId, then Write Topic | It first checks for the Write action on the TransactionalId resource, then it checks the Topic in subject. |
| ADD_OFFSETS_TO_TXN (25) | Write | TransactionalId, then Read Group | |
| END_TXN (26) | Write | TransactionalId | |
| TXN_OFFSET_COMMIT (28) | Write TransactionalId + Read Group + Read Topic | | |
| DESCRIBE_ACLS (29) | Describe | Cluster | |
| CREATE_ACLS (30) / DELETE_ACLS (31) | Alter | Cluster | |
| DESCRIBE_CONFIGS (32) | DescribeConfigs | Cluster (broker configs) / Topic (topic configs) | |
| ALTER_CONFIGS (33) / INCREMENTAL_ALTER_CONFIGS (44) | AlterConfigs | Cluster (broker configs) / Topic (topic configs) | |
| CREATE_PARTITIONS (37) | Alter | Topic | |
| DELETE_GROUPS (42) | Delete | Group | |
| OFFSET_DELETE (47) | Delete Group + Read Topic | | |
| DESCRIBE_CLIENT_QUOTAS (48) / ALTER_CLIENT_QUOTAS (49) | DescribeConfigs / AlterConfigs | Cluster | |
| DESCRIBE_USER_SCRAM_CREDENTIALS (50) / ALTER_USER_SCRAM_CREDENTIALS (51) | Describe / Alter | Cluster | |
| DESCRIBE_CLUSTER (60) | Describe | Cluster | |
| DESCRIBE_PRODUCERS (61) | Read | Topic | |
| CREATE_DELEGATION_TOKEN (38) | CreateTokens | User | Allows creating delegation tokens for the User resource. |
| DESCRIBE_DELEGATION_TOKEN (41) | Describe DelegationToken / DescribeTokens User | | |
