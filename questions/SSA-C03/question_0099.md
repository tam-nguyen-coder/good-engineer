# Question #99 - Topic 1

A company is implementing a shared storage solution for a gaming application that is hosted in an on-premises data center. The company needs the ability to use Lustre clients to access data. The solution must be fully managed. Which solution meets these requirements?

## Options

**A.** Create an AWS Storage Gateway file gateway. Create a file share that uses the required client protocol. Connect the application server to the file share.

**B.** Create an Amazon EC2 Windows instance. Install and configure a Windows file share role on the instance. Connect the application server to the file share.

**C.** Create an Amazon Elastic File System (Amazon EFS) file system, and configure it to support Lustre. Attach the file system to the origin server. Connect the application server to the file system.

**D.** Create an Amazon FSx for Lustre file system. Attach the file system to the origin server. Connect the application server to the file system.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Gaming app on-prem, cần shared storage với Lustre clients.
- **Existing Resources:** On-prem gaming application.
- **Current Issue/Goal:** Fully managed Lustre file system.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `Lustre clients` | Cần **Lustre** file system protocol |
| `fully managed` | Managed service, không tự quản lý |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Storage
- **Constraints:** Lustre protocol, fully managed

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- **Amazon FSx for Lustre** — fully managed Lustre file system, hiệu năng cao.
- Lustre là high-performance file system thường dùng cho gaming, HPC, media processing.
- Tích hợp với S3, có thể truy cập từ on-prem qua VPN/Direct Connect.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Storage Gateway File Gateway hỗ trợ SMB/NFS, **không hỗ trợ Lustre**.

**❌ Đáp án B:**
- EC2 Windows + file share — không phải "fully managed", không hỗ trợ Lustre.

**❌ Đáp án C:**
- **EFS không hỗ trợ Lustre** — EFS dùng NFS protocol.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"FSx for Lustre = high-performance Lustre (HPC/gaming). EFS = NFS. Storage Gateway = SMB/NFS"*
