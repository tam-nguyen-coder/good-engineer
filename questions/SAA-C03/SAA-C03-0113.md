# Question #113 - Topic 1

A company uses 50 TB of data for reporting. The company wants to move this data from on premises to AWS. A custom application in the company’s data center runs a weekly data transformation job. The company plans to pause the application until the data transfer is complete and needs to begin the transfer process as soon as possible. The data center does not have any available network bandwidth for additional workloads. A solutions architect must transfer the data and must configure the transformation job to continue to run in the AWS Cloud. Which solution will meet these requirements with the LEAST operational overhead?

## Options

**A.** Use AWS DataSync to move the data. Create a custom transformation job by using AWS Glue.

**B.** Order an AWS Snowcone device to move the data. Deploy the transformation application to the device.

**C.** Order an AWS Snowball Edge Storage Optimized device. Copy the data to the device. Create a custom transformation job by using AWS Glue.

**D.** Order an AWS Snowball Edge Storage Optimized device that includes Amazon EC2 compute. Copy the data to the device. Create a new EC2 instance on AWS to run the transformation application.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** 50TB data transfer from on-prem to AWS. No bandwidth available. Need to transfer + continue transformation in cloud.
- **Existing Resources:** On-prem data, custom transformation app.
- **Current Issue/Goal:** Transfer 50TB without network, continue transformation in AWS.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `50 TB of data` | Lớn, không thể dùng Snowcone (8TB) |
| `no available network bandwidth` | Không thể dùng DataSync — cần **Snowball Edge** |
| `continue to run in the AWS Cloud` | Cần compute để transform |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Data transfer
- **Constraints:** 50TB, no bandwidth, offline transfer

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- **Snowball Edge Storage Optimized with EC2 compute** — 80TB capacity + compute capabilities.
- Copy data lên Snowball tại on-prem.
- Gửi Snowball về AWS, data được import vào S3.
- Tạo EC2 instance trên AWS để chạy transformation job.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- DataSync cần network bandwidth — không available.

**❌ Đáp án B:**
- **Snowcone** chỉ 8TB — không đủ cho 50TB.

**❌ Đáp án C:**
- Snowball Edge Storage Optimized (without compute) — đủ dung lượng nhưng không thể chạy transformation trên device.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Snowball Edge = 80TB offline transfer. Snowcone = 8TB. DataSync = online (needs bandwidth)"*
