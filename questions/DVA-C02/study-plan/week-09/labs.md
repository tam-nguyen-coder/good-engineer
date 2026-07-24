# 🧪 Hands-on Labs — Tuần 9: Observability & Optimization (`CloudWatch` / `X-Ray` / `CloudTrail` / `EventBridge`)

> Lab cầm tay chỉ việc, chạy được trên tài khoản AWS thật (Free Tier). LUÔN chạy phần Dọn dẹp cuối mỗi lab.
> ⚙️ Yêu cầu chung: đã cấu hình `AWS CLI v2` (xem Lab 1.1 tuần 1) + IAM đủ quyền cho dịch vụ trong lab.
> Về [plan tuần](README.md) · [Câu hỏi luyện tập](questions.md) · [Kế hoạch tổng](../../DVA-C02-STUDY-PLAN.md)

---

## 🔧 Chuẩn bị chung (làm 1 lần, dùng cho mọi lab)

```bash
# 1) Đặt region (đổi theo bạn — ví dụ us-east-1 hoặc us-east-1)
export AWS_REGION=us-east-1
export AWS_DEFAULT_REGION=$AWS_REGION

# 2) Lấy Account ID để dựng ARN
export ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "Account: $ACCOUNT_ID · Region: $AWS_REGION"
```

> 🧠 **Bản đồ trigger `Lambda`** (ôn lại — tuần này dùng `EventBridge` + `API Gateway`):
> - `EventBridge` (rule/schedule) → `Lambda`: **async push** → phải `lambda add-permission` principal `events.amazonaws.com`.
> - `API Gateway` → `Lambda`: **sync** (proxy `AWS_PROXY`) → `lambda add-permission` principal `apigateway.amazonaws.com`.
> - **`EventBridge` Scheduler** thì KHÁC: không cần resource policy — Scheduler **assume một IAM role** để gọi target.
> - `Kinesis`/`DynamoDB Streams` → `Lambda`: **event source mapping (poll)** → metric **`IteratorAge`** đo độ trễ (gặp lại ở Lab 9.5).

> 🧠 **Câu thần chú Domain 4:** *hiệu năng/log → `CloudWatch`; **ai gọi API gì, khi nào → `CloudTrail`**.*

---

## Lab 9.1 — `X-Ray` active tracing cho `Lambda` + `API Gateway` ⭐
**🎯 Mục tiêu:** Bật **active tracing**, instrument code bằng `aws-xray-sdk-core`, thêm **annotation** (index → filter được) và **metadata** (không index), xem **service map** `API GW → Lambda → STS` và **filter trace theo annotation** ngay bằng CLI.
**🧩 Luyện kỹ năng (liên quan đề):**
- Câu bẫy số 1 của tuần: **annotation vs metadata** — chỉ annotation mới filter/query được.
- Bật `X-Ray` cho `Lambda` = **active tracing** (`--tracing-config Mode=Active`) + role có `AWSXRayDaemonWriteAccess`.
- `captureAWSv3Client()` bọc client SDK v3 → tự tạo **subsegment downstream** (hiện node trên service map).
- Tích hợp sync `API Gateway (REST) → Lambda` (proxy `AWS_PROXY`) + tracing trên **stage**.

**⏱️ ~40 phút** · **Yêu cầu trước:** Chuẩn bị chung; có `node` 24 + `npm`.

### Các bước
1. Tạo execution role (basic logs + quyền ghi `X-Ray`).
   ```bash
   cat > trust-lambda.json <<'EOF'
   { "Version":"2012-10-17","Statement":[{"Effect":"Allow",
     "Principal":{"Service":"lambda.amazonaws.com"},"Action":"sts:AssumeRole"}] }
   EOF
   aws iam create-role --role-name lab9-xray-role \
     --assume-role-policy-document file://trust-lambda.json
   aws iam attach-role-policy --role-name lab9-xray-role \
     --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
   aws iam attach-role-policy --role-name lab9-xray-role \
     --policy-arn arn:aws:iam::aws:policy/AWSXRayDaemonWriteAccess
   ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/lab9-xray-role"
   ```

2. Viết handler có annotation + metadata + 1 lời gọi downstream (STS) để service map có node.
   ```javascript
   // index.mjs
   import AWSXRay from "aws-xray-sdk-core";
   import { STSClient, GetCallerIdentityCommand } from "@aws-sdk/client-sts";

   // captureAWSv3Client bọc client -> tạo subsegment downstream (STS) trên service map
   const sts = AWSXRay.captureAWSv3Client(new STSClient({}));

   export const handler = async (event) => {
     const qs = event.queryStringParameters || {};
     const orderType = qs.orderType || "STANDARD";

     const seg = AWSXRay.getSegment();                 // facade segment do active tracing tạo
     const sub = seg.addNewSubsegment("processOrder");
     sub.addAnnotation("orderType", orderType);        // ✅ INDEXED -> filter được
     sub.addMetadata("rawEvent", event);               // ❌ KHÔNG index -> không filter được
     const { Account } = await sts.send(new GetCallerIdentityCommand({})); // -> node STS trên service map
     sub.close();

     return {
       statusCode: 200,
       body: JSON.stringify({ orderType, account: Account }),
     };
   };
   ```

3. Đóng gói kèm thư viện `aws-xray-sdk-core` rồi tạo function **bật active tracing**.
   > ⚠️ Runtime `nodejs24.x` đã bundle sẵn `@aws-sdk/client-*`, nhưng **`aws-xray-sdk-core` KHÔNG được bundle** → phải `npm install` và đóng gói kèm `node_modules` vào zip.
   ```bash
   mkdir -p build && cp index.mjs build/
   (cd build && npm init -y >/dev/null && npm install aws-xray-sdk-core >/dev/null)
   (cd build && zip -qr ../xray-fn.zip .)   # zip gồm index.mjs + node_modules

   aws lambda create-function --function-name lab9-xray-fn \
     --runtime nodejs24.x --handler index.handler \
     --role "$ROLE_ARN" --zip-file fileb://xray-fn.zip --timeout 15 \
     --tracing-config Mode=Active
   aws lambda wait function-active-v2 --function-name lab9-xray-fn
   FN_ARN=$(aws lambda get-function --function-name lab9-xray-fn \
     --query Configuration.FunctionArn --output text)
   ```

4. Tạo **REST API** (v1 — bản hỗ trợ X-Ray tracing trên stage), resource `/order`, method GET, integration proxy tới `Lambda`.
   ```bash
   API_ID=$(aws apigateway create-rest-api --name lab9-orders-api \
     --query id --output text)
   ROOT_ID=$(aws apigateway get-resources --rest-api-id "$API_ID" \
     --query 'items[0].id' --output text)
   RES_ID=$(aws apigateway create-resource --rest-api-id "$API_ID" \
     --parent-id "$ROOT_ID" --path-part order --query id --output text)

   aws apigateway put-method --rest-api-id "$API_ID" --resource-id "$RES_ID" \
     --http-method GET --authorization-type NONE

   aws apigateway put-integration --rest-api-id "$API_ID" --resource-id "$RES_ID" \
     --http-method GET --type AWS_PROXY --integration-http-method POST \
     --uri "arn:aws:apigateway:${AWS_REGION}:lambda:path/2015-03-31/functions/${FN_ARN}/invocations"

   # Cho API Gateway quyền gọi Lambda (resource-based policy, principal apigateway)
   aws lambda add-permission --function-name lab9-xray-fn \
     --statement-id apigw-invoke --action lambda:InvokeFunction \
     --principal apigateway.amazonaws.com \
     --source-arn "arn:aws:execute-api:${AWS_REGION}:${ACCOUNT_ID}:${API_ID}/*/*/order"
   ```

5. Deploy stage `prod` rồi **bật X-Ray tracing trên stage**.
   ```bash
   aws apigateway create-deployment --rest-api-id "$API_ID" --stage-name prod
   aws apigateway update-stage --rest-api-id "$API_ID" --stage-name prod \
     --patch-operations op=replace,path=/tracingEnabled,value=true
   INVOKE_URL="https://${API_ID}.execute-api.${AWS_REGION}.amazonaws.com/prod/order"
   echo "$INVOKE_URL"
   ```

6. Gọi API vài lần với `orderType` khác nhau để sinh trace.
   ```bash
   for t in PREMIUM STANDARD PREMIUM STANDARD PREMIUM; do
     curl -s "${INVOKE_URL}?orderType=${t}" ; echo
   done
   ```

### ✅ Kiểm chứng
- **Filter theo annotation bằng CLI** (chứng minh annotation ĐƯỢC index). Chờ ~1–2 phút cho trace lên:
  ```bash
  END=$(date -u +%s); START=$((END-600))
  aws xray get-trace-summaries --start-time $START --end-time $END \
    --filter-expression 'annotation.orderType = "PREMIUM"' \
    --query 'length(TraceSummaries)'
  ```
  → trả về số trace `PREMIUM` (>0). Đổi `"STANDARD"` sẽ ra tập khác. **KHÔNG có** cú pháp `metadata.` để filter → đó là điểm thi.
- **Console:** mở `CloudWatch → X-Ray traces → Service map` thấy sơ đồ **client → lab9-orders-api → lab9-xray-fn → STS**. Vào **Traces**, gõ filter `annotation.orderType = "PREMIUM"` → lọc đúng; mở 1 trace → thấy `metadata.rawEvent` hiển thị nhưng **không dùng filter được**.

### 🧹 Dọn dẹp (tránh tính phí)
```bash
aws apigateway delete-rest-api --rest-api-id "$API_ID"
aws lambda delete-function --function-name lab9-xray-fn
aws iam detach-role-policy --role-name lab9-xray-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
aws iam detach-role-policy --role-name lab9-xray-role \
  --policy-arn arn:aws:iam::aws:policy/AWSXRayDaemonWriteAccess
aws iam delete-role --role-name lab9-xray-role
rm -rf build xray-fn.zip index.mjs trust-lambda.json
```

### 🧠 Ý nghĩa với đề thi
- Bật `X-Ray` cho `Lambda` = **active tracing**; role cần `AWSXRayDaemonWriteAccess`. `X-Ray` daemon nghe **UDP cổng 2000**.
- **ANNOTATIONS** = key-value **được index** → filter/query trace (tối đa **50/trace**). **METADATA** = **không index**, chỉ để tham khảo. Thấy "muốn tìm/lọc trace theo giá trị" → **annotation**.
- Service không tự gửi segment (STS/DynamoDB…) → `X-Ray` tạo **inferred segment** từ subsegment của client.
- `X-Ray` giờ hợp nhất dưới **`CloudWatch`** console (từ 11/2024) — khái niệm segment/subsegment/sampling vẫn nguyên; sampling mặc định = **request đầu mỗi giây + 5%** còn lại.

---

## Lab 9.2 — Custom metric: `PutMetricData` (AWS SDK v3) + EMF từ log `Lambda`
**🎯 Mục tiêu:** Đẩy số liệu app tùy chỉnh vào `CloudWatch` bằng **2 cách**: gọi trực tiếp API **`PutMetricData`** (high-resolution + dimension), và ghi log **EMF (Embedded Metric Format)** từ `Lambda` để `CloudWatch` **tự trích metric từ log** (không gọi API riêng).
**🧩 Luyện kỹ năng (liên quan đề):**
- `PutMetricData`: namespace + dimension + **StorageResolution=1** (high-resolution tới 1 giây).
- EMF: cấu trúc `_aws.CloudWatchMetrics` trong log → hợp với `Lambda` ("log ra là có metric").
- Mỗi tổ hợp dimension = **một metric riêng**; không có default namespace.

**⏱️ ~20 phút** · **Yêu cầu trước:** Chuẩn bị chung; có `node` 24 + `npm` (cho script chạy local).

### Các bước
1. **Cách A — `PutMetricData` trực tiếp** (one-liner nhanh):
   ```bash
   aws cloudwatch put-metric-data --namespace "MyApp" \
     --metric-name OrdersProcessed --value 1 --unit Count
   ```
   Bản đầy đủ (dimension + high-resolution) bằng **AWS SDK v3** — đây là **script chạy local**, nên cần cài SDK:
   ```bash
   npm init -y >/dev/null && npm install @aws-sdk/client-cloudwatch >/dev/null
   ```
   ```javascript
   // push_metric.mjs
   import { CloudWatchClient, PutMetricDataCommand } from "@aws-sdk/client-cloudwatch";
   const cw = new CloudWatchClient({ region: "us-east-1" });

   for (let i = 0; i < 5; i++) {
     await cw.send(new PutMetricDataCommand({
       Namespace: "MyApp",
       MetricData: [{
         MetricName: "OrdersProcessed",
         Dimensions: [{ Name: "Environment", Value: "prod" }],
         Value: Math.floor(Math.random() * 10) + 1,
         Unit: "Count",
         StorageResolution: 1,     // high-resolution (hạt 1 giây)
       }],
     }));
     await new Promise((r) => setTimeout(r, 1000));
   }
   console.log("Đã đẩy 5 điểm dữ liệu high-resolution vào MyApp/OrdersProcessed");
   ```
   ```bash
   node push_metric.mjs
   ```

2. **Cách B — EMF từ `Lambda`.** Tạo role cơ bản + function ghi log EMF (không gọi `PutMetricData`).
   ```bash
   cat > trust-lambda.json <<'EOF'
   { "Version":"2012-10-17","Statement":[{"Effect":"Allow",
     "Principal":{"Service":"lambda.amazonaws.com"},"Action":"sts:AssumeRole"}] }
   EOF
   aws iam create-role --role-name lab9-emf-role \
     --assume-role-policy-document file://trust-lambda.json
   aws iam attach-role-policy --role-name lab9-emf-role \
     --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
   EMF_ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/lab9-emf-role"
   ```
   ```javascript
   // index.mjs
   export const handler = async (event, context) => {
     const emf = {
       _aws: {
         Timestamp: Date.now(),
         CloudWatchMetrics: [{
           Namespace: "MyApp/EMF",
           Dimensions: [["FunctionName"]],
           Metrics: [{ Name: "OrdersProcessed", Unit: "Count" }],
         }],
       },
       FunctionName: context.functionName,                 // dimension value
       OrdersProcessed: Math.floor(Math.random() * 5) + 1, // giá trị metric
     };
     console.log(JSON.stringify(emf));   // CloudWatch tự trích metric từ dòng log này
     return { ok: true };
   };
   ```
   ```bash
   zip emf.zip index.mjs
   aws lambda create-function --function-name lab9-emf-fn \
     --runtime nodejs24.x --handler index.handler \
     --role "$EMF_ROLE_ARN" --zip-file fileb://emf.zip --timeout 10
   aws lambda wait function-active-v2 --function-name lab9-emf-fn
   for i in 1 2 3; do aws lambda invoke --function-name lab9-emf-fn /dev/null >/dev/null; done
   ```

### ✅ Kiểm chứng
- Cách A: metric xuất hiện trong namespace `MyApp`.
  ```bash
  aws cloudwatch list-metrics --namespace MyApp
  ```
- Cách B: metric `MyApp/EMF` được `CloudWatch` **tự tạo từ log** (chờ ~1–2 phút):
  ```bash
  aws cloudwatch list-metrics --namespace "MyApp/EMF"
  ```
- (Tùy chọn) Console → `CloudWatch → Metrics → MyApp` / `MyApp/EMF` → xem đồ thị.

### 🧹 Dọn dẹp
```bash
aws lambda delete-function --function-name lab9-emf-fn
aws iam detach-role-policy --role-name lab9-emf-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
aws iam delete-role --role-name lab9-emf-role
rm -f push_metric.mjs index.mjs emf.zip trust-lambda.json package.json package-lock.json
rm -rf node_modules
```
> ℹ️ Metric **không xóa được** thủ công — tự hết hạn sau **15 tháng** nếu không có data mới (không phát sinh phí lưu trữ).

### 🧠 Ý nghĩa với đề thi
- Đẩy số liệu app tùy chỉnh → **`PutMetricData`**; hoặc **EMF** để trích metric từ log (đỡ 1 API call, hợp serverless).
- **High-resolution** = `StorageResolution=1` (hạt 1 giây, giữ 3 giờ); standard = 1 phút. Mỗi `PutMetricData` đều **tính phí**.
- **Namespace bắt buộc** (không có default); dimension là một phần định danh metric → tổ hợp khác = metric khác.

---

## Lab 9.3 — Metric filter (log `ERROR`) + Alarm → `SNS` email ⭐
**🎯 Mục tiêu:** Từ **log group**, tạo **metric filter** đếm dòng chứa `ERROR` → sinh metric; gắn **alarm** trên metric đó với **action gửi email qua `SNS`**; ghi log đủ `ERROR` để đẩy alarm `OK → ALARM` và nhận mail.
**🧩 Luyện kỹ năng (liên quan đề):**
- Chuỗi tích hợp kinh điển: **Logs → metric filter → metric → alarm → `SNS`**.
- `defaultValue=0` cho metric filter → chu kỳ không match báo 0 (alarm không kẹt `INSUFFICIENT_DATA`).
- 3 trạng thái alarm; action `SNS`; alarm chỉ kích khi **đổi trạng thái**.

**⏱️ ~25 phút** · **Yêu cầu trước:** Chuẩn bị chung; có email để xác nhận subscription.

### Các bước
1. Tạo `SNS` topic + subscribe **email** (phải mở hộp thư bấm **Confirm subscription**).
   ```bash
   TOPIC_ARN=$(aws sns create-topic --name lab9-alerts --query TopicArn --output text)
   aws sns subscribe --topic-arn "$TOPIC_ARN" --protocol email \
     --notification-endpoint you@example.com   # 👉 đổi thành email của bạn
   echo "Mở email và bấm 'Confirm subscription' trước khi chạy tiếp."
   ```

2. Tạo **log group** + **log stream** cho app.
   ```bash
   aws logs create-log-group --log-group-name /lab9/app
   aws logs create-log-stream --log-group-name /lab9/app --log-stream-name s1
   ```

3. Tạo **metric filter**: pattern `"ERROR"` → metric `AppErrorCount` (namespace `MyApp`), `defaultValue=0`.
   ```bash
   aws logs put-metric-filter --log-group-name /lab9/app \
     --filter-name count-errors --filter-pattern "ERROR" \
     --metric-transformations \
       metricName=AppErrorCount,metricNamespace=MyApp,metricValue=1,defaultValue=0
   ```

4. Tạo **alarm**: `Sum(AppErrorCount) >= 3` trong 1 chu kỳ 60s → action publish `SNS`.
   ```bash
   aws cloudwatch put-metric-alarm --alarm-name lab9-too-many-errors \
     --namespace MyApp --metric-name AppErrorCount \
     --statistic Sum --period 60 --threshold 3 \
     --comparison-operator GreaterThanOrEqualToThreshold \
     --evaluation-periods 1 --treat-missing-data notBreaching \
     --alarm-actions "$TOPIC_ARN" --ok-actions "$TOPIC_ARN"
   ```

5. Ghi log chứa `ERROR` (≥3 dòng trong cùng phút) để kích alarm.
   ```bash
   TS=$(( $(date +%s) * 1000 ))
   aws logs put-log-events --log-group-name /lab9/app --log-stream-name s1 \
     --log-events \
       timestamp=$TS,message="ERROR database timeout" \
       timestamp=$TS,message="ERROR null pointer" \
       timestamp=$TS,message="ERROR disk full" \
       timestamp=$TS,message="INFO request handled ok"
   ```

### ✅ Kiểm chứng
- Theo dõi alarm chuyển sang `ALARM` (chờ ~1–3 phút cho metric filter + alarm đánh giá):
  ```bash
  aws cloudwatch describe-alarms --alarm-names lab9-too-many-errors \
    --query 'MetricAlarms[0].StateValue'
  ```
  → `"ALARM"`, và bạn nhận **email cảnh báo** từ `SNS`.
- Muốn test action **không cần chờ log**, ép trạng thái thủ công (chỉ tồn tại tới lần đánh giá kế tiếp):
  ```bash
  aws cloudwatch set-alarm-state --alarm-name lab9-too-many-errors \
    --state-value ALARM --state-reason "manual test"
  ```

### 🧹 Dọn dẹp
```bash
aws cloudwatch delete-alarms --alarm-names lab9-too-many-errors
aws logs delete-metric-filter --log-group-name /lab9/app --filter-name count-errors
aws logs delete-log-group --log-group-name /lab9/app
aws sns delete-topic --topic-arn "$TOPIC_ARN"
```

### 🧠 Ý nghĩa với đề thi
- **Metric filter** = tạo metric từ **pattern trong log** (không đổi code app). Đừng nhầm với **subscription filter** = **stream log** real-time tới `Lambda`/`Kinesis`/`Firehose`.
- Alarm 3 trạng thái **`OK` / `ALARM` / `INSUFFICIENT_DATA`**; action: `SNS` / Auto Scaling / EC2. Alarm **chỉ kích khi đổi trạng thái** và duy trì đủ số period.
- Có thể tạo alarm cho **custom metric trước khi metric tồn tại** (phải khai đủ namespace + name + dimension).

---

## Lab 9.4 — `EventBridge`: rule schedule → `Lambda` + Scheduler one-time (timezone) ⭐
**🎯 Mục tiêu:** Chạy `Lambda` **định kỳ** bằng `EventBridge` **rule schedule** (`rate`/`cron`), và tạo lịch **one-time có timezone** bằng **`EventBridge` Scheduler** — thấy rõ khác biệt: rule cần **resource policy**, Scheduler cần **IAM role**.
**🧩 Luyện kỹ năng (liên quan đề):**
- "Chạy `Lambda`/task theo lịch" → `EventBridge` schedule (`cron`/`rate`), KHÔNG tự viết cron trong `Lambda`.
- Rule → `Lambda` = **async push** → `lambda add-permission` principal `events.amazonaws.com`.
- **Scheduler** = one-time/recurring, **timezone**, flexible time window, không cần event bus, **assume role** để gọi target.

**⏱️ ~25 phút** · **Yêu cầu trước:** Chuẩn bị chung.

### Các bước
1. Tạo role cơ bản + function "tick" (chỉ log timestamp).
   ```bash
   cat > trust-lambda.json <<'EOF'
   { "Version":"2012-10-17","Statement":[{"Effect":"Allow",
     "Principal":{"Service":"lambda.amazonaws.com"},"Action":"sts:AssumeRole"}] }
   EOF
   aws iam create-role --role-name lab9-tick-role \
     --assume-role-policy-document file://trust-lambda.json
   aws iam attach-role-policy --role-name lab9-tick-role \
     --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
   TICK_ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/lab9-tick-role"
   ```
   ```javascript
   // index.mjs
   export const handler = async (event) => {
     console.log(`[TICK] chạy lúc ${new Date().toISOString()} source=${event.source ?? "manual"}`);
     return { ok: true };
   };
   ```
   ```bash
   zip tick.zip index.mjs
   aws lambda create-function --function-name lab9-tick-fn \
     --runtime nodejs24.x --handler index.handler \
     --role "$TICK_ROLE_ARN" --zip-file fileb://tick.zip --timeout 10
   aws lambda wait function-active-v2 --function-name lab9-tick-fn
   FN_ARN=$(aws lambda get-function --function-name lab9-tick-fn \
     --query Configuration.FunctionArn --output text)
   ```

2. **Phần A — `EventBridge` rule schedule.** Tạo rule `rate(1 minute)` (test nhanh) + target `Lambda` + permission.
   ```bash
   aws events put-rule --name lab9-every-min \
     --schedule-expression "rate(1 minute)"        # cron ví dụ: "cron(0 12 * * ? *)" = 12:00 UTC mỗi ngày
   RULE_ARN=$(aws events describe-rule --name lab9-every-min --query Arn --output text)

   aws lambda add-permission --function-name lab9-tick-fn \
     --statement-id eb-rule-invoke --action lambda:InvokeFunction \
     --principal events.amazonaws.com --source-arn "$RULE_ARN"

   aws events put-targets --rule lab9-every-min \
     --targets "Id"="1","Arn"="$FN_ARN"
   ```

3. **Phần B — `EventBridge` Scheduler one-time (timezone).** Tạo role cho Scheduler **assume** để gọi `Lambda`.
   ```bash
   cat > trust-scheduler.json <<'EOF'
   { "Version":"2012-10-17","Statement":[{"Effect":"Allow",
     "Principal":{"Service":"scheduler.amazonaws.com"},"Action":"sts:AssumeRole"}] }
   EOF
   aws iam create-role --role-name lab9-scheduler-role \
     --assume-role-policy-document file://trust-scheduler.json
   aws iam put-role-policy --role-name lab9-scheduler-role --policy-name invoke-tick \
     --policy-document "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Action\":\"lambda:InvokeFunction\",\"Resource\":\"$FN_ARN\"}]}"
   SCHED_ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/lab9-scheduler-role"
   ```
   Đặt giờ chạy ~3 phút tới, hiểu theo múi giờ `Asia/Ho_Chi_Minh`:
   ```bash
   AT=$(TZ=Asia/Ho_Chi_Minh date -v+3M +%Y-%m-%dT%H:%M:%S 2>/dev/null \
        || TZ=Asia/Ho_Chi_Minh date -d '+3 minutes' +%Y-%m-%dT%H:%M:%S)   # macOS || Linux
   echo "Scheduler sẽ chạy lúc $AT (Asia/Ho_Chi_Minh)"

   aws scheduler create-schedule --name lab9-once \
     --schedule-expression "at(${AT})" \
     --schedule-expression-timezone "Asia/Ho_Chi_Minh" \
     --flexible-time-window '{"Mode":"OFF"}' \
     --target "{\"Arn\":\"$FN_ARN\",\"RoleArn\":\"$SCHED_ROLE_ARN\"}"
   ```

### ✅ Kiểm chứng
- Rule chạy mỗi phút → log có nhiều dòng `[TICK] ... source=aws.events`:
  ```bash
  aws logs tail /aws/lambda/lab9-tick-fn --since 5m --follow
  ```
- Scheduler one-time: đúng giờ `$AT` sẽ có **1 lần** invoke thêm. Kiểm tra lịch còn/đã chạy:
  ```bash
  aws scheduler get-schedule --name lab9-once --query 'State'
  ```
  > ⚠️ Nhớ **tắt/xóa rule** sớm để không bị gọi mỗi phút mãi (Free Tier vẫn nên dọn).

### 🧹 Dọn dẹp
```bash
aws events remove-targets --rule lab9-every-min --ids 1
aws events delete-rule --name lab9-every-min
aws scheduler delete-schedule --name lab9-once
aws lambda delete-function --function-name lab9-tick-fn
aws iam delete-role-policy --role-name lab9-scheduler-role --policy-name invoke-tick
aws iam delete-role --role-name lab9-scheduler-role
aws iam detach-role-policy --role-name lab9-tick-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
aws iam delete-role --role-name lab9-tick-role
rm -f index.mjs tick.zip trust-lambda.json trust-scheduler.json
```

### 🧠 Ý nghĩa với đề thi
- "Chạy job theo lịch" → **`EventBridge` schedule (`cron`/`rate`)**, không tự cron trong app/`Lambda`.
- **Rule (schedule)** gắn event bus + cần **resource policy** (`add-permission` principal `events.amazonaws.com`). **Scheduler** không cần event bus, dùng **IAM role**, hỗ trợ **timezone / one-time / flexible time window / 270+ service**.
- Phản xạ: "**lịch có timezone / one-time quy mô lớn**" → **`EventBridge` Scheduler**.

---

## Lab 9.5 — Troubleshoot: `Throttles` / `Errors` / `IteratorAge` + Logs Insights + `CloudTrail`
**🎯 Mục tiêu:** Cố ý gây **lỗi** và **throttling** cho `Lambda`, đọc metric mặc định (`Errors`, `Throttles`), truy vấn log bằng **CloudWatch Logs Insights**, và dùng **`CloudTrail`** để biết **ai đã gọi API** thay đổi cấu hình.
**🧩 Luyện kỹ năng (liên quan đề):**
- Đọc metric `Lambda`: `Errors` (lỗi code) vs `Throttles` (vượt concurrency — KHÔNG tính vào `Errors`).
- `IteratorAge` = độ trễ xử lý **stream** (`Kinesis`/`DynamoDB Streams`).
- Logs Insights query; `CloudTrail lookup-events` = "ai gọi API gì, khi nào".

**⏱️ ~25 phút** · **Yêu cầu trước:** Chuẩn bị chung.

### Các bước
1. Tạo role + function "flaky" — ném lỗi khi input có `fail`.
   ```bash
   cat > trust-lambda.json <<'EOF'
   { "Version":"2012-10-17","Statement":[{"Effect":"Allow",
     "Principal":{"Service":"lambda.amazonaws.com"},"Action":"sts:AssumeRole"}] }
   EOF
   aws iam create-role --role-name lab9-flaky-role \
     --assume-role-policy-document file://trust-lambda.json
   aws iam attach-role-policy --role-name lab9-flaky-role \
     --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
   FLAKY_ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/lab9-flaky-role"
   ```
   ```javascript
   // index.mjs
   export const handler = async (event) => {
     if (event.fail) {
       throw new Error("ERROR: downstream dependency failed");  // -> metric Errors + stack trace trong log
     }
     return { ok: true };
   };
   ```
   ```bash
   zip flaky.zip index.mjs
   aws lambda create-function --function-name lab9-flaky-fn \
     --runtime nodejs24.x --handler index.handler \
     --role "$FLAKY_ROLE_ARN" --zip-file fileb://flaky.zip --timeout 10
   aws lambda wait function-active-v2 --function-name lab9-flaky-fn
   ```

2. **Gây `Errors`:** invoke với `{"fail": true}` vài lần.
   ```bash
   for i in 1 2 3; do
     aws lambda invoke --function-name lab9-flaky-fn \
       --payload '{"fail":true}' --cli-binary-format raw-in-base64-out /dev/null
   done
   ```

3. **Gây `Throttles`:** đặt reserved concurrency = 0 rồi invoke → mọi lần gọi bị throttle.
   ```bash
   aws lambda put-function-concurrency --function-name lab9-flaky-fn \
     --reserved-concurrent-executions 0
   for i in 1 2 3; do
     aws lambda invoke --function-name lab9-flaky-fn --payload '{}' \
       --cli-binary-format raw-in-base64-out /dev/null || echo "throttled (429/TooManyRequests)"
   done
   aws lambda delete-function-concurrency --function-name lab9-flaky-fn   # bỏ giới hạn
   ```

### ✅ Kiểm chứng
- **Metric `Errors` & `Throttles`** (namespace `AWS/Lambda`, chờ ~1–2 phút):
  ```bash
  END=$(date -u +%Y-%m-%dT%H:%M:%SZ); START=$(TZ=UTC date -v-15M +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u -d '-15 min' +%Y-%m-%dT%H:%M:%SZ)
  for M in Errors Throttles; do
    echo "== $M =="
    aws cloudwatch get-metric-statistics --namespace AWS/Lambda --metric-name $M \
      --dimensions Name=FunctionName,Value=lab9-flaky-fn \
      --start-time $START --end-time $END --period 60 --statistics Sum \
      --query 'Datapoints[].[Timestamp,Sum]' --output text
  done
  ```
- **CloudWatch Logs Insights** — đếm/lọc dòng lỗi:
  ```bash
  QID=$(aws logs start-query --log-group-name /aws/lambda/lab9-flaky-fn \
    --start-time $(( $(date +%s) - 900 )) --end-time $(date +%s) \
    --query-string 'fields @timestamp, @message | filter @message like /ERROR/ | sort @timestamp desc | limit 20' \
    --query queryId --output text)
  sleep 5
  aws logs get-query-results --query-id "$QID" --query 'results'
  ```
- **`CloudTrail` — ai đã gọi API?** (vd ai đặt reserved concurrency):
  ```bash
  aws cloudtrail lookup-events \
    --lookup-attributes AttributeKey=EventName,AttributeValue=PutFunctionConcurrency \
    --max-results 5 \
    --query 'Events[].{Time:EventTime,User:Username,Event:EventName}'
  ```
  → thấy **ai (Username), khi nào (EventTime)** gọi `PutFunctionConcurrency`. Đây là việc `CloudWatch` **không** làm được.
- **`IteratorAge` (concept):** chỉ có với event source **stream**. Nếu đã làm Lab 5.4 (`Kinesis`→`Lambda`), quan sát bằng:
  ```bash
  aws cloudwatch get-metric-statistics --namespace AWS/Lambda --metric-name IteratorAge \
    --dimensions Name=FunctionName,Value=<kinesis-consumer> \
    --start-time $START --end-time $END --period 60 --statistics Maximum
  ```
  `IteratorAge` cao = consumer **tụt hậu** so với tốc độ ghi stream → tăng batch/parallelization hoặc số shard.

### 🧹 Dọn dẹp
```bash
aws lambda delete-function --function-name lab9-flaky-fn
aws iam detach-role-policy --role-name lab9-flaky-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
aws iam delete-role --role-name lab9-flaky-role
rm -f index.mjs flaky.zip trust-lambda.json
```

### 🧠 Ý nghĩa với đề thi
- **`Errors`** = lỗi code/timeout; **`Throttles`** = vượt concurrency limit (**429 / TooManyRequests**), KHÔNG tính vào `Errors`. Lỗi `429` = **client throttling** → **retry exponential backoff + jitter**.
- **`IteratorAge`** cao (stream) = xử lý chậm/tụt hậu; cold start nhiều → **Provisioned Concurrency**; `Duration` cao → tăng **memory** (CPU tăng theo tỉ lệ, dùng **Lambda Power Tuning**).
- **`CloudWatch` vs `CloudTrail`:** metric/log/hiệu năng → `CloudWatch`; **ai gọi API gì, khi nào, từ đâu → `CloudTrail`** (Event history giữ **90 ngày** management events, miễn phí).
- **Logs Insights** = query nhanh để tổng hợp/lọc log khi điều tra sự cố.

---

> ✅ Xong 5 lab? Đối chiếu lại [Lab checklist trong README](README.md#-lab-checklist), rồi bước vào phần lớn nhất tuần này: **⭐⭐ FULL MOCK #1 — 65 câu / 130 phút** ([questions.md](questions.md) · [answers.md](answers.md)) và **review 100% câu sai** để KẾT THÚC Domain 4.
