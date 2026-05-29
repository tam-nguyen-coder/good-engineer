# Question #463 - Topic 1

An IoT company is releasing a mattress that has sensors to collect data about a user's sleep. The sensors will send data to an Amazon S3 bucket. The sensors collect approximately 2 MB of data every night for each mattress. The company must process and summarize the data for each mattress. The results need to be available as soon as possible. Data processing will require 1 GB of memory and will finish within 30 seconds. Which solution will meet these requirements MOST cost-effectively?

## Options

**A.** Use AWS Glue with a Scala job

**B.** Use Amazon EMR with an Apache Spark script

**C.** Use AWS Lambda with a Python script

**D.** Use AWS Glue with a PySpark job

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** IoT mattress sensors gửi 2MB dữ liệu/đêm lên S3. Cần process và summarize cho mỗi mattress.
- **Existing Resources:** S3 bucket.
- **Current Issue/Goal:** Process data càng sớm càng tốt, cost-effective. Yêu cầu 1GB memory, finish trong 30s.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `2 MB of data` | Rất nhỏ, không cần big data framework. |
| `1 GB of memory` | Lambda hỗ trợ tối đa 10GB memory (từ 2020). |
| `finish within 30 seconds` | Lambda max execution timeout 15 minutes → 30s là hợp lý. |
| `MOST cost-effective` | Serverless (Lambda) = pay per request, không tốn chi phí cố định. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most cost-effective
- **Constraints:** 1GB memory, finish < 30s, data nhỏ (2MB/night)

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- AWS Lambda: hỗ trợ tối đa 10GB memory, max 15 phút execution → 1GB memory và 30s hoàn toàn phù hợp.
- Data nhỏ (2MB) → Lambda lý tưởng, không cần cluster.
- Pay per invocation, không tốn chi phí khi không chạy → cost-effective nhất.
- Có thể trigger từ S3 event.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A (AWS Glue Scala):**
- Glue là ETL service, provision capacity (DPU) → tốn chi phí cố định.
- Scala job overkill cho 2MB data.

**❌ Đáp án B (EMR Spark):**
- EMR cần cluster (EC2 instances) → chi phí cao, overkill.
- Spark có overhead khởi tạo cluster.

**❌ Đáp án D (Glue PySpark):**
- Glue với PySpark cũng provision DPU, chi phí cao hơn Lambda.
- Overkill cho data nhỏ.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Data nhỏ + 1GB RAM + 30s → Lambda. Glue/EMR = overkill (big data tools cho data nhỏ)."*
