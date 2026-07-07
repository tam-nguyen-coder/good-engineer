# 🟦 Tuần 1 — Developer mindset + AWS SDK/CLI + `Lambda` (cơ bản)

> **Domain:** Domain 1 – Development (32%) · **Thời lượng:** ~11h (4 buổi) · **Vị trí:** Tuần 1/5 của Domain 1
>
> **Điều hướng:** [🏠 Kế hoạch tổng](../DVA-C02-STUDY-PLAN.md) · [Tuần 2 ➡️](week-02.md)

## 🎯 Mục tiêu tuần này
- Giải thích được **khác biệt tư duy Architect → Developer**: đề DVA hỏi "làm bằng code/CLI/SDK thế nào", không hỏi "chọn kiến trúc nào".
- Tự tay cấu hình được **AWS CLI với nhiều named profile** và đọc hiểu `~/.aws/credentials` + `~/.aws/config`.
- Đọc thuộc **credential provider chain** theo đúng thứ tự ưu tiên và giải thích được vì sao code không bao giờ hard-code key.
- Tự tay khởi tạo **SDK client**, dùng được **paginator** và **waiter**, và viết đoạn code có **retry + exponential backoff + jitter**.
- Tự tạo 1 `Lambda` bằng **cả 3 cách** (Console, CLI, SDK), invoke nó và xem log ở `CloudWatch Logs`.
- Phân biệt được **execution role** (function gọi service khác) với **resource-based policy** (ai được invoke function).

## 📚 Nội dung học chi tiết

### 🅰️ Buổi A — Lý thuyết (~3h)

**1. Chuyển tư duy Architect → Developer**
- SAA-C03 hỏi *"kiến trúc nào đúng / rẻ / bền"*. DVA-C02 hỏi *"viết code / gọi CLI / dùng SDK thế nào để làm được điều đó"*.
- Đề DVA thường cho sẵn kiến trúc và hỏi: gọi API nào? cấu hình flag nào? xử lý lỗi/throttle ra sao? phân quyền cho code thế nào?
- **Vì sao quan trọng:** cùng một dịch vụ (vd `S3`), SAA hỏi "storage class nào", còn DVA hỏi "dùng multipart upload / presigned URL / SDK method nào". Đổi lăng kính đọc đề ngay từ tuần 1.

**2. AWS CLI — cấu hình & profile**
- `aws configure` ghi ra 2 file: **credentials** (`~/.aws/credentials`, chứa key) và **config** (`~/.aws/config`, chứa region/output/settings).
- **Named profiles:** tách nhiều tài khoản/vai trò. Dùng `--profile <tên>` hoặc biến `AWS_PROFILE`.
- Trong `~/.aws/config`, profile (khác default) được ghi dưới dạng section `[profile <tên>]`; còn trong `~/.aws/credentials` chỉ là `[<tên>]`.
- Thứ tự chọn region cho 1 lệnh: cờ `--region` > `AWS_REGION`/`AWS_DEFAULT_REGION` > region trong profile của `~/.aws/config`.
- `output` chọn `json` / `table` / `text` (text tiện cho `grep`/script).

Ví dụ `~/.aws/credentials`:
```ini
[default]
aws_access_key_id = AKIA...
aws_secret_access_key = ...

[dev]
aws_access_key_id = AKIA...
aws_secret_access_key = ...
```
Ví dụ `~/.aws/config`:
```ini
[default]
region = ap-southeast-1
output = json

[profile dev]
region = us-east-1
output = table
```

**3. Credential provider chain (ĐIỂM THI HAY HỎI)**
SDK/CLI tìm credentials theo **thứ tự ưu tiên giảm dần**:

| # | Nguồn | Ghi chú |
|---|-------|---------|
| 1 | Tham số truyền trực tiếp khi tạo client | Ưu tiên cao nhất (hard-code — chỉ để test, **không** dùng production) |
| 2 | Biến môi trường | `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` / `AWS_SESSION_TOKEN` |
| 3 | Shared credentials file | `~/.aws/credentials` (theo profile) |
| 4 | Shared config file | `~/.aws/config` |
| 5 | Container credentials | ECS task role |
| 6 | EC2 instance profile | Lấy qua IMDS |

- **Ý chính cho đề:** env vars được ưu tiên **trước** file profile; code chạy trên AWS (EC2/ECS/`Lambda`) nên dùng **IAM role**, tuyệt đối **không hard-code** key.
- **Vì sao quan trọng:** đề hay đưa tình huống "credentials nào được dùng khi vừa set env var vừa có profile" → nhớ env đứng trên file.

**4. AWS SDK — dùng cho đúng**
- **Khởi tạo client:** chọn region/endpoint; nếu không truyền credentials, SDK tự chạy credential chain ở trên.
- **Pagination (paginator):** API trả nhiều trang (token `NextToken`/`Marker`). Dùng **paginator** để SDK tự lặp qua các trang thay vì gọi thủ công — tránh sót dữ liệu ở trang sau.
- **Waiters:** poll một cách chuẩn hoá đến khi tài nguyên đạt trạng thái mong muốn (vd chờ bảng `DynamoDB` `ACTIVE`, chờ hàm `Lambda` sẵn sàng) thay vì tự viết vòng lặp `sleep`.
- **Xử lý lỗi:** bắt exception theo mã lỗi service; phân biệt lỗi **throttling** (nên retry) với lỗi **client 4xx** như thiếu quyền/tham số sai (retry vô ích).

**5. Retry & resilience**
- **Exponential backoff + jitter:** mỗi lần retry đợi lâu hơn theo cấp số nhân, cộng thêm ngẫu nhiên (jitter). **Jitter tránh "thundering herd"** — nhiều client cùng retry đồng loạt lại làm service sập tiếp.
- **SDK retry modes:**

| Mode | Đặc điểm |
|------|----------|
| `legacy` | Chế độ cũ, số lần retry cơ bản |
| `standard` | Chuẩn hoá across-SDK, retry nhiều loại lỗi hơn |
| `adaptive` | `standard` + client-side rate limiting, tự điều tiết khi bị throttle |

- **Idempotency:** thiết kế thao tác gọi lại nhiều lần vẫn cho kết quả như một lần (dùng client token / khoá duy nhất) → an toàn khi retry.

### 🅱️ Buổi B — Hands-on (~3.5h)

**Bước 1 — Cấu hình CLI + profile**
```bash
# Tạo profile mặc định
aws configure
# Tạo thêm named profile "dev"
aws configure --profile dev
# Kiểm tra danh tính đang dùng
aws sts get-caller-identity --profile dev
```

**Bước 2 — Tạo IAM execution role cho `Lambda`**
```bash
# Trust policy: cho phép Lambda service assume role này
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

aws iam create-role \
  --role-name dva-lab-lambda-role \
  --assume-role-policy-document file://trust.json

# Gắn quyền ghi CloudWatch Logs (managed policy cơ bản cho Lambda)
aws iam attach-role-policy \
  --role-name dva-lab-lambda-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
```

**Bước 3 — Tạo `Lambda` bằng CLI**
```bash
# Code handler tối giản (Node.js)
mkdir fn && cd fn
cat > index.mjs <<'EOF'
export const handler = async (event, context) => {
  console.log("event:", JSON.stringify(event));
  console.log("requestId:", context.awsRequestId);
  return { statusCode: 200, body: "hello DVA" };
};
EOF
zip function.zip index.mjs

aws lambda create-function \
  --function-name dva-lab-fn \
  --runtime nodejs20.x \
  --role arn:aws:iam::<ACCOUNT_ID>:role/dva-lab-lambda-role \
  --handler index.handler \
  --zip-file fileb://function.zip
```

**Bước 4 — Tạo `Lambda` bằng Console (cách thứ 2)**
1. Vào `Lambda` → **Create function** → *Author from scratch*.
2. Đặt tên, chọn runtime, ở phần permissions chọn **Use an existing role** → `dva-lab-lambda-role`.
3. Dán code vào editor, bấm **Deploy**, rồi **Test** với một event JSON mẫu.

**Bước 5 — Invoke bằng CLI**
```bash
aws lambda invoke \
  --function-name dva-lab-fn \
  --payload '{"name":"tam"}' \
  --cli-binary-format raw-in-base64-out \
  out.json
cat out.json
```

**Bước 6 — Xem log ở `CloudWatch Logs`**
```bash
# Log group của Lambda: /aws/lambda/<tên-function>
aws logs tail /aws/lambda/dva-lab-fn --follow
```

**Bước 7 — Đoạn SDK có retry/backoff (cách thứ 3: tạo/invoke bằng SDK)**
```javascript
import { LambdaClient, InvokeCommand } from "@aws-sdk/client-lambda";

// retryMode + maxAttempts: SDK tự backoff+jitter khi bị throttle
const client = new LambdaClient({
  region: "ap-southeast-1",
  retryMode: "adaptive",
  maxAttempts: 5,
});

const res = await client.send(new InvokeCommand({
  FunctionName: "dva-lab-fn",
  Payload: Buffer.from(JSON.stringify({ name: "sdk" })),
}));
console.log(new TextDecoder().decode(res.Payload));
```

### 🅲️ Buổi C — Bổ sung (~2.5h)

**1. `Lambda` cơ bản — mổ xẻ handler**
- **Cấu trúc handler:** `handler(event, context)` — điểm vào mà runtime gọi mỗi lần invoke.
- **`event`:** dữ liệu đầu vào (payload / sự kiện từ service kích hoạt như `API Gateway`, `S3`, `SQS`).
- **`context`:** thông tin runtime — `awsRequestId`, thời gian còn lại, tên/version function, log group/stream.
- **Runtimes:** Node.js, Python, Java, .NET, Go, Ruby — và custom runtime qua **Runtime API**.
- **Execution role:** IAM role mà function *assume* để gọi service khác (đọc `S3`, ghi `DynamoDB`, ...). Đây là quyền của **chính function**.
- **Ghi log tự động:** `Lambda` tự đẩy stdout/stderr và log của bạn vào `CloudWatch Logs` (log group `/aws/lambda/<tên>`) — **với điều kiện role có quyền** `logs:CreateLogGroup/CreateLogStream/PutLogEvents` (đã có sẵn trong `AWSLambdaBasicExecutionRole`).

**2. Execution role vs Resource-based policy** (đọc kỹ, đề rất hay bẫy)

| | Execution role | Resource-based policy |
|---|----------------|-----------------------|
| Trả lời câu hỏi | Function được phép **gọi ai** | **Ai được phép invoke** function |
| Gắn ở đâu | IAM role của function | Ngay trên chính function |
| Ví dụ | Function đọc `S3`, ghi `DynamoDB` | Cho `API Gateway`/`S3` quyền gọi function |

**3. Đọc tài liệu**
- AWS CLI User Guide — *Configuration and credential files*, *Named profiles*.
- SDK Developer Guide — *Credential provider chain*, *Retries and timeouts*, *Paginators*, *Waiters*.
- `Lambda` Developer Guide — *Lambda programming model*, *Execution role*.

### 🅳 Buổi D — Practice + Review (~2h)
- Làm **15–20 câu practice** về: CLI/profile, credential chain, SDK retry/pagination, `Lambda` cơ bản & execution role.
- **Ghi sổ câu sai:** mỗi câu sai ghi lại *keyword bẫy* + *lý do đúng*.
- **Spaced repetition:** đặt lịch ôn lại các fact tuần này ở mốc **1 / 3 / 7 ngày**.
- Đọc to phần "🚪 Cổng tự kiểm tra" và tự trả lời không nhìn đáp án.

## 🧠 PHẢI NHỚ tuần này

| Fact | Chi tiết |
|------|----------|
| Credential chain (thứ tự) | (1) tham số client → (2) env var → (3) `~/.aws/credentials` → (4) `~/.aws/config` → (5) ECS task role → (6) EC2 instance profile (IMDS) |
| Env vs file | **Env var được ưu tiên TRƯỚC** shared credentials/config file |
| Không hard-code | Production dùng **IAM role**, không nhét access key trong code |
| `Lambda` timeout | Tối đa **15 phút (900s)** |
| `Lambda` memory | **128 MB – 10240 MB**, CPU tỉ lệ thuận theo memory |
| Log tự động | Đẩy vào `CloudWatch Logs`, group `/aws/lambda/<tên>` (cần quyền logs trong execution role) |
| Execution role | Quyền để **function gọi service khác** (≠ ai được invoke) |
| Resource-based policy | Quy định **ai được phép invoke** function |
| Backoff + jitter | Jitter tránh **thundering herd** khi nhiều client cùng retry |

## ⚠️ Bẫy đề hay gặp
- Thấy *"vừa set env var vừa có profile trong file"* → dễ chọn "dùng profile", nhưng đúng là **env var thắng** vì đứng trước file trong chain.
- Thấy *"code trên EC2/`Lambda` cần gọi `S3`"* → dễ nghĩ "tạo access key gắn vào code", nhưng đúng là **gắn IAM role** (execution role/instance profile), không hard-code key.
- Thấy *"function chạy được nhưng không thấy log trong `CloudWatch`"* → dễ đổ tại code, nhưng đúng là **execution role thiếu quyền** `logs:*` (thiếu `AWSLambdaBasicExecutionRole`).
- Thấy *"muốn cho `API Gateway`/`S3` gọi function"* → dễ chọn "sửa execution role", nhưng đúng là **thêm resource-based policy** cho function (execution role chỉ cấp quyền function gọi ra ngoài).
- Thấy *"bị `ThrottlingException`, cần code bền hơn"* → dễ chọn "tăng timeout", nhưng đúng là **retry + exponential backoff + jitter** (và cân nhắc `adaptive` mode).
- Thấy *"list trả về thiếu dữ liệu"* → dễ nghĩ "bug API", nhưng đúng là **chưa xử lý pagination** (bỏ qua `NextToken`) → dùng **paginator**.
- Thấy *"retry làm tạo trùng bản ghi"* → dễ chọn "tắt retry", nhưng đúng là thiết kế **idempotency** (client token) để gọi lại vẫn an toàn.

## 🔁 Phản xạ nhanh (keyword → đáp án)

| Thấy từ khoá | Bật ngay |
|--------------|----------|
| "credentials nào được dùng" + có cả env & profile | Env var thắng (chain ưu tiên) |
| "code trên EC2/ECS/`Lambda` gọi service" | IAM role, không hard-code key |
| "chờ tài nguyên đạt trạng thái ACTIVE/ready" | Dùng **waiter** |
| "list trả về thiếu / có NextToken/Marker" | Dùng **paginator** |
| "`ThrottlingException` / `Rate exceeded`" | Exponential backoff + jitter, retry mode `adaptive` |
| "gọi lại nhiều lần không tạo trùng" | **Idempotency** (client token) |
| "function không ghi được log" | Thiếu quyền logs trong **execution role** |
| "cho service khác quyền invoke function" | **Resource-based policy** |
| "function cần đọc `S3`/ghi `DynamoDB`" | **Execution role** |
| "timeout hàm tối đa?" | 15 phút (900s) |

## 🧪 Lab checklist
- [ ] Cấu hình `default` profile + named profile `dev` bằng `aws configure`
- [ ] Xác minh danh tính bằng `aws sts get-caller-identity --profile dev`
- [ ] Tạo IAM **execution role** cho `Lambda` + gắn `AWSLambdaBasicExecutionRole`
- [ ] Tạo `Lambda` bằng **CLI** (`aws lambda create-function`)
- [ ] Tạo `Lambda` bằng **Console**
- [ ] Tạo/invoke `Lambda` bằng **SDK**
- [ ] Invoke bằng `aws lambda invoke` và đọc `out.json`
- [ ] Xem log ở `CloudWatch Logs` (`aws logs tail /aws/lambda/<tên>`)
- [ ] Viết đoạn SDK có **retry + backoff/jitter** (`retryMode`, `maxAttempts`)

## 🚪 Cổng tự kiểm tra (phải trả lời trôi chảy mới sang tuần sau)
- **Credential provider chain tìm creds theo thứ tự nào?**
  **Đáp án gọn:** (1) tham số client → (2) env var → (3) `~/.aws/credentials` → (4) `~/.aws/config` → (5) ECS task role → (6) EC2 instance profile qua IMDS. Env đứng trước file.
- **Vì sao dùng backoff + jitter khi bị throttle?**
  **Đáp án gọn:** backoff giãn thời gian retry theo cấp số nhân; jitter thêm ngẫu nhiên để tránh **thundering herd** (nhiều client retry đồng loạt lại làm sập service).
- **Execution role của `Lambda` dùng để làm gì? Khác resource-based policy chỗ nào?**
  **Đáp án gọn:** execution role = quyền để **function gọi service khác**; resource-based policy = quy định **ai được invoke** function.
- **Vì sao code không nên hard-code access key?**
  **Đáp án gọn:** rò rỉ/khó xoay vòng; production dùng **IAM role** (instance profile / task role / execution role), SDK tự lấy qua credential chain.
- **Đã tự tạo & invoke `Lambda` bằng cả 3 cách (Console/CLI/SDK) chưa? Log function nằm ở đâu?**
  **Đáp án gọn:** rồi; log ở `CloudWatch Logs`, log group `/aws/lambda/<tên-function>`.
- **`Lambda` timeout và memory tối đa là bao nhiêu?**
  **Đáp án gọn:** timeout tối đa 15 phút (900s); memory 128 MB–10240 MB, CPU tỉ lệ theo memory.

## 📎 Tài nguyên tuần này
> 📂 **Đã crawl sẵn tài liệu AWS vào** [`resources/week-01/`](resources/week-01/INDEX.md) — đọc offline được.
- AWS Docs: *AWS CLI User Guide* – Configuration and credential file settings; Named profiles.
- AWS Docs: *AWS SDKs and Tools Reference Guide* – Credential provider chain; Retries; (SDK) Paginators & Waiters.
- AWS Docs: *Lambda Developer Guide* – Lambda programming model (handler/event/context); Execution role; Resource-based policies.
- AWS FAQ: *AWS Lambda FAQs* (timeout, memory, runtimes).
- Khoá **Stephane Maarek (DVA-C02)** — phần AWS CLI/SDK & Lambda intro.
- Khoá **Adrian Cantrill (Developer Associate)** — phần Lambda fundamentals & credentials.

## ✅ Checklist hoàn thành Tuần 1
- [ ] Hoàn thành 4 buổi A/B/C/D
- [ ] Đọc thuộc credential provider chain (đúng thứ tự)
- [ ] Tạo & invoke `Lambda` bằng cả 3 cách (Console/CLI/SDK)
- [ ] Xem được log function trong `CloudWatch Logs`
- [ ] Viết được đoạn SDK có retry/backoff/jitter
- [ ] Phân biệt được execution role vs resource-based policy
- [ ] Ghi sổ câu sai + lên lịch spaced repetition (1/3/7 ngày)
- [ ] Vượt Cổng tự kiểm tra
