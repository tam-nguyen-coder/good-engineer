# Question #500 - Topic 1

A company has multiple Windows file servers on premises. The company wants to migrate and consolidate its files into an Amazon FSx for Windows File Server file system. File permissions must be preserved to ensure that access rights do not change. Which solutions will meet these requirements? (Choose two.)

## Options

**A.** Deploy AWS DataSync agents on premises. Schedule DataSync tasks to transfer the data to the FSx for Windows File Server file system.

**B.** Copy the shares on each file server into Amazon S3 buckets by using the AWS CLI. Schedule AWS DataSync tasks to transfer the data to the FSx for Windows File Server file system.

**C.** Remove the drives from each file server. Ship the drives to AWS for import into Amazon S3. Schedule AWS DataSync tasks to transfer the data to the FSx for Windows File Server file system.

**D.** Order an AWS Snowcone device. Connect the device to the on-premises network. Launch AWS DataSync agents on the device. Schedule DataSync tasks to transfer the data to the FSx for Windows File Server file system.

**E.** Order an AWS Snowball Edge Storage Optimized device. Connect the device to the on-premises network. Copy data to the device by using the AWS CLI. Ship the device back to AWS for import into Amazon S3. Schedule AWS DataSync tasks to transfer the data to the FSx for Windows File Server file system.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Migrate và consolidate Windows file servers on-prem → FSx for Windows File Server. Cần preserve file permissions (NTFS permissions).
- **Existing Resources:** Multiple Windows file servers on-premises.
- **Current Issue/Goal:** Migration với permission preservation.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `File permissions must be preserved` | DataSync preserves NTFS permissions khi transfer tới FSx for Windows. |
| `FSx for Windows File Server` | Managed Windows file server, SMB protocol. |
| `DataSync` | AWS DataSync: preserves metadata, permissions, supports SMB. |
| `choose two` | 2 đáp án đúng. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Migration (choose 2)
- **Constraints:** Preserve file permissions, migrate Windows file servers.

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A và D**

**Giải thích:**
- **A. DataSync agents on-premises:** DataSync có thể đọc từ Windows file servers (SMB), transfer data trực tiếp tới FSx for Windows, và **preserve NTFS permissions** (DACLs, SACLs, owner, timestamps).
- **D. Snowcone + DataSync:** Snowcone là thiết bị nhẹ, có thể chạy DataSync agent onboard. Kết nối vào network on-prem, chạy DataSync tasks để transfer data tới FSx for Windows. Cũng preserve permissions.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Copy vào S3 trước (qua CLI): S3 không preserve Windows NTFS permissions (S3 dùng object-level permissions khác). DataSync từ S3 → FSx sẽ mất permissions.

**❌ Đáp án C:**
- Ship drives: Vận chuyển vật lý, không có DataSync agent để preserve permissions. Import vào S3 trước cũng làm mất permissions.

**❌ Đáp án E:**
- Snowball Edge: Copy bằng CLI lên device, ship về AWS import vào S3 → mất permissions. DataSync từ S3 → FSx không restore được NTFS permissions.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Preserve NTFS permissions → DataSync trực tiếp từ Windows → FSx (hoặc Snowcone + DataSync). S3 không giữ Windows permissions."*
