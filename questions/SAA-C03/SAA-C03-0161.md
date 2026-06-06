# Question #161 - Topic 1

A company has a small Python application that processes JSON documents and outputs the results to an on-premises SQL database. The application runs thousands of times each day. The company wants to move the application to the AWS Cloud. The company needs a highly available solution that maximizes scalability and minimizes operational overhead. Which solution will meet these requirements?

## Options

**A.** Place the JSON documents in an Amazon S3 bucket. Run the Python code on multiple Amazon EC2 instances to process the documents. Store the results in an Amazon Aurora DB cluster.

**B.** Place the JSON documents in an Amazon S3 bucket. Create an AWS Lambda function that runs the Python code to process the documents as they arrive in the S3 bucket. Store the results in an Amazon Aurora DB cluster.

**C.** Place the JSON documents in an Amazon Elastic Block Store (Amazon EBS) volume. Use the EBS Multi-Attach feature to attach the volume to multiple Amazon EC2 instances. Run the Python code on the EC2 instances to process the documents. Store the results on an Amazon RDS DB instance.

**D.** Place the JSON documents in an Amazon Simple Queue Service (Amazon SQS) queue as messages. Deploy the Python code as a container on an Amazon Elastic Container Service (Amazon ECS) cluster that is configured with the Amazon EC2 launch type. Use the container to process the SQS messages. Store the results on an Amazon RDS DB instance.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Python app process JSON → SQL DB. Runs thousands of times/day. HA, scalable, min overhead.
- **Existing Resources:** Python app.
- **Current Issue/Goal:** Serverless migration.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `maximizes scalability` | Lambda auto-scale |
| `minimizes operational overhead` | Serverless |
| `Python` | Lambda hỗ trợ Python runtime |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Serverless migration
- **Constraints:** HA, scalable, min overhead

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- **S3 event → Lambda** — serverless, auto-scale, chỉ chạy khi có JSON document.
- **Aurora** — managed DB, HA, scalable.
- Python code chạy trong Lambda → không cần quản lý servers.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- EC2 instances — phải quản lý, không auto-scale như Lambda.

**❌ Đáp án C:**
- EBS Multi-Attach — complex, limited to few instances.

**❌ Đáp án D:**
- ECS + EC2 — operational overhead cao hơn Lambda.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"S3 + Lambda = serverless event-driven. Aurora = managed DB. EC2/ECS = more overhead"*
