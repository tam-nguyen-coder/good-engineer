# 🏗️ Capstone Project — Tuần 10: **Serverless Notes/Media App** (ghép toàn bộ 4 domain)

> Đây **KHÔNG** phải các lab rời — mà là **1 dự án end-to-end** bạn tự tay build qua các PHẦN nối tiếp (Part 1 → 7). Mỗi Part chồng thêm 1 lớp lên hệ thống đã có, và ôn lại đúng những gì đã học ở các tuần trước.
> Chạy được trên tài khoản AWS thật (Free Tier). LUÔN giữ tài nguyên tới hết Part 6, rồi chạy **Part 7 — Dọn dẹp toàn bộ**.
> ⚙️ Yêu cầu chung: đã cấu hình `AWS CLI v2` (xem Lab 1.1 tuần 1) + IAM đủ quyền + (Part 6) đã cài `AWS SAM CLI`.
> Về [plan tuần](README.md) · [Câu hỏi luyện tập](questions.md) · [Kế hoạch tổng](../../DVA-C02-STUDY-PLAN.md)

---

## 🎯 Bạn sẽ build cái gì

Một app ghi chú + đính kèm media, **hoàn toàn serverless**:
- Người dùng đăng nhập (`Cognito`), gọi REST API (`API Gateway`) để **CRUD notes** (lưu `DynamoDB`).
- Muốn đính kèm ảnh/file → xin **presigned URL** rồi **upload thẳng lên `S3`**.
- `S3` báo có file mới → `Lambda` xử lý **bất đồng bộ**, ghi metadata vào `DynamoDB`, rồi **publish `SNS`** → fan-out sang `SQS` → **worker `Lambda`** xử lý tiếp.
- Toàn bộ được bảo mật (`Cognito` + `KMS` + `Secrets Manager`/`Parameter Store`), quan sát được (`X-Ray` + `CloudWatch`), và cuối cùng **đóng gói lại bằng `SAM`** (IaC) với **canary deploy**.

### 🗺️ Sơ đồ kiến trúc

```
                         (1) đăng nhập, lấy JWT
   ┌────────────┐  ───────────────────────────►  ┌──────────────────┐
   │  Client    │                                 │  Cognito         │
   │ (curl/web) │  ◄───────────────────────────   │  User Pool       │
   └─────┬──────┘        id/access token          └────────┬─────────┘
         │                                                  │ (authorizer)
         │ (2) REST call + Bearer token                     │
         ▼                                                  ▼
   ┌───────────────────────────┐   COGNITO_USER_POOLS   validate
   │  API Gateway (REST)        │◄───── authorizer ──────────┘
   │  /notes  /uploads          │
   └───────────┬───────────────┘
               │ AWS_PROXY (SYNC)
               ▼
   ┌───────────────────────────┐   read/write   ┌──────────────────┐
   │  notes-api  Lambda         │───────────────►│  DynamoDB        │
   │  CRUD notes + presigned URL│                │  NotesTable (KMS)│
   └───────────┬───────────────┘                └────────▲─────────┘
               │ (3) presigned PUT URL                    │ write metadata
               ▼                                          │
   ┌───────────────────────────┐  (4) s3:ObjectCreated    │
   │  S3  media bucket (KMS)    │──── (ASYNC push) ───►┌───┴──────────────┐
   └───────────────────────────┘                      │ media-processor  │
                                                       │ Lambda           │
                                          publish ─────┤ (metadata + SNS) │
                                                       └───┬──────────────┘
                                                           │ (5) SNS publish
                                                           ▼
                                                 ┌──────────────────┐
                                                 │  SNS topic       │──► email sub (fan-out)
                                                 │  (fan-out)       │
                                                 └────────┬─────────┘
                                                          │ subscribe (raw)
                                                          ▼
                                                 ┌──────────────────┐  event source
                                                 │  SQS queue       │─── mapping (POLL) ──►┌──────────────┐
                                                 │  (+ DLQ)         │                      │ worker Lambda│
                                                 └──────────────────┘                      └──────────────┘

   Xuyên suốt: Secrets Manager / Parameter Store (config)  ·  KMS (mã hoá at-rest)
               X-Ray (trace end-to-end + annotation)  ·  CloudWatch (alarm + metric)
               Part 6: đóng gói phần lõi (API+data+S3) bằng SAM template + canary DeploymentPreference
```

### 📌 Mỗi Part ôn lại tuần / domain nào

| Part | Ghép dịch vụ gì | Ôn lại tuần | Domain |
|---|---|---|---|
| **Part 1** ⭐ | `API Gateway (REST)` → `Lambda` → `DynamoDB` (CRUD) | Tuần 1–2 (`Lambda`), 3 (`DynamoDB`), 4 (`API Gateway`) | **1 – Development** |
| **Part 2** ⭐ | `S3` presigned URL + `S3 event` → `Lambda` (async) | Tuần 4 (`S3`), 2 (event sources) | **1 – Development** |
| **Part 3** ⭐ | `SNS` fan-out → `SQS` → worker `Lambda` (event source mapping) | Tuần 5 (Messaging) | **1 – Development** |
| **Part 4** ⭐ | `Cognito` authorizer + `Secrets Manager`/`SSM` + `KMS` | Tuần 6 (`Cognito`/`IAM`), 7 (`KMS`/`Secrets`) | **2 – Security** |
| **Part 5** ⭐ | `X-Ray` tracing + annotation + `CloudWatch` alarm/metric | Tuần 9 (`CloudWatch`/`X-Ray`) | **4 – Troubleshooting & Optimization** |
| **Part 6** ⭐ | Đóng gói phần lõi (API+data+S3) bằng `SAM` + canary `DeploymentPreference` | Tuần 8 (CI/CD, `CloudFormation`/`SAM`) | **3 – Deployment** |
| **Part 7** | Dọn dẹp toàn bộ (`sam delete` + xoá tài nguyên tạo tay) | — | — |

> 🧠 **Bản đồ tích hợp `Lambda`** (BẮT BUỘC nhớ — capstone này minh hoạ đủ 4 kiểu):
> - `API Gateway` → `Lambda`: **synchronous** (proxy `AWS_PROXY`) — Part 1.
> - `S3` → `Lambda`: **async push** qua bucket notification — Part 2.
> - `SNS` → `Lambda`/subscriber: **async push** — Part 3.
> - `SQS` → `Lambda`: **event source mapping** (Lambda **POLL**) — Part 3.

---

## 🔧 Chuẩn bị chung (làm 1 lần, dùng cho mọi Part)

```bash
# 1) Đặt region (đổi theo bạn — ví dụ ap-southeast-1 hoặc us-east-1)
export AWS_REGION=ap-southeast-1
export AWS_DEFAULT_REGION=$AWS_REGION

# 2) Account ID để dựng ARN
export ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# 3) Tên tài nguyên dùng chung (bucket phải là DUY NHẤT toàn cầu → thêm account id)
export APP=notesapp
export TABLE_NAME=NotesTable
export MEDIA_BUCKET=${APP}-media-${ACCOUNT_ID}
echo "Account: $ACCOUNT_ID · Region: $AWS_REGION · Bucket: $MEDIA_BUCKET"

# 4) Thư mục làm việc
mkdir -p ~/capstone && cd ~/capstone
```

> 💡 Part 1–5 build **bằng tay** (CLI/SDK) để bạn thấy rõ từng mảnh ghép và cách nối chúng. Part 6 gói lại bằng `SAM` — cách "thật" trong công việc.

---

## Part 1 — Data + API: `API Gateway` → `Lambda` → `DynamoDB` ⭐
**🎯 Mục tiêu:** Có một REST API `/notes` để **tạo / liệt kê / xoá** note; `Lambda` là backend (proxy), `DynamoDB` là kho lưu.
**🧩 Luyện kỹ năng (liên quan đề):**
- `API Gateway` → `Lambda` là **synchronous**, integration `AWS_PROXY`, cần `lambda add-permission` principal `apigateway.amazonaws.com`.
- Cấu trúc event proxy (`httpMethod`, `body`, `queryStringParameters`) và response bắt buộc `{statusCode, headers, body}`.
- Table `DynamoDB` composite key (`PK`=userId, `SK`=noteId), `PAY_PER_REQUEST` (on-demand).

**⏱️ ~40 phút** · **Yêu cầu trước:** Chuẩn bị chung.

### Các bước
1. Tạo bảng `DynamoDB` (composite key, on-demand).
   ```bash
   aws dynamodb create-table --table-name "$TABLE_NAME" \
     --attribute-definitions AttributeName=userId,AttributeType=S AttributeName=noteId,AttributeType=S \
     --key-schema AttributeName=userId,KeyType=HASH AttributeName=noteId,KeyType=RANGE \
     --billing-mode PAY_PER_REQUEST
   aws dynamodb wait table-exists --table-name "$TABLE_NAME"
   ```

2. Tạo execution role cho `notes-api` (logs + đọc/ghi bảng + tạo presigned URL cho `S3` ở Part 2).
   ```bash
   cat > trust-lambda.json <<'EOF'
   { "Version":"2012-10-17","Statement":[{"Effect":"Allow",
     "Principal":{"Service":"lambda.amazonaws.com"},"Action":"sts:AssumeRole"}] }
   EOF
   aws iam create-role --role-name ${APP}-api-role \
     --assume-role-policy-document file://trust-lambda.json
   aws iam attach-role-policy --role-name ${APP}-api-role \
     --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
   aws iam put-role-policy --role-name ${APP}-api-role --policy-name app-access \
     --policy-document "{\"Version\":\"2012-10-17\",\"Statement\":[
       {\"Effect\":\"Allow\",\"Action\":[\"dynamodb:PutItem\",\"dynamodb:Query\",\"dynamodb:DeleteItem\",\"dynamodb:GetItem\"],\"Resource\":\"arn:aws:dynamodb:${AWS_REGION}:${ACCOUNT_ID}:table/${TABLE_NAME}\"},
       {\"Effect\":\"Allow\",\"Action\":[\"s3:PutObject\"],\"Resource\":\"arn:aws:s3:::${MEDIA_BUCKET}/*\"}
     ]}"
   export API_ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/${APP}-api-role"
   sleep 10   # chờ IAM propagate
   ```

3. Viết handler `notes-api` (proxy). Đã chừa sẵn route `/uploads` cho Part 2.
   ```python
   # api.py
   import json, os, time, uuid, boto3
   from boto3.dynamodb.conditions import Key

   ddb   = boto3.resource("dynamodb")
   table = ddb.Table(os.environ["TABLE_NAME"])
   s3    = boto3.client("s3")
   BUCKET = os.environ.get("MEDIA_BUCKET")

   def _resp(code, body):
       return {"statusCode": code,
               "headers": {"Content-Type": "application/json"},
               "body": json.dumps(body, default=str)}

   def handler(event, context):
       method = event["httpMethod"]
       path   = event.get("resource") or event.get("path") or ""
       # Part 4 sẽ thay bằng Cognito sub; tạm hard-code để test Part 1
       user = "demo-user"

       # --- Part 2: xin presigned URL để upload media ---
       if "uploads" in path and method == "POST":
           b = json.loads(event.get("body") or "{}")
           key = f"{user}/{uuid.uuid4()}-{b.get('filename','file.bin')}"
           url = s3.generate_presigned_url(
               "put_object", Params={"Bucket": BUCKET, "Key": key}, ExpiresIn=300)
           return _resp(200, {"uploadUrl": url, "key": key})

       # --- Part 1: CRUD notes ---
       if method == "POST":
           b = json.loads(event.get("body") or "{}")
           item = {"userId": user, "noteId": str(uuid.uuid4()),
                   "title": b.get("title",""), "body": b.get("body",""),
                   "createdAt": int(time.time())}
           table.put_item(Item=item)
           return _resp(201, item)
       if method == "GET":
           r = table.query(KeyConditionExpression=Key("userId").eq(user))
           return _resp(200, r["Items"])
       if method == "DELETE":
           nid = (event.get("queryStringParameters") or {}).get("noteId")
           table.delete_item(Key={"userId": user, "noteId": nid})
           return _resp(200, {"deleted": nid})
       return _resp(405, {"error": "method not allowed"})
   ```

4. Đóng gói + tạo function (truyền env `TABLE_NAME`, `MEDIA_BUCKET`).
   ```bash
   zip api.zip api.py
   aws lambda create-function --function-name ${APP}-api \
     --runtime python3.12 --handler api.handler --role "$API_ROLE_ARN" \
     --zip-file fileb://api.zip --timeout 15 \
     --environment "Variables={TABLE_NAME=$TABLE_NAME,MEDIA_BUCKET=$MEDIA_BUCKET}"
   aws lambda wait function-active-v2 --function-name ${APP}-api
   export API_FN_ARN=$(aws lambda get-function --function-name ${APP}-api \
     --query Configuration.FunctionArn --output text)
   ```

5. Tạo REST API + resource `/notes` + method `ANY` proxy → `Lambda`.
   ```bash
   export API_ID=$(aws apigateway create-rest-api --name ${APP}-api \
     --query id --output text)
   export ROOT_ID=$(aws apigateway get-resources --rest-api-id "$API_ID" \
     --query "items[?path=='/'].id" --output text)

   export NOTES_ID=$(aws apigateway create-resource --rest-api-id "$API_ID" \
     --parent-id "$ROOT_ID" --path-part notes --query id --output text)

   # method ANY (không auth ở Part 1 — Part 4 sẽ thêm Cognito authorizer)
   aws apigateway put-method --rest-api-id "$API_ID" --resource-id "$NOTES_ID" \
     --http-method ANY --authorization-type NONE

   # AWS_PROXY: bắt buộc POST tới lambda:path/.../invocations
   aws apigateway put-integration --rest-api-id "$API_ID" --resource-id "$NOTES_ID" \
     --http-method ANY --type AWS_PROXY --integration-http-method POST \
     --uri arn:aws:apigateway:${AWS_REGION}:lambda:path/2015-03-31/functions/${API_FN_ARN}/invocations

   # --- resource /uploads (Part 2 sẽ gọi POST /uploads để xin presigned URL) ---
   # Tạo NGAY từ Part 1 để tránh 403 "Missing Authentication Token" khi Part 2 curl vào route chưa tồn tại.
   export UPLOADS_ID=$(aws apigateway create-resource --rest-api-id "$API_ID" \
     --parent-id "$ROOT_ID" --path-part uploads --query id --output text)
   aws apigateway put-method --rest-api-id "$API_ID" --resource-id "$UPLOADS_ID" \
     --http-method POST --authorization-type NONE
   aws apigateway put-integration --rest-api-id "$API_ID" --resource-id "$UPLOADS_ID" \
     --http-method POST --type AWS_PROXY --integration-http-method POST \
     --uri arn:aws:apigateway:${AWS_REGION}:lambda:path/2015-03-31/functions/${API_FN_ARN}/invocations
   ```

6. **Cấp quyền cho `API Gateway`** gọi `Lambda` (resource-based policy) + deploy stage `prod`.
   ```bash
   # source-arn dùng /*/*/* để bao MỌI route (cả /notes lẫn /uploads) — nếu chỉ scope
   # .../*/*/notes thì POST /uploads (Part 2) sẽ bị 403 vì Lambda từ chối API Gateway gọi.
   aws lambda add-permission --function-name ${APP}-api \
     --statement-id apigw-invoke --action lambda:InvokeFunction \
     --principal apigateway.amazonaws.com \
     --source-arn "arn:aws:execute-api:${AWS_REGION}:${ACCOUNT_ID}:${API_ID}/*/*/*"

   aws apigateway create-deployment --rest-api-id "$API_ID" --stage-name prod
   export API_URL="https://${API_ID}.execute-api.${AWS_REGION}.amazonaws.com/prod"
   echo "API_URL=$API_URL"
   ```

### ✅ Kiểm chứng
```bash
# Tạo note
curl -s -X POST "$API_URL/notes" -d '{"title":"first","body":"hello capstone"}'
# Liệt kê
curl -s "$API_URL/notes"
```
- POST trả về `201` kèm `noteId`; GET trả về mảng note vừa tạo. Nếu `502`/`Internal server error` → xem log:
  ```bash
  aws logs tail /aws/lambda/${APP}-api --since 5m
  ```
- Lỗi hay gặp: quên `add-permission` (API trả `500` "not authorized to perform: lambda:InvokeFunction").

### 🧠 Ý nghĩa với đề thi
- Proxy integration `AWS_PROXY` = `API Gateway` gửi **nguyên event** vào `Lambda`, và `Lambda` phải trả **đúng shape** `{statusCode, headers, body}` — sai shape → `502`.
- `API Gateway` → `Lambda` là **sync**; luôn cần **resource-based policy** cho principal `apigateway.amazonaws.com`.
- `DynamoDB` on-demand (`PAY_PER_REQUEST`) hợp workload không đoán trước; composite key (HASH+RANGE) cho phép `Query` theo 1 user.

---

## Part 2 — Upload media: presigned URL + `S3 event` → `Lambda` (async) ⭐
**🎯 Mục tiêu:** Client xin **presigned PUT URL** rồi upload thẳng lên `S3` (không đi qua `Lambda`); khi file vào bucket, `S3` **async** kích hoạt `media-processor` ghi metadata vào `DynamoDB`.
**🧩 Luyện kỹ năng (liên quan đề):**
- **Presigned URL**: offload upload khỏi backend, không lộ credential; hết hạn theo `ExpiresIn`.
- `S3` → `Lambda` là **asynchronous** qua **bucket notification** — KHÔNG phải event source mapping; cần `add-permission` principal `s3.amazonaws.com`.
- Cấu trúc event `Records[].s3.object.key` (nhớ `urllib.parse.unquote_plus`).

**⏱️ ~35 phút** · **Yêu cầu trước:** xong Part 1.

### Các bước
1. Tạo bucket media (chặn public, bật versioning nhẹ tuỳ ý).
   ```bash
   if [ "$AWS_REGION" = "us-east-1" ]; then
     aws s3api create-bucket --bucket "$MEDIA_BUCKET"
   else
     aws s3api create-bucket --bucket "$MEDIA_BUCKET" \
       --create-bucket-configuration LocationConstraint="$AWS_REGION"
   fi
   aws s3api put-public-access-block --bucket "$MEDIA_BUCKET" \
     --public-access-block-configuration BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true
   ```

2. Role + handler cho `media-processor` (ghi bảng; Part 3 sẽ thêm `sns:Publish`).
   ```bash
   aws iam create-role --role-name ${APP}-proc-role \
     --assume-role-policy-document file://trust-lambda.json
   aws iam attach-role-policy --role-name ${APP}-proc-role \
     --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
   aws iam put-role-policy --role-name ${APP}-proc-role --policy-name proc-access \
     --policy-document "{\"Version\":\"2012-10-17\",\"Statement\":[
       {\"Effect\":\"Allow\",\"Action\":[\"dynamodb:PutItem\"],\"Resource\":\"arn:aws:dynamodb:${AWS_REGION}:${ACCOUNT_ID}:table/${TABLE_NAME}\"}
     ]}"
   export PROC_ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/${APP}-proc-role"
   sleep 10
   ```
   ```python
   # processor.py
   import os, json, urllib.parse, boto3

   ddb   = boto3.resource("dynamodb")
   table = ddb.Table(os.environ["TABLE_NAME"])
   sns   = boto3.client("sns")
   TOPIC = os.environ.get("TOPIC_ARN")   # rỗng ở Part 2, có ở Part 3

   def handler(event, context):
       for rec in event["Records"]:
           key  = urllib.parse.unquote_plus(rec["s3"]["object"]["key"])
           size = rec["s3"]["object"]["size"]
           user = key.split("/")[0]
           table.put_item(Item={"userId": user, "noteId": f"media#{key}",
                                 "type": "media", "s3key": key, "size": size})
           print(f"[proc] wrote metadata for {key} ({size} bytes)")
           if TOPIC:
               sns.publish(TopicArn=TOPIC, Subject="New media uploaded",
                           Message=json.dumps({"user": user, "key": key, "size": size}))
       return {"processed": len(event["Records"])}
   ```
   ```bash
   zip processor.zip processor.py
   aws lambda create-function --function-name ${APP}-processor \
     --runtime python3.12 --handler processor.handler --role "$PROC_ROLE_ARN" \
     --zip-file fileb://processor.zip --timeout 30 \
     --environment "Variables={TABLE_NAME=$TABLE_NAME}"
   aws lambda wait function-active-v2 --function-name ${APP}-processor
   ```

3. **Cấp quyền cho `S3`** gọi function + cấu hình **bucket notification** (async trigger).
   ```bash
   aws lambda add-permission --function-name ${APP}-processor \
     --statement-id s3-invoke --action lambda:InvokeFunction \
     --principal s3.amazonaws.com \
     --source-arn "arn:aws:s3:::${MEDIA_BUCKET}"

   PROC_ARN=$(aws lambda get-function --function-name ${APP}-processor \
     --query Configuration.FunctionArn --output text)
   cat > notif.json <<EOF
   { "LambdaFunctionConfigurations": [
       { "LambdaFunctionArn": "$PROC_ARN", "Events": ["s3:ObjectCreated:*"] } ] }
   EOF
   aws s3api put-bucket-notification-configuration \
     --bucket "$MEDIA_BUCKET" --notification-configuration file://notif.json
   ```

### ✅ Kiểm chứng
```bash
# 1) Xin presigned URL qua API
UP=$(curl -s -X POST "$API_URL/uploads" -d '{"filename":"cat.png"}')
echo "$UP"
URL=$(echo "$UP" | python3 -c 'import sys,json;print(json.load(sys.stdin)["uploadUrl"])')

# 2) Upload 1 file bất kỳ bằng chính presigned URL (PUT) — không cần credential
echo "hello media" > cat.png
curl -s -X PUT --upload-file cat.png "$URL" -o /dev/null -w "%{http_code}\n"   # 200
```
- Xem log thấy `[proc] wrote metadata ...`:
  ```bash
  aws logs tail /aws/lambda/${APP}-processor --since 5m
  ```
- `GET /notes` giờ có thêm item `noteId=media#...` (metadata do processor ghi).

### 🧠 Ý nghĩa với đề thi
- Presigned URL = **client upload trực tiếp `S3`**, giảm tải/không lộ key; quyền của URL = quyền của **role tạo ra nó** (`s3:PutObject`).
- `S3` → `Lambda` **async**: `S3` không chờ kết quả; function lỗi → `Lambda` **retry 2 lần** → nên gắn **DLQ/destinations**.
- Bẫy troubleshooting: upload xong mà function không chạy → thường thiếu `add-permission` `s3.amazonaws.com` hoặc chưa `put-bucket-notification-configuration`.

---

## Part 3 — Async & notify: `SNS` fan-out → `SQS` → worker `Lambda` ⭐
**🎯 Mục tiêu:** Khi có media mới, `media-processor` **publish `SNS`**; topic **fan-out** sang (a) email và (b) một `SQS` queue; queue được **worker `Lambda`** tiêu thụ qua **event source mapping (poll)**.
**🧩 Luyện kỹ năng (liên quan đề):**
- **Fan-out** `SNS` → nhiều subscriber (email + `SQS`); phân biệt với 1 `SQS` (mỗi message chỉ 1 consumer).
- `SNS` → subscriber là **push**; `SQS` → `Lambda` là **event source mapping (poll)**.
- Queue cần **resource policy** cho `SNS`; worker cần DLQ + `RawMessageDelivery`.

**⏱️ ~40 phút** · **Yêu cầu trước:** xong Part 2.

### Các bước
1. Tạo topic + (tuỳ chọn) subscribe email để thấy fan-out ra người thật.
   ```bash
   export TOPIC_ARN=$(aws sns create-topic --name ${APP}-media-events --query TopicArn --output text)
   # tuỳ chọn: nhận email (phải bấm confirm trong hộp thư)
   aws sns subscribe --topic-arn "$TOPIC_ARN" --protocol email \
     --notification-endpoint you@example.com
   ```

2. Cho `media-processor` quyền `sns:Publish` + truyền `TOPIC_ARN` vào env (kích hoạt nhánh publish đã viết ở Part 2).
   ```bash
   aws iam put-role-policy --role-name ${APP}-proc-role --policy-name proc-sns \
     --policy-document "{\"Version\":\"2012-10-17\",\"Statement\":[
       {\"Effect\":\"Allow\",\"Action\":\"sns:Publish\",\"Resource\":\"$TOPIC_ARN\"}]}"
   aws lambda update-function-configuration --function-name ${APP}-processor \
     --environment "Variables={TABLE_NAME=$TABLE_NAME,TOPIC_ARN=$TOPIC_ARN}"
   aws lambda wait function-updated-v2 --function-name ${APP}-processor
   ```

3. Tạo `SQS` queue + DLQ; cấp **queue policy** cho `SNS`; subscribe queue vào topic (raw delivery).
   ```bash
   DLQ_URL=$(aws sqs create-queue --queue-name ${APP}-media-dlq --query QueueUrl --output text)
   DLQ_ARN=$(aws sqs get-queue-attributes --queue-url "$DLQ_URL" \
     --attribute-names QueueArn --query Attributes.QueueArn --output text)

   cat > qattr.json <<EOF
   { "RedrivePolicy": "{\"deadLetterTargetArn\":\"$DLQ_ARN\",\"maxReceiveCount\":\"3\"}",
     "VisibilityTimeout": "180" }
   EOF
   QUEUE_URL=$(aws sqs create-queue --queue-name ${APP}-media-queue \
     --attributes file://qattr.json --query QueueUrl --output text)
   QUEUE_ARN=$(aws sqs get-queue-attributes --queue-url "$QUEUE_URL" \
     --attribute-names QueueArn --query Attributes.QueueArn --output text)

   # queue policy: cho phép SNS gửi vào (điều kiện SourceArn = topic)
   cat > qpolicy.json <<EOF
   { "Policy": "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":{\"Service\":\"sns.amazonaws.com\"},\"Action\":\"sqs:SendMessage\",\"Resource\":\"$QUEUE_ARN\",\"Condition\":{\"ArnEquals\":{\"aws:SourceArn\":\"$TOPIC_ARN\"}}}]}" }
   EOF
   aws sqs set-queue-attributes --queue-url "$QUEUE_URL" --attributes file://qpolicy.json

   aws sns subscribe --topic-arn "$TOPIC_ARN" --protocol sqs \
     --notification-endpoint "$QUEUE_ARN" --attributes RawMessageDelivery=true
   ```

4. Worker `Lambda` + role (đọc `SQS`) + **event source mapping**.
   ```bash
   aws iam create-role --role-name ${APP}-worker-role \
     --assume-role-policy-document file://trust-lambda.json
   aws iam attach-role-policy --role-name ${APP}-worker-role \
     --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaSQSQueueExecutionRole
   WORKER_ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/${APP}-worker-role"
   sleep 10
   ```
   ```python
   # worker.py
   import json
   def handler(event, context):
       for rec in event["Records"]:
           body = json.loads(rec["body"])          # raw delivery -> body = message gốc
           print(f"[worker] xử lý media {body['key']} của {body['user']} ({body['size']} bytes)")
           # ... ở đây có thể tạo thumbnail, transcode, quét virus ...
       return {"handled": len(event["Records"])}
   ```
   ```bash
   zip worker.zip worker.py
   aws lambda create-function --function-name ${APP}-worker \
     --runtime python3.12 --handler worker.handler --role "$WORKER_ROLE_ARN" \
     --zip-file fileb://worker.zip --timeout 30
   aws lambda wait function-active-v2 --function-name ${APP}-worker

   aws lambda create-event-source-mapping --function-name ${APP}-worker \
     --event-source-arn "$QUEUE_ARN" --batch-size 5
   ```

### ✅ Kiểm chứng
```bash
# Upload 1 file mới (lặp lại bước Part 2) rồi xem chuỗi lan truyền:
aws logs tail /aws/lambda/${APP}-processor --since 5m   # thấy publish SNS
aws logs tail /aws/lambda/${APP}-worker --since 5m       # thấy [worker] xử lý media ...
```
- Nếu đã confirm email → nhận được 1 mail thông báo (đó là nhánh fan-out thứ 2).
- Không thấy worker chạy? Kiểm tra `State=Enabled` của mapping + queue policy cho `SNS`:
  ```bash
  aws lambda list-event-source-mappings --function-name ${APP}-worker \
    --query 'EventSourceMappings[0].State'
  ```

### 🧠 Ý nghĩa với đề thi
- "Một event → **nhiều** hệ thống độc lập cùng nhận" → **fan-out `SNS` → nhiều `SQS`/subscriber**, KHÔNG phải 1 `SQS`.
- `SQS` → `Lambda` = **event source mapping (poll)**; `VisibilityTimeout` queue nên **≥ 6× function timeout**; DLQ đặt trên **queue**.
- Chèn `SQS` giữa `SNS` và worker = **buffer** chống spike + **retry/độ bền** (redrive từ DLQ sau khi vá lỗi).

---

## Part 4 — Security: `Cognito` authorizer + `Secrets Manager`/`SSM` + `KMS` ⭐
**🎯 Mục tiêu:** Chỉ user đã đăng nhập (`Cognito`) mới gọi được `/notes`; lấy `userId` **thật** từ token; đưa config/secret ra `Parameter Store`/`Secrets Manager`; mã hoá dữ liệu bằng `KMS`.
**🧩 Luyện kỹ năng (liên quan đề):**
- `API Gateway` **`COGNITO_USER_POOLS` authorizer**: validate JWT trước khi tới `Lambda`; đọc claim `sub`/`email` từ `requestContext.authorizer.claims`.
- `Secrets Manager` (secret có rotation/versioning) vs `Parameter Store` (config, `SecureString` free tier).
- `KMS`: CMK mã hoá at-rest cho `DynamoDB`/`S3`; phân biệt AWS-owned vs customer-managed key.

**⏱️ ~45 phút** · **Yêu cầu trước:** xong Part 1.

### Các bước
1. Tạo `Cognito` User Pool + app client (không secret, cho luồng `USER_PASSWORD_AUTH`) + 1 user test.
   ```bash
   export POOL_ID=$(aws cognito-idp create-user-pool --pool-name ${APP}-pool \
     --query UserPool.Id --output text)
   export CLIENT_ID=$(aws cognito-idp create-user-pool-client --user-pool-id "$POOL_ID" \
     --client-name ${APP}-client --no-generate-secret \
     --explicit-auth-flows ALLOW_USER_PASSWORD_AUTH ALLOW_REFRESH_TOKEN_AUTH \
     --query UserPoolClient.ClientId --output text)

   aws cognito-idp admin-create-user --user-pool-id "$POOL_ID" \
     --username alice --message-action SUPPRESS
   aws cognito-idp admin-set-user-password --user-pool-id "$POOL_ID" \
     --username alice --password 'Passw0rd!23' --permanent
   ```

2. Đọc `sub` từ token trong handler — sửa dòng `user = "demo-user"` trong `api.py`.
   ```python
   # THAY: user = "demo-user"
   # BẰNG: lấy identity thật từ authorizer (fallback demo-user khi test cục bộ)
   claims = (event.get("requestContext", {}).get("authorizer", {}) or {}).get("claims", {})
   user = claims.get("sub", "demo-user")
   ```
   ```bash
   zip api.zip api.py
   aws lambda update-function-code --function-name ${APP}-api --zip-file fileb://api.zip
   aws lambda wait function-updated-v2 --function-name ${APP}-api
   ```

3. Gắn **Cognito authorizer** vào API + đổi method `/notes` sang `COGNITO_USER_POOLS` + redeploy.
   ```bash
   export AUTHZ_ID=$(aws apigateway create-authorizer --rest-api-id "$API_ID" \
     --name ${APP}-cognito --type COGNITO_USER_POOLS --identity-source 'method.request.header.Authorization' \
     --provider-arns "arn:aws:cognito-idp:${AWS_REGION}:${ACCOUNT_ID}:userpool/${POOL_ID}" \
     --query id --output text)

   aws apigateway update-method --rest-api-id "$API_ID" --resource-id "$NOTES_ID" \
     --http-method ANY \
     --patch-operations op=replace,path=/authorizationType,value=COGNITO_USER_POOLS \
                        op=replace,path=/authorizerId,value=$AUTHZ_ID
   aws apigateway create-deployment --rest-api-id "$API_ID" --stage-name prod
   ```
   > 📝 Ở đây chỉ gắn authorizer cho `/notes`; route `POST /uploads` vẫn để `NONE` (handler tự đọc `sub` từ claims, rỗng thì fallback `demo-user`). Muốn siết chặt hơn thì `update-method` cho `$UPLOADS_ID` sang `COGNITO_USER_POOLS` y hệt rồi redeploy.

4. Config qua `Parameter Store` + secret qua `Secrets Manager` + tạo `KMS` CMK.
   ```bash
   # Config không nhạy cảm
   aws ssm put-parameter --name /${APP}/max-note-size --type String --value "10240"
   # Secret nhạy cảm (vd API key bên thứ 3)
   aws secretsmanager create-secret --name ${APP}/thirdparty-key \
     --secret-string '{"apiKey":"demo-1234"}'
   # Customer-managed key để mã hoá at-rest
   export KMS_ARN=$(aws kms create-key --description "${APP} CMK" \
     --query KeyMetadata.Arn --output text)
   aws kms create-alias --alias-name alias/${APP} --target-key-id "$KMS_ARN"
   ```
   > 🔒 Mã hoá at-rest bằng CMK: `S3` đặt default encryption `SSE-KMS`; `DynamoDB` bảng mới có thể `--sse-specification Enabled=true,SSEType=KMS,KMSMasterKeyId=$KMS_ARN`. (Bảng đã tạo ở Part 1 dùng AWS-owned key; trong Part 6 khai báo CMK ngay từ template.)
   ```bash
   aws s3api put-bucket-encryption --bucket "$MEDIA_BUCKET" \
     --server-side-encryption-configuration "{\"Rules\":[{\"ApplyServerSideEncryptionByDefault\":{\"SSEAlgorithm\":\"aws:kms\",\"KMSMasterKeyID\":\"$KMS_ARN\"}}]}"
   ```

5. **Cấp quyền `KMS` cho role tạo presigned URL** — bắt buộc khi bucket bật `SSE-KMS` (CMK).
   ```bash
   # api-role đã KÝ presigned URL nên khi client PUT, S3 dùng chính api-role để mã hoá object
   # -> role phải có kms:GenerateDataKey trên CMK, nếu không PUT sẽ AccessDenied.
   aws iam put-role-policy --role-name ${APP}-api-role --policy-name api-kms \
     --policy-document "{\"Version\":\"2012-10-17\",\"Statement\":[
       {\"Effect\":\"Allow\",\"Action\":[\"kms:GenerateDataKey\",\"kms:Decrypt\"],\"Resource\":\"$KMS_ARN\"}]}"
   # (Nếu về sau media-processor phải ĐỌC object đã mã hoá -> thêm y hệt statement này cho proc-role.)
   ```
   > 🧠 **Bẫy hay gặp:** client PUT qua presigned URL được đánh giá bằng quyền của **identity ĐÃ KÝ URL** (ở đây là `api-role`), KHÔNG phải quyền của client. Bucket dùng `SSE-KMS` thì role đó **bắt buộc** có `kms:GenerateDataKey` — thiếu là `AccessDenied` dù `s3:PutObject` đã đủ.

### ✅ Kiểm chứng
```bash
# 1) Gọi KHÔNG token -> 401 Unauthorized
curl -s -o /dev/null -w "%{http_code}\n" "$API_URL/notes"          # 401

# 2) Lấy token rồi gọi CÓ token -> 200
TOKEN=$(aws cognito-idp initiate-auth --client-id "$CLIENT_ID" \
  --auth-flow USER_PASSWORD_AUTH \
  --auth-parameters USERNAME=alice,PASSWORD='Passw0rd!23' \
  --query 'AuthenticationResult.IdToken' --output text)

curl -s -X POST "$API_URL/notes" -H "Authorization: $TOKEN" \
  -d '{"title":"secure","body":"chỉ alice thấy"}'
curl -s "$API_URL/notes" -H "Authorization: $TOKEN"   # note gắn với sub của alice
```
- Đọc lại config/secret:
  ```bash
  aws ssm get-parameter --name /${APP}/max-note-size --query Parameter.Value --output text
  aws secretsmanager get-secret-value --secret-id ${APP}/thirdparty-key --query SecretString --output text
  ```

### 🧠 Ý nghĩa với đề thi
- `COGNITO_USER_POOLS` authorizer = xác thực **trước** khi request tới `Lambda`; `Lambda` đọc identity từ `requestContext.authorizer.claims` (đừng tin `body`).
- `Secrets Manager` (rotation tự động, versioning) cho **credential**; `Parameter Store` (`SecureString`, rẻ/free) cho **config** — chọn theo có cần rotation không.
- `KMS`: hiểu **envelope encryption** + phân biệt AWS-owned / AWS-managed / **customer-managed (CMK)** key; CMK cho phép tự đặt key policy + audit `CloudTrail`.

---

## Part 5 — Observability: `X-Ray` tracing + annotation + `CloudWatch` alarm/metric ⭐
**🎯 Mục tiêu:** Trace **xuyên suốt** một request (API → `Lambda` → `DynamoDB`/`S3`), thêm **annotation** để lọc trace, và dựng **alarm** + **custom metric** trên `CloudWatch`.
**🧩 Luyện kỹ năng (liên quan đề):**
- Bật **active tracing** trên `Lambda` + `API Gateway`; `X-Ray` **service map** để tìm bottleneck.
- `annotation` (index, filter được) vs `metadata` (không index) trong `X-Ray`.
- `CloudWatch` alarm trên metric có sẵn (`Errors`) + **custom metric** (EMF / `put-metric-data`).

**⏱️ ~35 phút** · **Yêu cầu trước:** xong Part 1 (và Part 4 để có luồng đầy đủ).

### Các bước
1. Thêm quyền `X-Ray` + bật **active tracing** cho function chính và stage API.
   ```bash
   aws iam attach-role-policy --role-name ${APP}-api-role \
     --policy-arn arn:aws:iam::aws:policy/AWSXRayDaemonWriteAccess
   aws lambda update-function-configuration --function-name ${APP}-api \
     --tracing-config Mode=Active
   aws lambda wait function-updated-v2 --function-name ${APP}-api

   # Bật tracing cho stage prod của API Gateway
   aws apigateway update-stage --rest-api-id "$API_ID" --stage-name prod \
     --patch-operations op=replace,path=/tracingEnabled,value=true
   ```

2. (Tuỳ chọn) Instrument code + thêm **annotation** (patch mọi boto3 call; đánh dấu subsegment).
   > ⚠️ **Đọc kỹ trước khi làm:** `aws_xray_sdk` KHÔNG có sẵn trong runtime `Lambda`. Nếu bạn thêm `import aws_xray_sdk` vào `api.py` rồi `update-function-code` mà **chưa bundle** thư viện, function sẽ `ImportError` ngay khi khởi động → API trả `502`. Chọn 1 trong 2:
   > - **Cách A — muốn xem annotation ngay ở Part 5:** thêm đoạn dưới vào `api.py`, RỒI bundle kèm dependency và deploy (bắt buộc cả 3 lệnh):
   >   ```bash
   >   mkdir -p ~/capstone/build && cp ~/capstone/api.py ~/capstone/build/ && cd ~/capstone/build
   >   pip install aws-xray-sdk -t .            # cài lib + deps (wrapt, jsonpickle...) vào cùng thư mục
   >   zip -r ../api.zip .                      # đóng gói code KÈM toàn bộ dependency
   >   aws lambda update-function-code --function-name ${APP}-api --zip-file fileb://../api.zip
   >   aws lambda wait function-updated-v2 --function-name ${APP}-api
   >   ```
   > - **Cách B — không muốn cài lib:** **BỎ QUA** việc thêm `import`/annotation ở bước này. `patch_all()` cùng dependency sẽ do **Part 6/`SAM`** tự đóng gói (`requirements.txt`); active tracing ở bước 1 vẫn cho bạn service map cơ bản.

   Đoạn instrument (chỉ dùng ở **Cách A**):
   ```python
   # thêm ĐẦU api.py
   from aws_xray_sdk.core import xray_recorder, patch_all
   patch_all()   # tự trace boto3 (DynamoDB/S3) thành subsegment

   # trong handler, sau khi tính được user & method:
   xray_recorder.put_annotation("userId", user)      # INDEX -> filter được trên console
   xray_recorder.put_annotation("httpMethod", method)
   xray_recorder.put_metadata("event_path", path)    # metadata: xem chi tiết, KHÔNG filter
   ```

3. Custom metric bằng **EMF** (Embedded Metric Format) — chỉ cần `print` JSON đúng schema, `CloudWatch` tự bóc thành metric (không tốn API call).
   ```python
   # ví dụ log EMF khi tạo note (đặt trong nhánh POST của api.py)
   print(json.dumps({
     "_aws": {"Timestamp": int(time.time()*1000),
              "CloudWatchMetrics": [{"Namespace": "NotesApp",
                 "Dimensions": [["Service"]],
                 "Metrics": [{"Name": "NotesCreated", "Unit": "Count"}]}]},
     "Service": "notes-api", "NotesCreated": 1}))
   ```

4. Tạo **alarm** trên số lỗi của function `notes-api`.
   ```bash
   aws cloudwatch put-metric-alarm --alarm-name ${APP}-api-errors \
     --namespace AWS/Lambda --metric-name Errors \
     --dimensions Name=FunctionName,Value=${APP}-api \
     --statistic Sum --period 60 --evaluation-periods 1 \
     --threshold 1 --comparison-operator GreaterThanOrEqualToThreshold \
     --treat-missing-data notBreaching
   ```

### ✅ Kiểm chứng
```bash
# Sinh vài request để có trace + metric
for i in 1 2 3; do curl -s -X POST "$API_URL/notes" -H "Authorization: $TOKEN" -d '{"title":"t'$i'"}' >/dev/null; done
```
- **X-Ray console → Service map**: thấy chuỗi `API Gateway → notes-api → DynamoDB`; mở 1 trace → filter theo annotation `userId`.
- **CloudWatch → Metrics → NotesApp/NotesCreated**: thấy đường metric tăng (từ EMF).
- Xem trạng thái alarm:
  ```bash
  aws cloudwatch describe-alarms --alarm-names ${APP}-api-errors \
    --query 'MetricAlarms[0].StateValue'
  ```

### 🧠 Ý nghĩa với đề thi
- `X-Ray` cần **active tracing** trên mọi mắt xích + IAM `xray:PutTraceSegments`; **service map** = công cụ số 1 tìm nút chậm/lỗi trong hệ phân tán.
- **annotation** (indexed, filter được) vs **metadata** (chi tiết, không filter) — câu hỏi hay đánh vào chỗ này.
- **EMF** = cách rẻ nhất tạo custom metric từ log (không gọi `PutMetricData` liên tục); alarm nên `treat-missing-data` hợp lý để tránh báo giả.

---

## Part 6 — Deploy: đóng gói phần lõi bằng `SAM` (+ canary) ⭐
**🎯 Mục tiêu:** Đóng gói **phần lõi** (API + data + S3) bằng `AWS SAM` làm **ví dụ IaC** — một `template.yaml` khai báo table, API (+Cognito auth), các function và event `S3`, rồi `sam build` / `sam deploy`. Các thành phần Part 3 (`SNS`/`SQS`/worker) và Part 4 (`Secrets`/`KMS`) **có thể mở rộng thêm** vào template sau. (Tuỳ chọn) bật **canary** cho function chính.
**🧩 Luyện kỹ năng (liên quan đề):**
- `SAM` = superset của `CloudFormation` cho serverless: `AWS::Serverless::Function/Api/SimpleTable`, `Events`, `Policies`.
- `sam build` (đóng gói dependency) → `sam deploy` (đẩy artifact lên `S3` + tạo/cập nhật stack).
- **`AutoPublishAlias` + `DeploymentPreference`** = **canary/linear** shift traffic sang version mới, gắn alarm để **tự rollback**.

**⏱️ ~50 phút** · **Yêu cầu trước:** đã cài `sam` (`sam --version`). Nên làm ở **thư mục/stack MỚI** để không đụng tài nguyên tạo tay (Part 7 dọn cả hai).

### Các bước
1. Bố trí project `SAM`.
   ```bash
   mkdir -p ~/capstone-sam/src && cd ~/capstone-sam
   cp ~/capstone/api.py src/          # tái dùng handler (giữ dòng đọc claims Cognito)
   cp ~/capstone/processor.py src/
   printf "aws-xray-sdk\n" > src/requirements.txt
   ```

2. Viết `template.yaml` (bản **rút gọn tiêu biểu** — đủ để deploy chạy được; **không** gồm `SNS`/`SQS`/worker của Part 3 hay `Secrets`/`KMS` của Part 4 — coi như bài tập mở rộng).
   ```yaml
   AWSTemplateFormatVersion: '2010-09-09'
   Transform: AWS::Serverless-2016-10-31
   Description: Capstone - Serverless Notes/Media App

   Globals:
     Function:
       Runtime: python3.12
       Timeout: 15
       Tracing: Active            # X-Ray cho mọi function
       Environment:
         Variables:
           TABLE_NAME: !Ref NotesTable
           MEDIA_BUCKET: !Ref MediaBucket

   Resources:
     NotesTable:
       # KHÔNG dùng AWS::Serverless::SimpleTable: nó chỉ có 1 khoá chính (HASH),
       # trong khi app dùng composite key (userId HASH + noteId RANGE). Nếu chỉ 1 khoá:
       # put_item cùng userId sẽ ĐÈ note cũ, và delete_item với {userId,noteId} -> ValidationException (DELETE 500).
       Type: AWS::DynamoDB::Table
       Properties:
         BillingMode: PAY_PER_REQUEST
         SSESpecification: { SSEEnabled: true }   # mã hoá at-rest
         AttributeDefinitions:
           - { AttributeName: userId, AttributeType: S }
           - { AttributeName: noteId, AttributeType: S }
         KeySchema:
           - { AttributeName: userId, KeyType: HASH }
           - { AttributeName: noteId, KeyType: RANGE }

     MediaBucket:
       Type: AWS::S3::Bucket
       Properties:
         PublicAccessBlockConfiguration:
           { BlockPublicAcls: true, BlockPublicPolicy: true,
             IgnorePublicAcls: true, RestrictPublicBuckets: true }

     UserPool:
       Type: AWS::Cognito::UserPool
       Properties: { UserPoolName: !Sub '${AWS::StackName}-pool' }
     UserPoolClient:
       Type: AWS::Cognito::UserPoolClient
       Properties:
         UserPoolId: !Ref UserPool
         ExplicitAuthFlows: [ ALLOW_USER_PASSWORD_AUTH, ALLOW_REFRESH_TOKEN_AUTH ]

     Api:
       Type: AWS::Serverless::Api
       Properties:
         StageName: prod
         TracingEnabled: true
         Auth:
           DefaultAuthorizer: CognitoAuth
           Authorizers:
             CognitoAuth:
               UserPoolArn: !GetAtt UserPool.Arn

     NotesApiFunction:
       Type: AWS::Serverless::Function
       Properties:
         CodeUri: src/
         Handler: api.handler
         AutoPublishAlias: live               # tạo alias 'live' -> bật canary
         DeploymentPreference:
           Type: Canary10Percent5Minutes      # 10% traffic 5', rồi 100%
           Alarms: [ !Ref ApiErrorsAlarm ]    # lỗi -> tự rollback
         Policies:
           - DynamoDBCrudPolicy: { TableName: !Ref NotesTable }
           - S3WritePolicy:      { BucketName: !Ref MediaBucket }
         Events:
           Notes:
             Type: Api
             Properties: { RestApiId: !Ref Api, Path: /notes, Method: ANY }
           Uploads:
             Type: Api
             Properties: { RestApiId: !Ref Api, Path: /uploads, Method: POST }

     ProcessorFunction:
       Type: AWS::Serverless::Function
       Properties:
         CodeUri: src/
         Handler: processor.handler
         Policies:
           - DynamoDBWritePolicy: { TableName: !Ref NotesTable }
         Events:
           MediaUploaded:                       # S3 -> Lambda (async) do SAM tự cấu hình
             Type: S3
             Properties: { Bucket: !Ref MediaBucket, Events: s3:ObjectCreated:* }

     ApiErrorsAlarm:
       Type: AWS::CloudWatch::Alarm
       Properties:
         Namespace: AWS/Lambda
         MetricName: Errors
         Dimensions:
           - { Name: FunctionName, Value: !Ref NotesApiFunction }
         Statistic: Sum
         Period: 60
         EvaluationPeriods: 1
         Threshold: 1
         ComparisonOperator: GreaterThanOrEqualToThreshold
         TreatMissingData: notBreaching

   Outputs:
     ApiUrl:
       Value: !Sub 'https://${Api}.execute-api.${AWS::Region}.amazonaws.com/prod'
   ```

3. Build + deploy (guided lần đầu, lưu cấu hình vào `samconfig.toml`).
   ```bash
   sam build
   sam deploy --guided \
     --stack-name ${APP}-stack \
     --capabilities CAPABILITY_IAM
   # trả lời: region, "Allow SAM ... IAM roles" = Y, save config = Y
   ```

### ✅ Kiểm chứng
```bash
# Lấy URL API từ output stack rồi test như Part 1 (dùng token Cognito của pool MỚI)
aws cloudformation describe-stacks --stack-name ${APP}-stack \
  --query "Stacks[0].Outputs[?OutputKey=='ApiUrl'].OutputValue" --output text
```
> ⚠️ `UserPool` trong `SAM` là **pool HOÀN TOÀN MỚI** (khác pool tạo tay ở Part 4) → **chưa có user nào**. Muốn lấy token để test phải tạo user trong pool này trước:
> ```bash
> SAM_POOL=$(aws cloudformation describe-stack-resources --stack-name ${APP}-stack \
>   --query "StackResources[?ResourceType=='AWS::Cognito::UserPool'].PhysicalResourceId" --output text)
> SAM_CLIENT=$(aws cloudformation describe-stack-resources --stack-name ${APP}-stack \
>   --query "StackResources[?ResourceType=='AWS::Cognito::UserPoolClient'].PhysicalResourceId" --output text)
> aws cognito-idp admin-create-user --user-pool-id "$SAM_POOL" --username alice --message-action SUPPRESS
> aws cognito-idp admin-set-user-password --user-pool-id "$SAM_POOL" \
>   --username alice --password 'Passw0rd!23' --permanent
> # rồi initiate-auth với $SAM_CLIENT như Part 4 để lấy IdToken
> ```
- `sam deploy` in ra changeset + tạo stack; `CloudFormation` console thấy đủ resource (table, bucket, 2 function, API, pool, alarm).
- Với canary: sau khi deploy 1 **thay đổi code**, xem alias `live` của `NotesApiFunction` dịch dần 10% → 100% (CodeDeploy). Có lỗi trong cửa sổ canary → **tự rollback** về version cũ.

### 🧠 Ý nghĩa với đề thi
- `SAM` policy templates (`DynamoDBCrudPolicy`, `S3WritePolicy`…) = least-privilege nhanh gọn thay vì tự viết IAM JSON.
- Event `Type: S3`/`Api`/`SQS` trong `SAM` **tự** dựng permission + notification/mapping tương ứng — đúng các mô hình push/poll đã học.
- `Canary10Percent5Minutes`/`Linear...` + alarm = **traffic shifting** an toàn, **auto-rollback** — keyword đề Domain 3 ("giảm rủi ro deploy", "gradual rollout").

---

## Part 7 — Dọn dẹp TOÀN BỘ (tránh tính phí) 🧹
> Xoá theo **thứ tự phụ thuộc ngược**. Gồm 2 nhóm: (A) tài nguyên **tạo tay** Part 1–5, (B) **stack `SAM`** Part 6.

> ⚠️ **Nếu bạn mở terminal MỚI** để dọn dẹp, mọi biến `$API_ID`, `$TOPIC_ARN`, `$QUEUE_URL`, `$DLQ_URL`, `$POOL_ID`, `$KMS_ARN`… đã **RỖNG** (chỉ tồn tại trong shell cũ). Lệnh xoá với biến rỗng sẽ **âm thầm bỏ sót** tài nguyên đang tính phí. Trước khi chạy, hãy **set lại biến chung** (`AWS_REGION`, `ACCOUNT_ID`, `APP`, `TABLE_NAME`, `MEDIA_BUCKET` ở mục Chuẩn bị chung) rồi **re-derive** phần còn lại theo tên `notesapp-*`, ví dụ:
> ```bash
> export API_ID=$(aws apigateway get-rest-apis --query "items[?name=='${APP}-api'].id" --output text)
> export TOPIC_ARN=$(aws sns list-topics --query "Topics[?ends_with(TopicArn,':${APP}-media-events')].TopicArn" --output text)
> export QUEUE_URL=$(aws sqs get-queue-url --queue-name ${APP}-media-queue --query QueueUrl --output text 2>/dev/null)
> export DLQ_URL=$(aws sqs get-queue-url --queue-name ${APP}-media-dlq --query QueueUrl --output text 2>/dev/null)
> export POOL_ID=$(aws cognito-idp list-user-pools --max-results 60 --query "UserPools[?Name=='${APP}-pool'].Id" --output text)
> export KMS_ARN=$(aws kms describe-key --key-id alias/${APP} --query KeyMetadata.Arn --output text 2>/dev/null)
> ```

### A) Tài nguyên tạo tay (Part 1–5)
```bash
cd ~/capstone
# --- API Gateway ---
aws apigateway delete-rest-api --rest-api-id "$API_ID"

# --- Event source mapping + Lambdas ---
UUID=$(aws lambda list-event-source-mappings --function-name ${APP}-worker \
  --query 'EventSourceMappings[0].UUID' --output text 2>/dev/null)
[ "$UUID" != "None" ] && [ -n "$UUID" ] && aws lambda delete-event-source-mapping --uuid "$UUID"
for FN in ${APP}-api ${APP}-processor ${APP}-worker; do
  aws lambda delete-function --function-name "$FN" 2>/dev/null
done

# --- SNS + SQS ---
aws sns delete-topic --topic-arn "$TOPIC_ARN" 2>/dev/null
aws sqs delete-queue --queue-url "$QUEUE_URL" 2>/dev/null
aws sqs delete-queue --queue-url "$DLQ_URL" 2>/dev/null

# --- S3 (xoá object trước rồi xoá bucket) ---
aws s3 rm "s3://$MEDIA_BUCKET" --recursive 2>/dev/null
aws s3api delete-bucket --bucket "$MEDIA_BUCKET" 2>/dev/null

# --- DynamoDB ---
aws dynamodb delete-table --table-name "$TABLE_NAME"

# --- Cognito ---
aws cognito-idp delete-user-pool --user-pool-id "$POOL_ID" 2>/dev/null

# --- Secrets / SSM / KMS ---
aws secretsmanager delete-secret --secret-id ${APP}/thirdparty-key --force-delete-without-recovery 2>/dev/null
aws ssm delete-parameter --name /${APP}/max-note-size 2>/dev/null
aws kms delete-alias --alias-name alias/${APP} 2>/dev/null
aws kms schedule-key-deletion --key-id "$KMS_ARN" --pending-window-in-days 7 2>/dev/null

# --- CloudWatch alarm + log groups ---
aws cloudwatch delete-alarms --alarm-names ${APP}-api-errors 2>/dev/null
# Log group của Lambda KHÔNG tự mất khi xoá function -> xoá tay kẻo còn tồn (lưu trữ tính phí):
for FN in api processor worker; do
  aws logs delete-log-group --log-group-name /aws/lambda/${APP}-$FN 2>/dev/null
done

# --- IAM roles (detach/delete inline + managed rồi xoá role) ---
for R in ${APP}-api-role ${APP}-proc-role ${APP}-worker-role; do
  for P in $(aws iam list-attached-role-policies --role-name "$R" \
      --query 'AttachedPolicies[].PolicyArn' --output text 2>/dev/null); do
    aws iam detach-role-policy --role-name "$R" --policy-arn "$P"
  done
  for P in $(aws iam list-role-policies --role-name "$R" \
      --query 'PolicyNames[]' --output text 2>/dev/null); do
    aws iam delete-role-policy --role-name "$R" --policy-name "$P"
  done
  aws iam delete-role --role-name "$R" 2>/dev/null
done

rm -f trust-lambda.json notif.json qattr.json qpolicy.json \
      api.zip processor.zip worker.zip api.py processor.py worker.py cat.png
```

### B) Stack `SAM` (Part 6)
```bash
cd ~/capstone-sam
sam delete --stack-name ${APP}-stack --no-prompts
# (nếu bucket media của stack còn object -> làm rỗng trước rồi chạy lại sam delete)
```

### ✅ Kiểm chứng đã sạch
```bash
aws dynamodb list-tables --query "TableNames" --output text
aws lambda list-functions --query "Functions[?starts_with(FunctionName,'${APP}')].FunctionName" --output text
aws cloudformation describe-stacks --stack-name ${APP}-stack 2>&1 | grep -q "does not exist" && echo "stack đã xoá"
```
> `KMS` key ở trạng thái **PendingDeletion 7 ngày** (không tính phí key nhàn rỗi) — có thể `cancel-key-deletion` nếu đổi ý.

---

## 🎓 Sau capstone
Hoàn thành cả 7 Part = bạn đã tự tay ghép **≥ 13 dịch vụ** và **cả 4 kiểu tích hợp `Lambda`** — đủ điều kiện "**hoàn thành toàn bộ hands-on nhóm Serverless & CI/CD**" (tiêu chí #4 để đăng ký thi). Quay lại [README tuần 10](README.md) đối chiếu **Checklist ngày thi** + **Cổng tự kiểm tra**, rồi vào [bộ câu hỏi mock cross-domain](questions.md).
