# 🧪 Hands-on Labs — Tuần 3: `DynamoDB` toàn tập

> Lab cầm tay chỉ việc, chạy được trên tài khoản AWS thật (Free Tier). LUÔN chạy phần Dọn dẹp cuối mỗi lab (hoặc **Dọn dẹp tổng** ở cuối file với các tài nguyên dùng chung).
> ⚙️ Yêu cầu chung: đã cấu hình `AWS CLI v2` (xem Lab 1.1 tuần 1) + IAM đủ quyền cho dịch vụ trong lab. Nhớ set region trước khi bắt đầu:
> ```bash
> export AWS_REGION=us-east-1          # đổi theo region của bạn
> export ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
> ```
> Về [plan tuần](README.md) · [Câu hỏi luyện tập](questions.md) · [Kế hoạch tổng](../../DVA-C02-STUDY-PLAN.md)

> 🗺️ **Bảng dùng chung:** Lab 3.1 tạo bảng `Orders` và **các lab sau dùng lại nó**. Chỉ xoá `Orders` (và các bảng phụ) ở phần **🧹 Dọn dẹp tổng** cuối file.

---

## Lab 3.1 — Tạo bảng + CRUD, so sánh Query vs Scan

**🎯 Mục tiêu:** Tạo bảng `Orders` (composite key), thao tác CRUD bằng cả CLI và `AWS SDK for JavaScript v3` (`@aws-sdk/lib-dynamodb`), rồi so sánh trực tiếp **Query** (đọc theo partition key) với **Scan** (đọc toàn bảng) qua `ConsumedCapacity`.

**🧩 Luyện kỹ năng (liên quan đề):**
- Tạo table với partition key + sort key, `billing-mode PAY_PER_REQUEST` (on-demand).
- `PutItem` / `GetItem` / `Query` / `Scan` — cú pháp CLI + SDK.
- Hiểu vì sao **Query nhanh & ít RCU**, **Scan chậm & tốn RCU**; filter expression chạy **sau khi đọc** nên không tiết kiệm capacity.

**⏱️ ~35 phút** · **Yêu cầu trước:** đã cấu hình `AWS CLI v2` + `Node.js 24` (`node --version`).

### Các bước

1. Tạo bảng `Orders` có **partition key `CustomerId` + sort key `OrderDate`**, khai luôn **LSI `ByAmount`** (LSI **bắt buộc khai lúc tạo bảng** — sẽ dùng ở Lab 3.2):
   ```bash
   aws dynamodb create-table \
     --table-name Orders \
     --attribute-definitions \
       AttributeName=CustomerId,AttributeType=S \
       AttributeName=OrderDate,AttributeType=S \
       AttributeName=Amount,AttributeType=N \
     --key-schema \
       AttributeName=CustomerId,KeyType=HASH \
       AttributeName=OrderDate,KeyType=RANGE \
     --local-secondary-indexes \
       "IndexName=ByAmount,KeySchema=[{AttributeName=CustomerId,KeyType=HASH},{AttributeName=Amount,KeyType=RANGE}],Projection={ProjectionType=ALL}" \
     --billing-mode PAY_PER_REQUEST
   aws dynamodb wait table-exists --table-name Orders
   ```

2. **CRUD bằng CLI** — thêm vài item để có dữ liệu Query/Scan (`Status` là **từ khoá dành riêng** của DynamoDB → phải dùng alias `#s`):
   ```bash
   aws dynamodb put-item --table-name Orders \
     --item '{"CustomerId":{"S":"C1"},"OrderDate":{"S":"2026-01-01"},"Amount":{"N":"100"},"Status":{"S":"NEW"}}'
   aws dynamodb put-item --table-name Orders \
     --item '{"CustomerId":{"S":"C1"},"OrderDate":{"S":"2026-01-05"},"Amount":{"N":"300"},"Status":{"S":"PAID"}}'
   aws dynamodb put-item --table-name Orders \
     --item '{"CustomerId":{"S":"C2"},"OrderDate":{"S":"2026-01-02"},"Amount":{"N":"50"},"Status":{"S":"NEW"}}'

   # GetItem: đọc 1 item theo full primary key
   aws dynamodb get-item --table-name Orders \
     --key '{"CustomerId":{"S":"C1"},"OrderDate":{"S":"2026-01-01"}}'
   ```

3. **Query vs Scan** — chú ý số `ConsumedCapacity` in ra:
   ```bash
   # QUERY: chỉ đọc phần dữ liệu của C1 → ít RCU, nhanh
   aws dynamodb query --table-name Orders \
     --key-condition-expression "CustomerId = :c" \
     --expression-attribute-values '{":c":{"S":"C1"}}' \
     --return-consumed-capacity TOTAL

   # SCAN: đọc TOÀN BẢNG rồi mới lọc Status=NEW → filter chạy SAU, vẫn tính RCU trên dữ liệu đã quét
   aws dynamodb scan --table-name Orders \
     --filter-expression "#s = :st" \
     --expression-attribute-names '{"#s":"Status"}' \
     --expression-attribute-values '{":st":{"S":"NEW"}}' \
     --return-consumed-capacity TOTAL
   ```
   > So sánh: Scan trả `ScannedCount` (số item đã quét) **lớn hơn** `Count` (số item khớp filter) → chứng minh filter **không** giảm RCU.

4. **CRUD + Query/Scan bằng `AWS SDK v3`** — script chạy LOCAL nên cần cài SDK trước:
   ```bash
   npm init -y
   npm install @aws-sdk/client-dynamodb @aws-sdk/lib-dynamodb
   ```
   Lưu `lab31.mjs` rồi `node lab31.mjs`:
   ```javascript
   import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
   import {
     DynamoDBDocumentClient,
     PutCommand,
     GetCommand,
     QueryCommand,
     ScanCommand,
   } from "@aws-sdk/lib-dynamodb";

   const ddb = DynamoDBDocumentClient.from(new DynamoDBClient({ region: "us-east-1" }));
   const TableName = "Orders";

   // PutItem
   await ddb.send(new PutCommand({
     TableName,
     Item: { CustomerId: "C3", OrderDate: "2026-01-03", Amount: 200, Status: "NEW" },
   }));

   // GetItem
   const got = await ddb.send(new GetCommand({
     TableName,
     Key: { CustomerId: "C3", OrderDate: "2026-01-03" },
   }));
   console.log("GET:", got.Item);

   // Query (theo partition key) — nên ưu tiên
   const q = await ddb.send(new QueryCommand({
     TableName,
     KeyConditionExpression: "CustomerId = :c",
     ExpressionAttributeValues: { ":c": "C1" },
   }));
   console.log("QUERY count:", q.Count, q.Items);

   // Scan (toàn bảng) — kèm pagination bằng LastEvaluatedKey
   const items = [];
   let start;
   do {
     const resp = await ddb.send(new ScanCommand({ TableName, ExclusiveStartKey: start }));
     items.push(...(resp.Items ?? []));
     start = resp.LastEvaluatedKey;
   } while (start);
   console.log("SCAN total:", items.length);
   ```

### ✅ Kiểm chứng
- `GetItem` trả đúng item vừa ghi.
- Query chỉ trả item của `C1`; Scan trả cả bảng, `ScannedCount > Count` khi có filter.
- `ConsumedCapacity` của Query nhỏ hơn Scan trên cùng lượng dữ liệu.

### 🧹 Dọn dẹp (tránh tính phí)
Bảng `Orders` được **dùng lại ở các lab sau** → chỉ xoá ở **Dọn dẹp tổng** cuối file. (Lệnh tham khảo: `aws dynamodb delete-table --table-name Orders`.)

### 🧠 Ý nghĩa với đề thi
- **Query > Scan** gần như luôn đúng: đề mô tả "đọc toàn bảng chậm" → đổi sang Query theo key.
- **Filter expression KHÔNG tiết kiệm RCU** (chạy sau khi đọc) — bẫy kinh điển.
- Kết quả bị cắt ở **1 MB/lần** → dùng `LastEvaluatedKey` để phân trang.

---

## Lab 3.2 — GSI (thêm sau) + LSI (lúc tạo bảng), query qua index

**🎯 Mục tiêu:** Chứng minh **LSI phải khai lúc tạo bảng** (đã làm ở Lab 3.1) và **GSI thêm được bất kỳ lúc nào**; query qua từng index và quan sát khác biệt consistency.

**🧩 Luyện kỹ năng (liên quan đề):**
- LSI: **cùng partition key**, sort key khác, **hỗ trợ strong consistency**, không thêm được sau.
- GSI: partition key **khác** bảng gốc, **throughput riêng**, **chỉ eventual consistency**, thêm/xoá tự do.
- Query `--index-name` + bẫy: `--consistent-read` chạy được trên LSI nhưng **lỗi** trên GSI.

**⏱️ ~30 phút** · **Yêu cầu trước:** đã làm Lab 3.1 (bảng `Orders` + LSI `ByAmount` đang tồn tại).

### Các bước

1. **Query qua LSI `ByAmount`** — LSI cùng partition key `CustomerId`, sort theo `Amount`, và **cho phép strong consistency** (`--consistent-read`):
   ```bash
   aws dynamodb query --table-name Orders --index-name ByAmount \
     --key-condition-expression "CustomerId = :c AND Amount > :min" \
     --expression-attribute-values '{":c":{"S":"C1"},":min":{"N":"150"}}' \
     --consistent-read
   ```

2. **Thêm GSI `ByStatus` SAU khi bảng đã chạy** (chứng minh GSI tạo bất kỳ lúc nào). Phải khai thêm `--attribute-definitions` cho key mới của index:
   ```bash
   aws dynamodb update-table --table-name Orders \
     --attribute-definitions AttributeName=Status,AttributeType=S \
     --global-secondary-index-updates \
     '[{"Create":{"IndexName":"ByStatus","KeySchema":[{"AttributeName":"Status","KeyType":"HASH"}],"Projection":{"ProjectionType":"ALL"}}}]'
   ```

3. Chờ GSI backfill xong (trạng thái `ACTIVE`):
   ```bash
   aws dynamodb describe-table --table-name Orders \
     --query "Table.GlobalSecondaryIndexes[?IndexName=='ByStatus'].IndexStatus" --output text
   # lặp lại tới khi in ra: ACTIVE
   ```

4. **Query qua GSI `ByStatus`** (partition key = `Status`, khác bảng gốc):
   ```bash
   aws dynamodb query --table-name Orders --index-name ByStatus \
     --key-condition-expression "#s = :st" \
     --expression-attribute-names '{"#s":"Status"}' \
     --expression-attribute-values '{":st":{"S":"NEW"}}'
   ```
   > Bẫy: thêm `--consistent-read` vào query GSI trên → **`ValidationException`** ("Consistent reads are not supported on global secondary indexes"). GSI **chỉ eventual**.

### ✅ Kiểm chứng
- Query LSI `ByAmount` trả item của `C1` có `Amount > 150`, có kèm strong read.
- `describe-table` cho thấy GSI `ByStatus` chuyển sang `ACTIVE`.
- Query GSI trả các item `Status=NEW` bất kể `CustomerId`; thêm `--consistent-read` → báo lỗi.

### 🧹 Dọn dẹp (tránh tính phí)
GSI có thể xoá riêng (bảng vẫn giữ lại cho các lab sau):
```bash
aws dynamodb update-table --table-name Orders \
  --global-secondary-index-updates '[{"Delete":{"IndexName":"ByStatus"}}]'
```
> Muốn giữ GSI để tiếp Lab 3.3+ cũng được — nó không phát sinh phí đáng kể ở on-demand khi rảnh.

### 🧠 Ý nghĩa với đề thi
- "Query theo thuộc tính **khác** partition key" / "thêm index **sau** khi bảng đã chạy" → **GSI** (LSI không làm được).
- "Cần **strongly consistent read** trên index" → **LSI** (GSI chỉ eventual).
- LSI dùng chung throughput với bảng; GSI có throughput riêng.

---

## Lab 3.3 — Conditional write + optimistic locking (version attribute)

**🎯 Mục tiêu:** Chống ghi đè khi tạo mới (`attribute_not_exists`) và chống **race condition** bằng **optimistic locking** với thuộc tính `Version`; mô phỏng 2 tiến trình ghi đè lên cùng item.

**🧩 Luyện kỹ năng (liên quan đề):**
- Conditional write → nếu điều kiện sai trả về `ConditionalCheckFailedException` (không ghi đè).
- Optimistic locking: chỉ update nếu `Version` còn bằng giá trị đã đọc.
- Phân biệt case này với `TransactWriteItems` (case đơn giản KHÔNG cần transaction).

**⏱️ ~25 phút** · **Yêu cầu trước:** đã làm Lab 3.1 (bảng `Orders`).

### Các bước

1. **Conditional create** — chỉ ghi khi item CHƯA tồn tại:
   ```bash
   # Lần 1: item chưa có → OK; đảm bảo có thuộc tính Version=1
   aws dynamodb put-item --table-name Orders \
     --item '{"CustomerId":{"S":"C1"},"OrderDate":{"S":"2026-01-01"},"Amount":{"N":"100"},"Status":{"S":"NEW"},"Version":{"N":"1"}}' \
     --condition-expression "attribute_not_exists(CustomerId) AND attribute_not_exists(OrderDate)"

   # Lần 2 chạy LẠI lệnh trên → ConditionalCheckFailedException (đã tồn tại, không ghi đè)
   ```

2. **Optimistic locking mô phỏng 2 tiến trình** — script chạy LOCAL (nếu chưa cài SDK ở Lab 3.1: `npm init -y && npm install @aws-sdk/client-dynamodb @aws-sdk/lib-dynamodb`). Lưu `lab33.mjs` rồi `node lab33.mjs`:
   ```javascript
   import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
   import { DynamoDBDocumentClient, GetCommand, UpdateCommand } from "@aws-sdk/lib-dynamodb";

   const ddb = DynamoDBDocumentClient.from(new DynamoDBClient({ region: "us-east-1" }));
   const TableName = "Orders";
   const key = { CustomerId: "C1", OrderDate: "2026-01-01" };

   // Cả 2 tiến trình đọc CÙNG version (giả lập đọc đồng thời)
   const got = await ddb.send(new GetCommand({ TableName, Key: key }));
   const current = got.Item.Version;   // ví dụ = 1
   console.log("Cả hai tiến trình đọc Version =", current);

   async function updateWithLock(name, newAmount, expectedVersion) {
     try {
       await ddb.send(new UpdateCommand({
         TableName,
         Key: key,
         UpdateExpression: "SET Amount = :a, Version = :newv",
         ConditionExpression: "Version = :curv",
         ExpressionAttributeValues: {
           ":a": newAmount,
           ":newv": expectedVersion + 1,
           ":curv": expectedVersion,
         },
       }));
       console.log(`[${name}] OK: Amount=${newAmount}, Version ${expectedVersion}->${expectedVersion + 1}`);
     } catch (e) {
       if (e.name === "ConditionalCheckFailedException") {
         console.log(`[${name}] THẤT BẠI: item đã bị tiến trình khác ghi trước → phải đọc lại & thử lại`);
       } else {
         throw e;
       }
     }
   }

   // Tiến trình A ghi trước với version cũ (1) → thành công, Version 1->2
   await updateWithLock("A", 500, current);
   // Tiến trình B cũng dùng version cũ (1) → điều kiện Version=1 KHÔNG còn đúng → thất bại
   await updateWithLock("B", 999, current);
   ```

### ✅ Kiểm chứng
```bash
aws dynamodb get-item --table-name Orders \
  --key '{"CustomerId":{"S":"C1"},"OrderDate":{"S":"2026-01-01"}}'
```
- Kết quả: `Amount=500`, `Version=2` → chỉ tiến trình A thắng; B in ra "THẤT BẠI" (không ghi đè mất dữ liệu của A).

### 🧹 Dọn dẹp (tránh tính phí)
Không tạo tài nguyên mới (chỉ ghi item vào `Orders`) → dọn ở **Dọn dẹp tổng**.

### 🧠 Ý nghĩa với đề thi
- "Tránh ghi đè khi tạo mới" → **conditional write** (`attribute_not_exists`).
- "Chống race condition / cập nhật đồng thời" → **optimistic locking** bằng version, KHÔNG cần transaction cho case đơn giản.
- `SET x = x + :inc` với condition là nền tảng của **atomic counter**.

---

## Lab 3.4 — TransactWriteItems (2 bảng, all-or-nothing)

**🎯 Mục tiêu:** Dùng `TransactWriteItems` ghi đồng thời sang **2 bảng** như một khối ACID; quan sát rằng khi **1 điều kiện fail** thì **toàn bộ** transaction bị huỷ (không ghi gì).

**🧩 Luyện kỹ năng (liên quan đề):**
- `TransactWriteItems`: gom `Put`/`Update`/`Delete`/`ConditionCheck`, all-or-nothing, ≤100 action / 100 item / 4 MB.
- Chi phí **2× WCU/item** (prepare + commit) — tính cả khi transaction bị huỷ.
- Fail điều kiện → `TransactionCanceledException` (SDK **không** tự retry).

**⏱️ ~30 phút** · **Yêu cầu trước:** đã làm Lab 3.1 (bảng `Orders`).

### Các bước

1. Tạo bảng phụ `Inventory` + 1 item tồn kho:
   ```bash
   aws dynamodb create-table --table-name Inventory \
     --attribute-definitions AttributeName=Sku,AttributeType=S \
     --key-schema AttributeName=Sku,KeyType=HASH \
     --billing-mode PAY_PER_REQUEST
   aws dynamodb wait table-exists --table-name Inventory
   aws dynamodb put-item --table-name Inventory \
     --item '{"Sku":{"S":"SKU1"},"Qty":{"N":"5"}}'
   ```

2. **Transaction THÀNH CÔNG** — tạo Order + trừ tồn kho (điều kiện `Qty >= 1` đúng):
   ```bash
   aws dynamodb transact-write-items --transact-items '[
     {"Put":{"TableName":"Orders","Item":{"CustomerId":{"S":"C9"},"OrderDate":{"S":"2026-02-01"},"Amount":{"N":"20"},"Status":{"S":"NEW"},"Version":{"N":"1"}}}},
     {"Update":{"TableName":"Inventory","Key":{"Sku":{"S":"SKU1"}},
       "UpdateExpression":"SET Qty = Qty - :n","ConditionExpression":"Qty >= :n",
       "ExpressionAttributeValues":{":n":{"N":"1"}}}}
   ]'
   ```

3. **Transaction THẤT BẠI** — đặt số lượng trừ vượt tồn kho (`Qty >= 999` sai) → cả 2 thao tác đều bị rollback:
   ```bash
   aws dynamodb transact-write-items --transact-items '[
     {"Put":{"TableName":"Orders","Item":{"CustomerId":{"S":"C10"},"OrderDate":{"S":"2026-02-02"},"Amount":{"N":"20"},"Status":{"S":"NEW"}}}},
     {"Update":{"TableName":"Inventory","Key":{"Sku":{"S":"SKU1"}},
       "UpdateExpression":"SET Qty = Qty - :n","ConditionExpression":"Qty >= :n",
       "ExpressionAttributeValues":{":n":{"N":"999"}}}}
   ]'
   # → TransactionCanceledException, CancellationReasons: [None, ConditionalCheckFailed]
   ```

### ✅ Kiểm chứng
```bash
# Sau bước 2: Qty giảm còn 4, có Order C9
aws dynamodb get-item --table-name Inventory --key '{"Sku":{"S":"SKU1"}}'

# Sau bước 3 (fail): Order C10 KHÔNG được ghi (all-or-nothing), Qty vẫn = 4
aws dynamodb get-item --table-name Orders \
  --key '{"CustomerId":{"S":"C10"},"OrderDate":{"S":"2026-02-02"}}'   # trả về rỗng
```
- Xác nhận thao tác `Put` C10 **không** thực thi dù điều kiện fail nằm ở thao tác `Update` khác → đúng bản chất all-or-nothing.

### 🧹 Dọn dẹp (tránh tính phí)
```bash
aws dynamodb delete-table --table-name Inventory
```
(Bảng `Orders` giữ cho lab sau — xoá ở **Dọn dẹp tổng**.)

### 🧠 Ý nghĩa với đề thi
- "Nhiều thao tác **phải cùng thành công hoặc cùng thất bại**" → **`TransactWriteItems`**, KHÔNG phải `BatchWriteItem` (batch không all-or-nothing, có thể thành công một phần).
- Nhớ **2× WCU** và transaction **không dùng được trên index**.
- Fail → `TransactionCanceledException`, SDK không retry (khác `ConditionalCheckFailedException` của 1 thao tác đơn).

---

## Lab 3.5 — `Lambda` CRUD `DynamoDB` ⭐

**🎯 Mục tiêu:** Viết 1 `Lambda` (`Node.js` + `AWS SDK v3`) đọc/ghi bảng `Orders` theo `action` trong event, deploy bằng zip và invoke trực tiếp. Đây là **nền cho API tuần 4** (`API Gateway` → `Lambda` → `DynamoDB`).

**🧩 Luyện kỹ năng (liên quan đề):**
- `Lambda` gọi `DynamoDB` qua `AWS SDK v3` (`@aws-sdk/lib-dynamodb`) — mô hình **synchronous invoke** (nền cho `API Gateway` proxy).
- Execution role = `AWSLambdaBasicExecutionRole` (ghi CloudWatch Logs) + quyền `DynamoDB`.
- Truyền cấu hình qua **environment variable** (`TABLE_NAME`).

**⏱️ ~40 phút** · **Yêu cầu trước:** đã làm Lab 3.1 (bảng `Orders`).

### Các bước

1. Tạo **execution role** cho Lambda (trust `lambda.amazonaws.com`) + gắn policy:
   ```bash
   cat > trust-policy.json <<'EOF'
   {
     "Version": "2012-10-17",
     "Statement": [{
       "Effect": "Allow",
       "Principal": {"Service": "lambda.amazonaws.com"},
       "Action": "sts:AssumeRole"
     }]
   }
   EOF

   aws iam create-role --role-name dva-week3-crud-role \
     --assume-role-policy-document file://trust-policy.json
   # Ghi CloudWatch Logs
   aws iam attach-role-policy --role-name dva-week3-crud-role \
     --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
   # Quyền DynamoDB (lab dùng managed policy; production nên scope xuống đúng bảng)
   aws iam attach-role-policy --role-name dva-week3-crud-role \
     --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess

   ROLE_ARN=$(aws iam get-role --role-name dva-week3-crud-role --query Role.Arn --output text)
   echo "$ROLE_ARN"
   ```

2. Viết handler `index.mjs` (runtime `nodejs24.x` đã bundle sẵn AWS SDK v3 → không cần `npm install`; DocumentClient tự map số nên không cần xử lý kiểu `Decimal` như boto3):
   ```javascript
   import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
   import {
     DynamoDBDocumentClient,
     PutCommand,
     GetCommand,
     QueryCommand,
     DeleteCommand,
   } from "@aws-sdk/lib-dynamodb";

   const ddb = DynamoDBDocumentClient.from(new DynamoDBClient({}));
   const TableName = process.env.TABLE_NAME;

   export const handler = async (event) => {
     const action = event.action;
     let result;
     if (action === "create") {
       await ddb.send(new PutCommand({ TableName, Item: event.item }));
       result = { message: "created", item: event.item };
     } else if (action === "read") {
       const got = await ddb.send(new GetCommand({ TableName, Key: event.key }));
       result = got.Item;
     } else if (action === "query") {
       const q = await ddb.send(new QueryCommand({
         TableName,
         KeyConditionExpression: "CustomerId = :c",
         ExpressionAttributeValues: { ":c": event.customerId },
       }));
       result = q.Items;
     } else if (action === "delete") {
       await ddb.send(new DeleteCommand({ TableName, Key: event.key }));
       result = { message: "deleted" };
     } else {
       return { statusCode: 400, body: "unknown action" };
     }
     return { statusCode: 200, body: JSON.stringify(result) };
   };
   ```

3. Đóng gói & tạo function (chờ role kịp propagate vài giây):
   ```bash
   zip function.zip index.mjs

   aws lambda create-function \
     --function-name dva-week3-crud \
     --runtime nodejs24.x \
     --handler index.handler \
     --role "$ROLE_ARN" \
     --zip-file fileb://function.zip \
     --environment "Variables={TABLE_NAME=Orders}" \
     --timeout 15
   ```

4. Invoke thử từng action (CLI v2 cần `--cli-binary-format raw-in-base64-out` để nhận payload JSON thô):
   ```bash
   # CREATE
   aws lambda invoke --function-name dva-week3-crud \
     --cli-binary-format raw-in-base64-out \
     --payload '{"action":"create","item":{"CustomerId":"C50","OrderDate":"2026-03-01","Amount":250,"Status":"NEW"}}' \
     out.json && cat out.json; echo

   # READ
   aws lambda invoke --function-name dva-week3-crud \
     --cli-binary-format raw-in-base64-out \
     --payload '{"action":"read","key":{"CustomerId":"C50","OrderDate":"2026-03-01"}}' \
     out.json && cat out.json; echo

   # QUERY theo partition key
   aws lambda invoke --function-name dva-week3-crud \
     --cli-binary-format raw-in-base64-out \
     --payload '{"action":"query","customerId":"C50"}' \
     out.json && cat out.json; echo
   ```

### ✅ Kiểm chứng
- `out.json` của CREATE trả `{"statusCode":200,"body":"{... created ...}"}`.
- READ/QUERY trả về đúng item `C50` vừa ghi.
- Xem log: `aws logs tail /aws/lambda/dva-week3-crud --follow`.

### 🧹 Dọn dẹp (tránh tính phí)
```bash
aws lambda delete-function --function-name dva-week3-crud
aws iam detach-role-policy --role-name dva-week3-crud-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
aws iam detach-role-policy --role-name dva-week3-crud-role \
  --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess
aws iam delete-role --role-name dva-week3-crud-role
```

### 🧠 Ý nghĩa với đề thi
- Đây là mô hình **backend serverless CRUD** chuẩn: `Lambda` + `AWS SDK v3` + `DynamoDB` — tuần 4 chỉ cần thêm `API Gateway` (proxy `AWS_PROXY`, invoke **synchronous**) phía trước.
- Execution role phải có **BasicExecutionRole** (logs) + quyền dịch vụ cụ thể (least privilege trong production).
- Env var để tách cấu hình khỏi code (12-factor).

---

## Lab 3.6 — `DynamoDB Streams` → `Lambda` (audit / aggregate) ⭐

**🎯 Mục tiêu:** Bật `DynamoDB Streams` trên `Orders`, gắn **event source mapping** để `Lambda` xử lý mỗi thay đổi — ghi **audit log** + **đếm (aggregate)** số thay đổi theo loại event vào bảng `OrderAudit`.

**🧩 Luyện kỹ năng (liên quan đề):**
- `DynamoDB Streams → Lambda` = **event source mapping** (Lambda **poll** stream), KHÔNG phải async push như S3.
- Bật stream `StreamViewType=NEW_AND_OLD_IMAGES`; `create-event-source-mapping --starting-position LATEST`.
- Role cần `dynamodb:GetRecords/GetShardIterator/DescribeStream/ListStreams` (nằm trong managed policy `AWSLambdaDynamoDBExecutionRole`).

**⏱️ ~45 phút** · **Yêu cầu trước:** đã làm Lab 3.1 (bảng `Orders`).

### Các bước

1. Tạo bảng đích `OrderAudit` (vừa lưu log vừa giữ counter):
   ```bash
   aws dynamodb create-table --table-name OrderAudit \
     --attribute-definitions AttributeName=PK,AttributeType=S \
     --key-schema AttributeName=PK,KeyType=HASH \
     --billing-mode PAY_PER_REQUEST
   aws dynamodb wait table-exists --table-name OrderAudit
   ```

2. Bật **Streams** trên `Orders` với view type thấy cả ảnh trước/sau, rồi lấy stream ARN:
   ```bash
   aws dynamodb update-table --table-name Orders \
     --stream-specification StreamEnabled=true,StreamViewType=NEW_AND_OLD_IMAGES

   STREAM_ARN=$(aws dynamodb describe-table --table-name Orders \
     --query "Table.LatestStreamArn" --output text)
   echo "$STREAM_ARN"
   ```

3. Tạo **role** cho Lambda xử lý stream (đọc stream + ghi bảng audit):
   ```bash
   aws iam create-role --role-name dva-week3-stream-role \
     --assume-role-policy-document file://trust-policy.json   # dùng lại từ Lab 3.5
   # Quyền đọc DynamoDB Streams + ghi CloudWatch Logs (GetRecords/GetShardIterator/DescribeStream/ListStreams)
   aws iam attach-role-policy --role-name dva-week3-stream-role \
     --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaDynamoDBExecutionRole
   # Quyền ghi bảng OrderAudit
   aws iam attach-role-policy --role-name dva-week3-stream-role \
     --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess

   STREAM_ROLE_ARN=$(aws iam get-role --role-name dva-week3-stream-role --query Role.Arn --output text)
   ```

4. Viết handler `index.mjs` — audit + aggregate (đếm theo `eventName`). Đọc thay đổi từ `event.Records[].dynamodb`; `Count` là **từ khoá dành riêng** nên phải alias `#c`:
   ```javascript
   import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
   import { DynamoDBDocumentClient, PutCommand, UpdateCommand } from "@aws-sdk/lib-dynamodb";

   const ddb = DynamoDBDocumentClient.from(new DynamoDBClient({}));
   const AuditTable = process.env.AUDIT_TABLE;

   export const handler = async (event) => {
     for (const record of event.Records) {
       const name = record.eventName;            // INSERT | MODIFY | REMOVE
       const keys = record.dynamodb.Keys;
       // 1) Audit log: 1 dòng cho mỗi thay đổi
       await ddb.send(new PutCommand({
         TableName: AuditTable,
         Item: {
           PK: `EVENT#${record.eventID}`,
           EventName: name,
           Keys: JSON.stringify(keys),
           At: new Date().toISOString(),
         },
       }));
       // 2) Aggregate: đếm số thay đổi theo loại (atomic counter)
       await ddb.send(new UpdateCommand({
         TableName: AuditTable,
         Key: { PK: `COUNTER#${name}` },
         UpdateExpression: "SET #c = if_not_exists(#c, :zero) + :one",
         ExpressionAttributeNames: { "#c": "Count" },
         ExpressionAttributeValues: { ":one": 1, ":zero": 0 },
       }));
     }
     console.log(`Đã xử lý ${event.Records.length} record`);
     return { processed: event.Records.length };
   };
   ```

5. Deploy + gắn **event source mapping** vào stream:
   ```bash
   zip stream.zip index.mjs
   aws lambda create-function \
     --function-name dva-week3-stream-audit \
     --runtime nodejs24.x \
     --handler index.handler \
     --role "$STREAM_ROLE_ARN" \
     --zip-file fileb://stream.zip \
     --environment "Variables={AUDIT_TABLE=OrderAudit}" \
     --timeout 30

   aws lambda create-event-source-mapping \
     --function-name dva-week3-stream-audit \
     --event-source-arn "$STREAM_ARN" \
     --starting-position LATEST \
     --batch-size 10
   ```

6. Sinh vài thay đổi trên `Orders` để kích hoạt stream:
   ```bash
   aws dynamodb put-item --table-name Orders \
     --item '{"CustomerId":{"S":"C60"},"OrderDate":{"S":"2026-04-01"},"Amount":{"N":"77"},"Status":{"S":"NEW"}}'
   aws dynamodb update-item --table-name Orders \
     --key '{"CustomerId":{"S":"C60"},"OrderDate":{"S":"2026-04-01"}}' \
     --update-expression "SET #s = :s" \
     --expression-attribute-names '{"#s":"Status"}' \
     --expression-attribute-values '{":s":{"S":"PAID"}}'
   aws dynamodb delete-item --table-name Orders \
     --key '{"CustomerId":{"S":"C60"},"OrderDate":{"S":"2026-04-01"}}'
   ```

### ✅ Kiểm chứng
```bash
# Log Lambda: thấy "Đã xử lý N record"
aws logs tail /aws/lambda/dva-week3-stream-audit --since 5m

# Bảng audit: có các dòng EVENT#... và counter theo loại (INSERT/MODIFY/REMOVE)
aws dynamodb scan --table-name OrderAudit
aws dynamodb get-item --table-name OrderAudit --key '{"PK":{"S":"COUNTER#INSERT"}}'
```
- Đủ 3 loại event (INSERT/MODIFY/REMOVE) được ghi audit; các `COUNTER#*` tăng đúng số lần thao tác.

### 🧹 Dọn dẹp (tránh tính phí)
```bash
# Xoá event source mapping (lấy UUID rồi xoá)
UUID=$(aws lambda list-event-source-mappings \
  --function-name dva-week3-stream-audit --query "EventSourceMappings[0].UUID" --output text)
aws lambda delete-event-source-mapping --uuid "$UUID"

aws lambda delete-function --function-name dva-week3-stream-audit
aws dynamodb delete-table --table-name OrderAudit

aws iam detach-role-policy --role-name dva-week3-stream-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaDynamoDBExecutionRole
aws iam detach-role-policy --role-name dva-week3-stream-role \
  --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess
aws iam delete-role --role-name dva-week3-stream-role
```
> Stream trên `Orders` sẽ mất khi xoá bảng ở Dọn dẹp tổng; hoặc tắt riêng: `aws dynamodb update-table --table-name Orders --stream-specification StreamEnabled=false`.

### 🧠 Ý nghĩa với đề thi
- "**Phản ứng khi item thay đổi / trigger Lambda**" → `DynamoDB Streams` + **event source mapping** (poll), `--starting-position LATEST`.
- View type `NEW_AND_OLD_IMAGES` để thấy cả trước/sau (dùng cho CDC, cập nhật search index, audit).
- Đây là mẫu **CDC / audit / aggregate** kinh điển; Streams giữ record **24 giờ** (khác Kinesis).
- Về "exactly-once": **exactly-once là ở TẦNG STREAM** (mỗi record xuất hiện đúng 1 lần trong stream, đúng thứ tự theo từng item); nhưng **`Lambda` event source mapping xử lý at-least-once** → cùng 1 record có thể được đưa cho handler **nhiều lần** (retry) → handler PHẢI **idempotent**.

---

## 🧹 Dọn dẹp tổng (chạy sau khi hoàn thành TẤT CẢ lab)

```bash
# Xoá các bảng dùng chung còn lại
aws dynamodb delete-table --table-name Orders
aws dynamodb delete-table --table-name Inventory 2>/dev/null || true
aws dynamodb delete-table --table-name OrderAudit 2>/dev/null || true

# Dọn file tạm
rm -f trust-policy.json function.zip stream.zip index.mjs out.json lab31.mjs lab33.mjs package.json package-lock.json
rm -rf node_modules
```
> Kiểm tra không còn tài nguyên tính phí: `aws dynamodb list-tables`, `aws lambda list-functions`, `aws iam list-roles | grep dva-week3`.
