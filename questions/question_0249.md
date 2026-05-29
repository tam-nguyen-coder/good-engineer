# Question #249 - Topic 1

A company is implementing a shared storage solution for a media application that is hosted in the AWS Cloud. The company needs the ability to use SMB clients to access data. The solution must be fully managed. Which AWS solution meets these requirements?

## Options

**A.** Create an AWS Storage Gateway volume gateway. Create a file share that uses the required client protocol. Connect the application server to the file share.

**B.** Create an AWS Storage Gateway tape gateway. Configure tapes to use Amazon S3. Connect the application server to the tape gateway.

**C.** Create an Amazon EC2 Windows instance. Install and configure a Windows file share role on the instance. Connect the application server to the file share.

**D.** Create an Amazon FSx for Windows File Server file system. Attach the file system to the origin server. Connect the application server to the file system.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Media app, shared storage, SMB clients. Fully managed.
- **Existing Resources:** Media application.
- **Current Issue/Goal:** Managed SMB file system.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `SMB clients` | Cần SMB protocol support |
| `fully managed` | **FSx for Windows File Server** |
| `shared storage` | File system accessible by multiple servers |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Storage / File system
- **Constraints:** SMB, fully managed

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- **FSx for Windows File Server** — fully managed Windows file system, hỗ trợ SMB protocol.
- HA built-in (Multi-AZ).
- Tích hợp với Active Directory.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Volume gateway — block storage (iSCSI), không SMB.

**❌ Đáp án B:**
- Tape gateway — VTL (Virtual Tape Library), không SMB.

**❌ Đáp án C:**
- EC2 Windows — không fully managed (phải tự quản lý).

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"FSx for Windows = managed SMB. Volume Gateway = iSCSI. Tape Gateway = VTL. EC2 = self-managed"*
