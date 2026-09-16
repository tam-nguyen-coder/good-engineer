# 🧪 Hands-on Labs — Tuần 9: Kafka trên AWS (`Amazon MSK`) + Design patterns

> Lab cầm tay chỉ việc. **Lab 9.3 → 9.6 chạy local** bằng cluster 3 node Tuần 1 (miễn phí). **Lab 9.1 / 9.2 / 9.7 chạy trên AWS và CÓ PHÍ** — đọc khung cảnh báo trước khi gõ lệnh, và LUÔN chạy phần Dọn dẹp ngay khi xong (không để cluster qua đêm).
> ⚙️ Yêu cầu chung: Docker Desktop, **Node.js 24**, cluster 3 node từ Tuần 1 (Lab 1.2); cho lab AWS: **AWS CLI v2** đã `aws configure`, quyền tạo MSK/IAM/EC2/Lambda/SQS/Pipes, **AWS SAM CLI** (Lab 9.2 phần local). Tổng ~3.5h (local ~2h10, AWS ~1h20).
> Về [plan tuần](README.md) · [Câu hỏi luyện tập](questions.md) · [Kế hoạch tổng](../../KAFKA-STUDY-PLAN.md)

> 💸 **CẢNH BÁO CHI PHÍ (Lab 9.1, 9.2, 9.7).** `MSK Serverless` tính tiền **ngay từ lúc cluster `ACTIVE`**, kể cả khi không có message: phí **cluster-hour** (~0,75 USD/giờ ở us-east-1 — kiểm tra trang pricing cho region của bạn) + **partition-hour** + throughput + storage. Cộng thêm EC2 `t3.small`, 2 **VPC interface endpoint** (Lambda + STS, ~0,01 USD/giờ mỗi endpoint) cho Lab 9.2/9.7. Làm gọn cả 3 lab trong **≤ 2 giờ** rồi xoá hết ⇒ tốn khoảng **2–4 USD**. Quên xoá 1 tuần ⇒ **> 130 USD**. Nguyên tắc: **tạo → làm → `delete-cluster` trong cùng buổi**; cuối file có checklist xoá tài nguyên.

---

## 🔧 Chuẩn bị chung

### 1) Cluster local 3 node + alias (cho Lab 9.3 → 9.6)

```bash
cd ~/kafka-labs
docker compose -f docker-compose.cluster.yml up -d
export KAFKA_CTR=kafka-1 KAFKA_BS=kafka-1:19092        # cluster 3 node
kt --list                                              # alias kt/kcp/kcc/kcg/kcfg/kq/ksh đã định nghĩa ở Tuần 1
```

> 📌 2 file compose chuẩn được định nghĩa ở [Tuần 1 — Lab 1.1 / 1.2](../week-01/labs.md). Lab 9.3 cần thêm Postgres + Debezium: dùng lại **`docker-compose.debezium.yml` của [Tuần 5 — Lab 5.6](../week-05/labs.md)** (in lại rút gọn trong Lab 9.3 cho ai làm tuần này độc lập).

### 2) Project Node.js cho tuần 9

```bash
mkdir -p ~/kafka-labs/week-09 && cd ~/kafka-labs/week-09
npm init -y >/dev/null && npm pkg set type=module
npm i kafkajs@2 pg            # pg: client PostgreSQL cho Lab 9.3
node -v                       # v24.x — Lab 9.4 dùng node:sqlite có sẵn trong Node 24
```

File dùng chung `kafka.mjs` (giống Tuần 3):

```javascript
// ~/kafka-labs/week-09/kafka.mjs — client dùng chung cho lab local tuần 9
import { Kafka, logLevel } from "kafkajs";

export const BROKERS = ["localhost:9092", "localhost:9094", "localhost:9096"];
export const kafka = new Kafka({ clientId: "week09-lab", brokers: BROKERS, logLevel: logLevel.WARN });
export const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
export const hdr = (message, name) => message.headers?.[name]?.toString();   // đọc header dạng string
```

### 3) Biến môi trường AWS (cho Lab 9.1 / 9.2 / 9.7) — chạy lại mỗi phiên terminal

```bash
export AWS_REGION=ap-southeast-1                                   # đổi theo region bạn dùng
export ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
export CLUSTER_NAME=orders-serverless
echo "$AWS_REGION / $ACCOUNT_ID"
```

> 🧠 Liên hệ `DVA-C02`/`SAA-C03`: 3 lab AWS ghép Kafka vào những mảnh bạn đã học — IAM policy theo resource ARN (như S3/DynamoDB), `Lambda` event source mapping (giống `Kinesis`/`SQS` ESM), `EventBridge Pipes`, VPC endpoint. Phần MSK **không** nằm trong đề CCDAK; phần pattern (Lab 9.3 → 9.6) **có**.

---

## Lab 9.1 ⭐ — `MSK Serverless` + IAM access control (AWS — CÓ PHÍ, đọc kỹ cảnh báo)

**🎯 Mục tiêu:** Tạo cluster `MSK Serverless` bằng `aws kafka create-cluster-v2 --serverless`, lấy bootstrap **port 9098**, viết IAM policy `kafka-cluster:*` đúng **required actions** cho topic `orders` + group `orders-*`; từ **EC2 trong VPC** tạo/list topic bằng `kafka-topics.sh --command-config client-iam.properties` (jar `aws-msk-iam-auth`) và produce/consume bằng Node `kafkajs` + `aws-msk-iam-sasl-signer-js`. Kết thúc bằng `delete-cluster`.
**🧩 Luyện kỹ năng (liên quan công việc):**

- Khối JSON `--serverless`: `VpcConfigs[].SubnetIds/SecurityGroupIds` + `ClientAuthentication.Sasl.Iam.Enabled=true`.
- ARN 4 loại (`cluster/` · `topic/` · `group/` · `transactional-id/`) và required actions (`ReadData` ← `Connect`+`DescribeTopic`+`AlterGroup`; `AlterGroup` ← `DescribeGroup`; idempotent producer ← `WriteDataIdempotently` trên **cluster ARN**).
- Client props Java (`SASL_SSL` / `AWS_MSK_IAM` / `IAMLoginModule` / `IAMClientCallbackHandler`) và Node (`oauthbearer` + `oauthBearerProvider`).
- Vì sao **không** mô phỏng được IAM ở local (xem cuối lab).

**⏱️ ~40 phút** (chờ cluster ~5–10 phút) · **Yêu cầu trước:** Chuẩn bị chung mục 3. **Chi phí:** cluster-hour + EC2 `t3.small` — làm liền tay rồi xoá.

### Các bước

1. Mạng: dùng **default VPC**, lấy **2 subnet ở 2 AZ khác nhau** (Serverless yêu cầu ≥ 2 AZ), tạo security group **tự tham chiếu** mở **9098** (client và broker cùng SG) + 443 (cho VPC endpoint ở Lab 9.2).

   ```bash
   export VPC_ID=$(aws ec2 describe-vpcs --filters Name=is-default,Values=true --query 'Vpcs[0].VpcId' --output text)
   export SUBNET_A=$(aws ec2 describe-subnets --filters Name=vpc-id,Values=$VPC_ID --query 'Subnets[0].SubnetId' --output text)
   export SUBNET_B=$(aws ec2 describe-subnets --filters Name=vpc-id,Values=$VPC_ID --query 'Subnets[1].SubnetId' --output text)
   aws ec2 describe-subnets --subnet-ids $SUBNET_A $SUBNET_B --query 'Subnets[].AvailabilityZone'   # phải là 2 AZ khác nhau

   export SG_ID=$(aws ec2 create-security-group --group-name msk-lab-sg --description "MSK lab week 9" \
     --vpc-id $VPC_ID --query GroupId --output text)
   aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 9098 --source-group $SG_ID  # client ↔ broker IAM
   aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 443  --source-group $SG_ID  # VPC endpoint (Lab 9.2)
   echo "VPC=$VPC_ID SUBNETS=$SUBNET_A,$SUBNET_B SG=$SG_ID"
   ```
2. Tạo cluster Serverless. Từ giây này **đồng hồ tính tiền bắt đầu chạy** khi cluster `ACTIVE`.

   ```bash
   cat > serverless.json <<EOF
   {
     "VpcConfigs": [
       { "SubnetIds": ["$SUBNET_A", "$SUBNET_B"], "SecurityGroupIds": ["$SG_ID"] }
     ],
     "ClientAuthentication": { "Sasl": { "Iam": { "Enabled": true } } }
   }
   EOF
   export CLUSTER_ARN=$(aws kafka create-cluster-v2 --cluster-name $CLUSTER_NAME \
     --serverless file://serverless.json --query ClusterArn --output text)
   echo $CLUSTER_ARN
   # arn:aws:kafka:ap-southeast-1:123456789012:cluster/orders-serverless/1a2b3c4d-....-s2

   until [ "$(aws kafka describe-cluster-v2 --cluster-arn $CLUSTER_ARN --query ClusterInfo.State --output text)" = "ACTIVE" ]; do
     echo "$(date +%T) state=$(aws kafka describe-cluster-v2 --cluster-arn $CLUSTER_ARN --query ClusterInfo.State --output text)"; sleep 30
   done
   export BOOTSTRAP=$(aws kafka get-bootstrap-brokers --cluster-arn $CLUSTER_ARN --query BootstrapBrokerStringSaslIam --output text)
   echo $BOOTSTRAP     # boot-xxxxxxxx.c1.kafka-serverless.ap-southeast-1.amazonaws.com:9098  ← chỉ có SaslIam, port 9098
   ```

   > 📌 `describe-cluster-v2` trả `ClusterType: SERVERLESS`; `get-bootstrap-brokers` **chỉ** có `BootstrapBrokerStringSaslIam` (Serverless không có TLS/SCRAM string). Với Provisioned bạn sẽ thấy thêm `BootstrapBrokerStringTls` (9094), `...SaslScram` (9096).
3. Viết IAM policy **đầy đủ required actions** cho topic `orders` + group `orders-*`. Tách 3 statement theo 3 loại ARN.

   ```bash
   export CLUSTER_UUID=${CLUSTER_ARN##*/}           # phần sau dấu / cuối
   cat > msk-orders-policy.json <<EOF
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Sid": "ClusterLevel",
         "Effect": "Allow",
         "Action": [
           "kafka-cluster:Connect",
           "kafka-cluster:DescribeCluster",
           "kafka-cluster:WriteDataIdempotently"
         ],
         "Resource": "arn:aws:kafka:$AWS_REGION:$ACCOUNT_ID:cluster/$CLUSTER_NAME/$CLUSTER_UUID"
       },
       {
         "Sid": "TopicOrders",
         "Effect": "Allow",
         "Action": [
           "kafka-cluster:CreateTopic",
           "kafka-cluster:DescribeTopic",
           "kafka-cluster:WriteData",
           "kafka-cluster:ReadData"
         ],
         "Resource": "arn:aws:kafka:$AWS_REGION:$ACCOUNT_ID:topic/$CLUSTER_NAME/$CLUSTER_UUID/orders"
       },
       {
         "Sid": "DescribeAllTopicsForList",
         "Effect": "Allow",
         "Action": ["kafka-cluster:DescribeTopic"],
         "Resource": "arn:aws:kafka:$AWS_REGION:$ACCOUNT_ID:topic/$CLUSTER_NAME/$CLUSTER_UUID/*"
       },
       {
         "Sid": "GroupsOrders",
         "Effect": "Allow",
         "Action": [
           "kafka-cluster:DescribeGroup",
           "kafka-cluster:AlterGroup"
         ],
         "Resource": "arn:aws:kafka:$AWS_REGION:$ACCOUNT_ID:group/$CLUSTER_NAME/$CLUSTER_UUID/orders-*"
       }
     ]
   }
   EOF
   cat msk-orders-policy.json | python3 -m json.tool >/dev/null && echo "policy JSON OK"
   ```

   > 🧠 Đối chiếu ACL Tuần 7: `ReadData` ↔ `READ Topic`; `AlterGroup` ↔ `READ Group` (quyền **join group**); `WriteDataIdempotently` ↔ `IDEMPOTENT_WRITE Cluster` — producer Java/kafkajs `idempotent: true` mà thiếu action này sẽ `ClusterAuthorizationException` dù `WriteData` đã có.
4. Tạo IAM role cho EC2 (trust `ec2.amazonaws.com`) gắn policy trên + `AmazonSSMManagedInstanceCore` (vào máy bằng **SSM Session Manager**, không cần mở SSH), rồi launch EC2 `t3.small` Amazon Linux 2023 **trong cùng subnet/SG**.

   ```bash
   cat > ec2-trust.json <<'EOF'
   { "Version": "2012-10-17", "Statement": [ { "Effect": "Allow", "Principal": { "Service": "ec2.amazonaws.com" }, "Action": "sts:AssumeRole" } ] }
   EOF
   aws iam create-role --role-name msk-lab-ec2-role --assume-role-policy-document file://ec2-trust.json >/dev/null
   aws iam put-role-policy --role-name msk-lab-ec2-role --policy-name msk-orders --policy-document file://msk-orders-policy.json
   aws iam attach-role-policy --role-name msk-lab-ec2-role --policy-arn arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore
   aws iam create-instance-profile --instance-profile-name msk-lab-ec2-profile >/dev/null
   aws iam add-role-to-instance-profile --instance-profile-name msk-lab-ec2-profile --role-name msk-lab-ec2-role
   sleep 10   # IAM eventual consistency

   export AMI_ID=$(aws ssm get-parameter --name /aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64 --query Parameter.Value --output text)
   export INSTANCE_ID=$(aws ec2 run-instances --image-id $AMI_ID --instance-type t3.small \
     --subnet-id $SUBNET_A --security-group-ids $SG_ID --associate-public-ip-address \
     --iam-instance-profile Name=msk-lab-ec2-profile \
     --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=msk-lab-client}]' \
     --query 'Instances[0].InstanceId' --output text)
   aws ec2 wait instance-running --instance-ids $INSTANCE_ID
   aws ssm start-session --target $INSTANCE_ID        # cần plugin session-manager-plugin; hoặc dùng EC2 Instance Connect trên console
   ```
5. **Trong EC2**: cài Java 17, tải Kafka CLI + jar `aws-msk-iam-auth`, viết `client-iam.properties`.

   ```bash
   sudo dnf install -y java-17-amazon-corretto-headless
   cd ~ && curl -LO https://archive.apache.org/dist/kafka/4.0.0/kafka_2.13-4.0.0.tgz
   tar xzf kafka_2.13-4.0.0.tgz && cd kafka_2.13-4.0.0
   # jar IAM auth (kiểm tra bản mới nhất tại github.com/aws/aws-msk-iam-auth/releases); đặt vào libs/ → tự vào classpath của kafka-run-class.sh
   curl -Lo libs/aws-msk-iam-auth-2.3.0-all.jar \
     https://github.com/aws/aws-msk-iam-auth/releases/download/v2.3.0/aws-msk-iam-auth-2.3.0-all.jar

   cat > client-iam.properties <<'EOF'
   # client-iam.properties — Kafka Java client nối MSK bằng IAM access control (port 9098)
   security.protocol=SASL_SSL
   sasl.mechanism=AWS_MSK_IAM
   sasl.jaas.config=software.amazon.msk.auth.iam.IAMLoginModule required;
   sasl.client.callback.handler.class=software.amazon.msk.auth.iam.IAMClientCallbackHandler
   # credential lấy từ default chain: ở đây là instance role của EC2. Muốn dùng profile: thêm awsProfileName="x" vào sasl.jaas.config
   EOF

   export BOOTSTRAP=<dán giá trị BootstrapBrokerStringSaslIam ở bước 2>
   export AWS_REGION=ap-southeast-1
   ```
6. **Trong EC2**: tạo topic `orders` và list topic qua IAM.

   ```bash
   bin/kafka-topics.sh --bootstrap-server $BOOTSTRAP --command-config client-iam.properties \
     --create --topic orders --partitions 3
   # Serverless tự đặt replication factor 3, không cần/không nên truyền --replication-factor
   bin/kafka-topics.sh --bootstrap-server $BOOTSTRAP --command-config client-iam.properties --list
   bin/kafka-topics.sh --bootstrap-server $BOOTSTRAP --command-config client-iam.properties --describe --topic orders

   # Thử SAI để nhớ: tạo topic không có trong policy
   bin/kafka-topics.sh --bootstrap-server $BOOTSTRAP --command-config client-iam.properties --create --topic payments --partitions 1
   # → TopicAuthorizationException: Not authorized to access topics: [payments]
   ```
7. **Trong EC2**: produce/consume bằng console tool (Java) — lấy dữ liệu cho Lab 9.2 sau này.

   ```bash
   printf 'order-1001:{"orderId":"order-1001","customerId":"cust-42","status":"PAID","amount":250}\norder-1002:{"orderId":"order-1002","customerId":"cust-7","status":"PENDING","amount":99}\n' | \
     bin/kafka-console-producer.sh --bootstrap-server $BOOTSTRAP --producer.config client-iam.properties \
       --topic orders --property parse.key=true --property key.separator=:
   bin/kafka-console-consumer.sh --bootstrap-server $BOOTSTRAP --consumer.config client-iam.properties \
     --topic orders --group orders-cli --from-beginning --property print.key=true --timeout-ms 10000
   ```
8. **Trong EC2**: bản Node.js với `kafkajs` + `aws-msk-iam-sasl-signer-js` (mechanism `oauthbearer`).

   ```bash
   sudo dnf install -y nodejs22 nodejs22-npm      # AL2023; hoặc cài Node 24 qua nvm
   mkdir -p ~/msk-node && cd ~/msk-node && npm init -y >/dev/null && npm pkg set type=module
   npm i kafkajs@2 aws-msk-iam-sasl-signer-js
   cat > msk-iam.mjs <<'EOF'
   // msk-iam.mjs — kafkajs nối MSK IAM: SASL_SSL + OAUTHBEARER, token SigV4 do signer lib sinh
   import { Kafka, logLevel } from "kafkajs";
   import { generateAuthToken } from "aws-msk-iam-sasl-signer-js";

   const region = process.env.AWS_REGION ?? "ap-southeast-1";
   const kafka = new Kafka({
     clientId: "lab91-node",
     brokers: [process.env.BOOTSTRAP],           // boot-xxx...kafka-serverless...:9098
     ssl: true,                                  // Java: security.protocol=SASL_SSL
     logLevel: logLevel.WARN,
     sasl: {
       mechanism: "oauthbearer",                 // Java dùng AWS_MSK_IAM; non-Java dùng OAUTHBEARER
       oauthBearerProvider: async () => {
         const { token } = await generateAuthToken({ region });   // ký SigV4 bằng credential mặc định (instance role)
         return { value: token };
       },
     },
   });

   const admin = kafka.admin();
   await admin.connect();
   console.log("topics:", await admin.listTopics());
   await admin.disconnect();

   const producer = kafka.producer({ idempotent: true, maxInFlightRequests: 1 }); // cần WriteDataIdempotently trên cluster ARN
   await producer.connect();
   const [meta] = await producer.send({
     topic: "orders", acks: -1,
     messages: [{ key: "order-1003", value: JSON.stringify({ orderId: "order-1003", customerId: "cust-42", status: "PAID", amount: 75 }) }],
   });
   console.log(`produced -> partition=${meta.partition} baseOffset=${meta.baseOffset}`);
   await producer.disconnect();

   const consumer = kafka.consumer({ groupId: "orders-node" });    // khớp ARN group orders-*
   await consumer.connect();
   await consumer.subscribe({ topic: "orders", fromBeginning: true });
   let n = 0;
   const timer = setTimeout(async () => { console.log(`consumed ${n} messages, exiting`); await consumer.disconnect(); process.exit(0); }, 8000);
   await consumer.run({
     eachMessage: async ({ partition, message }) => {
       n++; timer.refresh();
       console.log(`p${partition} off=${message.offset} key=${message.key} value=${message.value}`);
     },
   });
   EOF
   BOOTSTRAP=$BOOTSTRAP AWS_REGION=$AWS_REGION node msk-iam.mjs
   ```
9. (Tuỳ chọn, 3 phút — rất đáng làm) **Thử thiếu required action**: trên máy bạn, xoá `kafka-cluster:AlterGroup` khỏi `msk-orders-policy.json`, `put-role-policy` lại, chờ ~10 s, chạy lại `msk-iam.mjs` trong EC2 → producer vẫn OK, consumer báo `Not authorized to access group: Group authorization failed`. Thêm lại rồi `put-role-policy`.

### ✅ Kiểm chứng

- `get-bootstrap-brokers` chỉ trả `BootstrapBrokerStringSaslIam` với host `*.kafka-serverless.<region>.amazonaws.com:9098`.
- Bước 6: `--list` in `orders`; `--describe` cho `ReplicationFactor: 3` dù bạn không truyền; tạo `payments` bị `TopicAuthorizationException` (policy chỉ cho `orders`).
- Bước 7–8: console consumer in 2 record; Node in `topics: [ 'orders' ]`, `produced -> partition=… baseOffset=…`, rồi 3 record (2 từ console + 1 từ Node). Group `orders-node` join được vì có `AlterGroup` + `DescribeGroup` trên `group/.../orders-*`.
- Bước 9: bỏ `AlterGroup` ⇒ **chỉ consumer hỏng**, đúng bảng required actions.
- CloudTrail (nếu muốn): event `kafka-cluster:Connect` ghi identity role EC2 — IAM auth cho audit theo identity, điều SCRAM không có.

### 🧹 Dọn dẹp

```bash
# --- Nếu làm tiếp Lab 9.2/9.7 ngay: GIỮ cluster + EC2 + SG, bỏ qua khối này. Nếu nghỉ: XOÁ HẾT ---
aws kafka delete-cluster --cluster-arn $CLUSTER_ARN                       # ⏱️ ngừng tính tiền khi State=DELETING→gone
aws ec2 terminate-instances --instance-ids $INSTANCE_ID >/dev/null
aws ec2 wait instance-terminated --instance-ids $INSTANCE_ID
aws iam remove-role-from-instance-profile --instance-profile-name msk-lab-ec2-profile --role-name msk-lab-ec2-role
aws iam delete-instance-profile --instance-profile-name msk-lab-ec2-profile
aws iam delete-role-policy --role-name msk-lab-ec2-role --policy-name msk-orders
aws iam detach-role-policy --role-name msk-lab-ec2-role --policy-arn arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore
aws iam delete-role --role-name msk-lab-ec2-role
# SG chỉ xoá được khi ENI của cluster đã biến mất (vài phút sau delete-cluster)
until aws ec2 delete-security-group --group-id $SG_ID 2>/dev/null; do echo "SG still in use, waiting..."; sleep 30; done
aws kafka list-clusters-v2 --query 'ClusterInfoList[].{name:ClusterName,state:State}'   # phải rỗng hoặc DELETING
```

### 🧠 Ý nghĩa với đề thi (và công việc)

- **IAM access control = auth + authz** trong 1 cơ chế, gắn vào **identity** (role EC2/Lambda/ECS) — không quản password/cert; Kafka ACL **vô hiệu** với identity IAM.
- Required actions là bẫy số 1: "có `ReadData` mà vẫn `GroupAuthorizationException`" ⇒ thiếu **`AlterGroup` + `DescribeGroup`** trên **group ARN**; "producer mặc định lỗi cluster authorization" ⇒ thiếu **`WriteDataIdempotently`** trên **cluster ARN**.
- Serverless: **chỉ IAM**, port **9098**, không sửa broker config, RF cố định 3, `auto.create.topics.enable=false` (khác Kafka local) ⇒ phải tạo topic trước.
- **Vì sao không mô phỏng IAM ở local?** Broker MSK là Kafka được AWS **sửa mã nguồn** để xác thực token SASL/OAUTHBEARER ký **SigV4** bằng cách gọi IAM/STS và đánh giá IAM policy; Apache Kafka open-source chỉ có OAUTHBEARER unsecured/JWT validator, không có "IAM authorizer", và LocalStack không mô phỏng data plane MSK. Ở local bạn chỉ luyện được **SASL/SCRAM + ACL** (Tuần 7); ánh xạ sang IAM bằng bảng required actions.

---

## Lab 9.2 ⭐ — `Lambda` event source mapping cho MSK (AWS có phí + test local bằng SAM)

**🎯 Mục tiêu:** Viết handler Node.js ESM decode **base64** `event.records["orders-0"][].value`; test **local, miễn phí** bằng `sam local invoke -e event-msk.json` với JSON event mẫu MSK đầy đủ; rồi deploy và tạo ESM `aws lambda create-event-source-mapping --event-source-arn <msk-arn> --topics orders --starting-position LATEST --batch-size 100 --maximum-batching-window-in-seconds 5 --filter-criteria ...`, produce từ EC2 và xem CloudWatch Logs.
**🧩 Luyện kỹ năng (liên quan DVA):**

- ESM = **Lambda poll** (như `Kinesis`/`SQS`/`DynamoDB Streams`), Lambda là **1 consumer group**, invoke **đồng bộ** theo batch, commit offset sau batch, lỗi ⇒ **retry cả batch**.
- Shape payload: `records` là **map `<topic>-<partition>` → array**, `key`/`value` base64, `headers[]` mảng byte, `eventSource: "aws:kafka"`.
- `FilterCriteria` lọc ở ESM (miễn phí invoke) thay `if` trong code.
- IAM: `AWSLambdaMSKExecutionRole` (describe cluster, bootstrap, **ENI trong VPC**) + `kafka-cluster:*` khi cluster dùng IAM.

**⏱️ ~40 phút** (local ~15, AWS ~25) · **Yêu cầu trước:** Lab 9.1 đang chạy (cluster + EC2 + `$CLUSTER_ARN`, `$SG_ID`, `$SUBNET_A/B`), **SAM CLI** cài trên máy (`sam --version`).

### Các bước

1. Tạo project function (trên **máy bạn**).

   ```bash
   mkdir -p ~/kafka-labs/week-09/lambda-orders/events && cd ~/kafka-labs/week-09/lambda-orders
   ```

   `index.mjs` — handler đầy đủ:

   ```javascript
   // ~/kafka-labs/week-09/lambda-orders/index.mjs — Lambda handler cho MSK event source mapping (Node.js ESM)
   // event.records = { "<topic>-<partition>": [ { topic, partition, offset, timestamp, timestampType, key, value, headers } ] }
   // key/value là base64; headers là mảng { headerName: [byte, byte, ...] }

   const decode = (b64) => (b64 == null ? null : Buffer.from(b64, "base64").toString("utf8"));
   const decodeHeaders = (headers = []) =>
     Object.fromEntries(headers.flatMap((h) => Object.entries(h).map(([k, bytes]) => [k, Buffer.from(bytes).toString("utf8")])));

   export const handler = async (event) => {
     console.log(`eventSource=${event.eventSource} arn=${event.eventSourceArn ?? "(self-managed)"} bootstrap=${event.bootstrapServers}`);
     let processed = 0;
     for (const [topicPartition, records] of Object.entries(event.records)) {
       console.log(`batch ${topicPartition}: ${records.length} record(s)`);
       for (const r of records) {
         const key = decode(r.key);
         const raw = decode(r.value);
         const headers = decodeHeaders(r.headers);
         let order;
         try {
           order = JSON.parse(raw);
         } catch {
           // poison pill: log + bỏ qua (KHÔNG throw — throw sẽ khiến Lambda retry CẢ batch mãi mãi)
           console.error(`POISON ${r.topic}-${r.partition}@${r.offset} key=${key} value=${raw}`);
           continue;
         }
         // Nghiệp vụ mẫu: chỉ log; production ghi DynamoDB bằng conditional write theo orderId (idempotent — ESM là at-least-once)
         console.log(JSON.stringify({ topic: r.topic, partition: r.partition, offset: r.offset, ts: r.timestamp, key, headers, order }));
         processed++;
       }
     }
     return { processed };   // trả về gì cũng được; ném lỗi ⇒ retry cả batch (BisectBatchOnFunctionError/ReportBatchItemFailures để tinh hơn)
   };
   ```

   `events/event-msk.json` — event mẫu MSK **đầy đủ** (2 record ở `orders-0`, 1 record ở `orders-2`; value là base64 của JSON order):

   ```json
   {
     "eventSource": "aws:kafka",
     "eventSourceArn": "arn:aws:kafka:ap-southeast-1:123456789012:cluster/orders-serverless/1a2b3c4d-5e6f-7a8b-9c0d-1e2f3a4b5c6d-s2",
     "bootstrapServers": "boot-abcdefgh.c1.kafka-serverless.ap-southeast-1.amazonaws.com:9098",
     "records": {
       "orders-0": [
         {
           "topic": "orders",
           "partition": 0,
           "offset": 15,
           "timestamp": 1757900000123,
           "timestampType": "CREATE_TIME",
           "key": "b3JkZXItMTAwMQ==",
           "value": "eyJvcmRlcklkIjoib3JkZXItMTAwMSIsImN1c3RvbWVySWQiOiJjdXN0LTQyIiwic3RhdHVzIjoiUEFJRCIsImFtb3VudCI6MjUwfQ==",
           "headers": [
             { "eventType": [79, 114, 100, 101, 114, 80, 97, 105, 100] },
             { "eventId": [51, 102, 50, 97, 57, 99, 49, 101, 45, 55, 98, 52, 100, 45, 52, 101, 48, 97, 45, 57, 102, 49, 98, 45, 50, 99, 51, 100, 52, 101, 53, 102, 54, 97, 55, 98] }
           ]
         },
         {
           "topic": "orders",
           "partition": 0,
           "offset": 16,
           "timestamp": 1757900000456,
           "timestampType": "CREATE_TIME",
           "key": "b3JkZXItMTAwMg==",
           "value": "eyJvcmRlcklkIjoib3JkZXItMTAwMiIsImN1c3RvbWVySWQiOiJjdXN0LTciLCJzdGF0dXMiOiJQRU5ESU5HIiwiYW1vdW50Ijo5OX0=",
           "headers": []
         }
       ],
       "orders-2": [
         {
           "topic": "orders",
           "partition": 2,
           "offset": 7,
           "timestamp": 1757900000789,
           "timestampType": "CREATE_TIME",
           "key": null,
           "value": "SGVsbG8sIHRoaXMgaXMgYSB0ZXN0Lg==",
           "headers": []
         }
       ]
     }
   }
   ```

   > 📌 Giải mã tay để tin: `echo b3JkZXItMTAwMQ== | base64 -d` → `order-1001`; record cuối là chuỗi `Hello, this is a test.` (không phải JSON) → handler coi là **poison pill**. So với `Kinesis` ESM: `Records[]` là **array phẳng** với `kinesis.data` base64; MSK là **map theo topic-partition**.

   `template.yaml` — cho SAM (chỉ để `sam local invoke`, không `sam deploy` trong lab này):

   ```yaml
   # ~/kafka-labs/week-09/lambda-orders/template.yaml
   AWSTemplateFormatVersion: "2010-09-09"
   Transform: AWS::Serverless-2016-10-31
   Resources:
     OrdersConsumer:
       Type: AWS::Serverless::Function
       Properties:
         FunctionName: orders-consumer
         Runtime: nodejs22.x          # đổi nodejs24.x nếu region đã có runtime này
         Handler: index.handler
         CodeUri: .
         Timeout: 30                  # ESM Kafka: tối đa 14 phút (không phải 15)
         MemorySize: 256
   ```
2. **Test local, miễn phí** với SAM (cần Docker đang chạy).

   ```bash
   cd ~/kafka-labs/week-09/lambda-orders
   sam local invoke OrdersConsumer -e events/event-msk.json
   ```
   Output mẫu (log đi ra stderr, kết quả hàm dòng cuối):
   ```
   eventSource=aws:kafka arn=arn:aws:kafka:...:cluster/orders-serverless/... bootstrap=boot-abcdefgh...:9098
   batch orders-0: 2 record(s)
   {"topic":"orders","partition":0,"offset":15,"ts":1757900000123,"key":"order-1001","headers":{"eventType":"OrderPaid","eventId":"3f2a9c1e-7b4d-4e0a-9f1b-2c3d4e5f6a7b"},"order":{"orderId":"order-1001","customerId":"cust-42","status":"PAID","amount":250}}
   {"topic":"orders","partition":0,"offset":16,...,"key":"order-1002","headers":{},"order":{"orderId":"order-1002",...,"status":"PENDING","amount":99}}
   batch orders-2: 1 record(s)
   POISON orders-2@7 key=null value=Hello, this is a test.
   {"processed":2}
   ```
3. **AWS**: VPC endpoint cho **Lambda** và **STS** trong subnet của cluster. Poller của ESM tạo ENI **trong subnet cluster** và phải gọi được Lambda/STS; default VPC là subnet public nhưng ENI không có public IP ⇒ **không ra Internet được qua IGW** ⇒ cần interface endpoint (hoặc NAT). Thiếu bước này ESM kẹt ở `PROBLEM: Connection error`.

   ```bash
   export EP_LAMBDA=$(aws ec2 create-vpc-endpoint --vpc-id $VPC_ID --vpc-endpoint-type Interface \
     --service-name com.amazonaws.$AWS_REGION.lambda --subnet-ids $SUBNET_A $SUBNET_B --security-group-ids $SG_ID \
     --private-dns-enabled --query VpcEndpoint.VpcEndpointId --output text)
   export EP_STS=$(aws ec2 create-vpc-endpoint --vpc-id $VPC_ID --vpc-endpoint-type Interface \
     --service-name com.amazonaws.$AWS_REGION.sts --subnet-ids $SUBNET_A $SUBNET_B --security-group-ids $SG_ID \
     --private-dns-enabled --query VpcEndpoint.VpcEndpointId --output text)
   echo "$EP_LAMBDA $EP_STS"    # ~0,01 USD/giờ mỗi endpoint — nhớ xoá
   ```
4. **AWS**: execution role = managed policy **`AWSLambdaMSKExecutionRole`** + inline `kafka-cluster:*` cho topic `orders`, group `orders-lambda`.

   ```bash
   cd ~/kafka-labs/week-09/lambda-orders
   cat > lambda-trust.json <<'EOF'
   { "Version": "2012-10-17", "Statement": [ { "Effect": "Allow", "Principal": { "Service": "lambda.amazonaws.com" }, "Action": "sts:AssumeRole" } ] }
   EOF
   aws iam create-role --role-name orders-lambda-role --assume-role-policy-document file://lambda-trust.json >/dev/null
   aws iam attach-role-policy --role-name orders-lambda-role --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaMSKExecutionRole

   cat > lambda-kafka-policy.json <<EOF
   {
     "Version": "2012-10-17",
     "Statement": [
       { "Effect": "Allow",
         "Action": ["kafka-cluster:Connect", "kafka-cluster:DescribeCluster", "kafka-cluster:DescribeClusterDynamicConfiguration"],
         "Resource": "arn:aws:kafka:$AWS_REGION:$ACCOUNT_ID:cluster/$CLUSTER_NAME/$CLUSTER_UUID" },
       { "Effect": "Allow",
         "Action": ["kafka-cluster:DescribeTopic", "kafka-cluster:ReadData"],
         "Resource": "arn:aws:kafka:$AWS_REGION:$ACCOUNT_ID:topic/$CLUSTER_NAME/$CLUSTER_UUID/orders" },
       { "Effect": "Allow",
         "Action": ["kafka-cluster:DescribeGroup", "kafka-cluster:AlterGroup"],
         "Resource": "arn:aws:kafka:$AWS_REGION:$ACCOUNT_ID:group/$CLUSTER_NAME/$CLUSTER_UUID/orders-lambda" }
     ]
   }
   EOF
   aws iam put-role-policy --role-name orders-lambda-role --policy-name msk-orders-read --policy-document file://lambda-kafka-policy.json
   sleep 10
   ```

   > 📌 `AWSLambdaMSKExecutionRole` gồm `kafka:DescribeCluster(V2)`, `kafka:GetBootstrapBrokers`, `ec2:CreateNetworkInterface / DescribeNetworkInterfaces / DescribeVpcs / DescribeSubnets / DescribeSecurityGroups / DeleteNetworkInterface`, `logs:*`. Đây là quyền để **poller tạo ENI trong VPC** — không phải quyền Kafka. Quyền Kafka (`kafka-cluster:*`) đi riêng vì cluster dùng IAM auth.
5. **AWS**: deploy function bằng zip + tạo ESM với **filter** chỉ nhận `status = PAID`.

   ```bash
   zip -q function.zip index.mjs
   export FN_ARN=$(aws lambda create-function --function-name orders-consumer --runtime nodejs22.x \
     --handler index.handler --zip-file fileb://function.zip --timeout 30 --memory-size 256 \
     --role arn:aws:iam::$ACCOUNT_ID:role/orders-lambda-role --query FunctionArn --output text)
   aws lambda wait function-active-v2 --function-name orders-consumer

   export ESM_UUID=$(aws lambda create-event-source-mapping \
     --function-name orders-consumer \
     --event-source-arn $CLUSTER_ARN \
     --topics orders \
     --starting-position LATEST \
     --batch-size 100 \
     --maximum-batching-window-in-seconds 5 \
     --amazon-managed-kafka-event-source-config '{"ConsumerGroupId":"orders-lambda"}' \
     --filter-criteria '{"Filters":[{"Pattern":"{\"value\":{\"status\":[\"PAID\"]}}"}]}' \
     --query UUID --output text)

   until [ "$(aws lambda get-event-source-mapping --uuid $ESM_UUID --query State --output text)" = "Enabled" ]; do
     aws lambda get-event-source-mapping --uuid $ESM_UUID --query '{State:State,Reason:StateTransitionReason,LastResult:LastProcessingResult}'; sleep 20
   done
   ```

   > 📌 `--starting-position LATEST` ⇒ Lambda **không** đọc 3 record cũ từ Lab 9.1; group `orders-lambda` chưa có offset nên vị trí = cuối topic. Nếu group **đã có** offset commit thì offset thắng `StartingPosition`. `Topics`, `StartingPosition`, `ConsumerGroupId` chỉ set được lúc **Create**.
6. **Trong EC2** (Lab 9.1): produce 3 record — 2 `PAID`, 1 `PENDING`, 1 poison.

   ```bash
   cd ~/kafka_2.13-4.0.0
   printf 'order-2001:{"orderId":"order-2001","customerId":"cust-1","status":"PAID","amount":10}\norder-2002:{"orderId":"order-2002","customerId":"cust-2","status":"PENDING","amount":20}\norder-2003:{"orderId":"order-2003","customerId":"cust-3","status":"PAID","amount":30}\norder-2004:not-json-at-all\n' | \
     bin/kafka-console-producer.sh --bootstrap-server $BOOTSTRAP --producer.config client-iam.properties \
       --topic orders --property parse.key=true --property key.separator=:
   ```
7. **Máy bạn**: xem log Lambda (chờ ≤ 5 s batching window + vài giây poll).

   ```bash
   aws logs tail /aws/lambda/orders-consumer --since 5m --follow
   # Ctrl+C khi thấy 2 dòng JSON order-2001 và order-2003
   aws lambda get-event-source-mapping --uuid $ESM_UUID --query '{State:State,LastResult:LastProcessingResult}'
   ```

### ✅ Kiểm chứng

- `sam local invoke` in đúng 2 order decode được + 1 dòng `POISON` + `{"processed":2}` — **không cần AWS**.
- ESM chuyển `Creating → Enabled`; `LastProcessingResult` = `OK` (hoặc `No records processed` trước khi produce). Nếu kẹt `PROBLEM: Connection error` ⇒ thiếu VPC endpoint (bước 3) hoặc SG chưa mở 9098/443 self-reference.
- CloudWatch Logs chỉ có **order-2001 và order-2003** (`PAID`); `order-2002` (`PENDING`) và `order-2004` (không phải JSON) bị **FilterCriteria loại trước khi invoke** — filter trên `value` chỉ match được record JSON hợp lệ, nên poison pill cũng không tới hàm (nhưng handler vẫn phải phòng như bước 1 vì filter là tuỳ chọn).
- `kafka-consumer-groups.sh --describe --group orders-lambda --command-config client-iam.properties` trong EC2 cho LAG = 0 sau khi Lambda xử lý — Lambda **commit offset như consumer group thường**.

### 🧹 Dọn dẹp

```bash
aws lambda delete-event-source-mapping --uuid $ESM_UUID >/dev/null
aws lambda delete-function --function-name orders-consumer
aws iam delete-role-policy --role-name orders-lambda-role --policy-name msk-orders-read
aws iam detach-role-policy --role-name orders-lambda-role --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaMSKExecutionRole
aws iam delete-role --role-name orders-lambda-role
aws logs delete-log-group --log-group-name /aws/lambda/orders-consumer 2>/dev/null
# GIỮ VPC endpoint nếu làm Lab 9.7 ngay; nếu không:
aws ec2 delete-vpc-endpoints --vpc-endpoint-ids $EP_LAMBDA $EP_STS
# Rồi chạy khối Dọn dẹp của Lab 9.1 (delete-cluster, EC2, role, SG) nếu không làm Lab 9.7.
```

### 🧠 Ý nghĩa với đề thi (DVA) và công việc

- "Lambda nhận message từ MSK" = **ESM poll**, không phải Kafka push; cùng gia đình với `Kinesis`/`DynamoDB Streams`/`SQS` ESM — batch 100 (max 10.000), window ≤ 300 s, invoke đồng bộ, **retry cả batch** ⇒ hàm phải **idempotent**.
- Payload MSK: `records` map `topic-partition` → array, **base64** key/value, headers mảng byte; quên decode ⇒ "chuỗi lạ".
- **`FilterCriteria`** thay `if` trong code ⇒ giảm invoke, giảm tiền; pattern chạy trên `value` đã decode (JSON).
- Timeout hàm cho ESM Kafka **≤ 14 phút**; `DestinationConfig.OnFailure` (SQS/SNS/S3) là DLQ mức batch; `ReportBatchItemFailures`/`BisectBatchOnFunctionError` để không retry cả 100 record vì 1 record hỏng.
- Networking là nơi hỏng nhiều nhất: ENI poller nằm trong subnet cluster ⇒ cần SG mở port broker và đường tới Lambda/STS (NAT hoặc endpoint).

---

## Lab 9.3 ⭐ — Transactional Outbox + CDC bằng Debezium `EventRouter` (LOCAL, miễn phí)

**🎯 Mục tiêu:** Chạy Postgres (`wal_level=logical`) + Debezium Connect chồng lên cluster Tuần 1; tạo bảng `orders` + `outbox`; app Node.js (`pg`) ghi order **và** outbox trong **một** transaction; đăng ký Postgres connector với `transforms=outbox` (`io.debezium.transforms.outbox.EventRouter`); kiểm chứng event ra topic **`outbox.event.Order`** với **key = `aggregateid`**, header `id` (eventId) + `eventType`. Chứng minh rollback ⇒ **không có event** (điều dual-write không làm được).
**🧩 Luyện kỹ năng (liên quan đề):**

- Dual-write vì sao sai; Outbox = ghi event vào bảng cùng DB transaction; relay = **transaction log tailing (CDC)**.
- Cột outbox chuẩn Debezium: `id` · `aggregatetype` (→ topic) · `aggregateid` (→ key) · `type` · `payload`.
- `EventRouter` options: `route.topic.replacement` mặc định `outbox.event.${routedByValue}`, `table.fields.additional.placement=type:header:eventType`, `table.expand.json.payload`; DELETE bị bỏ qua ⇒ INSERT + DELETE cùng transaction để outbox không phình.
- At-least-once ⇒ consumer idempotent (Lab 9.4).

**⏱️ ~40 phút** · **Yêu cầu trước:** Chuẩn bị chung mục 1–2; đã có `docker-compose.debezium.yml` từ Tuần 5 (nếu chưa, tạo theo khối rút gọn dưới).

### Các bước

1. Khởi động Postgres + Debezium Connect chồng lên cluster.

   ```bash
   cd ~/kafka-labs
   export COMPOSE_FILE=docker-compose.cluster.yml:docker-compose.debezium.yml
   docker compose up -d
   until curl -s localhost:8084/ >/dev/null; do sleep 3; echo "waiting debezium..."; done
   curl -s localhost:8084/connector-plugins | grep -o 'io.debezium.connector.postgresql.PostgresConnector'
   ```

   <details>
   <summary>docker-compose.debezium.yml (rút gọn — bản đầy đủ + giải thích ở Tuần 5 Lab 5.6)</summary>

   ```yaml
   # ~/kafka-labs/docker-compose.debezium.yml — override: Postgres (logical WAL) + Connect cluster thứ 2 chạy Debezium
   # Debezium REST: http://localhost:8084 (container 8083) · Postgres: localhost:5432 (postgres/postgres, db shop)
   services:
     postgres:
       image: postgres:16
       container_name: postgres
       hostname: postgres
       command: ["postgres", "-c", "wal_level=logical", "-c", "max_wal_senders=4", "-c", "max_replication_slots=4"]
       ports:
         - "5432:5432"
       environment:
         POSTGRES_USER: postgres
         POSTGRES_PASSWORD: postgres
         POSTGRES_DB: shop

     debezium:
       image: quay.io/debezium/connect:3.1        # 3.0/3.1 đều chạy được lab này
       container_name: debezium
       hostname: debezium
       depends_on: [postgres, kafka-1, kafka-2, kafka-3]
       ports:
         - "8084:8083"
       environment:
         BOOTSTRAP_SERVERS: kafka-1:19092,kafka-2:19092,kafka-3:19092
         GROUP_ID: debezium-cluster
         CONFIG_STORAGE_TOPIC: dbz-configs
         OFFSET_STORAGE_TOPIC: dbz-offsets
         STATUS_STORAGE_TOPIC: dbz-status
         CONFIG_STORAGE_REPLICATION_FACTOR: 3      # min.insync.replicas=2 của cluster Tuần 1
         OFFSET_STORAGE_REPLICATION_FACTOR: 3
         STATUS_STORAGE_REPLICATION_FACTOR: 3
         KEY_CONVERTER_SCHEMAS_ENABLE: "false"
         VALUE_CONVERTER_SCHEMAS_ENABLE: "false"
   ```

   </details>
2. Tạo bảng `orders` + `outbox` (đúng tên cột mặc định của `EventRouter`) và **tạo trước topic đích** (MSK mặc định `auto.create.topics.enable=false` — tập thói quen).

   ```bash
   docker exec -i postgres psql -U postgres -d shop <<'EOF'
   CREATE TABLE orders (
     id          TEXT PRIMARY KEY,
     customer_id TEXT NOT NULL,
     amount      NUMERIC(10,2) NOT NULL,
     status      TEXT NOT NULL,
     created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
   );
   CREATE TABLE outbox (
     id            UUID PRIMARY KEY,          -- eventId → Kafka header "id"
     aggregatetype TEXT NOT NULL,             -- "Order" → topic outbox.event.Order
     aggregateid   TEXT NOT NULL,             -- orderId → Kafka key (ordering theo order)
     type          TEXT NOT NULL,             -- OrderCreated / OrderPaid → header eventType
     payload       JSONB NOT NULL,            -- Kafka value
     created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
   );
   EOF
   export KAFKA_CTR=kafka-1 KAFKA_BS=kafka-1:19092
   kt --create --topic outbox.event.Order --partitions 3 --replication-factor 3
   ```
3. Đăng ký connector Debezium Postgres với SMT `outbox`.

   ```bash
   cd ~/kafka-labs/week-09
   cat > outbox-connector.json <<'EOF'
   {
     "name": "outbox-connector",
     "config": {
       "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
       "tasks.max": "1",
       "database.hostname": "postgres",
       "database.port": "5432",
       "database.user": "postgres",
       "database.password": "postgres",
       "database.dbname": "shop",
       "topic.prefix": "shop",
       "plugin.name": "pgoutput",
       "slot.name": "outbox_slot",
       "publication.autocreate.mode": "filtered",
       "table.include.list": "public.outbox",
       "tombstones.on.delete": "false",

       "transforms": "outbox",
       "transforms.outbox.type": "io.debezium.transforms.outbox.EventRouter",
       "transforms.outbox.route.by.field": "aggregatetype",
       "transforms.outbox.route.topic.replacement": "outbox.event.${routedByValue}",
       "transforms.outbox.table.field.event.id": "id",
       "transforms.outbox.table.field.event.key": "aggregateid",
       "transforms.outbox.table.field.event.payload": "payload",
       "transforms.outbox.table.fields.additional.placement": "type:header:eventType",
       "transforms.outbox.table.expand.json.payload": "true",

       "key.converter": "org.apache.kafka.connect.storage.StringConverter",
       "value.converter": "org.apache.kafka.connect.json.JsonConverter",
       "value.converter.schemas.enable": "false"
     }
   }
   EOF
   curl -s -X POST -H "Content-Type: application/json" --data @outbox-connector.json localhost:8084/connectors | python3 -m json.tool | head -5
   sleep 5
   curl -s localhost:8084/connectors/outbox-connector/status | python3 -c "import json,sys; s=json.load(sys.stdin); print(s['connector']['state'], [t['state'] for t in s['tasks']])"
   # RUNNING ['RUNNING']
   ```

   > 📌 4 dòng `route.by.field` / `table.field.event.*` chính là **giá trị mặc định** — in ra để bạn thấy mapping cột → topic/key/header. Muốn topic tên `Order-events` như README mô tả thì đổi `route.topic.replacement` thành `${routedByValue}-events` (và tạo topic đó trước).
4. Mở **terminal 2** consumer console in key + header, giữ chạy suốt lab.

   ```bash
   export KAFKA_CTR=kafka-1 KAFKA_BS=kafka-1:19092
   kcc --topic outbox.event.Order --from-beginning \
     --property print.key=true --property print.headers=true --property print.partition=true
   ```
5. App Node.js `outbox-writer.mjs`: ghi `orders` + `outbox` trong **một** transaction; `FAIL=1` mô phỏng crash sau 2 INSERT ⇒ ROLLBACK.

   ```javascript
   // ~/kafka-labs/week-09/outbox-writer.mjs — Transactional Outbox: business row + outbox row trong CÙNG transaction
   import pg from "pg";
   import { randomUUID } from "node:crypto";

   const client = new pg.Client({ connectionString: "postgres://postgres:postgres@localhost:5432/shop" });
   await client.connect();

   const orderId = process.argv[2] ?? `order-${Date.now()}`;
   const status = process.argv[3] ?? "CREATED";
   const eventType = status === "PAID" ? "OrderPaid" : "OrderCreated";
   const eventId = randomUUID();                       // eventId do PRODUCER sinh → consumer dedup (Lab 9.4)
   const payload = { orderId, customerId: "cust-42", amount: 250, status, eventId };

   try {
     await client.query("BEGIN");
     await client.query(
       `INSERT INTO orders (id, customer_id, amount, status) VALUES ($1, $2, $3, $4)
        ON CONFLICT (id) DO UPDATE SET status = EXCLUDED.status`,
       [orderId, payload.customerId, payload.amount, status]
     );
     await client.query(
       `INSERT INTO outbox (id, aggregatetype, aggregateid, type, payload) VALUES ($1, $2, $3, $4, $5)`,
       [eventId, "Order", orderId, eventType, JSON.stringify(payload)]
     );
     if (process.env.FAIL === "1") throw new Error("simulated crash AFTER both inserts, BEFORE commit");
     if (process.env.KEEP_OUTBOX !== "1") {
       // Debezium bỏ qua DELETE nhưng INSERT vẫn nằm trong WAL → xoá ngay để bảng outbox luôn rỗng
       await client.query(`DELETE FROM outbox WHERE id = $1`, [eventId]);
     }
     await client.query("COMMIT");
     console.log(`COMMIT  order=${orderId} status=${status} eventId=${eventId} type=${eventType}`);
   } catch (e) {
     await client.query("ROLLBACK");
     console.log(`ROLLBACK order=${orderId}: ${e.message}`);
   } finally {
     await client.end();
   }
   ```

   ```bash
   cd ~/kafka-labs/week-09
   KEEP_OUTBOX=1 node outbox-writer.mjs order-1001 CREATED     # giữ row để bạn SELECT thấy
   node outbox-writer.mjs order-1001 PAID                       # INSERT+DELETE cùng transaction
   node outbox-writer.mjs order-1002 CREATED
   FAIL=1 node outbox-writer.mjs order-1003 CREATED             # ROLLBACK → KHÔNG có event
   docker exec -i postgres psql -U postgres -d shop -c "SELECT id, status FROM orders ORDER BY id;" \
                                                   -c "SELECT aggregateid, type FROM outbox;"
   ```
6. Đọc **terminal 2**: 3 event (2 của `order-1001`, 1 của `order-1002`), **không** có `order-1003`.

   Output mẫu:
   ```
   Partition:1	id:3f2a9c1e-7b4d-4e0a-9f1b-2c3d4e5f6a7b,eventType:OrderCreated	order-1001	{"orderId":"order-1001","customerId":"cust-42","amount":250,"status":"CREATED","eventId":"3f2a9c1e-..."}
   Partition:1	id:9b0c...,eventType:OrderPaid	order-1001	{"orderId":"order-1001",...,"status":"PAID",...}
   Partition:0	id:7d1e...,eventType:OrderCreated	order-1002	{"orderId":"order-1002",...}
   ```
7. So sánh với **dual-write** (chỉ đọc, không cần chạy): nếu app `INSERT orders` → `COMMIT` → `producer.send()` mà crash giữa 2 bước ⇒ DB có order, Kafka không có event; nếu `send()` trước rồi DB rollback ⇒ event "ma". Outbox: `order-1003` rollback ⇒ **cả hai** cùng biến mất. Kafka transaction (Lab 3.5) **không** bao Postgres.

### ✅ Kiểm chứng

- Connector `RUNNING`; `kt --list` có `outbox.event.Order` (+ `dbz-*` internal). Không có topic `shop.public.outbox` vì SMT đã **route** record sang topic theo `aggregatetype`.
- Terminal 2: 2 event của `order-1001` **cùng partition** (key = `aggregateid` = `order-1001`), đúng thứ tự `OrderCreated` → `OrderPaid`; header `id` = UUID trong cột `id`, header `eventType` từ cột `type`.
- `order-1003` không xuất hiện (ROLLBACK). Bảng `outbox` chỉ còn 1 row (lần chạy `KEEP_OUTBOX=1`); các lần khác đã DELETE nhưng event vẫn ra — DELETE bị `EventRouter` lọc.
- `docker exec -i postgres psql -U postgres -d shop -c "SELECT slot_name, active FROM pg_replication_slots;"` → `outbox_slot | t`.

### 🧹 Dọn dẹp

```bash
curl -s -X DELETE localhost:8084/connectors/outbox-connector
docker exec -i postgres psql -U postgres -d shop -c "SELECT pg_drop_replication_slot('outbox_slot');" \
  -c "DROP PUBLICATION IF EXISTS dbz_publication;" -c "DROP TABLE IF EXISTS outbox, orders;"
# Ctrl+C terminal 2
kt --delete --topic outbox.event.Order
# Tắt Postgres + Debezium (giữ cluster cho Lab 9.4–9.6)
docker compose stop debezium postgres && docker compose rm -f debezium postgres
unset COMPOSE_FILE
```

### 🧠 Ý nghĩa với đề thi

- "Đảm bảo event chỉ phát khi DB commit / atomically update DB and publish" ⇒ **Outbox + CDC**, không phải `acks=all`, không phải Kafka transaction (chỉ atomic Kafka→Kafka).
- `EventRouter`: `aggregatetype` → **topic**, `aggregateid` → **key** (ordering theo aggregate), `id` → header (eventId để dedup), `type` → header/envelope tuỳ `additional.placement`.
- Outbox là **at-least-once** (relay có thể publish lại sau crash) ⇒ downstream **idempotent consumer** — Lab 9.4 dùng đúng header `id`/`eventId` này.
- Trên AWS: Debezium chạy trên **MSK Connect** (plugin zip từ S3), RDS Postgres cần `rds.logical_replication=1`; "CDC phía AWS-native" tương đương là `DynamoDB Streams` + `Lambda`.

---

## Lab 9.4 — Idempotent consumer: dedup theo `eventId` và theo `(topic, partition, offset)`

**🎯 Mục tiêu:** Consumer `kafkajs` ghi "side effect" (bảng `ledger` trong SQLite) và dedup bằng bảng `processed_events` **trong cùng transaction SQLite**: khoá chính = header `eventId`, fallback `topic-partition-offset`. Chạy, rồi `kcg --reset-offsets --to-earliest --execute` để **replay toàn bộ** → số dòng `ledger` **không đổi**. Lặp lại với `DEDUP=off` để thấy gấp đôi.
**🧩 Luyện kỹ năng (liên quan đề):**

- Kafka là **at-least-once** mặc định (auto-commit sau xử lý, rebalance, replay) ⇒ consumer phải chịu duplicate.
- 2 chiến lược dedup: **business id** (`eventId` do producer sinh — chống cả duplicate từ producer app retry) vs **`(topic,partition,offset)`** (không cần producer hợp tác, chống replay/reset offset).
- Ghi kết quả + dấu "đã xử lý" trong **cùng transaction** của store đích; store cần **TTL**.

**⏱️ ~25 phút** · **Yêu cầu trước:** Chuẩn bị chung; Node 24 (`node:sqlite` có sẵn — có thể in `ExperimentalWarning`, bỏ qua; Node < 22.13 cần `--experimental-sqlite`).

### Các bước

1. Tạo topic và producer gửi 10 order **có header `eventId`** (5 order cuối cố tình **không** có header để thấy fallback).

   ```bash
   export KAFKA_CTR=kafka-1 KAFKA_BS=kafka-1:19092
   kt --create --topic orders --partitions 3 --replication-factor 3
   ```

   ```javascript
   // ~/kafka-labs/week-09/lab94-producer.mjs — 10 order, 5 đầu có header eventId, 5 sau không
   import { randomUUID } from "node:crypto";
   import { kafka } from "./kafka.mjs";

   const producer = kafka.producer({ idempotent: true, maxInFlightRequests: 1 });   // chống duplicate do RETRY NỘI BỘ (Tuần 3)
   await producer.connect();
   const messages = Array.from({ length: 10 }, (_, i) => {
     const orderId = `order-${3000 + i}`;
     const eventId = randomUUID();
     return {
       key: orderId,
       value: JSON.stringify({ orderId, customerId: `cust-${i % 3}`, amount: (i + 1) * 10, status: "PAID" }),
       headers: i < 5 ? { eventId, eventType: "OrderPaid" } : { eventType: "OrderPaid" },   // 5 record sau: không có eventId
     };
   });
   const res = await producer.send({ topic: "orders", acks: -1, messages });
   console.log("sent:", res.map((r) => `p${r.partition}@${r.baseOffset}`).join(" "));
   await producer.disconnect();
   ```
2. Consumer idempotent `lab94-consumer.mjs`.

   ```javascript
   // ~/kafka-labs/week-09/lab94-consumer.mjs — idempotent consumer với node:sqlite
   // DEDUP=on (mặc định) | off. Store: ./lab94-<DEDUP>.db (2 file để so sánh)
   import { DatabaseSync } from "node:sqlite";
   import { kafka, hdr } from "./kafka.mjs";

   const DEDUP = (process.env.DEDUP ?? "on") === "on";
   const db = new DatabaseSync(`./lab94-${DEDUP ? "on" : "off"}.db`);
   db.exec(`
     CREATE TABLE IF NOT EXISTS processed_events (
       dedup_key   TEXT PRIMARY KEY,           -- eventId hoặc topic-partition-offset
       strategy    TEXT NOT NULL,              -- 'eventId' | 'offset'
       topic TEXT, partition INTEGER, "offset" INTEGER,
       processed_at TEXT NOT NULL DEFAULT (datetime('now'))
     );
     CREATE TABLE IF NOT EXISTS ledger (        -- SIDE EFFECT nghiệp vụ: mỗi dòng = 1 lần ghi sổ
       id INTEGER PRIMARY KEY AUTOINCREMENT, order_id TEXT NOT NULL, amount REAL NOT NULL, at TEXT NOT NULL DEFAULT (datetime('now'))
     );`);
   const insertProcessed = db.prepare(`INSERT INTO processed_events (dedup_key, strategy, topic, partition, "offset") VALUES (?, ?, ?, ?, ?)`);
   const insertLedger = db.prepare(`INSERT INTO ledger (order_id, amount) VALUES (?, ?)`);
   const count = (t) => db.prepare(`SELECT count(*) AS n FROM ${t}`).get().n;

   let handled = 0, skipped = 0;
   function process({ topic, partition, message }) {
     const order = JSON.parse(message.value.toString());
     const eventId = hdr(message, "eventId");
     const dedupKey = eventId ?? `${topic}-${partition}-${message.offset}`;     // chiến lược 1, fallback chiến lược 2
     const strategy = eventId ? "eventId" : "offset";

     db.exec("BEGIN");
     try {
       if (DEDUP) insertProcessed.run(dedupKey, strategy, topic, partition, Number(message.offset)); // PK violation ⇒ duplicate
       insertLedger.run(order.orderId, order.amount);                                                 // side effect
       db.exec("COMMIT");
       handled++;
       console.log(`HANDLED  p${partition}@${message.offset} ${order.orderId} via ${strategy}`);
     } catch (e) {
       db.exec("ROLLBACK");
       if (String(e.message).includes("UNIQUE constraint failed")) {
         skipped++;
         console.log(`DUPLICATE p${partition}@${message.offset} ${order.orderId} (${strategy}) → skip`);
       } else throw e;
     }
   }

   const consumer = kafka.consumer({ groupId: "lab94-idem" });
   await consumer.connect();
   await consumer.subscribe({ topic: "orders", fromBeginning: true });
   const timer = setTimeout(async () => {
     console.log(`\nDEDUP=${DEDUP ? "on" : "off"} handled=${handled} skipped=${skipped} | ledger rows=${count("ledger")} processed_events rows=${count("processed_events")}`);
     await consumer.disconnect(); db.close(); process.exit(0);
   }, 6000);
   await consumer.run({ eachMessage: async (p) => { process(p); timer.refresh(); } });
   ```
3. Chạy lần 1 (DEDUP on), rồi **replay** bằng reset offset, chạy lần 2.

   ```bash
   cd ~/kafka-labs/week-09
   node lab94-producer.mjs
   node lab94-consumer.mjs                    # lần 1: HANDLED ×10 → ledger rows=10
   kcg --describe --group lab94-idem          # LAG = 0
   kcg --group lab94-idem --topic orders --reset-offsets --to-earliest --execute     # group inactive mới reset được
   node lab94-consumer.mjs                    # lần 2 (REPLAY): DUPLICATE ×10 → ledger rows VẪN 10
   ```
4. Đối chứng **không dedup**: cùng kịch bản với `DEDUP=off` (file db riêng).

   ```bash
   kcg --group lab94-idem --topic orders --reset-offsets --to-earliest --execute
   DEDUP=off node lab94-consumer.mjs          # ledger rows=10
   kcg --group lab94-idem --topic orders --reset-offsets --to-earliest --execute
   DEDUP=off node lab94-consumer.mjs          # ledger rows=20  ← ghi sổ 2 lần!
   ```
5. Điền bảng so sánh (số mẫu):

   | Lần chạy | `DEDUP` | `handled` | `skipped` | `ledger` rows | Chiến lược dùng |
   |---|---|---|---|---|---|
   | 1 (lần đầu) | on | 10 | 0 | **10** | 5 `eventId` + 5 `offset` |
   | 2 (replay `--to-earliest`) | on | 0 | 10 | **10** | dedup bắt cả 10 |
   | 3 (lần đầu) | off | 10 | 0 | 10 | — |
   | 4 (replay) | off | 10 | 0 | **20** | duplicate lọt hết |

### ✅ Kiểm chứng

- Lần 2: đúng **10 dòng `DUPLICATE`**, `ledger rows=10` không đổi — số bản ghi side-effect **bất biến** qua replay.
- `sqlite3 lab94-on.db "SELECT strategy, count(*) FROM processed_events GROUP BY 1"` (nếu có `sqlite3`; hoặc thêm câu query vào script) → `eventId 5 / offset 5`.
- Lần 4 (`DEDUP=off`): `ledger rows=20` — đây là hiện tượng "consumer xử lý trùng sau reset offset" mà đề hay mô tả.
- Suy nghĩ thêm: nếu **producer app** gọi `send()` 2 lần cho cùng order với `eventId` mới ⇒ chiến lược `eventId` **không** bắt được (2 id khác) và `offset` cũng không (2 offset khác) ⇒ cần dedup theo **business key** (`orderId` + upsert). Chọn key dedup theo nguồn duplicate.

### 🧹 Dọn dẹp

```bash
kcg --delete --group lab94-idem
kt --delete --topic orders
rm -f ~/kafka-labs/week-09/lab94-*.db
```

### 🧠 Ý nghĩa với đề thi

- Kafka + outbox + retry = **at-least-once** ⇒ "consumer processes duplicates after rebalance/reset" ⇒ **idempotent consumer**, không phải bug producer.
- Dedup theo **`eventId`** cần producer sinh id (header/payload) và store có PK/conditional write (`DynamoDB attribute_not_exists`, bảng PK); dedup theo **`(topic,partition,offset)`** không cần producer hợp tác, hợp cho replay.
- Điểm chết người: ghi `processed_events` và side effect phải **cùng transaction** — ghi tách rời thì crash giữa 2 bước lại tạo duplicate hoặc mất.
- Rẻ nhất khi làm được: **upsert/PUT** thay `INSERT`/`+=` — idempotent bằng nghiệp vụ.

---

## Lab 9.5 — Retry topics + DLQ (non-blocking) với `pause()` + `setTimeout`

**🎯 Mục tiêu:** Consumer chính đọc `orders`; lỗi **tạm thời** ⇒ publish sang `orders-retry-1` kèm header `attempts`, `retry-at`, `original-*`, `error`; consumer retry đọc `orders-retry-1/2/3`, **`pause()` partition** tới `retry-at` (backoff 2 s → 4 s → 8 s) rồi xử lý; fail đủ **3 lần** ⇒ `orders-dlq`. **Poison pill** (không parse được) ⇒ DLQ **ngay**. Quan sát bằng mắt việc **mất ordering** của non-blocking retry.
**🧩 Luyện kỹ năng (liên quan đề):**

- Kafka **không có DLQ/`maxReceiveCount` sẵn** cho consumer (khác `SQS`) ⇒ tự thiết kế bằng topic + header.
- Blocking retry (pause/resume tại chỗ, giữ ordering, chặn partition, rủi ro `max.poll.interval.ms`) vs non-blocking (retry topic, không chặn, **mất ordering**).
- Phân loại lỗi: tạm thời ⇒ retry exponential backoff; poison/validation ⇒ DLQ ngay.

**⏱️ ~35 phút** · **Yêu cầu trước:** Chuẩn bị chung.

### Các bước

1. Tạo 5 topic.

   ```bash
   export KAFKA_CTR=kafka-1 KAFKA_BS=kafka-1:19092
   for t in orders orders-retry-1 orders-retry-2 orders-retry-3 orders-dlq; do kt --create --topic $t --partitions 3 --replication-factor 3; done
   ```
2. Module dùng chung `lab95-common.mjs`: xử lý nghiệp vụ giả lập + hàm route lỗi.

   ```javascript
   // ~/kafka-labs/week-09/lab95-common.mjs
   import { hdr } from "./kafka.mjs";

   export const MAX_ATTEMPTS = 3;                                   // sau 3 lần retry → DLQ
   export const RETRY_TOPIC = (n) => `orders-retry-${n}`;           // n = 1..3
   export const DLQ = "orders-dlq";
   export const backoffMs = (attempt) => 2000 * 2 ** (attempt - 1); // 2s, 4s, 8s (+ jitter ở production)

   export class PoisonPill extends Error {}
   export class TransientError extends Error {}

   // Nghiệp vụ giả lập: value phải là JSON; order.failUntilAttempt = n → fail khi attempt < n
   export function handleOrder(message, attempt) {
     let order;
     try { order = JSON.parse(message.value.toString()); } catch { throw new PoisonPill(`cannot parse: ${message.value}`); }
     if (typeof order.orderId !== "string") throw new PoisonPill("missing orderId");   // validation vĩnh viễn → DLQ
     if ((order.failUntilAttempt ?? 0) > attempt) throw new TransientError(`downstream 503 (attempt ${attempt})`);
     return order;
   }

   // Chuyển record sang retry topic kế tiếp hoặc DLQ, kèm header ngữ cảnh
   export async function routeFailure(producer, { topic, partition, message }, err, attempt) {
     const original = {
       "original-topic": hdr(message, "original-topic") ?? topic,
       "original-partition": hdr(message, "original-partition") ?? String(partition),
       "original-offset": hdr(message, "original-offset") ?? String(message.offset),
     };
     const toDlq = err instanceof PoisonPill || attempt >= MAX_ATTEMPTS;
     const nextAttempt = attempt + 1;
     const target = toDlq ? DLQ : RETRY_TOPIC(nextAttempt);
     const retryAt = toDlq ? "" : String(Date.now() + backoffMs(nextAttempt));
     await producer.send({
       topic: target, acks: -1,
       messages: [{
         key: message.key, value: message.value,
         headers: {
           ...Object.fromEntries(Object.entries(message.headers ?? {}).filter(([k]) => k === "eventId")),
           ...original,
           attempts: String(toDlq ? attempt : nextAttempt),
           "retry-at": retryAt,
           error: `${err.constructor.name}: ${err.message}`,
           "failed-at": new Date().toISOString(),
         },
       }],
     });
     console.log(`  ↳ ${toDlq ? "DLQ " : "RETRY"} ${target} key=${message.key} attempts=${toDlq ? attempt : nextAttempt}${retryAt ? ` retry-at=+${backoffMs(nextAttempt)}ms` : ""} (${err.message})`);
   }
   ```
3. Consumer chính `lab95-main.mjs` — không chặn partition, fail ⇒ route ngay.

   ```javascript
   // ~/kafka-labs/week-09/lab95-main.mjs — consumer topic chính: xử lý, lỗi → retry-1 hoặc DLQ, KHÔNG chặn
   import { kafka } from "./kafka.mjs";
   import { handleOrder, routeFailure } from "./lab95-common.mjs";

   const producer = kafka.producer();
   const consumer = kafka.consumer({ groupId: "orders-main" });
   await producer.connect(); await consumer.connect();
   await consumer.subscribe({ topic: "orders", fromBeginning: true });

   await consumer.run({
     eachMessage: async ({ topic, partition, message }) => {
       const attempt = 0;                                     // lần xử lý đầu
       try {
         const order = handleOrder(message, attempt);
         console.log(`${new Date().toISOString()} MAIN  OK   p${partition}@${message.offset} key=${message.key} ${order.orderId}`);
       } catch (err) {
         console.log(`${new Date().toISOString()} MAIN  FAIL p${partition}@${message.offset} key=${message.key}`);
         await routeFailure(producer, { topic, partition, message }, err, attempt);   // publish xong → offset này được commit → partition chạy tiếp
       }
     },
   });
   process.on("SIGINT", async () => { await consumer.disconnect(); await producer.disconnect(); process.exit(0); });
   ```
4. Consumer retry `lab95-retry.mjs` — **`eachBatch` + `pause()` + `setTimeout(resume)`**, không `sleep` trong handler.

   ```javascript
   // ~/kafka-labs/week-09/lab95-retry.mjs — consumer 3 retry topic; delay bằng pause() partition tới retry-at
   import { kafka, hdr } from "./kafka.mjs";
   import { handleOrder, routeFailure, RETRY_TOPIC, MAX_ATTEMPTS } from "./lab95-common.mjs";

   const producer = kafka.producer();
   const consumer = kafka.consumer({ groupId: "orders-retry" });
   await producer.connect(); await consumer.connect();
   for (let n = 1; n <= MAX_ATTEMPTS; n++) await consumer.subscribe({ topic: RETRY_TOPIC(n), fromBeginning: true });

   await consumer.run({
     eachBatchAutoResolve: false,        // tự resolveOffset: record chưa tới giờ KHÔNG được coi là xong
     eachBatch: async ({ batch, resolveOffset, heartbeat, isRunning, isStale }) => {
       const { topic, partition } = batch;
       for (const message of batch.messages) {
         if (!isRunning() || isStale()) break;
         const retryAt = Number(hdr(message, "retry-at") ?? 0);
         const wait = retryAt - Date.now();
         if (wait > 0) {
           // Chưa tới giờ: PAUSE partition này, hẹn RESUME, và DỪNG batch mà không resolve → sau resume kafkajs fetch lại đúng record này
           consumer.pause([{ topic, partitions: [partition] }]);
           setTimeout(() => consumer.resume([{ topic, partitions: [partition] }]), wait);
           console.log(`${new Date().toISOString()} RETRY wait ${wait}ms  ${topic} p${partition}@${message.offset} key=${message.key} (paused partition)`);
           return;
         }
         const attempt = Number(hdr(message, "attempts"));   // 1..3
         try {
           const order = handleOrder(message, attempt);
           console.log(`${new Date().toISOString()} RETRY OK   ${topic} p${partition}@${message.offset} key=${message.key} ${order.orderId} attempt=${attempt}`);
         } catch (err) {
           console.log(`${new Date().toISOString()} RETRY FAIL ${topic} p${partition}@${message.offset} key=${message.key} attempt=${attempt}`);
           await routeFailure(producer, { topic, partition, message }, err, attempt);
         }
         resolveOffset(message.offset);
         await heartbeat();
       }
     },
   });
   process.on("SIGINT", async () => { await consumer.disconnect(); await producer.disconnect(); process.exit(0); });
   ```

   > 📌 Vì sao `eachBatch` + `eachBatchAutoResolve: false`? Trong kafkajs, `pause()` bên trong `eachMessage` mà không `throw` thì record vẫn bị coi là đã xử lý. Với `eachBatch`, record chưa `resolveOffset` sẽ được fetch lại sau khi `resume()` — đúng nghĩa "delay". `heartbeat()` giữ session; delay dài không đụng `max.poll.interval.ms` vì handler trả về ngay.
5. Producer thử nghiệm `lab95-producer.mjs`: 4 record, cùng key `cust-1` cho 2 record đầu để thấy mất ordering.

   ```javascript
   // ~/kafka-labs/week-09/lab95-producer.mjs
   import { randomUUID } from "node:crypto";
   import { kafka } from "./kafka.mjs";
   const producer = kafka.producer(); await producer.connect();
   const msg = (key, order) => ({ key, value: typeof order === "string" ? order : JSON.stringify(order), headers: { eventId: randomUUID() } });
   await producer.send({
     topic: "orders", acks: -1,
     messages: [
       msg("cust-1", { orderId: "A-flaky-then-ok", failUntilAttempt: 2 }),   // fail ở main + retry-1, OK ở retry-2 (attempt 2)
       msg("cust-1", { orderId: "B-ok-immediately" }),                        // cùng key với A, gửi SAU A
       msg("cust-2", { orderId: "C-always-fails", failUntilAttempt: 99 }),   // retry-1 → 2 → 3 → DLQ
       msg("cust-3", "{not valid json"),                                      // poison pill → DLQ ngay
     ],
   });
   console.log("sent 4 records"); await producer.disconnect();
   ```
6. Chạy: terminal 1 main, terminal 2 retry, terminal 3 DLQ watcher, terminal 4 producer.

   ```bash
   # T1
   cd ~/kafka-labs/week-09 && node lab95-main.mjs
   # T2
   cd ~/kafka-labs/week-09 && node lab95-retry.mjs
   # T3
   kcc --topic orders-dlq --from-beginning --property print.key=true --property print.headers=true
   # T4
   cd ~/kafka-labs/week-09 && node lab95-producer.mjs
   ```
   Timeline mẫu (T1 + T2 gộp, rút gọn):
   ```
   T+0.0s MAIN  FAIL p1@0 key=cust-1              ↳ RETRY orders-retry-1 attempts=1 retry-at=+2000ms
   T+0.0s MAIN  OK   p1@1 key=cust-1 B-ok-immediately        ← B xử lý XONG trước A dù gửi sau (mất ordering theo key)
   T+0.0s MAIN  FAIL p0@0 key=cust-2              ↳ RETRY orders-retry-1 attempts=1 retry-at=+2000ms
   T+0.0s MAIN  FAIL p2@0 key=cust-3              ↳ DLQ  orders-dlq attempts=0 (PoisonPill: cannot parse)
   T+0.1s RETRY wait 1900ms orders-retry-1 p1@0 key=cust-1 (paused partition)
   T+2.0s RETRY FAIL orders-retry-1 p1@0 key=cust-1 attempt=1   ↳ RETRY orders-retry-2 attempts=2 retry-at=+4000ms
   T+2.0s RETRY FAIL orders-retry-1 p0@0 key=cust-2 attempt=1   ↳ RETRY orders-retry-2 attempts=2 retry-at=+4000ms
   T+6.1s RETRY OK   orders-retry-2 ... key=cust-1 A-flaky-then-ok attempt=2
   T+6.1s RETRY FAIL orders-retry-2 ... key=cust-2 attempt=2     ↳ RETRY orders-retry-3 attempts=3 retry-at=+8000ms
   T+14.2s RETRY FAIL orders-retry-3 ... key=cust-2 attempt=3    ↳ DLQ  orders-dlq attempts=3 (TransientError: downstream 503)
   ```

### ✅ Kiểm chứng

- T3 (DLQ) có đúng **2 record**: `cust-3` (`attempts:0`, `error:PoisonPill…`, tới **ngay lập tức**) và `cust-2` (`attempts:3`, `error:TransientError…`, tới sau ~14 s). Header `original-topic:orders`, `original-partition`, `original-offset` giữ nguyên qua 3 chặng.
- `A-flaky-then-ok` thành công ở `orders-retry-2` với `attempt=2`; **`B-ok-immediately` (cùng key `cust-1`, gửi sau A) hoàn tất trước A ~6 s** ⇒ non-blocking retry **mất ordering theo key** — đây là cái giá phải trả.
- Trong lúc chờ, T1 (main) **không bị chặn**: gửi thêm `node lab95-producer.mjs` lần 2, record OK vẫn được xử lý ngay.
- `kcg --describe --group orders-retry` trong lúc pause: LAG > 0 ở partition đang pause (record chưa resolve) — dùng lag retry topic làm chỉ báo "downstream đang ốm".
- Đối chứng **blocking retry** (tự làm, 5 phút): trong `lab95-main.mjs` thay `routeFailure` bằng `pause()` partition + `setTimeout(resume, backoff)` + `throw err` ⇒ A được retry **tại chỗ**, B chờ sau A (giữ ordering) nhưng **cả partition** đứng, kể cả record của key khác trên partition đó.

### 🧹 Dọn dẹp

```bash
# Ctrl+C T1, T2, T3
for t in orders orders-retry-1 orders-retry-2 orders-retry-3 orders-dlq; do kt --delete --topic $t; done
kcg --delete --group orders-main; kcg --delete --group orders-retry
```

### 🧠 Ý nghĩa với đề thi

- "Retry without blocking, ordering not required" ⇒ **retry topics** + header `attempts`/`retry-at`; "retry but keep per-key ordering" ⇒ **blocking retry `pause()`/`resume()`** (hoặc ordered-retry với registry key).
- **Poison pill ⇒ DLQ ngay**, không retry — retry vô ích và nếu retry tại chỗ còn kéo `max.poll.interval.ms` (5 phút) ⇒ rebalance.
- Backoff **exponential + jitter**; header phải có original topic/partition/offset, attempt count, error, timestamp để **redrive thủ công** (Kafka không có `StartMessageMoveTask` như `SQS`).
- Có sẵn DLQ chỉ ở **Connect sink** (`errors.tolerance=all` + `errors.deadletterqueue.topic.name`) và **Streams** exception handler; `Lambda` ESM có `OnFailure` destination mức batch.

---

## Lab 9.6 — Partition sizing bằng thí nghiệm: `kafka-producer-perf-test.sh` × `kafka-consumer-perf-test.sh`

**🎯 Mục tiêu:** Đo throughput producer trên topic **1 / 3 / 12 partition**, và throughput consumer với **1 vs 3 consumer** cùng group trên topic 3 và 12 partition; lập **bảng kết quả** (MB/s, records/s, p99 latency) và rút ra công thức `partitions = max(T / P_throughput, T / C_throughput, C)`; xác nhận **không giảm được** số partition.
**🧩 Luyện kỹ năng (liên quan đề):**

- Đọc output perf-test: `records/sec`, `MB/sec`, `avg latency`, `99th`; consumer: `MB.sec`, `nMsg.sec`, `rebalance.time.ms`, `fetch.time.ms`.
- Consumer parallelism ≤ partition; consumer thứ N+1 idle.
- Over-partition: FD, election, latency; `--alter --partitions` chỉ tăng.

**⏱️ ~30 phút** · **Yêu cầu trước:** Chuẩn bị chung; máy rảnh (đóng app nặng để số đo ổn định).

### Các bước

1. Tạo 3 topic.

   ```bash
   export KAFKA_CTR=kafka-1 KAFKA_BS=kafka-1:19092
   kt --create --topic perf-1  --partitions 1  --replication-factor 3
   kt --create --topic perf-3  --partitions 3  --replication-factor 3
   kt --create --topic perf-12 --partitions 12 --replication-factor 3
   ```
2. Producer perf: 300.000 record × 1 KB, `acks=all`, batch/linger giống nhau cho 3 topic. Chạy **2 lần mỗi topic**, lấy lần 2 (lần 1 warm-up JIT/page cache).

   ```bash
   pperf() {   # $1 = topic
     echo "=== producer → $1 ==="
     docker exec -it kafka-1 /opt/kafka/bin/kafka-producer-perf-test.sh --topic $1 \
       --num-records 300000 --record-size 1024 --throughput -1 \
       --producer-props bootstrap.servers=kafka-1:19092 acks=all linger.ms=5 batch.size=65536 compression.type=none | tail -1
   }
   for t in perf-1 perf-3 perf-12; do pperf $t; pperf $t; done
   ```
   Dòng cuối mẫu: `300000 records sent, 61234.5 records/sec (59.80 MB/sec), 412.30 ms avg latency, 1187.00 ms max latency, 390 ms 50th, 820 ms 95th, 1010 ms 99th, 1150 ms 99.9th.`
3. Consumer perf **1 consumer** (mỗi topic đã có 600.000 record từ 2 lần producer; đọc 300.000).

   ```bash
   cperf() {   # $1 = topic  $2 = group
     docker exec -it kafka-1 /opt/kafka/bin/kafka-consumer-perf-test.sh --bootstrap-server kafka-1:19092 \
       --topic $1 --group $2 --num-records 300000 --timeout 30000 2>/dev/null | tail -2
   }
   cperf perf-1  c1-p1
   cperf perf-3  c1-p3
   cperf perf-12 c1-p12
   ```
   Output 2 dòng: header `start.time, end.time, data.consumed.in.MB, MB.sec, data.consumed.in.nMsg, nMsg.sec, rebalance.time.ms, fetch.time.ms, fetch.MB.sec, fetch.nMsg.sec` rồi dòng số. Lấy **`MB.sec`** và **`nMsg.sec`**.
4. Consumer perf **3 consumer cùng group** chạy song song (mỗi consumer đọc 100.000 — tổng 300.000). Group mới để bắt đầu từ đầu.

   ```bash
   cperf3() {   # $1 = topic  $2 = group  — 3 tiến trình song song, tổng throughput = cộng 3 dòng MB.sec
     echo "=== 3 consumers → $1 ==="
     for i in 1 2 3; do
       docker exec kafka-1 /opt/kafka/bin/kafka-consumer-perf-test.sh --bootstrap-server kafka-1:19092 \
         --topic $1 --group $2 --num-records 100000 --timeout 30000 2>/dev/null | tail -1 &
     done
     wait
   }
   cperf3 perf-1  c3-p1      # 1 partition: 2 consumer IDLE → 2 dòng có thể timeout/0 message (đúng như lý thuyết)
   cperf3 perf-3  c3-p3
   cperf3 perf-12 c3-p12
   kcg --describe --group c3-p12 | head -15      # CONSUMER-ID: mỗi consumer giữ 4 partition
   ```

   > ⚠️ Với `perf-1`, chỉ 1 consumer có partition; 2 consumer kia chờ tới `--timeout` rồi thoát với 0 message — **chính là bài học** "consumer > partition = idle". Nếu 3 tiến trình join lệch nhau gây rebalance, `rebalance.time.ms` sẽ lớn — ghi lại con số đó.
5. Điền **bảng kết quả** (số dưới là ví dụ trên laptop; **số của bạn khác**, chú ý xu hướng):

   | Topic | Partition | Producer records/s | Producer MB/s | Producer p99 (ms) | 1 consumer MB/s | 3 consumer tổng MB/s | Ghi chú |
   |---|---|---|---|---|---|---|---|
   | `perf-1` | 1 | | | | | (chỉ 1 consumer có việc) | 1 leader = 1 broker gánh hết |
   | `perf-3` | 3 | | | | | | leader rải 3 broker |
   | `perf-12` | 12 | | | | | | mỗi consumer 4 partition |

   Câu hỏi để tự rút kết luận:
   - Producer: 1 → 3 partition tăng vì **3 leader trên 3 broker** cùng nhận ghi; 3 → 12 tăng ít hoặc **giảm nhẹ p99** xấu hơn vì batch bị chia nhỏ theo partition (cùng `linger.ms`) và nhiều request hơn — over-partition có giá.
   - Consumer: 1 → 3 consumer chỉ tăng khi **partition ≥ 3**; trên `perf-1` là 0 lợi ích.
6. Xác nhận **không giảm được** partition.

   ```bash
   kt --alter --topic perf-12 --partitions 1
   # → org.apache.kafka.common.errors.InvalidPartitionsException: Topic currently has 12 partitions, which is higher than the requested 1.
   kt --alter --topic perf-1 --partitions 2 && kt --describe --topic perf-1     # tăng thì được (nhưng phá key mapping — Tuần 3)
   ```
7. Áp công thức vào bài toán mẫu: mục tiêu **T = 100 MB/s**, producer đo được `P ≈ 25 MB/s`/partition, consumer xử lý nghiệp vụ `C ≈ 5 MB/s`/consumer, cần tối đa 20 consumer song song ⇒ `max(100/25, 100/5, 20) = max(4, 20, 20) = 20` ⇒ chọn **24** (bội số dễ chia, dư tăng trưởng). Nếu chọn 12 ⇒ chỉ 12 consumer có việc ⇒ tối đa 60 MB/s ⇒ lag tăng mãi.

### ✅ Kiểm chứng

- Bảng có đủ 3 hàng × cột producer + consumer; `perf-3`/`perf-12` có tổng 3 consumer **≥** 1 consumer; `perf-1` có 2 consumer 0 message.
- `kcg --describe --group c3-p12` (trong lúc chạy hoặc ngay sau) cho 12 dòng, 3 `CONSUMER-ID` khác nhau, mỗi id 4 partition.
- Bước 6 in đúng `InvalidPartitionsException` với chữ "higher than the requested".

### 🧹 Dọn dẹp

```bash
for t in perf-1 perf-3 perf-12; do kt --delete --topic $t; done
for g in c1-p1 c1-p3 c1-p12 c3-p1 c3-p3 c3-p12; do kcg --delete --group $g 2>/dev/null; done
unset -f pperf cperf cperf3
```

### 🧠 Ý nghĩa với đề thi

- **Consumer parallelism ≤ partition**: "tăng throughput consumer" ⇒ tăng partition trước (và không quá số consumer × k).
- Công thức khởi điểm `max(T/P, T/C, C_max)` × growth; đo `P`/`C` bằng perf-test, không đoán.
- Over-partition: nhiều FD/segment, leader election lâu hơn khi broker chết, batch nhỏ ⇒ **latency tăng**; MSK Serverless trần **2.400** leader partition/cluster; khuyến nghị ≤ ~4.000/broker.
- **Không giảm được** partition ⇒ sai thì topic mới + migrate; chọn **bội số** (6/12/24).

---

## Lab 9.7 (Option) — `EventBridge Pipes`: MSK → `SQS` không viết consumer (AWS — CÓ PHÍ)

**🎯 Mục tiêu:** Tạo pipe với source MSK (`ManagedStreamingKafkaParameters`: topic, `StartingPosition`, `BatchSize`, `ConsumerGroupID`), filter `status=PAID`, target `SQS`; produce từ EC2 → `receive-message` thấy record ở SQS. Xoá pipe + queue + **cluster**.
**🧩 Luyện kỹ năng (liên quan DVA):**

- Pipes = "ESM không cần Lambda": source → filter → (enrichment) → target; cùng tham số với Lambda ESM.
- Role của pipe cần quyền **đọc MSK (`kafka:*`, `kafka-cluster:*`, ENI)** + **ghi target (`sqs:SendMessage`)**.
- Khi nào Pipes (chuyển + lọc + enrich) vs Lambda ESM (logic tuỳ ý).

**⏱️ ~20 phút** · **Yêu cầu trước:** Lab 9.1 (cluster, EC2, `$CLUSTER_ARN`, `$CLUSTER_UUID`) và Lab 9.2 bước 3 (VPC endpoint Lambda/STS — poller của Pipes dùng cùng hạ tầng). **Chi phí:** Pipes tính theo request (rất nhỏ); phí lớn vẫn là **cluster-hour** ⇒ xoá ngay sau lab.

### Các bước

1. Tạo queue SQS.

   ```bash
   export QUEUE_URL=$(aws sqs create-queue --queue-name orders-from-msk --query QueueUrl --output text)
   export QUEUE_ARN=$(aws sqs get-queue-attributes --queue-url $QUEUE_URL --attribute-names QueueArn --query Attributes.QueueArn --output text)
   ```
2. Role cho pipe (trust `pipes.amazonaws.com`) với quyền source MSK + target SQS.

   ```bash
   cat > pipes-trust.json <<EOF
   { "Version": "2012-10-17", "Statement": [ { "Effect": "Allow", "Principal": { "Service": "pipes.amazonaws.com" }, "Action": "sts:AssumeRole",
     "Condition": { "StringEquals": { "aws:SourceAccount": "$ACCOUNT_ID" } } } ] }
   EOF
   aws iam create-role --role-name msk-pipe-role --assume-role-policy-document file://pipes-trust.json >/dev/null
   cat > pipes-policy.json <<EOF
   {
     "Version": "2012-10-17",
     "Statement": [
       { "Effect": "Allow",
         "Action": ["kafka:DescribeClusterV2", "kafka:GetBootstrapBrokers"],
         "Resource": "$CLUSTER_ARN" },
       { "Effect": "Allow",
         "Action": ["ec2:CreateNetworkInterface", "ec2:DeleteNetworkInterface", "ec2:DescribeNetworkInterfaces",
                    "ec2:DescribeSecurityGroups", "ec2:DescribeSubnets", "ec2:DescribeVpcs"],
         "Resource": "*" },
       { "Effect": "Allow",
         "Action": ["kafka-cluster:Connect", "kafka-cluster:DescribeClusterDynamicConfiguration"],
         "Resource": "arn:aws:kafka:$AWS_REGION:$ACCOUNT_ID:cluster/$CLUSTER_NAME/$CLUSTER_UUID" },
       { "Effect": "Allow",
         "Action": ["kafka-cluster:DescribeTopic", "kafka-cluster:ReadData"],
         "Resource": "arn:aws:kafka:$AWS_REGION:$ACCOUNT_ID:topic/$CLUSTER_NAME/$CLUSTER_UUID/orders" },
       { "Effect": "Allow",
         "Action": ["kafka-cluster:DescribeGroup", "kafka-cluster:AlterGroup"],
         "Resource": "arn:aws:kafka:$AWS_REGION:$ACCOUNT_ID:group/$CLUSTER_NAME/$CLUSTER_UUID/orders-pipe" },
       { "Effect": "Allow", "Action": ["sqs:SendMessage"], "Resource": "$QUEUE_ARN" }
     ]
   }
   EOF
   aws iam put-role-policy --role-name msk-pipe-role --policy-name msk-to-sqs --policy-document file://pipes-policy.json
   sleep 10
   ```
3. Tạo pipe với filter.

   ```bash
   aws pipes create-pipe --name msk-orders-to-sqs \
     --role-arn arn:aws:iam::$ACCOUNT_ID:role/msk-pipe-role \
     --source $CLUSTER_ARN \
     --source-parameters '{
       "ManagedStreamingKafkaParameters": {
         "TopicName": "orders",
         "StartingPosition": "LATEST",
         "BatchSize": 10,
         "MaximumBatchingWindowInSeconds": 5,
         "ConsumerGroupID": "orders-pipe"
       },
       "FilterCriteria": { "Filters": [ { "Pattern": "{\"value\":{\"status\":[\"PAID\"]}}" } ] }
     }' \
     --target $QUEUE_ARN \
     --target-parameters '{"SqsQueueParameters":{}}'

   until [ "$(aws pipes describe-pipe --name msk-orders-to-sqs --query CurrentState --output text)" = "RUNNING" ]; do
     aws pipes describe-pipe --name msk-orders-to-sqs --query '{State:CurrentState,Reason:StateReason}'; sleep 20
   done
   ```
4. **Trong EC2**: produce 2 record (1 `PAID`, 1 `PENDING`).

   ```bash
   cd ~/kafka_2.13-4.0.0
   printf 'order-4001:{"orderId":"order-4001","status":"PAID","amount":11}\norder-4002:{"orderId":"order-4002","status":"PENDING","amount":22}\n' | \
     bin/kafka-console-producer.sh --bootstrap-server $BOOTSTRAP --producer.config client-iam.properties \
       --topic orders --property parse.key=true --property key.separator=:
   ```
5. **Máy bạn**: nhận ở SQS và decode.

   ```bash
   sleep 15
   aws sqs receive-message --queue-url $QUEUE_URL --max-number-of-messages 10 --wait-time-seconds 10 \
     --query 'Messages[].Body' --output text | tee pipe-body.json
   # Mỗi Body là JSON record kiểu MSK (topic/partition/offset/key/value base64) — có thể là 1 object hoặc 1 mảng tuỳ batch; decode value:
   python3 - <<'PY'
   import json, base64
   for line in open("pipe-body.json"):
       line = line.strip()
       if not line: continue
       body = json.loads(line)
       for r in (body if isinstance(body, list) else [body]):
           print(r["topic"], r["partition"], r["offset"], "→", base64.b64decode(r["value"]).decode())
   PY
   ```

### ✅ Kiểm chứng

- Pipe `RUNNING`; SQS nhận **1** message (batch chứa `order-4001` `PAID`); `order-4002` bị filter loại. Nếu `ApproximateNumberOfMessages` = 0 sau 1 phút ⇒ xem `StateReason`, thường là role thiếu `kafka-cluster:*` hoặc thiếu VPC endpoint.
- Body có shape giống record Lambda ESM (`topic`, `partition`, `offset`, `timestamp`, `key`, `value` base64, `headers`) — Pipes và Lambda ESM dùng **cùng poller**.

### 🧹 Dọn dẹp — XOÁ HẾT TÀI NGUYÊN AWS CỦA TUẦN

```bash
aws pipes delete-pipe --name msk-orders-to-sqs
aws sqs delete-queue --queue-url $QUEUE_URL
aws iam delete-role-policy --role-name msk-pipe-role --policy-name msk-to-sqs
aws iam delete-role --role-name msk-pipe-role
aws ec2 delete-vpc-endpoints --vpc-endpoint-ids $EP_LAMBDA $EP_STS          # từ Lab 9.2
# Cuối cùng: khối Dọn dẹp Lab 9.1 (delete-cluster, terminate EC2, role, SG) — rồi kiểm tra lần cuối:
aws kafka list-clusters-v2 --query 'ClusterInfoList[].ClusterName'         # []
aws lambda list-event-source-mappings --query 'EventSourceMappings[].UUID' # []
aws ec2 describe-vpc-endpoints --filters Name=vpc-id,Values=$VPC_ID --query 'VpcEndpoints[].VpcEndpointId'  # []
aws ec2 describe-instances --filters Name=tag:Name,Values=msk-lab-client Name=instance-state-name,Values=running --query 'Reservations[].Instances[].InstanceId'  # []
```

> 💸 Sau khi xoá, mở **Billing → Cost Explorer** ngày hôm sau, lọc service `Amazon Managed Streaming for Apache Kafka` để chắc chắn phí đã dừng.

### 🧠 Ý nghĩa với đề thi (DVA/SAA)

- "Route Kafka → SQS/Step Functions/Kinesis **không viết code**" ⇒ **`EventBridge Pipes`**; cần logic tuỳ ý ⇒ Lambda ESM; cần cả hai ⇒ Pipes + enrichment Lambda.
- Tham số source Pipes = tham số ESM (`StartingPosition`, `BatchSize`, `MaximumBatchingWindowInSeconds`, `ConsumerGroupID`, `FilterCriteria`).
- Role pipe là **1 role cho cả source và target** — lỗi "pipe không chạy" gần như luôn là role thiếu quyền một phía hoặc mạng (endpoint/SG).

---

> ✅ Xong 7 lab (tối thiểu 9.3 → 9.6 local + 9.1 hoặc 9.2 trên AWS)? **Kiểm tra lần cuối `aws kafka list-clusters-v2` trả rỗng** — cluster Serverless bỏ quên là khoản tốn nhất tuần này. Đối chiếu [Lab checklist trong README](README.md#-lab-checklist), làm [bộ câu hỏi luyện tập](questions.md) (28 câu), rồi bước vào **🎯 FULL MOCK #1 (60 câu / 90 phút, ngưỡng ≥ 75%)** theo quy trình Buổi D — ghi điểm theo domain trước khi sang Tuần 10.
