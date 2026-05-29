# Question #483 - Topic 1

A company containerized a Windows job that runs on .NET 6 Framework under a Windows container. The company wants to run this job in the AWS Cloud. The job runs every 10 minutes. The job's runtime varies between 1 minute and 3 minutes. Which solution will meet these requirements MOST cost-effectively?

## Options

**A.** Create an AWS Lambda function based on the container image of the job. Configure Amazon EventBridge to invoke the function every 10 minutes.

**B.** Use AWS Batch to create a job that uses AWS Fargate resources. Configure the job scheduling to run every 10 minutes.

**C.** Use Amazon Elastic Container Service (Amazon ECS) on AWS Fargate to run the job. Create a scheduled task based on the container image of the job to run every 10 minutes.

**D.** Use Amazon Elastic Container Service (Amazon ECS) on AWS Fargate to run the job. Create a standalone task based on the container image of the job. Use Windows task scheduler to run the job every 10 minutes.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Windows container job (.NET 6), chạy mỗi 10 phút, runtime 1-3 phút. Cần chạy trên AWS cost-effectively.
- **Existing Resources:** Windows container image.
- **Current Issue/Goal:** Chạy scheduled job trên Windows container với chi phí thấp nhất.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `Windows container` | Lambda không support Windows container. AWS Batch và ECS Fargate support Windows containers. |
| `runs every 10 minutes` | Cần scheduled execution. ECS có native Scheduled Tasks (EventBridge). |
| `runtime varies between 1 minute and 3 minutes` | Job ngắn → Fargate pay-per-second phù hợp. |
| `most cost-effectively` | Fargate (không cần quản lý EC2) + scheduled task (native). |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most cost-effective
- **Constraints:** Windows container, scheduled mỗi 10 phút.

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- ECS on Fargate support Windows containers.
- **Scheduled task** (ECS native) tích hợp với EventBridge → chạy đúng lịch mỗi 10 phút.
- Fargate pay-per-second: job 1-3 phút → chi phí thấp.
- Không cần quản lý EC2 instances → giảm operational cost.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- **AWS Lambda:** Lambda không support Windows containers. Lambda runtime environment là Amazon Linux. Container images cho Lambda phải đáp ứng Lambda runtime API, không chạy Windows.

**❌ Đáp án B:**
- **AWS Batch on Fargate:** Có thể chạy Windows container nhưng AWS Batch có nhiều component (job queue, job definition, compute environment) → phức tạp hơn ECS scheduled task cho use case đơn giản này.

**❌ Đáp án D:**
- **Windows task scheduler + standalone task:** Sử dụng Windows task scheduler on-premises không tối ưu cho cloud. ECS Scheduled Task là giải pháp native, không cần phụ thuộc vào Windows OS scheduler.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Windows container → không dùng Lambda. ECS Fargate + Scheduled Task = đơn giản, rẻ cho job ngắn."*
