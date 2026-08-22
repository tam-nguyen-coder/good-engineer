# Question #407 - Topic 1

A company is implementing a shared storage solution for a gaming application that is hosted in the AWS Cloud. The company needs the ability to use Lustre clients to access data. The solution must be fully managed. Which solution meets these requirements?

## Options

**A.** Create an AWS DataSync task that shares the data as a mountable file system. Mount the file system to the application server.

**B.** Create an AWS Storage Gateway file gateway. Create a file share that uses the required client protocol. Connect the application server to the file share.

**C.** Create an Amazon Elastic File System (Amazon EFS) file system, and configure it to support Lustre. Attach the file system to the origin server. Connect the application server to the file system.

**D.** Create an Amazon FSx for Lustre file system. Attach the file system to the origin server. Connect the application server to the file system.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Gaming app needs shared storage with Lustre client support. Fully managed.
- **Existing Resources:** Gaming application hosted in AWS Cloud.
- **Current Issue/Goal:** Find managed Lustre file system.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `Lustre` | High-performance parallel file system. FSx for Lustre = AWS managed Lustre. |
| `fully managed` | AWS managed service, không tự build. |
| `gaming application` | High throughput, low latency (Lustre use case). |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Storage / File system
- **Constraints:** Lustre protocol, fully managed

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- Amazon FSx for Lustre: fully managed Lustre file system, hỗ trợ Lustre clients.
- High-performance cho gaming, HPC, media processing.
- Tích hợp S3 để import/export data.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- AWS DataSync: data transfer tool, không phải file system. Không hỗ trợ Lustre.

**❌ Đáp án B:**
- Storage Gateway file gateway: hỗ trợ NFS/SMB, không phải Lustre.

**❌ Đáp án C:**
- EFS: NFS-based, không hỗ trợ Lustre. EFS không thể "configure to support Lustre".

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Lustre = FSx for Lustre (gaming/HPC). EFS = NFS, không phải Lustre."*

