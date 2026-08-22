# Question #160 - Topic 1

An ecommerce company hosts its analytics application in the AWS Cloud. The application generates about 300 MB of data each month. The data is stored in JSON format. The company is evaluating a disaster recovery solution to back up the data. The data must be accessible in milliseconds if it is needed, and the data must be kept for 30 days. Which solution meets these requirements MOST cost-effectively?

## Options

**A.** Amazon OpenSearch Service (Amazon Elasticsearch Service)

**B.** Amazon S3 Glacier

**C.** Amazon S3 Standard

**D.** Amazon RDS for PostgreSQL

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Analytics app, 300MB/month JSON data. DR backup: milliseconds access, keep 30 days.
- **Existing Resources:** Analytics application.
- **Current Issue/Goal:** Cost-effective DR backup with milliseconds access.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `milliseconds` | Cần **S3 Standard** (immediate access) |
| `300 MB of data each month` | Rất nhỏ |
| `30 days` | Retention ngắn |
| `most cost-effectively` | S3 Standard rẻ cho dung lượng nhỏ |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** DR + Cost optimization
- **Constraints:** Milliseconds access, 30 days

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- **S3 Standard** — milliseconds retrieval, 99.99% availability, 11 9's durability.
- 300MB là dung lượng rất nhỏ → cost của S3 Standard không đáng kể.
- Phù hợp cho DR backup với access nhanh.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- OpenSearch — overkill, đắt hơn S3 cho 300MB backup.

**❌ Đáp án B:**
- **S3 Glacier** — retrieval time phút → giờ, không milliseconds.

**❌ Đáp án D:**
- **RDS** — provisioned database, expensive cho 300MB JSON backup.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"300MB → S3 Standard = rẻ + milliseconds. Glacier = slow retrieval. RDS = overkill"*
