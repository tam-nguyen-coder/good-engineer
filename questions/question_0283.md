# Question #283 - Topic 1

A research company runs experiments that are powered by a simulation application and a visualization application. The simulation application runs on Linux and outputs intermediate data to an NFS share every 5 minutes. The visualization application is a Windows desktop application that displays the simulation output and requires an SMB file system. The company maintains two synchronized file systems. This strategy is causing data duplication and inefficient resource usage. The company needs to migrate the applications to AWS without making code changes to either application. Which solution will meet these requirements?

## Options

**A.** Migrate both applications to AWS Lambda. Create an Amazon S3 bucket to exchange data between the applications.

**B.** Migrate both applications to Amazon Elastic Container Service (Amazon ECS). Configure Amazon FSx File Gateway for storage.

**C.** Migrate the simulation application to Linux Amazon EC2 instances. Migrate the visualization application to Windows EC2 instances. Configure Amazon Simple Queue Service (Amazon SQS) to exchange data between the applications.

**D.** Migrate the simulation application to Linux Amazon EC2 instances. Migrate the visualization application to Windows EC2 instances. Configure Amazon FSx for NetApp ONTAP for storage.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Linux simulation app dùng NFS, Windows visualization app dùng SMB. Hai filesystem đang được sync thủ công gây dư thừa.
- **Existing Resources:** Two synchronized file systems (NFS + SMB).
- **Current Issue/Goal:** Loại bỏ data duplication, không code changes, hỗ trợ cả NFS và SMB.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `NFS` | Linux file sharing protocol. |
| `SMB` | Windows file sharing protocol. |
| `without making code changes` | Phải giữ nguyên protocol (NFS/SMB) như cũ. |
| `Amazon FSx for NetApp ONTAP` | Hỗ trợ đồng thời NFS và SMB trên cùng một filesystem. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Which solution meets requirements
- **Constraints:** No code changes, support both NFS and SMB, eliminate data duplication

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- FSx for NetApp ONTAP hỗ trợ cả NFS (Linux) và SMB (Windows) trên cùng một file system → giải quyết vấn đề đồng bộ và data duplication.
- Migration lên EC2 Linux cho simulation và EC2 Windows cho visualization giữ nguyên application code.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Lambda không chạy Windows desktop app và không support SMB.

**❌ Đáp án B:**
- FSx File Gateway là gateway kết nối với on-premises FSx, không phải storage solution đa giao thức trong cloud.

**❌ Đáp án C:**
- SQS là message queue, không thể thay thế NFS/SMB cho việc exchange intermediate data. Sẽ phải thay đổi code.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Need NFS + SMB on same storage → FSx for NetApp ONTAP. Không code changes → EC2 Linux + Windows."*
