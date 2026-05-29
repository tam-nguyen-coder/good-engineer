# Question #546 - Topic 1

A recent analysis of a company's IT expenses highlights the need to reduce backup costs. The company's chief information officer wants to simplify the on-premises backup infrastructure and reduce costs by eliminating the use of physical backup tapes. The company must preserve the existing investment in the on-premises backup applications and workflows. What should a solutions architect recommend?

## Options

**A.** Set up AWS Storage Gateway to connect with the backup applications using the NFS interface.

**B.** Set up an Amazon EFS file system that connects with the backup applications using the NFS interface.

**C.** Set up an Amazon EFS file system that connects with the backup applications using the iSCSI interface.

**D.** Set up AWS Storage Gateway to connect with the backup applications using the iSCSI-virtual tape library (VTL) interface.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Công ty muốn giảm chi phí backup, loại bỏ băng từ vật lý (physical tapes). Phải giữ nguyên các ứng dụng và workflow backup hiện tại.
- **Existing Resources:** On-premises backup applications, physical tape infrastructure.
- **Current Issue/Goal:** Thay thế physical tapes bằng giải pháp cloud, tương thích với backup apps hiện tại.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `physical backup tapes` | Hiện tại đang dùng băng từ → cần VTL (Virtual Tape Library) |
| `preserve the existing investment` | Giữ nguyên ứng dụng và workflow backup hiện tại |
| `on-premises backup applications` | Cần giao thức tương thích với backup software |
| `Storage Gateway` | Dịch vụ kết nối on-prem với AWS storage |
| `iSCSI` | Giao thức thường dùng cho tape library |
| `VTL` | Virtual Tape Library – thay thế băng từ vật lý |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most appropriate solution
- **Constraints:** Giữ nguyên backup apps/workflows hiện tại, giảm chi phí

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- AWS Storage Gateway cung cấp Virtual Tape Library (VTL) interface qua iSCSI. Đây là giải pháp thay thế trực tiếp cho physical tape library.
- Các ứng dụng backup hiện tại (như Veeam, NetBackup, v.v.) vốn dùng iSCSI để giao tiếp với tape libraries → không cần thay đổi gì.
- Dữ liệu được lưu trữ trong S3 Glacier one zone hoặc S3 Glacier Flexible Retrieval, giảm chi phí đáng kể.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A (Storage Gateway NFS):** File Gateway (NFS) dùng cho file storage, không phù hợp với tape backup workflows. Backup apps thường dùng tape protocols.

**❌ Đáp án B (EFS NFS):** EFS là file system, không hỗ trợ tape backup workflows. Cũng không có iSCSI support.

**❌ Đáp án C (EFS iSCSI):** EFS không hỗ trợ giao thức iSCSI. EFS chỉ hỗ trợ NFS.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Physical tapes → Storage Gateway VTL (iSCSI). File backup → File Gateway (NFS). EFS = NFS only, no iSCSI."*
