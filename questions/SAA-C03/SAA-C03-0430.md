# Question #430 - Topic 1

A manufacturing company has machine sensors that upload .csv files to an Amazon S3 bucket. These .csv files must be converted into images and must be made available as soon as possible for the automatic generation of graphical reports. The images become irrelevant after 1 month, but the .csv files must be kept to train machine learning (ML) models twice a year. The ML trainings and audits are planned weeks in advance. Which combination of steps will meet these requirements MOST cost-effectively? (Choose two.)

## Options

**A.** Launch an Amazon EC2 Spot Instance that downloads the .csv files every hour, generates the image files, and uploads the images to the S3 bucket.

**B.** Design an AWS Lambda function that converts the .csv files into images and stores the images in the S3 bucket. Invoke the Lambda function when a .csv file is uploaded.

**C.** Create S3 Lifecycle rules for .csv files and image files in the S3 bucket. Transition the .csv files from S3 Standard to S3 Glacier 1 day after they are uploaded. Expire the image files after 30 days.

**D.** Create S3 Lifecycle rules for .csv files and image files in the S3 bucket. Transition the .csv files from S3 Standard to S3 One Zone-Infrequent Access (S3 One Zone-IA) 1 day after they are uploaded. Expire the image files after 30 days.

**E.** Create S3 Lifecycle rules for .csv files and image files in the S3 bucket. Transition the .csv files from S3 Standard to S3 Standard-Infrequent Access (S3 Standard-IA) 1 day after they are uploaded. Keep the image files in Reduced Redundancy Storage (RRS).

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Machine sensors upload CSV to S3. Convert CSV → images (urgent). Images expire after 1 month. CSV kept 6 months (ML training + audits). ML planned weeks ahead.
- **Existing Resources:** S3 bucket.
- **Current Issue/Goal:** Cost-effective conversion + lifecycle.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `as soon as possible` | S3 event → Lambda (near-real time). |
| `images irrelevant after 1 month` | Expire (delete) after 30 days. |
| `CSV kept for ML twice a year` | Glacier: cheap, retrieval hours (planned weeks ahead). |
| `most cost-effectively` | Serverless (Lambda) + Glacier (cold storage). |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Cost optimization / Lifecycle
- **Constraints:** Near-real time conversion, 30d image retention, long-term CSV

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B, C**

**Giải thích:**
- **B:** Lambda triggered by S3 event (s3:ObjectCreated) → convert CSV to images ngay lập tức. Serverless, chi phí thấp.
- **C:** CSV → Glacier sau 1 ngày (rẻ, phù hợp truy xuất 2 lần/năm có kế hoạch). Images → expire sau 30 ngày (xóa).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- EC2 Spot Instance chạy hourly: không real-time, chi phí cao hơn Lambda, cần quản lý instance.

**❌ Đáp án D:**
- One Zone-IA: single AZ, không durable cho data cần giữ lâu dài (ML + audits).

**❌ Đáp án E:**
- RRS: deprecated, không recommended. Standard-IA đắt hơn Glacier cho data rarely accessed.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"S3 upload → Lambda convert. CSV → Glacier (rare access). Images → expire 30 days."*