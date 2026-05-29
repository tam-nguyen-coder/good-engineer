# Question #54 - Topic 1

A company runs multiple Windows workloads on AWS. The company's employees use Windows file shares that are hosted on two Amazon EC2 instances. The file shares synchronize data between themselves and maintain duplicate copies. The company wants a highly available and durable storage solution that preserves how users currently access the files. What should a solutions architect do to meet these requirements?

## Options

**A.** Migrate all the data to Amazon S3. Set up IAM authentication for users to access files.

**B.** Set up an Amazon S3 File Gateway. Mount the S3 File Gateway on the existing EC2 instances.

**C.** Extend the file share environment to Amazon FSx for Windows File Server with a Multi-AZ configuration. Migrate all the data to FSx for Windows File Server.

**D.** Extend the file share environment to Amazon Elastic File System (Amazon EFS) with a Multi-AZ configuration. Migrate all the data to Amazon EFS.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Windows workloads, Windows file shares trên 2 EC2 instances, đang sync duplicate copies.
- **Existing Resources:** 2 EC2 instances với Windows file shares.
- **Current Issue/Goal:** HA + durable storage, **preserve current access method** (Windows file share/SMB).

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `Windows workloads` | Cần Windows-native solution |
| `Windows file shares` | SMB protocol |
| `preserves how users currently access the files` | Phải giữ nguyên cách truy cập (file share qua SMB) |
| `highly available and durable` | Multi-AZ managed service |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Highly available + Durable + Minimal change
- **Constraints:** Windows, file shares (SMB), giữ nguyên cách truy cập

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- **Amazon FSx for Windows File Server** là managed Windows file server, hỗ trợ SMB protocol — giữ nguyên cách users truy cập.
- **Multi-AZ configuration** tự động replicate dữ liệu sang AZ khác, cung cấp HA và durability.
- Loại bỏ nhu cầu tự sync dữ liệu giữa 2 EC2 instances — FSx quản lý hoàn toàn.
- Tích hợp native với Active Directory, Windows ACLs.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- S3 là object storage, sử dụng S3 API hoặc IAM auth — **không giữ nguyên cách truy cập** Windows file share (SMB).
- Users không thể map S3 bucket như network drive.

**❌ Đáp án B:**
- **S3 File Gateway** cung cấp file interface (SMB/NFS) nhưng backend là S3.
- Vẫn cần 2 EC2 instances, không loại bỏ sync complexity.
- Không native HA như FSx Multi-AZ.
- Thêm độ phức tạp (gateway) so với FSx managed.

**❌ Đáp án D:**
- **EFS** là NFS file system — Linux/Unix, **không hỗ trợ Windows** (Windows dùng SMB, không phải NFS).
- EFS không tích hợp Active Directory, không hỗ trợ Windows ACLs.
- Không thể dùng cho Windows file shares.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"FSx for Windows = SMB + AD + Windows. EFS = NFS + Linux. File Gateway = S3 with file interface"*
