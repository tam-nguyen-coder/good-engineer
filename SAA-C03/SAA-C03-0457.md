# Question #457 - Topic 1

A company that uses AWS is building an application to transfer data to a product manufacturer. The company has its own identity provider (IdP). The company wants the IdP to authenticate application users while the users use the application to transfer data. The company must use Applicability Statement 2 (AS2) protocol. Which solution will meet these requirements?

## Options

**A.** Use AWS DataSync to transfer the data. Create an AWS Lambda function for IdP authentication.

**B.** Use Amazon AppFlow flows to transfer the data. Create an Amazon Elastic Container Service (Amazon ECS) task for IdP authentication.

**C.** Use AWS Transfer Family to transfer the data. Create an AWS Lambda function for IdP authentication.

**D.** Use AWS Storage Gateway to transfer the data. Create an Amazon Cognito identity pool for IdP authentication.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Transfer data to manufacturer. Custom IdP for user auth. Must use AS2 protocol.
- **Existing Resources:** IdP, application.
- **Current Issue/Goal:** AS2 data transfer + custom IdP auth.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `AS2` | Applicability Statement 2: B2B protocol. AWS Transfer Family supports AS2. |
| `own identity provider` | Custom IdP → Lambda function for authentication. |
| `Transfer Family` | Managed AS2, SFTP, FTPS, FTP. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Data transfer / B2B
- **Constraints:** AS2 protocol, custom IdP

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- AWS Transfer Family: managed service hỗ trợ AS2 protocol.
- Lambda function: custom IdP authentication cho Transfer Family users.
- AS2: B2B EDI protocol phổ biến.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- DataSync: data transfer service, không hỗ trợ AS2 protocol.

**❌ Đáp án B:**
- AppFlow: SaaS integration (Salesforce, etc.), không hỗ trợ AS2.

**❌ Đáp án D:**
- Storage Gateway: hybrid storage, không hỗ trợ AS2.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"AS2 + custom IdP = AWS Transfer Family + Lambda auth."*