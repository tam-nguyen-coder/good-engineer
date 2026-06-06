# Question #621 - Topic 1

An online photo-sharing company stores its photos in an Amazon S3 bucket that exists in the us-west-1 Region. The company needs to store a copy of all new photos in the us-east-1 Region. Which solution will meet this requirement with the LEAST operational effort?

## Options

**A.** Create a second S3 bucket in us-east-1. Use S3 Cross-Region Replication to copy photos from the existing S3 bucket to the second S3 bucket.

**B.** Create a cross-origin resource sharing (CORS) configuration of the existing S3 bucket. Specify us-east-1 in the CORS rule's AllowedOrigin element.

**C.** Create a second S3 bucket in us-east-1 across multiple Availability Zones. Create an S3 Lifecycle rule to save photos into the second S3 bucket.

**D.** Create a second S3 bucket in us-east-1. Configure S3 event notifications on object creation and update events to invoke an AWS Lambda function to copy photos from the existing S3 bucket to the second S3 bucket.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Photo-sharing company, S3 bucket in us-west-1, cần copy all new photos to us-east-1.
- **Existing Resources:** S3 bucket in us-west-1.
- **Current Issue/Goal:** Cross-region replication cho new objects với least operational effort.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `copy of all new photos` | Cần replicate objects tự động khi upload. |
| `Cross-Region Replication` | S3 CRR: tự động replicate objects giữa các regions, zero code. |
| `least operational effort` | CRR là managed tính năng của S3, không cần code. |
| `new photos` | CRR replicate objects mới (hoặc tất cả nếu enabled). |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Least operational effort
- **Constraints:** Cross-region copy for new objects only

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- S3 Cross-Region Replication (CRR): tính năng built-in của S3, tự động replicate objects từ bucket us-west-1 sang bucket us-east-1.
- Chỉ cần configure replication rule một lần, không cần code hay infrastructure.
- CRR là giải pháp managed, operational effort thấp nhất.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- CORS (Cross-Origin Resource Sharing) là tính năng cho web browser security, không liên quan đến replication.

**❌ Đáp án C:**
- S3 Lifecycle rule dùng để transition objects giữa các storage classes, không phải để copy giữa các buckets.

**❌ Đáp án D:**
- S3 Event + Lambda function: phải code, deploy, maintain Lambda function → operational effort cao hơn CRR.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Copy objects between regions → S3 Cross-Region Replication (managed, no code). Lambda = effort hơn."*
