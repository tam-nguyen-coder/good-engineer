# Question #409 - Topic 1

A solutions architect must migrate a Windows Internet Information Services (IIS) web application to AWS. The application currently relies on a file share hosted in the user's on-premises network-attached storage (NAS). The solutions architect has proposed migrating the IIS web servers to Amazon EC2 instances in multiple Availability Zones that are connected to the storage solution, and configuring an Elastic Load Balancer attached to the instances. Which replacement to the on-premises file share is MOST resilient and durable?

## Options

**A.** Migrate the file share to Amazon RDS.

**B.** Migrate the file share to AWS Storage Gateway.

**C.** Migrate the file share to Amazon FSx for Windows File Server.

**D.** Migrate the file share to Amazon Elastic File System (Amazon EFS).

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Windows IIS app on EC2 multi-AZ + ALB. Need to replace on-prem NAS file share.
- **Existing Resources:** Windows IIS web app, on-prem NAS (SMB file share).
- **Current Issue/Goal:** Migrate file share to AWS. MOST resilient and durable.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `Windows IIS` | Windows-based → cần SMB protocol. |
| `file share` | Shared storage, không phải database. |
| `most resilient and durable` | Fully managed, multi-AZ capable. |
| `FSx for Windows File Server` | Managed Windows file server, SMB, multi-AZ. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Storage - Most resilient and durable
- **Constraints:** Windows, file share, multi-AZ EC2

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- Amazon FSx for Windows File Server: fully managed Windows file server, native SMB support.
- Multi-AZ deployment: tự động failover, dữ liệu replicated giữa AZs → resilient + durable.
- Tích hợp với Windows/AD, supports Windows ACLs.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Amazon RDS: relational database, không phải file share. Không support SMB.

**❌ Đáp án B:**
- Storage Gateway file gateway: cung cấp SMB/NFS share nhưng không resilient bằng FSx (single appliance, cần on-prem hoặc EC2 để chạy).

**❌ Đáp án D:**
- Amazon EFS: NFS-based, Linux only. Windows không support NFS natively (cần cấu hình thêm).

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Windows file share = FSx for Windows (SMB, multi-AZ). EFS = Linux (NFS). RDS ≠ file share."*

