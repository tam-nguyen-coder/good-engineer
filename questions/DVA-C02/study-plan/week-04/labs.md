# 🧪 Hands-on Labs — Tuần 4: `API Gateway` + `S3` + `CloudFront` (góc Developer)

> Lab cầm tay chỉ việc, chạy được trên tài khoản AWS thật (Free Tier). LUÔN chạy phần Dọn dẹp cuối mỗi lab.
> ⚙️ Yêu cầu chung: đã cấu hình `AWS CLI v2` (xem Lab 1.1 tuần 1) + IAM đủ quyền cho dịch vụ trong lab.
> Về [plan tuần](README.md) · [Câu hỏi luyện tập](questions.md) · [Kế hoạch tổng](../../DVA-C02-STUDY-PLAN.md)

**6 lab trong tuần này** — ⭐ = lab **tích hợp giữa các dịch vụ** (ưu tiên luyện vì hay ra thi):

| Lab | Nội dung | ⭐ |
|-----|----------|----|
| 4.1 | `S3` → `Lambda` (event notification, **ASYNC**) | ⭐ |
| 4.2 | `REST API` → `Lambda` → `DynamoDB` (CRUD, proxy `AWS_PROXY`) | ⭐ |
| 4.3 | Proxy vs non-proxy integration + mapping `VTL` + lỗi 502 | |
| 4.4 | `S3` presigned URL (PUT/GET bằng `boto3`) | ⭐ |
| 4.5 | `CloudFront` + `S3` với `OAC` (bucket private) | ⭐ |
| 4.6 | `Lambda authorizer` / `Cognito` + bật **CORS** cho API ở Lab 4.2 | |

---

## 🧰 Chuẩn bị chung (chạy 1 lần)

```bash
# Đặt region của bạn (VD Singapore). CloudFront là global nên không cần region.
export AWS_REGION=ap-southeast-1
export ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "Account=$ACCOUNT_ID Region=$AWS_REGION"

# Trust policy dùng lại cho MỌI Lambda role trong tuần này
cat > trust-lambda.json <<'EOF'
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": { "Service": "lambda.amazonaws.com" },
    "Action": "sts:AssumeRole"
  }]
}
EOF
```

> 💡 Placeholder: `<YOUR_BUCKET>`, `<API_ID>`, `<DIST_ID>`... — thay bằng giá trị thật của bạn. Bucket name phải **globally unique**, nên bài dùng hậu tố ngẫu nhiên.

---

## Lab 4.1 — `S3` → `Lambda` (event notification, ASYNC) ⭐
**🎯 Mục tiêu:** Upload 1 object lên `S3` → tự động kích hoạt `Lambda` ghi log + tạo file metadata JSON. Hiểu đây là mô hình **asynchronous qua S3 event notification**, KHÔNG phải event source mapping.
**🧩 Luyện kỹ năng (liên quan đề):**
- Cấu hình `s3:ObjectCreated:*` bắn tới `Lambda` (`put-bucket-notification-configuration`).
- Cấp quyền cho S3 gọi Lambda: `lambda add-permission` principal **`s3.amazonaws.com`**.
- Phân biệt **async push** (S3/SNS/EventBridge) vs **event source mapping** (SQS/DynamoDB Streams/Kinesis).
**⏱️ ~30 phút** · **Yêu cầu trước:** đã chạy phần Chuẩn bị chung.

### Các bước
1. Tạo bucket + role cho Lambda (basic execution + quyền ghi metadata trở lại bucket).
   ```bash
   export B41=week4-s3lambda-$RANDOM-$ACCOUNT_ID
   aws s3api create-bucket --bucket $B41 --region $AWS_REGION \
     --create-bucket-configuration LocationConstraint=$AWS_REGION

   aws iam create-role --role-name week4-s3lambda-role \
     --assume-role-policy-document file://trust-lambda.json
   aws iam attach-role-policy --role-name week4-s3lambda-role \
     --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
   aws iam put-role-policy --role-name week4-s3lambda-role --policy-name s3-meta-write \
     --policy-document "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Action\":[\"s3:PutObject\"],\"Resource\":\"arn:aws:s3:::$B41/metadata/*\"}]}"
   ```
2. Viết handler xử lý event (ghi log + tạo `metadata/<file>.json`). Chú ý: notification chỉ lắng nghe prefix `uploads/`, còn metadata ghi vào prefix `metadata/` → **tránh vòng lặp vô hạn**.
   ```python
   # s3_handler.py
   import boto3, json, urllib.parse, datetime
   s3 = boto3.client('s3')

   def handler(event, context):
       for rec in event['Records']:
           bucket = rec['s3']['bucket']['name']
           key = urllib.parse.unquote_plus(rec['s3']['object']['key'])
           size = rec['s3']['object'].get('size')
           print(f"ASYNC event: new object s3://{bucket}/{key} size={size}")
           meta = {"sourceKey": key, "size": size,
                   "processedAt": datetime.datetime.utcnow().isoformat() + "Z"}
           meta_key = "metadata/" + key.split('/', 1)[-1] + ".json"
           s3.put_object(Bucket=bucket, Key=meta_key,
                         Body=json.dumps(meta).encode('utf-8'))
           print(f"Wrote metadata to s3://{bucket}/{meta_key}")
       return {"processed": len(event['Records'])}
   ```
3. Đóng gói + tạo function.
   ```bash
   zip s3_handler.zip s3_handler.py
   sleep 10   # chờ role propagate
   aws lambda create-function --function-name week4-s3-processor \
     --runtime python3.12 --handler s3_handler.handler \
     --role arn:aws:iam::$ACCOUNT_ID:role/week4-s3lambda-role \
     --zip-file fileb://s3_handler.zip --timeout 30 --region $AWS_REGION
   ```
4. **Cấp quyền cho S3 gọi Lambda** (principal `s3.amazonaws.com`) — phải làm TRƯỚC khi gắn notification, nếu không `put-bucket-notification` sẽ báo lỗi thiếu quyền.
   ```bash
   aws lambda add-permission --function-name week4-s3-processor \
     --statement-id s3invoke --action lambda:InvokeFunction \
     --principal s3.amazonaws.com \
     --source-arn arn:aws:s3:::$B41 --source-account $ACCOUNT_ID \
     --region $AWS_REGION
   ```
5. Gắn event notification `s3:ObjectCreated:*` (lọc prefix `uploads/`).
   ```bash
   LAMBDA_ARN=$(aws lambda get-function --function-name week4-s3-processor \
     --query 'Configuration.FunctionArn' --output text --region $AWS_REGION)

   cat > notif.json <<EOF
   {
     "LambdaFunctionConfigurations": [{
       "LambdaFunctionArn": "$LAMBDA_ARN",
       "Events": ["s3:ObjectCreated:*"],
       "Filter": {"Key": {"FilterRules": [{"Name": "prefix", "Value": "uploads/"}]}}
     }]
   }
   EOF
   aws s3api put-bucket-notification-configuration --bucket $B41 \
     --notification-configuration file://notif.json
   ```
6. Kích hoạt: upload 1 file vào prefix `uploads/`.
   ```bash
   echo "hello week4" > sample.txt
   aws s3 cp sample.txt s3://$B41/uploads/sample.txt
   ```

### ✅ Kiểm chứng
```bash
# 1) Log CloudWatch của Lambda (thấy dòng "ASYNC event...")
aws logs tail /aws/lambda/week4-s3-processor --since 5m --region $AWS_REGION

# 2) File metadata đã được tạo
aws s3 ls s3://$B41/metadata/
aws s3 cp s3://$B41/metadata/sample.txt.json - 2>/dev/null
```

### 🧹 Dọn dẹp (tránh tính phí)
```bash
aws s3 rm s3://$B41 --recursive
aws s3api delete-bucket --bucket $B41 --region $AWS_REGION
aws lambda delete-function --function-name week4-s3-processor --region $AWS_REGION
aws iam delete-role-policy --role-name week4-s3lambda-role --policy-name s3-meta-write
aws iam detach-role-policy --role-name week4-s3lambda-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
aws iam delete-role --role-name week4-s3lambda-role
```

### 🧠 Ý nghĩa với đề thi
- `S3` → `Lambda` là **asynchronous push** qua **S3 event notification** (hoặc EventBridge). Cấu hình = `put-bucket-notification-configuration` + `add-permission` principal `s3.amazonaws.com`. **KHÔNG** dùng `create-event-source-mapping` (mapping chỉ cho SQS/DynamoDB Streams/Kinesis — Lambda POLL).
- Async invoke retry **2 lần**, thất bại thì đẩy sang **DLQ / destinations**. Payload async tối đa **1 MB**.
- Đích của event notification có thể là `Lambda` / `SQS` / `SNS` / `EventBridge`.
- Bẫy thực tế: ghi ngược vào chính bucket đang lắng nghe → **vòng lặp vô hạn**; giải bằng prefix/suffix filter.

---

## Lab 4.2 — `REST API` → `Lambda` → `DynamoDB` (CRUD) ⭐
**🎯 Mục tiêu:** Dựng API CRUD đầy đủ (POST/GET/PUT/DELETE) bằng `REST API` với integration **`Lambda proxy (AWS_PROXY)`**, backend ghi/đọc `DynamoDB`, deploy stage `dev`, test bằng `curl`.
**🧩 Luyện kỹ năng (liên quan đề):**
- Integration `AWS_PROXY`: API Gateway truyền **nguyên** request, `Lambda` tự trả `{statusCode, headers, body}`.
- Cấp quyền cho API Gateway gọi Lambda: `add-permission` principal **`apigateway.amazonaws.com`**.
- `create-deployment` → stage có URL riêng; phân nhánh theo `event.httpMethod`.
**⏱️ ~50 phút** · **Yêu cầu trước:** đã chạy Chuẩn bị chung. (Các Lab 4.3 & 4.6 dùng lại API này.)

### Các bước
1. Tạo bảng `DynamoDB` `Items` (partition key `id` String, on-demand → Free Tier friendly).
   ```bash
   aws dynamodb create-table --table-name Items \
     --attribute-definitions AttributeName=id,AttributeType=S \
     --key-schema AttributeName=id,KeyType=HASH \
     --billing-mode PAY_PER_REQUEST --region $AWS_REGION
   aws dynamodb wait table-exists --table-name Items --region $AWS_REGION
   ```
2. Tạo role Lambda (basic execution + quyền CRUD trên bảng `Items`).
   ```bash
   aws iam create-role --role-name week4-crud-role \
     --assume-role-policy-document file://trust-lambda.json
   aws iam attach-role-policy --role-name week4-crud-role \
     --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
   aws iam put-role-policy --role-name week4-crud-role --policy-name ddb-crud \
     --policy-document "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Action\":[\"dynamodb:PutItem\",\"dynamodb:GetItem\",\"dynamodb:DeleteItem\",\"dynamodb:Scan\"],\"Resource\":\"arn:aws:dynamodb:$AWS_REGION:$ACCOUNT_ID:table/Items\"}]}"
   ```
3. Viết handler CRUD (đọc `event.httpMethod` để phân nhánh; trả đúng format proxy).
   ```python
   # crud.py
   import json, os, boto3
   table = boto3.resource('dynamodb').Table(os.environ.get('TABLE_NAME', 'Items'))

   def resp(code, body):
       return {
           "statusCode": code,
           "headers": {"Content-Type": "application/json",
                       "Access-Control-Allow-Origin": "*"},   # kèm sẵn cho Lab 4.6 (CORS)
           "body": json.dumps(body, default=str)
       }

   def handler(event, context):
       method = event['httpMethod']
       item_id = (event.get('pathParameters') or {}).get('id')
       try:
           if method == 'POST':
               data = json.loads(event.get('body') or '{}')
               table.put_item(Item=data)
               return resp(201, {"created": data})
           if method == 'GET' and item_id:
               item = table.get_item(Key={'id': item_id}).get('Item')
               return resp(200, item) if item else resp(404, {"error": "not found"})
           if method == 'GET':
               return resp(200, table.scan().get('Items', []))
           if method == 'PUT' and item_id:
               data = json.loads(event.get('body') or '{}'); data['id'] = item_id
               table.put_item(Item=data)
               return resp(200, {"updated": data})
           if method == 'DELETE' and item_id:
               table.delete_item(Key={'id': item_id})
               return resp(200, {"deleted": item_id})
           return resp(400, {"error": "unsupported method"})
       except Exception as e:
           return resp(500, {"error": str(e)})
   ```
   ```bash
   zip crud.zip crud.py
   sleep 10
   aws lambda create-function --function-name week4-crud \
     --runtime python3.12 --handler crud.handler \
     --role arn:aws:iam::$ACCOUNT_ID:role/week4-crud-role \
     --zip-file fileb://crud.zip --timeout 30 \
     --environment "Variables={TABLE_NAME=Items}" --region $AWS_REGION
   CRUD_ARN=$(aws lambda get-function --function-name week4-crud \
     --query 'Configuration.FunctionArn' --output text --region $AWS_REGION)
   ```
4. Tạo `REST API` + resource `/items` và `/items/{id}`.
   ```bash
   export API_ID=$(aws apigateway create-rest-api --name week4-crud-api \
     --region $AWS_REGION --query id --output text)
   ROOT_ID=$(aws apigateway get-resources --rest-api-id $API_ID \
     --query 'items[?path==`/`].id' --output text --region $AWS_REGION)
   ITEMS_ID=$(aws apigateway create-resource --rest-api-id $API_ID \
     --parent-id $ROOT_ID --path-part items --query id --output text --region $AWS_REGION)
   ITEM_ID=$(aws apigateway create-resource --rest-api-id $API_ID \
     --parent-id $ITEMS_ID --path-part '{id}' --query id --output text --region $AWS_REGION)
   echo "API_ID=$API_ID  ITEMS_ID=$ITEMS_ID  ITEM_ID=$ITEM_ID"
   ```
5. Tạo method + integration **`AWS_PROXY`** cho từng cặp (resource, method). Dùng vòng lặp cho gọn.
   ```bash
   URI=arn:aws:apigateway:$AWS_REGION:lambda:path/2015-03-31/functions/$CRUD_ARN/invocations

   # /items → POST, GET  |  /items/{id} → GET, PUT, DELETE
   for pair in "$ITEMS_ID POST" "$ITEMS_ID GET" "$ITEM_ID GET" "$ITEM_ID PUT" "$ITEM_ID DELETE"; do
     set -- $pair; RID=$1; M=$2
     aws apigateway put-method --rest-api-id $API_ID --resource-id $RID \
       --http-method $M --authorization-type NONE --region $AWS_REGION
     aws apigateway put-integration --rest-api-id $API_ID --resource-id $RID \
       --http-method $M --type AWS_PROXY --integration-http-method POST \
       --uri $URI --region $AWS_REGION
   done
   ```
6. **Cấp quyền cho API Gateway gọi Lambda** (principal `apigateway.amazonaws.com`; source-arn phủ mọi method/stage).
   ```bash
   aws lambda add-permission --function-name week4-crud \
     --statement-id apigw-invoke --action lambda:InvokeFunction \
     --principal apigateway.amazonaws.com \
     --source-arn "arn:aws:execute-api:$AWS_REGION:$ACCOUNT_ID:$API_ID/*/*/*" \
     --region $AWS_REGION
   ```
7. **Deploy** lên stage `dev` rồi test bằng `curl`.
   ```bash
   aws apigateway create-deployment --rest-api-id $API_ID \
     --stage-name dev --region $AWS_REGION
   export BASE=https://$API_ID.execute-api.$AWS_REGION.amazonaws.com/dev

   curl -s -X POST $BASE/items -H "Content-Type: application/json" \
     -d '{"id":"1","name":"demo","price":9}'      # → 201 created
   curl -s $BASE/items                             # → list (scan)
   curl -s $BASE/items/1                           # → 1 item
   curl -s -X PUT $BASE/items/1 -d '{"name":"demo2","price":12}'   # → updated
   curl -s -X DELETE $BASE/items/1                 # → deleted
   ```

### ✅ Kiểm chứng
- `POST` trả `201` và item xuất hiện khi `GET /items`; `GET /items/1` trả đúng item; `DELETE` xong `GET /items/1` trả `404`.
- Kiểm chéo dữ liệu thật trong bảng: `aws dynamodb scan --table-name Items --region $AWS_REGION`.

### 🧹 Dọn dẹp
> ⚠️ Nếu định làm tiếp **Lab 4.3 / 4.6**, GIỮ lại API + Lambda + bảng; dọn dẹp sau khi xong các lab đó.
```bash
aws apigateway delete-rest-api --rest-api-id $API_ID --region $AWS_REGION
aws lambda delete-function --function-name week4-crud --region $AWS_REGION
aws dynamodb delete-table --table-name Items --region $AWS_REGION
aws iam delete-role-policy --role-name week4-crud-role --policy-name ddb-crud
aws iam detach-role-policy --role-name week4-crud-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
aws iam delete-role --role-name week4-crud-role
```

### 🧠 Ý nghĩa với đề thi
- `API Gateway` → `Lambda` là **synchronous** (proxy `AWS_PROXY`); phải `add-permission` principal `apigateway.amazonaws.com`.
- Proxy đẩy trách nhiệm **format response** cho Lambda: sai `{statusCode, headers, body}` → **502** (xem Lab 4.3).
- Stage = một bản deploy có URL riêng; đổi backend theo môi trường bằng **stage variables → `Lambda alias`**.
- Sync payload tối đa **6 MB**; integration timeout mặc định **29s**.

---

## Lab 4.3 — Proxy vs non-proxy integration (`VTL`) + lỗi 502
**🎯 Mục tiêu:** Trên cùng 1 function, thấy rõ khác biệt giữa **non-proxy (`AWS` + mapping template `VTL`)** và **proxy (`AWS_PROXY`)**, và tái hiện lỗi **502** khi Lambda trả sai format ở proxy.
**🧩 Luyện kỹ năng (liên quan đề):**
- Mapping template `VTL` biến đổi request trước khi vào backend (chỉ có ở non-proxy).
- Proxy: Lambda **bắt buộc** trả `{statusCode, headers, body}`; thiếu → `502 Malformed Lambda proxy response`.
**⏱️ ~35 phút** · **Yêu cầu trước:** đã hoàn tất Lab 4.2 (dùng lại `$API_ID`, `$ROOT_ID`).

### Các bước
1. Tạo 1 function trả `{"result": n*n}`. Cùng function này xử lý được cả 2 kiểu integration (đọc `number` khi non-proxy, đọc `body.n` khi proxy).
   ```python
   # square.py
   import json
   def handler(event, context):
       if event.get('body'):                 # proxy: request nằm trong body (string)
           n = json.loads(event['body']).get('n', 0)
       else:                                  # non-proxy: đã được VTL map thành {"number": n}
           n = event.get('number', 0)
       return {"result": n * n}               # CHỦ Ý: chưa có statusCode/body
   ```
   ```bash
   zip square.zip square.py
   aws lambda create-function --function-name week4-square \
     --runtime python3.12 --handler square.handler \
     --role arn:aws:iam::$ACCOUNT_ID:role/week4-crud-role \
     --zip-file fileb://square.zip --timeout 15 --region $AWS_REGION
   SQ_ARN=$(aws lambda get-function --function-name week4-square \
     --query 'Configuration.FunctionArn' --output text --region $AWS_REGION)
   SQ_URI=arn:aws:apigateway:$AWS_REGION:lambda:path/2015-03-31/functions/$SQ_ARN/invocations
   aws lambda add-permission --function-name week4-square --statement-id apigw \
     --action lambda:InvokeFunction --principal apigateway.amazonaws.com \
     --source-arn "arn:aws:execute-api:$AWS_REGION:$ACCOUNT_ID:$API_ID/*/*/*" --region $AWS_REGION
   ```
2. **NON-PROXY** — resource `/square` với mapping template `VTL` (`{"n":5}` → `{"number":5}`).
   ```bash
   SQ_RID=$(aws apigateway create-resource --rest-api-id $API_ID --parent-id $ROOT_ID \
     --path-part square --query id --output text --region $AWS_REGION)
   aws apigateway put-method --rest-api-id $API_ID --resource-id $SQ_RID \
     --http-method POST --authorization-type NONE --region $AWS_REGION

   # VTL: lấy field n từ request, đổi tên thành number
   cat > req-template.json <<'EOF'
   {"application/json": "{ \"number\": $input.json('$.n') }"}
   EOF
   aws apigateway put-integration --rest-api-id $API_ID --resource-id $SQ_RID \
     --http-method POST --type AWS --integration-http-method POST --uri $SQ_URI \
     --request-templates file://req-template.json --region $AWS_REGION

   # Non-proxy PHẢI khai báo method response + integration response
   aws apigateway put-method-response --rest-api-id $API_ID --resource-id $SQ_RID \
     --http-method POST --status-code 200 \
     --response-models application/json=Empty --region $AWS_REGION
   aws apigateway put-integration-response --rest-api-id $API_ID --resource-id $SQ_RID \
     --http-method POST --status-code 200 --region $AWS_REGION
   ```
3. **PROXY (sinh 502)** — resource `/square-proxy` trỏ tới CÙNG function.
   ```bash
   SP_RID=$(aws apigateway create-resource --rest-api-id $API_ID --parent-id $ROOT_ID \
     --path-part square-proxy --query id --output text --region $AWS_REGION)
   aws apigateway put-method --rest-api-id $API_ID --resource-id $SP_RID \
     --http-method POST --authorization-type NONE --region $AWS_REGION
   aws apigateway put-integration --rest-api-id $API_ID --resource-id $SP_RID \
     --http-method POST --type AWS_PROXY --integration-http-method POST \
     --uri $SQ_URI --region $AWS_REGION
   ```
4. Deploy + test cả hai.
   ```bash
   aws apigateway create-deployment --rest-api-id $API_ID --stage-name dev --region $AWS_REGION
   BASE=https://$API_ID.execute-api.$AWS_REGION.amazonaws.com/dev

   curl -s -X POST $BASE/square       -d '{"n":5}'   # NON-PROXY → {"result":25}
   curl -s -X POST $BASE/square-proxy -d '{"n":5}'   # PROXY → 502 {"message":"Internal server error"}
   ```
5. **SỬA lỗi 502** — Lambda proxy phải trả đúng format. Cập nhật handler rồi deploy code.
   ```python
   # square.py (bản proxy đúng)
   import json
   def handler(event, context):
       n = json.loads(event.get('body') or '{}').get('n', 0)
       return {"statusCode": 200,
               "headers": {"Content-Type": "application/json"},
               "body": json.dumps({"result": n * n})}
   ```
   ```bash
   zip square.zip square.py
   aws lambda update-function-code --function-name week4-square \
     --zip-file fileb://square.zip --region $AWS_REGION
   curl -s -X POST $BASE/square-proxy -d '{"n":5}'   # bây giờ → 200 {"result":25}
   ```

### ✅ Kiểm chứng
- `/square` (non-proxy) trả `{"result":25}` — chứng tỏ VTL đã map `n`→`number` và Lambda nhận đúng `event["number"]`.
- `/square-proxy` ban đầu trả **502**; log Lambda có dòng `Execution failed ... Malformed Lambda proxy response`. Sau khi sửa format → **200**.
  ```bash
  aws logs tail /aws/lambda/week4-square --since 5m --region $AWS_REGION
  ```

### 🧹 Dọn dẹp
```bash
aws lambda delete-function --function-name week4-square --region $AWS_REGION
# 2 resource /square, /square-proxy sẽ bị xoá cùng khi xoá rest-api ở cuối Lab 4.2/4.6
```

### 🧠 Ý nghĩa với đề thi
- "Truyền nguyên request, Lambda tự format" → **`Lambda proxy (AWS_PROXY)`**; "biến đổi request/response bằng template" → **non-proxy + mapping `VTL`**.
- Thấy "`Lambda proxy` mà lỗi **502**" → gần như luôn do Lambda **không trả** `{statusCode, headers, body}`.
- Non-proxy cần khai báo **method response + integration response** (proxy thì không).

---

## Lab 4.4 — `S3` presigned URL (PUT/GET bằng `boto3`) ⭐
**🎯 Mục tiêu:** Sinh **presigned URL** để bên thứ ba upload (PUT) và download (GET) object **trực tiếp lên/từ `S3`** mà KHÔNG cần credential AWS và KHÔNG sửa bucket policy.
**🧩 Luyện kỹ năng (liên quan đề):**
- `generate_presigned_url('put_object'/'get_object', ...)` bằng `boto3`.
- URL **kế thừa quyền của identity đã tạo** ra nó; là **bearer token** — ai cầm cũng dùng được trong hạn.
- Số liệu hạn dùng: `SigV4` tối đa **7 ngày**; Console tối đa **12h**; temp credentials → hết hạn theo credential.
**⏱️ ~25 phút** · **Yêu cầu trước:** đã chạy Chuẩn bị chung.

### Các bước
1. Tạo bucket private (mặc định đã chặn public).
   ```bash
   export B44=week4-presign-$RANDOM-$ACCOUNT_ID
   aws s3api create-bucket --bucket $B44 --region $AWS_REGION \
     --create-bucket-configuration LocationConstraint=$AWS_REGION
   ```
2. Sinh presigned URL bằng `boto3` (PUT để upload, GET để download).
   ```python
   # presign.py
   import boto3, os
   bucket = os.environ['B44']
   key = 'shared/report.txt'
   # QUAN TRỌNG: ép SigV4 để hạn tối đa 7 ngày
   s3 = boto3.client('s3', config=boto3.session.Config(signature_version='s3v4'))

   put_url = s3.generate_presigned_url(
       'put_object', Params={'Bucket': bucket, 'Key': key}, ExpiresIn=300)
   get_url = s3.generate_presigned_url(
       'get_object', Params={'Bucket': bucket, 'Key': key}, ExpiresIn=300)
   print('PUT_URL=' + put_url)
   print('GET_URL=' + get_url)
   ```
   ```bash
   pip install boto3 -q 2>/dev/null
   B44=$B44 python3 presign.py
   ```
3. Dùng URL (bất kỳ máy nào có `curl`, không cần AWS credential).
   ```bash
   # Upload trực tiếp lên S3 bằng PUT URL (thay <PUT_URL> vừa in ra)
   echo "presigned upload demo" > report.txt
   curl -s -X PUT --upload-file report.txt "<PUT_URL>"

   # Download bằng GET URL
   curl -s "<GET_URL>"
   ```
   > Cách nhanh (dùng `aws s3 presign` cho GET, tương đương): `aws s3 presign s3://$B44/shared/report.txt --expires-in 300`.

### ✅ Kiểm chứng
```bash
# Object đã lên bucket dù client không có credential
aws s3 ls s3://$B44/shared/
# GET URL trả đúng nội dung "presigned upload demo"
```
Thử URL **sau khi hết hạn 300s** hoặc sửa 1 ký tự chữ ký → nhận **403 Forbidden** / `SignatureDoesNotMatch`.

### 🧹 Dọn dẹp
```bash
aws s3 rm s3://$B44 --recursive
aws s3api delete-bucket --bucket $B44 --region $AWS_REGION
```

### 🧠 Ý nghĩa với đề thi
- "Cho người ngoài upload/download tạm, KHÔNG lộ credential, KHÔNG sửa bucket policy" → **`S3` presigned URL** (PUT để upload).
- URL kế thừa quyền **identity tạo ra nó**; người tạo phải có `s3:PutObject`/`s3:GetObject` tương ứng, nếu không → **403**.
- Hạn: `SigV4` ≤ **7 ngày** (CLI/SDK), Console ≤ **12h**; ký bằng temp credentials (STS/role/EC2 profile) → hết hạn theo credential (thường 1–6h), dù đặt expiry dài hơn.
- Phân biệt với **`CloudFront` signed URL** (Lab 4.5): presigned = truy cập thẳng S3; signed URL = qua edge/CDN, ký bằng key group.

---

## Lab 4.5 — `CloudFront` + `S3` với `OAC` (bucket private) ⭐
**🎯 Mục tiêu:** Phân phối 1 bucket **private** qua `CloudFront`; khoá S3 để **CHỈ `CloudFront` đọc được** bằng **`OAC` (Origin Access Control)** — user không truy cập S3 trực tiếp được.
**🧩 Luyện kỹ năng (liên quan đề):**
- Tạo `OAC` (`SigV4`, thay cho `OAI` đời cũ) và gắn vào origin S3.
- Bucket policy chỉ allow service principal `cloudfront.amazonaws.com` với condition `AWS:SourceArn` = distribution ARN.
**⏱️ ~40 phút (chờ distribution deploy ~5–10 phút)** · **Yêu cầu trước:** đã chạy Chuẩn bị chung.

### Các bước
1. Tạo bucket private + upload 1 trang.
   ```bash
   export B45=week4-cf-oac-$RANDOM-$ACCOUNT_ID
   aws s3api create-bucket --bucket $B45 --region $AWS_REGION \
     --create-bucket-configuration LocationConstraint=$AWS_REGION
   echo '<h1>Private via CloudFront OAC</h1>' > index.html
   aws s3 cp index.html s3://$B45/index.html
   ```
2. Tạo **OAC**.
   ```bash
   OAC_ID=$(aws cloudfront create-origin-access-control --origin-access-control-config \
     Name=week4-oac-$RANDOM,SigningProtocol=sigv4,SigningBehavior=always,OriginAccessControlOriginType=s3 \
     --query 'OriginAccessControl.Id' --output text)
   echo "OAC_ID=$OAC_ID"
   ```
3. Tạo distribution trỏ tới bucket (dùng managed cache policy `CachingOptimized`).
   ```bash
   cat > dist-config.json <<EOF
   {
     "CallerReference": "week4-oac-$(date +%s)",
     "Comment": "Week4 OAC lab",
     "Enabled": true,
     "DefaultRootObject": "index.html",
     "Origins": {
       "Quantity": 1,
       "Items": [{
         "Id": "s3-origin",
         "DomainName": "$B45.s3.$AWS_REGION.amazonaws.com",
         "OriginAccessControlId": "$OAC_ID",
         "S3OriginConfig": {"OriginAccessIdentity": ""}
       }]
     },
     "DefaultCacheBehavior": {
       "TargetOriginId": "s3-origin",
       "ViewerProtocolPolicy": "redirect-to-https",
       "CachePolicyId": "658327ea-f89d-4fab-a63d-7e88639e58f6"
     }
   }
   EOF
   read DIST_ID DIST_DOMAIN < <(aws cloudfront create-distribution \
     --distribution-config file://dist-config.json \
     --query 'Distribution.[Id,DomainName]' --output text)
   echo "DIST_ID=$DIST_ID  DIST_DOMAIN=$DIST_DOMAIN"
   ```
   > 💡 Nếu CLI báo thiếu field, bổ sung theo thông báo — hoặc dùng Console (*Create distribution → Origin: chọn bucket → Origin access: Origin access control settings → Create OAC*, Console tự sinh bucket policy để copy).
4. Gắn bucket policy: **chỉ `CloudFront` (đúng distribution này) được `s3:GetObject`**.
   ```bash
   cat > bucket-policy.json <<EOF
   {
     "Version": "2012-10-17",
     "Statement": [{
       "Sid": "AllowCloudFrontOAC",
       "Effect": "Allow",
       "Principal": {"Service": "cloudfront.amazonaws.com"},
       "Action": "s3:GetObject",
       "Resource": "arn:aws:s3:::$B45/*",
       "Condition": {"StringEquals": {
         "AWS:SourceArn": "arn:aws:cloudfront::$ACCOUNT_ID:distribution/$DIST_ID"}}
     }]
   }
   EOF
   aws s3api put-bucket-policy --bucket $B45 --policy file://bucket-policy.json
   ```
5. Chờ distribution deploy xong (Status = `Deployed`).
   ```bash
   aws cloudfront wait distribution-deployed --id $DIST_ID
   ```

### ✅ Kiểm chứng
```bash
# Qua CloudFront → 200 + nội dung trang
curl -s https://$DIST_DOMAIN/index.html

# Truy cập THẲNG S3 → 403 (bucket private, chỉ CloudFront đọc được)
curl -s -o /dev/null -w "%{http_code}\n" https://$B45.s3.$AWS_REGION.amazonaws.com/index.html
```

> 🔒 **(Tuỳ chọn) Signed URL / Signed cookies:** với nội dung private có phí, tạo **trusted key group** (upload public key), gắn vào cache behavior, rồi ký URL bằng private key (`CloudFrontSigner` trong `boto3`). `Signed URL` = 1 file; `Signed cookies` = nhiều file cùng lúc, giữ nguyên URL.

### 🧹 Dọn dẹp (CloudFront phải disable trước khi xoá)
```bash
# 1) Lấy config hiện tại + ETag, tắt Enabled=false, update
aws cloudfront get-distribution-config --id $DIST_ID > cur.json
ETAG=$(python3 -c "import json;print(json.load(open('cur.json'))['ETag'])")
python3 -c "import json;d=json.load(open('cur.json'))['DistributionConfig'];d['Enabled']=False;json.dump(d,open('disabled.json','w'))"
aws cloudfront update-distribution --id $DIST_ID \
  --distribution-config file://disabled.json --if-match $ETAG
# 2) Chờ deploy xong rồi xoá (lấy ETag mới)
aws cloudfront wait distribution-deployed --id $DIST_ID
NEW_ETAG=$(aws cloudfront get-distribution-config --id $DIST_ID --query ETag --output text)
aws cloudfront delete-distribution --id $DIST_ID --if-match $NEW_ETAG
aws cloudfront delete-origin-access-control --id $OAC_ID \
  --if-match $(aws cloudfront get-origin-access-control --id $OAC_ID --query ETag --output text)
# 3) Bucket
aws s3 rm s3://$B45 --recursive && aws s3api delete-bucket --bucket $B45 --region $AWS_REGION
```

### 🧠 Ý nghĩa với đề thi
- "Khoá bucket `S3` **chỉ cho `CloudFront`** đọc" → **`OAC`** (thay `OAI`; `OAC` hỗ trợ `SSE-KMS`, mọi region, là khuyến nghị hiện tại).
- Bucket policy phải khớp **service principal `cloudfront.amazonaws.com`** + condition `AWS:SourceArn` = distribution ARN.
- `CloudFront signed URL` (1 file) vs `signed cookies` (nhiều file) — cả hai ký bằng **trusted key group**; khác `S3` presigned URL (truy cập thẳng S3).
- Đẩy nội dung mới trước TTL: `CreateInvalidation` (1000 path/tháng đầu miễn phí) hoặc tốt hơn: **versioned object name** (`app.v2.js`).

---

## Lab 4.6 — `Lambda authorizer` / `Cognito` + bật CORS cho API (Lab 4.2)
**🎯 Mục tiêu:** Bảo vệ CRUD API (Lab 4.2) bằng **`Lambda authorizer` (TOKEN)** trả IAM policy Allow/Deny, và bật **CORS** để trình duyệt gọi được từ domain khác.
**🧩 Luyện kỹ năng (liên quan đề):**
- `create-authorizer` type `TOKEN`, identity source `Authorization` header; authorizer trả `{principalId, policyDocument}`.
- Cấp quyền cho API Gateway gọi authorizer (`add-permission`, source-arn `.../authorizers/<id>`).
- CORS với **proxy**: Lambda phải tự trả header CORS; preflight `OPTIONS` xử lý bằng **Mock integration**.
**⏱️ ~40 phút** · **Yêu cầu trước:** đã hoàn tất Lab 4.2 (còn `$API_ID`, `$ITEMS_ID`, `$ITEM_ID`, role `week4-crud-role`).

### Các bước
1. Viết + tạo function authorizer (TOKEN). Token `allow`→Allow, `deny`→Deny(403), rỗng/`unauthorized`→401.
   ```python
   # authorizer.py
   def handler(event, context):
       token = event.get('authorizationToken', '')
       arn = event['methodArn']
       if token == 'allow':
           effect = 'Allow'
       elif token == 'deny':
           effect = 'Deny'                       # → 403 Forbidden
       else:
           raise Exception('Unauthorized')       # message "Unauthorized" → 401
       return {
           "principalId": "user",
           "policyDocument": {
               "Version": "2012-10-17",
               "Statement": [{"Action": "execute-api:Invoke",
                              "Effect": effect, "Resource": arn}]
           },
           "context": {"who": "week4-lab"}        # (tuỳ chọn) đẩy xuống backend
       }
   ```
   ```bash
   zip authorizer.zip authorizer.py
   aws lambda create-function --function-name week4-authorizer \
     --runtime python3.12 --handler authorizer.handler \
     --role arn:aws:iam::$ACCOUNT_ID:role/week4-crud-role \
     --zip-file fileb://authorizer.zip --timeout 10 --region $AWS_REGION
   AUTH_ARN=$(aws lambda get-function --function-name week4-authorizer \
     --query 'Configuration.FunctionArn' --output text --region $AWS_REGION)
   ```
2. Tạo authorizer trong API + cấp quyền cho API Gateway gọi nó.
   ```bash
   AUTHZ_ID=$(aws apigateway create-authorizer --rest-api-id $API_ID \
     --name tokenAuth --type TOKEN \
     --authorizer-uri arn:aws:apigateway:$AWS_REGION:lambda:path/2015-03-31/functions/$AUTH_ARN/invocations \
     --identity-source method.request.header.Authorization \
     --query id --output text --region $AWS_REGION)

   aws lambda add-permission --function-name week4-authorizer \
     --statement-id apigw-authorizer --action lambda:InvokeFunction \
     --principal apigateway.amazonaws.com \
     --source-arn "arn:aws:execute-api:$AWS_REGION:$ACCOUNT_ID:$API_ID/authorizers/$AUTHZ_ID" \
     --region $AWS_REGION
   ```
3. Gắn authorizer vào method `GET /items` (đổi authorizationType → CUSTOM).
   ```bash
   aws apigateway update-method --rest-api-id $API_ID --resource-id $ITEMS_ID \
     --http-method GET --patch-operations \
     op=replace,path=/authorizationType,value=CUSTOM \
     op=replace,path=/authorizerId,value=$AUTHZ_ID --region $AWS_REGION
   ```
4. **Bật CORS** cho `/items`: tạo `OPTIONS` (Mock) trả 3 header preflight.
   ```bash
   aws apigateway put-method --rest-api-id $API_ID --resource-id $ITEMS_ID \
     --http-method OPTIONS --authorization-type NONE --region $AWS_REGION
   aws apigateway put-integration --rest-api-id $API_ID --resource-id $ITEMS_ID \
     --http-method OPTIONS --type MOCK \
     --request-templates '{"application/json":"{\"statusCode\":200}"}' --region $AWS_REGION
   aws apigateway put-method-response --rest-api-id $API_ID --resource-id $ITEMS_ID \
     --http-method OPTIONS --status-code 200 --response-models application/json=Empty \
     --response-parameters method.response.header.Access-Control-Allow-Headers=false,method.response.header.Access-Control-Allow-Methods=false,method.response.header.Access-Control-Allow-Origin=false \
     --region $AWS_REGION
   aws apigateway put-integration-response --rest-api-id $API_ID --resource-id $ITEMS_ID \
     --http-method OPTIONS --status-code 200 \
     --response-parameters "method.response.header.Access-Control-Allow-Headers='Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',method.response.header.Access-Control-Allow-Methods='DELETE,GET,HEAD,OPTIONS,PUT,POST,PATCH',method.response.header.Access-Control-Allow-Origin='*'" \
     --region $AWS_REGION
   ```
   > Với proxy integration, các method thật (GET/POST...) tự trả `Access-Control-Allow-Origin` **từ trong Lambda** — handler Lab 4.2 đã kèm sẵn header đó trong `resp()`.
5. Deploy lại + test.
   ```bash
   aws apigateway create-deployment --rest-api-id $API_ID --stage-name dev --region $AWS_REGION
   BASE=https://$API_ID.execute-api.$AWS_REGION.amazonaws.com/dev

   curl -s -o /dev/null -w "no-token  → %{http_code}\n"                 $BASE/items   # 401
   curl -s -o /dev/null -w "deny      → %{http_code}\n" -H "Authorization: deny"  $BASE/items   # 403
   curl -s -o /dev/null -w "allow     → %{http_code}\n" -H "Authorization: allow" $BASE/items   # 200
   # Preflight CORS
   curl -s -o /dev/null -w "OPTIONS   → %{http_code}\n" -X OPTIONS $BASE/items      # 200
   curl -s -D - -X OPTIONS $BASE/items | grep -i access-control                     # thấy 3 header
   ```

### ✅ Kiểm chứng
- Không token → **401**; `Authorization: deny` → **403**; `Authorization: allow` → **200** trả danh sách items.
- `OPTIONS /items` → **200** kèm `Access-Control-Allow-Origin/-Methods/-Headers`.

### 🔁 (Thay thế) Dùng `Cognito User Pool authorizer`
```bash
# Tạo user pool + app client (JWT), rồi tạo authorizer type COGNITO_USER_POOLS
POOL_ID=$(aws cognito-idp create-user-pool --pool-name week4-pool \
  --query 'UserPool.Id' --output text --region $AWS_REGION)
CLIENT_ID=$(aws cognito-idp create-user-pool-client --user-pool-id $POOL_ID \
  --client-name week4-client --explicit-auth-flows ALLOW_USER_PASSWORD_AUTH ALLOW_REFRESH_TOKEN_AUTH \
  --query 'UserPoolClient.ClientId' --output text --region $AWS_REGION)
aws apigateway create-authorizer --rest-api-id $API_ID --name cognitoAuth \
  --type COGNITO_USER_POOLS --identity-source method.request.header.Authorization \
  --provider-arns arn:aws:cognito-idp:$AWS_REGION:$ACCOUNT_ID:userpool/$POOL_ID --region $AWS_REGION
# Gọi API kèm IdToken (JWT) lấy từ InitiateAuth trong header Authorization.
```

### 🧹 Dọn dẹp
```bash
aws lambda delete-function --function-name week4-authorizer --region $AWS_REGION
# (nếu đã tạo Cognito) aws cognito-idp delete-user-pool --user-pool-id $POOL_ID --region $AWS_REGION
# Rồi dọn nốt API/Lambda/DynamoDB/role theo phần Dọn dẹp Lab 4.2.
```

### 🧠 Ý nghĩa với đề thi
- `Lambda authorizer` nhận identity → trả **IAM policy Allow/Deny** (+ principalId, tuỳ chọn `context`). `TOKEN` = 1 bearer token; `REQUEST` = nhiều nguồn (AWS khuyến nghị `REQUEST`).
- Deny → **403 ACCESS_DENIED**; token rỗng/`unauthorized` → **401 UNAUTHORIZED**.
- "Xác thực JWT của user đăng nhập app" → **`Cognito User Pool authorizer`**; "ký request bằng cred AWS" → **`IAM (SigV4)`**.
- CORS với **proxy**: backend (Lambda) tự trả header CORS; bật CORS trên Console mà vẫn lỗi → do Lambda chưa trả `Access-Control-Allow-Origin`.
