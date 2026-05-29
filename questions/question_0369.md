# Question #369 - Topic 1

A company has migrated an application to Amazon EC2 Linux instances. One of these EC2 instances runs several 1-hour tasks on a schedule. These tasks were written by different teams and have no common programming language. The company is concerned about performance and scalability while these tasks run on a single instance. A solutions architect needs to implement a solution to resolve these concerns. Which solution will meet these requirements with the LEAST operational overhead?

## Options

**A.** Use AWS Batch to run the tasks as jobs. Schedule the jobs by using Amazon EventBridge (Amazon CloudWatch Events).

**B.** Convert the EC2 instance to a container. Use AWS App Runner to create the container on demand to run the tasks as jobs.

**C.** Copy the tasks into AWS Lambda functions. Schedule the Lambda functions by using Amazon EventBridge (Amazon CloudWatch Events).

**D.** Create an Amazon Machine Image (AMI) of the EC2 instance that runs the tasks. Create an Auto Scaling group with the AMI to run multiple copies of the instance.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** EC2 Linux chạy 1-hour tasks (multiple teams, different languages). Need performance/scalability. Single instance bottleneck.
- **Existing Resources:** EC2 Linux instance, multiple 1-hour tasks.
- **Current Issue/Goal:** Scalability, least operational overhead.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `no common programming language` | Tasks khác ngôn ngữ → container hóa hoặc AWS Batch (chạy scripts). |
| `1-hour tasks` | Lambda max 15 min → không đủ. |
| `AWS Batch` | Managed batch computing, chạy jobs trên EC2, schedule via EventBridge. |
| `least operational overhead` | AWS Batch tự động quản lý compute resources và job scheduling. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Least operational overhead
- **Constraints:** Multiple languages, 1-hour tasks, scheduled

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- AWS Batch: managed service cho batch jobs, hỗ trợ bất kỳ ngôn ngữ nào (chạy script), tự động provision EC2 instances dựa trên job requirements.
- Schedule via EventBridge → không cần tự quản lý cron.
- Job queue + tự động scale compute → giải quyết performance/scalability.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- App Runner: dùng cho containerized web apps, không phải batch jobs.

**❌ Đáp án C:**
- Lambda max timeout 15 minutes → không thể chạy 1-hour tasks.

**❌ Đáp án D:**
- ASG + AMI: vẫn chạy tất cả tasks trên mỗi instance, không giải quyết resource contention giữa các tasks.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Multi-language batch jobs → AWS Batch (managed). Lambda = 15 min max. App Runner = web apps."*
