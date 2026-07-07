# Defining Lambda function permissions with an execution role

> **Nguồn (AWS official):** https://docs.aws.amazon.com/lambda/latest/dg/lambda-intro-execution-role.html
> **Tuần:** 1 — SDK/CLI + `Lambda` cơ bản · **Loại:** AWS Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)
- **Execution role** = IAM role cấp cho function quyền **truy cập các service/tài nguyên AWS khác** (vd gửi log tới `CloudWatch`, upload trace tới `X-Ray`, ghi `DynamoDB`). Đây là quyền của **chính function** — KHÁC với resource-based policy (ai được invoke).
- `Lambda` **tự động assume execution role** khi function được invoke — **không** tự gọi `sts:AssumeRole` trong code.
- **Trust policy** của role bắt buộc phải khai báo service principal **`lambda.amazonaws.com`** là trusted service thì Lambda mới assume được.
- Console mặc định tạo role tối thiểu gắn managed policy **`AWSLambdaBasicExecutionRole`** → cho phép ghi log vào `CloudWatch Logs`. Cần thêm quyền thì chọn "Use another role" / gắn policy khác (vd `AWSLambdaDynamoDBExecutionRole`).
- **CLI:** tạo role bằng `aws iam create-role --assume-role-policy-document ...` (trust policy inline hoặc `file://trust-policy.json`), rồi gắn quyền bằng `aws iam attach-role-policy --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole`.
- **Least privilege:** trước khi lên production, cắt bớt quyền thừa. Dùng **IAM Access Analyzer** đọc CloudTrail logs để sinh policy chỉ gồm quyền function thực sự dùng.

---

## 📄 Nội dung (trích từ tài liệu gốc)

A Lambda function's execution role is an AWS Identity and Access Management (IAM) role that grants the function permission to access AWS services and resources. For example, you might create an execution role that has permission to send logs to Amazon CloudWatch and upload trace data to AWS X-Ray.

Lambda automatically assumes your execution role when you invoke your function. You should avoid manually calling `sts:AssumeRole` to assume the execution role in your function code. If your use case requires that the role assumes itself, you must include the role itself as a trusted principal in your role's trust policy.

In order for Lambda to properly assume your execution role, the role's **trust policy must specify the Lambda service principal (`lambda.amazonaws.com`) as a trusted service.**

## Creating an execution role in the IAM console

By default, Lambda creates an execution role with minimal permissions when you create a function in the Lambda console. Specifically, this execution role includes the **`AWSLambdaBasicExecutionRole` managed policy**, which gives your function basic permissions to log events to Amazon CloudWatch Logs. You can select **Create default role** in the **Permissions** section.

You can choose an existing role by selecting **Use another role** in the **Permissions** section. If your Lambda function needs additional permissions (e.g., updating entries in an Amazon DynamoDB table in response to events), you can create a custom execution role with the necessary permissions.

**To configure an execution role from Console:**
1. Enter a **role name** in the Role details section.
2. In the **Policy** section, select **Use existing policy**.
3. Select the AWS managed policies to attach to your role. For example, if your function needs to access DynamoDB, select the **AWSLambdaDynamoDBExecutionRole** managed policy.
4. Choose **Create role**.

## Creating and managing roles with the AWS CLI

To create an execution role, use the **create-role** command. A role's trust policy gives the specified principals permission to assume the role. The following grants the Lambda service principal permission to assume your role:

```
aws iam create-role \
  --role-name lambda-ex \
  --assume-role-policy-document '{"Version": "2012-10-17", "Statement": [{ "Effect": "Allow", "Principal": {"Service": "lambda.amazonaws.com"}, "Action": "sts:AssumeRole"}]}'
```

You can also define the trust policy using a separate JSON file.

**Example `trust-policy.json`:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

```
aws iam create-role \
  --role-name lambda-ex \
  --assume-role-policy-document file://trust-policy.json
```

To add permissions to the role, use the **attach-role-policy** command. The following adds the `AWSLambdaBasicExecutionRole` managed policy to the `lambda-ex` execution role:

```
aws iam attach-role-policy --role-name lambda-ex --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
```

After you create your execution role, attach it to your function.

## Grant least privilege access to your Lambda execution role

When you first create an IAM role during development, you might grant permissions beyond what is required. Before publishing to production, as a best practice, adjust the policy to include only the required permissions.

Use **IAM Access Analyzer** to help identify the required permissions for the IAM execution role policy. IAM Access Analyzer reviews your AWS CloudTrail logs over the date range that you specify and generates a policy template with only the permissions that the function used during that time. You can use the template to create a managed policy with fine-grained permissions, then attach it to the IAM role.

## Related topics
- Viewing and updating permissions in the execution role
- Working with AWS managed policies in the execution role
- Using source function ARN to control function access behavior
