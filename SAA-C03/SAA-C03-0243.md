# Question #243 - Topic 1

A medical research lab produces data that is related to a new study. The lab wants to make the data available with minimum latency to clinics across the country for their on-premises, file-based applications. The data files are stored in an Amazon S3 bucket that has read-only permissions for each clinic. What should a solutions architect recommend to meet these requirements?

## Options

**A.** Deploy an AWS Storage Gateway file gateway as a virtual machine (VM) on premises at each clinic.

**B.** Migrate the files to each clinic's on-premises applications by using AWS DataSync for processing.

**C.** Deploy an AWS Storage Gateway volume gateway as a virtual machine (VM) on premises at each clinic.

**D.** Attach an Amazon Elastic File System (Amazon EFS) file system to each clinic's on-premises servers.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Medical data in S3, clinics need low-latency access via on-premises file-based apps. Read-only.
- **Existing Resources:** S3 bucket with data.
- **Current Issue/Goal:** Local caching for low-latency file access.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `minimum latency` | Local cache — **File Gateway** |
| `on-premises, file-based applications` | **File Gateway** (NFS/SMB) |
| `read-only permissions` | File gateway cache + S3 permissions |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Storage / Hybrid
- **Constraints:** Low latency, file-based, on-premises

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- **File Gateway** — cung cấp NFS/SMB mount point on-premises, cache dữ liệu locally → low latency.
- Data được lưu trong S3 → read-only access cho clinics.
- VM chạy on-premises at each clinic.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- DataSync — one-time migration, không low-latency access.

**❌ Đáp án C:**
- Volume gateway — block storage (iSCSI), không file-based.

**❌ Đáp án D:**
- EFS — không attach trực tiếp vào on-premises servers.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"File Gateway = SMB/NFS cache on-prem. Volume Gateway = block storage. DataSync = one-time transfer"*
