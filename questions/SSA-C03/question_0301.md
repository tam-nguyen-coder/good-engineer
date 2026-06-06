# Question #301 - Topic 1

A university research laboratory needs to migrate 30 TB of data from an on-premises Windows file server to Amazon FSx for Windows File Server. The laboratory has a 1 Gbps network link that many other departments in the university share. The laboratory wants to implement a data migration service that will maximize the performance of the data transfer. However, the laboratory needs to be able to control the amount of bandwidth that the service uses to minimize the impact on other departments. The data migration must take place within the next 5 days. Which AWS solution will meet these requirements?

## Options

**A.** AWS Snowcone

**B.** Amazon FSx File Gateway

**C.** AWS DataSync

**D.** AWS Transfer Family

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** 30 TB data migration từ on-premises Windows file server lên FSx for Windows File Server, 1 Gbps shared network, phải xong trong 5 ngày, cần kiểm soát bandwidth.
- **Existing Resources:** On-premises Windows file server, 1 Gbps shared link.
- **Current Issue/Goal:** Migrate 30 TB với bandwidth control, complete trong 5 ngày.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `30 TB` | Lượng data lớn, có thể transfer online với 1 Gbps trong 5 ngày (~6 TB/ngày ~ 556 Mbps, trong tầm với). |
| `control the amount of bandwidth` | DataSync hỗ trợ bandwidth throttling (--max-bandwidth). |
| `minimize the impact on other departments` | Cần giới hạn bandwidth usage. |
| `AWS DataSync` | Tool migration online, support bandwidth limit, support FSx for Windows File Server destination. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Which solution meets requirements
- **Constraints:** 30 TB in 5 days, bandwidth control, FSx for Windows destination

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- AWS DataSync hỗ trợ transfer data từ on-premises (NFS/SMB) lên AWS storage (FSx for Windows File Server).
- Có tính năng bandwidth throttling: giới hạn bandwidth usage để không ảnh hưởng đến network chia sẻ.
- 30 TB qua 1 Gbps trong 5 days là khả thi với DataSync (tối ưu hóa transfer performance).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Snowcone chỉ có 8 TB dung lượng (hoặc 14 TB với Snowcone SSD) → không đủ cho 30 TB.

**❌ Đáp án B:**
- FSx File Gateway là hybrid storage gateway, không phải data migration tool. Không hỗ trợ bandwidth control.

**❌ Đáp án D:**
- AWS Transfer Family hỗ trợ SFTP/FTP/FTPS transfer lên S3, không hỗ trợ FSx for Windows trực tiếp và không có bandwidth throttling.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"DataSync = online transfer + bandwidth throttling. Snowcone quá nhỏ cho 30 TB. FSx File Gateway = hybrid access, không phải migration."*
