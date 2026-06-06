# Question #525 - Topic 1

A company wants to add its existing AWS usage cost to its operation cost dashboard. A solutions architect needs to recommend a solution that will give the company access to its usage cost programmatically. The company must be able to access cost data for the current year and forecast costs for the next 12 months. Which solution will meet these requirements with the LEAST operational overhead?

## Options

**A.** Access usage cost-related data by using the AWS Cost Explorer API with pagination.

**B.** Access usage cost-related data by using downloadable AWS Cost Explorer report .csv files.

**C.** Configure AWS Budgets actions to send usage cost data to the company through FTP.

**D.** Create AWS Budgets reports for usage cost data. Send the data to the company through SMTP.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Cần programmatic access để lấy AWS usage cost và forecast costs.
- **Existing Resources:** AWS accounts with usage cost.
- **Current Issue/Goal:** Tích hợp cost data vào operation dashboard, cần historical (current year) + forecast (12 months).

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `programmatically` | Cần API, không phải file download hay email |
| `Cost Explorer API` | API truy xuất cost data và forecast |
| `forecast costs for the next 12 months` | Cost Explorer hỗ trợ forecasting |
| `least operational overhead` | Dùng managed API, không cần xử lý file |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Least operational overhead
- **Constraints:** Programmatic access, current year + 12-month forecast

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- AWS Cost Explorer API cung cấp programmatic access để query historical cost data và forecast.
- API hỗ trợ pagination để lấy dữ liệu lớn.
- Dễ tích hợp vào operation dashboard.
- Không cần xử lý file, không cần cấu hình delivery.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- CSV files là manual process, không phải programmatic access.
- Cần tải file và parse → operational overhead cao hơn dùng API.

**❌ Đáp án C:**
- AWS Budgets actions không hỗ trợ gửi cost data qua FTP.
- Budgets dùng để cảnh báo khi vượt ngân sách, không phải để lấy cost data programmatically.

**❌ Đáp án D:**
- Budgets reports gửi qua email (SMTP), không phải programmatic access.
- Không hỗ trợ forecast costs.

## 6. MẸO GHI NHỚ (MEMORY HOOK)
🧠 *"Programmatic cost access = Cost Explorer API + pagination. CSV/email = manual."*
