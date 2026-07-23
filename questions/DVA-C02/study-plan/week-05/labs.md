# 🧪 Hands-on Labs — Tuần 5: Messaging (`SQS`/`SNS`/`Kinesis`) + `Step Functions` + Caching

> Lab cầm tay chỉ việc, chạy được trên tài khoản AWS thật (Free Tier). LUÔN chạy phần Dọn dẹp cuối mỗi lab.
> ⚙️ Yêu cầu chung: đã cấu hình `AWS CLI v2` (xem Lab 1.1 tuần 1) + IAM đủ quyền cho dịch vụ trong lab.
> Về [plan tuần](README.md) · [Câu hỏi luyện tập](questions.md) · [Kế hoạch tổng](../../DVA-C02-STUDY-PLAN.md)

---

## 🔧 Chuẩn bị chung (làm 1 lần, dùng cho mọi lab)

```bash
# 1) Đặt region (đổi theo bạn — ví dụ ap-southeast-1 hoặc us-east-1)
export AWS_REGION=ap-southeast-1
export AWS_DEFAULT_REGION=$AWS_REGION

# 2) Lấy Account ID để dựng ARN
export ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "Account: $ACCOUNT_ID · Region: $AWS_REGION"
```

> 🧠 **Bản đồ tích hợp `Lambda`** (BẮT BUỘC nhớ, hay bị nhầm):
> - `SNS` → `Lambda`: **async push** (subscribe + `add-permission` principal `sns.amazonaws.com`).
> - `Kinesis`/`SQS`/`DynamoDB Streams` → `Lambda`: **event source mapping** (Lambda **POLL**), không phải push.
> - `S3` → `Lambda`: async qua bucket notification. `API Gateway` → `Lambda`: sync.

---

## Lab 5.1 — Fan-out `SNS` → nhiều `SQS` ⭐
**🎯 Mục tiêu:** Publish **1** message lên `SNS` topic và thấy **2** queue `SQS` cùng nhận được bản sao — mô hình fan-out kinh điển của đề.
**🧩 Luyện kỹ năng (liên quan đề):**
- Decouple + broadcast 1→N (task statement: "nhiều hệ thống xử lý độc lập cùng 1 event").
- Bẫy #1 của tuần: publish thành công nhưng queue **không nhận** vì thiếu **queue access policy** cho `SNS`.
- `RawMessageDelivery=true` để `SQS` nhận đúng body gốc.

**⏱️ ~25 phút** · **Yêu cầu trước:** đã làm phần Chuẩn bị chung.

### Các bước
1. Tạo 2 queue và lấy URL + ARN của chúng.
   ```bash
   ANALYTICS_URL=$(aws sqs create-queue --queue-name orders-analytics --query QueueUrl --output text)
   BILLING_URL=$(aws sqs create-queue --queue-name orders-billing --query QueueUrl --output text)

   ANALYTICS_ARN=$(aws sqs get-queue-attributes --queue-url "$ANALYTICS_URL" \
     --attribute-names QueueArn --query Attributes.QueueArn --output text)
   BILLING_ARN=$(aws sqs get-queue-attributes --queue-url "$BILLING_URL" \
     --attribute-names QueueArn --query Attributes.QueueArn --output text)
   ```

2. Tạo topic.
   ```bash
   TOPIC_ARN=$(aws sns create-topic --name new-orders --query TopicArn --output text)
   ```

3. **Cấp queue policy** cho phép `SNS` gọi `sqs:SendMessage` (điều kiện `aws:SourceArn` = ARN topic). Thiếu bước này → fan-out "im lặng" thất bại.
   ```bash
   cat > sqs-policy.json <<EOF
   {
     "Policy": "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":{\"Service\":\"sns.amazonaws.com\"},\"Action\":\"sqs:SendMessage\",\"Resource\":\"QUEUE_ARN\",\"Condition\":{\"ArnEquals\":{\"aws:SourceArn\":\"$TOPIC_ARN\"}}}]}"
   }
   EOF

   # Gắn cho từng queue (thay QUEUE_ARN tương ứng)
   sed "s#QUEUE_ARN#$ANALYTICS_ARN#" sqs-policy.json > policy-analytics.json
   sed "s#QUEUE_ARN#$BILLING_ARN#"   sqs-policy.json > policy-billing.json
   aws sqs set-queue-attributes --queue-url "$ANALYTICS_URL" --attributes file://policy-analytics.json
   aws sqs set-queue-attributes --queue-url "$BILLING_URL"   --attributes file://policy-billing.json
   ```

4. Subscribe từng queue vào topic (`--protocol sqs`, bật raw delivery).
   ```bash
   aws sns subscribe --topic-arn "$TOPIC_ARN" --protocol sqs \
     --notification-endpoint "$ANALYTICS_ARN" --attributes RawMessageDelivery=true
   aws sns subscribe --topic-arn "$TOPIC_ARN" --protocol sqs \
     --notification-endpoint "$BILLING_ARN"   --attributes RawMessageDelivery=true
   ```

5. Publish **1** message.
   ```bash
   aws sns publish --topic-arn "$TOPIC_ARN" --message '{"orderId":"1001","total":250}'
   ```

### ✅ Kiểm chứng
- Đọc **cả hai** queue → mỗi queue đều có 1 bản sao của message. Đó chính là fan-out.
  ```bash
  aws sqs receive-message --queue-url "$ANALYTICS_URL" --max-number-of-messages 1 --wait-time-seconds 5
  aws sqs receive-message --queue-url "$BILLING_URL"   --max-number-of-messages 1 --wait-time-seconds 5
  ```
- (Tùy chọn) Thêm **filter policy** trên 1 subscription rồi publish với `--message-attributes` để thấy chỉ subscriber khớp mới nhận.

### 🧹 Dọn dẹp (tránh tính phí)
```bash
aws sns delete-topic --topic-arn "$TOPIC_ARN"
aws sqs delete-queue --queue-url "$ANALYTICS_URL"
aws sqs delete-queue --queue-url "$BILLING_URL"
rm -f sqs-policy.json policy-analytics.json policy-billing.json
```

### 🧠 Ý nghĩa với đề thi
- "Nhiều consumer cần **cùng** dữ liệu, xử lý độc lập" → **fan-out `SNS` → nhiều `SQS`**, KHÔNG phải 1 `SQS` (mỗi message của `SQS` chỉ 1 consumer xử lý).
- Queue phải có **resource policy** cho phép `SNS` gửi vào — điểm hay bị bỏ sót trong câu hỏi troubleshooting.
- `RawMessageDelivery` quyết định body thô vs bọc JSON của `SNS`.

---

## Lab 5.2 — `SNS` → `Lambda` (async push) ⭐
**🎯 Mục tiêu:** Đăng ký một `Lambda` function làm subscriber của `SNS` topic; publish message → `SNS` **đẩy** (push) invoke function bất đồng bộ.
**🧩 Luyện kỹ năng (liên quan đề):**
- Phân biệt **push** (`SNS`→`Lambda`) vs **poll/event source mapping** (`SQS`/`Kinesis`→`Lambda`).
- Resource-based policy: `lambda add-permission` với principal `sns.amazonaws.com`.
- Cấu trúc event `Records[].Sns.Message`.

**⏱️ ~25 phút** · **Yêu cầu trước:** Chuẩn bị chung.

### Các bước
1. Tạo execution role cho `Lambda` (ghi CloudWatch Logs).
   ```bash
   cat > trust-lambda.json <<'EOF'
   { "Version": "2012-10-17",
     "Statement": [{ "Effect": "Allow",
       "Principal": { "Service": "lambda.amazonaws.com" },
       "Action": "sts:AssumeRole" }] }
   EOF

   aws iam create-role --role-name lab5-lambda-basic-role \
     --assume-role-policy-document file://trust-lambda.json
   aws iam attach-role-policy --role-name lab5-lambda-basic-role \
     --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
   ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/lab5-lambda-basic-role"
   ```

2. Viết handler ghi log nội dung message.
   ```python
   # handler.py
   def handler(event, context):
       for rec in event["Records"]:
           sns = rec["Sns"]
           print(f"[SNS] subject={sns.get('Subject')} message={sns['Message']}")
       return {"status": "ok"}
   ```

3. Đóng gói + tạo function.
   ```bash
   zip function.zip handler.py
   aws lambda create-function --function-name sns-consumer \
     --runtime python3.12 --handler handler.handler \
     --role "$ROLE_ARN" --zip-file fileb://function.zip --timeout 15
   aws lambda wait function-active-v2 --function-name sns-consumer
   FUNCTION_ARN=$(aws lambda get-function --function-name sns-consumer \
     --query Configuration.FunctionArn --output text)
   ```

4. Tạo topic + **cấp quyền cho `SNS`** gọi function (resource-based policy).
   ```bash
   TOPIC_ARN=$(aws sns create-topic --name order-events --query TopicArn --output text)
   aws lambda add-permission --function-name sns-consumer \
     --statement-id sns-invoke --action lambda:InvokeFunction \
     --principal sns.amazonaws.com --source-arn "$TOPIC_ARN"
   ```

5. Subscribe function vào topic (`--protocol lambda`) rồi publish.
   ```bash
   aws sns subscribe --topic-arn "$TOPIC_ARN" --protocol lambda \
     --notification-endpoint "$FUNCTION_ARN"
   aws sns publish --topic-arn "$TOPIC_ARN" --subject "new-order" \
     --message '{"orderId":"2002"}'
   ```

### ✅ Kiểm chứng
- Xem log CloudWatch của function thấy dòng `[SNS] ... message={"orderId":"2002"}`.
  ```bash
  aws logs tail /aws/lambda/sns-consumer --since 5m --follow
  ```
- Nếu **không** thấy invoke: kiểm tra đã chạy `add-permission` với đúng `--source-arn` chưa (lỗi hay gặp nhất).

### 🧹 Dọn dẹp
```bash
aws sns delete-topic --topic-arn "$TOPIC_ARN"
aws lambda delete-function --function-name sns-consumer
aws iam detach-role-policy --role-name lab5-lambda-basic-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
aws iam delete-role --role-name lab5-lambda-basic-role
rm -f handler.py function.zip trust-lambda.json
```

### 🧠 Ý nghĩa với đề thi
- `SNS`→`Lambda` là **asynchronous push**: `SNS` gọi thẳng function, không cần event source mapping.
- Async invoke: `Lambda` tự **retry 2 lần** nếu function lỗi → cân nhắc **DLQ / destinations** cho function.
- Thiếu `add-permission` cho principal `sns.amazonaws.com` = subscribe "confirmed" nhưng không bao giờ invoke.

---

## Lab 5.3 — `SQS` DLQ + `maxReceiveCount` + redrive
**🎯 Mục tiêu:** Cấu hình Dead-Letter Queue, ép 1 "poison message" rơi vào DLQ sau khi vượt `maxReceiveCount`, rồi **redrive** message từ DLQ về queue gốc.
**🧩 Luyện kỹ năng (liên quan đề):**
- `RedrivePolicy` (`deadLetterTargetArn` + `maxReceiveCount`) — poison message pattern.
- `ApproximateReceiveCount` tăng mỗi lần nhận mà không xóa.
- Redrive bằng `start-message-move-task`.

**⏱️ ~20 phút** · **Yêu cầu trước:** Chuẩn bị chung.

### Các bước
1. Tạo DLQ và lấy ARN.
   ```bash
   DLQ_URL=$(aws sqs create-queue --queue-name payments-dlq --query QueueUrl --output text)
   DLQ_ARN=$(aws sqs get-queue-attributes --queue-url "$DLQ_URL" \
     --attribute-names QueueArn --query Attributes.QueueArn --output text)
   ```

2. Tạo queue chính `payments` gắn `RedrivePolicy` (`maxReceiveCount`=3) + visibility ngắn để test nhanh.
   ```bash
   cat > redrive.json <<EOF
   {
     "RedrivePolicy": "{\"deadLetterTargetArn\":\"$DLQ_ARN\",\"maxReceiveCount\":\"3\"}",
     "VisibilityTimeout": "5"
   }
   EOF
   MAIN_URL=$(aws sqs create-queue --queue-name payments \
     --attributes file://redrive.json --query QueueUrl --output text)
   ```

3. Gửi 1 message "lỗi".
   ```bash
   aws sqs send-message --queue-url "$MAIN_URL" --message-body '{"paymentId":"bad-001"}'
   ```

4. Giả lập xử lý thất bại: nhận message nhiều lần nhưng **KHÔNG delete** (đặt visibility=0 để nó xuất hiện lại ngay). Sau 3 lần nhận, lần nhận thứ 4 → message chuyển sang DLQ.
   ```bash
   for i in 1 2 3 4 5; do
     echo "--- attempt $i ---"
     RH=$(aws sqs receive-message --queue-url "$MAIN_URL" \
           --attribute-names ApproximateReceiveCount \
           --query 'Messages[0].ReceiptHandle' --output text)
     if [ "$RH" != "None" ] && [ -n "$RH" ]; then
       aws sqs change-message-visibility --queue-url "$MAIN_URL" \
         --receipt-handle "$RH" --visibility-timeout 0
     else
       echo "queue chính rỗng — message có thể đã vào DLQ"
     fi
   done
   ```

### ✅ Kiểm chứng
- Đọc DLQ → thấy message `bad-001` đã rơi vào đây.
  ```bash
  aws sqs receive-message --queue-url "$DLQ_URL" --wait-time-seconds 5
  ```
- **Redrive** message từ DLQ trở về queue nguồn (điều tra xong, xử lý lại):
  ```bash
  aws sqs start-message-move-task --source-arn "$DLQ_ARN"
  # theo dõi:
  aws sqs list-message-move-tasks --source-arn "$DLQ_ARN"
  ```

### 🧹 Dọn dẹp
```bash
aws sqs delete-queue --queue-url "$MAIN_URL"
aws sqs delete-queue --queue-url "$DLQ_URL"
rm -f redrive.json
```

### 🧠 Ý nghĩa với đề thi
- Message vào DLQ **khi số lần receive vượt `maxReceiveCount` mà chưa bị xóa** (không phải hết retention).
- DLQ đặt trên **queue** (kể cả khi nguồn là event source mapping `SQS`→`Lambda`).
- `start-message-move-task` = cách CLI/console redrive hàng loạt sau khi vá lỗi consumer.

---

## Lab 5.4 — `Kinesis Data Streams` → `Lambda` (event source mapping) ⭐
**🎯 Mục tiêu:** Tạo stream 2 shard, gắn `Lambda` bằng **event source mapping** (`--starting-position LATEST`), `put-records` và quan sát `Lambda` được invoke theo **batch, tách theo shard**.
**🧩 Luyện kỹ năng (liên quan đề):**
- `Kinesis`→`Lambda` là **poll/event source mapping**, batch theo shard (khác `SNS` push).
- Vai trò `partition key` quyết định record vào shard nào (ordering trong shard).
- `LATEST` chỉ xử lý record ghi **sau** khi mapping active.

**⏱️ ~30 phút** · **Yêu cầu trước:** đã có execution role như Lab 5.2 (ở đây dùng role riêng có quyền đọc Kinesis).

### Các bước
1. Tạo stream 2 shard (thấy rõ batch tách theo shard) và chờ ACTIVE.
   ```bash
   aws kinesis create-stream --stream-name lab-stream --shard-count 2
   aws kinesis wait stream-exists --stream-name lab-stream
   STREAM_ARN=$(aws kinesis describe-stream-summary --stream-name lab-stream \
     --query StreamDescriptionSummary.StreamARN --output text)
   ```

2. Tạo role cho `Lambda` với quyền đọc `Kinesis` (managed policy `AWSLambdaKinesisExecutionRole` gồm cả basic logs + GetRecords/GetShardIterator/DescribeStream/ListStreams).
   ```bash
   cat > trust-lambda.json <<'EOF'
   { "Version":"2012-10-17","Statement":[{"Effect":"Allow",
     "Principal":{"Service":"lambda.amazonaws.com"},"Action":"sts:AssumeRole"}] }
   EOF
   aws iam create-role --role-name lab5-lambda-kinesis-role \
     --assume-role-policy-document file://trust-lambda.json
   aws iam attach-role-policy --role-name lab5-lambda-kinesis-role \
     --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaKinesisExecutionRole
   ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/lab5-lambda-kinesis-role"
   ```

3. Handler giải mã record + in shard/partition key.
   ```python
   # handler.py
   import base64
   def handler(event, context):
       print(f"Batch nhận {len(event['Records'])} record")
       for r in event["Records"]:
           data = base64.b64decode(r["kinesis"]["data"]).decode("utf-8")
           print(f"eventID={r['eventID']} pk={r['kinesis']['partitionKey']} data={data}")
       return {"status": "ok"}
   ```

4. Tạo function rồi gắn **event source mapping**.
   ```bash
   zip function.zip handler.py
   aws lambda create-function --function-name kinesis-consumer \
     --runtime python3.12 --handler handler.handler \
     --role "$ROLE_ARN" --zip-file fileb://function.zip --timeout 30
   aws lambda wait function-active-v2 --function-name kinesis-consumer

   aws lambda create-event-source-mapping \
     --function-name kinesis-consumer \
     --event-source-arn "$STREAM_ARN" \
     --starting-position LATEST \
     --batch-size 100 --maximum-batching-window-in-seconds 5
   ```

5. Đợi mapping `State=Enabled` (~1 phút) rồi `put-records` với partition key khác nhau để phân bổ nhiều shard.
   ```bash
   aws lambda list-event-source-mappings --function-name kinesis-consumer \
     --query 'EventSourceMappings[0].State'

   aws kinesis put-records --stream-name lab-stream \
     --cli-binary-format raw-in-base64-out \
     --records '[{"Data":"order-1","PartitionKey":"user-a"},
                 {"Data":"order-2","PartitionKey":"user-b"},
                 {"Data":"order-3","PartitionKey":"user-a"},
                 {"Data":"order-4","PartitionKey":"user-c"}]'
   ```

### ✅ Kiểm chứng
- Xem log thấy `Lambda` được invoke, mỗi invoke là 1 batch của **một shard** (record cùng partition key nằm cùng shard, giữ thứ tự).
  ```bash
  aws logs tail /aws/lambda/kinesis-consumer --since 5m --follow
  ```
- Vì dùng `LATEST`: record ghi **trước** khi mapping enabled sẽ KHÔNG được xử lý (đổi `TRIM_HORIZON` nếu muốn đọc từ đầu).

### 🧹 Dọn dẹp
```bash
UUID=$(aws lambda list-event-source-mappings --function-name kinesis-consumer \
  --query 'EventSourceMappings[0].UUID' --output text)
aws lambda delete-event-source-mapping --uuid "$UUID"
aws lambda delete-function --function-name kinesis-consumer
aws kinesis delete-stream --stream-name lab-stream --enforce-consumer-deletion
aws iam detach-role-policy --role-name lab5-lambda-kinesis-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaKinesisExecutionRole
aws iam delete-role --role-name lab5-lambda-kinesis-role
rm -f handler.py function.zip trust-lambda.json
```

### 🧠 Ý nghĩa với đề thi
- `Kinesis`→`Lambda` = **event source mapping (poll)**, batch **theo shard**, có thể **replay** (retention 24h–365 ngày) — khác hẳn `SQS`/`SNS`.
- `partition key` → chọn shard → giữ thứ tự trong shard; scale = tăng shard (1 MB/s hoặc 1000 rec/s ghi mỗi shard).
- `LATEST` vs `TRIM_HORIZON`: một bẫy hay hỏi khi "không thấy record nào được xử lý".

---

## Lab 5.5 — `Step Functions` state machine (`Choice` + `Retry` + `Catch`)
**🎯 Mục tiêu:** Dựng state machine `Standard` (ASL) điều phối **2** `Lambda`: `Choice` rẽ nhánh theo số tiền, nhánh charge có `Retry` + `Catch`; chạy execution và xem đồ thị.
**🧩 Luyện kỹ năng (liên quan đề):**
- ASL states: `Choice`, `Task`, `Retry` (backoff), `Catch`, `Fail`.
- Đưa retry/error-handling ra **workflow** thay vì nhồi vào code Lambda.
- IAM role cho `Step Functions` gọi `lambda:InvokeFunction`.

**⏱️ ~35 phút** · **Yêu cầu trước:** biết tạo `Lambda` + role (Lab 5.2).

### Các bước
1. Tạo role cơ bản + 2 function. `charge-card` sẽ ném lỗi khi input có `"fail": true` (để demo `Retry`/`Catch`).
   ```bash
   cat > trust-lambda.json <<'EOF'
   { "Version":"2012-10-17","Statement":[{"Effect":"Allow",
     "Principal":{"Service":"lambda.amazonaws.com"},"Action":"sts:AssumeRole"}] }
   EOF
   aws iam create-role --role-name lab5-sfn-lambda-role \
     --assume-role-policy-document file://trust-lambda.json
   aws iam attach-role-policy --role-name lab5-sfn-lambda-role \
     --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
   LAMBDA_ROLE="arn:aws:iam::${ACCOUNT_ID}:role/lab5-sfn-lambda-role"
   ```
   ```python
   # charge.py
   def handler(event, context):
       if event.get("fail"):
           raise Exception("payment gateway timeout")   # ép Retry/Catch
       return {"charged": True, "amount": event.get("amount")}
   ```
   ```python
   # review.py
   def handler(event, context):
       return {"review": "queued", "amount": event.get("amount")}
   ```
   ```bash
   zip charge.zip charge.py && zip review.zip review.py
   aws lambda create-function --function-name charge-card --runtime python3.12 \
     --handler charge.handler --role "$LAMBDA_ROLE" --zip-file fileb://charge.zip
   aws lambda create-function --function-name manual-review --runtime python3.12 \
     --handler review.handler --role "$LAMBDA_ROLE" --zip-file fileb://review.zip
   aws lambda wait function-active-v2 --function-name charge-card
   aws lambda wait function-active-v2 --function-name manual-review
   CHARGE_ARN=$(aws lambda get-function --function-name charge-card   --query Configuration.FunctionArn --output text)
   REVIEW_ARN=$(aws lambda get-function --function-name manual-review --query Configuration.FunctionArn --output text)
   ```

2. Tạo role cho `Step Functions` (được phép invoke 2 Lambda).
   ```bash
   cat > trust-sfn.json <<'EOF'
   { "Version":"2012-10-17","Statement":[{"Effect":"Allow",
     "Principal":{"Service":"states.amazonaws.com"},"Action":"sts:AssumeRole"}] }
   EOF
   aws iam create-role --role-name lab5-sfn-role \
     --assume-role-policy-document file://trust-sfn.json
   aws iam put-role-policy --role-name lab5-sfn-role --policy-name invoke-lambda \
     --policy-document "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Action\":\"lambda:InvokeFunction\",\"Resource\":[\"$CHARGE_ARN\",\"$REVIEW_ARN\"]}]}"
   SFN_ROLE="arn:aws:iam::${ACCOUNT_ID}:role/lab5-sfn-role"
   ```

3. Viết ASL (`Choice` → 2 nhánh `Task`; nhánh charge có `Retry` + `Catch`).
   ```json
   {
     "Comment": "Order flow: Choice + Retry + Catch",
     "StartAt": "CheckAmount",
     "States": {
       "CheckAmount": {
         "Type": "Choice",
         "Choices": [
           { "Variable": "$.amount", "NumericGreaterThan": 1000, "Next": "ManualReview" }
         ],
         "Default": "ChargeCard"
       },
       "ChargeCard": {
         "Type": "Task",
         "Resource": "CHARGE_ARN",
         "Retry": [
           { "ErrorEquals": ["States.TaskFailed"], "IntervalSeconds": 2, "MaxAttempts": 3, "BackoffRate": 2.0 }
         ],
         "Catch": [
           { "ErrorEquals": ["States.ALL"], "Next": "ChargeFailed" }
         ],
         "End": true
       },
       "ManualReview": {
         "Type": "Task",
         "Resource": "REVIEW_ARN",
         "End": true
       },
       "ChargeFailed": { "Type": "Fail", "Error": "ChargeError", "Cause": "Charge thất bại sau khi retry" }
     }
   }
   ```
   Thay ARN thật rồi tạo state machine `Standard`:
   ```bash
   # lưu JSON trên vào order-flow.asl.json, rồi:
   sed -e "s#CHARGE_ARN#$CHARGE_ARN#" -e "s#REVIEW_ARN#$REVIEW_ARN#" \
     order-flow.asl.json > order-flow.final.json
   SM_ARN=$(aws stepfunctions create-state-machine --name order-flow \
     --definition file://order-flow.final.json --role-arn "$SFN_ROLE" \
     --type STANDARD --query stateMachineArn --output text)
   ```

4. Chạy 3 execution để thấy đủ 3 đường đi.
   ```bash
   aws stepfunctions start-execution --state-machine-arn "$SM_ARN" --input '{"amount":500}'              # -> ChargeCard (thành công)
   aws stepfunctions start-execution --state-machine-arn "$SM_ARN" --input '{"amount":2000}'             # -> ManualReview
   aws stepfunctions start-execution --state-machine-arn "$SM_ARN" --input '{"amount":500,"fail":true}'  # -> Retry x3 -> Catch -> ChargeFailed
   ```

### ✅ Kiểm chứng
- Liệt kê + mô tả execution để xem trạng thái (`SUCCEEDED` / `FAILED`).
  ```bash
  aws stepfunctions list-executions --state-machine-arn "$SM_ARN" --max-results 5
  # lấy 1 arn rồi:
  aws stepfunctions describe-execution --execution-arn <EXECUTION_ARN>
  ```
- Mở **Step Functions console → Executions**: xem **đồ thị** — execution `fail:true` sẽ hiện 3 lần retry ở `ChargeCard` (backoff 2s→4s→8s) rồi nhảy sang `ChargeFailed`.

### 🧹 Dọn dẹp
```bash
aws stepfunctions delete-state-machine --state-machine-arn "$SM_ARN"
aws lambda delete-function --function-name charge-card
aws lambda delete-function --function-name manual-review
aws iam delete-role-policy --role-name lab5-sfn-role --policy-name invoke-lambda
aws iam delete-role --role-name lab5-sfn-role
aws iam detach-role-policy --role-name lab5-sfn-lambda-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
aws iam delete-role --role-name lab5-sfn-lambda-role
rm -f charge.py review.py charge.zip review.zip trust-lambda.json trust-sfn.json \
      order-flow.asl.json order-flow.final.json
```

### 🧠 Ý nghĩa với đề thi
- `Retry`/`Catch`/`Choice` xử lý lỗi & rẽ nhánh **trong workflow** → giữ code `Lambda` sạch (keyword đề: "orchestrate nhiều bước, retry, chờ").
- `Standard` = **exactly-once**, tới **1 năm**, tính theo **state transition**; `Express` = tới **5 phút**, high-volume (`Express` **Asynchronous** = **at-least-once**; `Express` **Synchronous** = **at-most-once**).
- `BackoffRate` × `IntervalSeconds` = độ trễ tăng dần giữa các lần retry.

---

## Lab 5.6 — Caching cho `Lambda`: `ElastiCache` lazy-loading (+ concept `RDS Proxy`)
**🎯 Mục tiêu:** Minh hoạ **lazy loading (cache-aside)** + **TTL** bằng client Redis; hiểu vì sao caching / connection pooling giảm tải DB khi `Lambda` scale.
**🧩 Luyện kỹ năng (liên quan đề):**
- Lazy loading vs write-through; vai trò TTL chống stale.
- `Redis` vs `Memcached`; khi nào dùng `RDS Proxy` (connection storm).

**⏱️ ~25 phút** · **Yêu cầu trước:** Python 3 + `pip install redis`.

> 💸 **LƯU Ý CHI PHÍ:** `ElastiCache` (kể cả Serverless) và `RDS`/`RDS Proxy` **KHÔNG** hoàn toàn Free Tier và nằm **trong VPC** (không nối trực tiếp từ laptop). Để học **pattern** miễn phí, dùng **Option A** (Redis local bằng Docker). Option B/C chỉ làm nếu bạn chấp nhận phát sinh phí và **xóa ngay** sau khi thử.

### Option A — Lazy loading demo (miễn phí, học pattern) ✅ khuyến nghị
1. Chạy Redis local.
   ```bash
   docker run -d --name lab-redis -p 6379:6379 redis:7
   pip install redis
   ```
2. Cache-aside + TTL bằng `redis` client.
   ```python
   # cache_aside.py
   import json, time, redis
   r = redis.Redis(host="localhost", port=6379, decode_responses=True)

   def query_db(product_id):
       time.sleep(0.5)                       # giả lập DB chậm
       return {"id": product_id, "name": f"Product {product_id}", "price": 100}

   def get_product(product_id, ttl=60):
       key = f"product:{product_id}"
       cached = r.get(key)
       if cached:                            # HIT
           print("CACHE HIT"); return json.loads(cached)
       print("CACHE MISS -> query DB")       # MISS -> lazy load
       data = query_db(product_id)
       r.set(key, json.dumps(data), ex=ttl)  # ghi cache kèm TTL (chống stale)
       return data

   if __name__ == "__main__":
       print(get_product("42"))   # MISS (chậm ~0.5s, ghi cache)
       print(get_product("42"))   # HIT  (nhanh, đọc cache)
   ```
   ```bash
   python3 cache_aside.py
   ```

### ✅ Kiểm chứng (Option A)
- Lần gọi 1 in `CACHE MISS -> query DB` (chậm ~0.5s); lần gọi 2 in `CACHE HIT` (tức thì). Sau khi key hết TTL → lại MISS. Đó là **lazy loading + TTL**.

### Option B — `ElastiCache Serverless` thật (tùy chọn, có phí)
```bash
# Tạo cache Serverless (Valkey). Xóa ngay sau khi thử!
aws elasticache create-serverless-cache \
  --serverless-cache-name lab-cache --engine valkey
# Endpoint chỉ truy cập ĐƯỢC từ EC2/Cloud9 CÙNG VPC (mở Security Group cổng 6379).
# Trỏ host=<endpoint> port=6379 trong cache_aside.py rồi chạy TỪ trong VPC.

# DỌN DẸP ngay:
aws elasticache delete-serverless-cache --serverless-cache-name lab-cache
```

### Option C — `RDS Proxy` (concept, dùng khi có sẵn RDS)
```bash
# CHỈ chạy nếu đã có RDS + secret + subnets. KHÔNG Free Tier.
aws rds create-db-proxy --db-proxy-name lab-proxy \
  --engine-family MYSQL \
  --auth '[{"AuthScheme":"SECRETS","SecretArn":"<SECRET_ARN>","IAMAuth":"DISABLED"}]' \
  --role-arn <PROXY_ROLE_ARN> \
  --vpc-subnet-ids <subnet-a> <subnet-b>
aws rds register-db-proxy-targets --db-proxy-name lab-proxy \
  --db-instance-identifiers <db-instance-id>
# Lambda kết nối tới ENDPOINT của proxy thay vì DB trực tiếp -> proxy pool/tái dùng connection.
aws rds delete-db-proxy --db-proxy-name lab-proxy   # DỌN DẸP
```

### 🧹 Dọn dẹp (Option A)
```bash
docker rm -f lab-redis
rm -f cache_aside.py
```

### 🧠 Ý nghĩa với đề thi
- **Lazy loading (cache-aside):** miss → query DB → ghi cache; chỉ cache dữ liệu thật sự dùng, nhưng lần miss đầu chậm & có thể stale → dùng **TTL**.
- **Write-through:** ghi DB thì ghi luôn cache → luôn mới, nhưng tốn bộ nhớ cho dữ liệu ít đọc.
- `Redis` (HA, persistence, cấu trúc dữ liệu, pub/sub) vs `Memcached` (đơn giản, đa luồng, scale ngang).
- **`RDS Proxy`**: keyword "`Lambda` scale → connection storm tới RDS" → **pool/tái dùng connection**, tăng độ bền khi failover (KHÔNG phải tăng size DB).

---

> ✅ Xong 6 lab? Đối chiếu lại [Lab checklist trong README](README.md#-lab-checklist) và làm tiếp [bộ câu hỏi luyện tập](questions.md) trước MINI-MOCK Domain 1.
