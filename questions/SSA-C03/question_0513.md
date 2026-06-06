# Question #513 - Topic 1

A social media company wants to allow its users to upload images in an application that is hosted in the AWS Cloud. The company needs a solution that automatically resizes the images so that the images can be displayed on multiple device types. The application experiences unpredictable traffic patterns throughout the day. The company is seeking a highly available solution that maximizes scalability. What should a solutions architect do to meet these requirements?

## Options

**A.** Create a static website hosted in Amazon S3 that invokes AWS Lambda functions to resize the images and store the images in an Amazon S3 bucket.

**B.** Create a static website hosted in Amazon CloudFront that invokes AWS Step Functions to resize the images and store the images in an Amazon RDS database.

**C.** Create a dynamic website hosted on a web server that runs on an Amazon EC2 instance. Configure a process that runs on the EC2 instance to resize the images and store the images in an Amazon S3 bucket.

**D.** Create a dynamic website hosted on an automatically scaling Amazon Elastic Container Service (Amazon ECS) cluster that creates a resize job in Amazon Simple Queue Service (Amazon SQS). Set up an image-resizing program that runs on an Amazon EC2 instance to process the resize jobs.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Upload images, auto-resize cho nhiều device types. Traffic unpredictable, cần HA và scalable.
- **Existing Resources:** AWS Cloud application.
- **Current Issue/Goal:** Serverless image processing pipeline, highly available, scalable.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `unpredictable traffic` | Cần serverless (scale tự động từ 0 đến vô hạn). |
| `highly available` | Không single point of failure. |
| `maximizes scalability` | Scale ngang, không giới hạn. |
| `automatically resizes images` | Xử lý sau khi upload (event-driven). |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Highly available + maximize scalability
- **Constraints:** Image upload + resize, unpredictable traffic

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- S3 static website host frontend, S3 bucket store images → HA và scalable vô hạn.
- S3 event notification trigger Lambda function khi có image upload → Lambda resize và lưu vào S3.
- Lambda tự động scale từ 0 đến hàng nghìn concurrent executions → phù hợp với unpredictable traffic.
- Serverless, không cần quản lý infrastructure.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Step Functions để resize images → overkill và không hiệu quả (Step Functions cho orchestration workflow, không cho compute).
- Lưu images vào RDS database → sai (RDS không phải object storage cho images). Cực kỳ tốn kém và không scalable.

**❌ Đáp án C:**
- Single EC2 instance → không highly available, không scalable. Single point of failure.

**❌ Đáp án D:**
- ECS cluster + SQS + EC2 resizer → quá phức tạp, operational overhead cao. EC2 instance cho resize là bottleneck và không serverless.
- Mặc dù scalable hơn C, nhưng vẫn kém hơn Lambda (serverless) về scalability và operational overhead.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Upload + resize → S3 event → Lambda (serverless). Không dùng EC2 cho unpredictable traffic."*
