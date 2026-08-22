# Question #114 - Topic 1

A company has created an image analysis application in which users can upload photos and add photo frames to their images. The users upload images and metadata to indicate which photo frames they want to add to their images. The application uses a single Amazon EC2 instance and Amazon DynamoDB to store the metadata. The application is becoming more popular, and the number of users is increasing. The company expects the number of concurrent users to vary significantly depending on the time of day and day of week. The company must ensure that the application can scale to meet the needs of the growing user base. Which solution meats these requirements?

## Options

**A.** Use AWS Lambda to process the photos. Store the photos and metadata in DynamoDB.

**B.** Use Amazon Kinesis Data Firehose to process the photos and to store the photos and metadata.

**C.** Use AWS Lambda to process the photos. Store the photos in Amazon S3. Retain DynamoDB to store the metadata.

**D.** Increase the number of EC2 instances to three. Use Provisioned IOPS SSD (io2) Amazon Elastic Block Store (Amazon EBS) volumes to store the photos and metadata.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Image analysis app, EC2 + DynamoDB. Growing users, variable concurrent users.
- **Existing Resources:** EC2, DynamoDB (metadata).
- **Current Issue/Goal:** Scale for growing + variable traffic.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `number of concurrent users to vary significantly` | Cần auto-scaling |
| `growing user base` | Cần scalable architecture |
| `photos` | File storage → **S3** (không phải DynamoDB) |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Scalability
- **Constraints:** Variable traffic, growing

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- **Lambda** — serverless, scale tự động theo số lượng requests.
- **S3** — lưu photos, scalable, durable.
- **DynamoDB** — lưu metadata, serverless, scalable.
- Tách biệt: S3 cho files, DynamoDB cho metadata.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- DynamoDB max item size **400 KB** — không thể lưu photos trong DynamoDB.

**❌ Đáp án B:**
- Kinesis Data Firehose là streaming delivery, không phải compute/storage cho image processing.

**❌ Đáp án D:**
- 3 EC2 instances không scale đủ. EBS không shared, không scalable như S3.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"DynamoDB max 400KB = không chứa file. S3 = file storage. Lambda = auto-scale compute"*
