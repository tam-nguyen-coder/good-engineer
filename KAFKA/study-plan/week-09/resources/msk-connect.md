# Amazon MSK Connect — managed Kafka Connect (connector, custom plugin, worker configuration, capacity)

> **Nguồn (official):** https://docs.aws.amazon.com/msk/latest/developerguide/msk-connect.html · https://docs.aws.amazon.com/msk/latest/developerguide/msk-connect-connectors.html · https://docs.aws.amazon.com/msk/latest/developerguide/msk-connect-capacity.html · https://docs.aws.amazon.com/msk/latest/developerguide/msk-connect-workers.html · https://docs.aws.amazon.com/msk/latest/developerguide/limits.html#mkc-quota
> **Tuần:** 9 — Kafka trên AWS (`Amazon MSK`) + Design patterns · **Loại:** AWS Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- `MSK Connect` = **Kafka Connect được AWS quản** (Kafka Connect **2.7.1 hoặc 3.7.x**): AWS lo patch, provisioning, scaling, tự restart task lỗi. Dùng được với cluster MSK **hoặc Kafka tự host** miễn là có kết nối vào VPC.
- 3 tài nguyên: **Custom plugin** (zip/jar connector upload lên **S3** → tạo plugin) · **Worker configuration** (properties của worker, ví dụ `key.converter`/`value.converter`; mặc định MSK Connect là `StringConverter` cho cả key & value) · **Connector** (plugin + worker config + connector config + capacity + `service execution role` + Kafka cluster/auth/encryption + log delivery).
- **MCU** (MSK Connect Unit) = **1 vCPU + 4 GiB RAM**. Capacity 2 chế độ: **Provisioned** (số worker + MCU/worker cố định) · **Autoscaled** (min/max worker, MCU/worker, ngưỡng **scale-in/scale-out theo `CpuUtilization`**; MSK Connect **ghi đè `tasks.max`** tỉ lệ với số worker × MCU; tuỳ chọn *maximum autoscaling task count*). Vertical scale MCU **1–8 vCPU** qua `UpdateConnector`.
- Mỗi worker chiếm **1 IP** trong subnet của bạn → subnet phải đủ IP, nhất là khi autoscale.
- Log delivery: **CloudWatch Logs / S3 / Firehose**. Kết nối riêng tư tới source/sink qua **PrivateLink + private DNS**.
- Quota: **100 custom plugin**, **100 worker configuration**, **60 worker/account**, **10 worker/connector**.
- **Không có Connect REST API (8083) trực tiếp** cho bạn gọi — quản lý qua **API/CLI MSK Connect** (`aws kafkaconnect create-connector`, `update-connector`, `describe-connector`). Worker properties nhạy cảm (bootstrap, group.id, internal topics, rest.*, security) do AWS đặt, không ghi đè.
- Bẫy đề: "cần chạy Debezium/S3 sink không muốn quản Connect worker" ⇒ MSK Connect; "connector không scale theo load" ⇒ chuyển sang **autoscaled** capacity; "connector lỗi permission ghi S3" ⇒ **service execution role** thiếu quyền (không phải IAM của cluster).

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Understand MSK Connect

MSK Connect is a feature of Amazon MSK that makes it easy for developers to stream data to and from their Apache Kafka clusters. MSK Connect uses **Kafka Connect versions 2.7.1 or 3.7.x**, which are open-source frameworks for connecting Apache Kafka clusters with external systems such as databases, search indexes, and file systems. With MSK Connect, you can deploy fully managed connectors built for Kafka Connect that move data into or pull data from popular data stores like Amazon S3 and Amazon OpenSearch Service. You can deploy connectors developed by 3rd parties like **Debezium** for streaming change logs from databases into an Apache Kafka cluster, or deploy an existing connector with **no code changes**. Connectors automatically scale to adjust for changes in load and you pay only for the resources that you use.

Use **source connectors** to import data from external systems into your topics. With **sink connectors**, you can export data from your topics to external systems.

MSK Connect supports connectors for **any Apache Kafka cluster with connectivity to an Amazon VPC**, whether it is an MSK cluster or an independently hosted Apache Kafka cluster.

MSK Connect continuously monitors connector health and delivery state, patches and manages the underlying hardware, and autoscales the connectors to match changes in throughput.

#### Benefits of using Amazon MSK Connect

- **Elimination of operational overhead** — takes away the operational burden associated with patching, provisioning, and scaling of Apache Kafka Connect clusters; automates patching and version upgrades without disrupting workloads.
- **Automatic restarting of Connect tasks** — automatically recovers failed tasks (e.g. caused by breaching the TCP connection limit for Kafka, or task rebalancing when new workers join the consumer group for sink connectors).
- **Automatic horizontal and vertical scaling** — you only need to specify the number of workers in the auto scaling group and the utilization thresholds. Use the `UpdateConnector` API operation to vertically scale up or scale down the vCPUs **between 1 and 8 vCPUs**.
- **Private network connectivity** — privately connects to source and sink systems by using **AWS PrivateLink and private DNS names**.

### Understand connectors

A connector integrates external systems and Amazon services with Apache Kafka by continuously copying streaming data from a data source into your Apache Kafka cluster, or continuously copying data from your cluster into a data sink. A connector can also perform lightweight logic such as transformation, format conversion, or filtering data before delivering the data to a destination.

A **worker** is a Java virtual machine (JVM) process that runs the connector logic. Each worker creates a set of **tasks** that run in parallel threads and do the work of copying the data. Tasks don't store state, and can therefore be started, stopped, or restarted at any time in order to provide a resilient and scalable data pipeline.

### Understand connector capacity

The total capacity of a connector depends on the number of workers that the connector has, as well as on the number of **MSK Connect Units (MCUs)** per worker. **Each MCU represents 1 vCPU of compute and 4 GiB of memory.** The MCU memory pertains to the total memory of a worker instance and not the heap memory in use.

MSK Connect workers consume IP addresses in the customer-provided subnets. **Each worker uses one IP address** from one of the customer-provided subnets. Ensure that you have enough available IP addresses in the subnets, especially when autoscaling connectors where the number of workers can fluctuate.

To create a connector, you must choose between one of the following two capacity modes:

- **Provisioned** — Choose this mode if you know the capacity requirements for your connector. You specify two values: the number of workers, and the number of MCUs per worker.
- **Autoscaled** — Choose this mode if the capacity requirements for your connector are variable or if you don't know them in advance. When you use autoscaled mode, Amazon MSK Connect **overrides your connector's `tasks.max` property** with a value that is proportional to the number of workers running in the connector and the number of MCUs per worker. You specify:
  - The minimum and maximum number of workers.
  - The scale-in and scale-out percentages for CPU utilization, determined by the `CpuUtilization` metric. When `CpuUtilization` exceeds the scale-out percentage, MSK Connect increases the number of workers. When it goes below the scale-in percentage, MSK Connect decreases the number of workers. The number of workers always remains within the minimum and maximum.
  - The number of MCUs per worker.
  - (Optional) **Maximum autoscaling task count** — the maximum number of tasks allocated to the connector during autoscaling operations, an upper limit on task creation in relation to your Kafka topic partitions.

### Understand MSK Connect workers

Changes to the number of workers, whether due to a scaling event or due to unexpected failures, are automatically detected by the remaining workers. They coordinate to rebalance tasks across the set of remaining workers. **Connect workers use Apache Kafka's consumer groups to coordinate and rebalance.**

#### Default worker configuration

MSK Connect provides the following default worker configuration:

```
key.converter=org.apache.kafka.connect.storage.StringConverter
value.converter=org.apache.kafka.connect.storage.StringConverter
```

A custom worker configuration lets you override converter settings (for example `value.converter=org.apache.kafka.connect.json.JsonConverter`, `value.converter.schemas.enable=false`) and other worker-level properties. Properties that MSK Connect manages on your behalf (bootstrap servers, group id, internal storage topics, REST listener, security settings) cannot be overridden.

### Example: create a connector with the AWS CLI (Debezium Postgres → MSK, autoscaled)

```bash
aws kafkaconnect create-connector \
  --connector-name orders-cdc \
  --kafka-connect-version 3.7.x \
  --plugins '[{"customPlugin":{"customPluginArn":"<PLUGIN_ARN>","revision":1}}]' \
  --service-execution-role-arn arn:aws:iam::123456789012:role/msk-connect-role \
  --kafka-cluster '{"apacheKafkaCluster":{"bootstrapServers":"b-1...:9098,b-2...:9098","vpc":{"subnets":["subnet-a","subnet-b"],"securityGroups":["sg-1"]}}}' \
  --kafka-cluster-client-authentication '{"authenticationType":"IAM"}' \
  --kafka-cluster-encryption-in-transit '{"encryptionType":"TLS"}' \
  --capacity '{"autoScaling":{"mcuCount":1,"minWorkerCount":1,"maxWorkerCount":4,"scaleInPolicy":{"cpuUtilizationPercentage":20},"scaleOutPolicy":{"cpuUtilizationPercentage":80}}}' \
  --connector-configuration '{"connector.class":"io.debezium.connector.postgresql.PostgresConnector","tasks.max":"1","database.hostname":"...","topic.prefix":"shop","table.include.list":"public.outbox","transforms":"outbox","transforms.outbox.type":"io.debezium.transforms.outbox.EventRouter"}' \
  --log-delivery '{"workerLogDelivery":{"cloudWatchLogs":{"enabled":true,"logGroup":"/msk-connect/orders-cdc"}}}'
```

### MSK Connect quota

- Up to **100 custom plugins**.
- Up to **100 worker configurations**.
- Up to **60 connect workers**. If a connector is set up to have auto scaled capacity, then the maximum number of workers that the connector is set up to have is the number MSK Connect uses to calculate the quota for the account.
- Up to **10 workers per connector**.
