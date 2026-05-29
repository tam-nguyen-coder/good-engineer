# Question #319 - Topic 1

A company has hundreds of Amazon EC2 Linux-based instances in the AWS Cloud. Systems administrators have used shared SSH keys to manage the instances. After a recent audit, the company's security team is mandating the removal of all shared keys. A solutions architect must design a solution that provides secure access to the EC2 instances. Which solution will meet this requirement with the LEAST amount of administrative overhead?

## Options

**A.** Use AWS Systems Manager Session Manager to connect to the EC2 instances.

**B.** Use AWS Security Token Service (AWS STS) to generate one-time SSH keys on demand.

**C.** Allow shared SSH access to a set of bastion instances. Configure all other instances to allow only SSH access from the bastion instances.

**D.** Use an Amazon Cognito custom authorizer to authenticate users. Invoke an AWS Lambda function to generate a temporary SSH key.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Hundreds of Linux EC2 instances. Shared SSH keys bị cấm. Cần secure access với least administrative overhead.
- **Existing Resources:** EC2 instances, administrators.
- **Current Issue/Goal:** Remove shared SSH keys, provide secure access.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `removal of all shared keys` | Không dùng SSH keys shared nữa. |
| `least amount of administrative overhead` | Không muốn quản lý bastion hosts, SSH keys. |
| `AWS Systems Manager Session Manager` | Cho phép access EC2 instances qua IAM (không cần SSH keys, không cần bastion, không cần open SSH port). |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Least administrative overhead
- **Constraints:** No shared SSH keys, secure access to hundreds of instances

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- Session Manager: kết nối đến EC2 instances qua SSM Agent, không cần SSH keys, không cần bastion hosts, không cần mở port 22.
- Authentication và authorization dựa trên IAM → quản lý centralized.
- Administrative overhead thấp nhất: không cần quản lý keys, bastion, security groups phức tạp.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- STS generate SSH keys vẫn cần cơ chế distribute keys + quản lý → overhead cao.

**❌ Đáp án C:**
- Bastion hosts: cần quản lý thêm instances, security groups, keys → overhead cao hơn Session Manager.

**❌ Đáp án D:**
- Cognito + Lambda generate temp SSH keys → phức tạp, cần maintain custom solution.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"No SSH keys → Systems Manager Session Manager (IAM-based, no bastion, no port 22)."*
