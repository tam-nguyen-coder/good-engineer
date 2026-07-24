# 🧪 Hands-on Labs — Tuần 1: Developer mindset + AWS SDK/CLI + `Lambda` (cơ bản)

> Lab cầm tay chỉ việc, chạy được trên tài khoản AWS thật (Free Tier). LUÔN chạy phần Dọn dẹp cuối mỗi lab.
> ⚙️ Yêu cầu chung: đã cấu hình `AWS CLI v2` (xem Lab 1.1) + IAM đủ quyền cho dịch vụ trong lab.
> Về [plan tuần](README.md) · [Câu hỏi luyện tập](questions.md) · [Kế hoạch tổng](../../DVA-C02-STUDY-PLAN.md)

> 🧰 **Biến shell dùng chung** (đặt 1 lần cho cả buổi — nhớ đổi region cho phù hợp, mặc định `us-east-1`):
> ```bash
> export REGION=us-east-1
> export ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
> export ROLE_NAME=dva-lab-lambda-role
> export ROLE_ARN=arn:aws:iam::$ACCOUNT_ID:role/$ROLE_NAME
> ```

---

## Lab 1.1 — Cấu hình `AWS CLI v2` + thực nghiệm credential provider chain
**🎯 Mục tiêu:** Cấu hình `default` profile và named profile `dev`, xác minh danh tính bằng `aws sts get-caller-identity`, rồi tự tay chứng minh **env var thắng file profile** trong credential provider chain.
**🧩 Luyện kỹ năng (liên quan đề):**
- Đọc hiểu `~/.aws/credentials` vs `~/.aws/config` và `[profile <tên>]` vs `[<tên>]`.
- Thứ tự chọn region: `--region` > `AWS_REGION`/`AWS_DEFAULT_REGION` > region trong profile.
- Credential provider chain: **env var đứng TRƯỚC** shared credentials/config file (bẫy đề hay gặp).
**⏱️ ~25 phút** · **Yêu cầu trước:** đã cài `AWS CLI v2` (`aws --version` → `aws-cli/2.x`) và có 1 cặp access key hợp lệ.

### Các bước
1. Cấu hình `default` profile và named profile `dev`.
   ```bash
   aws configure                 # nhập key/secret, region, output cho [default]
   aws configure --profile dev   # cặp key khác (hoặc cùng account), region khác để dễ thấy
   ```
2. Xem 2 file cấu hình sinh ra và để ý sự khác biệt tên section.
   ```bash
   aws configure list-profiles
   cat ~/.aws/credentials     # section: [default] và [dev]
   cat ~/.aws/config          # section: [default] và [profile dev]
   ```
3. Xác minh danh tính đang dùng theo từng profile.
   ```bash
   aws sts get-caller-identity                 # dùng default
   aws sts get-caller-identity --profile dev   # dùng dev → khác Account/Arn nếu khác account
   ```
   Output có 3 trường: `Account`, `Arn`, `UserId`.
4. **Thực nghiệm chọn region** (không đổi credentials): cờ dòng lệnh thắng biến môi trường thắng profile.
   ```bash
   aws configure get region                                  # region trong profile (~/.aws/config)
   AWS_REGION=eu-west-1 aws configure list | grep region     # env var override profile (nạp từ env)

   # Chứng minh cờ --region thắng tất cả khi gọi API thực tế (dùng --debug để xem endpoint):
   AWS_REGION=eu-west-1 aws sts get-caller-identity --region ap-northeast-1 --debug 2>&1 | grep "Making request"
   # → Endpoint gửi tới https://sts.ap-northeast-1.amazonaws.com/ (cờ --region thắng cả env var và profile)
   ```
   > ⚠️ **Lưu ý về `aws configure list`:** Lệnh này liệt kê nguồn nạp cấu hình (file hoặc `env`). Cờ CLI `--region` là tham số thực thi thời gian thực chứ không phải giá trị cấu hình tĩnh nạp từ env/file, do đó `aws configure list` vẫn hiện nguồn từ config file/env var. Tuy nhiên khi thực thi API thực tế, `--region` luôn có độ ưu tiên cao nhất.
   
5. **Thực nghiệm credential chain — env var thắng file.** Cố tình đặt env var credentials SAI rồi gọi lại: nếu lệnh báo lỗi token không hợp lệ (thay vì fallback về profile hợp lệ) nghĩa là SDK/CLI đã **dừng ở env var** — env đứng trước file.
   ```bash
   # Đang OK nhờ [default] trong file:
   aws sts get-caller-identity

   # Nạp credentials SAI qua env var (KHÔNG truyền --profile):
   export AWS_ACCESS_KEY_ID=AKIAINVALIDKEYEXAMPLE
   export AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/INVALIDSECRETKEYEXAMPLE
   aws sts get-caller-identity
   # → Lỗi: InvalidClientTokenId / "security token ... is invalid"
   #   Chứng minh CLI DÙNG env var (dù profile file vẫn hợp lệ) → env thắng file.

   # Gỡ env var để trở lại dùng profile file:
   unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY
   aws sts get-caller-identity   # OK trở lại
   ```
   > ⚠️ Lưu ý chuẩn xác: thí nghiệm này **không** truyền `--profile`. Nếu bạn truyền `--profile <tên>` tường minh trên dòng lệnh thì đó là *command-line option* (ưu tiên cao nhất), CLI sẽ dùng profile đó và bỏ qua credentials trong env var. Bỏ `--profile` để so đúng cặp **env var vs file**.

### ✅ Kiểm chứng
- `aws sts get-caller-identity --profile dev` trả về `Arn` đúng của profile `dev`.
- Bước 5: khi có env var sai → lệnh **fail** ngay (không âm thầm dùng profile file) → đã tận mắt thấy env var được ưu tiên trước file trong chain.

### 🧹 Dọn dẹp (tránh tính phí)
```bash
unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN AWS_REGION
# (Tuỳ chọn) xoá profile dev nếu chỉ tạo để thử:
# mở ~/.aws/credentials và ~/.aws/config, xoá section [dev] / [profile dev]
```
> Lab này không tạo tài nguyên tính phí — chỉ cần dọn env var.

### 🧠 Ý nghĩa với đề thi
- "Vừa set env var vừa có profile trong file → creds nào được dùng?" → **env var thắng** (đứng trước file trong chain).
- Region resolution: `--region` > `AWS_REGION`/`AWS_DEFAULT_REGION` > profile config.
- Không hard-code key: production dùng IAM role (instance profile / task role / execution role), SDK tự lấy qua chain.

---

## Lab 1.2 — Tạo & invoke `Lambda` bằng 3 cách (Console · CLI · SDK) + đọc `CloudWatch Logs`
**🎯 Mục tiêu:** Tạo 1 execution role, tạo 1 hàm `Lambda` Node.js (`nodejs24.x`), invoke nó bằng **cả 3 cách** (Console, CLI với zip, SDK v3 `@aws-sdk/client-lambda`) và đọc log ở `CloudWatch Logs`.
**🧩 Luyện kỹ năng (liên quan đề):**
- `aws lambda create-function` với deployment package (`.zip`).
- Trust policy `lambda.amazonaws.com` + managed policy `AWSLambdaBasicExecutionRole` để ghi log.
- Cấu trúc handler ESM `export const handler = async (event, context) => {...}`; log tự động đẩy vào group `/aws/lambda/<tên>`.
**⏱️ ~40 phút** · **Yêu cầu trước:** đã làm Lab 1.1 (CLI + biến shell dùng chung).

### Các bước
1. Tạo **execution role** cho `Lambda` (trust policy cho service principal `lambda.amazonaws.com`).
   ```bash
   cat > trust.json <<'EOF'
   {
     "Version": "2012-10-17",
     "Statement": [{
       "Effect": "Allow",
       "Principal": { "Service": "lambda.amazonaws.com" },
       "Action": "sts:AssumeRole"
     }]
   }
   EOF

   aws iam create-role --role-name "$ROLE_NAME" \
     --assume-role-policy-document file://trust.json

   # Quyền ghi CloudWatch Logs (bắt buộc để thấy log)
   aws iam attach-role-policy --role-name "$ROLE_NAME" \
     --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
   ```
2. Viết handler tối giản và đóng gói `.zip`.
   ```javascript
   // index.mjs
   export const handler = async (event, context) => {
     console.log("event:", JSON.stringify(event));
     console.log("requestId:", context.awsRequestId);
     return { statusCode: 200, body: "hello DVA" };
   };
   ```
   ```bash
   zip function.zip index.mjs
   ```
3. **Cách 1 — CLI:** tạo hàm từ zip (chờ vài giây cho role kịp propagate nếu gặp lỗi `InvalidParameterValueException` về role).
   ```bash
   aws lambda create-function \
     --function-name dva-lab-fn \
     --runtime nodejs24.x \
     --role "$ROLE_ARN" \
     --handler index.handler \
     --zip-file fileb://function.zip \
     --region "$REGION"
   ```
   Invoke bằng CLI:
   ```bash
   aws lambda invoke \
     --function-name dva-lab-fn \
     --payload '{"name":"cli"}' \
     --cli-binary-format raw-in-base64-out \
     --region "$REGION" \
     out.json
   cat out.json    # → {"statusCode": 200, "body": "hello DVA"}
   ```
4. **Cách 2 — Console:** vào `Lambda` → hàm `dva-lab-fn` → tab **Test** → tạo test event JSON `{"name":"console"}` → **Test**. (Hoặc **Create function** → *Author from scratch* → **Use an existing role** = `dva-lab-lambda-role` → dán code → **Deploy** → **Test**.) Quan sát panel *Execution results*.
5. **Cách 3 — SDK v3 (`@aws-sdk/client-lambda`):** invoke bằng code.
   ```javascript
   // invoke_sdk.mjs
   import { LambdaClient, InvokeCommand } from "@aws-sdk/client-lambda";

   const lambda = new LambdaClient({ region: process.env.REGION || "us-east-1" });
   const resp = await lambda.send(new InvokeCommand({
     FunctionName: "dva-lab-fn",
     InvocationType: "RequestResponse",              // synchronous
     Payload: Buffer.from(JSON.stringify({ name: "sdk" })),
   }));
   console.log("StatusCode:", resp.StatusCode);        // 200
   console.log("Payload:", Buffer.from(resp.Payload).toString());
   ```
   ```bash
   # Script chạy LOCAL (không phải Lambda) → phải tự cài SDK v3
   npm init -y && npm install @aws-sdk/client-lambda
   node invoke_sdk.mjs
   ```
6. Đọc log ở `CloudWatch Logs` (group tự sinh `/aws/lambda/<tên>`).
   ```bash
   aws logs tail /aws/lambda/dva-lab-fn --follow --region "$REGION"
   ```

### ✅ Kiểm chứng
- Cả 3 cách đều trả `statusCode 200` / body `hello DVA`.
- `aws logs tail` in ra `event: {...}` với 3 giá trị `name` khác nhau (`cli`, `console`, `sdk`) + dòng `START/END/REPORT` (có `requestId`, billed duration).

### 🧹 Dọn dẹp (tránh tính phí)
```bash
aws lambda delete-function --function-name dva-lab-fn --region "$REGION"
aws logs delete-log-group --log-group-name /aws/lambda/dva-lab-fn --region "$REGION" 2>/dev/null || true
# Giữ lại role nếu làm tiếp Lab 1.3/1.5; muốn xoá hẳn:
# aws iam detach-role-policy --role-name "$ROLE_NAME" --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
# aws iam delete-role --role-name "$ROLE_NAME"
```

### 🧠 Ý nghĩa với đề thi
- Log không hiện trong `CloudWatch` → nghi **execution role thiếu quyền `logs:*`** (thiếu `AWSLambdaBasicExecutionRole`), không phải lỗi code.
- Handler nhận `event` (payload) + `context` (`context.awsRequestId`, thời gian còn lại...); code khai báo ngoài handler được tái sử dụng giữa các invoke → tạo SDK client ở init.
- `InvocationType`: `RequestResponse` (sync) vs `Event` (async) — nhớ phân biệt cho các lab tuần sau.

---

## Lab 1.3 — ⭐ `Lambda` gọi `DynamoDB` + `S3` qua execution role (thấy `AccessDenied` → fix bằng IAM policy)
**🎯 Mục tiêu:** Viết handler Node.js (SDK v3: `DynamoDBDocumentClient` + `S3Client`) ghi 1 item vào `DynamoDB` và put 1 object lên `S3`. Cố tình chạy khi execution role **thiếu quyền** để thấy `AccessDenied`, rồi gắn IAM policy least-privilege để fix và chạy lại thành công.
**🧩 Luyện kỹ năng (liên quan đề):**
- **Execution role** = quyền để function **gọi service khác** (đọc/ghi `S3`, `DynamoDB`) — nền tảng của mọi tích hợp `Lambda`.
- Đọc lỗi `AccessDeniedException` / `not authorized to perform: dynamodb:PutItem` trong `CloudWatch Logs`.
- Vá quyền theo **least privilege** (inline policy giới hạn đúng resource ARN).
- Dùng **waiter** chờ bảng `DynamoDB` `ACTIVE`.
**⏱️ ~45 phút** · **Yêu cầu trước:** đã có role `dva-lab-lambda-role` (Lab 1.2). Đặt tên bucket toàn cục duy nhất.

### Các bước
1. Đặt tên tài nguyên và tạo `DynamoDB` table + `S3` bucket.
   ```bash
   export TABLE=dva-lab-events
   export BUCKET=dva-lab-events-$ACCOUNT_ID   # phải duy nhất toàn cầu

   # DynamoDB on-demand (Free Tier friendly), PK = id (String)
   aws dynamodb create-table \
     --table-name "$TABLE" \
     --attribute-definitions AttributeName=id,AttributeType=S \
     --key-schema AttributeName=id,KeyType=HASH \
     --billing-mode PAY_PER_REQUEST \
     --region "$REGION"
   aws dynamodb wait table-exists --table-name "$TABLE" --region "$REGION"   # waiter

   # S3 bucket
   aws s3api create-bucket --bucket "$BUCKET" --region "$REGION"
   # us-east-1 là default → KHÔNG cần LocationConstraint. (Region khác: thêm --create-bucket-configuration LocationConstraint=<region>)
   ```
2. Viết handler tích hợp và đóng gói lại.
   ```javascript
   // index.mjs
   import { randomUUID } from "crypto";
   import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
   import { DynamoDBDocumentClient, PutCommand } from "@aws-sdk/lib-dynamodb";
   import { S3Client, PutObjectCommand } from "@aws-sdk/client-s3";

   const TABLE  = process.env.TABLE_NAME;
   const BUCKET = process.env.BUCKET_NAME;

   // client tạo ở init → tái sử dụng giữa các invoke
   const ddb = DynamoDBDocumentClient.from(new DynamoDBClient({}));
   const s3  = new S3Client({});

   export const handler = async (event, context) => {
     const itemId = randomUUID();
     // (1) Ghi item vào DynamoDB — cần dynamodb:PutItem trong execution role
     await ddb.send(new PutCommand({
       TableName: TABLE,
       Item: { id: itemId, ts: Math.floor(Date.now() / 1000), msg: event.msg ?? "hi" },
     }));
     // (2) Put object lên S3 — cần s3:PutObject
     await s3.send(new PutObjectCommand({
       Bucket: BUCKET,
       Key: `events/${itemId}.json`,
       Body: JSON.stringify(event),
     }));
     return { ok: true, id: itemId };
   };
   ```
   ```bash
   # nodejs24.x đã bundle sẵn @aws-sdk/client-dynamodb, lib-dynamodb, client-s3 → chỉ cần zip index.mjs
   zip app.zip index.mjs
   ```
3. Tạo hàm mới, truyền tên bảng/bucket qua **environment variables**. Role hiện chỉ có `AWSLambdaBasicExecutionRole` → **chưa có** quyền `DynamoDB`/`S3`.
   ```bash
   aws lambda create-function \
     --function-name dva-lab-integrate \
     --runtime nodejs24.x \
     --role "$ROLE_ARN" \
     --handler index.handler \
     --zip-file fileb://app.zip \
     --environment "Variables={TABLE_NAME=$TABLE,BUCKET_NAME=$BUCKET}" \
     --region "$REGION"
   ```
4. **Invoke lần 1 — kỳ vọng THẤT BẠI (AccessDenied):**
   ```bash
   aws lambda invoke \
     --function-name dva-lab-integrate \
     --payload '{"msg":"first-try"}' \
     --cli-binary-format raw-in-base64-out \
     --region "$REGION" \
     out.json
   cat out.json     # → có "errorType": ... "AccessDeniedException"
   aws logs tail /aws/lambda/dva-lab-integrate --region "$REGION"
   # Log: "User: ...dva-lab-lambda-role... is not authorized to perform: dynamodb:PutItem"
   ```
5. **Fix bằng inline policy least-privilege** (chỉ đúng bảng + bucket này), rồi chờ IAM propagate vài giây.
   ```bash
   cat > lab13-policy.json <<EOF
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": "dynamodb:PutItem",
         "Resource": "arn:aws:dynamodb:$REGION:$ACCOUNT_ID:table/$TABLE"
       },
       {
         "Effect": "Allow",
         "Action": "s3:PutObject",
         "Resource": "arn:aws:s3:::$BUCKET/*"
       }
     ]
   }
   EOF

   aws iam put-role-policy \
     --role-name "$ROLE_NAME" \
     --policy-name dva-lab-ddb-s3 \
     --policy-document file://lab13-policy.json
   ```
6. **Invoke lần 2 — kỳ vọng THÀNH CÔNG.**
   ```bash
   aws lambda invoke \
     --function-name dva-lab-integrate \
     --payload '{"msg":"after-fix"}' \
     --cli-binary-format raw-in-base64-out \
     --region "$REGION" \
     out.json
   cat out.json     # → {"ok": true, "id": "..."}
   ```

### ✅ Kiểm chứng
- Lần 1 log có `AccessDeniedException` (execution role thiếu quyền) — đúng như kỳ vọng.
- Sau khi gắn policy, đọc lại dữ liệu thực:
  ```bash
  aws dynamodb scan --table-name "$TABLE" --region "$REGION" --query "Items[].id"
  aws s3 ls "s3://$BUCKET/events/" --region "$REGION"
  ```
  → thấy item trong bảng và object `events/<id>.json` trong bucket.

### 🧹 Dọn dẹp (tránh tính phí)
```bash
aws lambda delete-function --function-name dva-lab-integrate --region "$REGION"
aws logs delete-log-group --log-group-name /aws/lambda/dva-lab-integrate --region "$REGION" 2>/dev/null || true
aws iam delete-role-policy --role-name "$ROLE_NAME" --policy-name dva-lab-ddb-s3
aws dynamodb delete-table --table-name "$TABLE" --region "$REGION"
aws s3 rm "s3://$BUCKET" --recursive
aws s3api delete-bucket --bucket "$BUCKET" --region "$REGION"
```

### 🧠 Ý nghĩa với đề thi
- "Code trên `Lambda`/EC2 cần gọi `S3`/`DynamoDB`" → gắn **IAM role** (execution role), **không** hard-code access key.
- Function chạy nhưng báo `AccessDenied` khi gọi service khác → **thiếu quyền trong execution role**, KHÔNG phải resource-based policy (đó là "ai được invoke function").
- Least privilege: policy giới hạn đúng `Action` + `Resource` ARN, không cấp `*` — điểm best-practice hay hỏi.

---

## Lab 1.4 — SDK v3: retry/exponential backoff (`maxAttempts`/`retryMode`) + paginator
**🎯 Mục tiêu:** Viết script Node.js (SDK v3) cấu hình **retry mode + max attempts** qua option `maxAttempts`/`retryMode` của client, và dùng **paginator** (`paginateListObjectsV2`, `paginateListTables`) để liệt kê **toàn bộ** object trong bucket / bảng trong account (không sót trang).
**🧩 Luyện kỹ năng (liên quan đề):**
- `new Client({ maxAttempts: N, retryMode: "standard|adaptive" })` — SDK tự backoff + full jitter khi throttle.
- Paginator xử lý `NextToken`/`Marker` tự động → tránh sót dữ liệu ở trang sau.
- Phân biệt lỗi nên retry (throttling/transient) vs không (`AccessDenied`, `Validation`).
**⏱️ ~30 phút** · **Yêu cầu trước:** đã có `AWS CLI v2`; nên có sẵn 1 bucket nhiều object để thấy phân trang (tạo tạm nếu cần).

### Các bước
1. (Tuỳ chọn) Tạo dữ liệu để phân trang: 1 bucket + vài chục object nhỏ.
   ```bash
   export BUCKET=dva-lab-paginate-$ACCOUNT_ID
   aws s3api create-bucket --bucket "$BUCKET" --region "$REGION"
   # us-east-1 là default → KHÔNG cần LocationConstraint. (Region khác: thêm --create-bucket-configuration LocationConstraint=<region>)
   for i in $(seq 1 30); do echo "obj $i" | aws s3 cp - "s3://$BUCKET/k/$i.txt"; done
   ```
2. Viết script có **retry config** + **paginator**.
   ```javascript
   // sdk_retry_paginate.mjs
   import { S3Client, paginateListObjectsV2, ListObjectsV2Command } from "@aws-sdk/client-s3";
   import { DynamoDBClient, paginateListTables } from "@aws-sdk/client-dynamodb";

   const REGION = process.env.REGION || "us-east-1";
   const BUCKET = process.env.BUCKET;

   // retryMode: standard (mặc định) | adaptive (single-resource, throttle nhiều)
   // maxAttempts = TỔNG số lần thử kể cả lần đầu (3 = 1 đầu + 2 retry); mặc định = 3
   const retryOpts = { maxAttempts: 5, retryMode: "adaptive" };

   const s3 = new S3Client({ region: REGION, ...retryOpts });

   // (A) Paginator liệt kê TOÀN BỘ object (tự lặp ContinuationToken)
   let count = 0;
   for await (const page of paginateListObjectsV2({ client: s3, pageSize: 10 }, { Bucket: BUCKET })) {
     for (const obj of page.Contents ?? []) {
       console.log(obj.Key);
       count++;
     }
   }
   console.log(`[S3] tổng object = ${count}`);

   // (B) Paginator liệt kê TOÀN BỘ bảng DynamoDB trong account/region
   const ddb = new DynamoDBClient({ region: REGION, ...retryOpts });
   const tables = [];
   for await (const page of paginateListTables({ client: ddb }, {})) {
     tables.push(...(page.TableNames ?? []));
   }
   console.log(`[DynamoDB] tổng bảng = ${tables.length} → ${tables}`);
   ```
   ```bash
   # Script chạy LOCAL (không phải Lambda) → phải tự cài SDK v3 trước khi chạy
   npm init -y && npm install @aws-sdk/client-s3 @aws-sdk/client-dynamodb
   node sdk_retry_paginate.mjs
   ```
3. (Tuỳ chọn) Chứng minh cấu hình retry qua **env var** (precedence: code > env > config file). Không đổi code, chỉ set env:
   ```bash
   AWS_RETRY_MODE=standard AWS_MAX_ATTEMPTS=8 node sdk_retry_paginate.mjs
   ```

### ✅ Kiểm chứng
- `[S3] tổng object = 30` (khớp số object đã tạo — paginator không sót dù `PageSize=10`).
- `[DynamoDB]` in ra danh sách đầy đủ các bảng trong region.
- So sánh: nếu chỉ gọi `s3.send(new ListObjectsV2Command({ Bucket }))` một lần và bỏ qua `NextContinuationToken`, kết quả bị cắt ở ~1000 object đầu → thấy rõ vì sao cần paginator.

### 🧹 Dọn dẹp (tránh tính phí)
```bash
aws s3 rm "s3://$BUCKET" --recursive
aws s3api delete-bucket --bucket "$BUCKET" --region "$REGION"
```

### 🧠 Ý nghĩa với đề thi
- Gặp `ThrottlingException` / `Rate exceeded` → **retry + exponential backoff + jitter** (cân nhắc `adaptive`), KHÔNG phải tăng timeout.
- `adaptive` chỉ hợp khi client nhắm **1 resource** và bị throttle nhiều; nhắm nhiều resource → dùng `standard`.
- "List trả về thiếu / có `NextToken`/`Marker`" → dùng **paginator**, không phải bug API.
- Precedence retry setting: code `{ maxAttempts, retryMode }` > env `AWS_RETRY_MODE`/`AWS_MAX_ATTEMPTS` > `~/.aws/config`.

---

## Lab 1.5 — Environment variables cho `Lambda` (+ mã hoá `KMS`) và đọc lúc runtime
**🎯 Mục tiêu:** Gắn environment variables cho hàm `Lambda`, đọc chúng lúc runtime bằng `process.env`, và hiểu cơ chế mã hoá at-rest bằng `KMS` (AWS managed key mặc định; tuỳ chọn Customer Managed Key).
**🧩 Luyện kỹ năng (liên quan đề):**
- `--environment "Variables={...}"` qua CLI; đọc bằng `process.env.XXX` trong handler.
- Env vars **mã hoá at-rest mặc định** bằng AWS managed key `aws/lambda`; có thể chỉ định **CMK** qua `--kms-key-arn`.
- Secret thật nên để ở `Secrets Manager`/`SSM Parameter Store`, không nhét plaintext vào env var.
**⏱️ ~30 phút** · **Yêu cầu trước:** đã có role `dva-lab-lambda-role` (Lab 1.2).

### Các bước
1. Handler đọc env var lúc runtime.
   ```javascript
   // index.mjs
   export const handler = async (event, context) => {
     const stage   = process.env.STAGE ?? "dev";
     const feature = process.env.FEATURE_FLAG ?? "off";
     const apiBase = process.env.API_BASE_URL;                       // bắt buộc phải có
     if (!apiBase) throw new Error("Missing env var API_BASE_URL");  // thiếu → lỗi rõ ràng, dễ phát hiện cấu hình sai
     console.log(`STAGE=${stage} FEATURE_FLAG=${feature} API_BASE_URL=${apiBase}`);
     return { stage, feature, api_base: apiBase };
   };
   ```
   ```bash
   zip env_app.zip index.mjs
   ```
2. Tạo hàm với environment variables ban đầu.
   ```bash
   aws lambda create-function \
     --function-name dva-lab-env \
     --runtime nodejs24.x \
     --role "$ROLE_ARN" \
     --handler index.handler \
     --zip-file fileb://env_app.zip \
     --environment "Variables={STAGE=dev,FEATURE_FLAG=off,API_BASE_URL=https://api.example.com}" \
     --region "$REGION"
   ```
3. Invoke và xem giá trị đọc được.
   ```bash
   aws lambda invoke --function-name dva-lab-env \
     --cli-binary-format raw-in-base64-out --payload '{}' \
     --region "$REGION" out.json
   cat out.json
   ```
4. **Cập nhật env var** (thay đổi config, không cần deploy lại code) và invoke lại.
   ```bash
   aws lambda update-function-configuration \
     --function-name dva-lab-env \
     --environment "Variables={STAGE=prod,FEATURE_FLAG=on,API_BASE_URL=https://api.prod.example.com}" \
     --region "$REGION"
   aws lambda invoke --function-name dva-lab-env \
     --cli-binary-format raw-in-base64-out --payload '{}' \
     --region "$REGION" out.json && cat out.json   # → STAGE=prod, FEATURE_FLAG=on
   ```
5. Kiểm tra thông tin **mã hoá `KMS`** của env vars (mặc định dùng AWS managed key `aws/lambda`).
   ```bash
   aws lambda get-function-configuration --function-name dva-lab-env \
     --region "$REGION" --query "Environment"
   aws lambda get-function-configuration --function-name dva-lab-env \
     --region "$REGION" --query "KMSKeyArn"   # null = đang dùng AWS managed key mặc định
   ```
6. **(Tuỳ chọn — CMK)** Dùng Customer Managed Key để mã hoá env vars at-rest.
   > ⚠️ CMK ~ $1/tháng (không hoàn toàn Free Tier). Làm xong nhớ schedule delete ở phần Dọn dẹp.
   ```bash
   export KMS_ARN=$(aws kms create-key --description "dva-lab env vars" \
     --query KeyMetadata.Arn --output text --region "$REGION")

   aws lambda update-function-configuration \
     --function-name dva-lab-env \
     --kms-key-arn "$KMS_ARN" \
     --region "$REGION"

   aws lambda get-function-configuration --function-name dva-lab-env \
     --region "$REGION" --query "KMSKeyArn"    # → giờ trỏ tới CMK
   ```

### ✅ Kiểm chứng
- `out.json` phản ánh đúng giá trị env var hiện hành (bước 3 = `dev/off`, bước 4 = `prod/on`).
- `get-function-configuration` cho thấy `Environment.Variables` và (nếu làm bước 6) `KMSKeyArn` trỏ tới CMK.

### 🧹 Dọn dẹp (tránh tính phí)
```bash
aws lambda delete-function --function-name dva-lab-env --region "$REGION"
aws logs delete-log-group --log-group-name /aws/lambda/dva-lab-env --region "$REGION" 2>/dev/null || true
# Nếu đã tạo CMK ở bước 6:
# aws kms schedule-key-deletion --key-id "$KMS_ARN" --pending-window-in-days 7 --region "$REGION"
# Xoá role nếu không dùng nữa:
# aws iam detach-role-policy --role-name "$ROLE_NAME" --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
# aws iam delete-role --role-name "$ROLE_NAME"
```

### 🧠 Ý nghĩa với đề thi
- Env vars `Lambda` **luôn mã hoá at-rest bằng `KMS`** (mặc định `aws/lambda`); cần kiểm soát khoá/audit → dùng **CMK** (`--kms-key-arn`).
- Đổi cấu hình runtime (env var) qua `update-function-configuration` **không cần** đóng gói lại code.
- Secret nhạy cảm (mật khẩu DB, API key) → nên để `Secrets Manager` / `SSM Parameter Store` (có rotation), không để plaintext trong env var; env var chỉ nên chứa tên tham số/tên secret.
