# Question #287 - Topic 1

A company wants to migrate a Windows-based application from on premises to the AWS Cloud. The application has three tiers: an application tier, a business tier, and a database tier with Microsoft SQL Server. The company wants to use specific features of SQL Server such as native backups and Data Quality Services. The company also needs to share files for processing between the tiers. How should a solutions architect design the architecture to meet these requirements?

## Options

**A.** Host all three tiers on Amazon EC2 instances. Use Amazon FSx File Gateway for file sharing between the tiers.

**B.** Host all three tiers on Amazon EC2 instances. Use Amazon FSx for Windows File Server for file sharing between the tiers.

**C.** Host the application tier and the business tier on Amazon EC2 instances. Host the database tier on Amazon RDS. Use Amazon Elastic File System (Amazon EFS) for file sharing between the tiers.

**D.** Host the application tier and the business tier on Amazon EC2 instances. Host the database tier on Amazon RDS. Use a Provisioned IOPS SSD (io2) Amazon Elastic Block Store (Amazon EBS) volume for file sharing between the tiers.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Windows application 3-tier (app, business, SQL Server). Cần SQL Server features (native backups, Data Quality Services) và shared file storage.
- **Existing Resources:** On-premises Windows app.
- **Current Issue/Goal:** Migrate lên AWS, support SQL Server features, shared file system.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `SQL Server specific features` | Native backups, Data Quality Services → không dùng được RDS (RDS giới hạn SQL Server features). |
| `share files for processing` | Cần shared file system giữa các tiers. |
| `Amazon FSx for Windows File Server` | Managed Windows file server hỗ trợ SMB, tích hợp Active Directory. |
| `Windows-based application` | Cần Windows file sharing (SMB). |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Design architecture
- **Constraints:** SQL Server native features, file sharing between tiers

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- SQL Server features (native backups, Data Quality Services) yêu cầu full control của SQL Server → cần EC2 (không thể dùng RDS vì RDS giới hạn).
- FSx for Windows File Server cung cấp SMB file sharing giữa các Windows EC2 instances, tích hợp native Windows.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- FSx File Gateway là gateway kết nối với FSx on-premises, không phải là managed file server trong cloud như FSx for Windows File Server.

**❌ Đáp án C:**
- RDS không hỗ trợ SQL Server Data Quality Services và native backups.
- EFS là NFS (Linux), không phải SMB (Windows) → không compatible với Windows.

**❌ Đáp án D:**
- RDS tương tự C (không hỗ trợ SQL Server features).
- EBS io2 không thể share giữa nhiều EC2 instances cùng lúc.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"SQL Server native features → EC2 (not RDS). Windows file sharing → FSx for Windows (SMB). Cả 3 tiers trên EC2."*
