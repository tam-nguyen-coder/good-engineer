# Question #57 - Topic 1

A company is running a popular social media website. The website gives users the ability to upload images to share with other users. The company wants to make sure that the images do not contain inappropriate content. The company needs a solution that minimizes development effort. What should a solutions architect do to meet these requirements?

## Options

**A.** Use Amazon Comprehend to detect inappropriate content. Use human review for low-confidence predictions.

**B.** Use Amazon Rekognition to detect inappropriate content. Use human review for low-confidence predictions.

**C.** Use Amazon SageMaker to detect inappropriate content. Use ground truth to label low-confidence predictions.

**D.** Use AWS Fargate to deploy a custom machine learning model to detect inappropriate content. Use ground truth to label low-confidence predictions.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Social media website, users upload images, need to detect inappropriate content.
- **Existing Resources:** Website với image upload.
- **Current Issue/Goal:** Detect inappropriate images, minimize development effort.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `images` | Dữ liệu là hình ảnh → cần image analysis |
| `minimizes development effort` | Dùng AI service có sẵn, không tự xây dựng model |
| `inappropriate content` | Moderation / NSFW detection |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Cost-effective + Minimal dev effort
- **Constraints:** Image content moderation

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- **Amazon Rekognition** có built-in **content moderation** API — phát hiện nội dung không phù hợp (NSFW, violence, v.v.).
- Là managed AI service, không cần train model → minimal dev effort.
- Hỗ trợ human review cho low-confidence predictions (có thể tích hợp với Amazon Augmented AI).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- **Amazon Comprehend** là NLP service cho text, không phân tích được nội dung hình ảnh.

**❌ Đáp án C:**
- **Amazon SageMaker** yêu cầu tự train/deploy model → nhiều dev effort hơn.

**❌ Đáp án D:**
- **Fargate + custom ML model** — nhiều dev effort nhất (phải tự build, train, deploy model).

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Rekognition = image/video analysis. Comprehend = text/NLP. SageMaker = custom ML"*
