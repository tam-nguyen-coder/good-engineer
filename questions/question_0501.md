# Question #501 - Topic 1

A company wants to ingest customer payment data into the company's data lake in Amazon S3. The company receives payment data every minute on average. The company wants to analyze the payment data in real time. Then the company wants to ingest the data into the data lake. Which solution will meet these requirements with the MOST operational efficiency?

## Options

**A.** Use Amazon Kinesis Data Streams to ingest data. Use AWS Lambda to analyze the data in real time.

**B.** Use AWS Glue to ingest data. Use Amazon Kinesis Data Analytics to analyze the data in real time.

**C.** Use Amazon Kinesis Data Firehose to ingest data. Use Amazon Kinesis Data Analytics to analyze the data in real time.

**D.** Use Amazon API Gateway to ingest data. Use AWS Lambda to analyze the data in real time.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Công ty cần ingest dữ liệu thanh toán (dạng streaming, mỗi phút một lần) vào data lake S3. Yêu cầu: phân tích real-time trước, sau đó mới đưa vào S3.
- **Existing Resources:** Data Lake trên S3, nguồn dữ liệu payment.
- **Current Issue/Goal:** Cần pipeline real-time vừa phân tích vừa lưu trữ, operational efficiency cao nhất.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `ingest data into Amazon S3 data lake` | Cần service tự động ghi dữ liệu xuống S3. |
| `analyze in real time` | Cần real-time analytics, không phải batch. |
| `MOST operational efficiency` | Càng ít phải tự quản lý càng tốt (serverless/managed). |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most operational efficiency
- **Constraints:** Real-time analysis + deliver to S3 data lake

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- Kinesis Data Firehose là fully managed service, tự động ingest và deliver dữ liệu vào S3 mà không cần quản lý consumer.
- Kinesis Data Analytics (KDA) có thể phân tích dữ liệu streaming real-time, output vào Firehose để ghi xuống S3.
- Kết hợp KDF + KDA cho phép vừa phân tích real-time vừa tự động lưu vào data lake với operational overhead thấp nhất.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Kinesis Data Streams ingest được nhưng cần tự quản lý consumer (EC2/Lambda) để đọc và xử lý stream. Lambda phân tích xong vẫn cần code riêng để ghi vào S3.
- Operational overhead cao hơn Firehose vì phải tự xây dựng consumer và S3 writer.

**❌ Đáp án B:**
- AWS Glue là ETL service dạng batch, không phù hợp cho real-time ingestion.
- Không thể "ingest real-time" bằng Glue.

**❌ Đáp án D:**
- API Gateway phù hợp cho REST/HTTP API, không phải streaming data ingestion.
- Mỗi phút gọi API → không tối ưu cho dữ liệu streaming liên tục.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Real-time analysis + S3 delivery → Kinesis Data Firehose + Kinesis Data Analytics. KDS cần tự build consumer, Glue là batch, API Gateway là REST."*
