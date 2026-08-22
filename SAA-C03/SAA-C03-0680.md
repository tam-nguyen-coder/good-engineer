# Question #680 - Topic 1

A solutions architect needs to copy files from an Amazon S3 bucket to an Amazon Elastic File System (Amazon EFS) file system and another S3 bucket. The files must be copied continuously. New files are added to the original S3 bucket consistently. The copied files should be overwritten only if the source file changes. Which solution will meet these requirements with the LEAST operational overhead?

## Options

**A.** Create an AWS DataSync location for both the destination S3 bucket and the EFS file system. Create a task for the destination S3 bucket and the EFS file system. Set the transfer mode to transfer only data that has changed.

**B.** Create an AWS Lambda function. Mount the file system to the function. Set up an S3 event notification to invoke the function when files are created and changed in Amazon S3. Configure the function to copy files to the file system and the destination S3 bucket.

**C.** Create an AWS DataSync location for both the destination S3 bucket and the EFS file system. Create a task for the destination S3 bucket and the EFS file system. Set the transfer mode to transfer all data.

**D.** Launch an Amazon EC2 instance in the same VPC as the file system. Mount the file system. Create a script to routinely synchronize all objects that changed in the origin S3 bucket to the destination S3 bucket and the mounted file system.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Continuous copy from S3 to EFS + another S3 bucket. Only overwrite if source changes.
- **Existing Resources:** Source S3 bucket, destination S3 bucket, EFS file system.
- **Current Issue/Goal:** Continuous sync with least overhead.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `continuously` | DataSync schedule hoặc event-driven. |
| `overwritten only if the source file changes` | DataSync "transfer only data that has changed" (incremental). |
| `AWS DataSync` | Managed service for data transfer between AWS storage services. |
| `least operational overhead` | DataSync (managed) vs custom Lambda or EC2 script. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Least operational overhead
- **Constraints:** Continuous, incremental copy, two destinations

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- DataSync là managed service chuyên dụng cho data transfer.
- Tạo DataSync location cho source S3, destination S3, destination EFS.
- Tạo 2 DataSync tasks (S3→S3 và S3→EFS) với scheduled execution để chạy liên tục.
- "Transfer only data that has changed" = incremental sync, chỉ copy files đã thay đổi.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Lambda function: cần code custom, mount EFS, handle errors → operational overhead cao.

**❌ Đáp án C:**
- "Transfer all data" mỗi lần chạy → không hiệu quả, copy lại file không thay đổi.

**❌ Đáp án D:**
- EC2 + custom script → operational overhead cao nhất (quản lý EC2, script, monitoring).

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"S3 to S3 + EFS sync → AWS DataSync incremental mode. Cheapest operational overhead."*
