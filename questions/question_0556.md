# Question #556 - Topic 1

A solutions architect is using an AWS CloudFormation template to deploy a three-tier web application. The web application consists of a web tier and an application tier that stores and retrieves user data in Amazon DynamoDB tables. The web and application tiers are hosted on Amazon EC2 instances, and the database tier is not publicly accessible. The application EC2 instances need to access the DynamoDB tables without exposing API credentials in the template. What should the solutions architect do to meet these requirements?

## Options

**A.** Create an IAM role to read the DynamoDB tables. Associate the role with the application instances by referencing an instance profile.

**B.** Create an IAM role that has the required permissions to read and write from the DynamoDB tables. Add the role to the EC2 instance profile, and associate the instance profile with the application instances.

**C.** Use the parameter section in the AWS CloudFormation template to have the user input access and secret keys from an already-created IAM user that has the required permissions to read and write from the DynamoDB tables.

**D.** Create an IAM user in the AWS CloudFormation template that has the required permissions to read and write from the DynamoDB tables. Use the GetAtt function to retrieve the access and secret keys, and pass them to the application instances through the user data.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Dùng CloudFormation deploy 3-tier web app: web tier (EC2), application tier (EC2), database tier (DynamoDB). Application EC2 instances cần truy cập DynamoDB mà không expose credentials trong template.
- **Existing Resources:** CloudFormation template, EC2 instances, DynamoDB tables.
- **Current Issue/Goal:** Cấp quyền EC2 → DynamoDB mà không hardcode credentials.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `without exposing API credentials` | Không được hardcode access key/secret key |
| `IAM role` | Cách an toàn để cấp permissions cho EC2 |
| `instance profile` | Container cho IAM role, gắn vào EC2 instance |
| `read and write` | Cần cả read và write permissions |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most appropriate solution
- **Constraints:** Không exposed credentials, EC2 cần truy cập DynamoDB

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- Tạo IAM role với policy cho phép read/write DynamoDB tables.
- Gán IAM role vào instance profile.
- Trong CloudFormation, associate instance profile với EC2 instances.
- EC2 tự động lấy temporary credentials từ instance metadata service – không cần lưu trữ credentials trong template.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A (IAM role read only):** Chỉ có quyền read, nhưng đề bài yêu cầu "stores and retrieves user data" – cần cả read và write.

**❌ Đáp án C (Parameter section + user input keys):** Yêu cầu user nhập access/secret keys vào template parameters, vẫn expose credentials (trong template, logs). Best practice không khuyến khích.

**❌ Đáp án D (IAM user + GetAtt + user data):** Tạo IAM user trong CloudFormation và dùng GetAtt lấy keys là không an toàn. Keys xuất hiện trong template outputs, CloudFormation logs, và user data – vi phạm "without exposing API credentials".

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"EC2 → AWS service = IAM role + instance profile. Never hardcode keys. Temporary credentials from metadata service."*
