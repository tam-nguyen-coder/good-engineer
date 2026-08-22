# Question #286 - Topic 1

A company has a static website that is hosted on Amazon CloudFront in front of Amazon S3. The static website uses a database backend. The company notices that the website does not reflect updates that have been made in the website's Git repository. The company checks the continuous integration and continuous delivery (CI/CD) pipeline between the Git repository and Amazon S3. The company verifies that the webhooks are configured properly and that the CI/CD pipeline is sending messages that indicate successful deployments. A solutions architect needs to implement a solution that displays the updates on the website. Which solution will meet these requirements?

## Options

**A.** Add an Application Load Balancer.

**B.** Add Amazon ElastiCache for Redis or Memcached to the database layer of the web application.

**C.** Invalidate the CloudFront cache.

**D.** Use AWS Certificate Manager (ACM) to validate the website's SSL certificate.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** CloudFront + S3 static website. CI/CD deploy thành công nhưng website không hiển thị cập nhật.
- **Existing Resources:** CloudFront distribution, S3 bucket, CI/CD pipeline.
- **Current Issue/Goal:** Website không hiển thị nội dung mới sau deploy.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `CloudFront` | CDN cache nội dung tại edge locations. |
| `does not reflect updates` | Cache cũ vẫn được serve dù nội dung S3 đã được cập nhật. |
| `successful deployments` | S3 đã được cập nhật → vấn đề nằm ở cache layer (CloudFront). |
| `Invalidate the CloudFront cache` | Xóa cache edge locations để lấy nội dung mới từ origin (S3). |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Which solution meets requirements
- **Constraints:** Deploy thành công nhưng content không reflect

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- CloudFront cache nội dung tại edge locations. Khi S3 được cập nhật, CloudFront vẫn serve phiên bản cũ từ cache.
- Invalidate cache (tạo invalidation request) → CloudFront fetch nội dung mới từ S3 và cập nhật edge locations.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- ALB không liên quan. Website dùng CloudFront + S3 không cần ALB.

**❌ Đáp án B:**
- ElastiCache giúp caching database queries, không liên quan đến CloudFront cache của static files.

❌ **Đáp án D:**
- ACM quản lý SSL/TLS certificates, không ảnh hưởng đến cache invalidation.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"CloudFront serve nội dung cũ sau deploy → cần invalidation. CI/CD nên tự động invalidate cache sau mỗi lần deploy."*
