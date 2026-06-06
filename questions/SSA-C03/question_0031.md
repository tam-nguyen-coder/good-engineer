# Question #31 - Topic 1

A company that hosts its web application on AWS wants to ensure all Amazon EC2 instances. Amazon RDS DB instances. and Amazon Redshift clusters are configured with tags. The company wants to minimize the effort of configuring and operating this check. What should a solutions architect do to accomplish this?

## Options

**A.** Use AWS Config rules to define and detect resources that are not properly tagged.

**B.** Use Cost Explorer to display resources that are not properly tagged. Tag those resources manually.

**C.** Write API calls to check all resources for proper tag allocation. Periodically run the code on an EC2 instance.

**D.** Write API calls to check all resources for proper tag allocation. Schedule an AWS Lambda function through Amazon CloudWatch to periodically run the code.



 ## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Một công ty đang chạy ứng dụng web trên AWS.
- **Existing Resources:** Tài nguyên bao gồm `Amazon EC2 instances`, `Amazon RDS DB instances`, và `Amazon Redshift clusters`.
- **Current Issue/Goal:** Công ty muốn đảm bảo tất cả các tài nguyên này đều được gắn `tags`. Đồng thời, công ty muốn **giảm thiểu tối đa** công sức cấu hình và vận hành việc kiểm tra này.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa |
|---------|---------|
| `tags` | Nhãn dùng để phân loại, quản lý chi phí và bảo mật tài nguyên AWS. |
| `minimize the effort` | Yêu cầu giải pháp fully managed, không cần tự viết code hay quản lý hạ tầng. |
| `AWS Config rules` | Quy tắc để đánh giá và ghi lại cấu hình tài nguyên AWS theo thời gian. |
| `Cost Explorer` | Công cụ phân tích chi phí, không phải công cụ kiểm tra compliance tài nguyên. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Lựa chọn dịch vụ AWS phù hợp nhất (Best Practice / Service Selection).
- **Constraints:** 
  - Phải kiểm tra được tags trên `EC2`, `RDS`, `Redshift`.
  - Phải **tối thiểu hóa effort** trong cấu hình và vận hành (không tự viết code, không quản lý server).

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**
**Giải thích:** `AWS Config` là dịch vụ được thiết kế riêng để đánh giá, ghi lại và kiểm tra cấu hình tài nguyên AWS. AWS cung cấp sẵn các managed rules (ví dụ: `required-tags`) cho phép phát hiện tự động các tài nguyên thiếu tag hoặc không đúng tag mà **không cần viết một dòng code nào**. Kết quả compliance được hiển thị trực quan trên dashboard, hoàn toàn serverless và không đòi hỏi vận hành thêm — đáp ứng hoàn hảo yêu cầu "minimize effort".

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:** `Cost Explorer` chủ yếu dùng để phân tích chi phí và yêu cầu tags phải là cost allocation tags mới hiển thị tốt. Nó không phải công cụ kiểm tra compliance tổng quát cho tất cả tài nguyên, và việc tag thủ công trái ngược với yêu cầu giảm thiểu công sức.
**❌ Đáp án C:** Việc tự viết API calls và chạy trên `EC2 instance` đòi hỏi phải quản lý server (cài đặt, bảo trì, patch, giám sát), tạo ra operational burden lớn, không đáp ứng yêu cầu minimize effort.
**❌ Đáp án D:** Dù dùng `AWS Lambda` có giảm bớt effort so với EC2, nhưng vẫn đòi hỏi phải tự viết code, triển khai, bảo trì logic kiểm tra và xử lý lỗi. `AWS Config` đã có sẵn chức năng này, do đó tự xây dựng giải pháp là không cần thiết và tốn effort hơn.

## 6. MẸO GHI NHỚ
🧠 *Khi đề bài hỏi về kiểm tra cấu hình tài nguyên (tags, encryption, public access...) với yêu cầu **tối thiểu effort / không code**, hãy nghĩ ngay đến `AWS Config Rules`. Đây là dịch vụ "bảo hiểm" cho configuration compliance trên AWS.*


 ---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Một công ty đang triển khai ứng dụng web trên AWS.
- **Existing Resources:** Các tài nguyên hiện có bao gồm `Amazon EC2 instances`, `Amazon RDS DB instances`, và `Amazon Redshift clusters`.
- **Current Issue/Goal:** Công ty muốn đảm bảo tất cả các tài nguyên này đều được cấu hình với `tags`. Đồng thời, công ty muốn **giảm thiểu tối đa** công sức cho việc cấu hình và vận hành quy trình kiểm tra này.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `tags` | Nhãn metadata dùng để phân loại, quản lý chi phí và bảo mật tài nguyên AWS |
| `minimize the effort` | Ưu tiên giải pháp fully managed, không cần tự viết code hay quản lý hạ tầng |
| `AWS Config rules` | Các quy tắc có sẵn để đánh giá và ghi lại cấu hình tài nguyên AWS theo thời gian |
| `Cost Explorer` | Công cụ phân tích chi phí, không phải công cụ kiểm tra `compliance` tài nguyên |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Lựa chọn giải pháp có `operational overhead` thấp nhất / ít effort nhất
- **Constraints:** Phải kiểm tra được `tags` trên `EC2`, `RDS`, và `Redshift`. Không được tốn công sức cấu hình và vận hành.

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- `AWS Config` là dịch vụ được thiết kế riêng để liên tục đánh giá, ghi lại và ki
