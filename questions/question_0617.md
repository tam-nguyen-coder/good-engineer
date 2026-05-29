# Question #617 - Topic 1

A company wants to migrate an on-premises data center to AWS. The data center hosts a storage server that stores data in an NFS-based file system. The storage server holds 200 GB of data. The company needs to migrate the data without interruption to existing services. Multiple resources in AWS must be able to access the data by using the NFS protocol. Which combination of steps will meet these requirements MOST cost-effectively? (Choose two.)

## Options

**A.** Create an Amazon FSx for Lustre file system.

**B.** Create an Amazon Elastic File System (Amazon EFS) file system.

**C.** Create an Amazon S3 bucket to receive the data.

**D.** Manually use an operating system copy command to push the data into the AWS destination.

**E.** Install an AWS DataSync agent in the on-premises data center. Use a DataSync task between the on-premises location and AWS.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Migrate on-premises NFS storage server (200 GB) to AWS, không interruption, cần NFS protocol access từ multiple AWS resources.
- **Existing Resources:** On-premises NFS storage server, 200 GB data.
- **Current Issue/Goal:** Migration không downtime + NFS access trên AWS.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `NFS-based file system` | Cần storage hỗ trợ NFS protocol. |
| `without interruption` | Cần online migration → DataSync hỗ trợ continuous replication. |
| `multiple resources in AWS` | Cần shared file system → EFS. |
| `200 GB` | Dung lượng nhỏ, EFS phù hợp. |
| `DataSync` | Online migration tool, tự động copy, validate, support NFS. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most cost-effective (Choose 2)
- **Constraints:** No interruption, 200 GB, NFS protocol

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B và E**

**Giải thích:**
- **B - Amazon EFS:** File system hỗ trợ NFSv4, có thể mount từ nhiều EC2 instances đồng thời, scalable, cost-effective cho 200 GB.
- **E - AWS DataSync:** Online migration, có agent chạy on-prem, copy data qua AWS mà không interruption, tự động validate integrity.
- Kết hợp: DataSync migrate data từ NFS server → EFS, sau đó các AWS resources mount EFS qua NFS.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- FSx for Lustre chuyên cho HPC, không phải general-purpose NFS, cost cao hơn EFS.

**❌ Đáp án C:**
- Amazon S3 không hỗ trợ NFS protocol trực tiếp (cần S3 File Gateway).

**❌ Đáp án D:**
- OS copy command (cp, rsync) không hỗ trợ continuous replication, có thể gián đoạn service.
- Không có validation built-in.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"NFS + multiple EC2 → EFS. Migration không downtime → DataSync. (Not S3, not rsync)"*
