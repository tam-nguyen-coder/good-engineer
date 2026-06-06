# Question #452 - Topic 1

A company runs a Java-based job on an Amazon EC2 instance. The job runs every hour and takes 10 seconds to run. The job runs on a scheduled interval and consumes 1 GB of memory. The CPU utilization of the instance is low except for short surges during which the job uses the maximum CPU available. The company wants to optimize the costs to run the job. Which solution will meet these requirements?

## Options

**A.** Use AWS App2Container (A2C) to containerize the job. Run the job as an Amazon Elastic Container Service (Amazon ECS) task on AWS Fargate with 0.5 virtual CPU (vCPU) and 1 GB of memory.

**B.** Copy the code into an AWS Lambda function that has 1 GB of memory. Create an Amazon EventBridge scheduled rule to run the code each hour.

**C.** Use AWS App2Container (A2C) to containerize the job. Install the container in the existing Amazon Machine Image (AMI). Ensure that the schedule stops the container when the task finishes.

**D.** Configure the existing schedule to stop the EC2 instance at the completion of the job and restart the EC2 instance when the next job starts.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Java job on EC2, hourly, 10s runtime, 1GB memory, low CPU. Optimize cost.
- **Existing Resources:** EC2 instance.
- **Current Issue/Goal:** Cheapest option for short, infrequent compute job.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `10 seconds to run` | Very short execution → Lambda (pay per ms) cheapest. |
| `1 GB of memory` | Lambda supports up to 10GB memory. |
| `optimize costs` | Lambda: pay per invocation + duration. |
| `Java-based` | Lambda supports Java runtime. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Cost optimization / Serverless
- **Constraints:** Hourly job, 10s, 1GB memory

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- Lambda: pay per request + duration. 10s x 730 giờ/tháng = ~2 giờ compute/tháng → rất rẻ.
- EventBridge schedule: trigger Lambda mỗi giờ.
- 1GB memory: Lambda supported.
- Java runtime: Lambda supports Java.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Fargate: pay per vCPU + memory per second. Đắt hơn Lambda cho job 10s.

**❌ Đáp án C:**
- Container trên existing AMI: vẫn chạy trên EC2 (trả tiền full time).

**❌ Đáp án D:**
- Stop/start EC2: phức tạp, EBS storage vẫn tính phí.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Short periodic job → Lambda + EventBridge. Rẻ nhất (pay per ms)."*