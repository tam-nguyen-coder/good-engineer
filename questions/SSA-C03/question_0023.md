# Question #23 - Topic 1

A company is storing backup files by using Amazon S3 Standard storage. The files are accessed frequently for 1 month. However, the files are not accessed after 1 month. The company must keep the files indefinitely. Which storage solution will meet these requirements MOST cost-effectively?

## Options

**A.** Configure S3 Intelligent-Tiering to automatically migrate objects.

**B.** Create an S3 Lifecycle configuration to transition objects from S3 Standard to S3 Glacier Deep Archive after 1 month.

**C.** Create an S3 Lifecycle configuration to transition objects from S3 Standard to S3 Standard-Infrequent Access (S3 Standard-IA) after 1 month.

**D.** Create an S3 Lifecycle configuration to transition objects from S3 Standard to S3 One Zone-Infrequent Access (S3 One Zone-IA) after 1 month.



 ## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Công ty đang lưu trữ file backup trên `Amazon S3 Standard`. Các file này được truy cập thường xuyên trong 1 tháng đầu tiên, sau đó không còn được truy cập nữa, nhưng bắt buộc phải được giữ lại vĩnh viễn.
- **Existing Resources:** `S3 Standard` đang chứa toàn bộ backup.
- **Current Issue/Goal:** Tìm giải pháp lưu trữ đáp ứng yêu cầu **MOST cost-effectively** (tiết kiệm chi phí nhất) cho dữ liệu ít truy cập nhưng cần giữ indefinitely.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa |
|---------|---------|
| `S3 Standard` | Storage class cho dữ liệu truy cập thường xuyên, chi phí lưu trữ cao, retrieval nhanh và rẻ. |
| `S3 Glacier Deep Archive` | Storage class rẻ nhất của S3, dành cho long-term archival (lưu trữ dài hạn), dữ liệu truy cập cực kỳ hiếm. |
| `S3 Lifecycle configuration` | Cấu hình tự động chuyển đổi (transition) hoặc xóa (expiration) objects sau một khoảng thời gian nhất định. |
| `S3 Intelligent-Tiering` | Tự động di chuyển objects giữa các tiers dựa trên pattern truy cập thực tế, tính phí monitoring. |
| `S3 Standard-IA` | Lưu trữ không thường xuyên truy cập, retrieval nhanh, chi phí lưu trữ thấp hơn Standard. |
| `S3 One Zone-IA` | Tương tự `Standard-IA` nhưng chỉ lưu trong một Availability Zone, rủi ro cao hơn. |
| `indefinitely` | Giữ vĩnh viễn / không có thời hạn xóa. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Cost Optimization – Lựa chọn Storage Class phù hợp.
- **Constraints:** 
  - Tháng đầu: truy cập thường xuyên.
  - Sau 1 tháng: không truy cập, giữ indefinitely.
  - Ưu tiên chi phí thấp nhất (MOST cost-effectively).

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:** Vì dữ liệu chỉ cần truy cập trong 1 tháng đầu và sau đó phải giữ vĩnh viễn mà không còn truy cập, `S3 Glacier Deep Archive` là storage class có **chi phí lưu trữ thấp nhất** trong hệ sinh thái S3, được thiết kế riêng cho long-term archival. Sử dụng `S3 Lifecycle configuration` để tự động chuyển objects từ `S3 Standard` sang `S3 Glacier Deep Archive` sau 1 tháng sẽ tối ưu hóa chi phí lưu trữ tối đa cho kịch bản này, đồng thời vẫn đảm bảo durability 11 nines như các storage class khác.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:** `S3 Intelligent-Tiering` phù hợp khi access pattern **không thể đoán trước**. Trong đề bài, pattern đã rõ ràng (1 tháng active → archival vĩnh viễn), nên việc dùng lifecycle cố định sẽ tránh được phí monitoring của `Intelligent-Tiering` và đưa dữ liệu trực tiếp vào lớp rẻ nhất thay vì đợi hệ thống tự động di chuyển qua các tầng trung gian.

**❌ Đáp án C:** `S3 Standard-IA` có chi phí lưu trữ cao hơn đáng kể so với `S3 Glacier Deep Archive`. Storage class này được thiết kế cho dữ liệu truy cập không thường xuyên nhưng vẫn cần truy cập ngay lập tức khi có yêu cầu, không phải là lựa chọn tiết kiệm nhất cho indefinite archival.

**❌ Đáp án D:** `S3 One Zone-IA` tuy rẻ hơn `Standard-IA` nhưng vẫn đắt hơn `Glacier Deep Archive`. Ngoài ra, nó chỉ lưu trữ trong một Availability Zone duy nhất, tiềm ẩn rủi ro mất dữ liệu nếu AZ đó bị phá hủy, và không đáp ứng được yêu cầu "most cost-effective" cho kịch bản backup dài hạn.

## 6. MẸO GHI NHỚ
🧠 *Khi đề bài xuất hiện các từ khóa "indefinitely", "not accessed", "rarely accessed", hoặc "long-term retention" kèm theo "MOST cost-effective" → hãy ưu tiên nghĩ đến `S3 Glacier Deep Archive`. `S3 Intelligent-Tiering` chỉ là lựa chọn tối ưu khi access pattern hoàn toàn không xác định được trước.*
