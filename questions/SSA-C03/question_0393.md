# Question #393 - Topic 1

A payment processing company records all voice communication with its customers and stores the audio files in an Amazon S3 bucket. The company needs to capture the text from the audio files. The company must remove from the text any personally identifiable information (PII) that belongs to customers. What should a solutions architect do to meet these requirements?

## Options

**A.** Process the audio files by using Amazon Kinesis Video Streams. Use an AWS Lambda function to scan for known PII patterns.

**B.** When an audio file is uploaded to the S3 bucket, invoke an AWS Lambda function to start an Amazon Textract task to analyze the call recordings.

**C.** Configure an Amazon Transcribe transcription job with PII redaction turned on. When an audio file is uploaded to the S3 bucket, invoke an AWS Lambda function to start the transcription job. Store the output in a separate S3 bucket.

**D.** Create an Amazon Connect contact flow that ingests the audio files with transcription turned on. Embed an AWS Lambda function to scan for known PII patterns. Use Amazon EventBridge to start the contact flow when an audio file is uploaded to the S3 bucket.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Audio files in S3 (voice recordings). Need transcription (speech-to-text) + PII redaction.
- **Existing Resources:** S3 bucket with audio files.
- **Current Issue/Goal:** Transcribe audio + remove PII.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `capture the text from the audio files` | Speech-to-text → Amazon Transcribe. |
| `remove ... PII` | Transcribe có built-in PII redaction feature (tự động detect và redact). |
| `Amazon Transcribe` | Managed speech-to-text service, hỗ trợ PII redaction. |
| `Textract` | Document text extraction (OCR), không phải audio. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Which solution meets requirements
- **Constraints:** Audio transcription + PII redaction

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- Amazon Transcribe: speech-to-text, có built-in PII redaction (tự động detect và redact PII như SSN, credit card, etc.).
- S3 event → Lambda → start Transcribe job → output to separate S3 bucket (without PII).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Kinesis Video Streams: for live video streaming, không phải batch processing audio files. Lambda tự scan PII không hiệu quả bằng Transcribe built-in.

**❌ Đáp án B:**
- Textract: extract text từ documents (invoice, forms), không xử lý audio files.

**❌ Đáp án D:**
- Amazon Connect: contact center service, không phải tool để batch process existing audio files.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Audio → text + PII removal → Amazon Transcribe (built-in PII redaction). Textract = documents. KVS = live video."*
