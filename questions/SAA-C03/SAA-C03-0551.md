# Question #551 - Topic 1

A company has a financial application that produces reports. The reports average 50 KB in size and are stored in Amazon S3. The reports are frequently accessed during the first week after production and must be stored for several years. The reports must be retrievable within 6 hours. Which solution meets these requirements MOST cost-effectively?

## Options

**A.** Use S3 Standard. Use an S3 Lifecycle rule to transition the reports to S3 Glacier after 7 days.

**B.** Use S3 Standard. Use an S3 Lifecycle rule to transition the reports to S3 Standard-Infrequent Access (S3 Standard-IA) after 7 days.

**C.** Use S3 Intelligent-Tiering. Configure S3 Intelligent-Tiering to transition the reports to S3 Standard-Infrequent Access (S3 Standard-IA) and S3 Glacier.

**D.** Use S3 Standard. Use an S3 Lifecycle rule to transition the reports to S3 Glacier Deep Archive after 7 days.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Ứng dụng tài chính tạo reports (~50KB), lưu trong S3. Reports được truy cập thường xuyên trong tuần đầu, sau đó lưu trữ nhiều năm. Cần truy xuất trong vòng 6 giờ.
- **Existing Resources:** S3 bucket.
- **Current Issue/Goal:** Chọn storage class và lifecycle policy tiết kiệm nhất đáp ứng yêu cầu truy cập và retrieval time.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `frequently accessed during the first week` | Tuần đầu cần S3 Standard |
| `stored for several years` | Sau đó cần chuyển sang storage class rẻ hơn |
| `retrievable within 6 hours` | Glacier (1-5 phút expedited, 3-5 giờ standard) OK. Deep Archive (12 giờ) không đáp ứng |
| `MOST cost-effectively` | Chi phí tối ưu nhất |
| `lifecycle rule` | Tự động transition giữa các storage classes |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most cost-effective
- **Constraints:** Frequently accessed first week, stored for years, retrievable within 6 hours

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- S3 Standard cho tuần đầu tiên (frequently accessed).
- Lifecycle rule sau 7 ngày transition sang S3 Glacier – chi phí lưu trữ rất thấp, phù hợp cho long-term archive.
- S3 Glacier có retrieval time từ 1-5 phút (expedited) đến 3-5 giờ (standard) → đáp ứng yêu cầu 6 giờ.
- 50KB là kích thước nhỏ nên Glacier minimal storage charge (tối thiểu 90 ngày) – vẫn là lựa chọn rẻ nhất.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B (S3 Standard → S3 Standard-IA):** Standard-IA rẻ hơn Standard cho chi phí lưu trữ nhưng vẫn đắt hơn Glacier. Cho long-term storage (nhiều năm), Glacier tiết kiệm hơn nhiều.

**❌ Đáp án C (Intelligent-Tiering):** S3 Intelligent-Tiering phù hợp khi không biết trước access pattern. Ở đây access pattern đã rõ (frequent → archive), nên lifecycle rules đơn giản và rẻ hơn Intelligent-Tiering (có monitoring fee).

**❌ Đáp án D (S3 Glacier Deep Archive):** Deep Archive có retrieval time từ 12 giờ (standard) → không đáp ứng yêu cầu "retrievable within 6 hours". Chi phí thấp nhất nhưng không phù hợp.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Frequent → archive: Standard 7 days → Glacier. Deep Archive = 12h retrieval, too slow for 6h requirement."*
