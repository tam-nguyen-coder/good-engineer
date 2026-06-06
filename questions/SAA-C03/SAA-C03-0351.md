# Question #351 - Topic 1

A company is moving its data management application to AWS. The company wants to transition to an event-driven architecture. The architecture needs to be more distributed and to use serverless concepts while performing the different aspects of the workflow. The company also wants to minimize operational overhead. Which solution will meet these requirements?

## Options

**A.** Build out the workflow in AWS Glue. Use AWS Glue to invoke AWS Lambda functions to process the workflow steps.

**B.** Build out the workflow in AWS Step Functions. Deploy the application on Amazon EC2 instances. Use Step Functions to invoke the workflow steps on the EC2 instances.

**C.** Build out the workflow in Amazon EventBridge. Use EventBridge to invoke AWS Lambda functions on a schedule to process the workflow steps.

**D.** Build out the workflow in AWS Step Functions. Use Step Functions to create a state machine. Use the state machine to invoke AWS Lambda functions to process the workflow steps.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Application migration to AWS, cần event-driven architecture, distributed + serverless workflow. Minimize operational overhead.
- **Existing Resources:** (none specified)
- **Current Issue/Goal:** Event-driven, serverless workflow orchestration.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `event-driven architecture` | Workflow orchestration với các steps phản ứng theo events. |
| `serverless concepts` | Step Functions (serverless orchestration) + Lambda (serverless compute). |
| `minimize operational overhead` | Step Functions + Lambda = serverless, không quản lý servers. |
| `AWS Step Functions` | State machine cho workflow orchestration: sequence, parallel, retry, error handling. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Which solution meets requirements
- **Constraints:** Event-driven, distributed, serverless, minimal overhead

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- Step Functions: serverless workflow orchestration (state machine), quản lý sequence, retries, error handling.
- Lambda: serverless compute cho mỗi step.
- Cả 2 đều serverless → không quản lý infrastructure, operational overhead thấp.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Glue là ETL service, không phải workflow orchestration cho event-driven architecture.

**❌ Đáp án B:**
- EC2 instances → không serverless, operational overhead cao hơn Lambda.

**❌ Đáp án C:**
- EventBridge: event bus, không phải workflow orchestration (không quản lý state, retry, sequence).

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Serverless workflow orchestration → Step Functions + Lambda. Glue = ETL. EventBridge = event bus."*
