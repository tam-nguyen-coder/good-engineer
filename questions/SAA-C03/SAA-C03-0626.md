# Question #626 - Topic 1

A company stores its data on premises. The amount of data is growing beyond the company's available capacity. The company wants to migrate its data from the on-premises location to an Amazon S3 bucket. The company needs a solution that will automatically validate the integrity of the data after the transfer. Which solution will meet these requirements?

## Options

**A.** Order an AWS Snowball Edge device. Configure the Snowball Edge device to perform the online data transfer to an S3 bucket.

**B.** Deploy an AWS DataSync agent on premises. Configure the DataSync agent to perform the online data transfer to an S3 bucket.

**C.** Create an Amazon S3 File Gateway on premises. Configure the S3 File Gateway to perform the online data transfer to an S3 bucket.

**D.** Configure an accelerator in Amazon S3 Transfer Acceleration on premises. Configure the accelerator to perform the online data transfer to an S3 bucket.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** On-prem data đang tăng vượt capacity, cần migrate lên S3. Yêu cầu tự động validate integrity sau transfer.
- **Existing Resources:** On-premises data.
- **Current Issue/Goal:** Online migration to S3 với automatic data integrity validation.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `migrate its data` | Online transfer to S3. |
| `automatically validate the integrity` | DataSync tự động verify checksums sau transfer. |
| `DataSync` | Online migration service, built-in data validation. |
| `Snowball` | Offline transfer, không phải "online data transfer". |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Meet requirements
- **Constraints:** Online migration, automatic integrity validation

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- AWS DataSync: dịch vụ online migration chuyên dụng, có agent chạy on-prem.
- Tự động validate data integrity bằng checksums sau mỗi transfer.
- Hỗ trợ NFS, SMB, self-managed object storage → copy đến S3.
- Có thể schedule incremental transfers.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Snowball Edge: offline physical device, không phải "online data transfer". Cần ship device đến AWS.

**❌ Đáp án C:**
- S3 File Gateway: cung cấp NFS/SMB interface đến S3, phù hợp cho hybrid access, không phải one-time migration tool. Không có built-in data validation như DataSync.

**❌ Đáp án D:**
- S3 Transfer Acceleration: tăng tốc upload qua internet dùng CloudFront edge locations. Không phải migration tool, không có data validation.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Online migration + integrity validation → DataSync (checksums). Snowball = offline, S3TA = speed only."*
