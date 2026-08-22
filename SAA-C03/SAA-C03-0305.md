# Question #305 - Topic 1

A company is designing a shared storage solution for a gaming application that is hosted in the AWS Cloud. The company needs the ability to use SMB clients to access data. The solution must be fully managed. Which AWS solution meets these requirements?

## Options

**A.** Create an AWS DataSync task that shares the data as a mountable file system. Mount the file system to the application server.

**B.** Create an Amazon EC2 Windows instance. Install and configure a Windows file share role on the instance. Connect the application server to the file share.

**C.** Create an Amazon FSx for Windows File Server file system. Attach the file system to the origin server. Connect the application server to the file system.

**D.** Create an Amazon S3 bucket. Assign an IAM role to the application to grant access to the S3 bucket. Mount the S3 bucket to the application server.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Gaming app cần shared storage với SMB access, fully managed.
- **Existing Resources:** Gaming application on AWS Cloud.
- **Current Issue/Goal:** Shared storage solution, SMB protocol, fully managed.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `SMB clients` | Windows file sharing protocol (Server Message Block). |
| `fully managed` | AWS quản lý hoàn toàn, không cần tự cấu hình OS. |
| `Amazon FSx for Windows File Server` | Managed Windows file server, hỗ trợ SMB protocol. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Which solution meets requirements
- **Constraints:** SMB access, fully managed

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- FSx for Windows File Server là fully managed Windows file server, hỗ trợ SMB protocol.
- Tích hợp với Active Directory, có sẵn tính năng shadow copies, deduplication.
- Không cần quản lý OS hay cài đặt file share role.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- DataSync là data transfer service, không phải shared file system. Không hỗ trợ SMB mount.

**❌ Đáp án B:**
- EC2 Windows + tự cài file share role → không fully managed (phải tự patch, bảo trì).

**❌ Đáp án D:**
- S3 không support SMB protocol natively. Mount S3 bucket cần third-party tool (VD: s3fs) → không fully managed, không SMB.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"SMB + fully managed → FSx for Windows File Server. EC2 tự cài = không managed. S3 = không SMB."*
