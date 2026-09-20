# Amazon MSK — What is MSK? Provisioned (Standard / Express brokers) vs Serverless + Ports + Quota

> **Nguồn (official):** https://docs.aws.amazon.com/msk/latest/developerguide/what-is-msk.html · https://docs.aws.amazon.com/msk/latest/developerguide/msk-broker-types-express.html · https://docs.aws.amazon.com/msk/latest/developerguide/serverless.html · https://docs.aws.amazon.com/msk/latest/developerguide/serverless-config.html · https://docs.aws.amazon.com/msk/latest/developerguide/limits.html · https://docs.aws.amazon.com/msk/latest/developerguide/port-info.html
> **Tuần:** 9 — Kafka trên AWS (`Amazon MSK`) + Design patterns · **Loại:** AWS Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất. Số liệu quota thay đổi theo thời gian → **đối chiếu quota** trước khi trả lời câu hỏi có con số.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- `Amazon MSK` = **fully managed Apache Kafka**: AWS lo **control plane** (tạo/sửa/xoá cluster, patch, thay broker hỏng, `ZooKeeper`/`KRaft` controller miễn phí), bạn dùng **data plane Kafka nguyên bản** (topic, produce/consume, tool & client cộng đồng **không đổi code**).
- 3 lựa chọn: **Provisioned Standard brokers** (chọn instance `kafka.m5/m7g/t3`, số broker/AZ, EBS 1–16.384 GiB/broker, storage auto-scaling, tiered storage) · **Provisioned Express brokers** (storage do AWS quản **không giới hạn**, **3×** throughput/broker, scale **20×** nhanh hơn, recovery **90%** nhanh hơn, **chỉ 3 AZ**, không maintenance window, không sửa được nhiều broker config) · **Serverless** (không chọn broker, trả theo throughput/partition-hour/storage, **chỉ IAM access control**, không hỗ trợ Kafka ACL).
- Ví dụ Express: `express.m7g.16xlarge` ghi an toàn **500 MBps**/broker so với **153,8 MBps** Standard tương đương; Express hỗ trợ Kafka **3.6 / 3.8 / 3.9 / 4.2**, KRaft từ **3.9**; chưa hỗ trợ đầy đủ Kafka Streams API và **KIP-932 share groups**.
- Quota Serverless (per cluster): ingress **200 MBps**, egress **400 MBps**, **5 MBps/partition** ingress, **10 MBps/partition** egress, **2.400 partition** (leader) cho topic thường / **120** cho compacted, **500 consumer group**, **3.000 client connection**, **100 connection/s**, message tối đa **8 MiB**, retention **không giới hạn** (mặc định `retention.ms` 7 ngày, `retention.bytes` 250 GiB), **10 cluster serverless/account**, **5 client VPC/cluster**.
- Quota Standard/Express: **90 broker/account**, **30 broker/cluster ZooKeeper** hoặc **60 broker/cluster KRaft**, **3.000 TCP connection IAM/broker**, **100 connection IAM/s/broker** (t3: 4/s).
- Ports: **9092** plaintext · **9094** TLS (public **9194**) · **9096** SASL/SCRAM (public **9196**) · **9098** IAM (public **9198**) · IPv6 dùng 20092/20094/20096/20098. Open Monitoring: JMX Exporter **11001**, Node Exporter **11002**.
- Serverless: broker config **không sửa được**; chỉ sửa topic-level `cleanup.policy` (chỉ lúc tạo), `compression.type`, `max.message.bytes` (≤ 8 MiB), `retention.ms`/`retention.bytes` (−1 = vô hạn), `message.timestamp.type`. Không sửa `segment.bytes`.
- Bẫy: Serverless **không có** Kafka ACL/SCRAM/mTLS → câu hỏi "cần mTLS" ⇒ Provisioned. "Không muốn quản EBS nhưng cần throughput cao/nhiều tính năng Provisioned" ⇒ **Express brokers**, không phải Serverless.

---

## 📄 Nội dung (trích từ tài liệu gốc)

### What is Amazon MSK?

Amazon Managed Streaming for Apache Kafka (Amazon MSK) is a fully managed service that enables you to build and run applications that use Apache Kafka to process streaming data. Amazon MSK provides the control-plane operations, such as those for creating, updating, and deleting clusters. It lets you use Apache Kafka data-plane operations, such as those for producing and consuming data. It runs open-source versions of Apache Kafka. This means existing applications, tooling, and plugins from partners and the Apache Kafka community are supported without requiring changes to application code.

These components describe the architecture of Amazon MSK:

- **Broker nodes** — When creating an Amazon MSK cluster, you specify how many broker nodes you want Amazon MSK to create in each Availability Zone. The minimum is one broker per Availability Zone. Each Availability Zone has its own VPC subnet. Amazon MSK Provisioned offers two broker types: **Standard brokers** and **Express brokers**. In **MSK Serverless**, MSK manages the broker nodes used to handle your traffic and you only provision your Kafka server resources at a cluster level.
- **ZooKeeper nodes** — Amazon MSK also creates the Apache ZooKeeper nodes for you (ZooKeeper-based clusters).
- **KRaft controllers** — In KRaft mode, cluster metadata is propagated within a group of Kafka controllers, which are part of the Kafka cluster, instead of across ZooKeeper nodes. KRaft controllers are included at **no additional cost** and require no additional setup or management from you.
- **Producers, consumers, and topic creators** — Amazon MSK lets you use Apache Kafka data-plane operations to create topics and to produce and consume data.
- **Cluster Operations** — Use the AWS Management Console, AWS CLI, or SDK APIs to perform control-plane operations (create/delete cluster, list clusters, view properties, update the number and type of brokers).

Amazon MSK detects and automatically recovers from the most common failure scenarios. When Amazon MSK detects a broker failure, it mitigates the failure or replaces the unhealthy broker with a new one. Where possible, it **reuses the storage from the older broker** to reduce the data that Kafka needs to replicate. After a recovery, producer and consumer apps continue to communicate with the **same broker IP addresses**.

### What is MSK Provisioned?

MSK Provisioned is an MSK cluster deployment option that allows you to manually configure and scale your Apache Kafka clusters. With MSK Provisioned, you can choose the instance types, storage volumes (Standard brokers), and number of broker nodes. You can also scale your cluster by adding or removing brokers. MSK Provisioned offers two main broker types – **Standard** and **Express**.

### Amazon MSK Express brokers

Express brokers for MSK Provisioned make Apache Kafka simpler to manage, more cost-effective to run at scale, and more elastic with low latency. Brokers include **pay-as-you-go storage that scales automatically** and requires no sizing, provisioning, or proactive monitoring. Depending on the instance size selected, each broker node can provide **up to 3x more throughput per broker, scale up to 20x faster, and recover 90% quicker** compared to standard Apache Kafka brokers. Express brokers come pre-configured with Amazon MSK's best practice defaults and enforce client throughput quotas.

- **No storage management**: elastic, virtually unlimited, pay-as-you-go, fully managed storage.
- **Faster scaling**: scale your cluster and move partitions up to 20x faster than on Standard brokers.
- **Higher throughput**: up to 3x more throughput per broker. For example, you can safely write data at up to **500 MBps with each m7g.16xlarge sized Express broker compared to 153.8 MBps** on the equivalent Standard broker.
- **Configured for high resilience**: guardrails on critical Apache Kafka configurations, throughput quotas, and capacity reservations for background operations and unplanned repairs.
- **No maintenance windows**: Amazon MSK automatically updates your cluster hardware on an ongoing basis.

Additional information:

- Express brokers work with Apache Kafka APIs, but **don't yet fully support KStreams API**.
- Express brokers are **only available in a 3 AZs configuration**.
- Express brokers are supported on Apache Kafka versions **3.6, 3.8, 3.9, and 4.2**; can be created with **KRaft mode from 3.9 onwards**.
- **KIP-932: Queues for Kafka is not yet supported** on Express brokers.

#### Express broker throughput throttle limits by broker size

| Instance size | Sustained ingress (MBps) | Max ingress (MBps) | Sustained egress (MBps) | Max egress (MBps) |
| --- | --- | --- | --- | --- |
| express.m7g.large | 15.6 | 23.4 | 31.2 | 58.5 |
| express.m7g.xlarge | 31.2 | 46.8 | 62.5 | 117 |
| express.m7g.2xlarge | 62.5 | 93.7 | 125 | 234.2 |
| express.m7g.4xlarge | 124.9 | 187.5 | 249.8 | 468.7 |
| express.m7g.8xlarge | 250 | 375 | 500 | 937.5 |
| express.m7g.12xlarge | 375 | 562.5 | 750 | 1406.2 |
| express.m7g.16xlarge | 500 | 750 | 1000 | 1875 |

Throughput per-partition: **max 15 MB/s**.

#### Express broker partition quota (leader + follower replicas)

| Broker size | Recommended partitions per broker | Maximum partitions per broker |
| --- | --- | --- |
| express.m7g.large | 1000 | 1500 |
| express.m7g.xlarge | 1000 | 2000 |
| express.m7g.2xlarge | 2500 | 4000 |
| express.m7g.4xlarge | 6000 | 8000 |
| express.m7g.8xlarge | 12000 | 16000 |
| express.m7g.12xlarge | 16000 | 24000 |
| express.m7g.16xlarge | 20000 | 32000 |

### What is MSK Serverless?

MSK Serverless is a cluster type for Amazon MSK that makes it possible for you to run Apache Kafka without having to manage and scale cluster capacity. It automatically provisions and scales capacity while managing the partitions in your topic. MSK Serverless offers a **throughput-based pricing model**, so you pay only for what you use.

MSK Serverless is fully compatible with Apache Kafka. It also integrates with: **AWS PrivateLink** (private connectivity), **IAM** for authentication and authorization using Java and non-Java languages, **AWS Glue Schema Registry**, **Amazon Managed Service for Apache Flink**, **AWS Lambda**.

> **Note:** MSK Serverless **requires IAM access control for all clusters. Apache Kafka access control lists (ACLs) are not supported.**

#### Configuration properties for MSK Serverless clusters

Amazon MSK sets broker configuration properties for serverless clusters. **You can't change these broker configuration property settings.** However, you can set or modify the following topic-level configuration properties. All other topic-level configuration properties are not configurable.

| Configuration property | Default | Editable | Maximum allowed value |
| --- | --- | --- | --- |
| cleanup.policy | Delete | Yes, but only at topic creation time | |
| compression.type | Producer | Yes | |
| max.message.bytes | 1048588 | Yes | 8388608 (8 MiB) |
| message.timestamp.difference.max.ms | long.max | Yes | |
| message.timestamp.type | CreateTime | Yes | |
| retention.bytes | 250 GiB | Yes | Unlimited; set to -1 for unlimited retention |
| retention.ms | 7 days | Yes | Unlimited; set to -1 for unlimited retention |

You can't modify the `segment.bytes` configuration for topics in MSK Serverless. When using the Apache Kafka command line tools with MSK Serverless you must include the `--command-config client.properties` parameter:

```
bin/kafka-configs.sh --bootstrap-server <bootstrap_server_string> --command-config client.properties \
  --entity-type topics --entity-name <topic_name> --alter --add-config retention.bytes=-1
```

#### MSK Serverless quota (per cluster unless stated)

| Dimension | Quota | Quota violation result |
| --- | --- | --- |
| Maximum ingress throughput | 200 MBps | Slowdown with throttle duration in response |
| Maximum egress throughput | 400 MBps | Slowdown with throttle duration in response |
| Maximum retention duration | Unlimited | N/A |
| Maximum number of client connections | 3000 | Connection close |
| Maximum connection attempts | 100 per second | Connection close |
| Maximum message size | 8 MiB | Request fails with INVALID_REQUEST |
| Maximum request rate | 15,000 per second | Slowdown |
| Maximum rate of topic management API requests | 2 per second | Slowdown |
| Maximum fetch bytes per request | 55 MB | Request fails with INVALID_REQUEST |
| Maximum number of consumer groups | 500 | JoinGroup request fails |
| Maximum number of partitions (leaders) | 2400 for non-compacted topics; 120 for compacted topics | Request fails with INVALID_REQUEST |
| Maximum rate of partition creation and deletion | 250 in 5 minutes | THROUGHPUT_QUOTA_EXCEEDED |
| Maximum ingress throughput per partition | 5 MBps | Slowdown |
| Maximum egress throughput per partition | 10 MBps | Slowdown |
| Maximum partition size (compacted topics) | 250 GB | THROUGHPUT_QUOTA_EXCEEDED |
| Maximum number of client VPCs per serverless cluster | 5 | |
| Maximum number of serverless clusters per account | 10 | |

### Amazon MSK Standard broker quota

| Dimension | Quota | Notes |
| --- | --- | --- |
| Brokers per account | 90 | Adjustable via Service Quotas |
| Brokers per cluster | 30 for ZooKeeper-based clusters; 60 for KRaft-based clusters | Adjustable |
| Minimum storage per broker | 1 GiB | |
| Maximum storage per broker | 16384 GiB | |
| Maximum TCP connections per broker (IAM access control) | 3000 | Adjust `listener.name.client_iam.max.connections` (risk of unavailability) |
| Maximum TCP connections rate per broker (IAM) | 100 per second (M5 and M7g); 4 per second (t3) | Set client `reconnect.backoff.ms` to handle retries |
| Maximum TCP connections per broker (non-IAM) | N/A | Not enforced; monitor CPU/memory |
| Configurations per account | 100 | |
| Configuration revisions per account | 50 | |

Express broker quota: same brokers per account/cluster; **Maximum storage: Unlimited**; max ingress per broker recommended 15.6–500 MBps, egress 31.2–1000 MBps based on instance size.

### Port information

Use the following port numbers so that Amazon MSK can communicate with client machines:

- To communicate with brokers in **plaintext**, use port **9092**.
- To communicate with brokers with **TLS encryption**, use port **9094** for access from within AWS and port **9194** for public access.
- To communicate with brokers with **SASL/SCRAM**, use port **9096** for access from within AWS and port **9196** for public access.
- To communicate with brokers in a cluster that is set up to use **IAM access control**, use port **9098** for access from within AWS and port **9198** for public access.
- IPv6 network type: plaintext **20092**, TLS **20094**, SASL/SCRAM **20096**, IAM **20098**.
