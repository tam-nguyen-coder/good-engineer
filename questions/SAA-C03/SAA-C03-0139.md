# Question #139 - Topic 1

A reporting team receives files each day in an Amazon S3 bucket. The reporting team manually reviews and copies the files from this initial S3 bucket to an analysis S3 bucket each day at the same time to use with Amazon QuickSight. Additional teams are starting to send more files in larger sizes to the initial S3 bucket. The reporting team wants to move the files automatically analysis S3 bucket as the files enter the initial S3 bucket. The reporting team also wants to use AWS Lambda functions to run pattern-matching code on the copied data. In addition, the reporting team wants to send the data files to a pipeline in Amazon SageMaker Pipelines. What should a solutions architect do to meet these requirements with the LEAST operational overhead?

## Options

**A.** Create a Lambda function to copy the files to the analysis S3 bucket. Create an S3 event notification for the analysis S3 bucket. Configure Lambda and SageMaker Pipelines as destinations of the event notification. Configure s3:ObjectCreated:Put as the event type.

**B.** Create a Lambda function to copy the files to the analysis S3 bucket. Configure the analysis S3 bucket to send event notifications to Amazon EventBridge (Amazon CloudWatch Events). Configure an ObjectCreated rule in EventBridge (CloudWatch Events). Configure Lambda and SageMaker Pipelines as targets for the rule.

**C.** Configure S3 replication between the S3 buckets. Create an S3 event notification for the analysis S3 bucket. Configure Lambda and SageMaker Pipelines as destinations of the event notification. Configure s3:ObjectCreated:Put as the event type.

**D.** Configure S3 replication between the S3 buckets. Configure the analysis S3 bucket to send event notifications to Amazon EventBridge (Amazon CloudWatch Events). Configure an ObjectCreated rule in EventBridge (CloudWatch Events). Configure Lambda and SageMaker Pipelines as targets for the rule.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Auto copy files initial S3 → analysis S3 (S3 replication), trigger Lambda + SageMaker Pipelines.
- **Existing Resources:** Initial S3 bucket.
- **Current Issue/Goal:** Auto replication + event-driven processing, least overhead.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `move the files automatically` | **S3 replication** (managed) |
| `pattern-matching code` | Lambda function |
| `SageMaker Pipelines` | ML pipeline |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Data processing + Automation
- **Constraints:** Least operational overhead

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- **S3 replication** — tự động copy files, managed, không cần Lambda copy.
- **S3 event notification** trên analysis bucket → trigger Lambda + SageMaker Pipelines.
- **Least operational overhead** — replication managed, event notification native.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Lambda để copy files — operational overhead (phải viết code, error handling).

**❌ Đáp án B:**
- Lambda copy + EventBridge — over-engineered, nhiều moving parts.

**❌ Đáp án D:**
- S3 replication đúng + EventBridge — EventBridge thêm complexity so với S3 event notification trực tiếp.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"S3 replication = managed copy. S3 event notification = trigger Lambda/SageMaker. EventBridge = extra complexity"*
