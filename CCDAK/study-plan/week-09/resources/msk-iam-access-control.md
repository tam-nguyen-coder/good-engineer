# Amazon MSK — IAM access control (actions, resource ARNs, client configuration)

> **Nguồn (official):** https://docs.aws.amazon.com/msk/latest/developerguide/iam-access-control.html · https://docs.aws.amazon.com/msk/latest/developerguide/kafka-actions.html · https://docs.aws.amazon.com/msk/latest/developerguide/configure-clients-for-iam-access-control.html
> **Tuần:** 9 — Kafka trên AWS (`Amazon MSK`) + Design patterns · **Loại:** AWS Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- **IAM access control** = **một cơ chế cho cả authentication + authorization** (thay SASL/SCRAM + Kafka ACL). Dưới lớp protocol là **SASL/OAUTHBEARER** (token ký bằng SigV4). Java client dùng lib `aws-msk-iam-auth` với `sasl.mechanism=AWS_MSK_IAM`; client khác (Node/Python/Go/.NET) dùng `sasl.mechanism=OAUTHBEARER` + signer lib (`aws-msk-iam-sasl-signer-js`...). Yêu cầu Kafka ≥ **2.7.1** cho non-Java.
- Client properties Java: `security.protocol=SASL_SSL` · `sasl.mechanism=AWS_MSK_IAM` · `sasl.jaas.config=software.amazon.msk.auth.iam.IAMLoginModule required;` · `sasl.client.callback.handler.class=software.amazon.msk.auth.iam.IAMClientCallbackHandler`. Thêm `awsProfileName="..."` / `awsRoleArn="..."` trong JAAS nếu cần. Port **9098** (public **9198**).
- Kafka ACL **không có tác dụng** với identity IAM; `allow.everyone.if.no.acl.found` bị bỏ qua khi bật IAM. IAM không áp dụng cho ZooKeeper node.
- Action `kafka-cluster:*` kèm **required actions**: `ReadData` cần `Connect` + `DescribeTopic` + `AlterGroup`; `WriteData` cần `Connect` + `DescribeTopic`; `WriteDataIdempotently` cần `Connect` + `WriteData` (resource **cluster**); `AlterGroup` (= READ GROUP ACL) cần `Connect` + `DescribeGroup`; `AlterTransactionalId` cần `Connect` + `DescribeTransactionalId` + `WriteData`.
- 4 loại resource ARN: `cluster/{name}/{uuid}` · `topic/{name}/{uuid}/{topic}` · `group/{name}/{uuid}/{group}` · `transactional-id/{name}/{uuid}/{txid}`. Wildcard `*` được dùng bất kỳ đâu sau `:topic/` v.v. (ví dụ `topic/MyCluster/*/*_test`).
- Wildcard action `kafka-cluster:*Topic` = Create/Describe/Alter/DeleteTopic nhưng **không** gồm `*TopicDynamicConfiguration`.
- WriteTxnMarkers (kết thúc transaction nội bộ) chỉ được IAM hỗ trợ từ Kafka **3.8**; cluster cũ hơn cần SCRAM/mTLS + ACL để làm việc này.
- Bẫy: consumer bị `TopicAuthorizationException`/`GroupAuthorizationException` dù đã có `ReadData` ⇒ thiếu `AlterGroup`/`DescribeGroup` trên **resource group** hoặc `DescribeTopic`. Producer idempotent (mặc định từ 3.0) cần thêm `WriteDataIdempotently` trên **cluster ARN**.

---

## 📄 Nội dung (trích từ tài liệu gốc)

### IAM access control

IAM access control for Amazon MSK enables you to handle **both authentication and authorization** for your MSK cluster. This eliminates the need to use one mechanism for authentication and another for authorization. For example, when a client tries to write to your cluster, Amazon MSK uses IAM to check whether that client is an authenticated identity and also whether it is authorized to produce to your cluster.

IAM access control works for **Java and non-Java clients**, including Kafka clients written in Python, Go, JavaScript, and .NET. IAM access control for non-Java clients is available for MSK clusters with Kafka version **2.7.1 or above**.

To make IAM access control possible, Amazon MSK makes minor modifications to Apache Kafka source code. Amazon MSK logs access events so you can audit them.

**Important considerations:**

- IAM access control doesn't apply to Apache ZooKeeper nodes.
- The `allow.everyone.if.no.acl.found` Apache Kafka setting has **no effect** if your cluster uses IAM access control.
- You can invoke Apache Kafka ACL APIs for an MSK cluster that uses IAM access control. However, **Apache Kafka ACLs have no effect on authorization for IAM identities**. You must use IAM policies to control access for IAM identities.

> **Note:** For clusters running Apache Kafka version 3.8 or later, IAM access control supports the WriteTxnMarkers API for terminating transactions. For clusters running earlier versions, to terminate transactions use SCRAM or mTLS authentication with appropriate ACLs instead.

### Authorization policy actions

When you include in your authorization policy an action from the *Action* column, you must also include the corresponding actions from the *Required actions* column.

| Action | Description (Kafka ACL equivalent) | Required actions | Required resource | Serverless |
| --- | --- | --- | --- | --- |
| kafka-cluster:Connect | Connect and authenticate to the cluster | None | cluster | Yes |
| kafka-cluster:DescribeCluster | DESCRIBE CLUSTER | Connect | cluster | Yes |
| kafka-cluster:AlterCluster | ALTER CLUSTER | Connect, DescribeCluster | cluster | No |
| kafka-cluster:DescribeClusterDynamicConfiguration | DESCRIBE_CONFIGS CLUSTER | Connect | cluster | No |
| kafka-cluster:AlterClusterDynamicConfiguration | ALTER_CONFIGS CLUSTER | Connect, DescribeClusterDynamicConfiguration | cluster | No |
| kafka-cluster:WriteDataIdempotently | IDEMPOTENT_WRITE CLUSTER | Connect, WriteData | cluster | Yes |
| kafka-cluster:CreateTopic | CREATE CLUSTER/TOPIC | Connect | topic | Yes |
| kafka-cluster:DescribeTopic | DESCRIBE TOPIC | Connect | topic | Yes |
| kafka-cluster:AlterTopic | ALTER TOPIC | Connect, DescribeTopic | topic | Yes |
| kafka-cluster:DeleteTopic | DELETE TOPIC | Connect, DescribeTopic | topic | Yes |
| kafka-cluster:DescribeTopicDynamicConfiguration | DESCRIBE_CONFIGS TOPIC | Connect | topic | Yes |
| kafka-cluster:AlterTopicDynamicConfiguration | ALTER_CONFIGS TOPIC | Connect, DescribeTopicDynamicConfiguration | topic | Yes |
| kafka-cluster:ReadData | READ TOPIC | Connect, DescribeTopic, **AlterGroup** | topic | Yes |
| kafka-cluster:WriteData | WRITE TOPIC | Connect, DescribeTopic | topic | Yes |
| kafka-cluster:DescribeGroup | DESCRIBE GROUP | Connect | group | Yes |
| kafka-cluster:AlterGroup | READ GROUP (join group) | Connect, DescribeGroup | group | Yes |
| kafka-cluster:DeleteGroup | DELETE GROUP | Connect, DescribeGroup | group | Yes |
| kafka-cluster:DescribeTransactionalId | DESCRIBE TRANSACTIONAL_ID | Connect | transactional-id | Yes |
| kafka-cluster:AlterTransactionalId | WRITE TRANSACTIONAL_ID | Connect, DescribeTransactionalId, WriteData | transactional-id | Yes |

You can use the asterisk (\*) wildcard any number of times in an action after the colon:

- `kafka-cluster:*Topic` stands for `CreateTopic`, `DescribeTopic`, `AlterTopic`, and `DeleteTopic`. It **doesn't** include `DescribeTopicDynamicConfiguration` or `AlterTopicDynamicConfiguration`.
- `kafka-cluster:*` stands for all permissions.

### Authorization policy resources

| Resource | ARN format |
| --- | --- |
| Cluster | `arn:aws:kafka:{region}:{account-id}:cluster/{cluster-name}/{cluster-uuid}` |
| Topic | `arn:aws:kafka:{region}:{account-id}:topic/{cluster-name}/{cluster-uuid}/{topic-name}` |
| Group | `arn:aws:kafka:{region}:{account-id}:group/{cluster-name}/{cluster-uuid}/{group-name}` |
| Transactional ID | `arn:aws:kafka:{region}:{account-id}:transactional-id/{cluster-name}/{cluster-uuid}/{transactional-id}` |

You can use the asterisk (\*) wildcard any number of times anywhere in the part of the ARN that comes after `:cluster/`, `:topic/`, `:group/`, and `:transactional-id/`:

- `arn:aws:kafka:us-east-1:0123456789012:topic/MyTestCluster/*` — all the topics in any cluster named MyTestCluster, regardless of the cluster's UUID.
- `arn:aws:kafka:us-east-1:0123456789012:topic/MyTestCluster/abcd1234-0123-abcd-5678-1234abcd-1/*_test` — all topics whose name ends with "_test" in that specific cluster.
- `arn:aws:kafka:us-east-1:0123456789012:transactional-id/MyTestCluster/*/5555abcd-...` — the same transactional ID across all incarnations of a cluster named MyTestCluster.

### Example authorization policy (producer + consumer on topic `orders`, group `orders-svc`)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["kafka-cluster:Connect", "kafka-cluster:DescribeCluster", "kafka-cluster:WriteDataIdempotently"],
      "Resource": "arn:aws:kafka:us-east-1:123456789012:cluster/demo-cluster/abcd1234-1111-2222-3333-abcd1234abcd-1"
    },
    {
      "Effect": "Allow",
      "Action": ["kafka-cluster:DescribeTopic", "kafka-cluster:ReadData", "kafka-cluster:WriteData"],
      "Resource": "arn:aws:kafka:us-east-1:123456789012:topic/demo-cluster/abcd1234-1111-2222-3333-abcd1234abcd-1/orders"
    },
    {
      "Effect": "Allow",
      "Action": ["kafka-cluster:DescribeGroup", "kafka-cluster:AlterGroup"],
      "Resource": "arn:aws:kafka:us-east-1:123456789012:group/demo-cluster/abcd1234-1111-2222-3333-abcd1234abcd-1/orders-svc"
    }
  ]
}
```

### Configure clients for IAM access control

To enable clients to communicate with an MSK cluster that uses IAM access control, you can use either of these mechanisms:

- Non-Java client configuration using **SASL_OAUTHBEARER** mechanism.
- Java client configuration using SASL_OAUTHBEARER mechanism or **AWS_MSK_IAM** mechanism.

#### Use the MSK custom AWS_MSK_IAM mechanism (Java)

Add the following to the `client.properties` file (remove `ssl.truststore.location` to use the JVM default certificates):

```
ssl.truststore.location=<PATH_TO_TRUST_STORE_FILE>
security.protocol=SASL_SSL
sasl.mechanism=AWS_MSK_IAM
sasl.jaas.config=software.amazon.msk.auth.iam.IAMLoginModule required;
sasl.client.callback.handler.class=software.amazon.msk.auth.iam.IAMClientCallbackHandler
```

To use a named profile that you created for AWS credentials, include `awsProfileName="{your profile name}";` in your client configuration file. Download the latest stable `aws-msk-iam-auth` JAR file and place it in the class path, or add the Maven dependency:

```xml
<dependency>
    <groupId>software.amazon.msk</groupId>
    <artifactId>aws-msk-iam-auth</artifactId>
    <version>1.0.0</version>
</dependency>
```

The Amazon MSK client plugin is open-sourced under the Apache 2.0 license.

#### Use the SASL_OAUTHBEARER mechanism (non-Java)

Python example (configuration changes are similar in other languages):

```python
from kafka import KafkaProducer
from aws_msk_iam_sasl_signer import MSKAuthTokenProvider

class MSKTokenProvider():
    def token(self):
        token, _ = MSKAuthTokenProvider.generate_auth_token('<my AWS Region>')
        return token

producer = KafkaProducer(
    bootstrap_servers='<myBootstrapString>',
    security_protocol='SASL_SSL',
    sasl_mechanism='OAUTHBEARER',
    sasl_oauth_token_provider=MSKTokenProvider(),
)
```

Helper libraries: JavaScript `aws-msk-iam-sasl-signer-js` (https://github.com/aws/aws-msk-iam-sasl-signer-js) · Python `aws-msk-iam-sasl-signer-python` · Go `aws-msk-iam-sasl-signer-go` · .NET `aws-msk-iam-sasl-signer-net` · Java: SASL_OAUTHBEARER support via the `aws-msk-iam-auth` jar.
