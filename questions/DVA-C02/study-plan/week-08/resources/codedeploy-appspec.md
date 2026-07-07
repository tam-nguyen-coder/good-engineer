# CodeDeploy AppSpec file reference

> **Nguồn (AWS official):** https://docs.aws.amazon.com/codedeploy/latest/userguide/reference-appspec-file.html
> **Tuần:** 8 — Deployment / CI-CD / IaC · **Loại:** AWS Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)
- AppSpec file là YAML hoặc JSON. Với **EC2/On-Premises** BẮT BUỘC là YAML, tên `appspec.yml`, đặt ở **root** của source; sai vị trí/tên → deployment fail.
- 3 compute platform → 3 cách dùng AppSpec khác nhau: **ECS** (chỉ `TaskDefinition` + `LoadBalancerInfo`, hooks chạy Lambda), **Lambda** (Lambda function version + validation functions), **EC2/On-Premises** (`files` + `hooks` chạy script trên instance).
- Section **`hooks`** = trái tim của AppSpec cho EC2/On-Premises: ánh xạ script vào các lifecycle event. Bẫy thi: nhớ thứ tự lifecycle event (đặc biệt `ApplicationStop` → `BeforeInstall` → `AfterInstall` → `ApplicationStart` → `ValidateService`).
- Mỗi hook có thể cấu hình `location` (đường dẫn script), `timeout` (giây), `runas` (user chạy script).
- ECS/Lambda deployment KHÔNG dùng `files`/EC2 hooks; ECS AppSpec chỉ trỏ tới task definition ARN và container/port cho ALB/NLB reroute traffic.
- Spacing trong YAML rất quan trọng — sai số khoảng trắng → lỗi khó debug. `version: 0.0` cho EC2/On-Premises.
- Revision = archive (zip/tar/tar.gz) chứa AppSpec + nội dung deploy; upload lên S3 hoặc GitHub. Lưu ý: tar/tar.gz KHÔNG hỗ trợ Windows Server.

---

## 📄 Nội dung (trích từ tài liệu gốc)

The application specification file (AppSpec file) is a YAML-formatted or JSON-formatted file used by CodeDeploy to manage a deployment.

**Note:** The AppSpec file for an EC2/On-Premises deployment must be named `appspec.yml`, unless you are performing a local deployment.

**Topics**
- AppSpec files on an Amazon ECS compute platform
- AppSpec files on an AWS Lambda compute platform
- AppSpec files on an EC2/on-premises compute platform
- AppSpec File structure
- AppSpec File example
- AppSpec File spacing
- Validate your AppSpec File and file location

## AppSpec files on an Amazon ECS compute platform

For Amazon ECS compute platform applications, the AppSpec file is used by CodeDeploy to determine:
- Your Amazon ECS task definition file. This is specified with its ARN in the `TaskDefinition` instruction in the AppSpec file.
- The container and port in your replacement task set where your Application Load Balancer or Network Load Balancer reroutes traffic during a deployment. This is specified with the `LoadBalancerInfo` instruction.
- Optional information about your Amazon ECS service, such as the platform version on which it runs, its subnets, and its security groups.
- Optional Lambda functions to run during hooks that correspond with lifecycle events during an Amazon ECS deployment.

## AppSpec files on an AWS Lambda compute platform

For AWS Lambda compute platform applications, the AppSpec file is used by CodeDeploy to determine:
- Which Lambda function version to deploy.
- Which Lambda functions to use as validation tests.

An AppSpec file can be YAML-formatted or JSON-formatted. You can also enter the contents of an AppSpec file directly into the CodeDeploy console when you create a deployment.

## AppSpec files on an EC2/on-premises compute platform

If your application uses the EC2/On-Premises compute platform, the AppSpec file must be a YAML-formatted file named `appspec.yml` and it must be placed in the root of the directory structure of an application's source code. Otherwise, deployments fail. It is used by CodeDeploy to determine:
- What it should install onto your instances from your application revision in Amazon S3 or GitHub.
- Which lifecycle event hooks to run in response to deployment lifecycle events.

After you have a completed AppSpec file, you bundle it, along with the content to deploy, into an archive file (zip, tar, or compressed tar).

**Note:** The tar and compressed tar archive file formats (.tar and .tar.gz) are not supported for Windows Server instances.

After you have a bundled archive file (known in CodeDeploy as a *revision*), you upload it to an Amazon S3 bucket or Git repository. Then you use CodeDeploy to deploy the revision. The appspec.yml for an EC2/On-Premises compute platform deployment is saved in the root directory of your revision.

## AppSpec File spacing

The following is the correct format for AppSpec file spacing. The numbers in square brackets indicate the number of spaces that must occur between items (e.g. `[4]` means insert four spaces). CodeDeploy raises an error that might be difficult to debug if the locations and number of spaces are not correct.

```
version:[1]version-number
os:[1]operating-system-name
files:
[2]-[1]source:[1]source-files-location
[4]destination:[1]destination-files-location
permissions:
[2]-[1]object:[1]object-specification
[4]pattern:[1]pattern-specification
[4]except:[1]exception-specification
[4]owner:[1]owner-account-name
[4]group:[1]group-name
[4]mode:[1]mode-specification
[4]acls:
[6]-[1]acls-specification
[4]context:
[6]user:[1]user-specification
[6]type:[1]type-specification
[6]range:[1]range-specification
[4]type:
[6]-[1]object-type
hooks:
[2]deployment-lifecycle-event-name:
[4]-[1]location:[1]script-location
[6]timeout:[1]timeout-in-seconds
[6]runas:[1]user-name
```

Here is an example of a correctly spaced AppSpec file (EC2/On-Premises):

```yaml
version: 0.0
os: linux
files:
  - source: /
    destination: /var/www/html/WordPress
hooks:
  BeforeInstall:
    - location: scripts/install_dependencies.sh
      timeout: 300
      runas: root
  AfterInstall:
    - location: scripts/change_permissions.sh
      timeout: 300
      runas: root
  ApplicationStart:
    - location: scripts/start_server.sh
    - location: scripts/create_test_db.sh
      timeout: 300
      runas: root
  ApplicationStop:
    - location: scripts/stop_server.sh
      timeout: 300
      runas: root
```

For more information about spacing, see the YAML specification.
