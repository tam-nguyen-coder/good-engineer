# 🧪 Hands-on Labs — Tuần 6: Security I — `IAM` + `STS` + `Cognito`

> Lab cầm tay chỉ việc, chạy được trên tài khoản AWS thật (Free Tier). LUÔN chạy phần Dọn dẹp cuối mỗi lab.
> ⚙️ Yêu cầu chung: đã cấu hình `AWS CLI v2` (xem Lab 1.1 tuần 1) + IAM đủ quyền cho dịch vụ trong lab.
> Về [plan tuần](README.md) · [Câu hỏi luyện tập](questions.md) · [Kế hoạch tổng](../../DVA-C02-STUDY-PLAN.md)

---

## 🔧 Chuẩn bị chung (làm 1 lần, dùng cho mọi lab)

```bash
# 1) Đặt region — mặc định us-east-1 (đổi nếu bạn dùng region khác)
export AWS_REGION=us-east-1
export AWS_DEFAULT_REGION=$AWS_REGION

# 2) Lấy Account ID để dựng ARN
export ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "Account: $ACCOUNT_ID · Region: $AWS_REGION"

# 3) Cần jq để parse JSON credentials/token (macOS: brew install jq)
jq --version || echo "⚠️ Cài jq trước: brew install jq"
```

> 🧠 **Bản đồ danh tính tuần này** (đừng nhầm ba khối):
> - **`IAM` policy evaluation:** explicit **`Deny`** > explicit **`Allow`** > **implicit Deny**. Một `Deny` là chặn tuyệt đối. Thấy `Principal` trong JSON → **resource-based / trust policy**.
> - **`STS`** trả về **credentials TẠM THỜI** (access key + secret + **`SessionToken`** + `Expiration`). `AssumeRole` = đổi vai (same/cross-account); `AssumeRoleWithWebIdentity` = federation OIDC (chính là thứ `Cognito Identity Pool` gọi ngầm).
> - **`Cognito`:** `User Pool` = **authentication** → trả **JWT** (ID/Access/Refresh). `Identity Pool` = **authorization** → đổi JWT lấy **AWS credentials tạm** để gọi thẳng service. `User Pool` lo *bạn là ai*; `Identity Pool` lo *bạn được làm gì trên AWS*.

---

## Lab 6.1 — Viết `IAM` policy least-privilege + chứng minh explicit `Deny` thắng `Allow`
**🎯 Mục tiêu:** Viết một policy vừa có `Allow` rộng (`s3:*` trên 1 bucket) vừa có `Deny` hẹp (chặn xóa), rồi DÙNG IAM Policy Simulator (CLI) chứng minh: ghi/đọc được nhưng **xóa bị chặn tuyệt đối** dù có `Allow` rộng — và action không khai báo là **implicit Deny**.
**🧩 Luyện kỹ năng (liên quan đề):**
- Đọc policy JSON và nói ngay allowed/denied (task statement kinh điển của Domain 2).
- Chứng minh thứ tự đánh giá: explicit `Deny` > explicit `Allow` > implicit `Deny`.
- Least-privilege: `Allow` đúng cái cần, `Deny` chặn cái nguy hiểm (delete).

**⏱️ ~20 phút** · **Yêu cầu trước:** đã làm phần Chuẩn bị chung. Không tạo tài nguyên tính phí (chỉ mô phỏng).

### Các bước
1. Viết policy có **Allow rộng** + **Deny hẹp** (thay `<YOUR_BUCKET>` bằng tên bucket bất kỳ, không cần tồn tại thật vì ta chỉ mô phỏng).
   ```bash
   cat > s3-allow-deny.json <<'EOF'
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Sid": "AllowFullBucketAccess",
         "Effect": "Allow",
         "Action": "s3:*",
         "Resource": [
           "arn:aws:s3:::my-lab-bucket",
           "arn:aws:s3:::my-lab-bucket/*"
         ]
       },
       {
         "Sid": "DenyDeletes",
         "Effect": "Deny",
         "Action": ["s3:DeleteObject", "s3:DeleteBucket"],
         "Resource": "*"
       }
     ]
   }
   EOF
   ```
2. Chạy **IAM Policy Simulator** bằng CLI để đánh giá nhiều action cùng lúc trên tài nguyên bucket:
   ```bash
   aws iam simulate-custom-policy \
     --policy-input-list file://s3-allow-deny.json \
     --action-names s3:PutObject s3:GetObject s3:DeleteObject dynamodb:PutItem \
     --resource-arns "arn:aws:s3:::my-lab-bucket/*" \
     --query 'EvaluationResults[*].{Action:EvalActionName,Decision:EvalDecision,DecidedBy:MatchedStatements[0].SourcePolicyId}' \
     --output table
   ```
3. Đọc kết quả — phải thấy đúng như sau:
   - `s3:PutObject` → **allowed** (khớp `Allow` rộng).
   - `s3:GetObject` → **allowed** (khớp `Allow` rộng).
   - `s3:DeleteObject` → **explicitDeny** ← *đây là điểm chứng minh: có `s3:*` Allow nhưng vẫn bị chặn vì có `Deny` hẹp.*
   - `dynamodb:PutItem` → **implicitDeny** (không statement nào cấp → mặc định từ chối).
4. (Tuỳ chọn — bản console) Mở **IAM → Policy Simulator** (https://policysim.aws.amazon.com), dán policy trên, chọn service `S3`, tick `DeleteObject`, bấm **Run Simulation** → cột **Permission = denied**, click để xem **statement `DenyDeletes`** là cái quyết định.

### ✅ Kiểm chứng
- Bảng CLI in ra 4 dòng: 2 `allowed`, 1 `explicitDeny` (DeleteObject), 1 `implicitDeny` (dynamodb). Nếu `DeleteObject` mà ra `allowed` → bạn quên statement `Deny` hoặc để nó cấp quyền rộng hơn.

### 🧹 Dọn dẹp (tránh tính phí)
```bash
rm -f s3-allow-deny.json   # Lab này KHÔNG tạo tài nguyên AWS -> không tốn phí, không cần xoá gì trên AWS
```

### 🧠 Ý nghĩa với đề thi
- **explicit `Deny` > explicit `Allow` > implicit `Deny`** — chỉ một `Deny` là chặn, bất kể bao nhiêu `Allow`.
- Action không được cấp = **implicit Deny** (không phải "mặc định cho phép").
- `simulate-custom-policy` / `simulate-principal-policy` là cách kiểm chứng quyền **không cần đụng tài nguyên thật** — an toàn và hay được nhắc.

---

## Lab 6.2 — `STS` `AssumeRole`: đổi vai lấy credentials tạm ⭐
**🎯 Mục tiêu:** Tạo một IAM role tin cậy chính tài khoản của bạn, gọi `aws sts assume-role`, export **temporary credentials**, dùng chúng gọi `S3`, và quan sát tận mắt **`SessionToken` + thời điểm hết hạn**.
**🧩 Luyện kỹ năng (liên quan đề):**
- `AssumeRole` → credentials TẠM THỜI (key + secret + **session token**), không phải key vĩnh viễn.
- **Trust policy** (có `Principal`) quyết định AI được assume — đóng vai resource-based policy của role.
- `DurationSeconds` mặc định **3600s**, min **900s**; role chaining giới hạn tối đa **1 giờ**.

**⏱️ ~25 phút** · **Yêu cầu trước:** Chuẩn bị chung + có `jq`.

### Các bước
1. Viết **trust policy** cho role, tin cậy chính account của bạn (any principal trong account có quyền `sts:AssumeRole`).
   ```bash
   cat > trust-policy.json <<EOF
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Principal": { "AWS": "arn:aws:iam::${ACCOUNT_ID}:root" },
         "Action": "sts:AssumeRole"
       }
     ]
   }
   EOF
   ```
   > 💡 Muốn mô phỏng **cross-account**: đổi `Principal.AWS` thành `arn:aws:iam::<ACCOUNT_A>:root` và ở account A user phải có quyền `sts:AssumeRole` với ARN role này. Muốn ép **MFA**: thêm `"Condition": {"Bool": {"aws:MultiFactorAuthPresent": "true"}}` rồi truyền `--serial-number` + `--token-code` khi assume.
2. Tạo role, gắn quyền least-privilege (chỉ đọc `S3`), lấy ARN.
   ```bash
   aws iam create-role --role-name Lab62-STSDemo \
     --assume-role-policy-document file://trust-policy.json

   aws iam attach-role-policy --role-name Lab62-STSDemo \
     --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess

   export ROLE_ARN=$(aws iam get-role --role-name Lab62-STSDemo --query Role.Arn --output text)
   echo "$ROLE_ARN"
   ```
3. Gọi `assume-role` và xem nguyên response (chú ý `SessionToken` dài + `Expiration`).
   ```bash
   aws sts assume-role \
     --role-arn "$ROLE_ARN" \
     --role-session-name demo-session \
     --duration-seconds 900
   # Response: Credentials { AccessKeyId, SecretAccessKey, SessionToken, Expiration }
   ```
4. Lưu credentials 1 lần rồi **export** 3 biến môi trường (đây là cách "dùng" creds tạm).
   ```bash
   CREDS=$(aws sts assume-role --role-arn "$ROLE_ARN" \
     --role-session-name demo-session --duration-seconds 900 \
     --query Credentials --output json)

   export AWS_ACCESS_KEY_ID=$(echo "$CREDS" | jq -r .AccessKeyId)
   export AWS_SECRET_ACCESS_KEY=$(echo "$CREDS" | jq -r .SecretAccessKey)
   export AWS_SESSION_TOKEN=$(echo "$CREDS" | jq -r .SessionToken)

   echo "Hết hạn lúc: $(echo "$CREDS" | jq -r .Expiration)"   # ~15 phút nữa (duration=900)
   ```
5. Kiểm tra danh tính đã đổi + dùng creds gọi service.
   ```bash
   aws sts get-caller-identity   # Arn giờ là .../assumed-role/Lab62-STSDemo/demo-session
   aws s3 ls                     # OK — role có quyền đọc S3
   aws iam list-users            # ❌ AccessDenied — role KHÔNG có quyền IAM (least-privilege)
   ```

### ✅ Kiểm chứng
- `get-caller-identity` đổi từ user của bạn sang `assumed-role/Lab62-STSDemo/demo-session`.
- `aws s3 ls` chạy được nhưng `aws iam list-users` bị `AccessDenied` → đúng least-privilege.
- Trường `Expiration` cho thấy creds là **tạm thời**; chờ >15 phút rồi gọi lại → `ExpiredToken`.

### 🧹 Dọn dẹp (tránh tính phí)
```bash
# Trả lại danh tính gốc (bỏ creds tạm khỏi shell)
unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN
aws sts get-caller-identity   # đã về user gốc

aws iam detach-role-policy --role-name Lab62-STSDemo \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess
aws iam delete-role --role-name Lab62-STSDemo
rm -f trust-policy.json
```

### 🧠 Ý nghĩa với đề thi
- Mọi API `STS` trả credentials TẠM THỜI có **`SessionToken`** — nhúng key vĩnh viễn vào code là SAI, dùng role để nhận creds tạm.
- Cross-account: account đích tạo role có **trust policy** cho account nguồn; user nguồn cần quyền `sts:AssumeRole`.
- `DurationSeconds`: 900s–43200s (chặn trên bởi max session của role), mặc định 3600s; **role chaining ⇒ tối đa 1 giờ**.

---

## Lab 6.3 — `Cognito User Pool`: đăng nhập lấy `JWT` (ID/Access/Refresh) ⭐
**🎯 Mục tiêu:** Dựng một `User Pool` + app client, tạo user, dùng `admin-initiate-auth` / `initiate-auth` để lấy **3 JWT**, rồi **giải mã** token xem claims (`sub`, `aud`, `token_use`, `exp`…).
**🧩 Luyện kỹ năng (liên quan đề):**
- `User Pool` = **authentication** → trả **JWT** (ID / Access / Refresh); ID/Access token mặc định hết hạn **1 giờ**.
- Phân biệt `admin-initiate-auth` (server-side, cần quyền admin) vs `initiate-auth` (client-side, không lộ secret).
- Đọc claims: `token_use=id` (ID token, kèm profile như email) vs `token_use=access` (Access token, kèm `scope`).

**⏱️ ~30 phút** · **Yêu cầu trước:** Chuẩn bị chung + `jq`.

### Các bước
1. Tạo `User Pool` với password policy.
   ```bash
   export POOL_ID=$(aws cognito-idp create-user-pool \
     --pool-name lab-userpool \
     --policies '{"PasswordPolicy":{"MinimumLength":8,"RequireUppercase":true,"RequireLowercase":true,"RequireNumbers":true,"RequireSymbols":false}}' \
     --query 'UserPool.Id' --output text)
   echo "Pool: $POOL_ID"
   ```
2. Tạo **app client** KHÔNG secret, bật các auth flow cần cho lab (ADMIN + USER_PASSWORD + REFRESH).
   ```bash
   export CLIENT_ID=$(aws cognito-idp create-user-pool-client \
     --user-pool-id "$POOL_ID" \
     --client-name lab-app-client \
     --no-generate-secret \
     --explicit-auth-flows ALLOW_ADMIN_USER_PASSWORD_AUTH ALLOW_USER_PASSWORD_AUTH ALLOW_REFRESH_TOKEN_AUTH \
     --query 'UserPoolClient.ClientId' --output text)
   echo "Client: $CLIENT_ID"
   ```
3. Tạo user và đặt **mật khẩu vĩnh viễn** (bỏ qua bước force-change để đăng nhập được ngay).
   ```bash
   aws cognito-idp admin-create-user \
     --user-pool-id "$POOL_ID" --username demo@example.com \
     --message-action SUPPRESS \
     --user-attributes Name=email,Value=demo@example.com Name=email_verified,Value=true

   aws cognito-idp admin-set-user-password \
     --user-pool-id "$POOL_ID" --username demo@example.com \
     --password 'Passw0rd!' --permanent
   ```
4. **Đăng nhập lấy JWT** — cách server-side (admin):
   ```bash
   aws cognito-idp admin-initiate-auth \
     --user-pool-id "$POOL_ID" --client-id "$CLIENT_ID" \
     --auth-flow ADMIN_USER_PASSWORD_AUTH \
     --auth-parameters USERNAME=demo@example.com,PASSWORD='Passw0rd!'
   # AuthenticationResult { IdToken, AccessToken, RefreshToken, ExpiresIn:3600, TokenType:"Bearer" }
   ```
   Cách client-side (không cần quyền admin — app mobile/web hay dùng):
   ```bash
   aws cognito-idp initiate-auth \
     --client-id "$CLIENT_ID" \
     --auth-flow USER_PASSWORD_AUTH \
     --auth-parameters USERNAME=demo@example.com,PASSWORD='Passw0rd!'
   ```
5. Lấy riêng **ID token** rồi **giải mã** phần payload (JWT = header.payload.signature, base64url).
   ```bash
   export ID_TOKEN=$(aws cognito-idp admin-initiate-auth \
     --user-pool-id "$POOL_ID" --client-id "$CLIENT_ID" \
     --auth-flow ADMIN_USER_PASSWORD_AUTH \
     --auth-parameters USERNAME=demo@example.com,PASSWORD='Passw0rd!' \
     --query 'AuthenticationResult.IdToken' --output text)
   ```
   Decode bằng Node.js (`base64url` của `Buffer` tự xử lý padding):
   ```javascript
   // decode_jwt.mjs — chạy: node decode_jwt.mjs "$ID_TOKEN"
   const payload = process.argv[2].split(".")[1];                        // JWT = header.payload.signature
   const claims = JSON.parse(Buffer.from(payload, "base64url").toString()); // "base64url" tự bù padding
   console.log(JSON.stringify(claims, null, 2));
   ```
   > 💡 Không cần tạo file cũng được — one-liner: `node -e 'console.log(Buffer.from(process.argv[1].split(".")[1],"base64url").toString())' "$ID_TOKEN"`
   ```bash
   node decode_jwt.mjs "$ID_TOKEN"        # runtime Node.js 24 có sẵn (không cần npm install)
   # Quan sát: "token_use":"id", "aud":<CLIENT_ID>, "iss":".../<POOL_ID>",
   #           "sub":<uuid>, "email":"demo@example.com", "exp" (=iat+3600)
   ```
   > 🖥️ **Hosted UI / Managed Login (tuỳ chọn):** thay vì gọi API, có thể bật giao diện đăng nhập sẵn của Cognito — tạo domain (`aws cognito-idp create-user-pool-domain --domain <prefix> --user-pool-id $POOL_ID`), thêm callback URL + OAuth scopes vào app client, rồi đăng nhập qua trình duyệt để nhận cùng bộ JWT qua OAuth redirect. `Hosted UI` = giao diện classic; **`Managed Login`** (2024) = bản mới no-code branding + passkey + dark mode (cần feature plan Essentials/Plus).

### ✅ Kiểm chứng
- `admin-initiate-auth` trả về đủ **IdToken + AccessToken + RefreshToken** với `ExpiresIn: 3600`.
- `decode_jwt.mjs` in ra claims: ID token có `token_use:"id"` + `email`; thử decode Access token sẽ thấy `token_use:"access"` + `scope` (khác nhau rõ giữa hai loại token).

### 🧹 Dọn dẹp (tránh tính phí)
```bash
# (Nếu định làm Lab 6.4 -> GIỮ LẠI $POOL_ID và $CLIENT_ID, dọn sau.)
# aws cognito-idp delete-user-pool-domain --domain <prefix> --user-pool-id "$POOL_ID"  # nếu đã tạo Hosted UI
aws cognito-idp delete-user-pool --user-pool-id "$POOL_ID"   # xoá luôn user + app client
rm -f decode_jwt.mjs
```

### 🧠 Ý nghĩa với đề thi
- "Đăng nhập app / cần **JWT** / user directory" → **`Cognito User Pool`** (authentication).
- 3 token: **ID** (danh tính người dùng, gửi cho app), **Access** (uỷ quyền gọi API theo scope), **Refresh** (xin token mới). ID/Access mặc định **1 giờ**, refresh cấu hình được.
- `User Pool` hỗ trợ MFA, federation (SAML/OIDC/social), groups, và **Lambda triggers** (Pre Token Generation, Post Confirmation…).

---

## Lab 6.4 — `Cognito Identity Pool`: đổi `JWT` lấy AWS credentials tạm ⭐
**🎯 Mục tiêu:** Liên kết `User Pool` (Lab 6.3) làm auth provider cho một `Identity Pool`, dùng `get-id` + `get-credentials-for-identity` đổi ID token lấy **temporary AWS credentials**, rồi dùng creds đó gọi **thẳng** `S3` — đúng kịch bản "client gọi trực tiếp AWS".
**🧩 Luyện kỹ năng (liên quan đề):**
- `Identity Pool` = **authorization** → temp AWS creds (ngầm gọi `AssumeRoleWithWebIdentity` tới `STS`), map vào IAM **authenticated role**.
- Luồng kết hợp kinh điển: `User Pool` (JWT) → `Identity Pool` → AWS creds → gọi service.
- Trust policy của authenticated role: `Principal.Federated = cognito-identity.amazonaws.com`, điều kiện `aud` = identity pool id + `amr` = `authenticated`.

**⏱️ ~35 phút** · **Yêu cầu trước:** **Lab 6.3 chưa dọn** (cần `$POOL_ID`, `$CLIENT_ID`) + `jq`.

### Các bước
1. Tạo `Identity Pool`, gắn `User Pool` làm authentication provider.
   ```bash
   export PROVIDER="cognito-idp.${AWS_REGION}.amazonaws.com/${POOL_ID}"

   export IDPOOL_ID=$(aws cognito-identity create-identity-pool \
     --identity-pool-name lab-identity-pool \
     --allow-unauthenticated-identities \
     --cognito-identity-providers ProviderName=${PROVIDER},ClientId=${CLIENT_ID} \
     --query 'IdentityPoolId' --output text)
   echo "Identity Pool: $IDPOOL_ID"
   ```
2. Tạo **authenticated role** với trust policy federation cho Cognito Identity.
   ```bash
   cat > cognito-trust.json <<EOF
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Principal": { "Federated": "cognito-identity.amazonaws.com" },
         "Action": "sts:AssumeRoleWithWebIdentity",
         "Condition": {
           "StringEquals": { "cognito-identity.amazonaws.com:aud": "${IDPOOL_ID}" },
           "ForAnyValue:StringLike": { "cognito-identity.amazonaws.com:amr": "authenticated" }
         }
       }
     ]
   }
   EOF

   aws iam create-role --role-name Lab64-CognitoAuth \
     --assume-role-policy-document file://cognito-trust.json
   aws iam attach-role-policy --role-name Lab64-CognitoAuth \
     --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess

   export AUTH_ROLE_ARN=$(aws iam get-role --role-name Lab64-CognitoAuth --query Role.Arn --output text)
   ```
3. Gắn authenticated role vào Identity Pool.
   ```bash
   aws cognito-identity set-identity-pool-roles \
     --identity-pool-id "$IDPOOL_ID" \
     --roles authenticated=$AUTH_ROLE_ARN
   ```
4. Lấy ID token mới từ `User Pool`, rồi **đổi token → AWS creds** (2 bước: `get-id` → `get-credentials-for-identity`).
   ```bash
   export ID_TOKEN=$(aws cognito-idp admin-initiate-auth \
     --user-pool-id "$POOL_ID" --client-id "$CLIENT_ID" \
     --auth-flow ADMIN_USER_PASSWORD_AUTH \
     --auth-parameters USERNAME=demo@example.com,PASSWORD='Passw0rd!' \
     --query 'AuthenticationResult.IdToken' --output text)

   export LOGINS="${PROVIDER}=${ID_TOKEN}"

   # (a) get-id: đăng ký/định danh identity trong pool
   export IDENTITY_ID=$(aws cognito-identity get-id \
     --identity-pool-id "$IDPOOL_ID" \
     --logins "$LOGINS" \
     --query 'IdentityId' --output text)
   echo "IdentityId: $IDENTITY_ID"

   # (b) get-credentials-for-identity: đổi lấy AWS creds tạm (ngầm AssumeRoleWithWebIdentity)
   CREDS=$(aws cognito-identity get-credentials-for-identity \
     --identity-id "$IDENTITY_ID" \
     --logins "$LOGINS" \
     --query 'Credentials' --output json)
   echo "$CREDS"   # AccessKeyId, SecretKey, SessionToken, Expiration
   ```
5. Export creds (⚠️ field ở đây là **`SecretKey`**, không phải `SecretAccessKey`) rồi gọi thẳng `S3`.
   ```bash
   export AWS_ACCESS_KEY_ID=$(echo "$CREDS" | jq -r .AccessKeyId)
   export AWS_SECRET_ACCESS_KEY=$(echo "$CREDS" | jq -r .SecretKey)
   export AWS_SESSION_TOKEN=$(echo "$CREDS" | jq -r .SessionToken)

   aws sts get-caller-identity   # .../assumed-role/Lab64-CognitoAuth/CognitoIdentityCredentials
   aws s3 ls                     # OK — client "gọi thẳng AWS" bằng creds đổi từ JWT
   ```

### ✅ Kiểm chứng
- `get-credentials-for-identity` trả về `AccessKeyId` + `SecretKey` + `SessionToken` + `Expiration`.
- Sau khi export, `get-caller-identity` cho thấy đang mang danh tính **`assumed-role/Lab64-CognitoAuth/CognitoIdentityCredentials`** → đúng authenticated role.
- `aws s3 ls` chạy được bằng creds đổi từ JWT (không dùng key vĩnh viễn nào).

### 🧹 Dọn dẹp (tránh tính phí)
```bash
unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN

aws cognito-identity delete-identity-pool --identity-pool-id "$IDPOOL_ID"
aws iam detach-role-policy --role-name Lab64-CognitoAuth \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess
aws iam delete-role --role-name Lab64-CognitoAuth
rm -f cognito-trust.json
# Nếu chưa cần Lab 6.5 nữa: aws cognito-idp delete-user-pool --user-pool-id "$POOL_ID"
```

### 🧠 Ý nghĩa với đề thi
- "Mobile/web client cần gọi TRỰC TIẾP `DynamoDB`/`S3` / cần **AWS credentials**" → **`Identity Pool`** (KHÔNG phải User Pool).
- Bên dưới, Identity Pool biến claim thành **`AssumeRoleWithWebIdentity`** → `STS` cấp creds tạm → map IAM role.
- Có **authenticated role** (đã đăng nhập) và **unauthenticated/guest role** (khách): bật `--allow-unauthenticated-identities` để cấp quyền hẹp cho khách.

---

## Lab 6.5 — Bảo vệ `API Gateway` bằng `Cognito` authorizer ⭐
**🎯 Mục tiêu:** Tạo REST API `API Gateway` với **Cognito User Pool authorizer**, chứng minh request **không có token → 401**, còn kèm **ID token của `User Pool` → 200**. (Kèm biến thể **Lambda authorizer**.)
**🧩 Luyện kỹ năng (liên quan đề):**
- `COGNITO_USER_POOLS` authorizer: API Gateway tự verify JWT do `User Pool` cấp trước khi cho vào integration.
- Luồng end-to-end: `User Pool` (Lab 6.3) → JWT → header `Authorization` → API Gateway kiểm → backend.
- Phân biệt Cognito authorizer (managed, chỉ verify JWT) vs **Lambda authorizer** (tuỳ biến, tự trả IAM policy).

**⏱️ ~35 phút** · **Yêu cầu trước:** **Lab 6.3 chưa dọn** (cần `$POOL_ID`, `$CLIENT_ID`, user `demo@example.com`).

### Các bước
1. Lấy ARN của `User Pool` (authorizer cần ARN này).
   ```bash
   export POOL_ARN=$(aws cognito-idp describe-user-pool \
     --user-pool-id "$POOL_ID" --query 'UserPool.Arn' --output text)
   ```
2. Tạo REST API + resource `/hello`.
   ```bash
   export API_ID=$(aws apigateway create-rest-api --name lab-secure-api --query id --output text)
   export ROOT_ID=$(aws apigateway get-resources --rest-api-id "$API_ID" --query 'items[0].id' --output text)
   export RES_ID=$(aws apigateway create-resource --rest-api-id "$API_ID" \
     --parent-id "$ROOT_ID" --path-part hello --query id --output text)
   ```
3. Tạo **Cognito authorizer** (đọc token từ header `Authorization`).
   ```bash
   export AUTH_ID=$(aws apigateway create-authorizer --rest-api-id "$API_ID" \
     --name cognito-auth --type COGNITO_USER_POOLS \
     --provider-arns "$POOL_ARN" \
     --identity-source 'method.request.header.Authorization' \
     --query id --output text)
   ```
4. Gắn method `GET /hello` yêu cầu authorizer + integration **MOCK** (không cần Lambda, tập trung vào auth).
   ```bash
   aws apigateway put-method --rest-api-id "$API_ID" --resource-id "$RES_ID" \
     --http-method GET --authorization-type COGNITO_USER_POOLS --authorizer-id "$AUTH_ID"

   aws apigateway put-integration --rest-api-id "$API_ID" --resource-id "$RES_ID" \
     --http-method GET --type MOCK \
     --request-templates '{"application/json":"{\"statusCode\":200}"}'

   aws apigateway put-method-response --rest-api-id "$API_ID" --resource-id "$RES_ID" \
     --http-method GET --status-code 200

   aws apigateway put-integration-response --rest-api-id "$API_ID" --resource-id "$RES_ID" \
     --http-method GET --status-code 200 \
     --response-templates '{"application/json":"{\"message\":\"hello from secured API\"}"}'
   ```
5. Deploy stage `prod` và dựng URL.
   ```bash
   aws apigateway create-deployment --rest-api-id "$API_ID" --stage-name prod
   export INVOKE_URL="https://${API_ID}.execute-api.${AWS_REGION}.amazonaws.com/prod/hello"
   echo "$INVOKE_URL"
   ```
6. Test: **không token → 401**, **có ID token → 200**.
   ```bash
   # (a) Không token
   curl -s -o /dev/null -w "HTTP %{http_code}\n" "$INVOKE_URL"          # -> HTTP 401

   # (b) Lấy ID token rồi gọi kèm header Authorization (giá trị = token, KHÔNG kèm "Bearer ")
   export ID_TOKEN=$(aws cognito-idp admin-initiate-auth \
     --user-pool-id "$POOL_ID" --client-id "$CLIENT_ID" \
     --auth-flow ADMIN_USER_PASSWORD_AUTH \
     --auth-parameters USERNAME=demo@example.com,PASSWORD='Passw0rd!' \
     --query 'AuthenticationResult.IdToken' --output text)

   curl -s -H "Authorization: ${ID_TOKEN}" "$INVOKE_URL"                # -> {"message":"hello from secured API"}
   ```

### ✅ Kiểm chứng
- Gọi không header → **401 Unauthorized** (authorizer chặn).
- Gọi kèm ID token hợp lệ → **200** + body `{"message":"hello from secured API"}`.
- Thử token rác (`Authorization: abc`) → 401 → chứng minh API Gateway thật sự verify chữ ký JWT.

### 🧹 Dọn dẹp (tránh tính phí)
```bash
aws apigateway delete-rest-api --rest-api-id "$API_ID"
aws cognito-idp delete-user-pool --user-pool-id "$POOL_ID"   # dọn nốt User Pool của chuỗi lab
```

### 🧩 Biến thể — **Lambda authorizer** (thay cho Cognito authorizer)
Khi cần logic tuỳ biến (verify token của IdP khác, kiểm tenant, IP allow-list…), dùng **Lambda authorizer** (`--type TOKEN` hoặc `REQUEST`): API Gateway gọi một `Lambda` trả về **IAM policy** `Allow`/`Deny` cho request.
```javascript
// index.mjs — TOKEN authorizer đơn giản (tạo Lambda với --handler index.handler)
export const handler = async (event) => {
  const token = event.authorizationToken ?? "";          // giá trị header Authorization
  const effect = token === "let-me-in" ? "Allow" : "Deny";
  return {
    principalId: "user",
    policyDocument: {
      Version: "2012-10-17",
      Statement: [{
        Action: "execute-api:Invoke",
        Effect: effect,
        Resource: event.methodArn,
      }],
    },
  };
};
```
```bash
# Tạo Lambda authorizer (runtime Node.js 24 đã bundle sẵn, chỉ cần zip index.mjs — KHÔNG cần npm install):
zip function.zip index.mjs
aws lambda create-function --function-name lab-lambda-authorizer \
  --runtime nodejs24.x --handler index.handler \
  --zip-file fileb://function.zip \
  --role "arn:aws:iam::${ACCOUNT_ID}:role/<LAMBDA_EXEC_ROLE>"
export LAMBDA_ARN=$(aws lambda get-function --function-name lab-lambda-authorizer \
  --query 'Configuration.FunctionArn' --output text)

# Cho phép API Gateway gọi Lambda này:
aws lambda add-permission --function-name lab-lambda-authorizer \
  --statement-id apigw-invoke --action lambda:InvokeFunction \
  --principal apigateway.amazonaws.com

# Gắn kiểu authorizer này (dùng $LAMBDA_ARN vừa tạo):
aws apigateway create-authorizer --rest-api-id "$API_ID" \
  --name lambda-auth --type TOKEN \
  --authorizer-uri "arn:aws:apigateway:${AWS_REGION}:lambda:path/2015-03-31/functions/${LAMBDA_ARN}/invocations" \
  --identity-source 'method.request.header.Authorization'
```

### 🧠 Ý nghĩa với đề thi
- **Cognito authorizer** = cách managed, chỉ verify JWT của `User Pool` — cấu hình nhanh, không viết code.
- **Lambda authorizer** = linh hoạt: tự verify token bất kỳ và trả **IAM policy**; `TOKEN` (dựa header) vs `REQUEST` (dựa nhiều tham số request). Kết quả nên bật **authorizer caching** để giảm chi phí.
- `API Gateway` → `Lambda` (backend) là tích hợp **synchronous** (proxy `AWS_PROXY`); còn Lambda authorizer chạy TRƯỚC integration để gác cổng.

---

> ✅ Xong 5 lab? Đối chiếu lại [Lab checklist trong README](README.md#-lab-checklist) và làm tiếp [bộ câu hỏi luyện tập](questions.md). Nhớ chạy hết phần **Dọn dẹp** để không phát sinh phí.
