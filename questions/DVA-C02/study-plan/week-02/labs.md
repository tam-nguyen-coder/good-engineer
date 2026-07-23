# 🧪 Hands-on Labs — Tuần 2: `Lambda` nâng cao (versions, aliases, layers, concurrency, event sources)

> Lab cầm tay chỉ việc, chạy được trên tài khoản AWS thật (Free Tier). LUÔN chạy phần Dọn dẹp cuối mỗi lab.
> ⚙️ Yêu cầu chung: đã cấu hình `AWS CLI v2` (xem Lab 1.1 tuần 1) + IAM đủ quyền cho dịch vụ trong lab.
> Về [plan tuần](README.md) · [Câu hỏi luyện tập](questions.md) · [Kế hoạch tổng](../../DVA-C02-STUDY-PLAN.md)

---

## 🔧 Chuẩn bị chung (làm 1 lần) — tạo execution role + function `myFn`

Các lab 2.1–2.3 dùng chung function `myFn`; lab 2.4–2.6 tạo function riêng nhưng **dùng lại role** này (có bổ sung quyền khi cần).

**1. Đặt biến môi trường (nhớ chọn Region gần bạn):**
```bash
export AWS_REGION=us-east-1
export ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "Account=$ACCOUNT_ID Region=$AWS_REGION"
```

**2. Tạo execution role cơ bản (ghi được CloudWatch Logs):**
```bash
aws iam create-role --role-name dva-lambda-role \
  --assume-role-policy-document '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"lambda.amazonaws.com"},"Action":"sts:AssumeRole"}]}'

aws iam attach-role-policy --role-name dva-lambda-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

export ROLE_ARN=arn:aws:iam::${ACCOUNT_ID}:role/dva-lambda-role
# đợi ~10s cho role kịp propagate trước khi tạo function
```

**3. Viết handler & tạo function `myFn`:**
```python
# handler.py — base function
import json, os

def handler(event, context):
    print("Received event:", json.dumps(event))
    version = os.environ.get("APP_VERSION", "v1")
    return {"statusCode": 200, "version": version}
```
```bash
zip function.zip handler.py
aws lambda create-function --function-name myFn \
  --runtime python3.12 --handler handler.handler \
  --role ${ROLE_ARN} \
  --zip-file fileb://function.zip \
  --timeout 10 --environment 'Variables={APP_VERSION=v1}'
```

> ✅ Kiểm tra nhanh: `aws lambda invoke --function-name myFn --cli-binary-format raw-in-base64-out --payload '{"hello":"world"}' out.json && cat out.json`

---

## Lab 2.1 — Publish version + tạo alias + weighted alias (canary 90/10)
**🎯 Mục tiêu:** Publish 2 version bất biến của `myFn`, tạo alias `prod`, rồi cấu hình routing canary chia 90% traffic sang v1 và 10% sang v2 — tất cả qua CLI.
**🧩 Luyện kỹ năng (liên quan đề):**
- "immutable snapshot của code" → publish **version** (có ARN riêng theo số).
- "con trỏ đổi version mà client không đổi ARN" → **alias**.
- "canary / chia 10% traffic sang bản mới" → **weighted alias** giữa **đúng 2 version**.
**⏱️ ~20 phút** · **Yêu cầu trước:** đã làm phần Chuẩn bị chung (có `myFn`).

### Các bước
1. Publish **version 1** từ `$LATEST` và xem ARN có số version:
   ```bash
   aws lambda publish-version --function-name myFn --description "v1 stable" \
     --query '{Version:Version, Arn:FunctionArn}'
   # -> Arn kết thúc bằng :myFn:1  (qualified ARN, bất biến)
   ```
2. Tạo alias `prod` trỏ tới **version 1**:
   ```bash
   aws lambda create-alias --function-name myFn --name prod --function-version 1
   ```
3. Đổi code (→ `$LATEST` khác v1) rồi publish **version 2**:
   ```bash
   # đổi biến để $LATEST khác v1 (đủ điều kiện publish version mới)
   aws lambda update-function-configuration --function-name myFn \
     --environment 'Variables={APP_VERSION=v2}'
   aws lambda wait function-updated --function-name myFn
   aws lambda publish-version --function-name myFn --description "v2 canary" \
     --query 'Version'   # -> "2"
   ```
4. Cấu hình **weighted alias**: `prod` giữ 90% ở v1, đẩy **10%** sang v2:
   ```bash
   aws lambda update-alias --function-name myFn --name prod \
     --function-version 1 \
     --routing-config '{"AdditionalVersionWeights":{"2":0.10}}'
   ```
5. Gọi qua alias `prod` nhiều lần để thấy canary phân bổ:
   ```bash
   for i in $(seq 1 20); do
     aws lambda invoke --function-name myFn --qualifier prod \
       --cli-binary-format raw-in-base64-out --payload '{}' o.json >/dev/null
     cat o.json | python3 -c 'import sys,json;print(json.load(sys.stdin)["version"])'
   done
   # ~18 dòng "v1", ~2 dòng "v2"
   ```

### ✅ Kiểm chứng
- `aws lambda get-alias --function-name myFn --name prod` → thấy `FunctionVersion:"1"` và `RoutingConfig.AdditionalVersionWeights` = `{"2":0.1}`.
- Vòng lặp invoke trả về hỗn hợp `v1`/`v2` xấp xỉ 90/10.

### 🧹 Dọn dẹp
```bash
# giữ myFn cho các lab sau; chỉ gỡ routing canary (không bắt buộc)
aws lambda update-alias --function-name myFn --name prod --function-version 1 --routing-config '{}'
```

### 🧠 Ý nghĩa với đề thi
- Version = **bất biến**, có **ARN theo số**; `$LATEST` mutable. **Không tạo alias từ unqualified ARN**.
- Weighted alias chỉ chia giữa **2 version** → mô hình chuẩn cho **canary/blue-green**, KHÔNG deploy 2 function.
- Alias **chỉ trỏ tới version**, không trỏ alias→alias (bẫy hay gặp).

---

## Lab 2.2 — Tạo & gắn Lambda layer (đóng gói dependency dùng chung)
**🎯 Mục tiêu:** Đóng gói một dependency Python (`requests`) vào `layer`, publish layer version, gắn vào `myFn`, và dùng thư viện đó trong handler.
**🧩 Luyện kỹ năng (liên quan đề):**
- "chia sẻ dependency giữa nhiều function / giảm dung lượng package" → **Layer**.
- Cấu trúc thư mục `python/` → Lambda giải nén vào `/opt`; runtime tự thấy trong `sys.path`.
- Giới hạn: **≤ 5 layer/function**; tổng giải nén (function + layers) **≤ 250 MB**; layer version **bất biến**.
**⏱️ ~20 phút** · **Yêu cầu trước:** có `myFn`; máy có `pip`.

### Các bước
1. Đóng gói dependency đúng cấu trúc `python/` (Lambda mount vào `/opt/python`):
   ```bash
   rm -rf layer && mkdir -p layer/python
   pip install requests -t layer/python
   (cd layer && zip -r ../layer.zip python >/dev/null)
   ```
2. Publish layer version (chỉ định runtime tương thích):
   ```bash
   LAYER_ARN=$(aws lambda publish-layer-version --layer-name my-deps \
     --description "requests lib" \
     --zip-file fileb://layer.zip \
     --compatible-runtimes python3.12 \
     --query 'LayerVersionArn' --output text)
   echo "$LAYER_ARN"   # -> ...:layer:my-deps:1 (phải chỉ định CHÍNH XÁC version)
   ```
3. Gắn layer vào `myFn`:
   ```bash
   aws lambda update-function-configuration --function-name myFn --layers "$LAYER_ARN"
   aws lambda wait function-updated --function-name myFn
   ```
4. Cập nhật handler để `import requests` (thư viện đến TỪ layer, không nằm trong package):
   ```python
   # handler.py — dùng dependency từ layer
   import json, requests   # 'requests' được cấp bởi layer ở /opt/python

   def handler(event, context):
       print("requests version:", requests.__version__)
       return {"ok": True, "requests_version": requests.__version__}
   ```
   ```bash
   zip function.zip handler.py
   aws lambda update-function-code --function-name myFn --zip-file fileb://function.zip
   aws lambda wait function-updated --function-name myFn
   ```

### ✅ Kiểm chứng
- `aws lambda invoke --function-name myFn --cli-binary-format raw-in-base64-out --payload '{}' out.json && cat out.json` → thấy `requests_version` (nếu quên gắn layer sẽ báo `No module named 'requests'`).
- `aws lambda get-function-configuration --function-name myFn --query 'Layers'` → liệt kê layer ARN đã gắn.

### 🧹 Dọn dẹp
```bash
aws lambda update-function-configuration --function-name myFn --layers   # gỡ layer (list rỗng)
aws lambda delete-layer-version --layer-name my-deps --version-number 1
```

### 🧠 Ý nghĩa với đề thi
- Layer để **tái sử dụng dependency** giữa nhiều function & giảm package; content được đưa vào **`/opt`**.
- Layer chỉ dùng cho function dạng **.zip** (container image thì gói thẳng vào image).
- Phải trỏ **đúng layer version ARN** (immutable) — không có khái niệm "layer version mới nhất tự động".

---

## Lab 2.3 — Reserved vs provisioned concurrency (set + quan sát) & mô phỏng throttle
**🎯 Mục tiêu:** Set **reserved concurrency** để chủ ý throttle `myFn` và quan sát `TooManyRequestsException`; set **provisioned concurrency** trên alias `prod` để giữ môi trường ấm.
**🧩 Luyện kỹ năng (liên quan đề):**
- "đảm bảo slot riêng / giới hạn function ngốn hết pool" → **reserved concurrency** (trần + sàn, không phí).
- "loại bỏ cold start / giữ môi trường ấm" → **provisioned concurrency** (có phí), gắn vào **alias/version**, KHÔNG `$LATEST`.
- "HTTP 429 / TooManyRequestsException" → bị **throttle** khi vượt concurrency.
**⏱️ ~15 phút** · **Yêu cầu trước:** có `myFn` và alias `prod` (Lab 2.1).

### Các bước
1. **Reserved concurrency = 0** để throttle hoàn toàn (cách chắc chắn tạo lỗi để quan sát):
   ```bash
   aws lambda put-function-concurrency --function-name myFn \
     --reserved-concurrent-executions 0
   ```
2. Gọi thử → bị chặn ngay:
   ```bash
   aws lambda invoke --function-name myFn \
     --cli-binary-format raw-in-base64-out --payload '{}' out.json
   # -> lỗi: TooManyRequestsException (HTTP 429), Reason: ReservedFunctionConcurrency
   ```
3. Nâng reserved lên **2** (đặt trần + dành riêng 2 slot cho function này, trừ khỏi pool chung):
   ```bash
   aws lambda put-function-concurrency --function-name myFn \
     --reserved-concurrent-executions 2
   aws lambda invoke --function-name myFn --cli-binary-format raw-in-base64-out \
     --payload '{}' out.json && cat out.json   # giờ chạy được
   ```
4. **Provisioned concurrency** trên alias `prod` (giữ 1 môi trường ấm → khử cold start). Trước hết **bắt buộc gỡ routing config** khỏi alias `prod`: nếu alias vẫn còn weighted routing (10% v2 từ Lab 2.1) thì lệnh set provisioned concurrency sẽ báo `InvalidParameterValueException: Alias with weights can not be used with Provisioned Concurrency`.
   ```bash
   # BẮT BUỘC trước khi set provisioned concurrency: gỡ weighted routing khỏi alias
   aws lambda update-alias --function-name myFn --name prod --routing-config '{}'

   aws lambda put-provisioned-concurrency-config --function-name myFn \
     --qualifier prod --provisioned-concurrent-executions 1
   # theo dõi tới khi READY
   aws lambda get-provisioned-concurrency-config --function-name myFn \
     --qualifier prod --query '{Status:Status, Allocated:AllocatedProvisionedConcurrentExecutions}'
   # Status: IN_PROGRESS -> READY
   ```

### ✅ Kiểm chứng
- Bước 2 in ra `TooManyRequestsException` (bằng chứng throttle do reserved=0).
- Bước 4 `Status` chuyển từ `IN_PROGRESS` sang `READY` với `Allocated: 1`.

### 🧹 Dọn dẹp
```bash
aws lambda delete-provisioned-concurrency-config --function-name myFn --qualifier prod
aws lambda delete-function-concurrency --function-name myFn   # trả concurrency về pool chung
```

### 🧠 Ý nghĩa với đề thi
- **Reserved** = trần + sàn, **không phí**; đặt = 0 để dừng hẳn function; reserve trừ vào pool chung của function khác.
- **Provisioned** = giữ sẵn môi trường ấm → khử **cold start**, **có phí**; chỉ gắn được vào **version/alias** (không `$LATEST`).
- Bẫy: "đảm bảo capacity, không nói cold start" → **reserved**; "khử cold start cho traffic ổn định" → **provisioned**.
- 🧠 **Exam fact:** **Weighted alias (routing config) và provisioned concurrency KHÔNG dùng đồng thời trên cùng 1 alias.** Phải gỡ routing (`--routing-config '{}'`) trước khi set provisioned concurrency, nếu không nhận `InvalidParameterValueException: Alias with weights can not be used with Provisioned Concurrency`.

---

## Lab 2.4 — Async invoke + DLQ + destinations (OnSuccess/OnFailure), quan sát retry 2 lần
**🎯 Mục tiêu:** Tạo function cố ý lỗi, gọi **async** (`--invocation-type Event`), quan sát Lambda **tự retry 2 lần** (tổng 3 lần thử) rồi đẩy record vào **DLQ (`SQS`)**; sau đó chuyển sang **destinations** để tách OnSuccess/OnFailure.
**🧩 Luyện kỹ năng (liên quan đề):**
- "async invoke lỗi lưu lại xử lý sau" → **DLQ** (`SQS`/`SNS`, chỉ OnFailure) hoặc **destinations OnFailure**.
- "route cả thành công lẫn thất bại" → **destinations** (`SQS`/`SNS`/`Lambda`/`EventBridge`, cả OnSuccess + OnFailure).
- Async retry **2 lần** (tổng **3 lần thử**), payload async tối đa **1 MB**.
**⏱️ ~25 phút** · **Yêu cầu trước:** đã có `ROLE_ARN`, `ACCOUNT_ID`, `AWS_REGION`.

### Các bước
1. Tạo function `async-fn` cố ý raise lỗi khi `event.fail == true`:
   ```python
   # async_handler.py
   def handler(event, context):
       print("Processing:", event)
       if event.get("fail"):
           raise Exception("intentional failure for DLQ/destination demo")
       return {"ok": True}
   ```
   ```bash
   zip async.zip async_handler.py
   aws lambda create-function --function-name async-fn \
     --runtime python3.12 --handler async_handler.handler \
     --role ${ROLE_ARN} --zip-file fileb://async.zip --timeout 10
   ```
2. Tạo 3 queue: DLQ, ok, fail; cho phép Lambda gửi (role có `AWSLambdaBasicExecutionRole` chưa đủ `sqs:SendMessage` → thêm inline policy):
   ```bash
   DLQ_URL=$(aws sqs create-queue --queue-name async-dlq --query QueueUrl --output text)
   OK_URL=$(aws sqs create-queue --queue-name async-ok --query QueueUrl --output text)
   FAIL_URL=$(aws sqs create-queue --queue-name async-fail --query QueueUrl --output text)
   DLQ_ARN=$(aws sqs get-queue-attributes --queue-url "$DLQ_URL"  --attribute-names QueueArn --query 'Attributes.QueueArn' --output text)
   OK_ARN=$(aws sqs get-queue-attributes  --queue-url "$OK_URL"   --attribute-names QueueArn --query 'Attributes.QueueArn' --output text)
   FAIL_ARN=$(aws sqs get-queue-attributes --queue-url "$FAIL_URL" --attribute-names QueueArn --query 'Attributes.QueueArn' --output text)

   aws iam put-role-policy --role-name dva-lambda-role --policy-name allow-sqs-send \
     --policy-document '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Action":"sqs:SendMessage","Resource":"*"}]}'
   ```
3. **Phần A — DLQ:** gắn DLQ, gọi async lỗi, quan sát 3 lần thử rồi vào DLQ:
   ```bash
   aws lambda update-function-configuration --function-name async-fn \
     --dead-letter-config "TargetArn=${DLQ_ARN}"
   aws lambda wait function-updated --function-name async-fn

   aws lambda invoke --function-name async-fn --invocation-type Event \
     --cli-binary-format raw-in-base64-out --payload '{"fail":true}' resp.json
   # StatusCode 202 (async trả về ngay, KHÔNG chờ code)
   # đợi retry: async retry 2 lần, có backoff -> chờ ~2-4 phút
   ```
   ```bash
   # đếm số lần thử trong log = 3 (initial + 2 retry)
   aws logs tail /aws/lambda/async-fn --since 10m | grep -c "Processing:"
   # nhận message từ DLQ
   aws sqs receive-message --queue-url "$DLQ_URL" --wait-time-seconds 10
   ```
4. **Phần B — destinations:** gỡ DLQ (để destinations không bị lẫn), set OnSuccess/OnFailure + giới hạn retry:
   > ⚠️ AWS coi **DLQ** và **on-failure destination** là hai lựa chọn thay thế; tài liệu không nêu quy tắc ưu tiên khi bật cả hai → để quan sát destinations rõ ràng thì nên GỠ DLQ trước.
   ```bash
   aws lambda update-function-configuration --function-name async-fn --dead-letter-config '{}'
   aws lambda wait function-updated --function-name async-fn

   aws lambda put-function-event-invoke-config --function-name async-fn \
     --maximum-retry-attempts 2 \
     --destination-config "{\"OnSuccess\":{\"Destination\":\"${OK_ARN}\"},\"OnFailure\":{\"Destination\":\"${FAIL_ARN}\"}}"
   ```
   ```bash
   # gọi thành công -> vào queue OK ; gọi lỗi -> vào queue FAIL
   aws lambda invoke --function-name async-fn --invocation-type Event \
     --cli-binary-format raw-in-base64-out --payload '{"fail":false}' r1.json
   aws lambda invoke --function-name async-fn --invocation-type Event \
     --cli-binary-format raw-in-base64-out --payload '{"fail":true}' r2.json
   ```

### ✅ Kiểm chứng
- Phần A: log `async-fn` có **3** dòng `Processing:` (1 gọi đầu + 2 retry); `async-dlq` nhận được message gốc.
- Phần B: sau ~1–3 phút, `async-ok` có record `responsePayload` (OnSuccess); `async-fail` có record kèm `condition:"RetriesExhausted"` (OnFailure). Kiểm tra:
  ```bash
  aws sqs receive-message --queue-url "$OK_URL"   --wait-time-seconds 10
  aws sqs receive-message --queue-url "$FAIL_URL" --wait-time-seconds 10
  ```

### 🧹 Dọn dẹp
```bash
aws lambda delete-function --function-name async-fn
for u in "$DLQ_URL" "$OK_URL" "$FAIL_URL"; do aws sqs delete-queue --queue-url "$u"; done
aws iam delete-role-policy --role-name dva-lambda-role --policy-name allow-sqs-send
```

### 🧠 Ý nghĩa với đề thi
- Async (`Event`) → Lambda trả `202` ngay, xếp vào internal queue; lỗi → **retry 2 lần** (tổng 3), hết thì vào **DLQ/OnFailure**.
- **DLQ** chỉ bắt thất bại (`SQS`/`SNS`); **destinations** hiện đại hơn: cả OnSuccess + OnFailure, nhiều metadata hơn, thêm đích `Lambda`/`EventBridge`.
- Bẫy số liệu: payload async **1 MB** (sync mới 6 MB).

---

## Lab 2.5 ⭐ — `SQS` → `Lambda` (event source mapping / poll) + partial batch response
**🎯 Mục tiêu:** Cho `Lambda` **poll** một `SQS` queue qua **event source mapping**: tạo queue, `create-event-source-mapping`, gửi message và xem function bị gọi theo batch; đặt **visibility timeout ≥ 6× function timeout** và trả **partial batch response** để chỉ message lỗi quay lại queue.
**🧩 Luyện kỹ năng (liên quan đề):**
- "`Lambda` đọc `SQS`" → **event source mapping** (Lambda POLL, KHÔNG phải trigger push).
- Role cần `sqs:ReceiveMessage/DeleteMessage/GetQueueAttributes` (managed policy `AWSLambdaSQSQueueExecutionRole`).
- Visibility timeout queue nên **≥ 6× function timeout**; ESM xử lý **at least once** → handler phải **idempotent**.
- `ReportBatchItemFailures` → chỉ item lỗi được đưa lại queue (partial batch).
**⏱️ ~25 phút** · **Yêu cầu trước:** đã có `ROLE_ARN`, `ACCOUNT_ID`, `AWS_REGION`.

### Các bước
1. Thêm quyền SQS cho role (đủ để Lambda poll & xoá message):
   ```bash
   aws iam attach-role-policy --role-name dva-lambda-role \
     --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaSQSQueueExecutionRole
   ```
2. Viết handler xử lý batch + partial batch response:
   ```python
   # sqs_handler.py
   def handler(event, context):
       failures = []
       for r in event["Records"]:
           body = r["body"]
           print("SQS message:", r["messageId"], body)
           if body == "POISON":          # cố ý cho 1 message lỗi
               failures.append({"itemIdentifier": r["messageId"]})
       # chỉ các message trong danh sách này quay lại queue để xử lý lại
       return {"batchItemFailures": failures}
   ```
   ```bash
   zip sqs.zip sqs_handler.py
   aws lambda create-function --function-name sqs-consumer \
     --runtime python3.12 --handler sqs_handler.handler \
     --role ${ROLE_ARN} --zip-file fileb://sqs.zip --timeout 10
   ```
3. Tạo queue với **VisibilityTimeout = 60** (= 6 × timeout 10s):
   ```bash
   Q_URL=$(aws sqs create-queue --queue-name esm-queue \
     --attributes VisibilityTimeout=60 --query QueueUrl --output text)
   Q_ARN=$(aws sqs get-queue-attributes --queue-url "$Q_URL" \
     --attribute-names QueueArn --query 'Attributes.QueueArn' --output text)
   ```
4. Tạo **event source mapping** (Lambda bắt đầu poll queue) + bật partial batch response:
   ```bash
   aws lambda create-event-source-mapping --function-name sqs-consumer \
     --event-source-arn "$Q_ARN" \
     --batch-size 5 \
     --function-response-types ReportBatchItemFailures
   # xem trạng thái mapping -> Enabled
   aws lambda list-event-source-mappings --function-name sqs-consumer \
     --query 'EventSourceMappings[].{UUID:UUID,State:State,Batch:BatchSize}'
   ```
5. Gửi message (gồm 1 message "POISON" để test partial failure):
   ```bash
   aws sqs send-message --queue-url "$Q_URL" --message-body "hello-1"
   aws sqs send-message --queue-url "$Q_URL" --message-body "hello-2"
   aws sqs send-message --queue-url "$Q_URL" --message-body "POISON"
   ```

### ✅ Kiểm chứng
- Log cho thấy function bị gọi và in các `messageId`/`body`:
  ```bash
  aws logs tail /aws/lambda/sqs-consumer --since 5m --follow
  ```
- `hello-1`, `hello-2` được xử lý & xoá khỏi queue; chỉ `POISON` quay lại (nhờ `batchItemFailures`) và được thử lại sau khi hết visibility timeout.
- `aws sqs get-queue-attributes --queue-url "$Q_URL" --attribute-names ApproximateNumberOfMessages` giảm dần (trừ message poison còn xoay vòng).

> 🧠 **Best practice:** queue này chưa có `RedrivePolicy` nên `POISON` sẽ xoay vòng **vô hạn**. Thực tế nên gắn `RedrivePolicy` (`maxReceiveCount` + DLQ) cho queue để sau N lần nhận thất bại, message lỗi tự rơi vào **DLQ** thay vì lặp mãi — xem [Lab 5.3](../week-05/labs.md).

### 🧹 Dọn dẹp
```bash
UUID=$(aws lambda list-event-source-mappings --function-name sqs-consumer --query 'EventSourceMappings[0].UUID' --output text)
aws lambda delete-event-source-mapping --uuid "$UUID"
aws lambda delete-function --function-name sqs-consumer
aws sqs delete-queue --queue-url "$Q_URL"
aws iam detach-role-policy --role-name dva-lambda-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaSQSQueueExecutionRole
```

### 🧠 Ý nghĩa với đề thi
- `SQS`→`Lambda` là **event source mapping (poll)**, tài nguyên do **Lambda** tạo/quản lý — KHÁC trigger push (S3/SNS).
- Visibility timeout **≥ 6× function timeout** để tránh message tái xuất hiện khi function còn đang xử lý.
- ESM **at least once** → handler **idempotent**; `ReportBatchItemFailures` để không phải reprocess cả batch khi chỉ 1 item lỗi.

---

## Lab 2.6 ⭐ — `DynamoDB Streams` → `Lambda` (event source mapping) — quan sát NEW/OLD image
**🎯 Mục tiêu:** Bật `DynamoDB Streams` cho một bảng, tạo **event source mapping** `--starting-position LATEST`, put/update/delete item và quan sát record với `NewImage`/`OldImage` trong log.
**🧩 Luyện kỹ năng (liên quan đề):**
- "`Lambda` đọc `DynamoDB Streams`/`Kinesis`" → **event source mapping** (poll theo shard, batch).
- Bật stream: `StreamViewType=NEW_AND_OLD_IMAGES`; ESM cần `--starting-position` (`LATEST`/`TRIM_HORIZON`).
- Role cần `dynamodb:GetRecords/GetShardIterator/DescribeStream/ListStreams` (managed policy `AWSLambdaDynamoDBExecutionRole`).
**⏱️ ~25 phút** · **Yêu cầu trước:** đã có `ROLE_ARN`, `ACCOUNT_ID`, `AWS_REGION`.

### Các bước
1. Thêm quyền đọc stream cho role:
   ```bash
   aws iam attach-role-policy --role-name dva-lambda-role \
     --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaDynamoDBExecutionRole
   ```
2. Viết handler in `eventName` (INSERT/MODIFY/REMOVE) + NEW/OLD image:
   ```python
   # ddb_handler.py
   import json
   def handler(event, context):
       for r in event["Records"]:
           dyn = r["dynamodb"]
           print("Event:", r["eventName"],
                 "NEW:", json.dumps(dyn.get("NewImage")),
                 "OLD:", json.dumps(dyn.get("OldImage")))
       return {"processed": len(event["Records"])}
   ```
   ```bash
   zip ddb.zip ddb_handler.py
   aws lambda create-function --function-name ddb-consumer \
     --runtime python3.12 --handler ddb_handler.handler \
     --role ${ROLE_ARN} --zip-file fileb://ddb.zip --timeout 10
   ```
3. Tạo bảng và **bật stream** với cả ảnh mới lẫn cũ:
   ```bash
   aws dynamodb create-table --table-name esm-table \
     --attribute-definitions AttributeName=id,AttributeType=S \
     --key-schema AttributeName=id,KeyType=HASH \
     --billing-mode PAY_PER_REQUEST \
     --stream-specification StreamEnabled=true,StreamViewType=NEW_AND_OLD_IMAGES
   aws dynamodb wait table-exists --table-name esm-table

   STREAM_ARN=$(aws dynamodb describe-table --table-name esm-table \
     --query 'Table.LatestStreamArn' --output text)
   echo "$STREAM_ARN"
   ```
4. Tạo **event source mapping** với `--starting-position LATEST`:
   ```bash
   aws lambda create-event-source-mapping --function-name ddb-consumer \
     --event-source-arn "$STREAM_ARN" \
     --starting-position LATEST \
     --batch-size 5
   aws lambda list-event-source-mappings --function-name ddb-consumer \
     --query 'EventSourceMappings[].{UUID:UUID,State:State,Pos:StartingPosition}'
   ```
5. Sinh sự kiện: put (INSERT) → update (MODIFY) → delete (REMOVE):
   ```bash
   aws dynamodb put-item --table-name esm-table \
     --item '{"id":{"S":"a1"},"name":{"S":"Alice"}}'
   aws dynamodb update-item --table-name esm-table \
     --key '{"id":{"S":"a1"}}' \
     --update-expression 'SET #n = :v' \
     --expression-attribute-names '{"#n":"name"}' \
     --expression-attribute-values '{":v":{"S":"Alice2"}}'
   aws dynamodb delete-item --table-name esm-table --key '{"id":{"S":"a1"}}'
   ```

### ✅ Kiểm chứng
```bash
aws logs tail /aws/lambda/ddb-consumer --since 5m --follow
```
- `INSERT` → chỉ có `NewImage`.
- `MODIFY` → có cả `NewImage` (`Alice2`) và `OldImage` (`Alice`).
- `REMOVE` → chỉ có `OldImage`.

### 🧹 Dọn dẹp
```bash
UUID=$(aws lambda list-event-source-mappings --function-name ddb-consumer --query 'EventSourceMappings[0].UUID' --output text)
aws lambda delete-event-source-mapping --uuid "$UUID"
aws lambda delete-function --function-name ddb-consumer
aws dynamodb delete-table --table-name esm-table
aws iam detach-role-policy --role-name dva-lambda-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaDynamoDBExecutionRole
```

### 🧠 Ý nghĩa với đề thi
- `DynamoDB Streams`→`Lambda` = **event source mapping** (poll theo shard) — cùng nhóm với `Kinesis`, KHÁC push trigger.
- `StreamViewType` quyết định record có gì: `KEYS_ONLY` / `NEW_IMAGE` / `OLD_IMAGE` / `NEW_AND_OLD_IMAGES`.
- `--starting-position`: `LATEST` (chỉ record mới) vs `TRIM_HORIZON` (từ đầu stream). SQS ESM KHÔNG cần tham số này.

---

## 🧹 Dọn dẹp cuối cùng (sau khi xong hết các lab)
```bash
aws lambda delete-alias --function-name myFn --name prod 2>/dev/null
aws lambda delete-function --function-name myFn
aws iam detach-role-policy --role-name dva-lambda-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
aws iam delete-role --role-name dva-lambda-role
```

> 🔗 Ôn lại lý thuyết tương ứng ở [README tuần 2](README.md) · làm [câu hỏi luyện tập](questions.md) sau khi hoàn tất lab.
