# 🧪 Hands-on Labs — Tuần 7: `KMS` + `Secrets Manager`/`Parameter Store` + Encryption

> Lab cầm tay chỉ việc, chạy được trên tài khoản AWS thật (Free Tier). LUÔN chạy phần Dọn dẹp cuối mỗi lab.
> ⚙️ Yêu cầu chung: đã cấu hình `AWS CLI v2` (xem Lab 1.1 tuần 1) + IAM đủ quyền cho `KMS`/`Secrets Manager`/`SSM`/`S3`/`Lambda`/`IAM`.
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

> 🧠 **2 con số phải khắc cốt tuần này:**
> - `KMS` `Encrypt`/`Decrypt` trực tiếp: tối đa **4 KB**. Lớn hơn → **envelope encryption** (`GenerateDataKey`).
> - Customer managed CMK tồn tại trong account là **có phí ~$1/tháng** (prorate theo giờ). Vì vậy các lab dưới đây **tái dùng CHUNG 1 CMK** `alias/dva-week7` (tạo ở Lab 7.1), và chỉ **huỷ key ở Lab 7.5** (lab cuối dùng key).
>
> 🧠 **Đọc secret từ `Lambda` (Lab 7.3 & 7.4):** `Lambda` KHÔNG hard-code credential — nó lấy quyền qua **execution role (IAM)** rồi gọi SDK (`boto3`) lúc **runtime**. Env var chỉ chứa **TÊN** secret/param, không chứa giá trị.

---

## Lab 7.1 — Tạo `KMS` CMK + `encrypt`/`decrypt` dữ liệu ≤ 4 KB (CLI)
**🎯 Mục tiêu:** Tạo customer managed key (CMK) đối xứng, mã hoá/giải mã một chuỗi nhỏ **hoàn toàn qua API `KMS`**, xem key policy mặc định, và **tự tay chứng minh** giới hạn 4 KB.
**🧩 Luyện kỹ năng (liên quan đề):**
- Task 2.2 (encryption at rest): tạo & dùng CMK, phân biệt 3 loại key.
- Nắm luồng `Encrypt` → `CiphertextBlob` → `Decrypt` (key material **không rời** `KMS`).
- Đọc key policy = resource-based policy **bắt buộc** của mỗi key.

**⏱️ ~20 phút** · **Yêu cầu trước:** đã làm phần Chuẩn bị chung.

### Các bước
1. Tạo CMK (symmetric, mặc định) + alias thân thiện.
   ```bash
   KEY_ID=$(aws kms create-key \
     --description "dva-week7-cmk" \
     --key-usage ENCRYPT_DECRYPT \
     --key-spec SYMMETRIC_DEFAULT \
     --query KeyMetadata.KeyId --output text)
   echo "KeyId: $KEY_ID"

   aws kms create-alias --alias-name alias/dva-week7 --target-key-id "$KEY_ID"
   ```

2. Mã hoá một chuỗi nhỏ (≤ 4 KB). Ghi ciphertext ra file nhị phân.
   ```bash
   printf 'top-secret-token-123' > plain.txt
   aws kms encrypt --key-id alias/dva-week7 \
     --plaintext fileb://plain.txt \
     --query CiphertextBlob --output text | base64 --decode > secret.enc
   ```

3. Giải mã ngược lại — plaintext key **không bao giờ** xuất hiện ở client, mọi thao tác diễn ra trong `KMS`.
   ```bash
   aws kms decrypt --ciphertext-blob fileb://secret.enc \
     --key-id alias/dva-week7 \
     --query Plaintext --output text | base64 --decode; echo
   # -> in ra: top-secret-token-123
   ```

4. Xem **key policy** mặc định (resource-based policy gắn liền key).
   ```bash
   aws kms get-key-policy --key-id "$KEY_ID" --policy-name default --output text
   ```

5. **Chứng minh giới hạn 4 KB:** tạo file 5 KB rồi thử `encrypt` trực tiếp → LỖI.
   ```bash
   head -c 5000 /dev/urandom > big.bin
   aws kms encrypt --key-id alias/dva-week7 --plaintext fileb://big.bin
   # -> ValidationException: '1' ... member must have length less than or equal to 4096
   ```

### ✅ Kiểm chứng
- Bước 3 in đúng chuỗi gốc `top-secret-token-123`.
- Bước 4 thấy JSON policy có statement `"Sid": "Enable IAM User Permissions"` cho principal `root` account.
- Bước 5 báo lỗi độ dài > 4096 bytes → đây chính là lý do phải dùng envelope encryption ở Lab 7.2.

### 🧹 Dọn dẹp (tránh tính phí)
> ⚠️ **Chỉ chạy phần huỷ key SAU KHI xong Lab 7.2, 7.4, 7.5** — vì các lab đó tái dùng `alias/dva-week7`. Việc huỷ key nằm ở cuối **Lab 7.5**. Ở đây chỉ dọn file tạm:
```bash
rm -f plain.txt secret.enc big.bin
```

### 🧠 Ý nghĩa với đề thi
- `KMS` symmetric key: dùng 1 key cho cả mã hoá + giải mã, **key material không bao giờ rời `KMS`** dưới dạng plaintext.
- **Key policy** là chốt chặn cuối cùng: thiếu nó thì IAM policy cũng vô dụng. Statement `Enable IAM User Permissions` cho phép account uỷ quyền tiếp qua IAM.
- Giới hạn **4 KB** của `Encrypt`/`Decrypt` là bẫy kinh điển → dữ liệu lớn phải chuyển sang envelope.
- CMK **có phí tháng** (khác AWS managed key `aws/<service>` không mất phí tồn tại) → nhớ `schedule-key-deletion`.

---

## Lab 7.2 — Envelope encryption với `GenerateDataKey` (script `boto3` + `cryptography`)
**🎯 Mục tiêu:** Mã hoá một file **1 MB** (vượt xa 4 KB) bằng đúng luồng envelope: xin data key, mã hoá payload **cục bộ**, lưu **kèm** data key đã mã hoá; rồi giải mã ngược. Hiểu vì sao > 4 KB **bắt buộc** dùng envelope.
**🧩 Luyện kỹ năng (liên quan đề):**
- Task 2.2: mô tả & thực hiện đúng 5 bước envelope encryption.
- Chỉ gọi `KMS` **1 lần** cho data key (32 bytes), payload mã hoá offline → không đụng giới hạn 4 KB, không phụ thuộc kích thước file.
- `GenerateDataKey` trả về **cả** plaintext key **và** encrypted key.

**⏱️ ~25 phút** · **Yêu cầu trước:** đã tạo CMK `alias/dva-week7` (Lab 7.1); có `python3` + `pip`.

### Các bước
1. Cài thư viện mã hoá cục bộ.
   ```bash
   pip install boto3 cryptography
   ```

2. Viết script envelope (mã hoá + giải mã). Lưu là `envelope.py`.
   ```python
   # envelope.py — envelope encryption thủ công với AWS KMS
   import boto3, os, sys
   from cryptography.hazmat.primitives.ciphers.aead import AESGCM

   KEY_ALIAS = "alias/dva-week7"
   kms = boto3.client("kms")

   def encrypt(infile, outfile):
       # (1) Xin data key: nhận plaintext key + encrypted key (bọc bởi CMK)
       resp = kms.generate_data_key(KeyId=KEY_ALIAS, KeySpec="AES_256")
       plaintext_key = resp["Plaintext"]        # 32 bytes -> CHỈ dùng trong RAM
       encrypted_key = resp["CiphertextBlob"]   # lưu KÈM dữ liệu, an toàn để ghi ra đĩa

       # (2) Mã hoá file CỤC BỘ bằng plaintext key — KHÔNG gọi KMS cho payload
       data = open(infile, "rb").read()
       nonce = os.urandom(12)
       ciphertext = AESGCM(plaintext_key).encrypt(nonce, data, None)

       # (3) Lưu định dạng: [4B len][encrypted_key][12B nonce][ciphertext]
       with open(outfile, "wb") as f:
           f.write(len(encrypted_key).to_bytes(4, "big"))
           f.write(encrypted_key)
           f.write(nonce)
           f.write(ciphertext)

       # (4) Xoá plaintext key khỏi bộ nhớ ngay
       del plaintext_key
       print(f"Đã mã hoá {len(data)} bytes -> {outfile}")

   def decrypt(infile, outfile):
       blob = open(infile, "rb").read()
       n = int.from_bytes(blob[:4], "big")
       encrypted_key = blob[4:4 + n]
       nonce = blob[4 + n:4 + n + 12]
       ciphertext = blob[4 + n + 12:]

       # (5) Gọi KMS Decrypt để lấy lại plaintext key -> giải mã payload cục bộ
       plaintext_key = kms.decrypt(CiphertextBlob=encrypted_key)["Plaintext"]
       data = AESGCM(plaintext_key).decrypt(nonce, ciphertext, None)
       open(outfile, "wb").write(data)
       del plaintext_key
       print(f"Đã giải mã -> {outfile} ({len(data)} bytes)")

   if __name__ == "__main__":
       mode, src, dst = sys.argv[1], sys.argv[2], sys.argv[3]
       (encrypt if mode == "encrypt" else decrypt)(src, dst)
   ```

3. Tạo file lớn 1 MB rồi chạy mã hoá + giải mã.
   ```bash
   head -c 1048576 /dev/urandom > bigfile.bin      # 1 MB, vượt xa 4 KB
   python3 envelope.py encrypt bigfile.bin bigfile.enc
   python3 envelope.py decrypt bigfile.enc bigfile.out
   ```

### ✅ Kiểm chứng
- File giải mã trùng khớp byte-by-byte với file gốc:
  ```bash
  cmp bigfile.bin bigfile.out && echo "MATCH ✅ (envelope round-trip OK)"
  ```
- File `bigfile.enc` chứa data key đã mã hoá **kèm** ciphertext → có thể lưu/gửi an toàn; muốn giải mã phải gọi lại `KMS` `Decrypt` trên data key.

### 🧹 Dọn dẹp
```bash
rm -f envelope.py bigfile.bin bigfile.enc bigfile.out
# CMK giữ lại cho Lab 7.4 & 7.5 — huỷ ở cuối Lab 7.5.
```

### 🧠 Ý nghĩa với đề thi
- **Vì sao cần envelope khi > 4 KB:** không gửi payload lớn cho `KMS` (chặn ở 4 KB), chỉ gửi **32-byte data key**. Payload mã hoá bằng `AES-256` **cục bộ** → không giới hạn kích thước, ít cuộc gọi API, rẻ.
- `GenerateDataKey` trả **plaintext key** (mã hoá dữ liệu) + **encrypted key** (lưu kèm). Sau khi dùng xong → **xoá plaintext key**.
- Đây chính là cơ chế `S3 SSE-KMS`, `EBS`, `RDS`, `DynamoDB` dùng ngầm bên dưới.
- Bẫy đề: "mã hoá file 1 MB / dữ liệu lớn" mà chọn gọi `KMS` `Encrypt` trực tiếp là **SAI** → phải envelope.

---

## Lab 7.3 — Đọc secret `Secrets Manager` từ `Lambda` (không hard-code) ⭐
**🎯 Mục tiêu:** Lưu DB credentials vào `Secrets Manager`, rồi `Lambda` **lấy credential lúc runtime** qua `boto3` với quyền `secretsmanager:GetSecretValue` — source code KHÔNG chứa password.
**🧩 Luyện kỹ năng (liên quan đề):**
- Task 2.3 (quản lý dữ liệu nhạy cảm): thay hard-coded credential bằng runtime retrieval.
- `Lambda` execution role gắn quyền cụ thể `secretsmanager:GetSecretValue` trên đúng secret ARN (least privilege).
- Sanitize log: ghi ra `CloudWatch` nhưng **KHÔNG** log password.
- Khái niệm rotation tự động (Lambda) — điểm mạnh riêng của `Secrets Manager`.

**⏱️ ~30 phút** · **Yêu cầu trước:** đã làm phần Chuẩn bị chung.

### Các bước
1. Tạo secret (JSON DB creds). Mặc định mã hoá bằng AWS managed key `aws/secretsmanager` (**miễn phí**).
   ```bash
   SECRET_ARN=$(aws secretsmanager create-secret \
     --name prod/dva-week7/db-creds \
     --description "DVA week7 demo DB creds" \
     --secret-string '{"username":"appuser","password":"P@ssw0rd-Demo!","host":"db.internal","port":3306}' \
     --query ARN --output text)
   echo "$SECRET_ARN"
   ```

2. *(TUỲ CHỌN)* Bật **automatic rotation**. Rotation thật cần 1 Lambda rotation function riêng (dễ nhất là dùng blueprint trong Console: secret → **Rotation** → chọn RDS/DB + lịch xoay). CLI khi đã có rotation Lambda:
   ```bash
   # aws secretsmanager rotate-secret --secret-id "$SECRET_ARN" \
   #   --rotation-lambda-arn <ROTATION_LAMBDA_ARN> \
   #   --rotation-rules AutomaticallyAfterDays=30
   ```
   > Trong lúc rotate quan sát staging labels: `AWSCURRENT` (đang dùng) → `AWSPENDING` (bản mới) → sau khi finish thành `AWSCURRENT`, bản cũ thành `AWSPREVIOUS`.

3. Tạo execution role cho `Lambda` (basic logging) + gắn quyền đọc **đúng** secret.
   ```bash
   cat > trust-lambda.json <<'EOF'
   { "Version": "2012-10-17",
     "Statement": [{ "Effect": "Allow",
       "Principal": { "Service": "lambda.amazonaws.com" },
       "Action": "sts:AssumeRole" }] }
   EOF

   aws iam create-role --role-name lab7-secrets-role \
     --assume-role-policy-document file://trust-lambda.json
   aws iam attach-role-policy --role-name lab7-secrets-role \
     --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

   cat > secrets-read-policy.json <<EOF
   { "Version": "2012-10-17",
     "Statement": [{ "Effect": "Allow",
       "Action": "secretsmanager:GetSecretValue",
       "Resource": "$SECRET_ARN" }] }
   EOF
   aws iam put-role-policy --role-name lab7-secrets-role \
     --policy-name read-db-secret --policy-document file://secrets-read-policy.json

   ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/lab7-secrets-role"
   ```
   > Nếu secret được mã hoá bằng **customer managed key** (không phải `aws/secretsmanager`), phải thêm quyền `kms:Decrypt` trên key đó.

4. Viết handler đọc secret lúc runtime — env var chỉ chứa **TÊN** secret, KHÔNG chứa password.
   ```python
   # secret_handler.py
   import boto3, json, os

   sm = boto3.client("secretsmanager")
   SECRET_NAME = os.environ["SECRET_NAME"]   # chỉ là tên, không phải giá trị

   def handler(event, context):
       resp = sm.get_secret_value(SecretId=SECRET_NAME)
       creds = json.loads(resp["SecretString"])
       # ... dùng creds["username"] / creds["password"] để kết nối DB ...
       # KHÔNG BAO GIỜ log password:
       print(f"OK — lấy creds cho user={creds['username']} host={creds['host']}")
       return {"user": creds["username"], "connected": True}
   ```

5. Đóng gói + tạo function, truyền tên secret qua env var.
   ```bash
   zip secret_fn.zip secret_handler.py
   aws lambda create-function --function-name lab7-read-secret \
     --runtime python3.12 --handler secret_handler.handler \
     --role "$ROLE_ARN" --zip-file fileb://secret_fn.zip --timeout 15 \
     --environment "Variables={SECRET_NAME=prod/dva-week7/db-creds}"
   aws lambda wait function-active-v2 --function-name lab7-read-secret
   ```
   > IAM role vừa tạo cần vài giây để propagate — nếu invoke báo AccessDenied, đợi ~10s rồi thử lại.

6. Invoke và đọc kết quả.
   ```bash
   aws lambda invoke --function-name lab7-read-secret --payload '{}' \
     --cli-binary-format raw-in-base64-out out.json
   cat out.json; echo
   ```

### ✅ Kiểm chứng
- `out.json` trả `{"user": "appuser", "connected": true}`.
- Log `CloudWatch` có dòng `OK — lấy creds cho user=appuser ...` nhưng **KHÔNG** thấy password:
  ```bash
  aws logs tail /aws/lambda/lab7-read-secret --since 5m
  ```
- Source code (`secret_handler.py`) hoàn toàn không chứa password → đạt mục tiêu "no hard-code".

### 🧹 Dọn dẹp
```bash
aws lambda delete-function --function-name lab7-read-secret
aws iam delete-role-policy --role-name lab7-secrets-role --policy-name read-db-secret
aws iam detach-role-policy --role-name lab7-secrets-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
aws iam delete-role --role-name lab7-secrets-role
aws secretsmanager delete-secret --secret-id "$SECRET_ARN" \
  --force-delete-without-recovery
rm -f secret_handler.py secret_fn.zip trust-lambda.json secrets-read-policy.json out.json
```

### 🧠 Ý nghĩa với đề thi
- Mô hình chuẩn "no hard-coded credential": app/`Lambda` lấy quyền qua **IAM role**, gọi `GetSecretValue` lúc **runtime**; rotate credential **không cần deploy lại** app.
- `Secrets Manager` điểm mạnh nhất = **automatic rotation built-in bằng Lambda** + tích hợp sẵn `RDS`/`Redshift`/`DocumentDB` → keyword "tự động xoay credential DB" chọn nó.
- Secret **luôn mã hoá bằng `KMS`**; dùng `aws/secretsmanager` là miễn phí, dùng CMK riêng thì trả phí `KMS`.
- Bẫy: chọn `Parameter Store` cho "auto-rotate DB creds" là **SAI** (Parameter Store không có rotation dựng sẵn).

---

## Lab 7.4 — `Parameter Store` SecureString đọc từ `Lambda` + so với `Secrets Manager` ⭐
**🎯 Mục tiêu:** Lưu một giá trị nhạy cảm dạng `SecureString` (mã hoá bằng CMK), đọc bằng `--with-decryption`, rồi cho `Lambda` đọc lúc runtime với quyền `ssm:GetParameter` + `kms:Decrypt`. So sánh chi phí/độ phù hợp với `Secrets Manager`.
**🧩 Luyện kỹ năng (liên quan đề):**
- Task 2.3: lưu config/secret đơn giản, mã hoá, **standard tier miễn phí**.
- Bẫy CLI kinh điển: thiếu `--with-decryption` chỉ nhận ciphertext, không có plaintext.
- SecureString dùng `KMS` → role cần `kms:Decrypt` trên key.
- Ra quyết định `Secrets Manager` vs `Parameter Store` từ keyword.

**⏱️ ~25 phút** · **Yêu cầu trước:** đã tạo CMK `alias/dva-week7` (Lab 7.1).

### Các bước
1. Ghi một `SecureString` param, mã hoá bằng CMK của Lab 7.1.
   ```bash
   aws ssm put-parameter \
     --name /dva-week7/app/db-password \
     --type SecureString \
     --value "P@ssw0rd-From-SSM!" \
     --key-id alias/dva-week7
   # (Bỏ --key-id thì SSM dùng AWS managed key alias/aws/ssm — cũng miễn phí ở standard tier)
   ```

2. Chứng minh bẫy `--with-decryption`.
   ```bash
   # KHÔNG có cờ -> nhận ciphertext (metadata mã hoá)
   aws ssm get-parameter --name /dva-week7/app/db-password \
     --query Parameter.Value --output text
   # CÓ cờ -> nhận plaintext
   aws ssm get-parameter --name /dva-week7/app/db-password --with-decryption \
     --query Parameter.Value --output text
   ```

3. Lấy ARN của CMK (để cấp quyền `kms:Decrypt` cho `Lambda`), rồi tạo role.
   ```bash
   KEY_ARN=$(aws kms describe-key --key-id alias/dva-week7 \
     --query KeyMetadata.Arn --output text)

   cat > trust-lambda.json <<'EOF'
   { "Version": "2012-10-17",
     "Statement": [{ "Effect": "Allow",
       "Principal": { "Service": "lambda.amazonaws.com" },
       "Action": "sts:AssumeRole" }] }
   EOF

   aws iam create-role --role-name lab7-ssm-role \
     --assume-role-policy-document file://trust-lambda.json
   aws iam attach-role-policy --role-name lab7-ssm-role \
     --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

   cat > ssm-read-policy.json <<EOF
   { "Version": "2012-10-17",
     "Statement": [
       { "Effect": "Allow", "Action": "ssm:GetParameter",
         "Resource": "arn:aws:ssm:${AWS_REGION}:${ACCOUNT_ID}:parameter/dva-week7/app/db-password" },
       { "Effect": "Allow", "Action": "kms:Decrypt", "Resource": "$KEY_ARN" }
     ] }
   EOF
   aws iam put-role-policy --role-name lab7-ssm-role \
     --policy-name read-secure-param --policy-document file://ssm-read-policy.json

   ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/lab7-ssm-role"
   ```

4. Handler đọc SecureString lúc runtime (`WithDecryption=True`), KHÔNG log giá trị.
   ```python
   # param_handler.py
   import boto3, os

   ssm = boto3.client("ssm")
   PARAM_NAME = os.environ["PARAM_NAME"]   # chỉ là tên param

   def handler(event, context):
       resp = ssm.get_parameter(Name=PARAM_NAME, WithDecryption=True)
       value = resp["Parameter"]["Value"]
       print(f"OK — đọc SecureString, len(value)={len(value)} (KHÔNG log giá trị)")
       return {"ok": True, "length": len(value)}
   ```

5. Đóng gói + tạo function + invoke.
   ```bash
   zip param_fn.zip param_handler.py
   aws lambda create-function --function-name lab7-read-param \
     --runtime python3.12 --handler param_handler.handler \
     --role "$ROLE_ARN" --zip-file fileb://param_fn.zip --timeout 15 \
     --environment "Variables={PARAM_NAME=/dva-week7/app/db-password}"
   aws lambda wait function-active-v2 --function-name lab7-read-param

   aws lambda invoke --function-name lab7-read-param --payload '{}' \
     --cli-binary-format raw-in-base64-out out.json
   cat out.json; echo
   ```

### ✅ Kiểm chứng
- Bước 2: không có `--with-decryption` trả về chuỗi mã hoá; có cờ trả về `P@ssw0rd-From-SSM!`.
- `out.json` trả `{"ok": true, "length": 18}` → `Lambda` giải mã được nhờ `kms:Decrypt`.
- Bỏ statement `kms:Decrypt` khỏi role → invoke sẽ `AccessDeniedException` khi giải mã (chứng minh SecureString phụ thuộc quyền `KMS`).

### 🧹 Dọn dẹp
```bash
aws lambda delete-function --function-name lab7-read-param
aws iam delete-role-policy --role-name lab7-ssm-role --policy-name read-secure-param
aws iam detach-role-policy --role-name lab7-ssm-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
aws iam delete-role --role-name lab7-ssm-role
aws ssm delete-parameter --name /dva-week7/app/db-password
rm -f param_handler.py param_fn.zip trust-lambda.json ssm-read-policy.json out.json
# CMK giữ lại cho Lab 7.5.
```

### 🧠 Ý nghĩa với đề thi — `Parameter Store` vs `Secrets Manager`
| Tiêu chí | `Parameter Store` (SecureString) | `Secrets Manager` |
|---|---|---|
| Chi phí | **Standard tier MIỄN PHÍ** | **Tính phí** (~mỗi secret + mỗi 10k API call) |
| Rotation tự động | ❌ không dựng sẵn | ✅ built-in bằng Lambda |
| Tích hợp DB | ❌ | ✅ `RDS`/`Redshift`/`DocumentDB` |
| Mã hoá | chỉ `SecureString` (KMS) | luôn mã hoá (KMS) |
| Hợp nhất khi | config/secret **đơn giản, không cần rotate, tiết kiệm** | credential DB **cần auto-rotate / cross-account** |

- Phản xạ: "lưu config/secret đơn giản, rẻ, không rotate" → **`Parameter Store` standard**; "tự động rotate credential DB" → **`Secrets Manager`**.
- Bẫy CLI: quên `--with-decryption` → tưởng đọc sai/giá trị bị mã hoá.

---

## Lab 7.5 — `S3` SSE-KMS: mã hoá object bằng CMK + so với SSE-S3
**🎯 Mục tiêu:** Upload object với `--server-side-encryption aws:kms --ssekms-key-id`, xác minh header mã hoá; upload thêm 1 object SSE-S3 để so sánh SSE-S3 (mặc định) vs SSE-KMS (audit `CloudTrail` + kiểm soát/rotation key).
**🧩 Luyện kỹ năng (liên quan đề):**
- Task 2.2: encryption at rest cho `S3`, chọn đúng loại SSE.
- Phân biệt SSE-S3 (`AES256`, AWS quản key) vs SSE-KMS (CMK, audit + kiểm soát).
- `S3 Bucket Keys` để giảm số cuộc gọi `KMS` (giảm chi phí).

**⏱️ ~20 phút** · **Yêu cầu trước:** đã tạo CMK `alias/dva-week7` (Lab 7.1). **Đây là lab CUỐI dùng CMK → phần dọn dẹp sẽ huỷ key.**

### Các bước
1. Tạo bucket (tên phải toàn cầu duy nhất).
   ```bash
   BUCKET="dva-week7-ssekms-${ACCOUNT_ID}"
   aws s3api create-bucket --bucket "$BUCKET" \
     --region "$AWS_REGION" \
     --create-bucket-configuration LocationConstraint="$AWS_REGION"
   # LƯU Ý: nếu region là us-east-1 thì BỎ hẳn cờ --create-bucket-configuration.
   ```

2. Lấy ARN CMK rồi put object với **SSE-KMS**.
   ```bash
   KEY_ARN=$(aws kms describe-key --key-id alias/dva-week7 \
     --query KeyMetadata.Arn --output text)

   printf 'hello sse-kms' > obj.txt
   aws s3api put-object --bucket "$BUCKET" --key kms/obj.txt \
     --body obj.txt \
     --server-side-encryption aws:kms \
     --ssekms-key-id "$KEY_ARN"
   ```

3. Put một object khác bằng **SSE-S3** (`AES256`) để so sánh.
   ```bash
   aws s3api put-object --bucket "$BUCKET" --key s3/obj.txt \
     --body obj.txt \
     --server-side-encryption AES256
   ```

4. *(Tuỳ chọn)* Đặt **default encryption = SSE-KMS** cho cả bucket + bật **Bucket Key** (giảm chi phí `KMS`).
   ```bash
   aws s3api put-bucket-encryption --bucket "$BUCKET" \
     --server-side-encryption-configuration "{\"Rules\":[{\"ApplyServerSideEncryptionByDefault\":{\"SSEAlgorithm\":\"aws:kms\",\"KMSMasterKeyID\":\"$KEY_ARN\"},\"BucketKeyEnabled\":true}]}"
   ```

### ✅ Kiểm chứng
```bash
# Object SSE-KMS: thấy aws:kms + đúng KeyId
aws s3api head-object --bucket "$BUCKET" --key kms/obj.txt \
  --query '{SSE:ServerSideEncryption, KeyId:SSEKMSKeyId}'
# -> { "SSE": "aws:kms", "KeyId": "arn:aws:kms:...:key/..." }

# Object SSE-S3: chỉ thấy AES256, KHÔNG có KeyId
aws s3api head-object --bucket "$BUCKET" --key s3/obj.txt \
  --query '{SSE:ServerSideEncryption}'
# -> { "SSE": "AES256" }
```

### 🧹 Dọn dẹp
```bash
aws s3 rm "s3://$BUCKET" --recursive
aws s3api delete-bucket --bucket "$BUCKET"
rm -f obj.txt

# ✅ ĐÃ XONG mọi lab dùng CMK -> huỷ key (min 7 ngày, ngừng tính phí sau khi xoá)
aws kms delete-alias --alias-name alias/dva-week7
aws kms schedule-key-deletion --key-id "$KEY_ARN" --pending-window-in-days 7
```

### 🧠 Ý nghĩa với đề thi
- **SSE-S3** (`AES256`): AWS quản key hoàn toàn, đơn giản, miễn phí — dùng khi chỉ cần "mã hoá at rest" cơ bản.
- **SSE-KMS** (`aws:kms`): mã hoá bằng CMK → **audit từng lần dùng key qua `CloudTrail`**, tự **kiểm soát rotation & key policy**, giới hạn qua `kms:ViaService` → chọn khi cần compliance/audit/kiểm soát key.
- **SSE-C**: client tự cấp key trong mỗi request (AWS không lưu key).
- `S3 Bucket Keys` (`BucketKeyEnabled=true`): giảm số cuộc gọi `KMS` `GenerateDataKey`/`Decrypt` → tiết kiệm chi phí `KMS` khi ghi/đọc nhiều object.
- Bẫy: cần "audit ai đã giải mã object / tự rotate key" → SSE-KMS, KHÔNG phải SSE-S3.

---

> ✅ Xong 5 lab? Đối chiếu lại [Lab checklist trong README](README.md#-lab-checklist), rồi làm [bộ câu hỏi luyện tập](questions.md) và **MINI-MOCK Domain 1+2 (~30 câu)** — phải đạt **≥72%** trước khi sang [Tuần 8](../week-08/README.md).
