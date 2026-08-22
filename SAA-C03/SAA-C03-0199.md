# Question #199 - Topic 1

A telemarketing company is designing its customer call center functionality on AWS. The company needs a solution that provides multiple speaker recognition and generates transcript files. The company wants to query the transcript files to analyze the business patterns. The transcript files must be stored for 7 years for auditing purposes. Which solution will meet these requirements?

## Options

**A.** Use Amazon Rekognition for multiple speaker recognition. Store the transcript files in Amazon S3. Use machine learning models for transcript file analysis.

**B.** Use Amazon Transcribe for multiple speaker recognition. Use Amazon Athena for transcript file analysis.

**C.** Use Amazon Translate for multiple speaker recognition. Store the transcript files in Amazon Redshift. Use SQL queries for transcript file analysis.

**D.** Use Amazon Rekognition for multiple speaker recognition. Store the transcript files in Amazon S3. Use Amazon Textract for transcript file analysis.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Call center, multi-speaker recognition → transcript → query for business patterns → store 7 years.
- **Existing Resources:** None.
- **Current Issue/Goal:** Speech-to-text + analytics.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `multiple speaker recognition` | **Amazon Transcribe** (speaker diarization) |
| `query the transcript files` | **Amazon Athena** (SQL on S3) |
| `store for 7 years` | S3 (durable, cheap) |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** AI / Analytics
- **Constraints:** Speech-to-text, query, long-term storage

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- **Amazon Transcribe** — tự động nhận dạng giọng nói, hỗ trợ speaker diarization (multiple speakers).
- **Amazon Athena** — query transcript files (JSON/CSV) trực tiếp trên S3 bằng SQL.
- S3 — cost-effective cho 7-year storage.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Rekognition — computer vision, không phải speech recognition.

**❌ Đáp án C:**
- Translate — language translation, không phải speech-to-text.

**❌ Đáp án D:**
- Rekognition + Textract — sai, Rekognition không xử lý audio, Textract là OCR cho documents.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Transcribe = speech-to-text (speaker diarization). Athena = SQL on S3. Rekognition = images. Translate = language"*
