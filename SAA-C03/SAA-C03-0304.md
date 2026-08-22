# Question #304 - Topic 1

A company recently created a disaster recovery site in a different AWS Region. The company needs to transfer large amounts of data back and forth between NFS file systems in the two Regions on a periodic basis. Which solution will meet these requirements with the LEAST operational overhead?

## Options

**A.** Use AWS DataSync.

**B.** Use AWS Snowball devices.

**C.** Set up an SFTP server on Amazon EC2.

**D.** Use AWS Database Migration Service (AWS DMS).

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** DR site ở Region khác, cần transfer data định kỳ giữa 2 NFS file systems cross-Region.
- **Existing Resources:** NFS file systems ở 2 Regions.
- **Current Issue/Goal:** Periodic data transfer between NFS systems, least operational overhead.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `large amounts of data` | DataSync hỗ trợ transfer lớn, tối ưu network. |
| `back and forth` | Two-way transfer. |
| `periodic basis` | Cần lên lịch tự động. |
| `NFS file systems` | Source và destination đều là NFS. |
| `AWS DataSync` | Transfer data automatically giữa NFS và AWS storage, support scheduling. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Least operational overhead
- **Constraints:** Cross-Region, periodic, NFS-to-NFS

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- AWS DataSync hỗ trợ transfer data giữa NFS file systems (on-premises hoặc AWS) với scheduling, bandwidth control, và incremental sync.
- Cross-Region transfer: DataSync tự động xử lý encryption và data validation.
- Operational overhead thấp nhất: chỉ cần tạo task và schedule.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Snowball devices là offline physical transfer, không phù hợp cho periodic "back and forth" data transfer.

**❌ Đáp án C:**
- SFTP server trên EC2 cần tự quản lý, cấu hình, bảo trì → operational overhead cao hơn nhiều.

**❌ Đáp án D:**
- DMS dùng cho database migration (SQL, NoSQL), không hỗ trợ NFS file transfer.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Periodic NFS cross-Region transfer → DataSync (scheduled, automated). Snowball = one-time. DMS = database."*
