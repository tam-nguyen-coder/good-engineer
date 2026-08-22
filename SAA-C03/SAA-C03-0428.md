# Question #428 - Topic 1

A serverless application uses Amazon API Gateway, AWS Lambda, and Amazon DynamoDB. The Lambda function needs permissions to read and write to the DynamoDB table. Which solution will give the Lambda function access to the DynamoDB table MOST securely?

## Options

**A.** Create an IAM user with programmatic access to the Lambda function. Attach a policy to the user that allows read and write access to the DynamoDB table. Store the access_key_id and secret_access_key parameters as part of the Lambda environment variables. Ensure that other AWS users do not have read and write access to the Lambda function configuration.

**B.** Create an IAM role that includes Lambda as a trusted service. Attach a policy to the role that allows read and write access to the DynamoDB table. Update the configuration of the Lambda function to use the new role as the execution role.

**C.** Create an IAM user with programmatic access to the Lambda function. Attach a policy to the user that allows read and write access to the DynamoDB table. Store the access_key_id and secret_access_key parameters in AWS Systems Manager Parameter Store as secure string parameters. Update the Lambda function code to retrieve the secure string parameters before connecting to the DynamoDB table.

**D.** Create an IAM role that includes DynamoDB as a trusted service. Attach a policy to the role that allows read and write access from the Lambda function. Update the code of the Lambda function to attach to the new role as an execution role.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** API Gateway → Lambda → DynamoDB. Lambda needs read/write DynamoDB.
- **Existing Resources:** API Gateway, Lambda, DynamoDB.
- **Current Issue/Goal:** Grant Lambda permissions to DynamoDB most securely.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `MOST securely` | IAM execution role (best practice). Không dùng long-term credentials. |
| `execution role` | Lambda assume role khi chạy → temporary credentials. |
| `trusted service` | Lambda là trusted entity, DynamoDB là resource. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Security / IAM
- **Constraints:** Lambda → DynamoDB permissions

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- IAM execution role với Lambda là trusted service → Lambda assume role tự động.
- Attach policy với DynamoDB read/write permissions.
- Temporary credentials (STS), không hardcode, tự động rotate.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- IAM user + env variables: long-term credentials trong code → security risk.

**❌ Đáp án C:**
- IAM user + Parameter Store: tốt hơn env vars nhưng vẫn dùng long-term credentials, quản lý phức tạp.

**❌ Đáp án D:**
- DynamoDB là trusted service → sai. Lambda execution role trust Lambda, không phải DynamoDB.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Lambda permissions = IAM execution role (trust Lambda). Không dùng IAM user credentials."*