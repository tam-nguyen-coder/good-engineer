# Question #65 - Topic 1

A hospital recently deployed a RESTful API with Amazon API Gateway and AWS Lambda. The hospital uses API Gateway and Lambda to upload reports that are in PDF format and JPEG format. The hospital needs to modify the Lambda code to identify protected health information (PHI) in the reports. Which solution will meet these requirements with the LEAST operational overhead?

## Options

**A.** Use existing Python libraries to extract the text from the reports and to identify the PHI from the extracted text.

**B.** Use Amazon Textract to extract the text from the reports. Use Amazon SageMaker to identify the PHI from the extracted text.

**C.** Use Amazon Textract to extract the text from the reports. Use Amazon Comprehend Medical to identify the PHI from the extracted text.

**D.** Use Amazon Rekognition to extract the text from the reports. Use Amazon Comprehend Medical to identify the PHI from the extracted text.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Hospital API (API Gateway + Lambda) upload PDF/JPEG reports, cần detect PHI (Protected Health Information).
- **Existing Resources:** API Gateway + Lambda.
- **Current Issue/Goal:** Identify PHI in reports, least operational overhead.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `protected health information (PHI)` | Dữ liệu y tế — cần **Comprehend Medical** |
| `least operational overhead` | Dùng managed AI services |
| `PDF format and JPEG format` | Cần OCR để extract text |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** AI/ML + Healthcare
- **Constraints:** PDF/JPEG → extract text → detect PHI, least overhead

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- **Amazon Textract** — extract text từ PDF và JPEG (OCR + form/data extraction).
- **Amazon Comprehend Medical** — specialized NLP service để detect PHI trong văn bản y tế. Được train đặc biệt cho medical terminology.
- Kết hợp 2 managed services → **least operational overhead**, không cần train model.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Tự viết Python libraries — nhiều dev effort, không tối ưu cho PHI detection.

**❌ Đáp án B:**
- SageMaker yêu cầu train/deploy custom model → nhiều operational overhead hơn Comprehend Medical.

**❌ Đáp án D:**
- **Rekognition** chủ yếu cho image/video analysis, không tối ưu cho OCR từ PDF documents.
- Textract tốt hơn cho document text extraction.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Textract = document text extraction. Comprehend Medical = PHI detection. Rekognition = image/video"*
