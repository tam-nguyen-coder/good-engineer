# Question #322 - Topic 1

A solutions architect is designing a multi-tier application for a company. The application's users upload images from a mobile device. The application generates a thumbnail of each image and returns a message to the user to confirm that the image was uploaded successfully. The thumbnail generation can take up to 60 seconds, but the company wants to provide a faster response time to its users to notify them that the original image was received. The solutions architect must design the application to asynchronously dispatch requests to the different application tiers. What should the solutions architect do to meet these requirements?

## Options

**A.** Write a custom AWS Lambda function to generate the thumbnail and alert the user. Use the image upload process as an event source to invoke the Lambda function.

**B.** Create an AWS Step Functions workflow. Configure Step Functions to handle the orchestration between the application tiers and alert the user when thumbnail generation is complete.

**C.** Create an Amazon Simple Queue Service (Amazon SQS) message queue. As images are uploaded, place a message on the SQS queue for thumbnail generation. Alert the user through an application message that the image was received.

**D.** Create Amazon Simple Notification Service (Amazon SNS) notification topics and subscriptions. Use one subscription with the application to generate the thumbnail after the image upload is complete. Use a second subscription to message the user's mobile app by way of a push notification after thumbnail generation is complete.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** User upload image → generate thumbnail (up to 60s). Want to notify user ngay khi upload thành công (async processing).
- **Existing Resources:** Mobile app, image upload system.
- **Current Issue/Goal:** Async dispatch, fast response to user, thumbnail generation diễn ra sau.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `asynchronously dispatch requests` | Cần decouple: upload response ngay lập tức, thumbnail processing sau. |
| `faster response time` | Không chờ thumbnail xong mới respond. |
| `SQS` | Message queue để decouple: upload → SQS → backend process thumbnail. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Asynchronous dispatch design
- **Constraints:** Faster response, thumbnail generation up to 60s

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- SQS queue nhận message khi image upload thành công → user nhận confirmation ngay.
- Backend worker poll SQS và generate thumbnail async.
- Decoupling giữa upload và thumbnail processing → user không phải chờ.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Lambda generate thumbnail đồng bộ (invoked by event) → user vẫn phải chờ nếu Lambda chạy lâu. Lambda max timeout 15 minutes nhưng synchronous response bị ảnh hưởng.

**❌ Đáp án B:**
- Step Functions orchestration phức tạp hơn cần thiết. Vẫn có thể gây delay cho user response nếu thiết kế synchronous.

**❌ Đáp án D:**
- SNS: publish/subscribe. Nếu subscriber xử lý thumbnail chậm, không có message persistence (trừ khi dùng SQS). SNS không persist messages → có thể mất messages nếu subscriber fails.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Async processing + fast response → SQS queue (decouple). SNS = no persistence. Lambda sync = chờ."*
