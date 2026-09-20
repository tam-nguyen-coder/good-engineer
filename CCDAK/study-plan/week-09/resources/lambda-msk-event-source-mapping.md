# AWS Lambda + Amazon MSK / self-managed Kafka — Event Source Mapping (ESM)

> **Nguồn (official):** https://docs.aws.amazon.com/lambda/latest/dg/with-msk.html · https://docs.aws.amazon.com/lambda/latest/dg/with-msk-configure.html · https://docs.aws.amazon.com/lambda/latest/dg/msk-esm-parameters.html · https://docs.aws.amazon.com/lambda/latest/dg/with-msk-permissions.html · https://docs.aws.amazon.com/lambda/latest/dg/with-kafka.html
> **Tuần:** 9 — Kafka trên AWS (`Amazon MSK`) + Design patterns · **Loại:** AWS Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- `Lambda` đọc Kafka qua **event source mapping (ESM)** — **Lambda POLL** (giống `SQS`/`Kinesis`/`DynamoDB Streams` trong DVA), **không phải Kafka push**. Lambda là **consumer group**, đọc tuần tự **mỗi partition**, gom **batch** rồi **invoke đồng bộ**; xử lý xong batch → **commit offset**. Batch lỗi → **retry cả batch** đến khi thành công hoặc record hết hạn; có thể gửi batch hỏng tới **on-failure destination** (`SQS`/`SNS`/`S3`), `BisectBatchOnFunctionError`, `MaximumRetryAttempts`, `MaximumRecordAgeInSeconds` (mặc định −1 = vô hạn).
- Tham số: `Topics` (bắt buộc, chỉ set khi Create) · `StartingPosition` **TRIM_HORIZON / LATEST / AT_TIMESTAMP** (+`StartingPositionTimestamp`; nếu consumer group **đã có offset commit thì offset đó thắng**) · `BatchSize` mặc định **100**, tối đa **10.000** · `MaximumBatchingWindowInSeconds` mặc định **500 ms**, tối đa **300 s** · `AmazonManagedKafkaEventSourceConfig.ConsumerGroupId` (tuỳ chỉnh group id, chỉ lúc Create) · `FilterCriteria` (event filtering, lọc theo `value` JSON đã decode/ key/ headers) · `ProvisionedPollersConfig` `MinimumPollers` (mặc định 1) / `MaximumPollers` (mặc định 200), `PollerGroupName` (chia sẻ EPU giữa ≤100 ESM cùng VPC, tổng ≤ 2.000 pollers) · `SchemaRegistryConfig` (Glue SR hoặc Confluent SR để decode Avro/Protobuf/JSON) · `SourceAccessConfigurations`.
- Payload: `records["<topic>-<partition>"][]` với `key`/`value` **base64**, `headers[]` là mảng byte, `eventSource` = `aws:kafka` (MSK) hoặc `SelfManagedKafka`. Hàm phải **idempotent** (ESM at-least-once).
- Function timeout tối đa cho ESM Kafka là **14 phút** (không phải 15).
- Quyền (MSK): managed policy **`AWSLambdaMSKExecutionRole`** = `kafka:DescribeCluster(V2)`, `kafka:GetBootstrapBrokers`, `ec2:CreateNetworkInterface`, `ec2:DescribeNetworkInterfaces/Vpcs/Subnets/SecurityGroups`, `ec2:DeleteNetworkInterface`, `logs:*`. Cluster IAM auth → thêm `kafka-cluster:Connect`, `DescribeGroup`, `AlterGroup`, `DescribeTopic`, `ReadData`, `DescribeClusterDynamicConfiguration`. SCRAM → `secretsmanager:GetSecretValue` (+`kms:Decrypt`), `kafka:ListScramSecrets`. Glue SR → `glue:GetRegistry`, `glue:GetSchemaVersion`. Destination → `sqs:SendMessage`/`sns:Publish`/`s3:PutObject`.
- **Self-managed Kafka** (Confluent Cloud, Redpanda, EC2, on-prem): `--self-managed-event-source '{"Endpoints":{"KAFKA_BOOTSTRAP_SERVERS":[...]}}'` + `SourceAccessConfigurations` loại **VPC_SUBNET / VPC_SECURITY_GROUP / SASL_SCRAM_512_AUTH / SASL_SCRAM_256_AUTH / BASIC_AUTH (SASL/PLAIN) / CLIENT_CERTIFICATE_TLS_AUTH / SERVER_ROOT_CA_CERTIFICATE**. Với MSK, VPC lấy từ cluster nên không khai báo VPC_SUBNET.
- Networking: Lambda poller tạo **ENI trong subnet của cluster**; subnet cần đường ra tới **STS, Lambda, Secrets Manager** (NAT hoặc **VPC endpoint/PrivateLink**) nếu private. Lỗi hay gặp: `PROBLEM: Connection error` do SG/NAT.
- Bẫy DVA: "xử lý MSK bằng serverless, ít code nhất" ⇒ ESM (không tự viết consumer trên EC2); "chỉ nhận event `status=FAILED`" ⇒ **FilterCriteria** thay vì lọc trong code; "spike traffic, cần đảm bảo throughput" ⇒ **provisioned mode** (min/max pollers).

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Using Lambda with Amazon MSK

This chapter explains how to use an Amazon MSK cluster as an event source for your Lambda function. The general process involves: (1) **Cluster and network setup**, (2) **Event source mapping setup**, (3) **Function and permissions setup**. You can create and manage your Amazon MSK event source mappings directly from either the Lambda or the Amazon MSK console; both offer the option to automatically handle the setup of the necessary Lambda execution role permissions.

#### Example event

Lambda sends the batch of messages in the event parameter when it invokes your function. Each array item contains details of the Amazon MSK topic and partition identifier, together with a timestamp and a **base64-encoded** message.

```json
{
   "eventSource":"aws:kafka",
   "eventSourceArn":"arn:aws:kafka:us-east-1:123456789012:cluster/vpc-2priv-2pub/751d2973-a626-431c-9d4e-d7975eb44dd7-2",
   "bootstrapServers":"b-2.demo-cluster-1.a1bcde.c1.kafka.us-east-1.amazonaws.com:9092,b-1.demo-cluster-1.a1bcde.c1.kafka.us-east-1.amazonaws.com:9092",
   "records":{
      "mytopic-0":[
         {
            "topic":"mytopic",
            "partition":0,
            "offset":15,
            "timestamp":1545084650987,
            "timestampType":"CREATE_TIME",
            "key":"abcDEFghiJKLmnoPQRstuVWXyz1234==",
            "value":"SGVsbG8sIHRoaXMgaXMgYSB0ZXN0Lg==",
            "headers":[ { "headerKey":[104,101,97,100,101,114,86,97,108,117,101] } ]
         }
      ]
   }
}
```

For self-managed Apache Kafka the payload is identical except `"eventSource": "SelfManagedKafka"` and there is no `eventSourceArn`.

### Using an Amazon MSK cluster as an event source

Lambda reads event data from the Kafka topics that you specify as `Topics` in a `CreateEventSourceMapping` request, based on the **starting position** that you specify. After successful processing, your Kafka topic is committed to your Kafka cluster.

Lambda **reads messages sequentially for each Kafka topic partition**. A single Lambda payload can contain messages from multiple partitions. When more records are available, Lambda continues processing records in batches, based on the `BatchSize` value, until your function catches up with the topic.

After Lambda processes each batch, it **commits the offsets** of the messages in that batch. If your function returns an error for any of the messages in a batch, Lambda **retries the whole batch** of messages until processing succeeds or the messages expire. You can send records that fail all retry attempts to an **on-failure destination** for later processing.

> **Note:** While Lambda functions typically have a maximum timeout limit of 15 minutes, event source mappings for Amazon MSK, self-managed Apache Kafka, Amazon DocumentDB, and Amazon MQ only support functions with **maximum timeout limits of 14 minutes**.

Apache Kafka as an event source operates similarly to using Amazon SQS or Amazon Kinesis. **Lambda internally polls for new messages from the event source and then synchronously invokes the target Lambda function.** The maximum batch size is configurable (the default is 100 messages). To optimize throughput, configure **provisioned mode**: define the minimum and maximum number of event pollers allocated to your ESM.

> **Warning:** Lambda event source mappings process each event **at least once**, and duplicate processing of records can occur. We strongly recommend that you make your function code **idempotent**.

### All Amazon MSK event source configuration parameters in Lambda

| Parameter | Required | Default | Notes |
| --- | --- | --- | --- |
| AmazonManagedKafkaEventSourceConfig | N | Contains the `ConsumerGroupId` field, which defaults to a unique value. | Can set only on Create |
| BatchSize | N | **100** | Maximum: **10,000** |
| DestinationConfig | N | N/A | Capturing discarded batches (OnFailure: SQS, SNS, S3) |
| Enabled | N | True | |
| BisectBatchOnFunctionError | N | False | Error handling controls |
| FunctionResponseTypes | N | N/A | e.g. `ReportBatchItemFailures` |
| MaximumRecordAgeInSeconds | N | -1 (infinite) | Error handling controls |
| MaximumRetryAttempts | N | -1 (infinite) | Error handling controls |
| EventSourceArn | Y | N/A | Can set only on Create |
| FilterCriteria | N | N/A | Control which events Lambda sends to your function |
| FunctionName | Y | N/A | |
| KMSKeyArn | N | N/A | Encryption of filter criteria |
| MaximumBatchingWindowInSeconds | N | **500 ms** | Max **300** seconds |
| ProvisionedPollersConfig | N | `MinimumPollers` default 1; `MaximumPollers` default 200; `PollerGroupName` N/A | Provisioned mode |
| SourceAccessConfigurations | N | No credentials | SASL/SCRAM or CLIENT_CERTIFICATE_TLS_AUTH (mTLS) credentials |
| StartingPosition | Y | N/A | **AT_TIMESTAMP, TRIM_HORIZON, or LATEST**; can set only on Create |
| StartingPositionTimestamp | N | N/A | Required if StartingPosition is AT_TIMESTAMP |
| Tags | N | N/A | |
| Topics | Y | N/A | Kafka topic name; can set only on Create |

When you specify a `PollerGroupName`, multiple ESMs within the same Amazon VPC can share Event Poller Unit (EPU) capacity: ESMs must be within the same VPC, maximum of **100 ESMs per poller group**, aggregate maximum pollers across all ESMs in a group cannot exceed **2000**.

### Configuring Lambda permissions for Amazon MSK event source mappings

The **`AWSLambdaMSKExecutionRole`** managed policy contains the minimum required permissions:

- **CloudWatch Logs:** `logs:CreateLogGroup`, `logs:CreateLogStream`, `logs:PutLogEvents`.
- **MSK cluster:** `kafka:DescribeCluster`, `kafka:DescribeClusterV2` (recommended; works with provisioned and serverless), `kafka:GetBootstrapBrokers`.
- **VPC:** `ec2:CreateNetworkInterface`, `ec2:DescribeNetworkInterfaces`, `ec2:DescribeVpcs`, `ec2:DeleteNetworkInterface`, `ec2:DescribeSubnets`, `ec2:DescribeSecurityGroups`.

Optional permissions depending on features:

- Cross-account clusters: `kafka:DescribeVpcConnection` (execution role) and `kafka:ListVpcConnections` (creator).
- SASL/SCRAM or mTLS: `kafka:ListScramSecrets`, `secretsmanager:GetSecretValue`, `kms:Decrypt` (customer managed key).
- Schema registry: AWS Glue Schema Registry → `glue:GetRegistry`, `glue:GetSchemaVersion`; Confluent Schema Registry with BASIC_AUTH / CLIENT_CERTIFICATE_TLS_AUTH → `secretsmanager:GetSecretValue`.
- IAM authentication on the cluster: `kafka-cluster:Connect`, `kafka-cluster:AlterGroup`, `kafka-cluster:DescribeGroup`, `kafka-cluster:DescribeTopic`, `kafka-cluster:ReadData` (and `kafka-cluster:DescribeClusterDynamicConfiguration`).
- On-failure destination: `sqs:SendMessage` / `sns:Publish` / `s3:PutObject` + `s3:ListBucket`.

Example inline policy for an IAM-auth MSK cluster:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    { "Effect": "Allow",
      "Action": ["kafka-cluster:Connect", "kafka-cluster:DescribeClusterDynamicConfiguration"],
      "Resource": "arn:aws:kafka:us-east-1:123456789012:cluster/demo-cluster/UUID" },
    { "Effect": "Allow",
      "Action": ["kafka-cluster:DescribeTopic", "kafka-cluster:ReadData"],
      "Resource": "arn:aws:kafka:us-east-1:123456789012:topic/demo-cluster/UUID/orders" },
    { "Effect": "Allow",
      "Action": ["kafka-cluster:DescribeGroup", "kafka-cluster:AlterGroup"],
      "Resource": "arn:aws:kafka:us-east-1:123456789012:group/demo-cluster/UUID/*" }
  ]
}
```

### CLI examples

MSK cluster:

```bash
aws lambda create-event-source-mapping \
  --function-name orders-consumer \
  --event-source-arn arn:aws:kafka:us-east-1:123456789012:cluster/demo-cluster/UUID \
  --topics orders \
  --starting-position LATEST \
  --batch-size 100 \
  --maximum-batching-window-in-seconds 5 \
  --amazon-managed-kafka-event-source-config '{"ConsumerGroupId":"orders-lambda"}' \
  --filter-criteria '{"Filters":[{"Pattern":"{\"value\":{\"status\":[\"PAID\"]}}"}]}' \
  --destination-config '{"OnFailure":{"Destination":"arn:aws:sqs:us-east-1:123456789012:orders-esm-dlq"}}'
```

Self-managed Apache Kafka (VPC + SASL/SCRAM):

```bash
aws lambda create-event-source-mapping \
  --function-name orders-consumer \
  --topics orders \
  --starting-position TRIM_HORIZON \
  --self-managed-event-source '{"Endpoints":{"KAFKA_BOOTSTRAP_SERVERS":["kafka-1.internal:9096","kafka-2.internal:9096"]}}' \
  --source-access-configurations \
    '[{"Type":"VPC_SUBNET","URI":"subnet:subnet-0aaa"},{"Type":"VPC_SUBNET","URI":"subnet:subnet-0bbb"},{"Type":"VPC_SECURITY_GROUP","URI":"security_group:sg-0ccc"},{"Type":"SASL_SCRAM_512_AUTH","URI":"arn:aws:secretsmanager:us-east-1:123456789012:secret:kafka-scram"}]'
```

### Configuring your cluster and VPC network for Lambda

Lambda must be able to reach the brokers: the ESM creates network interfaces in the cluster's subnets (MSK) or in the subnets you provide (self-managed). If the subnets are private with no NAT gateway, create **VPC endpoints (AWS PrivateLink)** for Lambda and STS (and Secrets Manager when using SASL/SCRAM or mTLS). Security groups must allow the Lambda ENIs to reach the broker ports (9092/9094/9096/9098) and allow the return traffic. Cross-account access uses **multi-VPC private connectivity (PrivateLink)** on the MSK cluster plus a cluster policy.
