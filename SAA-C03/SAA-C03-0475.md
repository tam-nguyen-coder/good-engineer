# Question #475 - Topic 1

A company is designing a containerized application that will use Amazon Elastic Container Service (Amazon ECS). The application needs to access a shared file system that is highly durable and can recover data to another AWS Region with a recovery point objective (RPO) of 8 hours. The file system needs to provide a mount target in each Availability Zone within a Region. A solutions architect wants to use AWS Backup to manage the replication to another Region. Which solution will meet these requirements?

## Options

**A.** Amazon FSx for Windows File Server with a Multi-AZ deployment

**B.** Amazon FSx for NetApp ONTAP with a Multi-AZ deployment

**C.** Amazon Elastic File System (Amazon EFS) with the Standard storage class

**D.** Amazon FSx for OpenZFS

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Containerized app on ECS, cần shared file system, durable, cross-region recovery (RPO 8h) via AWS Backup, mount target mỗi AZ.
- **Existing Resources:** ECS containers.
- **Current Issue/Goal:** Shared file system đáp ứng các yêu cầu.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `shared file system` | EFS hoặc FSx. |
| `mount target in each Availability Zone` | EFS có mount target trong mỗi AZ. |
| `AWS Backup to manage the replication to another Region` | EFS hỗ trợ AWS Backup cross-region replication. |
| `highly durable` | EFS Standard: 11x9s durability, Multi-AZ. |
| `containerized application on ECS` | EFS là native shared file system cho ECS (EFS volume driver). |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Shared file system for ECS
- **Constraints:** Durable, mount target per AZ, AWS Backup cross-region, RPO 8h

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- EFS Standard: shared file system, mount target trong mỗi AZ.
- EFS hỗ trợ AWS Backup để cross-region replication.
- EFS là giải pháp tự nhiên cho ECS (EFS có ECS volume integration).
- Highly durable (11x9s) với Standard storage class (Multi-AZ).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A (FSx for Windows):**
- FSx for Windows: dùng cho Windows-based workloads, SMB protocol. Containerized app trên ECS thường dùng Linux.
- AWS Backup có hỗ trợ FSx, nhưng EFS đơn giản hơn cho use case này.

**❌ Đáp án B (FSx for NetApp ONTAP):**
- FSx for ONTAP: feature-rich, nhưng overkill và cost cao hơn EFS.
- Không phải lựa chọn đơn giản nhất.

**❌ Đáp án D (FSx for OpenZFS):**
- FSx for OpenZFS: single-AZ mặc định, không có mount target per AZ như EFS.
- Không có AWS Backup integration sẵn như EFS.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"ECS + shared file system + mount target mỗi AZ + AWS Backup → EFS Standard. FSx = use case đặc thù (Windows, ONTAP)."*
