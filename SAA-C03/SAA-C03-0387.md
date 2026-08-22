# Question #387 - Topic 1

A new employee has joined a company as a deployment engineer. The deployment engineer will be using AWS CloudFormation templates to create multiple AWS resources. A solutions architect wants the deployment engineer to perform job activities while following the principle of least privilege. Which combination of actions should the solutions architect take to accomplish this goal? (Choose two.)

## Options

**A.** Have the deployment engineer use AWS account root user credentials for performing AWS CloudFormation stack operations.

**B.** Create a new IAM user for the deployment engineer and add the IAM user to a group that has the PowerUsers IAM policy attached.

**C.** Create a new IAM user for the deployment engineer and add the IAM user to a group that has the AdministratorAccess IAM policy attached.

**D.** Create a new IAM user for the deployment engineer and add the IAM user to a group that has an IAM policy that allows AWS CloudFormation actions only.

**E.** Create an IAM role for the deployment engineer to explicitly define the permissions specific to the AWS CloudFormation stack and launch stacks using that IAM role.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Deployment engineer cần dùng CloudFormation. Cần least privilege.
- **Existing Resources:** (none specified)
- **Current Issue/Goal:** Grant only necessary CloudFormation permissions.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `principle of least privilege` | Chỉ cấp quyền tối thiểu cần thiết. |
| `AWS CloudFormation templates` | Engineer cần permissions để create/update/delete stacks. |
| `IAM policy that allows CloudFormation actions only` | Narrowest scope possible (D). |
| `IAM role with specific permissions` | Role-based access + specific stack permissions (E). |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Choose two, least privilege
- **Constraints:** CloudFormation operations

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D và E**

**Giải thích:**
- **D:** IAM policy chỉ cho phép CloudFormation actions (CreateStack, UpdateStack, DeleteStack...) → narrow scope.
- **E:** IAM role với permissions cụ thể cho CloudFormation stack → role can be assumed as needed, following least privilege.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Root user: full access, violation of least privilege. Không bao giờ dùng root cho日常工作.

**❌ Đáp án B:**
- PowerUsers: có thể create/modify resources nhưng không quản lý IAM. Quá rộng cho chỉ CloudFormation.

**❌ Đáp án C:**
- AdministratorAccess: full admin → violation of least privilege.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Least privilege cho CloudFormation → IAM policy CloudFormation actions only + IAM role specific permissions. PowerUsers/Admin = quá rộng."*
