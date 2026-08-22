# Question #548 - Topic 1

A company has separate AWS accounts for its finance, data analytics, and development departments. Because of costs and security concerns, the company wants to control which services each AWS account can use. Which solution will meet these requirements with the LEAST operational overhead?

## Options

**A.** Use AWS Systems Manager templates to control which AWS services each department can use.

**B.** Create organization units (OUs) for each department in AWS Organizations. Attach service control policies (SCPs) to the OUs.

**C.** Use AWS CloudFormation to automatically provision only the AWS services that each department can use.

**D.** Set up a list of products in AWS Service Catalog in the AWS accounts to manage and control the usage of specific AWS services.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Công ty có nhiều AWS accounts riêng cho finance, data analytics, development. Muốn kiểm soát service nào được dùng trong mỗi account vì lý do cost và security.
- **Existing Resources:** Nhiều AWS accounts riêng lẻ.
- **Current Issue/Goal:** Hạn chế services mà mỗi account được phép sử dụng.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `control which services` | Chặn/khoá các service không được phép |
| `AWS Organizations` | Dịch vụ quản lý nhiều accounts |
| `service control policies (SCPs)` | Chính sách kiểm soát services trong Organizations |
| `organizational units (OUs)` | Nhóm accounts theo department |
| `LEAST operational overhead` | Giải pháp đơn giản, dễ quản lý nhất |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Least operational overhead
- **Constraints:** Kiểm soát services theo account/department

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- AWS Organizations cho phép tạo OUs theo department và gán SCPs để chặn các services không mong muốn.
- SCPs hoạt động như một permission guardrail – account members không thể truy cập services đã bị chặn, kể cả admin.
- Đây là giải pháp centralized, chỉ cần cấu hình một lần ở management account.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A (Systems Manager templates):** AWS Systems Manager dùng để quản lý cấu hình và patch cho EC2, không phải để kiểm soát services account-wide.

**❌ Đáp án C (CloudFormation):** CloudFormation dùng để provisioning infrastructure, không phải để enforce service restrictions. Nếu dùng CloudFormation, user vẫn có thể tạo resources bằng console hoặc CLI.

**❌ Đáp án D (Service Catalog):** Service Catalog giúp tạo danh sách các sản phẩm được phép dùng (portfolios), nhưng không thể block services ở cấp độ account. User có thể bypass Service Catalog và dùng console/CLI trực tiếp. Operational overhead cũng cao hơn SCPs.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"SCPs = guardrails for AWS services across accounts. OUs group by department. Service Catalog controls provisioning, not blocking."*
