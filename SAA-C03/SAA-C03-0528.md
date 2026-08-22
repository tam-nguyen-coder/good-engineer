# Question #528 - Topic 1

A data analytics company wants to migrate its batch processing system to AWS. The company receives thousands of small data files periodically during the day through FTP. An on-premises batch job processes the data files overnight. However, the batch job takes hours to finish running. The company wants the AWS solution to process incoming data files as soon as possible with minimal changes to the FTP clients that send the files. The solution must delete the incoming data files after the files have been processed successfully. Processing for each file needs to take 3-8 minutes. Which solution will meet these requirements in the MOST operationally efficient way?

## Options

**A.** Use an Amazon EC2 instance that runs an FTP server to store incoming files as objects in Amazon S3 Glacier Flexible Retrieval. Configure a job queue in AWS Batch. Use Amazon EventBridge rules to invoke the job to process the objects nightly from S3 Glacier Flexible Retrieval. Delete the objects after the job has processed the objects.

**B.** Use an Amazon EC2 instance that runs an FTP server to store incoming files on an Amazon Elastic Block Store (Amazon EBS) volume. Configure a job queue in AWS Batch. Use Amazon EventBridge rules to invoke the job to process the files nightly from the EBS volume. Delete the files after the job has processed the files.

**C.** Use AWS Transfer Family to create an FTP server to store incoming files on an Amazon Elastic Block Store (Amazon EBS) volume. Configure a job queue in AWS Batch. Use an Amazon S3 event notification when each file arrives to invoke the job in AWS Batch. Delete the files after the job has processed the files.

**D.** Use AWS Transfer Family to create an FTP server to store incoming files in Amazon S3 Standard. Create an AWS Lambda function to process the files and to delete the files after they are processed. Use an S3 event notification to invoke the Lambda function when the files arrive.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Migrate batch processing system lên AWS. Nhận files qua FTP, cần process ngay khi file đến (không chờ overnight), xóa file sau khi process.
- **Existing Resources:** FTP clients gửi files.
- **Current Issue/Goal:** Minimal changes to FTP clients, process as soon as possible, delete after processing, 3-8 phút/file.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `FTP` | AWS Transfer Family → managed FTP server, không cần thay đổi client |
| `process as soon as possible` | Event-driven, real-time processing |
| `3-8 minutes per file` | Lambda max timeout 15 phút → phù hợp |
| `delete after processed` | Lambda tự động xóa object sau khi xử lý |
| `most operationally efficient` | Serverless (Transfer Family + S3 + Lambda) |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most operationally efficient
- **Constraints:** Minimal changes to FTP clients, process ASAP, delete after processing

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- AWS Transfer Family cung cấp managed FTP server, không cần thay đổi FTP clients.
- Files được lưu trực tiếp vào S3 Standard.
- S3 event notification → trigger Lambda function ngay khi file upload.
- Lambda xử lý file (3-8 phút, trong Lambda limit 15 phút), sau đó xóa file khỏi S3.
- Hoàn toàn serverless, không cần quản lý EC2, operational overhead thấp nhất.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- S3 Glacier Flexible Retrieval: không phù hợp vì cần process ASAP (Glacier có retrieval time từ phút đến giờ).
- Batch job chỉ chạy nightly, không real-time.

**❌ Đáp án B:**
- Dùng EC2 FTP server (không phải Transfer Family) → cần quản lý EC2 instance.
- EBS volume → không scale tốt, không serverless.
- Batch nightly, không real-time.

**❌ Đáp án C:**
- Transfer Family + EBS là sai: Transfer Family lưu file vào S3, không phải EBS.
- Batch job vẫn cần compute environment (EC2) → operational overhead cao hơn Lambda.

## 6. MẸO GHI NHỚ (MEMORY HOOK)
🧠 *"Transfer Family + S3 + Lambda = managed FTP serverless processing. Không cần EC2, process real-time."*
