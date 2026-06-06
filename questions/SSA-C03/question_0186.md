# Question #186 - Topic 1

A company has a Windows-based application that must be migrated to AWS. The application requires the use of a shared Windows file system attached to multiple Amazon EC2 Windows instances that are deployed across multiple Availability Zones. What should a solutions architect do to meet this requirement?

## Options

**A.** Configure AWS Storage Gateway in volume gateway mode. Mount the volume to each Windows instance.

**B.** Configure Amazon FSx for Windows File Server. Mount the Amazon FSx file system to each Windows instance.

**C.** Configure a file system by using Amazon Elastic File System (Amazon EFS). Mount the EFS file system to each Windows instance.

**D.** Configure an Amazon Elastic Block Store (Amazon EBS) volume with the required size. Attach each EC2 instance to the volume. Mount the file system within the volume to each Windows instance.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Windows app, need shared file system across multiple Windows EC2 instances across AZs.
- **Existing Resources:** Windows-based application.
- **Current Issue/Goal:** Shared Windows file system, multi-AZ.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `Windows-based application` | Windows file system — **FSx for Windows File Server** |
| `shared Windows file system` | SMB protocol |
| `multiple Availability Zones` | Multi-AZ access |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Storage / Migration
- **Constraints:** Windows, shared, multi-AZ

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- **FSx for Windows File Server** — managed Windows-native file system, hỗ trợ SMB protocol.
- Multi-AZ deployment — accessible từ instances ở nhiều AZs.
- Designed for Windows workloads.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Storage Gateway volume gateway — block storage (iSCSI), không phải shared file system.

**❌ Đáp án C:**
- EFS — NFS protocol, không hỗ trợ Windows instances.

**❌ Đáp án D:**
- EBS — single-attach (trừ io2 Multi-Attach nhưng limited), không thể attach đến nhiều instances.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"FSx for Windows = Windows shared file system. EFS = Linux only. EBS = single-attach"*
