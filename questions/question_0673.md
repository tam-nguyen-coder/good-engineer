# Question #673 - Topic 1

A company runs an SMB file server in its data center. The file server stores large files that the company frequently accesses for up to 7 days after the file creation date. After 7 days, the company needs to be able to access the files with a maximum retrieval time of 24 hours. Which solution will meet these requirements?

## Options

**A.** Use AWS DataSync to copy data that is older than 7 days from the SMB file server to AWS.

**B.** Create an Amazon S3 File Gateway to increase the company's storage space. Create an S3 Lifecycle policy to transition the data to S3 Glacier Deep Archive after 7 days.

**C.** Create an Amazon FSx File Gateway to increase the company's storage space. Create an Amazon S3 Lifecycle policy to transition the data after 7 days.

**D.** Configure access to Amazon S3 for each user. Create an S3 Lifecycle policy to transition the data to S3 Glacier Flexible Retrieval after 7 days.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** On-prem SMB file server, large files frequently accessed for 7 days, then rarely accessed but need retrieval within 24 hours.
- **Existing Resources:** On-prem SMB file server.
- **Current Issue/Goal:** Extend storage, lifecycle management.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `SMB file server` | Cần SMB protocol support. |
| `frequently accessed for up to 7 days` | Data hot trong 7 ngày → local cache/standard storage. |
| `maximum retrieval time of 24 hours` | Glacier Deep Archive (12h) hoặc Glacier Flexible Retrieval (1-12h) đều đáp ứng. |
| `S3 File Gateway` | File gateway hỗ trợ SMB, lưu data trong S3, cache local cho frequent access. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Meet requirements
- **Constraints:** SMB protocol, frequent first 7 days, 24h retrieval after

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- S3 File Gateway hỗ trợ SMB protocol, cung cấp file share với S3 backend.
- Data mới (0-7 days) được cache locally trên gateway → fast access.
- S3 Lifecycle policy transition data sang Glacier Deep Archive sau 7 days → tiết kiệm chi phí.
- Glacier Deep Archive retrieval time ~12 hours, dưới 24h yêu cầu.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- DataSync copy data >7 days → mất access đến local data. Không giải quyết vấn đề hot data 7 ngày đầu.

**❌ Đáp án C:**
- FSx File Gateway (Amazon FSx for Windows File Server) là managed file server, không gateway. Từ "gateway" trong option gây nhầm.
- Dùng FSx for Windows File Server + lifecycle policy đến S3 Glacier có thể hoạt động nhưng đắt hơn S3 File Gateway.

**❌ Đáp án D:**
- Configure access to S3 cho mỗi user → operational overhead rất cao, không practical.
- Glacier Flexible Retrieval (phút đến giờ) đắt hơn Deep Archive.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"SMB file server extension → S3 File Gateway + Lifecycle to Glacier Deep Archive after 7 days."*
