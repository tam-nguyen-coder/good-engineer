# Question #24 - Topic 1

A company observes an increase in Amazon EC2 costs in its most recent bill. The billing team notices unwanted vertical scaling of instance types for a couple of EC2 instances. A solutions architect needs to create a graph comparing the last 2 months of EC2 costs and perform an in-depth analysis to identify the root cause of the vertical scaling. How should the solutions architect generate the information with the LEAST operational overhead?

## Options

**A.** Use AWS Budgets to create a budget report and compare EC2 costs based on instance types.

**B.** Use Cost Explorer's granular filtering feature to perform an in-depth analysis of EC2 costs based on instance types.

**C.** Use graphs from the AWS Billing and Cost Management dashboard to compare EC2 costs based on instance types for the last 2 months.

**D.** Use AWS Cost and Usage Reports to create a report and send it to an Amazon S3 bucket. Use Amazon QuickSight with Amazon S3 as a source to generate an interactive graph based on instance types.



 ## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Một công ty quan sát thấy chi phí `Amazon EC2` tăng bất thường trong bill gần nhất. Đội billing phát hiện có hiện tượng vertical scaling không mong muốn trên một số instance.
- **Existing Resources:** Các `EC2 instances` đang chạy.
- **Current Issue/Goal:** Cần tạo biểu đồ so sánh chi phí `EC2` trong 2 tháng qua và thực hiện phân tích chuyên sâu (in-depth analysis) để xác định root cause của việc vertical scaling. Yêu cầu **LEAST operational overhead**.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa |
|---------|---------|
| `vertical scaling` | Thay đổi instance type lên loại lớn hơn (ví dụ: t3.medium → t3.large) gây tăng chi phí |
| `graph comparing the last 2 months` | Cần khả năng visualize xu hướng chi phí theo thời gian |
| `in-depth analysis` | Phân tích chi tiết, có thể lọc (filter) theo nhiều chiều |
| `LEAST operational overhead` | Giải pháp phải có ít công sức vận hành nhất, không cần setup thêm infrastructure |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Cost Optimization / Operational Analysis
- **Constraints:** Phải tạo được biểu đồ so sánh 2 tháng, phân tích theo instance type, và đặc biệt là **ít overhead nhất** (không cần cấu hình phức tạp, không cần thêm dịch vụ khác).

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**
**Giải thích:** `AWS Cost Explorer` là công cụ được thiết kế riêng để visualize và phân tích chi phí, usage của AWS theo thời gian. Nó cho phép:
- Xem biểu đồ chi phí `EC2` trong khoảng thời gian tùy chỉnh (last 2 months).
- Sử dụng **granular filtering** để lọc theo `instance type`, `region`, `tag`, v.v.
- Thực hiện in-depth analysis ngay trên console mà không cần setup thêm infrastructure nào khác.
- Operational overhead gần như bằng 0 vì đây là managed UI có sẵn trong `AWS Billing and Cost Management`.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:** `AWS Budgets` chủ yếu dùng để **thiết lập ngân sách** (budgets) và **gửi cảnh báo** (alerts) khi chi phí vượt ngưỡng. Nó không phải là công cụ để phân tích lịch sử chi tiết, tạo biểu đồ so sánh hoặc drill-down theo instance type.

**❌ Đáp án C:** `AWS Billing and Cost Management dashboard` cung cấp **high-level overview** về tổng chi phí, nhưng không đủ granular để thực hiện in-depth analysis theo từng `instance type`. Dashboard này thiếu khả năng lọc chi tiết và so sánh sâu như `Cost Explorer`.

**❌ Đáp án D:** `AWS Cost and Usage Reports` (`CUR`) kết hợp với `Amazon S3` và `Amazon QuickSight` có thể tạo ra interactive graph rất mạnh, nhưng operational overhead **cực kỳ cao**: phải cấu hình report, provision `S3 bucket`, setup `QuickSight`, import dataset, tạo visualization. Điều này vi phạm yêu cầu **LEAST operational overhead** của đề bài.

## 6. MẸO GHI NHỚ
🧠 *Phân tích chi phí nhanh + ít overhead nhất → `Cost Explorer`.  
Cần cảnh báo ngân sách → `AWS Budgets`.  
Cần báo cáo raw data chi tiết nhất để xử lý bên ngoài/business intelligence → `CUR` (nhưng overhead cao).*


---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Một công ty nhận thấy chi phí `Amazon EC2` tăng bất thường trong bill gần nhất. Nhóm billing phát hiện có hiện tượng `vertical scaling` không mong muốn trên một số `instance types`.
- **Existing Resources:** Các `EC2 instances` đang chạy trong hệ thống.
- **Current Issue/Goal:** Cần tạo biểu đồ so sánh chi phí `EC2` trong 2 tháng qua và thực hiện `in-depth analysis` để xác định `root cause` của việc `vertical scaling`. Yêu cầu quan trọng nhất là **LEAST operational overhead**.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `vertical scaling` | Thay đổi `instance type` sang loại lớn hơn (ví dụ: `t3.medium` → `t3.large`), dẫn đến tăng chi phí |
| `graph comparing the last 2 months` | Cần khả năng `visualize` xu hướng chi phí theo thời gian |
| `in-depth analysis` | Phân tích chi tiết, có khả năng `filter` và `group by` theo nhiều chiều |
| `LEAST operational overhead` | Ít công sức vận hành nhất, không cần `setup` thêm `infrastructure` hay dịch vụ bổ trợ |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Cost Analysis / `Least operational overhead`
- **Constraints:** Phải tạo được biểu đồ so sánh 2 tháng, phân tích theo `instance type`, và không được tốn nhiều công sức vận hành.

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- `AWS Cost Explorer` là công cụ chuyên dụng để `visualize` và phân tích chi phí cũng như `usage` của AWS theo thời gian.
- Nó cho phép xem biểu đồ chi phí `EC2` trong khoảng thời gian tùy chỉnh (`last 2 months`) và sử dụng tính năng `granular filtering` để lọc cũng như nhóm theo `instance type`, `region`, `tag`, v.v.
- Có thể thực hiện `in-depth analysis` và `drill-down` ngay trên console mà không cần cấu hình thêm bất kỳ `infrastructure` nào khác.
- `Operational overhead` gần như bằng không vì đây là `managed UI` có sẵn trong `AWS Billing and Cost Management console`, hoàn toàn phù hợp với yêu cầu của đề bài.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- `AWS Budgets` chủ yếu được thiết kế để thiết lập `budgets` (ngân sách) và gửi `alerts` khi chi phí vượt ngưỡng. Nó không phải là công cụ để phân tích lịch sử chi tiết, tạo biểu đồ so sánh, hay `drill-down` theo `instance type` để tìm `root cause`.

**❌ Đáp án C:**
- `AWS Billing and Cost Management dashboard` chỉ cung cấp cái nhìn tổng quan ở mức `high-level` (tổng chi phí theo dịch vụ). Nó thiếu khả năng `granular filtering` theo từng `instance type` và không đủ sâu để thực hiện `in-depth analysis` so sánh chi phí giữa các loại `instance`.

**❌ Đáp án D:**
- `AWS Cost and Usage Reports` (`CUR`) kết hợp với `Amazon S3` và `Amazon QuickSight` có thể tạo ra `interactive graph` rất mạnh mẽ cho `business intelligence`. Tuy nhiên, giải pháp này có `operational overhead` rất cao: phải cấu hình `report`, `provision` `S3 bucket`, `setup` `QuickSight`, `import dataset`, và tạo `visualization`. Điều này trái ngược hoàn toàn với yêu cầu `LEAST operational overhead`.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *Phân tích chi phí nhanh + ít overhead nhất → `Cost Explorer`. Cần cảnh báo ngân sách → `AWS Budgets`. Cần dữ liệu raw chi tiết nhất để `BI` → `CUR` + `QuickSight` (nhưng overhead cao).*

---
