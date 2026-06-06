# Question #375 - Topic 1

An ecommerce company is building a distributed application that involves several serverless functions and AWS services to complete order- processing tasks. These tasks require manual approvals as part of the workflow. A solutions architect needs to design an architecture for the order-processing application. The solution must be able to combine multiple AWS Lambda functions into responsive serverless applications. The solution also must orchestrate data and services that run on Amazon EC2 instances, containers, or on-premises servers. Which solution will meet these requirements with the LEAST operational overhead?

## Options

**A.** Use AWS Step Functions to build the application.

**B.** Integrate all the application components in an AWS Glue job.

**C.** Use Amazon Simple Queue Service (Amazon SQS) to build the application.

**D.** Use AWS Lambda functions and Amazon EventBridge events to build the application.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Distributed order processing, Lambda functions + manual approvals. Orchestrate across Lambda, EC2, containers, on-premises. Least operational overhead.
- **Existing Resources:** (none specified)
- **Current Issue/Goal:** Workflow orchestration with manual approvals.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `manual approvals` | Step Functions hỗ trợ activity tasks + manual approval steps (wait for callback). |
| `orchestrate data and services` | Step Functions: orchestrate Lambda, EC2, containers, on-premises. |
| `combine multiple Lambda functions` | Step Functions state machine gọi Lambda tuần tự/parallel. |
| `least operational overhead` | Step Functions serverless orchestration. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Least operational overhead
- **Constraints:** Manual approvals, multi-service orchestration

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- Step Functions: serverless workflow orchestration, support manual approval steps (task token, wait for callback).
- Có thể invoke Lambda, EC2 (run tasks), containers (ECS/Fargate), on-premises (HTTP activity workers).
- Built-in retry, error handling, state management.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Glue là ETL service, không phải workflow orchestration cho business processes.

**❌ Đáp án C:**
- SQS: message queue, không có built-in orchestration, state management, manual approval.

**❌ Đáp án D:**
- Lambda + EventBridge: có thể orchestrate nhưng không có state management, retry, manual approval built-in.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Manual approval + multi-service orchestration → Step Functions (state machine). SQS = queue only, không orchestration."*
