# Question #102 - Topic 1

A company wants to migrate an on-premises data center to AWS. The data center hosts an SFTP server that stores its data on an NFS-based file system. The server holds 200 GB of data that needs to be transferred. The server must be hosted on an Amazon EC2 instance that uses an Amazon Elastic File System (Amazon EFS) file system. Which combination of steps should a solutions architect take to automate this task? (Choose two.)

## Options

**A.** Launch the EC2 instance into the same Availability Zone as the EFS file system.

**B.** Install an AWS DataSync agent in the on-premises data center.

**C.** Create a secondary Amazon Elastic Block Store (Amazon EBS) volume on the EC2 instance for the data.

**D.** Manually use an operating system copy command to push the data to the EC2 instance.

**E.** Use AWS DataSync to create a suitable location configuration for the on-premises SFTP server.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Migrate 200GB SFTP data (NFS) to EC2 + EFS. Tự động hóa.
- **Existing Resources:** On-prem SFTP server, NFS storage.
- **Current Issue/Goal:** EC2 + EFS, automated transfer.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `automate this task` | Cần **AWS DataSync** |
| `NFS-based file system` | DataSync hỗ trợ NFS |
| `200 GB of data` | DataSync lý tưởng cho lượng data vừa |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Data transfer + Automation
- **Constraints:** Chọn 2 đáp án

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B và E**

**Giải thích:**
- **B: DataSync agent on-prem** — cài agent trong data center để đọc data từ NFS.
- **E: DataSync location config** — tạo source location (on-prem NFS) và destination (EFS).
- DataSync tự động transfer, schedule, verify data.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- EC2 cần ở cùng AZ với EFS để mount — đúng kỹ thuật nhưng một mình nó không đủ để transfer.

**❌ Đáp án C:**
- EBS volume — không cần, EFS là shared storage.

**❌ Đáp án D:**
- Manual copy — không tự động hóa.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"DataSync = automated data transfer on-prem ↔ AWS. Agent on-prem + location config = complete setup"*
