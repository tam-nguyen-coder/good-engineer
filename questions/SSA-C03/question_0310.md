# Question #310 - Topic 1

A company sells datasets to customers who do research in artificial intelligence and machine learning (AI/ML). The datasets are large, formatted files that are stored in an Amazon S3 bucket in the us-east-1 Region. The company hosts a web application that the customers use to purchase access to a given dataset. The web application is deployed on multiple Amazon EC2 instances behind an Application Load Balancer. After a purchase is made, customers receive an S3 signed URL that allows access to the files. The customers are distributed across North America and Europe. The company wants to reduce the cost that is associated with data transfers and wants to maintain or improve performance. What should a solutions architect do to meet these requirements?

## Options

**A.** Configure S3 Transfer Acceleration on the existing S3 bucket. Direct customer requests to the S3 Transfer Acceleration endpoint. Continue to use S3 signed URLs for access control.

**B.** Deploy an Amazon CloudFront distribution with the existing S3 bucket as the origin. Direct customer requests to the CloudFront URL. Switch to CloudFront signed URLs for access control.

**C.** Set up a second S3 bucket in the eu-central-1 Region with S3 Cross-Region Replication between the buckets. Direct customer requests to the closest Region. Continue to use S3 signed URLs for access control.

**D.** Modify the web application to enable streaming of the datasets to end users. Configure the web application to read the data from the existing S3 bucket. Implement access control directly in the application.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Large AI/ML datasets in S3 us-east-1, customers in NA and Europe. Dùng S3 signed URLs. Cần giảm data transfer cost, maintain/improve performance.
- **Existing Resources:** S3 bucket us-east-1, web app (EC2 + ALB), S3 signed URLs.
- **Current Issue/Goal:** Reduce data transfer costs, improve performance for global users.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `reduce cost associated with data transfers` | S3 data transfer (egress) cost cao → CloudFront giảm cost (giá egress CloudFront thấp hơn S3). |
| `maintain or improve performance` | CloudFront cache at edge → giảm latency cho global users. |
| `CloudFront` | CDN: cache content at edge locations worldwide, giảm S3 data transfer cost. |
| `CloudFront signed URLs` | Thay thế S3 signed URLs, cho phép kiểm soát access tại CloudFront edge. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Reduce cost + maintain/improve performance
- **Constraints:** Global users (NA + Europe), S3 origin, access control needed

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- CloudFront cache datasets tại edge locations gần users → improved performance (lower latency) và giảm load trên S3 origin.
- CloudFront egress pricing thường thấp hơn S3 data transfer → reduced cost.
- CloudFront signed URLs thay thế S3 signed URLs, vẫn kiểm soát access.
- Không cần thay đổi application logic.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- S3 Transfer Acceleration chỉ tăng tốc upload lên S3, không cải thiện download performance và không giảm data transfer cost.

**❌ Đáp án C:**
- S3 CRR + second bucket ở eu-central-1: vẫn trả S3 data transfer cost từ S3 đến users (không giảm). Cross-Region replication có chi phí replication.

**❌ Đáp án D:**
- Streaming qua web application không giảm data transfer cost và tăng operational overhead (application phải xử lý streaming).

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Global users + S3 data cost → CloudFront (edge cache, egress rẻ hơn). Transfer Acceleration = upload only."*
