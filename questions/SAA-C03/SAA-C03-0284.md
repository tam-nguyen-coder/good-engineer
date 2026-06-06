# Question #284 - Topic 1

As part of budget planning, management wants a report of AWS billed items listed by user. The data will be used to create department budgets. A solutions architect needs to determine the most efficient way to obtain this report information. Which solution meets these requirements?

## Options

**A.** Run a query with Amazon Athena to generate the report.

**B.** Create a report in Cost Explorer and download the report.

**C.** Access the bill details from the billing dashboard and download the bill.

**D.** Modify a cost budget in AWS Budgets to alert with Amazon Simple Email Service (Amazon SES).

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Cần report AWS billed items phân theo user để tạo ngân sách cho các phòng ban.
- **Existing Resources:** (none specified)
- **Current Issue/Goal:** Lấy report billed items by user một cách efficient nhất.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `billed items listed by user` | Cần thông tin tag/user để phân bổ chi phí. |
| `Cost Explorer` | Tool trực quan, có sẵn trong AWS Console để tạo report và download. |
| `most efficient way` | Cần giải pháp đơn giản, không cần cấu hình phức tạp. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most efficient way
- **Constraints:** Budget planning, department-level reporting

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- Cost Explorer có sẵn tính năng tạo custom reports, filter theo user/tags, và download xuống CSV.
- Đây là cách đơn giản, nhanh nhất, không cần cấu hình thêm.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Athena cần có dữ liệu từ AWS Cost and Usage Reports (CUR) được xuất ra S3 trước → cần cấu hình CUR, phức tạp hơn.

**❌ Đáp án C:**
- Bill dashboard chỉ tổng hợp hóa đơn, không phân tích chi tiết theo user/tag.

**❌ Đáp án D:**
- AWS Budgets dùng để tạo ngân sách và cảnh báo, không phải để tạo report.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Cost Explorer = reports + download CSV cho budget planning. Athena dùng cho CUR (nặng hơn)."*
