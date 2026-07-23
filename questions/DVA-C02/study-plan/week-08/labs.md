# 🧪 Hands-on Labs — Tuần 8: Deployment — CI/CD + `CloudFormation`/`SAM` + `ECS`/`ECR`

> Lab cầm tay chỉ việc, chạy được trên tài khoản AWS thật (Free Tier). LUÔN chạy phần Dọn dẹp cuối mỗi lab.
> ⚙️ Yêu cầu chung: đã cấu hình `AWS CLI v2` (xem Lab 1.1 tuần 1) + IAM đủ quyền cho dịch vụ trong lab. Lab 8.2/8.3 cần thêm **`AWS SAM CLI`** + **Docker**; Lab 8.6 cần **Docker**.
> Về [plan tuần](README.md) · [Câu hỏi luyện tập](questions.md) · [Kế hoạch tổng](../../DVA-C02-STUDY-PLAN.md)

---

## 🔧 Chuẩn bị chung (làm 1 lần, dùng cho mọi lab)

```bash
# 1) Đặt region (đổi theo bạn — ví dụ us-east-1 hoặc us-east-1)
export AWS_REGION=us-east-1
export AWS_DEFAULT_REGION=$AWS_REGION

# 2) Lấy Account ID để dựng ARN / tên bucket toàn cục
export ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "Account: $ACCOUNT_ID · Region: $AWS_REGION"
```

> 🧠 **Nhớ nhanh Domain 3** (hay bị nhầm, sẽ minh hoạ xuyên suốt các lab):
> - `buildspec.yml` → **`CodeBuild`**, đặt ở **ROOT** repo; phase `install → pre_build → build → post_build`.
> - `appspec.yml` → **`CodeDeploy`**. `In-place` **CHỈ** EC2/on-prem; `Lambda`/`ECS` = **Blue/Green + Canary/Linear**.
> - Cross-stack: stack nguồn `Outputs` + **`Export`**; stack đích **`Fn::ImportValue`**. Xem trước thay đổi = **change set**; sửa tay lệch template = **drift**.
> - `ECS`: **execution role** = kéo image `ECR` + ghi log (cho ECS agent); **task role** = quyền app trong container gọi AWS API.

---

## Lab 8.1 — Viết `buildspec.yml` (4 phase + artifacts) + chạy `CodeBuild`

**🎯 Mục tiêu:** Tự tay viết `buildspec.yml` đủ 4 phase, tạo `CodeBuild` project (source = `S3`), chạy build, xem log 4 phase chạy đúng thứ tự và kiểm tra artifact đã lên `S3`.
**🧩 Luyện kỹ năng (liên quan đề):**
- Thứ tự phase `install → pre_build → build → post_build` (bẫy thi kinh điển).
- Lấy secret an toàn qua `parameter-store` (SSM) thay vì hardcode trong `variables`.
- `artifacts` (`files` + `base-directory`) → nơi output được zip & upload lên `S3`; `cache` giữ dependency.

**⏱️ ~30 phút** · **Yêu cầu trước:** Chuẩn bị chung.

### Các bước
1. Tạo 2 bucket (source + artifact) và 1 tham số `SSM` để `buildspec` kéo vào (chứng minh không hardcode secret).
   ```bash
   SRC_BUCKET=lab8-cb-src-$ACCOUNT_ID
   ART_BUCKET=lab8-cb-art-$ACCOUNT_ID
   aws s3 mb s3://$SRC_BUCKET --region $AWS_REGION
   aws s3 mb s3://$ART_BUCKET --region $AWS_REGION
   aws ssm put-parameter --name /lab8/greeting --value "hello-from-ssm" --type String
   ```

2. Viết `buildspec.yml` — **đặt ở ROOT** của source (đủ 4 phase + `artifacts` + `cache`).
   ```yaml
   version: 0.2
   env:
     variables:
       APP_ENV: "dev"                 # biến thường (plaintext) — KHÔNG để secret ở đây
     parameter-store:
       GREETING: /lab8/greeting       # kéo từ SSM Parameter Store (cần ssm:GetParameters)
   phases:
     install:
       runtime-versions:
         nodejs: 20                   # chỉ phase install mới có runtime-versions
       commands:
         - echo "[install] chuẩn bị runtime & dependencies"
     pre_build:
       commands:
         - echo "[pre_build] APP_ENV=$APP_ENV GREETING=$GREETING"
     build:
       commands:
         - echo "[build] tạo artifact"
         - mkdir -p dist
         - echo "Built $(date) env=$APP_ENV msg=$GREETING" > dist/output.txt
     post_build:
       commands:
         - echo "[post_build] hoàn tất"
   artifacts:
     files:
       - "**/*"
     base-directory: dist             # gốc để gom file artifact
   cache:
     paths:
       - "/root/.npm/**/*"            # giữ dependency giữa các lần build
   ```

3. Zip source (chỉ cần `buildspec.yml`) rồi upload lên `S3`.
   ```bash
   zip source.zip buildspec.yml
   aws s3 cp source.zip s3://$SRC_BUCKET/source.zip
   ```

4. Tạo **service role** cho `CodeBuild` (ghi Logs + đọc/ghi `S3` + đọc `SSM`).
   ```bash
   cat > trust-cb.json <<'EOF'
   { "Version":"2012-10-17","Statement":[{"Effect":"Allow",
     "Principal":{"Service":"codebuild.amazonaws.com"},"Action":"sts:AssumeRole"}] }
   EOF
   aws iam create-role --role-name lab8-codebuild-role \
     --assume-role-policy-document file://trust-cb.json

   cat > cb-policy.json <<EOF
   {
     "Version":"2012-10-17",
     "Statement":[
       {"Effect":"Allow","Action":["logs:CreateLogGroup","logs:CreateLogStream","logs:PutLogEvents"],"Resource":"*"},
       {"Effect":"Allow","Action":["s3:GetObject","s3:GetObjectVersion","s3:PutObject","s3:GetBucketAcl","s3:GetBucketLocation"],
        "Resource":["arn:aws:s3:::${SRC_BUCKET}","arn:aws:s3:::${SRC_BUCKET}/*","arn:aws:s3:::${ART_BUCKET}","arn:aws:s3:::${ART_BUCKET}/*"]},
       {"Effect":"Allow","Action":["ssm:GetParameters"],"Resource":"arn:aws:ssm:${AWS_REGION}:${ACCOUNT_ID}:parameter/lab8/*"}
     ]
   }
   EOF
   aws iam put-role-policy --role-name lab8-codebuild-role \
     --policy-name cb-inline --policy-document file://cb-policy.json
   CB_ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/lab8-codebuild-role"
   ```

5. Tạo project (source `S3`, artifact `S3`, managed image) rồi start build.
   ```bash
   cat > project.json <<EOF
   {
     "name": "lab8-build",
     "source": { "type": "S3", "location": "${SRC_BUCKET}/source.zip", "buildspec": "buildspec.yml" },
     "artifacts": { "type": "S3", "location": "${ART_BUCKET}", "packaging": "ZIP", "name": "lab8-artifacts.zip" },
     "environment": {
       "type": "LINUX_CONTAINER",
       "image": "aws/codebuild/amazonlinux-x86_64-standard:5.0",
       "computeType": "BUILD_GENERAL1_SMALL"
     },
     "serviceRole": "${CB_ROLE_ARN}"
   }
   EOF
   aws codebuild create-project --cli-input-json file://project.json

   BUILD_ID=$(aws codebuild start-build --project-name lab8-build --query 'build.id' --output text)
   echo "Build: $BUILD_ID"
   ```
   > 📝 Từ 11/2024 AWS đổi alias `amazonlinux2-x86_64-standard:5.0` → `amazonlinux-x86_64-standard:5.0` (alias cũ vẫn chạy nhưng nên dùng tên mới); `standard:5.0` thực chất là **Amazon Linux 2023** (có sẵn Node 20/22).

### ✅ Kiểm chứng
- Chờ build xong rồi xem trạng thái + log 4 phase.
  ```bash
  aws codebuild batch-get-builds --ids "$BUILD_ID" \
    --query 'builds[0].{status:buildStatus,phases:phases[].phaseType}'
  aws logs tail /aws/codebuild/lab8-build --since 10m
  ```
  Log phải in `[install] → [pre_build] → [build] → [post_build]` đúng thứ tự; giá trị `GREETING` được **che (masked)** vì đến từ SSM.
- Kiểm tra artifact đã lên `S3`:
  ```bash
  aws s3 ls s3://$ART_BUCKET/
  ```

### 🧹 Dọn dẹp (tránh tính phí)
```bash
aws codebuild delete-project --name lab8-build
aws ssm delete-parameter --name /lab8/greeting
aws s3 rm s3://$SRC_BUCKET --recursive; aws s3 rb s3://$SRC_BUCKET
aws s3 rm s3://$ART_BUCKET --recursive; aws s3 rb s3://$ART_BUCKET
aws iam delete-role-policy --role-name lab8-codebuild-role --policy-name cb-inline
aws iam delete-role --role-name lab8-codebuild-role
rm -f buildspec.yml source.zip trust-cb.json cb-policy.json project.json
```

### 🧠 Ý nghĩa với đề thi
- `buildspec.yml` **thuộc `CodeBuild`**, mặc định ở **ROOT** repo; đổi tên/vị trí phải khai trong project (`buildspecOverride`).
- Secret trong build (DB password/API key) → dùng `parameter-store`/`secrets-manager`, KHÔNG để trong `variables` (plaintext).
- `artifacts` quyết định cái gì được upload lên `S3`; `cache` tăng tốc build lần sau.

---

## Lab 8.2 — `SAM` app end-to-end: `Function` + `Api` + `SimpleTable` ⭐
**🎯 Mục tiêu:** Dựng 1 app serverless bằng `SAM`: 2 `Lambda` sau `API Gateway` ghi/đọc 1 bảng `DynamoDB` (`SimpleTable`); test local bằng `sam local`, rồi `sam deploy --guided` và gọi API thật.
**🧩 Luyện kỹ năng (liên quan đề):**
- `Transform: AWS::Serverless-2016-10-31` → cú pháp rút gọn nở thành `CloudFormation`.
- `AWS::Serverless::Function` + event `Api` = tích hợp `API Gateway` → `Lambda` **synchronous** (proxy).
- `SimpleTable` (`DynamoDB`) + policy rút gọn (`DynamoDBCrudPolicy`); chuỗi lệnh `sam init/build/local/deploy`.

**⏱️ ~40 phút** · **Yêu cầu trước:** `AWS SAM CLI` + Docker đang chạy.

### Các bước
1. Khởi tạo project rồi vào thư mục.
   ```bash
   sam init --name lab8-sam --runtime python3.12 --dependency-manager pip \
     --app-template hello-world --no-tracing --no-application-insights
   cd lab8-sam
   rm -rf hello_world tests events && mkdir -p src events
   ```

2. Thay `template.yaml` bằng template dưới (Function + Api + SimpleTable).
   ```yaml
   AWSTemplateFormatVersion: '2010-09-09'
   Transform: AWS::Serverless-2016-10-31
   Description: Lab 8.2 - SAM Function + Api + SimpleTable

   Globals:
     Function:
       Runtime: python3.12
       Timeout: 10
       MemorySize: 128

   Resources:
     ItemsTable:
       Type: AWS::Serverless::SimpleTable      # DynamoDB rút gọn
       Properties:
         PrimaryKey: { Name: id, Type: String }

     PutItemFunction:
       Type: AWS::Serverless::Function
       Properties:
         Handler: app.put_item
         CodeUri: src/
         Environment:
           Variables:
             TABLE_NAME: !Ref ItemsTable
         Policies:
           - DynamoDBCrudPolicy: { TableName: !Ref ItemsTable }
         Events:
           PutApi:
             Type: Api                         # tạo API Gateway (sync, proxy)
             Properties: { Path: /items, Method: post }

     GetItemFunction:
       Type: AWS::Serverless::Function
       Properties:
         Handler: app.get_item
         CodeUri: src/
         Environment:
           Variables:
             TABLE_NAME: !Ref ItemsTable
         Policies:
           - DynamoDBCrudPolicy: { TableName: !Ref ItemsTable }
         Events:
           GetApi:
             Type: Api
             Properties: { Path: /items/{id}, Method: get }

   Outputs:
     ApiUrl:
       Description: Base URL của API Gateway
       Value: !Sub "https://${ServerlessRestApi}.execute-api.${AWS::Region}.amazonaws.com/Prod"
   ```

3. Viết handler + requirements rỗng (boto3 có sẵn trong runtime).
   ```python
   # src/app.py
   import os, json, boto3
   table = boto3.resource("dynamodb").Table(os.environ["TABLE_NAME"])

   def put_item(event, context):
       body = json.loads(event.get("body") or "{}")
       table.put_item(Item={"id": body["id"], "name": body.get("name", "")})
       return {"statusCode": 200, "body": json.dumps({"saved": body["id"]})}

   def get_item(event, context):
       item_id = event["pathParameters"]["id"]
       resp = table.get_item(Key={"id": item_id})
       return {"statusCode": 200, "body": json.dumps(resp.get("Item", {}))}
   ```
   ```bash
   : > src/requirements.txt
   ```

4. Build + deploy có hướng dẫn (guided). Trả lời prompt: Stack name `lab8-sam`, Region của bạn, cho phép tạo IAM role (`Y`), lưu `samconfig.toml` (`Y`); các API không auth → chọn `y` khi hỏi "…may not have authorization defined".
   ```bash
   sam build
   sam deploy --guided
   ```

### ✅ Kiểm chứng
- Lấy URL API từ Outputs rồi gọi thật (POST ghi item, GET đọc lại):
  ```bash
  API=$(aws cloudformation describe-stacks --stack-name lab8-sam \
        --query "Stacks[0].Outputs[?OutputKey=='ApiUrl'].OutputValue" --output text)
  curl -s -XPOST "$API/items" -d '{"id":"1","name":"widget"}'; echo
  curl -s "$API/items/1"; echo   # -> {"id": "1", "name": "widget"}
  ```
- Test **local** (mechanics của `sam local`) — bảng đã tồn tại sau deploy nên chạy được với creds của bạn:
  ```bash
  cat > events/get.json <<'EOF'
  { "pathParameters": { "id": "1" } }
  EOF
  sam local invoke GetItemFunction -e events/get.json     # cần Docker
  sam local start-api                                     # phục vụ http://127.0.0.1:3000 (Ctrl+C để dừng)
  # tab khác: curl -s http://127.0.0.1:3000/items/1
  ```

### 🧹 Dọn dẹp
```bash
sam delete --stack-name lab8-sam --no-prompts
cd .. && rm -rf lab8-sam
```

### 🧠 Ý nghĩa với đề thi
- `SAM` = **superset của `CloudFormation`** cho serverless; nhận diện bằng header `Transform: AWS::Serverless-2016-10-31`.
- `Api` event = `API Gateway` → `Lambda` **synchronous** (proxy); policy rút gọn (`DynamoDBCrudPolicy`) SAM nở thành IAM policy.
- Luồng lệnh phải thuộc: `sam init → build → local invoke/start-api → deploy` (deploy thực thi qua `CloudFormation`).

---

## Lab 8.3 — `CodeDeploy` Lambda **Canary** qua `DeploymentPreference` (SAM) ⭐
**🎯 Mục tiêu:** Bật `DeploymentPreference: Canary10Percent5Minutes` cho 1 `Lambda`; đổi code rồi deploy lại để `SAM` kích `CodeDeploy` **shift traffic trên alias** (10% → 100% sau 5 phút); quan sát trọng số (weighting) của alias thay đổi.
**🧩 Luyện kỹ năng (liên quan đề):**
- `Lambda`/`ECS` KHÔNG dùng In-place → dùng **Blue/Green + Canary/Linear** shift traffic qua `CodeDeploy`.
- `AutoPublishAlias` + `DeploymentPreference` = cách an toàn khi update `Lambda`.
- Alias `RoutingConfig`/`AdditionalVersionWeights` = cơ chế chia % traffic giữa 2 version.

**⏱️ ~35 phút** · **Yêu cầu trước:** `AWS SAM CLI` (Lab 8.2).

### Các bước
1. Tạo project SAM tối giản.
   ```bash
   mkdir -p lab8-canary/src && cd lab8-canary
   : > src/requirements.txt
   ```
   ```yaml
   # template.yaml
   AWSTemplateFormatVersion: '2010-09-09'
   Transform: AWS::Serverless-2016-10-31
   Description: Lab 8.3 - Lambda canary via DeploymentPreference

   Resources:
     CanaryFunction:
       Type: AWS::Serverless::Function
       Properties:
         Handler: app.handler
         Runtime: python3.12
         CodeUri: src/
         AutoPublishAlias: live               # tạo alias 'live' + publish version mỗi lần deploy
         DeploymentPreference:
           Type: Canary10Percent5Minutes      # shift 10% rồi 90% còn lại sau 5 phút (qua CodeDeploy)
   Outputs:
     FunctionName:
       Value: !Ref CanaryFunction
   ```
   ```python
   # src/app.py  (version 1)
   def handler(event, context):
       return {"version": "v1"}
   ```

2. Deploy lần đầu (function mới → chưa có shift).
   ```bash
   sam build && sam deploy --guided   # stack name: lab8-canary; cho phép tạo IAM role
   FN=$(aws cloudformation describe-stack-resource --stack-name lab8-canary \
        --logical-resource-id CanaryFunction \
        --query 'StackResourceDetail.PhysicalResourceId' --output text)
   aws lambda get-alias --function-name "$FN" --name live \
     --query '{Version:FunctionVersion,Routing:RoutingConfig}'
   # -> Version "1", Routing null
   ```

3. Đổi code sang **v2** rồi deploy lại → `CodeDeploy` bắt đầu canary.
   ```bash
   cat > src/app.py <<'EOF'
   def handler(event, context):
       return {"version": "v2"}
   EOF
   sam build && sam deploy      # dùng lại samconfig.toml; không cần --guided nữa
   ```

### ✅ Kiểm chứng
- **Ngay trong 5 phút** shift: alias `live` vẫn trỏ version 1 nhưng có `AdditionalVersionWeights` ~`0.1` cho version 2 (10% canary):
  ```bash
  aws lambda get-alias --function-name "$FN" --name live \
    --query '{Version:FunctionVersion,Routing:RoutingConfig}'
  aws deploy list-deployments \
    --query 'deployments' --output text   # có deployment đang InProgress
  ```
- Gọi alias nhiều lần → khoảng 10% trả `v2`, 90% trả `v1`:
  ```bash
  for i in $(seq 1 20); do
    aws lambda invoke --function-name "$FN:live" out.json >/dev/null && cat out.json && echo
  done | sort | uniq -c
  ```
- Sau ~5 phút: alias `live` chuyển hẳn sang version 2, `RoutingConfig` = null.
- (Khái niệm rollback) Nếu gắn `DeploymentPreference.Alarms` và alarm kêu trong lúc shift → `CodeDeploy` **tự rollback** về version cũ.

### 🧹 Dọn dẹp
```bash
sam delete --stack-name lab8-canary --no-prompts
cd .. && rm -rf lab8-canary
rm -f out.json
```

### 🧠 Ý nghĩa với đề thi
- `Lambda` update an toàn = **alias + version + traffic shift** (Canary/Linear) qua `CodeDeploy`, KHÔNG có "In-place cho Lambda".
- **Canary** = 1 cục nhỏ (10%) trước, phần còn lại 1 lần sau X phút; **Linear** = đều đặn 10% mỗi X phút. Nhớ tên: `Canary10Percent5Minutes`.
- Hooks Lambda: `BeforeAllowTraffic`, `AfterAllowTraffic` (khác EC2/ECS).

---

## Lab 8.4 — `CodePipeline` end-to-end: Source → `CodeBuild` → Deploy ⭐
**🎯 Mục tiêu:** Ráp pipeline 3 stage (Source `S3` → Build `CodeBuild` → Deploy `S3`), chạy tự động và quan sát **artifact store `S3`** truyền artifact giữa các stage.
**🧩 Luyện kỹ năng (liên quan đề):**
- Cấu trúc `Pipeline → Stage → Action`; artifact truyền qua **artifact store (S3 bucket)**.
- `input/output artifacts` nối Source → Build → Deploy.
- Nguồn từ GitHub dùng **`CodeConnections`** (trước là `CodeStar Connections`) — biến thể ở cuối lab.

**⏱️ ~45 phút** · **Yêu cầu trước:** Chuẩn bị chung.

### Các bước
1. Tạo 3 bucket: source (**bật versioning** — bắt buộc cho S3 source), artifact store, deploy đích.
   ```bash
   SRC_BUCKET=lab8-pipe-src-$ACCOUNT_ID
   ART_BUCKET=lab8-pipe-artifact-$ACCOUNT_ID
   DEPLOY_BUCKET=lab8-pipe-deploy-$ACCOUNT_ID
   aws s3 mb s3://$SRC_BUCKET --region $AWS_REGION
   aws s3api put-bucket-versioning --bucket $SRC_BUCKET --versioning-configuration Status=Enabled
   aws s3 mb s3://$ART_BUCKET --region $AWS_REGION
   aws s3 mb s3://$DEPLOY_BUCKET --region $AWS_REGION
   ```

2. Tạo source (buildspec dạng `CODEPIPELINE` + 1 file web) rồi upload.
   ```bash
   cat > buildspec.yml <<'EOF'
   version: 0.2
   phases:
     build:
       commands:
         - echo "building site..."
         - mkdir -p dist && cp index.html dist/
         - echo "<p>built at $(date)</p>" >> dist/index.html
   artifacts:
     files:
       - "**/*"
     base-directory: dist
   EOF
   echo '<h1>Lab 8.4 CodePipeline</h1>' > index.html
   zip source.zip buildspec.yml index.html
   aws s3 cp source.zip s3://$SRC_BUCKET/source.zip
   ```

3. Role cho `CodeBuild` (Logs + `S3` artifact store) và project (source/artifacts = `CODEPIPELINE`).
   ```bash
   cat > trust-cb.json <<'EOF'
   { "Version":"2012-10-17","Statement":[{"Effect":"Allow",
     "Principal":{"Service":"codebuild.amazonaws.com"},"Action":"sts:AssumeRole"}] }
   EOF
   aws iam create-role --role-name lab8-pipe-cb-role \
     --assume-role-policy-document file://trust-cb.json
   aws iam put-role-policy --role-name lab8-pipe-cb-role --policy-name cb-inline \
     --policy-document "{\"Version\":\"2012-10-17\",\"Statement\":[
       {\"Effect\":\"Allow\",\"Action\":[\"logs:CreateLogGroup\",\"logs:CreateLogStream\",\"logs:PutLogEvents\"],\"Resource\":\"*\"},
       {\"Effect\":\"Allow\",\"Action\":[\"s3:GetObject\",\"s3:GetObjectVersion\",\"s3:PutObject\",\"s3:GetBucketLocation\"],\"Resource\":[\"arn:aws:s3:::${ART_BUCKET}\",\"arn:aws:s3:::${ART_BUCKET}/*\"]}]}"
   CB_ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/lab8-pipe-cb-role"

   cat > project.json <<EOF
   {
     "name": "lab8-pipe-build",
     "source": { "type": "CODEPIPELINE" },
     "artifacts": { "type": "CODEPIPELINE" },
     "environment": { "type": "LINUX_CONTAINER", "image": "aws/codebuild/amazonlinux-x86_64-standard:5.0", "computeType": "BUILD_GENERAL1_SMALL" },
     "serviceRole": "${CB_ROLE_ARN}"
   }
   EOF
   aws codebuild create-project --cli-input-json file://project.json
   ```

4. Role cho `CodePipeline` (dùng S3 các bucket + gọi CodeBuild).
   ```bash
   cat > trust-cp.json <<'EOF'
   { "Version":"2012-10-17","Statement":[{"Effect":"Allow",
     "Principal":{"Service":"codepipeline.amazonaws.com"},"Action":"sts:AssumeRole"}] }
   EOF
   aws iam create-role --role-name lab8-pipe-role \
     --assume-role-policy-document file://trust-cp.json
   aws iam put-role-policy --role-name lab8-pipe-role --policy-name cp-inline \
     --policy-document "{\"Version\":\"2012-10-17\",\"Statement\":[
       {\"Effect\":\"Allow\",\"Action\":[\"s3:GetObject\",\"s3:GetObjectVersion\",\"s3:PutObject\",\"s3:GetBucketVersioning\",\"s3:ListBucket\"],
        \"Resource\":[\"arn:aws:s3:::${SRC_BUCKET}\",\"arn:aws:s3:::${SRC_BUCKET}/*\",\"arn:aws:s3:::${ART_BUCKET}\",\"arn:aws:s3:::${ART_BUCKET}/*\",\"arn:aws:s3:::${DEPLOY_BUCKET}\",\"arn:aws:s3:::${DEPLOY_BUCKET}/*\"]},
       {\"Effect\":\"Allow\",\"Action\":[\"codebuild:StartBuild\",\"codebuild:BatchGetBuilds\"],\"Resource\":\"*\"}]}"
   CP_ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/lab8-pipe-role"
   ```

5. Tạo pipeline (create-pipeline tự chạy 1 execution ngay).
   ```bash
   cat > pipeline.json <<EOF
   {
     "pipeline": {
       "name": "lab8-pipeline",
       "roleArn": "${CP_ROLE_ARN}",
       "artifactStore": { "type": "S3", "location": "${ART_BUCKET}" },
       "stages": [
         { "name": "Source", "actions": [{
             "name": "S3Source",
             "actionTypeId": { "category":"Source","owner":"AWS","provider":"S3","version":"1" },
             "configuration": { "S3Bucket":"${SRC_BUCKET}","S3ObjectKey":"source.zip","PollForSourceChanges":"false" },
             "outputArtifacts": [{ "name":"SourceOutput" }] }] },
         { "name": "Build", "actions": [{
             "name": "BuildAction",
             "actionTypeId": { "category":"Build","owner":"AWS","provider":"CodeBuild","version":"1" },
             "configuration": { "ProjectName":"lab8-pipe-build" },
             "inputArtifacts": [{ "name":"SourceOutput" }],
             "outputArtifacts": [{ "name":"BuildOutput" }] }] },
         { "name": "Deploy", "actions": [{
             "name": "S3Deploy",
             "actionTypeId": { "category":"Deploy","owner":"AWS","provider":"S3","version":"1" },
             "configuration": { "BucketName":"${DEPLOY_BUCKET}","Extract":"true" },
             "inputArtifacts": [{ "name":"BuildOutput" }] }] }
       ]
     }
   }
   EOF
   aws codepipeline create-pipeline --cli-input-json file://pipeline.json
   ```

### ✅ Kiểm chứng
- Xem trạng thái từng stage (chờ đến khi Deploy `Succeeded`):
  ```bash
  aws codepipeline get-pipeline-state --name lab8-pipeline \
    --query 'stageStates[].{stage:stageName,status:latestExecution.status}'
  ```
- Xem **artifact store `S3`** — mỗi action đẩy output artifact (zip) vào đây rồi action sau lấy ra:
  ```bash
  aws s3 ls s3://$ART_BUCKET/lab8-pipeline/ --recursive
  ```
- Xem kết quả deploy (file web đã bung ra deploy bucket):
  ```bash
  aws s3 ls s3://$DEPLOY_BUCKET/
  ```
- Re-trigger: upload lại `source.zip` (đối tượng có version mới) rồi:
  ```bash
  aws codepipeline start-pipeline-execution --name lab8-pipeline
  ```
  > 💡 `PollForSourceChanges=false`: production nên dùng **EventBridge**/webhook để auto-detect thay vì polling.

### 🧹 Dọn dẹp
```bash
aws codepipeline delete-pipeline --name lab8-pipeline
aws codebuild delete-project --name lab8-pipe-build
for b in $SRC_BUCKET $ART_BUCKET $DEPLOY_BUCKET; do
  aws s3 rm s3://$b --recursive; aws s3 rb s3://$b
done
aws iam delete-role-policy --role-name lab8-pipe-cb-role --policy-name cb-inline
aws iam delete-role --role-name lab8-pipe-cb-role
aws iam delete-role-policy --role-name lab8-pipe-role --policy-name cp-inline
aws iam delete-role --role-name lab8-pipe-role
rm -f buildspec.yml index.html source.zip trust-cb.json trust-cp.json project.json pipeline.json
```

### 🧠 Ý nghĩa với đề thi
- `CodePipeline` = **orchestration**: nối các stage; artifact truyền giữa stage qua **artifact store `S3`** (không phải chép tay).
- 1 stage **khoá** trong khi xử lý 1 execution; SUPERSEDED là execution mode mặc định.
- Nguồn GitHub → dùng **`CodeConnections`** (biến thể dưới); có thể chèn stage **Approval** thủ công trước Deploy.

> 🔁 **Biến thể — Source từ GitHub qua `CodeConnections`:** tạo connection rồi **authorize trong Console** (handshake không làm hết bằng CLI được):
> ```bash
> aws codeconnections create-connection --provider-type GitHub --connection-name lab8-gh
> # Trạng thái PENDING -> vào Console > Developer Tools > Connections > "Update pending connection" để cấp quyền GitHub.
> # Sau đó thay stage Source: provider "CodeStarSourceConnection",
> #   configuration: { ConnectionArn, FullRepositoryId: "owner/repo", BranchName: "main" }
> ```

---

## Lab 8.5 — `CloudFormation`: cross-stack `Export`/`Fn::ImportValue` + change set + drift
**🎯 Mục tiêu:** Stack A `Export` 1 giá trị qua `Outputs`; stack B đọc bằng `Fn::ImportValue`. Tạo **change set** xem trước rồi mới apply lên stack A; bật **drift detection** để phát hiện sửa tay.
**🧩 Luyện kỹ năng (liên quan đề):**
- `Outputs` + `Export` ↔ `Fn::ImportValue` (cross-stack reference).
- `Parameters` + `Ref`/`Fn::GetAtt`/`Fn::Sub` + pseudo params (`AWS::Region`, `AWS::AccountId`).
- **change set** (xem trước) khác **drift detection** (phát hiện lệch template) — hay bị nhầm.

**⏱️ ~30 phút** · **Yêu cầu trước:** Chuẩn bị chung.

### Các bước
1. Viết stack A (`lab8-export.yaml`) — có `Parameters`, `Ref`, `GetAtt`, `Sub`, và `Outputs` kèm `Export`.
   ```yaml
   AWSTemplateFormatVersion: '2010-09-09'
   Description: Lab 8.5 Stack A - export giá trị cho stack khác
   Parameters:
     TopicName:
       Type: String
       Default: lab8-shared-topic
   Resources:
     SharedTopic:
       Type: AWS::SNS::Topic
       Properties:
         TopicName: !Ref TopicName
   Outputs:
     TopicArn:
       Description: ARN chia sẻ cho stack khác
       Value: !Ref SharedTopic
       Export:
         Name: Lab8-SharedTopicArn         # tên export toàn Region (duy nhất)
     TopicRealName:
       Value: !GetAtt SharedTopic.TopicName
     Info:
       Value: !Sub "Topic ${TopicName} @ ${AWS::Region} / acct ${AWS::AccountId}"
   ```

2. Deploy stack A rồi xem export.
   ```bash
   aws cloudformation create-stack --stack-name lab8-stack-a \
     --template-body file://lab8-export.yaml
   aws cloudformation wait stack-create-complete --stack-name lab8-stack-a
   aws cloudformation list-exports --query "Exports[?Name=='Lab8-SharedTopicArn']"
   ```

3. Viết stack B (`lab8-import.yaml`) dùng `Fn::ImportValue` (lưu ARN import được vào 1 `SSM Parameter` — free).
   ```yaml
   AWSTemplateFormatVersion: '2010-09-09'
   Description: Lab 8.5 Stack B - import giá trị từ Stack A
   Resources:
     ImportedArnParam:
       Type: AWS::SSM::Parameter
       Properties:
         Name: /lab8/imported-topic-arn
         Type: String
         Value: !ImportValue Lab8-SharedTopicArn
   Outputs:
     ImportedArn:
       Value: !ImportValue Lab8-SharedTopicArn
   ```
   ```bash
   aws cloudformation create-stack --stack-name lab8-stack-b \
     --template-body file://lab8-import.yaml
   aws cloudformation wait stack-create-complete --stack-name lab8-stack-b
   ```

4. Sửa stack A (thêm `DisplayName` — không đụng export) và tạo **change set** để xem trước.
   ```bash
   # thêm 1 dòng dưới Properties của SharedTopic trong lab8-export.yaml:
   #   DisplayName: "Lab8 Shared"
   aws cloudformation create-change-set --stack-name lab8-stack-a \
     --change-set-name add-display-name --template-body file://lab8-export.yaml
   aws cloudformation describe-change-set --stack-name lab8-stack-a \
     --change-set-name add-display-name \
     --query 'Changes[].ResourceChange.{Action:Action,Res:LogicalResourceId,Replace:Replacement}'
   aws cloudformation execute-change-set --stack-name lab8-stack-a --change-set-name add-display-name
   ```

### ✅ Kiểm chứng
- Stack B đọc đúng ARN của topic tạo bởi stack A:
  ```bash
  aws ssm get-parameter --name /lab8/imported-topic-arn --query 'Parameter.Value' --output text
  ```
- **Bẫy phụ thuộc:** thử xoá stack A khi B còn import → **fail** (`Export ... cannot be deleted as it is in use`). Đó là lý do phải xoá B trước.
- **Drift detection:** chạy detect (ban đầu `IN_SYNC`), sửa tay resource, detect lại thấy `MODIFIED`.
  ```bash
  TOPIC_ARN=$(aws cloudformation list-exports \
    --query "Exports[?Name=='Lab8-SharedTopicArn'].Value" --output text)
  # sửa tay ngoài template:
  aws sns set-topic-attributes --topic-arn "$TOPIC_ARN" \
    --attribute-name DisplayName --attribute-value "changed-by-hand"
  DID=$(aws cloudformation detect-stack-drift --stack-name lab8-stack-a \
        --query StackDriftDetectionId --output text)
  aws cloudformation describe-stack-drift-detection-status --stack-drift-detection-id "$DID" \
    --query '{Status:DetectionStatus,Drift:StackDriftStatus}'
  aws cloudformation describe-stack-resource-drifts --stack-name lab8-stack-a \
    --query 'StackResourceDrifts[].{Res:LogicalResourceId,Drift:StackResourceDriftStatus}'
  ```

### 🧹 Dọn dẹp
```bash
# XOÁ B TRƯỚC (gỡ phụ thuộc import), rồi mới xoá A
aws cloudformation delete-stack --stack-name lab8-stack-b
aws cloudformation wait stack-delete-complete --stack-name lab8-stack-b
aws cloudformation delete-stack --stack-name lab8-stack-a
aws cloudformation wait stack-delete-complete --stack-name lab8-stack-a
rm -f lab8-export.yaml lab8-import.yaml
```

### 🧠 Ý nghĩa với đề thi
- Chia sẻ giá trị giữa stack = **`Export` (Outputs) + `Fn::ImportValue`**; không copy-paste, không lồng resource.
- **change set** = xem trước thay đổi TRƯỚC khi apply (tránh sửa/xoá ngoài ý muốn); **drift** = phát hiện resource bị sửa tay lệch template — 2 khái niệm khác nhau.
- Không xoá được stack đang có export bị stack khác import → nhớ thứ tự xoá; muốn giữ resource khi xoá stack thì `DeletionPolicy: Retain`.

---

## Lab 8.6 — `ECR` + `ECS`/`Fargate`: build/push image, run task, task role vs execution role ⭐
**🎯 Mục tiêu:** Build & push image lên `ECR` (login qua `get-login-password`), đăng ký task definition `Fargate` với **2 role tách biệt**, `run-task` và xem log; phân biệt rõ **task role** vs **execution role**.
**🧩 Luyện kỹ năng (liên quan đề):**
- Luồng login/tag/push `ECR`; `scanOnPush` + lifecycle policy.
- Task definition `Fargate` (`awsvpc`, cpu/mem, logging) chạy ra 1 **task**.
- **Execution role** (kéo image `ECR` + ghi log — cho ECS agent) vs **task role** (quyền app gọi AWS API) — bẫy hay gặp.

**⏱️ ~40 phút** · **Yêu cầu trước:** Docker đang chạy; có **default VPC** trong Region.

### Các bước
1. Tạo repo `ECR` (bật scan on push) + lifecycle policy (dọn image cũ).
   ```bash
   aws ecr create-repository --repository-name lab8-app \
     --image-scanning-configuration scanOnPush=true
   REPO_URI=$(aws ecr describe-repositories --repository-names lab8-app \
     --query 'repositories[0].repositoryUri' --output text)

   cat > lifecycle.json <<'EOF'
   { "rules": [{ "rulePriority":1, "description":"keep last 3",
     "selection": { "tagStatus":"any","countType":"imageCountMoreThan","countNumber":3 },
     "action": { "type":"expire" } }] }
   EOF
   aws ecr put-lifecycle-policy --repository-name lab8-app --lifecycle-policy-text file://lifecycle.json
   ```

2. Build image nhỏ (dùng base **public ECR** để tránh Docker Hub rate limit), login rồi push.
   ```bash
   cat > Dockerfile <<'EOF'
   FROM public.ecr.aws/amazonlinux/amazonlinux:2023
   CMD ["sh","-c","echo 'Hello from Fargate task'; echo region=$AWS_REGION; sleep 20; echo done"]
   EOF

   aws ecr get-login-password --region $AWS_REGION \
     | docker login --username AWS --password-stdin ${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com
   docker build -t lab8-app:latest .
   docker tag lab8-app:latest ${REPO_URI}:latest
   docker push ${REPO_URI}:latest
   ```

3. Tạo **2 role** riêng biệt (cùng trust `ecs-tasks.amazonaws.com`).
   ```bash
   cat > trust-ecs.json <<'EOF'
   { "Version":"2012-10-17","Statement":[{"Effect":"Allow",
     "Principal":{"Service":"ecs-tasks.amazonaws.com"},"Action":"sts:AssumeRole"}] }
   EOF
   # Execution role: kéo image ECR + ghi CloudWatch Logs (cho ECS agent)
   aws iam create-role --role-name lab8-ecs-execution --assume-role-policy-document file://trust-ecs.json
   aws iam attach-role-policy --role-name lab8-ecs-execution \
     --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy
   # Task role: quyền cho APP trong container gọi AWS API (ví dụ list S3)
   aws iam create-role --role-name lab8-ecs-task --assume-role-policy-document file://trust-ecs.json
   aws iam put-role-policy --role-name lab8-ecs-task --policy-name app-perms \
     --policy-document '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Action":"s3:ListAllMyBuckets","Resource":"*"}]}'
   EXEC_ROLE_ARN=arn:aws:iam::${ACCOUNT_ID}:role/lab8-ecs-execution
   TASK_ROLE_ARN=arn:aws:iam::${ACCOUNT_ID}:role/lab8-ecs-task
   ```

4. Log group + đăng ký task definition `Fargate` (khai cả 2 role).
   ```bash
   aws logs create-log-group --log-group-name /ecs/lab8-app

   cat > taskdef.json <<EOF
   {
     "family": "lab8-app",
     "requiresCompatibilities": ["FARGATE"],
     "networkMode": "awsvpc",
     "cpu": "256", "memory": "512",
     "executionRoleArn": "${EXEC_ROLE_ARN}",
     "taskRoleArn": "${TASK_ROLE_ARN}",
     "containerDefinitions": [{
       "name": "app",
       "image": "${REPO_URI}:latest",
       "essential": true,
       "logConfiguration": {
         "logDriver": "awslogs",
         "options": {
           "awslogs-group": "/ecs/lab8-app",
           "awslogs-region": "${AWS_REGION}",
           "awslogs-stream-prefix": "ecs"
         }
       }
     }]
   }
   EOF
   aws ecs register-task-definition --cli-input-json file://taskdef.json
   ```

5. Tạo cluster + `run-task` trên `Fargate` (dùng subnet/SG mặc định; `assignPublicIp=ENABLED` để kéo image `ECR`).
   ```bash
   aws ecs create-cluster --cluster-name lab8-cluster
   SUBNET=$(aws ec2 describe-subnets --filters "Name=default-for-az,Values=true" \
     --query 'Subnets[0].SubnetId' --output text)
   SG=$(aws ec2 describe-security-groups --filters "Name=group-name,Values=default" \
     --query 'SecurityGroups[0].GroupId' --output text)
   aws ecs run-task --cluster lab8-cluster --launch-type FARGATE \
     --task-definition lab8-app \
     --network-configuration "awsvpcConfiguration={subnets=[$SUBNET],securityGroups=[$SG],assignPublicIp=ENABLED}"
   ```

### ✅ Kiểm chứng
- Theo dõi task đến khi chạy rồi STOPPED, và xem log:
  ```bash
  aws ecs list-tasks --cluster lab8-cluster
  aws ecs describe-tasks --cluster lab8-cluster \
    --tasks $(aws ecs list-tasks --cluster lab8-cluster --query 'taskArns[0]' --output text) \
    --query 'tasks[0].{last:lastStatus,stopped:stoppedReason}'
  aws logs tail /ecs/lab8-app --since 10m       # thấy "Hello from Fargate task"
  ```
- **Bẫy role (quan trọng):** nếu bỏ `executionRoleArn` (hoặc thiếu quyền) → task fail ở bước **kéo image** với `CannotPullContainerError` — đây là dấu hiệu thiếu **execution role**, KHÔNG phải task role. Task role chỉ ảnh hưởng quyền của app **lúc chạy** (ví dụ gọi `s3:ListAllMyBuckets`).

### 🧹 Dọn dẹp
```bash
# đợi task về STOPPED trước khi xoá cluster
aws ecs deregister-task-definition --task-definition lab8-app:1   # task definition không tính phí nhưng nên dọn
aws ecs delete-cluster --cluster lab8-cluster
aws ecr delete-repository --repository-name lab8-app --force
aws logs delete-log-group --log-group-name /ecs/lab8-app
aws iam detach-role-policy --role-name lab8-ecs-execution \
  --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy
aws iam delete-role --role-name lab8-ecs-execution
aws iam delete-role-policy --role-name lab8-ecs-task --policy-name app-perms
aws iam delete-role --role-name lab8-ecs-task
docker rmi lab8-app:latest ${REPO_URI}:latest 2>/dev/null || true
rm -f Dockerfile taskdef.json lifecycle.json trust-ecs.json
```

### 🧠 Ý nghĩa với đề thi
- **Execution role** = kéo image `ECR` + ghi log (cấp cho ECS agent); **task role** = quyền cho app trong container gọi AWS API. Kéo image lỗi/thiếu quyền log → thiếu **execution role**.
- `Fargate` bắt buộc `networkMode: awsvpc` (mỗi task có ENI riêng); `Fargate` = serverless, không quản EC2.
- `ECR`: `get-login-password | docker login` → `tag` → `push`; `lifecycle policy` dọn image cũ, `scanOnPush` quét lỗ hổng.

---

> ✅ Xong 6 lab? Đối chiếu lại [Lab checklist trong README](README.md#-lab-checklist) rồi làm [bộ câu hỏi luyện tập](questions.md) và **⭐ MINI-MOCK Domain 3 (~25 câu)** — phải đạt **≥70%** trước khi sang Tuần 9.
