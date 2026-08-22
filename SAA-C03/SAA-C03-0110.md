# Question #110 - Topic 1

A social media company allows users to upload images to its website. The website runs on Amazon EC2 instances. During upload requests, the website resizes the images to a standard size and stores the resized images in Amazon S3. Users are experiencing slow upload requests to the website. The company needs to reduce coupling within the application and improve website performance. A solutions architect must design the most operationally efficient process for image uploads. Which combination of actions should the solutions architect take to meet these requirements? (Choose two.)

## Options

**A.** Configure the application to upload images to S3 Glacier.

**B.** Configure the web server to upload the original images to Amazon S3.

**C.** Configure the application to upload images directly from each user's browser to Amazon S3 through the use of a presigned URL

**D.** Configure S3 Event Notifications to invoke an AWS Lambda function when an image is uploaded. Use the function to resize the image.

**E.** Create an Amazon EventBridge (Amazon CloudWatch Events) rule that invokes an AWS Lambda function on a schedule to resize uploaded images.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Image upload website, EC2 resize images → S3. Slow uploads.
- **Existing Resources:** EC2 website, S3 bucket.
- **Current Issue/Goal:** Reduce coupling, improve performance.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `reduce coupling` | Decouple upload từ processing |
| `improve website performance` | Giảm tải cho web server |
| `presigned URL` | Upload trực tiếp từ browser → S3 |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Performance + Decoupling
- **Constraints:** Chọn 2 đáp án

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C và D**

**Giải thích:**
- **C: Presigned URL** — user browser upload trực tiếp vào S3, không qua EC2 → giảm tải, tăng tốc.
- **D: S3 Event → Lambda** — resize image async, không block upload, decoupled.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- S3 Glacier không phù hợp cho upload/download thường xuyên.

**❌ Đáp án B:**
- Upload qua web server vẫn tạo bottleneck, không giảm coupling.

**❌ Đáp án E:**
- Scheduled Lambda — không real-time, ảnh không được resize ngay sau upload.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Presigned URL = direct upload to S3. S3 Event + Lambda = async processing. Decoupled + fast"*
