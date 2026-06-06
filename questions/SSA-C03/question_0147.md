# Question #147 - Topic 1

A company needs to retain application log files for a critical application for 10 years. The application team regularly accesses logs from the past month for troubleshooting, but logs older than 1 month are rarely accessed. The application generates more than 10 TB of logs per month. Which storage option meets these requirements MOST cost-effectively?

## Options

**A.** Store the logs in Amazon S3. Use AWS Backup to move logs more than 1 month old to S3 Glacier Deep Archive.

**B.** Store the logs in Amazon S3. Use S3 Lifecycle policies to move logs more than 1 month old to S3 Glacier Deep Archive.

**C.** Store the logs in Amazon CloudWatch Logs. Use AWS Backup to move logs more than 1 month old to S3 Glacier Deep Archive.

**D.** Store the logs in Amazon CloudWatch Logs. Use Amazon S3 Lifecycle policies to move logs more than 1 month old to S3 Glacier Deep Archive.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** 10TB/month application logs, retain 10 years. Access past month regularly, older rarely.
- **Existing Resources:** Chưa có.
- **Current Issue/Goal:** Most cost-effective log storage.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `10 TB of logs per month` | Lượng lớn → **S3** rẻ hơn CloudWatch Logs |
| `logs older than 1 month are rarely accessed` | S3 Lifecycle → **Glacier Deep Archive** |
| `most cost-effectively` | S3 Lifecycle policy (free, managed) |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Cost optimization + Log retention
- **Constraints:** 10 years, 10TB/month

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- **S3** — chi phí lưu trữ thấp hơn CloudWatch Logs cho dung lượng lớn.
- **S3 Lifecycle** — tự động move objects từ S3 Standard → Glacier Deep Archive sau 1 tháng.
- Lifecycle policy là **free**, managed, không cần AWS Backup.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- AWS Backup — thêm chi phí, không cần thiết khi có S3 Lifecycle.

**❌ Đáp án C:**
- **CloudWatch Logs** — expensive cho 10TB/month (ingestion + storage costs cao).
- AWS Backup không thể move từ CloudWatch Logs.

**❌ Đáp án D:**
- CloudWatch Logs expensive. S3 Lifecycle không áp dụng cho CloudWatch Logs.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"S3 Lifecycle = free + managed. CloudWatch Logs = expensive for large volume. Glacier Deep Archive = cheapest archive"*
