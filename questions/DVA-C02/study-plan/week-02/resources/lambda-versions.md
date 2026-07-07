# Manage Lambda function versions

> **Nguồn (AWS official):** https://docs.aws.amazon.com/lambda/latest/dg/configuration-versions.html
> **Tuần:** 2 — `Lambda` nâng cao · **Loại:** AWS Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)
- `$LATEST` = phiên bản chưa publish, **mutable**; mỗi lần deploy code sẽ **ghi đè** lên `$LATEST`.
- **Publish version** → tạo **snapshot bất biến (immutable)** của code + phần lớn config; sau đó KHÔNG sửa được code/ARN.
- Mỗi version có **ARN riêng có số** (qualified ARN, vd `...:function:helloworld:42`); ARN không có số là **unqualified** (ngầm gọi `$LATEST`).
- **Không thể tạo alias từ unqualified ARN.**
- Lambda **không tái sử dụng số version** (monotonically increasing), kể cả sau khi xóa và tạo lại function.
- Chỉ publish version mới **nếu code đã thay đổi** so với version cuối; nếu `$LATEST` giống hệt version trước thì không publish được.
- Vẫn **cấu hình được sau khi publish**: triggers, destinations, provisioned concurrency, async invocation, DB connections/proxies.
- **Reserved concurrency** là "operational setting" → thay đổi nó **KHÔNG** kích hoạt publish version mới.

---

## 📄 Nội dung (trích từ tài liệu gốc)

You can use versions to manage the deployment of your functions. For example, you can publish a new version of a function for beta testing without affecting users of the stable production version. Lambda creates a new version of your function each time that you publish the function. The new version is a copy of the unpublished version of the function. The unpublished version is named `$LATEST`.

Importantly, any time you deploy your function code, you overwrite the current code in `$LATEST`. To save the current iteration of `$LATEST`, create a new function version. If `$LATEST` is identical to a previously published version, you won't be able to create a new version until you deploy changes to `$LATEST`. These changes can include updating the code, or modifying the function configuration settings.

After you publish a function version, its code, runtime, architecture, memory, layers, and most other configuration settings are immutable. This means that you can't change these settings without publishing a new version from `$LATEST`. You can configure the following items for a published function version:
- Triggers
- Destinations
- Provisioned concurrency
- Asynchronous invocation
- Database connections and proxies

**Note:** When using runtime management controls with **Auto** mode, the runtime version used by the function version is updated automatically. When using **Function update** or **Manual** mode, the runtime version is not updated.

## Creating function versions

You can change the function code and settings only on the unpublished version of a function. When you publish a version, Lambda locks the code and most of the settings to maintain a consistent experience for users of that version.

**To create a new function version (console)**

1. Open the Functions page of the Lambda console.
2. Choose a function and then choose the **Versions** tab.
3. On the versions configuration page, choose **Publish new version**.
4. (Optional) Enter a version description.
5. Choose **Publish**.

Alternatively, you can publish a version of a function using the `PublishVersion` API operation.

The following AWS CLI command publishes a new version of a function:

```
aws lambda publish-version --function-name my-function
```

Output:

```
{
  "FunctionName": "my-function",
  "FunctionArn": "arn:aws:lambda:us-east-2:123456789012:function:my-function:1",
  "Version": "1",
  "Role": "arn:aws:iam::123456789012:role/lambda-role",
  "Handler": "function.handler",
  "Runtime": "nodejs24.x",
  ...
}
```

**Note:** Lambda assigns monotonically increasing sequence numbers for versioning. Lambda never reuses version numbers, even after you delete and recreate a function.

## Using versions

You can reference your Lambda function using either a qualified ARN or an unqualified ARN.

- **Qualified ARN** – The function ARN with a version suffix. The following example refers to version 42 of the `helloworld` function.

  ```
  arn:aws:lambda:aws-region:acct-id:function:helloworld:42
  ```

- **Unqualified ARN** – The function ARN without a version suffix.

  ```
  arn:aws:lambda:aws-region:acct-id:function:helloworld
  ```

You can use a qualified or an unqualified ARN in all relevant API operations. However, you can't use an unqualified ARN to create an alias.

If you decide not to publish function versions, you can invoke the function using either the qualified or unqualified ARN in your event source mapping. When you invoke a function using an unqualified ARN, Lambda implicitly invokes `$LATEST`.

The qualified ARN for each Lambda function version is unique. After you publish a version, you can't change the ARN or the function code.

Lambda publishes a new function version only if the code has never been published, or if the code has changed from the last published version. If there is no change, the function version remains at the last published version.

When you publish a version, Lambda creates an immutable snapshot of your function's code and configuration. Not all configuration changes trigger the publication of a new version. The following configuration changes qualify a function for version publication:
- Function code
- Environment variables
- Runtime
- Handler
- Layers
- Memory size
- Timeout
- VPC configuration
- Dead Letter Queue (DLQ) configuration
- IAM role
- Description
- Architecture (x86_64 or arm64)
- Ephemeral storage size
- Package type
- Code storage mode (switching between Lambda-managed and self-managed S3 storage)
- Logging configuration
- File system configuration
- SnapStart
- Tracing configuration

Operational settings such as **reserved concurrency** don't trigger the publication of a new version when changed.

## Granting permissions

You can use a resource-based policy or an identity-based policy to grant access to your function. The scope of the permission depends on whether you apply the policy to a function or to one version of a function.

You can simplify the management of event sources and IAM policies by using function aliases.
