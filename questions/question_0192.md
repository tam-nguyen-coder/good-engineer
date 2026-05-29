# Question #192 - Topic 1

A hospital wants to create digital copies for its large collection of historical written records. The hospital will continue to add hundreds of new documents each day. The hospital's data team will scan the documents and will upload the documents to the AWS Cloud. A solutions architect must implement a solution to analyze the documents, extract the medical information, and store the documents so that an application can run SQL queries on the data. The solution must maximize scalability and operational efficiency. Which combination of steps should the solutions architect take to meet these requirements? (Choose two.)

## Options

**A.** Write the document information to an Amazon EC2 instance that runs a MySQL database.

**B.** Write the document information to an Amazon S3 bucket. Use Amazon Athena to query the data.

**C.** Create an Auto Scaling group of Amazon EC2 instances to run a custom application that processes the scanned files and extracts the medical information.

**D.** Create an AWS Lambda function that runs when new documents are uploaded. Use Amazon Rekognition to convert the documents to raw text. Use Amazon Transcribe Medical to detect and extract relevant medical information from the text.

**E.** Create an AWS Lambda function that runs when new documents are uploaded. Use Amazon Textract to convert the documents to raw text. Use Amazon Comprehend Medical to detect and extract relevant medical information from the text.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Hospital scanned documents → analyze → extract medical info → SQL queries. Hundreds/day.
- **Existing Resources:** Scanned documents.
- **Current Issue/Goal:** Serverless document processing + SQL-capable storage.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `written records` | Scanned documents → **Textract** (OCR) |
| `medical information` | **Comprehend Medical** (NLP for medical) |
| `run SQL queries` | **S3 + Athena** (serverless SQL) |
| `maximize scalability and operational efficiency` | Serverless |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Document processing / AI
- **Constraints:** Chọn 2, scalable, efficient

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B và E**

**Giải thích:**
- **E: Lambda + Textract + Comprehend Medical** — Textract (OCR) trích xuất text từ scanned documents, Comprehend Medical phát hiện thông tin y tế.
- **B: S3 + Athena** — lưu kết quả dạng structured (CSV/JSON/Parquet) → Athena query bằng SQL.
- Cả hai đều serverless → tối đa scalability và efficiency.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- EC2 + MySQL — không scalable, operational overhead.

**❌ Đáp án C:**
- EC2 ASG + custom app — overhead, không cần thiết khi có Textract + Comprehend Medical.

**❌ Đáp án D:**
- Rekognition — computer vision, không phải OCR. Transcribe Medical — cho audio, không phải documents.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Textract = document OCR. Comprehend Medical = medical NLP. Athena = SQL on S3. Rekognition = images. Transcribe = audio"*
