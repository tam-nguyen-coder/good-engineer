# Question #414 - Topic 1

A company has a business system that generates hundreds of reports each day. The business system saves the reports to a network share in CSV format. The company needs to store this data in the AWS Cloud in near-real time for analysis. Which solution will meet these requirements with the LEAST administrative overhead?

## Options

**A.** Use AWS DataSync to transfer the files to Amazon S3. Create a scheduled task that runs at the end of each day.

**B.** Create an Amazon S3 File Gateway. Update the business system to use a new network share from the S3 File Gateway.

**C.** Use AWS DataSync to transfer the files to Amazon S3. Create an application that uses the DataSync API in the automation workflow.

**D.** Deploy an AWS Transfer for SFTP endpoint. Create a script that checks for new files on the network share and uploads the new files by using SFTP.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Business system writes CSV reports to network share. Need near-real time storage in AWS for analysis.
- **Existing Resources:** On-prem business system, network share.
- **Current Issue/Goal:** Near-real time S3 upload. Least admin overhead.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `near-real time` | Sync liên tục, không batch cuối ngày. |
| `least administrative overhead` | Minimal config, managed service. |
| `S3 File Gateway` | Mount S3 as network share (NFS/SMB) → tự động upload. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Least admin overhead / Storage
- **Constraints:** Near-real time, CSV on network share

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- S3 File Gateway: cung cấp SMB/NFS share → business system chỉ cần thay đổi network share path.
- File được upload lên S3 gần như real-time.
- Admin overhead thấp: không cần script, không cần scheduled task.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- DataSync scheduled end of day: batch, không near-real time.

**❌ Đáp án C:**
- DataSync API + custom app: cần phát triển và maintain application → overhead cao.

**❌ Đáp án D:**
- SFTP endpoint + script: cần viết script check + upload → overhead cao hơn File Gateway.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Near-real time file to S3 → S3 File Gateway (mount as network share)."*

